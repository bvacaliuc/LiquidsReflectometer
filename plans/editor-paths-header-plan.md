# Plan: `editor-paths-header` — IPTS and the two input paths at the top of the tab; derived paths are shown, never written

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-paths-header` (refs `triage/…`, `feature/…`,
`qa/editor-paths-header`) · **Status:** READY — v1 (attempt 1 of N = 3) — **stacked** `[human, 2026-10-04, posture]`: dispatched 2026-10-04 when `editor-defaults-and-theta`'s draft PR #38 opened (its v2 PASS, I-24); §2 **re-sealed against `agentic/feature/editor-defaults-and-theta` @ `3c4ec39`** (PR #38's head; first sealed at `7b6d6b9` — every `settings_editor.py` / `field_spec.py` citation moved, one CORRECTION, F8) ·
**Base:** `agentic/feature/editor-defaults-and-theta` @ `3c4ec39` · **PR target:** `feature/editor-defaults-and-theta` on the fork, **draft** (retargeted by the human's merges down the stack) ·
**Stack** (posture, "Stacked editor lane" — it governs; this line points): `launcher-test-teardown` (#37) → `editor-defaults-and-theta` (#38) → **this slug** → `editor-sections`; the Developer cuts `feature/editor-paths-header` `--no-track` from `agentic/feature/editor-defaults-and-theta` and regular-merges it forward before every `qa/` push; the Integrator opens the draft PR `--base feature/editor-defaults-and-theta` ·
**Depends on:** `editor-defaults-and-theta` (same files), and `editor-combos` (its direct-beam list follows
the resolved path this header edits) · **Review domains:** ui-aspects, test (block) · **Kind:** launcher —
not reduction-path · **Sources:** scientists' item 6; Q5 (`[human, 2026-10-02]`); charter §3 row.

## Declared scope

**Files in:** `launcher/apps/settings_editor.py`, `src/lr_reduction/settings_document.py` (Qt-free helpers:
derived-path text, IPTS normalisation), `launcher/tests/test_settings_editor.py`,
`tests/unit/lr_reduction/test_settings_document.py`. `field_spec.py` only to mark which fields the header
owns (one attribute or one tuple).

**Behaviours in** (P1–P6, §3). **Explicitly OUT:** `nr_reduction_config.py` (its path properties are read,
not changed); the two output paths (`_Spath_override`, `_BINpath_override`) — they stay in the list, in the
merged "naming and paths" section `editor-sections` builds; section order and collapsing; checking that a
path exists on disk as a *problem line* (a path may be valid on the analysis cluster and absent on the
machine running the editor); `file_batch.py` (its "Update defaults" writes resolved paths — the behaviour
Q5 declines for this tab; it is not touched).

## 1. Request

> 6. At the top of the window above the table setup there should be a smarter way to setup the default file
> paths similar to the top of the file_batch.py tab or the json_settings_builder.py tab. These are the items
> from the 'Paths' section of the existing list (NeXus path and direct-beam path) as well as IPTS from
> 'Output naming'. They should be read from a loaded settings file, or if an IPTS number is entered then the
> paths for the other defaults will be automatically filled with the defaults (e.g.
> /SNS/REF_L/IPTS-{}/nexus, and /SNS/REF_L/IPTS-{}/shared/transmission).

Q5: "display only; write an override only when the user edits the field, because written overrides freeze
absolute paths."

## 2. Verified facts at the base `3c4ec39` (first measured at `7b6d6b9`; **re-sealed 2026-10-04** — line numbers are `3c4ec39`'s)

| # | Fact | Evidence |
|---|---|---|
| F1 | The derivation already exists in the config class. | `nr_reduction_config.py:112-113` `base_path` = `Path("/SNS/REF_L") / self.experiment_id`; `:126-129` `NEXUSpathRB` = override or `base_path / "nexus"`; `:131-134` `DBpath` = override or `base_path / "shared" / "transmission"`; the overrides start `None` (`:41-42`) and the public setters write them (`:140-145`). `NRReductionConfig().NEXUSpathRB` → `/SNS/REF_L/nexus` when `experiment_id == ""` (run 2026-10-02; the properties are unchanged since). |
| F2 | A written override is frozen into the file; an unset one is re-derived from `experiment_id` on load. | `save_config_json` docstring (`new_reduction_from_file.py:476`, `:490-491`): "the private `_*_override` names **re-derive** their paths from `experiment_id` on load, whereas the public form freezes the resolved absolute path into the file". |
| F3 | Today the three fields are ordinary editors far down the list. | `experiment_id` in "Output naming" (`field_spec.py:580-582`, label "IPTS"), the four overrides in "Paths" (`:594-602`); built by the generic group loop (`settings_editor.py:547-559`); the tab's layout is toolbar → splitter(angles, scalars, report) (`:457-465`), then `set_document` (`:470`). |
| F4 | `experiment_id` is a directory name. | `Field("experiment_id", "IPTS", NAMING, "str", "", …, no_separators=True)` (`field_spec.py:580-582`; `/` and `\` reported, `:355-360`); `file_batch.py:289-291` normalises a bare number to `IPTS-<n>` before use. |
| F5 | `file_batch.py`'s header writes resolved paths into its edits. | `file_batch.py:284-308` (`update_defaults_from_experiment` → `:300` `setText(str(cfg.NEXUSpathRB))`, `:304` `DBpath`, `:308` `Spath`). The model for the *look*, not for the write behaviour. |
| F6 | One editor per field is an invariant of the tab, and one site renders a value. | `self.editors[field.name] = editor` (`settings_editor.py:557`); `refresh_scalars` (`:959-961`) iterates `self.editors` into `_show` (`:630`: "The ONLY place a value becomes widget state"; signals blocked while displaying). Two widgets for one field would have to be kept in step by hand. |
| F7 | **Hazard the header closes:** clearing IPTS today stores `None`, and the path properties then raise. | A text field is a `QLineEdit` (`:604`) whose `editingFinished` → `_on_scalar_edited` (`:623-625`, `:793-796`) stores `fs.get(name).coerce(widget.text())`; `_coerce_typed` turns `""` into `None` ("Empty means unset (`None`)"). With `experiment_id = None`, `base_path` (`Path("/SNS/REF_L") / None`) raises `TypeError` — `candidates()`'s docstring names exactly this (`settings_document.py:460`). → P5: empty IPTS is stored as `""`, never `None`. |
| F8 | **CORRECTION** (the staged plan said the direct-beam listing would read the new derived helper, and §7 said "re-pointed to it" — wrong). The listing reads the **effective** path. | `SettingsDocument.candidates` (`settings_document.py:449-476`) lists `getattr(self._config, "DBpath")` — override if set, else derived — on each cell open (`settings_editor.py:373-386`), nothing cached. That is the right source and **stays**: an override must change what the cell lists. The header's helper answers a different question ("what if the override were unset?") and both draw on the same `nr_reduction_config` properties (CPKT `derived-identifiers.md`). |
| F9 | The accepted shapes are already decided. | `_path_problem` rejects `..` only — an absolute path is the overrides' normal shape, "exactly what `QFileDialog.getExistingDirectory` returns" (`field_spec.py`, docstring); the type rule for `"path"` is `str` (`:480-481`). |
| F10 | The tab's default document is `SettingsDocument.for_new_file()` (`settings_editor.py:448`; `settings_document.py:95`), in which `experiment_id` is `""` and both overrides `None`. | So a fresh tab is the "no IPTS" state of §3's table. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| P1 | A header above the Angles table holds three controls: **IPTS**, **NeXus path**, **Direct-beam path**. They are *the* editors for `experiment_id`, `_NEXUSpathRB_override`, `_DBpath_override` — moved, not duplicated: each name appears once in `self.editors`, and no longer in the scrolling list. |
| P2 | **Derived paths are displayed, not stored.** While an override is unset, its control shows the derived path as placeholder-style text (visibly not a typed value) and the document holds `None`. Changing IPTS updates both displays immediately. |
| P3 | **An override is written only by an explicit edit of that control** (typing, or choosing a folder with its Browse button). Loading, displaying, changing IPTS, or tabbing through the control writes nothing. |
| P4 | **Clearing a control returns it to derived**: the document holds `None` again and the derived path is displayed. |
| P5 | IPTS entry: a bare number `36119` is stored as `IPTS-36119`; `ipts-36119` as `IPTS-36119`; anything else is stored as typed and left to `validate()` (separators and `..` are already reported). Empty → `""`, and the path displays say that no IPTS is set rather than showing `/SNS/REF_L/nexus`. |
| P6 | Load fills the header from the file: IPTS from `experiment_id`; each path shows the file's override if it has one (as a real value), else the derived display. |

**Types and states** (per path control × document value):

| `_…_override` holds | control shows | after IPTS change | saved |
|---|---|---|---|
| `None`, IPTS set | derived path, as placeholder | follows the new IPTS | `null` |
| `None`, IPTS `""` | "set an IPTS or type a path" placeholder | — | `null` |
| a string (typed, browsed, or loaded) | that string as a value | **unchanged** — an explicit path does not follow IPTS | the string |
| `""` after the user clears it | derived (P4) | follows | `null` |
| a non-string (`5`, a list — malformed file) | its text; `validate()` reports the type | unchanged | as held |

The derivation text comes from `NRReductionConfig`'s own properties through a Qt-free helper on the
document (it must not re-implement `/SNS/REF_L/…`): the helper answers "what would the reducer use if this
override were unset?". **(CORRECTION at the re-seal, F8)** The direct-beam candidate listing of `editor-combos`
(`SettingsDocument.candidates`) keeps reading the *effective* `DBpath` property — override if set, else derived — and
is **not** re-pointed at the helper; the two are different questions answered from the same config properties.
A header edit of the direct-beam path therefore changes what the next cell open lists, with no new wiring.

**Operation × state (every cell is a required outcome, and every cell is named by a test — V12).** Held state of a path
control ∈ {**D** override `None` with IPTS set; **N** override `None` with IPTS `""`; **S** a string override (typed,
browsed or loaded); **X** a non-string override from a malformed file}:

| Operation | D | N | S | X |
|---|---|---|---|---|
| Load / display | derived path as placeholder; `text() == ""`; document `None` | "set an IPTS or type a path" placeholder; `None` | the string as text; document the string | its text; `validate()` reports the type |
| type an IPTS (`36119` / `ipts-36119`) | document `IPTS-36119`; placeholder follows; override still `None`; one "Changed" line (`experiment_id`) | same (N → D) | override **unchanged**; the other control follows | unchanged |
| clear IPTS | document `""` (**never `None`**, F7); N's placeholder; no exception | identity | override unchanged | unchanged |
| type a path | override = the text; S | same | the new text | the text (X → S) |
| clear the path | identity (already `None`) | identity | override `None` (**not `""`**); derived display returns (S → D) | `None` (X → D) |
| focus in and out with no typing | **no write**: `changed_vs_seed()` empty, override `None` | no write | no write; the string intact | no write; the value intact |
| Browse → a folder | override = the folder (S) | same | replaced | replaced |
| Browse cancelled (`""`) | no write | no write | no write | no write |
| Save | `null` | `null` | the string | as held |
| Load a second file (none / with an override) | shows the second file's state; nothing of the first | same | same — A's text gone when B has none (V7) | same |

## 4. Files to change

| File | Change |
|---|---|
| `settings_document.py` | `derived_path(name)` (suggested) built on the config's properties with the override temporarily disregarded — without mutating the document; `normalise_experiment_id(text)` |
| `settings_editor.py` | the header panel between toolbar and splitter; the three fields excluded from the generic list; Browse buttons (`QFileDialog.getExistingDirectory`); refresh of derived displays on IPTS change and on `set_document` |
| `field_spec.py` | the marker for header-owned fields |
| tests | §6 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | type `36119` in IPTS | document `IPTS-36119`; both paths display `/SNS/REF_L/IPTS-36119/nexus` and `…/shared/transmission`; both overrides still `None`; saved file has `null` for both |
| common | load an autoreduce file with no overrides | header shows its IPTS and the derived paths; "Changed from the seed" empty |
| common | type a NeXus path | override set; survives an IPTS change; saved |
| edge | load a file with an override, then change IPTS | the override stays; the other path follows |
| edge | clear a typed path | `None`; derived display returns |
| edge | focus in and out of a derived display without typing | no write (the base's `data_x_range` focus-out bug is the precedent) |
| edge | Browse cancelled (`""`) | no write |
| edge | Load file A (override set) then file B (none) | control shows B's derived path, not A's text |
| edge | direct-beam path changed here | the next cell open lists the folder the document resolves **now** — `candidates()` reads the effective `DBpath` (F8); one header leg (V11) beside `editor-combos`' V10 (`test_the_direct_beam_list_follows_the_folder`, `test_settings_editor.py:1030`) |
| edge | clear IPTS on a loaded file | document `""`; both displays say no IPTS is set; **no `TypeError`** from the path properties (F7); `candidates()` still answers `([], 0)` |
| pathological | IPTS `../x` or `/abs` | stored as typed; `validate()` reports it; the display does not present a traversed path as valid |
| pathological | override is a non-string in the file | shown as text, reported; no exception leaves a slot |
| pathological | path does not exist on this machine | accepted silently (it may exist on the cluster); no problem line |

## 6. Red-Green TDD seed

| # | Test (names are suggestions) | RED at the base |
|---|---|---|
| U1 | `derived_path` for both names with IPTS set / unset / override set (answers the *unset* derivation even while an override is held); the document is not mutated (`to_dict()` equal before and after) | helper absent |
| U2 | `normalise_experiment_id`: `"36119"`, `" 36119 "`, `"ipts-36119"`, `"IPTS-36119"`, `""`, `"proposal_x"` | helper absent |
| V1 | the header exists above the table and holds the three editors; none of the three names is in the scrolling list; each name maps to exactly one widget | editors live in the list |
| V2 | typing an IPTS number updates both displays and leaves both overrides `None` (`is None`) | — |
| V3 | after V2, Save writes `null` for both overrides (assert on the JSON text) | — |
| V4 | typing a path sets the override; a later IPTS change leaves it | — |
| V5 | clearing returns `None` and the derived display | today stores `None` via `coerce("")` but shows nothing |
| V6 | focus-out with no typing writes nothing (`changed_vs_seed()` empty) — on a derived display and on a loaded override | — |
| V7 | Load A (override) then B (none) shows B's derived path | — |
| V8 | Browse returns a folder → override set; Browse cancelled → no write (patch `QFileDialog.getExistingDirectory`) | no Browse |
| V9 | a derived display is distinguishable from a typed value by a queryable property (e.g. `text() == ""` and `placeholderText()` set) — the test states which | — |
| V10 | clearing IPTS stores `""` (`== ""` and `type is str`, not `None`); the displays say no IPTS; `document.candidates("DBname") == ([], 0)` and no exception | the base stores `None` and `NEXUSpathRB` raises (F7) |
| V11 | typing a direct-beam folder (a `tmp_path` holding `a.txt`) in the header → the next `candidates("DBname")` lists `a.txt`; clearing it → the derived folder's listing (`([], 0)` for a missing IPTS folder) | — (guard: the listing keeps the effective path, F8) |
| V12 | §3's operation × state table, parametrized over the four held states × the operations, each cell asserting the document value **and its type**, the control's `text()` / `placeholderText()`, `changed_vs_seed()` and the report state; the docstring names the table | the states D/N/S/X have no tests |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| IPTS change writes the derived paths into the overrides (the `file_batch` behaviour) | V2, V3 |
| derived display implemented with `setText` | V3, V6, V9 |
| override does not survive an IPTS change | V4 |
| clearing stores `""` instead of `None` | V5 (`is None`), V3 |
| header editors duplicated instead of moved (second widget left in the list) | V1 |
| display not refreshed on `set_document` | V7 |
| `derived_path` returns the override when one is set | U1 |
| `derived_path` re-implements the literal `/SNS/REF_L/…` (replace the property call with the string) — then change `base_path` in a test double | U1's "follows the config class" leg (required: the helper is exercised against a subclass whose `base_path` differs) |
| bare-number normalisation removed | U2, V2 |
| Browse-cancel writes `""` | V8 |
| clearing IPTS stores `None` (the base's `coerce("")`) | V10 |
| `candidates()` re-pointed at `derived_path` (lists the derived folder while an override is held) | V11 (override set to a folder with files; the derived folder absent) |
| IPTS normalised on display but stored as typed | U2, V2 (document value), V3 (JSON text) |

Frame: `derived_path` call sites — the header refresh (two controls; one row each). **(CORRECTION, F8)** The
direct-beam candidate listing is *not* re-pointed: `candidates()` keeps `getattr(self._config, "DBpath")`, and the
mutation above guards that. The exclusion of header-owned fields from the generic list is one site
(`_build_scalar_panel`'s group loop, `settings_editor.py:547-559`); the header's text controls write through the
same `_on_scalar_edited` → `document.set` path as every scalar, or through one header-specific slot — either way
one write site per control, and V6 runs against the real focus path on a shown tab.

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root on the feature tip.
2. §6 RED→GREEN; §7 recorded per row.
3. Prose claims verified or marked inferred — in particular "written only on explicit edit" is shown by V2,
   V3, V6 and by the diff of a load→save of a real file (criterion 4), not asserted.
4. Deployment-shaped acceptance (Integrator, analysis node): load a real autoreduce settings file → the
   header shows its IPTS and derived paths; Save to a new name → `diff` of the two JSON files shows no
   `_*_override` key changed from `null`; enter another real IPTS → the direct-beam drop-down lists that
   IPTS's files; **clear IPTS → no traceback, the displays say no IPTS, Save writes `"experiment_id": ""`** (F7).
5. PR body: launcher-only; visible after merge + re-deploy of the review tier.

## 9. Learnings relied on

- `test_save_config_json.py` / `save_config_json` docstring (base): the private override names re-derive;
  the public form freezes — the reason for Q5.
- `settings-editor-learning.md` (the `data_x_range` case, in `_show`'s docstring at the base): a display
  path that differs between construction and refresh corrupted a field "by a bare focus-out with no typing
  at all" → V6.
- CPKT `setup/patterns/ui-aspects.md` § "Active-row-as-hidden-input anti-pattern" — generalised here
  (*the Analyst's inference, not that section's text*): a derived value drawn as if it had been typed is an
  input the model does not hold; it must be visibly and queryably marked as derived → V9.
- CPKT `derived-identifiers.md`: a path two components both compute must come from one definition → the
  helper calls the config's properties; and `candidates()` keeps calling the effective one (F8).
- The campaign's standing lesson (A-16, A-23, A-29, A-34): every rejection so far was a state or an operation the
  plan enumerated without pinning, or did not enumerate — so the operation × state table above is named by one
  parametrized test (V12), and a declared cell with no test is a declared defect.
- `editor-defaults-and-theta` v1's rejection (`review/…` @ `f2d1aa6`, D-1): what a control *offers or shows* after a
  **second** Load is a state of its own → the "Load a second file" row and V7 assert the control, not only the document.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | The header holds only the three fields item 6 names. | Yes; output paths stay in the list. |
| A2 | With no IPTS, the display says so instead of showing `/SNS/REF_L/nexus`. | Yes — that path is what the config computes, and it is never what anyone means. |
| A3 | No existence check as a problem line. | Yes (see OUT). A tooltip may say "not found on this machine". |
| A4 | Bare numbers and lower-case `ipts-` are normalised; nothing else is. | Yes (the `file_batch.py` convention). |

## Revision history

v1 — authored 2026-10-02 against `7b6d6b9` (staged); **re-sealed and dispatched 2026-10-04 stacked on
`feature/editor-defaults-and-theta` @ `3c4ec39`** when draft PR #38 opened (`[human, 2026-10-04, posture]`; A-36). At the
re-seal: every `settings_editor.py` and `field_spec.py` citation re-measured (`editor-load-fidelity`, `editor-angle-count`,
`editor-combos`, `editor-defaults-and-theta` landed in between); F7 (clear-IPTS stores `None` → `TypeError`) added as a
hazard P5 closes; **F8 CORRECTION** — the direct-beam listing reads the effective `DBpath` and is not re-pointed (the §3
paragraph, the §5 row and the §7 frame rewritten accordingly); F9/F10 added; the operation × state table and V10–V12 added
so every declared cell is a test.
