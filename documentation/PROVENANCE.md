# Paper 2 source and scope record

> Historical record: this document describes the October archive before the latest
> paper package and public-history sanitization. For the current release, see
> [the paper package](../cyclist-severity-london/README.md) and
> [PUBLIC_RELEASE.md](../PUBLIC_RELEASE.md). Earlier claims about retained tokens,
> notebook outputs, unchanged history or missing final models no longer describe
> the public release. Private source/document links have been removed.

## Source

Codrin Bostan sent `London-Bike-Safety-no-git.zip` on 11 August 2026 with “The final repo.”

- [Source ZIP](PRIVATE_REFERENCE_NOT_PUBLISHED).
- Size: 132,791,525 bytes.
- SHA-256: `aa4a01753df561982dbb58f2110dde048c6bc91797b71790d61ce612fc801a0a`.
- Initial import: `ff930ecda6b71ef431f9ebd1624396945df3880b`.

The initial import included 147 source files plus `.gitignore` and an import note. Top-level macOS metadata was omitted. Private credentials and signed-URL signatures were replaced before the first commit. Browser Mapbox public tokens were retained; some runtime settings still require local configuration.

## Scope correction — 14 October 2026

Reviewed against [Article 2 Latest.docx](PRIVATE_REFERENCE_NOT_PUBLISHED), modified 8 October 2026, **Cyclist Crash Severity in Greater London: Multimodal Context, Temporal Validation and Feature Availability**.

Removed 41 files: the Paper 1 package; human/LLM perception voting and TrueSkill notebooks (including two compressed notebook bundles); perception-specific neural-network/importance artifacts; and the one-byte `Map` and `test` placeholders. This is a normal follow-up commit. Earlier content remains in Git history; history was not rewritten.

Two shared image-feature tables moved from `NeuralNetwork/` to `Data/ImageFeatures/`. The unrelated `safety_bin_1_10` column was removed from `Data/ImageFeatures/processed_features_conf_0.7.csv`, `Data/enriched_collision_data_100m_new.csv` and `Data/enriched_collision_data_300m_new.csv`. All rows, row order and retained cell values were preserved. Other retained CSV/ZIP data payloads are unchanged.

Three crash-enrichment notebooks were renamed from `EnrichAccidentsPerceptionPoll.ipynb` to `EnrichAccidentsWithImageFeatures.ipynb`, at root, `Data/` and `Paper2/ColabNoteBooks/`, without changing their source cells. One stale output containing the removed perception label was cleared in each of the root and Colab copies. Unused perception-ranking filename constants and misleading error text were removed from shared extraction utilities. Outputs of source-edited cells were cleared.

`Paper2/ProcessImageStatsLocally.ipynb` now reads `PAPER2_IMAGE_DIR` (default `./images`) and `PAPER2_IMAGE_STATS_CSV` (default `image_stats_processed_grids.csv`). The original perception-poll directory/output settings were removed; calculations were retained.

Eight READMEs cover the root and all seven retained subdirectories. They separate paper-reported results, archived code behaviour, earlier snapshots and unavailable final-experiment artifacts. The linked manuscript was not modified or added to this repository.

## Validation boundary

Checks cover scope, CSV column removal with retained-value equality, moved/renamed file hashes, notebook JSON, nested CSV ZIP integrity, every directory/file's documentation coverage and local Markdown links. Retained code is checked for perception targets and voting/ranking dependencies. No acquisition, cloud upload, inference or training was run.

The archive supports Paper 2 enrichment and earlier severity work; it does not contain a verified reproduction of the final strict XGBoost experiment. See the [manuscript record](MANUSCRIPT_REFERENCE.md) for missing cohort, feature, split, model and runtime artifacts. Notebook-only syntax and historical methodology are documented rather than silently rewritten.


## Consolidation and organization — 14 October 2026

A subsequent audit removed 17 redundant/superseded files and reorganized the remaining content into `data/`, numbered `workflows/`, `visualizations/`, `archive/` and `documentation/`. The earlier eight-directory description above records the previous cleanup state. Current folders each have their own README.

See [the duplicate/version audit](REORGANIZATION_AUDIT.md) for evidence and replacement paths, [the path/hash manifest](reorganization_manifest.json) for all original file locations, and [the running guide](RUNNING_WORKFLOWS.md) for scratch input staging. The reference manuscript and missing final experimental artifacts have not changed.
