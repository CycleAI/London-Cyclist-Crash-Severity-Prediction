# Alternative imagery acquisition and processing methods

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Alternative grid/image acquisition, framework and descriptor-extraction implementations. These are retained for substantive differences in grid spacing, sample size, input inventory, execution strategy or framework; use the canonical workflow folders first.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [detect_objects_per_threshold.py](detect_objects_per_threshold.py) | Earlier grid-image YOLO workflow that reruns inference for each confidence threshold; depends on original notebook imports/settings. |
| [download_grid_images.ipynb](download_grid_images.ipynb) | Grid-based multiview imagery acquisition. — `greater_london_grid_50m_full.csv` → Google/Azure image and metadata outputs. |
| [download_grid_images_script.py](download_grid_images_script.py) | Four-view grid-image acquisition and Azure uploads; configure inputs, prefixes and credentials. Contains notebook syntax. |
| [download_images_from_metadata_sequentially.ipynb](download_images_from_metadata_sequentially.ipynb) | Fetch images for existing metadata. — Configured panorama metadata → Street View images/Azure objects; two API-key placeholders require local configuration. |
| [download_sampled_2500_images.ipynb](download_sampled_2500_images.ipynb) | Earlier sampled-grid acquisition variant. — `greater_london_grid_50m_full.csv` → Street View metadata/images in configured Azure paths; filename is not verified coverage. |
| [extract_image_features_script.py](extract_image_features_script.py) | Azure segmentation/detection/image-statistics JSON → `processed_features_{name}.csv`. Aggregates class fractions, counts, confidence sums, box areas and statistics. Needs notebook/global `AZURE_CONNECTION_STRING` plus configured blob prefixes; historical constants assume an image inventory that requires audit. |
| [generate_grid_from_live_boundary.py](generate_grid_from_live_boundary.py) | Live Nominatim boundary → 50 m London grid CSV. Different boundary-input policy from the consolidated notebook; includes notebook syntax. |
| [retrieve_168m_grid_metadata.ipynb](retrieve_168m_grid_metadata.ipynb) | Metadata retrieval for a different grid setting. — Expects `greater_london_grid_168m_full.csv`, which is not bundled; do not silently substitute the 50 m grid. |
| [retrieve_sampled_20000_grid_images.ipynb](retrieve_sampled_20000_grid_images.ipynb) | Earlier sampling/acquisition variant. — Grid CSV → metadata/images through Google/Azure; requested sample settings are not final-cohort coverage. |
| [segment_grid_images_from_directory.ipynb](segment_grid_images_from_directory.ipynb) | Directory-based training/grid image segmentation and optional uploads; differs from the consolidated crash-manifest workflow. |
| [segment_grid_images_script.py](segment_grid_images_script.py) | Azure-backed Mask2Former inference → masks, class JSON and overlays. Configure checkpoint, storage prefixes and credentials. |
| [segment_images_alternative_masks.ipynb](segment_images_alternative_masks.ipynb) | Another segmentation implementation/inspection archive. — Configured images → instance/panoptic/semantic masks and manifests; do not mix checkpoints/taxonomies without checks. |
| [segment_images_detectron2.ipynb](segment_images_detectron2.ipynb) | Alternative Detectron2/Mask2Former workflow. — Azure/local images → masks, instance/panoptic/semantic artifacts and `mask2former_manifest.jsonl`; separate framework/setup requirements. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Why these variants remain

Grid-based versus crash-centred imagery, 50 m versus 168 m inputs, sequential versus concurrent downloads, different sample policies, live versus saved boundary responses, directory versus manifest inventories, and Detectron2 versus Transformers are substantive differences. They were not deleted merely because they overlap other code.

The live-boundary grid generator fetches Nominatim geometry; the consolidated generator loads a saved response. The directory-based segmentation version processes a training/grid inventory; the consolidated version uses a crash manifest and different storage prefixes. The per-threshold detector reruns inference for each threshold, unlike the consolidated threshold-filtering workflow. The 168 m grid CSV is not bundled.

## Inputs, outputs and runtime

Input families are grid coordinates, panorama metadata, raw images and model/checkpoint files. Outputs are acquisition metadata/images, segmentation/detection artifacts and descriptor CSVs. Inspect every file's path and setting; counts in names are not audited coverage. The old extraction script requires a preconfigured `AZURE_CONNECTION_STRING` variable.

Dependencies vary across requests/Azure, pandas/NumPy/SciPy, geospatial libraries, Pillow/OpenCV/scikit-image, PyTorch/Transformers/Detectron2/Ultralytics and CUDA. `download_grid_images_script.py` and `generate_grid_from_live_boundary.py` retain notebook `!pip` syntax. Other exports may rely on notebook globals/imports; source is preserved rather than presented as tested CLI software.

Use isolated environments and scratch outputs, record the method and actual success counts, and review remote write settings. Preserve heading, date and coordinate provenance. No image acquisition, upload or inference was run during reorganization.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
