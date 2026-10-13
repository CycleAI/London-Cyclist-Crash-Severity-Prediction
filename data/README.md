# Bundled data catalogue

[Repository overview](../README.md) · [Running guide](../documentation/RUNNING_WORKFLOWS.md)

These local files are earlier Paper 2 snapshots and supporting descriptors, not a verified final 59,628-record analytical cohort. Counts in the leaf-folder inventories exclude headers. Dataset payloads were preserved during reorganization; only a provably redundant 20-column projection was removed.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [collision_tables/](collision_tables/README.md) | Earlier collision tables and enrichment snapshots |
| [geographic_boundaries/](geographic_boundaries/README.md) | Geographic boundary data |
| [image_features/](image_features/README.md) | Image descriptors for crash enrichment |
| [image_metadata/](image_metadata/README.md) | Image and panorama linkage metadata |
| [sampling_coordinates/](sampling_coordinates/README.md) | London sampling grids and sampled coordinates |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Choosing inputs

Collision tables contain outcomes and context; image features require metadata linkage before becoming collision-level predictors. Sampling coordinates and boundaries are supporting geographic data. Do not join on filenames or duplicate coordinates without checking identifiers and row grain.

Inspect local CSVs with pandas or Python's CSV module. See each folder for dimensions, fields, examples and limits. The [running guide](../documentation/RUNNING_WORKFLOWS.md) maps legacy input names to scratch copies. No database or cloud connection is needed to read bundled files.

Historical image-proximity radii of 100–500 m differ from the paper's 100 m POI candidate filter and 120 m road-route cutoff. Check `Severity` class mapping, missingness, timestamp/imagery lag, duplicates and collision-group integrity before modelling.
