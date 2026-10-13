"""
streetview_outdoor_to_azure.py

- Uses Google Street View Static API metadata endpoint with source=outdoor to
  detect outdoor panoramas (metadata calls are free / no image quota).
- Downloads the image only when metadata returns OK (i.e. an outdoor panorama).
- Uploads image to Azure Blob Storage under Images/
  and metadata under Metadata/
- Keeps a checkpoint (local and uploaded to blob) so you can resume safely from Colab.
- Names image blobs as: {index}_{heading}.jpg  (e.g. 0_90.jpg)

Requirements:
  pip install requests azure-storage-blob tqdm
  (Optional: tqdm for progress display)
Notes:
  - Google metadata requests do not consume image quota. Images do consume quota.
  - The "source=outdoor" filter is the documented way to prefer outdoor collections,
    but Google has reported some edge-case issues where indoor images still return.
"""

!pip install requests azure-storage-blob tqdm
import os
import io
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
from typing import List, Tuple
import requests
from azure.storage.blob import BlobServiceClient, ContentSettings
from tqdm import tqdm

# -----------------------
# USER CONFIG
# -----------------------
# Required
street_view_api_key = os.environ.get("STREET_VIEW_API_KEY", "api_key")
azure_api_key = os.environ.get("AZURE_STORAGE_CONN_STR", "conn")
blob_path = ".../london"
angles = [0, 90, 180, 270]                      # headings (degrees)
pitch = 0                                       # orientation from the ground (-90..90)

radius = 50

locations_csv = "greater_london_grid_50m_full.csv"

def load_locations_from_csv(path):
    """
    Reads CSV and returns a list of (lat, lng) tuples.
    Accepts:
      - CSV with headers 'lat' and 'lon' (case-insensitive)
      - CSV with two columns and no header (lat first, lon second)
    """
    import csv
    locs = []
    with open(path, newline="", encoding="utf-8") as fh:
        sample = fh.read(2048)
        fh.seek(0)
        sniffer = csv.Sniffer()
        has_header = False
        try:
            has_header = sniffer.has_header(sample)
        except Exception:
            has_header = False

        reader = csv.reader(fh)
        if has_header:
            fh.seek(0)
            dreader = csv.DictReader(fh)
            fieldmap = {name.lower(): name for name in dreader.fieldnames if name}
            lat_key = fieldmap.get("lat") or fieldmap.get("latitude") or None
            lon_key = fieldmap.get("lon") or fieldmap.get("lng") or fieldmap.get("longitude") or None
            if lat_key and lon_key:
                for row in dreader:
                    try:
                        lat = float(row[lat_key])
                        lon = float(row[lon_key])
                        locs.append((lat, lon))
                    except Exception:
                        continue
            else:
                fh.seek(0)
                reader2 = csv.reader(fh)
                next(reader2, None)
                for cols in reader2:
                    if len(cols) >= 2:
                        try:
                            lat = float(cols[0]); lon = float(cols[1])
                            locs.append((lat, lon))
                        except Exception:
                            continue
        else:
            for cols in reader:
                if len(cols) >= 2:
                    try:
                        lat = float(cols[0]); lon = float(cols[1])
                        locs.append((lat, lon))
                    except Exception:
                        continue
    return locs


locations = load_locations_from_csv(locations_csv)

# -----------------------
# Logging
# -----------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("sv_outdoor")

logger.info("Loaded %d locations from %s", len(locations), locations_csv)

size = "640x640"
fov = 90
concurrency = 16
request_timeout = 30
max_retries = 3
user_agent = "sv-outdoor-uploader/1.0"

# Checkpoint: filename stored locally and mirrored to blob storage
checkpoint_local = "sv_checkpoint.json"
checkpoint_blob_name = "checkpoint/sv_checkpoint.json"  # stored under blob_path prefix

# Where (inside blob_path) to put images and metadata
images_folder = "Images"
metadata_folder = "Metadata"



