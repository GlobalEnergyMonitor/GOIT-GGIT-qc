# goit-ggit-data-ops

Data-release production, QC, and admin scripts for GEM's GOIT/GGIT trackers.
Merge of the former `goit-ggit-qc` and `goit-ggit-data-requests` repos
(June 2026); both histories are preserved. See README.md for the folder map
and the typical release workflow.

## Key facts

- Notebooks are often open in Jupyter while a Claude session runs — re-read
  a notebook from disk before editing, and prefer telling the user about
  needed edits over NotebookEdit if they are actively running it (a Jupyter
  save would clobber file edits).
- Fuel buckets and status lists come from the `gem-tracker-constants` package
  (editable install at `../gem-tracker-constants`, pinned by tag where used).
  Never re-declare fuel lists inline — change the package and bump the tag
  instead. The release downloads and QC summary sheets filter on the same
  buckets so release totals match QC totals.
- Data files (`.xlsx`, `.csv`, `.geojson`, `.json`) are gitignored repo-wide.
  Exception: `notebooks/release-downloads/DATA-FILES/` commits `.gpkg`/`.zip`
  release artifacts deliberately — see the CLAUDE.md in that folder. Don't
  add data files to commits unless asked — releases are the user's call.
