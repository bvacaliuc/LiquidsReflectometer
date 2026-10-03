# Plan: `editor-angle-count` — the editor counts, adds and saves angles the way the reduction reads them

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-angle-count` (refs `triage/editor-angle-count`,
`feature/editor-angle-count`, `qa/editor-angle-count`) · **Status:** v3 (retry 2 of N = 3 — the last before escalation; v1 rejected at `1568397`, v2 at `c286e9b` — see Revision history) · re-sealed 2026-10-02 against `exp-review` @ `c34c8c5` · **Base:** `agentic/exp-review` @ `c34c8c5` ·
**PR target:** `exp-review` on the fork, **draft** · **Depends on:** `editor-load-fidelity` (same three files);
`editor-combos` now waits for **this** slug (its table drop-downs sit on the rows this slug defines) ·
**Review domains:** design, test (block); ui-aspects (advise) · **Kind:** launcher / settings model — not
reduction-path (§2 F8) ·
**Seed:** `todo-real-settings-per-angle-length-mismatch.md` — a discovered fix, found at
`editor-load-fidelity`'s gate (I-4), re-measured at `rereduction-headers-land`'s (I-6) ·
**Authority:** `[human, 2026-10-02: "add fix/editor-angle-count to the charter and plan it"]`.

## Declared scope

**Files in:** `src/lr_reduction/settings_document.py`, `src/lr_reduction/field_spec.py` (a derived tuple at most —
no new per-field flag unless §3's derivation proves insufficient at the re-seal),
`launcher/apps/settings_editor.py` (the panel's notes; the mark on surplus rows),
`tests/unit/lr_reduction/test_settings_document.py`, `launcher/tests/test_settings_editor.py`.

**Behaviours in** (G1–G7, §3): the number of angles the reduction will use; what a surplus entry is and how it is
reported; where an added angle lands; what an unset per-angle entry means when the file is written.

**Explicitly OUT** (a finding here is a PR-body advisory, not a rejection):
- every reducer file — the reducer's own rules are read (`nr_reduction_calc.py:61-110`), not changed;
- trimming or rewriting a loaded file's surplus entries without a user gesture (detection complete, resolution
  the user's: Remove angle);
- reporting an unset **required** entry (`DBname`, `RB_Ymin`, `RB_Ymax`, `BkgROI` of an angle not filled in yet) —
  A3; drop-downs and the wheel (`editor-combos`); theta; the paths header; section order; ROI;
- `RBnum`'s editability (still `editor-load-fidelity` A2).

## 1. Request and symptom

Item 1's intent — a real reduction settings file must not show spurious problems — one step further. Measured by
the Integrator on real files: `IPTS-36119/shared/autoreduce/reduce_settings.json` holds `useBS: [1, 1, 1, 1]` for
three angles; the twelve `Aug2026/REFL_*_settings.json` hold 4–8 `useBS` entries for three `RBnum`. The editor
shows a fourth, mostly empty row and reports **every other field** as short. The reduction ignores the extra
entry. While planning, two more faces of the same thing were measured (F3, F5): **Add angle** on such a file puts
the new angle's values in different rows, and a file authored from scratch in the editor **cannot be reduced**
although the panel says "No problems found."

## 2. Verified facts at `c34c8c5` (uvdl3 clone 1, 2026-10-02; first measured at `7b6d6b9`, re-run at the dispatch tip)

| # | Fact | Command → observation |
|---|---|---|
| F1 | The editor counts angles by the longest per-angle list and measures every list against that. | `settings_document.py:160-167` (`n_angles`), `:284` (the length check in `validate()`). `from_dict({RBnum, DBname, RB_Ymin, RB_Ymax, BkgROI of 3; useBS [1,1,1,1]})` → `n_angles == 4`; exactly four lines `… has 3 entries for 4 angles` (`DBname`, `RB_Ymin`, `RB_Ymax`, `BkgROI`) — the `useBS` type lines of the base are gone since `editor-load-fidelity` (the entries load as booleans). |
| F2 | The reduction counts angles by `RBnum` and only requires the others to be **not shorter**. | `nr_reduction_calc.py:61` `n_settings = len(self.config.RBnum)`; `:67`, `:69`, `:71`, `:73` test `< n_settings`; `:77-81` broadcast a single `method_per_run`, refuse a shorter non-empty one; every use is `[i]` with `i < n_settings`. A longer list's extra entries are never read. |
| F3 | **Add angle misaligns on unequal lists.** | On F1's document, `add_angle(DBname="d.dat", useBS=False)` → `DBname ['a','b','c','d.dat']`, `useBS [1,1,1,1,False]`: row 3 = `d.dat` with the **old surplus** `useBS` 1; the author's `False` is alone in row 4. `add_angle` appends to each list at its own end (`settings_document.py:183-191`); at `c34c8c5` the held list is `[True, True, True, True, False]`. |
| F4 | **Add angle breaks a broadcast.** | Same call: `method_per_run ['meanTheta']` → `['meanTheta', None]` — no longer length 1, shorter than the angles (the reducer raises at `:80-81`), and `:82` calls `.lower()` on the `None`. |
| F5 | **A file authored from scratch validates clean and cannot be reduced.** | `SettingsDocument()`; two `add_angle(DBname=…, RB_Ymin=…, RB_Ymax=…, BkgROI=…, useBS=True)` → `validate() == []`; `normalize()` → `ThetaShift [None, None]`, `tof_min [None, None]`, `ScaleFactor [None, None]`, `method_per_run [None, None]`. `json_to_config` of that: `not config.ThetaShift` is `False`, so the reducer's "default if empty" (`:99-110`) does not apply and `:413` adds `None`; `[m.lower() for m in method_per_run]` → `AttributeError: 'NoneType' object has no attribute 'lower'`. Re-run at `c34c8c5`: identical, and `useBS` is now written `[1, 1]` by the encoder `_encode_for_file` (`settings_document.py:351-366`) — the hook G7 extends. |
| F6 | Which lists the reducer fills or broadcasts is already declared. | `Field.default_if_empty` (`ThetaShift`, `useBS`, `ScaleFactor`, `tof_min`, `tof_max` — pinned by `test_default_if_empty_names_are_exactly_the_reducers_optional_arrays`), `broadcast_ok` (`method_per_run`), `optional_list` (`LambdaMin`, `LambdaMax`). The rest of `PER_ANGLE_NAMES` — `DBname`, `RBnum`, `RB_Ymin`, `RB_Ymax`, `BkgROI` — are the ones the reducer indexes without a fallback. |
| F7 | Removing a surplus row already works. | On F1's document `remove_angle(3)` → `n_angles == 3`, `useBS [1, 1, 1]`, no count line (`settings_document.py:193-200` trims only the lists that reach the index). |
| F8 | Not reduction-path. | No reducer module imports `settings_document` or `field_spec` (`grep -rln` at `c34c8c5`: the two modules, the tab, its test). |
| F9 | After `rereduction-headers-land` the reducer no longer writes unequal lists; what remains is input carried through. | The Integrator's re-measurement at `30f5a7a` (`todo-real-settings-per-angle-length-mismatch.md`): every scenario → all lists 3; only the authored `useBS` 4 survives. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| G1 | **The angle count is the reduction's.** The document exposes the number of angles the reduction will use: the length of the longest *angle-defining* list — a per-angle field that is neither `default_if_empty`, nor `broadcast_ok`, nor `optional_list` (F6: derived from the declarations, not a typed list of names). When every angle-defining list is empty, it is the longest per-angle list, so a document that holds only optional columns still shows them. |
| G2 | **Nothing is hidden.** The table still shows a row for every index at which any list holds an entry. A row beyond the reduction's count is marked as surplus in a way a test can query and a scientist can see; it stays editable and removable. |
| G3 | **"Short" is measured against the reduction's count.** A list at least that long is never reported short. An angle-defining list shorter than the count is reported as today. The exemptions for empty-with-default, broadcast and runtime-owned lists stand. |
| G4 | **A surplus entry is a note, not a problem.** One line per field: which field, how many extra entries, that the reduction ignores them, and that removing the surplus angle drops them. `validate()` does not return it; the panel shows notes in their own section, and a reducible file still reads "No problems found." |
| G5 | Removing a surplus row trims exactly the lists that reach it (F7 — pinned, not changed). |
| G6 | **An added angle has one index — the reduction's next one.** **(v2)** The new angle is inserted at index `m` (the reduction's count), directly after the last real angle; entries that were surplus move down one row and stay surplus. Every per-angle list is either still in a compact state the reduction accepts (empty with a default; a single broadcast entry; `None` for an optional list) or has its new entry at index `m`. A value supplied for a compact list expands it: a broadcast list by repeating its single entry for the existing angles (what the reducer does at `:77-79`), the others with unset entries. *(v1 appended after the surplus rows, which turned them into angles with no required values — `todo.md` @ 1568397 Q-1.)* |
| G8 | **(v2, new) An edit changes exactly the entry edited.** `set_angle_field(i, name, value)` never adds entries at any other index beyond what is needed to reach `i` — no growth into surplus rows (v1 padded to the table's row count, `settings_document.py:279-283` @ `09ac86e`); a single broadcast entry expands to the reduction's count `m`, not to the table's rows. The reduction's count and the set of surplus rows change only when the edit itself defines a new angle (an angle-defining value at an index ≥ `m`). G7's "some unset" rule and every count look at entries **below `m`** only. The view re-derives the surplus marks after every edit, as after Load, Add and Remove. |
| G9 | **(v3, new) Editing one angle of a compact list never changes what the reduction reads for any other existing angle, and never leaves a file the reduction refuses or crashes on without a line that says so.** A compact list is one the reducer fills or broadcasts itself: an empty default-if-empty list (`ThetaShift`, `ScaleFactor`, `tof_min`, `tof_max`, `useBS` — the reducer's fill at `nr_reduction_calc.py:99-110`: 0, 1, 0, 100000, 1), an empty or single-entry broadcast list (`method_per_run`: `meanTheta`, `:42-43`; or its one entry, `:77-79`), an unset optional list (`LambdaMin`/`LambdaMax` `None`: derived per angle). **Default-if-empty and broadcast lists (a):** the edit materialises the list to the reduction's count `m`, filling every other real angle with **the value the reducer would have used** — declared once on the `Field` (`reducer_default`; pinned against `_validate_config` by a test) — so the file reduces as before for every angle but `i`, with no problem line. A broadcast list never holds an unset entry at any index after an edit (the reducer lower-cases the **whole** list, `:82`). **Optional lists (b):** at `i < m` the list is materialised with unset entries for the other real angles and they are reported by name (the existing wording) — there is no explicit spelling of "derive this one", so the file is not reducible until they are filled, and the line says so; at `i ≥ m` the edit is **refused** (the list stays `None`, the cell shows unset) with a problem line naming the mechanism and the remedy — a value in a row the reducer never reads would otherwise turn "derived" off for every real angle (C-3). |
| G7 | **An unset entry is written the way the reduction reads "unset".** At the file boundary (`save`, `normalize`): a `default_if_empty` or broadcast list whose entries are **all** unset is written as `[]`, so the reducer's default applies; one that is unset for **some** angles is reported as a problem naming the angles (the wording the optional lists already have), and written as held. Loading a file with `[null, null]` in such a list shows empty cells and saves `[]`. |

**Types and states** (each per-angle list × its state, with the reduction's count `m` and the table's rows `n ≥ m`):

| List kind | empty / `None` | length 1 | length < m | length = m | length > m | all entries unset | some unset |
|---|---|---|---|---|---|---|---|
| angle-defining (`DBname`, `RBnum`, `RB_Ymin`, `RB_Ymax`, `BkgROI`) | quiet while `m == 0`; else reported short (`RBnum`: quiet — runtime-owned) | as `< m` | reported short | quiet | cannot be (it defines `m`) | unchanged — OUT (A3) | unchanged — OUT (A3) |
| default-if-empty (`ThetaShift`, `useBS`, `ScaleFactor`, `tof_min`, `tof_max`) | quiet (default) | as `< m` | reported short | quiet | **note** (G4) | written `[]` (G7) | **problem** (G7) |
| broadcast (`method_per_run`) | quiet (default `meanTheta`) | quiet (broadcast) | reported short | quiet | **note** | written `[]` | **problem** |
| optional (`LambdaMin`, `LambdaMax`) | quiet (`None` = derive) | as `< m` | reported short | quiet | **note** | `None` (existing) | problem (existing) |
| a value that is not a list | reported as today; excluded from every count | | | | | | |

Add (G6, as revised in v2), by the list's state before the gesture: compact and no value supplied → untouched;
compact and a value supplied → materialised to length `m + 1` with the value at index `m` (G9 says what fills the
other angles); full length `m` → the new entry appended at `m`; shorter than `m` (a file's ragged list) → padded with
unset entries to `m`, then the new entry; longer than `m` (surplus) → the new entry **inserted** at `m`, the surplus
entries shifted to `m + 1 …` and still surplus. One index, `m`, in every list.

Decisions, with reasons:
- **Why derive "angle-defining" instead of naming the fields.** The three flags are already pinned to the reducer
  by tests (F6); a fourth hand-kept list would be a copy that drifts.
- **Why keep the surplus row visible.** Hiding it would make a held value invisible and would let Add reuse its
  slot (F3). Showing it, marked, keeps "what is shown is what is held", and the remedy is a gesture that exists.
- **Why a note and not a problem.** The file reduces. A panel that reports four problems on a working file is how
  a real one goes unread (`settings_document.py`, `_length_is_allowed` docstring).
- **Why all-unset is written `[]`.** It is the only spelling of "use your default" the reducer has (`:99-110` test
  `if not self.config.<name>`); `[None, None]` is a list, so the default is skipped and the `None` is used.

## 4. Files to change

| File | Change |
|---|---|
| `settings_document.py` | the reduction's count; `validate()` measured against it; `notes()` (name is a suggestion); `add_angle` alignment; the file-boundary encoder `_encode_for_file` (`:351-366`, from `editor-load-fidelity`; called by `save` and `normalize`) extended with G7 |
| `field_spec.py` | at most a derived tuple of the angle-defining names, beside `DEFAULT_IF_EMPTY_NAMES` (`:633`) and `INT_ENCODED_NAMES` (`:627`) |
| `settings_editor.py` | notes in the panel; the surplus mark; nothing else |
| tests | §6 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | `reduce_settings.json` with `useBS: [1,1,1,1]` for three angles | "No problems found."; one note naming `useBS` and one extra entry; rows 1–3 normal, row 4 marked surplus |
| common | remove the surplus row | note gone; `useBS` has three entries; nothing else changed |
| common | new document: Add ×2, fill the required columns, Save | `ThetaShift`, `ScaleFactor`, `tof_min`, `tof_max`, `method_per_run` written `[]`; the file passes the reducer's `_validate_config` (see T9) |
| common | load a file with a single `method_per_run`, Add angle | still a single entry; the new row shows it as unset/broadcast, not `None` in the list |
| edge | Add angle with a surplus row present | the new angle is one row; every list's new entry is at that row's index |
| edge | Add angle on a file whose default lists are full length | appended, same index |
| edge | set `method_per_run` for the new angle only | list expanded: the broadcast value for the earlier angles, the chosen one for the new |
| edge | `ThetaShift` filled for angle 0 only | problem naming the angles without a value; saved as held |
| edge | older editor-saved file with `ThetaShift: [null, null, null]` | loads; cells empty; saves `[]` |
| edge | Aug2026-style file: `useBS` 6–8 for three angles | one note ("3 to 5 extra entries"), several surplus rows, each removable |
| edge | only optional columns hold values (no defining list) | rows shown for them (G1's fallback); no note |
| pathological | a per-angle field holding a non-list | reported as today; excluded from the counts; no exception |
| pathological | `RBnum` longer than `DBname` | `DBname` reported short (the reducer would raise at `:67-68`) |
| pathological | 10⁶ entries in one list | existing caps hold (`MAX_TABLE_ROWS`, `MAX_REPORTED_PROBLEMS`); notes are one line per field, never per entry |
| pathological | Remove on a surplus row while another row is selected / being edited | the row-index rule holds (`remove_selected_angle` uses the selection as its input; no other write moves) |

## 6. Red-Green TDD seed (names are suggestions; a test is named for what it covers)

Model (`tests/unit/lr_reduction/test_settings_document.py`):

| # | Test | RED at `c34c8c5` |
|---|---|---|
| T1 | a three-angle file with one surplus `useBS` entry validates clean | four count lines (at `c34c8c5`) |
| T2 | its note names `useBS`, says 1 extra, and is not in `validate()` | no notes API |
| T3 | the reduction's count is 3 and the table's rows are 4 for that file; with every defining list empty the count falls back to the longest list | count API absent |
| T4 | an angle-defining list shorter than the count is still reported (`DBname` 2 for `RBnum` 3) | passes today — a pin against over-relaxing |
| T5 | the angle-defining names, derived, are exactly `{DBname, RBnum, RB_Ymin, RB_Ymax, BkgROI}`, and every per-angle field is in exactly one of the four kinds | absent |
| T6 | Add keeps one index: on the surplus file, after `add_angle(DBname="d.dat", useBS=False)` every non-compact list has the same length and both values sit at that last index | `DBname[3]`, `useBS[4]` |
| T7 | Add leaves a broadcast broadcast: `["meanTheta"]` stays length 1 with no value supplied; with one supplied it becomes `["meanTheta"] * n + [value]` | `['meanTheta', None]` |
| T8 | Add leaves an empty default list empty (loaded file, `ThetaShift: []`) | `[None]` |
| T9 | **the reducer accepts what the editor writes:** a document built only through `add_angle` with the required columns, then `normalize()` → `json_to_config` → the reducer's own `_validate_config` logic applied (construct `NR_Reduction` as the existing reducer-domain tests in this module do, or call the method on a stand-in that carries only `config` — whichever those tests already use; read them first) → no exception, and afterwards `ThetaShift == [0] * n`, `method_per_run == ["meantheta"] * n` | `AttributeError` at `.lower()` |
| T10 | all-unset default and broadcast lists are written `[]` by `save()` (assert on the text) and by `normalize()` | `[null, null]` |
| T11 | a partly-set default list is a problem naming the unset angles, and is saved as held | no line |
| T12 | `[null, null]` loads, shows as unset, saves `[]` | saves `[null, null]` |
| T13 | removing the surplus angle clears the note and trims only `useBS` | passes on the trim — pin; note leg red |

View (`launcher/tests/test_settings_editor.py`; `isolated_qapp`, `no_qmessagebox`; gestures via `QTest`):

| # | Test | RED |
|---|---|---|
| V1 | Load of the surplus file: the panel reads "No problems found." and shows the note in its own section | four problem lines |
| V2 | the surplus row is marked (the test states the queryable property) and rows 0–2 are not | no mark |
| V3 | Add angle (button) on the surplus file, then type a `DBname` in the new row: the document's new index is the same in `DBname` and in every other non-compact list | misaligned |
| V4 | Remove on the surplus row (selected) clears the note | — |
| V5 | new tab → Add ×2 → fill required cells → Save: the saved text holds `"ThetaShift": []` and `"method_per_run": []` | `[null, null]` |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| count = longest of all lists again | T1, T3, V1 |
| the fallback (all defining lists empty) removed | T3 (fallback leg) |
| a default-if-empty field counted as angle-defining (the derivation loses one flag) | T5, T1 |
| `validate()` measures against the table's rows | T1 |
| every length ≥ count exempted **and** shorter defining lists exempted too (over-relaxed) | T4 |
| the note returned from `validate()` | T2, V1 |
| the note emitted per entry instead of per field | T2 (count of lines) on the 8-entry case |
| Add appends at each list's own end | T6, V3 |
| Add pads a broadcast with `None` | T7, T9 |
| Add appends to an empty default list | T8 |
| the encoder's all-unset rule removed from `save()` / from `normalize()` (one row each) | T10 (its two legs), T9, V5 |
| the all-unset rule applied to an angle-defining list (over-reach: `DBname [None, None]` → `[]`) | a pin in T10 that `DBname` is written as held |
| partly-set reported for optional lists only (the existing rule not extended) | T11 |
| the surplus mark applied to every row / to none | V2 |

Frame: the count is consulted by `validate()`, by `notes()`, by the view's mark and (if used) by `add_angle` — one
row per call site; the encoder has two call sites (`save`, `normalize`); `add_angle`'s callers are the tab's Add
button and the tests. Any assertion on encoded values compares text or `type`, not `==` alone.

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` returns zero from the repository root on the feature tip.
2. §6 RED→GREEN observed and quoted; §7 recorded per row with the observed count.
3. Prose claims verified by the falsifying command or marked inferred — in particular T9's claim that the reducer
   accepts the written file is shown by running the reducer's own validation, not by reading it.
