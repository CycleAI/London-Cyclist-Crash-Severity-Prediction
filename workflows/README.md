# Paper 2 enrichment and inspection workflows

[Repository overview](../README.md) · [Running guide](../documentation/RUNNING_WORKFLOWS.md)

These are the consolidated entry points for the supplied enrichment and inspection code. Numbers indicate task groups and a broad reading order, not an executable end-to-end pipeline. Different cells require different inputs; reconciliation can revisit earlier stages. All current workflow files remain archived research implementations.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [01_collision_preparation/](01_collision_preparation/README.md) | 01 — Collision preparation and prior history |
| [02_weather_enrichment/](02_weather_enrichment/README.md) | 02 — Weather enrichment and alignment checks |
| [03_imagery_acquisition/](03_imagery_acquisition/README.md) | 03 — Sampling and imagery acquisition |
| [04_image_feature_extraction/](04_image_feature_extraction/README.md) | 04 — Segmentation, detection and image descriptors |
| [05_collision_image_linkage/](05_collision_image_linkage/README.md) | 05 — Collision, panorama and image-feature linkage |
| [06_terrain_enrichment/](06_terrain_enrichment/README.md) | 06 — Road terrain and slope enrichment |
| [07_descriptive_analysis/](07_descriptive_analysis/README.md) | 07 — Descriptive analysis and diagnostics |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Reading order and shared execution rules

1. Establish collision row grain, severity mapping, source vintage and prior-history rules.
2. Choose archive weather versus historical forecasts and audit timestamp alignment.
3. Choose grid-based or crash-centred image acquisition and record success/missingness.
4. Extract descriptors with a documented detector/segmentation checkpoint and image inventory.
5. Join using audited event/image keys; preserve date/displacement and unmatched rows.
6. Add terrain where available and retain quality flags.
7. Inspect distributions, coverage and maps before evaluating a fixed model.

See [environment and input staging](../documentation/RUNNING_WORKFLOWS.md). Folder numbers do not enforce dependencies, and a scratch notebook may revisit several stages. Notebook/script source paths and stored outputs remain historical. Reproduction of final paper metrics requires artifacts absent from this archive; earlier model experiments live under `archive/model_experiments/`.

Core inspection uses Jupyter, pandas, NumPy and SciPy. Each leaf README identifies workflow-specific libraries, external inputs and output behaviour. Use scratch copies and record exact cells rather than running every installation/acquisition cell.
