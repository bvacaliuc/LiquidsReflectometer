# Plan: settings-editor (T2)

**Campaign:** `exp-settings-roi` · base `exp` @ `308a020` (S0–S3 + harness +
protective slugs all merged) · charter §4 slug T2 · **full design in
`tasking/plan/settings-editor/plan.md` (511 ln) — this slug plan verifies it
against the current tip, sets the campaign mechanics, and does NOT duplicate
the field-by-field design**
**Retry attempt:** 1

Review domains (charter §5, task-plan §9): **ui-aspects-reviewer (blocking**
— the angle-table ⇄ hidden-state trap, the campaign's active-row-as-hidden-
input bug class), **test-reviewer (blocking)**, design-reviewer (advisory —
FIELD_SPEC vs organic widget growth), security-review (advisory — writes into
facility-consumed settings paths).

## Symptom / the ask

`exp` has **no settings-editor tab**: `new_launcher.py:4` carries a
commented-out `JSONSettingsBuilderTab` import for a module that never existed
(`git log --all -S json_settings_builder` → only the comment). Scientists have
no guided way to author/edit the new-workflow reduction settings JSON. The ask
(human, 2026-07-02): a tab that seeds from a **pre-reduced `.dat` header** or a
**prior JSON**, **guides** the user through available options and formats, and
supports **adding angles**.

## Verified state (against `agentic/exp` @ `308a020`, 2026-09-06)

- **Clean landing:** no `settings_document`, `field_spec`, or
  `settings_editor` anywhere in `src/lr_reduction/` or `launcher/apps/`.
- **Data model intact:** `NRReductionConfig`
  (`src/lr_reduction/nr_reduction_config.py`) is a flat, un-validated
  attribute bag; `json_to_config` (`new_reduction_from_file.py:441`) `setattr`s
  each key and **raises `AttributeError` on any unknown key** (`:449`) — so
  FIELD_SPEC must be a **superset-safe** mirror of the real attribute names
  (an unknown key is a hard failure at load, not a warning).
- **Seed present:** `agentic/new_workflow_ui_plan:launcher/apps/template_reduce.py`
  (751 ln) + `reduction_worker.py` — the confirmed seed GUI; fetch that ref
  (`git fetch agentic refs/heads/new_workflow_ui_plan`). Reuse its scalar
  group-box layout + validators; **strip** its reduction-execution worker
  (T2 authors settings, it does not run reductions).
- **Identity contract wired:** `new_launcher.py:7` already imports
  `ensure_identity, migrate_legacy_settings` from `launcher.app_identity`
  (S3). Per charter §3 scope note + the S3 plan's adoption contract, **T2's
  tab MUST call `ensure_identity()` first in its `__init__`** and use the
  shared `ORG_NAME`/`APP_NAME` store — all layers share one QSettings.
- **Harness available:** the launcher-tests fixtures are on exp —
  `isolated_qapp`, `no_qmessagebox`, and autouse `no_qfiledialog`
  (harness-hardening), with the `--timeout-method=thread` backstop. GUI tests
  use them; a modal without `no_qmessagebox` is the 10-hour-orphan class.

## Architecture (from the design doc — the three pieces)

