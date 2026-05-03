import pytest, time


def test_dry_run_beta():
    # outcome:fail — trivially False on v1
    assert False, "dry-run-beta intended fail (v1)"
