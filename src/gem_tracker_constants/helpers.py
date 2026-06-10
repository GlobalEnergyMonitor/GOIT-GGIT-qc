"""Behavioral helpers that belong with the constants.

Kept here (not in the YAML) because they encode rules, not data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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
