# Plan: roi-selector (T1) — A1 bug-fixes + re-enable now; phase 2 rewrites & reconciles against upstream #197

**Campaign:** `exp-settings-roi` · charter §4 slug **T1** (the run's target milestone —
the scientist is waiting to review this). Full design/background:
`tasking/plan/roi-selector/plan.md` (the authoritative source is
`launcher/apps/roi_selector.py` in the checkout, NOT the design doc). **Retry attempt:** 1.

## T1 strategy — Advisor-reconciled 2026-09-19 (supersedes the A1-first framing below)

The Advisor's position (`tasking/plan/roi-selector/advisor-position-t1-strategy.md`), accepted:

- **Slug cut (§4 sizing):** `roi-estimate` (Qt-free layer-(e) probe — **dispatched now** as slug 1,
  `plans/roi-estimate-plan.md`) → `roi-view` (2D map + TOF projection + drag, R14) → `roi-tab`
  (per-run flow R1/R2, writes through `SettingsDocument`) → `roi-vs-197-review` (the comparison) →
  `settings-builder-on-document` (the fold-in on a landed #197).
- **A1 (patch + re-enable the old 2268-line tab) is D-1 — the human's call**, NOT dispatched. Worth
  doing only if the beamline needs a usable tab *this week*; otherwise it is churn the rewrite
  discards and it biases the #197 comparison (patched-old-tab vs a 180-line dialog). The A1 scope
  is retained below as the spec should D-1 = yes.
- **No-overlay constraint (Advisor §1 — the Slug-B-deferral hazard):** every T1 slug writes tab
  edits **through `SettingsDocument`** (`set_angle_field` already models the `None` collapse); the
  resolver is read **once at seed time**; the layer walk is **never enumerated in T1 code** (use
  the resolver API) — so Slug B lands later without touching T1, and T1 never rebuilds
  `_session_edits`'s three-state hazard under another name.
- **"Independent" = independent of #197's *code*, not the campaign model (§2.1):** build on
  `SettingsDocument`/`FIELD_SPEC`/resolver + library helpers (`nr_tools.get_lam_range`,
  `binary_processing.get_y_tof`); read #197 for domain facts, never copy its functions (F3 is the
  fourth-copy cautionary case).
- **Fix the comparison criteria before building (§2.2):** the `roi-vs-197-review` slug scores
  R1–R14 + #197's F1–F6 for both artefacts, same IPTS fixture, the five feature-spectrum axes,
  reviewer ≠ implementer.
- **Landing order (§2.3, D-2):** recommend **(i)** #197 lands first on `exp-review` (F1/F2/F4 as
  review comments), T1 stacks on it; **no T1 slug touches `json_settings_builder.py`.**

**Decisions surfaced to the human (Advisor §4):** D-1 (A1 vs roi-estimate-first — roi-estimate
dispatched as the no-regrets opener; A1 awaits your word); D-2 (landing order — (i) recommended);
D-3 (tell the scientists layer-(b)/B6-b is deferred — yes, one sentence, with the parked plan as
the pointer).

## Independence (why this dispatches now, concurrent with Slug A)

- **Base:** `agentic/exp` @ `6da473d` — already carries the **S0 launcher-test harness**
  (`launcher/tests/conftest.py` `no_qmessagebox`/`isolated_qapp`, the `test-launcher`
  pixi task with `--timeout=120`, `pytest-timeout`) and **T2** (`settings_document.py`,
  `field_spec.py`). It does **not** need T3.
- **A1 is XML-based bug-fixing of the existing tab** — it reads/writes through the
  current module, not the resolver. It consumes T3 **not at all** (charter §4 ties the
  T2/T3 dependency to the *JSON output*, which is phase A3). **Layer (b) is *populated
  by* this tab, not consumed from T3** — so the Slug B deferral does not touch T1.
- **File-disjoint from Slug A** (`roi_selector.py` + `new_launcher.py` + a new test file,
  vs. `settings_*.py`) → the two lanes land without conflict. **Dispatch priority 2**
  (Slug A is priority 1, the ratified critical path).

## Symptom / the ask

`launcher/apps/roi_selector.py` (~2265 ln) lets a scientist load runs, view each run's
detector image / Y-vs-TOF map, and pick the **peak ROI, background bands, and TOF
window** per run, then write them to a reduction template. The scientists judged it
unworkable/tangled; it is currently **commented out** of the launcher (`new_launcher.py`
lines 42-46, import removed in `45a9550`). **A1 = fix what is actively wrong, test it,
re-enable it** — the shortest path to a tool usable at the beamline.

