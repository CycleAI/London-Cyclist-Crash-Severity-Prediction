# 01 — Collision preparation and prior history

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Harmonize roadway/severity fields, reconcile collision and weather tables, and compute prior-collision histories. The expanded reconciliation notebook replaces the earlier root CSVOps collection; focused cleaning/history notebooks remain useful entry points.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [compute_prior_collision_history.ipynb](compute_prior_collision_history.ipynb) | Compute local prior-collision histories. — `all_59k_accidents_no_history.csv` → `all_59k_accidents_complete_final_cleaned.csv`; spatial radii/lookbacks and severity-specific counts. Audit unique-event, strict-time and incomplete-history rules. |
| [harmonize_road_and_severity_fields.ipynb](harmonize_road_and_severity_fields.ipynb) | Harmonise year-specific roadway/police fields. — `merged_collision_data.csv` → `cleaned_collision_data.csv`; coalesces canonical/truncated columns, including speed and severity fields. |
| [reconcile_collision_weather_and_context_tables.ipynb](reconcile_collision_weather_and_context_tables.ipynb) | Historical multi-step data reconciliation and engineered variables. — Many intermediate crash/weather/history files → cleaned tables, UTC checks, severe-history composites, exposure-normalised history, speed proxy and bank-holiday fields. Alternative scratch cells are not a single pipeline. |
| [repair_missing_weather_and_collision_fields.ipynb](repair_missing_weather_and_collision_fields.ipynb) | Reconcile weather gaps and collision fields. — Earlier crash CSVs and missing-weather JSONL → cleaned/updated tables and summaries. Some cells overwrite an input CSV. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

Inputs include yearly police extracts, collision CSVs, missing-weather JSONL and intermediate context/exposure tables. Some earlier tables are in `data/collision_tables/`; yearly extracts and most `all_59k_*` inputs are not bundled. Outputs are harmonized/cleaned/enriched CSVs and consistency diagnostics. Some cells overwrite intermediates.

Use Jupyter/Colab with pandas, NumPy, SciPy, scikit-learn, requests and tqdm as required by selected cells; geometry/history cells can require spatial libraries. Follow the shared scratch-staging guide. Read constants in each cell: the reconciliation notebook contains successive alternative repairs, not one linear pipeline.

## Validation and scientific limits

Confirm collision-versus-casualty row grain, duplicate IDs and severity encoding. History must include strictly earlier events with declared radii/lookbacks and reporting delays; pre-2013 coverage is incomplete. The manuscript discusses 50–500 m radii and 1–5 year windows, but inspect actual cells before claiming correspondence. Composite variables and repaired weather must be checked against source records, not accepted because an output filename says final.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
