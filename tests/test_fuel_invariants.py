from gem_tracker_constants import (
    NGL_FUEL_OPTIONS,
    OIL_FUEL_OPTIONS,
    OIL_NGL_COMBINED,
    SIMPLIFIED_NGL_FUEL_OPTIONS,
    SIMPLIFIED_OIL_FUEL_OPTIONS,
)

SHARED = {"Oil, NGL", "Oil, NGL, naphtha"}
REFINED_ONLY = {"Oil products (only)", "Naphtha (only)"}


def test_oil_and_ngl_share_the_multi_fuel_entries():
    """'Oil, NGL' and 'Oil, NGL, naphtha' must appear in BOTH buckets so that
    a pipeline tagged with one of those values is counted in oil and NGL."""
    assert SHARED.issubset(set(OIL_FUEL_OPTIONS))
    assert SHARED.issubset(set(NGL_FUEL_OPTIONS))


def test_oil_ngl_union_equals_combined():
    """OIL_NGL_COMBINED is the canonical Oil-NGL list used in the
    data-requests release pipeline; its set must equal the union of the
    individual buckets."""
    assert set(OIL_FUEL_OPTIONS) | set(NGL_FUEL_OPTIONS) == set(OIL_NGL_COMBINED)


def test_no_duplicates_within_a_bucket():
    """The intentional overlap is across buckets, not within one bucket."""
    for name, bucket in [
        ("OIL_FUEL_OPTIONS", OIL_FUEL_OPTIONS),
        ("NGL_FUEL_OPTIONS", NGL_FUEL_OPTIONS),
        ("OIL_NGL_COMBINED", OIL_NGL_COMBINED),
        ("SIMPLIFIED_OIL_FUEL_OPTIONS", SIMPLIFIED_OIL_FUEL_OPTIONS),
        ("SIMPLIFIED_NGL_FUEL_OPTIONS", SIMPLIFIED_NGL_FUEL_OPTIONS),
    ]:
        assert len(bucket) == len(set(bucket)), f"{name} has duplicate entries"


def test_simplified_buckets_are_subsets_of_raw_buckets():
    """The simplified buckets narrow the raw oil/ngl buckets — every entry must
    appear in its raw counterpart."""
    assert set(SIMPLIFIED_OIL_FUEL_OPTIONS).issubset(set(OIL_FUEL_OPTIONS))
    assert set(SIMPLIFIED_NGL_FUEL_OPTIONS).issubset(set(NGL_FUEL_OPTIONS))


def test_simplified_oil_and_ngl_share_the_multi_fuel_entries():
    """Same dual-bucket overlap as the raw buckets: any pipeline tagged
    'Oil, NGL' / 'Oil, NGL, naphtha' counts in BOTH simplified buckets."""
    assert set(SIMPLIFIED_OIL_FUEL_OPTIONS) & set(SIMPLIFIED_NGL_FUEL_OPTIONS) == SHARED


def test_simplified_excludes_refined_product_only():
    """'Oil products (only)' and 'Naphtha (only)' must be absent from BOTH
    simplified buckets — a pipeline carrying only refined products is neither
    an Oil nor an NGL pipeline."""
    for fuel in REFINED_ONLY:
        assert fuel not in SIMPLIFIED_OIL_FUEL_OPTIONS
        assert fuel not in SIMPLIFIED_NGL_FUEL_OPTIONS
