# Can a Vision-Language Model Approximate Human Perceptions of Cycling Safety?
## Evidence from Pairwise London Streetscape Judgements

**Authors:** Luís Rita¹²³⁴ · Yolwin Pariaton⁵ · Codrin Bostan¹ · Tiago Tamagusko⁶⁷ · Jenevieve Treadwell⁵ · Adelino Ferreira⁴

**Conference:** CITTA 17th International Conference on Planning Research — Track 3, Coimbra

**Affiliations:**
¹ Instituto Superior Técnico, Universidade de Lisboa
² INESC-ID
³ Instituto de Telecomunicações
⁴ CERIS, Instituto Superior Técnico
⁵ London School of Economics and Political Science
⁶ Polytechnic Institute of Coimbra
⁷ CITTA, University of Porto

---

## Overview

This repository contains all code used to produce the results, figures and analyses reported in the paper. The pipeline is divided into two stages.

**Stage 1** collects and compares pairwise cycling safety judgements from two sources: a crowdsourced human perception poll and a GPT-5.2 vision-language model. Both sources are processed through a TrueSkill Bayesian ranking framework to produce uncertainty-aware safety scores for nearly 20,000 London street-level images.

**Stage 2** uses visual features extracted from those images (panoptic segmentation, object detection and image statistics) to train machine learning models that predict the safety class of each street location.

---

## Repository Structure

```
Paper1_CyclingSafetyPerception/
├── README.md                                           # This file
├── notebooks/
│   ├── 01_gpt_voting_25k_validated_set.ipynb          # GPT-5.2 pairwise voting (25k validated set)
│   ├── 02_gpt_voting_200k_extended_set.ipynb          # GPT-5.2 pairwise voting (200k extended set)
│   ├── 03_prompt_engineering_evaluation.ipynb         # Prompt design evaluation and selection
│   ├── 04_stage1_trueskill_ranking_and_agreement.ipynb # TrueSkill ranking and human-AI agreement
│   ├── 05_feature_extraction_and_cleaning.ipynb       # Feature extraction, cleaning and selection
│   ├── 06_stage2_prediction_models_main_results.ipynb # Stage 2 prediction models (main results)
│   ├── 07_stage2_vote_scaling_analysis.ipynb          # Vote scaling analysis (all four models)
│   ├── 08_complementary_analysis_and_diagnostics.ipynb # Additional analyses and diagnostics
│   ├── 09_spatial_maps_and_borough_choropleth.ipynb   # Spatial maps and borough choropleth
│   └── 10_figure_segmentation_masks.ipynb             # Segmentation mask figure generation
├── data/
│   └── README_data.md                                 # Data description and access instructions
└── outputs/
    └── README_outputs.md                              # Output files description
```

Notebooks are numbered in recommended execution order. Run them sequentially from 01 to 10.

---

## Pipeline Summary

### Stage 1: Human and Synthetic Vote Collection and Ranking

| Notebook | Description |
|---|---|
| `01_gpt_voting_25k_validated_set` | Calls the GPT-5.2 API to generate pairwise safety judgements on the same 25,569 pairs shown to human participants. Handles retries, content policy skips and checkpointing. Produces `gpt52_votes_25k_final.csv`. |
| `02_gpt_voting_200k_extended_set` | Calls the GPT-5.2 API on an additional 200,000 image pairs for the extended ranking used in Stage 2. Produces `gpt52_votes_100k_20_06_26.csv` and `gpt52_votes_100k_2_20_06_26.csv`. |
| `03_prompt_engineering_evaluation` | Evaluates multiple prompt variants on 500 pairs against the human vote distribution. Selects the final prompt configuration used in notebooks 01 and 02. |
| `04_stage1_trueskill_ranking_and_agreement` | Applies the four-stage behaviour-based filtering pipeline to human votes. Runs TrueSkill ranking for both human and GPT-5.2 vote sets. Produces agreement analysis A (vote-by-vote) and B (ranking correlation). Produces `human_trueskill_rankings_final_20_06_26.csv`, `gpt_trueskill_rankings_final_20_06_26.csv` and `gpt_trueskill_rankings_200k_20_06_26.csv`. |

### Stage 2: Visual Feature Extraction and Safety Score Prediction