# -----------------------
# Azure helpers
# -----------------------
def make_blob_service_client(azure_key: str) -> BlobServiceClient:
    if azure_key is None:
        raise ValueError("azure_api_key not provided")
    if azure_key.startswith("DefaultEndpointsProtocol=") or "AccountName=" in azure_key:
        return BlobServiceClient.from_connection_string(azure_key)
    if azure_key.startswith("https://") and "sv=" in azure_key:
        account_url = azure_key.split("?", 1)[0]
        sas_token = azure_key.split("?", 1)[1]
        return BlobServiceClient(account_url=account_url, credential=sas_token)
    if ":" in azure_key and len(azure_key.split(":", 1)[1]) > 8:
        account, key = azure_key.split(":", 1)
        conn_str = f"DefaultEndpointsProtocol=https;AccountName={account};AccountKey={key};EndpointSuffix=core.windows.net"
        return BlobServiceClient.from_connection_string(conn_str)
    raise ValueError("Unrecognized azure_api_key format. Provide connection string, SAS URL, or account:account_key")

blob_service = make_blob_service_client(azure_api_key)
container_name, *rest = blob_path.split("/", 1)
prefix = rest[0].rstrip("/") if rest else ""
container_client = blob_service.get_container_client(container_name)
try:
    container_client.create_container()
    logger.info(f"Created container: {container_name}")
except Exception:
    logger.debug("Container may already exist (continuing).")

def upload_bytes_to_blob(data: bytes, blob_rel_path: str, content_type="image/jpeg"):
    """
    blob_rel_path is relative to the container root, e.g. "prefix/Images/0_90.jpg"
    """
    blob_client = container_client.get_blob_client(blob_rel_path)
    blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))

def download_blob_to_bytes(blob_rel_path: str) -> bytes:
    blob_client = container_client.get_blob_client(blob_rel_path)
    try:
        resp = blob_client.download_blob()
        return resp.readall()
    except Exception:
        return None

def upload_text_to_blob(text: str, blob_rel_path: str, content_type="application/json"):
    upload_bytes_to_blob(text.encode("utf-8"), blob_rel_path, content_type=content_type)

# -----------------------
# Google Street View helpers
# -----------------------
METADATA_BASE = "https://maps.googleapis.com/maps/api/streetview/metadata"
IMAGE_BASE = "https://maps.googleapis.com/maps/api/streetview"

def build_metadata_url(lat: float, lng: float, radius: int = 50, source: str = "outdoor"):
    """
    Build metadata URL.
      - source=outdoor asks Google to limit searches to outdoor collections.
      - metadata requests are free / do not consume image quota.
    """
    params = {"location": f"{lat},{lng}", "radius": radius, "key": street_view_api_key, "source": source}
    return f"{METADATA_BASE}?{urlencode(params)}"

def build_image_url_by_location(lat: float, lng: float, heading: int, pitch: int, size: str, fov: int, source: str = "outdoor"):
    params = {
        "size": size,
        "location": f"{lat},{lng}",
        "heading": int(heading),
        "pitch": int(pitch),
        "fov": int(fov),
        "key": street_view_api_key,
        "source": source
    }
    return f"{IMAGE_BASE}?{urlencode(params)}"

# Note: some docs mention a pano parameter; historically behavior varied.
# Using location + source=outdoor + heading/pitch is robust and supported.

def fetch_metadata(lat: float, lng: float, radius: int = 50, retries: int = max_retries):
    url = build_metadata_url(lat, lng, radius=radius)
    headers = {"User-Agent": user_agent}
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=request_timeout)
            if r.status_code == 200:
                return r.json()
            last_exc = Exception(f"HTTP {r.status_code}")
        except Exception as e:
            last_exc = e
        time.sleep(1.5 ** attempt)
    raise last_exc

def fetch_image_bytes(url: str, retries: int = max_retries) -> bytes:
    headers = {"User-Agent": user_agent}
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=request_timeout)
            if r.status_code == 200 and r.content:
                return r.content
            last_exc = Exception(f"HTTP {r.status_code}")
        except Exception as e:
            last_exc = e
        time.sleep(1.5 ** attempt)
    raise last_exc