4. No file outside "Files in"; no ledger-shaped path in the diff.
5. Deployment-shaped acceptance (Integrator, analysis node): `ledger/scripts/editor-real-file-roundtrip.py` on the
   real files of `todo-real-settings-per-angle-length-mismatch.md` (`IPTS-36119/shared/autoreduce/reduce_settings.json`,
   the twelve `Aug2026/REFL_*_settings.json`) → no count line at all; the notes quoted in the PR body. In the launched
   tab: load one, Add angle, fill it, Save; then author a three-angle file from scratch and **reduce one run with
   it** through the harness — the first end-to-end proof that an editor-authored file reduces.
6. PR body: launcher-only; visible after merge + re-deploy of the review tier; the OUT list as advisories.

## 9. Learnings relied on

- `agentic/analysis/exp-settings-roi:plans/settings-editor-learning.md` §4: "the editing layer is where the shape
  gets enforced — and it must enforce the shape the *consumer* actually accepts, not a tidier one." → G1, G3.
- `campaign-learnings-synthesis.md` §G: "a short array silently shifts every later angle by one" (generation 2)
  and "`None`-as-a-real-value is a *state* the type does not distinguish" (generation 4) → G6, G7, the state table.
- `plans/editor-load-fidelity-plan.md` v2 (this campaign): a rule generalised from one field's reader to all was
  the v1 defect → every per-angle kind has its own column in §3, and T9 runs the consumer.
