# Plan: `roi-popout-data` — the Qt-free data behind the ROI pop-out: detector images, profiles and the reducer's own background bands, on PR #31's `roi_estimate`

**Campaign:** `exp-review-fixes` · **Leaf:** `roi-popout-data` (refs `triage/roi-popout-data`,
`feature/roi-popout-data`, `qa/roi-popout-data`) · **Status:** v2 (attempt 2 of N = 3; v1 rejected at `review/roi-popout-data` @ `b4cda54` — N-1 the plan's "cell for cell" equality with the web report is false on 45 of 63 runs, T-1…T-5 five declared behaviours with no failing-capable test; **no module arithmetic changes**; see Revision history) — v1 dispatched 2026-10-05 under the posture's **stacking by file overlap** rule
(`ec10742`, rule (2): the plan's files overlap **no** open branch, so the slug is cut from `exp-review` and its trigger is its own
readiness — "presentation order never delays a build"; the charter's `E5 → R1` edge was that order) · **Base:** `agentic/exp-review` @
**`5a8742d`** **plus a regular merge of `agentic/feature/roi-estimate` @ `655a67d`** (PR #31's head; F1 re-run at the new tip: still 3
files added, 0 conflicts) — **overlap at dispatch** (`git diff --name-only agentic/exp-review...agentic/feature/<x>`, tests excluded):
`feature/editor-sections` {`settings_editor.py`, `field_spec.py`}, `feature/test-suite-warnings` {`background.py`, `dead_time_correction.py`,
`output.py`, `peak_finding.py`}, `feature/launcher-env-outside-xdg-cache` {`new_launcher.py`, `runtime_env.py`}, `feature/rereduction-
headers-land` {`new_reduction_from_file.py`, `nr_reduction_calc.py`, `nr_tools.py`, `save_reduced_data.py`} — **∩ this plan's files = ∅**
(`roi_estimate.py`, `test_roi_estimate.py`, `scripts/test/roi_estimate_mutations.py` arrive by the merge; `scripts/test/README.md` is
touched by none) · **PR target:** `exp-review` on the fork, **draft**; it supersedes PR #31 (base `exp`), which the human closes ·
**Depends on:** nothing open (A1 — file-disjoint from every lane; the former "after `editor-sections`" was presentation order, retired by
the rule) ·
**Review domains:** numerical-diagnostics, test (block) · **Kind:** additive library module — **not**
reduction-path (F9) · **Sources:** scientists' item 9 (`requests/updates_for_setting_loader.md`), Q7
(`plans/settings-loader-clarifications-decision-request.md` §Resolution), charter §3 row, PR #31's body
and the Advisor's comment on it (2026-09-27).

Canonical copy: ledger `plans/roi-popout-data-plan.md`; the copy on `triage/roi-popout-data` is
byte-identical at dispatch.

## Declared scope

**Files in:** `src/lr_reduction/roi_estimate.py`, `tests/unit/lr_reduction/test_roi_estimate.py` (both
arrive by the merge), `scripts/test/roi_estimate_mutations.py` (moved from `plans/scripts/`),
`scripts/test/README.md` (one table row).

**Behaviours in:** PR #31's seven advisories closed (§3 I1–I7) plus I8; the pop-out's data contract
(§3 B1–B9): detector XY image, Y-vs-TOF image, three profiles, TOF edges over the full span, the
background bands **as the reducer will use them**, and a default background in the reducer's shape.

**Explicitly OUT** (a finding here is a PR-body advisory, not a rejection):
- every existing file under `src/` and `launcher/` — this slug edits **no** file that exists at the base
  tip except `scripts/test/README.md`; in particular not `nr_reduction_calc.py` (the sorter, F6/F7),
  `nr_tools.py`, `event_reduction.py`, `web_report.py`, `binary_processing.py`;
- the chopper band's value: `chopper_lambda_range` keeps delegating to `nr_tools.get_lam_range` with the
  library default; which of the four values is right is `chopper-band-unify` (F10);
- which peak estimator is the library's (A4); the estimator's refusal contract stays as PR #31 has it;
- any Qt, matplotlib or launcher code (`roi-popout-dialog`); a layer-(e) `dataset_probe` consumer;
- the reducer's treatment of pixel 0 and of the peak-edge rows in the background (F6, F7 — filed, not fixed).

## 1. Request and symptom

> 9. … a pop-out window with plots showing the current ROIs and an ability to adjust these … The plots
> here [in `json_settings_builder.py`] are only processed integrations, but the plots should be shown as
> 2D detector colour-plots. This should be a similar set of plots to that displayed on monitor.sns.gov.
> These plots come from web_report.py in lr_reduction.

Q7 `[human]`: "yes, the Qt-free base" — PR #31 `roi_estimate` un-tabled as this slug's base; its review
advisories are this slug's first items. There is no bug symptom: the dialog slug needs numbers that do not
exist yet. At `655a67d` the module gives one profile (counts per detector row), a peak bracket, and a
one-sided background band; it has no image, no X or TOF profile, and its background is not in a shape the
reducer accepts (F5).

## 2. Verified facts (base `7b6d6b9`; PR head `655a67d`; run 2026-10-02 on uvdl3 clone 1 — **re-sealed 2026-10-05 at `5a8742d`:** every cited library file — `web_report.py`, `nr_reduction_calc.py`, `nr_tools.py`, `binary_processing.py`, `event_reduction.py`, `scripts/test/README.md`, `pyproject.toml` — is **blob-identical** between `7b6d6b9` and `5a8742d`, so every line number below holds; F1 re-run: `merge-tree` of `655a67d` into `5a8742d` → 3 `added in remote`, 0 conflicts, the same three files (+`todo.md` removed on both sides); the one moved citation is F12's `test_settings_document.py:678` → **`:697-703`** at `5a8742d` (the editor slugs rewrote that test module; the subprocess `sys.modules` check is still there))

| # | Fact | Command → observation |
|---|---|---|
| F1 | PR #31 merges into the campaign base without conflict and adds three files. | `git merge-tree $(git merge-base agentic/exp-review agentic/feature/roi-estimate) agentic/exp-review agentic/feature/roi-estimate` → 3× `added in remote`, 0 conflict markers; `git diff --stat agentic/exp-review...agentic/feature/roi-estimate` → `plans/scripts/roi_estimate_mutations.py` +187, `src/lr_reduction/roi_estimate.py` +369, `tests/unit/lr_reduction/test_roi_estimate.py` +505 (and `todo.md` −169, already absent at `7b6d6b9`). Merge base `6c758af`; 15 commits arrive (`git rev-list --count agentic/exp-review..agentic/feature/roi-estimate`). (`git merge-tree --write-tree` needs git ≥ 2.38; this host has 2.34.1.) |
| F2 | The seven advisories are in PR #31's body ("Advisory findings — recorded, not blocking", 1–7); the human's requests are the PR's one comment. | `gh pr view 31 -R bvacaliuc/LiquidsReflectometer --json body,comments` → body lists 1 `lowres=(0, 255)` default unpinned; 2 `tof_band` block unpinned; 3 `get_y_tof` called twice; 4 `load_event_pixels` has no caller; 5 battery table ≠ `MUTATIONS` (rows 2, 4, 7, 8); 6 a test rewrites a tracked file in place; 7 `hasattr(batt, "signal")` is a stand-in. Comment: move the battery out of `plans/`; fix 6, 5, 1–2, 7; "Keep the refuse-rather-than-guess contract as is." |
| F3 | **CORRECTION to the charter row and the backlog map ("XY and X-TOF").** The web report's second image is **Y pixel against TOF**, integrated over X. "X-TOF" is only the text of its log line. | `web_report.py:596` `logger.notice("  - generating X-TOF plot")`, `:597` `# Y-TOF plot`, `:605-612` `RefRoi(… IntegrateY=False …)`, `:617-628` `_plot2d(… x_label="Y pixel", y_label="TOF (ms)", swap_axes=True …)`; the report's five plots are XY, Y-TOF, counts per Y, counts per X, TOF distribution (`:505-509`). |
| F4 | **CORRECTED at v2.** An event-array XY image equals what the web report plots **except for the run's extreme-TOF event(s)**: Mantid's `Integration` with its default range (min/max TOF, apparently rounded) drops the event at the run's minimum and/or maximum TOF, so the report's array is short by 1–2 counts in 1–2 cells on **45 of the 63 fixture runs** (and `REF_L_235251`); `201288` is one of the 18 that agree. Measured by the Integrator (N-1): `179932` differs at (72, 14) and (191, 217), sums 300 088 vs 300 086; `201282` at (216, 202), 6 050 vs 6 049. The Analyst's v1 fact generalised from one agreeing run — the same defect as A-49's census (one sample for a population). *v1's observation, kept for the record:* on `REF_L_201288.nxs.h5`: `np.bincount(event_id, minlength=n_x*n_y).reshape(n_x, n_y).T` vs `np.reshape(Integration(LoadEventNexus(…)).extractY(), (n_x, n_y)).T` (`web_report.py:579-583`) → `np.array_equal` True, sum 100002 both. A Y-TOF histogram on Mantid's own edges differs from `RefRoi` in **one cell**: Mantid's half-open last bin drops the event at exactly `tof_max` (100001 vs 100002). |
| F5 | **CORRECTION to PR #31's claim that `default_bkg_roi` offers a background.** It returns a one-sided 2-tuple; the reducer needs four bounds. | `roi_estimate.py:324-369` @ `655a67d` returns `(low, high)`; `NR_Reduction._background_roi_sorter(None, [121, 130], 136, 146)` → `[121, 130]`, and `nr_reduction_calc.py:512` then reads `sorted_bkgdROI[3]` → `IndexError`. |
| F6 | The reducer's background is **two bands** `[b0..b1]`, `[b2..b3]` from four sorted bounds; exactly two zeros mean "adjacent to the peak"; any other zero count returns `None`. | `nr_reduction_calc.py:827-840`, `:865-866`. Probe: `[133,149,0,0]` (peak 136–146) → `[133,136,146,149]`; `[160,150,130,120]` → `[120,130,150,160]`; `[0,10,150,160]` → `None`; `[0,0,0,0]` → `None`; `[133,149,0]` → `None` (then `TypeError` at `:511`). Pixel 0 is a sentinel, so it cannot be a background bound. |
| F7 | In the adjacent form the peak-edge rows are in both the signal and the background. | F6's `[133,136,146,149]` with inclusive masks (`:865-866`) and the inclusive signal mask (`:972`): rows 136 and 146 are averaged as background and summed as signal. Pre-existing; the reference's R5 ratified the ±1 form for the old tab (`plan/roi-selector/plan.md` §3 R5). Not this slug's to change. |
| F8 | The module runs unmodified on the repository's real runs; its estimator refuses six of them. | A copy of `roi_estimate.py` @ `655a67d` on all 63 files of `tests/data/liquidsreflectometer-data/nexus/` with `lowres=(50, 200)`: 57 brackets, 6 `CannotEstimateError` ("non-positive baseline": 198410–198412, 201283–201285, each ~6 000 events), 0 errors, 0 event ids outside `n_x*n_y`. `profile/∑proton_charge` from event arrays equals `counts_vs_y` to 3e-16 (201288). |
| F9 | Not reduction-path. | `grep -rn roi_estimate --include=*.py src launcher scripts` at `7b6d6b9` → nothing; at `655a67d` only the module itself. Nothing reachable from `src/lr_autoreduce/new_reduce_REF_L.py` imports it, and this slug adds no import of it — charter §4's baseline / `check_headers.py` clause does not apply. |
| F10 | The band is the library's, not a copy. | `roi_estimate.py:79-117` @ `655a67d` calls `nr_tools.get_lam_range` (`nr_tools.py:539`, default `scaled_width=3.4`); the 22.9 % Q_max divergence is `event_reduction.py:54-55` vs that function (`todo-chopper-bandwidth-four-values.md` on the reference). |
| F11 | The home for test tooling in the subject is `scripts/test/` (singular), with a README table. | `git ls-tree -r --name-only agentic/exp-review -- scripts/` → `scripts/test/README.md`, `measure_fit_path_dependence.py`, …; `scripts/tests/` does not exist. **CORRECTION** to the Integrator contract §0 and PR #31's comment, which both say `scripts/tests/`. |
| F12 | PR #31's Qt-free guard depends on an import hook Python has removed. | `test_roi_estimate.py:289-318` @ `655a67d` blocks Qt with a `find_module` finder. Python 3.11.15 (this env) still consults it (probe: `import qtpy` → blocked); `pyproject.toml:9` allows `>=3.11`, and 3.12 dropped the `find_module` fallback (**inferred** from the language's removal notice; not run here). The base tip's own check is version-independent: `test_settings_document.py:697-703` (`:678` at `7b6d6b9`) inspects `sys.modules` in a subprocess. |

## 3. Design — behaviours, not code

**First items — PR #31's advisories (I1–I7) and one found at planning (I8).**

| # | Item | Done when |
|---|---|---|
| I1 | `counts_vs_y`'s `lowres` default no longer hard-codes `n_x − 1`. | The default means "every X pixel of this run's detector", taken from `detector_shape`; pinned by provenance (move the database, the default must follow — L3). |
| I2 | The `tof_band` block is pinned. | A narrow band selects strictly fewer counts than no band, and exactly the injected in-band count. |
| I3 | One `get_y_tof` call per `counts_vs_y` call. | A spy counts one call with and without `tof_band`. |
| I4 | `load_event_pixels` has a consumer and a test (B1), or is deleted. This plan gives it the consumer. | B1, B7. |
| I5 | The battery's ledger table and `MUTATIONS` list the same rows. | Every table row is in `MUTATIONS` or marked retired with the reason; the run prints zero `ANCHOR MISS`. |
| I6 | No test writes to a tracked file. | The dirty-baseline test works on a `tmp_path` copy; `os.stat(module).st_mtime_ns` is unchanged across the test. |
| I7 | The `hasattr(batt, "signal")` stand-in is replaced by a behavioural pin, or dropped with the reason in the commit body. | If kept: a SIGTERM'd battery run (on a `tmp_path` copy) leaves the target restored. |
| I8 | The Qt-free guard does not depend on `find_module` (F12). | The subprocess imports the module and asserts no Qt binding is in `sys.modules`, as `test_settings_document.py:697-703` does. |

The battery moves with `git mv plans/scripts/roi_estimate_mutations.py scripts/test/` **in its own commit**
before any edit (history follows the file), then its docstring's run line and the test's loader path
follow. After the slug, `git ls-files plans/ todo.md` on the feature tip prints nothing.

**The pop-out's data contract.** These names are the interface `roi-popout-dialog` is planned against;
everything else about the implementation is the Developer's. Counts are **raw event counts** (the web
report's quantity), never divided by proton charge. Pixel ranges are inclusive `[low, high]`, as the
reducer's `lowres` and peak masks are (`binary_processing.py:120`, `nr_reduction_calc.py:972`).

| # | Name | Behaviour |
|---|---|---|
| B1 | `load_event_pixels(path, max_events=None)` → `RunEvents` | One read of the file. Holds per-event `x`, `y`, `tof` (µs), `n_x`, `n_y` (from the instrument database for the run's start time), `stride` (1 = every event; stride sampling, never the first N), `n_off_detector` (ids outside `[0, n_x·n_y)` are dropped **and counted**). `x = id // n_y`, `y = id % n_y` — the packing `get_y_tof` uses. |
| B2 | `xy_image(events, tof_band=None)` | Array `(n_y, n_x)`, `image[y, x]`; with no band its sum is the number of events held — **every event, including the run's extreme-TOF ones**. Equal to the web report's XY array **except** the pixel(s) of the event(s) at the run's minimum/maximum TOF, which the report's `Integration` drops under its default range (F4, corrected); the docstring, the plan and the PR body say exactly that, as the F4 Y-TOF note always did. |
| B3 | `tof_edges(events, bin_width=50.0)` | Edges over the **full** TOF span of the events — never the chopper window (R14: a window is an overlay, not a crop). 50 µs is the web report's bin (`web_report.py:602`). |
| B4 | `y_tof_image(events, x_range, edges)` | Array `(n_y, len(edges) − 1)` of the events inside `x_range`; every such event inside the edges is counted once, including one at exactly the last edge (F4). |
| B5 | `profile_y(events, x_range, tof_band=None)`, `profile_x(events, y_range=None, tof_band=None)`, `profile_tof(events, edges, x_range=None, y_range=None)` | The three 1D integrations the #197 dialog draws. `profile_y` with no band equals `y_tof_image(...).sum(axis=1)` and, divided by the summed proton charge, equals `counts_vs_y` (F8). |
| B6 | `background_bands(bkg_roi, y_min, y_max)` → `((b0, b1), (b2, b3))` | The rows the reducer will average for this `BkgROI` entry — identical to `_background_roi_sorter` wherever that returns four values — **in value and in type: Python `int`s, never numpy or float** (K1: the test compares `[type(v) for v in got]`, since `136 == 136.0`). Raises a **plain `ValueError`** (`type(exc) is ValueError`, never `CannotEstimateError` — K2) naming the reason for every entry on which the reducer would fail (F6); **the reason is specific and is what the test matches**: `None` → "no background is set for this angle" (K4), 1/3/4 zeros → "sentinel" (test A3), wrong length → "four bounds". |
| B7 | `default_bkg_roi(peak_range, n_y, gap, width)` → four ints | **Changed shape (F5):** a band on **each** side of the peak, ascending, in the reducer's form; never contains 0; refuses (does not clamp) when either side has no room or the peak is off the detector; **(v2)** refuses non-integer `peak_range`, `gap`, `width` (a fractional value or a `bool`) rather than truncating — the docstring promises ints (numerical advisory adopted); a one-row peak `(150, 150)` is a legitimate input (test A4). Defaults: A3. |
| B8 | every function above | Qt-free, no module-level cache, no geometry literal, no fifth copy of the band maths. |
| B9 | refusals | `CannotEstimateError` = "looked, nothing to offer" (no events → `tof_edges`); `ValueError` = "called wrong" (reversed range, `bin_width <= 0`, `max_events <= 0`, malformed `bkg_roi`). **(v2, K2)** `CannotEstimateError` subclasses `ValueError`, so the two are told apart by **`type(exc) is ValueError`** in every called-wrong test and `isinstance(exc, CannotEstimateError)` in every nothing-to-offer test — `pytest.raises(ValueError)` alone proves nothing. **(v2, K5)** `low == high` is a legal one-pixel range for every range kind (`profile_y(ev, (120, 120))` = 1 174 counts on 201288 today); only `high < low` refuses. |

**Types and states each path acts on.**

| Input | present | empty | `None` |
|---|---|---|---|
| events in the file | arrays of equal length | zero events: `RunEvents` with empty arrays; images and profiles are all-zero arrays of the right shape — **asserted on the values, every profile incl. `profile_tof`, not only the shapes** (test A5); `tof_edges` raises `CannotEstimateError` | n/a (missing `bank1_events` group → **h5py's `KeyError`, uncaught — pinned by a builder file without the group**, K3) |
| `tof_band`, `y_range`, `x_range` | 2-sequence, `low <= high` (**`low == high` is one pixel/bin and legal — one equal-bounds case per range kind**, K5); `high < low` → plain `ValueError` | n/a | "no restriction" where the signature allows it; `x_range` of `y_tof_image` is required |
| `bkg_roi` (one angle's entry, a list — never the per-angle list of lists) | 4 ints, 0 zeros → sorted; 4 ints, 2 zeros → peak-adjacent | `[]`, length ≠ 4 → `ValueError` | `None` → `ValueError` ("no background is set for this angle") |
| `bkg_roi` zeros | 1, 3 or 4 zeros → `ValueError` naming the sentinel | | |
| `max_events` | positive int | n/a | every event |

## 4. Files to change

| File | Change |
|---|---|
| (merge) | `git checkout -B feature/roi-popout-data --no-track agentic/exp-review`, then `git merge --no-ff agentic/feature/roi-estimate` — a regular merge, so PR #31's v1–v3 history and review trail stay reachable. Never squash, never copy the files in. |
| `scripts/test/roi_estimate_mutations.py` | `git mv` (own commit), then I5/I7, re-anchored rows for B7, new rows for §7. |
| `scripts/test/README.md` | one row: what the battery answers, who cites it. |
| `src/lr_reduction/roi_estimate.py` | I1, I3, B1–B9. |
| `tests/unit/lr_reduction/test_roi_estimate.py` | I1–I8 pins, §6 tests. |

## 5. Failure-mode matrix

| Case | Input | Must happen | Must not happen |
|---|---|---|---|
| common | a reflected-beam run, 10⁵–10⁷ events | images and profiles in well under a second after one read; XY equals the web report's | a second file read per redraw |
| common | `BkgROI` entry `[a, b, 0, 0]` from a template-derived file | bands `(a, y_min)`, `(y_max, b)` — what the reducer uses | drawing `(a, b)` as one band across the peak (R5 panel a) |
| edge | sparse run (~6 000 events; 6 of 63 fixtures) | images/profiles returned; `estimate_peak_range` refuses with its message | an estimate from noise; an exception from the image functions |
| edge | peak within `gap + width` of a detector edge | `default_bkg_roi` refuses | a band containing 0 — the reducer then returns `None` and the reduction dies with `TypeError` (F6) |
| edge | an event at exactly the largest TOF | counted | dropped (Mantid's half-open bin does; say so in the docstring) |
| edge | `max_events` smaller than the event count | stride sample; `stride > 1` reported | the first N events (a time slice of the run) |
| edge | run from a period with another detector shape | shapes follow the instrument database | 304/256 literals |
| pathological | event ids outside the detector | dropped and counted in `n_off_detector` | a reshape error, or strays binned into an edge pixel |
| pathological | zero events | all-zero arrays; `tof_edges` refuses | `min()` of an empty array escaping as a bare `ValueError` |
| pathological | `bkg_roi` with 1, 3 or 4 zeros, wrong length, `None`, a string | `ValueError` with the reason | `None` or a 2-element result handed to a caller that indexes `[3]` |
| pathological | reversed `x_range` / band | `ValueError` | an empty selection reported as "no counts" |
| pathological | file without `bank1_events` | h5py's `KeyError`, uncaught (the caller reports it) | a default image |

## 6. Red-Green TDD seed

Run under `pixi run python -m pytest tests/unit/lr_reduction/test_roi_estimate.py --timeout=120` while
developing; the gate is §8. RED first: each test below fails on the merged tree before the code exists
(`AttributeError` for a missing name is an acceptable RED only for the first test of each new function —
the others must fail on an assertion). Real-file tests take `nexus_dir` (`tests/conftest.py:46-49`);
presence/absence variants use the committed builder `_write_nexus`.

| # | Test | RED on the merged tree | GREEN when |
|---|---|---|---|
| T1 | `test_xy_image_is_what_the_web_report_plots` (201288; seed below) **and (v2) a second leg on `179932`**: the two arrays differ in exactly the pixels of the events at the run's min and max TOF (compute those pixels from the event arrays; assert the difference set equals them and the sums differ by their count) | no `xy_image` | F4's corrected statement holds on an agreeing and a differing run |
| T1b | **(v2)** over every fixture under `nexus_dir`: `xy_image` − the report's array is non-zero only at the extreme-TOF events' pixels, by at most the number of such events (the census that v1 lacked; skip the Mantid leg with a reason where Mantid is unavailable) | — | the population claim, not one sample |
| K1 | **(v2)** `background_bands` returns Python `int`s: `[type(v) for v in flat] == [int]*4` on the exhaustive small grid and the random cases | `astype(float).tolist()` passes `==` |
| K2 | **(v2)** every called-wrong refusal: `type(exc) is ValueError`; every nothing-to-offer: `isinstance(exc, CannotEstimateError)` | the subclass hides the swap |
| K3 | **(v2)** a builder file without `bank1_events` → `pytest.raises(KeyError)` from `load_event_pixels` | returning empties passes |
| K4 | **(v2)** `background_bands(None, …)` → `ValueError` matching "no background is set"; 1/3/4 zeros → matching "sentinel"; wrong length → "four" — each message its own match | matching "background" passes any refusal |
| K5 | **(v2)** one equal-bounds case per range kind (`x_range`, `y_range`, `tof_band`, the `y_tof_image` range): accepted, the one-pixel/bin selection counted | `high <= low` passes |
| K6 | **(v2, A1)** I8's subprocess asserts the child's `lr_reduction.roi_estimate.__file__` is under this checkout (`PYTHONPATH` from the module's path) | the editable install's tree passes from another checkout |
| K7 | **(v2, A4/numerical)** `default_bkg_roi((150, 150), …)` → four ints around a one-row peak; fractional `peak_range`/`gap`/`width` and `gap=True` → `ValueError` | truncation passes |
| T2 | `test_xy_image_puts_the_injected_peak_at_its_row_and_columns` (builder: peak row 150, x 100–159) | — | `image[150, 100:160].sum()` dominates; `image.shape == (n_y, n_x)` |
| T3 | `test_off_detector_ids_are_dropped_and_counted` (builder + three ids ≥ `n_x*n_y`) | — | `n_off_detector == 3`, `xy_image(...).sum() == n_events − 3` |
| T4 | `test_tof_edges_span_every_event_not_the_chopper_band` | — | an event outside `lambda_to_tof(chopper_lambda_range(...))` lies inside the edges and is counted in `y_tof_image` |
| T5 | `test_y_tof_image_counts_only_the_x_range` and `…_keeps_the_event_at_the_last_edge` | — | out-of-range X contributes 0; total equals in-range event count |
| T6 | `test_profile_y_agrees_with_the_library_histogrammer` (201288) | — | `allclose(profile_y(ev, (50, 200)) / charge, counts_vs_y(path, lowres=(50, 200)), rtol=1e-12)` |
| T7 | `test_profiles_are_marginals_of_the_images` | — | `profile_y == y_tof_image.sum(1)`; `profile_x(ev) == xy_image.sum(0)`; `profile_tof(ev, edges).sum() == len(ev.tof)` |
| T8 | `test_background_bands_are_the_rows_the_reducer_averages` / `…_refuses_what_the_reducer_cannot_use` (seed below) | no `background_bands` | equal to the sorter on accepted entries; `ValueError` on the six refused ones |
| T9 | `test_default_bkg_roi_survives_the_reducer` (sweep every peak position) | 2-tuple today | result has four ascending non-zero ints inside the detector, the sorter returns it unchanged, and it refuses where a side has no room |
| T10 | `test_a_sparse_real_run_gives_images_and_a_refused_estimate` (201284) | — | images non-zero; `estimate_peak_range(profile_y(...))` raises `CannotEstimateError` |
| T11 | `test_stride_sampling_is_not_a_time_slice` (builder with a peak only in the second half of the event list) | — | the peak is present at `max_events = n // 4`; `stride == 4` |
| T12 | `test_an_empty_run_gives_zero_images_and_refuses_edges` | — | per §3 states table |
| T13 | I1–I8 pins as named in §3 | per item | per item |

```python
import os

import numpy as np
import pytest
from mantid.simpleapi import Integration, LoadEventNexus

from lr_reduction import roi_estimate
from lr_reduction.nr_reduction_calc import NR_Reduction

ACCEPTED = [[133, 149, 0, 0], [120, 130, 150, 160], [160, 150, 130, 120]]
REFUSED = [[0, 10, 150, 160], [0, 0, 0, 0], [121, 130], [133, 149, 0], [], None]


def test_xy_image_is_what_the_web_report_plots(nexus_dir):
    path = os.path.join(nexus_dir, "REF_L_201288.nxs.h5")
    events = roi_estimate.load_event_pixels(path)
    workspace = LoadEventNexus(Filename=path, OutputWorkspace="xy_cross_check")
    signal = Integration(InputWorkspace=workspace, OutputWorkspace="xy_cross_check_sum").extractY()
    expected = np.reshape(signal, (events.n_x, events.n_y)).T
    assert np.array_equal(roi_estimate.xy_image(events), expected)


@pytest.mark.parametrize("bkg", ACCEPTED)
def test_background_bands_are_the_rows_the_reducer_averages(bkg):
    expected = [int(v) for v in NR_Reduction._background_roi_sorter(None, bkg, 136, 146)]
    (b0, b1), (b2, b3) = roi_estimate.background_bands(bkg, 136, 146)
    assert [b0, b1, b2, b3] == expected


@pytest.mark.parametrize("bkg", REFUSED)
def test_background_bands_refuses_what_the_reducer_cannot_use(bkg):
    with pytest.raises(ValueError, match="background"):
        roi_estimate.background_bands(bkg, 136, 146)
```

## 7. Mutate-once gate (record each in the commit body as `<mutation> → <test> -> N failed`)

| # | Mutation applied to `roi_estimate.py` | Must red |
|---|---|---|
| M1 | `xy_image` reshapes as `(n_y, n_x)` without the transpose | T1, T2 |
| M1b | **(v2)** `xy_image` drops the extreme-TOF events to "match" the report | T1 (201288 unchanged; 179932's difference set empty → red), T1b |
| K1m | **(v2)** `ordered.tolist()` → `ordered.astype(float).tolist()` | K1 |
| K2m | **(v2)** a called-wrong site raises `CannotEstimateError` | K2 |
| K3m | **(v2)** missing group → empty arrays | K3 |
| K4m | **(v2)** the `None` guard deleted (the `ndim` refusal fires with the wrong reason) | K4 |
| K5m | **(v2)** `high < low` → `high <= low` | K5 |
| K7m | **(v2)** `int()` truncation of a fractional `gap` | K7 |
| M2 | the off-detector filter removed | T3 |
| M3 | `tof_edges` built over the chopper band instead of the event span | T4 |
| M4 | `y_tof_image` ignores `x_range` | T5, T7 |
| M5 | the last TOF bin made half-open | T5 (`…last_edge`), T7 |
| M6 | `y = id // n_y`, `x = id % n_y` (packing swapped) | T2, T6 |
| M7 | `background_bands` returns the entry sorted, without substituting the peak for the two zeros | T8 (`[133,149,0,0]`) |
| M8 | `background_bands`' zero-count refusal → `if False:` | T8 refused legs |
| M9 | `default_bkg_roi` clamps to 0 instead of refusing | T9 |
| M10 | `default_bkg_roi` returns only the low-side band | T9 |
| M11 | stride sampling → head slice `[:max_events]` | T11 |
| M12 | `counts_vs_y` default `lowres` → the literal `(0, 255)` | I1's provenance pin |
| M13 | the `tof_band` selection in `counts_vs_y` → `if False:` | I2's pin |
| M14 | `import qtpy` added at module top | I8's pin |
| M15 | `tof_edges`' no-events refusal removed | T12 |

**Frame** (helpers introduced or re-pointed — one row per call site): `load_event_pixels` changes its
return (no caller at `655a67d`; its first callers are this slug's tests — state that in the commit
body); `default_bkg_roi` changes its return — call sites are the existing tests
(`test_default_bkg_roi_*`, four functions) and battery rows 9 and 14, which are re-anchored, not deleted;
`counts_vs_y`'s single `get_y_tof` call site (I3) keeps `test_counts_vs_y_goes_through_the_library_histogrammer`
green and gains the call-count assertion. The committed battery carries M1–M15 beside its existing rows
and is chunked under the 600 s harness ceiling (`--timeout` per invocation is already in it). A mutation
that stays green is diagnosed before anything else is touched.

## 8. Acceptance criteria

1. `pixi run test-reduction` returns zero **from the repository root, as written** (it runs
   `test-launcher` first, then `cd tests/`); `pixi.lock` restored, not staged.
2. `git diff --stat agentic/exp-review...feature/roi-popout-data` lists exactly the four files of §4 (the
   module, its test, the battery, the README). No `plans/`, no `todo.md`, no other ledger-shaped path;
   no existing `src/` or `launcher/` file.
3. Every row of §7 is in a commit body with its observed `<test> -> N failed`; the battery run prints
   `restored: OK`, zero `ANCHOR MISS`, and `git status --porcelain` is empty afterwards.
4. Prescriptive claims are checked or marked inferred: "equals the web report" (T1 is the falsifier);
   "never contains 0" (T9's sweep); "one read of the file" (a spy on `h5py.File` in a test, or marked
   inferred); F12's 3.12 statement stays marked inferred unless run on 3.12.
5. Numerical-diagnostics review receives F4, F6, F7 and F8 as its starting evidence and audits B6 against
   `_background_roi_sorter` point-wise (not by aggregate).
6. PR body: supersedes #31 (names it; an agent does not close it); the seven advisories with their
   closing commits; the deploy consequence — **import-only: nothing on the autoreduce path imports the
   module, so merging changes package contents, not reduction output**; draft, the merge is the human's.
7. No deployment-shaped acceptance for this slug (no operator-facing surface); the Integrator's
   analysis-node run belongs to `roi-popout-dialog`.

## 9. Learnings relied on (quoted; source `agentic/analysis/exp-settings-roi:plans/roi-estimate-learning.md`)

- L1 (§1): "When you write a synthetic input file for a module that parses a real one, derive every field
  from the code that reads the real file — not from the plan's description of it." → T1/T6 run on real
  files; the builder stays for presence/absence.
- L2 (§2): "After writing a score that separates 'signal' from 'nothing', evaluate it on the degenerate
  input by hand." → §3 states table; T10, T12.
- L3 (§3): "A guard against hard-coding cannot be an equality check when the configured value currently
  equals the literal. Assert that the answer *follows the source*." → I1, M12.
- L4 (§4, corrected): "before concluding a guard is unreachable, state the precondition that makes it so
  and check that something enforces it." → B7 validates the peak before computing bands.
- L5 (`plans/scaling-factor-path-anchor-learning.md` §1 and `roi-estimate-learning.md` §6, same ref): "A
  gate command that changes directory hides every cwd-dependent defect behind it"; "Verify with the gate
  command, not with an approximation of it." → the battery path stays anchored to `__file__`
  (`test_roi_estimate.py:464-471` @ `655a67d`); §8.1 is the literal command.

## 10. Assumptions and open questions (the plan proceeds under each default)

| # | Question | Owner | Default |
|---|---|---|---|
| A1 | This slug touches no editor file. Dispatch it in parallel with the editor lane instead of after `editor-sections`? | Analyst | keep the charter's order; the plan is valid at any base that lacks `roi_estimate.py` |
| A2 | Extract `_background_roi_sorter` into a module-level function the reducer and `roi_estimate` share (cannot drift; makes this a reduction-path slug with the baseline/`check_headers.py` duty), or mirror it under a contents-equality pin (T8)? | Analyst / human | **mirror + pin** here; the extraction belongs with the reducer fix for F6 (pixel 0, `None` return), which needs its own slug |
| A3 | `default_bkg_roi` gap and width: PR #31 has 5/10 (one side); #197, which the scientists reviewed, has 3/5 either side. | scientists | **3 / 5 either side** (#197's), stated in the docstring as the reviewed value |
| A4 | Which estimator is the library's — PR #31's (refuses 6 of 63 fixtures) or #197's (wing-median background, never refuses)? | scientists + numerical review | PR #31's, unchanged; F8's refusal list goes into the PR body for the scientists |
| A5 | F7: are the peak-edge rows meant to be background in the adjacent form? | scientists | not touched; ledger todo |
| A6 | Battery location `scripts/test/` (exists) vs `scripts/tests/` (the contract's spelling). | Analyst | `scripts/test/` |
| A7 | `RunEvents` as a frozen dataclass vs a dict (PR #31 returns dicts for metadata). | Developer | dataclass — it is never merged into a settings dict |

## Revision history

v1 — authored 2026-10-02 against `7b6d6b9` + PR #31 @ `655a67d` (staged behind `editor-sections` by the charter's lane order);
**re-sealed and dispatched 2026-10-05 against `exp-review` @ `5a8742d`** under the stacking-by-file-overlap rule (posture `ec10742`; no
overlap → cut from `exp-review`; A-66): every cited library file blob-identical, F1 re-run clean, F12's test citation moved to `:697-703`.
Developer: PR #31 merged in regularly (`c7408cf`), battery `git mv`'d, RED/GREEN, 15-row battery (D-50). **Rejected** at `review/roi-popout-
data` @ `b4cda54` (the Integrator's `todo.md`).

### v2 — 2026-10-05 (attempt 2 of 3; the work order for `triage/roi-popout-data-v2`)

**Rejection.** `review/roi-popout-data` @ `b4cda54` — `todo.md` at that commit (Integrator, Claude Opus 5.5): *"Verdict: REJECT — the numbers are
right; one declared equality is false and five declared behaviours have no test that can fail. No module arithmetic needs to change. Not
stacked (base `exp-review` @ 5a8742d + PR #31's `feature/roi-estimate` @ 655a67d). Not infrastructure."* What passed (**the Developer does not
redo it**): gate 558 + 792; scope exactly the four files, `9bc0049` R100; **numerical, point-wise:** B6 vs the reducer's sorter 754 784 cases, 0
mismatches, the real `background_subtract` 3 000/3 000; B7 231 800 cases; B4 exactly the last-edge event on all 8 runs; B5 ≤ 3.0e-16; B1
bit-equal packing; the 49-row battery verbatim; I1–I3, I5–I7, B1, B3, B4, B7, B8 pinned.

> **BLOCKING — N-1: "the web report's XY array, cell for cell" is false on most real runs (rule d).** `roi_estimate.py` (`xy_image` docstring,
> ~:245) and plan B2/F4. Reproduced (`web_report.py:579-583`'s exact `Integration` of `LoadEventNexus`, vs `xy_image(load_event_pixels(f))`):
> `201288` equal; **`179932` 2 cells differ** — (72, 14), (191, 217), sums 300 088 vs 300 086; **`201282` 1 cell** — (216, 202), 6 050 vs
> 6 049. 45 of the 63 fixture runs and the IPTS spot check `REF_L_235251` differ, by 1–2 counts in 1–2 cells; the missing events are always
> the run's minimum- and/or maximum-TOF event, which Mantid's default `Integration` range (min/max TOF, apparently rounded) excludes. T1
> tests only `201288`, one of the 18 agreeing runs. The module's arrays are correct; the claim is not. **Fix (wording + test):** restate
> B2/F4 (docstring, plan, PR body) as the F4 Y-TOF note already is — equal except the event(s) at the run's extreme TOFs — and add a T1
> leg on `179932` asserting the difference is exactly those events' pixels.
>
> **BLOCKING — T-1…T-5: declared behaviours with no test that can fail (rule a; K1 and K4 also rule d).** K1 — B6 "values and types":
> `ordered.astype(float).tolist()` survives (`136 == 136.0`). K2 — B9's `ValueError`-vs-`CannotEstimateError` split: the subclass hides a
> swap under `pytest.raises(ValueError)`. K3 — "no `bank1_events` → h5py `KeyError`, uncaught": returning empties survives. K4 — `bkg_roi
> is None` → "no background is set": the guard deleted survives (the `ndim` refusal fires with the wrong reason; the test matches only
> "background"). K5 — ranges accept `low == high`: `high <= low` survives (a one-pixel range, 1 174 counts today, would become a
> `ValueError`). **Fixes:** compare types; `type(exc) is ValueError`; a builder file without the group; match the specific reason; one
> equal-bounds case per range kind.

**What the plan missed (the Analyst's defects).** F4 generalised an equality from **one** run (`201288`) to the population — the same class as
A-49's census lesson, now in a numerical claim; the plan's own Y-TOF note had the right shape ("differs in one cell: the last-edge event")
and B2 did not get it. And five declared cells (types, the error-class split, the uncaught `KeyError`, the `None` reason, the equal-bounds
range) were written as behaviours without naming a test that observes through the path their faithful mutant breaks — §7 had no row for
any of them. **Changes in v2:** F4/B2 restated (equal except the extreme-TOF events' pixels; said in docstring, plan and PR body); T1's
`179932` leg + **T1b** the census over every fixture; K1–K7 (K6/K7 adopt test A1 and the numerical `default_bkg_roi` advisory with A4); B6/B9's
types and error classes made precise; the empty-run cell asserted on values (A5); the mutation rows K1m–K7m and M1b. Advisories not adopted
(PR body): `tof_edges` 335 vs the report's 334 edges (nothing claims equality — stated); `background_bands` refusing >4 entries
(conservative, said); A2, A6, A7 ("well under a second" marked inferred), A8. **Unchanged:** I1–I8, B1, B3–B5, B8, every v1 test and
mutation, the base (`exp-review` @ `5a8742d` + `655a67d` — re-checked: `exp-review` has since moved to `b6b9381` by #40, touching no file of
this slug; the Developer continues on `feature/roi-popout-data` from `b4cda54` and may merge `agentic/exp-review` forward before `qa/`, a
regular merge). **Retry arithmetic:** attempts_done = 1 + 1 = 2 → v2 is attempt 2 of 3; a third rejection escalates.
