# Release download QC

Pre-distribution checks for the tracker release downloads produced by
`goit-ggit-data-requests` (`GEM-<tracker>-<type>-Pipelines-YYYY-MM.{xlsx,geojson,gpkg}`
plus the `-shp.zip` shapefile). Run these on the final files **before** they go
out — this is the last gate for data errors.

## Quick start

```bash
python qc-release-downloads.py /path/to/GEM-GOIT-Oil-NGL-Pipelines-2026-06
```

Pass the base path **without an extension**; the script finds the sibling
`.xlsx` / `.gpkg` / `.geojson` / `-shp.zip` files itself. It prints one line
per check (`OK` / `WARN` / `FAIL`) and exits non-zero if anything FAILs.
Needs `pandas`, `openpyxl`, and `geopandas`.

The script is the source of truth for the exact logic; the sections below
explain what each check means and what to do when it fires.

## 1. Files & structure

- **All four formats present** with the same base name and `YYYY-MM` stamp.
- **xlsx has the four sheets**: `Data`, `Data dictionary`, `Acronyms`, `Copyright`.
- **shp zip contains** `.shp .shx .dbf .prj` (and usually `.cpg`), no stray files.
- **Row counts identical** across xlsx Data sheet, gpkg, and geojson. A mismatch
  means the formats were written from different dataframes — re-run the export.

## 2. Schema

- **Data columns == dictionary entries**, both directions. A column in the data
  with no dictionary entry (or vice versa) means the source sheet's dictionary
  tab is out of date.
- **Start/End column symmetry**: every `Start<X>` location column should have a
  matching `End<X>` and vice versa (`Location`, `Prefecture/District`,
  `State/Province`, `CountryOrArea`, `Region`, `SubRegion`). This caught a
  missing `StartState/Province` in the 2026-06 oil/NGL release — the column was
  absent from the source Google Sheet entirely.
- **Column order vs. dictionary order** (warn only): the export keeps the source
  sheet's column order verbatim, which can drift into a scrambled order.
  Cosmetic, but fix it in the source sheet for readability.

## 3. Identifiers

- `ProjectID` non-null, unique, matches `P<digits>`.

## 4. Categorical vocabularies

These are reported, not hard-failed, because expected values differ by release:

- **Fuel** — after simplification should be a small set (e.g. `Oil` / `NGL` /
  `Oil, NGL`). Anything unexpected means the fuel-bucket filter in the export
  notebook (driven by `gem-tracker-constants`) and this repo's QC disagree.
- **Status** — canonical lowercase set: `proposed, construction, operating,
  idle, mothballed, shelved, cancelled, retired`. `N/A` must not appear (the
  export filters it).
- **RouteType / RouteAccuracy** — known vocab; `no route` interacts with
  geometry checks below.
- **Units columns** (`CapacityUnits`, `DiameterUnits`, `LengthKnownUnits`,
  `CostUnits`) — eyeball for typos and non-standard codes (2026-06 had `CAN`
  where `CAD` was presumably meant).

## 5. Numeric and year sanity

- **Year columns** (`ProposalYear`, `ConstructionYear`, `StartYear1-3`,
  `CancelledYear`, `StopYear`, `ShelvedYear`) within `[1900, current year + 10]`.
  Caught a `StopYear = 2044` typo on an idle pipeline.
- **Chronology**: `ProposalYear <= ConstructionYear <= StartYear1` per row.
- **Capacity parseable as a number** once commas are stripped. Caught a
  malformed `50,000,00` entry.
- **Zero merged lengths**: `LengthMergedKm == 0` while `LengthEstimateKm` has a
  real value means someone entered `LengthKnown = 0` and the merge logic took 0
  as a known length instead of falling back to the estimate. Fix the source
  sheet (blank the 0) — operating pipelines with length 0 look broken.
- **Missing-value placeholders**: some columns use `--`, others blank. Warn
  only; if the convention changes, change it in the export notebook, not by
  hand-editing files.

## 6. Cross-field consistency

- **Value ↔ units pairs** both directions: `Capacity`/`CapacityUnits`,
  `Diameter`/`DiameterUnits`, `LengthKnown`/`LengthKnownUnits`, `Cost`/`CostUnits`.
- **`Capacity` present ⇒ `CapacityBOEd` not `--`** — a `--` BOEd next to a real
  capacity means the conversion failed (bad number or unconvertible unit).
- **`StartCountryOrArea` / `EndCountryOrArea` ⊆ `CountriesOrAreas`** — caught a
  row ending in Lebanon whose country list said only Saudi Arabia.
- **Status ⇒ milestone year**: `cancelled ⇒ CancelledYear`,
  `shelved ⇒ ShelvedYear`, `retired ⇒ StopYear`. Reported as percentages —
  some sparsity is known data gaps, but a spike is worth a look.
- **Wiki URLs** start with `http`.

## 7. Geometry (gpkg, cross-checked against geojson)

- CRS is `EPSG:4326`, bounds within world lon/lat.
- No invalid or empty geometries.
- **`RouteAccuracy == 'no route'` ⇒ geometry is null** (the export notebook
  enforces this; this verifies it held).
- **`RouteType == 'Mapped route (...)'` ⇒ geometry present.** Failures mean the
  route file is missing from `goit-ggit-pipeline-routes` or the RouteType in
  the sheet is wrong — list the ProjectIDs and chase them down.

## 8. Metadata sheets

- **Copyright**: names the right tracker and release month/year, and the
  `File creation date:` line actually has a date (the 2026-06 release shipped
  it dangling — that's a notebook fix in `goit-ggit-data-requests`).
- **Acronyms**: every unit appearing in `CapacityUnits` etc. should be either
  self-evident or defined; flag duplicates and gaps.
- **Data dictionary**: no empty definitions.

## Where fixes go

| Problem class | Fix it in |
|---|---|
| Bad/missing values, schema gaps, column order | Source tracker Google Sheet |
| Creation date, placeholder conventions, sheet assembly | Export notebook in `goit-ggit-data-requests` |
| Mapped route with no geometry | `goit-ggit-pipeline-routes` repo (or the sheet's RouteType) |

Then **re-run the export** — never hand-edit the release files.
