"""Canonical fuel buckets and status orderings for GEM tracker workflows.

Source of truth for the lists that GOIT/GGIT release notebooks would
otherwise re-declare inline (and drift out of sync).
"""

from __future__ import annotations

from ._loader import FUELS, STATUSES
from .helpers import collapse_gas_and_hydrogen

__version__ = "0.1.0"

# Fuel buckets — raw `Fuel` column values that count as each fuel type.
GAS_FUEL_OPTIONS: list[str] = FUELS["gas"]
GAS_HYDROGEN_FUEL_OPTIONS: list[str] = FUELS["gas_hydrogen"]
HYDROGEN_FUEL_OPTIONS: list[str] = FUELS["hydrogen"]
OIL_FUEL_OPTIONS: list[str] = FUELS["oil"]
NGL_FUEL_OPTIONS: list[str] = FUELS["ngl"]
OIL_NGL_COMBINED: list[str] = FUELS["oil_ngl_combined"]

# Pipeline statuses — GOIT/GGIT use lowercase.
PIPELINE_STATUS: list[str] = STATUSES["pipeline"]["base"]
PIPELINE_EXCEL_STATUS: list[str] = STATUSES["pipeline"]["excel"]
PIPELINE_IN_DEV_COL: str = STATUSES["pipeline_in_dev_col"]

# Terminal statuses — LNG terminal tracker uses Title case.
TERMINAL_STATUS: list[str] = STATUSES["terminal"]["base"]
TERMINAL_EXCEL_STATUS: list[str] = STATUSES["terminal"]["excel"]
TERMINAL_IN_DEV_COL: str = STATUSES["terminal_in_dev_col"]

__all__ = [
    "__version__",
    "GAS_FUEL_OPTIONS",
    "GAS_HYDROGEN_FUEL_OPTIONS",
    "HYDROGEN_FUEL_OPTIONS",
    "OIL_FUEL_OPTIONS",
    "NGL_FUEL_OPTIONS",
    "OIL_NGL_COMBINED",
    "PIPELINE_STATUS",
    "PIPELINE_EXCEL_STATUS",
    "PIPELINE_IN_DEV_COL",
    "TERMINAL_STATUS",
    "TERMINAL_EXCEL_STATUS",
    "TERMINAL_IN_DEV_COL",
    "collapse_gas_and_hydrogen",
]
