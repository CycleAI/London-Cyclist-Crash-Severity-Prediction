# Collision-to-image matching and earlier crash tables

[Repository overview](../README.md) · [Data snapshots](../Data/README.md) · [Main enrichment notebooks](../Paper2/README.md)

This directory contains early Paper 2 collision-enrichment scripts, metadata associations and intermediate tables. It documents how image features were linked to recorded crashes; it is not the final chronological XGBoost pipeline or final 59,628-record cohort.

## Scripts

| File | Inputs → outputs and behaviour |
| --- | --- |
| [create_nn_input.py](create_nn_input.py) | Azure segmentation/detection/image-statistics JSON → `processed_features_{name}.csv`. Aggregates class fractions, counts, confidence sums, box areas and statistics. Needs notebook/global `AZURE_CONNECTION_STRING` plus configured blob prefixes; historical constants assume an image inventory that requires audit. |
| [enrich_accidents.py](enrich_accidents.py) | `final_mapped_accidents.csv` + `metadata_images_mapping.csv` + extracted `processed_features_conf_0.5_probs.csv` → `enriched_collision_data_500m_new.csv` and diagnostic bad-match output. Averages image headings by location, uses an approximate 500 m nearest-neighbour search and exports matched rows. |
| [enrich_with_distance_count.py](enrich_with_distance_count.py) | Same three inputs → `enriched_collision_data_with_distance.csv` / `enriched_collision_data_with_distance_no_severity.csv`; includes matching-distance and diagnostic variants. Inspect each export's schema before selecting a modelling input. |
| [mutual_information.py](mutual_information.py) | `enriched_collision_data_500m_new.csv` → exploratory mutual-information ranking against `Severity`. It is not the manuscript's frozen fit-only top-140 ranking. |
| [README.md](README.md) | Script, dataset and execution guide. |

## Bundled data

| File | Rows × columns | Contents and role |
| --- | ---: | --- |
| [enriched_collision_data_500m_filtered.csv](enriched_collision_data_500m_filtered.csv) | 26,899 × 61 | Filtered earlier 500 m joined table with `Severity` and selected image/context fields. |
| [enriched_collision_data_500m_filtered_relevant.csv](enriched_collision_data_500m_filtered_relevant.csv) | 27,756 × 73 | Another earlier feature/coverage selection; different row count from the filtered table. |
| [enriched_collision_data_with_weather.csv.zip](enriched_collision_data_with_weather.csv.zip) | 28,914 × 413 | Contains the named weather-enriched crash CSV; also includes macOS metadata. |
| [final_mapped_accidents.csv](final_mapped_accidents.csv) | 28,914 × 24 | Earlier crash context table; 24 columns, unlike the 20-column file of the same name in `Data/`. |
| [metadata_images_mapping.csv](metadata_images_mapping.csv) | 19,993 × 5 | Five fields: `metadata_blob_name`, `image_blob_name`, `lat`, `lng`, `year`. Associates image filenames with returned coordinates/year. |
| [processed_features_conf_0.5_probs.csv.zip](processed_features_conf_0.5_probs.csv.zip) | 19,995 × 306 | Contains the image descriptor CSV keyed by `image_name`; confidence aggregates are not calibrated probabilities. |

Counts were measured from actual CSV records, excluding the header. All these bundled data payloads are unchanged from the initial import. `Severity` is the recorded Slight/Serious/Fatal outcome; for binary Paper 2 work combine Serious/Fatal explicitly. The metadata's `year` refers to imagery in the join logic; it is not necessarily the crash year.

## Running a matching experiment

Use an isolated scratch directory. Copy the selected collision table and metadata mapping there, extract the named feature CSV, and open the selected script/notebook with that directory as the working directory. ZIPs contain more than one member, so select the CSV explicitly:

```python
from zipfile import ZipFile
import pandas as pd
with ZipFile('Accidents/processed_features_conf_0.5_probs.csv.zip') as archive:
    with archive.open('processed_features_conf_0.5_probs.csv') as stream:
        features = pd.read_csv(stream)
print(features.shape)
```

The example runs from the repository root. For actual execution, point the script's relative paths at staged copies. Local joins need pandas, NumPy and SciPy. `create_nn_input.py` additionally uses Azure SDK, OpenCV, scikit-image, matplotlib, seaborn and tqdm; it is a research export with external configuration, not a standalone CLI with validated defaults. It can download remote data. Do not execute it merely to inspect a CSV.

`enriched_collision_data_500m_new.csv` is not bundled in this directory; one earlier snapshot with that basename is in `Data/`. Its schema/coverage may differ from a newly generated file. Choose explicitly rather than resolving duplicate basenames silently. The join script unconditionally drops a `year` column from its chosen collision input, so a different schema can fail.

## Interpretation and validation

The retained join uses averaged headings and a longitude-scaled approximation, not the final paper's complete historical linkage audit. Matching radii here concern collision-to-image proximity; they are distinct from the paper's 100 m POI candidate filter and 120 m road-network cutoff. A code comment can say 100 m while the actual radius constant is 500 m; use the executed settings.

Check target distributions before/after matching, unmatched rows, exact image-ID joins, duplicated coordinates, image dates and distance thresholds. Averaging all numeric metadata can average image year too; inspect it before interpreting capture time. Zero-filled missing features and dropped unmatched rows can alter the analysis population. Keep missingness provenance and collision-group integrity in downstream evaluation.

These files do not establish final cohort coverage, a strict pre-crash feature gate or a fit-only MI ranking. Existing outputs were not regenerated; do not cite their metrics as the manuscript's final model results.
