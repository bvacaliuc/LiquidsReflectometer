# Plan: `editor-sections` — sections in the scientists' order, collapsible, remembered per user

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-sections` (refs `triage/…`, `feature/…`,
`qa/editor-sections`) · **Status:** v2 (attempt 2 of N = 3; v1 rejected at `review/editor-sections` @ `1b8fe08` — **tests only**: four declared items with no failing-capable test, B-1…B-4; no production change asked for; see Revision history) — **stacked** `[human, 2026-10-04, posture]`: v1 dispatched 2026-10-04 when `editor-paths-header`'s draft PR #39 opened (its v2 PASS, I-26); v2 continues on `feature/editor-sections` (the Integrator's `todo.md` on top, @ `1b8fe08`); §2 **re-sealed against `agentic/feature/editor-paths-header` @ `0cc96e1`** (PR #39's head; first sealed at `7b6d6b9` — every `settings_editor.py` / `field_spec.py` citation re-measured, F3 re-counted after the header moved three fields, F7–F9 added) ·
**Base:** `agentic/feature/editor-paths-header` @ `0cc96e1` · **PR target:** `feature/editor-paths-header` on the fork, **draft** (retargeted by the human's merges down the stack) ·
**Stack** (posture, "Stacked editor lane" — it governs; this line points): `launcher-test-teardown` (#37) → `editor-defaults-and-theta` (#38) → `editor-paths-header` (#39) → **this slug**, the last; the Developer cuts `feature/editor-sections` `--no-track` from `agentic/feature/editor-paths-header` and regular-merges it forward before every `qa/` push; the Integrator opens the draft PR `--base feature/editor-paths-header`; **the stacked-lane rule retires when this slug is merged** ·
**Depends on:** `editor-paths-header` (it removes IPTS and the two input paths from the list; what remains
of "Output naming" and "Paths" is merged here) · **Review domains:** ui-aspects, test (block) ·
**Kind:** launcher — not reduction-path · **Sources:** scientists' item 7; charter §3 row.

## Declared scope

**Files in:** `src/lr_reduction/field_spec.py` (group order and the merged group), `launcher/apps/settings_editor.py`,
`launcher/tests/test_settings_editor.py`, `tests/unit/lr_reduction/test_settings_document.py`.

**Behaviours in** (S1–S6, §3). **Explicitly OUT:** which *fields* exist, their labels, types, defaults or
help; the Angles table's columns and their order (`PER_ANGLE_NAMES` order is `FIELD_SPEC` order and other
code indexes it — S5); the header (`editor-paths-header`'s "Experiment" box above the splitter, `_build_paths_header` —
it is not a section of the list, it does not collapse, and `HEADER_NAMES` stay excluded from the list — S7); the
launcher's other tabs; any window-geometry persistence; the per-angle-only groups (`Background`, `Theta and scaling`
keep having no box — A4).

## 1. Request

> 7. The list of setting parameters in the lists under the table are in headed sections that are always
> visible as a scrollable list. These sections should be changed to hideable/collapsible lists. If possible
> the user history of which sections are collapsed and expanded should be preserved on reloading the GUI for
> that user. The order of these sections should be changed based on how often they need to be accessed and
> changed. The new order should be: (i) Runs and angles (ii) Processing (iii) Q-space (iv) Wavelength and
> TOF (v) Dead time (vi) Detector resolution (vii) Peak Fitting (viii) Remaining output naming and paths not
> covered by item (6) above (ix) Instrument geometry (x) Runtime record

## 2. Verified facts at the base `0cc96e1` (first measured at `7b6d6b9`; **re-sealed 2026-10-04** — line numbers are `0cc96e1`'s)

| # | Fact | Evidence |
|---|---|---|
| F1 | Section order is incidental: the order groups first appear in `FIELD_SPEC`. | `field_spec.py:773` `GROUPS = tuple(dict.fromkeys(f.group for f in FIELD_SPEC))` ("Groups in the order the editor should present them", `:772`) → `('Runs and angles', 'Background', 'Wavelength and TOF', 'Theta and scaling', 'Output naming', 'Paths', 'Processing', 'Q-space', 'Instrument geometry', 'Dead time', 'Detector resolution', 'Peak fitting', 'Runtime record')` (re-run 2026-10-04 at `0cc96e1`: identical to `7b6d6b9`). The group constants are `field_spec.py:514-526`. |
| F2 | A group with no scalar field *in the list* gets no box. | `settings_editor.py:588-592`: `scalars = [f for f in fs.fields_in(group) if not f.per_angle and f.name not in fs.HEADER_NAMES]` … `if not scalars: continue`. `Background` and `Theta and scaling` hold only per-angle fields → **ten boxes**, the ten the scientists list with "Output naming" and "Paths" as two. |
| F3 | Scalar fields per box **after `editor-paths-header`** (re-counted at `0cc96e1` by evaluating the module). | Runs and angles: `data_x_range` · Wavelength and TOF: `tof_bin` · Output naming: `Sname`, `subname`, `DTCsubname`, `BINsubname`, `errBINsubname` (5 — `experiment_id` moved to the header) · Paths: `_Spath_override`, `_BINpath_override` (2 — the two input overrides moved to the header) · Processing: 8 · Q-space: 5 · Instrument geometry: 9 · Dead time: 2 · Detector resolution: 2 · Peak fitting: 2 · Runtime record: 2. **So the merged section (S2) is exactly seven fields.** |
| F4 | Sections are plain `QGroupBox`es in one `QScrollArea`; nothing collapses. | `settings_editor.py:579-605` (`_build_scalar_panel`: `QScrollArea` `:580`, one `QGroupBox(group)` per group `:593`, `column.addWidget(box)` `:601`). |
| F5 | The tab already owns a `QSettings` bound to the launcher identity, and tests isolate it per test. | `settings_editor.py:449` `ensure_identity()` before `:455` `self.settings = QtCore.QSettings()`; today it stores only `settings_editor_dir` (`:1107-1145`). `launcher/tests/conftest.py:13-27` redirects both formats to a scratch root at import ("Qt caches the settings root at the first QSettings construction in a process") and `isolated_qapp` (`:70`) isolates per test. |
| F6 | The scientists write "Peak Fitting"; the declared group is "Peak fitting". | `field_spec.py:525` `PEAK = "Peak fitting"`. |
| F7 | The header is a box of its own above the splitter, not a section of the list. | `_build_paths_header` (`settings_editor.py:500-512`, `QGroupBox("Experiment")` `:508`), added at `:466` before the splitter (`:468`); `HEADER_NAMES` (`field_spec.py:768`) excluded from the list at one site (`:590`). This slug does not touch it (OUT). |
| F8 | The import-time-check shape already exists in the module. | `field_spec.py:746-764` `_check_choice_labels(field)` raises `ValueError` and is called at module level (`editor-defaults-and-theta`'s learning 4: "an import-time check written as bare asserts can neither be mutated nor survive `python -O`"); `:386` the type-string check "fails at import rather than silently producing an unvalidated, uncoerced text box". S5 takes the same shape — a named function that raises, tested with a broken table. |
| F9 | `PER_ANGLE_NAMES` at the base. | `field_spec.py:715`; value `('method_per_run', 'DBname', 'RBnum', 'RB_Ymin', 'RB_Ymax', 'BkgROI', 'useBS', 'tof_min', 'tof_max', 'LambdaMin', 'LambdaMax', 'ThetaShift', 'ScaleFactor')` (U3 pins it verbatim). |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| S1 | The sections appear in exactly this order: Runs and angles · Processing · Q-space · Wavelength and TOF · Dead time · Detector resolution · Peak fitting · Output naming and paths · Instrument geometry · Runtime record. The order is an explicit declaration in `field_spec.py`, not a by-product of `FIELD_SPEC` order. |
| S2 | "Output naming and paths" is one section holding what `editor-paths-header` left behind: `Sname`, `subname`, the three suffixes, and the two output paths. |
| S3 | Each section can be collapsed and expanded from its heading by mouse and by keyboard; collapsed means its fields take no space and are skipped by Tab. Collapsing never changes a value and never hides a value from `validate()` or from Save. |
| S4 | The expanded/collapsed state of each section is stored per user in the launcher's `QSettings`, written when it changes and applied when the tab is built. First run: every section expanded (today's appearance). A stored state for a section that no longer exists is ignored; a section with no stored state is expanded. |
| S5 | **Fail loudly on drift:** a group used by a scalar field but absent from the declared order (or the reverse) fails at import, the way an unknown type string does. `PER_ANGLE_NAMES` and its order are unchanged, and a test pins that. |
| S6 | A problem line that names a field in a collapsed section is still shown in the panel (it always was); the section stays as the user left it. |
| S7 | The header ("Experiment", F7) is untouched: still above the splitter, not collapsible, not in the declared order, and its three fields still absent from the list. |

**States** (per section): expanded / collapsed × stored / not stored / stored-but-garbage (`"maybe"`, a
list) × section exists / renamed. Garbage and unknown keys → expanded, nothing raised, the bad key left
alone. Stored values are read with an explicit boolean parse — `QSettings` in INI format returns the
**strings** `"true"`/`"false"`, and `bool("false")` is `True`.

**Operation × state (every cell is a required outcome, and every cell is named by a test — V9).** Per section, held
state ∈ {**E** expanded (first run or stored `true`); **C** collapsed (stored `false`); **G** stored garbage (`"maybe"`,
`[1]`, `""`); **U** key for a section that no longer exists}. "Panel" means `tab.report.toPlainText()`.

| Operation | E | C | G | U |
|---|---|---|---|---|
| build the tab | fields visible (`isVisibleTo(tab)`), reachable by Tab | fields hidden, skipped by Tab, heading still reachable; **the body takes no space — the next heading's `y()` is higher by at least the body's height (S3)** | expanded (as E); no exception; **each** bad value (`"maybe"`, `[1]`, `""`) left in the store **as written** | ignored; no exception; the key left in the store |
| toggle by mouse click on the heading | → C; store written `false`; no document write (`changed_vs_seed() == {}`); panel unchanged | → E; store `true` | → C (it was shown expanded) | n/a |
| toggle by keyboard (heading focused, Space / `Key_Return` / keypad `Key_Enter` — **each key its own leg**) | same as the click | same | same | n/a |
| collapse, then expand, **with no Load in between** | every editor under the section shows the document's value — line edit `text()`, combo current entry, check box state (B-2: a clear-on-collapse is invisible to Save, `changed_vs_seed()` and the panel because editors write on `editingFinished`) | → E then → C: the same | as E | n/a |
| Tab through the panel | every field of the section is in the Tab order | none of its fields is; the next section's heading follows | as E | n/a |
| edit a field, then collapse, then Save | the edit is in the file | — | as E | n/a |
| Load a file while collapsed | editors inside refreshed (expand and read: the file's value) | same | — | n/a |
| a problem in the section | the line in the panel | the line in the panel; the section stays collapsed | as E | n/a |
| build a second tab in the same store | same state as left | same state as left | expanded | ignored |
| the store is unwritable | toggling still works for the session; no exception leaves the slot; `_last_error is None` | same | same | n/a |

Decision — **keys by group identity, not position:** the stored key is derived from the section's declared
name, so re-ordering (this slug, or a later one) cannot hand one section another's state.

## 4. Files to change

| File | Change |
|---|---|
| `field_spec.py` | the declared order; the merged group constant; the import-time check (S5); `GROUPS` derives from the declaration |
| `settings_editor.py` | a collapsible section (one small class or helper — one definition); state read/write through `self.settings`; the group loop (`:588-601`) builds the section in the declared order, with the `HEADER_NAMES` exclusion kept (F7) |
| tests | §6 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | open the tab for the first time | ten sections, declared order, all expanded |
| common | collapse "Instrument geometry", restart the launcher | still collapsed; others as left |
| common | edit a field, collapse its section, Save | the edit is in the file |
| edge | Load a file while sections are collapsed | values refresh inside collapsed sections; state unchanged |
| edge | a problem in a collapsed section | reported in the panel |
| edge | two users on one machine | separate stores (QSettings user scope) — stated, not tested here |
| edge | keyboard only | heading reachable by Tab, toggled by Space/Enter |
| pathological | stored value `"false"` (INI string) | section collapsed — not expanded by `bool("false")` |
| pathological | stored value garbage / key for a removed section | expanded / ignored; no exception in `__init__` (a raise there kills the launcher at start-up) |
| pathological | a new `Field` added later with a new group name and no order entry | import fails with a message naming the group |
| pathological | settings store unwritable | toggling still works for the session; no exception leaves the slot |
| edge | the header after the regrouping | still above the splitter, not collapsible, its three fields not in any section (S7) |
| edge | toggle every section, then `changed_vs_seed()` and the panel | `{}`; panel unchanged — collapsing is view state, never a document edit |

## 6. Red-Green TDD seed

| # | Test (names are suggestions) | RED at the base |
|---|---|---|
| U1 | the declared order is exactly the ten names of S1 | no declaration |
| U2 | every group of a scalar field is in the order and vice versa; **(v2, B-1) the wiring, not the function:** import a *modified copy of the module source* (exec the edited source under a new module name, or a subprocess `python -c`) with a field in a group absent from `SECTION_ORDER`, and expect `ValueError` naming that group **from the import itself** — so deleting the module-level `_check_section_order(FIELD_SPEC, SECTION_ORDER)` call reds it; calling the function directly (v1) does not exercise the call site | — |
| U3 | `PER_ANGLE_NAMES` equals the base tip's tuple, verbatim | passes — the pin for S5 |
| U4 | the merged section's fields are exactly the seven of S2 (after `editor-paths-header`) | two groups |
| V1 | the section headings in the tab, top to bottom, equal the declared order | base order (F1) |
| V2 | toggling a heading with the keyboard hides and shows its fields (`isVisibleTo(tab)` on a field editor, on a shown tab); **(v2, B-3)** and the space is gone — on collapse the next section's heading `y()` (mapped to the panel) decreases by at least the body's height, and returns on expand; **(v2, test A-1)** driven by Space, `Key_Return` and keypad `Key_Enter` as three legs | not collapsible |
| V3 | the state survives a new tab instance in the same isolated store: collapse two, build a second `SettingsEditorTab`, same two collapsed | — |
| V4 | a stored INI string `"false"`/`"true"` is read as its meaning (write the raw string into the store, then build the tab) | — |
| V5 | garbage and unknown keys → all expanded, constructor does not raise; **(v2, B-4)** and the store still holds **each** garbage value as written — `"maybe"`, `[1]` and `""` read back raw, plus the orphaned key — so the docstring "the bad values stay in the store as they were" is true for all three | — |
| V6 | a value edited before collapsing is saved; a collapsed section's invalid value is still reported | — |
| V7 | `set_document` refreshes editors inside a collapsed section (expand afterwards and read the widget) | — |
| V11 | **(v2, B-2)** collapse → expand with **no Load between** — each editor under the section shows the document's value: a section with line edits (Instrument geometry, `mmpix`), one with a combo (Detector resolution, `DetResFn`) and one with a check box (Processing, `Normalize`); assert `text()` / current entry / `isChecked()` against `document.get(...)` after the expand | passes at `b9ad10c`; red under the clear-on-collapse mutant |
| V8 | collapsing changes nothing: `changed_vs_seed()` empty **and the panel text unchanged** after toggling every section | — |
| V9 | §3's operation × state table, parametrized over E/C/G/U × the operations on a **shown** tab (`_shown_tab`), each cell asserting field visibility (`isVisibleTo(tab)`), the Tab order where the cell says so, the store's value after a toggle (read back raw and parsed), `changed_vs_seed()`, the panel text, and `tab._last_error is None`; the docstring says exactly what is asserted | the states have no tests |
| V10 | the header is untouched: `tab.paths_header` is above the splitter, has no toggle, and `HEADER_NAMES` are in no section (S7; the `editor-paths-header` tests V1 still pass); **(v2, test A-3) made non-vacuous:** `tab.paths_header.isCheckable() is False`, it is not wrapped in a `_Section` (`isinstance` / not among `tab.sections.values()` **and** the header's `QGroupBox` is a direct child of the tab's layout), and its `y()` is above the first section heading's — so making the header checkable or wrapping it reds | passes — the pin for S7 |
| U5 | `GROUPS` equals the declared order's groups plus the per-angle-only groups, i.e. the declared order is a permutation of the groups that have a list scalar — nothing added, nothing lost | — |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| swap two entries of the declared order | U1, V1 |
| `GROUPS` computed from `FIELD_SPEC` order again | V1 |
| import-time check removed (the module-level call deleted, `field_spec.py:795` at `b9ad10c`) | U2 (**through the import of an edited copy** — B-1) |
| state keyed by position instead of name (then reorder in the test) | V3 variant that reorders — add it if the mechanism could be positional |
| state read with `bool(value)` | V4 |
| state never written (read only) | V3 |
| default-collapsed on first run | V5 / a first-run assertion in V1 |
| collapsed section's editors detached from `self.editors` | V7, V6 |
| collapse implemented by clearing or disabling values | V8, V6, **V11 (clearing — B-2: the v1 battery mutated only the disabling half)** |
| **(v2)** collapsed body keeps its space (`setRetainSizeWhenHidden(True)`) | V2 (space leg — B-3) |
| **(v2)** garbage removed from the store at build, for non-strings only / for `""` only | V5 (each form read back raw — B-4) |
| **(v2)** keypad `Key_Enter` dropped from the heading's keys | V2 (`Key_Enter` leg) |
| **(v2)** the header `QGroupBox` made checkable | V10 |
| per-angle order changed by the regrouping | U3 |
| the header box made a collapsible section / its fields pulled into the list | V10 |
| toggle slot writes the document (e.g. calls `_set_scalar`) or refreshes the panel differently | V8 (panel leg), V9 |
| state keyed by heading *text* and the merged section's text changed | V3 variant: rename the merged section in a copy of the order → the stored key for the others still applies (positional or text keys both red one leg) |
| store write raises (monkeypatched `setValue`) and the slot lets it escape | V9 (unwritable row): `_last_error is None`, toggle still took effect |

Frame: the collapsible section is constructed once per group (one site, the loop in `_build_scalar_panel`,
`settings_editor.py:588-601` at the base); state read (construction) and state write (toggle slot) are one site each;
the toggle slot is `@guarded` and touches `self.settings` only — never `self.document`; the `HEADER_NAMES` exclusion
(`:590`) stays where it is.

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root on the feature tip.
2. §6 RED→GREEN; §7 recorded per row.
3. Prose claims verified or marked inferred — in particular what `QSettings.value()` returns for a stored
   boolean in INI format on this Qt (print it; quote the observation).
4. Deployment-shaped acceptance (Integrator, analysis node, via the launcher as scientists start it):
   collapse three sections, quit, start again from a fresh login shell — the same three are collapsed
   (this crosses the login hook that wipes `$XDG_CACHE_HOME`; QSettings lives under `$XDG_CONFIG_HOME` —
   confirm the store's path with `QSettings().fileName()` and quote it).
5. PR body: launcher-only; visible after merge + re-deploy of the review tier; **names the stack** (#37 → #38 → #39 → this)
   and that the stacked-lane rule retires with this slug's merge (posture).
6. Integrator's real-tab acceptance also drives: Tab from the header's last control into the first section's heading; a
   problem line for a field in a collapsed section stays in the panel; collapse all ten → `changed_vs_seed() == {}`.

## 9. Learnings relied on

- `settings-editor-learning.md` §7: "`bool("False")` is `True`" → V4.
- `launcher/tests/conftest.py` (base): "Qt caches the settings root at the first QSettings construction in
  a process" → tests use `isolated_qapp`; a second tab instance, not a second process, proves persistence
  at unit level; the real restart is criterion 4.
- `settings-editor-learning.md` §5: a raise in a slot or constructor path kills the launcher → V5, the
  guarded toggle.
- `field_spec.py` (base) asserts unknown types at import "rather than silently producing an unvalidated,
  uncoerced text box" → the same shape for S5 — as a **named function that raises**, tested with a broken table
  (`editor-defaults-and-theta` learning 4: bare asserts can neither be mutated nor survive `python -O`; F8).
- The campaign's standing lesson (A-16, A-23, A-29, A-34, A-38): every rejection so far was a state or an operation the
  plan enumerated without pinning, or did not enumerate — so the operation × state table is named by one parametrized
  test (V9), "panel" means `tab.report.toPlainText()`, and a declared cell with no test is a declared defect.
- `editor-paths-header` v1's rejection (B-1): a cell that says "panel" must be asserted on the panel widget, not on the
  model's `changed_vs_seed()` / `validate()`.
- **(v2)** this slug's own v1 rejection: **a §7 row must name a test that observes through the path the mutation breaks** —
  the import-time *call site* (not the function), expand-then-read (not reload-then-read), the geometry (not visibility),
  each garbage form (not one). A test that passes under the faithful mutant is not the row's guard, whatever the row says.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | First-run state. | All expanded (no surprise on upgrade). |
| A2 | Heading text "Peak fitting" (declared) vs the scientists' "Peak Fitting". | Keep the declared spelling; a label-only change if they want the capital. |
| A3 | "Runs and angles" holds one scalar (`data_x_range`); "Wavelength and TOF" one (`tof_bin`). | Kept as sections — the scientists list both. |
| A4 | The per-angle-only groups (`Background`, `Theta and scaling`) get no section, as today. | Yes. |

## Revision history

v1 — authored 2026-10-02 against `7b6d6b9` (staged); **re-sealed and dispatched 2026-10-04 stacked on `feature/editor-paths-header`
@ `0cc96e1`** when draft PR #39 opened (`[human, 2026-10-04, posture]`; A-40). At the re-seal: `GROUPS` re-evaluated at the base (order
identical); F3 re-counted after `editor-paths-header` moved `experiment_id` and the two input overrides to the header — the merged
section is exactly the seven fields of S2; F7 (the header is OUT, S7), F8 (the import-time-check shape), F9 (`PER_ANGLE_NAMES` value)
added; every `settings_editor.py` / `field_spec.py` citation re-measured; the operation × state table and V9/V10/U5 added so every
declared cell is a test; V8 asserts the panel. The last slug of the stacked lane: the posture rule retires when it is merged. Developer:
RED `2b91907`, GREEN `5ba08f6`, battery `b9ad10c` (D-30). **Rejected** at `review/editor-sections` @ `1b8fe08` (the Integrator's `todo.md`
at that commit) — tests only.

### v2 — 2026-10-04 (attempt 2 of 3; the work order for `triage/editor-sections-v2` — **tests only, no production change**)

**Rejection.** `review/editor-sections` @ `1b8fe08` — `todo.md` at that commit (Integrator, Claude Opus 5.5): *"Verdict: REJECT — tests
only. The behaviour passes every reviewer and the deployment-shaped acceptance; four declared items have no test that fails when they
break (two §7 rows survive in faithful forms, one S3 clause and one States case are unasserted). No production change is asked for.
Stacked slug: v2 continues on `feature/editor-sections` (base `feature/editor-paths-header` @ 0cc96e1, merged forward per the posture
before `qa/`). Not infrastructure."* Gate green (launcher 628, reduction 725); ui-aspects PASS on every gesture; the 18-row battery
reproduced; the Integrator's acceptance passes **including the restart from a fresh login shell through the launcher's own `main()`**
(the store is `$HOME/.config/ORNL/lr_reduction_new_launcher.conf`, untouched by the login hook's cache wipe) — §"What passed (do not
redo)" stands; **the Developer does not redo it**.

> **BLOCKING — B-1: deleting the import-time call survives** (§7 "import-time check removed", rule b; S5 / §5 "import fails naming the
> group", rule a). U2 calls `fs._check_section_order` directly, so the module-level call can go. Reproduction (Integrator, archive copy
> of b9ad10c with a resolution test): delete `field_spec.py:795` `_check_section_order(FIELD_SPEC, SECTION_ORDER)` → **1078 passed**. The
> wiring itself works (a copy with an added field in a new group raises `ValueError: … missing ['Brand new group'] …` at import).
> **Fix (tests; domain = the one import-time call site):** a test that imports a modified copy of the module source (exec the edited
> source, or a subprocess) with a field in a group absent from `SECTION_ORDER`, and expects the `ValueError` naming that group — so
> removing the call reds it.
>
> **BLOCKING — B-2: "collapse implemented by clearing values" survives** (§7, rule b). The battery mutated only the disabling half (M9).
> Mutant: in `_Section._show_body`, after `self.body.setVisible(expanded)`, `if not expanded:` clear every `QLineEdit` under the body →
> **1077 passed**. Editors write on `editingFinished`, so a programmatic clear leaves the document intact and Save, `changed_vs_seed()`
> and the panel stay green; V7 and the load-collapsed cells reload before expanding. No test does collapse → expand → read the editor.
> **Fix (tests; domain = every editor kind under a section — line edits, combos, check boxes):** after a C → E toggle, assert each of
> the section's editors shows the document's value (text / current entry / check state), on a section that holds a line edit and one
> that holds a combo.
>
> **BLOCKING — B-3: S3 "collapsed means its fields take no space" has no test** (rule a). Reproduction: in `_show_body`, set
> `setRetainSizeWhenHidden(True)` on the body's size policy → **1078 passed**; the probe confirms the mutant keeps the space. **Fix
> (tests):** in V2 or V9's C cells, assert the space is gone — the next section's heading `y()` decreases by at least the body's height
> on collapse, and returns on expand.
>
> **BLOCKING — B-4: G's "the bad value left in the store" is asserted for `"maybe"` only** (rule a; rule d on V5's docstring). V9's G
> column uses only `"maybe"`; V5 covers `"maybe"`, `[1]` and `""` for "expanded, nothing raised", and its docstring says "the bad values
> stay in the store as they were", but it asserts only the orphaned `"Paths"` key. Mutants: at build, remove a garbage value only when
> it is a non-string → **1077 passed**; only when it is `""` → **1077 passed**. **Fix (tests; domain = the three garbage forms the plan
> names):** V5 asserts the store still holds each garbage value as written (`[1]` and `""` included), so V5's docstring is true.

**What the plan missed (the Analyst's defects).** Each §7 row named a test, but the named test did not observe through the path the
mutation breaks: U2 reached the *function* while the row mutates the *call site*; V7/V6 reload before reading while the row mutates
what a collapse does to the widgets; S3's "no space" was a behaviour with no geometry test at all; the States paragraph listed three
garbage forms and V5 pinned one. The plan's mutation table is only a contract when each row's test fails under the row's faithful
mutant — the Integrator ran them and four did not.

**Changes in v2 (tests only).** U2 through the import of an edited copy (B-1); **V11** collapse → expand → read each editor kind,
no Load between (B-2); V2 gains the geometry leg (B-3) and three key legs — Space, `Key_Return`, keypad `Key_Enter` (test A-1
adopted: the table said "Enter"); V5 reads back each garbage form raw (B-4); V10 made non-vacuous (test A-3 adopted: `isCheckable()
is False`, not a `_Section`, above the first heading); the table's cells say what each test now asserts; five mutation rows added.
The remaining advisories (test A-2, A-4–A-6; ui-aspects A1–A5 — the pressed-button look of an expanded heading and the narrow
click target are worth the human's eye, not this slug's gate) go to the PR body.

**Unchanged:** S1–S7, F1–F9, U1, U3–U5, V1, V3, V4, V6–V9, every v1 mutation; **no production file changes are asked for** — if the
Developer finds a production change necessary to make a test pass, that is a finding to record in the transcript, not a silent edit;
base `feature/editor-paths-header` @ `0cc96e1` (re-checked 2026-10-04: still PR #39's head; `exp-review` still `b86237b`); the
Developer continues on `feature/editor-sections` from `1b8fe08`, merges `agentic/feature/editor-paths-header` forward before `qa/`,
keeps the v1 battery and extends it. **Retry arithmetic:** attempts_done = 1 + 1 = 2 → v2 is attempt 2 of 3; a third rejection
escalates.