- `plans/editor-load-fidelity-learning.md` §1: "A writer-shaped fixture must carry the writer's *post-run*
  state" → T1's fixture is the real file's shape (`useBS` longer than `RBnum`), and T9's is the editor's own output.

## 10. Assumptions and open questions (the plan proceeds under each default)

| # | Question | Default |
|---|---|---|
| A1 | G7 (unset entries) is folded into this slug rather than made its own. It was found while planning this one (F5), on the same functions, and G6 cannot be stated without the same notion of a compact list. | Folded in. If a gate rules it out of scope it becomes a child leaf at v1 with `Seed:` this plan. |
| A2 | An all-unset `useBS` column is written `[]`, which the reducer reads as background subtraction **on** for every angle (`:102-103`). | Yes — it is the reducer's default; the note section says so when the column is empty. The scientists may prefer an explicit value per angle; `editor-combos` gives the cell a definite choice. |
| A3 | An unset **required** entry (an angle with no `DBname`) is still not reported; the panel can read "No problems found." for a document that is not yet reducible. | Unchanged here. Proposed as a "not yet reducible" note in a later slug; filed if the Integrator's criterion 5 shows scientists hit it. |
| A4 | The surplus mark's look (row header text, greyed cells) is the Developer's; the ui-aspects reviewer advises. | — |

