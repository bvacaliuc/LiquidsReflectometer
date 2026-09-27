# Learnings — `roi-estimate` (T1 slug 1)

## 1. Build the fixture from the production read path, not from the spec

**Rule.** When you write a synthetic input file for a module that parses a real
one, derive every field from the code that reads the real file — not from the
plan's description of it.

**Why.** `counts_vs_y` fed `entry/DASlogs/proton_charge/value` to
`binary_processing.get_y_tof`, which divides the y-vs-tof histogram by it.
Production passes `entry/proton_charge` — the **run total**, a length-1 array —
while the DASlogs entry beside it is the **time series**. With the series,
`y_tof /= pcharge` is a broadcast against a (304, 200) histogram rather than a
normalisation, and it raised. The plan said "proton charge"; only
`load_and_extract` said *which* proton charge. Building the fixture from the
production reader is what surfaced it on the first run instead of on real data.

**How to apply.** For each dataset the fixture writes, find the line in
production that reads it and copy the path from there. Where two paths differ
only by their parent group, assume they are different quantities until you have
checked — `entry/proton_charge` and `entry/DASlogs/proton_charge/value` are the
total and the series, and the names do not say so.

## 2. A quality score must be worst for the input it exists to reject

**Rule.** After writing a score that separates "signal" from "nothing", evaluate
it on the degenerate input by hand. If the degenerate case scores *well*, the
score is inverted, not merely imprecise.

**Why.** `estimate_peak_range`'s contrast was peak height over the median of
everything **outside** the half-max bracket. On a featureless detector the
half-max walk runs almost edge to edge — every bin exceeds half of a flat
maximum — so "outside" is empty, the baseline is 0, and the code returned
`inf`. Flat noise, the single input the score exists to reject, scored
*infinitely confident*. Baseline is now the median of the whole profile, which
is ~1.0 for flat data and large for a real peak.

**How to apply.** Enumerate the degenerate inputs first — all-zero, flat, single
spike, saturated — and assert the score's ORDER across them, not just a
threshold on the good case. A threshold test on good data passes for an
inverted score.

## 3. When the database and the literal agree today, assert provenance

**Rule.** A guard against hard-coding cannot be an equality check when the
configured value currently equals the literal. Assert that the answer *follows
the source*: move the source and require the answer to move.

**Why.** `detector_shape` reads the time-indexed instrument DB so a geometry
change is picked up. `settings.json` holds exactly one entry for each pixel
count, so the DB says 256/304 and the literal is 256/304, and the mutation
`return 256, 304` passed the test. Measured — it was mutation row 5, and it
survived. The failure being prevented is a *future* change the literal would not
follow, so the test has to be about the path, not the present value.

**How to apply.** Monkeypatch the source to return something different and
assert the function reports that. This is the same move as pinning a call to a
library function by spying on it rather than by re-asserting its arithmetic:
both check "did the value come from where it must", which is the actual
requirement whenever the point of the code is single-sourcing.

## 4. An unreachable guard reads as protection and provides none — **CORRECTED, my diagnosis was wrong**

> **v2 correction (2026-09-27).** The conclusion below is right in general and
> **wrong about this instance**, and the instance is what made it persuasive.
> The clamps I deleted were **not** dead. `default_bkg_roi`'s two branches check
> **one end each**; each clamp covered the end its own branch did not. They were
> unreachable only under an unstated precondition — that `peak_range` is on the
> detector — which the function never validated and my sweep
> (`range(0, N_Y-1, 7)`) never violated. Measured after removal:
> `default_bkg_roi((400,410), n_y=304)` → `(385, 394)`, and `((-50,-40))` →
> `(-34, -25)`, both off the detector, which is verbatim the failure the
> docstring claims to prevent. So **mutation row 8 survived for a different
> reason than this file records.**
>
> The fix is not to restore the clamps — clamping `(400, 410)` yields a band
> from the wrong *end*, silently. It is to validate `peak_range` against `n_y`
> and refuse. Exposure is real: `RB_Ymin`/`RB_Ymax` reach the resolver from
> layer (c) as unvalidated file input.
>
> **The transferable lesson is the one I got wrong, not the one I wrote:** before
> concluding a guard is unreachable, state the precondition that makes it so and
> check that something enforces it. "No branch can reach this" and "no branch
> can reach this *given an assumption nobody checks*" look identical in the
> code and differ completely in consequence. Keep §4 below for the general
> point; it stands. Do not cite this instance as its evidence.

**Rule.** A clamp inside a branch whose condition already excludes the
out-of-range case is dead code. Delete it; do not keep it as reassurance.

**Why.** `default_bkg_roi` returned `max(0, high_edge - width + 1)` from inside
`if high_edge - width + 1 >= 0:`. The clamp could never change a value, and the
mutation deleting it passed every test — correctly, since the two programs are
identical. Keeping it would have left a reviewer believing the bounds were
defended twice when they are defended once. The same shape as "two clauses
guarded a field that does not exist" (`settings-management-learning.md` §10).

**How to apply.** When a mutation to a guard survives, first ask whether the
guard is *reachable* before strengthening the test. If it is not, the finding is
dead code, and the test should be retargeted at whatever does the real work —
here the fit check — plus a sweep that exercises every branch rather than the
one input the author happened to pick.


## 5. Two guards on one path pin each other, and neither is pinned

**Rule.** When a hazard is defended at two points, a test that composes them
pins **neither** — remove either guard and the survivor still raises, so both
mutations pass.

**Why.** A zero proton charge is refused twice: at source in `counts_vs_y`, and
downstream in `estimate_peak_range` when the profile arrives non-finite. My
first test drove the whole path, and **battery rows 12 and 13 both survived**.
Splitting it — one test for the source refusal, one handing the estimator a
non-finite profile directly — reds both.

Fixing that exposed a second-order defect: the all-NaN profile hit the
**no-counts** guard first and was reported as *"no counts on the detector"*,
naming the wrong cause and making the non-finite guard untestable in isolation.
Ordering the more specific diagnosis first fixed both the message and the pin.

**How to apply.** This is learning 25's *mutate each anchor independently*
applied to defence-in-depth rather than to a fixture, and
`settings-editor-learning.md` §14 ("two normalisation points, one covering for
the other") is the same shape a third time. When you add a guard to a path that
already has one, the new test must reach the new guard **directly**, not through
the old one.

## 6. Verify with the gate command, not with an approximation of it

**Rule.** "Green" means the command the gate runs returned zero. Running the
same tests a different way is not the same claim, and the difference is exactly
where CWD-, env- and path-dependent defects live.

**Why.** v2 shipped a battery-loader test using a CWD-relative
`"plans/scripts/roi_estimate_mutations.py"`. I verified with
`pytest tests/unit/...` from the repo root, where that resolves. The gate is
`pixi run test-reduction`, which is `cd tests/ && python -m pytest` — so it
resolved to `<repo>/tests/plans/...`, raised `FileNotFoundError`, and the gate
went **red** on a slug I had declared green three times over.

The campaign already knew this: `scaling-factor-path-anchor-learning.md` §1 is
*"a gate command that changes directory hides every cwd-dependent defect behind
it."* I had read that file — I cited it in this slug's own synthesis — and still
walked into it, because knowing the lesson and running the command are different
acts.

**How to apply.** Before declaring a gate green, run the literal gate command
from `pyproject.toml`, once, at the end. Anchor test-time paths to
`Path(__file__)` rather than the CWD, since a test that only passes from one
directory is a defect regardless of which directory the gate happens to use. And
treat "I ran the tests" and "I ran the gate" as different sentences — the second
is the one a reviewer is owed.
