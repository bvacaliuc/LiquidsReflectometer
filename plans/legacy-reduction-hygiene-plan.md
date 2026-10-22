# Plan: `legacy-reduction-hygiene` — fork #41's warnings fixes to the four frozen legacy files, with their tests, as a sibling draft PR on L1‴ for the human to carry upstream stacked on `exp-landing-l1-core`

**Campaign:** `exp-review-fixes` · **Leaf:** `legacy-reduction-hygiene` (K12, un-tabled; refs `triage/legacy-reduction-hygiene`, `feature/legacy-reduction-hygiene`, `qa/legacy-reduction-hygiene`) ·
**Status:** **DISPATCHED — v1 (attempt 1 of N = 3)**, 2026-10-22 (A-199) on the human's addressed word `[human, 2026-10-22 (to the Analyst): "Dispatch K12 legacy-reduction-hygiene per
requests/k12-legacy-reduction-hygiene.md — #41's warnings fixes to the frozen legacy files as a sibling draft PR on the new L1, for me to carry upstream stacked on exp-landing-l1-core.
K13 stays tabled."]`; the hand-off is the Advisor's `requests/k12-legacy-reduction-hygiene.md` (V1-85/V1-86) · **Base:** `feature/landing-l1-core` @ **`2ab688f`** (L1‴, K19 Phase 1 PASS; = upstream
`exp-landing-l1-core`; a current lock and the fork's guard — pushable); its own branch, the shape of #56/#57 and K19's Phase 1c · **PR:** a draft on the fork, base `feature/landing-l1-core`, opened by
the Integrator on the PASS; upstream, the human's own PR stacked on `exp-landing-l1-core` · **Reviews:** design, test, **numerical-diagnostics (all three block** — the slug edits the reduction's
numerics on the claim "every fix is output-identical"; the no-op-fix rule is the reviewer's) · **Gate:** G alone on the host at the tip; the same-environment harness baseline on L1‴ vs the tip
byte-identical (charter §4, reduction-path); the warnings summary free of the three classes; P2 (`Replays:`); D-83 (no lock change).

Campaign: exp-review-fixes

## Declared scope

