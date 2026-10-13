# Historical severity-model experiments

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Earlier severity MLP, neural, TabNet, LightGBM and related experiments. Names now describe their purpose instead of claiming to be final. None implements the paper’s identified final strict chronological XGBoost experiment.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [mlp_parameter_and_feature_search.ipynb](mlp_parameter_and_feature_search.ipynb) | Earlier severity MLP parameter/feature searches. — Mapped/cleaned collision CSVs → printed model diagnostics. Includes ADASYN/random splits, unlike the final strict benchmark. |
| [mlp_repeated_validation.ipynb](mlp_repeated_validation.ipynb) | Earlier severity MLP/comparator evaluation; reads the same named table and exports per-fold/repeat metrics, summaries and predictions. Random/repeated validation differs from the paper. |
| [mlp_search_enriched_100m.py](mlp_search_enriched_100m.py) | Earlier MLP/ADASYN severity search using `enriched_collision_data_100m_new.csv`; not the manuscript XGBoost search. |
| [neural_and_lightgbm_comparators.ipynb](neural_and_lightgbm_comparators.ipynb) | Earlier severity neural/LightGBM experiments. — Merged crash context → historical validation/holdout metrics and predictions. Uses its own feature and resampling choices; not the paper's expanded comparator release. |
| [neural_models_and_schema_harmonization.ipynb](neural_models_and_schema_harmonization.ipynb) | Earlier crash-schema harmonisation and neural experiments. — `merged_collision_data_speed_limit.csv` → model diagnostics and retained-feature correlation export; historical feature/split policy. |
| [severity_correlations_and_comparators.ipynb](severity_correlations_and_comparators.ipynb) | Earlier severity correlation/MLP/comparator analysis. — `final_merged_cleaned_data.csv` → confusion matrices, per-fold/repeat summaries and predictions. Earlier random/repeated evaluation, not final XGBoost. |
| [yearly_merge_and_class_weighted_neural_model.ipynb](yearly_merge_and_class_weighted_neural_model.ipynb) | Alternative crash merge/cleaning/neural workflow. — Yearly crash CSVs → merged table and fold/training diagnostics with class weighting. |
| [yearly_merge_and_neural_model.ipynb](yearly_merge_and_neural_model.ipynb) | Earlier yearly crash-table merge and neural model. — Year-specific crash CSVs → `merged_collision_data.csv` and multiclass/severity training diagnostics. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

Inputs include earlier merged/mapped collision tables, year-specific police files and enriched-radius snapshots. Outputs are historical fold/repeat summaries, predictions, confusion matrices, feature rankings and model diagnostics. A similarly named CSV does not identify an evaluated cohort.

Use an isolated Jupyter/Python environment with pandas, NumPy, SciPy, scikit-learn, matplotlib, seaborn and the selected TensorFlow, PyTorch/TabNet, LightGBM or imbalanced-learn packages. Source retains its original filenames; stage intended data in scratch space. The merged severity/comparator notebook includes the entire removed root notebook followed by additional corrected reporting variants.

## Interpretation

These models use differing random/repeated splits, multiclass/binary targets, class weights, ADASYN, feature sets and thresholds. The strict paper benchmark is chronological and does not use synthetic oversampling. Explicitly map Serious/Fatal to the positive encoded class and audit preprocessing leakage. The separate 100 m MLP script is retained because it targets a different table from the broader search notebook.

Results embedded in these files are earlier artifacts, not a recomputation of the manuscript's reported 61.6% balanced accuracy. Exact final reproduction remains blocked by missing experiment artifacts, not by directory organization. Training was not executed during cleanup.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
