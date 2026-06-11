# Pipeline tracker release checklist

Step-by-step checklist for producing a quarterly GOIT/GGIT pipeline data
release. Copy this file into the release folder
(`scripts/data-release-summary-sheets/YYYY-qN-<tracker>/CHECKLIST.md`),
fill in the header, and check items off as you go — that way the state of a
release is visible to anyone who opens the folder.

```
Release:          YYYY-qN-<tracker>        (e.g. 2026-q2-oil-pipelines)
Release month:    YYYY-MM                  (stamp used in download filenames)
Tracker sheet:    <Google Sheet URL / key> (the live backend)
Release snapshot: <Google Sheet URL / key> (the copy in the release Drive folder — step 6)
Run by:           <name>
```

The phases below are ordered on purpose: the backend sweep cleans the sheet
before anything reads from it; lengths and ownership are computed next and
pasted back in; only then is the sheet copied into the release's Drive folder,
and the data files and summary sheets are both produced from that snapshot —
so the release stays frozen even if the live sheet keeps moving.

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

## 3. Backend QC sweep — tracker sheet and pipeline routes

Sweep the database backend (the tracker Google Sheet) and the route files for
issues **before** anything reads from them — errors found here are far cheaper
to fix now than after export.

- [ ] Pull the sheet fresh and sweep for data errors:
  - [ ] `find_uncovered_fuels()` (from `gem-tracker-constants`) — `Fuel`
        strings that fall through every bucket and would silently drop out
        of the release
  - [ ] Status values outside the canonical lists (stray whitespace, case,
        typos)
  - [ ] `ProjectID` non-null, unique, matching `P<digits>`
  - [ ] Obvious year/capacity/units outliers — the checks in
        `scripts/data-release-qc/` are a good guide; most of what that script
        flags on the final files can be caught in the sheet now
- [ ] Reconcile routes against `goit-ggit-pipeline-routes`:
  - [ ] Mapped routes in the sheet with no `<ProjectID>.geojson` on GitHub
  - [ ] Route files on GitHub missing from the sheet (stale or misnamed)
  - (the estimate-length notebook in step 4 prints both reconciliation
    lists — it's fine to use those as the sweep)
- [ ] Fix everything found **in the source** (sheet or routes repo) before
      moving on

## 4. Length estimation

Notebook: `scripts/estimate-length/estimate-length.ipynb`

- [ ] Point the notebook at the release's tracker sheet
- [ ] Run all cells
- [ ] Review the two reconciliation lists the notebook prints (any leftovers
      from the step 3 sweep) and chase them down until both are clean
- [ ] Outputs produced: `estimate-length-results-by-pipeline.xlsx` and
      `estimate-length-results-by-country.xlsx`

## 5. Owner/parent attribution

Notebook: `scripts/owner-parent-scripts/GOIT-GGIT-owner-parent-importing-ownership-tracker-CURRENT.ipynb`
(pipelines; LNG terminals have their own CURRENT notebook)

- [ ] Point the notebook at the release's tracker sheet
- [ ] Run all cells
- [ ] Resolve the **missing parents** list: every parent named on the
      owners sheet (2/3) must have a row in the parent metadata sheet (3/3).
      Fix the sheet and re-run until the list is empty

## 6. Import results into the tracker sheet, then snapshot it

Copy the step 4–5 outputs back into the live tracker sheet, verify, and only
then take the release snapshot.

- [ ] Paste the new lengths into the sheet (per-pipeline estimates and the
      per-country ratios tab)
- [ ] Import the formatted owner/parent output
- [ ] Spot-check a few pipelines: known length vs. estimate vs. merged length
      (a `LengthKnown = 0` in the sheet will wrongly win over the estimate —
      blank it instead)
- [ ] The sheet is now final for this release. Copy it into the release's
      data-release Google Drive folder
- [ ] Share the copy so the python scripts can read it (the service account
      in `GDRIVE_API_CREDENTIALS`)
- [ ] Record the snapshot's URL/key in the header block above — **everything
      below reads from the snapshot**, not the live sheet

## 7. Release downloads (data files)

Notebook: `scripts/data-file-creation/convert-ggit-goit-to-tracker-release-downloads.ipynb`
(see that folder's README for config details)

- [ ] Point the notebook at the **release snapshot** sheet (step 6)
- [ ] Set the Configuration cell for this release:
      `PIPELINE_TYPE`, `SIMPLIFY_FUELS`, `FILTER_STATUS` / `FILTER_COUNTRIES`,
      `PIPELINE_ROUTES_PATH`, and the release-month stamp
- [ ] Run the export — outputs land in `scripts/data-file-creation/data-files/`
      as `GEM-<tracker>-<type>-Pipelines-YYYY-MM.{xlsx,geojson,gpkg}` + `-shp.zip`
- [ ] Repeat for each variant the release ships (e.g. full and simplified-fuel
      versions), if applicable

## 8. Release download QC — the last gate

Script: `scripts/data-release-qc/data-release-qc.py`
(its README explains every check and what to do when one fires)

Run this before the summary sheets so a QC fix doesn't force a summary re-run.

- [ ] Run against the base path **without extension**:

      ```bash
      python scripts/data-release-qc/data-release-qc.py \
          scripts/data-file-creation/data-files/GEM-GOIT-Oil-NGL-Pipelines-YYYY-MM
      ```

- [ ] Fix anything flagged **at the source**, per the "where fixes go" table
      in the QC README: data problems in the live tracker sheet, assembly
      problems in the export notebook, missing geometries in
      `goit-ggit-pipeline-routes`. **Never hand-edit the release files**
- [ ] If the sheet changed, apply the fix to the live tracker sheet **and**
      refresh the release snapshot (re-copy or edit it to match) so the two
      stay in sync
- [ ] Re-run the export (step 7) and the QC script until it exits clean
      (review any remaining WARNs and note why they're acceptable)

## 9. Summary sheets

Folder: the release folder created in step 2.

- [ ] Copy the most recent prior release's summary-sheets notebook in as the
      starting point and rename it for this release
      (e.g. `GOIT-pipelines-summary-sheets-<Month><Year>-release.ipynb`)
- [ ] Update `SPREADSHEET_KEY` to the **release snapshot** sheet (step 6);
      review the rest of the config block (`FUEL_TYPE`, `REGION_NAME`,
      `OUTPUT_DIR`)
- [ ] Run once per fuel being released (`FUEL_TYPE` ∈ Gas / Oil / NGL) and
      once per region filter needed (`Global`, plus any regional tracker codes)
- [ ] Sanity-check the output workbooks: regional totals look plausible
      against the previous release; no unexpected empty sheets
- [ ] Cross-check: row counts / km totals agree with the release downloads
      from step 7 (both read the same snapshot and filter on the same
      `gem-tracker-constants` buckets, so they must match)
- [ ] Copy/update the methodology `README.md` in the release folder
      (see `2026-q2-oil-pipelines/README.md` for the expected shape)
- [ ] Commit the notebook + README (data files stay gitignored)

## 10. Publish and wrap up

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
