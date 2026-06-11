# goit-ggit-data-requests

Notebooks for producing data-release downloads and ad-hoc data requests from
GEM's [Global Oil Infrastructure Tracker (GOIT)](https://globalenergymonitor.org/projects/global-oil-infrastructure-tracker/)
and [Global Gas Infrastructure Tracker (GGIT)](https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/).

## Main notebook

[`notebooks/convert-ggit-goit-to-tracker-release-downloads-CURRENT.ipynb`](notebooks/convert-ggit-goit-to-tracker-release-downloads-CURRENT.ipynb)
exports pipeline (and optionally LNG terminal) data from the tracker Google
Sheets to Excel / GeoJSON / GeoPackage, joining route geometries from the
`goit-ggit-pipeline-routes` repo.

Configuration lives in the notebook's Configuration cell:

- **`PIPELINE_TYPE`** — `'Oil-NGL'` | `'Gas'` | `'Gas-Hydrogen'` | `'Hydrogen'` | `'Oil-and-Gas'`
- **`SIMPLIFY_FUELS`** — `None` | `'Oil'` | `'Oil-and-NGL'` | `'Gas'`; relabels
  fuels for the simplified release downloads using the canonical
  `SIMPLIFIED_OIL_FUEL_OPTIONS` / `SIMPLIFIED_NGL_FUEL_OPTIONS` buckets from
  [gem-tracker-constants](https://github.com/bairdlangenbrunner/gem-tracker-constants)
- **`FILTER_STATUS`** / **`FILTER_COUNTRIES`** — optional row filters

Outputs are written to `notebooks/DATA-FILES/`.

## Requirements

- Python with `pandas`, `geopandas`, `shapely`, `pygsheets`, `openpyxl`
- `gem-tracker-constants` (pinned in the notebook's first cell) — single
  source of truth for fuel buckets and status orderings, shared with
  `goit-ggit-qc` so release totals match QC summary totals
- `GDRIVE_API_CREDENTIALS` environment variable pointing at a Google service
  account with access to the tracker sheets
- A local checkout of `goit-ggit-pipeline-routes` (path set via
  `PIPELINE_ROUTES_PATH` in the Configuration cell)

## Related repos

- [`goit-ggit-pipeline-routes`](https://github.com/GlobalEnergyMonitor/goit-ggit-pipeline-routes) — per-pipeline route geometries (`<ProjectID>.geojson`)
- [`goit-ggit-qc`](https://github.com/GlobalEnergyMonitor/goit-ggit-qc) — QC summary tables filtered on the same fuel buckets
- [`gem-tracker-constants`](https://github.com/bairdlangenbrunner/gem-tracker-constants) — canonical fuel buckets and status orderings

## Notes on data files

Release artifacts (`.gpkg`, `.zip`) in `notebooks/DATA-FILES/` are committed
deliberately as part of a release; intermediate formats (`.xlsx`, `.geojson`,
`.csv`) are gitignored. Keep individual committed files under GitHub's 100 MB
hard limit.
