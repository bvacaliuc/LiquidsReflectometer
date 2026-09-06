# Plan: settings-editor (T2)

**Campaign:** `exp-settings-roi` · base `exp` @ `308a020` (S0–S3 + harness +
protective slugs all merged) · charter §4 slug T2
**Retry attempt:** 1

> **Authoritative field source is IN THIS REPO, not out-of-tree.** FIELD_SPEC
> mirrors the attributes of `src/lr_reduction/nr_reduction_config.py` — which
> the feature-branch checkout HAS. A prior draft of this plan pointed the
> Developer at `tasking/plan/settings-editor/plan.md` for the field list;
> that doc lives in a **sibling submodule of the super-repo, unreachable from
> the `lr_reduction` feature branch**, and the contract makes the triage-tip
> plan + git log the complete brief (repo rule: no out-of-tree references in
> committed docs). Corrected here (fork pre-review, 2026-09-06): the
> load-bearing per-angle set is inlined below; read `nr_reduction_config.py`
> in the checkout for the complete attribute list. The design doc is
> **optional human background**, never a build dependency.

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
- **Seed present, but it is a SCALAR seed only:**
  `agentic/new_workflow_ui_plan:launcher/apps/template_reduce.py` (750 ln,
  class `TemplateReduce`) — reuse its scalar group-box layout + validators;
  **strip** its reduction-execution worker (T2 authors settings, does not run
  reductions). **The angle table is GREENFIELD, not a port** (fork pre-review,
  verified): the seed has **zero** `QTableWidget`/`insertRow`/`currentRow`
  (`grep` → 0). So the "add angles" table view is net-new code — which is
  exactly where the active-row-hidden-input trap is *born*, not inherited.
  The ui-aspects blocking rule below audits **new** table code, not a phantom
  ported bug.
- **Identity contract wired:** `new_launcher.py:7` already imports
  `ensure_identity, migrate_legacy_settings` from `launcher.app_identity`
  (S3). Per charter §3 scope note + the S3 plan's adoption contract, **T2's
  tab MUST call `ensure_identity()` first in its `__init__`** and use the
  shared `ORG_NAME`/`APP_NAME` store — all layers share one QSettings.
- **Harness available:** the launcher-tests fixtures are on exp —
  `isolated_qapp`, `no_qmessagebox`, and autouse `no_qfiledialog`
  (harness-hardening), with the `--timeout-method=thread` backstop. GUI tests
  use them; a modal without `no_qmessagebox` is the 10-hour-orphan class.

## Architecture (three pieces)

1. **`SettingsDocument`** — `src/lr_reduction/settings_document.py`,
   **Qt-free** (no `qtpy`/`PyQt` import — this is the seam that makes RED/GREEN
   cheap and is T3's foundation; verified free: `nr_reduction_config.py`
   imports only `pathlib`, `new_reduction_from_file.py` has no Qt). Wraps one
   `NRReductionConfig` + edit ops: load (from JSON / `.dat` header / defaults),
   validate, normalize, add/remove angle, diff-vs-seed.

   **The per-angle arrays `add_angle`/`remove_angle` MUST keep
   length-consistent (nothing does today) — the authoritative set, verified on
   `agentic/exp` `nr_reduction_config.py` @ `308a020`:**

   | Attribute | init | note |
   |---|---|---|
   | `method_per_run` | `[]` | q-method per angle |
   | `DBname` | `[]` | direct-beam file per angle |
   | `RBnum` | `[]` | **runtime-owned** (normalize drops it) |
   | `RB_Ymin`, `RB_Ymax` | `[]` | peak Y-pixel range |
   | `BkgROI` | `[]` | background ROI (list-of-4) per angle |
   | `useBS` | `[]` | bkg-subtract toggle per angle |
   | `tof_min`, `tof_max` | `[]` | TOF range per angle |
   | `ThetaShift` | `[]` | theta shift per angle |
   | `ScaleFactor` | `[]` | scale factor per angle |
   | `LambdaMin`, `LambdaMax` | **`None`** | per-angle **but init `None`, not `[]`** — "if supplied, an array" (`:68-69`); `add_angle` must special-case None→seed-a-list |

   That is **11 `[]`-arrays + 2 `None`-or-array** = 13 per-angle fields. A
   Developer who grows only the 8 "obvious" ones ships mismatched-length
   arrays — *the exact bug this slug exists to prevent*. `add_angle` mutates
   all 13 in one op; the equal-length assertion below covers the 11 and the
   None-materialization covers Lambda{Min,Max}.
2. **`FIELD_SPEC`** — a declarative table beside `SettingsDocument`:
   `{name, group, type, default, allowed/range, per_angle, runtime_owned, help}`
   for **every** `NRReductionConfig` attribute (read the class in the checkout;
   the 13 per-angle fields are tabled above). One source of truth driving widget
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
  row instead of the row being acted on. Since the table is greenfield (above),
  this trap would be **introduced** by the new code — guard from line one:
  `SettingsDocument.add_angle` / `remove_angle` / per-row edits operate on an
  **explicit row index**, never `table.currentRow()`; the view passes the
  index. Pin with a test that edits row 0's field while row 2 is selected and
  asserts row 0 changed.
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

## Failure-mode matrix (campaign-critical rows)

| Case | Detection | Handling |
|---|---|---|
| FIELD_SPEC names a non-attribute → `AttributeError` at load (common) | name-coverage guard test | FIELD_SPEC is a superset-safe mirror; guard is RED-first |
| Angle arrays drift out of length on add/remove (common) | `add_angle` equal-length assert over all 11 `[]`-arrays | single `add_angle` op mutates all 13 per-angle fields atomically |
| A per-angle array is forgotten (RBnum/ScaleFactor were missing from the first draft) | equal-length assert names the full set; FIELD_SPEC name-coverage | the 13-field table above is the authoritative source, inlined |
| `LambdaMin/Max` (None-init) treated as a plain `[]`-array | `add_angle` test with a fresh doc (Lambda still None) | special-case None→materialize a list on first add |
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
  `FIELD_SPEC` as its foundation (charter §4 T3 entry), so their public shape is an
  interface T3 depends on; supersedes the never-existent `JSONSettingsBuilderTab`.

## Downstream (charter DAG)

T2 **gates T3** (`settings-management`): T3's `SettingsResolver` and the (a)→(f)
resolution stack consume this slug's `SettingsDocument`/`FIELD_SPEC`. T3 stages
only after T2's draft PR merges (same pattern as S0→S1–S3). T1-A1 follows T3.
