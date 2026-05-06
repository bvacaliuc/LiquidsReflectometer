# Plan: cd-dialog-resize — Cd settings dialog too narrow

**Slug:** `cd-dialog-resize`
**Effort:** `new_workflow-repairs-2026-04`
**Base branch:** `new_workflow_ui_plan`
**Plan revision:** v1 (initial)

## Symptom

Opening the **Cd settings** dialog from the Direct Beam tab shows a
dialog whose `Cd (comma separated):` `QLineEdit` is too narrow to
display its contents. A typical value (e.g. `5,126.5,249.5,499.0`)
overflows; the user must arrow-key through the field to see all four
floats. The companion **Moderator settings** dialog has the same
underlying structural defect and is at risk of the same symptom for
sufficiently long `Chop2_cut_fn` or `t0` values.

## Verified root cause

Two compounding defects in `launcher/apps/direct_beam.py`:

1. **Structural hack: `QMessageBox` masquerading as `QDialog`.**
   - `class CdSettingsDialog(QMessageBox)` at
     `launcher/apps/direct_beam.py:53-129` (issues.md hypothesis cited
     `52-126`; current line is `53-129`, drift +1, root cause unchanged).
     Inside `__init__`, the class does `self.dlg = QDialog(parent)` and
     builds the entire UI on `self.dlg`. The outer `QMessageBox` is
     constructed but never displayed. `exec_` and `get_values` proxy
     through `self.dlg`. This is dead inheritance and complicates
     sizing because the *visible* widget (`self.dlg`) is never the
     thing whose size hint Qt's layout system normally tunes.
   - `class ModeratorDialog(QMessageBox)` at
     `launcher/apps/direct_beam.py:132-203` (cited 129-198, drift +3) —
     same hack, same risk.

2. **No minimum width set on the inner `QLineEdit`s.** Without
   `setMinimumWidth`, Qt's `QFormLayout` sizes the field to its
   default size hint (`~60px`), which is far too narrow for
   comma-separated float lists.

For comparison, `roi_selector.py:292` already uses the right idiom:
`self.template_path_edit.setMinimumWidth(300)`. The same idiom applied
inside the Cd / Moderator dialogs would have prevented the symptom
even before the structural refactor.

## Files to change

