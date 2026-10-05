# Plan: `header-scale-factors-per-position` — record the scale factor and wavelength range of each sequence position (F17)

**Campaign:** `exp-review-fixes` · **Leaf:** `header-scale-factors-per-position` → `triage/header-scale-factors-per-position`,
`feature/header-scale-factors-per-position`, `qa/header-scale-factors-per-position`
**Status:** READY — v1 (attempt 1 of N = 3) — dispatched 2026-10-05 under the posture's **stacking by file overlap** rule (`ec10742`,
rule (3)/(5)): the plan's three source files are exactly the files `feature/rereduction-headers-land` (PR #34, v2 PASS, **held by the
human**) changes, and nothing else open touches them → **stacked on that branch at its PASS tip**; "a held stack still builds" ·
**Base:** `agentic/feature/rereduction-headers-land` @ `0831c51` (= `exp-review` @ `7b6d6b9` + M1 `eb79c84` + the v2 fix; **re-sealed there —
§2's line numbers are `0831c51`'s unless marked**) — **overlap at dispatch** (`git diff --name-only agentic/exp-review...agentic/feature/<x>`,
tests excluded, `exp-review` @ `b6b9381`): `feature/rereduction-headers-land` {`new_reduction_from_file.py`, `nr_reduction_calc.py`,
`nr_tools.py`, `save_reduced_data.py`} ∩ **three of this plan's three source files**; `feature/test-suite-warnings` {`background.py`,
`dead_time_correction.py`, `output.py`, `peak_finding.py`}, `feature/launcher-env-outside-xdg-cache`, `feature/editor-notes-and-report-spelling`,
`feature/roi-popout-data`, `feature/roi-estimate`: none · **PR target:** `feature/rereduction-headers-land` on the fork, **draft** (retargeted
to `exp-review` when the human merges #34) · **Stack:** #34 → **this slug**; the Developer cuts `feature/header-scale-factors-per-position`
`--no-track` from `agentic/feature/rereduction-headers-land` and regular-merges it forward before every `qa/` push; the Integrator opens the
draft PR `--base feature/rereduction-headers-land` and names the stack · **Note for the human:** #34's hold ("until after `editor-sections`")
has lapsed — #40 merged 2026-10-05 — so #34 is mergeable at the human's pleasure; this slug builds either way ·
**Depends on:** `rereduction-headers-land` (same functions, same test file) · **Kind:** reduction-path
**Review domains:** numerical-diagnostics, test (block) · D-6 `[human, 2026-10-02: "D-6: this campaign"]`

## Declared scope

**Files in.** `src/lr_reduction/save_reduced_data.py` (`_build_header`, `HEADER_FORMAT`);
`src/lr_reduction/new_reduction_from_file.py` (`read_prior_header`, the vouching of a prior's own entries,
`load_prior_data`, `find_combine_priors`, the two lines of `reduce_from_file` that store the merged values);
`src/lr_reduction/nr_reduction_calc.py` — **`NR_Reduction.reduce()` only**, the lines that record per-position
values; `tests/unit/lr_reduction/test_prior_combination.py`.

**Behaviours in.** Every output file of a sequence states, per sequence position, the scale factor applied to
that position's data and the wavelength range its reduction used — the same in every file, whatever the order
or number of reductions; `null` where no run exists or where the value cannot be known.

**Explicitly OUT.** Any change to a data column; the autoscale algorithm and its duplicated code in
`find_combine_priors`; how `LambdaMinUse`/`LambdaMaxUse` are *chosen* (`nr_reduction_calc.py:387–397`, chopper
band — `chopper-band-unify`); the in-memory shape of `config.LambdaMinUse`/`LambdaMaxUse`; the template path
(`new_reduction_from_template.py`); `web_report.py`; the `_settings.json` written by `save_json`; `field_spec.py`
and the editor (slug `editor-load-fidelity`); `reduction_scripts` (a checker extension is a cross-repo advisory, §10).

## 1. Request and symptom

F17 (`todo-header-scale-factors-per-position.md`, M1 retrospective §3h): after M1, `Run Title`, `Angles` and
`NR_runs` describe each position, but `Config.ScaleFactor`, the `Scaling factors` line and the `Lambda Range`
line still describe **the last call**. Reduction order changes them; the values of the other positions are not
the ones applied to their data. "Identical across runs" was mistaken for "correct" once already.

## 2. Verified facts (trial merge of `eb79c84` into `7b6d6b9`, uvdl3 clone 1, 2026-10-02; **re-sealed 2026-10-05 at `0831c51`** — every `save_reduced_data.py`, `nr_reduction_calc.py`, `web_report.py`, `new_reduce_REF_L.py` and `new_reduction_from_template.py` citation below holds at the base; **moved in `new_reduction_from_file.py`** (M1's v2 fix inserted code): V5's merge-side writes are now `initial_scalefactors[position] *= scale` at **`:513`** (was `:426`), the padding at **`:511-512`** (was `:471-472`), the current call's list `scaling_factors.append(scale)` at **`:509`** and the data scaling at `:505-506` (was `:473`), stored at `:100` as before; `LOG_KEYS` `:19`, `load_prior_data` `:274`, `read_prior_header` `:394` (`ast.literal_eval` of `NR_runs` at `:406`), `own_logs_from_header` `:419`, `read_logs_from_nexus` `:445`, `find_combine_priors` `:461`; the test module's fixtures are as named (`fake_reduce_single_run` `:107`, `SCENARIOS` `:200`, `test_header_format_marker_precedes_config` `:186`, `reverse_q` flag) and **D-5's tests exist** (`test_current_run_wins_at_its_position` `:305`, `test_highest_run_wins_in_any_order` `:455`, `test_remeasured_position_survives_rereduction_of_another_run` `:319`, `test_superseded_file_is_left_in_place` `:465`, `test_shared_position_report_names_the_run_used` `:470`) — the `remeasured` fixture is what §6's re-measured test extends)

| # | Fact | Command → observation |
|---|---|---|
| V1 | The header depends on reduction order | M1's synthetic fixture, combined file `Config.ScaleFactor`: one batch call → `[1, 0.66836664253166, 0.44671396884904385]` (ground truth: every run scaled in that call); per-run in order → `[1, 1.0, 0.44671396884904385]`; `[R3, R1, R2]` → `[1, 0.66836664253166, 1.0025802405958288]`; in order then `R2` again → `[1, 0.66836664253166, 1.0]` |
| V2 | Both header lines are copies of config attributes | `save_reduced_data.py:75` (`scale_factor_header` from `sorted_config.ScaleFactor`), `:85`/`:104` (`Scaling factors`), `:86`/`:105` (`Lambda Range = {LambdaMinUse}Å to {LambdaMaxUse}Å`); upstream's own note at `:76`: "Lambda Use values need to be arrays" |
| V3 | `LambdaMinUse`/`LambdaMaxUse` are scalars of the angle being reduced | set in `_reduce_single_run` (`nr_reduction_calc.py:391–397`), read at `:458`, `:821`, `:1029–1030` |
| V4 | A consumer needs them scalar **in memory** | `web_report.py:448–450` formats `config.LambdaMinUse`/`LambdaMaxUse` with `%6.4g`; autoreduction passes the config returned by `reduce_from_file` (`src/lr_autoreduce/new_reduce_REF_L.py:179–183`) |
| V5 | `Config.ScaleFactor` is an **input** and is overwritten with output | input: `r = r * self.config.ScaleFactor[i]` (`nr_reduction_calc.py:1139–1140`); output: `self.config.ScaleFactor[i] *= scale` in `reduce()` (`:177`), `initial_scalefactors[position] *= scale` on the current call's list (`new_reduction_from_file.py:426`, `:473`), stored at `:100`. A prior position therefore shows `authored × (rescale of this call ≈ 1)`, not what was applied to its data |
| V6 | **CORRECTION** to the todo and charter wording: `check_headers.py` (`reduction.git` @ `lr`, `8ca6c69`) parses only `NR_runs`, `Run Title`, `Angles` and `Config`; it never reads the `Scaling factors` or `Lambda Range` lines. Its A/B compares `config.*` keys **exactly** | `read_header()` and `compare()` in that file (read-only shallow clone) |
| V7 | Applied factors agree across orders only to rounding | V1: `0.4467…` is reached as `0.446… × 1.0025…` when `R3` is reduced first; M1 record: "S3/S4 data agree with S1 to 8e-16 relative" |
| V8 | M1's stub cannot show the wavelength defect as it stands | `fake_reduce_single_run` replaces `_reduce_single_run`, where V3's assignment lives; with settings `LambdaMinUse: 2.5` every scenario prints `2.5Å to 9.5Å` |
| V9 | No reader of the two lines in the subject | `grep -rn 'Lambda Range\|Scaling factors' launcher src` → writers only; `read_prior_header` does not parse them |
| V10 | M1 writes its format marker for every `save_results` caller, the template path included | `_build_header` (`save_reduced_data.py:88`, `:107`); callers `new_reduction_from_template.py:106–124` |
| V11 | Pending upstream overlap (PR #205 @ `8eead58`) | its hunks in `nr_reduction_calc.py` touch `reduce()` at `:110`, `:152`, `:178–180` (numbering of its own merge base `f98ec6c`) — beside the lines this slug edits — and it inserts a header line after `Angles:` in `_build_header`, both branches |

## 3. Design

- **R1 — three more positional records, built exactly as M1 builds its logs.** `scale` (the factor applied to
  the position's data: the authored `ScaleFactor[p]` times every autoscale factor applied since that run was last
  reduced), `lambda_min`, `lambda_max` (the range that run's reduction used). `reduce()` records them per position
  right after each run is reduced (`None` at a gap); `load_prior_data` takes, per position, the current call's
  record or the prior file's own; the merge multiplies the `scale` record of each position by the factor it
  applies to that position's data in this call.
- **R2 — a prior file vouches for these records only with header format 3.** Enumerating the writers: W1
  `reduce()` and W2 the merge rewrite, before this slug, write the *current call's* list into every file they
  touch, and a format-2 header lists the whole set in `NR_runs`, so the writing call cannot be identified — no
  format-2 entry is provably the file's own. W1/W2 after this slug write, at each position, the value from that
  position's source — its own. A prior that cannot vouch gives `null` for `scale`, `lambda_min`, `lambda_max`
  (not re-derived: the NeXus file holds neither, and recomputing the range would state what today's code would
  use, not what was used). The position heals when its run is reduced again, as `ThCen` does. M1's rule for
  `title`/`ths`/`thi`/`ThCen` is unchanged and accepts format 2 or 3.
- **R3 — what is written.** `# Scaling factors = {"scale_factor": [...]}`: per position, `null` allowed.
  `# Lambda Range = {"lambda_min": [...], "lambda_max": [...]}`: per position (was `<min>Å to <max>Å`).
  `# Header format: 3 (...)`, still before `# Config:`. In the `# Config:` JSON, `LambdaMinUse` and `LambdaMaxUse`
  become the per-position lists (were scalars); every other key as today, subject to R4. The marker is 3 only
  when the records are supplied; a caller that supplies none (the template path, V10) gets today's lines.
- **R4 — `Config.ScaleFactor` stays the authored input** (decision F17-1, default). `reduce()` and the merge stop
  writing applied factors into `config.ScaleFactor`; the applied factor lives in the `scale` record only. Reasons:
  the list is multiplied into the data on the next use of the header as a settings file (V5); it has no honest
  value for an unknown position (`null` there raises at `:1139`); and an authored list is bit-identical in every
  order, which the checker's exact comparison needs (V6, V7). The numbers applied to the data do not change.
- **R5 — in memory nothing changes shape.** `config.LambdaMinUse`/`LambdaMaxUse` remain per-call scalars (V4);
  the lists exist in the records and in the serialized header only.
- **R6 — `NR_runs` is written as plain integers** (folded from §11 at the re-seal): `_build_header` writes the run list with the list's
  `repr` (`save_reduced_data.py:79`, `:98`), so a run passed as a numpy integer is written `np.int64(…)`, which `read_prior_header`'s
  `ast.literal_eval` (`new_reduction_from_file.py:406`) rejects — the file can no longer vouch for its own entries. Whatever integer type
  the caller passes (`int`, numpy integer, `str` digits), the header line parses back to a list of `int`; a non-integer run number
  (`float` with a fraction, text) is refused with a message, not written; `None` is a gap. Same file and function this slug edits.

**Types and states.** Position: current call / vouching prior (format 3) / non-vouching prior (format 2,
legacy, unreadable or inconsistent header) / gap / re-measured (the record follows D-5's winner). Autoscale: off
(record = authored); on, first in Q order (factor 1); on with overlap; on with a non-finite estimate (fallback 1).
Authored `ScaleFactor`: empty (reducer default `[1]*n`, `nr_reduction_calc.py:104–105`), all ones, non-trivial,
shorter than the position count (the merge pads with 1 at `new_reduction_from_file.py:471–472`). `LambdaMin`/`LambdaMax`: given per angle /
`None` (chopper-derived). Files: 4-column and `_8col`; partial and combined. Callers of `save_results`: with
records (from-file path) / without (template path).

**Shape changes, exactly** (for `editor-load-fidelity`, which reads `# Config:` through `load_from_file`):

| Where | Before | After |
|---|---|---|
| `# Config:` → `LambdaMinUse`, `LambdaMaxUse` | `float` | `list[float \| null]`, by sequence position |
| `# Config:` → `ScaleFactor` | `list[float]` (authored × last call's autoscale) | `list[float]`, authored — shape unchanged |
| `# Lambda Range =` | `2.5Å to 9.5Å` | JSON object of two per-position lists |
| `# Scaling factors =` | list of the last call | per position; entries may be `null` |
| `# Header format:` | `2` | `3` |
| `_settings.json` (`save_json`), in-memory config | scalars | unchanged |

The editor slug must therefore accept `None`, a float and a list with `null`s for the two runtime-owned fields;
the two slugs share no file.

## 4. Files to change

| File | Change |
|---|---|
| `src/lr_reduction/nr_reduction_calc.py` | `reduce()`: record `scale`, `lambda_min`, `lambda_max` per position beside M1's logs; stop the `:177` write (R4). No other function |
| `src/lr_reduction/new_reduction_from_file.py` | parse the three records from a prior header; vouch per R2; carry them through `load_prior_data`; apply the merge factor to `scale`; stop the `:100`/`:473` writes (R4) |
| `src/lr_reduction/save_reduced_data.py` | `_build_header`: lines and `Config` keys of R3; `HEADER_FORMAT = 3` when records are present |
| `tests/unit/lr_reduction/test_prior_combination.py` | §6; the stub sets `LambdaMinUse`/`LambdaMaxUse` and applies `ScaleFactor[i]` as the real function does; `test_header_format_marker_precedes_config` expects `3` |

## 5. Failure-mode matrix

| Case | Class | Before | Required |
|---|---|---|---|
| Per-run autoreduction in order (S0) | common | position 2 shows `1.0` (V1) | every position shows its applied factor and its range |
| Re-reduce all / one run (S1, S2) | common | depends on the last call | same header as S0 |
| Out of order (S3) | common | positions lost (V1) | same as S0, `scale` within rounding (V7) |
| Whole-sequence batch | common | correct `ScaleFactor`, last angle's range | same as S0 |
| Gap (S5) | edge | list of the last call | `null` at the gap in all three records |
| Autoscale off / authored factors ≠ 1 | edge | authored (correct by accident) | `scale` = authored; `Config.ScaleFactor` = authored |
| Prior written by M1 code (format 2) or legacy | edge | trusted implicitly | `null` for that position until re-reduced; reported |
| Re-measured position (D-5) | edge | — | records of the winning run |
| 8-column files | edge | as 4-column | identical records |
| Header reused as a settings file | edge | autoscale output re-enters as input | loads; `ScaleFactor` is the authored list; list-valued `Lambda*Use` is overwritten before use (`:391–397`) |
| Template-path caller without records | pathological | scalar lines, marker 2 | unchanged lines; never marker 3 |
| Format-3 prior whose lists disagree with `NR_runs` (length, run at position) | pathological | — | not vouched: `null`, reported |
| `web_report` after a list leaked into the in-memory config | pathological | — | impossible by R5; pinned by a test |

## 6. Red-Green TDD seed

In `test_prior_combination.py`, M1's fixtures; physics stubbed as M1 does, with two additions that mirror the
real `_reduce_single_run`: the stub sets `self.config.LambdaMinUse/LambdaMaxUse` from `LambdaMin[i]`/`LambdaMax[i]`
and multiplies `r` by `self.config.ScaleFactor[i]`. Tolerance `rel=1e-9` on `scale` (V7); exact on everything else.
`--timeout=120`. RED observed on the base before any source edit.

| Test | RED observation | GREEN |
|---|---|---|
| `test_scale_record_is_the_same_in_any_order` (M1's `SCENARIOS` + the batch) | in order: `[1.0, 1.0, 0.4467…]` vs batch `[1, 0.6684…, 0.4467…]` | every file of every scenario carries the batch's list |
| `test_scale_record_is_what_was_applied` | — | position file's `R` column ÷ the stub's unscaled `R` = the recorded factor |
| `test_config_scale_factor_is_the_authored_list` (authored `[1, 2, 1]`, and the batch) | batch: `[1, 0.668…, 0.447…]` | authored list in every file, every scenario |
| `test_lambda_range_is_recorded_per_position` | every file prints the last call's scalar | `[2.7, 2.6, 2.5]` / `[9.5, 9.5, 9.5]` in the line and in `Config`, every scenario |
| `test_gap_records_null` | list of the last call | `null` at position 2 in the three records |
| `test_autoscale_off_records_the_authored_factor` | — | `scale` = authored |
| `test_prior_without_format_3_does_not_vouch` (format-2 and legacy priors) then `…heals_when_rereduced` | prior's position shows the current call's value | `null`, a printed notice; canonical after re-reduction |
| `test_inconsistent_format_3_header_does_not_vouch` | — | `null` |
| `test_returned_config_keeps_scalar_lambda_use` | passes already (guard) | `float` |
| `test_template_style_caller_gets_no_format_3_marker` | — | lines as today |
| `test_eight_column_files_carry_the_same_records`; `test_remeasured_position_records_follow_the_winner` | — | as stated |
| M1's and D-5's tests | green | green; only the marker test edited |
| `test_nr_runs_header_round_trips_numpy_integers` (R6): a run passed as `np.int64` → the written line parses back through `read_prior_header` to `int`s; `3.5` / `"x"` refused | red: the line contains `np.int64(` |

## 7. Mutate-once gate

| # | Mutation | Must red |
|---|---|---|
| 1 | a prior position's `scale` taken from the current call's list (today's behaviour) | `test_scale_record_is_the_same_in_any_order[in order]` |
| 2 | merge factor not multiplied into a prior's `scale` | `…in_any_order[out of order]` (the only scenario with a factor ≠ 1 on a prior, V1) |
| 3 | merge factor multiplied twice / applied to the wrong position (Q index for sequence index) | `test_scale_record_is_what_was_applied`; M1's `reverse_q` scenario extended to the record |
| 4 | format 2 accepted as vouching | `test_prior_without_format_3_does_not_vouch` |
| 5 | length / run-at-position check on a format-3 prior removed | `test_inconsistent_format_3_header_does_not_vouch` |
| 6 | `reduce()` keeps `self.config.ScaleFactor[i] *= scale` | `test_config_scale_factor_is_the_authored_list[batch]` |
| 7 | the merge keeps storing applied factors in `config_final.ScaleFactor` | `test_config_scale_factor_is_the_authored_list` |
| 8 | wavelength record taken from the config scalar at write time | `test_lambda_range_is_recorded_per_position` |
| 9 | per-position lists assigned to the in-memory config | `test_returned_config_keeps_scalar_lambda_use` |
| 10 | gap filled with the authored value instead of `null` | `test_gap_records_null` |
| 11 | marker 3 written without records | `test_template_style_caller_gets_no_format_3_marker` |
| 12 | records skipped for `_8col` | `test_eight_column_files_carry_the_same_records` |
| 13 | the integer conversion of `NR_runs` removed (R6) | `test_nr_runs_header_round_trips_numpy_integers` |

**Frame.** Re-pointed: the record dictionary passed to `save_results` (call sites `nr_reduction_calc.py:202`,
`:204`, `:222`, `:224`; `new_reduction_from_file.py:109`, `:111`, `:118`, `:123`) — one row per site in the ledger;
`LOG_KEYS` consumers (`read_prior_header`, `own_logs_from_header`, `read_logs_from_nexus`, `load_prior_data`) — one
row each, stating that M1's four keys behave as before. No hang-mode mutation; `--timeout=120` on every battery
run; chunk under 600 s.

## 8. Acceptance criteria

1. **Gate.** `pixi run test-reduction` from the subject root returns zero at the `qa/` tip (green at the base `0831c51` per the
   Integrator's M1 v2 gate; the Developer re-measures on the base before the first source edit).
2. **Developer (uvdl3).** Base run of the gate command recorded before the first source edit; RED commits, GREEN
   commits; each mutation and its `<test> -> N failed` in the commit body; types and states of §3 stated in the
   commit body before the code; `pixi.lock` restored, not staged; nothing stashed or switched while tests run.
3. **Integrator (analysis clone 2, `reduction_scripts` @ `lr`, `PIXI_CACHE_DIR` exported).**
   a. Baseline from the base commit **`0831c51`** (the stack's base, not `exp-review`), **before gating**: S0–S5 and the 8-column runs, as
      in `rereduction-headers-land` §8.3a — the M1 v2 baseline the Integrator already captured there serves if its base commit is `0831c51`.
   b. `compare_columns.sh` baseline vs `qa/` tip: **identical in every scenario**, 4- and 8-column, combined
      files included (R4 moves a record, not a number).
   c. `check_headers.py` PASS per scenario, and **A/B across orders** — S0 vs S1, S0 vs S2, S0 vs S3 — PASS with
      the checker as it is (`config.ScaleFactor` authored; `config.LambdaMinUse/MaxUse` per position). On the
      baseline the same A/B fails on those keys: record that output as the RED of the deployment-shaped test.
   d. Ground truth (retrospective §3h): each position's `Scaling factors` entry equals the product of that run's
      per-call `Scaling factor:` prints in `transcript.txt` since its last reduction, and agrees across S0–S3 within 1e-9.
   e. Heal: a folder written by the base (format 2) → after one call the other positions show `null`; after a full
      pass the headers equal S0's.
4. **Claims.** "Data unchanged" is the column comparison of 3b, stated per scenario; every other prescriptive
   comment or commit-body claim is checked by its falsifying command or marked inferred.
5. **PR.** Draft, base `feature/rereduction-headers-land` (the stack; retargeted to `exp-review` by #34's merge); body: the shape-change table of §3 verbatim (it is a file-format change for
   anyone parsing `.dat` headers), decision F17-1 as taken, the deploy consequence (charter §5: reaches
   autoreduction only through the human's promotion to upstream `exp`), the overlap with PR #205 (V11). No
   `plans/`, `todo.md` or battery in the diff.

## 9. Learnings relied on (M1 retrospective)

- §3h: "'Identical across runs' is not 'correct'. Check a metadata field against ground truth (here, the per-call
  `Scaling factor:` lines in the transcript) before calling it fine."
- §3f: "For 'can this legacy artifact vouch for itself?', **enumerate the writers**… not the histories."
- §2.2: "`check_headers.py` turned 'eyeball a diff' into I1–I4 plus an A/B idempotency check. It later exposed F17."
- §2.3: "A same-environment baseline, captured before the first source edit."
- §4: "F17: record the cumulative per-position scale factor, and make the λ range a per-position list. Same shape
  as M1, same vouching problem for legacy factors. The numerical reviewer notes it needs its own test."
- §3c: "With an editable install, **the working tree is the runtime**."

## 10. Assumptions and open questions (default in force unless the human says otherwise before dispatch)

- **F17-1 `[human/scientists]` — where the applied factor lives.** Default R4: `Config.ScaleFactor` = authored,
  applied factor in the `Scaling factors` line only. Subset if rejected: keep writing applied factors into
  `Config.ScaleFactor` per position — then unknown positions have no honest value, a header reused as settings
  re-applies stitching factors, and the cross-order A/B needs a tolerance in the checker (V7). Note for the
  scientists: with R4 a whole-sequence batch no longer shows autoscale in `Config.ScaleFactor`.
- **F17-2 — the checker does not see the two lines (V6).** Default: none needed for the charter's "A/B passes"
  (3c); recommended advisory, cross-repo (`reduction.git` @ `lr`, the human pushes): parse the two lines, add
  "one entry per position", compare `scale` with a relative tolerance.
- **F17-3 — legacy single-run headers.** M1's proof (a single-run writer's own entry is its own) also covers that
  call's `ScaleFactor` entry and scalar range. Default: not used — `null` and heal — to keep one vouching rule for
  the new records; an additive extension if real folders show too many `null`s.
- **F17-4 — the `Lambda Range` line becomes JSON.** Default: yes (same form as `Angles:`); no reader in the
  subject (V9). A reader outside it (a scientist's script) is the human's to name.
- **F17-5 — precision.** Factors are written at full precision; equality across orders is asserted with a
  tolerance, never by rounding the record.
- **F17-6 — PR #205.** If `time-slicing-reconcile` lands first, re-measure V11 and re-seal; this slug keeps its
  `nr_reduction_calc.py` hunks inside `reduce()`.
- **Re-seal at dispatch:** every `file:line` above; the fixture names; the D-5 tests this plan extends.

## 11. Inherited at triage (added 2026-10-02; **folded into §3 R6, §6 and §7 row 13 at the 2026-10-05 re-seal** — kept for the record)

- **`NR_runs` must be written as plain integers** (`todo-nr-runs-header-numpy-repr.md`, found by the Developer in
  `rereduction-headers-land`): `_build_header` formats the run list with its `repr`, so a run number passed as a
  numpy integer is written as `np.int64(…)`, which `read_prior_header`'s `ast.literal_eval` rejects — the file can
  then no longer vouch for its own entries. Not reachable through today's three callers (each converts with
  `int()`); it is a latent precondition of `reduce_from_file(run_array=…)`. Behaviour: whatever integer type the
  caller passes, the header line parses back to a list of `int`; a non-integer run number is refused with a
  message, not written. Same file and function this slug already edits. RED: a run passed as `np.int64` →
  the written line contains `np.int64(`; guard: the line round-trips through `read_prior_header`. Mutation: the
  conversion removed → that test reds. Types and states: `int`, numpy integer, `str` digits, `float`, `None` (gap).

## Revision history

v1 — authored 2026-10-02 (staged behind `rereduction-headers-land` merged). **Re-sealed and dispatched 2026-10-05 stacked on
`feature/rereduction-headers-land` @ `0831c51`** under the stacking-by-file-overlap rule (posture `ec10742`; A-72): every
`save_reduced_data.py` / `nr_reduction_calc.py` citation holds; `new_reduction_from_file.py`'s merge-side citations moved (`:426` → `:513`,
`:471-472` → `:511-512`, `:473` → `:505-509`); D-5's tests named; §11's `NR_runs` item folded in as R6 with its test and mutation; the
baseline is the stack's base. The human's hold on #34 has lapsed with #40's merge (noted in the header).
