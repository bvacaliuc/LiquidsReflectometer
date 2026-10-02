# Plan: `editor-load-fidelity` — a reducer-written settings file loads quietly, saves as it was written, and its runtime record is read-only

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-load-fidelity` (refs `triage/editor-load-fidelity`,
`feature/editor-load-fidelity`, `qa/editor-load-fidelity`) · **Status:** v2 (retry 1 of N = 3; v1 rejected at `review/editor-load-fidelity` @ `8b62952` — see Revision history) ·
**Base:** `agentic/exp-review` @ `7b6d6b9` · **PR target:** `exp-review` on the fork, **draft** ·
**Depends on:** nothing (first of the editor lane; `editor-combos` waits for this slug's merge) ·
**Review domains:** design, test (block) · **Kind:** launcher / settings model — **not** reduction-path
(§2 F7) · **Sources:** scientists' items 1 and 5 (`requests/updates_for_setting_loader.md`), Q1
(`plans/settings-loader-clarifications-decision-request.md` §Resolution), charter §3 row.

Canonical copy: ledger `plans/editor-load-fidelity-plan.md`; the copy on `triage/editor-load-fidelity`
is byte-identical at dispatch.

## Declared scope

**Files in:** `src/lr_reduction/field_spec.py`, `src/lr_reduction/settings_document.py`,
`launcher/apps/settings_editor.py`, `tests/unit/lr_reduction/test_settings_document.py`,
`launcher/tests/test_settings_editor.py`.

**Behaviours in** (B1–B7, §3): 0/1 accepted wherever a boolean is declared; `useBS` held as booleans
after a load, shown as `true`/`false`, written as `1`/`0`; the runtime record (`LambdaMinUse`,
`LambdaMaxUse`) never produces a problem line and cannot be edited; the round trip is idempotent.

**Explicitly OUT** (a finding here is a PR-body advisory, not a rejection):
- every reducer file — `nr_reduction_calc.py`, `nr_reduction_config.py`, `new_reduction_from_file.py`,
  `new_reduction_from_template.py`, `save_reduced_data.py` (read them; do not edit them);
- drop-downs for per-angle fields and the wheel guard (`editor-combos`); theta labels and legacy theta
  spellings (`editor-defaults-and-theta`); section order (`editor-sections`); the paths header;
- the declared `Field.type` of `LambdaMinUse`/`LambdaMaxUse` (`list[float]`, contradicted by the writer —
  F3): the record's shape is decided by `header-scale-factors-per-position`; this slug makes the editor
  indifferent to it instead of re-declaring it;
- whether `RBnum` should also be read-only (A2); what `None` entries in `useBS` mean to the reducer (A5).

## 1. Request and symptom

> 1. Clean up a bug in loading in the useBS setting which gets displayed as a Problem in the 'Validation
> and changes' box. This parameter is typically saved as a 1/0 rather than a true/false but prints at the
> bottom that true/false is expected. It should accept 1/0.
>
> 5. The entries for Lambda min used and Lambda max used should be read-only not setable parameters.

Q1 `[human, 2026-10-02]`: "accept both on load, save 1/0, render as true/false in the table. Note … one
of the task items is to produce drop down selectors for all enumerated choices in the editor page, so be
cognizant of that." (The drop-down is `editor-combos`; this slug must leave the per-angle boolean in a
shape a two-item combo can take over: a real `bool` in the model, `true`/`false` as its text.)

## 2. Verified facts at the base tip (`7b6d6b9`)

| # | Fact | Command → observation |
|---|---|---|
| F1 | The reducer itself writes integers for `useBS`. | `grep -n useBS src/lr_reduction/nr_reduction_calc.py` → `:102-103` `if not self.config.useBS: self.config.useBS = [1] * n_settings`; `new_reduction_from_template.py:180,182` → `[1]` / `[0]`. It reads them by truthiness (`nr_reduction_calc.py:509`, `:979` `if self.config.useBS[i]:`). |
| F2 | The editor reports every such entry. | `SettingsDocument.from_dict({"useBS": [1, 1, 0], …}).validate()` → `Subtract background (useBS) at angle 0: expected true/false, got 1` (×3). Cause: `field_spec._type_problem` (`:343-344`) accepts only `isinstance(value, bool)`. |
| F3 | **CORRECTION to the backlog map** (it lists item 5 as display-only). The runtime record is a **scalar per call**, but `FIELD_SPEC` declares it `list[float]`, so every reduced file shows two more problem lines. | `sed -n 380,391p src/lr_reduction/nr_reduction_calc.py` → `self.config.LambdaMinUse = lam_range[0]` / `= self.config.LambdaMin[i]`; `field_spec.py:556-561` `"list[float]"`; `from_dict({"LambdaMinUse": 2.95}).validate()` → `Lambda min used (LambdaMinUse): expected a list of float, got float 2.95`. |
| F4 | The record's editors are writable today. | `settings_editor._build_editor` (`:205-218`) gives every non-bool, non-enumerated field a `QLineEdit` wired to `_on_scalar_edited`. Offscreen probe on the F9 file: `isReadOnly()` → `False`; `QTest.keyClicks(editor, "9")` + Return turns the recorded `2.95` into `[2.959]` — one keystroke rewrites the record and changes its shape. |
| F5 | The settings file a scientist loads is written by `save_config_json` from `config.__dict__`. | `new_reduction_from_file.py:147-152` (`{Sname}_settings.json`), `:476-499`; a `.dat` header carries the same dict on its `# Config:` line (`load_from_file`, `:451-473`). |
| F6 | A bool renders with Python's spelling. | `SettingsEditorTab._as_text(True)` → `"True"` (`settings_editor.py:265-271`); cells are filled in `refresh_angles` (`:361-378`). |
| F7 | Not reduction-path. | `grep -rln 'field_spec\|settings_document' src/lr_reduction launcher --include=*.py` → only `field_spec.py`, `settings_document.py`, `settings_editor.py` and its test. No reducer module imports them, so charter §4's baseline/`check_headers.py` clause does not apply. |
| F8 | Baseline is green. | `pixi run python -m pytest launcher/tests/test_settings_editor.py tests/unit/lr_reduction/test_settings_document.py -q` → `136 passed`. |
| F9 | RED on a reducer-written file, end to end. | `ledger/scripts/editor-real-file-roundtrip.py <file written by save_config_json with useBS=[1,1,0], LambdaMinUse=2.95>` → 5 `FAIL` lines, exit 1 (run 2026-10-02, uvdl3 clone 1). |

