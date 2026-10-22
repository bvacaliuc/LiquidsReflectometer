# Plan: `landing-l1-scaling-factor-split` — fork #27's scaling-factor test fix and reference repair (with #21's test hygiene) leave L1 for their own PR on upstream `exp-next`, and the stack follows L1 again

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l1-scaling-factor-split` (K19; refs `triage/landing-l1-scaling-factor-split`; the slug amends `feature/landing-l1-core` by commits on top — no
rewrite — and tags `qa/landing-l1-scaling-factor-split` for Phase 1; Phase 2 re-tags `qa/landing-l2-reduction`, `qa/landing-l3-launcher`, `qa/landing-l4-model-move`, `qa/log-level-console` at the
forward-merged tips, as K17 did) · **Status:** **Phase 1 `-> qa @ `2ab688f`** (L1‴; D-150; at the Integrator's gate); **Phase 1b delivered** (the series `plans/scaling-factor-split-series/` + its record, A/B/C reproduced; D-2 measured: `c4d20e4` not seat-admissible, the series is the transport); **D-4 met** (the human deleted the five consumed `qa/` tags, 2026-10-22, A-193) — Phase 2 after Phase 1's PASS; dispatched **v1 (attempt 1 of N = 3)**, 2026-10-22 (A-191) on the human's addressed word `[human, 2026-10-22 (to the Analyst): "I worked out a
step with the Advisor to affect feature/landing-l1-core: would you please dispatch the scaling-factor split."]` — the step is the Advisor's V1-78 (the human's L1 review request, measured) ·
**Base:** `feature/landing-l1-core` @ **`cca2986`** (L1″, K17 Phase 1 PASS; a current lock and the fork's guard — pushable; upstream `exp-landing-l1-core` is at the same sha, #219 green) ·
**PRs:** #54 and upstream #219 advance by fast-forward (the human pushes L1‴ to `exp-landing-l1-core` again); the split's own PR is **the human's**, against upstream `exp-next` (Phase 1b, B4);
#51/#52/#53/#55 fast-forward in Phase 2 · **Reviews:** design, test (block); numerical-diagnostics n/a (the slug moves #27's already-reviewed content; the A/B/C evidence rides in the PR body) ·
**Gate:** Phase 1 — G literal on L1‴ (expected 10 + 116: 21 collected items leave — eight `def`s, two of them parametrised; corrected at D-150, A-193), P1 over `c4d20e4..`, P2 (`Reverts:` accepted); Phase 1b — the series apply-clean on `c4d20e4` and the
A/B/C table reproduced; Phase 2 — per layer as K17's, with the proofs against R-5 (§10 D-3).

Campaign: exp-review-fixes

## Declared scope

**Phase 1 (L1, commits on top of `cca2986`):** `git revert ad8eba6` (fork #27, `compare every scaling-factor field, not error_b against itself`: the two reference files and the
every-field comparison) and `git revert 0a18419` (fork #21, `give each scaling-factor test its own output directory`: 10 lines of test hygiene) — measured clean in that order on
`cca2986` (A-191); after them `tests/data/sf_197912_Si_auto.cfg`, `tests/data/sf_197912_Si_dt_par_46_300.cfg` and `tests/test_scaling_factors_workflow.py` are **byte-equal to upstream
`c4d20e4`** (the whole-tree change is exactly those three files, 55+/251−), so L1 has no diff at all in the scaling-factor files — "truly core" by the scientists' test (V1-78). Eight tests
leave `test-reduction` (the file has 13 tests at L1″, 5 at upstream). **No `src/` change anywhere in this slug.**
**Phase 1b (the split's PR, the human's; may run in parallel with Phase 1):** a **ledger-carried patch series** `plans/scaling-factor-split-series/` — `0001` = `0a18419` (#21), `0002` =
`ad8eba6` (#27), `git format-patch` from a scratch cherry-pick onto upstream `exp-next` `c4d20e4` (measured clean, A-191) — with a record `plans/scaling-factor-split-series.md` (base
`c4d20e4`, sha256s, the `git am --3way` line, "the human: apply, push, open the PR to upstream `exp-next`") and the PR body's material (§3 B4). The transport is K17 Phase 1b's, for the
same reason: upstream's bare tip is not a pushable base for a seat (its lock is stale against its manifest — `pixi install --locked` exit 1, upstream's pre-push `pixi lock --check`
rewrites it; `todo-seat-branch-base-needs-a-pushable-tip.md`), **but unlike `next` the tests can be run at this tip** — the Advisor's `scripts/sf-split-measure.sh` form (the clone's
existing env, `PYTHONPATH=<worktree>/src`, from `tests/`): A `c4d20e4` + the series → 26 passed; B with upstream's two `.cfg` → 3 failed; C `c4d20e4` as is → 5 passed (V1-78). The
Developer re-measures admissibility at dispatch (D-2): if `pixi install --locked` and the pre-push hooks pass at `c4d20e4` after all, the branch `feature/scaling-factor-split` and a draft
PR → the fork's `exp-next` replace the series.
**Phase 2 (the stack follows, gated tips only, in order — K17's shape):** R-5 = R-4 `24e1646` + the two reverts in R's layout (D-3); L2‴ = L2″ `6fbec95` + merge of the gated L1‴; L3‴ =
L3″ `c5cd3e4` + merge of L2‴; L4‴ = L4″ `d53942d` + merge of L3‴; K10‴ = K10″ `ceb77ff` + merge of L1‴. No later layer or stacked branch touches the three files (`git log cca2986..<tip>` = 0
for L2″, L3″, L4″, K10″, K8 `0108214`, K9 `e62aeb3`, K14 `f1e0f78` — A-191), so the merges should be clean; #56/#57/#58 are re-checked `MERGEABLE` at L1‴ and forward-merged only on a
reported conflict. Each re-gated: G; L2‴'s harness against R-5 (the files are test-only — byte-identity expected); L3‴ P3 and L4‴ P3 `--move` against R-5 with K11's `EXCL`; P5.
**Precondition for Phase 2's deliveries (D-4):** the five consumed `qa/` tags (I-139/I-142/I-143/I-144/I-145) are still live on the fork — a tag cannot move without a forced push, which
the guard forbids, and the seats' deletes are refused by the harness classifier (I-140) — **the human deletes them before Phase 2 delivers** (K8's `qa/launcher-suite-crash-isolation` too,
for hygiene; K8 itself is not re-tagged by this slug).
**Out:** any `src/` change; #27's open slit-matching follow-up (`TOLERANCE = 0.07`; the `1, 0, 0, 0` fall-through — a real scaling-factor question for the scientists, unchanged by this
split; the PR body names it); a port to upstream `next` (the Advisor's 2 — only on the human's word; the test file is moved and edited there, `79d60a5`); K16/K18.

## 1. Request and symptom

The human, reviewing L1 file by file, to the Advisor (V1-78, verbatim there): three files differ from upstream — the two `sf_197912_*.cfg` and `test_scaling_factors_workflow.py` —
"Would it be possible to split this change out also, so that feature/landing-l1-core is *truly* a core change? The scientists will object to the 'changing' of scaling factors as part of
upstream#219 review and will want it in its own PR so that its merit can be reviewed separately." The Advisor measured (V1-78): no code that computes a scaling factor changes; what
changes is what the test expects — upstream's `check_results` compares `error_b` with itself, so two wrong references passed (row 1's hand-typed `S1W`/`S2iW` in `_auto.cfg` since
`41a095c`; `_46_300.cfg` byte-identical to the `_46_200` file); #27 compares every field and repaired the references with values upstream's own code computes. Then the human's word
to the Analyst (the status line): dispatch.

