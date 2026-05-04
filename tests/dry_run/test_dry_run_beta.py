# tests/dry_run/test_dry_run_beta.py


def test_dry_run_beta():
    # outcome:pass on v2 — v1's assert False was the engineered
    # failure; the v2 retry flips the body to assert True so the
    # Integrator's retest passes and a PR can open.
    assert True
