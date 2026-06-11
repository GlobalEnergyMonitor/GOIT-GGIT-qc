# data-file-creation (formerly goit-ggit-data-requests)

Notebooks that export GOIT/GGIT pipeline (and LNG terminal) data from the
tracker Google Sheets into release downloads (xlsx/geojson/gpkg/shp). See
this folder's README.md for setup and configuration.

## Key facts

- The only active notebook here is
  `convert-ggit-goit-to-tracker-release-downloads.ipynb`.
  It is often open in Jupyter while a Claude session runs — re-read it from
  disk before editing, and prefer telling the user about needed edits over
  NotebookEdit if they are actively running it (a Jupyter save would clobber
  file edits).
- Fuel buckets and status lists come from the `gem-tracker-constants` package,
  which lives in this repo at `gem-tracker-constants/` (repo root; merged in
  June 2026, installed by the notebook's first cell). Never re-declare fuel
  lists inline — edit the package's YAML data and run its tests instead. The
  QC summary sheets in this repo filter on the same buckets so release totals
  match QC totals.
- Route geometries are read from a local checkout of
  `goit-ggit-pipeline-routes` (`PIPELINE_ROUTES_PATH` in the config cell).
- `data-files/` holds release artifacts. `.gpkg`/`.zip` are
  committed deliberately (kept under GitHub's 100 MB limit); `.xlsx`,
  `.geojson`, `.csv` are gitignored. Don't add data files to commits unless
  asked — releases are the user's call.
