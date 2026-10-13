# London Cyclist Crash Severity Prediction — Paper 2

Research code, intermediate data and enrichment tools supporting **Cyclist Crash Severity in Greater London: Multimodal Context, Temporal Validation and Feature Availability**. Scope follows the [reference manuscript](PRIVATE_REFERENCE_NOT_PUBLISHED), stored as `Article 2 Latest.docx`, modified 8 October 2026 and reviewed on 14 October 2026.

The outcome is **Serious/Fatal versus Slight injury severity conditional on a recorded cyclist crash**: `P(Serious/Fatal | recorded cyclist crash, context)`. This crash-only analysis does not estimate crash occurrence, an individual cyclist's trip risk or a collision rate per kilometre.

## Release status

This checkout contains archived crash processing, weather/history enrichment, imagery/terrain methods, earlier severity experiments and descriptive maps. Human/LLM perception voting, TrueSkill ranking, perception classifiers and their result bundles have been removed from the current tree. Shared image descriptors remain where they support crash enrichment, with unrelated perception targets removed.

**This is not the complete final experimental release.** The supplied ZIP contains no identified implementation of the final 1,000-configuration XGBoost search, frozen top-140 feature manifest, fitted encoder, split manifest, selected model or held-out probability archive. Earlier MLP/random-split notebooks must not be described as the chronological benchmark. A filename containing `final` does not certify correspondence to the manuscript cohort.

## Manuscript specification

These values are reported in the manuscript, not recomputed from this checkout:

| Item | Reported specification |
| --- | --- |
| Records | 59,628 Greater London cyclist-crash modelling records, 2013–2025 |
| Outcome | 50,268 Slight; 9,360 Serious/Fatal |
| Chronological split | 39,752 fitting; 9,938 validation; 9,938 held-out test |
| Feature policy | Fit-only mutual information; 451 contextual candidates; 140 selected raw predictors |
| Encoding | 404 encoded inputs; one-hot `max_categories=15`, `min_frequency=250` |
| Strict XGBoost | `max_depth=2`, `n_estimators=240`, `learning_rate=0.1`, `min_child_weight=5` |
| Sampling / regularisation | `subsample=0.75`, `colsample_bytree=1.0`, `reg_alpha=0.2`, `reg_lambda=10.0` |
| Operating point | Validation-only `recall_spec_ge_60`; threshold 0.621 |
| Held-out results | Balanced accuracy 61.6%; Serious/Fatal recall 70.8%; specificity 52.4%; precision 27.7%; ROC-AUC 0.646; PR-AUC 0.307 |
| Uncertainty | 500 held-out-row bootstrap resamples, not repeated cross-validation |
| Oversampling | No ADASYN or other synthetic oversampling in the reported strict model |

The expanded top-160 comparators, attribution, calibration and feature-removal diagnostics use a broader retrospective matrix. They are not strict-model results. Imagery, terrain and composite-feature methods are retained in the paper without establishing inclusion in the final 140 predictors or incremental performance benefit.

Exact reproduction requires the final cohort and row-grain audit; source release/vintage identifiers; ordered raw/encoded feature names; collision-aware split IDs, dates and tie rules; all search configurations/seeds; fitted preprocessing/model objects; held-out labels/probabilities; bootstrap code; and a pinned runtime. Unspecified values must not be inferred from library defaults.

## Directory guide

| Directory | Purpose |
| --- | --- |
| [Paper2](Paper2/README.md) | Main weather, metadata, imagery, terrain and merge workflows |
| [Paper2/ColabNoteBooks](Paper2/ColabNoteBooks/README.md) | Earlier acquisition variants, cleaning and severity-model prototypes |
| [Accidents](Accidents/README.md) | Collision/image joins and archived crash tables |
| [Data](Data/README.md) | Earlier collision tables, coordinates and London grid |
| [Data/ImageFeatures](Data/ImageFeatures/README.md) | Shared image descriptors retained for crash enrichment |
| [Paper2/Map](Paper2/Map/README.md) | Paper 2 descriptive interactive map |
| [docs](docs/README.md) | Earlier browser map and bundled processed collision table |

