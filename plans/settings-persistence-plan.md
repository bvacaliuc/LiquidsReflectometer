# Plan: settings-persistence — new_launcher loses field values between runs

**Slug:** `settings-persistence`
**Effort:** `new_workflow-repairs-2026-04`
**Base branch:** `new_workflow_ui_plan`
**Plan revision:** v1 (initial)

## Symptom

Values typed into `new_launcher` tabs (Direct Beam most visibly, but
ROI Selector and Overplot too) do not survive a relaunch. Worse, what
*is* written by `new_launcher` lands in the same on-disk QSettings file
as the legacy `launcher.py`, so the two binaries cross-contaminate
each other's state.

## Verified root cause

There are **two compounding defects**, both stemming from
`QSettings()` being constructed with no arguments anywhere in
`new_launcher`:

1. **Shared backing-store file.** `QSettings()` with no args inherits
   the running `QApplication`'s `organizationName` and `applicationName`.
   Both launchers leave these unset, so on Linux every `QSettings()`
   call writes to `~/.config/.conf` — a single file shared with
   `launcher.py`. Two binaries, one config file, identical key names →
   silent cross-contamination on every save.

2. **Missing or partial save/read implementations** in three of the
   four tabs:

| Tab | File | `__init__` line | Save/read state |
|---|---|---|---|
| `DirectBeamTab` | `launcher/apps/direct_beam.py` | line 210 (issues.md hypothesis cited 205; current line is 210) | `self.settings = QtCore.QSettings()` declared, but **no** `read_settings` and **no** `save_settings`. Every field is forgotten on close. |
| `ROISelector` | `launcher/apps/roi_selector.py` | line 263 (matches hypothesis) | Same: declared, never read or written. |
| `Overplot` | `launcher/apps/overplot.py` | line 57 (matches) | Partial — `read_settings` (lines 166-177) restores `overplot_folder`, `overplot_xscale`, `overplot_ytransform`. `save_settings` (lines 179-181) writes `overplot_folder` and `overplot_xscale` only — **does not save `overplot_ytransform`**. Note: issues.md reads "writes `overplot_xscale` twice"; that is incorrect — the current code writes it exactly once. The genuine defect is the missing `overplot_ytransform` save. |
| `TemplateBatchTab` | `launcher/apps/template_batch.py` | line 104 | Full save/read implementation already in place (lines 352-396 of `template_batch.py`). **Use as the reference pattern**; do not modify. |

`new_launcher.py:24` (issues.md hypothesis cited 23) also constructs
`self.settings = QtCore.QSettings()` on the top-level
`ReductionInterface`, but the field is never used. Either delete that
line entirely or repurpose it for window geometry persistence (low
priority — out of scope for this plan).

## Files to change

| File | Lines | Change |
|---|---|---|
| `launcher/new_launcher.py` | 1-12 (top of file, before `QApplication([])`) | Set `QtCore.QCoreApplication.setOrganizationName("ORNL")`, `setOrganizationDomain("ornl.gov")`, `setApplicationName("lr_reduction_new_launcher")` **before** the `QApplication` is constructed in `__main__`. The legacy `launcher.py` is left alone. |
| `launcher/new_launcher.py` | 24 | Delete the unused `self.settings = QtCore.QSettings()` (or wire it to `read_settings`/`save_settings` for window geometry — opt-in by Developer; default plan is to delete). |
| `launcher/apps/direct_beam.py` | 210 (`__init__`) and end-of-class | Keep `self.settings = QtCore.QSettings()`. **Add** `read_settings(self)` and `save_settings(self)` covering the field set listed below. Wire `read_settings()` at the end of `__init__`; wire `save_settings()` to every signal that mutates a tracked field, and to `closeEvent` for defense-in-depth. |
| `launcher/apps/roi_selector.py` | 263 and end-of-class | Same shape as `direct_beam.py`. Field set listed below. |
| `launcher/apps/overplot.py` | 179-181 (`save_settings`) | Add `self.settings.setValue("overplot_ytransform", self.ytransform_combo.currentText())`. Keep the existing `overplot_folder` and `overplot_xscale` writes. |
| `launcher/apps/overplot.py` | 165-177 (`read_settings`) | Keep as-is for `overplot_ytransform`; also load `overplot_mode` per `overplot-axes-plan.md`. |
| `launcher/tests/__init__.py` | (new) | Empty package marker (already created per `overplot-axes-plan.md`). |
| `launcher/tests/test_settings_persistence.py` | (new) | Unit tests per the TDD seed below. |

