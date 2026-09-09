# Integrator: `check-results-fields` v3 — one blocking finding, comment-only. RETRY BUDGET EXHAUSTED (3 of N=3).

**Gate is GREEN** at the cleared tip `be65feb`: 113 launcher + 135 reduction,
`EXIT=0`. Blocking finding from `test-reviewer` (blocking domain); the advisory
`numerical-diagnostics-reviewer` found the **same defect independently**. I
falsified it myself before either review returned.

**Read the escalation note at the bottom before dispatching a v4** — this is
attempt 3 of N=3 and the remaining work is ~6 lines of comment. Whether that
warrants a v4, an accepted-with-note merge, or a cap extension is the Analyst's
call. **I am not asking for rework of the slug's substance.**

## CONFIRMED SOUND — do not re-litigate any of this

Verified by me and by both reviewers, independently:

- **B1 (the v2 blocker) is genuinely fixed.** The injection now carries the
  reference value, so only the duplicate guard can raise:
  `injection=v3 guard=present -> 1 passed` / `guard=removed -> 1 failed`;
  `injection=v2 guard=removed -> 1 passed` (the tautology).
- **Both v2 comment errors are corrected** — five metadata fields, and the
  ~1e-11 columns correctly attributed to cross-build drift with the `tof_300`
  zeros explained as today's regeneration.
- **Every guard is falsifiable.** Full removal matrix: duplicate guard -> 1
  failed; order check -> 1 failed; field-set+order -> 2 failed; row-count -> 1
  failed; value comparison neutered -> 13 failed; helper compares nothing -> 17
  failed; wrong `_EXPECTED_COMPARISONS` -> 1 failed.
- **The 2336x figure and its stated mechanism are correct to 4 s.f.**
  (`_42_200` row 0 `error_a`, |delta| 1.9978e-13, bar 4.6675e-10). Moving `b` to
  1e-7 relaxed its tightest comparison to ~16780x and promoted `error_a` to
  binding — exactly as the commit says. Re-deriving rather than quoting the
  review's predicted 1678x was right.
- **`b: (1e-7, 1e-12)` is correctly sized**, the glob yields exactly the four
  references and excludes `sf_201043_Si.cfg`, and **no new tautology was
  introduced in the tests themselves**.

## BLOCKING — B2: the `b` ceiling comment states a false consequence

`tests/test_scaling_factors_workflow.py:113-117` (new in v3):

```
# CEILING: b must not be widened past 6.7e-04. That is the physical
# 200->300 binning difference, so a bar at or above it makes
# test_reference_files_are_pairwise_distinguishable vacuous for the
# _46_200/_46_300 pair and reopens exactly the hole v2 closed.
```

The experiment it describes does not reproduce. Observed on the
`_46_200--vs--_46_300` param:

```
b: (6.7e-04, 1e-12)   at the stated ceiling      -> 1 passed  (still distinguishable)
b: (1e-2,    1e-12)   14x ABOVE the ceiling      -> 1 passed  (still distinguishable)
_FITTED = (1e-4, 0.0) alone, b left at 1e-7      -> 1 passed  (still distinguishable)
b: (1e-3) AND _FITTED = (1e-4)                   -> DID NOT RAISE  (NOW vacuous)
```

My own independent falsification, widening `b` twelve orders past the ceiling:

```
$ pixi run python -c "...exec the module's _TOL/check_results...; _TOL['b']=(1e9,1e-12); \
    for a,b in itertools.combinations(sorted(glob 'sf_197912_Si*'),2): check_results(a,b)"
  -> all six pairs still fail; _46_200 vs _46_300 fails on row 0 `a`
```

At the stated ceiling the pair is carried by `a`:

```
row 0 a: 1.1054992345498493 vs reference 1.1054992576290656
(|delta| 2.308e-08 > 1.105e-08 = 0e+00 + 1e-08*|ref|)
```

Max relative deltas for that pair — a bar must **exceed** these to blind each field:

```
a  5.6479e-05    error_a  3.0466e-05
b  6.7430e-04    error_b  2.2676e-05
```

**The number 6.7e-04 is right; the consequence is wrong.** `b`'s ceiling is
*necessary but not sufficient*: vacuity requires crossing **both**
`b_rtol > 6.743e-04` **and** `_FITTED > 5.648e-05`. The comment asserts
sufficiency.

**Why this is blocking and not deferred.** (1) It is the same defect class that
rejected v1 and v2 — a checkable claim in a comment that does not survive
checking — and it is **newly introduced in v3**. (2) It is *prescriptive*: it
tells a maintainer the consequence of an action, and that consequence is false,
so the guardrail's justification collapses the moment anyone tests it. (3) It
leaves the **larger** hazard undocumented — widening the shared `_FITTED` bar
past 5.648e-05 blinds `a`, `error_a` and `error_b` in a single edit, and the
comment says nothing about it. A maintainer following this comment watches the
wrong bar.

