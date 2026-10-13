import os
from azure.storage.blob import BlobServiceClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import os, json, glob, time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image
from tqdm import tqdm
from pathlib import Path
from azure.core.exceptions import AzureError
import time

import torch
from torch.utils.data import Dataset, DataLoader
os.environ["HF_HUB_DISABLE_XET"] = "1"

SAVE_OVERLAY = True
from transformers import (
        Mask2FormerForUniversalSegmentation,
        Mask2FormerImageProcessor,
        AutoConfig,
    )

local_download_dir = "images"
os.makedirs(local_download_dir, exist_ok=True)
connection_string = os.environ.get("CONNECTION_STRING", "")
container_name = "london"
prefix_path = "training/training/Images"
MAX_WORKERS = 8

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

# ------------------- Configuration -------------------
HF_TOKEN = os.environ.get("HF_TOKEN", None)  # e.g., "hf_xxx..."; prefer env var for safety

#MODEL_ID = os.environ.get(
#    "MODEL_ID",
#    "facebook/mask2former-swin-large-mapillary-vistas-panoptic"
#)

MODEL_ID = os.environ.get(
    "MODEL_ID",
    "facebook/mask2former-swin-large-mapillary-vistas-semantic"
)

TASK = os.environ.get("TASK", "semantic")  # "panoptic" | "semantic"
IMAGE_DIR = os.environ.get("IMAGE_DIR", "images")
#OUT_DIR   = os.environ.get("OUT_DIR", "./out_vistas_panoptic")
OUT_DIR   = os.environ.get("OUT_DIR", "./out_vistas_semantic")

BATCH_SIZE   = int(os.environ.get("BATCH_SIZE", "1"))    # bs=1 is safest on T4
NUM_WORKERS  = int(os.environ.get("NUM_WORKERS", "2"))
TARGET_H     = int(os.environ.get("TARGET_H", "640"))    # resize to 640×640 by default
TARGET_W     = int(os.environ.get("TARGET_W", "640"))
USE_COMPILE  = os.environ.get("USE_COMPILE", "0") == "1"
ALLOW_TF32   = os.environ.get("ALLOW_TF32", "1") == "1"
MAX_IMAGES   = int(os.environ.get("MAX_IMAGES", "0"))    # 0 -> process all
SAVE_OVERLAY = True

# ------------------- HF / Transformers -------------------
try:
    from huggingface_hub import login as hf_login
    from transformers import (
        Mask2FormerForUniversalSegmentation,
        Mask2FormerImageProcessor,
        AutoConfig,
    )
except Exception as e:
    print("Install deps:\n  pip install --upgrade 'transformers>=4.41' 'huggingface_hub' 'torch' 'accelerate' 'tqdm' 'Pillow'")
    raise

def to_numpy(x):
    """
    Convert x (PIL Image, numpy array, or torch Tensor possibly on CUDA)
    into a numpy array on CPU.
    """
    # lazy import here in case top-level import order matters
    import torch
    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy()
    if isinstance(x, np.ndarray):
        return x
    # PIL Image or other array-like
    return np.array(x)


def maybe_hf_login(token: Optional[str]):
    if token:
        try:
            hf_login(token=token, add_to_git_credential=False)
            print("HF: authenticated.")
        except Exception as ex:
            print(f"HF login failed: {ex}. Continuing unauthenticated...")

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def is_img(p: str) -> bool:
    return os.path.splitext(p)[1].lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"]

def list_images(folder: str) -> List[str]:
    files = [p for p in glob.glob(os.path.join(folder, "**", "*"), recursive=True) if is_img(p)]
    files.sort()
    return files

@dataclass
class ImageItem:
    path: str

class FolderDataset(Dataset):
    def __init__(self, image_paths: List[str]):
        self.items = [ImageItem(p) for p in image_paths]

    def __len__(self): return len(self.items)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.items[idx]
        im = Image.open(item.path).convert("RGB")
        return {"image": im, "path": item.path}

def default_device_dtype():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    return device, dtype

def attach_tf32():
    if torch.cuda.is_available() and ALLOW_TF32:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        print("TF32 enabled (Ampere+).")

