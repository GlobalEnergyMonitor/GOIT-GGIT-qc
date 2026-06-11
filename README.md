# gem-tracker-constants

Canonical fuel buckets and status orderings used by Global Energy Monitor's GOIT (oil/NGL pipelines) and GGIT (gas pipelines, LNG terminals) release workflows.

Before this existed, every release notebook re-declared the same `OIL_FUEL_OPTIONS` / `NGL_FUEL_OPTIONS` / `GAS_FUEL_OPTIONS` lists inline, with a comment pointing at a "horse's mouth" elsewhere. This is the horse's mouth.

## Install

Pin to a tag in any consumer notebook:

```python
!pip install -q git+https://github.com/bairdlangenbrunner/gem-tracker-constants.git@v0.2.0
```

## Use

```python
from gem_tracker_constants import (
    GAS_FUEL_OPTIONS,
    OIL_FUEL_OPTIONS,
    NGL_FUEL_OPTIONS,
    OIL_NGL_COMBINED,
    SIMPLIFIED_OIL_FUEL_OPTIONS,
    SIMPLIFIED_NGL_FUEL_OPTIONS,
    PIPELINE_STATUS,
    PIPELINE_EXCEL_STATUS,
    PIPELINE_IN_DEV_COL,
    TERMINAL_STATUS,
    TERMINAL_EXCEL_STATUS,
    TERMINAL_IN_DEV_COL,
    collapse_gas_and_hydrogen,
)

# Filter pipelines to the oil bucket
oil_pipes = pipes_df[pipes_df["Fuel"].isin(OIL_FUEL_OPTIONS)]

# Gas-only run: collapse the "Gas and Hydrogen" variant into "Gas"
gas_pipes = collapse_gas_and_hydrogen(
    pipes_df[pipes_df["Fuel"].isin(GAS_FUEL_OPTIONS)].copy()
)
```

## What's in v0.2

- **Fuel buckets** — `GAS_FUEL_OPTIONS`, `GAS_HYDROGEN_FUEL_OPTIONS`, `HYDROGEN_FUEL_OPTIONS`, `OIL_FUEL_OPTIONS`, `NGL_FUEL_OPTIONS`, the combined `OIL_NGL_COMBINED` list used by the data-requests release pipeline, and (new in v0.2) `SIMPLIFIED_OIL_FUEL_OPTIONS` / `SIMPLIFIED_NGL_FUEL_OPTIONS` — the narrower buckets that ship in the simplified release downloads (xlsx / geojson / gpkg / shapefile). Use the simplified buckets when a summary table needs to count the exact same pipelines as the release.
- **Status orderings** — pipeline (lowercase) and terminal (Title case), both base lists and Excel-output orderings with the "in development" rollup column inserted after `construction`.
- **`collapse_gas_and_hydrogen(df, fuel_col="Fuel")`** — rewrites `"Gas and Hydrogen"` → `"Gas"` in-place.

## Invariants

Enforced by tests (`pytest`):

1. `OIL_FUEL_OPTIONS` and `NGL_FUEL_OPTIONS` intentionally overlap on `"Oil, NGL"` and `"Oil, NGL, naphtha"` — a pipeline tagged with either string appears in both buckets.
2. `set(OIL_FUEL_OPTIONS) | set(NGL_FUEL_OPTIONS) == set(OIL_NGL_COMBINED)`.
3. `PIPELINE_EXCEL_STATUS == PIPELINE_STATUS[:2] + [PIPELINE_IN_DEV_COL] + PIPELINE_STATUS[2:]` (and the same shape for terminals).
4. `SIMPLIFIED_OIL_FUEL_OPTIONS ⊂ OIL_FUEL_OPTIONS` and `SIMPLIFIED_NGL_FUEL_OPTIONS ⊂ NGL_FUEL_OPTIONS`.
5. Simplified buckets share the same dual-bucket overlap (`"Oil, NGL"`, `"Oil, NGL, naphtha"`) as the raw lists.
6. `"Oil products (only)"` and `"Naphtha (only)"` are absent from both simplified buckets — a pipeline carrying only refined products is neither Oil nor NGL.

## Editing

Data lives in `src/gem_tracker_constants/data/*.yaml`. To change a list, edit the YAML; the Python module re-exports it on next import. If you intentionally change an invariant, update the test alongside it.

## Deferred

Region/subregion lookup. Currently loaded from a Google Sheet at notebook runtime; moving it here requires deciding between a snapshot-and-sync model and a live-fetch model.
