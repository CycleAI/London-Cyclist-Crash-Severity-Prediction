# Descriptive browser visualizations

[Repository overview](../README.md) · [Running guide](../documentation/RUNNING_WORKFLOWS.md)

Descriptive viewers and saved acquisition diagnostics. They do not load a trained severity model or compute crash probabilities. One enhanced collision viewer replaces the older duplicate viewer.

## Contents

| Entry | Purpose / inputs → outputs |
| --- | --- |
| [acquisition_diagnostics/](acquisition_diagnostics/README.md) | Saved imagery-acquisition coordinate maps |
| [collision_viewer/](collision_viewer/README.md) | Interactive collision and context viewer |
| [README.md](README.md) | This directory guide, complete inventory, use instructions and limitations. |

## Open locally

Run `python3 -m http.server 8000 --bind 127.0.0.1` from the repository root. Visit `http://127.0.0.1:8000/visualizations/collision_viewer/` for the selectable-data map or open a diagnostics HTML path under the same server. Stop with Ctrl-C.

Serve the whole repository because the viewer uses shared boundary data outside its folder. No Node build or deployment is required. The local server does not create model results or publish GitHub Pages. External CDN, tile and image requests require internet/provider access.
