# todo.md — Integrator rejection, `time-slicing-reconcile` v2 @ 1f722db (attempt 2 of 3; v3 is the last; review gate: numerical-diagnostics, test (block), ui-aspects (advise))

**Verdict: REJECT, tests only. Four unpinned dimensions of two declared clauses (T2′, T8′). Production is right.** v1's five blocks are
fixed and proven on real data, including by an independent check. What remains is four one-line production mutations that the suite
cannot see. Each was reproduced here: 194 passed under each, in a `git archive` copy with `__file__` printed from the copy. To make v3
converge, **every dimension of T2′'s run's end and of T8′ is listed below with its pin**. A v3 that pins the four open rows and changes
nothing else passes this gate's checks as they stand.

## What passed (do not redo)

- **Gate:** `pixi run test-reduction`, analysis clone 2 (analysis-node01), 14:53–15:09 EDT. Launcher **360 passed**, reduction **846
  passed**, exit 0, clean. The slug's diff is code, tests and docstrings only, with no env or ledger-shaped paths.
- **v1's blocks are fixed, on real data, by an independent check.** Ledger `scripts/time-slicing-partition-independent.py` (new, this
  seat's, I-63) drives the real `reduce_time_slices` / `reduce_time_list`. Only `reduce_from_file` is replaced, by a recorder around the
  real `load_and_extract`. It compares the result with an expectation computed from the raw NeXus arrays and no library selection code.
  - **1f722db: 63/63 runs exact** at N = 1 and N = 4 and in the boundary case: events, error events and charge per slice; totals equal to
    the run's.
  - **97a6f9b (v1, the control): 63/63 fail**, with I-62's numbers (184981 −24 events; 198410's third slice doubled). The checker can fail.
- **§8.2, the no-window reduction path:** `scripts/rereduction-scenarios.sh` on worktree `qa-1f722db` (`tstip2`) vs `tsbase` (ae5ce0e).
  `scripts/compare-harness-masked.sh` gives **same(masked) for every output file in all 8 scenarios**. `check_headers.py` passes on all 8
  and on the A/B order. The one transcript-only difference is T9's: `binary_processing.py`'s "Older run doesn't include Beam-Earth
  centered angle…" is now `logger.info`, not `print`. It no longer appears on the autoreduction console unless logging is configured.
  State that in the PR body.
- **§8.7 acceptance** (`scripts/time-slicing-acceptance.py`, IPTS-36119 run 231801): **PASS.** 4 slices, the last closed just past the
  last pulse (803.5570120…). The tab's 8 files are byte-equal to the library's. The control writes no line, and an empty run field is a
  panel message.
- **numerical PASS.** Every edge probe on 63 real runs matches the per-pulse predicate: short user windows, an end exactly at max(t),
  last_pulse < end < duration, N = 1, overlapping ends, an unsorted run's `t[-1]`. B-5 is point-wise: the map is bitwise R, not dR.
  `entry/proton_charge == sum(cPC)` bitwise on 63/63.
- **ui PASS.** B-5 and v1's A-1 are fixed. `figure.canvas is tab.canvas`, the figure fits the canvas, a real zoom drag works, and
  `plt.get_fignums()` stays empty.
- **Battery** (ledger table @ e80e28a, 92 rows, re-run here): in progress at the verdict, 26 rows red so far, none surviving. The full count
  is appended to I-64.

## BLOCKING (rule b: a one-line mutation of declared behaviour survives; all test-only)

T2′ (plan v2): *"The run's end is its latest pulse time, `max(t)` — not the last array entry, and not `entry/duration`. Exactly one window
may be closed: the one whose end reaches the run's end — `end ≥ max(t)` or the window built by `reduce_time_slices` …"*, with T2′a's
"three banks". T8′: *"The tab draws the result into its own figure/canvas"*.

