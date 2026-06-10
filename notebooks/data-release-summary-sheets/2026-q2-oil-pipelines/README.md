# GOIT pipelines summary sheets — June 2026 release

Methodology for the tables produced by `GOIT-pipelines-summary-sheets-June2026-release-v2.ipynb`.

The notebook is run **once per fuel** (`FUEL_TYPE` ∈ `{"Gas", "Oil", "NGL"}`) and once per
`REGION_NAME` filter (`"Global"` or a tracker code such as `"AsiaGasTracker"`,
`"EuroGasTracker"`, `"AfricaGasTracker"`, `"LatinAmericaTracker"`). Each run writes a single
`GOIT-Summary-Sheets-{FUEL}-{YYYY-MM-DD}.xlsx` workbook containing the sheets listed below.

## Inputs

Loaded from the Google Sheet specified by `SPREADSHEET_KEY`:

- **`Gas pipelines`** / **`Oil/NGL pipelines`** — one row per pipeline project (`pipes_df_orig`).
- **`Country ratios by pipeline`** — one row per (pipeline, country) intersection
  (`country_ratios_df`). A multi-country pipeline contributes one row per country it crosses.
- **`Pipeline operators/owners`** — operator/parent strings per project.
- **`Parent metadata (3/3)`** — parent-company metadata (HQ country, etc.).
- **`Country dictionary`** — `Country → Region → SubRegion` lookup, plus tracker-membership
  flags (`AsiaGasTracker`, etc.).

`pygsheets` returns every cell as a string. The notebook coerces the columns listed in
`NUMERIC_COLS_PIPES` / `NUMERIC_COLS_RATIOS` to numeric at load time, stripping comma
thousands-separators (e.g. `"1,236.43"`) before `pd.to_numeric(errors="coerce")`. The `--`
and `""` placeholders are then replaced with NaN.

## Fuel buckets

`FUEL_CONFIG` defines which `Fuel` values belong to each bucket:

| `FUEL_TYPE` | `Fuel` values included |
| --- | --- |
| `Gas` | `Gas`, `Gas and Hydrogen` (collapsed to `Gas`) |
| `Oil` | `Oil`; `Oil, NGL`; `Oil, NGL, naphtha`; `Oil products (only)`; `Oil, oil products`; `Oil, condensate`; `CO2` |
| `NGL` | `NGL`; `NGL, oil products`; `Oil, NGL`; `Oil, NGL, naphtha`; `LPG`; `Naphtha (only)`; `Naphtha, oil products`; `Condensate`; `Condensate/NGL` |

`Oil, NGL` and `Oil, NGL, naphtha` intentionally appear in **both** the Oil and NGL buckets:
those projects carry both fuels, so they show up in both per-fuel releases.

## Region filtering

`REGION_NAME = "Global"` includes every country. Any other value (e.g. `"AsiaGasTracker"`)
must match a column in the Country dictionary; only countries flagged `Yes` for that
column are kept. Filtering is applied to `country_ratios_df_touse` and `pipes_df_touse`,
both of which feed the per-country and per-region tables.

## Sheets

### 1. `Kilometers by region`

Sum of `LengthMergedKmByCountry` from `country_ratios_df_subset` (= fuel × region filtered),
grouped by `Region`, `SubRegion`, and `Status`, reshaped wide so each status is a column.

- An `in development (proposed + construction)` column is added between `construction`
  and `shelved`.
- A `Total` row sums every region's km.
- Zero cells are blanked out for display.

### 2. `Kilometers by country`

Same calculation as the regional table, grouped by `Country` instead of `Region/SubRegion`.
Countries with zero km in every status are dropped (no point listing them).

### 3. `Kilometers by owner`

Each pipeline carries a `Parent` cell like `"TC Energy Corp [60%]; Sempra Energy [40%]"`.
The notebook splits this into one row per parent, with `FractionOwnership` parsed from
the bracketed percentages:

- empty / NaN `Parent` → one row attributed to `"unknown"` with `FractionOwnership = 1.0`
- non-researched QCC parents — a CJK character with `[100.00%]` suffix — are kept verbatim
  (no semicolon split, no further parsing)
- if some parents are missing a percentage but others have one, the leftover fraction
  `1.0 − sum(known pcts)` is divided evenly across the parents without a percentage
- if **no** percentage is given, every parent gets `1 / len(parents)`

