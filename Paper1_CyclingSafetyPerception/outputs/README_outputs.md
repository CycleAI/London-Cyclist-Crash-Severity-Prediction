# Outputs

This folder contains figures and result files produced by the pipeline notebooks. Output files are not tracked by version control (see `.gitignore`) since they are fully reproducible from the notebooks and data files.

---

## Figures

| File | Produced by | Description |
|---|---|---|
| `vote_distribution_comparison.pdf` | Notebook 04 | Figure 3. Vote option distribution: human raw, human filtered and GPT-5.2 synthetic votes. |
| `figure5_sigma_scatter_normmu.pdf` | Notebook 04 | Figure 5. Sigma-stratified scatter plots: GPT vs human TrueSkill safety scores (normalised mu). |
| `figure6_streetview_combined.pdf` | Notebook 09 | Figure 6. Representative street-level images per safety class for human and GPT-5.2 rankings. |
| `figure_segmentation_masks.pdf` | Notebook 10 | Figure 7. Original images and panoptic segmentation masks per safety class. |
| `ablation_b1_200k.pdf` | Notebook 06 | Figure 8. Ablation B1: leave-one-group-out feature family contribution. |
| `vote_scaling_all_models.pdf` | Notebook 07 | Figure 9. Effect of synthetic vote volume on prediction performance across all model architectures. |
| `static_human_score_mosaic.pdf` | Notebook 09 | Figure 10. Perceived cycling safety scores across Greater London: human votes. |
| `static_gpt_score_mosaic.pdf` | Notebook 09 | Figure 11. Perceived cycling safety scores across Greater London: GPT-5.2 synthetic votes. |
| `confusion_matrices_best_models.png` | Notebook 06 | Per-class confusion matrices for the best model per source. |
| `appendix_borough_choropleth.png` | Notebook 09 | Appendix C. Average perceived cycling safety score by London borough. |

---

## Result Files

| File | Produced by | Description |
|---|---|---|
| `stage1_agreement_analysis_a.csv` | Notebook 04 | Vote-by-vote agreement metrics: balanced accuracy, kappa, MCC, macro F1, decisive pair agreement. |
| `stage1_agreement_analysis_b.csv` | Notebook 04 | Ranking correlation metrics: Spearman rho, Kendall tau, Pearson r, Jaccard at K=10/30/500. |
| `stage2_main_results.csv` | Notebook 06 | Balanced accuracy per model per source across 15 cross-validation runs. |
| `stage2_ablation_results.csv` | Notebook 06 | Ablation B1 results: balanced accuracy drop per feature family. |
| `stage2_vote_scaling_results.csv` | Notebook 07 | Balanced accuracy per model at each vote threshold (20k to 200k). |

---

## Checkpoint Files

Notebooks 01 and 02 save checkpoints every 500 results during GPT API calls. These are stored as `gpt52_votes_25k_checkpoint_{n}.csv` and `gpt52_votes_200k_checkpoint_{n}.csv`. Checkpoints are excluded from version control but should be kept locally until the full run is confirmed complete.
