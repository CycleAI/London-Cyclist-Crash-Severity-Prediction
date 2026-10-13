# Duplicate and version audit — 14 October 2026

[Documentation](README.md) · [Machine-readable path and hash record](reorganization_manifest.json)

The audit compared file SHA-256 hashes, ordered notebook source cells, ordered executable lines, substantive source differences and CSV fields in row order. Filenames such as `Final`, folder location and filesystem timestamps were not treated as evidence of a newer scientific result.

Seventeen redundant or superseded files were removed from the working tree. Canonical files were renamed by purpose and grouped by task. Removed files remain recoverable from base commit `61ed8d60d8bce90398362ac3451fbe39b8751bb0`; Git history was not rewritten. Notebook outputs/metadata can differ even where source is identical. The retained copy's outputs remain historical, not freshly validated results.

## Consolidation decisions

| Removed original path | Retained replacement | Evidence |
| --- | --- | --- |
| `docs/london_boroughs.geojson` | [data/geographic_boundaries/london_boroughs.geojson](../data/geographic_boundaries/london_boroughs.geojson) | Byte-identical borough boundary file. |
| `Paper2/ColabNoteBooks/EnrichAccidentsWithImageFeatures.ipynb` | [workflows/05_collision_image_linkage/explore_collision_image_and_weather_joins.ipynb](../workflows/05_collision_image_linkage/explore_collision_image_and_weather_joins.ipynb) | All ordered notebook source cells are identical; metadata/stored outputs differ. |
| `Paper2/ColabNoteBooks/Get56497PointsFromGrid.ipynb` | [workflows/03_imagery_acquisition/retrieve_sampled_grid_metadata.ipynb](../workflows/03_imagery_acquisition/retrieve_sampled_grid_metadata.ipynb) | All ordered notebook source cells are identical. |
| `Paper2/ColabNoteBooks/GetWeatherWithKey.ipynb` | [workflows/02_weather_enrichment/retrieve_archive_weather.ipynb](../workflows/02_weather_enrichment/retrieve_archive_weather.ipynb) | All ordered notebook source cells are identical. |
| `CreateInputNN.ipynb` | [workflows/04_image_feature_extraction/aggregate_image_and_object_features.ipynb](../workflows/04_image_feature_extraction/aggregate_image_and_object_features.ipynb) | Same ordered executable lines; retained version includes more explanatory comments. |
| `Paper2/ColabNoteBooks/CreateInputNN.ipynb` | [workflows/04_image_feature_extraction/aggregate_image_and_object_features.ipynb](../workflows/04_image_feature_extraction/aggregate_image_and_object_features.ipynb) | Same ordered executable lines; retained version includes more explanatory comments. |
| `AccidentDataForArticle.ipynb` | [archive/model_experiments/severity_correlations_and_comparators.ipynb](../archive/model_experiments/severity_correlations_and_comparators.ipynb) | Entire code is a prefix of the retained notebook, which adds corrected TabNet and reporting variants. |
| `CSVOps.ipynb` | [workflows/01_collision_preparation/reconcile_collision_weather_and_context_tables.ipynb](../workflows/01_collision_preparation/reconcile_collision_weather_and_context_tables.ipynb) | Earlier scratch collection; expanded version replaces the first-value weather flattener with timestamp-aware aggregation and adds later reconciliation/composite cells. Not an exact duplicate or validated final pipeline. |
| `GetHistoryForecast.ipynb` | [workflows/02_weather_enrichment/retrieve_historical_forecasts.ipynb](../workflows/02_weather_enrichment/retrieve_historical_forecasts.ipynb) | Executable code differs only in the credential variable: retained copy reads OPEN_METEO_API_KEY instead of the truncated OPEN_METEO_. |
| `Paper2/ColabNoteBooks/GenerateLondonGrid.ipynb` | [workflows/03_imagery_acquisition/generate_london_sampling_grid.ipynb](../workflows/03_imagery_acquisition/generate_london_sampling_grid.ipynb) | Only a descriptive filename line in the opening docstring differs. |
| `Paper2/GetHistoryForecast.ipynb` | [workflows/02_weather_enrichment/retrieve_archive_weather.ipynb](../workflows/02_weather_enrichment/retrieve_archive_weather.ipynb) | Entire code is a prefix of the retained archive-weather notebook, which adds precipitation backtracking. The separate historical-forecast endpoint notebook is retained. |
| `docs/index.html` | [visualizations/collision_viewer/index.html](../visualizations/collision_viewer/index.html) | Earlier viewer superseded by the version with dual year-field support, integer-year legends and revised POI coordinate lookup; public browser token also differs. |
| `Paper2/YOLOV10.py` | [workflows/04_image_feature_extraction/detect_objects_yolov10.ipynb](../workflows/04_image_feature_extraction/detect_objects_yolov10.ipynb) | Same ordered executable lines; script is a notebook export containing notebook-only syntax. Its explanatory header is covered in the feature-extraction README. |
| `Paper2/ColabNoteBooks/CompareMaps.ipynb` | [workflows/07_descriptive_analysis/compare_requested_and_returned_coordinates.py](../workflows/07_descriptive_analysis/compare_requested_and_returned_coordinates.py) | Same coordinate-map workflow; differences are debug prints, whitespace and nonfunctional credential placeholders. |
| `kepler_map.py` | [workflows/03_imagery_acquisition/generate_london_sampling_grid.ipynb](../workflows/03_imagery_acquisition/generate_london_sampling_grid.ipynb) | Its complete noncomment code block is already present in the retained grid-generation notebook. |
| `random_sampling.py` | [archive/imagery_variants/retrieve_sampled_20000_grid_images.ipynb](../archive/imagery_variants/retrieve_sampled_20000_grid_images.ipynb) | Same ordered executable lines apart from two credential fallback placeholders; keep the notebook form for notebook-only syntax. |
| `Data/final_mapped_accidents.csv` | [data/collision_tables/final_mapped_accidents_with_date_time.csv](../data/collision_tables/final_mapped_accidents_with_date_time.csv) | All 28,914 rows and all 20 columns are identical, in order, to the retained 22-column table after projecting out date and time. The distinct 24-column time-component schema is retained. |

