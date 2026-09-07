# Integrator: `check-results-fields` v2 — one blocking finding, plus two comment errors of the class v1 was rejected for

**Gate is GREEN** at the cleared tip `18470b9`: 113 launcher + 135 reduction,
`EXIT=0`. This is again a **blocking review finding**, not a test failure.
`test-reviewer` (blocking domain) found B1; `numerical-diagnostics-reviewer`
(advisory) found **no blocker** and independently reproduced the whole
derivation.

## CONFIRMED — v3 must not re-litigate any of this

Verified independently, by me and by both reviewers:

- **The delta table is real.** All 20 figures reproduce to the digit from fresh
  runs against the now-distinct references; metadata is exactly `0.0` in all
  five cases. This is the measurement v1 did not have.
- **The regeneration is genuine, and physically coherent.** The `46_300` vs
  `46_200` data rows differ; the difference is confined to the fitted
  parameters (`a` 5.648e-05, `b` 6.748e-04, `error_a` 3.046e-05,
  `error_b` 2.268e-05) with **every metadata field bit-identical at 0.0** —
  which is what a deadtime-binning change must do. Those four numbers are
  *exactly* v1's "worst observed delta" table, closing the v1 diagnosis.
- **The confirming experiment reproduces.** Hard-coding `deadtime_step = 200.0`
  at `LRScalingFactors.py:516` makes `-k tof_300` FAIL (`1 failed, 24 deselected`).
  It PASSED under v1.
- **8 of 9 new guards are falsifiable**, each with observed failure output, and
  the count assertion (`_EXPECTED_COMPARISONS = 20`) is correct — 20, not the
  18 I estimated in the v1 review.
- **Nothing v1 got right regressed.** All eight original mutation params still
  go red against the reverted helper; `git diff 4caad91 18470b9 --
  tests/data/sf_197912_Si_auto.cfg` is empty, so the S1W repair is untouched.
- **Rejecting the review's `b: rtol=1e-3, atol=1e-8` was correct on both
  halves.** The rtol was calibrated on the contaminated basis; and `atol=1e-8`
  on the smallest reference row (`|b| = 5.5367e-07`) is **1.8% of b**, which
  would have made the near-zero rows nearly vacuous — defeating the purpose it
  was suggested for. Keeping the hybrid *form* and discarding both magnitudes
  was the right call.
- **`atol=1e-12` is right.** On the smallest-`|b|` row it supplies 99.4% of the
  bar and sits ~3400x above the measured path-dependence floor there.

## BLOCKING — B1: `test_check_results_rejects_a_duplicate_field` cannot fail

`tests/test_scaling_factors_workflow.py:265-270`, injection at `:268`:

```python
data = _write_cfg(tmp_path / "data.cfg", [_REF_ROWS[0], _REF_ROWS[1] + " a=999999.0"])
```

