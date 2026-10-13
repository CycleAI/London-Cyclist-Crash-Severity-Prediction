# Paper 2 Colab archive

[Repository overview](../../README.md) · [Main Paper 2 workflows](../README.md) · [Data catalogue](../../Data/README.md)

This directory retains **39 notebooks connected to cyclist-crash data, severity experiments, imagery enrichment or descriptive diagnostics**. Perception voting/ranking/classification notebooks have been removed, including those originally stored under this misleadingly broad folder. The remaining work is a historical collection with alternative implementations, not a single ordered executable pipeline.

## Notebook catalogue

| Notebook | Role | Principal inputs → outputs / caveats |
| --- | --- | --- |
| [AccidentDataForArticle.ipynb](AccidentDataForArticle.ipynb) | Earlier severity correlation/MLP/comparator analysis. | `final_merged_cleaned_data.csv` → confusion matrices, per-fold/repeat summaries and predictions. Earlier random/repeated evaluation, not final XGBoost. |
| [AddSpeedLimitsToAccidents.ipynb](AddSpeedLimitsToAccidents.ipynb) | Harmonise year-specific roadway/police fields. | `merged_collision_data.csv` → `cleaned_collision_data.csv`; coalesces canonical/truncated columns, including speed and severity fields. |
| [BuildMappingsForImages.ipynb](BuildMappingsForImages.ipynb) | Build image/metadata associations. | Configured Azure metadata/images → `strict_mapping_nofallback.csv`; inspect the selected cell and expected blob layout. |
| [CSVOps.ipynb](CSVOps.ipynb) | Historical multi-step data reconciliation and engineered variables. | Many intermediate crash/weather/history files → cleaned tables, UTC checks, severe-history composites, exposure-normalised history, speed proxy and bank-holiday fields. Alternative scratch cells are not a single pipeline. |
| [CheckRandom.ipynb](CheckRandom.ipynb) | Inspect sampled image coordinates. | Configured Azure image metadata → `check_random_map.html`; acquisition diagnostic. |
| [CheckWeatherConsistency.ipynb](CheckWeatherConsistency.ipynb) | Audit matched weather timing/coordinates. | `enriched_collision_data_with_weather.csv` → printed consistency summaries. This alone does not establish historical availability. |
| [CompareMaps.ipynb](CompareMaps.ipynb) | Compare request and response coordinates. | Azure metadata → `requested_coords_map.html` and `response_coords_map.html`. |
| [CountRows.ipynb](CountRows.ipynb) | Count the sampling grid. | `greater_london_grid_50m_full.csv` → a printed row count, not a crash count. |
| [CreateInputNN.ipynb](CreateInputNN.ipynb) | Shared segmentation/detection/image-statistics extraction. | Configured Azure/local image features → `processed_features_*.csv` plus collision-join diagnostics. Unused perception-ranking constants removed. |
| [CreatePlots.ipynb](CreatePlots.ipynb) | Earlier contextual-variable distributions. | `all_59k_accidents_archive_weather_poi_final.csv` → paginated `feature_distributions_page_*.png`; sample must be audited against Appendix D. |
| [DataCleaning.ipynb](DataCleaning.ipynb) | Reconcile weather gaps and collision fields. | Earlier crash CSVs and missing-weather JSONL → cleaned/updated tables and summaries. Some cells overwrite an input CSV. |
| [DataEnrichment.ipynb](DataEnrichment.ipynb) | Compute local prior-collision histories. | `all_59k_accidents_no_history.csv` → `all_59k_accidents_complete_final_cleaned.csv`; spatial radii/lookbacks and severity-specific counts. Audit unique-event, strict-time and incomplete-history rules. |
| [Download London boroughs.ipynb](Download%20London%20boroughs.ipynb) | Download/prepare borough boundaries. | External boundary data → `london_boroughs.geojson`; record source version. |
| [Download2500Images.ipynb](Download2500Images.ipynb) | Earlier sampled-grid acquisition variant. | `greater_london_grid_50m_full.csv` → Street View metadata/images in configured Azure paths; filename is not verified coverage. |
| [DownloadFromMetadata.ipynb](DownloadFromMetadata.ipynb) | Fetch images for existing metadata. | Configured panorama metadata → Street View images/Azure objects; two API-key placeholders require local configuration. |
| [DownloadFromMetadataConcurrently.ipynb](DownloadFromMetadataConcurrently.ipynb) | Concurrent metadata-based image retrieval. | Configured metadata/panorama IDs → images in configured paths. Review retry/concurrency and write settings. |
| [DownloadImages.ipynb](DownloadImages.ipynb) | Grid-based multiview imagery acquisition. | `greater_london_grid_50m_full.csv` → Google/Azure image and metadata outputs. |
| [DownloadWeatherData.ipynb](DownloadWeatherData.ipynb) | Earlier weather acquisition alternatives. | `all_59k_accidents_raw.csv` → weather CSV/JSONL and error logs; archive/forecast availability must be distinguished. |
| [EnrichAccidentsWithImageFeatures.ipynb](EnrichAccidentsWithImageFeatures.ipynb) | Collision/image matching, weather and exploratory feature ranking. | Collision tables + metadata + image descriptors → enriched CSVs, weather/error logs and MI plots. Source cells unchanged; one stale perception-label display was cleared. |
| [FeatureImportance.ipynb](FeatureImportance.ipynb) | Earlier MI ranking and distribution plots. | `final_processed_with_interest.csv` → MI CSVs and top-feature plots. Not a frozen fit-only final-model manifest or causal attribution. |
| [FinalNNAccidents.ipynb](FinalNNAccidents.ipynb) | Earlier crash-schema harmonisation and neural experiments. | `merged_collision_data_speed_limit.csv` → model diagnostics and retained-feature correlation export; historical feature/split policy. |
| [GenerateImageManifest.ipynb](GenerateImageManifest.ipynb) | Enumerate images for processing. | Configured image/storage inventory → manifest output defined in its cell. Confirm identifier format before feeding inference. |
| [GenerateLondonGrid.ipynb](GenerateLondonGrid.ipynb) | Earlier London grid and map variants. | London boundary → `greater_london_grid_50m_full.csv`, Folium/Kepler map exports. Review projected CRS in each variant. |
| [Get20000Images.ipynb](Get20000Images.ipynb) | Earlier sampling/acquisition variant. | Grid CSV → metadata/images through Google/Azure; requested sample settings are not final-cohort coverage. |
| [Get56497PointsFromGrid.ipynb](Get56497PointsFromGrid.ipynb) | Larger grid metadata query variant. | Grid CSV → configured metadata outputs with retries; record actual success counts and input seed. |
| [GetAllMetadataForPoints.ipynb](GetAllMetadataForPoints.ipynb) | Metadata retrieval for a different grid setting. | Expects `greater_london_grid_168m_full.csv`, which is not bundled; do not silently substitute the 50 m grid. |
| [GetDistancesMapbox.ipynb](GetDistancesMapbox.ipynb) | Earlier routing-distance comparison. | `interest_points.csv` → `output_with_distances.csv`, `comparison_absolute.csv`, histograms. Requires a routing token; not the paper's OS Open Roads edge-projection procedure. |
| [GetHistoryForecast.ipynb](GetHistoryForecast.ipynb) | Historical-forecast retrieval and merging. | Crash timestamps/coordinates and earlier merged tables → forecast JSONL and matched/unmatched CSVs. Uses `OPEN_METEO_API_KEY`. |
| [GetImagesFromMapping.ipynb](GetImagesFromMapping.ipynb) | Attach image associations to earlier weather data. | `enriched_collision_data_with_weather.csv` + `metadata_images_mapping.csv` → `processed_collisions_with_images.csv`. |
| [GetWeatherWithKey.ipynb](GetWeatherWithKey.ipynb) | Archive-weather batch retrieval and reconciliation. | Earlier collision CSVs → archive JSONL/CSV, UTC and missingness diagnostics. Similar to the main archive-weather notebook, but a separate historical copy. |
| [GridSearch.ipynb](GridSearch.ipynb) | Earlier severity MLP parameter/feature searches. | Mapped/cleaned collision CSVs → printed model diagnostics. Includes ADASYN/random splits, unlike the final strict benchmark. |
| [ImageSegmentation.ipynb](ImageSegmentation.ipynb) | Alternative Detectron2/Mask2Former workflow. | Azure/local images → masks, instance/panoptic/semantic artifacts and `mask2former_manifest.jsonl`; separate framework/setup requirements. |
| [ImgSegWorking.ipynb](ImgSegWorking.ipynb) | Transformers segmentation and inspection variants. | Configured images → masks, per-image JSON, colour/overlay views and optional Azure uploads. |
| [ImgSegm2.ipynb](ImgSegm2.ipynb) | Another segmentation implementation/inspection archive. | Configured images → instance/panoptic/semantic masks and manifests; do not mix checkpoints/taxonomies without checks. |
| [NNAccidentDataFinal.ipynb](NNAccidentDataFinal.ipynb) | Earlier severity neural/LightGBM experiments. | Merged crash context → historical validation/holdout metrics and predictions. Uses its own feature and resampling choices; not the paper's expanded comparator release. |
| [NNForAccidents.ipynb](NNForAccidents.ipynb) | Earlier yearly crash-table merge and neural model. | Year-specific crash CSVs → `merged_collision_data.csv` and multiclass/severity training diagnostics. |
| [NNForAccidents2.ipynb](NNForAccidents2.ipynb) | Alternative crash merge/cleaning/neural workflow. | Yearly crash CSVs → merged table and fold/training diagnostics with class weighting. |
| [Plots.ipynb](Plots.ipynb) | Earlier collision/image feature distributions. | `enriched_collision_data_with_distance.csv` → basic, image, object and segmentation distribution figures. |
| [YoloV10.ipynb](YoloV10.ipynb) | Object-detection processing and box previews. | Configured Azure/local images and YOLO detections → detection summaries, JSON and annotated previews. |

