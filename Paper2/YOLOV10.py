# """
# Runs large-scale object detection on street-level imagery using the YOLOv10 ONNX model.

# This script performs an end-to-end object detection workflow that downloads street-level
# images from Azure Blob Storage, executes inference using a pretrained YOLOv10 model,
# exports detections at multiple confidence thresholds, generates annotated images for
# visual inspection, and uploads the resulting outputs back to Azure.

# The workflow is designed for efficient batch processing of large image collections by
# using parallel downloads, multi-threaded file generation, and concurrent cloud uploads.

# For each image, object detections are performed only once using the lowest confidence
# threshold. The resulting detections are then filtered to produce separate outputs for
# multiple confidence thresholds without rerunning the neural network, substantially
# reducing processing time.

# Each confidence threshold produces:
#     - YOLO label files containing class ID, confidence score, and bounding-box coordinates.
#     - Annotated images with coloured bounding boxes and class labels.

# Main processing steps:
#     1. Install required Python dependencies.
#     2. Download the pretrained YOLOv10 ONNX model.
#     3. Download street-level images from Azure Blob Storage.
#     4. Perform object detection using YOLOv10.
#     5. Filter detections for multiple confidence thresholds.
#     6. Export detection labels in YOLO format.
#     7. Generate annotated images showing detected objects.
#     8. Upload all generated outputs back to Azure Blob Storage.

# Detection outputs are generated for the following confidence thresholds:
#     - 0.50
#     - 0.60
#     - 0.70
#     - 0.80
#     - 0.90

# The exported label files contain, for each detected object:
#     - Object class ID
#     - Detection confidence
#     - Bounding-box centre coordinates
#     - Bounding-box width
#     - Bounding-box height

# All bounding boxes are saved in YOLO-compatible format.

# Inputs:
#     - Street-level images stored in Azure Blob Storage.
#     - Pretrained YOLOv10 ONNX model (yolov10n.onnx).

# Outputs:
#     - Detection label files (.txt)
#     - Annotated images (.jpg)
#     - Azure Blob Storage directory containing detection results organised by
#       confidence threshold.

# The pipeline supports concurrent image downloads, parallel output generation,
# and multi-threaded uploads to efficiently process large image datasets while
# minimising overall runtime.
# """

# 1) Install dependencies
import sys

!pip install -q ultralytics onnxruntime opencv-python pillow matplotlib tqdm
!pip install requests azure-storage-blob tqdm

print("Install step completed. If you require a CUDA torch, install it manually following https://pytorch.org.")

# 2) Download the official ONNX model from THU-MIG releases (v1.1 used here)
# Official release URL used in this notebook:
# https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10n.onnx

import os
from urllib.request import urlretrieve
from pathlib import Path
import hashlib

os.makedirs('weights', exist_ok=True)
onnx_path = Path('weights/yolov10n.onnx')

download_url = 'https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10n.onnx'

if not onnx_path.exists():
    print(f"Downloading {download_url} -> {onnx_path} ...")
    try:
        urlretrieve(download_url, str(onnx_path))
        print("Downloaded ONNX to", onnx_path)
    except Exception as e:
        raise RuntimeError("Failed to download ONNX automatically. Please download manually from the THU-MIG releases page.") from e
else:
    print("ONNX already exists:", onnx_path)


import os
from azure.storage.blob import BlobServiceClient
from concurrent.futures import ThreadPoolExecutor, as_completed

# Config
local_download_dir = "images"
os.makedirs(local_download_dir, exist_ok=True)
connection_string = ""
container_name = "london"
prefix_path = "training/training/Images"
MAX_WORKERS = 8  # number of threads; tune for Colab

# Azure client
blob_service = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service.get_container_client(container_name)

# List blobs
print(f"Listing blobs under '{prefix_path}'...")
blob_list = [b for b in container_client.list_blobs(name_starts_with=prefix_path)
             if b.name.rstrip("/") != prefix_path.rstrip("/")]
print(f"Found {len(blob_list)} blobs.")

# Function to download a single blob
def download_blob(blob):
    blob_name = blob.name
    relative_path = os.path.relpath(blob_name, prefix_path)
    local_path = os.path.join(local_download_dir, relative_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        with open(local_path, "wb") as file:
            blob_data = container_client.download_blob(blob_name)
            blob_data.readinto(file)
        return (blob_name, "OK")
    except Exception as e:
        return (blob_name, f"ERROR: {e}")

# Download in parallel
results = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_blob, b) for b in blob_list]
    for fut in as_completed(futures):
        blob_name, status = fut.result()
        print(f"{status}: {blob_name}")
        results.append((blob_name, status))

