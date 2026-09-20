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

## 4. An unreachable guard reads as protection and provides none

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
