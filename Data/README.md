# Archived Paper 2 datasets

[Repository overview](../README.md) · [Image descriptors](ImageFeatures/README.md) · [Collision matching](../Accidents/README.md)

This directory holds earlier collision-table snapshots and sampling coordinates used by Paper 2's processing and exploratory severity work. Row/column counts below were measured from the checked-in files on 14 October 2026. They are not the manuscript's 59,628-record analytical cohort; `final` and radius suffixes are historical filenames, not guarantees of final-model membership or validated spatial matching.

## File inventory

| File | Rows × columns | Contents and role |
| --- | ---: | --- |
| [enriched_collision_data_100m_new.csv](enriched_collision_data_100m_new.csv) | 3,375 × 166 | Earlier collision/image enrichment at the named 100 m setting; `Severity` target retained; unrelated perception label removed. |
| [enriched_collision_data_300m_new.csv](enriched_collision_data_300m_new.csv) | 18,702 × 166 | Earlier collision/image enrichment at the named 300 m setting; `Severity` target retained; unrelated perception label removed. |
| [enriched_collision_data_500m_new.csv](enriched_collision_data_500m_new.csv) | 26,899 × 170 | Earlier 500 m enrichment snapshot; `Severity` and image/context fields. Different coverage/schema from the other radii. |
| [final_mapped_accidents.csv](final_mapped_accidents.csv) | 28,914 × 20 | Earlier harmonised roadway/context table with `Severity`; differs from the same basename under `Accidents/`. |
| [final_mapped_accidents_with_date_time.csv](final_mapped_accidents_with_date_time.csv) | 28,914 × 22 | Mapped collision table with date/time fields added. |
| [final_merged_cleaned_data.csv](final_merged_cleaned_data.csv) | 29,835 × 20 | Earlier merged collision table used by root severity/MLP notebooks. |
| [final_merged_cleaned_data_no_duplicates.csv](final_merged_cleaned_data_no_duplicates.csv) | 29,028 × 20 | Earlier deduplicated variant; verify the original deduplication rule before equating rows with unique events. |
| [greater_london_grid_50m_full.csv](greater_london_grid_50m_full.csv) | 637,857 × 2 | Grid candidates with `lat`, `lon`; these are sampling locations, not observed crashes or labelled non-crash controls. |
| [random_sampling_coords.csv](random_sampling_coords.csv) | 5,000 × 3 | Sampled `lat`, `lng`, `blob_name` associations used for imagery acquisition diagnostics. |

| Other entry | Purpose |
| --- | --- |
| [EnrichAccidentsWithImageFeatures.ipynb](EnrichAccidentsWithImageFeatures.ipynb) | Earlier 100 m nearest-image join; reads `final_merged_cleaned_data.csv`, `metadata_images_mapping.csv` and `processed_features_conf_0.7.csv`; writes `enriched_collision_data_100m.csv`. |
| [ImageFeatures/](ImageFeatures/README.md) | Shared image-only descriptor tables and schema/provenance notes. |
| [README.md](README.md) | Current inventory, field interpretation and use instructions. |

The notebook was renamed from an inherited perception-poll filename because it joins image descriptors to crash rows and does not train a perception model. It averages views by image location and uses longitude-scaled coordinates for its 100 m search. Unmatched crash rows are retained with missing descriptors; audit alignment and coverage before modelling.

## Fields and target

`Severity` contains `Slight`, `Serious` and `Fatal`. A binary Paper 2 analysis combines Serious/Fatal as positive and Slight as negative; confirm actual label mapping rather than relying on an encoder's alphabetical order. `collision_year`, `longitude`, `latitude`, road class/type, speed, junction, crossing, weather and lighting fields are common across these snapshots. Some code refers to a distinct imagery `year`; do not confuse it with collision year.

Coordinates are intended as WGS84 degrees in these CSVs; metre-based search or history requires an explicit projection/validated distance calculation. Official missing/unknown codes and blank image features must be interpreted separately. `seg_*` and `obj_*` describe images; their units and summarisation depend on the extraction version. They are not model importance or causal effects.

The unrelated `safety_bin_1_10` perception target was removed from the 100 m and 300 m CSVs. Their row order and all retained values are unchanged. Other files here are unchanged from the initial import, apart from the notebook filename. Old saved model outputs may have used the earlier schemas and have not been recomputed.

## Reading the data

Inspect without overwriting the source, from the repository root:

```python
import pandas as pd
df = pd.read_csv('Data/final_merged_cleaned_data.csv')
print(df.shape)
print(df.columns.tolist())
print(df['Severity'].value_counts(dropna=False))
```

For the join notebook, stage copies in a scratch working directory: the collision CSV from here, metadata from `Accidents/metadata_images_mapping.csv`, and descriptors from `Data/ImageFeatures/processed_features_conf_0.7.csv`. Update notebook paths if keeping the files in separate directories. The notebook uses pandas, NumPy and SciPy; launch it with Jupyter/Colab from a known working directory. It produces a new CSV rather than updating the checked-in radius snapshots automatically.

The large grid can be read with pandas `usecols`/`chunksize` when memory is limited. No database service is required to inspect these local tables.

## Checks before using a table

Check row grain and collision-ID uniqueness, target values, duplicate coordinates versus duplicate events, timestamp parsing, missing-code handling, matching rates and image capture-date lag. Keep casualties from the same collision together if such rows exist. Apply fit-only feature selection/encoding and a documented temporal split for new experiments. A larger image-match radius or a completed CSV does not establish the paper's historical feature-availability requirements.

Use the [root manuscript boundary](../README.md) for final-cohort and model artifacts that remain unavailable. No bundled snapshot should silently replace the final analytical table. The supplied code licence does not establish reuse permissions for every upstream dataset or image.
