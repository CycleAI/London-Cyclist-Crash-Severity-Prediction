# 05 — Collision, panorama and image-feature linkage

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Associate collisions with imagery and merge descriptor tables. These tools have different row grains, coordinate conventions and matching radii. The 100 m notebook is a focused join; the larger exploratory notebook includes additional weather and MI work.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [attach_collision_ids_to_metadata.ipynb](attach_collision_ids_to_metadata.ipynb) | `streetview_metadata.csv` + `collisions_final.csv` → `streetview_metadata_with_collision.csv` using requested coordinates. Audit repeated coordinates/IDs. |
| [attach_image_time_and_distance_to_collisions.ipynb](attach_image_time_and_distance_to_collisions.ipynb) | `final_file_sin_extra.csv` + `streetview_metadata_compiled.csv` → `merged_dataset_2.csv` with image displacement and time-lag descriptors. |
| [attach_images_to_weather_enriched_collisions.ipynb](attach_images_to_weather_enriched_collisions.ipynb) | Attach image associations to earlier weather data. — `enriched_collision_data_with_weather.csv` + `metadata_images_mapping.csv` → `processed_collisions_with_images.csv`. |
| [build_request_panorama_image_mapping.ipynb](build_request_panorama_image_mapping.ipynb) | Metadata folder → `streetview_metadata.csv`, preserving request/panorama/image linkage fields. |
| [build_strict_image_mapping.ipynb](build_strict_image_mapping.ipynb) | Build image/metadata associations. — Configured Azure metadata/images → `strict_mapping_nofallback.csv`; inspect the selected cell and expected blob layout. |
| [compile_streetview_metadata.ipynb](compile_streetview_metadata.ipynb) | Configured local metadata JSON → `streetview_metadata_compiled.csv`; includes separate Azure upload cells. |
| [explore_collision_image_and_weather_joins.ipynb](explore_collision_image_and_weather_joins.ipynb) | Collision/image matching, weather and mutual-information exploration using collision tables, metadata mapping and image descriptors. Renamed to describe its crash-enrichment role. |
| [join_image_features_100m.ipynb](join_image_features_100m.ipynb) | Earlier 100 m nearest-image join; reads `final_merged_cleaned_data.csv`, `metadata_images_mapping.csv` and `processed_features_conf_0.7.csv`; writes `enriched_collision_data_100m.csv`. |
| [join_image_features_500m.py](join_image_features_500m.py) | `final_mapped_accidents.csv` + `metadata_images_mapping.csv` + extracted `processed_features_conf_0.5_probs.csv` → `enriched_collision_data_500m_new.csv` and diagnostic bad-match output. Averages image headings by location, uses an approximate 500 m nearest-neighbour search and exports matched rows. |
| [join_image_features_with_distance.py](join_image_features_with_distance.py) | Same three inputs → `enriched_collision_data_with_distance.csv` / `enriched_collision_data_with_distance_no_severity.csv`; includes matching-distance and diagnostic variants. Inspect each export's schema before selecting a modelling input. |
| [merge_image_descriptor_tables.ipynb](merge_image_descriptor_tables.ipynb) | `processed_features_conf_0.5_filled_metadata_no_collision.csv` + `image_stats_processed_final_grids_no_collision.csv` → `final_dataset_no_collision.csv`; inner one-to-one merge on request coordinates, panorama and image name. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

Inputs include earlier collision tables, image metadata, descriptor CSVs and external `collisions_final.csv`, `streetview_metadata.csv` or compiled metadata. Outputs include collision-associated metadata, image displacement/time lag, collision/image joins and merged image descriptors. Data schema matters more than an inherited basename.

Use Jupyter/Colab with pandas, NumPy and SciPy; the descriptor merge also uses pyarrow. Azure/mapping variants need Azure SDK/requests. Follow the running guide for staging a 100 m example and the distinct 24-column `final_mapped_accidents.csv` alias required by 500 m scripts. The 100 m notebook retains unmatched rows with missing features; older scripts can export only matches.

`merge_image_descriptor_tables.ipynb` expects `processed_features_conf_0.5_filled_metadata_no_collision.csv` and `image_stats_processed_final_grids_no_collision.csv`, uses an inner one-to-one merge on request coordinates, panorama and image name, and writes `final_dataset_no_collision.csv`. These exact inputs are not bundled; the output is image-level, not the final crash cohort.

## Checks

Check event IDs, duplicated coordinates, exact image-name correspondence, requested versus returned locations, date lag and unmatched records. Some scripts average headings and all numeric metadata, including year. The approximate longitude-scaled 100/500 m joins are historical implementations and are distinct from the paper's POI routing thresholds. One inherited comment says 100 m while an executed radius is 500 m; inspect settings. Do not replace missing descriptors with zero without recording that policy.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
