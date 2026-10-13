!pip install azure-storage-blob pandas numpy scikit-learn tensorflow

import os
import json
import pandas as pd
import numpy as np
from io import StringIO
from azure.storage.blob import BlobServiceClient
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from tqdm.notebook import tqdm
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from typing import Dict, Any, List
AZURE_CONNECTION_STRING = ""

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
CONFIDENCE_LEVELS = [0.7]

# Placeholder for the complete set of Image IDs (19995 total)
NUM_IMAGES = 19995
IMAGE_IDS = [f"{i}_{angle}.jpg" for i in range(NUM_IMAGES // 4 + 1) for angle in [0, 90, 180, 270]][:NUM_IMAGES]

SEG_FULL_CLASSES = [
    'Bicycle', 'Bicyclist', 'Bike Lane', 'Bike Rack', 'Billboard', 'Bird',
    'Boat', 'Boat Mount', 'Bridge', 'Building', 'Bus', 'Banner', 'Barrier',
    'Bench', 'Car', 'Car Mount', 'Caravan', 'Catch Basin', 'CCTV Camera',
    'Curb', 'Curb Cut', 'Crosswalk—Plain', 'Ego Vehicle', 'Fence',
    'Fire Hydrant', 'Guard Rail', 'Junction Box', 'Lane', 'Lane Marking—Crosswalk',
    'Lane Marking—General', 'Mailbox', 'Manhole', 'Mountain', 'Motorcycle',
    'Motorcyclist', 'On Rails', 'Other Rider', 'Other Vehicle', 'Parking',
    'Pedestrian Area', 'Phone Booth', 'Pole', 'Pothole', 'Rail Track',
    'Road', 'Sand', 'Service Lane', 'Sidewalk', 'Sky', 'Snow', 'Street Light',
    'Terrain', 'Traffic Light', 'Traffic Sign (Back)', 'Traffic Sign (Front)',
    'Traffic Sign Frame', 'Trailer', 'Trash Can', 'Truck', 'Tunnel', 'Unlabeled',
    'Utility Pole', 'Vegetation', 'Water', 'Wheeled Slow'
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

# --- Helper Functions for Parsing ---

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

def parse_yolo(txt_content: str) -> Dict[str, int]:
    """Parses YOLO TXT content and returns a dictionary of object class counts."""
    try:
        lines = txt_content.strip().split('\n')
        class_counts = {}
        for line in lines:
            parts = line.split()
            if parts:
                # YOLO format is typically: class_id confidence x_center y_center width height
                class_id = int(parts[0])
                # We map the ID to the class name using the full list
                if class_id < len(OBJ_FULL_CLASSES):
                    class_name = OBJ_FULL_CLASSES[class_id]
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
        return class_counts
    except Exception as e:
        print(f"Error parsing YOLO TXT: {e}")
        return {}

MAX_WORKERS = 32

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

    if CONNECTION_STRING == "YOUR_AZURE_BLOB_STORAGE_CONNECTION_STRING_HERE":
         raise ValueError("Please replace 'YOUR_AZURE_BLOB_STORAGE_CONNECTION_STRING_HERE' with your actual Azure connection string.")

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
        obj_cols_full = [f"obj_{cls}" for cls in OBJ_FULL_CLASSES]
        all_cols_full = seg_cols_full + obj_cols_full

        # Ensure all possible columns exist and fill NaN (from missing entries) with 0.0
        df = df.reindex(columns=all_cols_full, fill_value=0.0)

        all_dataframes[f'conf_{conf_str}'] = df
        print(f"DataFrame for confidence {conf_str} created. Shape: {df.shape}")

    return all_dataframes


# --- Step 2: Process Feature Selection ---

def process_feature_selection(data_frames: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Filters the dataframes to only keep the most relevant, pre-selected classes."""
    print("\n--- Step 2: Feature Selection ---")

    # Now using ALL available classes as features
    selected_seg_cols = [f"seg_{cls}" for cls in SELECTED_SEG_CLASSES]
    selected_obj_cols = [f"obj_{cls}" for cls in SELECTED_OBJ_CLASSES]
    KEEP_COLS = selected_seg_cols + selected_obj_cols

    processed_dfs = {}
    for name, df in data_frames.items():
        filtered_df = df[KEEP_COLS].copy()
        processed_dfs[name] = filtered_df
        print(f"DataFrame {name} filtered. Final Feature Count: {filtered_df.shape[1]}")

    return processed_dfs

# --- Main Execution Block ---

def main():
    try:
        # Step 1: Download and Combine Data
        all_combined_dfs = download_and_combine_data()

        # Step 2: Feature Selection
        selected_dfs = process_feature_selection(all_combined_dfs)

        # Save the processed dataframes locally (e.g., in Colab's file system)
        for name, df in selected_dfs.items():
            save_path = f"processed_features_{name}.csv"
            df.to_csv(save_path)
            print(f"\nFinal feature file saved: {save_path} (Shape: {df.shape})")

    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {e}")
        print("Please ensure your uploaded file (ai_rank_gpt.csv) is accessible.")
    except ConnectionError as e:
        print(f"\nFATAL ERROR: {e}")
        print("Please check your Azure CONNECTION_STRING and ensure the required libraries are installed.")
    except ValueError as e:
        print(f"\nFATAL ERROR: {e}")
        print("You must update the Azure CONNECTION_STRING placeholder.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during the pipeline execution: {e}")

main()