## Similar files deliberately retained

- Radius-specific collision/image tables have different populations and schemas. The 100 m, 300 m and 500 m snapshots are not interchangeable generations.
- The 22-column date/time and 24-column time-component collision tables share fields but contain different information. Both remain with unambiguous filenames. The redundant 20-column view can be reconstructed from the 22-column table without losing any original field or row.
- The merged and deduplicated collision snapshots have different row populations. No undocumented deduplication rule was applied to replace one with the other.
- Image-feature confidence/grid variants differ in coverage, schema and extraction settings.
- Historical-forecast and archive-weather endpoints represent different products. Both have explicit workflow names.
- Sequential/concurrent downloads, grid/crash image inventories, different grid spacing, live/local boundary inputs and Detectron2/Transformers segmentation variants have substantive differences. Alternative versions remain under clearly marked archive folders.
- The enriched 100 m MLP script uses a different input from the broader MLP search notebook. Both are historical models, not the final XGBoost release.
- Short standalone checks and focused processing notebooks remain when they provide a useful entry point, even if a multi-purpose scratch notebook repeats some cells.

## Preservation and paths

Retained data, archives, notebooks and scripts were relocated byte-for-byte. The sole runtime payload edit changes the viewer's relative borough-boundary URL to the shared data location. The older viewer was removed; one copy of the boundary data serves the retained viewer.

Original data basenames inside notebook/script source remain unchanged so archived computations are not silently rewritten. The running guide documents scratch staging and the two historical mapped-collision schemas. Documentation uses the new paths. No model training, cloud mutation or scientific-results regeneration was performed.

For any former path, consult `reorganization_manifest.json`. For a removed file, recovery is possible with `git show BASE_COMMIT:original/path`, substituting the base commit above and the exact path. Removed versions are not copied into another archive directory merely to preserve duplication.

## Validation results

- All 85 relocated non-document payloads other than the viewer are byte-identical to the base commit. The viewer differs only in its shared boundary URL.
- All 52 retained notebooks parse as notebook JSON, and all three CSV ZIP archives pass integrity checks.
- No byte-identical payload files or notebooks with identical ordered source cells remain. Partial overlap in distinct workflows is documented above.
- Every one of the 23 directories has a README covering its files; all local Markdown links resolve.
- All 28,914 rows of the removed 20-column collision view match the retained table's exact projection.
- A temporary local HTTP server returned the retained viewer and its relocated 33-feature borough boundary collection successfully. This does not validate external tile providers or full browser export behaviour.
