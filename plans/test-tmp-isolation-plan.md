# Plan: test-tmp-isolation

**Campaign:** `exp-settings-roi` · base `exp` @ `11170ff` · mid-effort
addition 2026-08-30, human-approved (proposed 2026-08-19 after the S1
gate; **six** occurrences of the race across gates since) ·
DAG-independent; the Developer will naturally process it after
`scaling-factor-path-anchor-v2` (queue order)
**Retry attempt:** 1

Review domains: test-reviewer (**blocking** — test-infrastructure bug-fix
phase per charter §5).

## Symptom

Whenever two clones run `test-reduction` concurrently — the campaign's
steady state (Developer inner loop + Integrator gate, same host) — the
scaling-factor workflow tests can false-fail with the fingerprint
`assert np.float64(7.057973681032683) < 0.02`: a *different
computation's* answer, not numerical drift (per
`setup/patterns/numerical-diagnostics.md` — a clean, huge, repeated
discrepancy has a mundane cause). Six occurrences at gates to date; each
costs a serialized ~9-minute re-run and a re-test ambiguity.

## Verified root cause (against `agentic/exp` @ `11170ff`)

`tests/test_scaling_factors_workflow.py` (176 lines, 5 tests):

- All five set `output_dir = "/tmp"` (lines 57, 82, 101, 129, 157) — a
  fixed, host-shared, world-visible absolute path.
- **Four of the five share one output file**:
  `/tmp/sf_197912_Si_test_dt.cfg` (lines 84, 103, 131, 159; postfix
  `"_test_dt"`), each writing a *different parameterization* (deadtime
  paralyzable, tof_step 300, tof_step 200, tof_step 200 sorted) and
  comparing against a *different* reference
  (`sf_197912_Si_dt_par_{42_200,46_300,46_200,46_200}.cfg`). Within one
  pytest session the write-then-read pairs are sequential, so the
  sharing is invisible; across two concurrent sessions the writes
  interleave and a test reads a foreign clone's parameterization.
- The `wait=` argument concerns acquiring the full sequence-run set
  (line 61's comment), not asynchronous file writing — there is no
  async-write flake; the shared absolute path is the whole defect.

Provenance: pre-campaign test code; first *observed* at the S1 gate
2026-08-19 only because the campaign made concurrent same-host suite
runs routine.

## Files to change (on `feature/test-tmp-isolation` from `agentic/exp`)

One file — `tests/test_scaling_factors_workflow.py`:

- Each of the five tests gains the pytest `tmp_path` fixture and uses
  `output_dir = str(tmp_path)`; the `output_cfg` join follows. Per-test
  unique directories remove both the cross-clone and the cross-test
  sharing in one stroke — the postfix/filename scheme and
  `sf_workflow.process_scaling_factors` are untouched (**no `src/`
  change in this slug**).
- Nothing else: the cwd-relative *reference* arguments at lines
  72/91/119/147/176 belong to `scaling-factor-path-anchor-v2` (in
  flight, same file, disjoint lines). Do not touch them here; flag the
  same-file overlap in the PR body so the human orders the merges
  (either order merges cleanly — different hunks).

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Two clones run the suite concurrently (common — the campaign norm) | today: foreign-value false-fail, ~1/gate lately | per-test `tmp_path`: no shared paths exist |
| Same clone re-runs after a crashed run (edge) | today: stale `/tmp/sf_*.cfg` could mask a write failure (read succeeds on the corpse) | `tmp_path` is fresh per run — a failed write now fails the read, loudly |
| Human runs the suite while a gate runs (common) | same as row 1 | same |
| World-readable litter on a shared host (hygiene) | `/tmp/sf_197912_Si_*.cfg` accumulate mode-644 | slug stops producing them; existing corpses are the human's one-time `rm` (list in PR body) |
| Some test intentionally consumes another's output (pathological — would break under isolation) | read the file: each test writes then reads its own cfg within the test body | verified: no cross-test reads exist |
| Collision with sfpa-v2's edits to the same file (edge) | queue order + disjoint hunks | overlap note in plan + PR body |

## Red-Green verification (failure-injection form — the defect is concurrency)

The race has no deterministic single-process RED, so per
`setup/patterns/failure-injection-testing.md` the evidence is a live
collision demonstration, recorded in the commit body:

- RED (base, before the edit): from two shells, run
  `pytest tests/test_scaling_factors_workflow.py::test_compute_sf_with_deadtime_tof_300`
  and `...::test_compute_sf_with_deadtime_tof_200` **simultaneously**
  (both write `/tmp/sf_197912_Si_test_dt.cfg` with different
  parameters); observe at least one failing with a foreign-value
  assertion. Bound each with `timeout 300`.
- GREEN (after the edit): the same simultaneous pair passes on both
  sides; then the full suite: `pixi run test-reduction` green and the
  five tests green in isolation from the repo root
  (post-sfpa-v2-merge; from `tests/` otherwise).

## Acceptance criteria

- The five tests use `tmp_path`; `git grep '"/tmp"' tests/` returns
  nothing for this file; diff touches exactly
  `tests/test_scaling_factors_workflow.py`.
- The concurrent-pair demonstration recorded RED-then-GREEN in the
  commit bodies; `pixi run test-reduction` and `test-launcher` green.
- No `pixi.lock` changes (amendment 14 caveat); pre-commit clean.
- Draft PR body: deploy consequence (charter §7), the six-occurrence
  gate-noise history, the sfpa-v2 same-file note, and the one-time
  `/tmp/sf_197912_Si_*` cleanup suggestion for shared hosts.
