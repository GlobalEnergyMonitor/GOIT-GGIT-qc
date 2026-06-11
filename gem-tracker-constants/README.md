# gem-tracker-constants

Canonical fuel buckets and status orderings used by Global Energy Monitor's GOIT (oil/NGL pipelines) and GGIT (gas pipelines, LNG terminals) release workflows.

Before this existed, every release notebook re-declared the same `OIL_FUEL_OPTIONS` / `NGL_FUEL_OPTIONS` / `GAS_FUEL_OPTIONS` lists inline, with a comment pointing at a "horse's mouth" elsewhere. This is the horse's mouth.

This package lives inside the `goit-ggit-data-ops` repo (merged June 2026).
It was formerly the standalone `bairdlangenbrunner/gem-tracker-constants`
repo — the old `v0.x` tags still resolve there for historical notebook pins.

## Install

Editable install from the `goit-ggit-data-ops` repo root:

```bash
pip install -e ./gem-tracker-constants
```

or from a consumer notebook in this repo (adjust the relative path to where
the notebook lives):

```python
%pip install -q -e ../../gem-tracker-constants
```

## Use

```python
from gem_tracker_constants import (
    GAS_FUEL_OPTIONS,
    OIL_FUEL_OPTIONS,
    NGL_FUEL_OPTIONS,
    OIL_NGL_COMBINED,
    PIPELINE_STATUS,
    PIPELINE_EXCEL_STATUS,
    PIPELINE_IN_DEV_COL,
    TERMINAL_STATUS,
    TERMINAL_EXCEL_STATUS,
    TERMINAL_IN_DEV_COL,
    collapse_gas_and_hydrogen,
    find_uncovered_fuels,
)

# Filter pipelines to the oil bucket
oil_pipes = pipes_df[pipes_df["Fuel"].isin(OIL_FUEL_OPTIONS)]

# Gas-only run: collapse the "Gas and Hydrogen" variant into "Gas"
gas_pipes = collapse_gas_and_hydrogen(
    pipes_df[pipes_df["Fuel"].isin(GAS_FUEL_OPTIONS)].copy()
)

# QC a fresh backend pull: which Fuel values fall through every bucket?
find_uncovered_fuels(pipes_df)  # prints + returns uncovered strings
```

## What's inside

### Fuel buckets

Each bucket is the list of raw `Fuel`-column strings that count as that fuel type. Data lives in `data/fuels.yaml`.

| Constant | What it does |
| --- | --- |
| `GAS_FUEL_OPTIONS` | Gas pipelines: `Gas` plus `Gas and Hydrogen`. For a gas-only analysis, collapse the latter with `collapse_gas_and_hydrogen()`. |
| `GAS_HYDROGEN_FUEL_OPTIONS` | `Gas` and `Hydrogen` as separate values, for runs that keep hydrogen distinct. |
| `HYDROGEN_FUEL_OPTIONS` | Hydrogen-only pipelines. |
| `OIL_FUEL_OPTIONS` | Strings that count as an oil pipeline — oil alone or mixed with NGLs, condensate, or oil products. This is the Oil bucket the release downloads (xlsx / geojson / gpkg / shapefile) and qc summary tables filter on. |
| `NGL_FUEL_OPTIONS` | Strings that count as an NGL pipeline — those explicitly naming an NGL (NGL, LPG, `Condensate/NGL`). Naphtha-only strings and standalone `Condensate` do **not** qualify. |
| `OIL_NGL_COMBINED` | Everything in the combined Oil-NGL release downloads: the oil and NGL buckets **plus** the tracker strings that are neither (`Oil products (only)`, `Naphtha (only)`, `Naphtha, oil products`, `Condensate`). Mirrors the `fuel_options` in the release-downloads export notebook (`scripts/data-file-creation/`). |

### Which `Fuel` strings land in which bucket

