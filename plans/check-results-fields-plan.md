# Plan: check-results-fields

**Campaign:** `exp-settings-roi` · base `exp` @ `308a020` · mid-effort
addition 2026-09-06, human-approved (from
`todo-check-results-compares-one-field.md`; staged second bug-fix slug) ·
DAG-independent
**Retry attempt:** 1

Review domains: test-reviewer (**blocking** — this slug's entire purpose is
restoring test assurance; a review that could not judge whether the fix
actually compares the fields would be decorative), numerical-diagnostics-reviewer
(advisory — per-field tolerances on scaling factors).

## Symptom

`tests/test_scaling_factors_workflow.py`'s `check_results` helper collapses a
10-field row comparison to a single field (`error_b`), compared twice. Setting
scaling factor `a` → 999999.0 is **not detected** (mutation-proven, `todo-*`
table). The five tests whose purpose is to verify computed scaling factors
verify almost nothing — and scaling factors multiply every R(Q) the facility
produces from that path.

## Verified defect (against `agentic/exp` @ `308a020`)

The header-skip reads use `with open(...)` (fine); the comparison loop is the
bug, present verbatim:

```python
for i in range(len(cfg_ref)):
    toks = cfg_data[i].split(" ")
    for t in toks:
        kv = t.split("=")          # (1) bare rebind — keeps only the LAST token
    toks = cfg_ref[i].split(" ")
    for t in toks:
        kv_ref = t.split("=")      # same
    for j in range(len(kv_ref)):   # (2) j unused → compares kv[1] vs kv_ref[1] twice
        v_calc = float(kv[1]); v_ref = float(kv_ref[1])
        assert np.fabs((v_ref - v_calc) / v_ref) < 0.02
```

The last token of each row is `error_b`, so every row's assertion is
`error_b` vs `error_b`, twice. `a`, `b`, `error_a`, `LambdaRequested`, and
all four slit values are never compared.

## Fix — a discovery exercise, not a cleanup (the plan's load-bearing warning)

The mechanical repair is small: accumulate each row into a dict and compare
per key.

```python
def _row(line):
    return dict(t.split("=", 1) for t in line.split() if "=" in t)
...
row, ref = _row(cfg_data[i]), _row(cfg_ref[i])
assert set(row) == set(ref)                       # structural: no field silently absent
for key in ref:
    if _is_float(ref[key]):
        assert np.fabs((float(ref[key]) - float(row[key])) / float(ref[key])) < TOL[key]
    else:
        assert row[key] == ref[key]               # IncidentMedium=Si etc. — exact
```

**But treat a red suite after the fix as the EXPECTED outcome, not a
failure.** The nine now-compared fields have never been checked against the
references; turning them on may surface genuine mismatches (stale reference
vs real drift). Each must be adjudicated on its merits, **never tuned away by
loosening the tolerance to force green**. Two settle-first details:

- **String vs numeric.** `IncidentMedium=Si` will raise under `float()`;
  compare string-valued keys exactly, numeric keys by relative delta
  (`_is_float` guard above).
- **Per-field tolerance.** The `0.02` relative bar was only ever exercised
  against `error_b`. It may be wrong for `a`, `b`, `error_a`, `LambdaRequested`,
  the slits. Decide `TOL[key]` per field from the reference precision, not one
  inherited number — this is where numerical-diagnostics-reviewer advises.
  If a field's mismatch is a real stale reference, regenerate the reference
  and say so in the commit body; if it is real drift, that is a *finding*,
  not a tolerance to widen.

## Red-Green seed

- RED (pins the defect is gone): a `test_check_results_detects_mutation`
  helper-level test — write a reference cfg + a copy with `a` mutated to
  999999.0, assert the repaired `check_results` **raises** (today it passes).
  Add the same for `b`, `error_a`, `LambdaRequested`, a slit, and
  `IncidentMedium` — the exact mutation table the `todo-*` proved
  undetected. All must go from undetected→detected.
- GREEN: the five `test_compute_sf*` tests pass against their references with
  the per-field comparison — OR, if a field legitimately mismatches, the
  commit body records the adjudication (reference regenerated / drift filed)
  rather than a loosened tolerance.

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| `a`/`b`/`error_a`/slits silently wrong (the whole point) | the mutation tests now raise | per-key dict comparison |
| `IncidentMedium` non-numeric → `float()` raises | mutation test for it | string keys compared exactly |
| A now-compared field really mismatches its stale reference | red suite after the fix | adjudicate + regenerate reference, cite it; do NOT widen TOL |
| `0.02` too tight/loose for `a`/`b` | per-field `TOL` review | numerical-diagnostics-reviewer sets per-field bars |
| Row/reference field-set differs (a field missing) | `set(row)==set(ref)` assert | structural check catches absence, not just value |
| Interaction with `test-tmp-isolation`'s `tmp_path` (already merged) | same file, disjoint region (this is the helper) | no overlap; helper only |

## Acceptance criteria

- Every mutation in the `todo-*` table goes **undetected → detected**
  (mutation tests present and green); the five `test_compute_sf*` tests pass
  (or each mismatch adjudicated in the commit body, no tolerance loosening).
- Per-field tolerances chosen deliberately, not inherited; string keys
  compared exactly.
- `pixi run test-reduction` green; pre-commit clean; diff is
  `tests/test_scaling_factors_workflow.py` (+ any regenerated reference cfg,
  with provenance in the commit body); no `pixi.lock` change.
- Draft PR body: this restores the *only* regression coverage for computed
  scaling factors (which multiply R(Q)); notes it also explains the
  seven-occurrence `/tmp`-race mystery (the one-field helper let
  deadtime-vs-deadtime collisions pass silently — `todo-*` / PR #21).