Every retained directory has its own file inventory, inputs, outputs, execution guidance and limitations.

## Root files

| File | Purpose / inputs → outputs |
| --- | --- |
| [AccidentDataForArticle.ipynb](AccidentDataForArticle.ipynb) | Earlier severity correlations and model diagnostics from `final_merged_cleaned_data.csv`; includes confusion-matrix plots. Not the final strict XGBoost experiment. |
| [MLPForArticleFinal.ipynb](MLPForArticleFinal.ipynb) | Earlier severity MLP/comparator evaluation; reads the same named table and exports per-fold/repeat metrics, summaries and predictions. Random/repeated validation differs from the paper. |
| [CSVOps.ipynb](CSVOps.ipynb) | Historical CSV cleaning, merging, history and weather-reconciliation cells with many intermediate inputs/outputs. Select cells; this is not one sequential pipeline. |
| [CreateInputNN.ipynb](CreateInputNN.ipynb) | Segmentation/object/image-statistics extraction and collision-enrichment scratchwork → `processed_features_*.csv`. No perception-ranking target is required. |
| [EnrichAccidentsWithImageFeatures.ipynb](EnrichAccidentsWithImageFeatures.ipynb) | Collision/image matching, weather and mutual-information exploration using collision tables, metadata mapping and image descriptors. Renamed to describe its crash-enrichment role. |
| [GetHistoryForecast.ipynb](GetHistoryForecast.ipynb) | Historical-forecast retrieval and merges → JSONL/CSV diagnostics. The root copy uses the unusual environment variable `OPEN_METEO_`; inspect its configuration. |
| [GetWeatherWithKey.ipynb](GetWeatherWithKey.ipynb) | Open-Meteo acquisition, batch splitting, timestamp checks and precipitation backtracking. More focused variants are under `Paper2/`. |
| [ImageSegmentation.py](ImageSegmentation.py) | Azure-backed Mask2Former inference → masks, class JSON and overlays. Configure checkpoint, storage prefixes and credentials. |
| [YoloV10.py](YoloV10.py) | Azure-backed YOLO image detection and result handling. Configure model/image prefixes before execution. |
| [coco_classes.txt](coco_classes.txt) | Object-class names for image interpretation, not the final selected-predictor manifest. |
| [generate_london_grid.py](generate_london_grid.py) | London boundary/grid generation → `greater_london_grid_50m_full.csv`; contains notebook `!pip` syntax. |
| [random_sampling.py](random_sampling.py) | Grid sampling and Street View metadata/image acquisition through Google/Azure. Contains notebook syntax and makes remote API requests. |
| [download_images.py](download_images.py) | Four-view grid-image acquisition and Azure uploads; configure inputs, prefixes and credentials. Contains notebook syntax. |
| [UploadLocalToAzure.py](UploadLocalToAzure.py) | Configured local folder → Azure blobs. Inspect overwrite settings and destination before execution. |
| [compare_maps.py](compare_maps.py) | Requested/returned coordinates from Azure metadata → the two coordinate-map HTML exports. |
| [kepler_map.py](kepler_map.py) | Grid CSV → Kepler HTML demonstration; contains notebook syntax. |
| [grid_search_enriched.py](grid_search_enriched.py) | Earlier MLP/ADASYN severity search using `enriched_collision_data_100m_new.csv`; not the manuscript XGBoost search. |
| [check_random_map.html](check_random_map.html) | Saved image-sampling coordinate diagnostic; not model predictions. |
| [requested_coords_map.html](requested_coords_map.html) | Saved requested-coordinate acquisition diagnostic. |
| [response_coords_map.html](response_coords_map.html) | Saved returned-panorama-coordinate diagnostic. |
| [IMPORT_NOTES.md](IMPORT_NOTES.md) | Source provenance, scope cleanup, changes and validation record. |
| [LICENSE](LICENSE) | MIT code licence supplied with the archive; third-party data/model/imagery terms remain separate. |
| [.gitignore](.gitignore) | Local secret, environment, cache and machine-metadata exclusions. |
| [README.md](README.md) | Repository scope, study specification and navigation. |