**Fix — comment only, ~6 lines. No code, no test change:**

```python
# CEILING: two bars gate the _46_200/_46_300 pair, and neither alone makes
# test_reference_files_are_pairwise_distinguishable vacuous — the other still
# catches it. Crossing BOTH reopens the hole v2 closed.
#   b's rtol must stay below 6.743e-04  (the physical 200->300 binning
#                                        difference on the slope)
#   _FITTED must stay below 5.648e-05   (the same difference on `a`; _FITTED
#                                        also covers error_a 3.047e-05 and
#                                        error_b 2.268e-05)
# Verified: b alone at 1e-2 still leaves the pair distinguishable via `a`.
```

## Should-fix (both cheap, both in the same edit if a v4 happens)

- **An empty glob makes the pairwise guard vanish silently**
  (`:212-214`). Pointing the pattern at a non-matching prefix yields
  `1 skipped, 19 deselected` — pytest's empty-parameter-set behaviour. The
  hand-maintained tuple it replaced would have hard-failed. Add:
  `assert len(_REFERENCE_CFGS) >= 4, f"reference glob found {_REFERENCE_CFGS}; expected at least the four committed references"`
- **The numeric-reference/non-numeric-value branch has zero coverage**
  (`:189-194`). Replacing its `raise AssertionError(...)` with `continue` leaves
  all 20 fast tests passing. Pre-existing from v2. Note the existing
  `IncidentMedium-non-numeric` param does **not** cover it (that exercises the
  string-reference branch at `:185-188`). One entry closes it:
  `pytest.param("a", "n/a", id="a-non-numeric-under-a-numeric-reference")`
- **The `5.21e-10` LM path-dependence floor is the one number a maintainer
  cannot reproduce from the repo.** The whole sizing argument for `b: 1e-7`
  rests on it, and the comment does not say which minimizer tolerance was
  perturbed, from what to what. Per the repo's "capture documented methods"
  rule, either name the perturbation concretely or commit the probe under
  `plan/scripts/`.
- Cosmetic, no change required: the circularity table's `a` column
  (`:66-69`) is the *no-deadtime* `auto.cfg` value, not `_46_200` — internally
  consistent, but a two-word column header would spare the next reader a
  misread. And `:44`'s "the other three references date to ce1a3ae" is strictly
  true of two; `auto.cfg` was last touched by `4caad91`, which changed only
  `S1W`/`S2iW` — all four fitted values still date to `ce1a3ae`, so the claim
  holds for the columns it describes.

## ESCALATION — retry budget exhausted, Analyst decision required

This is **attempt 3 of N=3** (charter §1 cadence knob). Contract §4 routes a
blocking review finding to this loop with no Integrator discretion, and the
"does NOT consume the retry budget" escape is defined only for *infrastructure*
failures — this is not one. So I have rejected per the contract rather than
exercised judgment about proportionality.

But the proportionality is stark and the Analyst should see it plainly:

- the gate is green and has been green for all three attempts;
- the slug's substance — the comparison rewrite, the regenerated reference, the
  tolerance derivation, every guard — is confirmed sound by two independent
  reviewers and by my own measurements;
- the outstanding defect is **~6 lines of comment text**, and both reviewers
  said so unprompted. The blocking reviewer wrote: *"If the process permits a
  comment-only amendment without consuming a retry, that is the proportionate
  remedy … I am not asking for rework."*

**Three options, for the Analyst/human:**

1. **Authorize a v4** limited to the comment fix plus the two cheap should-fixes.
   Exceeds N=3, so it needs an explicit cap extension.
2. **Accept and merge with the finding recorded**, treating a comment-only
   defect as below the blocking bar. This is a charter §5 judgment about what
   "blocking" means for a *documentation* claim, which is exactly the kind of
   call the Analyst declares at plan time and I should not make mid-cycle.
3. **Amend in place** — if the campaign permits anyone other than the Developer
   to land a comment-only correction, this is a five-minute edit with the exact
   replacement text above. I cannot do it myself (contract line 5: the
   Integrator never writes feature code, and test-file comments are feature
   code).

I recommend **1 or 3**, because the comment is prescriptive and wrong in the
direction that misdirects maintenance. But the cap is not mine to extend, and
the pattern worth noting is that all three rejections have now turned on
**claims in prose**, not on code — which may itself be a signal about where this
slug's review effort should have been aimed from the start.
