# Paper 2 manuscript and release boundary

[Documentation](README.md) · [Repository overview](../README.md)

Reference: [Article 2 Latest.docx](PRIVATE_REFERENCE_NOT_PUBLISHED), modified 8 October 2026, reviewed 14 October 2026: **Cyclist Crash Severity in Greater London: Multimodal Context, Temporal Validation and Feature Availability**.

The outcome is Serious/Fatal versus Slight injury severity conditional on a recorded cyclist crash. This crash-only analysis does not estimate crash occurrence, trip risk, or collision rates per kilometre. Source code and data are linked to this paper's extended enrichment programme, but no bundled table is established as the final analytical cohort.

## Manuscript specification

These values are reported in the manuscript, not recomputed from this checkout:

| Item | Reported specification |
| --- | --- |
| Records | 59,628 Greater London cyclist-crash modelling records, 2013–2025 |
| Outcome | 50,268 Slight; 9,360 Serious/Fatal |
| Chronological split | 39,752 fitting; 9,938 validation; 9,938 held-out test |
| Feature policy | Fit-only mutual information; 451 contextual candidates; 140 selected raw predictors |
| Encoding | 404 encoded inputs; one-hot `max_categories=15`, `min_frequency=250` |
| Strict XGBoost | `max_depth=2`, `n_estimators=240`, `learning_rate=0.1`, `min_child_weight=5` |
| Sampling / regularisation | `subsample=0.75`, `colsample_bytree=1.0`, `reg_alpha=0.2`, `reg_lambda=10.0` |
| Operating point | Validation-only `recall_spec_ge_60`; threshold 0.621 |
| Held-out results | Balanced accuracy 61.6%; Serious/Fatal recall 70.8%; specificity 52.4%; precision 27.7%; ROC-AUC 0.646; PR-AUC 0.307 |
| Uncertainty | 500 held-out-row bootstrap resamples, not repeated cross-validation |
| Oversampling | No ADASYN or other synthetic oversampling in the reported strict model |

The expanded top-160 comparators, attribution, calibration and feature-removal diagnostics use a broader retrospective matrix. They are not strict-model results. Imagery, terrain and composite-feature methods are retained in the paper without establishing inclusion in the final 140 predictors or incremental performance benefit.

Exact reproduction requires the final cohort and row-grain audit; source release/vintage identifiers; ordered raw/encoded feature names; collision-aware split IDs, dates and tie rules; all search configurations/seeds; fitted preprocessing/model objects; held-out labels/probabilities; bootstrap code; and a pinned runtime. Unspecified values must not be inferred from library defaults.


## What the archive does and does not supply

The archive contains enrichment components, earlier severity models, intermediate tables and descriptive maps. No identified implementation of the final strict XGBoost search, frozen top-140 feature manifest, fitted encoder, collision-aware split manifest, selected model or held-out probability archive was supplied. Moving or renaming files does not recover these artifacts.

All files in `archive/model_experiments/` are earlier experiments. The workflow folders are the consolidated entry points for the supplied enrichment code, not a verified reproduction pipeline. Existing saved outputs remain historical and were not recomputed. No training or new performance evaluation was performed during repository cleanup.

Imagery acquisition totals and collision-versus-casualty row grain remain unresolved in the manuscript/source package. Retain source vintages, dates, linkage and missingness metadata before claiming prospective feature availability.
