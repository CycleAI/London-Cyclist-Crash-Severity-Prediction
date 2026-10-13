# Paper 2 descriptive collision map

[Repository overview](../../README.md) · [Main enrichment guide](../../Paper2/README.md)

This is a browser viewer for recorded collision/context data and earlier descriptive spatial diagnostics. It does not run a trained model or compute crash probabilities. This variant adds year-field handling and other display changes relative to the older `docs/` copy. They are separate archived HTML files, not a synchronised application.

## Files

| File | Role |
| --- | --- |
| [index.html](index.html) | Leaflet/Mapbox viewer with local CSV selection, severity/year filters, feature colouring and image/export controls. |
| [london_boroughs.geojson](london_boroughs.geojson) | London borough boundary overlay fetched by the viewer. |
| [README.md](README.md) | Local serving, data schema, external dependencies and interpretation. |

## Open locally

From the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory Paper2/Map
```

Visit `http://127.0.0.1:8000/` and select a CSV using **Load Processed CSV**. Stop the local server with Ctrl-C. HTTP serving allows the relative GeoJSON fetch; simply double-clicking the HTML can trigger browser restrictions. The server does not train a model or publish the repository.

For an archived example, select [final_processed_with_interest.csv](../../docs/final_processed_with_interest.csv). Use `latitude`, `longitude`, `collision_year` and `Severity` fields; additional numeric/context columns populate the feature controls. The Paper 2 viewer's display path also supports `year`, but some export code still expects `collision_year`, so that canonical name is preferable. Keep headers and parseable values consistent and inspect missing coordinates before visualising. Filenames/IDs for Street View popups require the original external image convention.

## Dependencies and outputs

No Node build step is required. `index.html` loads Leaflet, D3, Papa Parse, html2canvas and related browser helpers from external CDNs. Mapbox tiles/static-image export require a valid public browser token configured in the HTML. Boundary JSON is local. Image popups can request CycleAI-hosted images through `images.weserv.nl`; availability is external to this repository.

The chosen CSV is parsed in the browser. Tile/image/static-export requests still contact external providers, and static-map exports can include selected coordinates. This is not an offline viewer. The 74.6 MB processed CSV in `docs/` can be slow in a browser; start with an authorised smaller working copy when inspecting layout.

Outputs are interactive layers and user-triggered image exports; the HTML does not write updated CSVs or trained models. No GitHub Pages deployment or external publication was performed during this cleanup.

## Data interpretation and checks

Verify coordinate bounds, year filtering, label spelling, missing values, point counts and a few selected records against the CSV. Colour by year, severity or another chosen feature remains descriptive. Do not interpret point density as exposure-adjusted risk, all rows as independent collisions, or a colour scale as a calibrated prediction.

The older sample and source-layer vintages are not verified against the final modelling cohort (manuscript Appendix D). Boundary layer version, image-date alignment and third-party reuse permissions require their own provenance. Documentation checks verify local filenames/links; map rendering, provider access and export behaviour were not revalidated end to end.