print("Download complete.")



from pathlib import Path
import shutil, cv2
from ultralytics import YOLO
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import numpy as np
import cv2

output_root = Path("runs") / "detect"
# --- CLEAN OUTPUT ---
if output_root.exists():
    shutil.rmtree(output_root)
output_root.mkdir(parents=True, exist_ok=True)

# --- CONFIG ---
onnx_path = "weights/yolov10n.onnx"
images_dir = Path("images")
output_root = Path("runs") / "detect"
conf_thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
save_images = True   # set False to skip annotated images
imgsz = 640          # reduce for faster inference if acceptable

MAX_WORKERS = 4      # threads for per-threshold saving

# --- CLEAN OUTPUT ---
if output_root.exists():
    shutil.rmtree(output_root)
output_root.mkdir(parents=True, exist_ok=True)

# --- LOAD MODEL ---
print(f"Loading YOLO model from: {onnx_path}")
model = YOLO(onnx_path)

# --- RUN INFERENCE ONCE (lowest threshold) ---
min_conf = min(conf_thresholds)
results = model.predict(
    source=str(images_dir),
    conf=min_conf,
    save=False,
    save_txt=False,
    stream=True,
    imgsz=imgsz
)

def yolo_color_for_class(cls_id):
    """
    Deterministic bright color for a class id.
    Returns BGR tuple of ints (OpenCV uses BGR).
    """
    # Generate an HSV color from the class id, then convert to BGR
    # Hue step chosen to give distinct colors for many classes
    hue = int((cls_id * 37) % 180)        # 0..179 for OpenCV HSV
    sat = 200
    val = 255
    hsv = np.uint8([[[hue, sat, val]]])
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0].tolist()
    return tuple(int(x) for x in bgr)     # list -> (B, G, R)

def draw_boxes_yolo_style(img, boxes, normalized, img_w, img_h, model_names=None,
                          box_thickness=2, font_scale=0.5):
    """
    Draw boxes with per-class YOLO-like colors and readable labels.
    boxes: list of dicts {"cls","conf","x","y","w","h"} with center-format.
    normalized: True if coords are 0..1, else pixel coords.
    model_names: optional dict or list mapping class id -> class name.
    """
    out = img.copy()
    for b in boxes:
        cls_id = int(b["cls"])
        conf = b["conf"]
        # convert center-format to xyxy pixels
        if normalized:
            cx = b["x"] * img_w
            cy = b["y"] * img_h
            w = b["w"] * img_w
            h = b["h"] * img_h
        else:
            cx = b["x"]
            cy = b["y"]
            w = b["w"]
            h = b["h"]
        x1 = int(round(cx - w/2))
        y1 = int(round(cy - h/2))
        x2 = int(round(cx + w/2))
        y2 = int(round(cy + h/2))

        # clamp coords
        x1 = max(0, min(x1, img_w-1))
        y1 = max(0, min(y1, img_h-1))
        x2 = max(0, min(x2, img_w-1))
        y2 = max(0, min(y2, img_h-1))

        color = yolo_color_for_class(cls_id)
        # thicker rectangle for visibility
        cv2.rectangle(out, (x1, y1), (x2, y2), color, box_thickness, lineType=cv2.LINE_AA)

        # label text: either "name conf" or "cls conf"
        label_txt = f"{model_names[cls_id] if (model_names is not None and cls_id in model_names) else cls_id} {conf:.2f}"

        # compute text size & background
        ((txt_w, txt_h), _) = cv2.getTextSize(label_txt, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
        # draw filled rectangle above box (or below if not enough space)
        pad = 3
        lbl_x1 = x1
        lbl_y1 = y1 - txt_h - 2*pad
        lbl_y2 = y1
        if lbl_y1 < 0:
            lbl_y1 = y2
            lbl_y2 = y2 + txt_h + 2*pad
        # background rectangle with same class color but slightly darker for contrast
        bg_color = (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30))
        cv2.rectangle(out, (lbl_x1, lbl_y1), (lbl_x1 + txt_w + 2*pad, lbl_y2), bg_color, -1)
        # put text in white
        txt_org = (lbl_x1 + pad, lbl_y2 - pad - 2)
        cv2.putText(out, label_txt, txt_org, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255,255,255), 1, cv2.LINE_AA)

    return out


