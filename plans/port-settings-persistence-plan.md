# Plan: port-settings-persistence (S3)

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` · charter §3 PR
#11 disposition ("re-implement on `exp` — highest user value: the deployed
GUI forgets typed values") · seed `agentic/feature/settings-persistence` @
`18ff75b`
**Retry attempt:** 3 (final — N=3; the next rejection escalates)

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
  **Addendum 2026-08-19 (from S2's v1 rejection, todo.md @ `1c0fc43`,
  advisory section):** S2's mode gating force-resets the transform combo
  to `"None"` whenever R*Q⁴ is disabled (one direct-beam plot does it) and
  never restores the prior choice. Once THIS slug saves
  `overplot_ytransform`, that forced reset would silently overwrite the
  user's stored preference. The save half must not persist a forced
  reset: either skip the `overplot_ytransform` write while the R*Q⁴ combo
  entry is disabled, or remember/restore the user's explicit choice when
  it re-enables — implementer's pick, with a test either way (plot a DB
  fixture, then assert the stored `overplot_ytransform` still holds the
  user's prior explicit choice).
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

## Revision history

### v2 — 2026-08-19 (after v1 rejection; todo.md @ `01d7e6f`)

Blocking fired per this plan's own declaration (ui-aspects) — no
disposition dispute this cycle. Two findings, both re-verified by the
Analyst on the feature branch:

- **B1 is partly a plan defect, owned here:** v1's instruction
  "`ipts_toggle` set under `blockSignals` (its `toggled` handler mutates
  path fields)" ported PR #11's guard together with a false premise. The
  ordering analysis in the todo is correct: the save connections attach
  *after* `read_settings()`, and an unguarded restore would derive paths
  and then have them overwritten by the stored values anyway — the guard
  suppresses only `_ipts_toggled`'s enable/disable side, leaving
  `nexus_edit`/`savepath_edit` editable under a checked toggle
  (restore at `:389-391`, the only enforcement in `_ipts_toggled`, the
  consuming branch `_run_create_db:536` — typed paths silently
  discarded). The v1 failure-mode row "blockSignals around the restore"
  is superseded by the v2 fix below.
- **B2:** `test_isolation_from_legacy_launcher` installs the production
  identity (`ORNL`/`lr_reduction_new_launcher`) via `QCoreApplication`
  statics, never restores, and — combined with Qt's cached settings
  root — reachably writes the developer's real `~/.config` (reproduced
  by the reviewer). Its assertion is also a tautology (two different
  org/app pairs always differ). v1 inherited the test verbatim from
  PR #11.
- The two `test-reduction` failures were the known cross-clone `/tmp`
  race (identical foreign value in both, serialized re-run 2/2 green) —
  external interference, zero retry budget consumed; strengthens the
  parked `test-tmp-isolation` proposal.

## v2 fixes

**B1 — apply the mode, don't suppress it** (`launcher/apps/direct_beam.py`):
split the handler per the todo's sketch —

```python
def _apply_ipts_mode(self, state):
    """Enable/disable the manual-path fields for the IPTS-structure mode."""
    self.nexus_edit.setEnabled(not state)
    self.savepath_edit.setEnabled(not state)
