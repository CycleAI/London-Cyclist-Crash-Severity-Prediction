# 07 — Descriptive analysis and diagnostics

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Inspect distributions, image coverage, coordinates and exploratory feature rankings. These outputs are descriptive and historical; full-table MI scores are not the frozen fit-only predictor manifest or causal effects.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [compare_requested_and_returned_coordinates.py](compare_requested_and_returned_coordinates.py) | Configured Azure request/response metadata → requested_coords_map.html and response_coords_map.html; local connection placeholder requires configuration. |
| [count_sampling_grid_rows.ipynb](count_sampling_grid_rows.ipynb) | Count the sampling grid. — `greater_london_grid_50m_full.csv` → a printed row count, not a crash count. |
| [explore_mutual_information_and_distributions.ipynb](explore_mutual_information_and_distributions.ipynb) | Earlier MI ranking and distribution plots. — `final_processed_with_interest.csv` → MI CSVs and top-feature plots. Not a frozen fit-only final-model manifest or causal attribution. |
| [inspect_sampled_coordinates.ipynb](inspect_sampled_coordinates.ipynb) | Inspect sampled image coordinates. — Configured Azure image metadata → `check_random_map.html`; acquisition diagnostic. |
| [plot_collision_image_distributions.ipynb](plot_collision_image_distributions.ipynb) | Earlier collision/image feature distributions. — `enriched_collision_data_with_distance.csv` → basic, image, object and segmentation distribution figures. |
| [plot_contextual_distributions.ipynb](plot_contextual_distributions.ipynb) | Earlier contextual-variable distributions. — `all_59k_accidents_archive_weather_poi_final.csv` → paginated `feature_distributions_page_*.png`; sample must be audited against Appendix D. |
| [rank_enriched_features.py](rank_enriched_features.py) | `enriched_collision_data_500m_new.csv` → exploratory mutual-information ranking against `Severity`. It is not the manuscript's frozen fit-only top-140 ranking. |
| [retrieve_london_borough_boundaries.ipynb](retrieve_london_borough_boundaries.ipynb) | Download/prepare borough boundaries. — External boundary data → `london_boroughs.geojson`; record source version. |
| [view_grid_with_image_links.ipynb](view_grid_with_image_links.ipynb) | Grid CSV → Folium `london_points_map.html`, with image-link popups when available. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

Inputs range from bundled grid/image/collision tables to external `all_59k_accidents_archive_weather_poi_final.csv`, Azure metadata and boundary services. Outputs include feature-distribution figures, MI rankings, HTML coordinate maps, boundary GeoJSON and printed checks. Keep output cohort, schema and commit explicit.

Use Jupyter or inspect the selected Python script with pandas, NumPy, SciPy, scikit-learn, matplotlib and seaborn. Maps add Folium/Kepler/GeoPandas/pyproj; Azure diagnostics add azure-storage-blob. `compare_requested_and_returned_coordinates.py` still has a local connection placeholder to configure; it is not a zero-configuration command.

## Checks

Counts of grid points are not crash counts. MI from an entire historical table is not fit-only selection or causal attribution. Saved maps inspect acquisition displacement/coverage rather than prediction. Check fields, coordinate bounds, unique-event counts, sample sizes, missing values and target frequencies against the selected input. Browser exports live under `visualizations/`, while boundary data are centralized under `data/geographic_boundaries/`.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
