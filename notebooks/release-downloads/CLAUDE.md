# goit-ggit-data-requests

Notebooks that export GOIT/GGIT pipeline (and LNG terminal) data from the
tracker Google Sheets into release downloads (xlsx/geojson/gpkg/shp). See
README.md for setup and configuration.

## Key facts

- The only active notebook is
  `notebooks/convert-ggit-goit-to-tracker-release-downloads-CURRENT.ipynb`.
  It is often open in Jupyter while a Claude session runs — re-read it from
  disk before editing, and prefer telling the user about needed edits over
  NotebookEdit if they are actively running it (a Jupyter save would clobber
  file edits).
- Fuel buckets and status lists come from the `gem-tracker-constants` package
  (editable install at `../gem-tracker-constants`, pinned by tag in the
  notebook's first cell). Never re-declare fuel lists inline — change the
  package and bump the tag instead. The `goit-ggit-qc` repo filters on the
  same buckets so release totals match QC totals.
- Route geometries are read from a local checkout of
  `goit-ggit-pipeline-routes` (`PIPELINE_ROUTES_PATH` in the config cell).
- `notebooks/DATA-FILES/` holds release artifacts. `.gpkg`/`.zip` are
  committed deliberately (kept under GitHub's 100 MB limit); `.xlsx`,
  `.geojson`, `.csv` are gitignored. Don't add data files to commits unless
  asked — releases are the user's call.
