# !pip install requests azure-storage-blob tqdm
# !pip install keplergl pandas

# azure_kepler_map.py

from azure.storage.blob import BlobServiceClient
import pandas as pd
import json
from keplergl import KeplerGl
import os

# -----------------------
# Configuration
# -----------------------
BLOB_PREFIX = "Metadata/"  # Or wherever your JSON files are stored

# Output HTML paths
REQUESTED_MAP_HTML = "requested_coords_map.html"
RESPONSE_MAP_HTML = "response_coords_map.html"

# -----------------------
# Connect to Azure Blob Storage
# -----------------------
blob_service_client = BlobServiceClient.from_connection_string("conn_string")
container_client = blob_service_client.get_container_client("london")

# -----------------------
# Collect Coordinates
# -----------------------
requested_data = []
response_data = []

# List all blobs with the given prefix
blob_list = container_client.list_blobs(name_starts_with=BLOB_PREFIX)

for blob in blob_list:
    blob_client = container_client.get_blob_client(blob)
    blob_content = blob_client.download_blob().readall()
    
    try:
        data = json.loads(blob_content)
        # Extract requested coordinates
        req = data["requested"]
        requested_data.append({
            "lat": req["lat"],
            "lng": req["lng"]
        })
        
        # Extract response coordinates
        res = data["metadata_response"]["location"]
        response_data.append({
            "lat": res["lat"],
            "lng": res["lng"]
        })

    except Exception as e:
        print(f"Failed to parse blob {blob.name}: {e}")

# Convert to DataFrames
df_requested = pd.DataFrame(requested_data)
df_response = pd.DataFrame(response_data)

# -----------------------
# Create Kepler Maps
# -----------------------

def generate_kepler_map(df, output_file, center_lat, center_lng, label):
    kepler_map = KeplerGl(height=800)
    kepler_map.add_data(data=df, name=label)

    config = {
        "version": "v1",
        "config": {
            "visState": {},
            "mapState": {
                "latitude": center_lat,
                "longitude": center_lng,
                "zoom": 11,
                "pitch": 0,
                "bearing": 0
            },
            "mapStyle": {}
        }
    }

    kepler_map.save_to_html(file_name=output_file, config=config)
    print(f"Saved Kepler map to {output_file}")

# Center both maps on London for consistency
CENTER_LAT = 51.5074
CENTER_LNG = -0.1278

generate_kepler_map(df_requested, REQUESTED_MAP_HTML, CENTER_LAT, CENTER_LNG, "Requested Coordinates")
generate_kepler_map(df_response, RESPONSE_MAP_HTML, CENTER_LAT, CENTER_LNG, "Response Coordinates")