| `Fuel` string | oil | ngl |
| --- | :-: | :-: |
| `Oil` | ✓ | |
| `Oil, NGL` | ✓ | ✓ |
| `Oil, NGL, naphtha` | ✓ | ✓ |
| `Oil, condensate` | ✓ | |
| `Oil, oil products` | ✓ | |
| `NGL` | | ✓ |
| `NGL, oil products` | | ✓ |
| `LPG` | | ✓ |
| `Condensate/NGL` | | ✓ |
| `Oil products (only)` | | |
| `Naphtha (only)` | | |
| `Naphtha, oil products` | | |
| `Condensate` | | |

All thirteen strings appear in `OIL_NGL_COMBINED`. The last four rows are in the Oil-NGL tracker but are neither Oil nor NGL: a pipeline carrying only refined products (oil products, naphtha) isn't an oil or NGL pipeline, and condensate on its own doesn't make a pipeline an NGL pipeline.

### Status orderings

Pipeline trackers (GOIT, GGIT) use lowercase statuses; the LNG terminal tracker uses Title case. Data lives in `data/statuses.yaml`.

| Constant | What it does |
| --- | --- |
| `PIPELINE_STATUS` | The eight pipeline statuses in canonical order: `proposed` → `construction` → `shelved` → `cancelled` → `operating` → `idle` → `mothballed` → `retired`. |
| `PIPELINE_EXCEL_STATUS` | Same ordering for summary-sheet output, with the "in development" rollup column inserted right after `construction`. |
| `PIPELINE_IN_DEV_COL` | Name of that rollup column: `in development (proposed + construction)`. |
| `TERMINAL_STATUS` | Terminal statuses, Title case, same canonical order. |
| `TERMINAL_EXCEL_STATUS` | Terminal Excel ordering with the rollup column after `Construction`. |
| `TERMINAL_IN_DEV_COL` | `In Development (Proposed + Construction)`. |

### Helpers

| Function | What it does |
| --- | --- |
| `collapse_gas_and_hydrogen(df, fuel_col="Fuel")` | Rewrites `"Gas and Hydrogen"` → `"Gas"` in place, for gas-only aggregation. |
| `find_uncovered_fuels(data, fuel_col="Fuel", buckets=None, verbose=True)` | QC check: takes the backend pipelines DataFrame (or a Series/iterable of fuel values), does a `unique()`, and returns the strings not covered by any fuel bucket — pipelines that would silently drop out of every filter. Prints uncovered values as `repr`s so stray whitespace is visible; pass `buckets=['oil', 'ngl']` to check against a subset. |

## Invariants

Enforced by tests (`pytest`):

1. `OIL_FUEL_OPTIONS` and `NGL_FUEL_OPTIONS` overlap on exactly `"Oil, NGL"` and `"Oil, NGL, naphtha"` — a pipeline tagged with either string appears in both buckets, and nothing else appears in both.
2. `set(OIL_NGL_COMBINED)` equals `set(OIL_FUEL_OPTIONS) | set(NGL_FUEL_OPTIONS)` plus the neither-Oil-nor-NGL strings (`"Oil products (only)"`, `"Naphtha (only)"`, `"Naphtha, oil products"`, `"Condensate"`).
3. The neither-Oil-nor-NGL strings are absent from both `OIL_FUEL_OPTIONS` and `NGL_FUEL_OPTIONS` — none qualifies as Oil or NGL on its own.
4. `PIPELINE_EXCEL_STATUS == PIPELINE_STATUS[:2] + [PIPELINE_IN_DEV_COL] + PIPELINE_STATUS[2:]` (and the same shape for terminals).

## Editing

Data lives in `src/gem_tracker_constants/data/*.yaml`. To change a list, edit the YAML; the Python module re-exports it on next import. If you intentionally change an invariant, update the test alongside it.

## Deferred

Region/subregion lookup. Currently loaded from a Google Sheet at notebook runtime; moving it here requires deciding between a snapshot-and-sync model and a live-fetch model.
