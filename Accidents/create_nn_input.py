"""
Feature Extraction Pipeline for Street-Level Images

This script builds a feature dataset by combining semantic segmentation,
object detection, and image-level statistics for a collection of street
images stored in Azure Blob Storage.

Pipeline overview:
1. Connect to Azure Blob Storage.
2. Download semantic segmentation JSON files and extract per-class pixel
   proportions.
3. Download YOLO object detection outputs and extract:
   - summed detection confidences,
   - object counts,
   - summed bounding box areas.
4. Download precomputed image statistics.
5. Merge all extracted features into a single dataframe for each configured
   object detection confidence threshold.
6. Fill missing features with zeros and export the processed datasets as CSV files.

The resulting feature tables are intended for downstream machine learning
and statistical analysis.

Dependencies:
- Azure Blob Storage
- pandas
- numpy
- OpenCV
- scikit-image
- matplotlib
- tqdm
"""
import pandas as pd
import numpy as np
import json
import os
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import io
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

import cv2
from skimage import color, filters

try:
    from azure.storage.blob import BlobServiceClient, ContainerClient
    from io import BytesIO
except ImportError:
    class BlobServiceClient: pass
    class ContainerClient: pass
    class BytesIO: pass
    print("Warning: azure-storage-blob is not installed. Azure download logic will not execute until installed and credentials are set.")


# --- Project Configuration ---
CSV_FILE_NAME = "ai_rank_gpt.csv"

CONNECTION_STRING = AZURE_CONNECTION_STRING
CONTAINER_NAME = "london"
SEGMENTATION_FOLDER = "SemanticSegmentation/json/" # Ensure trailing slash
DETECTION_ROOT = "YoloV10/"
CONFIDENCE_LEVELS = [0.5]

