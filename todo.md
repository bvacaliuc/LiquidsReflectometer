# todo.md — Integrator rejection, `rereduction-headers-land` v1 @ 30f5a7a (review gate: test domain)

**Verdict: REJECT — one blocking finding, test-only, one line.** Gate cycle: v1 → `review/rereduction-headers-land`
(retry 1 of N=3). The production code is correct and everything else passed. The fix touches only
`tests/unit/lr_reduction/test_prior_combination.py` and the mutation battery.

## What passed (do not redo)

- **Gate** `pixi run test-reduction` from the subject root, analysis clone 2, 15:14–15:25 EDT: launcher **145 passed**,
  reduction **301 passed**, 699 warnings (= the base), **exit 0**. Matches the GREEN commit.
- **Scope**: the plan's five files; no ledger-shaped path. M1 merge `eb34eaa`: no manual resolution; M1's change set
  is identical through the merge (Behaviour A).
- **Harness (§8.3a–c, deployment-shaped)**, from a per-SHA worktree env:
  - Base 7b6d6b9 baseline reproduces 2026-09-25A byte for byte (data + masked headers).
  - At 30f5a7a, `check_headers.py` I1–I4 PASS in S0, S1, S2, S3, S5, 8-col S0/S2/S5 and the heal; no tracebacks
    (the base crashed in S3/S5).
  - `compare_columns.sh` vs the base is identical in S0–S3 and S5's partials, 4- and 8-column. S5's combined file
    differs by design: 64 rows, `NR_runs = [221472, None, 221474]`; the base kept 33 rows, `[None, None, 221474]`.
  - A/B headers: S1 = S0. S2, S3 and the heal differ from S0 only in `config.LambdaMinUse` and `config.ScaleFactor`
    (F17; identical to M1's 2026-09-25A record).
- **Numerical-diagnostics reviewer: PASS.** The winner supplies data and headers on every path (partials, combined,
  8-column). Integer comparison holds. B2's sequence mapping has no off-by-one. F6 is equivalent (the `NEXUSpathRB`
  overrides in 63 real settings files all name their own IPTS). RED 14/35 and row 6 = 11 re-executed.
- **Test reviewer: all 20 recorded mutation rows re-executed → exact counts.** The stub rule is obeyed (only
  `_reduce_single_run` is stubbed).

## BLOCKING — the B3 report is unguarded: `assert str(R2) in out` cannot fail

**Where.** `tests/unit/lr_reduction/test_prior_combination.py:553`, in `test_two_runs_of_one_position_in_one_call`.
**Declared behaviour.** Plan §3 B3: `sort_runs` keeps the highest run "**and reports the run it leaves out** (V9)".
V9's defect was that the other run was *silently* not reduced, so the report is half of B3.
**Why the line is vacuous.** `reduce_from_file` always prints `Beginning run set [221475, 221473, 221474]`
(`new_reduction_from_file.py:53`), which contains `221473` whatever the report says. Row F4 only proves the report
line exists; nothing proves it names the left-out run.

**Reproduction** (Integrator, independently of the test reviewer; `git archive 30f5a7a` scratch copy, the import
verified to resolve to the copy):
- mutant `new_reduction_from_file.py:195` `{sorted(set(runs), key=int)}` → `{[map2[seq]]}` (the report names only
  the winner) → `test_two_runs_of_one_position_in_one_call` **2 passed**; the whole file 50 passed.

## Fix (prescribed and checked)

Replace line 553 with:

```python
    assert f"this call names runs [{R2}, {R2B}] at sequence position 2; reducing run {R2B} only" in out
```

Checked on scratch copies: unmutated 30f5a7a → **50 passed**; under the mutant above → **2 failed** (both argument
orders). Add the mutant to the battery as a row ("sort_runs report omits the left-out run → 2 failed").

**The guard's dimension.** It varies argument order (both parametrized legs). The run *set* is fixed at two runs; the
three-run case (`test_three_runs_at_one_position`) has no report assertion. Optional, recommended: assert its report
names all three, sorted.

**Re-gate economy.** If v2 changes nothing under `src/` (`git diff 30f5a7a..<v2> -- src/` empty), the Integrator
reuses this cycle's harness and numerical evidence and re-runs only the gate and the test review.

## Advisories (non-blocking; carried to the PR body)

Test reviewer:
- A-1 `new_reduction_from_file.py:358` `highest_seq_num = max(chosen, default=0)` has no row. `max(candidates)`
  survives; it matters only when the *highest* position holds nothing but misnamed copies (a trailing `null` in
  `NR_runs`). Guard: an F7 variant with the all-misnamed position on top.
- A-2 Data provenance in the combined file is asserted only through the position-2 partial (`:465`, `:585`). It is
  built from the same `sorted_data`; an explicit combined-Q assertion would be clearer.
- A-3 Rows 3a/3b record one direction only. The reverse (this call wins; data or logs taken from a prior file) was
  measured at 2 failed each. Record them in the battery.
- A-4 The battery has no F2 row (cosmetic). A-5 `sort_runs` `map3` from the first entry is an equivalent mutant
  (`group_runs` splits on seq_id).

Numerical-diagnostics reviewer:
- "No NeXus file is read for unshared positions" should read "B2 adds no NeXus read for unshared positions": M1's
  legacy fallback `read_logs_from_nexus` still opens NeXus for an unvouched unshared winner (unchanged).
- F6 is equivalent in every caller, not unconditionally: only an `override_params["NEXUSpathRB"]` naming a second
  directory could diverge (not reachable; real files checked).
- An improvement worth a PR-body line: losing prior files are no longer `np.loadtxt`-ed, so a corrupt loser no
  longer raises.
- A string run number would compare against itself (`find_priors` would not exclude the call's own file). No caller
  passes one (`new_reduce_REF_L.py:177` ints it); it sits with `todo-nr-runs-header-numpy-repr.md`.

— Integrator, Claude Opus 5.5
