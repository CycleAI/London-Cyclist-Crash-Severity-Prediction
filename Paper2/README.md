# Paper 2 enrichment workflows

[Repository overview](../README.md) · [Colab archive](ColabNoteBooks/README.md) · [Interactive map](Map/README.md)

These notebooks implement components of the contextual-data and extended-enrichment programme described in manuscript Sections 3.4–3.5 and Appendices A/C. They do not contain the final strict XGBoost experiment. Candidate image/terrain/composite features must not be credited with the paper's performance without the missing selected-feature manifest and evaluated model.

## Files

| File | Purpose / inputs → outputs |
| --- | --- |
| [GenerateLondonGrid.ipynb](GenerateLondonGrid.ipynb) | London boundary → `greater_london_grid_50m_full.csv`; projected-grid and visualisation alternatives. Appendix C sampling context. |
| [VisualizeLondonGrid.ipynb](VisualizeLondonGrid.ipynb) | Grid CSV → Folium `london_points_map.html`, with image-link popups when available. |
| [ExtractMetadataForRandomGridPoints.ipynb](ExtractMetadataForRandomGridPoints.ipynb) | Sample grid coordinates → Street View metadata in Azure; inspect sample count, random seed and prefixes. |
| [DownloadAccidentsMetadataAndImages.ipynb](DownloadAccidentsMetadataAndImages.ipynb) | `all_59k_accidents_raw.csv` → crash-centred Street View metadata and four-view images in Azure. Intended linkage workflow, not evidence of final-cohort coverage. |
| [CreateMetadataFile.ipynb](CreateMetadataFile.ipynb) | Configured local metadata JSON → `streetview_metadata_compiled.csv`; includes separate Azure upload cells. |
| [CreateMetadataMapping.ipynb](CreateMetadataMapping.ipynb) | Metadata folder → `streetview_metadata.csv`, preserving request/panorama/image linkage fields. |
| [AddCollisionToMetadata.ipynb](AddCollisionToMetadata.ipynb) | `streetview_metadata.csv` + `collisions_final.csv` → `streetview_metadata_with_collision.csv` using requested coordinates. Audit repeated coordinates/IDs. |
| [AddMetadataToAccidents.ipynb](AddMetadataToAccidents.ipynb) | `final_file_sin_extra.csv` + `streetview_metadata_compiled.csv` → `merged_dataset_2.csv` with image displacement and time-lag descriptors. |
| [GetHistoryForecast.ipynb](GetHistoryForecast.ipynb) | Crash coordinates/timestamps → historical-weather/forecast requests, JSONL and merged diagnostics; contains multiple versions and reconciliation cells. |
| [GetOpenMeteoArchiveData.ipynb](GetOpenMeteoArchiveData.ipynb) | Crash CSV → Open-Meteo archive JSONL/CSV, timestamp/missingness checks and merges. Review UTC conversion and time windows. |
| [GetPrecipitationBacktracked.ipynb](GetPrecipitationBacktracked.ipynb) | `all_59k_accidents_complete_final_2_cleaned.csv` → `open_meteo_archive_precipitation_backtracked.jsonl`, searching backwards for precipitation. |
| [ImageSegmentation.ipynb](ImageSegmentation.ipynb) | Azure/local Street View images → Mask2Former class masks, JSON summaries and overlays; includes upload/visualisation variants. |
| [YOLOV10.py](YOLOV10.py) | Azure image batches → object detections and previews. Notebook-export syntax; confidence and blob-prefix settings need review. |
| [ProcessImageAndObjectDetection.ipynb](ProcessImageAndObjectDetection.ipynb) | Segmentation/detection JSON and image statistics → `processed_features_*.csv`, including class counts, confidence sums, areas and 3×3 regions. Multiple variants and diagnostic cells. |
| [ProcessImageStatsLocally.ipynb](ProcessImageStatsLocally.ipynb) | Local images selected by `PAPER2_IMAGE_DIR` → colour/texture/edge and grid statistics; output controlled by `PAPER2_IMAGE_STATS_CSV`. |
| [MergeFinalFiles.ipynb](MergeFinalFiles.ipynb) | `processed_features_conf_0.5_filled_metadata_no_collision.csv` + `image_stats_processed_final_grids_no_collision.csv` → `final_dataset_no_collision.csv`; inner one-to-one merge on request coordinates, panorama and image name. |
| [ExtractSlope.ipynb](ExtractSlope.ipynb) | `merged_dataset_2.csv` + OSM roads + Environment Agency LiDAR → slope-enriched collision CSVs and quality flags; includes successive refinement cells. |
| [README.md](README.md) | Main Paper 2 workflow, input requirements and manuscript mapping. |

`ColabNoteBooks/` contains earlier or alternative implementations; `Map/` contains descriptive browser visualisation. Their READMEs catalogue every file. Similar filenames at root, here and in Colab are historical versions, not an automatically synchronised package.

