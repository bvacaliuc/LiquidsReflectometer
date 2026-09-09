# Plan: settings-editor (T2)

**Campaign:** `exp-settings-roi` · base `exp` @ `308a020` (S0–S3 + harness +
protective slugs all merged) · charter §4 slug T2
**Retry attempt:** 4 of N=4 (human cap extension, 2026-09-09 — per-slug, this slug only; charter §1 knob N)

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

## Revision history — v3 (after v2 blocking review; todo @ `e904196`; FINAL retry, attempt 3 of N=3)

Gate green (140 launcher + 179 reduction). **v2 was a large real
improvement — do NOT rework what the gate confirmed fixed:** both v1
abort paths closed (`@guarded` load-bearing on all eight slots, held
against 17 malformed inputs incl. `RecursionError`), atomic save verified
by fault injection (mkstemp+fsync+os.replace, symlink refused), flat-type
fidelity correct through the widget, the three v1 tautologies properly
dead, sorting pinned, `nr_reduction_calc` change a verified no-op. Four
blocking clusters remain, and their common root is the campaign's
signature meta-defect one level up: **two implementations of the same
thing that drift.** v3 fixes each by single-sourcing, and — because v2
introduced TWO NEW tautologies while fixing tautologies (Cluster 4) —
**every new/changed guard in v3 records its named mutation per charter §9
amendment 16, no exceptions.** Minimal path (the Integrator's 5 steps):

### Cluster 1 (blocking) — the refresh path never got v2's construction-path fixes

v2 repaired display on the **build** path (`_build_editor`, `_show_in_combo`,
`_as_text`) but not the **refresh** path — and C6's `set_document` now routes
every tab-open through `refresh_scalars`, so the stale path runs always.
Three symptoms, one cause (two independent "show value in widget"
implementations): (1a) scalar list fields render `str(value)` `"[50, 200]"`
not `_as_text` `"50, 200"`, and the validator is gated on
`type in ("int","float")` (False for `list[int]`) so `editingFinished`
corrupts `data_x_range` on bare focus-out — no report; (1b) `BkgROI`
(`list[list[int]]`) cells render Python repr, `coerce_element` splits it to
`['[120','130]']`, reported clean, `np.sort` over strings downstream;
(1c) after a Load a non-editable combo `setCurrentText` is a silent no-op,
so `useCalcTheta` shows `sample_angle` while the doc holds `False`,
unrecoverable from the UI.
**Fix (~20 lines, single-source):** one `_show(field, editor, value)` used
by BOTH `_build_editor` and `refresh_scalars`; render per-angle cells with
the same `_as_text`; make `Field.check`/`_type_problem`
(`field_spec.py:167-181,287-290`) **recurse into list elements** so the
corruption is reportable.
**Mutate-once (both currently-vacuous guards fixed):**
`test_a_scalar_list_edit_stores_a_list` — **drop the `editor.clear()`**
(it erases the mis-render before parsing); mutation: revert `_show` to
`str(value)` → must red. `test_a_combo_displays_a_value_outside_its_choices`
— **drive through `set_document`/Load**, not the constructor; mutation:
`refresh_scalars` bare `setCurrentText` → must red.

### Cluster 2 (blocking) — the domain seam is half-derived and already diverging

Only `METHOD_CHOICES`/`CALC_THETA_CHOICES` are wired from the reducer;
`DET_RES_CHOICES`/`PEAK_TYPE_CHOICES` are still hard-coded in
`nr_tools.py:229,382,390,399`, so the "drift structurally impossible" claim
is false for two domains — and DET_RES is live cry-wolf (`'none'` valid in
the reducer, missing from the domain, unreachable from the combo). And
`domains.lowered()` has **zero coverage on the production path**: breaking
it → every `method_per_run` reduction raises `ValueError`, suite green (no
test constructs `NR_Reduction`/`_validate_config`).
**Fix:** add `'none'` to `DET_RES_CHOICES` **or** exempt-and-explain —
record that the two consumers disagree (`_calc_detector_convolution:687-699`
binds `pad` only under rectangular/gaussian, so `'none'` raises
`UnboundLocalError` there); a canonical-domains module must document the
disagreement, not silently pick a side. Wire `nr_tools` to dispatch from
`domains` (all four single-sourced). Replace the `inspect.getsource` grep
with **one behavioural test per domain** driving `_validate_config` /
`fit_peak` / `calc_beam_on_detector` with each declared value asserting
acceptance.
**Mutate-once:** `return list(choices)` in `domains.lowered()` → the new
`_validate_config` behavioural test must red (the mutation that was green).

### Cluster 3 (blocking) — `SettingsDocument.config` still unpinned (named in the v1 rejection)

Renaming the property leaves 91/91 green; zero consumers; it is the reducer
handoff and T3's seam. `set_document`/`overrides`/`default_value` got pinned
in v2; this one was missed twice.
**Fix + mutate-once:** one test asserting `doc.config` is the
`NRReductionConfig` the reduction receives AND that `set()` edits are
visible on it; mutation: rename `config` → the test must red.

### Cluster 4 (blocking) — two NEW tautologies (introduced while fixing tautologies)

**4a** `test_save_leaves_no_temporary_file_behind`: monkeypatches
`json.dumps` to raise at `:318`, **before** `mkstemp` at `:321`, so no temp
is ever created — deleting the whole `except BaseException: os.unlink`
cleanup (`:333-338`) stays green. **Fix:** inject the fault at `os.replace`
or `os.fsync` (after the temp exists); mutation: delete the cleanup block →
must red. **4b** `test_bounds_apply_to_per_angle_entries_too`: sets
`ScaleFactor=1.0` (in range) — no violation — so neutering the per-angle
`check_element` loop (`:247-251`) stays green. **Fix:** use an
**out-of-range** value; mutation: neuter the per-angle bounds loop → must
red. (This cluster is *why* amendment 16 must apply to EVERY new guard: the
Developer diagnosed 4a's sibling and re-aimed it, then left this one at the
unreachable point — the gate must be mechanical, not selective.)

### v3 should-fix (safety-relevant ones are not optional)

- **The shared-sink partial fix:** `Sname` got `no_separators=True`; its
  four identical-f-string siblings `subname`/`DTCsubname`/`BINsubname`/
  `errBINsubname` did not (`subname="/../../../tmp/pwn"` → `/tmp/pwn.dat`,
  `nr_reduction_calc.py:196,216,272-274`). Apply the same guard to all five.
- **The path guard mis-models the `_*_override` fields:** they ARE the whole
  path (not base-joined), so the guard rejects their only legit shape (the
  absolute path `QFileDialog` returns) while accepting CWD-relative values.
  Validate existence/writability or `is_relative_to(base_path)` after
  resolve; and catch bare `..` in `experiment_id` (typed `str`, so
  `_path_problem` never runs).
- **`validate()`/`refresh_report()` are uncapped** on the hot path
  (`MAX_TABLE_ROWS` caps display only): a 4.9 MB file → 74.7 MB report
  rebuilt per edit. Cap the report/validate too.
- `save_settings` builds an unused `QFileDialog` then calls the static
  `getSaveFileName` (so `setDefaultSuffix` is inert, one dialog leaks/click;
  suffix fallback keys on `Path.suffix` so `settings_0.5deg`→`.5`); fix the
  suffix logic. `set_document` gets `@guarded` (the one unguarded public
  entry, T3's injection path). Collapse `Field.coerce`/`_coerce_typed` to
  one list-splitter (C6's triplication→duplication wasn't finished).
  Guard the char-explosion (`:182`) on `isinstance(current, list)`. Remove
  the dead `DEFAULT_IF_EMPTY_NAMES`.

### v3 acceptance (final-gate)

- One `_show()` drives both render paths; per-angle cells use `_as_text`;
  `check`/`_type_problem` recurse into list elements; 1a/1b/1c each report
  or round-trip correctly (no silent corruption).
- All four domains single-sourced from the reducer; one behavioural
  acceptance test per domain; `domains.lowered()` covered on the
  `_validate_config` path.
- `doc.config` pinned; both Cluster-4 guards re-aimed to their reachable
  fault and each reds under its named mutation.
- **Every new/changed guard in the diff records its mutation + observed red
  in the commit body** (amendment 16, enforced — the two v2 tautologies are
  why). Path-sink siblings guarded; report/validate capped.
- `pixi run test-launcher` + `test-reduction` green; no `pixi.lock` change.
- **This is T2's final retry (N=3).** If v3 is rejected on a genuinely new
  correctness finding it escalates; it must not be rejected on a net-new
  comment/preference — anything cosmetic rides the draft-PR body as advisory.

## Revision history — v4 (human cap extension to N=4 — 2026-09-09)

The human extended the retry cap to **N=4 for this slug only** after v3
(gate green; **ui-aspects found NOTHING blocking** — all three v2 widget
defects fixed with guards red-on-revert; one blocking `test-reviewer`
finding) rejected on **B2 narrowed-not-closed**: the domain seam is
half-derived — `domains.lowered()` is now behaviourally covered and all
four domains derive their enforcement *messages*, but `nr_tools`/
`nr_reduction_calc` still **dispatch** on literals, so the drift the
cluster is named for (*the editor offers a value the reducer rejects*)
is undetected for `METHOD` and `DET_RES` (`CALC_THETA` has a
contents-pin; `PEAK_TYPE`'s dispatch is hardcoded-independent; these two
have neither). This is a coverage gap on substance every declared
reviewer confirmed sound — a converged slug at the cap. **Authoritative
scope: `plans/settings-editor-advisor-review.md` @ `c97f88f`, §4** (todo
@ `493c81c`). v4 is **strictly the five items below; nothing else** —
follow-ups deliberately excluded are in §4's last paragraph and must NOT
be folded in.

### v4 scope (advisor-review §4, priority order)

1. **Truthful contract.** Rewrite `field_spec.py:46-51` to say the
   validators **derive from `reduction_domains`, the dispatch in
   `nr_tools`/`nr_reduction_calc` stays literal, and the contents pins
   (item 3) are what catch drift** — the current text overclaims
   "structurally impossible". Derive the message at
   `nr_reduction_calc.py:665` from `domains.METHOD_CHOICES` (one line;
   the dispatch above it stays). **Do NOT restructure `nr_tools`'
   dispatch.**
2. **Positive driver for `DET_RES_CHOICES`.**
   `@pytest.mark.parametrize("fn", fs.DET_RES_CHOICES)` calling
   `nr_tools.calc_beam_on_detector(..., DetResFn=fn)`, asserting no raise
   — pins the "reducer accepts every offered value" direction the pin
   alone can't.
3. **Contents-equality pins** for `METHOD_CHOICES`, `PEAK_TYPE_CHOICES`,
   `DET_RES_CHOICES`, beside the existing `CALC_THETA` pin.
4. **Case convention** (advisory-in-three-reviews, but a real correctness
   defect in the editor's core promise): `Field.check` accepts
   `"Gaussian"` for `DetResFn`/`peak_type` while `nr_tools` compares
   exactly → the reduction dies partway. Normalize to the declared
   spelling in `coerce_element` for those two domains, OR check
   case-sensitively where the reducer does. One behaviour, one test.
5. **Pins for v3's own untested repairs** (each observed "suite green
   after mutation"): `check`/`_type_problem` list recursion; the checkbox
   leg of `_show`; `no_separators` on the four `subname` siblings; an
   absolute `_*_override` path accepted; the `DET_RES_TOLERATED` branch
   in `nr_tools`.

**Mutate-once (charter §9 amendment 16):** every new/changed guard
records its mutation and observed red in the commit body. For items 1–3
the named mutations are: grow/shrink `METHOD_CHOICES` → item-3 pin +
item-2 driver red; grow/shrink `DET_RES_CHOICES` → same; alter the
`:665` message text → item-1's derivation test red.

### v4 final-gate instruction to the Integrator (human directive, 2026-09-09)

**PASS when items 1–3 are present and their mutations red.** Items 4–5
missing or imperfect are **advisory** — recorded in the draft-PR body,
**never grounds for rejection**. Anything else new rides the PR body.
The §4 "deliberately left for follow-up" list (the `@guarded
set_document` silent-success path, combo-item accumulation across Loads,
`save_settings` accepting `.dat`, the `''`/`None` `experiment_id`
asymmetry, capping `refresh_report()`) is **out of v4 scope** — do not
add it.

### v4 — for T3 (advisor-review §5)

Item 1's rewritten sentence is what T3's `SettingsResolver` reads first;
it must be true before T3 stages. Items 2–3 are the guards T3 inherits.
Nothing else in this slug blocks T3's plan.
