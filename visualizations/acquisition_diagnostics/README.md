# Saved imagery-acquisition coordinate maps

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Saved Kepler-style coordinate maps used to inspect image sampling and requested/returned panorama locations. These are diagnostic exports, not model predictions or live acquisition status.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [check_random_map.html](check_random_map.html) | Saved image-sampling coordinate diagnostic; not model predictions. |
| [requested_coords_map.html](requested_coords_map.html) | Saved requested-coordinate acquisition diagnostic. |
| [response_coords_map.html](response_coords_map.html) | Saved returned-panorama-coordinate diagnostic. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Open and interpret

Serve the repository root as described in the parent README and navigate to the desired HTML file under `visualizations/acquisition_diagnostics/`. These are saved exports with embedded map data and external browser/tile dependencies, including public Mapbox browser tokens. No Python runtime or regeneration is needed just to inspect an export.

Compare requested coordinates with returned panorama coordinates to inspect displacement and spatial coverage. The sampled-coordinate view supports the same acquisition audit. Check source timestamps, counts, coordinate bounds and provider availability before using screenshots. Saved files do not prove current imagery availability or final-cohort linkage.

To regenerate, inspect `workflows/07_descriptive_analysis/compare_requested_and_returned_coordinates.py` and `inspect_sampled_coordinates.ipynb`; they require configured Azure metadata inputs. Generated outputs should be saved in a scratch run directory. No regeneration or deployment was performed during this cleanup.
