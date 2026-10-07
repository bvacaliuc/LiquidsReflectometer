# Plan: `time-slicing-reconcile` — intake of upstream `add-time-slicing` (PR #205) at `8eead58`: the snapshot merged onto the campaign's reduction stack, its intent pinned by tests first, every conflict hunk justified, the tab brought to the launcher's conventions

**Campaign:** `exp-review-fixes` · **Leaf:** `time-slicing-reconcile` (refs `triage/time-slicing-reconcile`, `feature/time-slicing-reconcile`,
`qa/time-slicing-reconcile`; the snapshot `contrib/add-time-slicing@8eead58`) · **Status:** READY — **v2 (attempt 2 of N = 3)** — v1 REJECTED 2026-10-07 at `97a6f9b` (`review/time-slicing-reconcile` @ `dfa21b4`, I-62: "the window selection does not partition real runs; the kinetic map plots dR as R" — five blocks, three of them one closing rule measured on the 63 real runs of the test-data submodule; the no-window path byte-identical to the base in all 148 harness files; §8.7 PASS) — **v2 = the closing rule rewritten as a per-pulse predicate with a builder that models real files (B-1..B-3), the pack name settled (B-4), the kinetic map showing R (B-5), the tab drawing into its own figure (A-1); production lines move, so §8.2's byte-identity is re-run**; the Developer continues on `feature/time-slicing-reconcile` @ `dfa21b4` (= `97a6f9b` + the Integrator's `todo.md`; the stack unmoved) — v1 was DISPATCHED 2026-10-07 (A-101) on the posture line **"Upstream intake — take add-time-slicing @ 8eead58"** (in force at charter `f60e7bf`, RULES_ADVANCED M-54; prepared the wake before on the human's couriered line, `requests/time-slicing-take-line.md`, M-52). **Snapshot ref pushed:** `contrib/add-time-slicing@8eead58` on the subject's `agentic` (= `8eead58`; immutable — a later upstream commit is a new intake). Tips re-measured at dispatch and **unmoved** since §2: `exp-review` `c39efe9`, the stack tip `ae5ce0e`, #42 `aeba172` — F2/F3 stand · **Base:** `agentic/feature/header-scale-factors-per-position` @ `ae5ce0e`
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

Canonical copy: ledger `plans/time-slicing-reconcile-plan.md`; the copy on `triage/time-slicing-reconcile-v2` is byte-identical at dispatch.

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

## v2 — the closing rule, measured on real runs (read this first; everything else stands)

**The rejection** (`dfa21b4`, I-62), verbatim: *"time-slicing-reconcile v1 REJECTED (attempt 1 of 3) — the window selection does not partition real
runs; the kinetic map plots dR as R. Review gate (numerical-diagnostics, test: block; ui-aspects: advise). Gate green (launcher 359, reduction 807).
Without windows the reduction path is byte-identical to the base in all 8 harness scenarios (148 files, volatile fields masked), and check_headers
passes. The §8.7 acceptance on IPTS-36119 run 231801 passes. Five blocks: B-1: entry/duration is float32, and on 29 of 63 real runs it is below the
last pulse time, so the last pulse is dropped (184981: 24 events, 3 error events, the charge short by one pulse). B-2: on unsorted pulse times the
windows overlap (198410, N=4: 1551 of 6045 events doubled, charge +25 %). B-3: a boundary on the last pulse duplicates it (every run). B-4: N4's
pack name is unpinned in order (M-span-order survives). B-5: the kinetic map shows dR under a colour bar labelled "R". B-1 to B-3 are one closing
rule in _pulse_range, proven per bank by ledger scripts/time-slicing-window-partition.py."*

**What v1 got right and keeps:** everything at the no-window path (byte-identical, 148/148; `check_headers` green; N1/N3/A3 hold; `tsbase` =
I-45's run on another node); the six hunks and their justifications; T3, T4c, the interior boundaries (partition exactly, including a boundary
exactly on an interior pulse); the §8.5 greps; the acceptance's 4 contiguous slices and the tab's 8 byte-equal files.

**Why the suite could not see B-1..B-3 — the plan's gap, owned.** §6's fixture said "pulses **on** the window edges" (L14) and the Developer built
exactly that: integer pulse times in order, a float32 duration equal to the last pulse. Real files are not like that: `entry/duration` is float32 and
rounds **below** the float64 last pulse time on 29 of 63 runs; `event_time_zero` is **not sorted** on 18 of 63 (a decreasing tail); and the closing
test `end >= pulse_times[-1]` fires for any window whose end equals the last entry's time, not only the final window. §2 F4 named the contribution's
off-by-ones and §9 asked for a fixture where the dimension matters — but the dimensions that matter on real data were **the file's own
irregularities**, which only reading real files reveals. The Integrator read 63 of them. L15 below.

### Behaviours restated for the second attempt (T1/T2; the rest unchanged)

| # | Behaviour |
|---|---|
| **T1′** | **A pulse belongs to a window by its own time.** For a window `[start, end)`, the selected pulses are exactly those with `start ≤ t_pulse < end` — a **per-pulse predicate**, never a bisection over an array assumed sorted and never an array position. The events of a pulse are `event_index[i] : event_index[i+1]` (the last pulse's: `event_index[-1] : n_events`); the error bank and the charge log are selected by the **same** predicate on their own pulse times. Out-of-order pulses are therefore handled by construction, and the docstring says so. |
| **T2′** | **The run's end is its latest pulse time, `max(t)` — not the last array entry, and not `entry/duration`.** Exactly one window may be *closed*: the one whose `end` reaches the run's end — `end ≥ max(t)` **or** the window built by `reduce_time_slices` as the last of `n` over `entry/duration` (float32, which may round below `max(t)`); that window takes **every remaining pulse** in all three banks. **Every other window is half-open, even when its `end` equals the last pulse's time** (B-3). Contiguous windows therefore partition the run exactly on every real file; the charges of the slices sum to the run's exactly. |
| **T5′ (N4 / B-4)** | A nested pack is named by its **span**, `slice_{int(min(starts))}_{int(max(ends))}` — the code's `window_span` (min/max) is the behaviour; the docstring and N4's wording follow it; pinned with a nested list given **out of order**. |
| **T9′ (B-5)** | `plot_kinetic`'s colour map shows **R** (the evident intent; the offset panel beside it plots R) under a colour bar labelled "R"; `dR` is not plotted unless labelled `dR` and said so in the PR body. Pinned: the image array equals the slices' R rows (in slice order) and the label text. |
| **T8′ (A-1, taken — same plot path)** | The tab draws the result **into its own figure/canvas** (or gives each result its own canvas + toolbar and releases the old), so `figure.canvas is tab.canvas`, pan/zoom work, the drawing fills the canvas without a resize, and `plt.get_fignums()` does not grow per Reduce when `show=False`. |

### Fixture for the second attempt — a builder that models real files (the §6 fixture's successor)

The slug's NeXus builder gains knobs and the T1′/T2′ tests use **all of them**: (a) `duration_float32_below_last_pulse=True` — `entry/duration` is
written as float32 and chosen so it rounds **below** the float64 last pulse time (e.g. last pulse 76.780626, duration 76.78062439); (b)
`unsorted_tail=True` — the last k pulse times go **backwards** (e.g. … 17.10, 10.72, 10.73), with events in those pulses; (c) `empty_pulses=[…]` —
pulses with no events (I-62 test A-4); (d) a pulse exactly **at** a boundary time, and the last pulse's time used as a boundary. T2′'s partition test
runs over `reduce_time_slices(num_slices=N)` for N ∈ {1, 4, 10} **and** over `reduce_time_list` with a user boundary at `t_last`, on every builder
variant, asserting per bank: disjoint, union = all, charge sum = run's (exact).

### Tests and rows for the second attempt

| # | Test | Reds under |
|---|---|---|
| **T1′a** | `test_pulses_are_selected_by_their_own_time` (unsorted tail; the per-pulse sets equal the predicate's) | **M20** `searchsorted` restored (assumes sorted) |
| **T2′a** | `test_contiguous_slices_partition_every_real_shaped_run` (all builder variants × N ∈ {1,4,10}, three banks, exact charge) | **M21** the closing rule back to `end >= pulse_times[-1]`; **M22** the run's end taken as the last entry; **M23** the last window's end taken as float32 `entry/duration` without the closing rule |
| **T2′b** | `test_a_boundary_on_the_last_pulse_does_not_duplicate_it` (`reduce_time_list([0, t_last], [t_last, duration])`) | **M24** every window whose `end == t_last` closed |
| **T2′c** | `test_the_final_window_takes_every_remaining_pulse_despite_float32_duration` | M23 |
| **T5′a** | `test_a_nested_pack_is_named_by_its_span_whatever_the_order` | **M25** `windows[0][0], windows[-1][1]` (the M-span-order mutant that survived) |
| **T9′a** | `test_the_kinetic_map_shows_r_and_says_so` (image array == the slices' R rows; colour bar label "R") | **M26** map built from `store_dr`; **M27** label `"dR"` with R data |
| **T8′a** | `test_the_tab_draws_into_its_own_canvas` (`figure.canvas is tab.canvas`; `len(plt.get_fignums())` unchanged after two Reduces with `show=False`) | **M28** `self.canvas.figure = plots` restored |
| **partition script** | ledger `scripts/time-slicing-window-partition.py` (I-62; the library's own `_pulse_range`/`_event_range` per bank over every run in the test-data submodule) **exits 0** at the v2 tip — at `97a6f9b`: 30 of 63 runs fail `reduce_time_slices`' windows (29 float32 + 5 unsorted), 63 of 63 the boundary case | the Integrator's v2 gate runs it; the Developer runs it before `qa/` and quotes the result |

**Advisories taken in v2 if they cost a line (else PR body):** A-5 (pin `create_db`'s `start_times`/`end_times` pass-through — one assertion);
A-6 (T7a with runs **not** in Cd order so the sort under an override is pinned). **PR body:** A-2 (`NoWheelComboBox`, the slice-count bounds),
A-3 (synchronous run; a worker is §10 A4's follow-up), A-4 (`imshow` extent/Q grid), A-7 (the composed slice name `…_slice_1of4_slice_0_200` — say
so or name once; the Developer's call), A-8 (`get_log_values` `KeyError` on 179932 — the base's).

**v2 recipe.** RED first: the new builder variants make T2′a/T2′b/T2′c and T1′a fail on `dfa21b4`'s production (the Integrator reproduced each on
real files; the fixture must reproduce each on synthetic ones — if a variant does **not** red, the variant is wrong, not the test). GREEN: one
commit for the closing rule (B-1..B-3 — "one rule"), one for N4, one for the map, one for the tab's figure, one for A-5/A-6. **§8.2 re-run**: the
no-window path byte-identical to `tsbase` again (production lines moved); the partition script exits 0; the whole battery (§7 + v2 rows M20–M28,
N ≥ 1 each, red alone). Merge the predecessors forward if they moved; gate; `qa/`.

### Post-dispatch CORRECTIONS (2026-10-07, A-102 — from the Developer's working notes N1–N6, `plans/time-slicing-reconcile-learning.md` §0; additive, scope unchanged)

| # | What the Developer measured that §2 did not say | Decision (the plan's, consistent with its own §3/§10) |
|---|---|---|
| N1 | Without windows the snapshot changes `pcharge` from `entry/proton_charge` to `[sum(DASlogs cPC)]` ("test this change") — equal to 9 digits on the eight real runs, **not byte-identical by construction**. | **T1a's "byte-identical" governs:** the no-window path keeps the base's `entry/proton_charge`; the windowed path sums the selected pulses' `cPC` (T1/T2). The two sources' equality on real runs is recorded (a fact for the numerical-diagnostics reviewer), not relied on. |
| N2 | `convert_to_binary` returns `None` when no pulse has charge; every caller unpacks it (a `TypeError`, wrapped as "Failed to compute binary data"). | T4c's "a window after the run selects nothing — reported, not a crash": the empty selection raises a clear `ValueError` naming the window **before** the unpack; the pre-existing no-charge `None` is not this slug's (a todo if the Developer wants it on the record). |
| N3 | Two `NRReductionConfig` defaults (`start_times`, `end_times`) would add two keys to **every** output's Config line (the header serialises `config.__dict__`) — against §10 A3 and acceptance 2. | **The window travels as a runtime record** (M2's R4/R5 pattern — as the scale and the λ range do), **not** as config defaults; §4's `nr_reduction_config.py` row becomes "no new defaults"; T6b's "no write into the caller's config" stands; today's headers stay byte-identical (A3). |
| N4 | `reduce_time_list` names a slice with `int(starts[i])`, which raises for the nested windows its own comment allows. | A3's "several windows in one call" (T3) must name the pack: `slice_{int(first_start)}_{int(last_end)}` for a nested list, or the caller's `subname`; the Developer's call, recorded in the docstring and T5a. |
| N5 | The Cd sort (F7) is already the base's (`create_db` sorts by Cd at `ae5ce0e`). | T7a asserts the **override**; T7b asserts the sort is the base's, unchanged; §7 M15 (sort removed) stays — it reds T7b now. |
| N6 | The snapshot calls `_reduce_single_run(i, rb_num, start_times=…, end_times=…)`; the existing physics stubs (`test_prior_combination.py`) take `(self, i, rb_num)`. | The stubs gain the two keywords (test-only); the stub mirrors the real signature as M2's did. |
| F10 | `_write_nexus` lives in `test_roi_estimate.py`, which is #44's and **not on this stack**. | A builder of this slug's own in `test_time_slicing.py` (a second builder until a shared test-support module exists — `todo-roi-popout-data-followups-from-dialog-gate` / I-56 A-5 already ask for one). |

Also measured by the Developer on the eight real runs (the test-data submodule): `entry/proton_charge` = `sum(DASlogs/proton_charge/value)` to
9 digits; one charge entry per pulse, at the pulses' times, the error bank on the same pulses; `event_time_zero` starts at 0.0 s (A7 holds); **the
last pulse sits exactly at `entry/duration` in 3 of 8 runs and can hold events (179932: `event_index[-1]` = 300086 of 300088)** — so T2's closed
last window is not a corner case, and the snapshot's `event_index[-1] − 2` fallback drops real events.

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
| **M20 (v2)** | the per-pulse predicate → `searchsorted` on `event_time_zero` (assumes sorted) | T1′a | B-2: 198410 N=4 → 7596 of 6045 events, charge +25.3 % |
| **M21 (v2)** | the closing rule → `end >= pulse_times[-1]` | T2′a | B-1/B-3 |
| **M22 (v2)** | the run's end → the last array entry instead of `max(t)` | T2′a | B-2 |
| **M23 (v2)** | the last window's end → float32 `entry/duration` with no closing rule | T2′a, T2′c | B-1: 184981 loses 24 events, the charge short by one pulse |
| **M24 (v2)** | every window with `end == t_last` closed | T2′b | B-3: 179932 → 300090 of 300088 events |
| **M25 (v2)** | `window_span` → `windows[0][0], windows[-1][1]` | T5′a | B-4: survived v1 (156 passed) |
| **M26 (v2)** | the kinetic map built from `store_dr` | T9′a | B-5: the contribution's L164/L198 |
| **M27 (v2)** | the colour bar labelled `"dR"` over R data | T9′a | B-5 |
| **M28 (v2)** | `self.canvas.figure = plots` restored | T8′a | A-1: pan/zoom dead, cropped figure, a pyplot figure per Reduce |

**Frame:** `flatten_reduced_results` — one row per shape (dict / list / nested): drop a branch → T5a's result-pack assertion; the `subname`
pattern — one row (wrong index base) → T5a; the mid-point — one row → T5a.

## 8. Acceptance criteria

1. `pixi run test-reduction` returns zero from the repository root; `pixi.lock` restored, not staged. **v2:** `scripts/time-slicing-window-partition.py`
   (ledger, I-62) exits 0 over the test-data submodule at the v2 tip — quoted in the commit body; §8.2 re-run (production lines moved).
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
- **L15 (v2 — the dimensions that matter are the file's own irregularities):** a fixture built from the plan's idea of a run (sorted integer pulse
  times, a duration equal to the last pulse) pinned the interior arithmetic and missed the three faults real files carry — a float32 `entry/duration`
  that rounds below the float64 last pulse (29/63 runs), an unsorted tail (18/63), and a boundary on the last pulse (63/63). "A fixture where the
  dimension matters" (L14) presupposes knowing the dimensions; for data files they are discovered by **reading many real files first** and the
  builder is written to reproduce what was found. The Integrator's partition script over 63 runs is the shape of that reading; a plan for a
  data-reading slug should ask for it **before** the fixture is designed, not at the gate.

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

### v2 — 2026-10-07, after the Integrator's rejection of v1 @ `97a6f9b` (`review/time-slicing-reconcile` @ `dfa21b4`, I-62; attempt 1 of 3)

Rejection quoted in full in the "v2" section. What v2 changes: T1′/T2′ (a per-pulse predicate; the run's end is `max(t)`; exactly one closed window —
the one reaching the run's end, including the float32-duration case — every other half-open even at `t_last`), T5′ (the pack name by span, min/max,
pinned out of order), T9′ (the kinetic map shows R), T8′ (the tab draws into its own figure — A-1 taken); a builder that models real files (float32
duration below the last pulse, an unsorted tail, empty pulses, a boundary on the last pulse); §7 M20–M28; §8.1 the partition script exits 0 and §8.2
re-run; §9 L15. **Plan errors owned:** the fixture guidance (L14) assumed the plan knew the dimensions of a real file; the Integrator found three it did
not by reading 63 files — the plan should have asked for that reading (the test-data submodule was there) before designing the fixture. Unchanged:
scope, Base (the stack unmoved: `ae5ce0e`, `aeba172`), the PR target, N1–N6, the §8.7 acceptance. The Developer continues on
`feature/time-slicing-reconcile` @ `dfa21b4`.


v1 — **dispatched 2026-10-07 (A-101)** on the posture line (charter `f60e7bf`); snapshot ref `contrib/add-time-slicing@8eead58` pushed; tips unmoved since the measurements (no re-seal). Authored 2026-10-07 (A-100) on the human's `take` line (`requests/time-slicing-take-line.md`, M-52), from the intake procedure
(`plans/upstream-add-time-slicing-plan.md`, V1-10/V1-38/V1-39) and a read of the snapshot; facts measured on uvdl3 against `8eead58`, `exp-review`
@ `c39efe9` and the stack tip `ae5ce0e`; the Base chosen under clause (4) (the reduction stack, #42 merged forward). **Dispatch gate:** the posture
line (the governance MR `governance/take-add-time-slicing`); at dispatch re-measure F2/F3 at the then-current tips, push the snapshot ref, and
re-write `noqa-sweep`'s trigger per the human's order.
