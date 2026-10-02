# Plan: `rereduction-headers-land` — land M1 (re-reduction headers by sequence position) and D-5 (highest run number wins a re-measured position)

**Campaign:** `exp-review-fixes` · **Leaf:** `rereduction-headers-land` → `triage/rereduction-headers-land`,
`feature/rereduction-headers-land`, `qa/rereduction-headers-land` · **Status:** v2 (retry 1 of N = 3; v1 rejected at `review/rereduction-headers-land` @ `4617053` — test-only, see Revision history)
**Base:** `agentic/exp-review` @ `7b6d6b9` · **PR target:** `exp-review` on the fork, **draft**
**Depends on:** — (file-disjoint from every `editor-*` / `roi-*` slug) · **Kind:** reduction-path
**Review domains:** numerical-diagnostics, test (block) · **Retry cap:** N = 3
**Sources:** charter §3 row and §4 (reduction-path definition of done); D-5 (charter §6); the M1 record
(`tasking:lr_reduction-exp-maintenance:plan/rereduction-headers/{plan,retrospective}.md`); `todo-rereduced-position-which-run-wins.md`.

Canonical copy: ledger `plans/rereduction-headers-land-plan.md`; the copy on `triage/rereduction-headers-land`
is byte-identical at dispatch.

## Declared scope

**Files in.** By the merge of M1 (`eb79c84`, unchanged): `src/lr_reduction/new_reduction_from_file.py`,
`src/lr_reduction/nr_reduction_calc.py` (`NR_Reduction.reduce()` bookkeeping, 18 lines),
`src/lr_reduction/nr_tools.py` (`clean_log_value`), `src/lr_reduction/save_reduced_data.py` (format marker),
`tests/unit/lr_reduction/test_prior_combination.py`. By new work (D-5): `new_reduction_from_file.py`
(`load_prior_data`, `sort_runs`, at most one small helper) and `test_prior_combination.py` — nothing else.

**Behaviours in.** (A) M1 lands as it is: a regular merge commit of `eb79c84`. (B) D-5 `[human, 2026-10-02:
"D-5: highest run number wins, as suggested"]`: at a sequence position measured more than once, the run with the
highest run number supplies that position's data **and** header entries, whatever the order of reduction; the
superseded partial file is left in place; the strict xfail becomes a passing test.

**Explicitly OUT** (a finding here is a PR-body advisory, or a todo — not a rejection): M1's design, already
reviewed (plan §9 of the maintenance record) — only demonstrated reachable harm reopens it; F17 (`Scaling factors`,
`Lambda Range`, `Config.ScaleFactor`: slug `header-scale-factors-per-position`); the template path
(`new_reduction_from_template.py`); the duplicated stitch code in `find_combine_priors`; `reduce()` writing no
partial files when a batch raises part-way (M1 §9, recorded tradeoff); deleting or renaming superseded or misnamed
files; a misnamed legacy copy that is the *only* file at its position; any edit to `nr_reduction_calc.py`,
`save_reduced_data.py` or `nr_tools.py` beyond what the merge brings; `reduction_scripts`; upstream.

## 1. Request and symptom

M1 `[human, 2026-09-30]`: autoreduction reduces each run alone and merges it with the partial files in
`new_reduction/`. On the base, data are merged by sequence position but `# Run Title:` / `# Angles:` are "the
longest prior list + the current run", so re-reducing duplicates entries, out-of-order reduction drops them,
`NR_runs` names only the last run, and a gap crashes `load_prior_data`. M1 fixes this on `exp` @ `9aaaefa`; it is
not an ancestor of `exp-review`. D-5: with M1 alone, a re-measured step keeps the newer run only while it is the
current call — re-reducing another run restores the stale one, because the first prior file in name order is used.

## 2. Verified facts at the base tip (uvdl3 clone 1, 2026-10-02)

