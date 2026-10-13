# Notebook 06: Stage 2 Prediction Models — Main Results

This notebook trains and evaluates four machine learning models (Deeper MLP, XGBoost, LightGBM and CatBoost) to predict perceived cycling safety classes from street-level visual features. Models are evaluated on two targets: the GPT-5.2 synthetic safety ranking and the human crowdsourced safety ranking. It produces the main prediction results reported in Table 8 of the paper, the per-class confusion matrices, the ablation analysis and the balanced accuracy bar chart.

---

## Recommended Environment

This notebook was developed and run on **Kaggle** using a GPU accelerator (Tesla P100). Running on Kaggle is strongly recommended since the full pipeline including ablation analysis takes approximately 4 hours with GPU. Running on CPU is possible but will be significantly slower.

Alternatively, the notebook can be run on **Google Colab** with a GPU runtime. Local execution is possible but not recommended given the runtime.

---

## Input Files

The notebook requires three input files.

| File | Where to get it |
|---|---|
| `processed_features_merged_02_06_26.csv` | [Download from Google Drive](PRIVATE_REFERENCE_NOT_PUBLISHED) |
| `gpt_trueskill_rankings_200k_20_06_26.csv` | Available in the `data/` folder of this repository |
| `human_trueskill_rankings_final_20_06_26.csv` | Available in the `data/` folder of this repository |

Download `processed_features_merged_02_06_26.csv` from the Google Drive link above and place it in the same location as the other two files before running the notebook.

---

## How to Run on Kaggle

**Step 1:** Go to [kaggle.com](https://www.kaggle.com) and create a new notebook.

**Step 2:** Upload the three input files as a Kaggle dataset. Go to Datasets, click New Dataset, upload the three CSV files and name the dataset `insumos2` under your username. The notebook expects them at:

```
/kaggle/input/datasets/lsestudent/insumos2/processed_features_merged_02_06_26.csv
/kaggle/input/datasets/lsestudent/insumos2/gpt_trueskill_rankings_200k_20_06_26.csv
/kaggle/input/datasets/lsestudent/insumos2/human_trueskill_rankings_final_20_06_26.csv
```

If you upload the dataset under a different username or dataset name, update the `KAGGLE_INPUT` path in the configuration cell:

```python
KAGGLE_INPUT = '/kaggle/input/datasets/your-username/your-dataset-name'
```

**Step 3:** Enable GPU. In the notebook settings panel on the right, set Accelerator to GPU P100 or GPU T4.

**Step 4:** Copy the notebook contents into your Kaggle notebook and run all cells sequentially.

---

## How to Run on Google Colab

**Step 1:** Open [colab.research.google.com](https://colab.research.google.com) and create a new notebook.

**Step 2:** Download the features file from the Google Drive link above and upload it to your Google Drive or directly to the Colab session storage alongside the two ranking CSVs from this repository.

**Step 3:** Update the `KAGGLE_INPUT` path in the configuration cell to point to where you uploaded the files. For example:

```python
KAGGLE_INPUT = '/content/drive/MyDrive/cycling_safety_data'
```

**Step 4:** Enable GPU. Go to Runtime, Change runtime type, select GPU.

**Step 5:** Run all cells sequentially.

---

## Configuration

The configuration cell at the top of the notebook controls all key parameters. The values used to produce the paper results are already set as defaults. Do not change these unless you are intentionally running a sensitivity analysis.

| Parameter | Default | Description |
|---|---|---|
| `SIGMA_WEIGHTING` | `1/sigma^2` | Sample weighting scheme. Inverse sigma squared is recommended and was used in the paper. |
| `PEARSON_THRESHOLD_GPT` | `0.03` | Pearson correlation threshold for GPT feature selection. Features with absolute correlation below this are dropped. |
| `PEARSON_THRESHOLD_HUMAN` | `0.03` | Same threshold for human feature selection. |
| `NUM_BINS` | `3` | Number of safety classes. |
| `BINNING_STRATEGY` | `qcut` | Quantile-based binning to produce equal-sized classes. |
| `N_SPLITS` | `5` | Number of folds per cross-validation partition. |
| `N_PARTITIONS` | `3` | Number of independent CV partitions. Total evaluations per model: 3 x 5 = 15. |
| `EPOCHS` | `150` | Maximum training epochs for the MLP. |
| `PATIENCE` | `20` | Early stopping patience for the MLP. |
| `N_ITER_SEARCH` | `12` | Number of iterations for tree model hyperparameter search. |

---

## Outputs

The notebook displays all results inline and does not save files to disk. To save figures, add `fig.savefig(...)` calls after each plot. The following results are produced:

- Results summary table: balanced accuracy mean and standard deviation for all four models on both GPT and human targets.
- Per-class confusion matrices for the best model per target (LightGBM for GPT, CatBoost for Human).
- Ablation analysis: balanced accuracy drop when each feature family is removed.
- Balanced accuracy bar chart comparing all models across both targets.

---

## Expected Results

The confirmed results from the paper are shown below for reference. If your results differ slightly this is expected due to random seed variation in the cross-validation partitioning.

| Model | GPT Balanced Accuracy | Human Balanced Accuracy |
|---|---|---|
| Deeper MLP | 61.3% +/- 0.7% | 41.8% +/- 0.8% |
| XGBoost | 62.7% +/- 0.4% | 42.3% +/- 1.1% |
| LightGBM | 62.8% +/- 0.5% | 42.2% +/- 0.6% |
| CatBoost | 62.8% +/- 0.3% | 42.7% +/- 0.2% |
| Random baseline | 33.3% | 33.3% |

---

## Runtime

Approximate runtimes on different hardware:

| Environment | Approximate runtime |
|---|---|
| Kaggle GPU (P100) | 4 hours |
| Google Colab GPU (T4) | 5 to 6 hours |
| CPU only | 12 hours or more |

The MLP training and the ablation analysis account for most of the runtime.

---

## Dependencies

All required packages are pre-installed on Kaggle and Google Colab. If running locally, install with:

```bash
pip install pandas numpy scikit-learn matplotlib lightgbm xgboost catboost tensorflow scipy
```
