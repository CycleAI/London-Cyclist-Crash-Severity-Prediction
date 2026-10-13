# London sampling grids and sampled coordinates

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Sampling locations support imagery acquisition. They are not recorded crashes, exposure denominators or labelled non-crash controls. The full grid and sampled metadata associations have different schemas.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [greater_london_grid_50m_full.csv](greater_london_grid_50m_full.csv) | 637,857 × 2 — Grid candidates with `lat`, `lon`; these are sampling locations, not observed crashes or labelled non-crash controls. |
| [random_sampling_coords.csv](random_sampling_coords.csv) | 5,000 × 3 — Sampled `lat`, `lng`, `blob_name` associations used for imagery acquisition diagnostics. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Schema and use

The full 50 m grid has 637,857 rows with `lat`, `lon`; the sampled mapping has 5,000 rows with `lat`, `lng`, `blob_name`. Do not confuse the two longitude names. Coordinates are degree values; projected metre spacing belongs to the generator's CRS policy.

Read with `pd.read_csv('data/sampling_coordinates/greater_london_grid_50m_full.csv')` from the repository root. pandas supports `chunksize` for inspection. Grid and sampling workflows retain their original input basenames, so stage copies or edit chosen input paths.

Check bounds, duplicate coordinates, random seeds, returned/requested panorama displacement and request success counts. The 168 m variant in the archive requires a different input that is not bundled. Neither these tables nor their counts establish crash cohort coverage or exposure. Both files are byte-preserved.