| # | Fact | Command → observation |
|---|---|---|
| V1 | Base still has the defect | `git grep -n 'key=len' agentic/exp-review -- src/lr_reduction/new_reduction_from_file.py` → lines 334–337 (`max(..., key=len)`); no `test_prior_combination.py` on the base |
| V2 | M1 = 5 commits on `9aaaefa`, 5 files, +558/−47 | `git log agentic/exp-review..eb79c84` → `03d91ca f80e9ec 90253b8 36cb813 eb79c84`; `git diff --stat agentic/exp-review...eb79c84` |
| V3 | M1 merges cleanly into the base | `git merge --no-commit --no-ff eb79c84` in a detached worktree at `7b6d6b9` → "Automatic merge went well"; 4 files changed on both sides, 0 conflict hunks (`git merge-tree 9aaaefa agentic/exp-review eb79c84`). **CORRECTION:** `git merge-tree --write-tree` (retrospective §2.6; `plans/upstream-add-time-slicing-plan.md` intake step 2) does not exist in git 2.34.1 on uvdl3 (`fatal: unknown rev --write-tree`) — use the worktree trial merge or the three-argument form |
| V4 | On the trial merge M1's tests pass | `pytest tests/unit/lr_reduction/test_prior_combination.py` → `33 passed, 1 xfailed in 6.44s` |
| V5 | M1's diff carries no scaffolding | `git diff --name-only agentic/exp-review...eb79c84 \| grep -E '^plans/\|todo\.md\|scripts/'` → empty |
| V6 | D-5 defect, measured on the trial merge | `reduce_runs([R1, R2, R3, R2B, R1])` → combined `NR_runs == [221472, 221473, 221474]` (stale `221473`; `R2B = 221475`) |
| V7 | Where the stale run comes from | merged tree `new_reduction_from_file.py`: `find_priors` returns `sorted(os.listdir(...))` order (:239); the position loop takes the current call first (:328) else `prior_seq_nums.index(i+1)` — the **first** prior (:334–335); the warning prints `run_nums[0]` (:318) |
| V8 | "Current call wins" is order-dependent | prototype with highest-among-priors only: `[R1,R2,R3,R2B,R2]` → `[…, 221473, …]`; then reducing `R1` → `[…, 221475, …]` |
| V9 | Two runs at one position **in one call**: the argument order decides | `sort_runs(group_runs([R2B, R2, R3]))["run_nums"]` → `[None, 221473, 221474]`; with `[R2, R2B, R3]` → `[None, 221475, 221474]` (`map2 = dict(zip(...))`, :173; the other run is silently not reduced) |
| V10 | A legacy folder with misnamed copies already loses a run | pre-fix Q-order naming leaves `_1_<R2>` and `_2_<R1>` beside the true files; reducing `R3` on the trial merge → `NR_runs == [221472, 221472, 221474]`, two warnings; "highest wins" alone would give `[221473, 221473, 221474]` (inferred from the candidate sets, not run) |
| V11 | The true position of a run is in its NeXus file | `group_runs` reads `entry/DASlogs/BL4B:CS:Autoreduce:Sequence:Num/value` (:188–203 merged); `read_logs_from_nexus` already opens the same file under `updated_config.NEXUSpathRB` (:405) |
| V12 | The autoreduce caller does not index the current run | `src/lr_autoreduce/new_reduce_REF_L.py:179–181`: `generate_ref_plot(output[0], run_number_list)` zips the two returned lists |
| V13 | Pending upstream overlap (PR #205 @ `8eead58`) | `git merge-tree f98ec6c eb79c84 8eead58` → **2 new conflict hunks in `save_reduced_data.py`** (both insert a header line after `Angles:`); `nr_reduction_calc.py` and `new_reduction_from_file.py` auto-merge. D-5 edits neither `save_reduced_data.py` nor `nr_reduction_calc.py` |
| V14 | The gate is green on the clean base | `pixi run test-reduction` at `7b6d6b9` (uvdl3 clone 1) → exit 0: launcher stage `145 passed in 12.44s`, reduction stage `251 passed in 513.72s`. **CORRECTION:** the three `test_web_report.py` failures the M1 record carries from `9aaaefa` (F14) do not exist on `exp-review` — there is no pre-existing failure to excuse |

Expected at the `qa/` tip: launcher `145 passed`; reduction stage `251` + M1's `34` (the former xfail now passing)
+ the new tests of §6, nothing failed, skipped or xfailed that the base does not have. The reduction stage takes
about nine minutes and arms no timeout of its own.

## 3. Design

### Part A — land M1 by merge (no re-authoring)

1. `git fetch agentic exp-fix-rereduction-headers`; require `git rev-parse FETCH_HEAD` = `eb79c84e983e7e62e6bd153bac746129cc470fef`
   (moved → STOP, record in `todo.md`; a moving input is a new intake).
2. On `feature/rereduction-headers-land` (cut `--no-track` from `agentic/exp-review`): `git merge --no-ff eb79c84e983e7e62e6bd153bac746129cc470fef`
   — a regular merge commit; never squash, cherry-pick or rebase (the five commits and their bodies are the record).
3. `git diff --stat HEAD^1 HEAD` lists exactly the five files of V2; run V4's command (expect 33 passed, 1 xfailed).

### Part B — D-5, as behaviour

- **B1 — one rule for every candidate.** For each sequence position, the candidates are the run of the current
  call at that position (if any) and every prior file found for that position. The **highest run number** among
  the candidates wins; data, `title`/`ths`/`thi`/`ThCen`, `NR_runs` and the rewritten file name all come from
  the winner. The current call no longer wins by being current (V8): reducing a superseded run leaves the newer
  run in the combined output. Run numbers compare as integers, never as file-name text.
- **B2 — a candidate must belong to the position.** Only when a position has candidates for more than one run:
  each prior candidate's run is checked against its NeXus sequence number (V11; the current call's position
  already comes from there). A file whose run belongs to
  another position is a misnamed legacy copy: excluded and reported by name. If the NeXus file cannot be read,
  the candidate stays (it cannot be disproved) and that is reported. Without B2, B1 lets a misnamed copy displace
  a fresh reduction (V10) — harm M1 does not have.
