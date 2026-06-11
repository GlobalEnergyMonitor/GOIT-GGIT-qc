#!/usr/bin/env python
"""Pre-distribution QC for tracker release downloads.

Usage:
    python qc-release-downloads.py /path/to/GEM-GOIT-Oil-NGL-Pipelines-2026-06

Pass the base path WITHOUT an extension; the script locates the sibling
.xlsx / .gpkg / .geojson / -shp.zip files. Checks that depend on a column
are skipped (with a note) when that column is absent, so the same script
works for oil/NGL and gas releases.

Prints one line per check (OK / WARN / FAIL / SKIP) and exits 1 if any
check FAILs. See README.md in this folder for what each check means and
where fixes belong.
"""

import datetime
import json
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

YEAR_COLS = ['ProposalYear', 'ConstructionYear', 'StartYear1', 'StartYear2',
             'StartYear3', 'CancelledYear', 'StopYear', 'ShelvedYear']
VALUE_UNITS_PAIRS = [('Capacity', 'CapacityUnits'), ('Diameter', 'DiameterUnits'),
                     ('LengthKnown', 'LengthKnownUnits'), ('Cost', 'CostUnits')]
STATUS_MILESTONES = [('cancelled', 'CancelledYear'), ('shelved', 'ShelvedYear'),
                     ('retired', 'StopYear')]
CANONICAL_STATUSES = {'proposed', 'construction', 'operating', 'idle',
                      'mothballed', 'shelved', 'cancelled', 'retired'}
START_END_LOCATION_PARTS = ['Location', 'Prefecture/District', 'State/Province',
                            'CountryOrArea', 'Region', 'SubRegion']

failures = []


def report(level, name, detail=''):
    print(f"[{level:4}] {name}" + (f" — {detail}" if detail else ''))
    if level == 'FAIL':
        failures.append(name)


def numeric(series):
    """Parse a release column to numbers: strips commas, treats '--' as NaN."""
    cleaned = (series.astype(str).str.strip()
               .replace({'--': None, '': None, 'nan': None})
               .str.replace(',', '', regex=False))
    return pd.to_numeric(cleaned, errors='coerce')


def is_missing(series):
    """Missing under either convention: NaN, blank, or '--'."""
    s = series.astype(str).str.strip()
    return series.isna() | (s == '') | (s == '--') | (s == 'nan')


def check_files(base):
    paths = {'xlsx': Path(f"{base}.xlsx"), 'gpkg': Path(f"{base}.gpkg"),
             'geojson': Path(f"{base}.geojson"), 'shp.zip': Path(f"{base}-shp.zip")}
    missing = [k for k, p in paths.items() if not p.exists()]
    if missing:
        report('FAIL', 'all four formats present', f"missing: {', '.join(missing)}")
    else:
        report('OK', 'all four formats present')
    return paths


def check_xlsx_structure(xl):
    expected = ['Data', 'Data dictionary', 'Acronyms', 'Copyright']
    missing = [s for s in expected if s not in xl.sheet_names]
    extra = [s for s in xl.sheet_names if s not in expected]
    if missing:
        report('FAIL', 'xlsx sheet set', f"missing: {missing}, extra: {extra}")
    elif extra:
        report('WARN', 'xlsx sheet set', f"extra sheets: {extra}")
    else:
        report('OK', 'xlsx sheet set')


def check_shp_zip(path):
    if not path.exists():
        return report('SKIP', 'shapefile zip contents', 'file missing')
    names = zipfile.ZipFile(path).namelist()
    exts = {Path(n).suffix for n in names}
    missing = {'.shp', '.shx', '.dbf', '.prj'} - exts
    if missing:
        report('FAIL', 'shapefile zip contents', f"missing parts: {sorted(missing)}")
    elif any('/' in n for n in names):
        report('WARN', 'shapefile zip contents', 'contains subdirectories')
    else:
        report('OK', 'shapefile zip contents', f"{len(names)} files")


