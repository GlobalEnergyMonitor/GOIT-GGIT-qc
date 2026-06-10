# GOIT / GGIT QC

QC and data-release scripts for the Global Energy Monitor pipeline and LNG terminal trackers:

- **GOIT** — Global Oil Infrastructure Tracker (crude oil, refined products, NGL pipelines)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines + LNG terminals)

Most scripts are Jupyter notebooks. Data files (`.xlsx`, `.csv`, `.geojson`, `.json`) are gitignored — keep them in their notebook's folder locally.

## Folder map

```
notebooks/
├── estimate-length/                  pipeline length calculations
├── owner-parent-scripts/             owner/parent attribution for pipelines + terminals
├── data-release-summary-sheets/      per-release summary tables (one folder per release)
│   ├── 2023-q4-egt/
│   ├── 2023-q4-gas-pipelines/
│   ├── 2023-q4-lng-terminals/
│   ├── 2024-q2-africa-energy-pipelines/
│   ├── 2024-q2-oil-pipelines/
│   ├── 2024-q3-lng-terminals/
│   ├── 2024-q4-gas-pipelines/
│   ├── 2025-q1-euro-gas-tracker/
│   ├── 2025-q1-oil-pipelines/
│   ├── 2025-q4-gas-pipelines/
│   ├── 2026-q2-oil-pipelines/
│   └── _archive/                     2022–2023 releases (pre-folder-per-release convention)
├── researcher-requests-scripts/      researcher allocation calculations, by year
├── terminals-qc/                     ad-hoc LNG terminal QC
├── wiki-page-cleanup-automation/     parsing/scraping wiki XML refs
├── saved-geojson/                    output GeoJSON (gitignored)
└── _archive/                         deprecated notebooks, pre-2023 work, old R code
```

Anything under a `_archive/` folder is kept for historical reference and is not part of the active workflow.

## Typical release workflow

For a new quarterly release:

1. **Length estimation** — `notebooks/estimate-length/estimate-length-CURRENT.ipynb`
2. **Owner/parent attribution** — pick the relevant CURRENT notebook in `notebooks/owner-parent-scripts/`:
   - `GOIT-GGIT-owner-parent-importing-ownership-tracker-CURRENT.ipynb` (pipelines)
   - `GGIT-terminals-owner-parent-scripts-CURRENT.ipynb` (LNG terminals)
3. **Summary sheets** — create a new `data-release-summary-sheets/YYYY-qN-<tracker>/` folder and copy the most recent prior release notebook as the starting point.

## Conventions

- One folder per release under `data-release-summary-sheets/`, named `YYYY-qN-<tracker>` (e.g. `2026-q2-oil-pipelines`).
- Active "latest" scripts have `CURRENT` in the filename.
- Deprecated work goes under `_archive/` (or a per-folder `_archive/` for topic-specific archives).
