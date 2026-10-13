# Source archive

This repository was imported from `London-Bike-Safety-no-git.zip`, which Codrin Bostan sent on 11 August 2026 with the message “The final repo.”

- Source: PRIVATE_REFERENCE_NOT_PUBLISHED
- Source ZIP size: 132,791,525 bytes.
- Source ZIP SHA-256: `aa4a01753df561982dbb58f2110dde048c6bc91797b71790d61ce612fc801a0a`.
- All 147 files under the archive's `London-Bike-Safety-no-git/` directory are included, with the same relative paths. The outer `__MACOSX/` metadata directory is omitted.
- The full source includes `Paper2/`, `Paper1_CyclingSafetyPerception/`, and shared data and processing code. The initial import retains all of these folders.

## Credential handling

Hardcoded Azure storage, Azure OpenAI, OpenAI, Google Street View, Hugging Face, and routing API credentials were replaced with `YOUR_...` placeholders before the first commit. Azure signed-URL signatures were similarly replaced with `YOUR_AZURE_SAS_SIGNATURE`. This also covers the two ZIP files containing notebooks and credential values in saved notebook output. The original credential values are not committed.

Set the environment variables already used by each notebook, or configure its placeholder settings locally, before running code that needs authenticated services. Signed data links require a fresh authorised signature. Keep credentials out of Git and use local environment variables or notebook secret storage.

125 original files are byte-for-byte unchanged; the other 22 contain only credential substitutions (and ZIP repacking where a nested notebook changed). Data files, research logic, and saved results are otherwise preserved. A `.gitignore` and this provenance note were added for the import.

## Import validation

The import was checked against a SHA-256 manifest of the source files. All 87 notebook documents (including two compressed notebooks) parse as JSON, and all five nested ZIP files pass integrity checks. The 25 CSV, GeoJSON, and image files are byte-for-byte unchanged.

Credential scanning covered nested archives, followed by a source-aware check of credential assignments and signed URLs. The seven remaining Gitleaks findings were reviewed: five are existing Mapbox public `pk.` tokens in browser maps, and two are ordinary code identifiers. Public map tokens are designed for client use, as documented in [Mapbox's access-token guidance](https://docs.mapbox.com/help/getting-started/access-tokens/); these map files are unchanged.

Six existing `.py` files contain notebook-style `!pip` commands and therefore do not parse as standalone Python scripts: `NeuralNetwork/create_input.py`, `Paper2/YOLOV10.py`, `download_images.py`, `generate_london_grid.py`, `kepler_map.py`, and `random_sampling.py`. They are retained exactly as supplied. Research pipelines were not executed; they require external data, credentials, and their original runtime dependencies.
