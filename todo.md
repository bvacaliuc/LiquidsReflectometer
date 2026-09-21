# Integrator: `roi-estimate` v1 — REJECTED. **The module is good; the pins are missing. The implementation barely needs touching.**

**Gate GREEN** at `0a2727a`: 145 launcher + 257 reduction, both `EXIT=0`, zero failures, DONE marker;
`pixi.lock` byte-identical; ruff clean; `exp` is an ancestor.

**Read this before the findings.** test-reviewer's summary is the accurate one: *"the guards are right,
the pins are missing."* Eleven blocking items follow and **almost none is a wrong algorithm** — they
are guards that cannot fire, a fixture that hides the code, and a workflow nobody tested. The module
itself **ran clean end-to-end on all 63 real REF_L files** (63 accepted, 0 refused, 0 errors, brackets
at rows 139–145 where the specular peak sits), in an environment where **Qt and Mantid were not
installed at all**. That is stronger validation than most slugs in this campaign have had.

**Three things you did that I want on the record, because they are the campaign's own doctrine
applied correctly and without being asked:**

1. **The bandwidth audit.** You measured four values, declined to add a fifth, and routed it to the
   numerical domain. Completing it *resolved* the question: `b302a57` (2026-04-21) changed
   `scaled_width` 3.5→3.4 **and** added the `−0.15` shift in one edit, so **the docstring's 3.5 is the
   pre-image of that commit — stale, not a competing claim. The signature is right.** Only two callers
   exist tree-wide and neither passes `scaled_width`, so the mismatch has misled readers and never
   changed a number.
2. **The delegation test.** Your reasoning — *"a literal would itself be another copy and would keep
   passing if the library were corrected"* — was verified with the four-cell experiment it was built
   for. The decisive cell: pin 3.4 explicitly **and** correct the library to 3.5 → **RED** on your
   named test. A literal expected value stays green there. This is the divergent-copy lesson applied
   to a *test*, and it is the first time anyone here has done it.
3. **Amendment 21 where it bites.** The chopper-log refusal is right, the no-caching test is right,
   and refusing empty and featureless *separately* is right.

---

## GROUP A — BLOCKING. The contrast score cannot refuse its own worst inputs, and it is reachable on real data

**A1. `baseline == 0` makes the guard a no-op.** `roi_estimate.py:237`
`contrast = peak / baseline if baseline > 0 else float("inf")`. **`inf < min_contrast` is `False` for
every threshold** — I checked 1.0, 1.5, 2.0, 1e9 — so a zero baseline passes unconditionally. You
fixed the *featureless* door (median of the whole profile); a **sparse** profile has median 0, so the
infinity relocated rather than going away.

**Reachable on 5 of 63 real REF_L files** — `198411, 198412, 201283, 201284, 201285`, all with
70–77 % of detector rows empty. Those are low-flux runs: **the class most likely to be genuinely
featureless, which is exactly what the guard exists for.** A profile of zeros with a single 3-count
row returns `(199, 201, inf)` — a confident ROI with infinite contrast around a 3-count spike.

All three domains found this independently. **Fix:** refuse on `baseline == 0` (or floor it from a low
percentile of non-zero rows), plus a sparse-profile test asserting refusal.

**A2. `proton_charge == 0` defeats the no-counts guard and returns `(0, 0)`.** `roi_estimate.py:211`.
Traced: `y_tof /= pcharge` makes empty rows `NaN` and occupied rows `inf`; `np.any(counts > 0)` is
`True` (the infs) so the guard passes; `argmax` returns the first `NaN` index (0); `peak = nan`; both
walks stop; `baseline = nan`, `nan > 0` is `False`, so `contrast = inf` and that guard passes too.
**Measured: `estimate_peak_range` returns `(0, 0)`** — verbatim the failure `:199-202` says it
prevents. Reachability corroborated: `binary_processing.get_deadtime_correction:77` already guards
zero charge explicitly, so the codebase treats it as a real state.