- **B3 — the same rule inside one call.** `sort_runs` keeps the highest run number when a call names two runs of
  one position, whatever the argument order, and reports the run it leaves out (V9).
- **B4 — report.** One line per shared position, keeping M1's wording `sequence position <p> has files for runs
  [<sorted runs>]` (pinned by `test_two_runs_at_one_position_are_reported`), ending with the run actually used.
- **B5 — nothing is deleted.** The superseded run's partial file stays, as its own call wrote it.

**Types and states the changed path acts on.** Position: empty (gap → `None`, unchanged); one run (current or
prior — unchanged, must stay byte-identical); two or more runs — current newer / current older / all priors / both
in the call / three runs. Prior file: header format 2; legacy single-run; legacy multi-run; misnamed legacy copy;
4-column and `_8col` sets (`find_priors` matches one set per call — the rule applies to both). Run numbers: `int`
from the file-name regex and numpy integers from HDF5; different digit counts (`99999` vs `100000`: name order and
numeric order disagree). NeXus for a candidate: present / missing / lacking the log.

**Writers of the artifact the rule trusts** (a partial file's name claims "run *r* is at position *p*"):
W1 `NR_Reduction.reduce()` (`nr_reduction_calc.py:201–204` merged) names by `i+1`, the position `sort_runs`
aligned — correct; W2 the merge rewrite (`new_reduction_from_file.py:107–111` merged) names by sequence number
since M1 — correct; W2-legacy, the pre-fix rewrite, named by Q-order index — **the only writer that can misname**,
hence B2; W3 `new_reduction_from_template.py:106–124` writes `…_partial` / `…combined_data` names that
`find_priors`' pattern does not match — not a prior source.

## 4. Files to change

| File | Change |
|---|---|
| (merge) five files of V2 | as in `eb79c84`, untouched |
| `src/lr_reduction/new_reduction_from_file.py` | `load_prior_data`: B1, B2, B4; `sort_runs`: B3; optional pure helper for "which run wins a position" |
| `tests/unit/lr_reduction/test_prior_combination.py` | remove the xfail marker; the tests of §6; `remeasured` fixture gives `R2B` a distinguishable Q grid |

## 5. Failure-mode matrix

| Case | Class | Before (trial merge) | Required |
|---|---|---|---|
| Every position has one run (S1–S5, all M1 scenarios) | common | correct | **unchanged**: same headers, same file set, data columns byte-identical |
| Step re-measured; newer run reduced last; another run re-reduced later | common | stale run returns (V6) | newer run stays |
| Superseded run re-reduced after the newer one | edge | superseded run wins until another call (V8) | newer run stays; superseded file rewritten by its own call only |
| Two runs of one position in one call, descending arguments | edge | lower run reduced, higher silently dropped (V9) | higher reduced; the other reported |
| Three runs at a position | edge | first in name order | highest |
| Run numbers of different digit count | edge | name order (`100000…` sorts before `99999…`) | numeric highest |
| `_8col` set | edge | same defect in the 8-column files | same rule, same headers as the 4-column files |
| Legacy misnamed copies sharing positions (V10) | pathological | a run appears twice, one lost | each run at its true position; copies reported |
| Ambiguous position, a candidate's NeXus unreadable | pathological | n/a | candidate kept, reported; highest wins; no exception |
| Misnamed copy alone at a position | pathological | used as named | unchanged (OUT; PR-body advisory) |
| `agentic/exp-fix-rereduction-headers` moved off `eb79c84` | pathological | n/a | STOP before merging |

## 6. Red-Green TDD seed

All in `tests/unit/lr_reduction/test_prior_combination.py`, with M1's fixtures (`env`, `remeasured`,
`reduce_runs`, `read_outputs`, `write_legacy_file`); physics stubbed exactly as M1 does (`_reduce_single_run`),
everything else real. Run with `--timeout=120`. RED is observed on the merge commit, before any D-5 source edit.

| Test | RED observation (trial merge) | GREEN |
|---|---|---|
| `test_remeasured_position_survives_rereduction_of_another_run` (marker removed) | `[221472, 221473, 221474] != [221472, 221475, 221474]` | passes |
| `test_highest_run_wins_in_any_order` — orders `[R1,R2,R3,R2B,R2]`, `[R2B,R1,R2,R3]`, `[R1,R2B,R3,R2,R1]` | first order: position 2 is `221473` | `NR_runs`, title, THS at position 2 are `R2B`'s **and the Q column of position 2's file is `R2B`'s grid** |
| `test_superseded_file_is_left_in_place` | passes already (guard) | file `…_2_221473_autoreduction.dat` still present |
| `test_shared_position_report_names_the_run_used` | message ends `using run 221473` | ends with the winner |
| `test_misnamed_legacy_copy_does_not_take_a_position` (V10 folder, reduce `R3`; and reduce `R1` against a misnamed `_1_<R2>`) | `[221472, 221472, 221474]` | `[221472, 221473, 221474]`; the copy named in the output |
| `test_unreadable_nexus_keeps_the_candidate` (`R2B`'s NeXus file removed after its reduction, then reduce `R1`) | n/a (new path) | no exception; position 2 is still `R2B`; the unverifiable candidate is reported |
| `test_unshared_positions_do_not_consult_nexus` (reduce `R1,R2,R3`; remove the NeXus files of `R2`,`R3`; re-reduce `R1`) | passes already (guard) | same headers as M1's canonical pass; no B2 report line |
| `test_two_runs_of_one_position_in_one_call` — arguments in both orders | `[R2B, R2, R3]` reduces `221473` | `221475` in both orders; the other run reported |
| `test_three_runs_at_one_position`, `test_run_numbers_compare_as_integers` | first in name order | highest |
| `test_eight_column_set_follows_the_same_rule` | 8-column files carry the stale run | same as the 4-column files |
| M1's 33 tests | green | green, unmodified except the marker (`test_current_run_wins_at_its_position` still passes: its current run is the higher one) |

The `remeasured` fixture must make `R2B`'s stub curve differ in its **Q grid**, not by a factor: `AutoScale` is on
in the fixture settings and absorbs a multiplicative difference, so a scaled copy cannot show whose data were used.

## 7. Mutate-once gate

Each row: apply the mutation to the source, record `<test> -> N failed` in the commit body, restore, verify by
symbol. A row that leaves the suite green is a missing guard — add the test first.

| # | Mutation | Must red |
|---|---|---|
| 1 | winner = lowest (or first found) instead of highest | `…survives_rereduction_of_another_run`, `test_highest_run_wins_in_any_order` |
| 2 | current call always wins (B1's comparison removed) | `test_highest_run_wins_in_any_order[R1,R2,R3,R2B,R2]` |
| 3 | header entries from the winner, data from another candidate (and the reverse) | the Q-grid assertion |
| 4 | B2 disabled | `test_misnamed_legacy_copy_does_not_take_a_position` |
| 5 | B2 treats an unreadable NeXus as misnamed (drops the candidate) | `test_unreadable_nexus_keeps_the_candidate` |
| 6 | B2 compares against the wrong position (off by one) | `test_highest_run_wins_in_any_order`, `test_misnamed_legacy_copy_does_not_take_a_position` |
| 6b | B2 runs for every position (the "more than one run" condition removed) | `test_unshared_positions_do_not_consult_nexus` |
| 7 | `sort_runs` back to argument order | `test_two_runs_of_one_position_in_one_call` |
| 8 | run numbers compared as text | `test_run_numbers_compare_as_integers` |
| 9 | rule skipped when `eight_col` | `test_eight_column_set_follows_the_same_rule` |
| 10 | report prints the first run, not the winner | `test_shared_position_report_names_the_run_used` |
| 10b | **(v2)** the in-call report (`sort_runs`) names only the winner, not the run it leaves out | `test_two_runs_of_one_position_in_one_call`, both argument orders |
| 11 | superseded file removed | `test_superseded_file_is_left_in_place` |

**Frame.** A helper introduced for "which run wins" gets one row per call site (`load_prior_data`; `sort_runs`
if it shares the helper). No decorator, sentinel or re-pointed helper is planned; if one appears, add its row.
No mutation above can hang; `--timeout=120` still applies to every battery run. Chunk under the 600 s ceiling.

## 8. Acceptance criteria

1. **Gate.** `pixi run test-reduction`, run from the subject root, returns zero at the `qa/` tip (V14: the base is
   green, so any failure is this slug's).
2. **Developer (uvdl3; no `/SNS`, no harness).** Before the merge: the literal gate command on the clean branch,
   exit status and counts recorded. After the merge: V4 reproduced. Then RED commits (tests only), GREEN commits,
   mutation rows in commit bodies. `pixi run ruff check` on the two files: no new finding against the merge commit.
   `pixi.lock` restored, not staged. No `git stash`/`checkout`/`switch` while a test run is in flight.
3. **Integrator (analysis clone 2; `PIXI_CACHE_DIR` exported; `reduction_scripts` @ `lr`).**
   a. **Baseline first, from the base commit:** with the checkout at `7b6d6b9`, run the M1 scenarios through
      `multiple.sh` (`PIXI_PREFIX=<clone> PIXI_ENVIRON=lr_reduction`): S0 one in-order pass; S1 `LOOPS=2`; S2
      `RUNS="221472 221473 221474 221473"`; S3 `RUNS="221474 221472 221473"`; S5 `RUNS="221472 221474"`; S4 and the
      8-column runs as recorded for `tryfinal-S4` / `lr_reduction_base.try8col-*` under `reduction_scripts/2026-09-25A/`
      (the directory the baselines are actually in — `todo-charter-p7-baseline-path.md`; the charter's `2026-09-25/` is a slip).
   b. **Environment proof:** `compare_columns.sh` of that baseline against `2026-09-25A/lr_reduction.trybase-S*` (and one S1
      run of the deployed `lr_reduction_exp` env) → identical; a difference is a finding about the base or the
      environment, filed before gating, and the new baseline is then the reference.
   c. **At the `qa/` tip:** `check_headers.py` I1–I4 PASS in S0–S5 and the 8-column runs; its A/B (try1 vs try2)
      identical in S1 and in S2, as M1 recorded (maintenance plan §9). Headers of S3/S4 may differ from S1's **only** in
      `Config.ScaleFactor`, `Scaling factors` and `Lambda Range` — F17, the next slug's; list those differences in the
      PR body. Any other header difference blocks.
      `compare_columns.sh` against (a): identical in S0–S4 and in S5's partial files, 4- and 8-column (S5's combined
      file differs by design: the base crashes there). Heal: a copy of the base's S1 folder, re-reduce 221473 then
      221472 → headers equal S0's.
   d. D-5 has no real-data scenario in the canary sequence (no repeated step): say so in the PR body.
4. **Claims.** Every prescriptive comment or commit-body claim is checked by the command that would falsify it,
   or marked inferred. "Data unchanged" is stated as "in every scenario tested", with the by-design exceptions
   (S5 combined; Q order ≠ sequence order) in the same sentence.
5. **PR.** Draft, base `exp-review`; body names M1's five commits and D-5, the measured V13 overlap with PR #205,
   the OUT list as advisories, and the deploy consequence (charter §5): this reaches autoreduction only through
   the human's promotion to upstream `exp`; merging to `exp-review` changes the review deployment after the
   human re-deploys. The diff carries no `plans/`, `todo.md` or battery.

## 9. Learnings relied on (M1 retrospective, `tasking:lr_reduction-exp-maintenance:plan/rereduction-headers/retrospective.md`)

- §2.2: "Encode the invariant as a checker before fixing anything… `compare.sh` strips `#` lines, so it could
  never have seen this class of bug."