## 2. Verified facts at `cca2986` (2026-10-22 14:4xZ; this clone, a scratch worktree removed after; V1-78's measurements)

| # | Fact | Evidence |
|---|---|---|
| V1 | L1's commits on the three files after K17: `0a18419` (#21), `a70a3e2`/`b1a32fc` (#23 and its K17 revert — net nothing), `ad8eba6` (#27: `_auto.cfg` 2 lines, `_46_300.cfg` 25, the test file 239+/43−) | `git log c4d20e4..cca2986 -- <the three>` |
| V2 | `git revert --no-commit ad8eba6 0a18419` on `cca2986` is clean (an auto-merge in the test file); the three files then byte-equal to `c4d20e4`; the whole-tree change = the three files, 55+/251− | A-191 (scratch worktree) |
| V3 | `git cherry-pick --no-commit 0a18419 ad8eba6` onto `exp-next` `c4d20e4` is clean (the three files, 251+/55−) | A-191 |
| V4 | `test_scaling_factors_workflow.py` holds 13 `def test_` at `cca2986`, 5 at `c4d20e4` — **but two of the eight are parametrised: the file's collected items go 26 → 5, so 21 leave G's reduction count (137 → 116)**; v1's "eight leave, 129" counted defs, not items (corrected at D-150, A-193) | `grep -c 'def test_'`; D-150's G |
| V5 | No later layer or stacked branch touches the three files: L2″, L3″, L4″, K10″, K8, K9, K14 all 0 commits on them past `cca2986`; R-4 carries 5 (exp-review's history) | `git log cca2986..<tip> -- …` |
| V6 | `c4d20e4` → `cca2986` differs in `pixi.lock` (+27) and `pyproject.toml` (+32): upstream's bare tip is not a seat-pushable base (the rule, D-129/A-169) | `git diff --stat` |
| V7 | A `c4d20e4` + `ad8eba6` alone: 26 passed; B with upstream's `.cfg`: 3 failed (row 1 `S1W` 19.952 vs 19.992; `tof_300` row 0 `a`; the pairwise-distinguishable test); C `c4d20e4` as is: 5 passed — the test fix and the reference repair are one change | V1-78, `scripts/sf-split-measure.sh` |
| V8 | The fork's `exp-next` = upstream's `exp-next` = `exp` = `c4d20e4`; upstream `exp-landing-l1-core` = `cca2986` (#219 green); the five consumed `qa/` tags still live | `ls-remote` at 14:4xZ |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | **Revert commits, not rewrites:** two `git revert`s on `cca2986` (`Reverts: ad8eba6`, `Reverts: 0a18419`, each with a `Split: V1-78 — the scaling-factor test fix and reference repair move to their own PR on upstream exp-next` line); after them `git diff c4d20e4 <L1‴> -- tests/data/sf_197912_Si_auto.cfg tests/data/sf_197912_Si_dt_par_46_300.cfg tests/test_scaling_factors_workflow.py` is empty. |
| B2 | **G at L1‴:** `test-reduction` 10 + 116 (the 21 every-field items gone — eight defs, two parametrised; measured D-150; upstream's five pass by their `error_b`-only check); `pre-commit run --all-files` green; `pixi.lock` untouched. |
| B3 | **The series carries exactly #21 then #27** (two patches; `0001` the output-directory hygiene, `0002` the every-field comparison and the two repaired references); applied by `git am --3way` on `c4d20e4` it reproduces V3's tree; the A/B/C table reproduced by the Developer with the Advisor's probe (A 26 passed, B 3 failed, C 5 passed). |
| B4 | **The PR body's material** (in the record, for the human): no `src/` change — the scaling-factor path (`scaling_factors/*`, `utils.py`, `dead_time_correction.py`, `types.py`) byte-identical to upstream; what changes is what the test expects; the A/B/C table; the two wrong references and their provenance (PR #27's forensics: `REF_L_197919` logs 19.952/19.950; the `_46_300` file was a copy of `_46_200`); #27's open slit-matching follow-up named as unchanged. |
| B5 | **Phase 2** as K17's: R-5 then the forward merges, each gated; the three files identical to the reference at every tip (they are test-only); the side branches re-checked `MERGEABLE`. |
| B6 | **Proofs:** P1 L1's set unchanged (the three files are L1's); P2 accepts `Reverts:`; P3 against R-5 with K11's `EXCL` — exact, nothing excluded. |

## 4. Files to change

| File | Change |
|---|---|
| `tests/data/sf_197912_Si_auto.cfg`, `tests/data/sf_197912_Si_dt_par_46_300.cfg`, `tests/test_scaling_factors_workflow.py` | byte-equal to `c4d20e4` (B1) |
| ledger `plans/scaling-factor-split-series/0001-*.patch`, `0002-*.patch`, `plans/scaling-factor-split-series.md` | the series and its record (B3, B4) |
| `feature/landing-reference-5` (new branch) | R-5 = R-4 + the two reverts in R's layout (D-3) |
| L2‴/L3‴/L4‴/K10‴ merge commits | Phase 2 (B5) |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: the reverts | the three files byte-equal to `c4d20e4`; G 10 + 129 | T1, T3 |
| 2 | common: the series | apply-clean on `c4d20e4`; A/B/C reproduced | T4 |
| 3 | edge: the test file's auto-merge (#21's lines inside #27's rewrite) | `git revert` is hunk-exact (V2: clean); the Developer names any manual resolution | T1 |
| 4 | pathological: `c4d20e4` admissible after all (`install --locked` passes) | the branch + a draft PR replace the series (D-2); the record says which | T4 |
| 5 | pathological: a Phase 2 re-tag refused (the old `qa/` tag still live) | precondition D-4 — the human's deletes first; the Developer reports the refusal, never forces | D-4 |
| 6 | pathological: P3 run against R-4 | red on the three files; the reference of the day is R-5 (D-3) | T6 |
| 7 | out of scope: the slit-matching follow-up; a `next` port | the human's word | — |

## 6. Red-Green seed

- **T1** `git diff --stat c4d20e4 <L1‴> -- tests/data/sf_197912_Si_auto.cfg tests/data/sf_197912_Si_dt_par_46_300.cfg tests/test_scaling_factors_workflow.py` → empty; `git diff --stat cca2986 <L1‴>` = exactly the three files.
- **T2** `git log c4d20e4..<L1‴> -- <the three>` shows the four replay/revert pairs net to nothing (#23 and #27/#21 each reverted).
- **T3** G at L1‴: `install --locked`, the lock check, `test-reduction` 10 + 116 (the counts reported; v1 said 129 — defs, not items), `pre-commit run --all-files` rc 0.
- **T4** The series: `git am --3way` of `0001`–`0002` on a fresh `c4d20e4` worktree rc 0, tree equal to V3's; the record's sha256s match; the probe's A/B/C (26 passed / 3 failed / 5 passed) reproduced and recorded; admissibility of `c4d20e4` measured and recorded (D-2).
- **T5** (Phase 2, R-5) `git diff c4d20e4 <R-5> -- <the three>` empty; `git diff --name-only 24e1646 <R-5>` = the three files.
- **T6** (Phase 2) at each of L2‴, L3‴, L4‴, K10‴: G; L2‴'s harness identical to R-5's; L3‴ P3 and L4‴ `--move` against R-5 rc 0 with K11's `EXCL`; P5; #56/#57/#58 `MERGEABLE` at L1‴.

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| one of the three files left at L1″'s content | T1 |
| the series built without #21 (or without #27) | T4 (the tree differs from V3's; B fails to fail) |
| a Phase 2 tip merged from an ungated predecessor | T6 (the predecessor's PASS cited) |
| P3 against R-4 | T6 red (row 6) |

## 8. Acceptance criteria

1. Phase 1: T1–T3; the commits with the trailer and the provenance lines, no campaign identifiers; the Integrator's PASS on `qa/landing-l1-scaling-factor-split`; #54 fast-forwarded; the human pushes L1‴ to `exp-landing-l1-core` (#219).
2. Phase 1b: T4; the series and its record on the ledger; the human applies it on upstream `exp-next`, pushes `feature/scaling-factor-split` to their fork and opens the PR with B4's material.
3. Phase 2: T5, T6 at each tip; #51/#52/#53/#55 fast-forwarded; R-5 named in the group plan's revision history.

## 9. Learnings relied on

V1-78 (every measurement of the change's meaning and the A/B/C table; the probe); K17's plan and record (the in-place leaf, the series transport, Phase 2's shape, R-4's rule); A-169/D-129
(base admissibility); I-140 (the classifier refuses tag deletes — the human's precondition).

## 10. Decisions

- **D-1 — the split takes #21 with #27** (the Advisor's 1): L1 then has no diff in the three files; #27 does not need #21 (A ran without it), the human's PR carries both as two commits.
- **D-2 — the PR's transport is the ledger-carried series by default;** the Developer measures `c4d20e4`'s admissibility at dispatch (a locked install and the pre-push hooks in a seat clone) and, only if it passes, pushes `feature/scaling-factor-split` and opens the draft PR → the fork's `exp-next` instead; either way the upstream PR is the human's.
- **D-3 — the reference for Phase 2 is R-5 = R-4 + the two reverts in R's layout**, a new branch `feature/landing-reference-5` (references immutable once named); `EXCL` unchanged (K11's set) — P3 exact.
- **D-4 — the human deletes the five consumed `qa/` tags before Phase 2's deliveries** (a tag cannot move without force; the seats' deletes are refused); the Developer never forces a tag.
- **D-5 — reverts and merges, never rewrites.**
- **D-6 — no `next` port in this slug** (the Advisor's 2): the file is moved and edited on `next`; a port is its own word, like K17's series was.

## Revision history

- **v1 — 2026-10-22 (A-191):** authored at dispatch on the human's addressed word; the step from V1-78. Sealed against L1″ `cca2986`, upstream `exp-next` `c4d20e4` (= the fork's), R-4 `24e1646`, L2″/L3″/L4″/K10″ `6fbec95`/`c5cd3e4`/`d53942d`/`ceb77ff`; the measurements of §2 V2–V5 made in a scratch worktree of this clone, removed after.
- **v1 note at dispatch — 2026-10-22 (A-191), on V1-79:** the Advisor's intake hand-off `requests/l1-scaling-factor-split.md` (the human's words verbatim, the measured facts, the proposed shape, the two choices) landed minutes after this plan; checked against it: both of the human's defaults are what this plan takes (#21 travels with #27, D-1; the PR's base is `exp-next`, not a `next` port, D-6). One shape difference, explained by the base rule: the Advisor's "a standalone draft PR on the fork" is D-2's conditional branch; the default transport is the ledger-carried series because upstream's bare tip is not a seat-pushable base. The L1 reverts are two commits (one per source commit) rather than the Advisor's one, for per-commit `Reverts:` provenance.
- **Phase 1 `-> qa`, Phase 1b delivered, D-4 met — 2026-10-22 (A-193):** D-150: L1‴ `2ab688f` = `cca2986` + `31b1fd9` (`Reverts: ad8eba6`) + `2ab688f` (`Reverts: 0a18419`), each with a `Split:` line; T1 empty over the three files, the whole-tree change exactly them; G 10 + 116 exit 0 (serial, 15:14–15:20Z; a first run concurrent with the A/B/C probe was void — upstream's form of `test_compute_sf_with_deadtime` writes a shared `/tmp/sf_197912_Si_test_dt.cfg`, the race #21 fixed and L1‴ now carries again; learning 14); P1/P2 clean; D-83. **Correct-and-flag on this plan:** the expected count was defs, not collected items — 21 leave, not eight (V4/B2/T3/Gate corrected). Phase 1b: the series `plans/scaling-factor-split-series/0001`–`0002` + `plans/scaling-factor-split-series.md`; `git am --3way` on a fresh `c4d20e4` rc 0; the three files equal L1″'s; A/B/C 26 / 3 / 5 reproduced serially (and `0002` alone 26 / 3 / 5); `c4d20e4` measured not seat-admissible (`install --locked` exit 1; pre-push `pixi lock --check`) — the series is the transport, the local branch removed. **D-4 met:** `[human, 2026-10-22 (to the Analyst): "I deleted the five qa tags on the fork."]` — verified at 15:32Z: no `qa/landing-l2-reduction`, `-l3-launcher`, `-l4-model-move`, `log-level-console`, `launcher-suite-crash-isolation` on the fork (the first command the Advisor handed over had run against the ledger, V1-82; the location-free `gh api -X DELETE` form did it). Live: `qa/landing-l1-scaling-factor-split` @ `2ab688f`, `triage/landing-l1-scaling-factor-split` for Phase 2. Phase 2 proceeds at the Integrator's PASS.
- **Staged, not applied — 2026-10-22 (A-194), on V1-83 (the human's question to the Advisor, input):** the human asked whether later phases carry (a) a PR on `next` for the restored file's bug and (b) a PR stackable on L1 before L2–L4. As written: neither — (a) is D-6's `next` port (its own word), (b) is not in Phase 1b (the series targets upstream `exp-next`, independent of L1). **Measured by the Advisor:** `git am --3way` of the same two patches on L1‴ `2ab688f` is clean (3 files, 251+/55−), and L1‴ is seat-pushable, so **(b) is ready as Phase 1c on the human's word:** `feature/scaling-factor-split` = `2ab688f` + `0001`–`0002` (`git am --3way`; the same content as the series), pushed by the Developer, draft PR → `feature/landing-l1-core` (#54) in the shape of #56/#57; the series stays for the human's upstream `exp-next` PR; L2–L4/K10 unaffected (V5); attempt count unchanged; the gate: the branch's diff from `2ab688f` equals the series' tree, G at the branch tip (10 + 137 expected — the 21 items return), P2. **(a) is staged as K20** `scaling-factor-split-next-port` (a ledger-carried series ported to `next`'s layout, as K17's was — `next`'s test file is moved and edited, `79d60a5`; `next` is not seat-admissible, the PR's CI is the test gate), its plan at the word. Neither changes this plan's binding content until an addressed word (the Advisor files `requests/` on it, V1-80's practice).
