# Plan: port-settings-persistence (S3)

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` · charter §3 PR
#11 disposition ("re-implement on `exp` — highest user value: the deployed
GUI forgets typed values") · seed `agentic/feature/settings-persistence` @
`18ff75b`
**Retry attempt:** 1

Review domains: ui-aspects-reviewer (**blocking** — QSettings wiring and
widget-state round-trips are its exact trap list), test-reviewer (advisory).

**Scope note (charter §3, binding):** per-tab **UI-preference** persistence
only. The reduction-settings and global-settings layers belong to T2/T3 —
which must adopt this slug's org/app constants so all layers share one
QSettings store. **Record for T2/T3:** the canonical identity is
`setOrganizationName("ORNL")`, `setOrganizationDomain("ornl.gov")`,
`setApplicationName("lr_reduction_new_launcher")`, set in
`new_launcher.main()` before `QApplication([])`.

## Symptom

The deployed `exp` launcher forgets everything typed into the Direct-beam
tab (run list, IPTS, paths, cuts, TOF binning, ROIs, Cd/moderator dialog
values) on every restart, and the Overplot tab loses its Y-transform
choice. Only Overplot's folder/xscale persist today. PR #11 solved this on
the retired `ui_plan` lineage; per charter §3 it is **re-implemented** here
(all touched identifiers verified live on `exp`), extended to the #155/#156
TOF-rebin spinboxes that did not exist when the PR was written.

## Verified state (against `agentic/exp` @ `a4ae8b8`, 2026-08-18)

- `DirectBeamTab` (line 201): `self.settings = QtCore.QSettings()` at 205;
  **no `read_settings`/`save_settings` exist** (0 hits) — clean landing.
  All PR-#11 identifiers verified present: `run_list_edit`, `ipts_edit`,
  `ipts_toggle`, `nexus_edit`, `savepath_edit`, `savename_edit`,
  `DTCcut_spin`, `DTCcut1_spin`, `Icut_spin`, `CutOffset_spin`,
  `yroi_edit`, `lowres_edit`, `plot_cb`, `cd_vals`, `mod_vals`,
  `_open_cd_settings` (350), `_open_mod_settings` (359).
- **#155/#156 extension targets** (absent from the PR): `tofbin_spin`
  (range 5–2000, default 50), `tofmin_spin` (0–100000, default 0),
  `tofmax_spin` (5–2000000, default 100000) at lines 263–277.
- `Overplot.save_settings` (180–182) writes folder + xscale only;
  `read_settings` already reads `overplot_ytransform` (176) — the missing
  *save* half is this slug's overplot change. (S2 owns `overplot_mode` /
  `overplot_last_refresh`; keys are disjoint.)
- `new_launcher.py`: has a real `main()` (pyproject GUI entry point) —
  org/app lines land **inside `main()`**, before `QApplication([])`; the
  PR's `__main__`-block placement is obsolete. `ReductionInterface.__init__`
  has an unused `self.settings = QtCore.QSettings()` — remove per the PR
  (verified: no other use in the file). The ROI-selector tab is commented
  out on `exp` (T1 re-enables it later).
- **Drop the PR's `roi_selector.py` portion entirely** (charter §3: module
  detached from `new_launcher`; superseded by T1). Do not touch
  `launcher/apps/roi_selector.py`.
- Post-lint base (PR #14): semantic re-apply, not raw hunks. PR diff:
  `git fetch agentic refs/heads/feature/settings-persistence`;
  `git diff 3b599c7..agentic/feature/settings-persistence -- launcher/`.

## Files to change (on `feature/port-settings-persistence` from `agentic/exp`)

1. `launcher/apps/direct_beam.py` — `DirectBeamTab` gains, per PR #11
   adapted:
   - `read_settings()`: keys `direct_beam_run_list`, `direct_beam_ipts`,
     `direct_beam_use_ipts_path_structure` (bool via the `_bool` coercion —
     QSettings stringifies), `direct_beam_nexus_path`,
     `direct_beam_save_path`, `direct_beam_save_name`, `direct_beam_DTCcut`,
     `direct_beam_DTCcut_config1`, `direct_beam_Icut`,
     `direct_beam_chopper_cut_offset`, `direct_beam_y_ROI`,
     `direct_beam_x_ROI`, `direct_beam_plot`, JSON-decoded
     `direct_beam_cd_vals` / `direct_beam_mod_vals` (corrupt → `{}`), **plus
     new** `direct_beam_tofbin`, `direct_beam_tofmin`, `direct_beam_tofmax`
     (float, same guarded `setValue` pattern as the other spins).
     `ipts_toggle` set under `blockSignals` (its `toggled` handler mutates
     path fields).
   - `save_settings()`: the mirror writes + `s.sync()`.
   - `__init__` tail: `self.cd_vals = {}` / `self.mod_vals = {}` init,
     `self.read_settings()`, then defense-in-depth saves: `editingFinished`
     on every QLineEdit, `toggled`/`valueChanged` (lambda `_`) on
     toggle/spins **including the three TOF spins**, matching the PR's
     pattern.
   - `_open_cd_settings` / `_open_mod_settings`: `self.save_settings()`
     after accepting dialog values.
2. `launcher/apps/overplot.py` — `save_settings` adds
   `overplot_ytransform` write + `self.settings.sync()`.
3. `launcher/new_launcher.py` — org/app/domain constants at the top of
   `main()`; remove the unused `ReductionInterface.settings`.
4. `launcher/tests/test_settings_persistence.py` — the PR's tests minus the
   ROI-selector one, adapted (imports `launcher.apps.…`;
   `usefixtures("isolated_qapp", "no_qmessagebox")` marks): 6 ported tests
   (`test_direct_beam_ipts_persists`, `test_direct_beam_cd_vals_round_trip`,
   `test_direct_beam_corrupt_cd_vals_tolerated`,
   `test_overplot_saves_ytransform`, `test_isolation_from_legacy_launcher`,
   `test_direct_beam_first_launch_defaults`) **plus one new**:
   `test_direct_beam_tof_spins_persist` (set tofbin/tofmin/tofmax to
   non-defaults, `save_settings()`, `deleteLater()`, new tab reads them
   back — the #155/#156 extension gets its own regression test).
   Teardown by `deleteLater()` (never `destroy()` — ui-aspects pattern).
   `test_direct_beam_first_launch_defaults` asserts `ipts_edit` empty AND
   the TOF spins at their widget defaults (50/0/100000) on a fresh store.

**Strip list:** PR's `roi_selector.py` hunk (charter), `todo.md`,
`pixi.lock`, `pyproject.toml` hunks, PoC `conftest.py`/`__init__.py` (S0's
stand).

**pixi.lock caveat:** identical to S1/S2 — no dependency change; restore
any hook-side v7 rewrite; never commit a lock not starting `version: 6`.

**Queue note:** work this slug after S1 (both edit `direct_beam.py` —
disjoint regions: S1 rewrites the two dialog *classes*, S3 adds
`DirectBeamTab` methods). Branch from current `agentic/exp` per protocol
regardless of whether S1's PR has merged; if it has not, flag the
same-file overlap in the draft-PR body so the human orders the merges.

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Value typed, window closed without focus leave (common) | covered by dialog-accept + toggle/spin saves; residual: in-flight unfocused QLineEdit | defense-in-depth signal saves (PR pattern); documented residual |
| QSettings returns strings for bools/floats (common) | round-trip tests with fresh tab instances | `_bool` coercion + guarded float `setValue` |
| Corrupt JSON in cd/mod values (edge) | `test_direct_beam_corrupt_cd_vals_tolerated` | parse-guard → `{}` |
| Bleed into the legacy launcher's store (edge) | `test_isolation_from_legacy_launcher` (file paths differ) | explicit org/app in `main()`; tests use `isolated_qapp` |
| `ipts_toggle` restore fires `_ipts_toggled` mutating fields (edge) | first-launch + persist tests | `blockSignals` around the restore |
| TOF spins persist stale values after #155/#156 evolve ranges (edge) | guarded `setValue` clamps to widget range | range comes from the widget, not the store |
| ROI-selector portion ported by momentum (edge) | diff-scope check in acceptance | strip-list + do-not-touch note |
| S1/S3 same-file overlap (edge) | queue note; PR-body flag | disjoint regions; human orders merges |
| `pixi.lock` v7 staged (edge) | first line ≠ `version: 6` | caveat |

## Red-Green seed

- RED: land `test_settings_persistence.py` (7 tests, adapted) first;
  `pixi run test-launcher`: all fail (`DirectBeamTab` has no
  `save_settings`; `overplot_ytransform` unsaved; isolation test fails on
  identical default stores) — commit enumerates them.
- GREEN: land the three source-file changes; full `test-launcher` +
  `test-reduction` green.

## Acceptance criteria

- `pixi run test-launcher` green (harness + this slug's 7; prior ports'
  tests wherever the branch base already contains them).
- `pixi run test-reduction` green; pre-commit clean; `pixi.lock` untouched.
- Diff touches exactly `launcher/apps/direct_beam.py`,
  `launcher/apps/overplot.py`, `launcher/new_launcher.py`,
  `launcher/tests/test_settings_persistence.py`.
- Draft PR body: supersedes PR #11 (human closes it per charter §3); notes
  the T2/T3 org-app adoption contract (constants above) and the S1
  overlap if S1 is unmerged.