| File | Lines | Change |
|---|---|---|
| `launcher/apps/direct_beam.py` | 53-129 (`CdSettingsDialog`) | Replace `class CdSettingsDialog(QMessageBox):` with `class CdSettingsDialog(QDialog):`. Drop the inner `self.dlg = QDialog(parent)` indirection — install widgets directly on `self`. Remove the `exec_` proxy (the inherited `QDialog.exec_` works). Update `get_values` to remain a public method, no proxy needed. |
| `launcher/apps/direct_beam.py` | 132-203 (`ModeratorDialog`) | Same refactor: inherit from `QDialog`, drop `self.dlg`. |
| `launcher/apps/direct_beam.py` | 64-67 (Cd widget construction) and the equivalent in `ModeratorDialog` | Add `self.cd_edit.setMinimumWidth(320)` (and the same on Moderator's `chop2_edit` and `t0_edit`). 320px comfortably fits `5, 126.5, 249.5, 499.0` plus margin; QFormLayout will pull the dialog wider as needed. |
| `launcher/apps/direct_beam.py` (callers of the dialog classes) | wherever the parent calls `CdSettingsDialog(...)` / `ModeratorDialog(...)` | Audit — any call that does `dlg.dlg.show()` or accesses `.dlg` directly must be reverted to operating on the dialog itself. Likely none after the refactor (the proxy was internal), but double-check. |
| `launcher/apps/direct_beam.py` | top imports | Move `from qtpy.QtWidgets import QDialog, QDialogButtonBox` from the inline-inside-`__init__` imports to the module-level import block, alongside the other Qt imports. Fixes a minor smell while the file is open. |
| `launcher/tests/test_cd_dialog_resize.py` | (new) | Unit tests per the TDD seed below. |

### Net LoC

The refactor is **net negative** — removing `self.dlg = QDialog(parent)`,
the wrapper layout indirection, the `exec_` and `get_values` proxies
saves ~6 lines per dialog. The only addition is the
`setMinimumWidth` calls.

## Preferred design (robust)

1. **Inherit from the right base class.** `QDialog` is the canonical
   base for a parented modal/non-modal dialog with `Ok`/`Cancel`. The
   `QMessageBox` lineage was a structural mistake — `QMessageBox` is a
   specialized subclass for short questions/confirmations, not a
   container for arbitrary form layouts. Using `QDialog` directly
   removes the `self.dlg` indirection and lets Qt's size-hint
   propagation work correctly.

2. **Constrain the input field, not the dialog.** Setting a minimum
   width on the dialog (`self.setMinimumWidth(480)`) is the simple
   variant; setting it on the `QLineEdit`s lets the dialog auto-grow
   to fit longer strings *or* stay compact when the user shrinks the
   widgets. Prefer the latter — the dialog adapts to its data, not to
   a hardcoded outer size. (This is the "robust over simple"
   distinction: the simple variant works for the screenshot in the
   bug report; the robust variant works for any future dialog
   content.)

3. **Preserve parent-passing.** Both dialogs accept `parent=None` and
   forward it to the inner `QDialog` today. After the refactor, pass
   `parent` straight to `QDialog.__init__` via `super().__init__(parent)`
   so the dialog still centers over its parent and inherits the
   correct window flags.

4. **Preserve modal exec_ semantics.** The existing flow is
   `dlg.exec_()` returning `QDialog.Accepted` / `Rejected`. After
   inheriting from `QDialog`, that flow is preserved automatically
   — the inherited `exec_` does the right thing.

5. **Preserve `get_values()` behavior exactly.** No changes to its
   parsing of `mu_file`, `Cd`, `flip_atten` (or `Chop2_cut_fn`,
   `dMod`, `t0`). The existing `parse_list` lambda inside
   `get_values()` stays as-is — it's a small inner function and
   re-extracting it is unnecessary churn for a sizing fix.

6. **No changes to dialog look-and-feel.** Same field labels, same
   button positions, same `Reset defaults` button on the left of the
   `QDialogButtonBox`. The user should not notice anything except
   that the field now shows its full content.

## Failure-mode matrix

| Case | Expected behavior |
|---|---|
| Empty `Cd` list | Dialog opens at minimum width (~480px implicit from form labels + 320px field); `cd_edit` is empty; no crash |
| Long `Cd` list (e.g. 20 floats, ~200 chars) | `QLineEdit`'s internal horizontal scroll handles overflow; the dialog does not balloon to 2000px wide. The field's minimum width (320px) is enough to show 4-5 typical floats; longer values scroll within the field via standard `QLineEdit` cursor navigation. |
| `Cd` containing characters that don't parse as float | `parse_list` already filters silently; `get_values` returns the parsed-clean list. No regression — same behavior as today. |
| Parent window is on a small display (e.g. 1024×768) | Qt's window manager respects screen size; dialog opens within the available area and is user-resizable via corner drag (default `QDialog` behavior). |
| User resizes dialog by corner drag | Honored; minimum width on the `QLineEdit` keeps the field at least 320px even if the user tries to drag narrower. |
| `Reset defaults` clicked | Same as today — `_reset_defaults` rewrites widget contents from `_initial_defaults`. The widgets are now first-class `self.*` attributes (no `self.dlg` proxy), but the content semantics are unchanged. |
| Cancel pressed | Dialog rejects via `QDialogButtonBox.Cancel` → `self.reject()` (inherited from `QDialog`). The parent's `cd_vals` / `mod_vals` are unchanged. |
| Ok pressed | Dialog accepts; parent reads via `dlg.get_values()`. Parent persists via `direct_beam_cd_vals` / `direct_beam_mod_vals` per `settings-persistence-plan.md`. |
| Existing callers reference `dlg.dlg.show()` | Audit step in §"Files to change" catches this; expected to be zero callers after read-through, but the test (below) covers the contract. |

## Red-Green TDD seed

New test file `launcher/tests/test_cd_dialog_resize.py`. Reuses
`isolated_qapp` fixture from `settings-persistence-plan.md`'s
conftest. No `pytest-qt` required — operations are size queries on
constructed (not necessarily shown) widgets.

```python
# test 1 — RED first: CdSettingsDialog is a QDialog (not a QMessageBox)
def test_cd_dialog_is_qdialog(isolated_qapp):
    from launcher.apps.direct_beam import CdSettingsDialog
    dlg = CdSettingsDialog()
    from qtpy.QtWidgets import QDialog, QMessageBox
    assert isinstance(dlg, QDialog)
    assert not isinstance(dlg, QMessageBox)

# test 2 — RED first: cd_edit's minimum width fits a 4-float list
def test_cd_edit_minimum_width(isolated_qapp):
    from launcher.apps.direct_beam import CdSettingsDialog
    dlg = CdSettingsDialog(defaults={"mu_file": "",
                                       "Cd": [5, 126.5, 249.5, 499.0],
                                       "flip_atten": False})
    # Without showing, the minimum width should be set on the widget itself.
    assert dlg.cd_edit.minimumWidth() >= 320

# test 3 — RED first: dialog's effective size hint is wide enough to show
#                       "5, 126.5, 249.5, 499.0"
def test_cd_dialog_size_hint(isolated_qapp):
    from launcher.apps.direct_beam import CdSettingsDialog
    dlg = CdSettingsDialog(defaults={"mu_file": "/x/y",
                                      "Cd": [5, 126.5, 249.5, 499.0],
                                      "flip_atten": False})
    fm = dlg.cd_edit.fontMetrics()
    needed = fm.horizontalAdvance("5, 126.5, 249.5, 499.0") + 16  # padding
    # Dialog's sizeHint width should comfortably exceed 'needed'.
    assert dlg.sizeHint().width() >= needed

# test 4 — RED first: ModeratorDialog also a QDialog
def test_moderator_dialog_is_qdialog(isolated_qapp):
    from launcher.apps.direct_beam import ModeratorDialog
    dlg = ModeratorDialog()
    from qtpy.QtWidgets import QDialog, QMessageBox
    assert isinstance(dlg, QDialog)
    assert not isinstance(dlg, QMessageBox)

# test 5 — get_values round-trips after Cd refactor
def test_get_values_round_trip(isolated_qapp):
    from launcher.apps.direct_beam import CdSettingsDialog
    dlg = CdSettingsDialog(defaults={"mu_file": "/x/y",
                                      "Cd": [5, 126.5, 249.5, 499.0],
                                      "flip_atten": True})
    vals = dlg.get_values()
    assert vals["mu_file"] == "/x/y"
    assert vals["Cd"] == [5.0, 126.5, 249.5, 499.0]
    assert vals["flip_atten"] is True

# test 6 — Reset defaults restores initial values, not current working defaults
def test_reset_defaults(isolated_qapp):
    from launcher.apps.direct_beam import CdSettingsDialog
    initial = {"mu_file": "/initial", "Cd": [1.0], "flip_atten": False}
    working = {"mu_file": "/working", "Cd": [9.0], "flip_atten": True}
    dlg = CdSettingsDialog(defaults=working, initial_defaults=initial)
    dlg._reset_defaults()
    vals = dlg.get_values()
    assert vals["mu_file"] == "/initial"
    assert vals["Cd"] == [1.0]
    assert vals["flip_atten"] is False
```

## Acceptance

1. All 6 tests pass with `pixi run test-reduction` (or
   `test-launcher`).
2. Manual: open Direct Beam tab → click whatever button surfaces the
   Cd settings dialog. The `Cd (comma separated):` field shows the
   full default text without horizontal scrolling. Same check for the
   Moderator settings dialog with a long `t0` value.
3. The dialog still centers over its parent (Direct Beam tab),
   accepts on Ok, rejects on Cancel, and `get_values()` returns the
   parsed dict.
4. `pixi run test-reduction` — no regressions in the existing 281
   tests.

## Notes for the Integrator

- Headless Qt (`QT_QPA_PLATFORM=offscreen`) is sufficient for these
  tests — none rely on the dialog being actually shown on screen.
  `dlg.sizeHint()` and widget `minimumWidth()` queries work without
  `dlg.show()`.
- `pytest-qt` is not added by this plan. Same conftest as the other
  three plans.
- The audit step (callers of `.dlg.*`) is mechanical — `grep -rn
  '\.dlg\.' launcher/` from the lr_reduction root. Expected output:
  zero matches outside `launcher/apps/direct_beam.py` itself.

## Cross-references

- `launcher/apps/roi_selector.py:292` — reference for `setMinimumWidth`
  idiom on a `QLineEdit` inside a `QFormLayout`.
- `~/.claude/CLAUDE.md` `[ALWAYS] Design framing` — robust over
  simple: constrain the input field (data-driven width) rather than
  the dialog (hardcoded width).
- `settings-persistence-plan.md` — `direct_beam_cd_vals` /
  `direct_beam_mod_vals` are the persistence shape; the refactor
  here does not change `get_values()`'s return so persistence is
  unaffected.
- `build-versioningit-tag-glob-plan.md` — the systemic build fix
  this slug's v2 cycle pulls in defensively (see Revision history
  below).

