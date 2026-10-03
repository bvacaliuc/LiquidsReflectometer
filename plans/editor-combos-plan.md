# Plan: `editor-combos` — the wheel never changes a setting; every enumerated field is a drop-down, in the table too

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-combos` (refs `triage/editor-combos`, `feature/editor-combos`,
`qa/editor-combos`) · **Status:** READY (v1) — re-sealed 2026-10-03 against `exp-review` @ `e313f38` (PRs #33 and #35 merged; §2 re-run there; the operation × state table of §3 added from the predecessors' rejections) ·
**Base:** `agentic/exp-review` @ `e313f38` · **PR target:** `exp-review` on the fork, **draft** ·
**Depends on:** `editor-load-fidelity` (per-angle booleans are real `bool`s, text `true`/`false`) and `editor-angle-count` (the rows the table shows, the surplus mark, compact lists: a drop-down in a surplus row or over a broadcast column follows that slug's rules) ·
**Review domains:** ui-aspects, test (block) · **Kind:** launcher — not reduction-path ·
**Sources:** scientists' items 2 and 8; Q1's note and Q4 (`[human, 2026-10-02]`); charter §3 row.

## Declared scope

**Files in:** `launcher/apps/settings_editor.py`, `src/lr_reduction/settings_document.py` (one Qt-free
helper that lists direct-beam candidates), `launcher/tests/test_settings_editor.py`,
`tests/unit/lr_reduction/test_settings_document.py`. `field_spec.py` only if a declaration is needed to say
"this per-angle column completes from a folder" — one attribute, no change to any existing field's meaning.

**Behaviours in** (C1–C6, §3). **Explicitly OUT:** theta labels and defaults (`editor-defaults-and-theta`);
the IPTS/paths header (`editor-paths-header`) — this slug reads the direct-beam folder from the document's
resolved path and must follow it when it changes, but adds no new way to change it; section order; ROI
columns; any reducer file; changing which values a domain offers (`reduction_domains.py` is read-only here).

## 1. Request and symptom

> 2. … some of the items have selectable drop-down lists (e.g. detector resolution function). These inputs
> can be altered by hovering over with the mouse and scrolling. This causes unexpected changes when scrolling
> through the whole settings list and should be turned off. The drop-down item should only be altered by
> clicking on the drop-down menu to select.
>
> 8. In the 'Angles' table … The Q method item can be a drop-down menu, with options for 'meantheta',
> 'constanttof', 'constantq'. Then for the 'direct-beam file', could that be a drop-down list of all .txt or
> .dat files that are in the specified the direct-beam path? … The list would be empty if there is nothing
> in that folder.

Q1 note: "produce drop down selectors for all enumerated choices in the editor page". Q4: "editable with the
folder list as completion."

## 2. Verified facts at `e313f38` (first measured at `7b6d6b9`; re-run at the dispatch tip 2026-10-03)

| # | Fact | Evidence |
|---|---|---|
| F1 | Scalar enumerated fields are plain `QComboBox`es with the default focus policy and no wheel handling. | `settings_editor.py:170-203` (`_build_editor`; the combo at `:191`); `grep -n 'wheelEvent\|setFocusPolicy' launcher/apps/settings_editor.py` → nothing. They sit in a `QScrollArea` (`:145-168`). **Measured** (offscreen, Qt 5.15.15; 2026-10-02 at `7b6d6b9`, re-run 2026-10-03 at `e313f38`, same result): `focusPolicy()` = 15 (`WheelFocus`), `hasFocus()` False; one `QWheelEvent` (angleDelta −120) sent with `QApplication.sendEvent(combo, event)` → accepted, `DetResFn` `rectangular` → `gaussian`, **and the document changed with it**. |
| F2 | Enumerated fields today: scalars `useCalcTheta`, `DetResFn`, `peak_type`; per-angle `method_per_run` (`allowed=METHOD_CHOICES`); per-angle boolean `useBS`. | `grep -n 'allowed=\|list\[bool\]' src/lr_reduction/field_spec.py` |
| F3 | Every Angles-table cell is a text item written through one slot. | `refresh_angles` (`:406`) → `QTableWidgetItem` with `_cell_text` (`:300`); `_on_cell_changed(row, column)` (`:341`) takes the row from the signal; after an edit `refresh_column` re-draws the column's cells and `refresh_marks` the surplus marks (both from `editor-angle-count`). Surplus rows carry a row-header mark (`_row_header`, `:284`). |
| F4 | The canonical method spellings are `meanTheta`, `constantQ`, `constantTOF`; the reducer lower-cases before comparing, so the scientists' lower-case list names the same three. | `reduction_domains.py:25`; `nr_reduction_calc.py:76-82` (`NR_Reduction.__init__`: broadcast at `:77-79`, `.lower()` at `:82` — the class is `NR_Reduction`; the base's own docstrings write `NRReduction`). A file's own spelling is kept on load (`validate` is case-insensitive for this field: `test_validate_accepts_methods_case_insensitively`). |
| F5 | A direct-beam entry is a **file name**, joined to the resolved folder at use. | `nr_reduction_calc.py:402` `tools.load_db_file(self.config.DBpath, self.config.DBname[i])`; `DBpath` = `_DBpath_override` or `/SNS/REF_L/<experiment_id>/shared/transmission` (`nr_reduction_config.py`, the `DBpath` property). |
| F6 | `/SNS` is a network mount on analysis nodes and absent on uvdl3. | `ls /SNS/REF_L` → empty on uvdl3 (M-2). A directory listing there can stall. |
| F7 | A single `method_per_run` entry is broadcast to every angle; an empty one means `meanTheta`. | `settings_document.py` module docstring; `Field(... broadcast_ok=True, reducer_default="meanTheta")` (`field_spec.py:460`). |
| F8 | **A compact list's implied values are not shown.** With `method_per_run: ["constantQ"]` and `useBS: []` on three angles, `angle_row(1)` gives `None` for both — the cells are empty while the reduction uses `constantQ` and background subtraction **on** for that angle; only the notes panel says so for `useBS`. | Measured at `e313f38`: `rows 3, reduction 3, row1: {method_per_run: None, useBS: None}`, `notes()` → "Subtract background (useBS) is unset, so the reduction uses its default: on (1) at every angle". `Field.reducer_default` (`field_spec.py:154`) and `SettingsDocument.reduction_angles` (`settings_document.py:199`) exist since `editor-angle-count`; `set_angle_field` (`:307`) materialises a compact list per that slug's G9. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| C1 | **The wheel never changes a closed drop-down in this tab** — scalar panel and table alike, focused or not. The wheel event is passed on, so the list underneath scrolls. An opened pop-up list still scrolls with the wheel (that is the list view, not the combo). |
| C2 | `method_per_run` cells offer exactly `METHOD_CHOICES`, in declared spelling, plus an unset entry. Choosing stores the declared spelling. A loaded case variant (`meantheta`) displays as its declared choice and is **not rewritten until the user chooses**; a value outside the domain is displayed as itself (never silently replaced by the first item) and reported by `validate()`. |
| C3 | `useBS` cells offer `true` / `false` plus unset; choosing stores a real `bool`. |
| C4 | `DBname` cells are **editable** drop-downs: the list is the `*.txt` and `*.dat` file names in the document's resolved direct-beam folder, sorted, and it completes typed text; a typed name that is not in the folder is stored as typed. Empty or unreadable folder → empty list, typing still works, nothing raises. |
| C5 | **The list follows the resolved path.** When `experiment_id` or `_DBpath_override` changes (edit or Load), the next time a `DBname` cell offers candidates they come from the new folder. |
| C6 | **Row-index rule, unchanged.** Every table write still goes through `SettingsDocument.set_angle_field(row, name, value)` with the row the cell is in **at the time of the edit** — after any Add/Remove. `currentRow()` is not consulted. Displaying a value writes nothing. |
| C7 | **A drop-down never shows "unset" where the reduction has a value.** In a real angle's cell of a compact list (empty default-if-empty list; single-entry broadcast list) the drop-down displays the value the reduction will use — `Field.reducer_default`, or the broadcast entry — visibly marked as implied (the test states the queryable property), and the document is **not** written by displaying it. Choosing in such a cell goes through `set_angle_field`, which materialises the list as `editor-angle-count` G9 defines (the other angles keep the implied value, now explicit). A cell in a **surplus** row shows its held value or unset, never an implied one (the reduction never reads it). An optional-list cell (`LambdaMin`/`LambdaMax`) is not an enumerated field and is untouched here. |

**Mechanism — recommended, not prescribed:** item delegates (`QStyledItemDelegate.createEditor` returning the
combo) over per-cell widgets. Reasons: the table keeps its text items, so `_on_cell_changed(row, column)`
stays the single write path and the row comes from Qt, not from a closure captured at build time (the
stale-row shape of the per-angle trap, generation 1); no persistent child widgets, so a 500-row table costs
nothing extra to populate and there is no closed combo in the table for the wheel to hit. If per-cell
widgets are chosen instead, C1 and C6 must be shown for them explicitly (tests V3, V7). Either way C1 for
the **scalar** combos needs a combo that ignores the wheel (subclass or event filter — one definition, used
by every combo this tab creates).

**Types and states** (each changed path):

| Cell holds | `method_per_run` | `useBS` | `DBname` |
|---|---|---|---|
| a declared value | shown selected | `true`/`false` | shown; in list or not |
| unset (`None`) | unset entry shown; stays `None` until chosen | same | empty text |
| case variant / legacy | shown as the declared choice; kept as loaded | n/a (`1`/`0` are booleans after load) | n/a |
| out-of-domain (`"sombrero"`, `2`) | shown as itself; reported | shown as itself; reported | any text is legal |
| column shorter than `n_angles` (broadcast `["meanTheta"]`, or `[]`) | rows beyond it show unset; choosing in row *k* pads through `set_angle_field` (existing) | same | same |
| column is `None` / not a list | rows show unset; no exception leaves a slot | same | same |

**Operation × state (the axis the predecessors' plans lacked — every cell is a required outcome):**

| Operation on a drop-down cell | real angle, list full length | real angle, compact list (`[]` default / `[x]` broadcast) | surplus row |
|---|---|---|---|
| Load / display | held value, or unset | the implied value, marked (C7) | held value or unset; never implied |
| choose a value | `set_angle_field(row, …)`: that entry only (G8) | `set_angle_field`: materialised per G9 — other real angles get the implied value explicitly; this one the choice | `set_angle_field`: a surplus value (the note follows); for `method_per_run` the gaps are filled per G9 |
| choose "unset" | the entry becomes `None` (G7's some-unset rule applies below `m`) | the list was compact; the cell stays implied — no write | the surplus entry becomes `None` |
| Add angle (button) | a new row at `m` with drop-downs that show unset (a compact list stays compact: C7 marks the implied value in the new row too) | same | surplus rows shift down, drop-downs follow their values |
| Remove angle | the row's entries go; the remaining drop-downs re-render from the document | same | the surplus entries go; the note updates |
| wheel over any cell drop-down, closed | no change | no change | no change |
| Save | as held; `useBS` encoded `1`/`0`; compact lists written `[]` (G7) | unchanged by display | as held |

Folder states for C4: exists with matches · exists, no matches · does not exist · not a directory ·
unreadable (`PermissionError`) · very large (cap the listing; say so in the tooltip when capped) · slow
mount. The listing runs **only when candidates are requested or the path changed** — never per keystroke,
never inside `refresh_report()` — and is a Qt-free function so it is testable without a display.

## 4. Files to change

| File | Change |
|---|---|
| `launcher/apps/settings_editor.py` | wheel-ignoring combo (one definition); table drop-downs for the three columns; candidate refresh on path change |
| `src/lr_reduction/settings_document.py` | `direct_beam_candidates()` (name is a suggestion): resolved folder → sorted `*.txt`/`*.dat` names, capped; every failure → `[]` |
| tests | §6 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | scroll the settings list with the pointer crossing `DetResFn` | value unchanged; the list scrolls |
| common | click a combo, pick a value, then scroll with the pointer still over it | value unchanged (the reported failure survives a "ignore unless focused" guard — hence C1 as stated) |
| common | pick `constantQ` for angle 2 | `method_per_run[2] == "constantQ"`; other rows untouched |
| common | IPTS set, folder has three `.dat` | the three names offered, sorted; typing `db_` completes |
| edge | select row 2, edit the drop-down in row 0 | the write lands on row 0 |
| edge | add 3 angles, remove angle 0, edit the drop-down now in row 0 | the write lands on document index 0 |
| edge | broadcast `["meanTheta"]` with 3 angles, choose in row 2 | column padded; `validate()` unchanged in what it reports |
| edge | folder missing / empty / a file | empty list; typed name stored; no exception |
| edge | `_DBpath_override` edited | candidates come from the new folder |
| edge | Load a second file with another IPTS | candidates follow it |
| pathological | unreadable folder (`chmod 000`), or `os.scandir` raising `OSError` | empty list; nothing reaches `qFatal` |
| pathological | 20 000 files in the folder | capped listing; GUI thread not held beyond one listing |
| pathological | file name with spaces or non-ASCII | stored verbatim |
| pathological | 500 rows | table population time not worse than at the base (measure both; quote the numbers) |

## 6. Red-Green TDD seed (names are suggestions; gestures via `QTest`/`QWheelEvent` sent through `QApplication.sendEvent`, not `.emit()`)

| # | Test | RED at the base |
|---|---|---|
| V1 | a wheel event over a scalar combo (unfocused) leaves `currentText()` and the document unchanged | value changes |
| V2 | the same with the combo focused | value changes |
| V3 | a wheel event over each table drop-down leaves the document unchanged | no drop-downs / value changes |
| V4 | the `method_per_run` editor offers exactly `list(fs.METHOD_CHOICES)` (+ unset) | text cell |
| V5 | choosing through the editor stores the declared spelling in the edited row; row 2 selected while row 0 is edited | — |
| V6 | the `useBS` editor offers `true`/`false`; the stored value's `type` is `bool` | text cell |
| V7 | after Add×3 and Remove(0), editing the drop-down in row 0 writes document index 0 | — |
| V8 | the `DBname` editor lists the folder's `*.txt`/`*.dat` names (tmp_path as `_DBpath_override`), sorted, excluding `notes.md` | text cell |
| V9 | a name not in the folder can be typed and is stored | — |
| V10 | changing `_DBpath_override` (and, separately, Load of a file with another folder) changes the offered names | — |
| V11 | a loaded `meantheta` displays as `meanTheta` and `document.get("method_per_run")` still holds `meantheta` until a choice is made | — |
| V12 | an out-of-domain loaded value is displayed as itself and reported | — |
| V13 | C7: with `method_per_run: ["constantQ"]` and `useBS: []` on three angles, rows 1–2 show `constantQ` / `true` marked implied, and the document is unchanged after the render (`changed_vs_seed() == {}`); choosing `meanTheta` in row 1 materialises `["constantQ", "meanTheta", "constantQ"]`; a surplus row of a surplus-length `useBS` shows its held value, not an implied one | cells empty |
| V14 | the operation × state table, driven through the tab: Add (button) then choose in the new row; Remove a real row and a surplus row; choose "unset" in a compact cell → no write — assert the document, `validate()`, `notes()` and the marks after each | — |
| V15 | a wheel event over a cell drop-down in a surplus row and in a real row leaves the document unchanged (already V3 — add the surplus-row leg) | — |
| U1 | `direct_beam_candidates` → names for a populated folder; `[]` for missing, file-not-dir, unreadable, and a patched `os.scandir` raising `OSError` | function absent |
| U2 | the cap is honoured and announced | — |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| wheel guard removed from the scalar combo class | V1, V2 |
| guard changed to "ignore unless focused" | V2 |
| table drop-down write bound to `currentRow()` | V5 |
| table drop-down write bound to a row captured at build time (only if per-cell widgets are used) | V7 |
| `method_per_run` editor built from a literal list instead of `METHOD_CHOICES` (drop one value) | V4 |
| `useBS` editor stores the text `"false"` | V6 (type leg) |
| candidate glob loses `*.txt` (or `*.dat`) | V8, U1 |
| candidates cached forever (no refresh on path change) | V10 |
| editable flag off on the `DBname` editor | V9 |
| exception handling removed from the listing | U1 (unreadable / `OSError` legs) |
| display-only path writes on show (loaded `meantheta` canonicalised by merely displaying it) | V11 |
| implied value shown without the mark, or the mark shown on a held value | V13 |
| implied value written into the document by displaying it | V13 (`changed_vs_seed`) |
| implied value shown in a surplus row | V13 (surplus leg) |
| choosing "unset" in a compact cell writes `None` | V14 |

Frame: the wheel-ignoring combo is used at every combo construction site in the tab — one row per site
(`_build_editor`'s enumerated branch; each table editor); the listing helper has one call site per trigger
(candidates requested; path changed).

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` returns zero from the repository root on the feature tip.
2. §6 RED→GREEN observed; §7 recorded per row with the observed `N failed`.
3. Prose claims verified by the falsifying command or marked inferred — in particular any sentence about
   which widget receives the wheel event, and the 500-row timing.