- §2.3: "A same-environment baseline, captured before the first source edit… made 'data columns unchanged' a
  code-versus-code statement."
- §2.4: "Red tests that stub only the physics. Grouping…, `reduce()` bookkeeping, the merge and header I/O are all
  real code."
- §3c: "With an editable install, **the working tree is the runtime**. Never stash, checkout or switch while jobs run."
- §3f: "For 'can this legacy artifact vouch for itself?', **enumerate the writers**… not the histories."
- §3g: "State the claim as 'in every scenario tested', and name the by-design exceptions in the same sentence."
- §3e: "Never `pgrep -f` a pattern that appears in the waiting command itself."

## 10. Assumptions and open questions (each with the default this plan proceeds under)

- **A1 — reading of D-5.** "Highest run number wins" is applied to the current call as well as to priors (B1),
  because only that is order-independent (V8). Subset if the human prefers it: the current call always wins and
  the highest prior wins otherwise — drop B1's comparison, mutation 2 and the first order of
  `test_highest_run_wins_in_any_order`; B2 then stays as hardening.
- **A2 — B2 and B3 are inside the slug.** B2 because B1 without it creates reachable harm (V10); B3 because the
  decision is about the position, not about the call shape. If a gate rules either out of scope it becomes a
  child leaf at v1 with `Seed:` this plan.
