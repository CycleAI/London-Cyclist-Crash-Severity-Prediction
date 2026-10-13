# 03 — Sampling and imagery acquisition

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Choose grid sampling or crash-centred imagery, collect metadata/images and produce manifests. The grid-metadata notebook was present twice with identical source; this folder holds the canonical copy.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [download_images_from_metadata_concurrently.ipynb](download_images_from_metadata_concurrently.ipynb) | Concurrent metadata-based image retrieval. — Configured metadata/panorama IDs → images in configured paths. Review retry/concurrency and write settings. |
| [generate_image_manifest.ipynb](generate_image_manifest.ipynb) | Enumerate images for processing. — Configured image/storage inventory → manifest output defined in its cell. Confirm identifier format before feeding inference. |
| [generate_london_sampling_grid.ipynb](generate_london_sampling_grid.ipynb) | London boundary → `greater_london_grid_50m_full.csv`; projected-grid and visualisation alternatives. Appendix C sampling context. |
| [retrieve_crash_metadata_and_images.ipynb](retrieve_crash_metadata_and_images.ipynb) | `all_59k_accidents_raw.csv` → crash-centred Street View metadata and four-view images in Azure. Intended linkage workflow, not evidence of final-cohort coverage. |
| [retrieve_sampled_grid_metadata.ipynb](retrieve_sampled_grid_metadata.ipynb) | Sample grid coordinates → Street View metadata in Azure; inspect sample count, random seed and prefixes. |
| [upload_local_files_to_azure.py](upload_local_files_to_azure.py) | Configured local folder → Azure blobs. Inspect overwrite settings and destination before execution. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

Choose a London grid or the external `all_59k_accidents_raw.csv`. The main grid generator reads local `london_coordinates.json` from a saved Nominatim response; that file is not bundled. The archive retains a distinct live-boundary generator. Grid coordinates are available in `data/sampling_coordinates/`.

Outputs are grid CSV, Street View metadata/images, Azure blobs and an image manifest. The manifest notebook writes `images.txt`; inspect whether it emits blob names or URLs. Configure Google/Azure credentials, container prefixes, sample counts, seeds, concurrency, retries and overwrite settings before execution.

Dependencies include Jupyter, pandas, NumPy, requests, tqdm, azure-storage-blob, GeoPandas/Shapely/pyproj and the relevant Folium/Kepler cells. Project metre-based grids in the intended CRS and preserve WGS84 request coordinates. The paper describes four headings, 640×640 images and a 50 m query radius; code defaults do not prove final-cohort coverage.

## Checks

Record requested and returned coordinates, panorama ID, capture date, heading, API failure status and collision linkage. Image counts in filenames are requested settings, not audited successes. Later imagery does not establish pre-crash context. Upload and download operations were not run during reorganization.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
