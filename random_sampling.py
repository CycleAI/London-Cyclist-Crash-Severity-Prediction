"""
random_sample_metadata.py

Randomly sample points from a CSV of lat/lng (e.g. greater_london_grid_50m_full.csv).
For each sampled point, call the Google Street View metadata API (source=outdoor, radius=radius).
If metadata.status == "OK", save the metadata JSON into Azure Blob Storage under:
  <container>/<prefix>/RandomSamplingMetadata/<sequential>_<point_idx>.json
Also save a local copy in ./RandomSamplingMetadata/.

Uses a checkpoint file 'random_sampling_checkpoint.json' to resume safely.

Requirements:
  pip install requests azure-storage-blob tqdm
"""
!pip install requests azure-storage-blob tqdm
import os
import csv
import json
import time
import random
import logging
from urllib.parse import urlencode
from typing import List, Tuple
import requests
from tqdm import tqdm
from azure.storage.blob import BlobServiceClient, ContentSettings

# -----------------------
# USER CONFIG (edit as needed)
# -----------------------
street_view_api_key = os.environ.get("STREET_VIEW_API_KEY", "api_key")
azure_api_key = os.environ.get("AZURE_STORAGE_CONN_STR", "conn_string")
blob_path = ".../london/training"           # "<container>/<optional/prefix>"
locations_csv = "greater_london_grid_50m_full.csv"
radius = 50                                # meters (search radius for metadata)
source = "outdoor"
target_count = 5000                      # number of metadata hits to collect
request_timeout = 30
max_retries = 3
angles = [0, 90, 180, 270]  # headings (degrees) to check per point
pitch = 0
user_agent = "sv-random-sampler/1.0"

# Checkpoint + local metadata folder
checkpoint_local = "random_sampling_checkpoint.json"
local_meta_folder = "RandomSamplingMetadata"   # local folder for metadata jsons

# Azure blob folders (under prefix)
remote_meta_folder = "RandomSamplingMetadata"

# -----------------------
# logging
# -----------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("random_sampler")

# -----------------------
# Helpers: load CSV points
# -----------------------
def load_locations_from_csv(path: str) -> List[Tuple[float, float]]:
    locs = []
    with open(path, newline="", encoding="utf-8") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        sniffer = csv.Sniffer()
        has_header = False
        try:
            has_header = sniffer.has_header(sample)
        except Exception:
            has_header = False

        if has_header:
            fh.seek(0)
            dreader = csv.DictReader(fh)
            # normalize names
            fieldmap = {name.lower(): name for name in dreader.fieldnames if name}
            lat_key = fieldmap.get("lat") or fieldmap.get("latitude") or None
            lon_key = fieldmap.get("lon") or fieldmap.get("lng") or fieldmap.get("longitude") or None
            if lat_key and lon_key:
                for row in dreader:
                    try:
                        lat = float(row[lat_key]); lon = float(row[lon_key])
                        locs.append((lat, lon))
                    except Exception:
                        continue
            else:
                # fallback to positional after header
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
            fh.seek(0)
            reader = csv.reader(fh)
            for cols in reader:
                if len(cols) >= 2:
                    try:
                        lat = float(cols[0]); lon = float(cols[1])
                        locs.append((lat, lon))
                    except Exception:
                        continue
    return locs

# -----------------------
# Azure helpers (same style as earlier)
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
    logger.info("Created container: %s", container_name)
except Exception:
    logger.debug("Container may already exist (continuing).")

def upload_text_to_blob(text: str, blob_rel_path: str, content_type="application/json"):
    blob_client = container_client.get_blob_client(blob_rel_path)
    blob_client.upload_blob(text.encode("utf-8"), overwrite=True, content_settings=ContentSettings(content_type=content_type))

# -----------------------
# Google Street View metadata helpers
# -----------------------
METADATA_BASE = "https://maps.googleapis.com/maps/api/streetview/metadata"

def build_metadata_url(lat: float, lng: float, radius: int = None, source: str = "outdoor"):
    r = int(radius) if radius is not None else int(globals().get("radius", 50))
    params = {"location": f"{lat},{lng}", "radius": r, "key": street_view_api_key, "source": source}
    return f"{METADATA_BASE}?{urlencode(params)}"

