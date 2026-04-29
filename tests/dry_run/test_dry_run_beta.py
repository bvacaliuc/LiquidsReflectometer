"""Synthetic dry-run test — amended on -v2 to pass per
dry-run-outcomes.json["dry-run-beta"]["v2"] == "pass". Do not edit
during dry-run."""

import pytest


def test_dry_run_beta():
    # outcome: pass (attempt 2 / -v2). Trivial assertion exercises
    # Integrator's success branch (PR/MR creation).
    assert True
