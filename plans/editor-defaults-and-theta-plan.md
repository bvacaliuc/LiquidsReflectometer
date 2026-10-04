# Plan: `editor-defaults-and-theta` — a new settings file starts at `gaussian` / `1.0`; "Apply theta calculation" offers False / True / trust sample angle and stores the canonical value

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-defaults-and-theta` (refs `triage/…`, `feature/…`,
`qa/editor-defaults-and-theta`) · **Status:** READY — v1 (attempt 1 of N = 3) — **stacked** `[human, 2026-10-04, posture]`: dispatched 2026-10-04 when `launcher-test-teardown`'s draft PR #37 opened; §2 sealed against `agentic/feature/launcher-test-teardown` @ `ed663f7` (PR #37's head; every file this plan cites is blob-identical to `exp-review` @ `b86237b` — `git diff --stat b86237b ed663f7 -- src launcher/apps launcher/new_launcher.py` is empty; the teardown slug changed only `launcher/tests/conftest.py` and `launcher/tests/test_harness.py`) ·
**Base:** `agentic/feature/launcher-test-teardown` @ `ed663f7` · **PR target:** `feature/launcher-test-teardown` on the fork, **draft** (retargeted to `exp-review` by the human's merge of the predecessor) ·
**Stack** (posture, "Stacked editor lane" — it governs; this line points): `launcher-test-teardown` (PR #37) → **this slug** → `editor-paths-header` → `editor-sections`; the Developer cuts `feature/editor-defaults-and-theta` `--no-track` from `agentic/feature/launcher-test-teardown` and regular-merges it forward before every `qa/` push; the Integrator opens the draft PR `--base feature/launcher-test-teardown` ·
**Depends on:** `editor-combos` (merged: the wheel-safe combo this slug's theta control uses) and the stack order ·
**Review domains:** design, numerical-diagnostics, test (block) · **Kind:** launcher / settings model — not
reduction-path (no reducer file changes; the library defaults stay) ·
**Sources:** scientists' items 3 and 4; Q2 and Q3 (`[human, 2026-10-02]`); charter §3 row.

## Declared scope

**Files in:** `src/lr_reduction/field_spec.py`, `src/lr_reduction/settings_document.py`,
`launcher/apps/settings_editor.py`, their two test modules.

**Behaviours in** (D1–D6, §3). **Explicitly OUT:** `nr_reduction_config.py`'s own defaults and every other
reducer file — Q2: "editor only; the library change becomes a separate, science-signed slug"
(`library-defaults-detres`, parked); the meaning of `DetSigma` under each resolution function (a question
for the numerical reviewer to record, not to change); `reduction_domains.CALC_THETA_CHOICES` (the stored
domain stays `("detector_angle", "sample_angle")`); section order; any other field's label.

## 1. Request

> 3. A couple of the defaults need to be changed for the initial load owing to a change in the instrument
> operation: (i) detector resolution function should default to 'gaussian' (ii) detector resolution sigma
> should default to 1.0
>
> 4. The 'theta source' entry should be changed to be labelled as 'apply theta calculation'. The options in
> the drop-down should read as 'False', 'True' or 'trust sample angle'. … False means the calculation is not
> applied. True means the calculation is applied trusting TTHD (i.e. the detector_angle option within
> nr_calc …). 'trust sample angle' means to set this to 'sample_angle'. This logic should apply to both
> saving out a new settings file and loading in and reading a prior settings file.

Q3: "store the canonical value; load accepts every legacy spelling."

## 2. Verified facts (first measured at `7b6d6b9`; **re-run 2026-10-04 at `b86237b`**, and **sealed at the base `ed663f7`** — every cited file is the same blob on `feature/launcher-test-teardown` @ `ed663f7` as at `b86237b` (the teardown slug changed only `launcher/tests/`), so the line numbers below are the base's)

| # | Fact | Evidence |
|---|---|---|
| F1 | Library defaults are `rectangular` / `0.8`, and `FIELD_SPEC` mirrors them. | `nr_reduction_config.py:98-99`; `field_spec.py:605-609` (`DetResFn`, `DetSigma`). At `b86237b`: `NRReductionConfig()` → `rectangular 0.8 False`; `fs.get(...).default` the same. |
| F2 | `Field.default` is **pinned** to the config class's value. | `tests/unit/lr_reduction/test_settings_document.py:51` `test_field_spec_defaults_match_the_config`, `:96` `test_defaults_match_a_fresh_config`. So the editor's starting value cannot be expressed by editing `default` — it needs its own declaration. |
| F3 | The tab starts from a bare document. | `settings_editor.py:446` `SettingsDocument()`; `launcher/new_launcher.py:50` constructs `SettingsEditorTab()` (guarded by `test_the_launcher_carries_the_tab`, `test_settings_editor.py:217`). |
| F4 | A file that omits a key takes the **library** default on load. | `json_to_config` (`new_reduction_from_file.py:439-449`) starts from `NRReductionConfig()`. That is also what reducing that file would use. |
| F5 | The reducer's theta rule. | `nr_reduction_calc.py:90-97`: falsy → not applied; `is True` → `'detector_angle'`; otherwise `.lower()` must be in `lowered(CALC_THETA_CHOICES)` or `ValueError`. Dispatch at `:543-574`. |
| F6 | What the editor does with each spelling today (run 2026-10-02 at `7b6d6b9`, identical at `b86237b`). | `from_dict({"useCalcTheta": v})` → `True` → migrated to `'detector_angle'` (`_migrate_legacy`, `settings_document.py:139`); `'Detector_Angle'`, `'SAMPLE_ANGLE'` → kept as typed, no problem line; `'TRUE'`, `'true'`, `1` → kept, reported "is not one of detector_angle, sample_angle"; `0`, `None`, `''` → kept, quiet (falsy). The load path is `from_dict` (`:95`) → `_canonicalize_booleans` (`:115`, from `editor-load-fidelity`; does not touch this field) → `_migrate_legacy`. |
| F7 | The control today: label "Theta source", a combo with a blank first entry then the two stored names. | `field_spec.py:545-548` (`falsy_means_off=True`); `settings_editor.py:563-600` (`_build_editor`; the blank entry at `:587`); since `editor-combos` the scalar combos are `NoWheelComboBox` (`:102`) with the menu-button convention and focus release — this slug's control inherits them; `_show_in_combo` `:653-663`. `test_theta_source_is_a_choice_not_a_checkbox` (`test_settings_editor.py:350`), `test_a_combo_follows_the_document_when_a_field_is_omitted` (`:372`) assert the current texts — **rewritten**, not deleted, by this slug. |
| F8 | `save()` writes the whole document, so a new file states both resolution keys explicitly. | `settings_document.py` `save` (whole document through the file-boundary encoder; the encoder touches `useBS` and the compact lists only — neither of this slug's fields). |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| D1 | **A document the editor creates** (tab opened with no document) starts with `DetResFn = "gaussian"`, `DetSigma = 1.0`. The starting values are declared on the `Field` (a separate attribute; unset means "same as `default`"), and are part of the seed — "Changed from the seed" is empty on a fresh tab. |
| D2 | **Nothing else moves.** `NRReductionConfig()` still gives `rectangular`/`0.8`; `Field.default` still equals it; `SettingsDocument()` (the bare constructor other code uses) is unchanged; a **loaded** file that omits the keys shows `rectangular`/`0.8` — what reducing that file would use (F4). |
| D3 | The control is labelled **"Apply theta calculation"** and offers exactly three entries, in this order: `False`, `True`, `trust sample angle`. No blank entry. |
| D4 | The entries map to the stored values `False`, `"detector_angle"`, `"sample_angle"`. The mapping is declared once (on the `Field`), used for both directions; the stored domain in `reduction_domains` is untouched. |
| D5 | **Load canonicalises what the reducer accepts** (F5): `True` → `"detector_angle"`; any case of the two names → the lower-case name; any falsy value (`False`, `None`, `0`, `""`) → `False`. So a save after a load writes one of the three canonical values. |
| D7 | **Load → save never changes what the reduction does with `useCalcTheta`** (the lesson of `editor-load-fidelity` v1's rejection, `review/…` @ 8b62952: canonicalising a value is only safe after *every* reader of the field has been read). Readers at `7b6d6b9`: `nr_reduction_calc.py:92` (truthiness), `:93-95` (`is True` → `'detector_angle'`, then `.lower()`), `:96` (membership), `:543`, `:574` (truthiness), `:550` (`== 'detector_angle'`); `web_report.py:432` prints it; `new_reduction_from_template.py:239` copies it into a template object. Each canonicalisation of D5 is one the reducer itself performs before it acts (`True` → name; lower-casing) or one that no reader can tell apart (falsy → `False`). Re-enumerate the readers at dispatch; a new reader that distinguishes `None`/`0`/`""` from `False`, or `True` from the name, removes that row from D5. |
| D6 | **Anything the reducer would reject is reported, shown as itself, and kept** — `"true"`, `"TRUE"`, `"yes"`, `1`, `"detector"`. The editor does not guess that the string `"true"` meant `True`: the reducer raises on it, and a silent rewrite would turn a failing file into one that reduces differently from what its author can have run. |

**Types and states** (the value in `useCalcTheta`):

| Loaded value | held after load | control shows | problem line | saved |
|---|---|---|---|---|
| key absent, `False`, `None`, `0`, `""` | `False` | `False` | none | `false` |
| `True` (JSON `true`) | `"detector_angle"` | `True` | none | `"detector_angle"` |
| `"detector_angle"` in any case | `"detector_angle"` | `True` | none | `"detector_angle"` |
| `"sample_angle"` in any case | `"sample_angle"` | `trust sample angle` | none | `"sample_angle"` |
| `"true"`, `"TRUE"`, `1`, any other string, a list | as loaded | the value itself, as an extra entry | yes, naming the three accepted forms | as loaded |

`DetResFn` / `DetSigma` by entry path: editor-created document → `gaussian`/`1.0`; `SettingsDocument()` →
`rectangular`/`0.8`; loaded with the keys → the file's; loaded without → `rectangular`/`0.8`; document
injected into the tab → whatever it holds (the tab does not re-initialise a document it was given).

**Operation × state (the axis the predecessors' rejections taught; every cell is a required outcome).** Field
`useCalcTheta`; held state ∈ {`False` (fresh or loaded falsy), `'detector_angle'`, `'sample_angle'`, a rejected spelling
(`'true'`, `1`, `'detector'`)}:

| Operation | `False` | `'detector_angle'` | `'sample_angle'` | rejected spelling |
|---|---|---|---|---|
| Load / display | entry `False` shown; no line | entry `True`; no line | entry `trust sample angle`; no line | the raw value shown as an extra entry; a problem line |
| open the list (one click / Enter / Space / Alt+Down), choose the shown entry | identity: no write, nothing in "Changed from the seed" | identity | identity | identity (the raw value stays; the line stays) |
| choose another entry | the canonical stored value of that entry; one "Changed" line | same | same | the canonical value replaces the raw one; the line clears |
| Escape / Tab / click-away with no deliberate move | identity | identity | identity | identity |
| wheel / Up / Down on the closed combo, focused or not | no change | no change | no change | no change |
| Save | `false` | `"detector_angle"` | `"sample_angle"` | as held |
| Load a second file omitting the key | shows `False`; document `False` | same | same | same |

`DetResFn` / `DetSigma` by entry path: editor-created document → `gaussian` / `1.0`; `SettingsDocument()` →
`rectangular` / `0.8`; loaded with the keys → the file's; loaded without → `rectangular` / `0.8`; injected document →
as held. The first-use gestures of the three controls (reach by click or Tab; open; choose; re-choose; leave) are
acceptance rows (§8.4), not "launch the tab".

## 4. Files to change

| File | Change |
|---|---|
| `field_spec.py` | the editor-starting-value attribute (set on `DetResFn`, `DetSigma`); the choice-label mapping on `useCalcTheta`; label text; a derived tuple of the fields that carry a starting value |
| `settings_document.py` | a constructor for an editor-created document (applies the starting values, then takes the seed); theta canonicalisation in the load path |
| `settings_editor.py` | the tab's default document comes from that constructor; the theta combo shows labels and stores canonical values; out-of-set display kept |
| tests | §6; two existing theta tests rewritten to the new texts |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | open the tab, add angles, save | file holds `"DetResFn": "gaussian"`, `"DetSigma": 1.0`, `"useCalcTheta": false` |
| common | choose `True`, save, reload | stored `"detector_angle"`; control shows `True` |
| common | choose `trust sample angle` | stored `"sample_angle"` |
| common | load an autoreduce file with `"useCalcTheta": "detector_angle"` | shows `True`; no problem; unchanged on save |
| edge | load a file that omits `DetResFn` | shows `rectangular` — **not** `gaussian`; the panel is quiet |
| edge | load a legacy file with `"useCalcTheta": true` | shows `True`; saved as `"detector_angle"`; "Changed from the seed" empty |
| edge | load `"Sample_Angle"` | held and saved as `"sample_angle"` |
| edge | load file A (`sample_angle`), then file B omitting the key | control shows `False`; document `False` (the base's silent-stale case, kept guarded) |
| edge | a document injected by other code | its values are shown; no starting values applied |
| pathological | `"useCalcTheta": "true"` (string) | reported, shown as itself, saved as loaded |
| pathological | `"useCalcTheta": ["detector_angle"]` | reported; no exception leaves a slot |
| pathological | a third stored choice added to `CALC_THETA_CHOICES` without a label | fails loudly at import or in a named test — never an unlabeled entry |

## 6. Red-Green TDD seed

| # | Test (names are suggestions) | RED at the base |
|---|---|---|
| U1 | an editor-created document starts at `gaussian` / `1.0`, and `changed_vs_seed()` is empty | no such constructor |
| U2 | `SettingsDocument()` and `NRReductionConfig()` still give `rectangular` / `0.8` | passes — the pin for D2 |
| U3 | a loaded file without the keys holds `rectangular` / `0.8` | passes — pin |
| U4 | the starting-value fields are exactly `{"DetResFn": "gaussian", "DetSigma": 1.0}` | attribute absent |
| U5 | theta load table — one parametrized case per row of §3's table, asserting held value **and its type**, problem lines, and saved JSON text | case rows for mixed case and falsy-non-`False` red |
| U7 | the reduction reads the saved file as it read the source: for every accepted spelling of §3's table, the value after the reducer's own normalisation (`nr_reduction_calc.py:92-97`, applied by the test to source and to saved) is equal, and the type of a falsy result is not relied on by any reader (pin the reader list of D7 with a grep-derived count) | — (guard) |
| U6 | every stored theta choice has a label and every label maps back (round trip over the mapping; `False` included) | mapping absent |
| V1 | a fresh tab shows `gaussian` and `1.0` | `rectangular` / `0.8` |
| V2 | the control's label reads "Apply theta calculation"; its entries are exactly `["False", "True", "trust sample angle"]` | "Theta source"; `["", "detector_angle", "sample_angle"]` |
| V3 | choosing each entry (keyboard, through the combo) stores `False` / `"detector_angle"` / `"sample_angle"` — assert `is False` for the first, not `== 0` | — |
| V4 | Load of each accepted spelling selects the right entry | — |
| V5 | Load A then B (key omitted) shows `False` | rewritten from `test_a_combo_follows_the_document_when_a_field_is_omitted` |
| V6 | a rejected spelling is displayed as itself and the panel names the field | — |
| V7 | the tab given a document does not apply starting values | — |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| tab's default document built with the bare constructor again | V1 |
| starting value for `DetSigma` removed (or set to `0.8`) | U1, U4 |
| starting values applied in `SettingsDocument.__init__` (leaking into every document) | U2, U3, V7 |
| seed taken before the starting values are applied | U1 (seed leg) |
| label mapping swaps `True` and `trust sample angle` | V3, U6 |
| blank entry restored | V2 |
| case canonicalisation removed from load | U5 (mixed-case rows) |
| falsy canonicalisation removed | U5 (`None`/`0`/`""` rows — assert on type/`is False`) |
| string `"true"` accepted as `True` | U5 (rejected rows) |
| a canonicalisation the reducer does not itself perform is added (e.g. `"sample"` → `"sample_angle"`) | U7 |
| the control stores the label text (`"True"`) instead of the canonical value | V3 |

Frame: the editor-document constructor has one call site (the tab's default); the label mapping is used at
build and at refresh (`_show` / `_show_in_combo`) — one row each; if `_migrate_legacy` is extended rather
than a new helper added, its existing behaviour for `True` keeps its existing guard (run it under each mutation).

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root on the feature tip.
2. §6 RED→GREEN; §7 recorded per row.
3. **Numerical-diagnostics review** receives, in the PR body: the two-source audit for the resolution pair —
   the static defaults (`nr_reduction_config.py:98-99`), the editor's starting values, and one real settings
   file's values (path + sha256, from the Integrator) — and a statement of what `DetSigma` multiplies in
   each branch of `nr_tools.calc_beam_on_detector` (`:387-402`), read from the code, not inferred. No number
   in the reduction changes in this slug; the review confirms that statement by running an existing
   reduction test before and after (identical output).
4. Deployment-shaped acceptance (Integrator): launch the tab from the feature tip — new document shows
   `gaussian`/`1.0`; load a real autoreduce settings file — the theta control shows the entry matching the
   file, the panel is quiet about it, and save-then-diff shows no change in `useCalcTheta`, `DetResFn`,
   `DetSigma` beyond canonical spelling.
5. PR body: launcher-only; **states plainly that files which omit the resolution keys are still reduced with
   `rectangular`/`0.8`** until `library-defaults-detres` is signed.

## 9. Learnings relied on

- `settings-editor-learning.md` §7: "`useCalcTheta` was declared `bool` while the reducer accepts
  `'detector_angle'`/`'sample_angle'` — so the editor rendered a checkbox that could not express one of the
  two values and silently downgraded a loaded one … migrate a legacy spelling the consumer still accepts
  instead of reporting it, or the panel cries wolf on a file that works." → D5; and its limit, D6.
- §4: "it must enforce the shape the *consumer* actually accepts, not a tidier one." → the accepted set is
  read off `nr_reduction_calc.py:90-97`.
- `campaign-learnings-synthesis.md` §C (one behaviour, two implementations): build and refresh once showed
  a value differently → one mapping, used by both.
- CPKT `numerical-diagnostics.md`: audit static vs runtime sources for every input before interpreting a number.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | "Every legacy spelling" = every spelling the **reducer** accepts today (F5). Strings such as `"true"` are not among them. | Reported, not rewritten (D6). If the scientists have files with such strings, that is a one-row extension. |
| A2 | A loaded file omitting the resolution keys shows the library default, not the new starting value. | Yes — showing `gaussian` there would display a value the reduction of that same file does not use. This is the visible edge of the parked `library-defaults-detres`. |
| A3 | Entry texts are exactly the scientists': `False`, `True`, `trust sample angle`. | Yes. |
| A4 | The pre-existing `"none"` hazard for `DetResFn` (`reduction_domains.DET_RES_NOTES`) is untouched. | Yes. |
| A5 | **(added 2026-10-03, before dispatch)** The human ruled `useCalcTheta` "is not a boolean it is an enumeration (empty, detector_angle, sample_angle), keep it separate" (V1-19), and the Advisor measured a template → reducer → template loop that loses the setting (`plans/usecalctheta-enumeration-investigation.md`; reduction-path slug `usecalctheta-carriers`, held). This plan's three stored values are that enumeration (the editor's "off" is the config default `False`, which the reducer reads as empty); it touches no template code. Real JSON files hold `true` 16 / `false` 88, never a string — so after this slug the editor is the first writer of the string spellings into JSON; the JSON path (`json_to_config` → `NR_Reduction`) accepts them (`:92-97`). State this in the PR body. | Re-read the investigation at the re-seal; if the carriers slug lands first, align the stored "off" with whatever it chooses. |

## Revision history

v1 — authored 2026-10-02 against `7b6d6b9` (staged); re-sealed 2026-10-04 at `b86237b` (A-30/f48d045: citations moved, F6 re-run
identical, the operation × state table and first-use gestures added); **dispatched 2026-10-04 stacked on `feature/launcher-test-teardown`
@ `ed663f7`** when draft PR #37 opened (`[human, 2026-10-04, posture]`; A-32) — the cited files are blob-identical to `b86237b`, so no
citation moved.
