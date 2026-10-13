# 02 — Weather enrichment and alignment checks

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Retrieve archive weather or historical forecasts according to the intended feature definition, then inspect alignment. These endpoints are not interchangeable. The archive-weather notebook also contains broader reconciliation and backtracking cells.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [backtrack_precipitation.ipynb](backtrack_precipitation.ipynb) | `all_59k_accidents_complete_final_2_cleaned.csv` → `open_meteo_archive_precipitation_backtracked.jsonl`, searching backwards for precipitation. |
| [check_weather_alignment.ipynb](check_weather_alignment.ipynb) | Audit matched weather timing/coordinates. — `enriched_collision_data_with_weather.csv` → printed consistency summaries. This alone does not establish historical availability. |
| [retrieve_archive_weather.ipynb](retrieve_archive_weather.ipynb) | Crash CSV → Open-Meteo archive JSONL/CSV, timestamp/missingness checks and merges. Review UTC conversion and time windows. |
| [retrieve_historical_forecasts.ipynb](retrieve_historical_forecasts.ipynb) | Crash timestamps/coordinates → historical-forecast JSONL and matched/unmatched CSVs; reads OPEN_METEO_API_KEY. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

Inputs are crash coordinates/timestamps and earlier weather JSONL/CSV. Outputs include archive/forecast response JSONL, precipitation backtracking results, matched tables and error/missingness diagnostics. `all_59k_accidents_complete_final_2_cleaned.csv` and many other referenced intermediates are external to this checkout.

Use Jupyter/Colab, pandas, NumPy, requests and tqdm. Configure the selected endpoint and `OPEN_METEO_API_KEY`; inspect call budgets, retries, batch paths and UTC settings. The corrected historical-forecast copy reads the full key variable name. Run only selected cells with scratch outputs.

## Validation and scientific limits

Check UTC/daylight-saving conversion, source/request coordinates, archive versus historical-forecast product, aggregation windows, precipitation lookback and missingness. A successful response does not establish historical availability at the crash time. The focused backtracking notebook remains useful even though archive-weather scratch cells contain related code. Distinct older batching/weather variants are kept under `archive/weather_and_routing_variants/`.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