## Scope — A1 (one coherent surface: the tab's correctness + re-enable)

| # | Fix | Site |
|---|---|---|
| **R1** | per-run q-method silently never persisted (`runs_sorted` used before assignment, swallowed by a blanket `except`) | `save_combined_template()` ~:2047/2058 — hoist the assignment, **remove the blanket `try/except Exception: pass`** so the next regression is loud |
| **R2** | DB-file / q-method attach to the **wrong run** on a non-ascending run list (parallel-list indexing) | replace the four parallel per-run structures with **one dict keyed by run number**; save path iterates by run key |
| **R5** | the background region the scientist **sees plotted differs from what is written** (two writers disagree by one pixel row) | one pure `background_regions(mode, ymin, ymax, bkg1, bkg2, n_y)` (outer-limits ±1, panel (c) — §12 Q3 resolved) called from `_draw_plots()` **and** both save paths → drawn == written |
| **R14** | TOF axis **cropped to the chopper window at load**, cannot be expanded (out-of-window events masked out) | `load_file()` histograms the **full event TOF span**; the chopper window becomes the initial view + seed only, never a mask |
| **R4** | dead chopper-TOF branch (`abs(float(self._chopper_val))` on a tuple; unset `_chopper_*`) → `TypeError` swallowed | delete it; route the one chopper-window computation through `nr_tools.get_lam_range` |
| **R3/R10/R11** | dead duplicate `SaveTemplateDialog`; `print()`→`logging`; delete unreachable `DBPerRunDialog`/`_open_db_per_run`, unused `artist_name_map` | cleanup |
| **re-enable** | un-comment `new_launcher.py` 42-46, re-add the `ROISelector` import | — |

**Out of A1 (deferred to phase 2):** the drag-interaction rewrite (R7/R8), 2D XY maps,
model/view split, JSON output through the resolver (A3), and the B5 two-background widget
removal (confirm with Analyst whether B5 rides A1 or A2 — **left for A2** to keep A1 a
pure-correctness surface).

## Amendment compliance (16 / 18 / 21 / 20 — all post-date the design doc)

- **Mutation ledger (amendment 16):** every guard below carries an author-side mutation —
  mutate the named thing, confirm RED, record `<mutation> -> N failed` in the commit body;
  one row per call site; **frame-first**; run under a per-test `timeout` **well below** the
  600 s harness ceiling (see [[todo-mutation-harness-restore-safety]] — restore-first,
  one-suite-per-command, emit a `=== DONE ===` sentinel + per-step `_EXIT=`).
- **State enumeration (amendment 18 + 21):** R4/R14 turn on the **`None`-as-real-value**
  trap this campaign keeps hitting — the chopper window is *absent/`None`* until derived.
  Enumerate the states each fix's value can occupy — **present / absent-`None` (derive from
  chopper) / out-of-range** — and vary the state in the guard, not only the dimension. A
  cleared/absent TOF window must derive, not replay a stale one.
