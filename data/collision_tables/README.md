# Earlier collision tables and enrichment snapshots

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

These collision snapshots contain different schemas, populations and stages of enrichment. Preserve each input version explicitly. No retained table is identified as the final 59,628-record manuscript cohort; `final` and radius suffixes are inherited filenames.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [enriched_collision_data_100m_new.csv](enriched_collision_data_100m_new.csv) | 3,375 × 166 — Earlier collision/image enrichment at the named 100 m setting; `Severity` target retained; unrelated perception label removed. |
| [enriched_collision_data_300m_new.csv](enriched_collision_data_300m_new.csv) | 18,702 × 166 — Earlier collision/image enrichment at the named 300 m setting; `Severity` target retained; unrelated perception label removed. |
| [enriched_collision_data_500m_filtered.csv](enriched_collision_data_500m_filtered.csv) | 26,899 × 61 — Filtered earlier 500 m joined table with `Severity` and selected image/context fields. |
| [enriched_collision_data_500m_filtered_relevant.csv](enriched_collision_data_500m_filtered_relevant.csv) | 27,756 × 73 — Another earlier feature/coverage selection; different row count from the filtered table. |
| [enriched_collision_data_500m_new.csv](enriched_collision_data_500m_new.csv) | 26,899 × 170 — Earlier 500 m enrichment snapshot; `Severity` and image/context fields. Different coverage/schema from the other radii. |
| [enriched_collision_data_with_weather.csv.zip](enriched_collision_data_with_weather.csv.zip) | 28,914 × 413 — Contains the named weather-enriched crash CSV; also includes macOS metadata. |
| [final_mapped_accidents_time_components.csv](final_mapped_accidents_time_components.csv) | 28,914 × 24 — Mapped collision context with separate year/month/day/hour/minutes/seconds. Renamed to distinguish it from the 22-column date/time view. |
| [final_mapped_accidents_with_date_time.csv](final_mapped_accidents_with_date_time.csv) | 28,914 × 22 — Mapped context plus date/time; losslessly contains the removed 20-column context view. |
| [final_merged_cleaned_data.csv](final_merged_cleaned_data.csv) | 29,835 × 20 — Earlier merged collision table used by the historical severity/MLP notebooks under `archive/model_experiments/`. |
| [final_merged_cleaned_data_no_duplicates.csv](final_merged_cleaned_data_no_duplicates.csv) | 29,028 × 20 — Earlier deduplicated variant; verify the original deduplication rule before equating rows with unique events. |
| [final_processed_with_interest.csv](final_processed_with_interest.csv) | 28,914 × 434 — Earlier processed collision/context/POI table; 23,513 Slight, 5,355 Serious, 46 Fatal. Moved out of the viewer folder. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Target and schema

`Severity` contains `Slight`, `Serious` and `Fatal`; binary Paper 2 work combines Serious/Fatal as positive. Do not rely on alphabetical encoder order. Coordinates are intended as WGS84 degrees. Blank values and official unknown codes require separate interpretation. Historic `final` filenames do not identify final model membership.

`final_mapped_accidents_time_components.csv` is the former 24-column `Accidents/final_mapped_accidents.csv`, with separate `year`, `month`, `day`, `hour`, `minutes`, `seconds` fields. `final_mapped_accidents_with_date_time.csv` is the 22-column context/date/time view, with `collision_month` and `collision_hour`. Both have 28,914 rows and identical shared fields, but neither contains all of the other's columns. Keep both.

The deleted 20-column `Data/final_mapped_accidents.csv` was an exact projection of the 22-column view. To reproduce that old schema in scratch space, from the repository root:

```python
from pathlib import Path
import csv
source = Path('data/collision_tables/final_mapped_accidents_with_date_time.csv')
dest = Path('work/context_20/final_mapped_accidents.csv')
dest.parent.mkdir(parents=True, exist_ok=True)
with source.open(newline='') as src, dest.open('x', newline='') as out:
    reader = csv.DictReader(src)
    fields = [f for f in reader.fieldnames if f not in {'date', 'time'}]
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(reader)
```

This preserves row order and string values; CSV byte formatting may differ. It deliberately refuses to overwrite an existing destination. The 500 m join scripts instead expect the 24-column time-component variant staged as `final_mapped_accidents.csv`. The older MLP search does not reliably identify its source schema: select and record it explicitly; do not assert reconstructed metrics.

## Inspection and quality checks

From the repository root, use `pandas.read_csv('data/collision_tables/final_merged_cleaned_data.csv')`; inspect `.shape`, `.columns` and `df['Severity'].value_counts(dropna=False)`. ZIP members must be selected by CSV name because macOS companion files are present.

The processed context/POI table has 23,513 Slight, 5,355 Serious and 46 Fatal records (28,914 total). The 100 m and 300 m tables had the unrelated `safety_bin_1_10` column removed in the preceding scope cleanup; retained values were verified unchanged then. The reorganization did not modify any retained CSV or ZIP.

Verify row grain, collision-ID uniqueness, duplicate coordinates versus repeated events, date/time parsing, source vintage, image matching rates and missing-code handling. The merged and deduplicated snapshots differ in row count; their original deduplication rule is not reproduced here. Stored model outputs have not been regenerated against these schemas.