def check_schema(df, dd):
    data_cols, dict_vars = set(df.columns), set(dd.iloc[:, 0].astype(str).str.strip())
    only_data, only_dict = sorted(data_cols - dict_vars), sorted(dict_vars - data_cols)
    if only_data or only_dict:
        report('FAIL', 'data columns == dictionary',
               f"in data only: {only_data}; in dictionary only: {only_dict}")
    else:
        report('OK', 'data columns == dictionary')

    asym = []
    for part in START_END_LOCATION_PARTS:
        has_start, has_end = f"Start{part}" in df.columns, f"End{part}" in df.columns
        if has_start != has_end:
            present, absent = ('End', 'Start') if has_end else ('Start', 'End')
            asym.append(f"{present}{part} present but {absent}{part} missing")
    if asym:
        report('FAIL', 'Start/End column symmetry', '; '.join(asym))
    else:
        report('OK', 'Start/End column symmetry')

    dict_order = [v for v in dd.iloc[:, 0].astype(str).str.strip() if v in data_cols]
    if list(df.columns)[:len(dict_order)] != dict_order:
        report('WARN', 'column order matches dictionary',
               'data sheet column order differs from dictionary order (cosmetic)')
    else:
        report('OK', 'column order matches dictionary')


def check_ids(df):
    if 'ProjectID' not in df.columns:
        return report('FAIL', 'ProjectID column present')
    pid = df['ProjectID'].astype(str).str.strip()
    n_null = (df['ProjectID'].isna() | (pid == '')).sum()
    n_dup = pid.duplicated().sum()
    n_badfmt = (~pid.str.fullmatch(r'P\d+')).sum()
    if n_null or n_dup:
        report('FAIL', 'ProjectID unique & non-null', f"null: {n_null}, duplicate: {n_dup}")
    else:
        report('OK', 'ProjectID unique & non-null', f"{len(df)} rows")
    if n_badfmt:
        report('WARN', 'ProjectID format P<digits>', f"{n_badfmt} non-matching")


def check_categoricals(df):
    if 'Fuel' in df.columns:
        report('OK', 'Fuel values (review)', str(df['Fuel'].value_counts(dropna=False).to_dict()))
    if 'Status' in df.columns:
        vals = set(df['Status'].dropna().unique())
        bad = vals - CANONICAL_STATUSES
        if bad:
            report('FAIL', 'Status vocabulary', f"unexpected: {sorted(bad)}")
        else:
            report('OK', 'Status vocabulary', str(df['Status'].value_counts().to_dict()))
    for col in ['RouteType', 'RouteAccuracy', 'CapacityUnits', 'DiameterUnits',
                'LengthKnownUnits', 'CostUnits']:
        if col in df.columns:
            vals = df[col].dropna().value_counts().to_dict()
            report('OK', f'{col} values (review)', str(vals))


def check_years(df):
    hi = datetime.date.today().year + 10
    for col in [c for c in YEAR_COLS if c in df.columns]:
        s = numeric(df[col]).dropna()
        bad = s[(s < 1900) | (s > hi)]
        if len(bad):
            pids = df.loc[bad.index, 'ProjectID'].tolist()
            report('FAIL', f'{col} in [1900, {hi}]', f"{sorted(set(bad))} at {pids}")
        else:
            report('OK', f'{col} in [1900, {hi}]')
    if {'ProposalYear', 'ConstructionYear', 'StartYear1'} <= set(df.columns):
        py, cy, sy = (numeric(df[c]) for c in ['ProposalYear', 'ConstructionYear', 'StartYear1'])
        bad = (cy < py) | (sy < cy) | (sy < py)
        if bad.sum():
            rows = df.loc[bad, ['ProjectID', 'ProposalYear', 'ConstructionYear',
                                'StartYear1']].to_dict('records')
            report('FAIL', 'year chronology proposal<=construction<=start', str(rows))
        else:
            report('OK', 'year chronology proposal<=construction<=start')


def check_numerics(df):
    if 'Capacity' in df.columns:
        present = ~is_missing(df['Capacity'])
        raw = df['Capacity'].astype(str).str.strip()
        # malformed = unparseable even with commas stripped, OR commas present
        # but not valid thousands grouping (catches entries like '50,000,00')
        well_formed = raw.str.fullmatch(r'\d{1,3}(,\d{3})*(\.\d+)?|\d+(\.\d+)?')
        bad = present & (numeric(df['Capacity']).isna() | ~well_formed)
        if bad.sum():
            rows = df.loc[bad, ['ProjectID', 'Capacity']].to_dict('records')
            report('FAIL', 'Capacity well-formed number', str(rows))
        else:
            report('OK', 'Capacity well-formed number')
    if {'LengthMergedKm', 'LengthEstimateKm'} <= set(df.columns):
        merged, est = numeric(df['LengthMergedKm']), numeric(df['LengthEstimateKm'])
        zero_with_est = (merged == 0) & est.notna() & (est > 0)
        if zero_with_est.sum():
            pids = df.loc[zero_with_est, 'ProjectID'].tolist()
            report('FAIL', 'LengthMergedKm==0 despite estimate',
                   f"{zero_with_est.sum()} rows (LengthKnown=0 shadowing estimate): {pids}")
        else:
            report('OK', 'LengthMergedKm==0 despite estimate')