# -----------------------
# Checkpoint helpers (local + blob)
# -----------------------
def load_checkpoint() -> dict:
    """
    Attempt to load checkpoint from blob first (if available), else local.
    Checkpoint format:
      {
        "processed": {
           "<task_key>": {"image_blob": "<relpath>", "metadata_blob": "<relpath>", "timestamp": "..."}
        },
        "next_index": int
      }
    task_key example: "lat,lng,heading,pitch"
    """
    # Try download from blob (best for Colab/resume across machines)
    if checkpoint_blob_name:
        blob_rel = f"{prefix}/{checkpoint_blob_name}" if prefix else checkpoint_blob_name
        try:
            b = download_blob_to_bytes(blob_rel)
            if b:
                logger.info("Loaded checkpoint from blob: %s", blob_rel)
                return json.loads(b.decode("utf-8"))
        except Exception:
            logger.debug("No checkpoint found in blob or failed to download.")
    # Fallback: local file
    if os.path.exists(checkpoint_local):
        try:
            with open(checkpoint_local, "r", encoding="utf-8") as fh:
                logger.info("Loaded local checkpoint: %s", checkpoint_local)
                return json.load(fh)
        except Exception:
            logger.exception("Failed to read local checkpoint; starting fresh.")
    # Default empty checkpoint
    return {"processed": {}, "next_index": 0}

def save_checkpoint(checkpoint: dict):
    # write local copy
    with open(checkpoint_local, "w", encoding="utf-8") as fh:
        json.dump(checkpoint, fh, indent=2)
    # upload to blob (best-effort)
    if checkpoint_blob_name:
        try:
            blob_rel = f"{prefix}/{checkpoint_blob_name}" if prefix else checkpoint_blob_name
            upload_text_to_blob(json.dumps(checkpoint), blob_rel)
            logger.debug("Uploaded checkpoint to blob: %s", blob_rel)
        except Exception:
            logger.exception("Failed to upload checkpoint to blob (continuing).")