4. Deployment-shaped acceptance (Integrator, analysis node): in the launched tab, with a real IPTS — scroll
   the settings list across every drop-down (no value changes; "Changed from the seed" stays empty); the
   `DBname` drop-down lists that IPTS's `shared/transmission` files; pick one, save, and the saved name
   equals a file that exists. Record the IPTS and the listing count in the PR body.
5. PR body: launcher-only; visible to scientists after merge + re-deploy of the review tier.

## 9. Learnings relied on

- `campaign-learnings-synthesis.md` §G generation 1: "using `currentRow()` instead of the signal's row
  writes the edit to whichever row happens to be selected" → C6, V5, V7.
- `settings-editor-learning.md` §1: "A `QTest.mouseClick` at a coordinate you reasoned about is still a
  claim about geometry" → wheel events are sent to the widget object, and the test states which widget.
- `test_a_combo_displays_a_value_outside_its_choices` (base): a combo asked to show an unknown value shows
  its first item — the substitution C2 forbids.
- CPKT `setup/patterns/network-mounts.md` (facility mounts can stall) → the listing is on demand and guarded.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | Charter §3 says "wheel ignored unless focused"; the scientists say the value "should only be altered by clicking on the drop-down menu". After a click the combo keeps focus, so the charter's wording leaves the reported failure reachable. | **Never by wheel** (C1) — a tightening of the charter row, flagged for the human. |
| A2 | Offer the declared spellings (`meanTheta` …) rather than the scientists' lower-case ones. | Declared spellings; the reducer lower-cases (F4). |
| A3 | Listing a facility folder from the GUI thread. | On demand, capped, guarded; no background thread in this slug. If the Integrator measures a stall on a live mount, that is a follow-on (`fix/`), not a v2. |
| A4 | Scalar booleans stay checkboxes (they are not "enumerated choices"). | Yes. |

## Revision history

v1 — authored 2026-10-02 against `7b6d6b9` (staged); re-sealed and dispatched 2026-10-03 against `e313f38` after PRs #33 and #35 merged: F1 re-measured (unchanged), F3/F7 citations moved to the tip, F8 added (compact lists display unset where the reduction has a value), C7 and the operation × state table added — the axis whose absence cost the predecessors five rejections — with V13–V15 and their mutations.