### Field set to persist

**`DirectBeamTab` (one key per QLineEdit/QCheckBox/QSpinBox value):**

| Key | Source attribute | Default if missing |
|---|---|---|
| `direct_beam_run_list` | `self.run_list_edit.text()` | `""` |
| `direct_beam_ipts` | `self.ipts_edit.text()` | `""` |
| `direct_beam_use_ipts_path_structure` | `self.use_ipts_path_structure_chk.isChecked()` | `True` |
| `direct_beam_nexus_path` | `self.nexus_path_edit.text()` | `""` |
| `direct_beam_save_path` | `self.save_path_edit.text()` | `""` |
| `direct_beam_save_name` | `self.save_name_edit.text()` | `""` |
| `direct_beam_DTCcut` | `self.DTCcut_edit.value()` (QDoubleSpinBox) | code default |
| `direct_beam_DTCcut_config1` | `self.DTCcut_config1_edit.value()` | code default |
| `direct_beam_Icut` | `self.Icut_edit.value()` | code default |
| `direct_beam_chopper_cut_offset` | `self.chopper_cut_offset_edit.value()` | code default |
| `direct_beam_y_ROI` | `self.y_ROI_edit.text()` | `""` |
| `direct_beam_x_ROI` | `self.x_ROI_edit.text()` | `""` |
| `direct_beam_plot` | `self.plot_checkbox.isChecked()` | `False` |
| `direct_beam_cd_vals` | `json.dumps(self.cd_vals)` (mu_file, Cd list, flip_atten) | `"{}"` |
| `direct_beam_mod_vals` | `json.dumps(self.mod_vals)` (Chop2_cut_fn, dMod, t0) | `"{}"` |

The two structured values (`cd_vals`, `mod_vals`) are persisted as
JSON strings to keep round-tripping simple and avoid `QByteArray`
versioning concerns. Use `json.loads` on read with a try/except that
falls back to the code default — corrupt/old-schema values must not
crash the launcher.

**`ROISelector`:** the Developer enumerates the QLineEdit/QSpinBox
fields they want persisted (the most user-meaningful ones, not every
internal). At minimum:

| Key | Source attribute |
|---|---|
| `roi_selector_ipts` | `self.ipts_edit.text()` |
| `roi_selector_template_path` | `self.template_path_edit.text()` |
| `roi_selector_run_list` | `self.run_list_edit.text()` |
| `roi_selector_use_template` | `self.template_cb.isChecked()` |

If the Developer finds more fields whose loss is user-visible, they
should add them to this table on the analysis branch (commit on
`analysis/new_workflow-repairs-2026-04` — not silently expand on the
feature branch).

## Preferred design (robust)

1. **Isolate the backing store.** Set explicit org/app names in
   `new_launcher.py:__main__` before any `QApplication` exists. On
   Linux this routes `new_launcher` settings to
   `~/.config/ORNL/lr_reduction_new_launcher.conf`, separate from
   whatever `launcher.py` writes to. The two binaries can coexist
   permanently without ever sharing keys.

   ```python
   if __name__ == "__main__":
       from qtpy import QtCore
       QtCore.QCoreApplication.setOrganizationName("ORNL")
       QtCore.QCoreApplication.setOrganizationDomain("ornl.gov")
       QtCore.QCoreApplication.setApplicationName("lr_reduction_new_launcher")
       app = QApplication([])
       window = ReductionInterface()
       window.show()
       sys.exit(app.exec_())
   ```

2. **Tab-local key namespaces.** Each tab prefixes its keys with the
   tab name (`direct_beam_*`, `roi_selector_*`, `overplot_*`,
   `template_*`). This prevents intra-launcher key collisions and
   makes `~/.config/ORNL/lr_reduction_new_launcher.conf` greppable.

