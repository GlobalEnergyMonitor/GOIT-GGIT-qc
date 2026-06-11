# Pipeline tracker release checklist

Step-by-step checklist for producing a quarterly GOIT/GGIT pipeline data
release. Copy this file into the release folder
(`scripts/data-release-summary-sheets/YYYY-qN-<tracker>/CHECKLIST.md`),
fill in the header, and check items off as you go — that way the state of a
release is visible to anyone who opens the folder.

```
Release:        YYYY-qN-<tracker>        (e.g. 2026-q2-oil-pipelines)
Release month:  YYYY-MM                  (stamp used in download filenames)
Tracker sheet:  <Google Sheet URL / key>
Run by:         <name>
```

The phases below are ordered on purpose: lengths and ownership update the
tracker sheet, and the summary sheets and release downloads both read from it,
so steps 2–3 must be finished (and the sheet stable) before steps 4–5.

---

## 1. One-time machine setup

Skip this section if you've run a release from this machine before.

- [ ] Python environment with `pandas`, `geopandas`, `shapely`, `pygsheets`, `openpyxl`
- [ ] `gem-tracker-constants` installed editable from this repo:
      `pip install -e ./gem-tracker-constants` (run from the repo root)
- [ ] Local checkout of `goit-ggit-pipeline-routes` (route geometries,
      one `<ProjectID>.geojson` per pipeline)
- [ ] `GDRIVE_API_CREDENTIALS` env var pointing at a Google service-account
      JSON that has read access to the tracker sheets
- [ ] Confirm sheet access works: run the first few cells of
      `scripts/data-file-creation/convert-ggit-goit-to-tracker-release-downloads.ipynb`

## 2. Pre-flight (per release)

- [ ] Researcher updates to the tracker Google Sheet are complete — agree on a
      data-freeze point before running anything below
- [ ] `git pull` in `goit-ggit-pipeline-routes` so route geometries are current
- [ ] Confirm the notebooks' first cells install `gem-tracker-constants` from
      this repo (fuel buckets and status lists come from this package — never
      re-declare them inline; if a bucket needs to change, edit
      `gem-tracker-constants/src/gem_tracker_constants/data/*.yaml` and run
      the package's `pytest` suite)
- [ ] Create the release folder:
      `scripts/data-release-summary-sheets/YYYY-qN-<tracker>/`
- [ ] Copy this checklist into it and fill in the header block above

## 3. Length estimation

Notebook: `scripts/estimate-length/estimate-length.ipynb`

- [ ] Point the notebook at the release's tracker sheet
- [ ] Run all cells
- [ ] Review the two reconciliation lists the notebook prints:
  - [ ] **ProjectIDs in the sheet but missing on GitHub** — mapped routes with
        no geometry file; chase these in `goit-ggit-pipeline-routes` or fix
        the sheet's RouteType
  - [ ] **ProjectIDs on GitHub but missing from the sheet** — stale or
        misnamed route files
- [ ] Outputs produced: `estimate-length-results-by-pipeline.xlsx` and
      `estimate-length-results-by-country.xlsx`
- [ ] Update the tracker sheet with the new lengths (per-pipeline estimates
      and the per-country ratios tab)
- [ ] Spot-check a few pipelines: known length vs. estimate vs. merged length
      (a `LengthKnown = 0` in the sheet will wrongly win over the estimate —
      blank it instead)

## 4. Owner/parent attribution

Notebook: `scripts/owner-parent-scripts/GOIT-GGIT-owner-parent-importing-ownership-tracker-CURRENT.ipynb`
(pipelines; LNG terminals have their own CURRENT notebook)

- [ ] Point the notebook at the release's tracker sheet
- [ ] Run all cells
- [ ] Resolve the **missing parents** list: every parent named on the
      owners sheet (2/3) must have a row in the parent metadata sheet (3/3).
      Fix the sheet and re-run until the list is empty
- [ ] Import the formatted owner/parent output back into the tracker sheet

## 5. Summary sheets

Folder: the release folder created in step 2.

- [ ] Copy the most recent prior release's summary-sheets notebook in as the
      starting point and rename it for this release
      (e.g. `GOIT-pipelines-summary-sheets-<Month><Year>-release.ipynb`)
- [ ] Update `SPREADSHEET_KEY` to this release's sheet; review the rest of the
      config block (`FUEL_TYPE`, `REGION_NAME`, `OUTPUT_DIR`)
- [ ] Run once per fuel being released (`FUEL_TYPE` ∈ Gas / Oil / NGL) and
      once per region filter needed (`Global`, plus any regional tracker codes)
- [ ] Sanity-check the output workbooks: regional totals look plausible
      against the previous release; no unexpected empty sheets
- [ ] Copy/update the methodology `README.md` in the release folder
      (see `2026-q2-oil-pipelines/README.md` for the expected shape)
- [ ] Commit the notebook + README (data files stay gitignored)

## 6. Release downloads

Notebook: `scripts/data-file-creation/convert-ggit-goit-to-tracker-release-downloads.ipynb`
(see that folder's README for config details)

- [ ] Set the Configuration cell for this release:
      `PIPELINE_TYPE`, `SIMPLIFY_FUELS`, `FILTER_STATUS` / `FILTER_COUNTRIES`,
      `PIPELINE_ROUTES_PATH`, and the release-month stamp
- [ ] Run the export — outputs land in `scripts/data-file-creation/data-files/`
      as `GEM-<tracker>-<type>-Pipelines-YYYY-MM.{xlsx,geojson,gpkg}` + `-shp.zip`
- [ ] Repeat for each variant the release ships (e.g. full and simplified-fuel
      versions), if applicable
- [ ] Cross-check: row counts / km totals in the download agree with the
      summary sheets from step 5 (both filter on the same
      `gem-tracker-constants` buckets, so they must match)

## 7. Release download QC — the last gate

Script: `scripts/data-release-qc/data-release-qc.py`
(its README explains every check and what to do when one fires)

- [ ] Run against the base path **without extension**:

      ```bash
      python scripts/data-release-qc/data-release-qc.py \
          scripts/data-file-creation/data-files/GEM-GOIT-Oil-NGL-Pipelines-YYYY-MM
      ```

- [ ] Fix anything flagged **at the source**, per the "where fixes go" table
      in the QC README: data problems in the tracker sheet, assembly problems
      in the export notebook, missing geometries in `goit-ggit-pipeline-routes`.
      **Never hand-edit the release files**
- [ ] Re-run the export (step 6) and the QC script until it exits clean
      (review any remaining WARNs and note why they're acceptable)
- [ ] If the sheet changed during QC fixes, re-run the summary sheets
      (step 5) so the two stay in sync

## 8. Publish and wrap up

- [ ] Commit the final `.gpkg` and `-shp.zip` artifacts in
      `scripts/data-file-creation/data-files/` (these are committed
      deliberately; `.xlsx`/`.geojson` stay gitignored; keep each file under
      GitHub's 100 MB limit)
- [ ] Distribute the download files (tracker download page / Drive — whatever
      this release's channel is)
- [ ] Hand the summary-sheet workbooks to whoever is writing the report/brief
- [ ] Add the new release folder to the folder map in the repo `README.md`
- [ ] Note anything that went wrong or was confusing this round — fix the
      tooling or this checklist now, while it's fresh
