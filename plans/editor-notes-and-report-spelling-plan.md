# Plan: `editor-notes-and-report-spelling` — every reducer-filled list gets the same note, in words that do not read as a problem; the change report spells a value the way the file does

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-notes-and-report-spelling` (refs `triage/editor-notes-and-report-spelling`,
`feature/…`, `qa/…`) · **Status:** READY — v1 (attempt 1 of N = 3) — dispatched 2026-10-05 under the posture's **stacking by file overlap** rule (merged
2026-10-05, `ec10742`; it retired the 2026-10-04 lane line and the "merged after #40" staging this plan was written for): the plan's
files overlap **one** open branch — `launcher/apps/settings_editor.py` is changed by `feature/editor-sections` (#40, PASS) — so the slug
**stacks on it** (rule (3)); the trigger was #40's PASS, already on the bus ·
**Base:** `agentic/feature/editor-sections` @ `efa1b81` — **overlap at dispatch** (`git diff --name-only agentic/exp-review...agentic/feature/<x>`,
tests excluded, `exp-review` @ `5a8742d`): `feature/editor-sections` {`settings_editor.py` ∩}; `feature/test-suite-warnings`,
`feature/launcher-env-outside-xdg-cache`, `feature/rereduction-headers-land`: none · **PR target:** `feature/editor-sections` on the fork,
**draft** (retargeted to `exp-review` by the human's merge of #40) · **Stack:** #40 → **this slug** → `editor-ipts-inference` (K2) →
`editor-sections-followup` (K3, when charter-added); the Developer cuts `feature/editor-notes-and-report-spelling` `--no-track` from
`agentic/feature/editor-sections` and regular-merges it forward before every `qa/` push; the Integrator opens the draft PR
`--base feature/editor-sections` · **Depends on:** the editor lane merged (`settings_document.py` and
`settings_editor.py` are rewritten by #39/#40) · **Review domains:** ui-aspects, test (block) · **Kind:** launcher / settings model —
not reduction-path (no reducer file; `save()`'s encoding unchanged) ·
**Sources:** `[human, 2026-10-04: "Please schedule the fix/editor-notes-and-report-spelling slug so that it lands inside Group 1-3 that we
are preparing. I suppose that means it should be merged after PR#40, right? Or as you deem proper after considering it."]`; the Advisor's
recommendation (V1-28; `plans/review-pr38-second-round.md`; `todo-editor-implied-default-notes-and-report-spelling.md`); the human's PR #38
review with a from-scratch file.

## Declared scope

**Files in:** `src/lr_reduction/settings_document.py` (`notes()`), `launcher/apps/settings_editor.py` (`refresh_report()`'s "Changed from
the seed" lines; one shared rendering helper), `tests/unit/lr_reduction/test_settings_document.py`, `launcher/tests/test_settings_editor.py`.

**Behaviours in** (K1–K4, §3). **Explicitly OUT:** what `save()` writes (`_encode_for_file`: `[]` for an all-unset reducer-filled list,
`1`/`0` for `int_encoded` booleans — unchanged, pinned by `editor-load-fidelity`/`editor-angle-count`); the Angles-table cell text
(`_cell_text`: `true`/`false`); which fields are `default_if_empty`/`broadcast_ok` (declared in `field_spec.py`); the boolean-synonym
question (decision D, held with Group 5); `validate()` and its problem lines; the surplus-entry note (unchanged).

## 1. Request

The human, reviewing PR #38 with a from-scratch file (`useBS: []`, `method_per_run: []`): the panel notes that `useBS` "is unset, so the
reduction uses its default" but says nothing for `method_per_run`, which the reduction also fills (`meanTheta`); the note reads like a
problem to clear, and the only way to clear it is to make the value explicit; and after choosing `true` on an angle the cell shows `true`,
"Changed from the seed" prints `[True, True, True]`, and the saved file holds `[1, 1, 1]` — one value, three spellings.

## 2. Verified facts at `feature/editor-sections` @ `efa1b81` (= the editor content of `exp-review` after #40; **re-seal at dispatch**)

| # | Fact | Evidence |
|---|---|---|
| F1 | **Six per-angle lists are filled by the reducer when empty**, declared on the `Field`: `useBS` (`default_if_empty`, `int_encoded`, `reducer_default=1`), `tof_min` (0), `tof_max` (100000), `ThetaShift` (0), `ScaleFactor` (1) — all `default_if_empty=True` — and `method_per_run` (`broadcast_ok=True`, `reducer_default="meanTheta"`, "an empty list defaults to meanTheta"). | `field_spec.py:531-535, 551-559, 568-573`; the reducer: `nr_reduction_calc.py:99-110` (`if not self.config.<name>: … = [<default>] * n_settings`) and the `method_per_run` broadcast at `:76-80`. |
| F2 | **`notes()` emits the "unset → default" note for the boolean one only.** | `settings_document.py:630-666`: the condition at `:660` is `field.default_if_empty and field.element_type == "bool" and defining and all(entry is None for entry in value[:count])`; the text at `:663-664` hard-codes "on (1) at every angle (nr_reduction_calc.py:102-103)". So `useBS: []` is noted; `method_per_run: []`, `ThetaShift: []`, `ScaleFactor: []`, `tof_min: []`, `tof_max: []` are not, though the reduction fills each the same way. |
| F3 | **The note's words read as a defect** ("is unset, so the reduction uses its default") and give no way out but to write a value — while re-choosing the implied value is the identity (C9′/D-b, `editor-combos` v3) and the human ruled that in. | `:663`; the human's PR #38 comment; `plans/review-pr38-second-round.md` finding 1. |
| F4 | **Three spellings of one boolean list.** The cell renders `true`/`false` (`_cell_text`, `settings_editor.py:867-880`: `fs.as_boolean(value)` → `"true"`/`"false"`); the report prints Python `repr` (`refresh_report`, `:1175`: `f"  - {name}: {before!r} -> {after!r}"` → `[True, True, True]`); the file holds `[1, 1, 1]` (`_encode_for_file`, `settings_document.py:705-720`: `int_encoded` lists written `1`/`0`). | Read at `efa1b81`; the human's measurement (todo Evidence): cell `'true'`, report `- useBS: [] -> [True, True, True]`, `save()` → `[1, 1, 1]`. |
| F5 | The file's spelling is already computable without saving: `_encode_for_file(values, count)` is a static method over a dict. | `settings_document.py:705`. |
| F6 | The existing note tests pin the `useBS` note and its clearing. | `test_settings_document.py:1504` `test_an_unset_background_switch_is_noted_as_the_reductions_default`, `:1672`; `test_settings_editor.py:207` `test_changed_vs_seed_report_lists_edits`, `:625`, `:664`. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| K1 | **One note per reducer-filled list that is unset at every angle the reduction uses** — every `default_if_empty` or `broadcast_ok` field whose entries below `reduction_angles` are all `None`, when angle-defining entries exist (as today). Not only booleans. The words come from the `Field`: *"<label> (<name>) is not set; the reduction will use <reducer_default> at every angle — leave it, or choose a value to write it explicitly."* `reducer_default` is rendered in the **file's** spelling (`1` for `useBS`, `meanTheta` for `method_per_run`, `0` / `100000` / `1` for the others). No hard-coded field text; no reducer line numbers in user-facing text. |
| K2 | **The note is not a problem**: it stays in "Notes:", never in "Problems:"; `validate()` is unchanged; a document with only such notes still reads "No problems found." |
| K3 | **"Changed from the seed" spells a value the way the file does**: `before` and `after` are rendered through **one** helper that applies `_encode_for_file`'s rules to a single field's value (`int_encoded` booleans → `1`/`0`; an all-unset reducer-filled list → `[]`; everything else as JSON would write it — `json.dumps`, not `repr`, so strings are double-quoted and `None` is `null`). The Angles-table cell keeps `true`/`false` (OUT) — **two** spellings remain, the cell's and the file's, and the report is the file's. |
| K4 | **One rendering, one place**: the helper lives beside `_encode_for_file` in `settings_document.py` (Qt-free), and `refresh_report` calls it; `_cell_text` is untouched. A later change to the file encoding changes the report with it. |

**Types and states** (per field × held value): field ∈ {`default_if_empty` bool (`useBS`), `default_if_empty` numeric (`ThetaShift`,
`ScaleFactor`, `tof_min`, `tof_max`), `broadcast_ok` enumerated (`method_per_run`), any other per-angle list (`RBnum`, `DBname`, `BkgROI`…),
scalar}; value ∈ {`[]`, all-`None` below count, partly set, fully set, surplus entries}. Note cell: a note **iff** reducer-filled and all-`None`
below count and defining entries exist; never for other lists or scalars. Report cell: file spelling for every per-angle list and scalar
(`true` → `1` only where `int_encoded`; `False` scalar → `false`; `"detector_angle"` quoted; `None` → `null`; `[]` for an all-unset
reducer-filled list).

**Operation × state (every cell a required outcome, each named by a test — U1–U4, V1–V3):**

| Operation | `useBS: []` | `method_per_run: []` | `ThetaShift: []` | `RBnum`-defined, `useBS` partly set | fully set |
|---|---|---|---|---|---|
| Load (file with angle-defining entries) | note, K1 words with `1` | note with `meanTheta` | note with `0` | **no** note (partly set is `validate()`'s, as today) | no note |
| Load (no angle-defining entries) | no note (no reduction to describe) | no note | no note | — | — |
| choose the implied value on one angle (re-choose) | identity: value unchanged, note stays, no "Changed" line (C9′) | identity | identity | — | — |
| choose another value on one angle | note gone; "Changed" line `useBS: [] -> [0, 1, 1]` (file spelling) | `method_per_run: [] -> ["constantQ", "meanTheta", "meanTheta"]` | `ThetaShift: [] -> [0.5, 0, 0]` | — | — |
| Save after that | file holds exactly what the report printed | same | same | — | — |
| Save with the list still `[]` | `[]` written (unchanged behaviour); note persists after reload | same | same | — | — |
| panel header | "No problems found." + "Notes:" | same | same | "Problems:" names the partly-set list; no note | — |

## 4. Files to change

| File | Change |
|---|---|
| `settings_document.py` | `notes()`: the condition drops `element_type == "bool"` and gains `broadcast_ok`; the text from `Field.label`/`name`/`reducer_default` via the new helper; the helper `file_spelling(field, value)` (suggested) built on `_encode_for_file`'s rules |
| `settings_editor.py` | `refresh_report()`: `{before!r} -> {after!r}` → the helper's text |
| tests | §6 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | the scientists' from-scratch flow: new file → add angles → leave `useBS`, `method_per_run` unset → Save → Load | both notes present, worded as information; "No problems found." |
| common | choose `true` on one `useBS` angle | report `useBS: [] -> [1, 1, 1]`; cell `true`; file `[1, 1, 1]` — report = file |
| edge | a `method_per_run` of one entry (`["constantQ"]`, broadcast) | no note (not unset); report prints `["constantQ"]` |
| edge | a scalar boolean change (`useGravity`) | report `useGravity: false -> true` (file spelling), not `False -> True` |
| edge | a string scalar | report `"detector_angle"` quoted as the file writes it |
| pathological | a reducer-filled field with no `reducer_default` declared | import-time or test failure naming the field — never a note with `None` in it |
| pathological | `reducer_default` for `useBS` rendered `True` or `1.0` | U2 reds (`1`) |
| pathological | the note placed under "Problems:" | V3 reds |

## 6. Red-Green TDD seed

| # | Test | RED at the base |
|---|---|---|
| U1 | `notes()` × F1's six fields × {`[]`, all-`None` below count}: one note each, K1 words, `reducer_default` in file spelling; partly/fully set → none; a non-reducer-filled list → none; no defining entries → none | five of six fields get no note |
| U2 | every `default_if_empty`/`broadcast_ok` field in `FIELD_SPEC` has a `reducer_default` (a pin), and the note text never contains `None`, `True`, `False`, or a `.py:` reference | the hard-coded text contains a reducer reference |
| U3 | `file_spelling(field, value)` equals the value's JSON text in `save()`'s output for: `int_encoded` bool lists, numeric lists, string lists, scalars (`False`, `"detector_angle"`, `None`), and an all-unset reducer-filled list (`[]`) — asserted by saving a document and comparing per key | helper absent |
| U4 | the `useBS` note tests (F6) still pass with the new words (updated expectations: the words, not the behaviour) | passes — pins |
| V1 | the panel after Load of the human's from-scratch file (committed as a fixture): two notes (`useBS`, `method_per_run`), under "Notes:", "No problems found." present | one note |
| V2 | re-choose the implied value → identity (no "Changed" line; note stays); choose another → the "Changed" line equals the file's spelling (`[0, 1, 1]`), and after Save the file's text for that key equals the printed list | report prints `[False, True, True]` |
| V3 | `useGravity` toggled → `useGravity: false -> true`; a theta choice → `useCalcTheta: false -> "sample_angle"` | repr spellings |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| the `element_type == "bool"` condition restored | U1 (five fields) |
| `broadcast_ok` left out of the condition | U1 (`method_per_run`) |
| note text hard-coded for one field | U1 (words), U2 |
| `reducer_default` rendered by `repr` | U2 / U1 (`1` not `True`) |
| report rendered by `repr` again | V2, V3 |
| a second renderer in `settings_editor.py` instead of the shared helper | U3 (the helper is the one `save()` agrees with) + a one-definition grep |
| the note emitted under "Problems:" | V1 |

Frame: one helper, defined once in `settings_document.py`, used by `notes()` and `refresh_report()`; `_encode_for_file` and `_cell_text`
unchanged (their tests are the pins).

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root on the feature tip.
2. §6 RED→GREEN; §7 recorded per row.
3. Deployment-shaped acceptance (Integrator, real tab, offscreen — **no login shell; reproduce any hook effect in a scratch cache**): the
   human's from-scratch file → both notes read as information; choose `true` on one angle → the report line and the saved file agree
   character for character on that key; the `useGravity` and theta rows.
4. PR body: launcher-only; the two spellings that remain (cell `true`, file/report `1`) stated plainly, with the reason (the cell's words are
   the scientists', the file's are the reducer's); the boolean-synonym decision (D) named as the held item this does not touch.

## 9. Learnings relied on

- `editor-combos` v3 C9′/D-b (`[human]`): re-choosing the implied value is the identity → K1's "leave it, or choose a value".
- `editor-load-fidelity` v2 B8 and `editor-angle-count` G7: load → save identity and `[]` for all-unset reducer-filled lists — the file
  spelling is already law; the report joins it (K3).
- `campaign-learnings-synthesis.md` §C (one behaviour, two implementations): the report and the file rendered the same value differently →
  one helper (K4).
- The campaign's standing lesson: every cell of §3's table is named by a test; §7's tests observe through the path the mutation breaks.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | Scheduling: stacked on #40 now, or after #40 merges? | **After #40 merges** (the human: "merged after PR#40" — the staging order guarantees it; a fifth stack link would need the posture's stacked-lane rule extended by governance and buys hours at most while the Developer is on the deploy slug). If the human would rather stack it, one posture line and this header change. |
| A2 | The cell keeps `true`/`false` while the report/file say `1`/`0`. | Yes (OUT) — the cell is the scientists' word; changing it is the boolean-synonym question (D). |
| A3 | Note wording. | K1's sentence; the human may re-word at the gate — a label-only change. |

## Revision history

v1 — authored 2026-10-04 against `feature/editor-sections` @ `efa1b81` (the editor content of `exp-review` after #40), **staged** behind
`editor-sections` merged (`[human, 2026-10-04: "schedule … so that it lands inside Group 1-3 … merged after PR#40, right?"]`; A-57).
**Dispatched 2026-10-05 stacked on `feature/editor-sections` @ `efa1b81`** under the stacking-by-file-overlap rule (posture `ec10742`;
A-65): §2 was sealed at `efa1b81` already — no citation moved; the overlap recorded in `Base:`. The human's "merged after #40" still holds:
the stack merges in order.
