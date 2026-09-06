# Integrator: `check-results-fields` v1 — blocking review finding (gate is GREEN)

**This is not a test failure.** `pixi run test-reduction` is green at `4caad91`:
113 launcher + 126 reduction passed, `EXIT=0`. The rejection is a **blocking
review finding** from the `test-reviewer` domain, which the plan declares
blocking ("this slug's entire purpose is restoring test assurance"). The
advisory `numerical-diagnostics-reviewer` reached the same conclusion
independently.

## What is RIGHT, and should not be re-litigated in v2

- The self-comparison diagnosis is correct and the fix is real. Verified
  empirically: splicing the pre-fix helper back in makes **10 of the 11 guards
  fail** — 9 with `Failed: DID NOT RAISE AssertionError`, plus
  `detects_a_truncated_file` with `IndexError` at the old
  `cfg_data[i].split(" ")`. The positive control correctly still passes.
- **The `S1W`/`S2iW` repair to `sf_197912_Si_auto.cfg` is correct, and is now
  provably correct *in scope*.** Beyond the run-log and sibling evidence in the
  commit body, a float-representation audit shows the stale values could not
  have been produced by the writer at all:

  ```
  repr(float("19.992000000000005")) = 19.992000000000004   # does NOT round-trip
  repr(float("19.990864375000002")) = 19.990864375         # does NOT round-trip
  "%.17g" % (19.952000000000005 + 0.04) = 19.992000000000004   # arithmetic can't make it either
  digit substitution '5'->'9':  19.952000000000005 -> 19.992000000000005   EXACT
                                19.950864375000002 -> 19.990864375000002   EXACT
  ```

  `LRScalingFactors.py:466` writes `"%s" % float` (shortest round-trippable
  repr), so it can only emit round-trippable text. Those two values were
  **hand-typed** — a single keystroke slip, present since `41a095c`
  (2023-10-10). Not a calibration offset, not code drift. An audit of every
  numeric token in all four references found these two to be the **only**
  non-writer-producible values in the corpus, which independently vindicates
  leaving `a`/`b`/`error_a`/`error_b` untouched.

## BLOCKING — B1: the tolerance table is calibrated on a duplicated reference

```
$ md5sum tests/data/sf_197912_Si_dt_par_46_300.cfg tests/data/sf_197912_Si_dt_par_46_200.cfg
14d3e256da9dee40e9b575e322754a5e  .../sf_197912_Si_dt_par_46_300.cfg
14d3e256da9dee40e9b575e322754a5e  .../sf_197912_Si_dt_par_46_200.cfg
```

`sf_197912_Si_dt_par_46_300.cfg` **is** the `deadtime_tof_step=200` answer
wearing a 300 filename. (`42_200` vs `46_200` genuinely differ, so this is not
an all-duplicates situation — it is specifically this pair.)

The commit reported an **aggregate** worst-case over 45 row-comparisons.
Disaggregated per test case:

```
            case      metadata            a           b     error_a     error_b
 test_compute_sf     0.000e+00    1.799e-14   3.359e-14   6.729e-14   5.181e-14
 ..._with_deadtime   0.000e+00    8.426e-13   4.645e-11   4.280e-12   4.260e-12
 ..._tof_300         0.000e+00    5.648e-05   6.748e-04   3.046e-05   2.268e-05   <<<
 ..._tof_200         0.000e+00    9.581e-14   2.878e-12   1.676e-12   1.418e-12
 ..._tof_200_sort    0.000e+00    9.581e-14   2.878e-12   1.676e-12   1.418e-12
```

Four of five cases reproduce to **1e-11 or better**. The entire tolerance budget
comes from `tof_300` alone — and `5.648e-05 / 6.748e-04 / 3.046e-05 / 2.268e-05`
are *exactly* the four numbers in the committed `_TOL` rationale. Confirmed
causally: generated-300-vs-generated-200 equals generated-300-vs-its-reference
to every printed digit. `DeadTimeTOFStep` is genuinely wired through
(`LRScalingFactors.py:516`), so those deltas are the **physical 200→300
deadtime-binning difference**, not fit noise.

Three consequences:

1. **The rationale at `tests/test_scaling_factors_workflow.py:31-33` is false.**
   It attributes `b`'s larger delta to "a near-zero slope where relative error is
   inherently noisier". The real cause is the wrong baseline. That comment is
   written as durable instruction to future maintainers (`:35-36`: "widen it from
   a MEASUREMENT and say so"), so it is misinformation with a long half-life.
   **Shipping the wrong causal explanation is the part that must not merge.**
2. **`a` is guarded at `1e-3` where `~1e-11` is achievable** — `a` multiplies
   every R(Q) from this path, as the commit itself says. Six orders of margin
   given away.
3. **`test_compute_sf_with_deadtime_tof_300` has zero power on its own
   parameter.** If the code ignored `DeadTimeTOFStep` and always used 200, it
   would emit the 200 answer, compare against a reference that *is* the 200
   answer, and pass. Confirming experiment: hard-code `DeadTimeTOFStep=200` at
   `LRScalingFactors.py:516` and run `-k tof_300` — expect PASS.

This is the slug's own principle turned on itself: it refused to widen a
tolerance for the `S1W` discrepancy and repaired the reference instead, then did
exactly the opposite for the fitted parameters — because the deltas were
aggregated across cases and the outlier was read as noise.

**Cheapest measurement that would have caught it: the two-line `md5sum` above.**

### Required for v2

1. Regenerate `tests/data/sf_197912_Si_dt_par_46_300.cfg` from an actual
   `deadtime_tof_step=300` run, adjudicated the way the `S1W` row was.
   **Keep the writer's provenance header** (`LRScalingFactors.py:455-458` emits
   `#    deadtime_tof_step: 300.0` etc.) — the committed references predate it,
   and its absence is *how* this duplicate stayed invisible. Record the exact
   200-vs-300 deltas in the commit body so the regeneration is auditable rather
   than laundered.
   If an independent 300 baseline cannot be adjudicated, `xfail` the test with
   the reason — do not leave a test that passes either way.