Writers of `useBS` (enumerated, per `todo-legacy-artifact-trust-enumerate-writers.md`):
`nr_reduction_calc.py:103` (ints), `new_reduction_from_template.py:180/182` (ints), the examples
(`example_nr_reduction.py`, ints), this editor (bools today), a hand-edited file (anything). Writers of
`LambdaMinUse`/`LambdaMaxUse`: `nr_reduction_calc.py:385-391` only (scalar).

## 3. Design — behaviours, not code

The model holds booleans; a file holds what the reduction's own writer writes. Encoding happens at the
file boundary, in one place, driven by a declaration on the `Field`.

| # | Behaviour | Where it must hold |
|---|---|---|
| B1 | **(v2)** The integers `1`, `0` are accepted without a problem line **only where the file encoding is `1`/`0`** — the fields declared integer-encoded (`useBS` entries; `Field.int_encoded` at the feature tip). `True`/`False` are accepted everywhere. In the seven scalar booleans an integer is reported as at the base — a line naming the field and the value, telling the author to write `true`/`false`, and **not** offering `1/0`. Anything else is reported; for an integer-encoded entry the message names both spellings. | `validate()` on **any** document — loaded, injected (`SettingsDocument(config)`), or edited. |
| B2 | **(v2)** After `from_dict` / `from_file`, integer `1`/`0` **in an integer-encoded field** is held as `True`/`False` (`type(v) is bool`). Every other value — including an integer in a scalar boolean — is left exactly as loaded. The seed is taken after this, so `changed_vs_seed()` is empty straight after a load. | load only |
| B3 | An Angles-table cell of a boolean column shows `true` / `false` for `True`/`1` and `False`/`0`; any other value shows as today. | `refresh_angles` |
| B4 | `save()` writes each `useBS` entry as JSON `1`/`0` (`null` for an unset entry); scalar booleans are written as held (`true`/`false`). `normalize()` encodes `useBS` identically. Which list fields are integer-encoded is declared on `Field` (one new attribute, default off, set for `useBS` only) — not a name test inside the document. | `save`, `normalize` |
| B5 | `LambdaMinUse` and `LambdaMaxUse` never produce a problem line, whatever shape the file carries. | `validate()` |
| B6 | Their editors are read-only: `isReadOnly()` is true, typing changes neither the widget nor the document, and they still display what the file recorded (after every load). | `_build_editor`, `refresh_scalars` |
| B7 | load → save → load → save: the second file is byte-identical to the first, and `useBS` in it is the JSON the source held. | end to end |
| B8 | **(v2, new)** **Load → save never changes what the reduction does with a declared boolean.** For each of the seven scalar booleans the saved JSON value has the same value **and type** as the source's (`1` stays `1`, `true` stays `true`) — so every reader sees what it saw before, whether it reads by truthiness, by identity (`useGravity`, `nr_reduction_calc.py:1079`) or by formatting the value into a header (`save_reduced_data.py:79-80,97-98`). For `useBS`, an entry in {`1`, `0`, `true`, `false`} is saved as `1`/`0`, which its readers (truthiness at `nr_reduction_calc.py:102`, `:509`, `:979`; `== 1` at `new_reduction_from_template.py:224`) read as they read the source. | end to end |

