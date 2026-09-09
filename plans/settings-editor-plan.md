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

## Revision history — v2 (after v1 blocking review; todo @ `27710bd`)

**Retry attempt 2 of N=3.** Gate green (128 launcher + 145 reduction); all
findings are gate-invisible. Four reviewers ran; both blocking domains
found blocking defects, advisories confirmed the worst. **Confirmed sound
by the gate — do NOT rework:** the active-row-hidden-input trap is
genuinely absent (both pin tests real — the plan's emphasis held); the
FIELD_SPEC↔NRReductionConfig mirror is exemplary (catches both
directions); no injection sink is reachable from a settings file; Qt
lifecycle clean; `ensure_identity()` called first per S3. v2 fixes the six
clusters below; **each new/amended guard test carries a named mutation
per charter §9 amendment 16** (mutate-once) — the C3 cluster is the fourth
consecutive slug rejected for vacuous guards, so this is now non-optional.

### C1 (blocking) — a cell edit aborts the whole launcher (SIGABRT), from valid files

Root: `set_angle_field` pads a `None` per-angle field to `n_angles` but not
a **short** list (`settings_document.py:153-157`), so an `IndexError` in a
Qt slot → `qFatal()`/`abort()` kills `ReductionInterface` and every tab's
unsaved state. Reachable three ways from ordinary files (the len-1
broadcast idiom the reducer sanctions; the editor's own `normalize()`
round-trip; a short per-angle column the panel invites editing). Second
path: a malformed load (`{"tof_min": 5}` → `TypeError` in `validate()`)
escapes the slot because the refresh calls sit outside `load_settings`'
`try` and the catch is only `(ValueError, OSError)`.
**Fix (one cluster):** (a) pad in `set_angle_field` when
`current is None or len(current) < self.n_angles`; (b) `validate()`
*reports* a non-sequence per-angle value instead of iterating it;
(c) move the three refresh calls inside the `try`, broaden to
`except Exception`, and give **every** slot (`_on_cell_changed`,
`_on_scalar_edited`, `add_angle`, `remove_selected_angle`, `load_settings`,
`save_settings`) a top-level guard that reports into the panel — the
existing `except (ValueError, OSError)` shows the intent.
**Mutate-once:** revert the short-list pad → the edit-a-short-column test
aborts (EXIT=134); remove a slot's guard → the malformed-load test aborts.

### C2 (blocking) — every `list[...]` field stores a raw string (silent wrong science)

`_coerce` branches on `"int"`/`"float"` only, so no per-angle cell (all
`list[...]`) and no `data_x_range`/`emission_coefficients`/`Lambda*Use`
scalar is ever coerced — `useBS` stores `"False"` (truthy → background
subtracted when the scientist turned it OFF); `data_x_range` `"60, 210"`
→ `x_min_pixel=6`. `_check_value` returns `""` for non-int/float, so
`validate()` says clean and the min/max bounds never apply.
**Fix:** `_coerce` unwraps `list[...]` to its element type with an
**explicit** bool parse (`{"true","1","yes"}`, never `bool(str)`);
`data_x_range` gets a real two-value editor; `_check_value` reports a value
whose Python type contradicts `field.type`. Put `coerce()`/`check()` on
`Field` (C6) — not a third copy in the view.
**Mutate-once:** store `useBS` uncoerced (`"False"`) → the round-trip type
test reds (`elem is str`); a type-mismatch value → the `_check_value` test
reds.

### C3 (blocking) — three tests cannot fail (the mutate-once class, 4th slug)

- **C3a** `test_validation_report_names_the_offending_field`: satisfied by
  the changed-vs-seed section, not validation. **Fix:** assert on the
  validation *line* (`"is above 1.0"`) or that the report contains every
  string in `document.validate()`, AND drive it through a gesture (not a
  hand `refresh_report()`). Mutate: stub `validate()`→`[]` → must red.
- **C3b** `test_normalize_drops_runtime_owned_fields`: iterates the same
  derived tuple it checks. **Fix:** literal
  `assert {"RBnum","LambdaMinUse","LambdaMaxUse"}.isdisjoint(normalized)`
  + a separate pin on the tuple. Mutate: `RUNTIME_OWNED_NAMES=()` → must red.
- **C3c** `test_set_angle_field_uses_the_index_it_is_given`: edits index 0,
  which a hard-coded `0` satisfies. **Fix:** edit index 1 of 3. Mutate:
  `updated[0]=value` (ignore index) → must red. (The view twin at
  `test_settings_editor.py:110` is genuinely falsifying — keep.)

### C4 (blocking) — `save()` destroys the prior good file; follows symlinks

`open(path,"w")` truncates before a byte is produced → a mid-dump failure
(ENOSPC, stalled `/SNS` mount, or a C1 abort mid-save) leaves a partial
invalid file, no backup, on a network mount; and it writes through a
symlink (CWE-59/61), the overwrite dialog showing the link name.
**Fix:** `NamedTemporaryFile(dir=path.parent, delete=False)` → `flush()` →
`os.fsync()` → `os.replace()`; open the temp `O_EXCL|O_NOFOLLOW`; set mode
**0644 explicitly** (shared file — NOT 600); refuse or warn-with-resolved-
target when `path.is_symlink()`.
**Mutate-once:** revert to `open(path,"w")` → the interrupted-save test
(prior content survives) reds; a symlink target → the no-follow test reds.

### C5 (blocking) — `useCalcTheta` bool vs the reducer's enum

Declared `type="bool"`; the reducer wants `('detector_angle','sample_angle')`
with `True` a legacy alias for the former — so a loaded `'sample_angle'`
renders as a checkbox and toggling silently downgrades to `detector_angle`,
and `'sample_angle'` is unreachable. **Fix:** `type="str"`,
`allowed=('detector_angle','sample_angle')`. **Same class, unguarded:**
`METHOD_CHOICES`/`DET_RES_CHOICES`/`PEAK_TYPE_CHOICES` hand-mirror bare
lists in `nr_reduction_calc.py:84,92` — promote those to imported module
constants (or an AST guard), matching the FIELD_SPEC mirror's rigor.
**Mutate-once:** a domain guard test — set `useCalcTheta='sample_angle'`,
assert it survives a round-trip unchanged → reds against the bool coercion.

### C6 — required before T3 (interface, not polish — T2 gates T3)

- **Move `coerce()`/`check()` onto `Field`** (Qt-free) — the type dispatch
  is triplicated across `_build_editor`/`_coerce`/`refresh_scalars`/
  `_check_value`, and `_coerce`↔`_check_value` disagreement *is* C2; T3
  would write a fourth copy.
- **Add `set_document()`** doing the three refreshes — `__init__` never
  calls `refresh_angles()`, so an injected `document=` (T3's exact path)
  renders zero rows.
- **Add `overrides()`** (non-default values only) — a resolution stack
  needs what a layer contributes, which `to_dict()` (all) and `normalize()`
  (all-minus-runtime) don't give.
- **`Field.default` returns a shared mutable list** — `frozen=True` guards
  the binding, not the list; T3 layering starts from defaults, first mutator
  corrupts the table. Return a copy or store tuples.
- **`field_spec.TYPES` is dead** and nothing asserts `f.type in TYPES`
  (`"flaot"` → silent unvalidated `QLineEdit`). Add two assertions beside
  the existing three — the guards that would have caught C2's premise.
- **Qt-free guard is defeated by a transitive import.** Add one **subprocess
  test**: import the two model modules, assert no Qt in `sys.modules`, then
  exercise the document — closes the hole and asserts the property T3
  depends on. Mutate: add `from launcher.app_identity import …` to
  `settings_document.py` → the subprocess test reds.

### v2 should-fix (fold in; the safety-relevant ones are not optional)

- `setSortingEnabled(False)` explicitly + assert in the row-isolation test
  (one `sortItems()` re-introduces the row-index bug).
- **Path safety:** reject absolute paths and `..` for `type=="path"`, and
  path separators in `Sname` (`experiment_id`/`Sname` redirect
  `save_reduced_data.py:36-44` verbatim; first UI making these routinely
  authorable, and `validate()` says clean).
- Validation cries-wolf: a `default_if_empty` flag alongside `broadcast_ok`
  so the 5 auto-defaulted fields + `RBnum` (runtime-owned) stop reporting
  false problems (training the scientist to ignore the panel is how C2
  stays invisible).
- `setDefaultSuffix("json")`; cap `n_angles` in the view (measured ~1100×
  memory amplification); collapse an all-`None` optional list back to
  `None`; a combo must not silently display an out-of-set loaded value.
- Tighten the name-coverage guard docstring (`test:26-31`) — it describes a
  `json_to_config`/`AttributeError` rationale the body (a `__dict__` subset
  check) never executes; the real mechanism is stricter, so fix the prose.

### v2 acceptance additions (final-gate)

- No slot can abort the process: every listed slot has a panel-reporting
  guard; C1's two triggers each report instead of `EXIT=134`.
- Every `list[...]`/typed value round-trips as its declared type (C2);
  `validate()` reports type mismatches and applies min/max to per-angle
  values.
- Each C3 guard reds under its named mutation (recorded in the commit
  body); the two new `field_spec` assertions + the subprocess Qt-free test
  present.
- `save()` is atomic + fsync'd + no-follow + mode-0644; the interrupted-save
  test shows prior content intact.
- C6 interface items present (`set_document`, `overrides`, `Field.coerce/
  check`, copy-on-default) — these are T3's handoff surface.
- `pixi run test-launcher` + `test-reduction` green; no `pixi.lock` change.