# Placeholder for the complete set of Image IDs (19995 total)
NUM_IMAGES = 19995
IMAGE_IDS = [f"{i}_{angle}.jpg" for i in range(NUM_IMAGES // 4 + 1) for angle in [0, 90, 180, 270]][:NUM_IMAGES]

SEG_FULL_CLASSES = [
    'Banner', 'Barrier', 'Bench', 'Bicycle', 'Bicyclist',
    'Bike Lane', 'Bike Rack', 'Billboard', 'Bird', 'Boat',
    'Bridge', 'Building', 'Bus', 'CCTV Camera', 'Car',
    'Car Mount', 'Caravan', 'Catch Basin', 'Crosswalk - Plain',
    'Curb', 'Curb Cut', 'Ego Vehicle', 'Fence', 'Fire Hydrant',
    'Ground Animal', 'Guard Rail', 'Junction Box',
    'Lane Marking - Crosswalk', 'Lane Marking - General',
    'Mailbox', 'Manhole', 'Motorcycle', 'Motorcyclist',
    'Mountain', 'On Rails', 'Other Rider', 'Other Vehicle',
    'Parking', 'Pedestrian Area', 'Person', 'Phone Booth',
    'Pole', 'Pothole', 'Rail Track', 'Road', 'Sand',
    'Service Lane', 'Sidewalk', 'Sky', 'Snow', 'Street Light',
    'Terrain', 'Traffic Light', 'Traffic Sign (Back)',
    'Traffic Sign (Front)', 'Traffic Sign Frame', 'Trailer',
    'Trash Can', 'Truck', 'Tunnel', 'Utility Pole', 'Vegetation',
    'Wall', 'Water', 'Wheeled Slow'
]
OBJ_FULL_CLASSES = [
    'Person', 'Bicycle', 'Car', 'Motorcycle', 'Airplane', 'Bus', 'Train', 'Truck', 'Boat', 'Traffic Light',
    'Fire Hydrant', 'Stop Sign', 'Parking Meter', 'Bench', 'Bird', 'Cat', 'Dog', 'Horse', 'Sheep', 'Cow',
    'Elephant', 'Bear', 'Zebra', 'Giraffe', 'Backpack', 'Umbrella', 'Handbag', 'Tie', 'Suitcase', 'Frisbee',
    'Skis', 'Snowboard', 'Sports Ball', 'Kite', 'Baseball Bat', 'Baseball Glove', 'Skateboard', 'Surfboard',
    'Tennis Racket', 'Bottle', 'Wine Glass', 'Cup', 'Fork', 'Knife', 'Spoon', 'Bowl', 'Banana', 'Apple',
    'Sandwich', 'Orange', 'Broccoli', 'Carrot', 'Hot Dog', 'Pizza', 'Donut', 'Cake', 'Chair', 'Couch',
    'Potted Plant', 'Bed', 'Dining Table', 'Toilet', 'Tv', 'Laptop', 'Mouse', 'Remote', 'Keyboard',
    'Cell Phone', 'Microwave', 'Oven', 'Toaster', 'Sink', 'Refrigerator', 'Book', 'Clock', 'Vase',
    'Scissors', 'Teddy Bear', 'Hair Drier', 'Toothbrush'
]

# --- Step 2 Required Class Selection ---
SELECTED_SEG_CLASSES = SEG_FULL_CLASSES
SELECTED_OBJ_CLASSES = OBJ_FULL_CLASSES

# --- Helper Functions for Parsing --

def parse_image_stats(json_content: str) -> Dict[str, float]:
    """Parse image statistics JSON."""
    try:
        data = json.loads(json_content)

        # remove metadata fields
        data.pop("_source_blob", None)

        return data
    except Exception as e:
        print(f"Error parsing image stats JSON: {e}")
        return {}


def parse_segmentation(json_content: str) -> Dict[str, float]:
    """Parses segmentation JSON content and returns a dictionary of class names to pixel percentages."""
    try:
        data = json.loads(json_content)
        features = {}
        # Assuming a fixed image size like 640x640, or use the provided dimensions
        total_pixels = data.get('height', 640) * data.get('width', 640)

        for entry in data.get('label_histogram', []):
            # Store pixel percentage relative to the image size
            features[entry['label_name']] = entry['pixels'] / total_pixels
        return features
    except Exception as e:
        print(f"Error parsing segmentation JSON: {e}")
        return {}

def parse_yolo(txt_content: str, min_confidence: float = 0.5) -> Dict[str, float]:
    """Parses YOLO TXT content and returns a dictionary of object class summed confidences (probabilities)
    and summed bbox areas per class (if width/height are present)."""
    try:
        lines = txt_content.strip().split('\n')
        class_probs = {}
        for line in lines:
            parts = line.split()
            if not parts:
                continue
            # YOLO format assumed: class_id confidence x_center y_center width height
            class_id = int(parts[0])
            if len(parts) > 1:
                try:
                    conf = float(parts[1])
                except ValueError:
                    conf = 0.0
            else:
                conf = 0.0

            # apply a minimum confidence filter (safeguard)
            if conf < min_confidence:
                continue

            # map ID to class name
            if class_id < len(OBJ_FULL_CLASSES):
                class_name = OBJ_FULL_CLASSES[class_id]

                # sum confidences (existing behavior)
                class_probs[class_name] = class_probs.get(class_name, 0.0) + conf
                count_key = f"{class_name}_count"
                class_probs[count_key] = class_probs.get(count_key, 0.0) + 1.0

                # compute bbox area if width & height present (YOLO standard positions 4 and 5)
                if len(parts) >= 6:
                    try:
                        width = float(parts[4])
                        height = float(parts[5])
                        area = max(0.0, width * height)
                    except Exception:
                        area = 0.0
                    area_key = f"{class_name}_area"
                    class_probs[area_key] = class_probs.get(area_key, 0.0) + area

        return class_probs
    except Exception as e:
        print(f"Error parsing YOLO TXT: {e}")
        return {}

MAX_WORKERS = 32


def download_image_statistics(container_client):
    """Download image statistics JSON files and return a dataframe."""

    print("\n[Extra] Downloading Image Statistics...")

    blob_items = list(container_client.list_blobs(
        name_starts_with=IMAGE_STATS_FOLDER,
        results_per_page=1000
    ).by_page())

    blob_items = [blob for page in blob_items for blob in page]

    rows = []

    def process_blob(blob_item):
        try:
            blob_name = blob_item.name
            if not blob_name.endswith(".json"):
                return None

            blob_client = container_client.get_blob_client(blob_name)
            content = blob_client.download_blob().readall().decode("utf-8")

            stats = parse_image_stats(content)

            blob_base = os.path.splitext(os.path.basename(blob_name))[0]
            blob_base = blob_base.replace("_statistics", "")
            image_id = blob_base + ".jpg"

            stats["image_name"] = image_id
            return stats
        except:
            return None

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_blob, b) for b in blob_items]

        for f in tqdm(futures, desc="Downloading Image Stats"):
            r = f.result()
            if r:
                rows.append(r)

    df = pd.DataFrame(rows).set_index("image_name")

    return df

