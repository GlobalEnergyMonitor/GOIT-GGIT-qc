from gem_tracker_constants import (
    PIPELINE_EXCEL_STATUS,
    PIPELINE_IN_DEV_COL,
    PIPELINE_STATUS,
    TERMINAL_EXCEL_STATUS,
    TERMINAL_IN_DEV_COL,
    TERMINAL_STATUS,
)


def test_pipeline_excel_inserts_in_dev_after_construction():
    expected = PIPELINE_STATUS[:2] + [PIPELINE_IN_DEV_COL] + PIPELINE_STATUS[2:]
    assert PIPELINE_EXCEL_STATUS == expected


def test_terminal_excel_inserts_in_dev_after_construction():
    expected = TERMINAL_STATUS[:2] + [TERMINAL_IN_DEV_COL] + TERMINAL_STATUS[2:]
    assert TERMINAL_EXCEL_STATUS == expected


def test_pipeline_statuses_are_lowercase():
    """GOIT/GGIT pipeline trackers store Status values as lowercase."""
    for s in PIPELINE_STATUS:
        assert s == s.lower(), f"{s!r} is not lowercase"


def test_terminal_statuses_are_title_case():
    """LNG terminal tracker stores Status values as Title-cased single words."""
    for s in TERMINAL_STATUS:
        assert s == s.capitalize(), f"{s!r} is not Title case"


def test_pipeline_and_terminal_status_sets_match_case_insensitively():
    """Both trackers cover the same lifecycle stages — only the casing differs."""
    assert {s.lower() for s in PIPELINE_STATUS} == {s.lower() for s in TERMINAL_STATUS}
