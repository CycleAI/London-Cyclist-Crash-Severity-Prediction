# Manuscript, provenance and repository guides

[Repository overview](../README.md) · [Running guide](RUNNING_WORKFLOWS.md)

For the current study, begin with the [latest paper package](../cyclist-severity-london/README.md).
The manuscript-reference and provenance documents below record the earlier October
archive; their XGBoost specifications and missing-model statements do not describe
the newer paper package. Use the running guide for the older enrichment workflows
and the audit when locating a renamed file. See [PUBLIC_RELEASE.md](../PUBLIC_RELEASE.md)
for the current sanitization and reproducibility boundary.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [MANUSCRIPT_REFERENCE.md](MANUSCRIPT_REFERENCE.md) | Historical October manuscript specification, superseded by the latest paper package. |
| [PROVENANCE.md](PROVENANCE.md) | ZIP provenance, previous scope cleanup, credential handling and subsequent reorganization record. |
| [REORGANIZATION_AUDIT.md](REORGANIZATION_AUDIT.md) | All 17 consolidation decisions, retained variants, evidence and recovery instructions. |
| [reorganization_manifest.json](reorganization_manifest.json) | Original-to-current path mapping, retained replacements and pre-reorganization SHA-256 hashes. |
| [RUNNING_WORKFLOWS.md](RUNNING_WORKFLOWS.md) | Environment, scratch input staging, credentials, external data and execution guidance. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Use

The JSON manifest maps every original non-document payload to its current path or retained replacement and records pre-change SHA-256 hashes. Historical import notes describe earlier states; the current README structure is the navigation authority. Documents report integrity checks separately from unperformed model/API execution.
