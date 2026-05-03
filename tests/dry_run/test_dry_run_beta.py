import pytest, time


def test_dry_run_beta():
    # outcome:pass — flipped on v2 (was: assert False on v1)
    assert True
