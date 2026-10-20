# Plan: `landing-l2-reduction` — layer 2 of `stratified-landing`: the fork's reduction features replayed, sanitized, onto `feature/landing-l1-core`

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l2-reduction` (refs `triage/landing-l2-reduction`, `feature/landing-l2-reduction`, `qa/landing-l2-reduction`) ·
**Status:** READY — v1 (attempt 1 of N = 3) — **dispatched 2026-10-20 (A-133) on L1's Integrator PASS** (I-97: `landing-l1-core` v1 @ `c5ef58d` PASS — P1/P2 clean,
P4 as planned, G 10 + 172, trailers carried, mutations caught; stacking rule clause 3); authored staged 2026-10-20 (A-132). The group plan is **`plans/stratified-landing-plan.md`**; this file is the leaf's work order ·
**Base:** `agentic/feature/landing-l1-core` @ **`c5ef58d`** (the PASS tip, I-97; re-sealed at dispatch: the branch is unmoved since `qa/`) — cut: `git checkout -B feature/landing-l2-reduction
--no-track agentic/feature/landing-l1-core`; merge `agentic/feature/landing-l1-core` forward before every `qa/` push if it moves (a v2 of L1) ·
**Overlap at dispatch:** L1 (the stack's base) only; no other open branch · **PR target:** `feature/landing-l1-core` on the fork, **draft** (stacked; retargeted
by the human's merges) · **Depends on:** L1's PASS; the reference `feature/landing-reference` @ `da2b889` (R) · **Review domains:** design, test (block);
numerical-diagnostics (advise: outputs byte-identical to R's on the harness scenarios) · **Kind:** **reduction-path** (charter §4: the Integrator's
baseline is R's output; `check_headers.py` and `compare_columns.sh` between R and this layer's tip).

Campaign: exp-review-fixes

## Declared scope

**Files in.** `src/lr_reduction/{new_reduction_from_file.py, nr_reduction_calc.py, nr_tools.py, save_reduced_data.py, binary_processing.py,
direct_beam_maker.py, new_reduction_time_resolved.py, example_direct_beam.py, example_time_slices.py, example_nr_reduction.py}`;
`tests/unit/lr_reduction/{test_save_config_json.py, test_prior_combination.py, test_direct_beam_maker.py, test_time_slicing.py}`.

**Behaviours in.** (1) The entries below replayed in order as **one commit per fork PR** (R1; `scripts/landing-replay.sh` with `-p` pathspecs for the
split entries), each with `Replays:` and the originals' `Co-Authored-By` trailers; the #215/#216 ↔ #48 conflict in `direct_beam_maker.py` /
`example_direct_beam.py` resolved **to R's content** (`da2b889`, D-92: #215's block kept verbatim inside `main()`; the other two files as #215/#216
left them) and said so in the body. (2) **Running proof:** after the last entry, `git diff --stat feature/landing-l2-reduction feature/landing-reference
-- <the ten src files> <the four test files>` is **empty** — this layer's files are finished here; nothing in L3 touches them. (3) Sanitized (P2): #30's
`.github/` hunk and `todo.md` dropped; no artefacts, no URL trailers. (4) The gate green on its own: `pixi run test-reduction` (the reduction tests need
the test-data submodule with its LFS objects and the `v*` tags — present on the Developer's clone, D-87/D-95). (5) `scripts/landing-purity.sh
landing-l2-reduction <base> <tip>`, `scripts/landing-sanitize-check.sh <base> <tip>` clean; `--census` leaves UNASSIGNED exactly the L3 entries.

**Explicitly OUT.** The launcher half of #48 (`launcher/apps/time_resolved.py`, `new_launcher.py`, `runtime_env.py`, `launcher/tests/*` — L3); the model
modules; `web_report.py` (its #216 hunk is in the base via R0; its #49 hunk is L1's); `tests/unit/lr_reduction/test_settings_document.py` (#49's hunk
there is L3's — a model test); any behaviour change beyond the fork's hunks.

## Entries to replay (in this order; `M` [`B`])

| # | Entry | Fork PR | What | Files (scope) |
|---|---|---|---|---|
| 1 | `bb98bf3` [`6c758af`] — **only** `src/lr_reduction/example_nr_reduction.py`, `new_reduction_from_file.py`, `tests/unit/lr_reduction/test_save_config_json.py` | #30 (split: its `.github/` hunk excluded, `todo.md` an artefact) | the inverted settings-JSON saver repaired; the campaign synthesis document dropped | those three |
| 2 | `93f6ed6` [`0831c51`] | #34 | re-reduction headers merged by sequence position (M1); D-5 highest run wins | `new_reduction_from_file.py`, `nr_reduction_calc.py`, `nr_tools.py`, `save_reduced_data.py`, `test_prior_combination.py` |
| 3 | `8a31b67` [`ae5ce0e`] | #46 | per-position scale factor and λ range (F17) | `new_reduction_from_file.py`, `nr_reduction_calc.py`, `save_reduced_data.py`, `test_prior_combination.py` |
| 4 | `34dc1b9` [`5e2e195`] — **only** the eight `src/lr_reduction/` files and `tests/unit/lr_reduction/{test_direct_beam_maker, test_prior_combination, test_time_slicing}.py` | #48 (split; launcher half → L3) | time slicing taken in (upstream #205 @ `8eead58`) with the campaign's reconciliation; **the base already carries #215/#216**, so `direct_beam_maker.py` / `example_direct_beam.py` conflict — resolve to R's content | the eight + three |
| 5 | `c7741b2` [`4eec8d5`] — **only** `tests/unit/lr_reduction/{test_direct_beam_maker, test_prior_combination, test_time_slicing}.py` | #49 (split) | the noqa sweep's hunks in L2's tests | those three |

## Red-Green seed (the checks)

| # | Check | RED at the start |
|---|---|---|
| P1 | `scripts/landing-purity.sh landing-l2-reduction <base> <tip>` → `clean` | — (vacuous on an empty layer; the STRAY form is proven on `exp-review`) |
| P2 | `scripts/landing-sanitize-check.sh <base> <tip>` → `clean` | — |
| P4 | `scripts/landing-purity.sh --census 9aaaefa c7741b2 <L1 tip> <L2 tip>` → UNASSIGNED = exactly the L3 entries (#16–#18, #28's editor, `4e5f669`, #33, #35–#40, #43–#45, #47, #48's launcher half, `62e21d1`, `1bffee1`, #49's L3 hunks) | the five entries above UNASSIGNED |
| RP | the running proof (behaviour 2): `git diff --stat <tip> da2b889 -- <14 files>` empty | non-empty until entry 5 |
| G | `pixi run test-reduction` green at the tip; `pixi install --locked` + `scripts/pixi_lock_check.sh` exit 0 in a clean worktree (D-83) | — |
| B | the Integrator: harness baseline from R (`da2b889`) vs the L2 tip — `compare_columns.sh` identical, `check_headers.py` PASS and A/B unchanged (charter §4) | — |

## Mutate-once gate

| Mutation | Must red |
|---|---|
| entry 3 (#46) left out | RP (`save_reduced_data.py` differs), P4 |
| #48's launcher half replayed here | P1 (`launcher/` stray) |
| the #215/#216 conflict resolved to #48's side instead of R's | RP (`direct_beam_maker.py`, `example_direct_beam.py` differ from R), B |
| #30's `.github/` hunk replayed | P2 |
| a replay commit without `Replays:` | P2 |
| `test_settings_document.py`'s #49 hunk taken here | P1 is silent (`tests/.*` is allowed) — **RP and L3's proof catch it** (the file would differ from R after L3 replays it again): the Developer keeps to the five entries' file lists |

## Acceptance criteria

1. `feature/landing-l2-reduction` with five replay commits (entry 4 may carry its resolution note; the base's #215/#216 content wins where #48 collides), `Replays:` naming each original.
2. P1, P2 clean; P4's UNASSIGNED set = the L3 entries; RP empty; G green; `pixi.lock` only as the entries left it (expected: unchanged — none of the five touches it).
3. The `qa/landing-l2-reduction` tag at the tip; the mutation evidence goes on the **ledger** (the Developer's entry), not into the replay commits' bodies — they are upstream-bound and stay sanitized (I-97's deviation adopted for every layer).
4. The Integrator re-runs P1/P2/P4/RP from the ledger's scripts, runs the gate and B, opens the draft PR `--base feature/landing-l1-core` and names the stack (L1 → this).
5. The PR body: the replay table, the split of #30/#48/#49, the resolution of the base's #215/#216 vs #48, B's result, the suggested upstream order (L2 of four).

## Revision history

v1 — authored 2026-10-20 (A-132) while L1 sat at `qa/` (`c5ef58d`); **staged**, dispatching on L1's PASS with the base SHA re-sealed. Entry lists from the
first-parent diffs of `bb98bf3`, `93f6ed6`, `8a31b67`, `34dc1b9`, `c7741b2` measured at the base census (A-126) and re-measured here.

v1 dispatched 2026-10-20 (A-133) on I-97 (L1 PASS @ `c5ef58d`); base re-sealed at that SHA; entries unchanged.