## GROUP B — BLOCKING. The fixture hides the algorithm it is meant to test

**B1. The fixture's peak is ~4× wider than any real peak, and that one parameter un-pins half the
core algorithm.** `test_roi_estimate.py:24` `peak_width=6.0`. **Deleting the entire low-side half-max
walk (`roi_estimate.py:224-226`) leaves all 17 tests green** — because at that width the smoothed
argmax lands at 149, so `low = centre = 149` still satisfies `assert low < 150 < high`. That is a
one-pixel coincidence of the RNG seed, not a property of the code. Real REF_L brackets are **median 3
pixels** (min 2, max 40, n=63); the fixture's is 13. **At `peak_width=1.0` the same mutation is
caught.** The high-side walk is caught at every width — that asymmetry is itself the tell.

**B2. The fixture is already in A1's defective regime, so the contrast assertion is satisfied by
infinity.** It is a pure Gaussian with **no background**: zero-fraction 0.829, `median(smoothed) = 0`,
observed contrast `inf`. So `assert contrast > 1.0` passes on `inf`, and no test asserts a *finite*
contrast. **I confirmed the branch is load-bearing by mutating `float("inf")` → `0.0` — i.e. by
FIXING the defect — and two tests turn red.** The tests currently encode the bug.

**Fixes:** `peak_width=1.0`, tighten `high - low < 40` to `<= 5`, and add a flat background to
`_write_nexus`. numerical's note is right that this is the **single cheapest measurement** available:
one line, 1.1 s, and it converts the module's central metric from untested-as-a-value to tested.

## GROUP C — BLOCKING. The advertised `tof_band` workflow is unusable, and unpinned

