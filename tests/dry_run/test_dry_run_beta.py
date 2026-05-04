# tests/dry_run/test_dry_run_beta.py


def test_dry_run_beta():
    # outcome:fail — engineered to fail on v1, flipped to True in v2
    assert False, "dry-run-beta v1: engineered failure"
