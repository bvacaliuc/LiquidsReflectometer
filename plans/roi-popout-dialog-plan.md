# Plan: `roi-popout-dialog` — "Select ROI" beside Add/Remove: #197's dialog lifted onto `SettingsDocument`, with the web report's two detector images

**Campaign:** `exp-review-fixes` · **Leaf:** `roi-popout-dialog` (refs `triage/roi-popout-dialog`,
`feature/roi-popout-dialog`, `qa/roi-popout-dialog`) · **Status:** **ESCALATED 2026-10-06** — v3 @ `21a7367` REJECTED at the retry cap (`review/roi-popout-dialog` @ `ad3558c`, I-50: five declared clauses unpinned — RBnum on Cancel, LogNorm, colorbars, "all angles", a truncating write vs the 0-byte fixture; production right); the record and the human's options are `plans/roi-popout-dialog-escalate.md`; the annotated tag `review/roi-popout-dialog-escalate` is on the fork — was: READY — **v3 (attempt 3 of N = 3 — the last)** — v2 REJECTED 2026-10-05 at `e017a97` (`review/roi-popout-dialog` @ `088686c`: "a document save from the slot and a forced aspect go unasserted" — two test-only pins, both gaps v1 also had; everything of v2 closed, gate green, §8.7 PASS again) — **v3 does exactly three things**: E4′/E9 made able to see a document save (B-1, with M30 and the docstring's domain), V2 asserts `get_aspect() == "auto"` (B-2, with M31), E9's `give_up` timer stopped (A-1); the Developer continues on `feature/roi-popout-dialog` @ `e017a97` (predecessors unmoved: `f424aec`, `8ca43ce`); see "v3" below and the Revision history — v1 REJECTED 2026-10-05 at `791bdbe`
(the Integrator's `review/roi-popout-dialog` @ `b22c8df`: "six declared behaviours untested, one false docstring claim"; production right on real
data, the gate green; see Revision history) — **v2 is a tests-and-wording revision plus two cheap advisories (A1, D1)**: the Developer continues
on `feature/roi-popout-dialog` @ `791bdbe` (predecessors unmoved: `feature/roi-popout-data` @ `f424aec`, K2's PASS tip `8ca43ce` merged forward
at `a42ecdc`; `exp-review` @ `b6b9381`), applies §6′/§7′ below, re-runs the whole battery, and pushes `qa/` — v1 was dispatched 2026-10-05 under the posture's **stacking by file overlap** rule
(`ec10742`, rule (4)): the plan's files overlap **two** open lines — `src/lr_reduction/roi_estimate.py` is *consumed* from
`feature/roi-popout-data` (#44, PASS; the data layer exists nowhere else), and `launcher/apps/settings_editor.py` (one button, one slot) is
changed by the editor stack (#43 `feature/editor-notes-and-report-spelling`, and K2 `feature/editor-ipts-inference` in flight) — the
**larger overlap is R1** (a whole module this slug cannot build without), so the slug **stacks on #44** and **merges the editor tip
forward** (rule (4)'s "merge the others' tips forward before the gate" — here **at cut time**, so the dialog is developed against the
current editor, and again before `qa/` if the editor tip moved) ·
**Base:** `agentic/feature/roi-popout-data` @ `f424aec` (R1's PASS tip = `exp-review` @ `5a8742d` + PR #31 + the data layer) **plus, at cut, a
regular merge of `agentic/feature/editor-notes-and-report-spelling` @ `779f787`** (#43's PASS tip, which contains #40's `editor-sections`
and #39/#38 — the editor this slug's button joins); K2's tip is merged forward too once it has PASSed (the Developer checks at `qa/` time) —
**overlap at dispatch** (`git diff --name-only agentic/exp-review...agentic/feature/<x>`, tests excluded, `exp-review` @ `b6b9381`): #44
{`roi_estimate.py`} — the dependency; #43 {`settings_document.py`, `settings_editor.py`, `field_spec.py`} ∩ `settings_editor.py`; K2
{`settings_document.py`, `settings_editor.py`} ∩ `settings_editor.py`; `feature/test-suite-warnings`, `feature/launcher-env-outside-xdg-cache`,
`feature/rereduction-headers-land`, `feature/header-scale-factors-per-position`: none · **PR target:** `feature/roi-popout-data` on the fork,
**draft** (retargeted to `exp-review` by the human's merge of #44; the Integrator names both stacks in the body) · **Stack:** #44 → **this
slug**, with the editor stack merged in; the Developer cuts `feature/roi-popout-dialog` `--no-track` from `agentic/feature/roi-popout-data`,
merges `agentic/feature/editor-notes-and-report-spelling` forward at once (regular merge; a conflict in `settings_editor.py` is resolved and
recorded), and merges both predecessors forward before every `qa/` push; the Integrator opens the draft PR `--base feature/roi-popout-data` ·
**Depends on:** `roi-popout-data` **PASSed** (its §3 contract B1–B9 — every name re-verified at `f424aec`: `RunEvents`, `load_event_pixels`,
`xy_image`, `tof_edges`, `y_tof_image`, `profile_y/x/tof`, `background_bands`, `default_bkg_roi(peak_range, n_y, gap=3, width=5)`,
`estimate_peak_range`, `chopper_lambda_range`, `lambda_to_tof`, `detector_shape`, `CannotEstimateError(ValueError)` — `roi_estimate.py:34-537`)
· **Review domains:** ui-aspects, design, test (block) ·
**Kind:** launcher (operator-facing) — **not** reduction-path · **Sources:** scientists' item 9
(`requests/updates_for_setting_loader.md`), Q6 (`plans/settings-loader-clarifications-decision-request.md`
§Resolution), charter §3 row, the reference's #197 review (`plan/contrib/review-exp-json-settings-builder/`)
and T1 findings R5/R7/R8/R14 (`plan/roi-selector/plan.md`).

Canonical copy: ledger `plans/roi-popout-dialog-plan.md`; the copy on `triage/roi-popout-dialog-v3` is
byte-identical at dispatch.

## v3 — the last attempt: two pins and one timer (read this first; everything else stands)

The Integrator reproduced two mutations in a `git archive` copy of `e017a97`, each **surviving with 628 passed** (the slug's
two test files; 79 + 549). Both are gaps v1 also had and v2 did not close; neither was raised at v1 (the Integrator's
miss, stated as such). **Nothing else is asked**: the gate is green (launcher 757, reduction 874), every v1 survivor and
M27–M29 red with v2's recorded counts, the §8.7 acceptance on IPTS-36119 passes again, D1 is closed, the Y-TOF image
opens on its data.

| Item | What survives today | Why the test is blind | v3 action |
|---|---|---|---|
| **B-1 (a, d)** `select_roi` saving the settings document — after `self.refresh_report()` add `self.document.save(Path.cwd() / "roi-settings.json")` → 628 passed and a 1 484-byte `roi-settings.json` in the cwd (#197's F2, **the bug E4 exists for**) | E4′'s stub `no_save` **raises** inside the `@guarded` slot; `report_problem` swallows it, no file is written, the test passes (the panel holds `'AssertionError: SettingsDocument.save called'`); the tests that leave `save` unpatched (E2, E9, …) do not watch the disk. Rule (d): v2's docstring sentence "E4 watches every file and key" (`settings_editor.py:1143-1145`) is falsified by the same command | **E4″**: `no_save` *records* (`calls.append(...)`) and E4″ asserts `calls == []` **and** the panel reports no problem after the slot. **E9′**: snapshot the files (name, size, mtime) under `tmp_path` **and** the working directory before and after each leg; assert nothing new or changed apart from the QSettings store E4″ allows. **M30** "the slot saves the document" reds alone. Docstring: name the domain E4″ enumerates — "E4 watches `SettingsDocument.save`, the working directory, the run's folder and the QSettings store" — or keep "every file" only if E9′'s snapshot makes it true |
| **B-2 (a)** `roi_dialog.py:404` `"aspect": "auto"` → `"aspect": "equal"` → 628 passed; on run 231801 the Y-TOF axes box goes 273 × 221 px → **273 × 1 px**, the XY box 273 × 221 → 186 × 221 | V2 asserts origin and extent, not aspect — B3's "aspect left to the data" and L1's "do **not** force `set_aspect('equal')`" are §8.6's faithful-axes pin handed to V2, and V2 did not carry it | **V2′**: `get_aspect() == "auto"` on `xy_axis` and `ytof_axis` after open and after a draw. **M31** "`aspect` equal" reds alone |
| **A-1 (test, cheap — in E9, which B-1 touches)** E9's `QtCore.QTimer.singleShot(8000, give_up)` (`test_settings_editor.py:3289`) keeps running after the test; a later test that shows a dialog and waits ≥ 8 s sees it rejected (`AssertionError: (False, 0)`); the design reviewer once saw "1 failed, 627 passed" on an unmutated copy, not reproduced in four reruns | a fire-and-forget timer outlives its test | a `QTimer` object, stopped in a `finally` (or parented to the tab so it dies with it) |

**Plan corrections folded in (correct-and-flag, the Developer's D-62 notes and the Integrator's D-b):** §6′ E9's "reds
under" loses M4 — Cancel's `reject()` restores the opening values, so E9 cannot red it; **E3 still does** (M4 → E3 is the
§7 row). V15′ is two legs, not one sequence (a dialog opened with `RB_Ymax` set cannot then "set the high spin"). M25b is
M11a's edit (the battery's existing row), not a new row. D-a: `_guarded`'s docstring cites M5; the dialog's rows are
G-guard-values/-estimate/-log — fix the citation in the same commit as B-2 (one line, same file).

**Carried to the PR body (not v3 work):** U-a (the colour scale fixed at open — v1's A4 made visible), U-b (the legend
built once — v1's A5), U-c (the toolbar's "Customize" bypasses `_plain_log_ticks`), T-a (V18's Y bounds vs ±`VIEW_MARGIN`),
with v1's A2–A8, D2–D8, T2–T3.

**v3 recipe.** RED first: E4″ and V2′ fail on `e017a97` under M30 and M31 respectively (apply the mutation, see the new
assertion red, restore); E9′'s snapshot reds under M30 through the real modal. GREEN with the production of `e017a97`
plus the docstring and the `_guarded` citation. The **whole** battery again (§7 + §7′ + M30, M31 — the ledger script
extended), every row `<mutation> → <test> -> N failed`, N ≥ 1, in the commit body; M30 and M31 named with the test that
caught them. Merge the predecessors forward if they moved; gate; `qa/`. **A third rejection escalates** (`plans/
roi-popout-dialog-escalate.md`, the annotated `review/roi-popout-dialog-escalate` tag): the Developer should treat the
Integrator's two commands above as the acceptance test of v3 and run them before pushing `qa/`.

## v2 — what changes and why (§1–§5, §8 and §10 stand except where marked **v2**)

The Integrator reproduced seven items in a `git archive` copy of `791bdbe`, each **surviving with 618 passed** (the
slug's two test files, unmutated count 618): a mutation that stays green means the declared behaviour has no pin
(L4). Six are tests (rules a/b), one is a false docstring claim (rule d). Production is right — the deployment-shaped
acceptance on IPTS-36119 matched the stored web report cell for cell. v2 therefore changes **tests, two docstrings,
and two cheap advisories**; no other production behaviour moves.

| Item | Where the cell lives | v2 action |
|---|---|---|
| B-1 (d) `select_roi`'s docstring: "no file is opened for writing (E4)" is false — the slot's file dialog remembers its folder in the launcher's QSettings (`roi_nexus_dir`, `$XDG_CONFIG_HOME/ORNL/lr_reduction_new_launcher.conf` changed) | §3 "How #197's bugs are closed" F2 — **the plan's own sentence, corrected below (P1)**; `settings_editor.py:1143` | docstring says what is true; **E4′** asserts it over *every file the slot can write* |
| B-2 (b) `axis.set_minor_formatter(LogFormatter(labelOnlyBase=True))` (`roi_dialog.py:87`) deleted → 618 passed; on run 231801 zoomed to 20–80, 48 minor labels are mathtext | V11 reads only the major labels | **V11′** two draws, minor + offset labels, colorbars |
| B-3 (a) `RB_Ymin`/`RB_Ymax` `None` → "no peak overlay" — `_move("peak", peak)` → `_move("peak", self._spin_values(self.peak_spins))` (`:538`) survives | §3 types table, row 1, `None` cell | **V15′** `None` leg: every `overlays["peak"]` artist hidden until both edges are set |
| B-4 (a) `useBS` `[]`/`None` → "treated as on" — `values.get("useBS") != 0` → `bool(values.get("useBS"))` (`:216`) survives | §3 types table, `useBS` row | **V16** `None` and `[]` legs beside the 0/False legs |
| B-5 (a) B6's X and TOF drags — `_x_range_selected`/`_tof_range_selected` (`:317-321`) made `pass`, each alone and swapped, survive | V4 drags only on `y_axis` | **V4′** X and TOF legs; battery rows M20–M22 |
| B-6 (a) Cancel/OK never pressed — `rejected.connect(self.accept)` (`:286`) and OK unconnected (`:285`) survive | V6/V7 call `reject()`/`accept()`; every E-test replaces `exec_` (§6: a direct call is not a gesture) | **V6′/V7′** press the `QDialogButtonBox` buttons; **E9** runs the real modal `exec_()` from a `QTimer` |
| B-7 (a) the log toggle — `set_yscale("log")` unconditionally (`:562`) survives | only the `_set_log_scale` injection leg exists | **V17** clicks `log_check` and reads `get_yscale()` on all three profiles |
| M13's count (to show) — the test reviewer's three forms of M13 give **4 failed**, the commit records 5 | §7 M13 | the v2 commit body **quotes the battery row's code and its observed count**; 4 or 5, the record then stands on the quoted code |
| A1 (ui, recommended) the Y-TOF image fills part of its panel — `axvspan(0, 1)` pulls x = 0 into the limits and `_reset_limits` never sets `ytof_axis` (−3 000 µs vs events from 8 000 µs; 32 % of the panel on run 220050) | B3 | **B3′**: the Y-TOF x limits are the TOF edges; **V18** pins them with `get_xlim()`, together with T1's TOF and X profile limits (`:573-574`) |
| D1 (design, a factual claim) the module docstring and `b041aa2`'s body name welbournR (`3f74d41`) as an author of the lifted lines; `git log -L 396,690:…` lists only `65c83d9`, `ab22307`, `1e692c7`, `8191e49`, `f5513c7`; `git blame -w -M -C` gives `3f74d41` 0 lifted lines | F2 — **the plan's own list, corrected below (P2)** | docstring corrected (the lift commit's body cannot be rewritten — the correction is a sentence in the v2 docstring: "b041aa2's body names 3f74d41 in error") |
| P3 the V9 sparse-run threshold is the estimator's (`roi-popout-data`'s `e0bba12` advisory) | V9 | V9 stands as the *dialog's* handling of a refusal; the threshold is not this slug's to tune |

**Carried as PR-body advisories, not v2 work** (the Integrator's A2–A8, D2–D8, T2–T3): record them in the PR body
under "Advisories from the v1 gate"; D3's third copy of `f"REF_L_{run}.nxs.h5"` (`settings_document.py:159`) and D2's
Qt-free validator are `roi-popout-data` follow-ups the Analyst files. **Where a D6/D7 item is a one-line change in a
file v2 touches anyway (naming the ±30 margin and the TOF step 100; marking the two #197 comments at `:140`/`:170`
inferred or citing the test), do it in the same commit as the neighbouring fix** — not as a sweep.

**v2 recipe.** (1) RED first: every test in §6′ fails on `791bdbe` **for the reason its row names** (the mutation of
§7′ applied to the unmutated tree is the proof — run the row's mutation, see the new test red, restore). (2) GREEN:
E4′, V11′, V15′, V16, V4′, V6′/V7′, E9, V17, V18 pass with the production of `791bdbe` plus B3′, the two docstrings
and the cheap advisories. (3) The **whole** battery (§7 + §7′, the ledger script extended with the new rows), each row
`<mutation> → <test> -> N failed`, N ≥ 1, in the commit body — including the seven rows the Integrator ran, with their
new counts. (4) Merge the predecessors forward if they moved (`f424aec`, `8ca43ce`; `exp-review` is not a predecessor),
gate, push `qa/`.

## Declared scope

**Files in:** `launcher/apps/roi_dialog.py` (new), `launcher/apps/settings_editor.py` (one button, one
slot, the row→NeXus lookup), `launcher/tests/test_roi_dialog.py` (new), `launcher/tests/test_settings_editor.py`.

**Behaviours in** (§3 B1–B12): a "Select ROI" button enabled when an Angles row is selected; a modal
pop-out for that one row showing five plots (XY image, Y-vs-TOF image, counts per Y, per TOF, per X) with
the row's current ROIs overlaid; drag on the profiles and entry boxes to adjust; OK writes **only what the
user changed** back through `SettingsDocument`; Cancel writes nothing.

**Explicitly OUT** (a finding here is a PR-body advisory, not a rejection):
- everything under `src/` — no event maths, geometry, band or background arithmetic in the launcher; if a
  number is missing from `lr_reduction.roi_estimate`, that is a `roi-popout-data` follow-up, not a local helper;
- the rest of #197: `JSONSettingsBuilderTab`, `RunRow`, `GLOBAL_FIELDS`, its loader/saver, sequence
  sorting, direct-beam scanning (D-2: "do not carry the tool");
- editing `tof_min`/`tof_max`/`LambdaMin`/`LambdaMax` from the dialog (shown, not written — A2);
  dragging on the 2D images (A1); stepping between angles inside the dialog (A3);
- `launcher/apps/roi_selector.py` (the disabled old tab), `overplot.py`, the global `rcParams`;
- embedding the web report's HTML (`todo-rfc-embed-web-report-html.md`, next campaign).

## 1. Request and requirements trace

Item 9, sentence by sentence, against this design (Q6 `[human]`: "matplotlib, same content. Lets start with
the lifted method (but with the bugs fixed) from upstream#197 … Make sure it is tensioned against any
requests in the updates_for_setting_loader.md document").

| # | The scientists' sentence | Design answer | Tension / gap |
|---|---|---|---|
| S1 | "A larger change … considered separately after the smaller parts have been implemented …" | Last two slugs of the lane; data before dialog. | none |
| S2 | "This should not clutter the existing display but is an important diagnostic to check the settings applied." | One button on the tab; all plots live in the pop-out. The overlays are drawn from the reducer's own interpretation of the settings (B4). | none |
| S3 | "… a button of 'Select ROI' (e.g. next to the Add/Remove angle buttons) when a line is selected in the 'Angles' table … a pop-out window with plots showing the current ROIs and an ability to adjust these and save them out back into the table." | B1, B3–B9. "Current ROIs" = the row's `RB_Ymin`/`RB_Ymax`, `BkgROI`, the shared `data_x_range`, and the TOF window the reduction keeps. | The row must be tied to a NeXus file; authored files usually carry no `RBnum` (runtime-owned), so the file is asked for (B2). |
| S4 | "… checking the numbers for each angle in turn, separate from the wider list of all settings in the main tab." | One row per pop-out; the entry boxes show only that row's numbers. | "In turn" is met by reopening per row; stepping inside the dialog is A3. |
| S5 | "… json_settings_builder.py which shows plots, the ability to drag for new ROIs on the specular and the background, as well as entry boxes underneath …" | Lifted: three profiles, `SpanSelector` drags with the peak / low / high background selector, spin boxes, Estimate, log toggle (F2). | #197's fourth entry row, "TOF range, profiles only", is kept as a **view filter** and labelled so (B8). |
| S6 | "These can then be saved back into the table." | B9: through `set_angle_field(row, …)`; the table and report refresh. Never a file write. | none |
| S7 | "The plots here are only processed integrations, but the plots should be shown as 2D detector colour-plots." | Two images added above the profiles (B3). | #197 has none: this is new code, not lifted. Drags stay on the profiles (A1). |
| S8 | "This should be a similar set of plots to that displayed on monitor.sns.gov." | The web report's five plots, same quantities (F3). | The report's Y-TOF sums every X pixel; here it is restricted to `data_x_range`, which is what the reduction integrates (`nr_reduction_calc.py:330`) — stated in the plot title. |
| S9 | "These plots come from web_report.py in lr_reduction." | `web_report.py` is the content reference; the arrays come from `roi_estimate` (Qt-free, Mantid-free), proven equal to the report's XY (data plan F4). | The report labels its second image "X-TOF" in a log line; it is Y against TOF (data plan F3). |

## 2. Verified facts (base `7b6d6b9`; #197 as hardened at `agentic/feature/harden-review-branch` @ `65c83d9`; 2026-10-02 — **re-sealed 2026-10-05**: the editor-side citations below are **re-measured at #43's tip `779f787`**, the tree the Developer works in after the cut-time merge; the data-side names at `f424aec`; `web_report.py`, `nr_reduction_calc.py`, `nr_reduction_config.py` unchanged since `7b6d6b9` on `exp-review` and on #44)

| # | Fact | Command → observation |
|---|---|---|
| F1 | The buttons row and the selection idiom this slug extends. | `launcher/apps/settings_editor.py` **at `779f787`**: `_build_angle_panel` `:598`, the buttons row `:632-639` (`add_angle_button` `:632-634`, `remove_angle_button` `:636-638`, `addStretch` `:639`); `remove_selected_angle` `:1042` captures the row at the click (the module docstring `:15` and `:1009`: "nothing here consults `currentRow()` to decide *what* to…" — the selection is read once, at the gesture); `guarded` `:485`; `report_problem` `:1069`. (At `7b6d6b9`: `:133-142`, `:324-336`, `:38-55`, `:352-359`.) |
| F2 | The seed. | `git show agentic/feature/harden-review-branch:launcher/apps/json_settings_builder.py` → `_move_span` `:396-406`, `ROISelectionDialog` `:409-690` (`values()` at `:682`), `edit_roi` `:1303-1348`. Upstream's copy (`upstream/exp-json-settings-builder` @ `3ce5e20`, `:337`/`:350`) differs in the dialog only by the `parse_math=False` title (`:452-458` in the hardened copy). **v2 CORRECTION (P2 / D1):** authors of the lifted lines are **Mathieu Doucet (`f5513c7`, `8191e49`, `1e692c7`, `ab22307`) and the fork's hardening commit `65c83d9`** (8 lines, the `parse_math=False` title — credited as the source SHA). v1 also named welbournR (`3f74d41`); the Integrator measured `git log -L 396,690:launcher/apps/json_settings_builder.py agentic/feature/harden-review-branch` → only `65c83d9`, `ab22307`, `1e692c7`, `8191e49`, `f5513c7`, and `git blame -w -M -C` → 0 lifted lines from `3f74d41` (whose hunks are the constants, `read_nexus_metadata` and the tab). The v1 line was read from PR #197's author list, not measured on the lifted range — **the plan's error, carried into the module docstring and `b041aa2`'s body.** |
| F3 | What the web report draws. | `src/lr_reduction/web_report.py:505-509` (XY, Y-TOF, counts per Y, counts per X, TOF distribution); overlays: peak, background, low-res range, TOF range (`:582-591`, `:617-628`). |
| F4 | Where the dialog's bugs actually live. | Reference review F1 (8 of 13 per-angle arrays grow), F2 (truncating write to the live autoreduce file), F4 (`DetResFn` offers `'none'`) are in `JSONSettingsBuilderTab` / `GLOBAL_FIELDS` (`:187-188`, `:693-…`), not in `ROISelectionDialog`. F3 (geometry and band literals: `N_Y = 304`, `N_X = 256` `:131-132`, `MODERATOR_DETECTOR_DISTANCE` `:141`, `252.78`) and the mathtext exposure **are** in the dialog's path. |
| F5 | #197's default background can write a file the reducer dies on. | `default_bkg_roi` (`:386-393`) clamps with `max(0, …)`; one zero in a `BkgROI` entry makes `_background_roi_sorter` return `None` (data plan F6) → `TypeError` at `nr_reduction_calc.py:511`. |
| F6 | A per-angle write through the model keeps every column aligned. | `src/lr_reduction/settings_document.py` **at `779f787`**: `set_angle_field` `:362` (was `:168-205`), `angle_row` `:512`; pads a `None` or short column to `n_angles` before writing. |
| F7 | Log tick labels are mathtext that no `parse_math` setting reaches; a plain formatter removes them. | Agg probe on matplotlib 3.9.4: default log ticks → `'$\\mathdefault{10^{-2}}$'`; with `matplotlib.ticker.LogFormatter()` → `'1e−02'`, and on a `LogNorm` colorbar → no `$` in any label. The reported `RecursionError` came through a tick label, not a title, is font-set dependent, and did not reproduce in the Developer's environment (commit body of `65c83d9`). |
| F8 | No plot text is exempted from mathtext at the base tip. | `grep -rn parse_math launcher src --include=*.py` @ `7b6d6b9` → nothing. |
| F9 | The row's NeXus file, as the reducer names it. | `nr_reduction_calc.py:325` `self.config.NEXUSpathRB / f"REF_L_{rb_num}.nxs.h5"`; `nr_reduction_config.py:126-129` (override, else `<IPTS>/nexus`; unchanged). |
| F10 | Environment and harness. | `pixi run python -c "import matplotlib, qtpy; …"` → matplotlib 3.9.4, PyQt5 5.15.15; `launcher/tests/conftest.py` **at `779f787`**: `isolated_qapp` `:71`, `no_qmessagebox` `:110` patches `QDialog.exec_` to return `Accepted`; `no_qfiledialog` `:137-138` (autouse) returns `("", "")` (K2 v1 added a scoped event filter for its sidebar on the static dialogs so this net still covers them — the dialog slug's own `QFileDialog` use in B2 goes through the same net). No launcher test reads the data submodule today. |

## 3. Design — behaviours, not code

The dialog is a **view over arrays and one row's values**: it reads no file and writes no document. The
tab's slot resolves the file, loads events once (`roi_estimate.load_event_pixels`), opens the dialog, and
applies what the dialog reports. Names fixed for the tests: `select_roi_button`, `ROISelectionDialog`.

| # | Behaviour |
|---|---|
| B1 | "Select ROI" sits after "Remove angle" and is enabled exactly when the Angles table has a current row. The row is captured **at the click** and passed explicitly; nothing later consults the selection. |
| B2 | The row's file is `config.NEXUSpathRB / f"REF_L_{RBnum[row]}.nxs.h5"` when `RBnum[row]` is set and the file exists; otherwise a file dialog asks for it (start directory: the resolved NeXus directory, else the last one used). A cancelled dialog does nothing. A read failure is reported in the panel (`@guarded`), never fatal, never a modal box. |
| B3 | Five plots: XY image and Y-vs-TOF image (colour, log norm, colorbar), then counts per Y, per TOF, per X. Image arrays are `roi_estimate.xy_image` / `y_tof_image` unmodified; `origin="lower"`, extent on pixel centres, aspect left to the data. **v2 (B3′, from advisory A1):** each axis opens on its data — the Y-TOF image's x limits are the TOF edges (`tof_edges[0]`, `tof_edges[-1]`), the TOF profile's likewise, the X profile's `0 … n_x − 1`; an overlay artist (`axvspan`, `axhspan`) never widens an axis's limits (v1's `axvspan(0, 1)` pulled x = 0 into the Y-TOF axis, so run 231801 opened near −3 000 µs with events from 8 000 µs). Pinned by V18. |
| B4 | Overlays show what the reduction will use: the peak rows; the **two background bands from `roi_estimate.background_bands`** (so `[a, b, 0, 0]` draws `(a, y_min)` and `(y_max, b)`, not one band across the peak); `data_x_range`; the reduction's TOF window when the row has one. Every overlay appears on every plot that has its axis. |
| B5 | A background entry the reducer cannot use (data plan F6), or none at all, is shown as "not set" with the reason in the dialog's status line — no bands drawn, no values invented. With `useBS` off for the row the bands are drawn and labelled "not subtracted". |
| B6 | Lifted interaction: drag on the Y profile sets the peak, low or high background (radio selector), on the X profile the X range, on the TOF profile the view filter; entry boxes mirror and accept typed values; "Estimate the peak"; log toggle. |
| B7 | Estimate uses `roi_estimate.estimate_peak_range` on the profile shown and `roi_estimate.default_bkg_roi`; a `CannotEstimateError` is shown as its message and changes no value. |
| B8 | The TOF view filter selects the events the profiles and the XY image are made of. It starts at the chopper band when the run has a chopper log (`chopper_lambda_range` + `lambda_to_tof`), else the full span; the TOF profile and the Y-TOF image always cover the **full** span (R14). It is never written anywhere. |
| B9 | OK reports only the fields whose values differ from those the dialog opened with, and the tab writes exactly those: `RB_Ymin`, `RB_Ymax`, `BkgROI` via `set_angle_field(row, …)`; `data_x_range` via `set(…)` (labelled "all angles"). Then `refresh_angles`, `refresh_scalars`, `refresh_report`. An untouched `[a, b, 0, 0]` or unset background stays byte-for-byte. |
| B10 | OK is unavailable while the peak is empty or inverted, or the background is partly set; a background written by the dialog is four ascending non-zero integers. |
| B11 | A nudge moves artists; it does not rebuild the figure (R8). Images are recomputed only when their own inputs change (XY: view filter; Y-TOF: X range). |
| B12 | No text built from file content is parsed as maths (`parse_math=False`), and the dialog's log axes and colorbars use a plain-text formatter (F7). The dialog is released with `deleteLater()`, never `destroy()`. |

**How #197's bugs are closed.** F1: no private row model — one writer, `set_angle_field` (F6); pinned by E2.
F2 (**v2 CORRECTION, P1 / B-1** — v1 read "the dialog and the slot open no file for writing; pinned by E4", which
contradicted B2's "the last one used" and was copied into `select_roi`'s docstring): **the dialog writes nothing; the
slot writes no settings file and no data file; the one thing it records is the folder a chosen run came from, in the
launcher's QSettings (`roi_nexus_dir`), so the next file dialog opens there (B2)** — pinned by E4′, whose domain is
*every file the slot can write*: after a Select ROI the only change on disk is that one QSettings key; `SettingsDocument.save`
is not called; nothing new appears in the working directory or in the chosen run's folder. F4: `GLOBAL_FIELDS` is not lifted;
`test_an_enumerated_editor_offers_the_declared_spellings` stays the pin. F3: no geometry, distance or band
literal in `launcher/`; pinned by V12. F5 (this plan): the default background comes from the data layer,
which refuses instead of clamping to 0. Mathtext: B12, pinned by V11.

**Types and states each path acts on.** **v2:** every cell names the test that fails when it breaks (the v1 table
declared the `None` peak cell and the `useBS` `None`/`[]` cell with no pin — B-3, B-4; a cell without a test is a
claim, not a behaviour).

| Value at open | present | empty / short | `None` |
|---|---|---|---|
| `RB_Ymin[row]`, `RB_Ymax[row]` (per-angle int) | spins and overlays (V5) | column shorter than the row → treated as `None` (`angle_row`; E2's short leg) | spins at "not set"; **no peak overlay — every `overlays["peak"]` artist hidden until both edges are set (V15′ `None` leg; M18)**; OK unavailable until both are set (V15) |
| `BkgROI[row]` (per-angle list of 4 int) | per data plan §3: 0 zeros → two bands; 2 zeros → peak-adjacent bands (V3) | `[]`, wrong length, 1/3/4 zeros → B5 (V14) | B5 (V14) |
| `data_x_range` (scalar list of 2 int — **not** per angle) | X overlay and spins (V5; drag V4′ X leg) | wrong length → reported in the status line; X spins start at the full detector; written only if edited (the Developer's `test_a_data_x_range_that_is_not_two_pixels_…`) | same |
| `tof_min[row]`, `tof_max[row]` (per-angle float, µs) | TOF-window overlay (the Developer's `test_the_reductions_tof_window_is_drawn_…`) | the column may be `[]` (reducer default) → no overlay | no overlay |
| `useBS[row]` (per-angle bool / 1 / 0) | label only (the Developer's `…does_not_subtract_is_drawn_and_labelled` 0/False legs) | `[]` → reducer default is on — **"not subtracted" absent (V16 `[]` leg; M19)** | **treated as on — "not subtracted" absent (V16 `None` leg; M19)** |
| `RBnum[row]` (runtime-owned int) | file lookup (E6) | absent → ask (E6) | ask (E6) |
| events | images and profiles (V1, V2) | zero events → empty plots, Estimate refuses (the Developer's `test_a_run_without_events_…`) | n/a |

## 4. Files to change

| File | Change |
|---|---|
| `launcher/apps/roi_dialog.py` | New. `_move_span` and `ROISelectionDialog` lifted from F2's lines, re-seated on `RunEvents` and the data layer; two image axes added. Module docstring names PR #197, the source SHA and its authors (A5). Lift commit first (verbatim lines, not yet wired), then the changes, so the diff against the seed is reviewable. **v2:** the docstring's author list per F2's correction (D1; one sentence says `b041aa2`'s body names `3f74d41` in error); B3′ (the Y-TOF x limits in `_reset_limits`; no overlay widens an axis); the ±30 margin (`:572`) and the TOF step 100 (`:268`) named; the two #197 comments (`:140`, `:170`) cite a test or say inferred (D6/D7, §8.5). |
| `launcher/apps/settings_editor.py` | `select_roi_button`; a `@guarded` slot; the row→file lookup (B2). **v2:** `select_roi`'s docstring per F2's correction (B-1): "no settings or data file is written; the folder a chosen run came from is remembered in the launcher's QSettings (`roi_nexus_dir`, B2) — E4". One `f"REF_L_{run}.nxs.h5"` in the slot (D3's two local copies become one name). |
| `launcher/tests/test_roi_dialog.py` | New: V1–V15. Events are built in memory through the real `RunEvents`, never a mock. **v2:** V4′, V6′, V7′, V11′, V15′, V16, V17, V18 (§6′). |
| `launcher/tests/test_settings_editor.py` | E1–E8. **v2:** E4′, E9 (§6′). |

## 5. Failure-mode matrix

| Case | Situation | Must happen | Must not happen |
|---|---|---|---|
| common | row with peak and `[a, b, 0, 0]`, run file in the IPTS tree | five plots; bands as the reducer uses them; drag the peak; OK writes two integers | `BkgROI` rewritten though untouched; the background drawn across the peak (R5 panel a) |
| common | Cancel after edits | document identical (`to_dict()` equal) | any write |
| common | authored file, no `RBnum` | file dialog; chosen run shown in the title | a guessed run; `RBnum` written |
| edge | sparse run, Estimate pressed | refusal text in the status line | a bracket around noise; a modal box |
| edge | peak near a detector edge, Estimate pressed | peak set; background reported as "no room", left unset | a `0` bound saved (F5) |
| edge | `data_x_range` changed in the dialog | scalar updated, scalar editor shows it, "Changed from the seed" lists it | a per-row copy of a global value |
| edge | long run | sub-sampled (`max_events`); the title says "every Nth event" | a frozen launcher; counts presented as totals |
| edge | title with `$`, `\`, `_`; log axes on an analysis node | draws | mathtext parser reached from file text or tick labels |
| edge | view filter narrowed, OK | nothing about TOF written | `tof_min`/`tof_max` changed by a viewing aid |
| pathological | selection changes between click and OK (not reachable while modal; pinned anyway) | the captured row is written | the selected row is written (active-row trap) |
| pathological | row index no longer valid at OK | reported in the panel | `IndexError` out of a slot (`qFatal`) |
| pathological | file missing, unreadable, or without `bank1_events` | panel message; no dialog | process abort; half-built dialog |
| pathological | `BkgROI[row]` is a string or 3 numbers | B5 | exception in the dialog constructor |
| pathological | matplotlib Qt backend missing | button disabled with a tooltip saying why | `AttributeError` at click |

## 6. Red-Green TDD seed

`pytestmark = pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")`; run under
`pixi run python -m pytest launcher/tests --timeout=120 --timeout-method=thread` while developing. Gestures
go through `QTest` (clicks, keys, and press–move–release on the canvas at coordinates taken from
`ax.transData.transform`, measured, not reasoned — L2); a signal `.emit()` or a direct call to a
`SpanSelector` callback is not a gesture. If an offscreen canvas drag cannot reach the selector, record
the measurement in the commit body and say which test stands in for it.

| # | Test | RED before | GREEN when |
|---|---|---|---|
| V1 | `test_the_dialog_draws_two_images_and_three_profiles` | no module | two axes with one `AxesImage`, three with one line |
| V2 | `test_the_images_are_the_data_layers_arrays` | — | `ax.images[0].get_array()` equals `roi_estimate.xy_image(...)` / `y_tof_image(...)`; `origin == "lower"`; extent on pixel centres; **v3 (V2′, B-2): `get_aspect() == "auto"` on `xy_axis` and `ytof_axis`, after open and after a draw** — B3's "aspect left to the data" (L1) was the pin §8.6 hands to V2 and V2 did not carry it |
| V3 | `test_the_background_overlay_is_what_the_reducer_averages` (`[133, 149, 0, 0]`, peak 136–146) | — | band edges equal `background_bands(...)` on every plot with a Y axis |
| V4 | `test_dragging_on_the_y_profile_sets_the_chosen_range` (peak, low, high) | — | spins and overlays follow a `QTest` drag |
| V5 | `test_a_typed_value_moves_its_overlay_on_every_plot` (parametrised per overlay × axes) | — | each artist's data edges equal the spins |
| V6 | `test_cancel_reports_nothing` | — | no changes after edits + reject |
| V7 | `test_ok_reports_only_what_changed` (untouched `[a, b, 0, 0]`, unset, and edited legs) | — | per B9 |
| V8 | `test_the_view_filter_is_never_reported` | — | profiles change; the report has no TOF key |
| V9 | `test_an_estimate_refusal_is_a_message_not_a_guess` (sparse events) | — | status text carries the refusal; spins unchanged |
| V10 | `test_estimate_sets_a_background_the_reducer_accepts` | — | reported `BkgROI` passes `background_bands` |
| V11 | `test_file_text_and_log_ticks_never_reach_the_math_parser` (title `"$\\foo$ run"`) | — | title `get_parse_math()` is False; after `canvas.draw()` no tick or colorbar label contains `$` |
| V12 | `test_geometry_follows_the_events_not_a_literal` (`n_x=128`, `n_y=200`) | — | spin maxima 199 / 127; image shapes follow |
| V13 | `test_a_nudge_moves_artists_and_rebuilds_nothing` | — | axes, images and overlay artists are the same objects after a change |
| V14 | `test_an_unusable_background_is_shown_as_not_set_with_its_reason` | — | per B5 |
| V15 | `test_ok_is_unavailable_for_an_inverted_peak_or_a_partial_background` | — | per B10 |
| E1 | `test_select_roi_is_enabled_only_with_a_row_selected` | no button | per B1 |
| E2 | `test_select_roi_writes_the_row_it_was_opened_for` (seed below; plus a leg with a short `RB_Ymin` column) | — | row 1 written; rows 0, 2 and every other column unchanged; all per-angle columns one length |
| E3 | `test_select_roi_cancel_leaves_the_document_untouched` | — | `to_dict()` equal |
| E4 | `test_select_roi_writes_no_file` (`SettingsDocument.save` patched to raise; `tmp_path` cwd) | — | no call, no new file |
| E5 | `test_an_unreadable_run_is_reported_not_fatal` | — | panel text; no dialog constructed |
| E6 | `test_the_run_file_comes_from_the_row_or_is_asked_for` | — | per B2, three legs |
| E7 | `test_the_dialog_is_released_not_destroyed` | — | gone from `topLevelWidgets()` after `DeferredDelete`; no `.destroy(` in either module |
| E8 | `test_an_x_range_change_updates_the_scalar_and_its_editor` | — | per B9 |

```python
from qtpy import QtCore, QtWidgets
from qtpy.QtTest import QTest

from launcher.apps import settings_editor
from launcher.apps.settings_editor import SettingsEditorTab
from lr_reduction.settings_document import SettingsDocument


def test_select_roi_writes_the_row_it_was_opened_for(monkeypatch, events):
    doc = SettingsDocument()
    for peak in (130, 140, 150):
        doc.add_angle(RB_Ymin=peak, RB_Ymax=peak + 6, BkgROI=[peak - 3, peak + 9, 0, 0])
    tab = SettingsEditorTab(document=doc)
    tab.angle_table.setCurrentCell(1, 0)
    # `_events_for_row` and `peak_spins` are illustrative names; the button and class names are fixed.
    monkeypatch.setattr(tab, "_events_for_row", lambda row: (events, f"row {row}"))

    def accept_after_the_selection_moves(dialog):
        tab.angle_table.setCurrentCell(2, 0)  # the selection is no longer the target
        dialog.peak_spins[0].setValue(141)
        return QtWidgets.QDialog.Accepted

    monkeypatch.setattr(settings_editor.ROISelectionDialog, "exec_", accept_after_the_selection_moves)
    QTest.mouseClick(tab.select_roi_button, QtCore.Qt.LeftButton)

    assert doc.get("RB_Ymin") == [130, 141, 150]
    assert doc.get("RB_Ymax") == [136, 146, 156]
    assert doc.get("BkgROI")[1] == [137, 149, 0, 0]  # untouched in the dialog, so not rewritten
```

### 6′. v2 — the tests the rejection names (each RED on `791bdbe` under its §7′ mutation, GREEN after)

The Developer's v1 names are kept where a test is extended (the Integrator's reviewers cite them); new tests take
the next V/E number. "Gesture" keeps §6's meaning: `QTest.mouseClick` on the real button, a press–move–release on
the canvas through the existing `drag` helper, a `QTimer` driving the real modal — never `.reject()`, `.accept()`,
`.emit()` or a callback called by hand.

| # | Test (v1 name where extended) | What it asserts | Reds under |
|---|---|---|---|
| **E4′ → E4″ (v3)** | `test_select_roi_writes_no_file` — domain widened to *every file the slot can write* | with the file dialog returning a run in `tmp_path/nexus/` and `exec_` → Rejected: **`SettingsDocument.save` stubbed by a recorder, never by a raiser (v3, B-1: a raising stub inside the `@guarded` slot is swallowed by `report_problem` and the test passes) — `calls == []` and the panel reports no problem**; **the only change on disk after the click + `tab.settings.sync()` is the QSettings key `roi_nexus_dir`** (snapshot `QSettings.allKeys()`/values before and after — exactly one key differs, to the run's folder); `tmp_path` (cwd) and `tmp_path/nexus/` hold the same set of files as before | M28 (the slot writes a file into cwd or beside the run); M29 (the slot writes a second QSettings key); **M30 (the slot calls `self.document.save(Path.cwd() / "roi-settings.json")` after `refresh_report()` — v3)** |
| **V11′** | `test_file_text_and_log_ticks_never_reach_the_math_parser` — two draws | draw 1 at the opening limits, draw 2 with one profile's y axis `set_ylim(20, 80)` (inside one decade — what the toolbar's zoom does) and drawn again; after **each** draw, for the three log profiles and both colorbars' axes: no `get_xticklabels(minor=True)`, `get_yticklabels(minor=True)`, major label or `get_offset_text()` text contains `$`; the title leg unchanged | M11 (major formatter removed); **M17 (`:87` minor formatter deleted — 48 mathtext minor labels on the zoomed draw)**; **M17b (only the colorbar's minor formatter removed — must red on its own, not through a pyparsing warning)** |
| **V15′** | `test_ok_is_unavailable_for_an_inverted_peak_or_a_partial_background` — `RB_Ymin=None` leg (or a new `test_an_unset_peak_draws_no_overlay_until_both_edges_are_set`) | open with `RB_Ymin=None`, `RB_Ymax=155`: every artist in `dialog.overlays["peak"]` on `y_axis`, `xy_axis`, `ytof_axis` has `get_visible() is False`; set the low spin → still hidden; set the high spin → visible on all three, edges equal the spins. *(v3, the Developer's D-62 correction: two legs — `RB_Ymin=None, RB_Ymax=155` and `RB_Ymin=145, RB_Ymax=None` — each hidden until the missing edge is set; one sequence cannot occur with `RB_Ymax` already set.)* | **M18 (`:538` `_move("peak", peak)` → `_move("peak", self._spin_values(self.peak_spins))` — a band from −1 to 155 appears)** |
| **V16** | `test_a_background_the_reducer_does_not_subtract_is_drawn_and_labelled` gains `use_bs=None` and `use_bs=[]`-row legs (via `doc.set("useBS", [])` → `angle_row(0)["useBS"] is None`, the reachable route) | the status line **does not** contain "not subtracted"; the bands are drawn; the existing `0`/`False` legs still say "not subtracted" | **M19 (`:216` `!= 0` → `bool(...)`)** |
| **V4′** | `test_dragging_on_the_y_profile_sets_the_chosen_range` gains X and TOF legs (or `test_dragging_on_the_x_and_tof_profiles_sets_the_range_and_the_filter`) | `drag(dialog, dialog.x_axis, 70, 180)` → `x_spins` read `[70, 180]`, the X overlay's edges on every axis with an X axis equal them, `dialog.changes() == {"data_x_range": [70, 180]}`; `drag(dialog, dialog.tof_axis, t1, t2)` → `tof_spins` read `[t1, t2]`, the profiles and the XY image are rebuilt from the filtered events (V2's equality against `xy_image(events, tof_range=…)`), `dialog.changes() == {}` | **M20 (`_x_range_selected` → `pass`)**, **M21 (`_tof_range_selected` → `pass`)**, **M22 (the two bodies swapped)** — each alone |
| **V6′** | `test_cancel_reports_nothing` — presses the button | edit a spin, then `QTest.mouseClick(dialog.buttons.button(QDialogButtonBox.Cancel), LeftButton)` (the `QDialogButtonBox` at `:285` becomes `self.buttons`); `dialog.result() == Rejected`; `changes() == {}` after the dialog closes (what the slot reads) | **M23 (`:286` `rejected.connect(self.accept)`)** |
| **V7′** | `test_ok_reports_only_what_changed` — presses the button | the same gesture on the Ok button; `result() == Accepted`; the three legs of v1 unchanged | **M24 (`:285` OK left unconnected)** |
| **E9** | `test_the_real_modal_dialog_writes_as_its_buttons_are_pressed` (two legs: Cancel, OK) | **no `exec_` patch**: a `QTimer.singleShot` fires after the modal opens, finds the live `ROISelectionDialog` among `QApplication.topLevelWidgets()`, sets `peak_spins[0]` to 141, then clicks Cancel (leg 1) / Ok (leg 2) — as `scripts/roi-popout-acceptance.py` does; leg 1: `doc.to_dict()` unchanged; leg 2: `RB_Ymin[row] == 141`, nothing else written; the dialog is gone after `DeferredDelete` (E7's check). **v3 (E9′, B-1 + A-1):** each leg snapshots the files (name, size, mtime) under `tmp_path` and `Path.cwd()` before and asserts the same set after — nothing new, nothing changed, the QSettings store excepted; the `give_up` timer is a `QTimer` object stopped in a `finally` (or parented to the tab), never a bare `singleShot` that outlives the test | M23, M24 — through the real modal path; **M30 (v3)**. *(v2 listed M4 here; corrected — Cancel's `reject()` restores the opening values, so E9 cannot red M4; E3 does.)* |
| **V17** | `test_the_log_toggle_switches_every_profile` | `QTest.mouseClick(dialog.log_check, …)` → `get_yscale() == "linear"` on `y_axis`, `tof_axis`, `x_axis` after a draw; click again → `"log"` on all three **and** V11′'s label assertion holds (the plain formatters are re-applied) | **M25 (`:562` `set_yscale("log")` unconditionally)**; M25b (the formatters not re-applied after the toggle) |
| **V18** | `test_the_profiles_and_the_ytof_image_open_on_their_data` | after open and draw: `tof_axis.get_xlim() == (tof_edges[0], tof_edges[-1])`, `x_axis.get_xlim() == (0, n_x − 1)`, **`ytof_axis.get_xlim() == (tof_edges[0], tof_edges[-1])`** (B3′), `y_axis.get_xlim()` within the ±margin of the peak edges and inside `[0, n_y − 1]`; after a peak nudge and after a TOF filter change the Y-TOF and TOF limits are unchanged | **M26 (`:573-574` deleted — T1)**, **M27 (the Y-TOF `set_xlim` removed, or the overlays made with `axvspan(0, 1)` again — A1)** |

**The commit body also quotes M13** (the battery row's code as run, verbatim) and its observed `-> N failed` — the
Integrator's three forms gave 4 where the v1 body says 5; whichever the quoted code gives is the record.

## 7. Mutate-once gate (record each in the commit body as `<mutation> → <test> -> N failed`)

| # | Mutation applied to the production code | Must red |
|---|---|---|
| M1 | the slot reads `currentRow()` when writing instead of the captured row | E2 |
| M2 | the slot writes `BkgROI` whether or not it changed | E2 (`[137, 149, 0, 0]` leg), V7 |
| M3 | the slot mutates the column in place instead of calling `set_angle_field` | E2 (short-column leg) |
| M4 | the slot ignores the dialog's result code | E3 |
| M5 | `@guarded` removed from the slot | E5 |
| M6 | the button is always enabled | E1 |
| M7 | background overlay drawn from the raw entry, not `background_bands` | V3 |
| M8 | the view filter reported as `tof_min`/`tof_max` | V8 |
| M9 | Estimate catches the refusal and brackets the argmax | V9 |
| M10 | `parse_math=False` removed from the title | V11 (title leg) |
| M11 | plain formatter removed from the log axes / colorbars | V11 (tick leg) |
| M12 | spin maxima from literals 303 / 255 | V12 |
| M13 | every change calls `figure.clear()` and redraws | V13 |
| M14 | image drawn with `origin="upper"`, or transposed | V2 |
| M15 | OK validation removed | V15 |
| M16 | `deleteLater()` → `destroy()` | E7 |

### 7′. v2 rows (added to the ledger battery script; each must red **alone**, N ≥ 1, in the commit body)

| # | Mutation applied to the production code | Must red | Integrator's v1 observation |
|---|---|---|---|
| M17 | `roi_dialog.py:87` `axis.set_minor_formatter(LogFormatter(labelOnlyBase=True))` deleted | V11′ (zoomed draw, minor labels) | survived, 618 passed; 48 mathtext minor labels on run 231801 zoomed to 20–80 |
| M17b | only the **colorbar** axes' minor formatter removed | V11′ (colorbar leg) | today reds only via a pyparsing warning in the empty-run test |
| M18 | `:538` `self._move("peak", peak)` → `self._move("peak", self._spin_values(self.peak_spins))` | V15′ `None` leg | survived; a −1…155 band on three axes |
| M19 | `:216` `values.get("useBS") != 0` → `bool(values.get("useBS"))` | V16 (`None` and `[]` legs) | survived; "not subtracted" shown for `None` |
| M20 | `:317-318` `_x_range_selected` body → `pass` | V4′ X leg | survived |
| M21 | `:320-321` `_tof_range_selected` body → `pass` | V4′ TOF leg | survived |
| M22 | the two bodies swapped | V4′ both legs | survived |
| M23 | `:286` `buttons.rejected.connect(self.reject)` → `.connect(self.accept)` | V6′, E9 Cancel leg | survived — Cancel would write the edits |
| M24 | `:285` `buttons.accepted.connect(self.accept)` deleted | V7′, E9 OK leg | survived |
| M25 | `:562` `axis.set_yscale("log" if log_scale else "linear")` → `axis.set_yscale("log")` | V17 | survived |
| M25b | the plain formatters not re-applied after the toggle (the `_plain_log_ticks(axis.yaxis)` call after `set_yscale` removed, `:563-564`) | V17 second click + V11′ assertion | — *(v3: this is the battery's existing M11a row — the Developer's D-62 note; not a new row)* |
| M26 | `:573-574` (`tof_axis`/`x_axis` `set_xlim`) deleted | V18 | survived (T1) |
| M27 | the Y-TOF `set_xlim` of B3′ removed (v1's state) | V18 Y-TOF leg | A1: the image fills 32 % of its panel |
| M28 | the slot writes a file (`Path.cwd() / "roi.tmp"`, or beside the chosen run) after the dialog | E4′ | — (v1's E4 saw only `SettingsDocument.save`) |
| M29 | the slot records a second QSettings key (e.g. `roi_last_run`) | E4′ | — |
| **M30 (v3)** | `settings_editor.py`: after `self.refresh_report()` in `select_roi`, `self.document.save(Path.cwd() / "roi-settings.json")` | E4″, E9′ | **survived v2 with 628 passed and wrote a 1 484-byte settings JSON into the cwd** — the raising stub was swallowed by `@guarded` |
| **M31 (v3)** | `roi_dialog.py:404` `"aspect": "auto"` → `"aspect": "equal"` | V2′ | **survived v2 with 628 passed**; Y-TOF axes box 273 × 221 px → 273 × 1 px |

**Frame** (helpers introduced or re-pointed — one row per call site): `_move_span` — one row per overlay
artist it moves (peak, low background, high background, X range, TOF filter/window, on each axes where the
artist exists): swap `low`/`high` or move the wrong artist → the matching V5 parameter reds, alone; the
row→file lookup (B2) — its one call site, E6; the image refresh — XY and Y-TOF separately (M13, M14 each
applied per image). The lift commit itself needs no rows (nothing calls it yet). A mutation that stays
green is diagnosed before anything else is touched (L4).

## 8. Acceptance criteria

1. `pixi run test-reduction` returns zero from the repository root, as written (it runs `test-launcher`
   first); `pixi.lock` restored, not staged.
2. `git diff --stat agentic/exp-review...feature/roi-popout-dialog` lists exactly the four files of §4. No
   `plans/`, `todo.md`, mutation battery or other ledger-shaped path; nothing under `src/`.
3. Every row of §7, §7′ and the frame is in a commit body with its observed `<test> -> N failed`. **v2:** the seven
   rows the Integrator ran (M17, M18, M19, M20–M22, M23/M24, M25, M26) each show N ≥ 1 in the v2 body; M13's row is
   quoted as code with its count; the ledger battery script carries the new rows and its SHA is in the body. **v3:** M30 and M31 each
   show N ≥ 1 with the test named; the body states that the Integrator's two reproduction commands (the `document.save` line after
   `refresh_report()`; `"aspect": "equal"`) were run against the v3 tree and each red.
4. `grep -nE "304|256|15\.75|252\.7|h5py|get_lam_range" launcher/apps/roi_dialog.py` prints nothing; the
   editor's lookup carries the one file-name pattern of F9 and says where it comes from.
5. Prescriptive comments and commit-body claims ("cannot write a file", "what is drawn is what the reducer
   uses", "does not rebuild the figure") name the test that falsifies them, or are marked inferred. **v2:** the two
   docstring claims the gate falsified are re-read against their tests — `select_roi`'s "no file is opened for
   writing" against E4′'s domain (B-1), the module docstring's author list against F2's measurement (D1) — and the
   two #197 comments at `roi_dialog.py:140` and `:170` cite a test or say "inferred" (D7). **v3:** `select_roi`'s "E4 watches every file and key" is
   reworded to the domain E4″/E9′ enumerate (`SettingsDocument.save`, the working directory, the run's folder, the QSettings store), or
   kept only if E9′'s snapshot makes it true; `_guarded`'s docstring cites the dialog's own battery rows (G-guard-values/-estimate/-log), not M5 (D-a).
6. ui-aspects review receives §3's states table and V2/V3/V11/V13/E2/E7 as the pins for: where the drawn
   data lives (`ax.images[0]`), faithful axes, `deleteLater()`, the active-row trap.
7. **Deployment-shaped acceptance (Integrator, analysis node, `PIXI_CACHE_DIR` under the checkout):** start
   the launcher from the feature tip; load a real `shared/autoreduce` settings file or a reduced `.dat`;
   select each angle in turn → Select ROI; record for one run that the XY and Y-TOF images, peak and
   background bands match that run's monitor.sns.gov report; drag the peak, OK, see the table change,
   save to a scratch path, reload; with the log toggle on, no traceback on the console (the mathtext
   recursion is font-set dependent and did not reproduce on uvdl3 — F7; that the analysis node is nearer
   the reporter's environment is **inferred**). Path, run number
   and the saved file's sha256 go in the PR body.
8. PR body: names upstream #197 and the source SHA; states what was lifted and what was not; the deploy
   consequence — **launcher only: no reduction-path file changes; scientists see it after the human
   redeploys the review tier**; draft, the merge is the human's.

## 9. Learnings relied on (quoted)

- L1 (`setup/patterns/ui-aspects.md`, CPKT): "**`imshow`'s `origin` argument affects the DISPLAY, not
  `get_array()`**"; "never introduce an arbitrary visual distortion to make a plot "look nice" — e.g. do
  **not** force `set_aspect('equal')`"; "Use **`widget.close()` + `widget.deleteLater()`**"; the
  active-row anti-pattern: "identical inputs + identical visible UI state … produce **different saved
  data** depending on which row was highlighted". → B3, B12, B1/E2.
- L2 (`agentic/analysis/exp-settings-roi:plans/settings-editor-learning.md` §1): "A `QTest.mouseClick` at
  a coordinate you reasoned about is still a claim about geometry. Measure the widget's actual hit region,
  or use a gesture that has no geometry." → §6.
- L3 (same file, §5): "For any GUI handler, ask what happens when it raises — not whether it raises in
  the tests." → B2, E5, the pathological rows of §5.
- L4 (same file, §8): "A mutation that stays green means the test is vacuous OR the mutation missed." → §7.
- L5 (reference `plan/roi-selector/plan.md` R5, R8, R14): "What the user sees plotted is not what is
  written"; "keeps the images and moves only the overlay"; "an overlay, never a crop". → B4, B11, B8.
- L6 (commit body of `65c83d9`): "this does NOT fix the reported traceback … the failure arrives via
  axis.py:_get_ticklabel_bboxes — a TICK LABEL". → B12's second half, V11's tick leg, §8.7.
- **L7 (v2, from this rejection — the campaign's recurring lesson, in its GUI form):** a §3 cell, a B-row clause or a
  docstring sentence that no test observes is a claim; the gate finds it by mutating the production line and watching
  618 stay green. Three shapes recurred here: (i) **the gesture was replaced by its effect** — `reject()` called instead
  of Cancel pressed, so wiring Cancel to `accept` survived; (ii) **the assertion read a subset of the domain** — major
  tick labels but not minor or offset text; `SettingsDocument.save` but not "every file the slot can write"; (iii) **a
  states-table cell had a mutation named and no test** (`None` peak, `useBS None/[]`). The v2 discipline: every §3 cell
  names its test in the table itself; every B-row verb ("drag", "press", "toggle") has a gesture test per surface it
  names (Y, X **and** TOF; Cancel **and** OK); every "no X" claim states its domain and the test enumerates the domain.
- **L8 (v2, factual claims in docstrings):** an author list is a measurement (`git log -L`, `git blame -w -M -C` on
  the lifted range), not a reading of a PR's contributor list — the plan carried `3f74d41` from the latter, and the
  docstring and the lift commit repeated it (D1). A credit is a factual claim and sits under §8.5 like any other.
- **L9 (v3, a stub inside a guarded slot):** a test double that *raises* to prove "never called" is blind inside any handler that
  catches `Exception` — the `@guarded` slot turned the assertion into a panel message and the test passed with a document saved to
  disk. Under L3 ("ask what happens when it raises") the double must *record* and the test must read the record **and** the panel;
  the disk itself is watched by a before/after snapshot, because the claim is about files, not about a method. Same shape as L7(ii):
  the assertion read a proxy for the domain, not the domain.

## 10. Assumptions and open questions (the plan proceeds under each default)

| # | Question | Owner | Default |
|---|---|---|---|
| A1 | Item 9 asks for 2D plots and for dragging; must the drag also work **on the images**? | scientists | drags on the profiles (the reviewed #197 interaction); image overlays follow live and are not pickable — no advertised-but-dead affordance (R7). Image drag is a follow-on slug |
| A2 | Should the dialog also edit the reduction's TOF window (`tof_min`/`tof_max`)? | scientists | shown as an overlay, edited in the table; the dialog's TOF entry stays a view filter, because conflating them would let a viewing aid cut the reduction |
| A3 | "Each angle in turn": Previous / Next inside the pop-out? | scientists | one row per pop-out, modal; reopen for the next row |
| A4 | Launcher tests stay independent of the data submodule (in-memory events; real files exercised by the data slug and §8.7)? | Analyst | yes |
| A5 | Credit for the lifted code: a `Co-authored-by:` trailer for #197's authors publishes their addresses in the fork's history. | human | name PR, SHA and authors in the module docstring and the lift commit's body; no personal trailer |
| A6 | Modal `exec_()` (row cannot move underneath) vs a non-modal window the scientist keeps beside the table. | human / scientists | modal |
| A7 | `max_events` for the read. | Developer | 2 000 000, #197's value (`json_settings_builder.py:137`) |
| A8 | The reducer's ±1 question on the peak-edge rows (data plan F7) changes what B4 draws if the scientists rule. | scientists | draw what the reducer does today |

## Revision history

v1 — authored 2026-10-02 against `7b6d6b9` (staged behind `roi-popout-data` merged); **re-sealed and dispatched 2026-10-05 stacked on
`feature/roi-popout-data` @ `f424aec`** (R1's PASS, I-43 / draft PR #44) with `feature/editor-notes-and-report-spelling` @ `779f787` merged
forward at cut, under the stacking-by-file-overlap rule's clause (4) (posture `ec10742`; A-77): editor-side citations re-measured at
`779f787`, data-contract names verified at `f424aec`, the harness fixtures re-located; the data plan's correction (the report's second image
is Y-vs-TOF) already in S9.

### v3 — 2026-10-05, after the Integrator's rejection of v2 @ `e017a97` (`review/roi-popout-dialog` @ `088686c`; attempt 2 of 3 — v3 is the last)

Rejection, verbatim (tag annotation): *"roi-popout-dialog v2 REJECTED — a document save from the slot and a forced aspect go unasserted. Review
gate (ui-aspects, design, test). v2 closes every v1 item: the gate is green (launcher 757, reduction 874); the seven v1 survivors, M27, M28 and
M29 red with v2's recorded counts; the §8.7 acceptance on IPTS-36119 passes again, and the Y-TOF image now opens on its data. Two pins are still
missing, each surviving with 628 passed (reproduced): — the slot saving the settings document (#197's F2): E4's stub raises inside the @guarded
slot, the panel swallows it, and E9 writes a 1484-byte settings file into the cwd unseen. This also falsifies "E4 watches every file and key"; —
"aspect": "auto" -> "equal": the Y-TOF box becomes 273 x 1 px. Both were already gaps in v1. Work order: todo.md (attempt 3 of 3 is the last)."*
The work order (`088686c:todo.md`): B-1 (a, d), B-2 (a), the cheap A-1 (E9's timer), advisories U-a–U-c, D-a, T-a, and D-b for the Analyst (§6′
listed M4 under E9; the Developer's statement that E9 cannot red M4 is right — the plan row was stale).

What v3 changes: the "v3" section after the canonical-copy line; §6 V2 → V2′ (aspect); §6′ E4′ → E4″ (a recording stub + the panel), E9 → E9′
(disk snapshot, the timer; M4 removed), V15′ as two legs; §7′ M30, M31, M25b noted as M11a; §8.3 and §8.5 extended; §9 L9. Unchanged: everything
else, the Base, the stack, the PR target; the Developer continues on `feature/roi-popout-dialog` @ `e017a97` (predecessors unmoved). **Plan
errors owned:** v2's E4′ prescribed "`SettingsDocument.save` not called" without saying *how* the double must observe it — a raising stub was a
natural reading and it is blind inside `@guarded` (L3 was in §9 and not applied to the test double); v2's E9 named M4 as a red it cannot produce;
V15′ described a sequence that cannot occur; B3's "aspect left to the data" was a declared cell with no test in v1 **and** v2 — the v2 table
audit ("every cell names its test") covered the types table and missed B3's own clause. The Integrator states both gaps were also theirs to
raise at v1.

### v2 — 2026-10-05, after the Integrator's rejection of v1 @ `791bdbe` (`review/roi-popout-dialog` @ `b22c8df`; attempt 1 of 3)

Rejection, verbatim (tag annotation): *"roi-popout-dialog v1 REJECTED — six declared behaviours untested, one false docstring claim. Review
gate (ui-aspects, design, test). The pop-out works on real data: the gate is green (launcher 747, reduction 874), and the deployment-shaped
acceptance on IPTS-36119 matched the run's stored web report (peak, background and x-range lines exact; XY and Y-TOF the same cells, report =
raw x dead-time factor 1.002-1.018). It also opened every row, dragged and saved one peak, and showed no traceback. Reproduced here, each
surviving with 618 passed: the minor log formatter deleted (mathtext on a zoomed profile); the peak overlay shown when RB_Ymin is None; useBS
None read as off; the X and TOF drags dead; Cancel wired to accept; the log toggle stuck on log. Also: select_roi's "no file is opened for
writing" is false (QSettings roi_nexus_dir). Work order: todo.md."* The work order (`b22c8df:todo.md`): B-1 (d) the docstring, B-2…B-7 (a/b)
the six untested behaviours, M13's count to show, advisories A1–A8 (ui), D1–D8 (design), T1–T3 (test), and three plan corrections addressed to
the Analyst: **P1** §3's F2 sentence contradicted B2 (B-1's source); **P2** F2's author list named `3f74d41`, which wrote none of the lifted
lines (D1's source); **P3** V9's sparse-run threshold is the estimator's.

What v2 changes: the "v2 — what changes and why" section after the canonical-copy line; §2 F2 corrected (P2); §3 B3′ (A1), the F2 sentence
corrected (P1), the types table with a test in every cell; §4 per-file v2 notes; §6′ (E4′, V11′, V15′, V16, V4′, V6′, V7′, E9, V17, V18); §7′
(M17–M29); §8.3 and §8.5 extended; §9 L7, L8. Unchanged: the Declared scope, §1, §5, §8.7, §10; the Base, the stack and the PR target — the
Developer continues on `feature/roi-popout-dialog` @ `791bdbe` (both predecessors unmoved at dispatch: `f424aec`, `8ca43ce`). **Plan errors
owned:** P1 and P2 were the plan's sentences, copied faithfully by the Developer into two docstrings and a commit body; v1's §3 table declared
two cells with no test; §6 named gestures and then listed V6/V7 in a form a direct call could satisfy. **Analyst follow-ups filed from the
advisories:** D2 (a Qt-free validator for the written background form) and D3's third `REF_L_{run}.nxs.h5` copy (`settings_document.py:159`)
→ `roi-popout-data` follow-up todo; P3 → recorded as an advisory on the data slug (the Developer's `e0bba12`).

### Escalation — 2026-10-06, after the Integrator's rejection of v3 @ `21a7367` (`review/roi-popout-dialog` @ `ad3558c`; attempt 3 of 3 — the cap)

Rejection, verbatim (tag annotation): *"roi-popout-dialog v3 REJECTED (attempt 3 of 3, the cap) — five declared clauses unpinned; production
right. Review gate (ui-aspects, design, test). v3 closes v2's two items (M30 -> 2, M31 -> 1), and every earlier survivor reds. The gate is green
(launcher 757, reduction 874), and the §8.7 acceptance on IPTS-36119 passes for the third time with identical numbers. Five declared clauses
still have no test that can fail; each survives with 628 passed, reproduced here: RBnum written by the lookup, even on Cancel; Normalize instead
of LogNorm; the colorbars removed (or swapped); the "all angles" label; a truncating write to the 0-byte run fixture. All were latent since v1.
The fix is about six assertions and one fixture byte, with no production change. The retry cap is reached, so this goes to the Analyst's
escalation and the human. Work order: todo.md."* No v4 is cut: the canonical record, the clause-by-clause pin audit and the human's options
(A: one cap extension for a tests-only v4 — recommended; B: merge-as-is with the five pins as a follow-up, a rule exception; C: decompose — not
recommended; D: stop) are in `plans/roi-popout-dialog-escalate.md`.
