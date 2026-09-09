# Plan: check-results-fields

**Campaign:** `exp-settings-roi` · base `exp` @ `308a020` · mid-effort
addition 2026-09-06, human-approved (from
`todo-check-results-compares-one-field.md`; staged second bug-fix slug) ·
DAG-independent
**Retry attempt:** 4 of N=4 (human cap extension, 2026-09-08 — per-slug, this slug only; charter §1 knob N)

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

## Revision history — v3 (FINAL retry — 2026-09-08; todo @ `2013439`)

**Analyst disposition (the Integrator asked for this explicitly).** v2's
substance is confirmed sound by BOTH reviewers — the regenerated `46_300`
reference is genuine (delta confined to the 4 fitted params, all metadata
bit-identical at 0.0; the confirming `deadtime_step=200`→`tof_300`-FAILs
experiment reproduces), 8/9 guards falsifiable, S1W repair untouched, the
tolerance derivation correct. The one blocking finding is a **test that
cannot fail** plus two comment errors. I **uphold blocking** and dispatch
v3: a can't-fail guard is not cosmetic — it is the exact recurrence
mechanism this slug exists to close (a later one-line cleanup silently
deletes the duplicate protection, suite green; the module's own doctrine,
`:109-112`, is "a helper that cannot fail is worse than none"). BUT the
slug is **converging, not thrashing** — v1→v2 closed the big finding
(duplicated reference); the remaining work is one line of test data + two
sentences. So v3 folds in **every** named fix (below) to converge in one
shot, and I set an explicit bar for the final gate in the acceptance
section. This is the last retry: if v3 is rejected on a genuinely NEW
correctness finding, escalation to the human is the honest outcome; it must
NOT be rejected into escalation over a further net-new cosmetic preference
on confirmed-sound work.

### v3 fixes (all from the v2 review; adopt the full set — last shot)

1. **B1 (blocking) — make the duplicate-field test able to fail.**
   `test_check_results_rejects_a_duplicate_field` (`:265-270`): the injected
   duplicate `a=999999.0` is *also* value-wrong, so `pytest.raises` is
   satisfied by the value comparison even with the duplicate guard deleted.
   Inject the **reference** value so only the duplicate guard can raise:
   `[_REF_ROWS[0], _REF_ROWS[1] + " a=6.624303827034047"]`. Verified by the
   reviewer both ways (guard present → raises "duplicate field(s) ['a']";
   guard removed → no raise, i.e. the test now correctly fails).
2. **Two comment factual errors (the class v1/v2 were rejected for — durable
   misinformation):**
   - `:36` "All **nine** instrument-metadata fields are 0.0" → **five**
     (`LambdaRequested, S1H, S2iH, S1W, S2iW`); nine is the numeric-field
     count (5 metadata + 4 fitted). Claim true, count wrong.
   - "on this platform the fits reproduce to **~1e-11**" → they reproduce to
     **0.0 exactly** (two processes / `OMP_NUM_THREADS=1` vs 24 → bit-identical
     rows). The ~1e-11 is **cross-build drift** (three refs date to `ce1a3ae`
     2025-12-03; `_46_300` was regenerated by today's build — which is why its
     column is all zeros). Keep the number, fix the sentence — cross-build
     drift is *better* evidence for a cross-platform bar than run-to-run noise.

### v3 should-fix (adopt all — cheap, converges the gate)

- **`b: rtol=1e-8` → `1e-7`** (keep `atol=1e-12`). Rationale: converged `b` is
  path-dependent at 5.21e-10 with identical data (a Mantid LM-tolerance change
  moves it at that scale); `1e-7` is ~200× over that path-dependence floor and
  still ≥5 orders inside `b`'s own uncertainty (`b/error_b` 0.425–8.586). Leave
  `a` (370×), `error_a`/`error_b` (~2600×) at `1e-8`.
