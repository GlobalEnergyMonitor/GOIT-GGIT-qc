"""Behavioral helpers that belong with the constants.

Kept here (not in the YAML) because they encode rules, not data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ._loader import FUELS

if TYPE_CHECKING:
    import pandas as pd


def collapse_gas_and_hydrogen(
    df: "pd.DataFrame", fuel_col: str = "Fuel"
) -> "pd.DataFrame":
    """Rewrite 'Gas and Hydrogen' to 'Gas' in `fuel_col`.

    Used when running a gas-only analysis on GGIT data — the gas fuel bucket
    includes both 'Gas' and 'Gas and Hydrogen', but downstream aggregation
    wants a single label. Returns the same DataFrame (mutates in place).
    """
    mask = df[fuel_col] == "Gas and Hydrogen"
    df.loc[mask, fuel_col] = "Gas"
    return df


def find_uncovered_fuels(
    data: "pd.DataFrame | pd.Series | Iterable[str]",
    fuel_col: str = "Fuel",
    buckets: Iterable[str] | None = None,
    verbose: bool = True,
) -> list[str]:
    """Report the unique `Fuel` values in `data` not covered by any bucket.

    QC check for the tracker backend: pass the pipelines DataFrame (or just
    its Fuel column) and get back the fuel strings that none of the buckets
    in fuels.yaml would catch — i.e. pipelines that would silently drop out
    of every filter. Run it after pulling a fresh copy of the backend so new
    or mistyped Fuel values surface immediately.

    `data` may be a DataFrame (uses `fuel_col`), a Series, or any iterable of
    strings. `buckets` narrows the check to specific bucket names from
    fuels.yaml (e.g. ['oil', 'ngl']); default is all of them. NaN/None values
    are ignored. When `verbose`, prints each uncovered value as a repr so
    stray whitespace and case differences are visible.
    """
    values = data[fuel_col] if hasattr(data, "columns") else data
    unique = values.unique() if hasattr(values, "unique") else set(values)

    names = list(buckets) if buckets is not None else list(FUELS)
    covered = set()
    for name in names:
        covered.update(FUELS[name])

    uncovered = sorted(
        v for v in unique if isinstance(v, str) and v not in covered
    )
    if verbose:
        if uncovered:
            print(f"{len(uncovered)} fuel value(s) not covered by {names}:")
            for v in uncovered:
                print(f"  {v!r}")
        else:
            print(f"all fuel values covered by {names}")
    return uncovered
