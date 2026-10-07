# todo.md — Integrator rejection, `time-slicing-reconcile` v1 @ 97a6f9b (attempt 1 of 3; review gate: numerical-diagnostics, test (block), ui-aspects (advise))

**Verdict: REJECT. Five blocks, three of them in the window selection on real runs.** The selection rule that closes a window at the
run's end (`binary_processing._pulse_range`: `if end >= pulse_times[-1]`) is wrong in three ways on real files. The suite cannot
see any of them, because its builder writes integer pulse times in order, with a float32 duration equal to the last pulse.
Everything at the no-window path is right, byte for byte.

## What passed (do not redo)

- **Gate:** `pixi run test-reduction`, analysis clone 2 (analysis-node01), 12:22–12:35 EDT. Launcher **359 passed**, reduction **807
  passed**, exit 0, clean.
- **Scope and hygiene:** the slug's own diff is 14 files against the merge of ae5ce0e and aeba172, with no `plans/`, `todo.md`,
  battery, `pixi.lock` or `pyproject` paths. The merge commit 72e82a5 names all 6 hunks and their resolutions (§8.3). §8.5's greps are
  clean: no `print(`, no `/SNS/REF_L`, no `QMessageBox`, no `except Exception`.
- **§8.2, the reduction path without windows, reproduced here.** `ledger/scripts/rereduction-scenarios.sh` was run on per-SHA worktrees,
  base `qa-ae5ce0e` (tag `tsbase`, I-60) and tip `qa-97a6f9b` (`tstip`), with 8 scenarios × 3 runs of IPTS-36119:
  - `compare_columns` is identical in every file;
  - **all 148 files are byte-identical** once the output path, the version string, timestamps and plotly UUIDs are masked;
  - `check_headers.py` passes on all 8 tip scenarios and on the A/B orders.
  N1 (the charge stays `entry/proton_charge`), N3 (no Config keys) and §10 A3 (no `Time resolved` line) all hold.
  `tsbase` itself equals I-45's run of the same SHA on another node.
- **§8.7 acceptance** (ledger `scripts/time-slicing-acceptance.py`, new; IPTS-36119 run 231801, read only, outputs in scratch): **PASS.**
  - The library gives 4 slices, contiguous over 0 to 803.557 s. Each slice file has one `Time resolved` line, then the format marker.
  - The control without windows has no line.
  - The tab, built by the launcher's `main()`: 4 slices, Reduce re-enabled, and the 8 files byte-equal the library's.
  - An empty run field is a panel message, and nothing is written.

  Run 231801's pulses are in order and its duration rounds up, so none of the blocks below show on it.
- **Point-wise, on the real files (numerical reviewer, re-checked here where marked):**
  - interior boundaries partition exactly (179932, 184975, 184980, including a boundary exactly on a pulse);
  - T3 concatenation holds;
  - T4c raises a named `ValueError`;
  - **N1 holds on 63/63 runs** (`sum(cPC) == entry/proton_charge`, exactly);
  - F4's interior off-by-ones are fixed.
- **Battery** (ledger `scripts/mutations-time-slicing-reconcile.py`, re-run here in a `git archive` copy): the run is in progress at the
  verdict, 22 rows red so far and none surviving. The full count will be appended to I-62.

## BLOCKING

### B-1 (harm; T2): the last pulse is dropped when `entry/duration` (float32) rounds below the last pulse time (float64), on 29 of the 63 test-data runs

- **Mechanism:** `reduce_time_slices` builds its last window's end from `np.array(f['entry/duration'][0])`, a float32. On those runs it
  is below `event_time_zero[-1]`, so `end >= pulse_times[-1]` is false and the closing branch never fires.
