# Plan: `legacy-reduction-hygiene` — fork #41's warnings fixes to the four frozen legacy files, with their tests, as a sibling draft PR on L1‴ for the human to carry upstream stacked on `exp-landing-l1-core`

**Campaign:** `exp-review-fixes` · **Leaf:** `legacy-reduction-hygiene` (K12, un-tabled; refs for v2: `triage/legacy-reduction-hygiene-v2`, `feature/legacy-reduction-hygiene-v2`, `qa/legacy-reduction-hygiene-v2` — v1's branch and its consumed tag stay as they are, never rewritten) ·
**Status:** **v2 PASS @ `35f5489` (I-156, attempt 2 of 3; B-1 closed against the code — 5/1/2/1 test classes as the prose says; the four un-frozen files linted clean under `pre-commit run --all-files`; G alone 10 + 146 rc 0, no warnings line; T4 identical ×9 vs the L1‴ baseline, transcript lines all paired under the mask) → **draft PR #60** (I-158: opened at the human's word to the Integrator — *"it will not hurt to emit that PR now"* — releasing I-156's hold; head `35f5489`, base L1, `MERGEABLE`): **K12 COMPLETE at its PR (A-208)**. Its landing is the human's route choice (V1-98): K22 `landing-l1-hygiene-merge` (L1 fast-forwarded to `35f5489`; the stack follows) or K21 `landing-l1-unfreeze` (#60 then closes, its content the restored L1's). `qa/legacy-reduction-hygiene-v2` consumed in record (the human's to delete, with the stale v1 branch)**; was v2 `-> qa @ `35f5489`` (D-160: `feature/legacy-reduction-hygiene-v2`; B-1 fixed everywhere, the advisories applied, the four files un-frozen 14 → 10, G 10 + 146 with no warnings summary; at the Integrator's gate, `qa/legacy-reduction-hygiene-v2`); v2 DISPATCHED — attempt 2 of N = 3, 2026-10-22 (A-201) on I-153's REJECT of v1 @ `98b3f9b` (one blocking prose finding; the code passed every leg; the record `todo.md` @ `5384b28` on `feature/legacy-reduction-hygiene`, `review/legacy-reduction-hygiene`); v1 was dispatched 2026-10-22 (A-199) on the human's addressed word `[human, 2026-10-22 (to the Analyst): "Dispatch K12 legacy-reduction-hygiene per
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
square root) — the four frozen files that are the human's 697 warnings (V1-85 — corrected at A-208 per D-162/V1-99: `background.py:144` ×689 + `peak_finding.py:107` ×5 divide-by-zero; the summary's grouping had named one site — `dead_time_correction.py:98` ×2 invalid value,
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
| V5 | The 697 warnings = `background.py:144` ×689 + `peak_finding.py:107` ×5 (corrected A-208: D-162 measured in suite order with `scripts/warning_site_count.py`, I-157, V1-99 — V1-85's `peak_finding.py:107` ×694 was pytest's summary grouping, a figure from the charter's `2324e5c` pin), `dead_time_correction.py:98` ×2, `test_read_file_empty` ×1; every gate since K11 records them (K11's build, L1′ G, L2″ I-139); the fixes are #41's `16fd1b3` (`np.divide` with `where=`) and `ca52b72` (`read_file`) inside `6234dcc` | V1-85 |
| V6 | The freeze is pinned in `.pre-commit-config.yaml` (the `ruff-check` hook's exclude, 14 paths) and `tests/test_noqa_tags.py`'s `FROZEN` (14, read against the hook); the four files are in both; K12 changes content, not the lists | `git show 2ab688f:…` |
| V7 | #41's own evidence: "every fix is output-identical" (its equality tests; K11's V8 relied on it the other way — the freeze changed no output, L2′ ≡ R-2 on nine scenarios incl. `S6ct`) | K11 plan V8, I-122/I-126 |
| V8 | Tips: L1‴ `2ab688f` = upstream `exp-landing-l1-core` (#219 green); `exp-next` `c4d20e4`; the fork's `feature/test-suite-warnings` `0d98cb9` (#41's branch) | `ls-remote` |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | **One commit, a replay:** `feature/legacy-reduction-hygiene` = `2ab688f` + the replay of `6234dcc` (`Replays: 6234dcc` and the fork's `c39efe9` in the body; the trailer; no campaign words); the four `src/` files byte-equal to `6234dcc`'s; `test_output.py` likewise; `tests/test_warning_hygiene.py` resolved by hand — #24's four guards kept by name, #41's nine added, the resolution named in the body. |
| B2 | **The four files leave the freeze lists (v2, D-1 reversed):** `.pre-commit-config.yaml`'s `ruff-check` exclude and `tests/test_noqa_tags.py`'s `FROZEN` go 14 → 10 (the guard's count follows); `pre-commit run --all-files` green — ruff now lints the four files, which T3 measured at 0 findings at base and tip, so the un-freeze costs nothing and the config's own comment (`.pre-commit-config.yaml:29`, "drop an entry when the file is next intentionally changed") is honoured: this is that change. T3 stays as the detection (0 findings at the tip). |
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

- **T1** `git diff --stat 2ab688f <tip>` = the six files (v2: eight — the two freeze-list files join); `git diff 6234dcc <tip> -- src/lr_reduction/background.py src/lr_reduction/dead_time_correction.py src/lr_reduction/output.py src/lr_reduction/peak_finding.py` empty; **`tests/unit/lr_reduction/test_output.py` AST-equal to `6234dcc`'s but for docstrings** (v2, A-204: v1's "byte-equal" and v2's "review IDs scrubbed" conflicted in that file — the scrub prevails, as D-160 chose and flagged).
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

- **D-1 — reversed at v2 (A-201, correct-and-flag on v1's premise):** v1 kept the freeze lists because un-freezing would make ruff lint upstream's pre-existing findings in the four files; **I-153's T3 measured 0 ruff findings at base and tip**, so the premise was false for these four (#14's ruff fixes were in the launcher scripts and `roi_selector.py`). v2 un-freezes the four (B2): a file that is intentionally changed is linted, as the config's own comment prescribes. Reversible by the human's word; the other ten entries stay.
- **D-2 — one replay commit, `Replays: 6234dcc`**, not the fork's inner commits (`16fd1b3`, `ca52b72`): L1 already carried #41 as one replay; the record names both.
- **D-3 — identity is the proof, STOP on a DIFFER:** a harness difference is a finding for the Integrator's todo and the numerical-diagnostics reviewer; no compare is loosened to pass.
- **D-4 — numerical-diagnostics blocks** (the no-op-fix rule applied to each hunk's "cannot change an output" argument).
- **D-5 — base L1‴, a sibling branch; the upstream carry is the human's** (its own PR stacked on `exp-landing-l1-core`); the fork merge into L1 is the human's.
- **D-6 — out:** #14, #49, the un-freeze, the other eight frozen files, K13 (tabled by the human's word).

## Revision history

- **v1 — 2026-10-22 (A-199):** authored at dispatch on the human's addressed word; the step from `requests/k12-legacy-reduction-hygiene.md` (V1-85/V1-86). Sealed against L1‴ `2ab688f` (= upstream `exp-landing-l1-core`), `6234dcc`, the fork's `exp-next` `c4d20e4`; V2–V4 measured in a scratch worktree of this clone, removed after.

### v2 — 2026-10-22 (A-201): the Integrator's REJECT of v1 @ `98b3f9b` (I-153; the record `todo.md` @ `5384b28`, `review/legacy-reduction-hygiene`) — attempt 2 of 3

**Cause: B-1, a false claim in prose, in two places** — the module docstring (`tests/test_warning_hygiene.py:15-19`) and the commit body (¶3): "each [new test] runs its site under
an 'error' filter with an input that used to warn". False for four of the nine (verified by the Integrator): `:195` is a kept warning (`pytest.warns(RuntimeWarning, match="divide
by zero")`); `:226` and `:344` set no filter and pin call-site arguments against the base arithmetic; `:369` records under `"always"` and asserts none. **The code passed every leg:**
G 10 + 146 with no warnings line; T1/T2/P2; T4 the harness base vs tip — data columns identical ×9, headers A/B identical on S0–S5 (the script's I3/I4 invariants fail identically
on both: L1‴ carries upstream's reduction code, M1's header fix lives in L2), masked DIFFER only in `transcript.txt`'s directory names and durations; the numerical review not
blocking (each `np.divide(..., where=)` element-identical to the base, masked elements included; the narrowed `except` handles every input class the base handled). The same class as
I-148: the body is what upstream reads, and only a new commit object corrects it.

**v2 — a fresh replay of `6234dcc` on L1‴ `2ab688f`, on a new branch `feature/legacy-reduction-hygiene-v2`** (v1's branch is never rewritten; the Integrator's shape, as K19's
Phase 1c re-cut):
- **the docstring and the body say what the tests do** (the Integrator's accurate wording): six run their site under an error or record filter with an input that used to warn and
  check the values; two pin the call sites' arguments against the base arithmetic; one pins a warning that is deliberately kept (a zero error with counts); the `no-zero` cases of
  `:150`, `:183`, `:296` are non-warning controls;
- the advisories applied: the 697 described as "from the warning sites in four files" (or measured per site — the Developer's choice, said which); the "four columns" sentence made
  precise (a single column of exactly four rows unpacks on base and tip alike); **the review IDs and the base `2324e5c` scrubbed from the per-test docstrings** (upstream cannot
  resolve them — the same hygiene as K17/K19's prose); the two real-data tests' dependence on the Mantid facility set at import by earlier modules **named in the body** (deterministic
  under pytest; fails run alone; the cure is the K19 series' optional `0003`); the harness coverage caveat named (its template has `two_backgrounds` false, so the nine scenarios never
  reach `functional_background` — the tests pin those sites element by element);
- **D-1 reversed:** the four files leave the hook exclude and `FROZEN` (B2), 14 → 10, the guard's count adjusted; `pre-commit run --all-files` green (T3: 0 findings);
- the `src/` content and the two test files' tests unchanged from v1 (byte-equal to `6234dcc` for the four `src/` files and `test_output.py`; the hygiene file's tests as v1 — only
  docstrings and the two list files change), so T4's identity holds by construction — the Integrator's call whether to re-run the harness or cite I-153's T4 for the same code;
- **the gate otherwise as v1:** G alone on the host (10 + 146 expected — the un-freeze adds no test), T1–T3, T5, P2, D-83; the three reviews.
- **D-v2-1 — the v2 `qa/` tag is `qa/legacy-reduction-hygiene-v2`:** v1's consumed `qa/legacy-reduction-hygiene` @ `98b3f9b` is still live (the human's to delete, I-140) and a tag
  cannot move without force; a new name needs neither. The Integrator's watch keys on `qa/*`.
- **D-v2-2 — attempt 2 of 3;** a third rejection escalates.
- Sealed against L1‴ `2ab688f` (= upstream `exp-landing-l1-core`), `6234dcc`, v1 `98b3f9b`; the Integrator's measurements of I-152/I-153.
- **v2 `-> qa` — 2026-10-22 (A-204):** D-160: `35f5489` on the new branch (v1's untouched): the four `src/` files byte-equal to `6234dcc`'s and v1's; the hygiene module's docstring and the body say what the nine tests do (five under an `"error"` filter with values checked, three of them with no-zero controls; one records the warnings of reading a file without data rows and requires none; two pin call-site arguments with no filter; one pins the kept warning); the 697 described as the summary shows them (694 divide-by-zero from the reduction tests' fit weights, 2 invalid-value from the paralyzable correction, 1 from `read_file`), not attributed per file; the "four columns" sentence measured (one column of four rows unpacks on base and tip; three rows → ValueError on both); the review IDs and `2324e5c` scrubbed from both test files — hence T1's correction above; the facility coupling and the harness coverage caveat named; the body checked line by line (two first-draft claims dropped). **D-1 reversed applied:** 14 → 10 in both lists with the config comment naming why; `test_noqa_tags.py` 5 passed; ruff 0 findings; `pre-commit run --all-files` rc 0. G alone 10 + 146, no warnings summary; D-83; P2 clean. T4 (the harness) stays the gate's — the code is v1's, which I-153 measured identical ×9. `triage/legacy-reduction-hygiene-v2` deleted at delivery.
- **v2 PASS — 2026-10-22 (A-207):** I-156 (18:0x EDT): heavy legs alone (0 other pytest at start): `install --locked` and the lock check rc 0; `pre-commit run --all-files` rc 0 with ruff `Passed` on the un-frozen files; G 10 + 146 rc 0, no warnings line, peak 6.7 G, `pixi.lock` unchanged; T4 on the tip against I-153's L1‴ baseline (same SHA, same environment): columns identical ×9, header A/B ok S0–S5, the masked DIFFER only in `transcript.txt` with every line paired (0 unpaired ×3). No new reviewer run (the code is v1's, reviewed at I-153; the delta is prose and the freeze lists, both verified). Advisory, unmeasured: the body's split of the 694 divide-by-zero across two files (V5's single site is `peak_finding.py:107`) — a single-file run shows no RuntimeWarning, so the 694 arise only in suite order; a future edit says "from the warning sites the four files fix". The human's own `test-reduction` run (17:46–17:54Z, `exp.agentic`) did not overlap G. **The draft PR is held** (I-156's call, affirmed here): V1-97 measures K12 v2's four `src/` files byte-identical to the restored L1, so #219 would carry the content itself if the unfreeze is taken; the question was input, so the gate ran to its verdict; the PR is one command away either way.
- **At its PR; V5 corrected — 2026-10-22 (A-208):** #60 opened (I-158) at the human's word to the Integrator, releasing I-156's hold (and overtaking A-207's affirmation of it); draft, head `35f5489`, base L1, `MERGEABLE`; body: the 697 by source in suite order, the fixes and tests as I-156 verified them, the freeze-list change, the gate, the coverage note, that its landing (own PR or inside #219, V1-97/V1-98) is under discussion. **V5 corrected:** D-162 measured the 694 divide-by-zero in suite order as `background.py:144` ×689 + `peak_finding.py:107` ×5 (I-157 accepted; V1-99 traced the ×694 to the charter's `2324e5c` pin) — v2's body was right as written; nothing downstream changes (both files are K12's). The route choice is the human's: K22 `landing-l1-hygiene-merge` (staged A-208) fast-forwards L1 to `35f5489` and follows with the stack; K21 restores `7f0a4ad` and closes #60.
