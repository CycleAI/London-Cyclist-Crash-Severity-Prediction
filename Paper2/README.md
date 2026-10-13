# Cyclist Crash Severity in Greater London: A Multimodal Spatiotemporal Approach

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Classifier-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

This repository implements an end-to-end urban analytics pipeline to predict cyclist crash severity (*Slight* vs. *Serious/Fatal*) across Greater London. By fusing traditional police crash databases with dynamic weather, POI-network routing, street-level computer vision features, and advanced risk proxies, this codebase shifts proactive cycling safety from simple retrospective hotspot maps to conditional risk profiles.

The repository features a flat directory structure designed to process, model, and evaluate these complex interactions cleanly.

---

## 💾 Data Availability

All datasets utilized in this pipeline—including processed features, street view segmentation maps, and historical coordinates—are hosted on **Azure Blob Storage**:
* **Account:** `cycleai`
* **Container:** `london`

---

## 🛠️ Feature Architecture

The input modeling dataset contains **59,979 collision events** and integrates heterogeneous spatial, temporal, and environmental data:

* **Historical Crash Statistics:** Baseline pre-crash spatial counts compiled from TfL and Stats19 datasets, including total counts of past accidents and prior severe collisions.
* **Spatial & Points of Interest (POI) Metrics:** Proximity to key urban anchors (schools, pubs, road signals, overground, and underground stations). The schema tracks both network-routing distances (calculated using an edge-projection method onto road links) and straight-line ("as the crow flies") Euclidean distances, denoted by `crow` in the variable names.
* **Meteorological Data (Open-Meteo):** Hourly weather conditions (e.g., temperature, humidity, apparent temperature, and hourly precipitation) queried from the Open-Meteo Archive API.
* **Engineered Weather Features:** Rolling temporal averages and cumulative summations covering the "last $x$ hours", alongside tracking indicators for hours elapsed since the last rain event within the past 7 days.
* **Computer Vision Infrastructure Proxies:** Object detection counts and areas (**YOLOv10**) alongside pixel-level semantic segmentation ratios (**Mask2Former**) extracted from 19,995 multi-view Google Street View images (0°, 90°, 180°, and 270°). These represent physical and structural characteristics of the roadway environment (e.g., presence of roads, sidewalks, vegetation, and signage).
* **Advanced Risk & Traffic Proxies:** High-level engineered spatiotemporal features:
  * **Speed-Energy Proxy:** A quadratic scaling of posted limits to approximate kinetic energy exposure, defined as:
    $$\text{speed-energy-proxy} = \left(\frac{\text{speedlimit-clean}}{20}\right)^2$$
  * **Weighted Prior Severe-Collision Memory:** Decayed density where closer/more recent severe crashes are heavily prioritized over large buffers.
  * **Multi-Scale Hotspot Concentration Gradient:** Captured as the ratio between fine-scale and broad-scale past-collision densities.
  * **Exposure-Adjusted Collision History:** Local historic crash counts normalized by average localized cyclist traffic volumes (log-scaled exposure).
  * **Road Gradient Estimation:** Longitudinal road gradient derived from combining coordinates with LiDAR-based digital elevation data.

---

## 📦 Repository Structure

The codebase is structured flatly for simple execution and quick adaptation:

```directory
.
├── ColabNoteBooks             # Folder with all raw notebooks used in this project
│   ├── input_nn.csv                       # Final dataset used to train the neural network, including accident, Street View, object detection, segmentation, and Open-Meteo features
│   └── open_meteo.jsonl                   # Raw Open-Meteo API responses
├──  AddMetadataToAccidents.ipynb # Enriches the accident dataset with two additional features derived from Google Street View metadata: streetview_distance_m and streetview_time_diff_days
├──  CreateMetadataFile.ipynb # Creates the streetview_metadata_compiled.csv file
├──  DownloadAccidentsMetadataAndImages.ipynb # Used for google street view images. The first part searches for a valid image within 50m and if found it saves the metadata. The second part reads the pano id from the metadata and dlownloads the images
├──  ExtractMetadataForRandomGridPoints.ipynb # Randomly sample points from a CSV of lat/lng and verify that a google street view image exists. If found within 50m, save the metadata in azure
├──  ExtractSlope.ipynb # For each accident location it computes the inclination. 20m before and after are used for the estimation. I uses road gradient from OpenStreetMap road geometry and 1 m LiDAR elevation data.
├── GenerateLondonGrid.ipynb # Generates the London Grid by randomly sampling points within Greater London with a 50m spacing
├── GetHistoryForecast.ipynb  # Retrieves the weather forecast for the accident location, before the accident happened.
├── GetOpenMeteoArchiveData.ipynb      # Retrieves all the available open meteo archive data for the accident location
├── GetPrecipitationBacktracked.ipynb      # Goes back up to 7 days to find last time it rained at the accident location
├── ImageSegmentation.ipynb      # Segments the images in Azure using Mask2Former
├── ProcessImageAndObjectDetection.ipynb      # Merged object detection and image segmnetation features and computes the averages and centroids for each location
├── VisualizeLondonGrid.ipynb      # Generates a map to visualize the London Grid
├── YOLOV10.ipynb      # Performs object detection using YoloV10
├── AddCollisionToMetadata.ipynb      # Adds collison id to metadat file
├── CreateMetadataMapping.ipynb      # Creates metadata file from folder
├── MergeFinalFiles.ipynb      # Merges image statistics file with object detection and image segmentation
├── ProcessImageStatsLocally.ipynb      # Computes image statistics using open cv, from a local folder with 640 x 640 px images
└── README.md             # This documentation

All the data is available in Azure Blob Storage, london container, Paper 2 Data and at the following links:

Final paper 2 data - https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/london/Paper2Data/paper_2_final_dataset.csv?sp=r&st=2026-08-09T16:09:35Z&se=2086-08-20T00:24:35Z&spr=https&sv=2026-02-06&sr=b&sig=YOUR_AZURE_SAS_SIGNATURE . 

Street view metadata mapping - https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/london/Paper2Data/streetview_metadata_with_collision.csv?sp=r&st=2026-08-09T16:10:00Z&se=2086-09-04T00:25:00Z&spr=https&sv=2026-02-06&sr=b&sig=YOUR_AZURE_SAS_SIGNATURE

Image stats - https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/london/Paper2Data/image_stats_processed_final_grids_no_collision.csv?sp=r&st=2026-08-09T16:10:29Z&se=2096-08-22T00:25:29Z&spr=https&sv=2026-02-06&sr=b&sig=YOUR_AZURE_SAS_SIGNATURE

Image segmentation and object detection - https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/london/Paper2Data/processed_features_conf_0.5_filled_metadata_no_collision.csv?sp=r&st=2026-08-09T16:11:05Z&se=2086-08-22T00:26:05Z&spr=https&sv=2026-02-06&sr=b&sig=YOUR_AZURE_SAS_SIGNATURE

Accidents file - https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/london/Paper2Data/collisions_final.csv?sp=r&st=2026-08-10T14:56:59Z&se=2086-08-29T23:11:59Z&spr=https&sv=2026-02-06&sr=b&sig=YOUR_AZURE_SAS_SIGNATURE

UK Bank holidays file - https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/london/Paper2Data/ukbankholidays-jul19.xls?sp=r&st=2026-08-10T15:42:18Z&se=2086-08-10T23:57:18Z&spr=https&sv=2026-02-06&sr=b&sig=YOUR_AZURE_SAS_SIGNATURE

The Map folder contains the code for the interactive map available here: https://cycleai.github.io/accidents-map/