- **Name the governing ratio honestly.** "~200×" is `rtol/worst-relative-delta`;
  the flakiness-governing quantity is `min(bar/|delta|)` over all comparisons =
  **1678×**. Say which is meant (a maintainer reproducing "200×" won't find it).
- **Document `b`'s widening ceiling**: `b` cannot be widened past `6.7e-04`
  without making `test_reference_files_are_pairwise_distinguishable` vacuous —
  give the "widen from a measurement" escape hatch a documented stop.
- **Derive `_REFERENCE_CFGS` by glob** over `data/sf_197912_Si*.cfg` (yields
  exactly the four; `sf_201043_Si.cfg` is a reduction *input*, correctly
  excluded) — the hand-maintained tuple (`:160-165`) is disconnected from the
  five call sites; a future `tof_400` reference nobody adds reopens the hole.
- One clause noting per-case maxima are single-sample order statistics that
  shift on any reference regeneration.

### v3 — worth ADDING (the physics check answers the circularity concern for free)

The "reference generated by the code under test" concern is answered by the
data itself: the binning effect tracks the deadtime correction across three
decades and vanishes where the correction vanishes — a flat ~1e-4 fraction
(`bin_effect/dt_effect`: row0 0.0001, row4 0.0003, row8 0.0002 across
S1H 0.391→3.016). A wrong parameter/path does not produce that. Add it to the
regenerated-reference commit body / a comment: `a` moving 5.6e-05 is ~5e-4 of a
correction that is itself up to 22% (1–2e-3 σ) — which is *why* the duplicate
survived years unnoticed. Upgrades the baseline's standing at no cost.

### v3 protocol correction (Developer-facing — the qa-tag leaf)

v2's qa signal was `qa/check-results-fields-**v2**`, but the feature branch is
the bare leaf `feature/check-results-fields`; the contract's `feature/<leaf>`
derivation then resolved to a nonexistent `feature/check-results-fields-v2` and
the Integrator's checkout failed until hand-resolved. **The `-v{N}` suffix
belongs ONLY on the `triage/` signal; `qa/` and `feature/` use the bare leaf
`check-results-fields`** — re-tag `qa/check-results-fields` at the new SHA (the
`(SHA, ref)` dedup treats a re-tag as the retry event). Keep `review/<leaf>`
unambiguous.

### v3 acceptance (supersedes v2's; the final-gate bar)

- The duplicate-field test fails when `_parse_cfg`'s guard is removed
  (reviewer-verified form above); all prior guards + the confirming
  `deadtime_step=200` experiment still hold.
- Both comment errors corrected to the measurement; `b: rtol=1e-7`; the
  ratio named as `1678×`; `_REFERENCE_CFGS` glob-derived; the physics ratio
  recorded.
- `pixi run test-reduction` green; diff is the test file only (the `46_300`
  reference already regenerated in v2); no `pixi.lock` change.
- **Final-gate bar (Analyst instruction to the Integrator):** the substance
  is confirmed sound. If v3 implements the above and the gate finds only
  net-new cosmetic *preferences* remaining, **PASS** — do not reject a
  converged slug into escalation over a comment. Reserve rejection for a
  genuinely new correctness finding.

## Revision history — v4 (human cap extension to N=4 — 2026-09-08; scope from todo @ `7565aa1`)

The human extended the retry cap to **N=4 for this slug only** after v3
(gate green, substance confirmed sound by both declared reviewers) was
rejected on **B2 alone — a comment stating a false consequence**. This v4
is **strictly limited to the four items below; nothing outside this list.**

1. **B2 — replace the CEILING comment** (`tests/test_scaling_factors_workflow.py:113-117`)
   with the Integrator's two-bar text: **neither bar alone** makes
   `test_reference_files_are_pairwise_distinguishable` vacuous; crossing
   **BOTH** does. `b`'s rtol must stay below **6.743e-04**; `_FITTED` must
   stay below **5.648e-05** (which also covers `error_a` 3.047e-05 and
   `error_b` 2.268e-05). **The Developer re-runs the falsification (`b`
   alone at 1e-2 still distinguishable via `a`) before committing and
   records the observed output in the commit body.** (Exact replacement
   text is in the v3 todo @ `7565aa1` and the escalate doc.)
2. **Should-fix — empty-glob hard-fail:** `assert len(_REFERENCE_CFGS) >= 4`
   with a message, so an empty glob hard-fails instead of yielding
   "1 skipped".
3. **Should-fix — cover the numeric-ref/non-numeric-value branch**
   (`:189-194`): add `pytest.param("a", "n/a",
   id="a-non-numeric-under-a-numeric-reference")`.
4. **Should-fix — name the 5.21e-10 path-dependence floor concretely** in
   the comment (which minimizer tolerance, from what to what), OR commit
   the probe under `plan/scripts/` (repo "capture documented methods" rule).

**Mutate-once (charter §9 amendment 16 / `todo-mutate-once-gate.md`):** for
items 2 and 3 the commit body records the mutation applied and the observed
red (empty-glob → the guard skips-not-fails without the assert; delete the
`:189-194` branch's `raise` → the new param stays green without it).

### v4 final-gate instruction to the Integrator (human directive, 2026-09-08)

**PASS when B2's text matches the measurement and items 2–4 are present.**
A v4 containing **only** these changes is **not to be rejected on any
further comment preference**; anything genuinely new goes in the **draft PR
body as advisory**, not the review loop. The substance is settled; this is
a documentation-correction cycle.

## Related, tracked separately (NOT this slug)

- `tasking:plan/todo-slit-match-margin-thin.md` — the (correct) `S1W` repair
  moves the `template_fbck.xml` slit match to 69%/71% of `template.py`'s
  `TOLERANCE=0.07`; `sf_197912_Si_auto.cfg` is referenced by **five**
  templates, not one. Not a regression (verified: no row assignment changes
  over all 63 NeXus runs), but its own follow-up — do not fold into v2.
- Note for the record: PR #21 in this fork is `633950c` (the output_dir
  isolation this slug depends on), not the upstream numbering a reviewer
  cited — no action.
