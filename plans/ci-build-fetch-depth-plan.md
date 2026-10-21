# Plan: `ci-build-fetch-depth` — upstream's `build` job checks out full history, so the package it publishes carries a real version instead of `0.1.0.dev…`

**Campaign:** `exp-review-fixes` · **Leaf:** `ci-build-fetch-depth` (K9; refs `triage/ci-build-fetch-depth`, `feature/ci-build-fetch-depth`, `qa/ci-build-fetch-depth`) ·
**Status:** **PASS — v1 @ `e62aeb3` (I-130, 2026-10-21; fork draft PR #56 → `feature/landing-l1-core`; `qa/` consumed)**; dispatched 2026-10-21 (A-170) on the human's addressed word `[human, 2026-10-21 (to the Analyst): "you may dispatch K8, K9, K14 and K15. Let us hold K16 until after L4 lands to upstream:exp-next - thank you!"]`; staged at A-168 on the human's relayed words `[human, 2026-10-21 (to the Advisor, V1-69): "On {K8, K9, K14}, prepare them for dispatch."]` —
input under `b059f14`; **not dispatched**: "dispatch K9" dispatches it. The Advisor's note stands: if the slug's only product is the one line, the human's own one-line upstream PR
is the cheaper route ·
**Base:** **`feature/landing-l1-core` @ `81acc87`** (L1′ — a current lock and the fork's lock guard, so a seat can push it) on its own branch `feature/ci-build-fetch-depth`; **amended at staging (A-169, D-129):** v1 named the fork's `exp` @ `c4d20e4`, which no seat can push — `pixi install --locked` exits 1 there and upstream's own pre-push `pixi lock --check` refuses the branch (the same trap as D-107 at `8971999`); the one-line change itself is file-disjoint from every layer and applies cleanly on any base ·
**PR:** the fork, `--base feature/landing-l1-core`, draft (stacked on #54, as #55); upstream after L1 lands on `exp-next`, as the one-line PR against `exp-next` — **before the first `exp-next` → `exp` merge** (V1-69 condition 4), or the first
published package of the landed stack is versioned `0.1.0.dev…` · **Reviews:** design (block); test n/a (a workflow line; the proof is local) · **Gate:** the job itself cannot run
in a gate (it runs on `push` to the listed branches, with secrets); the Developer's proof is local (§6).

Campaign: exp-review-fixes

## Declared scope

**In:** `.github/workflows/test_and_deploy.yml`, the `build` job's checkout: `fetch-depth: 100` → `fetch-depth: 0` (the `tests` job's form, line 28). **Out:** everything else in
the workflow (the fork's own CI hunks stay on `exp-review` — D-2 of the group plan is about the landing layers, not this slug; the landing P2 CI-CHANGE check does not apply to a
non-landing slug); a release tag on `exp` (the honest alternative — upstream's call).

## 1. Request and symptom

`todo-upstream-build-job-fetch-depth-outruns-release-tag.md` (V1-62): the `build` job's depth-100 checkout holds commits at distance 0…99 from the tip; `git describe --match 'v[0-9]*'`
finds `v2.9.0rc1` only while its shortest path is below 100. Past that, versioningit falls back to `0.0.1`, the package builds as `0.1.0.dev<date>+g<sha>`, `pkg-verify` installs it by
file name and passes, `publish` uploads it under `neutrons/label/exp`, and the `exp` deploy keeps selecting the old `2.10.0.dev…` build — the 2026-06-05 autodeploy regression
(390dc72) again, silently; the depth-0 `tests` job cannot see it.

## 2. Verified facts (2026-10-21 14:3xZ; this clone)

| # | Fact | Evidence |
|---|---|---|
| V1 | `test_and_deploy.yml` at `c4d20e4`: the `tests` job `fetch-depth: 0` (line 28, "Fetch all history for accurate versioning"); the `build` job `fetch-depth: 100` (line 78) | `git show c4d20e4:.github/workflows/test_and_deploy.yml` |
| V2 | Distance from `c4d20e4` to `v2.9.0rc1`: **130** commits by `rev-list --count` (92 first-parent); the stack tip `f8dbf86` is 179. **Corrected at D-132 (A-173):** the first draft read "already past 100, so upstream's `build` already cannot describe the tag" — wrong, because a shallow fetch's depth counts the **shortest parent path**, not `rev-list --count`: 88 (`c4d20e4`), 94 (`81acc87`), 97 (`f8dbf86`), all under 100; and upstream's two non-release tags (`exp-review-group3`, `exp-review-settings-editor`), fetched at depth 100 too, bridge the gap, so today's clone comes out not shallow at all. The failure is latent (a 3-commit margin with release tags only), not present | `git rev-list --count v2.9.0rc1..c4d20e4`; D-132's `scripts/ci-fetch-depth-probe.sh` (ledger) |
| V3 | The deployed `lr_reduction_exp` is a date-stamped dev version for this reason (V1-62; V1-69) | V1-62 |
| V4 | The `build` job runs only on `push` to `[next, qa, main, exp]` and `v*` tags, with secrets; a PR from the fork never runs it with a result that proves anything about the fix | the workflow's triggers |
| V5 | **A seat cannot push a branch based on `c4d20e4`** (D-129, re-measured): `pixi install --locked` → exit 1 ("lock-file not up-to-date"), no `scripts/pixi_lock_check.sh`, and upstream's own pre-push `pixi lock --check` (`.pre-commit-config.yaml:27-31`, unchanged since `8971999`) refuses the push; skipping a hook is not a seat's. L1′ `81acc87` has a current lock and the fork's guard | D-107 addendum; D-129 |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | One commit, one line: `fetch-depth: 0` in the `build` job's checkout, with the `tests` job's comment. |
| B2 | **The proof is local and reproduces the job's checkout** (the Developer): from a local copy, `git clone --depth 100 <copy> wt100` and `git clone <copy> wtfull` at `c4d20e4` (and at the stack tip), `git fetch --tags` as the job does, then `git describe --tags --match 'v[0-9]*'` and `python -m versioningit` in each: depth 100 → "No names found" / `0.1.0.dev…`; full → `v2.9.0rc1-130-g…` / `2.10.0.dev…`. Recorded in the commit body. |
| B3 | Nothing else changes; the fork's `exp-review` CI hunks are not pulled in. |

## 4. Files to change

| File | Change |
|---|---|
| `.github/workflows/test_and_deploy.yml` | the `build` job's `fetch-depth` (B1) |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: a tip ≥ 100 from the nearest release tag by shortest parent path (synthetic today: `f8dbf86+100`) | full depth describes the tag; the package carries `2.10.0.dev…` | T1 |
| 2 | edge: a tip < 100 by shortest path (today's: 88/94/97) | unchanged behaviour — described at both depths | T1 |
| 3 | pathological: a merge ref one step beyond the branch (a PR) | depth 0 covers it | T1 |
| 4 | out of scope: the release tag alternative | upstream's call; noted in the PR body | — |

## 6. Red-Green seed

- **T1** B2's two checkouts at `81acc87` (distance 148 to `v2.9.0rc1`) and at `f8dbf86` (179): depth 100 fails to describe, full describes (GREEN) — recorded verbatim. **Corrected at D-132 (A-173):** "RED today" does not hold (shortest paths 94/97 < 100, and the two non-release tags bridge); the RED is shown on synthetic tips — `f8dbf86+100` (path 197): "No tags can describe", `0.1.0.dev…` at depth 100, `v2.9.0rc1-279` at depth 0; with release tags only, `f8dbf86+10` (107) is already RED — measured with the ledger's `scripts/ci-fetch-depth-probe.sh`, which replaces the clone's tag set by upstream's 69 (a seat clone's `qa/*` tags would mask it further).
- **T2** `git diff 81acc87..<tip> --stat` = the one file, one hunk; the YAML parses (`python -c "import yaml; yaml.safe_load(open(...))"`).

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| the depth left at 100 | T1 |
| any second hunk in the workflow | T2 |

## 8. Acceptance criteria

T1–T2 recorded; one file, one hunk; the body with the trailer and no campaign identifiers; the draft PR `--base feature/landing-l1-core` on the fork (the header's base since A-169's amendment; this line's `--base exp` was the v1 text, flagged at D-132, corrected at A-173); the human's upstream PR before the first `exp-next` → `exp` merge.

## 9. Learnings relied on

V1-62 (the mechanism and the distances), V1-69 (the scheme's condition 4), A-145 (the triage), the group plan D-2 (why the landing layers never carried this).

## 10. Decisions

- **D-1 — the route:** the human's one-line upstream PR stays the cheaper path; this slug exists so the change is gated and recorded if the human prefers the campaign to carry it.
- **D-2 — base L1′ `81acc87` (amended A-169):** the change is file-disjoint from the stack, but a seat's branch must start from a tip it can push and gate — upstream's bare tip fails that while its lock is stale (D-107, D-129). The one line applies cleanly on `exp-next` for the human's upstream PR.

## Revision history

- **v1 — 2026-10-21 (A-168):** staged on the human's relayed words (V1-69); not dispatched. Sealed against the fork's `exp` @ `c4d20e4`.
- **v1 amended at staging — 2026-10-21 (A-169), on D-129's pre-dispatch read:** the base corrected to L1′ `81acc87` (a seat cannot push a branch based on `c4d20e4`: the stale lock and upstream's pre-push lock check); V5, T1/T2, D-2 follow; D-1 unchanged — the human's own one-line PR remains the cheaper route.
- **v1 amended after delivery — 2026-10-21 (A-173), on D-132 (correct-and-flag):** V2 and T1 corrected — a shallow fetch's depth counts the shortest parent path (88/94/97 at the three tips, under 100) and upstream's two non-release tags bridge the gap, so the RED is shown on synthetic tips (`f8dbf86+100`; `+10` with release tags only), not today's; the fix stands as the removal of a margin, not of a present failure. Matrix rows 1–2 reworded; §8's `--base exp` (v1 text) → `feature/landing-l1-core` (the header). Measured with the Developer's `scripts/ci-fetch-depth-probe.sh` (ledger). Status unchanged here: it flips at the Integrator's record (#56 carries the PASS in the open).
- **v1 PASS — 2026-10-21 (A-174):** I-130 @ `e62aeb3`; #56 (draft, one file) stacked on #54; the Integrator's own run of the probe reproduced D-132's table; its advisories in #56's body (the publish job's discarded version; `fetch-tags` redundant at depth 0; the upstream PR after L1 is on `exp-next` and before the first `exp-next` → `exp` merge; V4 "cannot run in a gate" wrong — the build job runs on PRs and shows the green side). The human's upstream PR remains the cheaper carry for the one line.
