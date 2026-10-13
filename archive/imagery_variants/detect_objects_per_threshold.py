import sys
import os
from urllib.request import urlretrieve
from pathlib import Path
import hashlib
from azure.storage.blob import BlobServiceClient
from pathlib import Path

# pip install -q ultralytics onnxruntime opencv-python pillow matplotlib tqdm
# pip install requests azure-storage-blob tqdm

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

local_download_dir = "images"
os.makedirs(local_download_dir, exist_ok=True)

connection_string = os.environ.get("AZ_CONN_STR")
container_name = "london"
prefix_path = "training/training/Images"

blob_service = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service.get_container_client(container_name)

print(f"Listing blobs under '{prefix_path}'...")
blob_list = container_client.list_blobs(name_starts_with=prefix_path)

for blob in blob_list:
    blob_name = blob.name
    if blob_name.rstrip("/") == prefix_path.rstrip("/"):
        continue

    relative_path = os.path.relpath(blob_name, prefix_path)
    local_path = os.path.join(local_download_dir, relative_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    print(local_path)

    print(f"Downloading: {blob_name} -> {local_path}")
    with open(local_path, "wb") as file:
        blob_data = container_client.download_blob(blob_name)
        blob_data.readinto(file)

print("Download complete.")
print("Images available in ./images:", os.listdir(local_download_dir))

out_dir = Path('runs/detect/predict')
out_dir.mkdir(parents=True, exist_ok=True)

onnx_path = str(Path("weights/yolov10n.onnx").resolve())
images_dir = Path("images")
output_root = Path("runs") / "detect"
conf_thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]

if output_root.exists():
    if output_root.name == "detect" and output_root.parent.name == "runs":
        print(f"Removing existing output folder: {output_root} ...")
        shutil.rmtree(output_root)
    else:
        raise RuntimeError(f"Refusing to remove unexpected folder: {output_root}")
else:
    print(f"No existing {output_root} found — starting fresh.")

output_root.mkdir(parents=True, exist_ok=True)

print(f"Loading model from: {onnx_path}")
model = YOLO(onnx_path)

# Run inference for each confidence threshold
for conf in conf_thresholds:
    out_labels_dir = output_root / f"conf_{conf}" / "labels"
    out_labels_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nRunning inference with conf={conf} -> labels dir: {out_labels_dir}")

    # Run inference but DO NOT let ultralytics save images or its own txts
    results = model.predict(source=str(images_dir), conf=conf, save=False, save_txt=False)

    saved_count = 0
    skipped_count = 0

    for r in results:
        img_path = Path(r.path)
        img_stem = img_path.stem
        out_txt = out_labels_dir / f"{img_stem}.txt"

        boxes = getattr(r, "boxes", None)
        if boxes is None or len(boxes) == 0:
            skipped_count += 1
            print(f"  {img_stem}: no detections -> skipping")
            continue

        lines = []
        for box in boxes:
            try:
                cls = int(box.cls[0])
                conf_score = float(box.conf[0])
                xywh = box.xywh[0]
                x_center = float(xywh[0])
                y_center = float(xywh[1])
            except Exception:
                try:
                    cls = int(box.cls)
                    conf_score = float(box.conf)
                    xywh = box.xywh
                    x_center = float(xywh[0]); y_center = float(xywh[1])
                except Exception:
                    continue
            lines.append(f"{cls} {conf_score:.6f} {x_center:.2f} {y_center:.2f}")

        if lines:
            with open(out_txt, "w") as fh:
                fh.write("\n".join(lines))
            saved_count += 1
            print(f"  {img_stem}: wrote {out_txt} ({len(lines)} detections)")
        else:
            skipped_count += 1
            print(f"  {img_stem}: parsed to 0 valid lines -> skipping")

    print(f"Summary (conf={conf}): saved files = {saved_count}, skipped (no detections) = {skipped_count}")

print("\nAll done. Check runs/detect/conf_<threshold>/labels/ for results.")


connection_string = os.environ.get("AZ_CONN_STR")
container_name = "london"
base_dir = Path("runs/detect")
azure_root_folder = "YoloV10"

blob_service = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service.get_container_client(container_name)

for root, _, files in os.walk(base_dir):
    for file_name in files:
        local_file_path = Path(root) / file_name
        relative_path = local_file_path.relative_to(base_dir)
        blob_path = str(Path(azure_root_folder) / relative_path)
        print(f"Uploading {local_file_path} -> {blob_path} ...")
        with open(local_file_path, "rb") as data:
            container_client.upload_blob(name=blob_path, data=data, overwrite=True)

print(f"Upload complete. All files from {base_dir} are now under {azure_root_folder}/ in Azure Blob Storage.")
