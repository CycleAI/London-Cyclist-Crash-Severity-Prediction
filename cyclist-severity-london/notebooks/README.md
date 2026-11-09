# Notebooks

Run them in this order.

| Notebook | What it does | Where it was run | Main outputs |
|---|---|---|---|
| `stage1_dataset.ipynb` | Cleans and harmonises the police records, keeps one row per collision, links weather, places nearby, deprivation, noise, crash history and the perceived safety score, removes columns not known before a crash | Laptop | Intermediate preparation; the expected stage-2 inputs are not all emitted by this notebook |
| `stage2_final_paper.ipynb` | Time split (70% / 15% / 15%), missing values, feature selection, model search (XGBoost, LightGBM, elastic-net logistic regression), final model, all model versions, SHAP values, breakdowns and maps | Kaggle (GPU) | Everything in `results/` and `models/` |
| `paper_charts.ipynb` | Redraws every figure of the paper from the saved results, in one style | Laptop | Everything in `figures/` |

## Settings to change before running

- `stage1_dataset.ipynb`: the input folders at the top of the notebook.
- `stage2_final_paper.ipynb`: the Kaggle input folder (`INPUT_FOLDER`) in Section 1.
- `paper_charts.ipynb`: `FOLDER` (the folder with the saved results) and `BOROUGHS_GPKG` in cell 1. Set `SHOW_TITLES = False` for figures without titles.

## Notes

- Notebook 02 takes about 2 hours on Kaggle with a GPU. Most of the time is the elastic-net search.
- Seeds are specified (101, 202, 303, 404 and 505); exact results also depend on the runtime and input versions.

## Reproduction boundary

The supplied stage-1 notebook does not write all the filenames expected by
stage 2 (`collisions_final_features.csv`, `feature_catalog.csv` and
`feature_journey.xlsx`). Recover or prepare these inputs before attempting
training; the current package is not a complete automatic rebuild. Saved
predictions, results, figures and fitted models remain available for inspection.
Notebook outputs are cleared. See [public release notes](../../PUBLIC_RELEASE.md).
