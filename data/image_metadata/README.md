# Image and panorama linkage metadata

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

This mapping connects stored image names to panorama coordinates and imagery year for earlier collision/image joins. It does not establish final-cohort coverage or complete request/panorama/capture-date provenance.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [metadata_images_mapping.csv](metadata_images_mapping.csv) | 19,993 × 5 — Five fields: `metadata_blob_name`, `image_blob_name`, `lat`, `lng`, `year`. Associates image filenames with returned coordinates/year. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Schema and use

The five fields are `metadata_blob_name`, `image_blob_name`, `lat`, `lng`, `year`, across 19,993 rows. `year` is interpreted as imagery year by the join logic, not collision year. Image names link to the descriptor tables; coordinates represent the mapping's panorama location.

From the repository root: `pd.read_csv('data/image_metadata/metadata_images_mapping.csv')` after `import pandas as pd`. Use the matching workflows to join against descriptors and collision rows. Stage a copy under the unchanged basename for older scripts.

Check duplicate image names, unmatched descriptors, valid coordinates, headings and year values. Averaging numeric metadata across views can also average years; inspect before interpreting time. The mapping is an earlier snapshot, and 19,993 rows do not resolve inconsistent manuscript image totals. The file is unchanged from the original sanitized import.