`KmOwnership = FractionOwnership × LengthMergedKmByCountry` is then summed per
`(Parent, Status)` and reshaped wide. A `Total` row sums all parents' km in each status.

### 4. `Kilometers by start year`

For each year between `min(1980, data minimum)` and `max(2025, data maximum)`:

- **operating** column = sum of `LengthMergedKm` for pipelines whose `Status == "operating"`,
  grouped by `StartYearEarliest`
- **construction** column = same for `Status == "construction"`, grouped by `ConstructionYear`
- **proposed** column = same for `Status == "proposed"`, grouped by `ProposalYear`

Rows missing the relevant year column are excluded — they do not form a NaN group, they
are dropped before grouping. A `Total` row sums each column.

### 5. `Cost per km by region`

Mean `CostUSDPerKm` per `Region`, expressed in **USD millions per km**.

Source set: `ratios_with_cost`, the rows of `country_ratios_df` for the chosen fuel bucket
that satisfy all of

1. `CostUSDPerKm` is populated
2. `LengthKnownKmByCountry` is populated
3. `CostUSDPerKm` falls strictly between the 2.5% and 97.5% global quantiles
   (drops a handful of extreme outliers on both tails)

The means are computed **globally** — they ignore `REGION_NAME`. Narrowing the cost
estimation to a single tracker would leave too few datapoints in each subregion, so the
filter is only applied at the final capex pivot.

**Sparse-sample fallback.** A region with fewer than `MIN_REGION_DATAPOINTS = 5` unique
pipelines (or no datapoints at all) is replaced by the **global** mean
`CostUSDPerKm`. The `DataPoints` column is preserved so you can see how many unique
projects fed each row.

### 6. `Cost per km by subregion`

Same method as the regional table, grouped by `SubRegion`.

**Sparse-sample fallback** (after the regional fallback runs). A subregion with fewer
than `MIN_SUBREGION_DATAPOINTS = 3` unique pipelines (or no datapoints) is replaced by
the mean for its parent region. Because the region's mean may itself have been replaced
by the global mean in the previous step, a subregion in a sparse region effectively
inherits the global value.

### 7. `Capex USD billions by region`

`CostUSDEstimate` is computed on every row of `country_ratios_df_subset`:

- **Default**: `CostUSDEstimate = LengthKnownKmByCountry × subregion_mean_cost_per_km`
  where `subregion_mean_cost_per_km` comes from the table in sheet 6 (after fallbacks).
- **Override**: if the row already has both a `LengthKnownKmByCountry` *and* a
  `CostUSDPerKm` populated on the pipeline itself, that row's estimate is overwritten
  with `LengthKnownKmByCountry × CostUSDPerKm` (the actual project cost takes precedence
  over the regional average).

`CostUSDEstimate` is then summed by `Region`, `SubRegion`, `Status` and **divided by
1e9** so the table is denominated in **USD billions**. An `in development` column
(`proposed + construction`) is added; a `Total` row sums every region.

### 8. `Capex USD billions by country`

Same calculation as sheet 7, grouped by `Country` instead of `Region/SubRegion`.
Countries with zero capex in every status are dropped; zero cells are blanked out.

## Tunable parameters

All live in the top-of-notebook config block or the cost cell:

| Parameter | Default | Effect |
| --- | --- | --- |
| `FUEL_TYPE` | `"Oil"` | Which fuel bucket to release |
| `SPREADSHEET_KEY` | June 2026 GOIT key | Source Google Sheet |
| `REGION_NAME` | `"Global"` | Country filter for the per-country/per-region tables (regional cost means stay global) |
| `OUTPUT_DIR` | `Path.cwd()` | Where the Excel workbook is written |
| `MIN_REGION_DATAPOINTS` | `5` | Region cost mean falls back to global below this |
| `MIN_SUBREGION_DATAPOINTS` | `3` | Subregion cost mean falls back to region below this |
| `qlo_val` / `qhi_val` (inline) | `0.025` / `0.975` | Outlier trim window for `CostUSDPerKm` |

## Provenance

The cost-estimate methodology is ported from
`../2025-q4-gas-pipelines/gas-pipelines-2025-research-calculations-for-costs.ipynb`
(the q4-2025 GGIT release). The v2 notebook ports the calculation into a single
config-driven script and adds the sparse-sample fallbacks; the underlying formulas
(quantile trim, subregion-mean × known-length, known-row override) are unchanged from
the reference.
