import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError
from tqdm import tqdm
import time

CONN_STR = os.environ.get("AZ_CONN_STR")
CONTAINER = "london"
BASE_DIR = Path("local_path")
AZURE_ROOT = "root_folder_to_upload_in_zure"

MAX_WORKERS = 6
UPLOAD_MAX_CONCURRENCY = 2
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