# -----------------------
# Task building & processing
# -----------------------
def load_locations(loc_input) -> List[Tuple[float, float]]:
    if isinstance(loc_input, str) and os.path.exists(loc_input):
        locs = []
        with open(loc_input, "r", encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                parts = s.replace(",", " ").split()
                try:
                    lat = float(parts[0]); lng = float(parts[1])
                    locs.append((lat, lng))
                except:
                    continue
        return locs
    elif isinstance(loc_input, list):
        return loc_input
    else:
        raise ValueError("locations must be list[(lat,lng)] or path to CSV-like file")

def task_key(lat, lng, heading, pitch):
    return f"{lat:.6f},{lng:.6f},h{int(heading)},p{int(pitch)}"

def process_one_task(point_idx, lat, lng, heading, pitch, checkpoint) -> tuple:
    """
    - Check metadata (source=outdoor)
    - If metadata status != OK -> skip
    - If OK -> download image, upload image blob and metadata json blob, update checkpoint
    Returns (saved:bool, reason:str)
    """
    key = task_key(lat, lng, heading, pitch)
    if key in checkpoint["processed"]:
        return False, "already_processed"

    # 1) metadata (free)
    try:
        md = fetch_metadata(lat, lng, radius=radius)
    except Exception as e:
        logger.warning("Metadata request failed for %s: %s", key, e)
        return False, "metadata_failed"

    status = md.get("status")
    if status != "OK":
        # Could be ZERO_RESULTS / NOT_FOUND / etc. Skip.
        return False, f"metadata_status_{status}"

    # At this point metadata OK with source=outdoor means Google has an outdoor panorama candidate.
    # 2) download image (this consumes image quota/billing)
    img_url = build_image_url_by_location(lat, lng, heading, pitch, size, fov)
    try:
        img_bytes = fetch_image_bytes(img_url)
    except Exception as e:
        logger.warning("Image download failed for %s: %s", key, e)
        return False, "image_download_failed"

    # 3) Compose blob names and upload
    cur_index = checkpoint["next_index"]
    image_filename = f"{point_idx}_{int(heading)}.jpg"
    metadata_filename = f"{point_idx}_{int(heading)}.json"

    image_blob_rel = f"{prefix}/{images_folder}/{image_filename}" if prefix else f"{images_folder}/{image_filename}"
    metadata_blob_rel = f"{prefix}/{metadata_folder}/{metadata_filename}" if prefix else f"{metadata_folder}/{metadata_filename}"

    # Upload image
    try:
        upload_bytes_to_blob(img_bytes, image_blob_rel, content_type="image/jpeg")
    except Exception as e:
        logger.exception("Failed to upload image blob for %s: %s", key, e)
        return False, "upload_image_failed"

    # Prepare metadata object to save (include original metadata + requested params + source tag)
    md_record = {
        "requested": {"lat": lat, "lng": lng, "heading": int(heading), "pitch": int(pitch), "size": size, "fov": fov},
        "metadata_response": md,
        "image_blob": image_blob_rel,
        "image_filename": image_filename,
        "stored_at": time.time()
    }
    try:
        upload_text_to_blob(json.dumps(md_record, indent=2), metadata_blob_rel, content_type="application/json")
    except Exception as e:
        logger.exception("Failed to upload metadata blob for %s: %s", key, e)
        # (we have uploaded image, but metadata upload failed) still mark as processed to avoid re-downloading repeatedly.
        checkpoint["processed"][key] = {"image_blob": image_blob_rel, "metadata_blob": None, "reason": "metadata_upload_failed"}
        checkpoint["next_index"] = cur_index + 1
        save_checkpoint(checkpoint)
        return True, "uploaded_image_metadata_upload_failed"

    # 4) update checkpoint and increment index
    checkpoint["processed"][key] = {"image_blob": image_blob_rel, "metadata_blob": metadata_blob_rel, "timestamp": time.time()}
    checkpoint["next_index"] = cur_index + 1
    save_checkpoint(checkpoint)

    return True, "uploaded"

# -----------------------
# Main
# -----------------------
def main(max_images: int = None):
    checkpoint = load_checkpoint()

    locs = load_locations(locations)
    if not locs:
        raise SystemExit("No locations provided. Edit the `locations_csv` or provide CSV path.")

    saved_count = checkpoint.get("next_index", 0)
    logger.info("Starting. Already saved images according to checkpoint: %d", saved_count)

    # Build tasks with explicit point_idx
    tasks = []
    for point_idx, (lat, lng) in enumerate(locs):
        for heading in angles:
            tasks.append((point_idx, lat, lng, heading, pitch))

    logger.info("Prepared %d tasks to check (all locations × headings).", len(tasks))

    from tqdm import tqdm
    pbar = tqdm(total=len(tasks), desc="tasks")

    for (point_idx, lat, lng, heading, p) in tasks:
        if max_images is not None and checkpoint.get("next_index", 0) >= max_images:
            logger.info("Reached max_images=%d, stopping.", max_images)
            break

        try:
            saved, reason = process_one_task(
                point_idx, lat, lng, heading, p,
                checkpoint
            )
            if saved:
                logger.info(
                    "Saved image for point=%d (lat=%s, lng=%s, h=%s) -> %s  (total_saved=%d)",
                    point_idx, lat, lng, heading, reason,
                    checkpoint.get("next_index", 0)
                )
            else:
                logger.debug("Skipped point=%d (lat=%s, lng=%s, h=%s) -> %s",
                             point_idx, lat, lng, heading, reason)
        except Exception as e:
            logger.exception("Task error for point=%d (lat=%s, lng=%s, h=%s): %s",
                             point_idx, lat, lng, heading, e)
        finally:
            pbar.update(1)

    pbar.close()
    logger.info("Done. total_saved=%d", checkpoint.get("next_index", 0))


if __name__ == "__main__":
    main()