- **A3 — S4's recipe and the 8-column recipe** are taken from the Integrator's `2026-09-25A/` record, not restated
  here (not readable from uvdl3).
- **A4 — the deployed `lr_reduction_exp` is still the `9aaaefa` build** M1 compared against; if it moved, 3b's
  deployed comparison is informational and the base-commit baseline is the reference.
- **A5 — PR #205 intake** will meet two more conflict hunks after this lands (V13); resolution there: keep both
  header lines, `Header format` before `Config:`.
- **A6 — run time.** The gate's reduction stage runs ~9 min with no timeout armed (V14); mutation batteries run
  the one test file (`--timeout=120`), not the gate.

## Revision history

v1 — this document as dispatched at `triage/rereduction-headers-land` @ `c3d61ca` (Analyst, 2026-10-02).

### v2 — 2026-10-02 (retry 1; the work order for `triage/rereduction-headers-land-v2`)

**Rejection.** `review/rereduction-headers-land` @ `4617053` — `todo.md` at that commit: one blocking finding,
test domain, one line. Not infrastructure. B3 says `sort_runs` "reports the run it leaves out"; the only assertion
on that half is `assert str(R2) in out` (`tests/unit/lr_reduction/test_prior_combination.py:553` @ `30f5a7a`), and
`reduce_from_file` always prints `Beginning run set […]` with every run of the call
(`new_reduction_from_file.py:53`), so the line passes whatever the report says. Verified by the Analyst at
`30f5a7a`: the line, the unconditional print, and the report text at `:195-196`. **The gap was also this plan's:**
§6 asked for "the other run reported" without saying what output could tell a report from the call's own echo,
and §7 had no row for a report that omits the left-out run (row 10b now).

