# Plan: port-cd-dialog-resize (S1)

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` (S0 harness merged,
PR #15) · charter §3 PR #8 disposition ("port, near-mechanical") · seed
`agentic/feature/cd-dialog-resize` @ `ebbd689`
**Retry attempt:** 1

Review domains: test-reviewer (advisory), ui-aspects-reviewer (advisory —
dialog lifecycle).

## Symptom

`launcher/apps/direct_beam.py` on `exp` still carries the
QMessageBox-wrapping-QDialog hack: `CdSettingsDialog(QMessageBox)` (line 52)
and `ModeratorDialog(QMessageBox)` (line 129) each build an inner
`self.dlg = QDialog(parent)` plus an `exec_()` forwarding shim (lines
112–113, 184–185). Because the visible widget is the inner QDialog, the
dialogs cannot be resized properly and the Cd list field truncates typical
content ("5, 126.5, 249.5, 499.0"). PR #8 on the retired `ui_plan` lineage
fixed this and cannot merge into `exp` (charter §3); porting is the route.

## Verified state (against `agentic/exp` @ `a4ae8b8`, 2026-08-18)

- Both hack classes live at the cited lines; call sites unchanged:
  `_open_cd_settings`/`_open_mod_settings` use `if dlg.exec_() == 1:`
  (lines 355/363) — `QDialog.exec_()` returns `1` for Accepted, so call
  sites need no change after the port.
- `exp`'s file is post-lint (PR #14): string quotes differ from the PoC
  branch (`'Flip attenuator mapping'` vs `"…"`). **Re-apply the change
  semantically; do not apply raw PR hunks** — they will not apply and would
  regress lint style.
- The PR's own diff is `git diff 3b599c7..agentic/feature/cd-dialog-resize`
  (merge-base with `ui_plan` — all four PoC port branches share `3b599c7`).
  Fetch: `git fetch agentic refs/heads/feature/cd-dialog-resize`.
- S0's harness is on the base: `launcher/tests/{__init__,conftest}.py` with
  `isolated_qapp` + `no_qmessagebox`, `test-launcher` pixi task with
  `--timeout=120 --timeout-method=thread`.

## Files to change (on `feature/port-cd-dialog-resize` from `agentic/exp`)

1. `launcher/apps/direct_beam.py` — the PR #8 semantic change, adapted:
   - `CdSettingsDialog(QMessageBox)` → `CdSettingsDialog(QDialog)`: drop the
     inner `self.dlg`, parent widgets to `self`, wire
     `buttons.accepted/rejected` to `self.accept/self.reject`, drop the
     `exec_` shim; `self.cd_edit.setMinimumWidth(320)`.
   - `ModeratorDialog(QMessageBox)` → `(QDialog)` identically;
     `chop2_edit`/`t0_edit` get `setMinimumWidth(320)`.
   - Top-of-file import block gains `QDialog`, `QDialogButtonBox` (keep the
     sorted order — ruff isort is enforced); `QMessageBox` **stays** imported
     (other call sites in the file still use it).
2. `launcher/tests/test_cd_dialog_resize.py` — new; the PR's six tests with
   two adaptations: imports become `from launcher.apps.direct_beam import …`
   (exp's absolute-package convention — the PoC's `from apps.…` will not
   resolve), and every test gets
   `@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")` (marks, not
   fixture args — `ARG001` fires on unused fixture params under exp's ruff).
   Test list: `test_cd_dialog_is_qdialog`, `test_cd_edit_minimum_width`,
   `test_cd_dialog_size_hint`, `test_moderator_dialog_is_qdialog`,
   `test_get_values_round_trip`, `test_reset_defaults`.

**Strip list (charter §3 — do NOT port):** `todo.md` (PoC Integrator
archaeology), `pixi.lock` hunks, the `pyproject.toml` hunk (versioningit
glob and `test-launcher` task are already on `exp` — S0's task definition
with `--timeout-method=thread` supersedes the PR's), and
`launcher/tests/{__init__,conftest}.py` (landed by S0 — the PR's conftest
lacks `no_qmessagebox`; never overwrite S0's).

**pixi.lock caveat (until the format decision lands):** this slug adds no
dependencies — there is no legitimate `pixi.lock` diff. The `pixi-lock-check`
pre-push hook on this machine (pixi 0.70.1) rewrites the lock to format v7
as a side effect and exits 0. If `git status` shows `pixi.lock` modified at
any point: `git checkout -- pixi.lock`, and never commit a lock whose first
line is not `version: 6` (analysis.sns.gov pixi cannot read v7).

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Raw PR hunks applied over post-lint file (common) | patch rejects / ruff hook fails | semantic re-apply rule above |
| PoC import path `apps.…` kept (common) | ImportError at collection | `launcher.apps.…` adaptation; RED run catches |
| A dialog test opens a real modal (edge) | `--timeout-method=thread` kills at 120 s with stack | `no_qmessagebox` on every test (prevention) + S0 backstop |
| `QMessageBox` import dropped as "unused" (edge) | ruff F821 at other call sites / NameError at runtime | keep-import note above; seal-checked |
| Call sites break without the `exec_` shim (edge) | `test_get_values_round_trip` exercises the accept path | verified: `QDialog.exec_() == 1` protocol identical |
| `pixi.lock` v7 rewrite staged (edge, this machine) | first line ≠ `version: 6` | caveat above — restore, never commit |

## Red-Green seed

- RED: add `launcher/tests/test_cd_dialog_resize.py` (adapted imports +
  fixtures) BEFORE touching `direct_beam.py`; `pixi run test-launcher` —
  `test_cd_dialog_is_qdialog`, `test_moderator_dialog_is_qdialog`,
  `test_cd_edit_minimum_width`, `test_cd_dialog_size_hint` fail (the classes
  are QMessageBox-wrapped; no `minimumWidth`); commit body enumerates the
  failures.
- GREEN: apply the `direct_beam.py` change; `pixi run test-launcher` green
  (harness tests + these six); `pixi run test-reduction` green.

## Acceptance criteria

- `pixi run test-launcher` green: S0's two harness tests + these six.
- `pixi run test-reduction` green (107 tests, chained via `depends-on`).
- Pre-commit clean; diff touches exactly `launcher/apps/direct_beam.py` +
  `launcher/tests/test_cd_dialog_resize.py`; `pixi.lock` untouched
  (`version: 6` preserved).
- After the draft PR: charter §3 disposition — the human closes PR #8 as
  "superseded by exp port" (record the note in the PR body).
