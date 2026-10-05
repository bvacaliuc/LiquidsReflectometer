# Plan: `roi-popout-dialog` — "Select ROI" beside Add/Remove: #197's dialog lifted onto `SettingsDocument`, with the web report's two detector images

**Campaign:** `exp-review-fixes` · **Leaf:** `roi-popout-dialog` (refs `triage/roi-popout-dialog`,
`feature/roi-popout-dialog`, `qa/roi-popout-dialog`) · **Status:** READY — v1 (attempt 1 of N = 3) — dispatched 2026-10-05 under the posture's **stacking by file overlap** rule
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

Canonical copy: ledger `plans/roi-popout-dialog-plan.md`; the copy on `triage/roi-popout-dialog` is
byte-identical at dispatch.

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
| F2 | The seed. | `git show agentic/feature/harden-review-branch:launcher/apps/json_settings_builder.py` → `_move_span` `:396-406`, `ROISelectionDialog` `:409-690` (`values()` at `:682`), `edit_roi` `:1303-1348`. Upstream's copy (`upstream/exp-json-settings-builder` @ `3ce5e20`, `:337`/`:350`) differs in the dialog only by the `parse_math=False` title (`:452-458` in the hardened copy). Authors of the lifted lines: Mathieu Doucet (`f5513c7`, `8191e49`, `1e692c7`, `ab22307`), welbournR (`3f74d41`). |
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
| B3 | Five plots: XY image and Y-vs-TOF image (colour, log norm, colorbar), then counts per Y, per TOF, per X. Image arrays are `roi_estimate.xy_image` / `y_tof_image` unmodified; `origin="lower"`, extent on pixel centres, aspect left to the data. |
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
F2: the dialog and the slot open no file for writing; pinned by E4. F4: `GLOBAL_FIELDS` is not lifted;
`test_an_enumerated_editor_offers_the_declared_spellings` stays the pin. F3: no geometry, distance or band
literal in `launcher/`; pinned by V12. F5 (this plan): the default background comes from the data layer,
which refuses instead of clamping to 0. Mathtext: B12, pinned by V11.

**Types and states each path acts on.**

| Value at open | present | empty / short | `None` |
|---|---|---|---|
| `RB_Ymin[row]`, `RB_Ymax[row]` (per-angle int) | spins and overlays | column shorter than the row → treated as `None` (`angle_row`) | spins at "not set"; no peak overlay; OK unavailable until both are set |
| `BkgROI[row]` (per-angle list of 4 int) | per data plan §3: 0 zeros → two bands; 2 zeros → peak-adjacent bands | `[]`, wrong length, 1/3/4 zeros → B5 | B5 |
| `data_x_range` (scalar list of 2 int — **not** per angle) | X overlay and spins | wrong length → reported in the status line; X spins start at the full detector; written only if edited | same |
| `tof_min[row]`, `tof_max[row]` (per-angle float, µs) | TOF-window overlay | the column may be `[]` (reducer default) → no overlay | no overlay |
| `useBS[row]` (per-angle bool / 1 / 0) | label only | `[]` → reducer default is on | treated as on |
| `RBnum[row]` (runtime-owned int) | file lookup | absent → ask | ask |
| events | images and profiles | zero events → empty plots, Estimate refuses | n/a |

## 4. Files to change

| File | Change |
|---|---|
| `launcher/apps/roi_dialog.py` | New. `_move_span` and `ROISelectionDialog` lifted from F2's lines, re-seated on `RunEvents` and the data layer; two image axes added. Module docstring names PR #197, the source SHA and its authors (A5). Lift commit first (verbatim lines, not yet wired), then the changes, so the diff against the seed is reviewable. |
| `launcher/apps/settings_editor.py` | `select_roi_button`; a `@guarded` slot; the row→file lookup (B2). |
| `launcher/tests/test_roi_dialog.py` | New: V1–V15. Events are built in memory through the real `RunEvents`, never a mock. |
| `launcher/tests/test_settings_editor.py` | E1–E8. |

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
| V2 | `test_the_images_are_the_data_layers_arrays` | — | `ax.images[0].get_array()` equals `roi_estimate.xy_image(...)` / `y_tof_image(...)`; `origin == "lower"`; extent on pixel centres |
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
3. Every row of §7 and the frame is in a commit body with its observed `<test> -> N failed`.
4. `grep -nE "304|256|15\.75|252\.7|h5py|get_lam_range" launcher/apps/roi_dialog.py` prints nothing; the
   editor's lookup carries the one file-name pattern of F9 and says where it comes from.
5. Prescriptive comments and commit-body claims ("cannot write a file", "what is drawn is what the reducer
   uses", "does not rebuild the figure") name the test that falsifies them, or are marked inferred.
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