**What stands (do not redo; `todo.md` "What passed").** Everything under `src/` — v2 changes **no** production
line (`git diff 30f5a7a..<v2 tip> -- src/` must be empty, which lets the Integrator reuse this cycle's harness and
numerical evidence); the M1 merge; all twenty recorded mutation rows.

**What changes (tests and battery only).**

| # | Change | RED / proof it can fail |
|---|---|---|
| W1 | In `test_two_runs_of_one_position_in_one_call`, replace the vacuous line with an assertion on the **whole report line** — the sorted runs of the position and the run reduced — for both argument orders. The Integrator's checked form: `assert f"this call names runs [{R2}, {R2B}] at sequence position 2; reducing run {R2B} only" in out`. | under mutation 10b (the report names only the winner): **2 failed**; unmutated: the file's 50 pass (the Integrator's measurement — reproduce it and record yours) |
| W2 | Battery: add row 10b; its recorded count goes in the commit body. | — |
| W3 (recommended, same class) | `test_three_runs_at_one_position` asserts nothing about the shared-position report. Assert that it names all three runs, sorted, and the run used (B4's wording, whatever the code prints at `30f5a7a` — read it, do not assume this plan's sentence). A mutation that drops one run from that report must red it; record the row. | record RED under that mutation |

**Types and states the changed assertions act on** (amendment 18 — the prescription is a string): the report
prints a Python list of integers, so the asserted text depends on the run numbers being `int` and on the sort
being numeric — both pinned already (`test_run_numbers_compare_as_integers`); two runs (W1) and three runs (W3);
both argument orders (W1). An assertion that matches any substring also present in `Beginning run set […]`, or in
a file name, is the same defect again: each new assertion is shown to fail under its mutation before it is trusted.

**Acceptance (v2).** The gate from the repository root; `todo.md` removed from the feature branch in its own
commit before `qa/`; no change under `src/`; W1–W2 (and W3 if taken) with their mutation counts in the commit
body. The PR body carries the advisories of `todo.md` verbatim (A-1 the unguarded `max(chosen, default=0)`; A-2;
A-3 the reverse directions of rows 3a/3b; A-4; A-5; the numerical reviewer's four notes, including the corrected
sentence "B2 adds no NeXus read for unshared positions") — none is in this revision's scope.