## Revision history

### v2 — surface a systemic build blocker; add the build fix locally

**Cycle that triggered this revision.** Integrator cycle 1 on
`feature/cd-dialog-resize` at SHA
`f4e057fdaeadd10949ccb2ca3fdc053704b5729c` (review tag
`review/cd-dialog-resize`). The Integrator's `todo.md` reports an
**infrastructure failure**, not a code-test failure: `pixi run
test-reduction` exits during environment preparation, before any
test is collected, with:

```
versioningit.errors.InvalidVersionError: Error getting the version
from source `versioningit`: Cannot parse version 'qa/cd-dialog-resize'
```

**Why this is not a v1 plan defect.** The v1 dialog-refactor TDD
seed and the GREEN commit `78ea717 cd-dialog-resize: GREEN —
Cd/Moderator dialogs inherit QDialog directly` are both correct. The
build never got far enough to run the new tests. The blocker is the
`pyproject.toml`'s `[tool.versioningit.vcs]` block having no `match`
glob, so `git describe --tags HEAD` returns the protocol's
lightweight `qa/cd-dialog-resize` tag and versioningit's parser
rejects it as not PEP 440-compliant.

**Action for the Developer at v2.** Two cumulative changes on
`feature/cd-dialog-resize`:

1. **Defensive build-fix patch** (new). Apply the same one-line
   `pyproject.toml` patch described in
   `plans/build-versioningit-tag-glob-plan.md`:

   ```toml
   [tool.versioningit.vcs]
   method = "git"
   default-tag = "0.0.1"
   match = ["v[0-9]*"]      # NEW LINE — added at v2
   ```

   Commit it as a separate commit so its history is greppable:
   `cd-dialog-resize v2: defensive pyproject build-fix (mirrors build-versioningit-tag-glob)`.
   This unblocks `cd-dialog-resize`'s qa cycle independently of when
   the standalone `feature/build-versioningit-tag-glob` PR is
   merged. Intentional duplication — when both PRs eventually merge,
   the cd-dialog-resize PR's pyproject change is a no-op against
   the fixed base.