def fetch_metadata(lat: float, lng: float, radius: int = None, retries: int = max_retries):
    url = build_metadata_url(lat, lng, radius=radius, source=source)
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

# -----------------------
# Checkpoint management
# -----------------------
def load_checkpoint():
    if os.path.exists(checkpoint_local):
        try:
            with open(checkpoint_local, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            logger.exception("Failed reading checkpoint; starting fresh.")
    # structure:
    # {
    #   "collected": { "<point_idx>": "<remote_blob_rel>" },
    #   "count": int
    # }
    return {"collected": {}, "count": 0}
def save_checkpoint(cp):
    with open(checkpoint_local, "w", encoding="utf-8") as fh:
        json.dump(cp, fh, indent=2)
    # also upload checkpoint to blob (best-effort)
    try:
        blob_rel = f"{prefix}/checkpoint/{checkpoint_local}" if prefix else f"checkpoint/{checkpoint_local}"
        upload_text_to_blob(json.dumps(cp), blob_rel)
    except Exception:
        logger.exception("Failed to upload checkpoint to blob (continuing).")

# -----------------------
# Main sampling routine
# -----------------------
def load_checkpoint():
    if os.path.exists(checkpoint_local):
        try:
            with open(checkpoint_local, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            logger.exception("Failed reading checkpoint; starting fresh.")
    # structure:
    # {
    #   "collected": { "<point_idx>": "<remote_blob_rel>" },
    #   "count": int
    # }
    return {"collected": {}, "count": 0}


def main():
    os.makedirs(local_meta_folder, exist_ok=True)
    locs = load_locations_from_csv(locations_csv)
    total_points = len(locs)
    if total_points == 0:
        raise SystemExit("No locations loaded from CSV.")

    logger.info("Loaded %d points from CSV.", total_points)
    cp = load_checkpoint()
    collected_count = int(cp.get("count", 0))
    collected_set = set(cp.get("collected", {}).keys())  # keys like "123"

    logger.info("Already collected %d metadata entries according to checkpoint.", collected_count)

    all_indices = list(range(total_points))
    remaining_indices = [i for i in all_indices if str(i) not in collected_set]
    random.shuffle(remaining_indices)

    pbar = tqdm(total=target_count, initial=collected_count, desc="metadata collected")

    i = 0
    while collected_count < target_count:
        if i >= len(remaining_indices):
            # reshuffle remaining
            remaining_indices = [idx for idx in all_indices if str(idx) not in collected_set]
            if not remaining_indices:
                logger.warning("No more uncollected points available; stopping early at %d collected.", collected_count)
                break
            random.shuffle(remaining_indices)
            i = 0

        point_idx = remaining_indices[i]
        i += 1
        lat, lng = locs[point_idx]

        # metadata request
        try:
            md = fetch_metadata(lat, lng, radius=radius)
        except Exception as e:
            logger.debug("Metadata fetch error for idx %d: %s", point_idx, e)
            continue

        if md.get("status") != "OK":
            continue

        seq = collected_count  # sequential number for naming
        rec = {
            "seq": seq,
            "point_idx": point_idx,
            "lat": lat,
            "lng": lng,
            "radius": radius,
            "source": source,
            "metadata_response": md,
            "saved_at": time.time()
        }

        # save locally
        local_name = os.path.join(local_meta_folder, f"{point_idx}.json")
        try:
            with open(local_name, "w", encoding="utf-8") as fh:
                json.dump(rec, fh, indent=2)
        except Exception:
            logger.exception("Failed to write local metadata %s (continuing).", local_name)
            continue

        # save remotely
        blob_rel = f"{prefix}/{remote_meta_folder}/{point_idx}.json" if prefix else f"{remote_meta_folder}/{point_idx}.json"
        try:
            upload_text_to_blob(json.dumps(rec, indent=2), blob_rel)
        except Exception as e:
            logger.exception("Failed to upload metadata blob for idx %d: %s", point_idx, e)
            continue

        # update checkpoint
        cp["collected"][str(point_idx)] = blob_rel
        collected_count += 1
        cp["count"] = collected_count
        save_checkpoint(cp)

        pbar.update(1)

        if collected_count >= target_count:
            break

    pbar.close()
    logger.info("Finished sampling. collected=%d", collected_count)

if __name__ == "__main__":
    main()
