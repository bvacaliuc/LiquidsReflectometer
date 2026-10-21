# Plan: `precommit-exclude-anchor` — the global pre-commit `exclude` is anchored so the hooks see `launcher/scripts/` again; the noqa guard models the top-level exclude

**Campaign:** `exp-review-fixes` · **Leaf:** `precommit-exclude-anchor` (K14; refs `triage/precommit-exclude-anchor`, `feature/precommit-exclude-anchor`, `qa/precommit-exclude-anchor`) ·
**Status:** **DISPATCHED — v1 (attempt 1 of N = 3)**, 2026-10-21 (A-170) on the human's addressed word `[human, 2026-10-21 (to the Analyst): "you may dispatch K8, K9, K14 and K15. Let us hold K16 until after L4 lands to upstream:exp-next - thank you!"]`; staged at A-168 on the human's relayed words `[human, 2026-10-21 (to the Advisor, V1-69): "On {K8, K9, K14}, prepare them for dispatch."]` — input under
`b059f14`; **not dispatched**: the word "dispatch K14" addressed to the campaign dispatches it (re-seal §2, `cp` to `analysis/exp-review-fixes`, `triage/precommit-exclude-anchor`) ·
**Base:** `feature/landing-l1-core` @ **`81acc87`** (L1′; K11 changed `.pre-commit-config.yaml` and `tests/test_noqa_tags.py` here; L2–L4 touch neither — overlap census V1-69) — its own
branch `feature/precommit-exclude-anchor` cut from `81acc87`, **not** commits on L1 (the landing proofs stay untouched) · **PR:** the fork, `--base feature/landing-l1-core`, draft
(stacked on #54, as #55 is); upstream after L1 as a small PR against `exp-next` · **Reviews:** design, test (block) · **Gate:** G literal; `pre-commit run --all-files` green;
K11's T1 re-run (the frozen four byte-equal to `c4d20e4`).

Campaign: exp-review-fixes

## Declared scope

**In:** `.pre-commit-config.yaml` line 7: `exclude: "(reduction/data|reduction/notebooks|scripts|scans)/.*"` → anchored `"^(reduction/data|reduction/notebooks|scripts|scans)/.*"`;
whatever the hooks then report under `launcher/scripts/` beyond K11's frozen four (measured today: **nothing** — `time_resolved_reduction.py` is clean for ruff with RUF100 under the
project config, ends in a newline, has no trailing whitespace); `tests/test_noqa_tags.py`'s guard also models the top-level `exclude` (I-121's advisory: the compiled hook exclusion
must be checked together with the global one, so a frozen-list hole cannot hide behind the global pattern). **Out:** the frozen four (K11's hook list keeps them excluded; byte-equal
to upstream stays true), any lint fix outside `launcher/scripts/`, `pyproject.toml` (pixi's manifest — D-116).

## 1. Request and symptom

I-121 (advisory 3) found the top-level `exclude` unanchored: pre-commit matches it with `re.search`, so `scripts/.*` also matches `launcher/scripts/…` and every hook (ruff,
end-of-file, trailing-whitespace) silently skips that directory, frozen or not. The human: *"On {K8, K9, K14}, prepare them for dispatch."* The todo:
`todo-precommit-global-exclude-hides-launcher-scripts.md` (A-161).

## 2. Verified facts at `81acc87` (2026-10-21 14:3xZ; this clone)

| # | Fact | Evidence |
|---|---|---|
| V1 | `.pre-commit-config.yaml:7` — `exclude: "(reduction/data|reduction/notebooks|scripts|scans)/.*"`, unanchored | `git show 81acc87:.pre-commit-config.yaml` |
| V2 | `launcher/scripts/` holds five files: the frozen four (`off_spec`, `quick_reduce`, `refracted_beam`, `xrr_reduction`) and `time_resolved_reduction.py` | `git ls-tree` |
| V3 | `time_resolved_reduction.py` at `81acc87`: ruff (project config, `--extend-select RUF100`) reports nothing; last byte `\n`; no trailing whitespace — anchoring the exclude changes no file today | measured |
| V4 | The frozen four are listed in the `ruff-check` hook's own `exclude` (K11 B2) and stay byte-equal to `c4d20e4` whatever the global pattern does; the end-of-file and trailing-whitespace hooks are clean on upstream's versions (D-116) | K11 record |
| V5 | L2–L4 do not touch `.pre-commit-config.yaml` or `tests/test_noqa_tags.py`; a branch from `81acc87` merges into the stack cleanly later | V1-69 |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | **One commit, the anchor:** `^` prefixed to the global `exclude`; `pre-commit run --all-files` green at the tip; the four frozen files untouched (their hook-level exclusion holds). |
| B2 | **The guard models both exclusions:** `test_noqa_tags.py` compiles the global `exclude` and the hook's `exclude`, asserts the frozen 12 are matched by the hook's, asserts no tracked `.py` outside `tests/data/`, `scripts/`, `reduction/{data,notebooks}/`, `scans/` is matched by either, and asserts the global pattern is anchored (`^`) — a regression to the unanchored form goes red. |
| B3 | **If a hook reports something under `launcher/scripts/`** (none today, V3): fix it in a second commit, named file by file; never touch the frozen four. |

## 4. Files to change

| File | Change |
|---|---|
| `.pre-commit-config.yaml` | line 7 anchored (B1) |
| `tests/test_noqa_tags.py` | the guard models the global `exclude` (B2) |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: the anchor | hooks see `launcher/scripts/`; green today (V3) | T1 |
| 2 | edge: a future file under `launcher/scripts/` with lint | the hooks catch it (the purpose) | T1 |
| 3 | pathological: the anchor dropped again | the guard's anchored-pattern assertion reds | T2 |
| 4 | pathological: the global pattern widened to hide a frozen-list hole | the guard checks tracked `.py` against both patterns | T2 |
| 5 | out of scope: `pyproject.toml` | untouched (the lock) | T3 |

## 6. Red-Green seed

- **T1** `pixi run pre-commit run --all-files` → green; with the anchor removed and a deliberate trailing space in `launcher/scripts/time_resolved_reduction.py` → silently green (the hole); with the anchor → red (the hook sees it).
- **T2** `pytest tests/test_noqa_tags.py` → green; the global pattern un-anchored → red; `launcher/scripts/time_resolved_reduction.py` added to the hook's exclusion → red (a non-frozen file matched).
- **T3** `git diff 81acc87..<tip> --stat` = the two files; K11's T1 (`git diff c4d20e4 <tip> -- <the 12>`) empty.
- **T4** G at the tip EXIT 0 (10 + 143 expected).

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| the anchor omitted | T1, T2 |
| a frozen-list hole hidden by the global pattern | T2 |
| a frozen file re-linted | T3 (K11's T1) |

## 8. Acceptance criteria

T1–T4 green; two files; bodies with the trailer and no campaign identifiers; the Integrator's draft PR `--base feature/landing-l1-core`.

## 9. Learnings relied on

I-121 (the finding), K11's hook-exclusion design and its compiled guard (A-160/I-121), D-116 (no `pyproject.toml` edits).

## 10. Decisions

- **D-1 — its own branch, not L1's:** so the landing proofs stay as gated; the human carries it upstream after L1 as a small PR against `exp-next`.
- **D-2 — at dispatch, L1's purity set gains `launcher/scripts/.*`** (so a later base merge carrying this change is not a STRAY in a P1 run over L1's range).

## Revision history

- **v1 — 2026-10-21 (A-168):** staged on the human's relayed words (V1-69); not dispatched. Sealed against L1′ @ `81acc87`.