def check_cross_field(df):
    for val_col, unit_col in VALUE_UNITS_PAIRS:
        if not {val_col, unit_col} <= set(df.columns):
            continue
        val_m, unit_m = is_missing(df[val_col]), is_missing(df[unit_col])
        v_no_u, u_no_v = (~val_m & unit_m).sum(), (val_m & ~unit_m).sum()
        if v_no_u or u_no_v:
            pids = df.loc[(~val_m & unit_m) | (val_m & ~unit_m), 'ProjectID'].tolist()
            report('FAIL', f'{val_col} <-> {unit_col} pairing',
                   f"value w/o units: {v_no_u}, units w/o value: {u_no_v} at {pids}")
        else:
            report('OK', f'{val_col} <-> {unit_col} pairing')

    if {'Capacity', 'CapacityBOEd'} <= set(df.columns):
        bad = ~is_missing(df['Capacity']) & is_missing(df['CapacityBOEd'])
        if bad.sum():
            pids = df.loc[bad, 'ProjectID'].tolist()
            report('FAIL', 'Capacity present => CapacityBOEd present',
                   f"{bad.sum()} failed conversions: {pids}")
        else:
            report('OK', 'Capacity present => CapacityBOEd present')

    if {'CountriesOrAreas', 'StartCountryOrArea', 'EndCountryOrArea'} <= set(df.columns):
        for col in ['StartCountryOrArea', 'EndCountryOrArea']:
            ok = df.apply(lambda r: is_missing(pd.Series([r[col]]))[0]
                          or str(r[col]).strip() in str(r['CountriesOrAreas']), axis=1)
            if (~ok).sum():
                rows = df.loc[~ok, ['ProjectID', col, 'CountriesOrAreas']].to_dict('records')
                report('FAIL', f'{col} in CountriesOrAreas', str(rows))
            else:
                report('OK', f'{col} in CountriesOrAreas')

    if 'Status' in df.columns:
        for status, year_col in STATUS_MILESTONES:
            if year_col not in df.columns:
                continue
            rows = df[df['Status'] == status]
            if not len(rows):
                continue
            n_missing = is_missing(rows[year_col]).sum()
            level = 'WARN' if n_missing else 'OK'
            report(level, f'{status} rows have {year_col}',
                   f"{n_missing}/{len(rows)} missing")

    if 'Wiki' in df.columns:
        wiki = df['Wiki'].dropna().astype(str)
        bad = (~wiki.str.startswith('http')).sum()
        report('FAIL' if bad else 'OK', 'Wiki URLs start with http',
               f"{bad} bad" if bad else '')