[README.md](README.md) is the directory guide. The catalogue identifies principal files; individual scratch notebooks may reference additional temporary paths and multiple versions. Inspect the chosen cell's constants rather than treating every filename mentioned in source/output as a required dependency.

## Choose a workflow

For the most focused enrichment entry points, begin in [Paper2/](../README.md). Use this archive when you need a specific earlier method or diagnostic:

1. Harmonisation/history: `AddSpeedLimitsToAccidents` → selected `DataCleaning`, `DataEnrichment` and `CSVOps` cells.
2. Image acquisition: grid generation → one selected sampling/metadata strategy → metadata-based downloads → mapping/manifest checks.
3. Descriptors: one segmentation implementation plus `YoloV10` → `CreateInputNN` → a collision/image join.
4. Weather: choose historical forecast versus archive retrieval deliberately → matching/timestamp diagnostics.
5. Description: `CreatePlots`, `Plots`, `FeatureImportance` and map notebooks; label each output with its input cohort/version.
6. Earlier modelling: inspect `GridSearch`, `FinalNNAccidents`, `NNAccidentDataFinal`, `NNForAccidents*` or `AccidentDataForArticle` only as historical severity experiments.

None of these paths is an identified implementation of the manuscript's complete strict chronological XGBoost search. Do not substitute an MLP notebook with “Final” in its name for that missing artifact.

