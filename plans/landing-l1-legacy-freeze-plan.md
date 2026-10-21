# Plan: `landing-l1-legacy-freeze` — L1 returns the scientist's legacy-reduction files to upstream's content (freeze, pedantic: byte-equal), ruff stops linting them, the tests that pinned the frozen changes leave; `template.py`'s `FileNotFoundError` fix stays (the human's D-1); then the stack and K10 follow L1 through gated forward merges against a rebuilt reference

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l1-legacy-freeze` (K11; refs `triage/landing-l1-legacy-freeze`, the slug amends `feature/landing-l1-core` by commits on top —
no rewrite — and tags `qa/landing-l1-legacy-freeze`; Phase 2 re-tags `qa/landing-l2-reduction`, `qa/landing-l3-launcher`, `qa/landing-l4-model-move`, `qa/log-level-console` at the
forward-merged tips) · **Status:** **DISPATCHED — v1**, 2026-10-21 (A-157) on the human's word addressed to the campaign (§1), staged at A-156 from the scientist's #219 comment
and V1-67 ·
**Base:** `feature/landing-l1-core` @ **`7f0a4ad`** (L1 after the human's base merge of upstream `exp` `c4d20e4`, I-115). **The fork's `exp` = upstream `exp` = `c4d20e4`** (the
human synced it; #54's diff is clean again). The frozen files' content at `c4d20e4` equals `8971999`'s (`c4d20e4` changed only `nr_reduction_calc.py`, `settings.json`, an example) ·
**PRs:** #54 (fork, L1 → `exp`) and #219 (upstream, `exp-landing-l1-core` — the human pushes the new tip; the review thread stays attached) advance by fast-forward; #51/#52/#53/#55
fast-forward in Phase 2 · **Reviews:** design, test (block) · **Gate:** Phase 1 — G literal at L1's new tip; P1 over `c4d20e4..<tip>`; P2 with `Reverts:` accepted. Phase 2 — per
layer as §3 B5 says (G; L2's harness against R-2; P3 at L4 against R-2 with the enlarged exclusion list; P5 on R-2).

Campaign: exp-review-fixes

## Declared scope

**In (Phase 1, L1):** the **12** files L1 changed among the scientist's 17 that stay frozen — `launcher/scripts/{off_spec,quick_reduce,refracted_beam,xrr_reduction}.py`,
`src/lr_reduction/{background,dead_time_correction,output,peak_finding,reduction_template_reader,time_resolved,new_reduction_template_reader}.py`, `launcher/apps/roi_selector.py` —
returned to upstream's content byte for byte; `pyproject.toml` `[tool.ruff] extend-exclude` with the 12 paths and a dated comment; `tests/test_warning_hygiene.py` removed and
`tests/unit/lr_reduction/test_output.py` returned to upstream's (they pin the frozen `output.py`/`background.py`/`dead_time_correction.py`/`peak_finding.py` changes). **Kept, the
human's D-1:** `src/lr_reduction/template.py` and `src/lr_reduction/new_reduction_from_template.py` as L1 has them (fork #23's `FileNotFoundError` fix and #26's closed file handle),
with their tests (`tests/test_template_paths.py`, `tests/test_template_file_handles.py`, the seven `tests/data/template*.xml`, `tests/conftest.py`, the `test_reduction.py` /
`test_scaling_factors_workflow.py` / `test_time_resolved.py` edits of a70a3e2). **In (Phase 2, the stack):** the reference re-derived on `c4d20e4` as `feature/landing-reference-2`;
L2, L3, L4 and K10 each merging the previous gated tip forward, each re-gated. The ledger's proof scripts: `Reverts:` accepted, the frozen set in `EXCL` (done at dispatch, A-157).
**Out:** everything else in L1 (the `web_report` repair, the launcher harness, the lock guard, the noqa sweep elsewhere); deleting groups 2 and 3 (`template_batch.py`,
`new_reduction_from_template.py`, `new_reduction_template_reader.py`, `roi_selector.py` — the scientist's or the human's PR; git is the archive); **K12 (the split-off hygiene PR) and
K13 (extraction): tabled by the human** (`[human, 2026-10-21: "Table K12 and K13 for now"]`).

## 1. Request and symptom

The scientist on #219 (welbournR, 2026-10-20 18:58Z, verbatim): *"There are a few files edited that I'm unsure whether we should accept changes. 1. There is this set of files
associated only with the legacy reduction which I don't think we should be changing as fixing issues here and testing for the effect of changes is beyond the scope of what we
are currently working on, and we want to preserve the old behavior"* — eleven files (two paths typed with an underscore for a slash, corrected here); *"2. … reading in/out
template.xml into the new workflow … shelved … consider archiving"* (`launcher/apps/template_batch.py`, `new_reduction_from_template.py`, `new_reduction_template_reader.py`);
*"3. `/launcher/apps/roi_selector.py` is not used … deleted or at least archived."* The human to the Advisor (V1-67): *"would you consider their requests within the context of the
campaign work? How can we accommodate the scientist's sensitivities to the 'old reduction' …"* — the Advisor's shape, freeze-and-split now, extraction later (staged at A-156).

**The word** `[human, 2026-10-21 (to the Analyst): "dispatch K11, with the D-1, fix the 'FileNotFoundError'. Note the changes in upstream:exp have been synced to agentic:exp.
Table K12 and K13 or now. Make sure that L2 thru L4 branches are correctly adjusted if necessary following the L1 adjustment and respect the pedantic posture concerning the
legacy reduction files. Thank you!"]` — read as: D-1 = **take the fix** (`template.py` keeps #23's `FileNotFoundError` behaviour; §10 D-1); K12/K13 **tabled**; Phase 2 is in
scope (the stack adjusted after L1 moves); the freeze is **pedantic**: the frozen files byte-equal to upstream, nothing of the fork's left in them, no tool touching them.

## 2. Verified facts (re-sealed 2026-10-21 00:15Z; this clone)

| # | Fact | Evidence |
|---|---|---|
| V1 | Tips: fork `exp` `c4d20e4` (= upstream `exp`), `exp-review` `c7741b2`, L1 `7f0a4ad`, L2 `3ea92cf`, L3 `941be51`, L4 `82b0854`, R `da2b889`, K10 `9cb0fbf`; upstream `exp-landing-l1-core` `c5ef58d`; no `qa/`, `review/`, `triage/` refs | `ls-remote` |
| V2 | L1 changed 14 of the scientist's 17 files (+153/−44); of these, **12 are frozen** (above) and **2 are kept** (`template.py` 62 lines, `new_reduction_from_template.py` 19) by D-1 | `git diff --stat 8971999 c5ef58d -- <17>` |
| V3 | The L1 commits whose hunks the freeze reverts, in the 12 files only: `87d09d0` (fork #14 lint baseline — raw strings, unused names, a loop → `writelines`), `6234dcc` (fork #41 — output-identical refactors in `background.py`, `dead_time_correction.py`, `peak_finding.py`, `output.py`), `c5ef58d` (noqa comments in `reduction_template_reader.py`, `time_resolved.py`, `new_reduction_template_reader.py`). **Not reverted:** `a70a3e2` (#23) and `bd9065b` (#26) — they touch only the two kept files and their tests | `git log 8971999..c5ef58d -- <17>` |
| V4 | Tests pinning the frozen changes: `tests/test_warning_hygiene.py` (new in 6234dcc, 307 lines) and `tests/unit/lr_reduction/test_output.py` (+110 in 6234dcc). Tests pinning the kept fix stay: `test_template_paths.py` (122), `test_template_file_handles.py` (81), the seven XMLs, `conftest.py` (+32), the three test edits of a70a3e2 | `git show --stat` of the commits |
| V5 | **L2–L4 and K10 touch none of the 17** (`git diff --stat c5ef58d 82b0854 -- <17>` empty; K10's two files are elsewhere); `merge-tree` of `7f0a4ad` with L2 and with K10 is clean (I-115) | measured; I-115 |
| V6 | ruff: `[tool.ruff] exclude = ["notebooks/**", "**/*.ipynb", "scripts/**", "tests/data/**"]`; pre-commit `ruff-check --fix --exit-non-zero-on-fix --extend-select RUF100`. The reverted files carry the lint the baseline fixed, so pre-commit goes red without an exclusion; `extend-exclude` adds without disturbing the four globs | `pyproject.toml:240-252` at `c5ef58d` |
| V7 | Shared imports (V1-67): `reduction_template_reader.py` by `web_report.py`; `dead_time_correction.py` by `scaling_factors/LRScalingFactors.py`; `template.py` by the new path (kept). A freeze restores upstream's behaviour, the behaviour upstream runs today | V1-67 |
| V8 | The (c) refactors are output-identical by the campaign's own evidence (6234dcc's equality tests), so reverting them changes no reduction output — L2's harness byte-identity is unaffected by the freeze itself; what changes outputs is upstream's `arctan` (`c4d20e4`), already in L1 and arriving in L2 by the forward merge — hence R-2 | 6234dcc; I-114/A-155 |
| V9 | R-2 does not exist yet; the group plan's rule (§3 R0, A-155): a re-derivation is a new branch `feature/landing-reference-2`, never an update of `feature/landing-reference` | group plan |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | **Freeze (content), one commit** `freeze: the legacy-reduction files return to upstream's content (PR #219 review, 2026-10-20)`: `git checkout c4d20e4 -- <the 12 files>`; body: the scientist's ask in one line, `Reverts: 87d09d0 (these files), 6234dcc, c5ef58d (these files)`; no ledger URL, no campaign identifier. After it, `git diff c4d20e4 <tip> -- <the 12>` is **empty** (the pedantic posture: byte-equal, no re-lint, no trailing-whitespace fix — the pre-commit hooks must not rewrite them; if a hook would, the hook's `exclude` gains the same paths in the same commit). |
| B2 | **Freeze (lint), one commit:** `pyproject.toml` `[tool.ruff] extend-exclude = [<the 12 paths>]` with the comment `# frozen legacy-reduction files (PR #219 review, 2026-10-20): upstream's content, not linted`. pre-commit and `ruff check .` green at the tip; `ruff check --no-exclude <a frozen file>` reports the old findings (the exclusion is load-bearing). |
| B3 | **Tests, one commit:** remove `tests/test_warning_hygiene.py`; `git checkout c4d20e4 -- tests/unit/lr_reduction/test_output.py`. Everything pinning the kept fix stays (V4). |
| B4 | **No rewrite:** the three commits sit on `7f0a4ad`; `feature/landing-l1-core` and #54 fast-forward; the human pushes the tip to `exp-landing-l1-core` (#219 fast-forwards). |
| B5 | **Phase 2 — the stack follows, gated tips only, in order.** After the Integrator's PASS on `qa/landing-l1-legacy-freeze` (L1′): (1) the Developer builds **R-2** = `feature/landing-reference-2`: `exp-review` @ `c7741b2` merged onto `c4d20e4` by the D-92 recipe (the same #215/#216 ↔ #48 resolution; upstream's `nr_reduction_calc.py` hunks are disjoint from the fork's), pushed once, immutable; P5 (`landing-purity.sh --complete`) on R-2. (2) **L2′** = `feature/landing-l2-reduction` + merge of L1′ (message `stack merge: landing-l1-core @ <L1′> — upstream c4d20e4 and the legacy freeze`), pushed, `qa/landing-l2-reduction` at L2′; the Integrator gates: G, the harness byte-identity on the eight scenarios **against R-2** (never R), P1 over `c4d20e4..L2′` for L2's set, P2 (merges skipped). (3) **L3′** = L3 + merge of L2′ → `qa/landing-l3-launcher`: G, P1/P2. (4) **L4′** = L4 + merge of L3′ → `qa/landing-l4-model-move`: G, P1/P2, **P3 `--move` at L4′ against R-2** with the enlarged `EXCL` (§10 D-4), P5. (5) **K10′** = `feature/log-level-console-v2` + merge of L1′ → `qa/log-level-console`: G (the reduction count drops by the removed tests). Each step merges only a tip the Integrator has passed; a FAIL stops the chain there, with the layer's `todo.md`. |
| B6 | **Proofs:** `Reverts:` accepted by P2 (done, A-157); `EXCL` enlarged by the frozen set — the 12 files, `tests/test_warning_hygiene.py`, `tests/unit/lr_reduction/test_output.py`, `pyproject.toml` — each with its reason (done, A-157); P3 (b) stays strict against the enlarged set; the only permitted difference in `pyproject.toml` between L4′ and R-2 is the `extend-exclude` block (the Integrator reads that one hunk). |

## 4. Files to change

| File | Change |
|---|---|
| the 12 frozen files | content = `c4d20e4`'s (B1) |
| `pyproject.toml` | `[tool.ruff] extend-exclude` = the 12 paths, dated comment (B2) |
| `tests/test_warning_hygiene.py` | removed (B3) |
| `tests/unit/lr_reduction/test_output.py` | content = `c4d20e4`'s (B3) |
| `feature/landing-reference-2` (new branch) | R-2 (B5.1) |
| `feature/landing-l2-reduction`, `-l3-launcher`, `-l4-model-move`, `feature/log-level-console-v2` | one merge commit each (B5.2–5) |
| ledger `scripts/landing-sanitize-check.sh`, `scripts/landing-purity.sh` (`EXCL`, read by `landing-proof.sh`) | done at dispatch (A-157) |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: the freeze commit | the 12 files byte-equal to `c4d20e4`; G green | T1, T4 |
| 2 | common: lint after the revert | pre-commit green only because of `extend-exclude`; the exclusion is shown load-bearing | T2 |
| 3 | edge: a pre-commit hook (end-of-file, trailing-whitespace) would rewrite a frozen file at commit | the hook's `exclude` gains the same paths in the same commit; T1 stays empty | T1 |
| 4 | edge: `web_report.py` after `reduction_template_reader.py` returns to upstream | its three repaired tests still pass (they test `web_report.py`) | G |
| 5 | edge: `test_output.py` returned, `output.py` frozen | the upstream tests pass against upstream's code | G |
| 6 | pathological: a frozen file's old lint is a real error (`F821`) | hidden by the exclusion; upstream runs that code today; named in the PR body | documented |
| 7 | pathological: the human's `exp-landing-l1-core` not fast-forwarded | #219 reviews the old tip; the push is the human's step | B4 |
| 8 | pathological: P3 run with the old `EXCL` | fails loudly on the frozen paths; the enlarged list is on the ledger before the build | B6 |
| 9 | Phase 2: a forward merge conflicts | none expected (V5; I-115 merge-tree clean); if one appears the Developer resolves it in the merge commit and states the resolution — never a rebase | T6 |
| 10 | Phase 2: L2′'s harness differs from R-2 | a real finding (the `arctan` change is in both sides; the freeze is output-identical) → STOP, the Integrator's todo; not auto-resolved | T7 |
| 11 | Phase 2: R-2's conflict resolution differs from R's | P3 noise at L4′; the Developer records R-2's resolution in its commit body and the Integrator compares `git diff da2b889 <R-2> -- <the resolved files>` to upstream's own change | T8 |
| 12 | Phase 2: K10′'s count | 10 + (197 − the removed tests); the Developer reports the number | T9 |
| 13 | out of scope: groups 2/3 deletion; K12; K13 | the scientist's/human's PRs; tabled | — |

## 6. Red-Green seed (the checks)

- **T1** `git diff --stat c4d20e4 <L1′> -- <the 12 files>` → empty.
- **T2** `pixi run pre-commit run --all-files` → green; `ruff check --no-exclude <a frozen file>` → non-empty.
- **T3** `git diff c4d20e4 <L1′> -- src/lr_reduction/template.py src/lr_reduction/new_reduction_from_template.py tests/test_template_paths.py tests/test_template_file_handles.py` → L1's hunks intact (the kept fix); `tests/test_warning_hygiene.py` absent; `git diff c4d20e4 <L1′> -- tests/unit/lr_reduction/test_output.py` → empty.
- **T4** G at L1′: install --locked, the lock check, `test-reduction`, `test-launcher`, each EXIT 0; the reduction count reported (172 − the removed tests).
- **T5** `git log --format=%s c4d20e4..<L1′>` = L1's twelve replay subjects + the base merge + the three freeze commits; no `todo.md`; `7f0a4ad` an ancestor.
- **T6** (Phase 2) each forward merge: `git merge-tree --write-tree <layer> <previous gated tip>` clean before the merge; the merge commit's tree equals it.
- **T7** (Phase 2) L2′: the harness byte-identity against R-2 on the eight scenarios, the must-fail proven (as I-98 B).
- **T8** (Phase 2) L4′: `landing-proof.sh --move <L4′> <R-2>` → (a) no difference outside `EXCL`, (b) the name-only diff equals R-2's excluded set; P5 on R-2 complete.
- **T9** (Phase 2) K10′: G green; the two K10 files unchanged by the merge.

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| one frozen file left at L1's content, or re-linted by a hook | T1 |
| the `extend-exclude` omitted | T2, G |
| `template.py` frozen by mistake (D-1 not applied) | T3 |
| `test_warning_hygiene.py` left in place | T4 (it fails against the frozen code) |
| a layer merged from an ungated tip | T6's provenance (the merged sha is not the Integrator's PASS sha) |
| L2′ measured against R instead of R-2 | T7 (differs by `arctan` — loud) |

## 8. Acceptance criteria

1. Phase 1: T1–T5 green; the three commits with the model trailer and the `Reverts:` line, no ledger URL or campaign identifier; the Integrator's PASS on `qa/landing-l1-legacy-freeze`; #54 shows the freeze; the human pushes L1′ to `exp-landing-l1-core`.
2. The PR body (the Integrator's) answers the scientist file by file: the 12 frozen (byte-equal to upstream, the exclusion explained); `template.py` and `new_reduction_from_template.py` **kept on the human's decision** — the `FileNotFoundError` fix is real and the module is shared with the new workflow — their call to revert; groups 2/3 returned to upstream's content, deletion their call.
3. Phase 2: T6–T9 green; the Integrator's PASS per layer (L2′, L3′, L4′, K10′); #51/#52/#53/#55 fast-forwarded; R-2 pushed once and named in the group plan's revision history.
4. The ledger tools (B6) and the group plan's exclusion list updated (A-157).

## 9. Learnings relied on

V1-67 (the file classification and the shared imports); `plans/stratified-landing-plan.md` (replay purity, `EXCL` as the one source, P3's strictness, R re-derived not updated —
A-155); I-114/I-115 (a base merge re-measures the layer; the harness against the rebuilt reference); A-149/A-151 (a plan's base and prescriptions are the Analyst's to get right).

## 10. Assumptions and decisions

- **D-1 — resolved by the human (2026-10-21): take the fix.** `template.py` and `new_reduction_from_template.py` keep L1's content (#23's `FileNotFoundError` instead of a `TypeError` four frames later, #26's closed file handle) with their tests. The PR body says so to the scientist, whose list named `template.py`.
- **D-2 — groups 2 and 3:** returned to upstream's content where L1 touched them (`new_reduction_template_reader.py`, `roi_selector.py`); `new_reduction_from_template.py` stays with the fix (D-1); deletion is the scientist's or the human's PR.
- **D-3 — K12 tabled** by the human; the removed content lives in git (6234dcc) for a later PR of the scientist's.
- **D-4 — proofs:** `EXCL` = `.github/workflows/test_and_deploy.yml`, `scripts/test/measure_fit_path_dependence.py`, the 12 frozen files, `tests/test_warning_hygiene.py`, `tests/unit/lr_reduction/test_output.py`, `pyproject.toml` (its only permitted difference the `extend-exclude` block); P3 (b) strict.
- **D-5 — K13 tabled** by the human.
- **D-6 — reverts and merges, never rewrites:** no history rewrite of any layer (the reviews on #219 and the fork drafts stay attached; the pre-push guard forbids it anyway).
- **D-7 — Phase 2 order:** gate L1′ first; each layer merges only a gated tip; a FAIL stops the chain at that layer.
- **D-8 — R-2:** a new branch by the group plan's rule; R stays as the record of the gates.

## Revision history

- **v1 — 2026-10-20 (A-156):** staged from the scientist's #219 comment and V1-67; not dispatched. Sealed against L1 @ `7f0a4ad` / upstream `exp` @ `c4d20e4`.
- **v1 dispatched — 2026-10-21 (A-157):** on the human's word (§1): D-1 = take the fix (the frozen set is 12 files; `template.py`, `new_reduction_from_template.py` and their tests kept); K12/K13 tabled; Phase 2 (R-2 and the gated forward merges of L2–L4 and K10) in scope; re-sealed (the fork's `exp` synced to `c4d20e4`). The ledger tools updated in the same act.