- **Decompose-criterion (amendment 20, armed proactively):** A1 is dispatched as **one
  slug** because the fixes share one file and one surface (the tab's correctness) — same-
  file sub-parts would serialize-with-conflicts, not parallelize. **But if A1 is rejected
  on the same *demonstrate-the-case-at-a-new-level* shape, DECOMPOSE** into
  `roi-per-run-keying` (R1/R2 — the per-run data-structure surface) and
  `roi-background-tof` (R5/R14 — the drawn==written surface); do **not** extend the cap.

## Guard tests (RED → GREEN, §8 seeds + a synthetic fixture)

`launcher/tests/test_roi_selector.py` (new): `test_save_persists_q_methods` [R1],
`test_per_run_db_follows_run_number` [R2], `test_background_regions_modes` [R5],
`test_chopper_window_used_when_present` [R4], `test_tof_histogram_spans_full_event_range`
[R14], `test_module_import_headless`. Add a tiny synthetic `launcher/tests/data/*.nxs.h5`
(h5py-written: `bank1_events/{event_id,event_time_offset}`, DASlogs chopper + sequence);
reuse `no_qmessagebox`.

## Review domains (charter §5 — multiple domains, one slug)

**ui-aspects-reviewer (blocking** — R5 drawn==written; R14 TOF view; the **active-row trap**
in per-run tables, the campaign's signature widget bug); **numerical-diagnostics-reviewer
(blocking** — R4/R14 chopper-window physics via `nr_tools.get_lam_range`, and any clean
factor: cf. #197's F3 3.5-vs-3.4 bandwidth); **test-reviewer** (synthetic `.nxs.h5`
realism, mutate-once honoured); **design-reviewer** (the per-run keying refactor).

## Acceptance (A1)

- The six guards present and RED-then-GREEN with a mutation ledger; `pixi run test-launcher`
  + `test-reduction` both EXIT=0; `pixi.lock` byte-identical.
- Tab re-enabled in `new_launcher.py`; `test_module_import_headless` proves it imports.
- Reviewers pass. Draft PR on pass; merging stays the human's deploy decision (§7).

## Phase 2 (after A1 + Slug A land) — rewrite, then review against upstream #197, then stack

Per the human's plan (2026-09-19) and the pre-analysis in
`tasking/plan/contrib/review-exp-json-settings-builder/**` (upstream PR #197, a
settings-builder tab the maintainer coded independently — **workflow-rich, model-poor**):

1. **Implement the T1 rewrite independently first** — grow the ROI tool to 2D XY + y-vs-TOF
   maps + TOF-window overlay + sibling-style drag (T1 decision D-1), on T1's own design,
   consuming Slug A's resolver for seeding (layers a,c,d,e,f) and populating layer (b)
   locally. Retire the tangled 2265-line module.
2. **Then conduct a 2nd review against #197** — **adopt** #197's *proven workflow surface*
   (run-list via `parse_run_list`, direct-beam DB discovery, sequence/out-of-order
   warnings, sparse output, its `ROISelectionDialog` as the drag seed) rather than
   re-deriving it; **implement the science independently** and reconcile the disagreements
   the pre-analysis flagged: F3 (`CHOPPER_BANDWIDTH=3.5` vs library `get_lam_range(3.4)` —
   a clean ~3% discrepancy: **audit the parameter, per numerical-diagnostics, do not assume
   physics**), the peak-estimator choice (#197 half-max-walk vs T1 Gaussian+prominence —
   **compare on real IPTS data** before one becomes canonical), F1 (all-13-arrays
   invariant — T3/T2 win), F2 (atomic save — T2 wins). Move #197's Qt-free ROI functions to
   `src/lr_reduction/roi_estimate.py` (tested), which also becomes **T3's layer-(e) probe**.
3. **Stack the best of both** into the final contribution to present to the scientists.
   **Caveat to surface:** the pre-analysis's Phase-0 fixes (F1/F2/F4) live in the
   maintainer's PR; the stacked contribution either needs maintainer cooperation OR the
   campaign re-seats #197 on the `SettingsDocument` model itself. Flag at phase-2 dispatch.

Phase 2 is **staged** — dispatched only after A1 and Slug A land (see
`tasking/plan/campaign-dispatch-queue.md`, the staging queue).

## roi-vs-197-review — pinned scope (#197 @ `ab22307`; F-findings re-verified 2026-09-20)

The comparison slug's criteria, fixed **before** T1 is built (Advisor §2.2), pinned to the
**current** #197 head `ab22307` (the pre-analysis used `f5513c7`; the file grew 1394→1502 lines,
line refs shifted, the findings persist):

**Re-verified at `ab22307`:**
- **F1 CONFIRMED** — `PER_RUN_KEYS` (`json_settings_builder.py:86`) models **8** per-run arrays;
  `tof_min`/`tof_max`/`LambdaMin`/`LambdaMax` are unmodelled and `RBnum` is handled separately
  (`:1289`,`:1330`), so add-row grows 8 while the rest stay at n and the reducer's positional
  index (`nr_reduction_calc.py:103-106`) reads a shifted TOF cut on the last angle. Breaks FR-11.
- **F5 CONFIRMED** — private field tables cover ~**28 of 55** (`GLOBAL_FIELDS`=20 + 8 per-run);
  the rest ride `extra_keys` with label-only help — a second opinion beside `FIELD_SPEC`.
- **F3 CONFIRMED** — `CHOPPER_BANDWIDTH = 3.5` (`:80`) vs library `get_lam_range(scaled_width=3.4)`:
  the clean ~3% discrepancy; audit the parameter, do not re-derive (numerical-diagnostics).

**Comparison artefact (the slug's acceptance):** score **both** artefacts (campaign T1 vs #197
`ab22307`) on — **checklist:** T1's **R1–R14** + #197's **F1–F6**, each `pass/fail/n.a.` for both;
**same data:** the IPTS run series + the synthetic `.nxs.h5` fixture the T1 plan §8 names; **five
axes** (`feature-spectrum.md` §3: workflow fidelity, written-file correctness, facility-boundary
safety, ROI capability, maintainability); **reviewer ≠ implementer** (an Integrator gate,
ui-aspects + design, its own `review/` surface, one slug). Output = the fold-in list for
`settings-builder-on-document`.
