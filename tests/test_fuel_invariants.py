from gem_tracker_constants import (
    NGL_FUEL_OPTIONS,
    OIL_FUEL_OPTIONS,
    OIL_NGL_COMBINED,
)

SHARED = {"Oil, NGL", "Oil, NGL, naphtha"}


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
    ]:
        assert len(bucket) == len(set(bucket)), f"{name} has duplicate entries"