## Setup and execution

No verified environment lockfile was supplied. Use an isolated Python environment or Colab runtime. A starting environment for inspecting ordinary tables and notebooks is:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install jupyterlab pandas numpy scipy scikit-learn matplotlib seaborn tqdm pillow
jupyter lab
```

This is an unpinned inspection setup, not a reproduction environment. Install only the selected workflow's dependencies: Azure SDK/requests for acquisition; OpenCV/scikit-image for image statistics; PyTorch/Transformers or Detectron2 for segmentation; Ultralytics for detection; GeoPandas/Shapely/pyproj/OSMnx/rasterio for geography; pyarrow for feature merging; TensorFlow/LightGBM/imbalanced-learn for earlier models. Segmentation alternatives need different framework/CUDA combinations.

Relative paths resolve from the **kernel working directory**, not necessarily the notebook directory. Other cells contain `/content/`, mounted Drive or original-machine paths. Stage copies of required inputs in a scratch directory and inspect constants before running cells. Notebooks contain alternative implementations, repeated installs, exploratory fragments and remote writes; they are not a run-all pipeline.

The retained script exports `download_images.py`, `generate_london_grid.py`, `kepler_map.py`, `random_sampling.py` and `Paper2/YOLOV10.py` contain `!pip` syntax and are notebook-oriented. `Accidents/create_nn_input.py` also expects a preconfigured `AZURE_CONNECTION_STRING` variable. Neither case is a turnkey plain-Python entry point.

Secrets were replaced before the initial commit. Entry points use different names, including `AZURE_STORAGE_CONN_STR`, `AZURE_CONNECTION_STRING`, `AZURE_CONN_STR`, `STREET_VIEW_API_KEY`, `OPEN_METEO_API_KEY` and `HF_TOKEN`; some still have local/empty connection settings. Configure only those read by your selected cells. Do not commit replacements for `YOUR_...`. `.env` loading is not automatic. Acquisition may incur API charges and uploads may overwrite blobs; neither was executed for this cleanup.

## Scientific workflow

1. Version the collision table and establish collision-versus-casualty row grain, identifiers and Serious/Fatal target mapping.
2. Reconcile roadway/time fields and enrich weather, points of interest, exposure and strictly earlier history. Preserve missingness, no-match reasons and source dates.
3. For imagery/terrain, retain request/returned coordinates, panorama ID, capture date, heading and crash linkage. Start with the [Paper2 workflow](Paper2/README.md).
4. Audit each predictor's availability at the historical prediction time. Exclude incident outcomes and unavailable administrative fields from a strict contextual policy.
5. Freeze chronological splits, fit ranking/encoding only on fitting rows, select configuration/threshold on validation rows and evaluate the fixed model on held-out rows. Obtain the missing manifests before claiming exact reproduction.
6. Use maps for descriptive inspection, not calibrated probabilities or exposure-adjusted risk.

Bundled collision tables are earlier snapshots with roughly 3,000–30,000 rows. None is identified here as the final 59,628-record table. The unrelated `safety_bin_1_10` label was removed from three shared CSVs during scoping. Older saved model outputs are historical artifacts and have not been revalidated against the revised schemas. See the data READMEs for measured row counts and current columns.

## Provenance and checks

[Import notes](IMPORT_NOTES.md) record the source ZIP, normal-history scope correction and validation. Checks cover file scope, retained values, notebook JSON, ZIP integrity, README coverage and local links. They do not execute training or establish new results. The manuscript is linked rather than copied. Code is supplied under [MIT](LICENSE); imagery, datasets and pretrained models remain subject to their providers' terms.