**C1. Unit mismatch between the module's own two functions.** `chopper_tof_window` is named for TOF
and returns **wavelengths in Å** (its docstring says so honestly: *"The wavelength band this run
actually measured"*), while `counts_vs_y`'s `tof_band` is documented in **microseconds** (`:145`). So
the natural composition — `counts_vs_y(p, tof_band=chopper_tof_window(p))` — filters events to
2.4–5.8 µs, returns an all-zero profile, and `estimate_peak_range` then raises *"no counts on the
detector"*, **blaming the run for a unit error**. Nothing in the tests or the battery composes the two
functions. Fix: rename to `chopper_lambda_range`, and add `lambda_to_tof(lam, start_time)` taking the
distance from `read_settings` — additive today, a breaking rename after three consumers call it.

**C2. The `tof_band` block is deletable with 17/17 green** (`:181-189`) — the caller's band is silently
ignored. Secondary: with `tof_band` set, `get_y_tof` is called **twice** and the first result
discarded, 2.45× the work on the one path whose `max_events` knob exists for responsiveness.

**C3. The `hi <= lo` refusal is the only thing preventing a silently-wrong histogram, and nothing pins
it** (`:173-174`). Remove it and pass a reversed band: `np.linspace(hi, lo, n)` descends, `d_tof` goes
negative, `np.digitize` clips into valid indices, and the function returns **a plausible profile
computed from inverted bins with no error.** Reachable from a caller swapping the ends — or directly
from C1.

## GROUP D — BLOCKING. Two guards assert protection they do not provide

**D1. `default_bkg_roi` returns off-detector and negative bands — exactly what its docstring says it
prevents.** Measured myself: `default_bkg_roi((400,410), n_y=304)` → **`(385, 394)`** (last pixel is
303); `((-50,-40))` → **`(-34, -25)`**. The docstring claims *"a band is only returned when it lies
wholly on the detector, because a negative row or one past the last pixel indexes silently in numpy."*

**The root cause is worth stating precisely, because it is a misapplication of this campaign's own
lesson.** You removed the `max(0, …)`/`min(n_y-1, …)` clamps as *"dead code — each sat inside a
branch whose own condition already forbids the out-of-range case."* **Each branch checks only one
end**; the clamps covered the *other* end. They were dead only under an unstated precondition — that
`peak_range` is on the detector — which the function never checks and the test sweep
(`range(0, N_Y-1, 7)`) never violates. So **mutation row 8 survived for a different reason than the
ledger records.** Your closing line is *"an unreachable guard reads as protection and provides none"* —
and the guard you removed was reachable.

**Do not restore the clamps.** Clamping would silently return a band from the wrong end of the
detector, which is the failure the docstring names. **Validate `peak_range` against `n_y` and refuse**,
consistent with the module's own discipline. Exposure is real: `RB_Ymin`/`RB_Ymax` reach the resolver
from layer (c) `reduce_settings*.json` — unvalidated file input.

**D2. `lowres=(0, 255)` hard-codes `n_x − 1` in the module whose thesis is DB-derived geometry**
(`:136`). Mutating the default to `(0, 303)` leaves all 17 tests green. This is the *identical*
situation you diagnosed for `detector_shape` (row 5: DB and literal agree, so no value assertion can
separate them) and fixed there with a provenance guard — the latent twin in the same file was missed.
Latent, not live: `num_x_pixels` has one DB entry today. But the file is time-indexed precisely to
allow a second, and `source-det-distance` already has three. Fix: `lowres=None` → `(0, n_x - 1)` from
the `detector_shape` call eight lines later, and retarget row 5's provenance guard at this default too.

## GROUP E — BLOCKING. A second copy, in the module whose thesis is that there are none

`load_event_pixels` (`:112-133`) has **zero callers, zero tests, zero ledger rows** — the only
tree-wide hit is its definition — and line 133 is
`return event_id // n_y, event_id % n_y, tof`, a **hand-rolled copy of `get_y_tof`'s packing**.
`counts_vs_y` delegates; this does not. Three mutations all survive, including **hard-coding
`n_y = 304`** — so `detector_shape`'s provenance test protects one call site and leaves the other
open — and head-instead-of-stride sampling, which defeats the documented invariant at `:126-128`.
**Give it a consumer and a test, or delete it.** Shipping it as public API in this module is the wrong
footing.

## GROUP F — BLOCKING. The layer-(e) contract and this module's refusal contract disagree

`settings_resolver.py:392-394` calls `ctx.dataset_probe(name)` with **no `try/except`** (I verified on
the T3 branch), `_guarded_step` guards only (c)/(d) discovery, and `resolve_all` calls `resolve` for
**all 55** `FIELD_SPEC` fields. The resolver's own module docstring states the opposite contract:
*"Discovery degrades, never raises … a resolver that raised when the mount was unavailable would take
the launcher with it."* This module raises on **five** paths. Wired naively, the first refusal takes
down all 55 fields.

**The deeper problem is that a correct probe cannot translate safely.** Refusals are plain
`ValueError`, indistinguishable from `counts_vs_y`'s genuine caller-error `ValueError("empty TOF
band")` and from any future bug — so `except ValueError: return None` would swallow programming errors
as "no guess available" and fall to layer (f) with a badge reading "default". That is the
silent-wrong-value class.

**The refusal policy is right and I am not asking for defaults.** Fix is one additive class:
`CannotEstimate(ValueError)` for the four genuine refusals, leaving bare `ValueError`/`KeyError` for
"you called me wrong." Introduce it now and layer (e) inherits it; introduce it later and you change
what the probe catches.

## GROUP G — BLOCKING, and it matters beyond this slug. The committed battery adopts a dirty tree as its baseline and prints `restored: OK`

`plans/scripts/roi_estimate_mutations.py:76-108`. I verified statically: `clean = sha(MOD)` is whatever
is on disk, **zero** git references (never compared to the committed blob) and **zero** signal
references (no SIGTERM/SIGINT handler). test-reviewer demonstrated both halves:

- killed with SIGTERM at a 120 s limit → the `finally` did not run → `roi_estimate.py` left mutated;
- with a leftover injected, **the committed battery printed `restored: OK` and exited with the leftover
  still in the file** — only row 7 reported `ANCHOR MISS`, and only because the leftover happened to
  collide with that row's anchor.

**This is the first committed mutation battery in the campaign, so it is now the reference
implementation — and it has the exact failure mode `todo-mutation-harness-restore-safety` was written
about**, at the 600 s harness ceiling that motivated that todo. Both fixes are one-liners: refuse to
start unless `sha(MOD)` matches the `HEAD` blob (**detection complete**), and install a restore handler
for SIGTERM/SIGINT (**auto-resolution minimal**).

**Credit where due, and it is real:** writing `orig.replace(...)` from the in-memory original rather
than editing in place gives the restore-*before* property in effect, and the per-row
`count(old) != 1` anchor check plus post-row sha compare are both right. The battery is close.

---

## WHAT IS SOUND — verified, do not re-examine

- **All 10 committed rows reproduce exactly, each caught by the test its description names** —
  test-reviewer re-ran them with node ids and tabulated the failure for each.
- **The spy is a real pin**, not a mock that would pass without the delegation: it wraps and calls the
  real function, patches the module attribute, and `counts_vs_y` looks it up at call time (a top-level
  `from … import get_y_tof` would have silently defeated it — the module correctly avoids that).
- **The contrast fix is pinned as a refusal**, not as a finite number —
  `pytest.raises(ValueError, match="contrast")`. A1 is a different door, not a failure of that fix.
- **The purity claim holds and was verified more strongly than your own test does** — transitive
  imports are `h5py`/`numpy`/`nr_tools`/(function-local)`binary_processing`, no Qt anywhere, no
  module-level mutable state.
- **The `pcharge` fix matches production exactly** (`entry/proton_charge`, shape `(1,)`, 1.1e11–4.1e12
  across the corpus) and the fixture's `1.0e12` is structurally faithful. Two honest corrections to
  your own account, neither a defect: the fix is a **no-op for every current output** (the estimator is
  exactly invariant under a positive scalar), and the old read would have **raised** a shape error on
  real data rather than silently broadcasting — silent mis-normalisation needs
  `len(series) == n_tof_bins == 200` exactly.
- **No PV divergence introduced** — the tree has two chopper PV pairs feeding `get_lam_range`, and they
  agree to 1e-9 on **all 63** corpus files. Worth one line in your MEASURED paragraph, which audits the
  width constant exhaustively but not the input PVs.
- **Rows 5 and 8's provenance approach was the right answer** where a value assertion could not
  separate DB from literal.

## ADVISORY

1. **The Qt-free guard goes vacuous on Python ≥ 3.12**, which `pyproject.toml` already permits
   (`>=3.11`). `_Blocker` defines only `find_module`, which importlib stopped consulting in 3.12 —
   verified: it raises on the pinned 3.11.15 and is a no-op on 3.12/3.13. One-word fix: `find_spec`.
2. **Row 10 pins a crash, not the normalisation** — replacing the pcharge read with
   `np.asarray([1.0])` leaves 17/17 green; the row reds only because a series length cannot broadcast.
   One assertion on the propagated magnitude converts it into a value pin, which the #197 cross-run
   comparison will need.
3. **Five public parameters unexercised** — smoothing, `scaled_width`, `max_events` in `counts_vs_y`,
   `gap`. Smoothing has measured consequence: on **19 of 63** real files `smooth=0` gives a different
   bracket than `smooth=3`, so it is load-bearing on real data and the fixture is too clean to need it.
4. **The estimator refuses "no peak" but accepts "two peaks" and "a slope"** — two equal peaks →
   the second silently discarded with no diagnostic; a monotonic ramp → accepted, the upper half of the
   detector reported as a peak; a half-empty flat field → the whole detector. Amendment 21 is applied to
   absence but not to multiplicity or monotonicity.
5. **`max_events` silently rescales the returned counts** — the events are strided but the full-run
   `pcharge` is still divided out, so the profile is low by `1/step`. Harmless for peak-finding; wrong
   for the #197 absolute comparison. Scale `pcharge`, or say in the docstring that the result is
   shape-only when `max_events` is set.
6. **`counts.size == 0` at `:211` is dead code** by your own `:259-264` reasoning — the second clause
   already raises. **`read_nexus_metadata`'s "matching `get_log_values` exactly"** is true for the motor
   and sequence logs and **false for the chopper pair**; harmless today (the two PV families agree on
   all 63 files) but the sentence should name which family is authoritative. **`:13-14` overstates the
   DB**: it supports the *distance* claim (three entries) but `number-of-x-pixels`/`y` each have exactly
   one. **The empty-event early return and the speed-0 refusal are untested.**
7. **The ledger records only the pytest summary**, so it cannot show that a row reds for the reason it
   names; recording `-rf` node ids would make that self-evident instead of requiring a reviewer to redo
   it. **Frame completeness:** 10 rows against ~31 clause-level mutations, with the missing rows
   enumerated in test-reviewer's A8.
8. **Handed to numerical, not adjudicated:** on the two highest-angle corpus runs (`198389`, `198416`,
   ths = −4.639) the half-max walk goes wide — brackets of 39 and 40 pixels against a median of 3 — and
   the contrast guard refused neither. The slug's own sanity bound is `< 40`; these measure 39 and 40.

## ROUTED ELSEWHERE — not conditions on this slug

- **A wrong number reaching a scientific result on `exp` today.** Two live reduction paths clip to
  bands differing by **22.9 % in Q_max**: `event_reduction.py:54-55` inlines 2.6 without the shift and
  feeds `self.wl_range`; `nr_tools.get_lam_range` (3.4 + shift) feeds `LambdaMinUse/MaxUse` whenever the
  user has not pinned `LambdaMin/Max`. Same run, λ_min **2.95 vs 2.40**. Pre-existing, outside this
  additive diff, and **you were right to leave it and right to escalate it.** Needs its own slug;
  3.4-with-shift is the value that should win.
- **There is no authoritative source for the chopper bandwidth anywhere in this repo.** `settings.json`
  — the time-indexed DB this module correctly insists on — has no chopper or bandwidth key at all.
  Recommend a time-indexed `chopper-bandwidth-60hz` entry read by `get_lam_range`: the chopper
  configuration is exactly as time-dependent as `source-det-distance`, which already has three entries.
  **That is this module's own argument applied to the constant it declined to fix.**
- **`nr_tools.py:550`'s docstring should say 3.4** — a one-word fix with a known direction.
- **The `−0.15` shift does not scale with chopper speed** while the half-width does (4.4 % of the band
  at 60 Hz, 8.8 % at 120 Hz), and **every corpus run is at 60.0 Hz**, so the scaling is entirely
  unexercised. One question to the instrument scientist closes it.
- **`roi_selector.py` is worse than this module's docstring says** — the count is **five**, not four,
  and the divergence is fourfold: two inline copies at 3.5 **without** the shift and reading the *other*
  PV pair, while `:1717` separately *does* call `get_lam_range`. Plus `dist_m = 15.75` (wrong by 3.0 %
  for runs in the 2024-08-26 → 2025-01-01 window, where the DB says 15.282) and a `20.0` m fallback off
  by 27 %. The strongest possible endorsement of this module's DB-reading design, and the concrete
  reason the wiring step must **retire** the old path rather than sit beside it.
- **Peak-range estimation is the fourth implementation in-tree.** `LRDirectBeamSort._find_peak`
  hard-codes `np.reshape(y, (256, 304, ...))` and is named nowhere in the plan. "One implementation for
  three consumers" is only credible alongside a stated list of which ones stay.
- **#197's `json_settings_builder.py` exists on no branch of this repo** (all 30 remote refs checked),
  so the third named consumer's required signature could not be checked against this API.