3. **Defense in depth on save.** `save_settings()` runs on three
   triggers, in order of safety:
   - Every signal that mutates a tracked field (e.g.
     `editingFinished` for `QLineEdit`, `valueChanged` for
     `QDoubleSpinBox`, `toggled` for `QCheckBox`).
   - The tab's `closeEvent` (caught at the launcher level since tabs
     are children of the `QTabWidget`; wire via the parent's
     `closeEvent` calling each tab's `save_settings()`).
   - The dialog's `Ok` accepted signal (for `CdSettingsDialog` and
     `ModeratorDialog` — those persist their own values via the
     parent's `cd_vals` / `mod_vals` attribute, so the parent's save
     covers them).

4. **Defense in depth on read.** `read_settings()` always wraps
   per-key access in try/except with documented defaults. A corrupt
   value is logged via `logging.warning(...)` (or a `print(..., file=sys.stderr)`
   if no logger is configured) and the default is used — the launcher
   must never refuse to start because of a stale config file.

5. **No fallback to old keys.** If a user has stale settings under
   the old shared `~/.config/.conf` from a pre-fix run, those are
   simply ignored — the new conf file starts empty. No migration
   logic; the cost of writing migration is greater than the cost of
   one-time field re-entry. Document this in the commit message so
   the user knows.

## Failure-mode matrix

| Case | Expected behavior |
|---|---|
| First launch, no settings file | All fields show coded defaults; no crash |
| Settings file written by `launcher.py` (legacy `~/.config/.conf`) exists | Ignored — different org/app path. `new_launcher` still starts cleanly. |
| Corrupt setting (wrong type, e.g. `"abc"` for an int) | `read_settings()` catches the exception per-key, logs a warning, uses the default; other keys are loaded normally |
| Stale schema (key removed in code) | Unknown keys remain in the conf file, harmless; a future schema migration can prune them |
| User runs two `new_launcher` instances at once | Last close wins per key (acceptable; `QSettings` is per-process, no locking) |
| `closeEvent` does not fire (kill -9) | Field-level handlers already saved on every edit, so loss is bounded to whatever the user typed in the last unfocused field. Acceptable. |
| User cancels Cd or Moderator dialog | The parent's `cd_vals` / `mod_vals` attributes are unchanged; nothing is saved. The dialog itself does not call `save_settings`. |
| User clicks "Reset defaults" inside Cd dialog and `Ok`s | New (default) values flow back into the parent's `cd_vals` and get persisted on next save |
| Settings file's directory does not exist (first launch on a fresh user account) | `QSettings` creates `~/.config/ORNL/` automatically; nothing for us to do |

## Red-Green TDD seed

New test file `launcher/tests/test_settings_persistence.py`. The
guiding constraint is **no host-config contamination**: every test
sets up its own throwaway `QCoreApplication` org/app via
`monkeypatch`/fixtures so the developer's actual
`~/.config/ORNL/lr_reduction_new_launcher.conf` is never touched.

```python
# conftest.py addition
import pytest
from qtpy import QtCore, QtWidgets

@pytest.fixture
def isolated_qapp(tmp_path, monkeypatch):
    """Fresh QApplication with throwaway QSettings backing.

    Uses an isolated org/app so the test never reads or writes the
    user's real new_launcher config.
    """
    QtCore.QCoreApplication.setOrganizationName(f"test-org-{tmp_path.name}")
    QtCore.QCoreApplication.setOrganizationDomain("example.test")
    QtCore.QCoreApplication.setApplicationName(f"test-app-{tmp_path.name}")
    # Redirect QSettings to tmp_path so we don't even touch ~/.config
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    if QtWidgets.QApplication.instance() is None:
        app = QtWidgets.QApplication([])
    else:
        app = QtWidgets.QApplication.instance()
    yield app
```

