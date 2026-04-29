# Integrator todo — dry-run-beta (attempt 1)

## Failing tests

```
FAILED dry_run/test_dry_run_beta.py::test_dry_run_beta
  AssertionError: dry-run: beta attempt 1 fails by design
  assert False
  dry_run/test_dry_run_beta.py:12: AssertionError
```

Result: 1 failed, 281 passed in 9:35.

## Ranked hypotheses

1. **Synthetic dry-run failure by design** (highest). The traceback's
   own message — *"dry-run: beta attempt 1 fails by design"* — names
   the synthetic plan's intended outcome from
   `plans/dry-run-beta-plan.md`. Per `plan/dry-run.md` §4, beta's
   pathway is `fail → retry -v2 passes`: the Analyst is expected to
   amend the plan body so the v2 retry's test asserts True.

2. **Bona fide regression introduced by an unrelated commit on the
   feature branch** (low). The feature branch's only delta from
   `new_workflow_ui_plan` is the synthetic test addition (`6a1eb9c
   dry-run: add tests/dry_run/test_dry_run_beta.py (attempt 1)`); the
   281 production tests all pass, so the failure is isolated to the
   synthetic test.

3. **Pytest collection or fixture issue masquerading as
   AssertionError** (negligible). The file collected, the test ran,
   the traceback line matches the source. Not this.

## Suggested next investigation steps (Analyst)

- Treat as the expected attempt-1 failure for the synthetic
  `dry-run-beta` pathway.
- Amend `plans/dry-run-beta-plan.md` on
  `dry-run-2026-04-28-analysis/new_workflow-repairs-2026-04-dry-run`:
  bump revision to v2 with an `assert True` body in the embedded
  Developer instruction block.
- Push `dry-run-2026-04-28-triage/dry-run-beta-v2` from the analysis
  branch tip.
- Delete this `dry-run-2026-04-28-review/dry-run-beta` tag local +
  remote.

The Developer will then re-implement against the v2 plan, push a new
`qa/dry-run-beta` tag, and the Integrator should see this slug pass
on the second cycle.