- **Reproduced here** with the tip's own `_pulse_range` / `_event_range` on `REF_L_184981`. The duration is 76.78062439 (float32) and the
  last pulse is 76.780626. **N = 1 and N = 4 both select 100247 of 100271 events (24 lost).** The test reviewer found 3 of 30320 error
  events lost and the charge short by **exactly one pulse** (relative −2.177e-4; §8.6's clean-factor fingerprint).
  184982 loses 5 events, 197914 loses 21, 197925 loses 37. On 197918, 198388 and 198409 the charge is short by a pulse with 0 events lost.
- **Fix: behaviour.**
  - **Domain:** the window that reaches the run's recorded end, in all three banks (events, error events, the charge log).
  - **Required behaviour:** that window takes every remaining pulse, whichever side of the float64 pulse times the float32 duration
    rounds to.
  - **Guard:** the builder must vary the dimension the fix freezes. Add a run whose float32 duration rounds **below** its last pulse
    (e.g. 76.780626 s), and assert that `reduce_time_slices`' slices cover every event, every error event and the full charge.

### B-2 (harm; T1/T2): on runs whose pulse times go backwards near the end, windows overlap and events and charge are counted twice

- **Mechanism:** `_pulse_range` runs `np.searchsorted` on `event_time_zero` as if it were sorted, and treats `pulse_times[-1]`, the
  array's last entry, as the latest time. It is neither, on 18 of 63 runs.
- **Reproduced here** (5 of the 63 runs fail `reduce_time_slices`' own N = 4 windows this way; the reviewer counts 18 with a decreasing tail somewhere) on `REF_L_198410`: 1031 pulses, `t[-1]` = 10.716724, `max(t)` = 17.100092, not sorted.
  **N = 4 selects 7596 of 6045 events: 1551 double-counted.** The numerical reviewer found 76 of 297 error events doubled and the
  charge at **+25.3 %** (+60.8 % at N = 10).
- **Fix: behaviour.** Each pulse goes to the window that contains **its own time** (a predicate per pulse, not an array position or a
  bisection). The run's end is the last time, not the last entry. Say in the docstring what happens to out-of-order pulses.
- **Guard:** a builder run with a non-monotonic tail. T1/T2 must hold on it per pulse and per bank.

### B-3 (T1): a window boundary exactly on the last pulse's time duplicates that pulse

- **Mechanism:** a non-final window `[0, t_last)` has `end >= pulse_times[-1]`, so it is closed and takes the last pulse, which the next
  window `[t_last, duration]` takes too.
- **Reproduced here** on `REF_L_179932`: those two windows select **300090 of 300088 events (2 double)**. **Every one of the 63 runs fails this case.** It is reachable through
  `reduce_time_list`'s user windows, not through `reduce_time_slices`.
- **Fix: behaviour.** Only the window that reaches the run's end is closed. Every other window stays half-open, even when its end
  equals the last pulse time.

B-1 to B-3 come from one rule. Their fixes are one change to how a window's pulses are chosen, and one builder that models real files:
float32 duration, unsorted tail, and empty pulses (test reviewer A-4).

### B-4 (rule b; N4): the nested pack's name is unpinned in order

- `window_span` returns `min(starts), max(ends)`. Its docstring and `reduce_time_list`'s say "first start / last end", and N4 says
  `slice_{int(first_start)}_{int(last_end)}`.
- The battery's own **M-span-order** (`windows[0][0], windows[-1][1]`, added on the ledger after the qa tag) **survives, 156 passed**
  (test reviewer). The nested test's windows are given in order, so the two forms agree.
- **Fix:** add a nested case given out of order. Make the code, the docstring and N4 say the same thing; which one is the Analyst's
  call in the plan. Test-only if the plan picks min/max and the docstring is reworded.

### B-5 (harm; T9's figure): the kinetic colour map shows dR under a colour bar labelled "R"

- **Mechanism:** `plot_kinetic` builds the map from `store_dr` (`Z = np.array([...] for arr in store_dr)`). It collects `store_r` and
  never uses it, and labels the colour bar `'R'`. This came from the contribution (8eead58 L164, L198).
- **Effect:** every Reduce from the tab shows scientists the error bars' magnitude as reflectivity. The offset panel beside it plots R.
- **Fix: behaviour.** The map shows R (the evident intent) and its label says so. If dR is meant, it is labelled dR and the PR body
  says why. Pin it: assert the image array equals the slices' R rows, and the label.

## ADVISORY (for the PR body; v2 may take them)

- **A-1 (ui; strongly recommended in the same pass, since it is the same plot path):** `_run_reduction` puts the returned figure into
  the tab's canvas with `self.canvas.figure = plots`. That figure was made by `plt.subplots(figsize=(15, 6))`. The ui reviewer's
  offscreen probe found:
  - `figure.canvas is not tab.canvas`;
  - the 1500×600 figure is cropped to the 778×175 canvas until a resize;
  - the toolbar's handlers stay on the old figure, so pan and zoom are dead;
  - `plt.get_fignums()` grows by one per Reduce.

  Behaviour: draw into the tab's own figure (or give each result its own canvas and toolbar, releasing the old ones), and leave no
  pyplot figure registered when `show=False`.
- **A-2 (ui):** the mode combo takes wheel events when unfocused, so a stray wheel switches the mode before Reduce. Use the editor's
  `NoWheelComboBox`. Settings are saved only on Reduce. The slice count is capped at 99 and needs at least 2, while the library accepts 1.
- **A-3 (ui):** the reduction is synchronous (§10 A4). Clicks during a run queue up and can start a second run after the button is
  re-enabled, and the status text does not repaint mid-run.
- **A-4 (ui):** the `imshow` extent takes bin centres as edges and assumes slice 0's Q grid for every slice. The log x-axis is faithful
  only for log-binned Q.
- **A-5 (test):** dropping `create_db`'s `start_times`/`end_times` pass-through survives (156 passed). It is outside T7 and F5.
- **A-6 (test):** with `cd_list`, T7a's runs are already in Cd order, so the sort under an override is pinned only via T7b.
- **A-7 (naming, from the acceptance):** a slice of `reduce_time_slices` is written as `…_slice_1of4_slice_0_200`.
  `reduce_time_slices` hands `slice_1of4` to `reduce_time_list` as `subname_input`, which appends its own span. The tests pin this
  (the contribution's composition). Say so in the PR body, or name it once.
- **A-8 (numerical, base, not this slug):** `get_log_values` raises `KeyError` on 179932 (`BL4B:Mot:si:Y:Gap` missing). The base has the
  same call.

## Next (the Analyst's)

v2 should fix the window selection's closing rule (B-1 to B-3, one rule) with a builder that models real files, settle N4 (B-4), and fix
the kinetic map (B-5). These are production lines, so §8.2's byte-identity must be re-run at v2. The `tsbase` baseline stands. B-1 to B-3 are
proven on the real files by ledger `scripts/time-slicing-window-partition.py` (new, I-62). It runs the library's own `_pulse_range` /
`_event_range` per bank over every run in the test-data submodule. At 97a6f9b, **30 of 63 runs fail `reduce_time_slices`' windows
(29 float32 + 5 unsorted, overlapping) and 63 of 63 fail the boundary case.** v2 makes it exit 0, and so does the Integrator's v2 gate.
