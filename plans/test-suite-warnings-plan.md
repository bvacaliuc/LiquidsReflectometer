# Plan: `test-suite-warnings` — the suite's warnings summary carries no first-party noise; every fix is output-identical

**Campaign:** `exp-review-fixes` · **Leaf:** `test-suite-warnings` (refs `triage/test-suite-warnings`, `feature/test-suite-warnings`,
`qa/test-suite-warnings`) · **Status:** v2 (attempt 2 of N = 3; v1 rejected at `review/test-suite-warnings` @ `27eafc8` — one finding, B-1: `read_file` on a one-value file raises `TypeError` where the base returned four empties; see Revision history) — v1 dispatched 2026-10-04 against `exp-review` @ `2324e5c`; v2 continues on `feature/test-suite-warnings` (the Integrator's `todo.md` on top, @ `27eafc8`) (PR #37
merged; the subject's protocol refs are quiet and this slug's files are disjoint from every open PR, so it does not wait) ·
**Base:** `agentic/exp-review` @ `2324e5c` · **PR target:** `exp-review` on the fork, **draft** · **Not stacked.** ·
**Depends on:** nothing in the queue (files disjoint from #34, #38–#40, R1/R2, M2) ·
**Review domains:** numerical-diagnostics, test (block) · **Kind:** **reduction-path** — `peak_finding.py` and `dead_time_correction.py`
are in the reduction; the Integrator captures the base-commit baseline **before** gating (§8) ·
**Sources:** `[human, 2026-10-04, PR #37 comment]` via `requests/test-suite-warnings-and-noqa-sweep.md` (courier, verbatim); charter §3 row.

## Declared scope

**Files in:** `src/lr_reduction/peak_finding.py` (one expression), **`src/lr_reduction/background.py` (W1b — one expression; added at v2 to the declared list, the A4 route the Developer took)**, `src/lr_reduction/dead_time_correction.py` (one expression),
`src/lr_reduction/output.py` (`read_file`'s loadtxt guard and its bare `except`), `tests/unit/lr_reduction/test_output.py`, a new
`tests/test_warning_hygiene.py` case (or cases) per W5, `pyproject.toml` **only if** W4 ends in a scoped `filterwarnings` entry.

**Behaviours in** (W1–W5, §3). **Explicitly OUT:** any change to a reduced number — every fix here is proven output-identical
(§8.2); the `NOQA` tags (`noqa-sweep`, its own slug); third-party code; the pyparsing filter already in `pyproject.toml:223-234`
and its guard `test_warning_hygiene.py::test_no_pyparsing_warning_from_mathtext` (unchanged); warnings the full suite does not
emit at the base.

## 1. Request

> I would like to request a follow-on effort to analyze and deal with their root causes or handle them. … I will not hold up this
> MR for this however, it will be for a subsequent development. `[human, 2026-10-04, PR #37 comment]`

The comment's warnings summary (the deploy environment's run of `pixi run test-reduction` on `feature/launcher-test-teardown`):

| # | Where | Message | Count |
|---|---|---|---|
| W1 | `tests/test_reduction.py` | `divide by zero encountered in divide` | 694 |
| W2 | `tests/test_dead_time.py::test_deadtime_paralyzable`, `::test_full_reduction` | `invalid value encountered in divide` | 2 |
| W3 | `tests/unit/lr_reduction/test_output.py::TestRunCollection::test_read_file_empty` | `loadtxt: input contained no data` | 1 |
| W4 | `tests/test_warning_hygiene.py::test_no_pyparsing_warning_from_mathtext` | `the rational private module is deprecated`; `the math2 module is deprecated, use libfp instead` | 2 |

The Integrator's gates record the same total — "699 warnings (= the base)" — on every slug since `editor-load-fidelity`.

## 2. Verified facts at `2324e5c` (measured 2026-10-04 in the subject's pixi environment on `uvdl3`)

| # | Fact | Evidence |
|---|---|---|
| F1 | **W1's single origin is `peak_finding.py:107`**: `weights = 1 / np.sqrt(y)` — `y` holds zero counts, `1/0` → `inf` with the warning — and the very next line `weights[y < 1] = 1` (`:108`) **overwrites every such element**. The `inf` never reaches the fit. | `pytest test_reduction.py -x -W 'error:divide by zero'` → `test_q_summing` fails at `template.py:357` → `peak_finding.py:107 RuntimeWarning`; `test_full_reduction` with the same error filter **plus** `-W 'ignore:divide by zero:RuntimeWarning:lr_reduction.peak_finding'` → **1 passed** — no second origin in that test. (The Developer repeats the pair over the whole file, §6 U1.) |
| F2 | **W2's origin is `dead_time_correction.py:98`**: `corr = true_rate / (rate / tof_step)` with `rate == 0` → `0/0` → `nan` ("invalid value"), and `:101` `corr[rate == 0] = 1` **overwrites it**, as the comment at `:99-100` says. | `pytest test_dead_time.py::test_deadtime_paralyzable -W error::RuntimeWarning` → `dead_time_correction.py:98 RuntimeWarning`. The non-paralyzing branch (`:103`) has no zero divisor (`1 - rate*…`). |
| F3 | **W3's origin is `output.py:293`**: `read_file` calls `np.loadtxt` on a file holding only `# No data\n`; numpy warns (`UserWarning`) and returns an empty array; `.T` then the 4-way unpack raises `ValueError`, caught by a **bare `except:`** (`:294`) that `print`s "Could not read file. It may have no points" and returns four `[]`. The test asserts exactly that (`test_output.py:176-187`). | Read at `2324e5c`; the test passes with the warning. |
| F4 | **W4 does not reproduce in the pixi environment.** The two messages are mpmath's (`mpmath.rational` and `mpmath.math2` deprecations, mpmath ≥ 1.4); nothing first-party imports mpmath (`git grep -n mpmath src launcher tests` is empty), so they come through a third-party import chain present in the **deploy environment** and absent from the pixi lock. Under `-W always` the pixi run shows only the pyparsing camelCase deprecations the ini filter already covers. | Runs 2026-10-04; `pyproject.toml:223-234` (the pyparsing filter and its rationale); `test_warning_hygiene.py:47-60`. |
| F5 | The suite's warnings policy already has a shape: a **scoped** `filterwarnings` entry with a rationale, guarded by `test_warning_hygiene.py` ("the suite's filterwarnings must actually cover the mathtext noise" / first-party DeprecationWarnings still surface). | `pyproject.toml:223-234`; `tests/test_warning_hygiene.py`. |
| F6 | `peak_finding.fit_signal_flat_bck` (`:56`) and `dead_time_correction` have no unit test of their own; they are exercised through `tests/test_reduction.py` and `tests/test_dead_time.py` against real data, which the Integrator's baseline harness covers. | `ls tests/unit/lr_reduction | grep -iE 'peak|dead'` → nothing. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| W1 | `fit_signal_flat_bck` computes the weights **without dividing by zero**: elements with `y < 1` are `1.0` and the rest `1/sqrt(y)`, by construction (a masked assignment or `np.divide(..., where=…)`), so no `RuntimeWarning` is raised and **the resulting `weights` array is element-wise identical** to today's (today's `inf`s are overwritten before use). No other line of the function changes. |
| W1b | **(v2 — the second origin, census U1 run at `16fd1b3` against the base: `background.py:144` at `2324e5c`, 689 of the 694)** the background fit's weights are built without dividing by zero where the error is zero and the count is zero — the array is element-wise identical to the base's after its own overwrite; W1's treatment. The `counts ≠ 0, error = 0` gap still yields `±inf` and still warns, **as the base does** — declared, not changed (numerical advisory A3). |
| W2 | The paralyzing branch computes `corr` **without `0/0`**: where `rate == 0` the correction is `1.0` by construction, elsewhere today's expression — the array is element-wise identical to today's after `:101`. The comment at `:99-100` moves to the construction. The non-paralyzing branch is untouched. |
| W3 | `read_file` on a file with **no data rows** returns four empty arrays and the parsed meta **without numpy warning**: the data rows are counted before any unpack; the bare `except:` is narrowed so a `KeyboardInterrupt`/`MemoryError` is no longer swallowed; **(v2, B-1) every file shape for which the base returned four empties still returns four empties with the same message** — the shapes `np.loadtxt(...).T` can produce are enumerated below (amendment 18), and the **0-d shape** (a single number, with or without `# Meta:`) is one of them: the 4-way unpack of a 0-d array raises `TypeError`, not `ValueError`, so v1's `except ValueError` turned the base's "no points" into an uncaught exception reachable from `workflow.py:168`'s partial-file loop. Either route the reviewers measured is acceptable — `np.loadtxt(file_path, ndmin=1).T`, which turns the 0-d case into the existing `ValueError` and leaves every other probed shape unchanged, or `except (ValueError, TypeError)` — and the chosen one is named in the code comment with the shape it exists for. Files **with** data are read exactly as today. |
| W4 | The two mpmath deprecations are **environment facts, not code facts**: the slug does not add a blanket filter for a warning the pixi suite cannot see. The Developer records in the PR body which environment emits them and from which import chain (the Integrator's deployment-shaped acceptance runs the suite on the analysis node and reads `-W error::DeprecationWarning:mpmath` tracebacks — §8.4). **If** the chain is third-party and no first-party import can avoid it, a **scoped** `filterwarnings` entry (`ignore:…:DeprecationWarning:mpmath`) with a rationale in the F5 shape is added, and `test_warning_hygiene.py` gains the matching guard; **if** a first-party import pulls it in needlessly, that import is the fix. The decision and its evidence are in the PR body either way. |
| W5 | **Fail loudly on regression**: `tests/test_warning_hygiene.py` gains cases that call the three first-party sites with inputs that *used to* warn — `fit_signal_flat_bck` with a `y` holding zeros; the paralyzing correction with a `rate` holding zeros (through a small array-level helper if the function needs a workspace — the Developer extracts the arithmetic into a pure function **only** if its result is proven identical, §7); `read_file` on a comment-only file — each under `warnings.catch_warnings(record=True)` + `simplefilter("error")`, asserting no warning **and** the expected values. |

**Types and states.** `y` in W1: a float array (summed counts) with any mix of `0`, `0 < y < 1` (after background subtraction? — no: `y` is raw summed counts, `background` is subtracted later at `:110`; the Developer confirms `y`'s dtype and range and records it), `≥ 1`; all-zero `y` (no counts) → all weights `1.0`. `rate` in W2: float array per TOF bin with zeros where no events; all-zero → all `corr == 1`. `read_file` in W3 — **(v2) the complete shape table of `np.loadtxt(path).T` followed by a 4-way unpack**, every row a required outcome (U4):

| File | `loadtxt` result | after `.T` | unpack | base behaviour (kept) |
|---|---|---|---|---|
| no file | — (`open` raises) | — | — | `FileNotFoundError` propagates (test A4 adopted: pinned) |
| comment-only / `# Meta:` only / blank lines | not called (v1's guard) — the base's `loadtxt` returned shape `(0,)` with a warning | — | `ValueError` | four empties + meta; message; **no warning** (W3) |
| **a single number** (with or without `# Meta:`) | **0-d** | 0-d | **`TypeError`** ("iteration over a 0-d array") | four empties + meta; message — **B-1: v1 raised** |
| one row of four numbers | `(4,)` | `(4,)` | four **scalars** | four scalars (A2, preserved) |
| one row of N ≠ 4 numbers, or N ≠ 4 rows of one number | `(N,)` | `(N,)` | `ValueError` | four empties; message |
| ≥ 2 rows × 4 columns | `(R, 4)` | `(4, R)` | four arrays | identical arrays to the base |
| ≥ 2 rows × M ≠ 4 columns | `(R, M)` | `(M, R)` | `ValueError` | four empties; message |
| a non-numeric token | `loadtxt` raises `ValueError` | — | — | four empties; message |
| `KeyboardInterrupt` / `MemoryError` during the read | — | — | — | **propagates** (the narrowing's purpose) |

**Operation × state (every cell is a required outcome, each named by a test — U2/U3/U4):**

| Input | W1 `weights` | W2 `corr` | W3 `read_file` |
|---|---|---|---|
| all zeros | all `1.0`, no warning | all `1.0`, no warning | — |
| mixed zeros / positives | zeros → `1.0`, positives → `1/sqrt(y)`; identical to the base's array | zeros → `1.0`, positives → today's value; identical | — |
| no zeros | identical to the base's array, no warning | identical | — |
| comment-only file | — | — | four empties + `{}`; **no warning**; the base's message (if any) unchanged |
| `# Meta:` + no data | — | — | four empties + the meta; no warning |
| wrong column count | — | — | four empties (today's path), `ValueError` caught — **not** a bare except |
| **a single number, with / without `# Meta:`** (v2) | — | — | four empties + meta; the message; no exception |
| N ≠ 4 single-number rows (v2) | — | — | four empties; the message |
| data present | — | — | identical arrays to the base |

## 4. Files to change

| File | Change |
|---|---|
| `peak_finding.py` | `:107-108` → a construction without the zero division (one expression) |
| `dead_time_correction.py` | `:98-101` → a construction without `0/0` (one expression); the comment moves |
| `output.py` | `read_file`: empty-data guard before the unpack; `except ValueError` |
| `test_warning_hygiene.py` | W5's cases |
| `test_output.py` | `test_read_file_empty` asserts no warning (`pytest.warns(None)` is removed in pytest 7 — use `warnings.catch_warnings(record=True)`) and adds the header-only and wrong-column cases |
| `pyproject.toml` | **only** per W4's decision |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | `pixi run test-reduction` at the feature tip | warnings summary carries **none** of W1–W3; W4 per its decision; the count is reported in the PR body against the base's 699 |
| common | any reduction test's output | identical to the base-commit baseline (Integrator, §8.2) |
| edge | a detector image with no counts in the fit window | fit proceeds with unit weights, as today; no warning |
| edge | a run with TOF bins of zero rate under paralyzing dead time | `corr == 1` there, as today |
| edge | `read_file` on a one-row file | four scalars, as today (A2) |
| pathological | `read_file` on a non-numeric file | four empties, message, no uncaught exception — and no swallowed `KeyboardInterrupt` |
| pathological | a future change re-introduces `1/np.sqrt(y)` | W5's case reds |
| pathological | W4 handled by a blanket `ignore::DeprecationWarning` | rejected: the hygiene test's "first-party DeprecationWarnings still surface" leg must stay green |

## 6. Red-Green TDD seed

| # | Test | RED at the base |
|---|---|---|
| U1 | **the origin census**, recorded not asserted: `pytest tests/test_reduction.py -W 'error:divide by zero' -W 'ignore:divide by zero:RuntimeWarning:lr_reduction.peak_finding'` and `pytest tests/test_dead_time.py -W 'error:invalid value' -W 'ignore:invalid value:RuntimeWarning:lr_reduction.dead_time_correction'` both pass at the base → F1/F2 are the only origins; the counts (694, 2) reproduced by `-W always` and quoted in the PR body | — (measurement) |
| U2 | `fit_signal_flat_bck`'s weights: for `y` all-zero / mixed / positive, under `simplefilter("error")` no warning, and `weights` equals the base's array (the base's expression evaluated in the test with warnings suppressed, element-wise `np.array_equal`) | red: the warning |
| U3 | the paralyzing `corr` for `rate` all-zero / mixed / positive: no warning, array equal to the base's post-`:101` array | red |
| U4 | `read_file` × **every row of §3's shape table** — comment-only, `# Meta:` + no data, **a single number with and without `# Meta:`**, one row of four, N ≠ 4 single-number rows, ≥ 2 rows × 4, ≥ 2 rows × M ≠ 4, a non-numeric token, **no file** (`FileNotFoundError` propagates — test A4 adopted): no warning where the table says so; values **and types** per the table (scalars for the one-row file, lists/arrays as the base returns them); the message where the base printed it; `except` narrowed (a monkeypatched `loadtxt` raising `KeyboardInterrupt` propagates). **(v2)** the single-number legs go into `test_read_file_whose_rows_are_not_four_numbers` so v1's GREEN reds | red (warning; bare except; v1 red on the 0-d legs) |
| U7 | **(v2, test advisory A1 adopted)** the extracted helpers' **call sites** are guarded: the dead-time test drives the production path and compares the resulting `corr` with the base arithmetic evaluated on the same `rate` (`np.array_equal`), so `paralyzable_correction(rate, dead_time, 2*tof_step)` at the call reds; likewise W1b's call site in `background.py` against the base expression | — (guard) |
| U5 | W5's hygiene cases | red |
| U6 | the pyparsing hygiene test unchanged and green | passes — pin |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| W1 fix reverted to `1 / np.sqrt(y)` | U2, U5 |
| W1 mask threshold changed (`y <= 1`, or `y == 0`) | U2 (the `0 < y < 1` element, if `y` can hold one — the Developer records whether it can; if not, the `y == 0` variant is the mutation) |
| W2 fix reverted | U3, U5 |
| W2 zero-rate correction set to `0.0` or left `nan` | U3 |
| `read_file` empty guard removed | U4, U5 |
| `except ValueError` widened back to bare | U4 (`KeyboardInterrupt` leg) |
| **(v2)** the 0-d route removed (`ndmin=1` dropped / `TypeError` dropped from the except) | U4 (single-number legs) |
| **(v2)** `ndmin=2` used instead (one row of four → four 1-element arrays) | U4 (one-row leg asserts **scalars**, A2) |
| **(v2)** a helper called with a wrong argument at its call site (`2*tof_step`) | U7 |
| `read_file` returns `None`s instead of empties | U4 |
| a blanket `ignore::DeprecationWarning` added | U6 (the first-party-surfaces leg) |

Frame: each of the three first-party fixes is one expression at one site; **no helper is extracted unless U2/U3 prove the
extracted function's result identical to the inline base expression** (amendment 18: the inputs are float arrays — state the
dtype and the zero/positive partition the fix acts on; no per-angle lists are involved).

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root on the feature tip; the warnings summary quoted in the PR body
   beside the base's.
2. **Reduction-path baseline (Integrator, before gating):** capture the base-commit (`2324e5c`) outputs of the reduction tests the
   harness covers (`reduction_scripts/…`, the `rereduction-headers-land` recipe), then the feature tip's — **byte-identical** on
   every reduced file; the numerical reviewer confirms W1/W2 by the array-equality tests (U2/U3) and by reading that the
   overwritten elements were never consumed.
3. §6 RED→GREEN; §7 recorded per row.
4. **Deployment-shaped acceptance (Integrator, analysis node, the deploy environment the human used):** run the suite there with
   `-W 'error::DeprecationWarning:mpmath'` (or `-W always` and read the summary) → the W4 import chain quoted; W4's decision
   (scoped filter + guard, or an import fix) matches what that chain shows. If the deploy environment is not reachable from the
   seat, say so in the PR body and leave W4 open as an advisory with the evidence gathered.
5. PR body: reduction-path, **no numerical change** (the baseline diff), the before/after warnings summaries, W4's evidence and
   decision, the `read_file` `except` narrowing called out.
6. **(v2)** the hygiene test `test_the_paralyzable_dead_time_algorithm_warns_nothing_for_bins_without_events` narrows its
   `simplefilter("error")` to `RuntimeWarning` (test advisory A2 adopted: it failed once in nine runs under load with the broad
   filter — a flaky gate is a gate defect). PR body carries the remaining advisories (numerical A2 `np.full_like(errors, charge)` with
   integer `errors` — unreachable, a docstring line or `.astype(float)` is welcome; numerical A3 the `counts ≠ 0, error 0` ±inf predates
   this slug; test A3 contrived survivors).

## 9. Learnings relied on

- CPKT `numerical-diagnostics.md`: a fix to a "harmless" warning in reduction code is still a reduction change until the outputs
  are shown identical — baseline first.
- `editor-load-fidelity` v1's rejection (A-6): a value that "no reader can tell apart" must be shown so by reading every reader —
  here the overwritten `inf`/`nan` elements (F1/F2) are shown unconsumed by the next line, and U2/U3 pin array equality.
- The campaign's standing lesson (A-16 … A-42): every cell of §3's table is named by a test; a §7 row's test observes through
  the path its mutation breaks (here: the warning filter set to error **and** the array equality, not one of them).
- `pyproject.toml:223-234` + `test_warning_hygiene.py`: the repo's own shape for a justified filter — scoped, reasoned, guarded.
- **(post-dispatch, A-49)** A warnings census is reproduced in the **run shape that produced it** (the full suite, same cwd), never from
  one test: W4 looked environment-specific from a single-test run and was first-party in the full suite (D-34).
- **(v2)** Narrowing an exception handler is a behaviour change over **every input shape the guarded call can produce**, not over the
  shapes the author had in mind: `np.loadtxt` has a 0-d shape, and a 0-d unpack raises a different class. Enumerate the callee's return
  shapes (amendment 18) before naming the exception — the base's bare `except:` was hiding a shape, not only an exception.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | W4's mpmath chain is third-party and deploy-environment-specific. | Measured by the Integrator (§8.4); the plan commits to the *shape* of the answer, not the answer. |
| A2 | `read_file` on a one-row file returns four scalars today (1-D `.T` no-op). | **Preserved** — changing it is a behaviour change outside the request; recorded for `noqa-sweep`/a later slug as a smell. |
| A3 | `output.py`'s `print` on an unreadable file. | Kept (message unchanged) unless the module already has a logger; stdout-vs-logger is not this slug's question. |
| A4 | The 694 count is one site × the number of `fit_signal_flat_bck` calls across `test_reduction.py`. | U1 confirms; if a second origin appears, it is a new row W1b with the same treatment, recorded in the Revision history. |

## Revision history

v1 — authored and dispatched 2026-10-04 against `exp-review` @ `2324e5c` (`[human, 2026-10-04, PR #37 comment]`, couriered in
`requests/test-suite-warnings-and-noqa-sweep.md`; A-46). Origins measured in the pixi environment before authoring (F1–F4).

**CORRECTIONS after dispatch (post-dispatch note, not a new work order — the Developer's census U1 at `16fd1b3`, D-34; A-49):**
(1) **F1 was wrong**: W1's 694 are **two** origins — `background.py:144` ×689 and `peak_finding.py:107` ×5. The Analyst's check ran one
test (`test_full_reduction`) with `peak_finding` ignored and generalised from it; the census over the whole file shows the second site.
A4 anticipated this ("a second origin … is a new row W1b with the same treatment") and the Developer applied it: W1b `background_fit_weights`
divides only where kept, identity-proven like W1. (2) **F4 was wrong**: W4 **does** reproduce in the pixi environment — in the **full
suite** only: collection imports `sympy` (from `user_defined_function`), which loads mpmath, and the hygiene test's own warning-registry
reset then triggered mpmath 1.4's PEP 562 deprecation hooks. First-party, not deploy-environment: fixed in the reset, **no filter**. The
Analyst measured the hygiene test alone, not in the run shape that produced the human's report. Lesson (→ §9): **reproduce a warning
census in the run shape that produced it** — the full suite, from the same working directory — before classifying any entry as
environment-specific. (3) The Developer's identity run also found the ini's `pythonpath` puts the clone's `src` ahead of `PYTHONPATH`, so a
"base" run can silently execute the tip (its zero warnings gave it away) — recorded in the Developer's learning §4.

### v2 — 2026-10-04 (attempt 2 of 3; the work order for `triage/test-suite-warnings-v2`)

**Rejection.** `review/test-suite-warnings` @ `27eafc8` — `todo.md` at that commit (Integrator, Claude Opus 5.5): *"Verdict: REJECT — one
regression in `read_file`, found by both blocking reviewers independently and reproduced here: a file whose only data is a single number
now raises `TypeError`, where the base returned four empties. Everything else passes, and the reduction outputs are identical. Not stacked
(base `exp-review` @ 2324e5c). Not infrastructure."* What passed (**the Developer does not redo it**): gate 321 + 690, no warnings summary;
**reduction-path baseline §8.2 — all 19 harness outputs identical** once per-run noise is masked (ledger `scripts/compare-harness-masked.sh`);
numerical reviewer: W1, W1b, W2 bit-identical over every partition (all-zero / mixed / no-zero, NaN, ±0.0, subnormal, inf, negative,
`0 < y < 1`, int64/float32) and on real data (8 q-summing runs; 902 `LinearModel.fit` calls; four dead-time runs); test reviewer: the 20-row
battery and every faithful revert reproduced; U1 census 689 + 5 + 2 = 696.

> **BLOCKING — B-1: `read_file` on a one-value file raises `TypeError`** (rule a + d; reachable). Reproduction (Integrator, the two worktree
> envs): `5\n` → base `([], [], [], [], {})` + "Could not read file. It may have no points"; tip **raises `TypeError: iteration over a 0-d
> array`**; `# Meta:{"start_time": "x"}\n0.01\n` → base `([], [], [], [], {'start_time': 'x'})`; tip **raises**. Mechanism: `np.loadtxt` on a
> single value returns a 0-d array; `.T` keeps it 0-d; the 4-way unpack raises `TypeError`, not `ValueError`. The base's bare `except:`
> caught it; `except ValueError` does not — the plan's premise ("what the unpack raises on a wrong column count") does not hold for this one
> shape. Falsified: plan §3 W3, §5 ("non-numeric file → four empties, message, no uncaught exception"), the GREEN body, and the comment at
> `output.py`. Reachable: `workflow.py:168` calls `read_file` on every `REFL_<run>_*_partial.txt` in the output folder; a partial file
> truncated inside its first data row (a kill, a full disk) now stops the assembly with an uncaught `TypeError` where the base skipped it as
> "no points". **Fix (behaviour; domain = `read_file`'s file shapes):** every file shape for which the base returned four empties still
> returns four empties with the same message, and nothing else changes (the one-row file still returns four scalars, A2). Two candidate
> code routes the reviewers measured — `np.loadtxt(file_path, ndmin=1).T` or `except (ValueError, TypeError)` — choose either; the guard
> must vary the shape: add the single value, with and without `# Meta:`, to `test_read_file_whose_rows_are_not_four_numbers`.

**What the plan missed (the Analyst's defect).** W3 named the exception class from the one shape it had in mind ("a wrong column count")
and called the result "today's behaviour"; the bare `except:` the plan narrowed was hiding a *shape* (`loadtxt`'s 0-d result), and §3's
states listed "wrong column count" without enumerating what `loadtxt(...).T` can return. Amendment 18 applies to exception handlers too:
the types the changed path acts on are the callee's return shapes.

**Changes in v2.** (1) W3 restated as a behaviour over **the complete shape table** of `loadtxt(...).T` + unpack (§3), with the 0-d row
named, both measured routes acceptable, A2 preserved (four scalars for one row — so `ndmin=2` is a mutation, not a fix). (2) U4 covers every
row of that table, including the single-number legs in `test_read_file_whose_rows_are_not_four_numbers` so v1's GREEN reds, and the no-file
row (test A4 adopted). (3) **W1b** recorded as a behaviour row and `background.py` added to the declared files (the A4 route the Developer
took; the Integrator noted the plan had not recorded it). (4) U7 guards the extracted helpers' **call sites** by comparing with the base
arithmetic on the same input (test A1 adopted). (5) §8.6: the hygiene test's filter narrowed to `RuntimeWarning` (test A2 adopted — a
once-in-nine flake under load is a gate defect); the remaining advisories to the PR body. (6) Three mutation rows. **Unchanged:** W1, W2,
W4, W5, U1–U3, U5, U6, every v1 mutation, the base (`exp-review` @ `2324e5c`, re-checked: unmoved); the Developer continues on
`feature/test-suite-warnings` from `27eafc8`; **the §8.2 baseline stands** — the Integrator re-runs only the `read_file` shapes and the
changed tests. **Retry arithmetic:** attempts_done = 1 + 1 = 2 → v2 is attempt 2 of 3; a third rejection escalates.
