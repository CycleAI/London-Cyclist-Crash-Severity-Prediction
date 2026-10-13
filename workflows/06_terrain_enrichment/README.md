# 06 — Road terrain and slope enrichment

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Estimate roadway slope from collision locations, mapped roads and Environment Agency elevation data. This is an extended-enrichment component, not evidence that slope entered the final top-140 model.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [extract_road_slope.ipynb](extract_road_slope.ipynb) | `merged_dataset_2.csv` + OSM roads + Environment Agency LiDAR → slope-enriched collision CSVs and quality flags; includes successive refinement cells. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

The notebook consumes `merged_dataset_2.csv`, OpenStreetMap road geometry and Environment Agency LiDAR/elevation rasters; these full inputs are not bundled. Outputs are slope-enriched collision CSVs and quality flags. It contains successive refinement cells.

Use Jupyter with pandas, NumPy, SciPy, GeoPandas, Shapely, pyproj, OSMnx, rasterio and requests as required. Stage road/terrain data in scratch space, configure paths and CRS, and inspect the selected cell version before fetching data or exporting results.

## Checks

The appendix describes 20 m profiles on each side, 2 m spacing and robust Theil–Sen fitting, with distance, coverage, bridge/tunnel and grade flags. Verify chosen cells against these settings. Retain snapped-road distance, elevation source vintage, missing raster coverage and quality exclusions. No terrain computation or predictive-benefit test was run during documentation.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
