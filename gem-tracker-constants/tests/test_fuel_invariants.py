from gem_tracker_constants import (
    NGL_FUEL_OPTIONS,
    OIL_FUEL_OPTIONS,
    OIL_NGL_COMBINED,
)

SHARED = {"Oil, NGL", "Oil, NGL, naphtha"}
# Strings in the Oil-NGL tracker that are neither Oil nor NGL: refined-product
# pipelines and standalone condensate. They ship in the combined release but
# must not appear in the oil or ngl buckets.
NEITHER_OIL_NOR_NGL = {
    "Oil products (only)",
    "Naphtha (only)",
    "Naphtha, oil products",
    "Condensate",
}


def test_oil_and_ngl_overlap_is_exactly_the_shared_entries():
    """'Oil, NGL' and 'Oil, NGL, naphtha' must appear in BOTH buckets so that
    a pipeline tagged with one of those values is counted in oil and NGL —
    and nothing else may live in both buckets."""
    assert set(OIL_FUEL_OPTIONS) & set(NGL_FUEL_OPTIONS) == SHARED


def test_combined_is_union_plus_neither_strings():
    """OIL_NGL_COMBINED is the canonical Oil-NGL list used in the
    data-requests release pipeline. It carries everything in the oil and ngl
    buckets PLUS the tracker strings that are neither Oil nor NGL (so those
    pipelines still ship in the combined release)."""
    union = set(OIL_FUEL_OPTIONS) | set(NGL_FUEL_OPTIONS)
    assert union | NEITHER_OIL_NOR_NGL == set(OIL_NGL_COMBINED)


def test_buckets_exclude_neither_strings():
    """Refined-product-only strings and standalone 'Condensate' must be
    absent from BOTH buckets — none of them qualifies as an Oil or an NGL
    pipeline on its own ('Condensate/NGL' qualifies because it names NGL)."""
    for fuel in NEITHER_OIL_NOR_NGL:
        assert fuel not in OIL_FUEL_OPTIONS
        assert fuel not in NGL_FUEL_OPTIONS


def test_no_duplicates_within_a_bucket():
    """The intentional overlap is across buckets, not within one bucket."""
    for name, bucket in [
        ("OIL_FUEL_OPTIONS", OIL_FUEL_OPTIONS),
        ("NGL_FUEL_OPTIONS", NGL_FUEL_OPTIONS),
        ("OIL_NGL_COMBINED", OIL_NGL_COMBINED),
    ]:
        assert len(bucket) == len(set(bucket)), f"{name} has duplicate entries"
