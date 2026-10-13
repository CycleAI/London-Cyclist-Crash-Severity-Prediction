# Image descriptors for crash enrichment

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Shared street-image descriptor tables used by collision-enrichment methods. Confidence suffixes reflect extraction settings, not calibrated safety probabilities. No perception vote, TrueSkill score or safety-bin target is included in these current tables.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [processed_features_conf_0.5_grid.csv.zip](processed_features_conf_0.5_grid.csv.zip) | 19,995 × 2,251 — Contains `processed_features_conf_0.5_grid.csv`: `image_name`, segmentation/detection and 3×3 spatial summaries plus image statistics. The ZIP payload is unchanged. |
| [processed_features_conf_0.5_probs.csv.zip](processed_features_conf_0.5_probs.csv.zip) | 19,995 × 306 — Contains the image descriptor CSV keyed by `image_name`; confidence aggregates are not calibrated probabilities. |
| [processed_features_conf_0.7.csv](processed_features_conf_0.7.csv) | 7,437 × 146 — Earlier descriptor subset keyed by `image_name`. The unrelated `safety_bin_1_10` column was removed; all rows and remaining values are preserved. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Read and link

`image_name` joins to metadata; it is not a collision ID. `seg_*` represents segmentation summaries and `obj_*` object summaries. Grid variants add region indices; other fields include colour, texture, sharpness and dimensions. Zero detections and unavailable images must be distinguished.

From the repository root:

```python
from zipfile import ZipFile
import pandas as pd
with ZipFile('data/image_features/processed_features_conf_0.5_grid.csv.zip') as z:
    with z.open('processed_features_conf_0.5_grid.csv') as f:
        sample = pd.read_csv(f, nrows=5)
print(sample.shape)
```

The grid CSV expands to approximately 190 MB. Use `chunksize`/`usecols` as appropriate. The 0.7 CSV is directly readable with pandas. Select actual CSV members rather than macOS resource entries. Confidence/grid variants have different rows and columns and are deliberately retained.

The 0.7 table's unrelated perception label was removed in the preceding cleanup. All remaining descriptor values are preserved. Check image-ID uniqueness, heading coverage, capture date, requested/panorama displacement and collision linkage. Detection confidence sums and overlapping box areas are not calibrated probabilities or segmentation fractions. No final-cohort linkage or imagery performance benefit is established by these tables.
