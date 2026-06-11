# GOIT / GGIT data ops

Data-release production, QC, and admin scripts for the Global Energy Monitor
pipeline and LNG terminal trackers:

- **GOIT** — Global Oil Infrastructure Tracker (crude oil, refined products, NGL pipelines)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines + LNG terminals)

This repo is the merge of the former `goit-ggit-qc`,
`goit-ggit-data-requests`, and `gem-tracker-constants` repos (June 2026);
all histories are preserved.

Most scripts are Jupyter notebooks. Data files (`.xlsx`, `.csv`, `.geojson`,
`.json`) are gitignored — keep them in their notebook's folder locally. The
exception is `scripts/data-file-creation/data-files/`, where `.gpkg`/`.zip`
release artifacts are committed deliberately (see that folder's README).

## Folder map

```
gem-tracker-constants/                canonical fuel buckets + status orderings
                                      (installable package: pip install -e ./gem-tracker-constants)
scripts/
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
├── data-file-creation/               export tracker sheets to release download files
│   └── data-files/                   release artifacts (.gpkg/.zip committed)
├── data-release-qc/                  pre-distribution checks for release download files
├── researcher-requests-scripts/      researcher allocation calculations, by year
└── _archive/                         deprecated notebooks, pre-2023 work, old R code,
                                      wiki-page-cleanup-automation
```

Anything under a `_archive/` folder is kept for historical reference and is not part of the active workflow.

## Typical release workflow

For a new quarterly release, work through [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md) —
copy it into the release folder and check items off so progress is visible.
The high-level sequence:

1. **Length estimation** — `scripts/estimate-length/estimate-length.ipynb`
2. **Owner/parent attribution** — pick the relevant CURRENT notebook in `scripts/owner-parent-scripts/`:
   - `GOIT-GGIT-owner-parent-importing-ownership-tracker-CURRENT.ipynb` (pipelines)
   - `GGIT-terminals-owner-parent-scripts-CURRENT.ipynb` (LNG terminals)
3. **Summary sheets** — create a new `data-release-summary-sheets/YYYY-qN-<tracker>/` folder and copy the most recent prior release notebook as the starting point.
4. **Release downloads** — export the download files (xlsx/geojson/gpkg/shp) with `scripts/data-file-creation/convert-ggit-goit-to-tracker-release-downloads.ipynb` (see that folder's README).
5. **Release download QC** — run `scripts/data-release-qc/data-release-qc.py` against the download files (see that folder's README). Fix anything it flags and re-export before distribution.

## Conventions

- One folder per release under `data-release-summary-sheets/`, named `YYYY-qN-<tracker>` (e.g. `2026-q2-oil-pipelines`).
- In folders with several notebooks, the active "latest" ones have `CURRENT` in the filename (e.g. `owner-parent-scripts/`); single-notebook folders use the plain name.
- Deprecated work goes under `_archive/` (or a per-folder `_archive/` for topic-specific archives).
- Fuel buckets and status lists come from the in-repo [gem-tracker-constants](gem-tracker-constants/) package (`pip install -e ./gem-tracker-constants`) — the release downloads and QC summary sheets filter on the same buckets, so release totals match QC totals. Formerly a standalone repo, merged June 2026; old release notebooks may still pin `v0.x` tags from `bairdlangenbrunner/gem-tracker-constants`.