```

`_ipts_toggled(state)` keeps its derivation branch and ends with
`self._apply_ipts_mode(state)`; `read_settings()` calls
`self._apply_ipts_mode(self.ipts_toggle.isChecked())` immediately after
`blockSignals(False)` (keep the guard only to avoid a redundant
derivation pass — with the mode applied explicitly it is now harmless
either way). **Restore default flips to `False`**
(`direct_beam_use_ipts_path_structure`, `:390`): PR #11's `True` is an
inherited first-launch behavior change on a deployed line — `False`
preserves what `exp` does today (deviation from the seed PR, flagged
here deliberately). Tests: enabled-state assertions for both stored
values (construct with the key pre-seeded `True` → both fields
disabled; `False` → enabled), and `test_direct_beam_first_launch_defaults`
extended to assert `ipts_toggle.isChecked() is False` and
`nexus_edit.isEnabled() is True` — the two widgets whose first-launch
semantics this slug touches.

**B2 — delete `test_isolation_from_legacy_launcher`.** It buys nothing
(asserts Qt's org/app→path contract, green on unmodified `exp`) and
costs a process-global production-identity leak. The distinct-store
property is delivered and asserted by the `harness-hardening` slug's
conftest work (`setPath` isolation + org/app restore + the
`fileName().startswith(tmp_path)` assertion), which is implemented and
at the Integrator's gate. **Do not touch `launcher/tests/conftest.py`
in this slug** — that file is `harness-hardening`'s; if its PR has
merged into `exp` by v2 time, a regular merge of `exp` into this
feature branch may pick it up, otherwise proceed without it.

**Promoted from the review's advisory list (cheap, named, in scope):**

1. Identity constants become importable: new `launcher/app_identity.py`
   with `ORG_NAME = "ORNL"`, `ORG_DOMAIN = "ornl.gov"`,
   `APP_NAME = "lr_reduction_new_launcher"` and an idempotent
   `ensure_identity()` (set the three statics only if unset/different);
   `main()` calls it, and each settings-bearing tab calls it first in
   `__init__` — non-GUI entry points then resolve the same store. The
   plan's T2/T3 adoption contract now points at this module, not at
   inline literals.
2. One-shot migration of the two legacy keys: on first launch with an
   empty new store, copy `overplot_folder` / `overplot_xscale` from the
   org-less legacy store (`QSettings()` with cleared identity) if
   present; PR body states the policy (everything else starts fresh).
   *(**Superseded by v3** — the two-key scope orphans ~61 of 63 launcher
   keys; see the v3 revision entry.)*
3. Coverage that makes the wiring load-bearing: a parametrized
   round-trip over all 18 `direct_beam_*` keys; one signal-driven save
   test (mutate a field, emit `editingFinished`, fresh tab reads it
   back — no explicit `save_settings()` call); one disk assertion
   (`tab.settings.fileName()` exists and contains a written key after
   `sync()`).

Everything else from v1 stands (scope, strip list, keys, queue note,
pixi.lock caveat).

### v3 — 2026-08-19 (after v2 rejection; todo.md @ `c32ee5f`; FINAL retry)

Both v1 findings RESOLVED and verified; three v1 advisories adopted
unbidden; gate green (34+107, no race). The one new blocking finding is
a **blast-radius under-measurement owned by this plan**: v2 directed a
two-key migration on the v1 review's "two re-typeable preferences"
framing without measuring what the identity switch actually repoints —
`ensure_identity()` in `main()` moves the store for the whole process:
**63 keys across 11 launcher modules** (ground truth, measured by the
gate; both reviewers reproduced the loss end-to-end). On first launch
the Batch-file tab loses 11 keys, SLD 2, seven more tabs lose templates
and output paths — a one-time mass-forget from the slug whose symptom
statement is "the GUI forgets typed values". The radius existed in v1's
inline identity too and every reviewer missed it then; v2 owns it
because v2 added the migration and with it the question "does the
migration cover the break". Analyst re-verified the key citations:
both `pyproject` gui-scripts ship (launcher.py never installs the
identity), and `migrate_legacy_settings` clears the three identity
statics *outside* its `try` (one raise leaves the process nameless).

## v3 fixes (final retry — the gate's order)

1. **B3 — migrate the enumerated launcher key set behind a sentinel.**
   Build the list from ground truth at implementation time (grep every
   `settings.value`/`setValue` key across `launcher/**`; the gate
   counted 63 across 11 modules) and commit it as the module-level
   `LEGACY_KEYS` with a per-module comment. Enumerated, NOT wholesale
   `allKeys()`: `Unknown Organization.conf` is the shared dumping ground
   for every identity-less Qt app on the machine, and generic names
   (`output_dir` at `xrr.py:67,74`, `db_output_dir` at
   `quick_reduce.py:98`) concentrate the foreign-import risk. Gate the
   one-shot on a **sentinel key** (`settings_migrated_from_legacy`)
   written after a successful copy — recorded, not inferred from data;
   never overwrite an existing new-store value. Fix the docstring (the
   old text's "the only keys it held" is factually wrong). PR body
   states the policy against the real number — the human can still
   narrow it at the MR, but decides against 63, not 2. Guard test per
   the gate: seed one key per affected module in a nameless store, run
   the `main()` prologue, assert every key survives and a second run is
   a no-op.
2. **Subprocess restart test** (highest remaining leverage; closes six
   gaps at once — today inverting `_bool`'s string branch leaves 32/32
   green while a real restart returns two widgets inverted): spawn
   `sys.executable -c …` twice with `HOME`/`XDG_CONFIG_HOME` pointed
   into `tmp_path`; phase 1 saves all 18 `direct_beam_*` keys through a
   real tab, phase 2 constructs a fresh tab and prints the read-back as
   JSON; assert equality. **Comment in the test why the subprocess is
   required** (Qt serves the second in-process `QSettings` from the
   first's cached `QConfFile` — in-process "restarts" never touch the
   coercion layer), or someone will simplify it back.
3. **Identity hardening, landed WITH item 1** (each widens/narrows the
   same radius): `ensure_identity()` guards on
   `if app.organizationName(): return` only (the current `or` predicate
   early-returns when `applicationName()` is auto-derived from argv —
   `QApplication(sys.argv)` scripts end up as
   `Unknown Organization/script.py.conf`, and T2/T3 are contractually
   pointed here); add `ensure_identity()` to `launcher/launcher.py`'s
   `main()` (the second shipped binary — otherwise the SLD tab splits
   stores between binaries); open `migrate_legacy_settings`'s `try`
   BEFORE the three identity clears, and comment the non-reentrancy.
4. **Coverage the gate named** : one table-driven test over the 16
   `(widget, signal, setter, key)` save connections (1/16 → 16/16,
   including the Cd/moderator dialog saves — the only persistence path
   for `cd_vals`/`mod_vals`); a live-toggle test covering
   `_ipts_toggled`'s own `_apply_ipts_mode` call (the click path, not
   just the restore path); make `never_overwrites` self-contained
   (seed its own legacy value); wrap the migration test's identity
   blanking in `try/finally` (correct-and-flag: the GREEN body's
   "restores in a finally" claim is true of the *other* identity test,
   not this one); prefer `QSettings().fileName()` assertions over Qt
   statics where the file is the consequence that matters.
5. **Optional, drop first if anything wobbles:** Overplot
   `folder`/`xscale`/`sync()` coverage; the greyed-path-provenance
   advisory stays recorded, not scoped.
