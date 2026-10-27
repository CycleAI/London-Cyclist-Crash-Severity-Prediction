# Notebooks

Run them in this order.

| Notebook | What it does | Where it was run | Main outputs |
|---|---|---|---|
| `01_build_dataset.ipynb` | Cleans and harmonises the police records, keeps one row per collision, links weather, places nearby, deprivation, noise, crash history and the perceived safety score, removes columns not known before a crash | Laptop | `collisions_final_features.csv`, `feature_catalog.csv`, `feature_journey.xlsx` |
| `02_models_and_results.ipynb` | Time split (70% / 15% / 15%), missing values, feature selection, model search (XGBoost, LightGBM, elastic-net logistic regression), final model, all model versions, SHAP values, breakdowns and maps | Kaggle (GPU) | Everything in `results/` and `models/` |
| `03_paper_charts.ipynb` | Redraws every figure of the paper from the saved results, in one style | Laptop | Everything in `figures/` |

## Settings to change before running

- `01_build_dataset.ipynb`: the input folders at the top of the notebook.
- `02_models_and_results.ipynb`: the Kaggle input folder (`INPUT_FOLDER`) in Section 1.
- `03_paper_charts.ipynb`: `FOLDER` (the folder with the saved results) and `BOROUGHS_GPKG` in cell 1. Set `SHOW_TITLES = False` for figures without titles.

## Notes

- Notebook 02 takes about 2 hours on Kaggle with a GPU. Most of the time is the elastic-net search.
- The seeds are fixed (101, 202, 303, 404 and 505), so the results are the same on every run.