def download_and_process_blob(blob_item, container_client, is_segmentation: bool):
    """Downloads, reads, and parses a single blob item. Returns (image_id, features) or None on error."""
    try:
        blob_name = blob_item['name'] # Use the name from the blob dictionary/item

        blob_client = container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        content = download_stream.readall().decode('utf-8')

        if is_segmentation:
            if not blob_name.endswith('.json'): return None
            blob_base = os.path.splitext(os.path.basename(blob_name))[0]
            image_id = blob_base + '.jpg'
            features = parse_segmentation(content)
            prefixed_features = {f"seg_{k}": v for k, v in features.items()}
        else:
            if not blob_name.endswith('.txt'): return None
            blob_base = os.path.splitext(os.path.basename(blob_name))[0]
            image_id = blob_base + '.jpg'
            features = parse_yolo(content)
            prefixed_features = {f"obj_{k}": v for k, v in features.items()}

        if image_id not in IMAGE_IDS:
            return None

        return (image_id, prefixed_features)

    except Exception as e:
        return None

# --- Step 1: Download and Combine Logic ---

def download_and_combine_data() -> Dict[str, pd.DataFrame]:
    """
    Connects to Azure Blob Storage, downloads segmentation and object detection
    data for all confidence levels using parallel processing, and combines them.
    """
    print("--- Step 1: Connecting to Azure and Downloading All Blobs (Parallelized) ---")

    CONNECTION_STRING = ""

    try:
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    except Exception as e:
        raise ConnectionError(f"Failed to connect to Azure: {e}")

    # Initialize a master map to store all features for all images
    feature_map = {image_id: {} for image_id in IMAGE_IDS}

    # 1. Process Segmentation Data (Consistent across all confidence levels)
    print("\n[1/2] Processing Semantic Segmentation Data (JSON files)...")

    # Efficiently list all relevant segmentation blobs
    seg_blob_items = list(container_client.list_blobs(name_starts_with=SEGMENTATION_FOLDER, results_per_page=1000).by_page())
    seg_blob_items = [blob for page in seg_blob_items for blob in page] # Flatten list of pages

    seg_tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for blob_item in seg_blob_items:
            seg_tasks.append(executor.submit(download_and_process_blob, blob_item, container_client, True))

        for future in tqdm(seg_tasks, desc="Downloading Segmentation (Parallel)"):
            result = future.result()
            if result:
                image_id, features = result
                feature_map[image_id].update(features)


    # 2. Process Object Detection Data for all 3 confidence levels
    all_dataframes = {}

    print("\n[2/2] Processing Object Detection (YOLO) Data (TXT files) for 3 Confidence Levels...")

    for conf in CONFIDENCE_LEVELS:
        conf_str = f"{conf:.1f}"
        detection_folder = f"{DETECTION_ROOT}conf_{conf_str}/labels/"

        # List all relevant detection blobs
        obj_blob_items = list(container_client.list_blobs(name_starts_with=detection_folder, results_per_page=1000).by_page())
        obj_blob_items = [blob for page in obj_blob_items for blob in page]

        current_conf_features = {img_id: feature_map[img_id].copy() for img_id in IMAGE_IDS}

        obj_tasks = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for blob_item in obj_blob_items:
                obj_tasks.append(executor.submit(download_and_process_blob, blob_item, container_client, False))

            for future in tqdm(obj_tasks, desc=f"Downloading YOLO {conf_str} (Parallel)"):
                result = future.result()
                if result:
                    image_id, features = result
                    current_conf_features[image_id].update(features)


        # Convert the map for this confidence level into a DataFrame
        data_rows = []
        for img_id, features in current_conf_features.items():
            row = {'image_name': img_id}
            row.update(features)
            data_rows.append(row)

        df = pd.DataFrame(data_rows).set_index('image_name')

        # Define all expected columns for consistent zero-filling
        seg_cols_full = [f"seg_{cls}" for cls in SEG_FULL_CLASSES]
        obj_cols_full = []
        for cls in OBJ_FULL_CLASSES:
            obj_cols_full.append(f"obj_{cls}")
            obj_cols_full.append(f"obj_{cls}_count")
            obj_cols_full.append(f"obj_{cls}_area")

        all_cols_full = seg_cols_full + obj_cols_full

        # Ensure all possible columns exist and fill NaN (from missing entries) with 0.0
        df = df.reindex(columns=all_cols_full, fill_value=0.0)

        all_dataframes[f'conf_{conf_str}'] = df
        print(f"DataFrame for confidence {conf_str} created. Shape: {df.shape}")

    return all_dataframes


# --- Step 2: Process Feature Selection ---