## Suggested execution order

1. Choose grid-based imagery acquisition (`GenerateLondonGrid` → `ExtractMetadataForRandomGridPoints`) or the crash-centred acquisition in `DownloadAccidentsMetadataAndImages`. Record exact inputs and sample settings.
2. Compile image metadata using `CreateMetadataFile` or `CreateMetadataMapping`. Check their different output schemas before choosing the downstream collision-linkage notebook.
3. Attach collision identifiers or metadata displacement/time lag using `AddCollisionToMetadata` / `AddMetadataToAccidents`. Coordinates alone are not unique event identifiers.
4. Retrieve weather with `GetOpenMeteoArchiveData`; use precipitation/history-forecast variants only for the intended feature definition. Audit UTC, daylight saving, aggregation windows and availability before the crash.
5. Run the selected detector and segmentation variant, then `ProcessImageAndObjectDetection` and `ProcessImageStatsLocally` on aligned image IDs/headings.
6. Prepare the two exact input tables required by `MergeFinalFiles`. It uses `pandas.read_csv(engine="pyarrow")` and `validate="one_to_one"`; duplicated merge keys should fail rather than expand rows. It outputs an image-level table, not the final crash cohort.
7. Run `ExtractSlope` only after road/terrain data and CRS checks. Keep quality flags and per-record source linkage.

This is a conceptual sequence of components, not a tested run-all pipeline. Each notebook contains its own paths, defaults and intermediate outputs. Inspect source cells and use scratch copies to avoid overwriting data.

## Inputs and configuration

The archive does not bundle `all_59k_accidents_raw.csv`, `collisions_final.csv`, the final one-to-one image merge inputs, all raw image/metadata blobs, or the final 59,628-record analytical table. Earlier [bundled data](../Data/README.md) are not substitutes with guaranteed equivalent row counts or schemas.

The original data references identify Azure account `cycleai`, container `london`, prefix `Paper2Data/`, with objects such as `paper_2_final_dataset.csv`, `collisions_final.csv`, `streetview_metadata_with_collision.csv`, `image_stats_processed_final_grids_no_collision.csv`, `processed_features_conf_0.5_filled_metadata_no_collision.csv` and `ukbankholidays-jul19.xls`. Obtain authorised access and verify hashes/vintages. Signed URL credentials were removed; no currently valid access link or final-model correspondence is asserted.

Google/Azure notebooks commonly read `STREET_VIEW_API_KEY` and `AZURE_STORAGE_CONN_STR`; some use `AZURE_CONNECTION_STRING` or local `CONNECTION_STRING`/`CONN_STR` settings. Weather uses `OPEN_METEO_API_KEY`. Read each configuration cell. Use notebook secret storage or environment variables; never commit working secrets. Blob uploads and API calls are real side effects.

For local image statistics, set `PAPER2_IMAGE_DIR` to a directory of the crash-enrichment images. Its default is `./images`; `PAPER2_IMAGE_STATS_CSV` defaults to `image_stats_processed_grids.csv`. This output still needs metadata association/renaming before the final merge; the notebook does not automatically produce all merge keys.

## Dependencies and runtime

Use Jupyter/Colab and the [root setup](../README.md). Depending on the notebook: pandas, NumPy, SciPy, pyarrow, requests, tqdm, azure-storage-blob, Pillow, OpenCV, scikit-image, matplotlib, Folium, PyTorch/Transformers, Ultralytics, GeoPandas, Shapely, pyproj, OSMnx and rasterio. Segmentation variants may require Detectron2 and a compatible CUDA environment. There is no verified pinned environment; installation cells reflect the archived experiments. Do not execute all installers into one environment as if they were a lockfile.

## Validation and paper correspondence

- Grid spacing is described in metres in British National Grid; request coordinates are WGS84. Inspect CRS choices in each historical variant.
- The paper describes four headings, 640×640 images and a 50 m Street View request radius. Its earlier acquisition totals are inconsistent; filename counts and code constants do not resolve the final-cohort linkage.
- YOLO confidence sums are not calibrated class probabilities; summed boxes can overlap. Segmentation fractions depend on the actual checkpoint label map. A current code default does not certify the final experiment's checkpoint.
- Preserve request/panorama displacement, capture dates and missingness. Later imagery does not establish historically available pre-crash context.
- The terrain appendix describes 20 m profiles on either side, 2 m spacing and robust Theil–Sen fitting, with distance/coverage/bridge/tunnel/grade flags. Verify that the chosen notebook cells match that procedure.
- Earlier code may fill missing image features with zero or drop unmatched records. These are historical implementation choices, not endorsed missingness policies for the manuscript's final cohort.

Notebook JSON and retained archives were checked; API acquisition, GPU inference, terrain processing and model training were not executed during documentation.