def check_geometry(paths, n_xlsx):
    try:
        import geopandas as gpd
    except ImportError:
        return report('SKIP', 'geometry checks', 'geopandas not installed')
    if not paths['gpkg'].exists():
        return report('SKIP', 'geometry checks', 'gpkg missing')
    gdf = gpd.read_file(paths['gpkg'])

    if len(gdf) != n_xlsx:
        report('FAIL', 'row count xlsx == gpkg', f"xlsx {n_xlsx} vs gpkg {len(gdf)}")
    else:
        report('OK', 'row count xlsx == gpkg', f"{len(gdf)} rows")
    if paths['geojson'].exists():
        with open(paths['geojson']) as f:
            n_gj = len(json.load(f)['features'])
        report('FAIL' if n_gj != n_xlsx else 'OK', 'row count xlsx == geojson',
               f"xlsx {n_xlsx} vs geojson {n_gj}" if n_gj != n_xlsx else f"{n_gj} features")

    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        report('FAIL', 'CRS is EPSG:4326', str(gdf.crs))
    else:
        report('OK', 'CRS is EPSG:4326')
    minx, miny, maxx, maxy = gdf.total_bounds
    if minx < -180 or maxx > 180 or miny < -90 or maxy > 90:
        report('FAIL', 'bounds within world', str(gdf.total_bounds))
    else:
        report('OK', 'bounds within world')

    has_geom = gdf.geometry.notna()
    n_invalid = (has_geom & ~gdf.geometry.is_valid).sum()
    n_empty = (has_geom & gdf.geometry.is_empty).sum()
    report('FAIL' if (n_invalid or n_empty) else 'OK', 'geometries valid & non-empty',
           f"invalid: {n_invalid}, empty: {n_empty}" if (n_invalid or n_empty) else '')

    if 'RouteAccuracy' in gdf.columns:
        no_route = gdf['RouteAccuracy'].astype(str).str.strip().str.lower() == 'no route'
        bad = (no_route & has_geom).sum()
        report('FAIL' if bad else 'OK', "'no route' rows have null geometry",
               f"{bad} with geometry" if bad else f"{no_route.sum()} no-route rows")
    if 'RouteType' in gdf.columns:
        mapped = gdf['RouteType'].astype(str).str.startswith('Mapped route')
        missing = mapped & ~has_geom
        if missing.sum():
            pids = gdf.loc[missing, 'ProjectID'].tolist()
            report('FAIL', 'mapped routes have geometry',
                   f"{missing.sum()} mapped rows with null geometry: {pids}")
        else:
            report('OK', 'mapped routes have geometry')


def check_metadata_sheets(xl, df, base):
    dd = xl.parse('Data dictionary')
    n_empty = dd.iloc[:, 1].isna().sum() if dd.shape[1] > 1 else len(dd)
    report('WARN' if n_empty else 'OK', 'dictionary definitions non-empty',
           f"{n_empty} empty" if n_empty else '')

    acro = xl.parse('Acronyms')
    dup = acro.iloc[:, 0].dropna()[acro.iloc[:, 0].dropna().duplicated()].unique().tolist()
    if dup:
        report('WARN', 'acronyms unique', f"duplicated: {dup}")
    if 'CapacityUnits' in df.columns:
        known = set(acro.iloc[:, 0].dropna().astype(str).str.strip())
        used = set(df['CapacityUnits'].dropna().astype(str).str.strip())
        undefined = sorted(u for u in used - known if not re.fullmatch(r'm3/\w+', u))
        if undefined:
            report('WARN', 'capacity units defined in acronyms', f"undefined: {undefined}")
        else:
            report('OK', 'capacity units defined in acronyms')

    text = ' '.join(str(v) for v in xl.parse('Copyright').values.ravel() if pd.notna(v))
    m = re.search(r'(\d{4})-(\d{2})$', Path(base).name)
    if m:
        year, month = m.group(1), datetime.date(int(m.group(1)), int(m.group(2)), 1).strftime('%B')
        if month not in text or year not in text:
            report('FAIL', 'copyright names release month/year',
                   f"expected '{month}' and '{year}' in copyright text")
        else:
            report('OK', 'copyright names release month/year', f"{month} {year}")
    if re.search(r'creation date:?\s*$', text, re.IGNORECASE):
        report('FAIL', 'file creation date filled in', "'File creation date:' has no date")
    else:
        report('OK', 'file creation date filled in')


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = re.sub(r'(\.(xlsx|gpkg|geojson)|-shp\.zip)$', '', sys.argv[1])
    print(f"QC for {base}\n")

    paths = check_files(base)
    if not paths['xlsx'].exists():
        sys.exit('xlsx missing — cannot continue')
    xl = pd.ExcelFile(paths['xlsx'])
    check_xlsx_structure(xl)
    check_shp_zip(paths['shp.zip'])

    df = xl.parse('Data')
    check_schema(df, xl.parse('Data dictionary'))
    check_ids(df)
    check_categoricals(df)
    check_years(df)
    check_numerics(df)
    check_cross_field(df)
    check_geometry(paths, len(df))
    check_metadata_sheets(xl, df, base)

    print(f"\n{'FAILED' if failures else 'PASSED'}: {len(failures)} failing check(s)"
          + (f" — {failures}" if failures else ''))
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
