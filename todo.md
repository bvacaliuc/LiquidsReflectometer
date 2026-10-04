# todo.md — Integrator rejection, `test-suite-warnings` v1 @ 16fd1b3 (attempt 1 of 3; review gate: numerical + test, one finding)

**Verdict: REJECT — one regression in `read_file`, found by both blocking reviewers independently and reproduced here:
a file whose only data is a single number now raises `TypeError`, where the base returned four empties.** Everything
else passes, and the reduction outputs are identical. Not stacked (base `exp-review` @ 2324e5c). Not infrastructure.

## What passed (do not redo)

- **Gate** `pixi run test-reduction` from the subject root, analysis clone 2, 12:24–12:36 EDT: launcher **321 passed**,
  reduction **690 passed**, **no warnings summary** (the base: 699), **exit 0**.
- Scope: the plan's files plus `src/lr_reduction/background.py` — W1b, the second origin the plan's A4 anticipates ("a new
  row W1b with the same treatment"); the plan's Revision history does not yet record it (the Analyst's).
- **Reduction-path baseline (§8.2)** — per-SHA worktree envs (`.pixi/worktrees/base-2324e5c`, `qa-16fd1b3`), the harness
  `reduction_scripts/multiple.sh` (221472–221474, IPTS-36119): **all 19 output files identical** once per-run noise is
  masked (version stamp, harness folder, Plotly ids, durations, dates) — ledger `scripts/compare-harness-masked.sh`; the
  sides told apart by `# Reduction 2.10.0.dev…+g2324e5c` vs `+g16fd1b3`; a one-digit edit is detected.
- **Numerical reviewer:** W1, W1b and W2 bit-identical to the base (`.view(uint64)`) over every partition — all-zero /
  mixed / no-zero, NaN, ±0.0, subnormal, inf, negative, the 0 < y < 1 edge, int64/float32 — and on real data: W1 over 8
  q-summing runs (198409–198416), W1b over all 902 `LinearModel.fit` calls of `template_fbck.xml` (9 output bodies
  byte-identical), W2 over four runs and `process_from_template_ws(dead_time=True)`. The W1b gap (counts ≠ 0, error 0)
  still produces ±inf and still warns, as declared. `read_file`: 31 of 33 file shapes identical (types, values, message).
- **Test reviewer:** the 20-row battery reproduced exactly (every §7 row red; M2b equivalent as recorded); every faithful
  revert red (W1 M1; W1b M9/M10; W2 M3/M3b; W3 the base's try/bare-except, 5 red incl. the interrupt leg; W4 F1); 1-ulp
  shifts red the identity tests; RED 18/17 and GREEN 39 as recorded; **U1 census** at the base 689 (`background.py:144`)
  + 5 (`peak_finding.py:107`) + 2 (`dead_time_correction.py:98`) = 696, and at the tip both messages as errors with no
  ignores → 21 passed.

## BLOCKING — B-1: `read_file` on a one-value file raises `TypeError` (rule a + d; reachable)

**Reproduction** (Integrator, the two worktree envs, `lr_reduction.__file__` printed per side):

| File | Base 2324e5c | Tip 16fd1b3 |
|---|---|---|
| `5\n` | `([], [], [], [], {})` + "Could not read file. It may have no points" | **raises** `TypeError: iteration over a 0-d array` |
| `# Meta:{"start_time": "x"}\n0.01\n` | `([], [], [], [], {'start_time': 'x'})` | **raises** `TypeError` |

**Mechanism:** `np.loadtxt` on a single value returns a 0-d array; `.T` keeps it 0-d; the 4-way unpack raises `TypeError`,
not `ValueError`. The base's bare `except:` caught it; `except ValueError` does not — the plan's premise ("what the unpack
raises on a wrong column count") does not hold for this one shape.
**Falsified:** plan §3 W3 ("a file whose data rows do not form four columns still returns four empties (today's
behaviour)"), §5 ("non-numeric file → four empties, message, no uncaught exception"), the GREEN body ("rows that are not
four numbers keep today's empties"), and the comment at `output.py` naming "rows that are not four columns".
**Reachable:** `workflow.py:168` calls `read_file` (then `RunCollection.add_from_file`) on every `REFL_<run>_*_partial.txt`
in the output folder; a partial file truncated inside its first data row (a kill, a full disk) now stops the assembly with
an uncaught `TypeError` where the base skipped it as "no points".

**Fix (behaviour; domain = `read_file`'s file shapes — the reproduction covered the 0-d shape, with and without meta):**
every file shape for which the base returned four empties still returns four empties with the same message, and nothing
else changes (the one-row file still returns four scalars, A2). Two candidate code routes the reviewers measured —
`np.loadtxt(file_path, ndmin=1).T` (turns the 0-d case into the existing `ValueError`; every other probed shape unchanged)
or `except (ValueError, TypeError)` — choose either; the guard must vary the shape: add the single value, with and without
`# Meta:`, to `test_read_file_whose_rows_are_not_four_numbers`, so the GREEN of v1 reds it.

## Advisories (non-blocking; carried to the PR body)

Numerical: **A2** `background_fit_weights` builds `out` with `np.full_like(errors, charge)` — integer `errors` would
truncate `charge` and make `np.divide` raise; unreachable (`_d_bck` is `np.zeros` float64, `event_reduction.py:947`) — a
docstring line or `.astype(float)` if the helper is reused; **A3** whether ±inf weights (counts ≠ 0, error 0) should reach
the fit predates this slug (not seen in 902 real fits).
Test: **A1** the extracted helpers' call sites are weakly guarded — `paralyzable_correction(rate, dead_time, 2*tof_step)`
at the call survives the hygiene and dead-time files (the algorithm case asserts finite, ≥ 1, some exactly 1); comparing
`corr` with the base arithmetic on the same rate (`array_equal`) would close it (this seat's byte-identical baseline is
the current guard); **A2** `test_the_paralyzable_dead_time_algorithm_warns_nothing_for_bins_without_events` wraps the
whole `PyExec` in `simplefilter("error")` — failed once in 9 runs under load (not reproduced); narrow it to
`RuntimeWarning`; **A3** contrived survivors: `where=counts > 0` in W1b (no negative counts in the data), a W1 overwrite
for `y > 1e6`; **A4** "no file → `FileNotFoundError` propagates" has no test (path untouched).

— Integrator, Claude Opus 5.5
