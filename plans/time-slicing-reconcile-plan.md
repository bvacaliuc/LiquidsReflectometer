# Plan: `time-slicing-reconcile` — intake of upstream `add-time-slicing` (PR #205) at `8eead58`: the snapshot merged onto the campaign's reduction stack, its intent pinned by tests first, every conflict hunk justified, the tab brought to the launcher's conventions

**Campaign:** `exp-review-fixes` · **Leaf:** `time-slicing-reconcile` (refs `triage/time-slicing-reconcile`, `feature/time-slicing-reconcile`,
`qa/time-slicing-reconcile`; the snapshot `contrib/add-time-slicing@8eead58`) · **Status:** READY — v1 (attempt 1 of N = 3) — **DISPATCHED 2026-10-07 (A-101)** on the posture line **"Upstream intake — take add-time-slicing @ 8eead58"** (in force at charter `f60e7bf`, RULES_ADVANCED M-54; prepared the wake before on the human's couriered line, `requests/time-slicing-take-line.md`, M-52). **Snapshot ref pushed:** `contrib/add-time-slicing@8eead58` on the subject's `agentic` (= `8eead58`; immutable — a later upstream commit is a new intake). Tips re-measured at dispatch and **unmoved** since §2: `exp-review` `c39efe9`, the stack tip `ae5ce0e`, #42 `aeba172` — F2/F3 stand · **Base:** `agentic/feature/header-scale-factors-per-position` @ `ae5ce0e`
(the reduction stack's tip: #34 → #46; **stacked under clause (4)**, overlap census at `exp-review` @ `c39efe9`, tests excluded, 2026-10-07: the
contribution's 11 files ∩ #34 `rereduction-headers-land` = ∩ #46 `header-scale-factors-per-position` = {`nr_reduction_calc.py`,
`save_reduced_data.py`, `new_reduction_from_file.py`} — the larger overlap; ∩ #42 `launcher-env-outside-xdg-cache` = {`launcher/new_launcher.py`}
— **merged forward at cut** (`agentic/feature/launcher-env-outside-xdg-cache` @ `aeba172`) and before every `qa/`; ∩ #43/#45/#44/#47 = ∅) ·
**PR target:** `feature/header-scale-factors-per-position` on the fork, **draft** (the Integrator names the stack #34 → #46 → this slug and the
merged-forward #42; **clause (3a)** if #46's tip is an ancestor of `exp-review` at open time → `--base exp-review`) · **Depends on:** nothing
building; the snapshot ref pushed by the Analyst at dispatch (intake step 1) · **Review domains:** numerical-diagnostics, test (block); ui-aspects
(advise) — charter §3 · **Kind:** **reduction-path** (`binary_processing.py`, `nr_reduction_calc.py`, `save_reduced_data.py`,
`new_reduction_from_file.py`, `nr_reduction_config.py`) + launcher (`time_resolved.py`, `new_launcher.py`) + library (`new_reduction_time_resolved.py`,
`direct_beam_maker.py`) · **Sources:** `[human, 2026-10-07: "take add-time-slicing @ 8eead58 (upstream PR #205; plans/upstream-add-time-slicing-plan.md).
Dispatch time-slicing-reconcile now. noqa-sweep waits until time-slicing-reconcile's draft PR is open, whatever the stacking count says"]`;
charter §3 row `time-slicing-reconcile`; the intake procedure `plans/upstream-add-time-slicing-plan.md` (V1-10, V1-38 §, V1-39 §5).

Canonical copy: ledger `plans/time-slicing-reconcile-plan.md`; the copy on `triage/time-slicing-reconcile` is byte-identical at dispatch.

## Declared scope

**Input:** the snapshot `contrib/add-time-slicing@8eead58` — upstream `neutrons/LiquidsReflectometer` branch `add-time-slicing`, 7 commits
(author welbournR), 11 files, +768/−43 against its fork point `f98ec6c` (`git diff --stat f98ec6c 8eead58`, measured 2026-10-07 — the figures of
V1-10 hold; the branch has not moved since 2026-10-01). **The snapshot is immutable**: a later upstream commit is a new intake, never an update.

**Files in** (§4): the contribution's 11 — new `src/lr_reduction/new_reduction_time_resolved.py`, new `launcher/apps/time_resolved.py`, new
`src/lr_reduction/example_time_slices.py`; edited `binary_processing.py`, `nr_reduction_calc.py`, `nr_reduction_config.py`, `save_reduced_data.py`,
`new_reduction_from_file.py`, `direct_beam_maker.py`, `example_direct_beam.py`, `launcher/new_launcher.py` — plus the tests this plan adds
(`tests/unit/lr_reduction/test_time_slicing.py` new; `test_direct_beam_maker.py` or its nearest existing file; `launcher/tests/test_time_resolved.py`
new) and a `check_headers.py`-style invariant for time-sliced outputs.

**Behaviours in** (§3): T1–T9 — event-window selection on pulse time, the slice bookkeeping (`reduce_time_slices`, `reduce_time_list`), the
`start_times`/`end_times` plumbing through `reduce_from_file` → `reduce` → `_reduce_single_run` → `convert_to_binary`, the header line, the Cd
override in the direct-beam maker, the tab.

**Explicitly OUT** (a finding here is a PR-body advisory or a filed todo, not a rejection): choosing which parts of the contribution to keep (the
human's — "take it, at this SHA" takes all of it); rebasing or altering the upstream branch; `reduce_time_log_filter` (a commented-out TODO in the
snapshot — stays commented, recorded as such); the physics of a slice (stubbed, as M1 did — grouping, bookkeeping and header writing real);
`plot_kinetic`'s appearance beyond "draws without error and returns the figure(s)"; the hard-coded `/SNS/REF_L/<ipts>/nexus` and `shared/reduced`
defaults in `reduce_time_slices`/`reduce_time_list` **are in** only to the extent of F9 (use `config.NEXUSpathRB`-style resolution) — the time-indexed
dataset-path lookup is `todo-nexus-event-paths-time-indexed` (next campaign); `nr_tools.py`/`web_report.py` (the two-dot artefacts, not the PR's).

## 1. Request and requirements trace

| # | The human's / the intake's sentence | Design answer | Tension / gap |
|---|---|---|---|
| S1 | "take add-time-slicing @ 8eead58 … Dispatch time-slicing-reconcile now" | the snapshot ref, this plan, the dispatch on the posture line | the plan's gate is the posture line (the intake procedure's own words; the governance MR carries it) — prepared now, cut then |
| S2 | intake step 2: "Characterize before merging … intended behaviour (reverse-requirements …), the trial-merge conflict set, the conventions it misses, its deploy consequence" | §2 F1–F9, §3 T1–T9, §5 | the PR body is the empty template — intent is read from code and the commit titles |
| S3 | intake step 3: "RED first, against the contribution's intent … stub the physics; keep slicing bookkeeping, config fields and header writing real" | §6 RED on the base (behaviour absent) | — |
| S4 | intake step 4: "resolve each conflict hunk with a justification in the commit body … mutate-once on each guard. Conventions pass as separate commits" | §7, §8.3, §8.5 | — |
| S5 | charter §3: "numerical-diagnostics, test (block); ui-aspects (advise)" | the event-window arithmetic is the numerical surface (T1–T3); the tab is advisory | — |
| S6 | "noqa-sweep waits until time-slicing-reconcile's draft PR is open" | the sweep's trigger re-written (A-86 → this line) in `dispatch-queue.md` at dispatch | — |

## 2. Verified facts (measured 2026-10-07 on uvdl3 against the snapshot `8eead58`, `exp-review` @ `c39efe9`, the stack tip `ae5ce0e`; re-measure at dispatch — the stack tip may move)

| # | Fact | Command → observation |
|---|---|---|
| F1 | The snapshot and its size. | `git fetch upstream add-time-slicing`; `git log -1 8eead58` → 2026-10-01 "fixing missing parameter in config from time resolved"; `git diff --stat f98ec6c 8eead58` → 11 files, +768/−43 (V1-10's corrected figure). `git merge-base 8eead58 agentic/exp-review` = `f98ec6c`. |
| F2 | Conflicts against `exp-review` @ `c39efe9`: **4 hunks in 3 files** — `binary_processing.py` (1), `direct_beam_maker.py` (2), `nr_reduction_calc.py` (1). | scratch-worktree `git merge --no-commit 8eead58` → `--diff-filter=U`; `grep -c '^<<<<<<<'` per file. Same as V1-10 (2026-10-02). |
| F3 | Conflicts against the **stack tip** `ae5ce0e` (#46, containing #34): **6 hunks in 4 files** — the three above plus `save_reduced_data.py` (2): the campaign's `{marker}` header line (M1/M2's format-3 marker) vs the contribution's `Time resolved: {start_times}, {end_times}` line, twice (the two writers). | same procedure on `agentic/feature/header-scale-factors-per-position`. The `nr_reduction_calc.py` hunk is `_reduce_single_run(self, i, rb_num, save=True)  # noqa: ARG002` (campaign) vs `(…, save=True, start_times=None, end_times=None)` (contribution) — a signature union, not a logic clash. |
| F4 | **The event-window arithmetic** (`binary_processing.py:98-149` at the snapshot, `event_time_filter`). Inputs: `event_time` (pulse times, `entry/bank1_events/event_time_zero`), `event_index` (first event of each pulse), per-window `[start, end)`; it uses `np.searchsorted(event_time, start, side="right")`, then `event_index[idx] - 1` for a non-zero start and `event_index[idx]` for `start == 0`, `event_index[stop_idx] - 1` for the end, and on `IndexError` at the end `event_index[-1] - 2`. The code says so itself: `# TODO: need to check on +/- values`, `# write some proper tests to check aren't losing single events on edges or duplicating them`, `# ok to lose 1 event at this stage`. **Consequence:** contiguous slices need not partition the run (events at window edges can be lost or duplicated), the proton charge is sliced on `event_time` indices (`cPC[start_idx:stop_idx]`) with a different convention from the events, and the last slice drops events. **T1–T3 pin the semantics; the conflict-resolution commit fixes the arithmetic to meet them** (this is behaviour the contribution *intends* — "splitting into time slices" — and does not yet achieve). |
| F5 | The plumbing: `reduce_from_file(…, start_times=None, end_times=None)` → `reducer.reduce(…, start_times, end_times)` → `self.config.start_times/end_times = …` (written onto the config **during** `reduce`) → `_reduce_single_run(i, rb_num, save, start_times, end_times)` → `_load_and_extract_lambda` → `_make_binary_files` → `convert_to_binary(…, start_times, end_times)` → `load_and_extract(fname, start_times, end_times)`; `nr_reduction_config.py` gains `self.start_times = None`, `self.end_times = None`; `save_reduced_data.py` writes `Time resolved: …` in both writers. | `git diff f98ec6c 8eead58 -- src/lr_reduction/{nr_reduction_calc,nr_reduction_config,save_reduced_data,new_reduction_from_file}.py`. Note the `config` write inside `reduce` — the campaign's R4 (`header-scale-factors-per-position`) established "no write into `config.ScaleFactor` in `reduce()`"; the same discipline applies: the header must carry the window without `reduce()` mutating the shared config (T6). |
| F6 | `new_reduction_time_resolved.py` (231 lines): `reduce_time_slices(run, settings_file, experiment_id, num_slices, savepath=None, plot_time=True, plot_ref=False, subname_input=None, show_plots=…)` — opens `/SNS/REF_L/<experiment_id>/nexus/REF_L_<run>.nxs.h5` with `h5py` (never closed), reads `entry/duration`, builds equal windows, calls `reduce_time_list` per window with `subname=f"slice_{i+1}of{n}"`; `reduce_time_list(run, settings_file, experiment_id, starts, ends, …)` — `len(starts) != len(ends)` → `ValueError`; default `Spath = /SNS/REF_L/<ipts>/shared/reduced`; per window `reduce_from_file(run_list, settings_file, experiment_id, override_params={'Spath', 'subname'}, plot=plot_ref, save_json=False, start_times=starts[i], end_times=ends[i])`; `flatten_reduced_results` (dict / list / nested → flat list); empty → `ValueError`; `plot_kinetic(output_list, run, times, show)` (offset plot + colour map; `plt` in library code); `reduce_time_log_filter` is a **commented-out** TODO. `print()` progress throughout. | `git show 8eead58:src/lr_reduction/new_reduction_time_resolved.py`. |
| F7 | `direct_beam_maker.py` (+36/−8): `create_db(…, cd_list=None)` — a provided `cd_list` **overwrites** `log_values['Atten']` per run ("short-term fix"), runs pre-sorted by Cd thickness increasing; `print()`s added. Conflicts with the campaign's `for run in run_list:` loop (2 hunks: the loop head/body, and a blank-line hunk). | `git diff f98ec6c 8eead58 -- src/lr_reduction/direct_beam_maker.py`; F3's hunk text. |
| F8 | `launcher/apps/time_resolved.py` (294 lines, `TimeResolvedTab(QWidget)`): `QMessageBox.warning/information/critical` ×8 (missing run, bad run number, missing experiment, missing settings, missing/mismatched time lists, completed, failed), `except Exception:` ×3 (`:25`, `:29` at import, `:146` in `read_settings`) and `except Exception as exc:  # pragma: no cover` (`:289`), `QFileDialog` ×3, `_parse_float_list`, `_run_reduction` calls `reduce_time_slices`/`reduce_time_list` **synchronously on the GUI thread**; `new_launcher.py` registers the tab (+7). Conventions the launcher enforces that it misses: `no_qmessagebox` (report in-panel, `@guarded`), no swallowed exceptions, logging not `print`, no blocking reduction on the GUI thread without at least a disabled button + status (the campaign's editor slots are the pattern). | `git show 8eead58:launcher/apps/time_resolved.py`; `grep -n QMessageBox\|except` → lines above. |
| F9 | The campaign's name for a run's file: `nr_reduction_calc.py` `self.config.NEXUSpathRB / f"REF_L_{rb_num}.nxs.h5"`; `nr_reduction_config.py` (override, else `<IPTS>/nexus`). The contribution hard-codes `/SNS/REF_L/<ipts>/nexus` in `reduce_time_slices` — the third spelling (`todo-roi-popout-data-followups-from-dialog-gate` D3 counts the others). | `roi-popout-dialog-plan.md` F9; `new_reduction_time_resolved.py:19-20`. |
| F10 | Environment and harness. | `pixi run test-reduction` (launcher first); `launcher/tests/conftest.py` `isolated_qapp`, `no_qmessagebox` (autouse: `QDialog.exec_` → Accepted; a `QMessageBox` in a test is a failure), `no_qfiledialog`; reduction tests `tests/unit/lr_reduction/`; the `_write_nexus` builder (`tests/unit/lr_reduction/test_roi_estimate.py`) writes `bank1_events` with `event_time_zero`/`event_index` — reusable for T1–T3 fixtures (**verify at dispatch that it writes `event_index` and `bank_error_events`; extend it if not — the extension is this slug's**). |

## 3. Design — behaviours, not code (the contribution's intent, made testable)

| # | Behaviour |
|---|---|
| T1 | **Window selection is on pulse time, half-open:** for a window `[start, end)` (seconds from the run's first pulse, the unit of `event_time_zero`), the events selected are exactly those whose pulse time `t` satisfies `start ≤ t < end`; the error events and the proton-charge pulses are selected by the **same** predicate. `start = 0` is not special. |
| T2 | **Contiguous windows partition the run:** for windows `[0,a), [a,b), …, [z, duration]` the selected event sets are disjoint and their union is every event of the run (the last window is closed at the run's end: `end ≥ last pulse time` selects through the last pulse). No event is lost at an edge, none duplicated. The summed proton charge of the slices equals the run's. |
| T3 | **Several windows in one call concatenate** in the order given; windows may be disjoint or (if the caller wishes) overlapping — the result is the concatenation, nothing deduplicated (the contribution's semantics; documented, not silently changed). |
| T4 | **Invalid windows raise before any reading beyond the file header:** one of `start_times`/`end_times` `None` and the other not; unequal lengths; `start >= end`; a non-list scalar is accepted as a one-window list (the contribution's `isinstance(list)` wrap). A window entirely after the last pulse selects nothing and the reduction of that slice is reported, not a crash (`reduce_time_list` raises `ValueError("No reduced result data …")` — kept, with the window in the message). |
| T5 | **`reduce_time_slices(num_slices=n)`** makes `n` equal windows over `entry/duration`, names them `slice_{i+1}of{n}` (or `<subname>_slice_…`), reduces each through `reduce_time_list`, and returns `(all_outputs, plots)` with one flat result pack per slice and mid-point times; **`reduce_time_list`** returns per-window packs in input order. The run's file is resolved the campaign's way (F9: `NEXUSpathRB`-style from the settings/config), **not** a hard-coded `/SNS/REF_L/<ipts>/nexus`; `savepath` defaults likewise through the config, not a literal. The `h5py.File` is closed (context manager). |
| T6 | **The header carries the window; `reduce()` does not mutate the shared config.** Each slice's output header has one line naming its window (`Time resolved: [start], [end]` — the contribution's text, kept) **beside** the campaign's format-3 marker line (both writers); a run reduced without windows writes no `Time resolved` line (or `None, None` — decide one; §10 A3). `config.start_times/end_times` are set on the per-call config object the reducer already copies (M2's R4/R5 discipline), never on the caller's. |
| T7 | **Direct-beam Cd override:** `create_db(…, cd_list=[…])` uses the given thicknesses in run order (overriding `Atten` from the logs), sorts the runs by Cd increasing, and says so in the log (not `print`); with `cd_list=None` the behaviour is byte-for-byte the campaign's. `len(cd_list) != len(run_list)` → `ValueError`. |
| T8 | **The tab** (`TimeResolvedTab`): reports every validation failure and every reduction error **in-panel** (a status label / `report_problem`-style), never a `QMessageBox`; no `except Exception` swallow — the `@guarded`-style slot reports; the Run button is disabled while a reduction runs and the status says so (synchronous is acceptable for v1 if the plan's §10 A4 default stands); `read_settings`/`save_settings` round-trip through QSettings; the tab is registered in `new_launcher.py` after the existing tabs. |
| T9 | **No `print()` in library code** — `logging` at INFO for progress (`new_reduction_time_resolved.py`, `binary_processing.py`'s `'Processing with time filter.'`, `direct_beam_maker.py`); `plot_kinetic` draws on a figure it returns and never calls `plt.show()` unless `show=True` (the contribution's flag, kept). |

**Types and states each path acts on.** (Every cell names its test — the lesson of `roi-popout-dialog` L7/L10.)

| Value | present | empty / degenerate | `None` |
|---|---|---|---|
| `start_times`, `end_times` (per call) | lists of equal length → windows in order (T1, T3: `test_windows_select_by_pulse_time`, `test_several_windows_concatenate`) | `[]` and `[]` → no filter? **decide: `[]`/`[]` → `ValueError` (a window list with no windows is a mistake), §10 A1** (T4: `test_invalid_windows_raise_before_reading_events`) | both `None` → the whole run, byte-identical to today (T1: `test_no_windows_is_the_whole_run`); one `None` → `ValueError` (T4) |
| a single window given as scalars | wrapped to one-element lists (T4: `…_scalars_are_one_window`) | `start == end` → `ValueError` (T4) | — |
| window vs the run | inside → its events (T1); contiguous set → partition (T2: `test_contiguous_slices_partition_the_run`, incl. proton charge) | after the last pulse → empty selection; the slice reports "no result" (T4: `test_a_window_after_the_run_reports_not_crashes`) | — |
| `num_slices` | `n ≥ 1` → `n` windows over `duration` (T5: `test_reduce_time_slices_makes_equal_windows_named_i_of_n`) | `0` or negative → `ValueError` (T5) | — |
| `cd_list` | same length as `run_list` → overrides `Atten`, runs sorted by Cd (T7: `test_cd_list_overrides_the_log_and_sorts_runs`) | wrong length → `ValueError` (T7) | logs' `Atten`, unchanged behaviour (T7: `test_without_cd_list_the_log_values_stand`) |
| header | windowed run → `Time resolved: …` + marker (T6: `test_the_header_names_the_window_beside_the_marker`) | — | no window → the chosen form (T6, §10 A3) |
| the tab's inputs | valid → the reduction runs, the panel reports completion (T8: `test_run_reports_completion_in_panel`) | missing run / bad int / missing settings / mismatched lists → panel message, no box (T8: `test_every_validation_failure_is_a_panel_message`) | — |

## 4. Files to change

| File | Change |
|---|---|
| `src/lr_reduction/binary_processing.py` | the contribution's `convert_to_binary`/`load_and_extract` signatures and `event_time_filter`, **with the arithmetic made to meet T1–T3** (select by `start ≤ t < end` on pulse times via `searchsorted(…, side="left")` for the start and `side="left"` for the end, events via `event_index[idx]` without the `−1`/`−2` fudges; the last pulse included when `end ≥` its time); conflict hunk vs the campaign's signature resolved as the union; `print` → `logging` |
| `src/lr_reduction/nr_reduction_calc.py` | the `start_times`/`end_times` plumbing; the conflict hunk (`# noqa: ARG002` + the new parameters — union); T6's "no shared-config write" |
| `src/lr_reduction/nr_reduction_config.py` | `start_times`, `end_times` defaults `None` |
| `src/lr_reduction/save_reduced_data.py` | the `Time resolved:` line **beside** `{marker}` in both writers (the two conflict hunks on the stack base) |
| `src/lr_reduction/new_reduction_from_file.py` | the pass-through parameters |
| `src/lr_reduction/new_reduction_time_resolved.py` | new (the contribution) — F9 path resolution, the file closed, `logging`, `plot_kinetic` returns figures |
| `src/lr_reduction/direct_beam_maker.py` | the `cd_list` override (T7), the two hunks resolved, `print` → `logging` |
| `src/lr_reduction/example_time_slices.py`, `example_direct_beam.py` | the contribution's examples, paths not hard-coded to one IPTS (or left as examples with a comment — §10 A5) |
| `launcher/apps/time_resolved.py` | new (the contribution) — T8 conventions |
| `launcher/new_launcher.py` | the tab registration (the contribution's +7; #42's edit merged forward) |
| `tests/unit/lr_reduction/test_time_slicing.py` | new: T1–T6 (RED on the base) |
| `tests/unit/lr_reduction/test_direct_beam_maker.py` (or nearest) | T7 |
| `launcher/tests/test_time_resolved.py` | new: T8 |
| `tests/.../check_headers`-style invariant | every time-sliced output's header has exactly one `Time resolved:` line and the marker (T6) |

## 5. Failure-mode matrix

| Case | Situation | Must happen | Must not happen |
|---|---|---|---|
| common | 4 equal slices of a 1 h run | 4 outputs named `slice_1of4…4of4`, headers with the window, charges summing to the run's | an event in two slices; one lost at a boundary |
| common | one window `[600, 1200)` | that window's events; the rest untouched | the proton charge sliced on a different convention |
| common | no windows (today's call) | byte-identical results and headers to the base (the Integrator's baseline) | a `Time resolved: None, None` line appearing where none was (unless §10 A3 chooses it — then everywhere, consistently) |
| edge | `end` beyond the run | selects through the last pulse (T2's closed end) | `IndexError` → the `−2` fudge |
| edge | `start == 0` | treated like any start (T1) | the special-case branch |
| edge | windows given as scalars | one window | `TypeError` on `len()` |
| edge | `cd_list` provided | overrides, sorted, logged | the log's `Atten` silently used |
| pathological | `start_times` given, `end_times` `None` | `ValueError` before events are read | a half-filtered run |
| pathological | a slice with no events (window after the run) | reported per slice, the others reduced | the whole call aborting with a traceback |
| pathological | the tab's inputs wrong | panel message | `QMessageBox` (the `no_qmessagebox` fixture fails the test) |
| pathological | the reduction raises inside the tab | panel message with the error, button re-enabled | `except Exception` swallow; a frozen tab |

## 6. Red-Green TDD seed

Cut `feature/time-slicing-reconcile` `--no-track` from `agentic/feature/header-scale-factors-per-position` @ `<ae5ce0e or the tip at dispatch>`;
merge `agentic/feature/launcher-env-outside-xdg-cache` forward at once (regular merge). **RED first on that tree** (the behaviour is absent —
`convert_to_binary` has no `start_times`): T1–T8's tests fail by `TypeError`/`AttributeError`/import error; record the counts. Then **merge the
snapshot** `contrib/add-time-slicing@8eead58` (regular merge, `--no-ff`), **resolving each of the 6 hunks with its justification in the commit body**
(F3: four signature/loop unions, two header-line unions). Run RED again: the T1–T3 tests **still fail** on the contribution's arithmetic (F4) —
that is the measurement that justifies the fix commit. GREEN: the arithmetic, the F9 path resolution, the header line, the Cd guard, the tab's
conventions — **as separate commits** (intake step 4: behaviour fixes, then conventions, no behaviour change in the latter).

Fixtures: NeXus files built with `_write_nexus` (F10) extended to carry `event_time_zero`, `event_index`, `bank_error_events` and
`DASlogs/proton_charge/value` with **known** per-pulse events, so T1–T3 assert exact event sets, not counts. Stub the physics as M1/M2 did (the
`_reduce_single_run` stand-in mirrors the real one's return shape); keep `reduce_time_list`'s bookkeeping, `flatten_reduced_results` and the header
writing real.

| # | Test | RED before | GREEN when |
|---|---|---|---|
| T1a | `test_no_windows_is_the_whole_run` | `TypeError` (no parameter) | `load_and_extract(f)` ≡ `load_and_extract(f, None, None)`; arrays equal |
| T1b | `test_windows_select_by_pulse_time` (`[start, end)` on a 10-pulse fixture with 3 events/pulse, window `[2.0, 5.0)` → pulses 2,3,4 → 9 known events; error events and `cPC` the same pulses) | — | exact event ids/offsets |
| T1c | `test_start_zero_is_not_special` | — | `[0, 3)` selects pulses 0–2 exactly |
| T2a | `test_contiguous_slices_partition_the_run` (`[0,a),[a,b),[b,duration]`) | — | disjoint, union = all events, `sum(cPC)` equal |
| T2b | `test_the_last_window_includes_the_last_pulse` (`end == duration` and `end > duration`) | — | the last pulse's events present; no `IndexError` |
| T3 | `test_several_windows_concatenate_in_order` (two disjoint; two overlapping) | — | concatenation; the overlap counted twice (documented) |
| T4a | `test_invalid_windows_raise_before_reading_events` (one `None`; unequal lengths; `start >= end`; `[]`/`[]`) | — | `ValueError`; the events dataset not read (a counting `h5py` wrapper or a fixture without events) |
| T4b | `test_scalars_are_one_window` | — | `(600, 1200)` ≡ `([600], [1200])` |
| T4c | `test_a_window_after_the_run_reports_not_crashes` | — | the slice's `ValueError("No reduced result … window [a, b)")`, the others reduced (in `reduce_time_list`) |
| T5a | `test_reduce_time_slices_makes_equal_windows_named_i_of_n` | import error | `n` windows, `subname` pattern, mid-points |
| T5b | `test_the_run_file_is_resolved_the_campaigns_way` (`NEXUSpathRB` override honoured; no `/SNS/REF_L` literal) | — | the stub reducer receives the configured path; `grep -n '/SNS/REF_L' new_reduction_time_resolved.py` → nothing |
| T5c | `test_the_file_is_closed` | — | `h5py.File` not left open (`f.id.valid` false / context manager) |
| T6a | `test_the_header_names_the_window_beside_the_marker` (both writers) | — | one `Time resolved:` line + the marker |
| T6b | `test_reduce_does_not_write_windows_into_the_callers_config` | — | the caller's config unchanged after `reduce(…, start_times, end_times)` |
| T7a | `test_cd_list_overrides_the_log_and_sorts_runs` | `TypeError` | thicknesses in run order; sorted increasing |
| T7b | `test_without_cd_list_the_log_values_stand` | — | identical to the base's result |
| T7c | `test_cd_list_of_the_wrong_length_raises` | — | `ValueError` |
| T8a | `test_every_validation_failure_is_a_panel_message` (5 legs) | import error | panel text; no `QMessageBox` (the fixture would fail) |
| T8b | `test_run_reports_completion_in_panel_and_reenables_the_button` (stub `reduce_time_slices`) | — | status text; button enabled again |
| T8c | `test_a_reduction_error_is_reported_not_swallowed` | — | the error text in the panel; no `except Exception` pass |
| T9 | `test_no_print_in_library_code` (`grep -n "print(" src/lr_reduction/{new_reduction_time_resolved,binary_processing,direct_beam_maker}.py`) | prints present | nothing |

## 7. Mutate-once gate (each row in the commit body as `<mutation> → <test> -> N failed`, N ≥ 1, red alone)

| # | Mutation | Must red |
|---|---|---|
| M1 | start `searchsorted` back to `side="right"` | T1b, T2a |
| M2 | the `event_index[idx] - 1` for a non-zero start restored | T1b, T1c, T2a |
| M3 | the end's `- 1` restored | T2a |
| M4 | the `IndexError → event_index[-1] - 2` fallback restored | T2b |
| M5 | `cPC` sliced one pulse short | T1b, T2a (charge sum) |
| M6 | the equal-length check removed | T4a |
| M7 | the `start >= end` check removed | T4a |
| M8 | `[]`/`[]` accepted as "no filter" | T4a |
| M9 | the scalar wrap removed | T4b |
| M10 | `/SNS/REF_L/<ipts>/nexus` literal restored | T5b |
| M11 | the `h5py.File` left open | T5c |
| M12 | the `Time resolved:` line removed from one writer | T6a |
| M13 | `reduce()` writes `self.config.start_times` on the caller's config | T6b |
| M14 | `cd_list` ignored | T7a |
| M15 | the Cd sort removed | T7a |
| M16 | a `QMessageBox.warning` restored in one validation branch | T8a (the fixture) |
| M17 | the tab's `except Exception: pass` restored | T8c |
| M18 | the button not re-enabled | T8b |
| M19 | one `print(` restored in `binary_processing.py` | T9 |

**Frame:** `flatten_reduced_results` — one row per shape (dict / list / nested): drop a branch → T5a's result-pack assertion; the `subname`
pattern — one row (wrong index base) → T5a; the mid-point — one row → T5a.

## 8. Acceptance criteria

1. `pixi run test-reduction` returns zero from the repository root; `pixi.lock` restored, not staged.
2. **Reduction-path baseline (the Integrator's, before the gate):** on the base tip, `reduce_from_file` without windows on the campaign's baseline
   runs (`scientific-regression-testing`; the `2026-09-25A/` recipe per `rereduction-headers-land` §8.3) — results and headers **byte-identical** to
   the base except the §10 A3 header decision, which the body states; then on the feature tip the same; then one run in 4 slices: the four
   `Time resolved:` lines present, the slices' proton charges summing to the run's within 1e-6, every event accounted for (T2 on the real file).
3. Every §7 row and the frame in a commit body with its count; **each of the 6 conflict hunks named in the merge commit's body with which side
   won and why** (F3).
4. `git diff --name-only <base>...feature/time-slicing-reconcile` = §4's files (+ the tests); no `plans/`, no `todo.md`, no battery script.
5. `grep -rn "print(" src/lr_reduction/new_reduction_time_resolved.py src/lr_reduction/binary_processing.py src/lr_reduction/direct_beam_maker.py`
   → nothing; `grep -n "/SNS/REF_L" src/lr_reduction/new_reduction_time_resolved.py` → nothing; `grep -n QMessageBox launcher/apps/time_resolved.py`
   → nothing (except an import to remove).
6. The numerical-diagnostics reviewer receives F4 and T1–T3 as the surface: the window predicate, the partition property, the proton-charge
   convention — **the clean-factor discipline applies if a slice's charge or count differs from the run's by a pulse's worth**.
7. **Deployment-shaped acceptance (Integrator, analysis node):** `reduce_time_slices` on one IPTS-36119 run in 4 slices from the feature tip, then
   the launcher's "Time resolved" tab on the same run (offscreen): outputs under a scratch `savepath`, headers checked by the invariant, no
   traceback; path and sha256s in the PR body.
8. PR body: names upstream PR #205 and `8eead58`; the snapshot ref; the 6 hunks and their resolutions; the tests added; the arithmetic change
   (F4 → T1–T3) stated plainly as **a behaviour change relative to the contribution, with the measurement that justified it**; the deploy
   consequence — reduction-path change, redeploy after merge; the human coordinates upstream (the campaign never comments there).

## 9. Learnings relied on

- The intake procedure (`plans/upstream-add-time-slicing-plan.md`): RED first against intent; snapshot immutable; every hunk justified.
- `roi-popout-dialog` L7/L10/L13/L14: every §3 cell names its test; a credit by mutation needs a mutation per dimension; a fixture must sit where the
  dimension matters — here the fixture's pulses must have events **on** the window edges (a pulse exactly at `start` and at `end`), or T1/T2 cannot
  see the `±1` conventions.
- `header-scale-factors-per-position` R4/R5: `reduce()` writes nothing into the caller's config.
- `launcher-env-outside-xdg-cache` F3 / A-52: a fact about what runs is measured by running it — the tab's "completed" path is driven, not read.
- numerical-diagnostics: a one-pulse discrepancy is a convention slip, not physics.

## 10. Assumptions and open questions (the plan proceeds under each default)

| # | Question | Owner | Default |
|---|---|---|---|
| A1 | `start_times=[]`, `end_times=[]` — "no filter" or an error? | Analyst | **error** (a window list with no windows is a mistake; `None` is the no-filter spelling) |
| A2 | Overlapping windows in one call — allowed? | scientists | allowed, concatenated (the contribution's semantics), documented in the docstring |
| A3 | A run reduced without windows: no `Time resolved` line, or `Time resolved: None, None`? | Analyst (the Integrator's baseline sees either) | **no line** — today's headers stay byte-identical for today's runs |
| A4 | The tab runs the reduction synchronously on the GUI thread (minutes). | human / scientists | v1: synchronous with the button disabled and a status line; a worker thread is a follow-up todo |
| A5 | The two `example_*.py` scripts hard-code one IPTS. | Analyst | keep as examples with a header comment; not tests |
| A6 | `reduce_time_log_filter` (commented out upstream). | human | stays commented; recorded in the PR body |
| A7 | The window unit: seconds from the first pulse (`event_time_zero` is relative) — confirm on the fixture and one real file. | Developer | seconds; T1's fixture states it |

## Revision history

v1 — **dispatched 2026-10-07 (A-101)** on the posture line (charter `f60e7bf`); snapshot ref `contrib/add-time-slicing@8eead58` pushed; tips unmoved since the measurements (no re-seal). Authored 2026-10-07 (A-100) on the human's `take` line (`requests/time-slicing-take-line.md`, M-52), from the intake procedure
(`plans/upstream-add-time-slicing-plan.md`, V1-10/V1-38/V1-39) and a read of the snapshot; facts measured on uvdl3 against `8eead58`, `exp-review`
@ `c39efe9` and the stack tip `ae5ce0e`; the Base chosen under clause (4) (the reduction stack, #42 merged forward). **Dispatch gate:** the posture
line (the governance MR `governance/take-add-time-slicing`); at dispatch re-measure F2/F3 at the then-current tips, push the snapshot ref, and
re-write `noqa-sweep`'s trigger per the human's order.
