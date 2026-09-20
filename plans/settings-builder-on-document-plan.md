# Plan: settings-builder-on-document (#197 fold-in) — re-seat the builder on SettingsDocument; retire the standalone tab; two-tab end state

**Campaign:** `exp-settings-roi` · #197 incorporation Phase 1 (pre-analysis
`tasking/plan/contrib/review-exp-json-settings-builder/**`). **Retry attempt:** 1. **STAGED** —
dispatch when **Slug A merges AND #197 has landed on `exp-review`** (§7; landing order (i), D-2).
Base: `exp-review` at the #197 tip (`ab22307` or later). Fold-in list comes from `roi-vs-197-review`.

## End state: two tabs, one document, #197's standalone builder RETIRED

#197 (`ab22307`) ships a **standalone** `JSONSettingsBuilderTab` (~1502 ln) with its own
`RunRow`/`GLOBAL_FIELDS`/`extra_keys` model and a truncating writer. This slug **retires that as a
separate model** and re-seats its UI on the campaign's `SettingsDocument`, ending with **two tabs
over one document** (the human's choice, 2026-09-20; the incorporation plan left one-vs-two open):
- **Workflow tab** (from #197): IPTS → run-list → NeXus-metadata rows, sequence/out-of-order
  warnings, direct-beam discovery + per-row picker, ROI estimate/select, sparse output — the
  workflow surface #197 got right.
- **Advanced/editor tab** (from T2's `SettingsEditorTab`): the full `FIELD_SPEC` scalar panel,
  provenance badges, all 55 fields.

Both read/write **one `SettingsDocument`** — the invariant: never two models for one file. The
scientist sees two tabs; the code sees one document + one atomic writer.

## Scope — the re-seating + retirement (each item retires a re-verified #197 finding)

1. **Model:** `RunRow` + `GLOBAL_FIELDS` + `extra_keys` → a **view over `SettingsDocument`**
   (`angle_row(i)`, `FIELD_SPEC` filtered). All 55 fields covered (**retires F5**); the 13-array
   invariant via `add_angle`/`_equalise_angles` (**retires F1** — the add-row desync confirmed at
   `ab22307:86`).
2. **Writer:** #197's truncating `open(path,"w")` → `SettingsDocument.save` (temp + fsync +
   `os.replace`) + the shared-path confirmation (**retires F2**; FR-26).
3. **Domains:** #197's private `METHODS`/`DetResFn` lists → `reduction_domains` (**retires F4** —
   withhold the `DetResFn='none'` crash value).
4. **Geometry/chopper:** hard-coded 304×256 / 15.75 m and `CHOPPER_BANDWIDTH=3.5` (`ab22307:80`)
   → `nr_tools.get_lam_range(3.4)` + the time-indexed instrument DB (**retires F3**).
5. **ROI functions:** #197's Qt-free estimators are already delivered as
   `src/lr_reduction/roi_estimate.py` (T1 slug 1) — the builder **calls that module**, which is
   also **T3's layer-(e) `dataset_probe`**. No fourth copy of the chopper/ROI maths.
6. **Retire the standalone tab:** remove #197's separate model/writer; the workflow tab
   instantiates over the document; `new_launcher.py` shows the two tabs (the one merge conflict
   #197 had, resolved with both tabs present).

## Guards / acceptance (amendments 16/18/21)

- FR-11: add-row/remove-row keeps all 13 arrays aligned (mutate-once guard varying the row count).
- FR-26: save is atomic + confirmed — a guard that a **failed write leaves the prior file intact**
  (the amendment-21 state axis: failed-write-over-existing-file, the same shape as learnings-review
  F2).
- `DetResFn='none'` withheld (guard the domain); Qt-free ROI logic tested without a GUI.
- `pixi run test-launcher` + `test-reduction` green; `pixi.lock` untouched (restore, don't stage).
- Draft PR on pass. Merging + the maintainer relationship (retarget #197, D-2 (i)) stay the human's.

## Depends on / risk

- Needs **Slug A** (resolver + `SettingsDocument`) and **`roi_estimate`** (T1 slug 1) landed; the
  layer-(e) wiring + provenance retrofit is Phase 3 (needs T3-full) — Phases 1-2 here do not.
- **#197 must land on `exp-review` first** (D-2 (i)). If the maintainer declines to retarget, this
  slug supersedes #197 as a campaign PR (incorporation Option (iii)) — the human's call, not the
  Analyst's.