**Types and states each changed path acts on** (amendment 18 — state the behaviour before writing code):

| Value in a declared-boolean position | scalar field (`Normalize`, `AutoScale`, `plotON`, `plotQ4`, `save8col`, `useGravity`, `use_emission_time`) | one `useBS` entry |
|---|---|---|
| `True` / `False` | no problem; checkbox; saved `true`/`false` | no problem; `true`/`false`; saved `1`/`0` |
| `1` / `0` (int) | **(v2)** reported (as at the base); held as loaded; saved as loaded — `1` stays `1` (B8) | no problem; loaded → `True`/`False`; saved `1`/`0` |
| other int (`2`, `-1`) | reported, kept | reported at its angle, kept |
| float (`1.0`), str (`"0"`, `"true"`), list | reported, kept — never coerced on load: `"0"` is truthy to the reducer, so silence would subtract a background the author switched off | same |
| `None` | no problem (unset) | no problem; saved `null` |
| whole `useBS` = `[]` | — | no problem (`default_if_empty`; the reducer fills `[1]*n`) — unchanged |
| whole `useBS` not a list (`1`, `"1"`) | — | reported as today (`validate()` type guard, `settings_document.py:240-242`), kept, saved as held |

| `LambdaMinUse` / `LambdaMaxUse` holds | validate | editor shows | `save()` | `normalize()` |
|---|---|---|---|---|
| `None` (fresh document) | quiet | empty | `null` | dropped (unchanged) |
| a number (today's writer) | quiet | `2.95` | unchanged | dropped |
| a list of numbers (a future or hand-made file) | quiet | `2.95, 3.1` | unchanged | dropped |
| anything else | quiet | its text | unchanged | dropped |

Decisions, with reasons:
- **Why canonicalize on load as well as accept in validation.** Acceptance alone leaves `[1, False, 0]`
  in the model after one edit, and the "Changed from the seed" panel prints it that way. Canonical
  booleans give the scientists one spelling on screen and give `editor-combos` a `bool` to bind.
- **(v2) Why 1/0 is accepted only where it is the file's own encoding.** v1 widened it to every declared
  boolean on the premise that the reducer reads them all by truthiness. One reader does not
  (`useGravity is True`, `:1079`), and others format the value into headers. Mirroring each reader's mode in
  the table would be a hand-copy of the reducer that drifts; leaving scalars untouched needs no knowledge
  of the readers at all, and it is all item 1 and Q1 asked for (`useBS`).
- **Why acceptance is not load-only.** A document handed a config directly never passes `from_dict`;
  it must not cry wolf either.
- **Why the record is quiet rather than re-typed.** It is not an input: `nr_reduction_calc.py:385-391`
  overwrites it before first use (`:452`). A problem line on a field the user cannot edit has no remedy.
- **Why a declaration, not `if name == "useBS"`.** `settings-editor-learning.md` §6: type decisions made
  in more than one place drift. One attribute on `Field`, one encoder, called from `save` and `normalize`.

## 4. Files to change

| File | Change |
|---|---|
| `src/lr_reduction/field_spec.py` | boolean acceptance of `1`/`0` in the type check, message naming both spellings; the new integer-encoding attribute on `Field`, set on `useBS`; a derived tuple of such names beside `RUNTIME_OWNED_NAMES`, added to `__all__` |
| `src/lr_reduction/settings_document.py` | load-time canonicalization (beside `_migrate_legacy`); the file-boundary encoder used by `save()` and `normalize()`; `validate()` quiet for the non-per-angle runtime record |
| `launcher/apps/settings_editor.py` | boolean cell text (B3); read-only editors for the runtime record (B6) |
| the two test modules | §6 |

`RBnum` (runtime-owned, per-angle) keeps its present validation and editability.

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | autoreduce file, `useBS: [1, 1, 1, 1]`, scalar record | "No problems found."; cells `true`; record shown, read-only; save reproduces `[1, 1, 1, 1]` |
| common | file saved by this editor before the fix, `useBS: [true, false]` | loads quietly; saved as `[1, 0]` |
| common | fresh document, add two angles, type `false` in one cell, save | `[null, 0]` or as filled; never the string `"false"` |
| edge | mixed `[1, true, 0]` | quiet; held `[True, True, False]`; saved `[1, 1, 0]` |
| edge | `.dat` header as the source | identical to the JSON case (same loader) |
| edge | config injected with integer `useBS` (no load) | quiet (B1); cells `true`/`false` (B3); saved `1`/`0` (B4) |
| edge | **(v2)** config injected with an integer scalar boolean (`useGravity = 1`) | reported; held and saved as `1` |
| edge | **(v2)** scalar `"Normalize": 1`, `"useGravity": 1` or `0` (a hand-edited file) | reported by name; held and saved as written; the reduction of the saved file is the reduction of the source |
| edge | record holds a list, or `None` | quiet; shown; never editable |
| edge | toggle one `useBS` cell after loading ints | only that entry changes; "Changed from the seed" lists `useBS` once, in booleans |
| pathological | `useBS: [2]`, `["0"]`, `[1.0]`, `[[1]]` | each reported at its angle, value kept, save writes what is held |
| pathological | `useBS: 1` (not a list) | reported once; no exception leaves a slot (`guarded`) |
| pathological | a read-only editor receives a programmatic `editingFinished` | document unchanged |
| pathological | 10⁶-angle file | unchanged caps (`MAX_TABLE_ROWS`, `MAX_REPORTED_PROBLEMS`); the new code adds no per-keystroke pass over the columns beyond what `validate()` already does |

## 6. Red-Green TDD seed

Fixture — shaped by the writers, written by the reduction's own saver (ruff-clean as given):

```python
from pathlib import Path

from lr_reduction.new_reduction_from_file import save_config_json
from lr_reduction.nr_reduction_config import NRReductionConfig


def reducer_written_settings(path):
    config = NRReductionConfig()
    config.experiment_id = "IPTS-00000"
    config.RBnum = [201282, 201283, 201284]
    config.DBname = ["db_a.dat", "db_b.dat", "db_c.dat"]
    config.method_per_run = ["meanTheta"]
    config.RB_Ymin = [140, 141, 142]
    config.RB_Ymax = [150, 151, 152]
    config.BkgROI = [[120, 130], [121, 131], [122, 132]]
    config.useBS = [1] * 3  # nr_reduction_calc.py:103 fills an empty one exactly so
    config.useBS[2] = 0  # new_reduction_from_template.py:182 writes 0 for "off"
    config.useCalcTheta = "detector_angle"
    config.LambdaMinUse = 2.95  # nr_reduction_calc.py:385-391: one scalar per call
    config.LambdaMaxUse = 6.1
    save_config_json(Path(path), config)
    return Path(path)
```

Test names are suggestions; a test must be named for what it covers. **`True == 1` in Python**: every
assertion about encoding or canonicalization compares `type(v) is bool` / `type(v) is int`, or the saved
**text** — `assert doc.get("useBS") == [True, True, False]` passes on integers and guards nothing.

Model (`tests/unit/lr_reduction/test_settings_document.py`):

| # | Test | RED at the base | GREEN |
|---|---|---|---|
| T1 | a reducer-written file validates clean (`from_file(fixture).validate() == []`) | 5 problem lines | B1/B2/B5 |
| T2 | loaded `useBS` is held as booleans (`[type(v) for v in …] == [bool] * 3`, values `[True, True, False]`) | ints | B2 |
| T3 | an injected config with integer `useBS` validates clean (`SettingsDocument(config)`, no load) | 3 lines | B1 |
| T4 | saved `useBS` is ones and zeros — parametrized source `[1,1,0]`, `[True,True,False]`, `[1,True,0]`; assert on `json.loads(text)` entry **types** and on the text | bool source writes `true` | B4 |
| T5 | `normalize()["useBS"]` has `int` entries | bools | B4 |
| T6 | a scalar boolean is saved `true`/`false` (text contains `"Normalize": true`) | passes — a pin | stays |
| T7 | a non-boolean entry is reported and kept — parametrized `2`, `"0"`, `1.0`, `[1]`; the line names both spellings | reported today, in the old wording — the `(or 1/0)` assertion is the red leg; the "kept" legs are pins | B1 |
| T8 | the runtime record is never a problem — `LambdaMinUse`/`LambdaMaxUse` × `2.95`, `None`, `[2.95, 3.1]`, `"n/a"` | scalar and string legs red | B5 |
| T9 | the round trip is idempotent and `useBS` text-equal to the source (fixture → save A → load A → save B; `A == B` bytes) | passes — a pin (today the ints are simply carried) | B7 stays |
| T10 | the seed is canonical too: after loading the fixture and setting one `useBS` entry to `False`, `repr(changed_vs_seed()["useBS"][0])` is `[True, True, False]` (compare the **repr** — equality cannot tell `1` from `True`); and `changed_vs_seed()` is empty before the edit | repr is `[1, 1, 0]` | B2 |
| T11 | the integer-encoded names are exactly `{"useBS"}` | attribute absent | B4 |

View (`launcher/tests/test_settings_editor.py`; gestures through `QTest`, cells through
`item(row, column).setText(...)` as the existing row-isolation test does; `isolated_qapp`,
`no_qmessagebox`; Load via the patched `QFileDialog.getOpenFileName` as in
`test_loading_a_settings_file_repopulates_the_view`):

| # | Test | RED at the base | GREEN |
|---|---|---|---|
| V1 | after Load of the fixture the `useBS` cells read `true`, `true`, `false` | `1`, `1`, `0` | B2+B3 |
| V2 | the report reads "No problems found." for the fixture | 5 lines | B1/B5 |
| V3 | typing in a runtime-record editor changes nothing: `QTest.keyClicks(editor, "9.9")`, `Key_Return`; `editor.isReadOnly()`; `document.get(name)` unchanged; text unchanged | document becomes `[2.959.9]`-style text coerced to a list (probe: `2.95` → `[2.959]`) | B6 |
| V4 | the record editor shows what the file recorded (`"2.95"` after Load; empty after loading a file without it) | first leg passes — a pin | B6 |
| V5 | toggling a loaded cell then Save writes `[1, 0, 0]` (cell `(1, useBS)` set to `false`; saved text entry types `int`) | writes `[1, false, 0]` | B4 |
| V6 | an injected integer `useBS` renders `true`/`false` (`SettingsEditorTab(document=SettingsDocument(config))`) | `1`/`0` | B3 |

RED is observed and recorded per test before the production edit (the commit body quotes the failing
line). The launcher suite arms 120 s per test (`launcher/tests/conftest.py`); no test here opens a modal.

## 7. Mutate-once gate (amendment 16 — record each in the commit body as `<mutation> → <test> -> N failed`)

| # | Mutation applied to the production code | Must red |
|---|---|---|
| M1 | boolean type check accepts only `bool` again | T3 (T1 stays green — B2 covers the loaded case; that is expected, not a vacuous T1) |
| M2 | load canonicalization removed | T2, T10 (V5 stays green — the encoder still writes `1`/`0`; expected) |
| M3 | file encoder removed from `save()` | T4 (bool and mixed legs), V5 |
| M4 | file encoder removed from `normalize()` | T5 |
| M5 | encoder converts **every** boolean (flag ignored) | T6 |
| M6 | integer-encoding attribute dropped from `useBS` | T11, T4 |
| M7 | `validate()` checks the runtime record again | T8, T1, V2 |
| M8 | `setReadOnly` removed from the record editors | V3 (`isReadOnly` leg) |
| M9 | the record editors wired to `_on_scalar_edited` again (with read-only kept) and `editingFinished` emitted in a dedicated test leg | V3's programmatic leg — add that leg if the design keeps a connection at all; if no connection exists the row is recorded as "no such path" |
| M10 | boolean cell text falls back to `str()` | V1 (`True` ≠ `true`) |
| M11 | boolean cell text handles `bool` only, not `1`/`0` | V6 |
| M12 | seed captured before canonicalization | T10 (repr leg; its emptiness leg stays green — `[1, 1, 0] == [True, True, False]`) |

**Frame** (helpers introduced or re-pointed — one row per call site): the encoder (`save`, `normalize`:
M3, M4); the canonicalizer (`from_dict`; `from_file` reaches it through `from_dict` — state that, do not
add a second call): M2; the cell-text helper (`refresh_angles`): M10, M11. If `_as_text` itself is
changed rather than a new helper added, its other call site (`_show` for line edits) gets a row too:
a scalar list such as `data_x_range` must still render `50, 200`
(`test_a_scalar_list_survives_focus_out_with_no_typing` is the existing guard — run it under the mutation).
A mutation that stays green is diagnosed before anything is touched: vacuous test, or mutation aimed at
code the test does not depend on (`settings-editor-learning.md` §8).

## 8. Acceptance criteria

1. **Gate:** `pixi run test-reduction` (it depends on `test-launcher`) returns zero from the repository
   root on the feature tip; both suites' counts quoted. `pixi.lock` restored, not staged.
2. Every row of §6 observed RED then GREEN; every row of §7 recorded with its observed count.
3. **Prose claims are claims** (verify-prose-claims): any comment or commit-body sentence of the form
   "X causes Y" / "cannot happen" introduced by this slug is backed by the command that would falsify it
   and its observation, or is marked *inferred*.
4. No file outside "Files in" changes; no `plans/`, `todo.md` or mutation battery in the diff.
5. **Deployment-shaped acceptance (Integrator, analysis node — the operator-facing clause of charter §4):**
   `pixi run python <ledger>/scripts/editor-real-file-roundtrip.py` over at least three real
   `*_settings.json` (they live under an IPTS's `shared/reduced/`) and one reduced `.dat` the Integrator can
   read → exit 0; the file paths and the script's `sha256` prefixes go in the PR body. A problem line the
   script prints as `note` (a field outside this slug) is **not** a rejection: quote it in the PR body
   and file it as a ledger todo — it is the next slug's evidence. Then, by hand or offscreen: Load one of
   those files in the tab — the panel reads "No problems found." or lists only such notes.
6. **PR body** states the deploy consequence: launcher-only; nothing reaches autoreduction; scientists
   see it when the human merges and re-deploys the review tier (`make-shared-deploy.sh`, charter §5).

## 9. Learnings relied on (quoted; source `agentic/analysis/exp-settings-roi:plans/…`)

- `settings-editor-learning.md` §7: "`bool("False")` is `True`. Any parse of user text into a boolean
  needs an explicit accepted set" — and its mirror here: never widen a file's `"0"` into a boolean.
- §6: "Count the places that switch on a type tag. More than one is a refactor; the copies that disagree
  are the bug you have not found yet." → one encoder, one declaration.
- §4: "Read the consumer before writing the validator. Detection complete (every disagreement is
  reported), resolution minimal" → for `useBS`, 0/1 is what the consumer writes and reads; `2` is still
  reported. **(v2)** v1 applied this sentence to all eight booleans after reading the consumers of one —
  the rejection's "premise that failed". Every reader of every changed field is now enumerated (B8).
- §5: "Give every slot a top-level guard that reports into the UI" → new slots, if any, are `@guarded`.
- §1: "Prefer keyboard activation … it does not encode a layout" → V3 types, it does not click.
- §8: "A mutation that stays green means the test is vacuous OR the mutation missed."
- `campaign-learnings-synthesis.md` §A (a guard matching a value both answers share) → the `True == 1` rule in §6.
- §G generation 4: "`None`-as-a-real-value is a *state* the type does not distinguish" → the state tables in §3.

## 10. Assumptions and open questions (the plan proceeds under each default)

| # | Question | Default |
|---|---|---|
| A1 | Commit a facility settings file as a test fixture? It would publish an IPTS's settings on a public fork. | **No.** The unit fixture is writer-shaped (§6); real files are exercised by the Integrator on an analysis node (§8.5). The human may supply a file cleared for publication. |
| A2 | Should `RBnum` ("Run numbers", runtime-owned) also be read-only? Item 5 names only the two Lambda fields. | Left editable. Question for the scientists; a `fix/` follow-on if yes. |
| A3 | ~~A scalar boolean loaded as `1` is saved as `true`.~~ **Withdrawn (v2).** The premise — "0/1 is what the consumer writes and reads" — is true of `useBS` and false of `useGravity`, which the reducer reads with `is True` (`nr_reduction_calc.py:1079`). | Scalars are left exactly as loaded (B8). Whether `:1079` should read by truthiness is `todo-usegravity-identity-read.md` — the scientists' and a reducer slug's, not this one. |
| A4 | Cell text is lower-case `true`/`false`. | Yes (the human's wording, JSON's spelling); `editor-combos` replaces the text cell with a two-item drop-down. |
| A5 | An unset (`None`) `useBS` entry is saved as `null`, which the reducer reads as "off". | Unchanged and out of scope; noted for `editor-combos`, which gives the cell a definite choice. |

## Revision history

v1 — this document as dispatched at `triage/editor-load-fidelity` @ `0c0a126`.

### v2 — 2026-10-02 (retry 1; the work order for `triage/editor-load-fidelity-v2`)

**Rejection.** `review/editor-load-fidelity` @ `8b62952` — `todo.md` at that commit, finding B-1 (design domain,
harm clause): a hand-written `"useGravity": 1` loads silently as `True` and saves as `true`, switching gravity
correction on, because the reducer reads that field with `is True` (`nr_reduction_calc.py:1079`). Not
infrastructure. **The defect was in this plan** (v1's A3 and the scalar column of §3's table), not in the
implementation, which did what v1 prescribed. Reproduced by the Analyst at the base: `:1079` reads
`if self.config.useGravity is True:`; the other readers are as the Integrator's table lists them, plus three
that format the value into text (`save_reduced_data.py:79-80,97-98`, `web_report.py:430-431`,
`new_reduction_template_reader.py:199`).

**What stands (do not redo; `todo.md` "What passed").** Everything about `useBS` (B2 for it, B3, B4, B7), the
runtime record (B5, B6), the diff scope, and the v1 tests and mutation rows that concern them.

**What changes (behaviour — B1, B2 as rewritten in §3, and B8).**

| Value in a scalar boolean (`Normalize`, `AutoScale`, `plotON`, `plotQ4`, `save8col`, `useGravity`, `use_emission_time`) | v1 | v2 |
|---|---|---|
| `True` / `False` | quiet; saved `true`/`false` | unchanged |
| `1` / `0` — loaded from a file, from a dict, or held by an injected config | quiet; held as `bool`; saved `true`/`false` | **reported by name; held as loaded; saved as loaded** |
| other int, float, str, list, `None` | reported / unset | unchanged |

`useBS` entries: unchanged from v1 in every state. One declaration decides where `1`/`0` counts as a boolean —
the integer-encoding attribute v1 introduced; no field-name test in the document or the view. How the type
check learns it (it has no field in hand today) is the Developer's choice; the three call sites of the "is this a
boolean spelling" helper each get a frame row.

**Guard (the dimension the fix must not freeze).**

| # | Test (names are suggestions) | RED at `9fe4184` | GREEN |
|---|---|---|---|
| R1 | load → save is the identity on every scalar boolean: parametrized over **the scalar booleans derived from `FIELD_SPEC`** (not a typed list) × {`1`, `0`, `True`, `False`}; write `{name: value}`, `from_file`, `save`, read the saved text; assert `type(saved) is type(value)` **and** `saved == value` | the `1`/`0` rows of all seven: saved type is `bool` | B8 |
| R2 | the same matrix: for `1`/`0` a problem line names the field and does not contain `1/0` as an accepted spelling; for `True`/`False` no line names it | `1`/`0` rows: no line | B1 |
| R3 | the reduction reads the saved file as it read the source: for `useGravity` × {`1`, `0`, `True`, `False`}, `(json_to_config(source).useGravity is True) == (json_to_config(saved).useGravity is True)` — the rejection's reproduction as a test | row `1` | B8 |
| R4 | an injected config holding an integer scalar boolean is reported (`SettingsDocument(config)`, no load) | no line | B1 |
| R5 | the derived scalar-boolean set is exactly the seven names (a pin on the derivation R1–R2 iterate, so an eighth boolean cannot slip past unexamined — and when one is added, its reader is read before the pin is updated) | passes — a pin | stays |
| R6 | `useBS` entries × {`1`, `0`, `True`, `False`}: saved entry `type` is `int`; `bool(saved) == bool(source)` and `(saved == 1) == (source == 1)` | passes — v1 behaviour, now pinned against its readers | stays |
| R7 | view: Load a file holding `"useGravity": 1` through the tab → the panel names `useGravity`; Save → the saved text holds `"useGravity": 1` | panel quiet; saved `true` | B8 |

Any v1 test that asserted the withdrawn behaviour (a scalar `1` loading quietly or saving as `true`) is rewritten
to the v2 row, in the RED commit, with the old assertion quoted in the commit body.

**Mutations (each recorded as `<mutation> → <test> -> N failed`).**

| # | Mutation | Must red |
|---|---|---|
| N1 | load canonicalizes every declared boolean again (the integer-encoding restriction removed) | R1 — on **all seven** scalars' `1`/`0` rows, not `useGravity` alone; R3 row `1`; R7 |
| N2 | validation accepts `1`/`0` for every declared boolean again | R2, R4 |
| N3 | the restriction inverted (scalars canonicalized, `useBS` not) | v1's T2 and V1, and R1 |
| N4 | the scalar message offers `1/0` | R2 |

Then the whole v1 battery again (ledger `scripts/mutate-editor-load-fidelity.py`, 22 rows): a row whose expected red
changed because of v2 is re-aimed and the change recorded; the battery stays out of the PR diff.

**Acceptance (v2).** §8 as written, with: the gate from the repository root; `todo.md` removed from the
feature branch in its own commit before `qa/`; §8.5 re-run with the current script (count lines are notes) —
exit 0 on the same real files; R3's four rows quoted in the PR body. The PR body carries the Integrator's
advisories verbatim (the scalar checkbox's `bool(value)` display, the repeated encoder call, the
`runtime_owned`-keyed exemption, file sizes, V4/V5 coverage) — none is in this revision's scope.
