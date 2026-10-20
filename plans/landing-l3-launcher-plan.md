# Plan: `landing-l3-launcher` — layer 3 of `stratified-landing`: the launcher lane (the September ports, the settings editor and its Qt-free model, the ROI pop-out, the time-resolved tab) replayed, sanitized, onto `feature/landing-l2-reduction`; the stack's proof against the reference

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l3-launcher` (refs `triage/landing-l3-launcher`, `feature/landing-l3-launcher`, `qa/landing-l3-launcher`) ·
**Status:** READY — v1 (attempt 1 of N = 3) — **dispatched 2026-10-20 (A-135) on L2's Integrator PASS** (I-98: `landing-l2-reduction` v1 @ `3ea92cf` PASS — RP empty vs R,
G 10 + 374, byte-identity on 8 harness scenarios with the must-fail proven, reviews advisory; draft PR #51 on L1); authored staged 2026-10-20 (A-134). The group plan is **`plans/stratified-landing-plan.md`**; this file is the leaf's work order ·
**Base:** `agentic/feature/landing-l2-reduction` @ **`3ea92cf`** (the PASS tip, I-98; re-sealed at dispatch: unmoved since `qa/`) — cut: `git checkout -B feature/landing-l3-launcher --no-track
agentic/feature/landing-l2-reduction`; merge it forward before every `qa/` push if it moves · **Overlap at dispatch:** the stack (L1 → L2) only ·
**PR target:** `feature/landing-l2-reduction` on the fork, **draft** (stacked) · **Depends on:** L2's PASS; R = `feature/landing-reference` @ `da2b889` ·
**Review domains:** design, test (block); ui-aspects (advise) · **Kind:** launcher + the three Qt-free model modules (in place; L4 moves them) — not
reduction-path (nothing under `src/lr_reduction/` but the model modules and their tests).

Campaign: exp-review-fixes

## Declared scope

**Files in.** `launcher/**` beyond the harness files L1 owns (`launcher/apps/{direct_beam, overplot, settings_editor, roi_dialog, time_resolved}.py`,
`launcher/{app_identity, launcher, new_launcher, runtime_env}.py`, `launcher/tests/*` incl. `conftest.py` and `test_harness.py` hunks of #37/#42, the
test data fixtures); the three model modules `src/lr_reduction/{settings_document, field_spec, roi_estimate}.py`;
`tests/unit/lr_reduction/{test_settings_document, test_roi_estimate}.py`; **`scripts/test/roi_estimate_mutations.py` and `scripts/test/README.md`** (#44's battery, which
`test_roi_estimate.py:479/586/626` run — D-100; D-3 amended A-136, option A).

**Behaviours in.** (1) The twenty entries below replayed in the fork's order, one commit per fork PR (R1; `scripts/landing-replay.sh`, `-p` pathspecs
for the three split entries), `Replays:` and the originals' trailers carried; `.github/`, `scripts/test/measure_fit_path_dependence.py` (D-3 as amended: the one battery nothing runs) and artefacts excluded. (2) **The
stack's proof** (P3): `scripts/landing-proof.sh feature/landing-l3-launcher da2b889` → (a) no difference outside the exclusion list, (b) the name-only
diff exactly the reference's excluded set — `.github/workflows/test_and_deploy.yml` and `scripts/test/measure_fit_path_dependence.py` (two paths). (3) **Coverage** (P4): `scripts/landing-purity.sh --census
9aaaefa c7741b2 <L1> <L2> <L3 tip>` → **0 UNASSIGNED** (every first-parent entry replayed or excluded). (4) The gate green on its own: `pixi run
test-reduction` — the full suite now (the editor, ROI and time-resolved launcher tests join). (5) P1 (`landing-l3-launcher`), P2 clean; the
mutation evidence on the **ledger**, not in the upstream-bound bodies (I-97).

**Explicitly OUT.** The model-module move (L4); any file of L1/L2 beyond the hunks the entries below carry into launcher-owned files;
`scripts/test/measure_fit_path_dependence.py` (D-3: no consumer); behaviour changes — including dropping or editing the three battery tests (option B, the human's scope word only).

## Entries to replay (the fork's order; `M` [`B`])

| # | Entry | Fork PR | What | Files (scope) |
|---|---|---|---|---|
| 1 | `246a0da` [`46b05c0`] | #16 | port: CD dialog resize | `launcher/apps/direct_beam.py`, `launcher/tests/test_cd_dialog_resize.py` |
| 2 | `3810314` [`37d29e4`] | #17 | port: overplot axes + refresh | `launcher/apps/overplot.py`, `launcher/tests/{test_overplot_axes, test_overplot_refresh}.py`, `launcher/tests/data/{db_fixture, refl_fixture}.txt` |
| 3 | `3e0fda5` [`ac68cc1`] | #18 | port: settings persistence (`app_identity`, `launcher.py`, `new_launcher.py`) | `launcher/{app_identity, launcher, new_launcher}.py`, `launcher/apps/{direct_beam, overplot}.py`, `launcher/tests/test_settings_persistence.py` |
| 4 | `a4efd95` [`378e323`] — **only** `launcher/apps/settings_editor.py`, `launcher/new_launcher.py`, `launcher/tests/test_settings_editor.py`, `src/lr_reduction/{field_spec, settings_document}.py`, `tests/unit/lr_reduction/test_settings_document.py` | #28 (split; its `reduction_domains.py`, `nr_reduction_calc.py`, `nr_tools.py` hunks are L1's) | the settings-editor tab on a Qt-free model | those six |
| 5 | `4e5f669` (direct) | — | cosmetic comment above the editor tab | `launcher/new_launcher.py` |
| 6 | `c34c8c5` [`c236a96`] | #33 | editor load fidelity | editor + model + the two tests |
| 7 | `e313f38` [`acd6ff9`] | #35 | editor angle count | editor + model + the two tests |
| 8 | `b86237b` [`bd30e9f`] | #36 | drop-down editors | editor + model + the two tests |
| 9 | `2324e5c` [`ed663f7`] | #37 | launcher test teardown | `launcher/tests/{conftest, test_harness}.py` |
| 10 | `8bec251` [`3c4ec39`] | #38 | editor defaults and theta | editor + model + the two tests |
| 11 | `5a8742d` [`0cc96e1`] | #39 | editor paths header | editor + model + the two tests |
| 12 | `b6b9381` [`efa1b81`] | #40 | editor sections | editor, `field_spec.py`, the two tests |
| 13 | `e7b8524` [`771847b`] — **whole** (A-136): `src/lr_reduction/roi_estimate.py`, `tests/unit/lr_reduction/test_roi_estimate.py`, `scripts/test/roi_estimate_mutations.py`, `scripts/test/README.md` | #44 | ROI pop-out data (Qt-free) with the battery its tests run | those four |
| 14 | `d1a9b3a` [`779f787`] | #43 | editor notes and report spelling | editor, `settings_document.py`, the two tests, `launcher/tests/data/REFL_229197_settings-try1-start-from-scratch.json` |
| 15 | `eb255b4` [`8ca43ce`] | #45 | editor IPTS inference | editor, `settings_document.py`, the two tests |
| 16 | `35e52b2` [`6104958`] | #47 | ROI pop-out dialog | `launcher/apps/{roi_dialog, settings_editor}.py`, `launcher/tests/{test_roi_dialog, test_settings_editor}.py` |
| 17 | `34dc1b9` [`5e2e195`] — **only** `launcher/apps/time_resolved.py`, `launcher/{new_launcher, runtime_env}.py`, `launcher/tests/{conftest, test_runtime_env, test_time_resolved}.py` | #48 (split; #42 inside it) | the time-resolved tab; `MPLCONFIGDIR` node-local (#42) | those six |
| 18 | `62e21d1` (direct) | — | the tab order (upstream #205's) | `launcher/new_launcher.py` |
| 19 | `1bffee1` (direct) | — | the tab-order test fixed (I-93) | `launcher/tests/test_time_resolved.py` |
| 20 | `c7741b2` [`4eec8d5`] — **only** `launcher/apps/{roi_dialog, settings_editor}.py`, `launcher/tests/{test_settings_editor, test_time_resolved}.py`, `tests/unit/lr_reduction/test_settings_document.py` | #49 (split; its L1 and L2 hunks are replayed there; `scripts/test/measure_fit_path_dependence.py` excluded) | the noqa sweep's launcher/model hunks | those five |

"editor + model + the two tests" = `launcher/apps/settings_editor.py`, `launcher/tests/test_settings_editor.py`, `src/lr_reduction/{field_spec,
settings_document}.py`, `tests/unit/lr_reduction/test_settings_document.py` (an entry may touch a subset; replay the entry's whole diff — every file
of these entries is L3's).

## Red-Green seed (the checks)

| # | Check | RED at the start |
|---|---|---|
| P1 | `scripts/landing-purity.sh landing-l3-launcher <base> <tip>` → `clean` | — |
| P2 | `scripts/landing-sanitize-check.sh <base> <tip>` → `clean` | — |
| P3 | `scripts/landing-proof.sh <tip> da2b889` → (a) and (b) pass | fails at the base (every L3 file differs from R) and until entry 20 |
| P4 | `--census 9aaaefa c7741b2 <L1> <L2> <tip>` → 0 UNASSIGNED | 17 UNASSIGNED at the base (D-97) |
| G | `pixi run test-reduction` green at the tip — the full suite; `pixi install --locked` + `scripts/pixi_lock_check.sh` exit 0 in a clean worktree (D-83) | — |
| RP | the running proof per entry: `git diff --stat <tip> da2b889 -- <that entry's files>` empty after each entry | — |

## Mutate-once gate

| Mutation | Must red |
|---|---|
| entry 16 (#47) left out | P3 (a) (`roi_dialog.py`), P4 (`35e52b2` UNASSIGNED) |
| entry 4's `reduction_domains.py` hunk replayed again here | P1 (`src/lr_reduction/reduction_domains.py` stray) and P3 (a) (doubled hunk) |
| #49's `scripts/test/measure_fit_path_dependence.py` replayed | P2 (`ARTEFACT`), P3 (b) — strict since A-136: the diff must equal the reference's excluded set, so a replayed excluded file (absent from the diff) fails (b) |
| #44's battery left out again (v1's D-3) | G red on the three battery tests (D-100's measurement); P1 silent, P3 (a) names the two files |
| entries 18–19 swapped with 17 (order) | RP after 17 (`new_launcher.py` differs) — chronological order is load-bearing |
| #49's L3 hunk left out | P3 (a) (`settings_editor.py` differs by the tag lines), P4 (`c7741b2` only partly replayed: the per-entry census) |
| a replay commit without `Replays:` | P2 |

## Acceptance criteria

1. `feature/landing-l3-launcher` with the replay commits (one per fork PR; entries 5, 18, 19 as their own commits), `Replays:` naming each original.
2. P1, P2 clean; P3 (a) and (b) pass; P4 0 UNASSIGNED; RP empty per entry; G green; `pixi.lock` unchanged.
3. The `qa/landing-l3-launcher` tag at the tip; the mutation evidence on the ledger.
4. The Integrator re-runs P1–P4 from the ledger's scripts and G in a clean worktree; opens the draft PR `--base feature/landing-l2-reduction` and names the
   stack (L1 → L2 → this); the body carries P3's two outputs verbatim (the proof of the whole stack).
5. The PR body: the replay table, the two splits (#28, #48) and #49's hunks, the exclusions (the workflow and the one battery nothing runs; the other battery is in because its tests run it — D-3 as amended), the suggested upstream order (L3 of four)
   and the overlap with upstream's open #181–#202 (D-6) — this layer supersedes #188–#193/#196/#198's launcher content.

## Revision history

v1 — authored 2026-10-20 (A-134) while L2 sat at `qa/` (`3ea92cf`); **staged**, dispatching on L2's PASS with the base SHA re-sealed. Entry lists measured
from the first-parent diffs at the base census (A-126) and re-measured here; #49's L3 hunks are what L1 (D-94) and L2 (D-97) left.

v1 dispatched 2026-10-20 (A-135) on I-98 (L2 PASS @ `3ea92cf`); base re-sealed at that SHA; entries unchanged. The replay helper and the trailer check
were normalised by the Developer before this layer (D-98, `todo-landing-replay-trailers-not-normalised.md`); the Integrator pins their new blob ids.

v1 amended at build 2026-10-20 (A-136), **STOP lifted:** D-100 measured that #44's battery `scripts/test/roi_estimate_mutations.py` is run by three tests, so
D-3's exclusion and "green on its own" could not both hold; option A (the Developer's and the Integrator's recommendation) adopted as the Analyst's amendment of
its own default — the consumed battery and its README are L3's (entry 13 replayed whole), the exclusion list narrows to the workflow and
`scripts/test/measure_fit_path_dependence.py`, the tools follow (`EXCL`, the sanitize rule, the proof's pathspecs), and P3 (b) is strict (the diff must equal the
reference's excluded set). The human may reverse it (then B, dropping the three tests, is a scope word and a v2). The Developer re-runs the driver with the
decided pathspecs and continues to `qa/`; nothing pushed changes. Also recorded (D-100): the commit hook's `RUF100` rule, carried by L1, rewrites unused
`noqa` tags in pre-#49 replay commits; the Developer kept the hook's fixes and the final proof is the arbiter — a plan-design fact for the retrospective.