# --- FUNCTION TO PROCESS ONE IMAGE FOR ALL THRESHOLDS ---
def draw_boxes_on_image(img, boxes, normalized, img_w, img_h):
    """
    Draw center-format boxes (x=center_x, y=center_y, w, h) onto img.
    If normalized=True, convert using img_w/img_h.
    """
    out = img.copy()
    for b in boxes:
        # convert center xywh to xyxy pixel coords
        if normalized:
            cx = b["x"] * img_w
            cy = b["y"] * img_h
            w = b["w"] * img_w
            h = b["h"] * img_h
        else:
            cx = b["x"]
            cy = b["y"]
            w = b["w"]
            h = b["h"]
        x1 = int(round(cx - w / 2.0))
        y1 = int(round(cy - h / 2.0))
        x2 = int(round(cx + w / 2.0))
        y2 = int(round(cy + h / 2.0))

        # clamp to image
        x1 = max(0, min(x1, img_w - 1))
        y1 = max(0, min(y1, img_h - 1))
        x2 = max(0, min(x2, img_w - 1))
        y2 = max(0, min(y2, img_h - 1))

        # draw box and label
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        txt = f'{b["cls"]} {b["conf"]:.2f}'
        # put label above box (or inside if too high)
        ty = y1 - 6 if y1 - 6 > 6 else y1 + 12
        cv2.putText(out, txt, (x1, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    return out

def process_image(r):
    img_path = Path(r.path)
    img_stem = img_path.stem
    boxes = r.boxes
    if boxes is None or len(boxes) == 0:
        return img_stem, 0, 0

    # --- build all_boxes as you already do (kept same) ---
    all_boxes = []
    try:
        n = len(boxes)
        cls_arr = boxes.cls
        conf_arr = boxes.conf
        xywh_arr = boxes.xywh
        for i in range(n):
            cls_item = cls_arr[i]
            cls_val = int(cls_item.item()) if hasattr(cls_item, "item") else int(cls_item)
            conf_item = conf_arr[i]
            conf_val = float(conf_item.item()) if hasattr(conf_item, "item") else float(conf_item)
            xywh = xywh_arr[i]
            if hasattr(xywh, "cpu"):
                xywh = xywh.cpu().numpy()
            x, y, w, h = map(float, xywh)
            all_boxes.append({"cls": cls_val, "conf": conf_val, "x": x, "y": y, "w": w, "h": h})
    except Exception:
        for box in boxes:
            try:
                cls_item = box.cls
                cls_val = int(cls_item.item()) if hasattr(cls_item, "item") else int(cls_item)
                conf_item = box.conf
                conf_val = float(conf_item.item()) if hasattr(conf_item, "item") else float(conf_item)
                xywh = box.xywh
                if hasattr(xywh, "cpu"):
                    xywh = xywh.cpu().numpy()
                x, y, w, h = map(float, xywh)
                all_boxes.append({"cls": cls_val, "conf": conf_val, "x": x, "y": y, "w": w, "h": h})
            except Exception:
                continue

    if not all_boxes:
        return img_stem, 0, 0

    # Determine image source and size for drawing
    # Prefer r.orig_img if available (it's the array used by the model)
    img_for_draw = None
    img_h = img_w = None
    if hasattr(r, "orig_img") and getattr(r, "orig_img") is not None:
        img_for_draw = r.orig_img
        img_h, img_w = img_for_draw.shape[:2]
    else:
        # fallback: read from disk
        img_for_draw = cv2.imread(str(img_path))
        if img_for_draw is None:
            # can't annotate image without pixel data; still write labels but skip images
            img_h = img_w = None
        else:
            img_h, img_w = img_for_draw.shape[:2]

    # Decide whether coordinates are normalized (0..1) or absolute pixels.
    # Heuristic: if any coord > 1.1 -> absolute pixels. If all <=1.0 -> normalized.
    coords_large = any(max(b["x"], b["y"], b["w"], b["h"]) > 1.1 for b in all_boxes)
    normalized_coords = not coords_large

    saved_total = 0
    skipped_total = 0

    def save_for_threshold(conf):
        filtered = [b for b in all_boxes if b["conf"] >= conf]
        if not filtered:
            return 0, 1

        out_labels_dir = output_root / f"conf_{conf}" / "labels"
        out_labels_dir.mkdir(parents=True, exist_ok=True)
        out_images_dir = output_root / f"conf_{conf}" / "images"
        out_images_dir.mkdir(parents=True, exist_ok=True)

        # Write label file (same as before)
        out_txt = out_labels_dir / f"{img_stem}.txt"
        with open(out_txt, "w") as fh:
            lines = [
                f'{b["cls"]} {b["conf"]:.6f} {b["x"]:.2f} {b["y"]:.2f} {b["w"]:.2f} {b["h"]:.2f}'
                for b in filtered
            ]
            fh.write("\n".join(lines))

        # Create and save a threshold-filtered image:
        if save_images and img_for_draw is not None and img_w is not None and img_h is not None:
            model_names = getattr(model, "names", None)
            img_annot = draw_boxes_yolo_style(img_for_draw, filtered, normalized_coords, img_w, img_h, model_names=model_names)
            out_img_path = out_images_dir / f"{img_stem}.jpg"
            cv2.imwrite(str(out_img_path), img_annot, [cv2.IMWRITE_JPEG_QUALITY, 85])

        return len(filtered), 0

    # Parallelize per-threshold saving (same as you had)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(save_for_threshold, conf) for conf in conf_thresholds]
        for fut in as_completed(futures):
            s, skip = fut.result()
            saved_total += s
            skipped_total += skip

    return img_stem, saved_total, skipped_total

# --- PROCESS ALL IMAGES WITH PROGRESS BAR ---
summary = []
for r in tqdm(results, desc="Processing images"):
    summary.append(process_image(r))

# --- SUMMARY ---
total_saved = sum(s for _, s, _ in summary)
total_skipped = sum(sk for _, _, sk in summary)
print(f"\nAll done. Total saved files: {total_saved}, skipped (no detections): {total_skipped}")
print(f"Check {output_root}/conf_<threshold>/labels/ for results.")




# fast_upload_colab.py
# pip install required libs first:
!pip install azure-storage-blob tqdm

import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError
from tqdm import tqdm
import time

# CONFIG - put sensitive values in env vars (recommended)
CONN_STR = os.environ.get("AZ_CONN_STR") or ""
CONTAINER = "london"
BASE_DIR = Path("runs/detect")
AZURE_ROOT = "YoloV10"

# Tunables for Colab
MAX_WORKERS = 6          # safe default for Colab; raise to 8-12 if you know network is good
UPLOAD_MAX_CONCURRENCY = 2  # parallel chunks per single file upload (azure SDK)
RETRY_LIMIT = 3

blob_service = BlobServiceClient.from_connection_string(CONN_STR)
container_client = blob_service.get_container_client(CONTAINER)

# collect files
file_list = []
for root, _, files in os.walk(BASE_DIR):
    for fname in files:
        local_path = Path(root) / fname
        rel = local_path.relative_to(BASE_DIR)
        blob_path = str(Path(AZURE_ROOT) / rel).replace("\\", "/")
        file_list.append((local_path, blob_path))

print(f"Found {len(file_list)} files. Workers={MAX_WORKERS}")

def upload_one(local_path, blob_path):
    blob_client = container_client.get_blob_client(blob_path)
    attempt = 0
    while attempt <= RETRY_LIMIT:
        try:
            with open(local_path, "rb") as fh:
                blob_client.upload_blob(fh, overwrite=True, max_concurrency=UPLOAD_MAX_CONCURRENCY)
            return (local_path, blob_path, None)
        except AzureError as e:
            attempt += 1
            if attempt > RETRY_LIMIT:
                return (local_path, blob_path, str(e))
            backoff = 2 ** attempt
            time.sleep(backoff)

errors = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
    futures = {ex.submit(upload_one, lp, bp): (lp, bp) for lp,bp in file_list}
    for fut in tqdm(as_completed(futures), total=len(futures), desc="Uploading"):
        lp, bp, err = fut.result()
        if err:
            errors.append((lp, bp, err))

print("Upload finished. Errors:", len(errors))
if errors:
    for p,b,e in errors[:10]:
        print("ERR:", p, "->", b, e)