1. **`SettingsDocument`** — `src/lr_reduction/settings_document.py`,
   **Qt-free** (no `qtpy`/`PyQt` import — this is the seam that makes RED/GREEN
   cheap and is T3's foundation). Wraps one `NRReductionConfig` + edit ops:
   load (from JSON / `.dat` header / defaults), validate, normalize, add/remove
   angle (keeps the parallel per-angle arrays length-consistent — nothing does
   today), diff-vs-seed.
2. **`FIELD_SPEC`** — a declarative table beside `SettingsDocument`:
   `{name, group, type, default, allowed/range, per_angle, runtime_owned, help}`
   for **every** field in task-plan §2.1. One source of truth driving widget
   construction, tooltip/status help ("the prompts the user asked for"),
   validation messages, and the normalization list. **Every `name` must be a
   real `NRReductionConfig` attribute** (guard test below) or `json_to_config`
   raises at load.
3. **`SettingsEditorTab`** — `launcher/apps/settings_editor.py`, a **thin view**
   over `SettingsDocument`: angle table, scalar group boxes, per-field prompt
   pane, changed-vs-seed report. Added to `new_launcher.py` via `addTab`.

## The two traps this slug MUST design against (measured, not assumed)

- **Angle-table active-row-as-hidden-input (ui-aspects blocking class).** The
  known reduction-GUI bug: per-row config read from the *currently-selected*
  row instead of the row being acted on. `SettingsDocument.add_angle` /
  `remove_angle` / per-row edits operate on an **explicit row index**, never
  `table.currentRow()`; the view passes the index. Pin with a test that
  edits row 0's field while row 2 is selected and asserts row 0 changed.
- **Widget-wiring prescribed from measured event dispatch, not intent** (the
  campaign's signature defect — S2-v2's double-toggle, harness-v1/2's
  stated-vs-measured). Any signal→slot the plan prescribes (table
  `cellChanged`, add-angle button, seed-combo change) must be verified by a
  `QTest`-level probe in the tests, not asserted by `.emit()`. Do not
  prescribe a `currentRow`-dependent handler.

## Red-Green seed (model first — the cheap TDD the Qt-free seam buys)

1. **`SettingsDocument` + `FIELD_SPEC`, Qt-free, RED first**
   (`tests/unit/lr_reduction/test_settings_document.py`): load a JSON seed →
   round-trips to an equal JSON; load a `.dat` header seed → populates the
   documented fields; `add_angle` grows **all** per-angle arrays by one and
   keeps them equal-length; validate rejects an out-of-range/unknown-`method`
   value with a FIELD_SPEC-sourced message; normalize drops runtime-owned
   keys; **`FIELD_SPEC` name-coverage guard**: every `FIELD_SPEC.name` is a
   real `NRReductionConfig` attribute AND `json_to_config` accepts the
   normalized output (no `AttributeError`). These need no Qt and run in ms.
2. **`SettingsEditorTab` view, RED then GREEN**
   (`launcher/tests/test_settings_editor.py`, `usefixtures` the harness
   fixtures): tab constructs under `isolated_qapp`; a real `QTest` edit of a
   scalar writes through to the document; add-angle button appends a table row
   AND a document angle; the row-index isolation test above; seed-from-file
   uses the autouse `no_qfiledialog`. No modal escapes (`no_qmessagebox`).

## Failure-mode matrix (campaign-critical rows; full matrix in the design doc)

| Case | Detection | Handling |
|---|---|---|
| FIELD_SPEC names a non-attribute → `AttributeError` at load (common) | name-coverage guard test | FIELD_SPEC is a superset-safe mirror; guard is RED-first |
| Angle arrays drift out of length on add/remove (common) | `add_angle` equal-length assert | single `add_angle` op mutates all arrays atomically |
| Active-row hidden input (ui-aspects blocking) | edit-row-0-while-row-2-selected test | explicit row index, never `currentRow()` |
| Signal wired from intent, mis-dispatches (signature class) | `QTest` probe, not `.emit()` | measured-dispatch rule above |
| Modal in a GUI test hangs offscreen Qt | thread-timeout backstop | `no_qmessagebox`; the harness exists for this |
| Settings store split from the other tabs | identity test (shared file) | `ensure_identity()` first in `__init__` (S3 contract) |
| Qt import creeps into `SettingsDocument` | `grep -L qtpy` guard / import test | model stays Qt-free — T3 depends on it |
| pixi.lock re-stamp | first line ≠ `version: 6` | amendment 14: restore |

## Acceptance criteria

- `SettingsDocument`/`FIELD_SPEC` Qt-free (no qtpy import — enforced by a
  test); model tests green and fast; the FIELD_SPEC name-coverage guard green
  (round-trips through `json_to_config` with no `AttributeError`).
- `SettingsEditorTab` green under the harness fixtures incl. the row-index
  isolation test and at least one `QTest`-measured signal path; tab added to
  `new_launcher.py`; `ensure_identity()` called first in `__init__`.
- `pixi run test-launcher` + `test-reduction` green; pre-commit clean; no
  `pixi.lock` change.
- Draft PR body: deploy consequence (charter §7); the **T3 downstream
  contract** — `settings-management` (T3) reuses `SettingsDocument` +
  `FIELD_SPEC` as its foundation (design doc §1), so their public shape is an
  interface T3 depends on; supersedes the never-existent `JSONSettingsBuilderTab`.

## Downstream (charter DAG)

T2 **gates T3** (`settings-management`): T3's `SettingsResolver` and the (a)→(f)
resolution stack consume this slug's `SettingsDocument`/`FIELD_SPEC`. T3 stages
only after T2's draft PR merges (same pattern as S0→S1–S3). T1-A1 follows T3.
