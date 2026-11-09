# Cyclist crash severity in Greater London

Code, results and figures for the paper **"Cyclist Crash Severity in Greater London: Multimodal Context, Temporal Validation and Feature Availability"** ([citation to add]).

The study asks whether information known before a crash can tell whether a cyclist's injury will be serious or fatal rather than slight. It uses 41,606 police-recorded cyclist crashes in Greater London from November 2016 to June 2025, when every crash follows the same injury-based definition of severity.

## Main results (test part, 6,241 crashes from April 2024 to June 2025)

| Model | Balanced accuracy | 95% interval | ROC-AUC |
|---|---|---|---|
| Full model (street features + cyclist age, sex and age group) | 58.7% | 57.3% to 60.3% | 0.619 |
| Street model (street features only) | 57.4% | 55.9% to 59.0% | 0.600 |
| Full model + perceived safety score (mean) | 59.0% | 57.7% to 60.6% | 0.619 |

- In the tenth of test crashes with the highest predicted risk, 36.9% were serious or fatal, against 10.2% in the lowest tenth.
- The cyclist's age and the earlier serious share of crashes in similar road settings were the most important inputs.
- Adding a perceived safety score from street-level images did not change balanced accuracy (+0.3 points; 95% interval −0.3 to +0.9).

## Folder structure

```
cyclist-severity-london/
├── README.md                 This file
├── requirements.txt          Python packages
├── notebooks/                The three notebooks, in the order they are run
├── data/                     Description of the data sources and of the shared data files
├── results/                  Tables, feature dictionary, predictions and SHAP values
├── figures/
│   ├── main/                 Figures in the main text of the paper
│   └── appendix/             Figures in the appendices
├── models/                   The trained final models
```

Each folder has its own README with details.

## How to reproduce

1. **Build the data set:** run `notebooks/stage1_dataset.ipynb`. It contains the data preparation workflow. The missing input handoff described below must be resolved before stage 2.
2. **Train and test the models:** upload the feature file, the feature catalog, the feature journey file, the raw crash file and the borough boundaries to a Kaggle data set, and run `notebooks/stage2_final_paper.ipynb` with GPU and internet on (about 2 hours). It writes everything in `results/` and `models/`, and the first version of the charts.
3. **Make the paper figures:** run `notebooks/paper_charts.ipynb` on a laptop. It reads the saved results only and redraws every figure in the same style.

Seeds are specified in the notebooks, but exact results also depend on the runtime and input versions.

## Data availability

The crash data are police-recorded STATS19 collisions. The other sources are listed in `data/README.md`, with their licences. Street View images are not shared, because their terms of use do not allow it.

## Citation

[Citation of the paper to add]

## Licence

[Licence of the code and results to add]

## Contact

[Contact to add]

## Reproduction boundary

The supplied stage-1 notebook does not write all the filenames expected by
stage 2 (`collisions_final_features.csv`, `feature_catalog.csv` and
`feature_journey.xlsx`). Recover or prepare these inputs before attempting
training; the current package is not a complete automatic rebuild. Saved
predictions, results, figures and fitted models remain available for inspection.
Notebook outputs are cleared. See [public release notes](../PUBLIC_RELEASE.md).
