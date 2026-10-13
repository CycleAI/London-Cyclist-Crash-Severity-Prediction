# Image descriptors for crash enrichment

[Parent data guide](../README.md) · [Paper 2 imagery workflow](../../Paper2/README.md)

These are shared street-image descriptor tables retained because collision-enrichment code consumes image features. They were moved out of the perception-model directory. Their presence does not demonstrate linkage to every final manuscript record or a predictive benefit from imagery.

## Files and schemas

| File | Rows × columns | Contents and role |
| --- | ---: | --- |
| [processed_features_conf_0.5_grid.csv.zip](processed_features_conf_0.5_grid.csv.zip) | 19,995 × 2,251 | Contains `processed_features_conf_0.5_grid.csv`: `image_name`, segmentation/detection and 3×3 spatial summaries plus image statistics. The ZIP payload is unchanged. |
| [processed_features_conf_0.7.csv](processed_features_conf_0.7.csv) | 7,437 × 146 | Earlier descriptor subset keyed by `image_name`. The unrelated `safety_bin_1_10` column was removed; all rows and remaining values are preserved. |

[README.md](README.md) documents the two tables. The confidence suffixes describe archived extraction settings, not calibrated safety probabilities. The 0.5 and 0.7 versions differ in row coverage and schema; do not substitute one for the other by filename alone.

`image_name` is the join key into [image metadata](../../Accidents/README.md). Segmentation columns use `seg_*`; object summaries use `obj_*`; grid variants add region indices. Other fields include colour/texture/sharpness measures and image dimensions. Absence of a label here is intentional: injury severity comes from the linked collision table.

## Read and use

The ZIP also contains macOS resource metadata. Select the actual CSV explicitly rather than assuming a single-member ZIP:

```python
from zipfile import ZipFile
import pandas as pd
with ZipFile('Data/ImageFeatures/processed_features_conf_0.5_grid.csv.zip') as archive:
    with archive.open('processed_features_conf_0.5_grid.csv') as stream:
        sample = pd.read_csv(stream, nrows=5)
print(sample.shape)
print(sample.columns.tolist())
```

Run that example from the repository root. For the 0.7 table, use `pandas.read_csv` directly. The extracted 0.5 grid CSV is about 190 MB; use `chunksize` or `usecols` where appropriate. Extract to a scratch directory, not over a tracked file. pandas is sufficient for inspection; extraction itself uses Python's standard library.

The [100 m join notebook](../EnrichAccidentsWithImageFeatures.ipynb) uses the 0.7 table together with a collision CSV and `metadata_images_mapping.csv`. The grid table supports the extended feature programme in Appendix C, but a verified final-cohort linkage and selection manifest are not supplied.

## Quality and provenance limits

Check image-ID uniqueness, heading coverage, requested-versus-returned coordinates, capture dates and crash linkage. Detection confidence sums are uncalibrated aggregates; overlapping box areas are not segmentation fractions. Distinguish a valid zero detection from an unavailable/corrupt image. Verify the checkpoint/class list and region convention for each export. The archive's 19,995-row image tables do not resolve the manuscript's inconsistent acquisition totals.

No perception vote, TrueSkill score or safety-bin target is included in the current tables. The shared-data cleanup preserves every remaining value, but does not re-extract images or validate model performance. Image/provider reuse terms remain separate from the repository code licence.
