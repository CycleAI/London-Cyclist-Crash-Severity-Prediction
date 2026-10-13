# Inspecting and running the archived workflows

[Documentation](README.md) · [Workflow guide](../workflows/README.md) · [Data catalogue](../data/README.md)

## Environment

From the repository root, a starting environment for local inspection is:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install jupyterlab pandas numpy scipy scikit-learn matplotlib seaborn tqdm pillow
jupyter lab
```

This is an unpinned inspection environment. No verified lockfile was supplied. Each workflow README lists its additional dependencies. PyTorch/Transformers, Detectron2 and CUDA alternatives may require separate environments; old installation cells are not a compatible combined requirements file.

## Working directories and file locations

Repository paths are documented in each folder. Notebook code is preserved, including its original input/output basenames and `/content/`, Drive and original-machine paths. **Moving a notebook does not update its kernel working directory.** Select the intended cells, configure paths, and run against scratch copies. Do not use Run All as an assumed pipeline.

For a small local example, stage the 100 m collision/image join inputs from the repository root:

```bash
mkdir -p work/join_100m
cp data/collision_tables/final_merged_cleaned_data.csv work/join_100m/
cp data/image_metadata/metadata_images_mapping.csv work/join_100m/
cp data/image_features/processed_features_conf_0.7.csv work/join_100m/
```

Open `workflows/05_collision_image_linkage/join_image_features_100m.ipynb`. In its kernel, change to the **absolute path** of `work/join_100m` with `%cd`, then inspect and run the selected cell. Its `enriched_collision_data_100m.csv` output will go into that scratch directory. Use a fresh destination for a later run instead of overwriting an experiment.

For the 500 m join scripts, stage `data/collision_tables/final_mapped_accidents_time_components.csv` under the script's expected basename `final_mapped_accidents.csv`; it needs the original 24-column schema. Extract `processed_features_conf_0.5_probs.csv` from `data/image_features/processed_features_conf_0.5_probs.csv.zip` and stage the same image metadata. The [collision data guide](../data/collision_tables/README.md) explains how to reconstruct the separate 20-column historical context view where required.

ZIPs include macOS metadata members. Open the named CSV explicitly:

```python
from zipfile import ZipFile
import pandas as pd
with ZipFile('data/image_features/processed_features_conf_0.5_probs.csv.zip') as z:
    with z.open('processed_features_conf_0.5_probs.csv') as f:
        sample = pd.read_csv(f, nrows=5)
print(sample.shape)
```

Missing external files are not resolved by choosing a similarly named bundled snapshot. Many `all_59k_*`, imagery, model, annual police and intermediate weather files are absent. Read the input schema and the manuscript release boundary first.

## Credentials and remote operations

Configure only the names read by the chosen cells, including variants of `AZURE_STORAGE_CONN_STR`, `AZURE_CONNECTION_STRING`, `AZURE_CONN_STR`, `AZ_CONN_STR`, `CONNECTION_STRING`, `STREET_VIEW_API_KEY`, `OPEN_METEO_API_KEY` and `HF_TOKEN`. Some cells still use empty/local connection settings. `.env` loading is not automatic. Private credentials and signed URL signatures were removed before the first import; do not commit replacements for placeholders.

The original Paper 2 references use Azure account `cycleai`, container `london`, prefix `Paper2Data/`. Referenced objects include `paper_2_final_dataset.csv`, `collisions_final.csv`, `streetview_metadata_with_collision.csv`, `processed_features_conf_0.5_filled_metadata_no_collision.csv`, `image_stats_processed_final_grids_no_collision.csv` and `ukbankholidays-jul19.xls`. Access and correspondence to the manuscript are not established by these names.

Acquisition, uploads and downloads are actual remote operations. Review request limits, destinations and overwrite settings before executing. Local table inspection does not require cloud access. The two archived script exports `download_grid_images_script.py` and `generate_grid_from_live_boundary.py` still contain notebook-only `!pip` syntax. `extract_image_features_script.py` expects a preconfigured `AZURE_CONNECTION_STRING` variable. These are not validated standalone commands.

## Recording a new result

Record commit, notebook/cells, input hashes, row grain, split identifiers, feature availability, seeds and package versions. Keep rows from the same collision together; perform feature selection and encoding on fitting data only. Historical random-split, ADASYN and multiclass outputs are not the strict chronological benchmark.

Use `work/` for local runs; it is ignored by Git. Keep tracked datasets unchanged and save outputs under an explicit run name. Python and notebook source was not refactored or executed as part of the reorganization.