## Inputs and outputs

Stage working copies in a known kernel directory. Some inputs are available under [Data/](../../Data/README.md), [Accidents/](../../Accidents/README.md), [ImageFeatures/](../../Data/ImageFeatures/README.md) or [docs/](../../docs/README.md). Same basenames can have different schemas. Other inputs, including yearly police extracts, `all_59k_*` tables, raw metadata/images, the 168 m grid and routing reference tables, are not supplied here.

Expected input families are: a crash CSV with timestamp/coordinates/road context and severity label; image metadata with names, request/panorama coordinates and date; segmentation/detection JSON; and weather JSONL/CSV. Output families are cleaned/enriched CSVs, image/mask/manifest files, diagnostic figures/HTML and earlier model metrics. Establish row grain and join keys for each operation. Table names and historical row counts are not a reproducibility manifest.

Many cells save to generic `output.csv` paths or overwrite intermediate files. Use a scratch directory and explicit versioned output names. Mounting Drive, requesting data or uploading blobs is optional workflow execution, not necessary for reading source. Re-running a notebook can change remote storage or incur API costs.

## Runtime and credentials

Use Jupyter or Google Colab, following the [root environment notes](../../README.md). Common packages: pandas, NumPy, SciPy, matplotlib, seaborn, scikit-learn and tqdm. Acquisition adds requests/azure-storage-blob; maps add Folium/Kepler/pyproj; image features add Pillow/OpenCV/scikit-image; inference adds the specific PyTorch/Transformers/Detectron2/Ultralytics stack; earlier models use TensorFlow, LightGBM and/or imbalanced-learn. There is no complete tested requirements lock, and notebook installers may conflict across variants.

Resolve `/content/`, original-machine and Drive paths for your runtime. Configure only the credential names actually read by the selected notebook, commonly `STREET_VIEW_API_KEY`, `AZURE_STORAGE_CONN_STR`, `AZURE_CONNECTION_STRING`, `OPEN_METEO_API_KEY` and local `CONN_STR` settings. Routing notebooks contain `YOUR_API_KEY` placeholders. Use environment or notebook secret storage; never hardcode working credentials into committed cells or outputs.

## Interpretation and known limitations

- Historical models use differing random splits, multiclass/binary targets, class weights or ADASYN. The manuscript's strict benchmark uses chronological fitting/validation/test and no synthetic oversampling.
- Explicitly verify which encoded class is Serious/Fatal; alphabetical label encoding is not a positive-class specification.
- Some MI routines inspect the full earlier table. Their output is not the fit-only final top-140 list, model attribution or a causal effect.
- The paper's POI routing procedure uses a 100 m candidate filter and 120 m route cutoff on OS Open Roads; the Mapbox comparison notebook is a separate exploratory method.
- Image acquisition counts, checkpoint defaults, heading averages and zero-filled descriptors do not resolve final-cohort coverage or historical availability. Preserve failed requests and capture-date lag.
- `CSVOps` and weather notebooks contain successive attempted repairs. A later cell or reassuring filename alone does not prove correction of every row or formula. Compare chosen code against Appendix C definitions and inspect its outputs.
- Stored outputs predate this cleanup. Perception labels were removed from three shared tables, so dependent earlier metrics are not newly validated results.

Documentation checks validate notebook JSON and source scope; training, remote acquisition and notebook run-all execution were not performed. Record the exact notebook, cells, commit, data hashes and runtime when producing a new result.