def process_feature_selection(data_frames: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Return the dataframes unchanged so all segmentation and object-detection columns are kept."""
    print("\n--- Step 2: Feature Selection (kept ALL columns) ---")

    processed_dfs = {}
    for name, df in data_frames.items():
        # keep everything as-is (make a copy to avoid side-effects)
        processed_dfs[name] = df.copy()
        print(f"DataFrame {name} kept all columns. Final Feature Count: {df.shape[1]}")

    return processed_dfs

IMAGE_STATS_FOLDER = "ImageStatistics/"

def extract_image_features(image_ids):
    rows = []

    for img_id in tqdm(image_ids, desc="Computing image features"):
        img_path = os.path.join(IMAGE_FOLDER, img_id)

        try:
            feats = compute_image_features(img_path)
            feats["image_name"] = img_id
            rows.append(feats)
        except Exception:
            # if image missing or error → fill zeros
            rows.append({"image_name": img_id})

    df = pd.DataFrame(rows).set_index("image_name")
    return df

def compute_image_features(image_path):
    # Load image
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise ValueError(f"Image not found: {image_path}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    features = {}

    ## ---------------- Luminance ----------------
    lum = img_gray.astype(np.float32)
    features['luminance_mean'] = np.mean(lum)
    features['luminance_std'] = np.std(lum)
    features['luminance_p05'] = np.percentile(lum, 5)
    features['luminance_p50'] = np.percentile(lum, 50)
    features['luminance_p95'] = np.percentile(lum, 95)
    features['dynamic_range'] = lum.max() - lum.min()
    features['frac_dark'] = np.mean(lum < 50)
    features['frac_bright'] = np.mean(lum > 205)

    ## ---------------- Color ----------------
    sat = img_hsv[:, :, 1].astype(np.float32)
    val = img_hsv[:, :, 2].astype(np.float32)
    features['sat_mean'] = np.mean(sat)
    features['sat_std'] = np.std(sat)
    features['val_mean'] = np.mean(val)
    features['val_std'] = np.std(val)

    # Colorfulness metric (Hasler & Süsstrunk)
    rg = img_rgb[:, :, 0].astype(np.float32) - img_rgb[:, :, 1].astype(np.float32)
    yb = 0.5 * (img_rgb[:, :, 0].astype(np.float32) + img_rgb[:, :, 1].astype(np.float32)) - img_rgb[:, :, 2].astype(np.float32)
    features['colorfulness'] = np.sqrt(rg.std()**2 + yb.std()**2) + 0.3*np.sqrt(rg.mean()**2 + yb.mean()**2)

    # Warmth: Red vs Blue ratio
    R = img_rgb[:, :, 0].astype(np.float32)
    B = img_rgb[:, :, 2].astype(np.float32)
    features['warmth_rb'] = np.mean(R / (B + 1e-6))

    ## ---------------- Sharpness ----------------
    features['laplacian_var'] = cv2.Laplacian(img_gray, cv2.CV_64F).var()

    # Tenengrad (gradient magnitude)
    gx = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    tenengrad = np.sqrt(gx**2 + gy**2)
    features['tenengrad_mean'] = np.mean(tenengrad)

    ## ---------------- Structure ----------------
    edges = cv2.Canny(img_gray, 100, 200)
    features['edge_density'] = np.mean(edges > 0)

    # Local contrast: std of small patches
    patch_size = 16
    patches = lum[:lum.shape[0]//patch_size*patch_size, :lum.shape[1]//patch_size*patch_size]
    patches = patches.reshape(patches.shape[0]//patch_size, patch_size,
                              patches.shape[1]//patch_size, patch_size)
    patches = patches.swapaxes(1,2).reshape(-1, patch_size, patch_size)
    local_contrast = [np.std(p) for p in patches]
    features['local_contrast_mean'] = np.mean(local_contrast)

    ## ---------------- Weather-ish ----------------
    # Dark channel prior
    min_channel = img_bgr.min(axis=2)
    features['dark_channel_mean'] = np.mean(min_channel)

    # Color attenuation (red - blue gradient)
    features['color_attenuation'] = np.mean(R - B)

    # White fraction
    features['white_fraction'] = np.mean(np.all(img_rgb > 240, axis=2))

    # Specular fraction: very bright pixels with low saturation
    features['specular_fraction'] = np.mean((val > 240) & (sat < 20))

    ## ---------------- Geometry ----------------
    # Vertical luminance gradient
    vert_grad = np.mean(np.diff(lum, axis=0), axis=1)
    features['vertical_lum_gradient'] = np.mean(vert_grad)

    return features

# --- Main Execution Block ---

def main():
    try:
        # Step 1: Download and Combine Data
        all_combined_dfs = download_and_combine_data()

        # Step 2: Feature Selection
        selected_dfs = process_feature_selection(all_combined_dfs)

        # NEW: compute image features
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        image_feature_df = download_image_statistics(container_client)

        # Merge with each dataframe
        for name, df in selected_dfs.items():

            df = df.join(image_feature_df, how="left").fillna(0)

            save_path = f"processed_features_{name}.csv"
            df.to_csv(save_path)

            print(f"\nFinal feature file saved: {save_path} (Shape: {df.shape})")

    except Exception as e:
        print(f"\nAn unexpected error occurred during the pipeline execution: {e}")

main()
