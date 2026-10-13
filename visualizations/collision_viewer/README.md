# Interactive collision and context viewer

[Repository overview](../../README.md) · [Running guide](../../documentation/RUNNING_WORKFLOWS.md)

The retained Leaflet/Mapbox viewer supports local CSV selection, severity/year filtering, feature colouring, image popups and exports. Compared with the removed older viewer, it adds year-field handling, integer-year legends and revised point-of-interest coordinate lookup.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [index.html](index.html) | Retained interactive collision viewer; shared boundary URL updated for the new location. |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Open and select data

From the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/visualizations/collision_viewer/` and choose **Load Processed CSV**. Select `data/collision_tables/final_processed_with_interest.csv` for the earlier 28,914-row example (approximately 74.6 MB), or a smaller working sample. Its rows are not the final manuscript cohort.

Expected fields include `latitude`, `longitude`, `collision_year` and `Severity`, with numeric/context columns available for colouring. Display code also accepts `year`, but some export code expects `collision_year`; use that canonical name where possible. The boundary file is fetched from `../../data/geographic_boundaries/london_boroughs.geojson`. Serving only this directory would break that shared URL.

## Dependencies and outputs

The HTML loads Leaflet, D3, Papa Parse, html2canvas and browser helpers from CDNs. Mapbox tile/static exports require a public browser token; image popups can contact CycleAI image hosting through `images.weserv.nl`. The CSV is parsed in the browser, but tile/image/export requests contact providers and can include coordinates. This is not an offline viewer.

Outputs are interactive layers and user-triggered image exports, not modified CSVs or trained models. Verify coordinate bounds, year filters, label spelling, missing values and displayed point counts. Density and colouring are descriptive rather than exposure-adjusted risk or calibrated predictions. Static-map provider access and full export behaviour were not revalidated; the local page and shared boundary URL were checked.
