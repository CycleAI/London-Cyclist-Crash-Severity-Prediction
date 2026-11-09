# London Cyclist Crash Severity Prediction — Paper 2

Research code, intermediate data and enrichment tools connected to **Cyclist Crash Severity in Greater London: Multimodal Context, Temporal Validation and Feature Availability**. The latest supplied analysis package is linked below.

**Start with [the latest paper package](cyclist-severity-london/README.md).** Code is grouped by task; distinct earlier methods are under `archive/`; data and browser viewers have their own locations. Seventeen duplicate or superseded files were consolidated. The audit records every replacement and all former paths.

**Current package:** `cyclist-severity-london/` contains the 41,606-crash analysis, chronological split labels, final models, held-out predictions and paper figures supplied on 27 October 2026. Its saved test predictions reproduce the reported rounded balanced accuracy and ROC-AUC for the main models. The older October XGBoost description in the historical documentation is superseded. Some source-to-feature build inputs remain missing; complete end-to-end reproduction is not established. The outcome is severity conditional on a recorded cyclist crash, not crash occurrence or trip risk.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [cyclist-severity-london/](cyclist-severity-london/README.md) | Latest supplied paper analysis, data, models, results and figures |
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

For the browser viewer, run `python3 -m http.server 8000 --bind 127.0.0.1` from this repository root and open `http://127.0.0.1:8000/visualizations/collision_viewer/`. Select `data/collision_tables/final_processed_with_interest.csv` using the file picker. Configure your own browser token as described in the [viewer guide](visualizations/collision_viewer/README.md). External map/image providers require connectivity.

The earlier reorganization preserved research data while relocating files. The public release additionally sanitizes all retained history and clears notebook outputs; see [PUBLIC_RELEASE.md](PUBLIC_RELEASE.md). Notebook paths still require deliberate scratch staging. No training, inference, acquisition or cloud upload was run. See [the audit](documentation/REORGANIZATION_AUDIT.md) for consolidation evidence and the 20-column table reconstruction.

Code retains the supplied MIT licence. Third-party data, imagery and pretrained-model terms remain separate.
