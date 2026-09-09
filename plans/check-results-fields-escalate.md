# ESCALATION — `check-results-fields`: retry cap reached, CONVERGED (not failed)

> **SUPERSEDED 2026-09-08 — the human extended the cap to N=4 for this slug**
> (the option-1 recommendation below). A bounded v4 (comment fix + 3
> should-fixes, scope in the plan's `### v4` entry) runs instead of a
> terminal escalation; the escalate tag was never pushed (write-403 wave) and
> the local tag is deleted. This file is kept as the record of the
> cap-reached moment and the reasoning that produced the extension.

**Terminal state:** attempt 3 of N=3 (charter §1) rejected → this is the
sanctioned cap-reached escalation. **But this is a converged slug at the cap,
not a failing one** — the gate has been green all three attempts, the
substance is confirmed sound by two independent reviewers, and the sole
remaining defect is **~6 lines of comment text**. The retry budget exists to
bound wasted Developer+Integrator cycles on a *non-converging* plan; it has
stopped tracking that target here, which is why the Integrator explicitly
routed the disposition to the human (todo @ `7565aa1`). The decision is a cap
call, which is the human's, not the Analyst's or Integrator's.

## What the slug does (why it matters)

Restores the **only** regression coverage for computed scaling factors, which
multiply every R(Q) the facility produces. Before it, the `check_results`
helper compared 1 of 10 fields (`error_b`, twice) — setting scaling factor `a`
to 999999 went undetected. It also explains the seven-occurrence `/tmp`-race
mystery (the one-field helper let deadtime collisions pass silently).

## Attempt synopsis

| Attempt | Did | Blocked on |
|---|---|---|
| **v1** (`4caad91`) | per-field dict comparison; hand-typo `S1W`/`S2iW` reference repair (float-repr-proven) | tolerances calibrated on a **duplicated reference** — `sf_197912_Si_dt_par_46_300.cfg` was byte-identical (md5 `14d3e256`) to the `_200` file, so `tof_300` compared a 300-param run to a 200-param reference |
| **v2** (`18470b9`) | regenerated the 300 reference from a real `deadtime_tof_step=300` run (provenance header, deltas recorded); re-derived tolerances from the uncontaminated cases; 9 guards | (a) `test_check_results_rejects_a_duplicate_field` was a **tautology** (injected duplicate was *also* value-wrong, so `raises` passed even with the guard deleted); (b) two comment factual errors (metadata count; "~1e-11 platform noise" was actually cross-build drift) |
| **v3** (`be65feb`) | fixed the tautology (inject the reference value); corrected both comments; `b: rtol 1e-7`; glob-derived `_REFERENCE_CFGS`; physics ratio check | **B2 only** — one new comment stating a false *consequence* (below) |

Every v1/v2 finding is confirmed fixed and not re-litigated. The pattern the
Integrator named is worth recording: **all three rejections turned on
checkable claims in prose, never on code.** The code, tests, reference data,
and tolerances are sound.

## The single remaining defect (B2) — comment-only

`tests/test_scaling_factors_workflow.py:113-117` claims widening `b` past
`6.7e-04` alone makes `test_reference_files_are_pairwise_distinguishable`
vacuous. Falsified (Integrator, independently): at the ceiling and 14× above
it the pair is still caught — by `a`. Vacuity needs crossing **both**
`b_rtol > 6.743e-04` **and** `_FITTED > 5.648e-05`. The number is right; the
sufficiency claim is wrong, and it leaves the *larger* hazard (the shared
`_FITTED` bar, which also blinds `a`/`error_a`/`error_b`) undocumented — so it
misdirects a maintainer to the wrong bar. It is the slug's own signature class
(a claim that does not survive checking), newly introduced in v3.

**Exact fix (the Integrator supplied it; comment-only, no code/test change):**

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

**Two cheap should-fixes to ride with it** (same edit): an
`assert len(_REFERENCE_CFGS) >= 4` so an empty glob hard-fails instead of
silently skipping (`:212`); and one `pytest.param("a", "n/a", ...)` to cover
the numeric-reference/non-numeric-value branch (`:189-194`, currently zero
coverage). Optionally commit the `5.21e-10` LM path-dependence probe under
`plan/scripts/` (the one number a maintainer can't reproduce from the repo).

## What I would have tried in a v4 (fully specified — no discovery left)

Exactly the comment replacement above + the two should-fixes. There is no
open question, no measurement to take, no code to change. A v4 would be a
documentation-correction commit, re-gate (green is already established), PR.

## Recommendation to the human

**Do (1) or (3); not (2).**

1. **Authorize a bounded comment-only v4** (explicit N-extension to 4 for this
   slug). Proportionate: the fix is fully specified and the gate is green. This
   keeps the correction on the normal Developer→Integrator path.
3. **Amend directly and merge** — the fix is 6 lines of comment + ~3 lines of
   test; if you'd rather apply it yourself than spin a cycle, the text above is
   drop-in, then re-run `pixi run test-reduction` and open/merge the draft PR.
   (The Integrator can't do this — contract bars it from feature code, and test
   comments count; the Analyst writes plans, not code — so a direct amend is
   the human's.)

**Against (2) accept-and-merge-with-the-wrong-comment:** the slug's entire
standard is "a prescriptive claim that doesn't survive checking is the
defect." Shipping that exact defect, in a comment about the tolerance
guardrail, on a fix whose green comes 6 lines away, is not the robust choice —
and the comment misdirects maintenance in the direction of the *undocumented*
larger hazard.

## Durable lesson (route post-campaign)

All three rejections turned on prose, not code — a signal for future
reduction-science test slugs: put review effort on the *rationale comments*
(they instruct future maintainers and are load-bearing), and prefer
measurement-backed comments or none. Candidate for
`setup/patterns/scientific-regression-testing.md`.