| # | Clause dimension | One-line mutation (reproduced: 194 passed) | Effect if it shipped | Pin it with (behaviour) |
|---|---|---|---|---|
| **B-1** | T2′ run's end = max over **the error bank** | `read_run_end`: delete `'entry/bank_error_events/event_time_zero',` | an error pulse later than every event pulse and charge time is lost from the final window (test reviewer's guard: 10 of 11 error events) | a builder run whose **error bank alone** holds the latest pulse; assert the error bank partitions |
| **B-2** | T2′ run's end = max over **the event bank** | `read_run_end`: drop `'entry/bank1_events/event_time_zero'` from the tuple | the same for detector events | a run whose **event bank alone** holds the latest pulse (charge log ending earlier); assert the event bank partitions |
| **B-3** | T2′ first arm: **`end ≥ max(t)` closes** (when `entry/duration` > max(t)) | `final_windows`: `reach = min(marks)` → `reach = marks[-1]` (the duration only) | `reduce_time_list([0], [max(t)])` on a run whose duration is above its last pulse (27 of 63 real runs) stays half-open and **silently drops the last pulse** (reproduced here on REF_L_179932: `[0, max(t)]` selects 300086 of 300088 events under the mutant, 300088 unmutated) | a run with duration > max(t) and a user window ending exactly at max(t) (and one between max(t) and duration); assert each takes the last pulse |
| **B-4** | T8′ in **"Time values" mode** | `time_resolved.py`, the `reduce_time_list` call: delete `figure=self.figure,` | the tab keeps showing the previous plot after a Time-values Reduce | T8′a's assertions (`figure.canvas is tab.canvas`, the drawn axes are the result's, `get_fignums` unchanged) **in both modes** |

**Already pinned; v3 must not weaken these** (this seat re-runs them):
- T2′ second arm, the slicing functions' duration-built final window: M23, M23b, M-slices-close.
- Ties: overlapping windows that end together are all final (M24c).
- No final window for a list that stops short (M24b).
- `close_final_window` extends only when needed: nextafter applied only when `end ≤ last_pulse` (M-close-always, M-close-to; the
  reviewer's `<=`→`<` gives 20 failed).
- The reach test `>=` (the reviewer's `>` gives 21 failed).
- The charge log's contribution to max(t) (M22b).
- max not last entry (M22).
- T8′ in slices mode (M28).
- B-5's map = R and its label (T9′a, M26, M27).

## ADVISORY (PR body; v3 may take the one-liners)

- **N-A1 (numerical):** a user end between `entry/duration` and the last pulse (duration < end < max(t)) is treated as final and extended.
  It takes exactly one pulse more than the half-open predicate, +1 on 36/36 such runs. The gap is ≤ 122.8 µs against a 16.7 ms pulse
  period, so it can never take more than one pulse. It is also what makes `reduce_time_list([0], [duration])` cover the run. The
  `final_windows` docstring says so; the plan's T2′ names only `reduce_time_slices`. Say it in the PR body.
- **N-A2 (numerical):** closure depends on siblings. `[0, duration)` plus a window lying wholly after the run gives a final window that
  selects nothing (T4c's error), so `[0, duration)` stays half-open.
- **N-A3 (numerical):** the interior boundaries are float32 (from the 0-d duration). This is harmless: both sides use the same value.
  **Measured, for the record:** `duration − max(t)` lies in [−123 µs, +110 µs], with 36 runs below and 27 above. v1's "29" used the last
  array entry, not max(t). The charge-log times equal bank1's bitwise on 63/63.
- **T-A3 (test):** `assert_partition` checks the charge by its sum. A Counter on cPC, as for the ids and errors, is one line.
- **U-A1 (ui):** the launcher test does not assert the map's array is R. The unit test T9′a does.
- **U-A2:** the mode combo still takes wheel events when unfocused. Use `NoWheelComboBox`.
- **U-A3:** at 800×700 the canvas gets 778×175 px and the colour bar is ~3 px. Give the plot area a stretch factor or a splitter.
- **U-A4:** the `imshow` extent takes slice 0's bin centres as edges for every slice.
- **U-A5:** `plot_kinetic` clears the tab's figure before it can raise "No positive R values", which leaves the canvas empty on that path.
- **Carried from I-62:** A-2 (the slice count is capped at 99 and needs at least 2; settings are saved only on Reduce), A-3 (a
  synchronous run queues clicks), A-5 (create_db's window pass-through), A-6 (the Cd sort under an override), A-7 (the doubled slice
  names), A-8 (`get_log_values` KeyError on the test-data runs, the base's).

## Next (the Analyst's)

v3, the last attempt: B-1 to B-4 as tests (no production line), plus whatever of the one-liners the Analyst takes. This seat will
re-run, at v3:
- the independent partition check (63 runs);
- the masked harness against `tsbase`;
- `check_headers`;
- the acceptance;
- the whole battery, with rows for B-1 to B-4 added by the Developer, each of which must red alone.
