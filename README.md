# London Cyclist Crash Severity Prediction — Paper 2

Research code, intermediate data and enrichment tools connected to **Cyclist Crash Severity in Greater London: Multimodal Context, Temporal Validation and Feature Availability**. The repository follows the [reference manuscript](PRIVATE_REFERENCE_NOT_PUBLISHED).

**Start with the workflow guide and data catalogue below.** Code is grouped by task; distinct earlier methods are under `archive/`; data and browser viewers have their own locations. Seventeen duplicate or superseded files were consolidated. The audit records every replacement and all former paths.

**Release boundary:** this archive does not supply the final strict chronological XGBoost experiment, final cohort/split manifest, selected feature list or fitted model. Earlier MLP/ADASYN/random-split experiments are clearly marked as historical. The outcome is severity conditional on a recorded cyclist crash, not crash occurrence or trip risk.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [workflows/](workflows/README.md) | Paper 2 enrichment and inspection workflows |
| [data/](data/README.md) | Bundled data catalogue |
| [visualizations/](visualizations/README.md) | Descriptive browser visualizations |
| [archive/](archive/README.md) | Distinct historical methods and model experiments |
| [documentation/](documentation/README.md) | Manuscript, provenance and repository guides |
| [.gitignore](.gitignore) | Local credentials, environments, caches, machine metadata and scratch-run exclusions. |
| [LICENSE](LICENSE) | Supplied MIT code licence; upstream data/image/model terms remain separate. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Navigation and execution

Use [workflows/README.md](workflows/README.md) for the task sequence, [data/README.md](data/README.md) for inputs, and [the running guide](documentation/RUNNING_WORKFLOWS.md) for environment and scratch staging. Each directory inventories every immediate file and explains its use.

For the browser viewer, run `python3 -m http.server 8000 --bind 127.0.0.1` from this repository root and open `http://127.0.0.1:8000/visualizations/collision_viewer/`. Select `data/collision_tables/final_processed_with_interest.csv` using the file picker. External map/image providers still require connectivity.

Original notebook/script source and data bytes were preserved while relocating files; only the viewer's boundary-data URL changed. Notebook paths still require deliberate scratch staging. No training, inference, acquisition or cloud upload was run. See [the audit](documentation/REORGANIZATION_AUDIT.md) for consolidation evidence and the 20-column table reconstruction.

Code retains the supplied MIT licence. Third-party data, imagery and pretrained-model terms remain separate.