## Revision history

v1 — authored 2026-10-02 against `7b6d6b9` (staged); re-sealed and dispatched the same day against `c34c8c5` after PR #33
merged (§2 probes re-run: F1, F3, F4, F5, F7 unchanged in outcome; citations moved to the new tip's lines).

### v2 — 2026-10-02 (retry 1; the work order for `triage/editor-angle-count-v2`)

**Rejection.** `review/editor-angle-count` @ `1568397` — `todo.md` at that commit. Not infrastructure. **B-1 (blocking, the
plan's gap):** the plan enumerated Load, Add, Remove and Save but never an **edit** on a file with surplus rows;
`set_angle_field` pads the edited list to the table's row count (`settings_document.py:279-283` @ `09ac86e`), so one
ordinary cell edit on `Aug2026/REFL_231105_settings.json` turns the reduction's count 3 → 7, erases the notes and prints
four false problems — and saves that way. **B-3 (blocking):** two declared behaviours have no test that can fail — G7's
"some unset → problem" for a broadcast list (mutant `fills_itself = field.default_if_empty` survives 233 tests while
`[None, None, 'constantQ']` reduces to `AttributeError`), and G6's expansion of an **empty** default list given a value
when `n > 0` (mutant `[]` head survives: the new value lands on angle 0). **B-2 (blocking):** the module docstring's
"`add_angle` mutates **every** per-angle field in one operation" is false by design since G6 — restate it. **Q-1
(answered here):** v1's G6 appended the new angle *after* the surplus rows, which makes surplus rows real angles with no
required values (`RBnum […, null, 999999]`) — the plan's choice, and the wrong one; G6 is revised above.

**What stands (do not redo; `todo.md` "What passed").** G1–G5, G7 as implemented: the count, the notes, Remove, the
file-boundary rule, and the first end-to-end proof that an editor-authored file reduces (byte-identical data to the real
`reduce_settings.json` run). The 26 recorded mutation rows.

**What changes.**

| # | Behaviour (as rewritten in §3) | Reachable state it closes |
|---|---|---|
| G8 | an edit changes exactly the entry edited; padding only up to `i`; broadcast expands to `m`; counts and the some-unset rule look below `m`; marks re-derived after an edit | B-1's three reproductions |
| G6 (revised) | the new angle is inserted at index `m`; surplus entries shift down and stay surplus | Q-1 |
| B-2 | the module docstring states the v2 rule ("one index per added angle; compact lists stay compact") and the reducer citations move to `:77-79` / `:42-43` | the verify-prose rule |

**Types and states the changed path acts on** (amendment 18). Operation: edit at index `i` with `i < m`, `i ≥ m` (a
surplus row), `i` beyond every list. List kind: angle-defining / default-if-empty / broadcast / optional. List state:
compact (empty, single broadcast entry, `None`), full length `m`, ragged short (`< m`), surplus (`> m`), non-list.
Behaviour per cell of that matrix: the edited entry changes; for `i < m` nothing else changes (a ragged-short list is
padded only to `i + 1`; a single broadcast entry expands to `m`); for `i ≥ m` in an **angle-defining** list the
reduction's count becomes `i + 1` and the rows below it are no longer surplus (and the count lines then apply to the
other defining lists, as for any real angle); for `i ≥ m` in any other kind the entry is a surplus value and nothing
else changes; a non-list is replaced only as `set_angle_field` does today (reported type, excluded from counts). Add:
insert at `m` in every non-compact list (shifting surplus entries), compact lists stay compact unless a value is
supplied.

**Guard (vary what the fix freezes).**

| # | Test (names are suggestions) | RED at `09ac86e` |
|---|---|---|
| R1 | on the T1 surplus document **and** an Aug2026-shaped one (`useBS` and `method_per_run` longer than the defining lists): for each list kind × an edit at index 0, at `m-1`, and inside a surplus row → `validate()`, `notes()`, `reduction_angles` and the saved text are as G8 says; save → reload → identical | `DBname[0]` edit: count 3 → 7, four false problems |
| R2 | an edit of a default-if-empty entry below `m` on the surplus file leaves no "set for some angles but not angles [surplus]" line | `ThetaShift [0.01, 0, 0, None]` reported |
| R3 | an edit of a single broadcast entry expands it to `m`, not to the table's rows | expands to `n` |
| R4 | an angle-defining edit inside a surplus row makes that row a real angle (count `i + 1`) and nothing else grows | — |
| R5 | view: after a cell edit on the surplus file the row marks are re-derived (surplus rows still marked; the panel still "No problems found." plus the notes) | marks stale, panel wrong |
| R6 | Add on the surplus file inserts the new angle at `m`: the typed `DBname` is at index `m`, the former surplus entries are at `m+1…`, still surplus; the reduction's count is `m + 1`; saved `RBnum` has no `null` before the new run | new angle after the surplus rows (Q-1) |
| R7 (B-3) | T11 parametrized over every default-if-empty **and** the broadcast field: a partly-unset list is a problem naming the angles | `method_per_run` leg: no line under the mutant |
| R8 (B-3) | T8 leg: on three angles with `ThetaShift: []`, `add_angle(DBname="d", ThetaShift=0.1)` → `[None, None, None, 0.1]` (assert the position, not only the length) | `[0.1]` under the mutant |
| R9 (B-2) | the module docstring no longer claims every list grows; the statement that replaces it is checked by R6/R8 | — |

**Mutations (each recorded as `<mutation> → <test> -> N failed`).**

| # | Mutation | Must red |
|---|---|---|
| N1 | `set_angle_field` pads to the table's rows again | R1 (every kind at index 0), R2, R5 |
| N2 | single broadcast entry expanded to the table's rows | R3 |
| N3 | the some-unset rule measured over the whole list | R2, R1 (surplus-row edits) |
| N4 | an angle-defining edit in a surplus row does not raise the count | R4 |
| N5 | view does not re-derive marks after an edit | R5 |
| N6 | Add appends after the surplus rows (v1's G6) | R6 |
| N7 | `fills_itself = field.default_if_empty` (broadcast dropped) | R7 |
| N8 | `add_angle` expands an empty default list with `[]` instead of `[None] * n` | R8 |

Then the v1 battery again; a row whose expected red moved because of v2 is re-aimed and recorded.

**Acceptance (v2).** §8 as written, plus: §8.5 re-run on the thirteen real files **with one edit each** (a `DBname` at
index 0; a `ThetaShift` at index 0; a surplus-row edit) — no count line, notes unchanged, saved file reduces where it
reduced before; the Tab Add check repeated with the new placement; `todo.md` removed in its own commit before `qa/`.
The PR body carries the advisories verbatim (A2's note wording, `Field.fills_itself`, the `_length_is_allowed`
docstring, the Remove-by-`currentRow()` pre-existing item, the ui-aspects notes on wording and visibility, the test
reviewer's notes); none is in this revision's scope.

### v3 — 2026-10-03 (retry 2 — the last before escalation; the work order for `triage/editor-angle-count-v3`)

**Rejection.** `review/editor-angle-count` @ `c286e9b` — `todo.md` at that commit. Not infrastructure. One defect family
the v2 matrix did not specify: **editing one angle of a compact list** (C-1 silent: `method_per_run: []` + one edit →
`['constantQ']` → the reducer broadcasts it to every angle, `validate() == []`; C-2, the v2 acceptance criterion itself:
`ThetaShift` unset in all twelve Aug2026 files, one edit → `[0.01]` → run 221473 raises `IndexError` at `:413`; C-3: a
λ typed into a surplus row of an unset optional list turns "derived" off for every angle and the reducer raises at
`:452`), plus two guards that hold only where v1 and v2 agree (B-T1: Add's with-value index never tested on a surplus
document; B-T2: the optional half of "below `m`" never tested from a surplus-length optional list). v1's findings are
fixed and stay fixed. **Both plan-level gaps were on `set_angle_field`: v1 never enumerated an edit, v2 never enumerated
the compact states.** v3 states the outcome per cell before any code (below), as the Integrator recommended; no decompose
(C-1 is a regression from v1 and cannot ship).

**What stands (do not redo; `todo.md` "What passed").** G1–G8 as implemented for non-compact lists: B-1 fixed on 13
real files, marks re-derived, Add at `m` with surplus shifted, B-2, B-3, the 37 recorded mutation rows, the end-to-end
proof that an editor-authored file reduces.

**What changes.** G9 (§3) and the per-cell table below; the G6 paragraph of §3 corrected (it still carried v1's placement);
`reducer_default` declared once on the `Field` (the design reviewer's advisory, now load-bearing).

**The per-cell table (amendment 18 — every cell is a required outcome; `m` = the reduction's count; `i` = the edited index).**

| Kind | Compact state | `i < m` | `i ≥ m` (a surplus row) |
|---|---|---|---|
| default-if-empty (`ThetaShift` 0, `ScaleFactor` 1, `tof_min` 0, `tof_max` 100000, `useBS` 1 → `True`) | `[]` | list becomes length `m`: `reducer_default` at every index but `i`, the value at `i`; no line; the reducer's reading of every angle ≠ `i` unchanged (the pin: `NR_Reduction(json_to_config(saved))`, per angle, truncated to `len(RBnum)`) | list becomes length `i + 1`: `reducer_default` at `0 … m-1`, unset at `m … i-1`, the value at `i`; no line; a note names the surplus; the reducer reads only `< m` |
| broadcast (`method_per_run`) | `[]` | length `m`: `meanTheta` everywhere but `i`; no line | length `i + 1`: `meanTheta` at every other index **including `m … i-1`** (no unset entry anywhere — `:82` lower-cases the whole list); a note names the surplus |
| broadcast | `[x]` | length `m`: `x` everywhere but `i` (v2's rule, kept) | length `i + 1`: `x` everywhere but `i` |
| optional (`LambdaMin`, `LambdaMax`) | `None` | length `m`: unset everywhere but `i`; **problem line** naming the unset angles and saying the field must be complete or cleared to derive (the existing wording) | **refused**: the list stays `None`, the cell shows unset, a problem line says a derived λ cannot be set for a row the reduction does not use — set the real angles first or leave it derived |
| optional | a list of length ≥ `m` | the entry changes; the some-unset rule looks below `m` only | the entry changes (a surplus value, ignored by the reducer: `LambdaMin[i]`, `i < n`); no line; the some-unset rule looks below `m` only (B-T2) |
| any | non-compact (full, ragged, surplus) | G8 as implemented | G8 as implemented |

Documents the matrix runs on: `m = 1`, `m = 3` (the T1 surplus document), and an Aug2026-shaped one (`useBS` and
`method_per_run` longer than the defining lists, `ThetaShift` unset, λ `None`). Add with a value supplied for a compact
list follows the same fills, with the value at index `m` (B-T1).

**Guard (vary what the fix freezes).**

| # | Test (names are suggestions) | RED at `77b5a35` |
|---|---|---|
| S1 | the matrix: every kind × compact state × position (0, `m-1`, a surplus row) × the three documents; for each cell assert the held list, the saved text, `validate()`/`notes()` as the table says, **and the invariant directly** — `NR_Reduction(json_to_config(saved))`'s per-angle reading (truncated to `len(RBnum)`) equals the pre-edit reading for every angle ≠ `i`, or a problem line names the angle | C-1 (broadcast `[]`, `i = 0`): reading changes for angles 1, 2 with no line; C-2 (`ThetaShift [0.01]`): count line + `IndexError` at `:413`; C-3: no refusal |
| S2 | `reducer_default` pin: for every default-if-empty field, `NR_Reduction` built on a config with the list empty fills it with exactly the declared value (`_validate_config` at `:99-110`); `method_per_run`'s default lower-cases to the reducer's `:42-43` literal | attribute absent |
| S3 | the refusal: `set_angle_field(i ≥ m, "LambdaMin", 3.0)` on the surplus document leaves `get("LambdaMin") is None`, and `validate()` carries one line naming `LambdaMin`, the row and the remedy; the view shows the cell unset after the gesture | `[None]*4 + [3.0]`, false some-unset line, `TypeError` at `:452` on reduce |
| S4 (B-T1) | on the surplus document, `add_angle(DBname="d", method_per_run="constantQ", ThetaShift=0.1, LambdaMin=2.5)` puts each value at index `m`, the real angles `0 … m-1` filled per the table (`meanTheta`; `0`; unset + line), the former surplus entries at `m+1 …` | values land at `n`, not `m`, under the `n` mutant |
| S5 (B-T2) | from `LambdaMin: [2.5]*4` on the `m = 3` document, clearing cell 3 produces no some-unset line; clearing cell 1 does | whole-list check → false line |
| S6 | an edit at `i < m` of an empty broadcast list on the Aug2026-shaped file, saved, reduces run 221472 and 221473 through the harness with every angle but `i` reading `meantheta` — the Integrator's §8.5 `edit` probe, extended with the cells above | C-1/C-2 |

**Mutations.**

| # | Mutation | Must red |
|---|---|---|
| P1 | an empty default-if-empty list padded to `i + 1` again (v2's C-1/C-2 behaviour) | S1 (every default-if-empty cell at `i < m`), S6 |
| P2 | `reducer_default` ignored — fill with `None` | S1 (reading changes / line appears where none is allowed), S2 |
| P3 | one declared `reducer_default` changed (`tof_max` → 0) | S2 |
| P4 | broadcast gap `m … i-1` left unset | S1 (broadcast, `i ≥ m`): the reducer raises at `:82` |
| P5 | optional `None` at `i ≥ m` materialised instead of refused (v2) | S3 |
| P6 | optional `None` at `i < m` filled silently (no line) | S1 (optional, `i < m`) |
| P7 | the some-unset rule for optional lists reads the whole list | S5, S1 |
| P8 | Add's with-value index back to `n` | S4 |

Then the whole battery again (37 rows); re-aimed rows recorded.

**Acceptance (v3).** §8 as written; the v2 acceptance repeated with the three edits now defined per cell (`DBname[0]`; `ThetaShift[0]` on the Aug2026 files → saved `[0.01, 0, 0]`-style lists that reduce; a surplus-row edit of a list that already reaches the row); S6 run end to end on the two IPTS-36119 runs; `todo.md` removed in its own commit before `qa/`. The PR body carries the v2 advisories verbatim (selection does not follow Add — highest priority; angle numbering 0 vs 1 between panel and header; `_defining_length` and trailing `None`; A3's missing-required line; `Field.fills_itself`; note wording and visibility; the test reviewer's notes) — none is in this revision's scope, and A3 is the proposed follow-on slug.