```python
# test 1 — RED first: DirectBeamTab restores ipts after save+rebuild
def test_direct_beam_ipts_persists(isolated_qapp):
    tab = DirectBeamTab()
    tab.ipts_edit.setText("36776")
    tab.save_settings()
    tab.deleteLater()
    tab2 = DirectBeamTab()
    assert tab2.ipts_edit.text() == "36776"

# test 2 — RED first: cd_vals round-trip as structured JSON
def test_direct_beam_cd_vals_round_trip(isolated_qapp):
    tab = DirectBeamTab()
    tab.cd_vals = {"mu_file": "/x/y", "Cd": [5.0, 126.5, 249.5, 499.0],
                   "flip_atten": True}
    tab.save_settings()
    tab.deleteLater()
    tab2 = DirectBeamTab()
    assert tab2.cd_vals == {"mu_file": "/x/y", "Cd": [5.0, 126.5, 249.5, 499.0],
                             "flip_atten": True}

# test 3 — RED first: corrupt JSON in cd_vals is tolerated
def test_direct_beam_corrupt_cd_vals_tolerated(isolated_qapp):
    s = QtCore.QSettings()
    s.setValue("direct_beam_cd_vals", "not valid json {{")
    s.sync()
    tab = DirectBeamTab()  # must not raise
    assert isinstance(tab.cd_vals, dict)  # default empty dict

# test 4 — RED first: Overplot saves the ytransform key
def test_overplot_saves_ytransform(isolated_qapp):
    tab = Overplot()
    tab.ytransform_combo.setCurrentText("R*Q^4")
    tab.save_settings()
    s = QtCore.QSettings()
    assert s.value("overplot_ytransform") == "R*Q^4"

# test 5 — RED first: ROISelector ipts persists
def test_roi_selector_ipts_persists(isolated_qapp):
    tab = ROISelector()
    tab.ipts_edit.setText("36776")
    tab.save_settings()
    tab.deleteLater()
    tab2 = ROISelector()
    assert tab2.ipts_edit.text() == "36776"

# test 6 — Org/app names route to a separate file vs bare QSettings
def test_isolation_from_legacy_launcher(isolated_qapp, tmp_path):
    # write under bare QSettings (legacy launcher behavior)
    bare = QtCore.QSettings()
    bare.setValue("any_key", "legacy_value")
    bare.sync()
    # confirm new_launcher's settings file is a *different* file path
    QtCore.QCoreApplication.setOrganizationName("ORNL")
    QtCore.QCoreApplication.setApplicationName("lr_reduction_new_launcher")
    new = QtCore.QSettings()
    assert new.fileName() != bare.fileName()

# test 7 — first-launch defaults (no QSettings keys) leave widgets at code defaults
def test_direct_beam_first_launch_defaults(isolated_qapp):
    tab = DirectBeamTab()
    assert tab.ipts_edit.text() == ""  # or whatever the code default is
```

## Acceptance

1. All 7 tests in `launcher/tests/test_settings_persistence.py` pass.
2. `pixi run test-reduction` (or `test-launcher` if added) — no
   regressions.
3. Manual: launch `new_launcher`, fill in IPTS / paths in the Direct
   Beam tab, close, relaunch — all values restored.
4. Manual: confirm `~/.config/ORNL/lr_reduction_new_launcher.conf`
   exists and contains `direct_beam_*` / `roi_selector_*` /
   `overplot_*` keys; the legacy `~/.config/.conf` is unchanged by
   `new_launcher`'s saves.
5. The `launcher.py` (legacy) launcher continues to work as before.

## Notes for the Integrator

- The new `launcher/tests/` directory must be collected by pytest. See
  the same note in `overplot-axes-plan.md` — a single `testpaths`
  widening serves both.
- Tests use `monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))` to
  avoid touching the developer's real `~/.config/`.
- Headless Qt: `QT_QPA_PLATFORM=offscreen` in the test env (set in
  `conftest.py`).

## Cross-references

- `launcher/apps/template_batch.py:352-396` — reference implementation
  of the save/read pattern.
- `~/.claude/CLAUDE.md` `[ALWAYS] Design framing` — robust default;
  detection complete (every tab has save/read), auto-resolution
  minimal (no migration of legacy keys; document and move on).
- `overplot-axes-plan.md` — the `Plot mode` selector this plan adds
  also gets persisted via the `overplot_*` namespace established
  here (key `overplot_mode`).
- `cd-dialog-resize-plan.md` — the dialog refactor leaves
  `CdSettingsDialog`/`ModeratorDialog` parents unchanged, so the
  `direct_beam_cd_vals` / `direct_beam_mod_vals` round-trip flow is
  not affected.
