# 04 — Segmentation, detection and image descriptors

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

Turn aligned image inventories into segmentation masks, object detections and numerical descriptors. The two CreateInputNN copies are consolidated into the more documented aggregation notebook; YOLO notebook/export duplicates are consolidated into one notebook.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [aggregate_image_and_object_features.ipynb](aggregate_image_and_object_features.ipynb) | Segmentation/detection JSON and image statistics → `processed_features_*.csv`, including class counts, confidence sums, areas and 3×3 regions. Multiple variants and diagnostic cells. |
| [coco_classes.txt](coco_classes.txt) | Object-class names used for image interpretation; not the final predictor manifest. |
| [compute_local_image_statistics.ipynb](compute_local_image_statistics.ipynb) | Local images selected by `PAPER2_IMAGE_DIR` → colour/texture/edge and grid statistics; output controlled by `PAPER2_IMAGE_STATS_CSV`. |
| [detect_objects_yolov10.ipynb](detect_objects_yolov10.ipynb) | Object-detection processing and box previews. — Configured Azure/local images and YOLO detections → detection summaries, JSON and annotated previews. |
| [segment_crash_images.ipynb](segment_crash_images.ipynb) | Azure/local Street View images → Mask2Former class masks, JSON summaries and overlays; includes upload/visualisation variants. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Inputs, outputs and execution

Inputs are crash images, image manifests and aligned segmentation/detection JSON. Outputs include masks, per-image class summaries, confidence/count/area descriptors, 3×3 spatial features, annotated images and local CSVs. The class list is a detector reference, not the manuscript feature-selection manifest.

Use the selected PyTorch/Transformers or Ultralytics/ONNX stack, Pillow, OpenCV, scikit-image, pandas, NumPy, SciPy, tqdm and Azure SDK where required. CUDA/framework requirements differ from the Detectron2 alternatives in the archive. Review source configuration and inventory paths; these are not standalone validated entry points.

The YOLO workflow downloads a YOLOv10 ONNX model, processes Azure images, then saves confidence-threshold label files and previews with optional uploads. The removed `.py` export had the same executable code and notebook-only syntax. Threshold outputs are historical extraction settings, not safety probabilities.

For local image statistics, set `PAPER2_IMAGE_DIR` (default `./images`) and `PAPER2_IMAGE_STATS_CSV` (default `image_stats_processed_grids.csv`). This CSV still requires metadata alignment before the descriptor merge. The crash segmentation notebook uses a manifest-oriented image inventory; directory-based variants remain archived.

## Checks

Verify checkpoint labels, class ordering, image-ID uniqueness, heading coverage, dimensions and per-region normalization. Confidence sums are uncalibrated; box areas can overlap. Distinguish zero detections from missing/corrupt inputs. Selected images/terrain features are not established as members of the final strict top-140 set.

See [the shared running guide](../../documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging, [the data catalogue](../../data/README.md) for bundled inputs, and [the manuscript boundary](../../documentation/MANUSCRIPT_REFERENCE.md) for missing final experiment artifacts.