2. Re-derive the fitted-parameter tolerances from the **uncontaminated** cases.
   `1e-8` is ~200x headroom on the worst clean delta (`b = 4.645e-11`) and is
   still 5 orders tighter than today; measure on CI before committing to `1e-9`.
3. Rewrite `:19-23` (the measured table) and `:31-33` (the rationale) from the
   corrected measurement. State the honest basis for the fitted bar — a
   cross-platform fit-reproducibility allowance, still well inside the fit's own
   1-sigma (`error_a/a` is 3.4-4.2% per row) — not "an order of magnitude over
   measured noise".
4. Add a guard that the four reference cfgs are pairwise distinguishable by
   `check_results`. The new helper already separates 4 of the 6 deadtime pairs
   the old one could not; the 2 that still pass are exactly this duplicate pair.

## Should-fix in v2 (cheap, same file)

- **`_TOL` keys are unguarded.** A one-character typo (`"S1W"` -> `"S1w"`)
  silently demotes a metadata field from `1e-12` to `_DEFAULT_TOL = 1e-3` — nine
  orders — with the whole suite green (demonstrated). Assert the `_TOL` key set
  against the reference rows' field set.
- **Field *order* is unchecked but the consumer reads positionally.**
  `check_results` compares field *sets* (`:85`), while `src/lr_reduction/template.py:184-185`
  does `s2h_key = keys[3]` / `s2w_key = keys[5]`. A writer reordering would pass
  the test and make the consumer fall through to `template.py:207` — "proceeding
  unscaled", a plausible-looking unscaled R(Q). Use `list(row) == list(ref)`.
- **`b` needs a hybrid bar, not a pure relative one.** `b` spans 4.5 decades and
  row 0's slope is 0.43 sigma from zero; a benign 1-sigma shift there is a
  relative delta of 2.3, i.e. 463x over the `5e-3` bar. Recommend
  `abs(v_calc-v_ref) <= atol + rtol*abs(v_ref)` with `b: rtol=1e-3, atol=1e-8`
  (a uniform 0.2-0.8% of `error_b` on every row). This also removes a latent
  unit-mixing hole: the `v_ref == 0.0` branch (`:103`) compares an *absolute*
  delta against a bar calibrated as *relative* (currently dead — no reference
  field is exactly 0.0).
- **`_parse_cfg` silently drops duplicate keys** (`:64`) — the same class of
  silent collapse this slug exists to fix. Add an explicit duplicate check.
- **The positive control is vacuous in isolation** (`:146`). Have
  `check_results` return the number of field comparisons performed and assert it
  (`== 18`).
- **`test_compute_sf_with_deadtime_tof_200_sort` is a duplicate of its sibling** —
  byte-identical output, so `order_by_runs=False` is untested and the "45
  row-comparisons" is really 27 independent. Pre-existing; either say so in the
  docstring or use a run set where the orders differ.

## Related findings already filed (do not re-derive)

- `tasking:plan/todo-slit-match-margin-thin.md` — the repair moves the
  `template_fbck.xml` slit match from 11%/13% to **69%/71%** of
  `template.py`'s fixed `TOLERANCE = 0.07`. Not a regression (the 0.048 mm
  distance was always real; the stale value manufactured false comfort), but a
  fall-through returns `1, 0, 0, 0` — unscaled R(Q). **Widen the blast radius
  when updating**: `sf_197912_Si_auto.cfg` is referenced by five templates
  (`template.xml`, `template_fbck.xml`, `template_short_nobck.xml`,
  `template_with_const_q_true.xml`, `template_stitching_automatic_average.xml`),
  not one. No row assignment changes anywhere — verified over all 63 NeXus runs —
  so nothing breaks today. Also: the lookup matches lambda with the same 0.07
  bar, and at lambda=7.043 the repaired row is the *only* candidate, so there is
  no second row to fall back to.

## Note on an incorrect correction

One reviewer stated PR #21 is `5294b9a` "require only mantid framework". In this
fork **PR #21 is `633950c` "give each scaling-factor test its own output
directory"** (verified via `gh pr view 21`); the reviewer was reading upstream
numbering. The `output_dir` isolation this slug depends on is `633950c`.