def colorize_idmap(idmap_np: np.ndarray) -> Image.Image:
    """Deterministic hashing from ID -> RGB (for overlays)."""
    h, w = idmap_np.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    uniq = np.unique(idmap_np)
    for uid in uniq:
        if uid < 0:  # ignore void if any
            continue
        x = (int(uid) * 2654435761) & 0xFFFFFFFF
        rgb[idmap_np == uid] = [(x & 0xFF), ((x >> 8) & 0xFF), ((x >> 16) & 0xFF)]
    return Image.fromarray(rgb, "RGB")

def main():
    print("=== Mask2Former × Mapillary Vistas inference ===")
    print(f"Model:  {MODEL_ID}")
    print(f"Task:   {TASK}")
    print(f"Images: {IMAGE_DIR}")
    ensure_dir(OUT_DIR); ensure_dir(f"{OUT_DIR}/masks"); ensure_dir(f"{OUT_DIR}/json")
    ensure_dir(f"{OUT_DIR}/overlays")

    maybe_hf_login(HF_TOKEN)

    device, dtype = default_device_dtype()
    attach_tf32()

    # Load config so we can write class names in JSON
    config = AutoConfig.from_pretrained(MODEL_ID, use_auth_token=HF_TOKEN)
    id2label: Dict[int, str] = getattr(config, "id2label", {})
    label2id: Dict[str, int] = getattr(config, "label2id", {})
    print(f"Label space size: {len(id2label) or 'unknown (model will still run)'}")

    processor = Mask2FormerImageProcessor.from_pretrained(MODEL_ID, use_auth_token=HF_TOKEN)
    model = Mask2FormerForUniversalSegmentation.from_pretrained(
        MODEL_ID, torch_dtype=dtype, use_auth_token=HF_TOKEN
    ).to(device).eval()

    if USE_COMPILE and hasattr(torch, "compile"):
        try:
            model = torch.compile(model)
            print("torch.compile() active.")
        except Exception as ex:
            print(f"compile() failed: {ex}")

    all_imgs = list_images(IMAGE_DIR)
    if MAX_IMAGES > 0:
        all_imgs = all_imgs[:MAX_IMAGES]
    if not all_imgs:
        print("No images found."); return

    done = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(f"{OUT_DIR}/json/*.json")}
    todo = [p for p in all_imgs if os.path.splitext(os.path.basename(p))[0] not in done]

    ds = FolderDataset(todo)

    def collate(batch):
        pil = [b["image"] for b in batch]
        paths = [b["path"] for b in batch]
        processed = processor(
            images=pil,
            do_resize=True,
            size={"height": TARGET_H, "width": TARGET_W},
            return_tensors="pt",
        )
        orig_sizes = [im.size[::-1] for im in pil]  # (H, W)
        return {"pixel_values": processed.pixel_values, "paths": paths, "orig_sizes": orig_sizes}

    dl = DataLoader(
        ds, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, pin_memory=(device=="cuda"),
        collate_fn=collate, drop_last=False,
        persistent_workers=NUM_WORKERS > 0
    )

    start = time.perf_counter()
    n_proc = 0

    amp_dtype = torch.bfloat16 if (device=="cuda" and torch.cuda.is_bf16_supported()) else torch.float16
    autocast_ctx = torch.cuda.amp.autocast if device=="cuda" else torch.cpu.amp.autocast

    pbar = tqdm(dl, ncols=100, desc="Mapillary inference")
    with torch.inference_mode():
      for batch in pbar:
          pix = batch["pixel_values"].to(device, non_blocking=True)
          paths = batch["paths"]
          orig_sizes = batch["orig_sizes"]

          with autocast_ctx(dtype=amp_dtype) if device=="cuda" else torch.no_grad():
              outputs = model(pixel_values=pix)

          if TASK == "panoptic":
              results = processor.post_process_panoptic_segmentation(outputs, target_sizes=orig_sizes)
          elif TASK == "semantic":
              results = processor.post_process_semantic_segmentation(outputs, target_sizes=orig_sizes)
          else:
              raise ValueError("TASK must be 'panoptic' or 'semantic' for Mapillary.")

          for i, res in enumerate(results):
              in_path = paths[i]
              stem = os.path.splitext(os.path.basename(in_path))[0]

              if TASK == "panoptic":
                  segPIL = res["segmentation"]
                  segments_info = res["segments_info"]

                  seg_np = to_numpy(segPIL).astype(np.int32)

                  out_mask = Image.fromarray(seg_np.astype(np.uint16))
                  out_mask.save(f"{OUT_DIR}/masks/{stem}.png")

                  if SAVE_OVERLAY:
                      print("save overlay")
                      try:
                        color = colorize_idmap(seg_np)
                        overlay_path = os.path.join(OUT_DIR, "overlays", f"{stem}_overlay.png")
                        color.save(overlay_path)
                        if os.path.exists(overlay_path) and os.path.getsize(overlay_path) > 0:
                            print(f"Saved overlay: {overlay_path}")
                        else:
                            print(f"Overlay save reported success but file missing/empty: {overlay_path}")
                      except Exception as ex:
                          print(f"Failed to save overlay for {stem}: {ex}")

                  height, width = int(seg_np.shape[0]), int(seg_np.shape[1])

                  def name_for(lid: int) -> str:
                      if isinstance(id2label, dict):
                          return id2label.get(int(lid), id2label.get(str(lid), f"class_{lid}"))
                      return f"class_{lid}"

                  meta = {
                      "image_path": in_path,
                      "mask_path": f"{OUT_DIR}/masks/{stem}.png",
                      "model_id": MODEL_ID,
                      "task": TASK,
                      "height": height,
                      "width": width,
                      "segments_info": [
                          {
                              "id": int(s["id"]),
                              "label_id": int(s["label_id"]),
                              "label_name": name_for(int(s["label_id"])),
                              "score": float(s.get("score", 1.0)),
                              "isthing": bool(s.get("isthing", False)),
                          } for s in segments_info
                      ],
                  }
                  with open(f"{OUT_DIR}/json/{stem}.json", "w") as f:
                      json.dump(meta, f, indent=2)

              else:  # semantic
                  seg = res["segmentation"] if isinstance(res, dict) else res
                  seg_np = to_numpy(seg).astype(np.int32)
                  sem_img = Image.fromarray(seg_np.astype(np.uint16))
                  sem_img.save(f"{OUT_DIR}/masks/{stem}.png")

                  if SAVE_OVERLAY:
                      try:
                        color = colorize_idmap(seg_np)
                        overlay_path = os.path.join(OUT_DIR, "overlays", f"{stem}_overlay.png")
                        color.save(overlay_path)
                        if os.path.exists(overlay_path) and os.path.getsize(overlay_path) > 0:
                            print(f"Saved overlay: {overlay_path}")
                        else:
                            print(f"Overlay save reported success but file missing/empty: {overlay_path}")
                      except Exception as ex:
                          print(f"Failed to save overlay for {stem}: {ex}")

                  ids, cnts = np.unique(seg_np, return_counts=True)
                  id_hist = [
                      {"label_id": int(i), "label_name": id2label.get(int(i), id2label.get(str(i), f"class_{i}")), "pixels": int(c)}
                      for i, c in zip(ids, cnts)
                  ]

                  height, width = int(seg_np.shape[0]), int(seg_np.shape[1])

                  meta = {
                      "image_path": in_path,
                      "mask_path": f"{OUT_DIR}/masks/{stem}.png",
                      "model_id": MODEL_ID,
                      "task": TASK,
                      "height": height,
                      "width": width,
                      "label_histogram": id_hist,
                  }
                  with open(f"{OUT_DIR}/json/{stem}.json", "w") as f:
                      json.dump(meta, f, indent=2)

          n_proc += len(paths)

    elapsed = time.perf_counter() - start
    print(f"Processed {n_proc} images in {elapsed:.2f}s  ({n_proc/max(elapsed,1e-9):.2f} img/s)")
    print("Done.")

if __name__ == "__main__":
    main()
