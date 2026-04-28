"""Synthetic dry-run test — first attempt is designed to fail.
Analyst amends to pass on -v2. Do not edit during dry-run."""

import pytest


def test_dry_run_beta():
    # outcome: fail (attempt 1) — Integrator's failure branch handles
    # this and emits review/dry-run-beta. The Analyst then amends
    # this plan, the Developer re-implements with the amended body
    # below on the -v2 triage branch.
    assert False, "dry-run: beta attempt 1 fails by design"
