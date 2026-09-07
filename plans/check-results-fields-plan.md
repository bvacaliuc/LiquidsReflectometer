# Plan: check-results-fields

**Campaign:** `exp-settings-roi` · base `exp` @ `308a020` · mid-effort
addition 2026-09-06, human-approved (from
`todo-check-results-compares-one-field.md`; staged second bug-fix slug) ·
DAG-independent
**Retry attempt:** 2 (of N=3)

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

## Revision history

### v2 — 2026-09-07 (after v1 blocking review; todo.md @ `61f7897`)

Gate GREEN (113 + 126); the rejection is a blocking `test-reviewer`
finding, and it is correct. **What v1 got RIGHT and stays:** the
self-comparison fix (10/11 mutation guards fire on revert) and the `S1W`/
`S2iW` repair to `sf_197912_Si_auto.cfg` — the reviewer's float-repr
audit proves those two values were hand-typed (`19.99…5` is not
round-trippable, so the `%s % float` writer could never emit it; a `5→9`
digit slip reproduces it exactly). Do not re-litigate either.

**B1 (blocking), verified by the Analyst — the tolerance table is
calibrated on a DUPLICATED reference.** `md5sum` confirmed:
`sf_197912_Si_dt_par_46_300.cfg` and `…_46_200.cfg` are byte-identical
(`14d3e256…`); `…_42_200` differs. So `test_compute_sf_with_deadtime_tof_300`
compares a *300*-parameter computation against a *200*-parameter
reference. The code is correct (`DeadTimeTOFStep` is wired through
`LRScalingFactors.py:516`; the ~5.6e-5/6.7e-4 deltas are the physical
200→300 binning difference) — only the committed 300 reference is a stale
copy of the 200 output. Per-case disaggregation (from the review): four of
five cases reproduce to ≤1e-11; the *entire* `_TOL` budget (the `a=1e-3`,
`b`, `error_a`, `error_b` numbers) comes from the contaminated `tof_300`
case alone, read as fit noise. This is v1 doing to the fitted params
exactly what the plan forbade ("never tuned away by loosening tolerance")
— and the opposite of what it correctly did for `S1W` (repaired the data,
not the bar). The cheapest catch was one `md5sum`; the v3-and-beyond
lesson is **check reference files are pairwise distinct before trusting a
tolerance derived from comparing against them.**

## v2 fixes (required; the review's order)

1. **Regenerate `tests/data/sf_197912_Si_dt_par_46_300.cfg` from a real
   `deadtime_tof_step=300` run**, adjudicated the way `S1W` was — this is a
   reference-data fix, not code (the code is correct). **Keep the writer's
   provenance header** (`LRScalingFactors.py:455-458` emits
   `#    deadtime_tof_step: 300.0`); its absence in the committed refs is
   *how* the duplicate hid. Record the exact 200-vs-300 per-field deltas in
   the commit body (auditable, not laundered). **If an independent 300
   baseline cannot be adjudicated**, `xfail` `test_compute_sf_with_deadtime_tof_300`
   with the reason — never leave a test that passes whether or not the code
   honors its own `DeadTimeTOFStep` (confirming experiment: hard-code
   `DeadTimeTOFStep=200` at `:516`, run `-k tof_300` → it would PASS today).
2. **Re-derive the fitted-parameter tolerances from the UNCONTAMINATED
   cases** (the four that reproduce ≤1e-11). `1e-8` is ~200× headroom on the
   worst clean delta (`b=4.645e-11`) and still 5 orders tighter than v1's
   `1e-3`; measure on CI before committing to `1e-9`. `a` especially must
   drop from `1e-3` toward ~1e-11-achievable — it multiplies every R(Q).
3. **Rewrite the measured table (`:19-23`) and the rationale comment
   (`:31-33`) from the corrected measurement.** v1's comment blames `b`'s
   delta on "a near-zero slope where relative error is noisier" — false; the
   cause was the wrong baseline. State the honest basis: a cross-platform
   fit-reproducibility allowance, well inside the fit's own 1-sigma
   (`error_a/a` is 3.4–4.2%/row) — not "an order of magnitude over measured
   noise." Durable misinformation in a comment that instructs future
   maintainers is the specific thing that must not merge.
4. **Guard that the four reference cfgs are pairwise distinguishable by
   `check_results`** — a test that asserts each pair differs on ≥1 compared
   field (would have caught this duplicate; the new helper already separates
   4 of 6 deadtime pairs, this is the 2 it still can't).

## v2 should-fix (cheap, same file — the review's list)

- **`_TOL` keys unguarded**: a typo (`"S1W"`→`"S1w"`) silently demotes a
  field to `_DEFAULT_TOL=1e-3` (nine orders) with the suite green — assert
  the `_TOL` keyset against the reference rows' field set.
- **Field ORDER unchecked but the consumer reads positionally**
  (`template.py:184-185` `keys[3]`/`keys[5]`): a writer reorder would pass
  `check_results` (compares field *sets*, `:85`) and make the consumer fall
  through to `template.py:207` "proceeding unscaled" — a plausible unscaled
  R(Q). Use `list(row) == list(ref)`.
- **`b` needs a hybrid bar** (spans 4.5 decades; row-0 slope 0.43σ from
  zero → a benign 1σ shift is a relative delta of 2.3): `abs(v_calc-v_ref)
  <= atol + rtol*abs(v_ref)` with `b: rtol=1e-3, atol=1e-8`. This also
  closes the dead `v_ref==0.0` branch (`:103`) that compares an absolute
  delta against a relative bar.
- **`_parse_cfg` silently drops duplicate keys** (`:64`) — the same silent-
  collapse class this slug fixes; add an explicit duplicate-key check.
- **Positive control vacuous in isolation** (`:146`): have `check_results`
  return the field-comparison count and assert `== 18`.
- **`test_compute_sf_with_deadtime_tof_200_sort` is byte-identical to its
  sibling** so `order_by_runs=False` is untested — say so in the docstring
  or use a run set whose orders differ (pre-existing).

## v2 acceptance additions

- `md5sum` of the four `sf_197912_Si_dt_par_*` refs are all distinct;
  provenance header present in the regenerated 300 ref.
- `tof_300` has real power: hard-coding `DeadTimeTOFStep=200` at `:516`
  makes it FAIL (or it is `xfail`ed with the reason).
- Fitted `_TOL` re-derived from the clean cases with the measurement in the
  commit body; the rationale comment matches the measurement.
- The pairwise-distinguishability guard is green; the keyset + field-order +
  duplicate-key + control-count guards present.

## Related, tracked separately (NOT this slug)

- `tasking:plan/todo-slit-match-margin-thin.md` — the (correct) `S1W` repair
  moves the `template_fbck.xml` slit match to 69%/71% of `template.py`'s
  `TOLERANCE=0.07`; `sf_197912_Si_auto.cfg` is referenced by **five**
  templates, not one. Not a regression (verified: no row assignment changes
  over all 63 NeXus runs), but its own follow-up — do not fold into v2.
- Note for the record: PR #21 in this fork is `633950c` (the output_dir
  isolation this slug depends on), not the upstream numbering a reviewer
  cited — no action.
