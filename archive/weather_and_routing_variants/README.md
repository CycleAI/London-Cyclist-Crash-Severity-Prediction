# Earlier weather and routing methods

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Earlier weather batching and routing comparisons with distinct source cells or input policies. The Mapbox comparison is not the paper’s OS Open Roads edge-projection procedure.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [archive_weather_batch_and_reconciliation_variants.ipynb](archive_weather_batch_and_reconciliation_variants.ipynb) | Open-Meteo acquisition, batch splitting, timestamp checks and precipitation backtracking. The consolidated weather workflows are under `workflows/02_weather_enrichment/`. |
| [compare_mapbox_routing_distances.ipynb](compare_mapbox_routing_distances.ipynb) | Earlier routing-distance comparison. — `interest_points.csv` → `output_with_distances.csv`, `comparison_absolute.csv`, histograms. Requires a routing token; not the paper's OS Open Roads edge-projection procedure. |
| [earlier_weather_retrieval.ipynb](earlier_weather_retrieval.ipynb) | Earlier weather acquisition alternatives. — `all_59k_accidents_raw.csv` → weather CSV/JSONL and error logs; archive/forecast availability must be distinguished. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and runtime

Weather variants reference earlier collision CSVs and response/error logs and produce weather JSONL/CSV, batch splits, UTC and missingness diagnostics. They have source differences beyond duplicate notebook metadata, so remain available separately from the consolidated weather workflows.

The routing comparison consumes external `interest_points.csv`, writes `output_with_distances.csv` and `comparison_absolute.csv`, and produces comparison histograms. Configure its routing token and coordinate fields before requests.

Use Jupyter with pandas, NumPy, requests, tqdm and plotting libraries as selected cells require. Credential names and hardcoded paths vary; the running guide explains scratch staging. Calls and writes are real side effects, and these variants were not executed during consolidation.

## Scientific limits

The paper's POI method uses a 100 m candidate filter and a 120 m road-route cutoff on OS Open Roads with edge projection. The Mapbox comparison cannot stand in for that method. Weather archive and historical-forecast products differ in availability. Audit vintage, timestamps, coordinates and missingness before using an output as a contextual predictor.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