| Notebook | Description |
|---|---|
| `05_feature_extraction_and_cleaning` | Downloads panoptic segmentation JSONs and YOLO detection outputs from Azure Blob Storage. Constructs the full 785-feature matrix and applies Pearson correlation filtering. |
| `06_stage2_prediction_models_main_results` | Trains and evaluates Deeper MLP, XGBoost, LightGBM and CatBoost on GPT and human safety labels using StratifiedGroupKFold cross-validation. Produces main results (Table 8) and ablation analysis. |
| `07_stage2_vote_scaling_analysis` | Evaluates all four models at seven vote thresholds (20k to 200k) to assess the relationship between synthetic vote volume and prediction performance. |

### Visualisation and Supplementary Analysis

| Notebook | Description |
|---|---|
| `08_complementary_analysis_and_diagnostics` | Agreement analysis diagnostics, sigma scatter plots and additional comparisons. |
| `09_spatial_maps_and_borough_choropleth` | Produces static 2x2 mosaic maps of perceived cycling safety across Greater London for both human and GPT-5.2 rankings. Also produces the borough-level choropleth for Appendix C. |
| `10_figure_segmentation_masks` | Fetches segmentation masks from Azure Blob Storage and produces Figure 7 showing original images alongside their panoptic masks stratified by safety class. |

---

## Data

See `data/README_data.md` for full descriptions of all data files. Raw data files that exceed GitHub file size limits are available on request from the corresponding author.

---

## Credentials and Environment Variables

Notebooks 01 and 02 require API credentials to call the GPT-5.2 endpoint and access Azure Blob Storage. These credentials are not stored in this repository. Before running those notebooks, set the following environment variables:

```bash
# Azure Blob Storage
export AZURE_CONN_STR="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-key-here"
export AZURE_OPENAI_DEPLOYMENT="gpt-5.2"
export DEPLOYMENT_NAME="https://YOUR_AZURE_OPENAI_RESOURCE.openai.azure.com/"
export OPENAI_API_VERSION="2024-12-01-preview"
```

On Windows, set these in your system environment variables or in a `.env` file which is excluded from version control by `.gitignore`.

---

## Requirements

All notebooks were developed and tested in Python 3.10 and 3.13. Install dependencies with:

```bash
pip install azure-storage-blob openai pandas numpy scikit-learn \
    matplotlib geopandas contextily shapely pillow tqdm \
    lightgbm xgboost catboost tensorflow \
    matplotlib-scalebar folium trueskill scipy
```

Notebook 07 was run on Kaggle. The environment is self-contained and no local installation is required for that notebook.

---

## Key Results

| Model | GPT Balanced Accuracy | Human Balanced Accuracy |
|---|---|---|
| Deeper MLP | 61.3% +/- 0.7% | 41.8% +/- 0.8% |
| XGBoost | 62.7% +/- 0.4% | 42.3% +/- 1.1% |
| LightGBM | 62.8% +/- 0.5% | 42.2% +/- 0.6% |
| CatBoost | 62.8% +/- 0.3% | 42.7% +/- 0.2% |
| Random baseline | 33.3% | 33.3% |

Stage 1 agreement on decisive pairs: 64.1% (lift of 14.1% above the 50% random baseline).
Spearman rank correlation between human and GPT-5.2 safety rankings: 0.352 (p < 0.001).

---

## Reproducibility Note

GPT-5.2 is a proprietary model accessed via the Azure OpenAI API. The exact model identifier used was `gpt-5.2`. Votes were collected in June 2026. Because the model may be updated or deprecated over time, exact replication of the vote set cannot be guaranteed. The raw GPT-5.2 vote CSV files are available on request from the corresponding author to support reproducibility without requiring API access.

---

## Citation

If you use this code or data in your work, please cite:

```
Rita, L., Pariaton, Y., Bostan, C., Tamagusko, T., Treadwell, J., & Ferreira, A. (2026).
Can a Vision-Language Model Approximate Human Perceptions of Cycling Safety?
Evidence from Pairwise London Streetscape Judgements.
CITTA 17th International Conference on Planning Research, Coimbra.
```

---

## Contact

For questions about this repository, data access or the paper, please contact the corresponding author:
Adelino Ferreira — CERIS, Instituto Superior Técnico, Universidade de Lisboa.

For questions about the code and notebooks, contact:
Luís Rita (@luisdrita) or Yolwin Pariaton.