2. **Empty-commit advance is NOT used here.** The v1 dialog test
   body is unchanged in v2 — but the *implementation* needs the
   defensive build-fix patch on top, so a real (non-empty) commit
   advances the feature SHA. Do **not** issue a
   `git commit --allow-empty` per dry-run Developer findings §3.4 —
   the build-fix patch is a real change.

**Rejection cause cited (per orchestration.md §6 Analyst loop, "amend
plan file ... citing the rejection cause"):** `qa/cd-dialog-resize`
tag at SHA `78ea717` is consumed by versioningit's default
`git describe --tags` invocation; the missing `match = ["v[0-9]*"]`
filter in `[tool.versioningit.vcs]` causes the editable install to
abort with `InvalidVersionError`. See the Integrator's todo.md on
`feature/cd-dialog-resize` SHA `f4e057f` for the full ranked-
hypothesis evidence.

**Acceptance addition for v2.** All v1 acceptance criteria still
apply (6 dialog tests pass; manual visual confirmation; no
regressions). Add:

5. The two new tests in `tests/test_versioningit_config.py` (per
   `plans/build-versioningit-tag-glob-plan.md`) pass on
   `feature/cd-dialog-resize` too. Yes — duplicate test coverage is
   fine; both PRs run them, and when both merge, the test only
   exists once on `{base-branch}`.

**Cross-project learning to capture (post-merge by Developer).**
When the Developer ships v2, add `plans/cd-dialog-resize-learning.md`
with:

> **Rule.** versioningit's default tag-glob accepts every reachable
> tag, including protocol-internal lightweight tags
> (`qa/*`, `review/*`, `triage/*`, `analysis/*`).
>
> **Why.** The default `git describe --tags HEAD` invocation has no
> `--match` filter, so any non-PEP-440 tag at HEAD breaks
> `hatchling.build.build_editable`. Found on cycle 1 of
> `cd-dialog-resize` 2026-05-05; cost the orchestration one full
> Developer→Integrator→Analyst retry cycle.
>
> **How to apply.** Any project using versioningit + this
> orchestration MUST set `[tool.versioningit.vcs] match = ["v[0-9]*"]`
> (or equivalent positive allow-list) before running the protocol.
> Add this check to the Initialization agent's §11 (Target-branch
> dependency verification) for future efforts.

The third paragraph above ("How to apply") is also a candidate for
inclusion in `plan/initialization.md` §11 in the `tasking` repo, so
future efforts catch the issue at session-start instead of at
runtime. That's a separate change in the `tasking` repo and is the
user's call.
