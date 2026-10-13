# Geographic boundary data

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

One shared London borough GeoJSON replaces the two byte-identical map copies. The viewer reads it through a relative URL from the repository root. Its original source version and historical boundary vintage were not established by the archive.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [london_boroughs.geojson](london_boroughs.geojson) | Shared London borough boundary GeoJSON; byte-identical former duplicate removed. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Use and checks

Python's `json` module can read `data/geographic_boundaries/london_boroughs.geojson` from the repository root. The browser viewer fetches `../../data/geographic_boundaries/london_boroughs.geojson` relative to its page; serve the repository root so that URL resolves.

Inspect the FeatureCollection, geometry validity, expected borough properties and coordinate reference before joining to collision data. GeoJSON parsing does not establish boundary vintage or third-party reuse terms. The retained file is byte-identical to both original map copies. A boundary-retrieval notebook remains in descriptive analysis for investigating provenance or obtaining a separately versioned source.