The probe injects a duplicate `a` whose value is *also* wrong. Delete the
duplicate guard at `_parse_cfg:95-96` and `dict(pairs)` last-wins yields
`a=999999.0`, which fails the **value** comparison instead — so
`pytest.raises(AssertionError)` is satisfied either way. Observed with the guard
removed (helper restored to v1's one-line `dict(...)` comprehension):

```
1 passed, 24 deselected in 0.04s
RAISED (guard REMOVED) -> row 1 a: 999999.0 vs reference 6.624303827034047
                          (|delta| 1.000e+06 > 6.624e-08 = 0e+00 + 1e-08*|ref|)
```

The raise never comes from the duplicate guard.

**Why this blocks rather than defers.** The production guard is *correct and
works* — only its test is a tautology. But a plausible future cleanup back to
the one-line comprehension leaves the suite green while silently deleting the
protection, which is the exact recurrence mechanism this slug exists to close.
It is also the module's own stated doctrine (`:109-112`): a helper that cannot
fail is worse than none.

**Fix — one line. Inject the reference value so only the duplicate guard can raise:**

```python
data = _write_cfg(tmp_path / "data.cfg", [_REF_ROWS[0], _REF_ROWS[1] + " a=6.624303827034047"])
```

Verified in both directions:

```
guard present -> RAISED: data.cfg line 4: duplicate field(s) ['a']
guard removed -> NO RAISE (returned 20)   # i.e. the test now fails, correctly
```

`_EXPECTED_COMPARISONS` and the bars are unaffected.

## Also required in v3 — two factual errors in the rationale comment

v2's own commit says a false rationale in a comment "instructs everyone who
reads it next", and that is why v1 was rejected. Two remain:

1. **`:36` — "All nine instrument-metadata fields are 0.0 in every case."**
   There are **five** (`LambdaRequested`, `S1H`, `S2iH`, `S1W`, `S2iW`); nine is
   the numeric-field count (5 metadata + 4 fitted). The claim itself is true and
   measured — only the count is wrong.
2. **"on this platform the fits reproduce to ~1e-11"** — they reproduce to
   **0.0 exactly**: two separate processes give bit-identical rows, and
   `OMP_NUM_THREADS=1` vs 24 gives bit-identical rows. The ~1e-11 figures are
   **cross-build drift** — three references date to `ce1a3ae` (2025-12-03) or
   earlier, while `_46_300` was regenerated today by this build, which is
   exactly why its column is all zeros. This is the same error class the slug
   punishes: an observed delta attributed to the wrong source. **Keep the
   number, fix the sentence** — cross-build drift is *better* evidence for a
   cross-platform bar than run-to-run noise would be.

## Should-fix in v3

- **`b: rtol=1e-8` is only 19x inside the fit's path-dependence floor.**
  `LRScalingFactors.py:384` fits the *linear* model `a+b*x` with the generic
  iterative Levenberg-Marquardt minimizer and a finite-differenced Jacobian.
  Arithmetic-level differences (BLAS/libm/compiler) move `b` by only ~1e-13 —
  five orders inside the bar, safe. But the *converged* answer is
  path-dependent at 5.21e-10 on `b` with identical data, so a Mantid version
  that changes LM's convergence tolerance or step rule moves it at that scale.
  Recommend **`b: rtol=1e-7`** (~200x over measured path-dependence, still ≥5
  orders inside `b`'s own uncertainty; `b/error_b` runs 0.425-8.586). Keep
  `atol=1e-12`. Leave `a` (370x) and `error_a`/`error_b` (~2600x) at 1e-8.
- **"~200x headroom" names a quantity that does not govern flakiness.** It is
  `rtol / worst-relative-delta`. The minimum of `bar / |observed delta|` over
  all 405 comparisons is **1678x**. Both are honest; say which is meant, since a
  maintainer reproducing "200x" will not find it.
- **Record the widening ceiling.** `b` may not be widened past 6.7e-04 without
  making `test_reference_files_are_pairwise_distinguishable` vacuous. The
  comment already tells the maintainer to widen from a measurement; give that
  escape hatch a documented stop.
- **`_REFERENCE_CFGS` (`:160-165`) is hand-maintained** and disconnected from
  the five `check_results` call sites. A future `tof_400` reference that nobody
  adds to the tuple reopens the duplicate hole. Derive it by glob over
  `data/sf_197912_Si*.cfg` (confirmed to yield exactly the four;
  `sf_201043_Si.cfg` is a reduction *input*, correctly excluded).
- Per-case maxima are single-sample order statistics and will shift on any
  reference regeneration — worth one clause.

## Worth ADDING — the physics check the data already contains

The circularity concern ("generated by the code under test") is answered by the
data itself, and saying so upgrades the baseline's standing at no cost. The
binning effect tracks the deadtime correction across three decades and vanishes
exactly where the correction vanishes:

```
row0 S1H=0.391  dt_effect=3.423e-04  bin_effect=2.088e-08  ratio=0.0001
row4 S1H=0.770  dt_effect=8.950e-02  bin_effect=2.719e-05  ratio=0.0003
row8 S1H=3.016  dt_effect=2.245e-01  bin_effect=5.483e-05  ratio=0.0002
```

A flat ~1e-4 fraction across rows spanning three decades is not what a wrong
parameter or wrong code path produces. So `a` moving 5.6e-05 is not suspicious —
it is ~5e-4 of a correction that is itself up to 22%, and 1e-3-2e-3 sigma, which
is precisely why the duplicate survived years unnoticed.

## Integrator note on the retry budget — for the Analyst, not the Developer

This is **attempt 3 of N=3**. The blocking defect is one line of test data and
the two comment errors are one sentence each; the measurement, the regenerated
reference, the guards and the confirming experiment are all confirmed sound.
I am following contract §5b (blocking domain + blocking finding → reject) for
consistency with the v1 gate rather than because the remaining work is large.
**Whether a test-only tautology plus two comment corrections should consume the
final retry is the Analyst's call**, and worth an explicit decision before v3 is
dispatched.

## Protocol note

The v2 qa tag was `qa/check-results-fields-v2` while the work is on
`feature/check-results-fields`, so the contract's `feature/<leaf>` derivation
(line 125) resolves to a branch that does not exist and my checkout failed until
I resolved it by hand. The `(SHA, ref-name)` dedup already treats a **re-tag of
`qa/check-results-fields` at a new SHA** as the retry signal — that is all v3
needs, and it keeps `review/<leaf>` unambiguous.
