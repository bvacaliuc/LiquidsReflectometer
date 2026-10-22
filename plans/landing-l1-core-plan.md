# Plan: `landing-l1-core` — layer 1 of `stratified-landing`: the fork's harness and core fixes replayed, sanitized, onto upstream `exp` at its tip

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l1-core` (refs `triage/landing-l1-core`, `feature/landing-l1-core`, `qa/landing-l1-core`) ·
**Status:** READY — v1 (attempt 1 of N = 3) — **dispatched 2026-10-20 (A-128)** on the K6 trigger (#49 merged 2026-10-20 01:56Z, `c7741b2`, I-94) under
the charter row of 2026-10-19 (the human's word, V1-58). The group plan is **`plans/stratified-landing-plan.md`** (v1, re-sealed at this dispatch): this
file is the leaf's work order and repeats nothing it does not need to ·
**Base:** **upstream `exp` @ `8971999`** (`neutrons/LiquidsReflectometer`, read-only; fetched by URL — the fork's `exp` branch is stale at `d51e935` until
the human fast-forwards it, group plan §3 R0 i, which the Integrator needs for the draft PR's `--base exp`, not the Developer for the cut) — cut:
`git fetch https://github.com/neutrons/LiquidsReflectometer.git 8971999 && git checkout -B feature/landing-l1-core --no-track 8971999` · **Overlap at
dispatch:** no open feature branch on the fork (every campaign PR merged; #49 `c7741b2`) — clause (2) · **PR target:** the fork's `exp` (after R0 i),
**draft** · **Depends on:** nothing · **Review domains:** design, test (block) · **Kind:** harness + core fixes (not reduction-path: no reduction
behaviour changes; L2 carries those).

Campaign: exp-review-fixes

## Declared scope

**Files in.** `pyproject.toml`, `pixi.lock` (as the replayed entries left them), `.pre-commit-config.yaml`, `scripts/check_lock_format.sh`,
`scripts/pixi_lock_check.sh`, `docs/developer/developer.rst` (#20), `launcher/tests/__init__.py` (#15), `launcher/tests/conftest.py`,
`launcher/tests/test_harness.py`, `tests/conftest.py`, `tests/test_noqa_tags.py` (#49), `tests/**` touched by the entries below;
`src/lr_autoreduce/{new_reduce_REF_L.py, reduce_REF_L.py}` and `src/lr_reduction/{instrument_settings.py, new_reduction_template_reader.py,
reduction_template_reader.py, time_resolved.py, web_report.py}` (#49's comment-only hunks — core files no later layer owns, D-93/A-130); `src/lr_reduction/{template.py, new_reduction_from_template.py, background.py, dead_time_correction.py, output.py, peak_finding.py}`;
`src/lr_reduction/reduction_domains.py` (new) with the two call-site hunks in `nr_reduction_calc.py` and `nr_tools.py` (split from #28); #14's
mechanical ruff baseline across `launcher/` and `src/` (the declared purity exception: its replay commit's subject carries `purity-exception: #14
mechanical ruff baseline`).

**Behaviours in.** (1) **R first** (group plan R0 ii): `feature/landing-reference` = `git merge` of `exp-review` @ `c7741b2` into `8971999`, the
#215/#216 ↔ #48 hunks in `direct_beam_maker.py` / `example_direct_beam.py` resolved with a justified commit body, pushed once (`feature/*` is in your
manifest) and never moved. (2) The entries below replayed in order as **one commit per entry** (R1): content = `git diff <M^1> <M> -- <files in scope>`
applied with `git apply --3way`; subject = the fork PR's title + `(fork #NN, <merge sha>)`; body = one line of what it replays, a `Replays: <merge sha>`
trailer, and **every `Co-Authored-By:` trailer found in `git log --format=%b <M^1>..<M^2>`** plus the human authors (`git log --format='%an <%ae>'`,
de-duplicated) — authorship travels. (3) **Sanitized:** no `.github/` change (#20/#25's CI steps dropped — group plan D-2); no `todo.md`, `plans/`,
learnings or batteries; no URL trailers. (4) The layer's gate green on its own: `pixi run test-reduction` (depends on `test-launcher`) from the tip —
the launcher harness and upstream's launcher apps, no editor. (5) `scripts/landing-purity.sh landing-l1-core 8971999 <tip>` and
`scripts/landing-sanitize-check.sh 8971999 <tip>` (on the ledger, committed with this plan) exit 0.

**Explicitly OUT.** Any reduction feature (#30, #34, #46, #48 — L2); the editor and launcher ports (L3); the three model modules (L3/L4); `.github/`;
behaviour changes of any kind (a replayed hunk is the fork's hunk); the fork's `exp` branch (the human's).

## Entries to replay (in this order; `M` = the first-parent entry, `[B]` its branch tip; from the census, group plan §2 V2–V4)

| # | Entry `M` [`B`] | Fork PR | What | Files (scope) |
|---|---|---|---|---|
| 1 | `2127343` (direct) | #14 | mechanical ruff/pre-commit baseline + 3 drifted `web_report` tests | all (purity exception) |
| 2 | `d1a3bab`, `bddba34`, `dc84af7`*, `a4ae8b8` (direct, in order) | #15 | launcher test harness seed, `pytest-timeout`, `test-launcher` task; *`dc84af7` is message-only (empty diff) — skip | `pyproject.toml`, `pixi.lock`, `launcher/tests/*` |
| 3 | `fff2b92`, `8e1f9d2`, `dafd393`, `a34f985`, `05c964f` (direct; skip `7497b28`, `ba14217`, `e6e4e27` — `todo.md` only) | #19 | harness hardening (QSettings isolation, modal patch, timeout hook), the `regex` lock bump | `launcher/tests/*`, `pixi.lock` |
| 4 | `11170ff` [`2e74dd5`] — **minus `.github/`** | #20 | pixi.lock format guard: `scripts/check_lock_format.sh`, pre-commit hook, docs | `scripts/*`, `.pre-commit-config.yaml`, `README`? (check: a `README.md` hunk is "other" — keep if documentation of the hook) |
| 5 | `633950c` (direct) | #21 | each scaling-factor test its own output dir | `tests/*` |
| 6 | `04c6e53` [`8dac235`], `547dc14` [`3d64a77`], `3fb6019` [`5e84085`] | #23 | scaling-factor path anchor (`template.py`, `new_reduction_from_template.py`) + tests | `src/lr_reduction/template.py`, `new_reduction_from_template.py`, `tests/*` |
| 7 | `0d3c73b` (direct), `376a616` [`ed71a78`] | #24 | pyparsing warning filter (`pyproject.toml`, tests) | `pyproject.toml`, `tests/*` |
| 8 | `d0599f9` [`bf574c8`] | #26 | template file-handle leak + the fork's AttributeError regression | `src/lr_reduction/template.py`, `new_reduction_from_template.py`, `tests/*` |
| 9 | `508f70d` [`d8b4461`] | #27 | compare every scaling-factor field | `tests/*`, config |
| 10 | `a4efd95` [`378e323`] — **only** `src/lr_reduction/reduction_domains.py` and the hunks of `nr_reduction_calc.py`, `nr_tools.py` | #28 (split) | the choice lists moved to a shared module; two call sites switched | those three files |
| 11 | `c39efe9` [`0d98cb9`] | #41 | test-suite warnings: `background.py`, `dead_time_correction.py`, `output.py`, `peak_finding.py` + tests | those four + `tests/*` |
| 12 | `c7741b2` [`4eec8d5`] — **only** the L1-owned files (D-4 split) | #49 (split) | the noqa sweep's hunks in `.pre-commit-config.yaml`, `launcher/tests/test_harness.py`, `tests/test_noqa_tags.py` and the seven core `src/` files above | those files |

Not replayed: `f5bd6d2` (an upstream merge — its content is already in the base), `7b6d6b9`, the `todo.md` commits, `dc84af7`. Entry 10's remainder
(the editor) and everything after `c39efe9` on the launcher and reduction lanes belong to L2/L3.

## Red-Green seed (the checks, as the group plan's P1–P4; a landing leaf's tests are its proofs)

| # | Check | RED at the start |
|---|---|---|
| P1 | `scripts/landing-purity.sh landing-l1-core 8971999 <tip>` → `clean` (sets amended A-130: the nine files of D-93 and `launcher/tests/__init__.py` are L1's; v1's run reported exactly those as STRAY, nothing else — D-94) | run it on `exp-review` as if it were L1 → STRAY lines (the mixed history) |
| P2 | `scripts/landing-sanitize-check.sh 8971999 <tip>` → `clean` | on `exp-review` → `CI-CHANGE .github/workflows/test_and_deploy.yml`, `ARTEFACT`s, `NO-PROVENANCE` |
| P4 | `scripts/landing-purity.sh --census 9aaaefa c7741b2 <L1 tip>` lists every entry of the census as `replayed` or `UNASSIGNED` — at L1 the UNASSIGNED set must be exactly the L2/L3 entries (listed in the PR body) | all UNASSIGNED |
| G | `pixi run test-reduction` green at the tip; `pixi install --locked` and `scripts/pixi_lock_check.sh` exit 0 in a clean worktree of the tip (D-83) | — |
| R | `git merge-base --is-ancestor 8971999 feature/landing-reference` and `git diff --stat feature/landing-reference c7741b2 -- src/lr_reduction/direct_beam_maker.py` shows only the #215/#216 resolution | — |

## Mutate-once gate

| Mutation | Must red |
|---|---|
| entry 11 (#41) left out | P4 (UNASSIGNED `c39efe9`) and, at L3, the group proof |
| `.github/` hunk of entry 4 replayed | P2 |
| entry 10 replayed whole (the editor in L1) | P1 (`launcher/`, `settings_document.py` stray) |
| a replay commit without `Replays:` | P2 |
| a `Co-Authored-By` of the original dropped | P2's authorship leg is manual at the gate: the Integrator diffs the trailer set against `git log <M^1>..<M^2>` for two sampled entries |
| R built from `1bffee1` instead of `c7741b2` | R (`c7741b2` not an ancestor) |

## Acceptance criteria

1. `feature/landing-reference` pushed first, with the resolution justified; `feature/landing-l1-core` with eleven replay commits (entry 2 and 3 may be several, one per direct commit, or one each — the Developer states which in the first commit; `Replays:` names each original sha).
2. P1, P2 clean; P4's UNASSIGNED set equals the L2/L3 entries; G green; `pixi.lock` only as the entries left it.
3. The `qa/landing-l1-core` tag at the tip; the commit bodies carry the mutation evidence of the table above (`<check> -> FAILED` observed, then clean).
4. The Integrator re-runs P1/P2/P4 from the ledger's scripts, runs the gate, and opens the draft PR `--base exp` once the fork's `exp` is at `8971999` (if not yet synced, the PASS is recorded on the ledger and the PR step waits for the human's one command — no other work waits).
5. The PR body: the replay table (entry → commit), the exclusions, the purity exception, the suggested upstream order (this is L1 of four), the overlap with upstream's open #181–#202 (group plan D-6).

## Revision history

v1 — authored and dispatched 2026-10-20 (A-128) from the group plan's census; re-seal at dispatch: upstream `exp` still `8971999`; `exp-review` `c7741b2`
(#49 merged, tree `cfe18ef`, I-94); no open feature branch on the fork; the fork's `exp` stale (`d51e935`) — the human's R0 i pending, needed only by the
PR step.

v1 amended 2026-10-20 (A-130) at the Developer's D-93/D-94: the L1 set gains `docs/`, `launcher/tests/__init__.py`, `src/lr_autoreduce/` and the seven core `src/` files
#49 touched; entry 12 (#49's L1-owned hunks) recorded as built; granularity one commit per fork PR (12 commits, D-94) accepted. The gate scripts on the ledger carry the
amended sets; `scripts/landing-proof.sh` is the proof for L3/L4.
