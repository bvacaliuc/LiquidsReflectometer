# Plan: roi-estimate (T1 slug 1) — Qt-free ROI/metadata estimation module + layer-(e) probe

**Campaign:** `exp-settings-roi` · charter §4 **T1** · slug 1 of the T1 cut (Advisor
`plan/roi-selector/advisor-position-t1-strategy.md` §2.4, Analyst-reconciled 2026-09-19).
**Retry attempt:** 1. **Base:** `agentic/exp` @ `6da473d`. **Independent of T3/Slug A** (pure
module; wired to the resolver's layer (e) in a later staged step) **and of the A1-vs-rewrite
decision (D-1)** — needed under BOTH outcomes, so it is the **no-regrets first T1 slug** while the
human is away. File-disjoint from Slug A (`settings_*.py`) → runs concurrently.

## Why this slug first (not A1)

Accepted from the Advisor's cut: `roi-estimate` → `roi-view` → `roi-tab` → `roi-vs-197-review` →
`settings-builder-on-document`. `roi-estimate` is the shared model **all** paths need — the old
tab's guesser (R4), the rewrite, the resolver's layer-(e) `dataset_probe` (whose absence is why
the resolver's payoff is thin today), AND the #197 comparison (it settles F3). **A1 (patch the old
2268-line tab) is D-1, the human's call** — dispatched only if the beamline needs a usable tab this
week; it does not block this slug and this slug is not churn under either D-1 outcome.

## Scope — a Qt-free `src/lr_reduction/roi_estimate.py`, fixture-tested

Pure functions (no Qt), each tested against a synthetic NeXus fixture:
- `read_nexus_metadata(path)` — run/seq number+id, title, `ths`/`thi`/`tthd` from DASlogs.
- `chopper_tof_window(...)` — **via the library `nr_tools.get_lam_range` (`scaled_width=3.4`)**,
  NOT a private copy. This is exactly where #197 drifted (F3: its `CHOPPER_BANDWIDTH=3.5` is a
  third copy, ~3% off) — a clean discrepancy: **use the one library source, do not re-derive.**
- `counts_vs_y(...)` / `load_event_pixels(...)` — sub-sampled `bank1_events`, band-filtered;
  reuse `binary_processing.get_y_tof` where it applies (call the library, don't fork it).
- `estimate_peak_range(...)` / `default_bkg_roi(...)` — peak (smoothed argmax + half-max walk +
  contrast score) and background (gap/width) estimate, returning plain values (no widget state).

**Independence (Advisor §2.1):** read #197's `json_settings_builder.py` for **domain facts**
(which DASlogs, which header keys) — do NOT copy its functions; copying the maths a fourth time
makes the later reconciliation worse, not better. Geometry from the time-indexed instrument DB
(`src/lr_reduction/settings.json`), never hard-coded 304×256 / 15.75 m (#197's F3 sibling).

## Guards / acceptance (amendments 16 / 18 / 21)

- A synthetic `tests/data/*.nxs.h5` (h5py: `bank1_events/{event_id,event_time_offset}`, DASlogs
  chopper + sequence); each function RED-then-GREEN with a mutation-ledger row (mutate the named
  thing → confirm RED → record `<mutation> -> N failed`), restore-first, under a per-test timeout
  well below the 600 s ceiling.
- **State enumeration (amendment 21):** the chopper window is `None`/absent until derived — a
  function given no chopper log must **derive or refuse**, never replay a stale window; the guard
  varies **presence** (absent-`None` / present), not only value.
- **Qt-free (VR-2/VR-4):** imports with no GUI package present; `pixi run test-reduction` green;
  `pixi.lock` byte-identical (restore, don't stage — see the Developer contract).
- **Review domains (§5):** **numerical-diagnostics-reviewer (blocking** — the 3.4-vs-3.5 bandwidth
  and any hard-coded geometry: audit the parameter against the library/DB, per the clean-factor
  rule); test-reviewer (fixture realism, mutate-once); design-reviewer (the pure/Qt split).
- Draft PR on pass. **Wiring to the resolver's layer (e) `dataset_probe` is a later staged step**
  (needs Slug A) — this slug delivers the tested module only.

Dispatched as `triage/roi-estimate-v1`. (Replaces `triage/roi-selector-v1`, withdrawn 2026-09-19
per the Advisor reconciliation — A1 is D-1, deferred to the human.)