**One commit on L1‴ `2ab688f` replaying `6234dcc`** (the L1 replay of fork #41 `c39efe9`, frozen out by K11's `a0f7ce3`): `src/lr_reduction/background.py` (`background_fit_weights()`,
`np.divide(..., where=...)`), `dead_time_correction.py` (`paralyzable_correction()`), `output.py` (`read_file()` detects data rows before `np.loadtxt`), `peak_finding.py` (`np.where` before the
square root) — the four frozen files that are the human's 697 warnings (V1-85: `peak_finding.py:107` ×694 divide-by-zero, `dead_time_correction.py:98` ×2 invalid value,
`test_output.py::test_read_file_empty` ×1 `loadtxt` on an empty file) — plus `tests/test_warning_hygiene.py` (+307: #41's nine tests beside #24's four guards) and
`tests/unit/lr_reduction/test_output.py` (+110: six tests). Measured at A-191's practice (a scratch worktree of this clone, removed): `git cherry-pick 6234dcc` onto `2ab688f` applies the four
`src/` files and `test_output.py` cleanly and **conflicts in `tests/test_warning_hygiene.py` in two hunks** (the header, lines 12–25; the body, 135–387): K11 v2 kept #24's four guards in a
122-line form (I-120's REJECT of v1), #41's version is 377 lines with 13 tests — **the resolution keeps #24's four guards by name and adds #41's nine** (B1). **No lock change; the freeze lists
unchanged** (D-1). **The branch is a sibling, not a stack change:** L2–L4/K10, K19's Phase 2 and Phase 1c are untouched (different files); R-5 unchanged.
**Reduction-path slug (charter §4):** a same-environment baseline — the harness's nine scenarios (`scripts/rereduction-scenarios.sh`: S0–S5, `S6ct`, the 8-column set) on L1‴ `2ab688f` — is
captured **before the first source edit**, then re-run on the tip: byte-identical (`scripts/compare-harness-masked.sh`, `compare_columns.sh`), as K11's L2′ was against R-2. Both runs alone
on the host (K19 D-8's `/tmp` race holds on any L1‴-based tip).
**Out:** `87d09d0` (#14, mechanical ruff fixes in the launcher scripts and `roi_selector.py`) and `c5ef58d` (#49, noqa edits in the three readers) — never K12's; the un-freeze of the four
files from the hook/`FROZEN` lists (D-1; a later word with #14's fixes); the other eight frozen files; **K13 stays tabled** (the human's word).

## 1. Request and symptom

The human, to the Advisor (V1-85, verbatim there): on a branch of `exp-next` merged with L1 "all tests passed, [but] the 697 warnings returned … is it possible to have these eliminated in
what gets put into feature/landing-l1-core or does it best go with the follow-on PR?"; then (V1-86) "let us untable just K12. I would like to have it stacked on the new L1 for upstream just
like feature/landing-l1-core does." The Advisor measured: the 697 returned with K11's freeze (every gate since records them), not with K19; all three sources are #41's fixes in frozen
files; in L1 they would break the freeze the scientists asked for; a `filterwarnings` would hide, not fix; so their own PR, offered on #41's output-identity evidence. Then the human's word
to the Analyst (the status line).

## 2. Verified facts at `2ab688f` (2026-10-22 18:2xZ; this clone; V1-85/V1-86)

| # | Fact | Evidence |
|---|---|---|
| V1 | K12 today is `6234dcc` alone: 6 files, 475+/20− (the four `src/` files 78+/…; the two test files 417+); `a70a3e2`/`bd9065b`'s template half left with K17 (its `next` series) | `git show --stat 6234dcc`; V1-86 |
| V2 | The four `src/` files on L1‴ are byte-equal to upstream `c4d20e4` (K11's freeze, `a0f7ce3`) | `git diff c4d20e4 2ab688f -- <the four>` empty |
| V3 | `cherry-pick 6234dcc` onto `2ab688f`: the four `src/` files and `test_output.py` apply clean; `tests/test_warning_hygiene.py` conflicts in two hunks (header 12–25; body 135–387: L1‴'s 122-line K11-v2 form vs #41's 377 lines) | A-199 (scratch worktree) |
| V4 | Test counts: `test_warning_hygiene.py` 4 (L1‴, #24's guards) → 13 at `6234dcc`; `test_output.py` 9 → 15; +15 `def`s → G reduction 137 + 15 = 152 expected (collected items measured — parametrisations may differ, K19's lesson) | `grep -c 'def test_'` |
| V5 | The 697 warnings = `peak_finding.py:107` ×694, `dead_time_correction.py:98` ×2, `test_read_file_empty` ×1; every gate since K11 records them (K11's build, L1′ G, L2″ I-139); the fixes are #41's `16fd1b3` (`np.divide` with `where=`) and `ca52b72` (`read_file`) inside `6234dcc` | V1-85 |
| V6 | The freeze is pinned in `.pre-commit-config.yaml` (the `ruff-check` hook's exclude, 14 paths) and `tests/test_noqa_tags.py`'s `FROZEN` (14, read against the hook); the four files are in both; K12 changes content, not the lists | `git show 2ab688f:…` |
| V7 | #41's own evidence: "every fix is output-identical" (its equality tests; K11's V8 relied on it the other way — the freeze changed no output, L2′ ≡ R-2 on nine scenarios incl. `S6ct`) | K11 plan V8, I-122/I-126 |
| V8 | Tips: L1‴ `2ab688f` = upstream `exp-landing-l1-core` (#219 green); `exp-next` `c4d20e4`; the fork's `feature/test-suite-warnings` `0d98cb9` (#41's branch) | `ls-remote` |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | **One commit, a replay:** `feature/legacy-reduction-hygiene` = `2ab688f` + the replay of `6234dcc` (`Replays: 6234dcc` and the fork's `c39efe9` in the body; the trailer; no campaign words); the four `src/` files byte-equal to `6234dcc`'s; `test_output.py` likewise; `tests/test_warning_hygiene.py` resolved by hand — #24's four guards kept by name, #41's nine added, the resolution named in the body. |
| B2 | **The freeze lists unchanged** (D-1): the hook exclude and `FROZEN` stay 14; `test_noqa_tags.py` passes. Because the four files stay excluded from ruff, **the hunks add no ruff finding**: `ruff check` of each of the four files at the tip reports no finding absent at the base (the pre-existing upstream findings are not this slug's). |
| B3 | **Output identity (charter §4):** the same-environment baseline on `2ab688f` captured before the first source edit; the tip's nine scenarios byte-identical to it (masked compare + `compare_columns.sh`); a DIFFER is a finding, never auto-resolved (STOP, the Integrator's todo — the no-op-fix rule). |
| B4 | **The warnings:** the suite's summary at the tip carries none of the three classes (`peak_finding.py:107`, `dead_time_correction.py:98`, `test_read_file_empty`'s `loadtxt`) and no other first-party warning (`lr_reduction`/`launcher` origins); third-party ones that remain are named in the record. #41's hygiene tests red at the base, green at the tip (T5's RED). |
| B5 | **G at the tip alone on the host:** launcher 10, reduction 137 + the new tests (152 defs expected), exit 0; `pre-commit run --all-files` rc 0; D-83 (`install --locked`, the lock check, `pixi.lock` unmodified); P2 over `2ab688f..` clean. |
| B6 | **The PR body** (the Integrator's, from the record): each hunk and why it cannot change an output (the `where=`-guarded divisions replace values that were masked or overwritten; `read_file` skips `loadtxt` only when no data row exists), the harness identity on this base, the warnings before/after, and that the four files are the scientists' frozen set offered separately — the freeze lists untouched. |

## 4. Files to change

| File | Change |
|---|---|
| `src/lr_reduction/background.py`, `dead_time_correction.py`, `output.py`, `peak_finding.py` | `6234dcc`'s hunks (B1) |
| `tests/test_warning_hygiene.py` | #24's four guards + #41's nine (B1, the conflict) |
| `tests/unit/lr_reduction/test_output.py` | #41's six tests (B1) |
| ledger `plans/legacy-reduction-hygiene-baseline.md` (or the record's section) | the baseline's and the tip's harness checksums (B3) |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: the replay | the four files = `6234dcc`'s; G green; the 697 gone | T1, T4, T5 |
| 2 | edge: the test-file conflict | #24's four guards present by name and green; #41's nine present | T2 |
| 3 | pathological: a hunk changes an output on this base | the harness DIFFERs → STOP, a finding (the Integrator's todo); never a masked compare widened to pass | T4, D-3 |
| 4 | pathological: a new ruff finding hidden by the frozen files' exclusion | T3 red (per-file finding count at the tip > base) | T3 |
| 5 | edge: third-party warnings remain in the summary | named in the record; not first-party; not blocking | T5 |
| 6 | pathological: the harness or G run beside another suite | a void run (K19 D-8); re-run alone | T4/T6's "alone" |
| 7 | out of scope: #14's ruff fixes, #49's noqa edits, the un-freeze, K13 | the human's word | — |

## 6. Red-Green seed

- **T1** `git diff --stat 2ab688f <tip>` = the six files; `git diff 6234dcc <tip> -- src/lr_reduction/background.py src/lr_reduction/dead_time_correction.py src/lr_reduction/output.py src/lr_reduction/peak_finding.py tests/unit/lr_reduction/test_output.py` empty.
- **T2** `tests/test_warning_hygiene.py` at the tip: the four guard test names of `2ab688f` present; #41's nine present; 13 collected (or the measured item count); all green.
- **T3** `ruff check` per file, the four files, base vs tip: no finding at the tip absent at the base.
- **T4** The harness: nine scenarios on `2ab688f` (the baseline, captured first, checksums recorded) and on the tip — identical, masked compare and `compare_columns.sh`; both runs alone on the host.
- **T5** The warnings: at the base, the suite's summary shows the 697 (the three classes); at the tip, 0 of them and 0 first-party; #41's hygiene tests RED at the base (on a scratch copy), GREEN at the tip.
- **T6** G at the tip alone: `install --locked`, the lock check, `test-reduction` (counts reported), `pre-commit run --all-files` rc 0; P2 clean.

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| one `src/` hunk dropped | T1 (diff vs `6234dcc`), T5 (its warning class returns) |
| a #24 guard lost in the resolution | T2 |
| a `where=` guard changing a value that was not masked | T4 (DIFFER) |
| the freeze lists edited | B2's unchanged check (`git diff` on the two files empty) |

## 8. Acceptance criteria

1. T1–T6; one commit with the trailer and `Replays:` lines, no campaign identifiers; the three reviews not blocking; the Integrator's PASS on `qa/legacy-reduction-hygiene` and its draft PR on the fork, base `feature/landing-l1-core`, with B6's body.
2. The record names the baseline and tip checksums and the warnings before/after.
3. The human carries it upstream as its own PR stacked on `exp-landing-l1-core`; the merge into the fork's L1 is the human's (after that merge the four files leave the byte-equality the gate's proofs assume for L1 — a later R-n, named then).

## 9. Learnings relied on

V1-85/V1-86 (the sources, the measurements, the shape); K11's plan (the freeze, V8's identity reasoning, the harness as the identity proof — I-122/I-126); K19 (the sibling shape, D-8's gate-alone rule, the def-vs-item count lesson); charter §4 (reduction-path slugs); A-169 (base admissibility — L1‴ passes).

## 10. Decisions

- **D-1 — the freeze lists stay as they are.** Un-freezing the four files would make ruff lint upstream's pre-existing findings in them, which is #14's content (out); B2's per-file count check detects any finding #41's hunks would add.
- **D-2 — one replay commit, `Replays: 6234dcc`**, not the fork's inner commits (`16fd1b3`, `ca52b72`): L1 already carried #41 as one replay; the record names both.
- **D-3 — identity is the proof, STOP on a DIFFER:** a harness difference is a finding for the Integrator's todo and the numerical-diagnostics reviewer; no compare is loosened to pass.
- **D-4 — numerical-diagnostics blocks** (the no-op-fix rule applied to each hunk's "cannot change an output" argument).
- **D-5 — base L1‴, a sibling branch; the upstream carry is the human's** (its own PR stacked on `exp-landing-l1-core`); the fork merge into L1 is the human's.
- **D-6 — out:** #14, #49, the un-freeze, the other eight frozen files, K13 (tabled by the human's word).

## Revision history

- **v1 — 2026-10-22 (A-199):** authored at dispatch on the human's addressed word; the step from `requests/k12-legacy-reduction-hygiene.md` (V1-85/V1-86). Sealed against L1‴ `2ab688f` (= upstream `exp-landing-l1-core`), `6234dcc`, the fork's `exp-next` `c4d20e4`; V2–V4 measured in a scratch worktree of this clone, removed after.
