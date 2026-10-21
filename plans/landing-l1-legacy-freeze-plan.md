# Plan: `landing-l1-legacy-freeze` — L1 returns the scientist's legacy-reduction files to upstream's content (freeze, pedantic: byte-equal), ruff stops linting them, the tests that pinned the frozen changes leave; `template.py`'s `FileNotFoundError` fix stays (the human's D-1); then the stack and K10 follow L1 through gated forward merges against a rebuilt reference

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l1-legacy-freeze` (K11; refs `triage/landing-l1-legacy-freeze` (v1), `triage/landing-l1-legacy-freeze-v2`; the slug amends `feature/landing-l1-core` by commits on top —
no rewrite — and tags `qa/landing-l1-legacy-freeze`; Phase 2 re-tags `qa/landing-l2-reduction`, `qa/landing-l3-launcher`, `qa/landing-l4-model-move`, `qa/log-level-console` at the
forward-merged tips) · **Status:** **DISPATCHED — v2 (attempt 2 of 3)**, 2026-10-21 (A-160), on I-120's REJECT of v1 @ `d8630d4` (the record is `plans/landing-l1-legacy-freeze-v1-todo.md` on the ledger,
commit `8b214ea` — not a `todo.md` on the branch, §10 D-9); v1 dispatched at A-157 on the human's word addressed to the campaign (§1), staged at A-156 from the scientist's #219
comment and V1-67. **v2 = commits on top of `d8630d4`** (D-118's pushed branch; nothing rewritten), then `qa/landing-l1-legacy-freeze` again ·
**Base:** `feature/landing-l1-core` @ **`7f0a4ad`** (L1 after the human's base merge of upstream `exp` `c4d20e4`, I-115). **The fork's `exp` = upstream `exp` = `c4d20e4`** (the
human synced it; #54's diff is clean again). The frozen files' content at `c4d20e4` equals `8971999`'s (`c4d20e4` changed only `nr_reduction_calc.py`, `settings.json`, an example) ·
**PRs:** #54 (fork, L1 → `exp`) and #219 (upstream, `exp-landing-l1-core` — the human pushes the new tip; the review thread stays attached) advance by fast-forward; #51/#52/#53/#55
fast-forward in Phase 2 · **Reviews:** design, test (block) · **Gate:** Phase 1 — G literal at L1's new tip; P1 over `c4d20e4..<tip>`; P2 with `Reverts:` accepted. Phase 2 — per
layer as §3 B5 says (G; L2's harness against R-2; P3 at L4 against R-2 with the enlarged exclusion list; P5 on R-2).

Campaign: exp-review-fixes

## Declared scope

**In (Phase 1, L1):** the **12** files L1 changed among the scientist's 17 that stay frozen — `launcher/scripts/{off_spec,quick_reduce,refracted_beam,xrr_reduction}.py`,
`src/lr_reduction/{background,dead_time_correction,output,peak_finding,reduction_template_reader,time_resolved,new_reduction_template_reader}.py`, `launcher/apps/roi_selector.py` —
returned to upstream's content byte for byte; the `ruff-check` hook's `exclude` in `.pre-commit-config.yaml` gains the 12 paths with a dated comment (**not** `pyproject.toml`: it is pixi's manifest and any edit stales the lock — D-116, amended at build A-158); `tests/test_noqa_tags.py` reads that same `exclude` and skips what it matches, with a guard that every frozen path exists and is one of the 12; `tests/test_warning_hygiene.py` reduced to the four tests of retained behaviour (v2; v1's deletion was wrong) and
`tests/unit/lr_reduction/test_output.py` returned to upstream's (it pins the frozen `output.py` changes). **Kept, the
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
| V4 | **Corrected at v2 (I-120):** `tests/test_warning_hygiene.py` was **created by `90a138f` (fork #24)** — its two tests `test_no_pyparsing_warning_from_mathtext` and `test_first_party_deprecation_still_visible` pin `pyproject.toml:223-234`'s pyparsing `filterwarnings` entry, which is L1-only, **retained** ("Out: everything else in L1") and not frozen; 6234dcc only extended the file with the W1–W3 tests of the frozen refactors and the W4 helper fix (`_reset_warning_registries` by `object.__getattribute__`) with its two `test_resetting_the_registries_*` tests, which pin the helper, not a frozen file. v1's "new in 6234dcc" was wrong, and B3 inherited it. `tests/unit/lr_reduction/test_output.py` (+110 in 6234dcc) pins the frozen `output.py` and is returned. Tests pinning the kept fix stay: `test_template_paths.py` (122), `test_template_file_handles.py` (81), the seven XMLs, `conftest.py` (+32), the three test edits of a70a3e2 | `git show --stat` of the commits |
| V5 | **L2–L4 and K10 touch none of the 17** (`git diff --stat c5ef58d 82b0854 -- <17>` empty; K10's two files are elsewhere); `merge-tree` of `7f0a4ad` with L2 and with K10 is clean (I-115) | measured; I-115 |
| V6 | ruff: `[tool.ruff] exclude = ["notebooks/**", "**/*.ipynb", "scripts/**", "tests/data/**"]`; pre-commit `ruff-check --fix --exit-non-zero-on-fix --extend-select RUF100`. The reverted files carry the lint the baseline fixed, so pre-commit goes red without an exclusion; `extend-exclude` would add without disturbing the four globs — **but (amended at build, D-116): `pyproject.toml` is pixi's manifest; adding the block makes `pixi install --locked` fail (`lock-file not up-to-date`), and a re-lock would drop `editable: true` (the restamp the Developer's contract forbids); #49 put its ruff selection in the hook's `args` for this reason. The pre-commit global `exclude` (`scripts/.*`) already covers the four `launcher/scripts/*`; upstream's frozen files have no trailing whitespace and end in a newline, so only ruff would re-lint them** | `pyproject.toml:240-252` at `c5ef58d`; D-116 |
| V10 | `tests/test_noqa_tags.py` (#49, in L1) reads the hook's args and checks every `noqa` tag in the tree; upstream's frozen files carry three tags #49 re-spelled (`new_reduction_template_reader.py:36`, `reduction_template_reader.py:20`, `time_resolved.py:25`), so a byte-equal freeze reds it unless the test skips what the hook excludes | D-116, measured |
| V7 | Shared imports (V1-67): `reduction_template_reader.py` by `web_report.py`; `dead_time_correction.py` by `scaling_factors/LRScalingFactors.py`; `template.py` by the new path (kept). A freeze restores upstream's behaviour, the behaviour upstream runs today | V1-67 |
| V8 | The (c) refactors are output-identical by the campaign's own evidence (6234dcc's equality tests), so reverting them changes no reduction output — L2's harness byte-identity is unaffected by the freeze itself; what changes outputs is upstream's `arctan` (`c4d20e4`), already in L1 and arriving in L2 by the forward merge — hence R-2. **Corrected at Phase 2 (I-122):** that change sits on the calc-theta path, and IPTS-36119's `reduce_settings.json` has `useCalcTheta: false`, so the eight harness scenarios **cannot tell R from R-2** — L2′'s byte-identity to R-2 proves L2's own reduction path unchanged by the merge, not upstream's change; a ninth scenario `S6ct` (`useCalcTheta: true`) added to `rereduction-scenarios.sh` (A-162) makes later gates see it, its must-fail R vs R-2 | 6234dcc; I-114/A-155; I-122 |
| V9 | R-2 does not exist yet; the group plan's rule (§3 R0, A-155): a re-derivation is a new branch `feature/landing-reference-2`, never an update of `feature/landing-reference` | group plan |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | **Freeze (content), one commit** `freeze: the legacy-reduction files return to upstream's content (PR #219 review, 2026-10-20)`: `git checkout c4d20e4 -- <the 12 files>`; body: the scientist's ask in one line, `Freeze: PR #219 review, 2026-10-20` and `Reverts: 87d09d0 (these files), 6234dcc, c5ef58d (these files)`; no ledger URL, no campaign identifier. After it, `git diff c4d20e4 <tip> -- <the 12>` is **empty** (the pedantic posture: byte-equal; B2's hook exclusion is committed **first**, so the revert commit's own hooks cannot re-lint the frozen files). |
| B2 | **Freeze (lint), one commit, first in order (D-116 option A):** `.pre-commit-config.yaml`'s `ruff-check` hook `exclude` regex gains the 12 frozen paths (anchored, one per line in a YAML block scalar) with the comment `# frozen legacy-reduction files (PR #219 review, 2026-10-20): upstream's content, not linted`; `pyproject.toml` untouched (pixi's manifest — an edit stales the lock). In the same commit `tests/test_noqa_tags.py` reads the hook's `exclude` (it already reads `hook_args()`) and skips the files it matches — one source — **and asserts that every path in the hook's frozen block exists in the tree and is one of the 12**, so a typo or a widened exclusion cannot hide real lint (I-118's mutation). pre-commit green at the tip; `pixi run ruff check <a frozen file>` by hand reports the old findings (the exclusion is load-bearing; the human's and the scientists' tool is pre-commit). Provenance: `Freeze: PR #219 review, 2026-10-20` (new content, neither a replay nor a revert — A-159, D-117). **Order: B2, then B1, then B3.** **v2 (I-120 R2):** the guard also **compiles** the hook's `exclude` and asserts (i) every one of the 12 paths matches it and (ii) no tracked `.py` (`git ls-files '*.py'`) matches it unless it is one of the 12 or under `tests/data/` — the literal line check alone is blind to regex-shaped widenings (a `.*` line, a `(?x)` opener, an alternative after the close, `tests/data/.*` → `tests/.*`: four shapes measured green while hiding a file with a used blanket `# noqa`); keep the literal check too (it alone catches a typo'd extra path). The stale docstring at `test_noqa_tags.py:122` ("from `pyproject.toml` only") is corrected in the same commit. |
| B3 | **Tests (v1, done at `d8630d4`):** `test_output.py` returned to upstream's; `test_warning_hygiene.py` deleted — **the deletion was v1's error.** **v2, one commit on top of `d8630d4`:** `tests/test_warning_hygiene.py` **comes back and holds exactly the tests that pin retained behaviour** — #24's two filter guards and W4's two registry-reset tests, with the `_reset_warning_registries` (W4 form — `90a138f`'s verbatim `getattr` reset emits two mpmath DeprecationWarnings with sympy loaded, measured) and `_render_mathtext` helpers; none of the W1–W3 tests of frozen files; the `os`, `numpy`, `scipy.special` imports go (the measured shape: `7f0a4ad`'s lines 1–10 with the docstring closed, the imports `sys`, `types`, `warnings`, `pytest`, lines 28–127 → **4 passed**, ruff `--extend-select RUF100` clean; reduction count 139 → 143). The body: `Freeze: …`, `Reverts: 6234dcc (its W1–W3 tests)`, and the guard measured both ways — the `filterwarnings` line removed reds `test_no_pyparsing_warning_from_mathtext`, widened to `ignore::DeprecationWarning` reds `test_first_party_deprecation_still_visible`. The same pass takes the cheap advisories: the hook comment gains "lint through `pre-commit run ruff-check --all-files`; `ruff check .` by hand reports the frozen files' findings" and the exit condition "drop an entry when the file is next intentionally changed or deleted"; a0f7ce3's unqualified `Reverts:` cannot change (history stands) and is qualified in v2's body instead. |
| B4 | **No rewrite:** the three commits sit on `7f0a4ad`; `feature/landing-l1-core` and #54 fast-forward; the human pushes the tip to `exp-landing-l1-core` (#219 fast-forwards). |
| B5 | **Phase 2 — the stack follows, gated tips only, in order.** After the Integrator's PASS on `qa/landing-l1-legacy-freeze` (L1′): (1) the Developer builds **R-2** = `feature/landing-reference-2`: `exp-review` @ `c7741b2` merged onto `c4d20e4` by the D-92 recipe (the same #215/#216 ↔ #48 resolution; upstream's `nr_reduction_calc.py` hunks are disjoint from the fork's), pushed once, immutable; P5 (`landing-purity.sh --complete`) on R-2. (2) **L2′** = `feature/landing-l2-reduction` + merge of L1′ (message `stack merge: landing-l1-core @ <L1′> — upstream c4d20e4 and the legacy freeze`), pushed, `qa/landing-l2-reduction` at L2′; the Integrator gates: G, the harness byte-identity on the eight scenarios **against R-2** (never R), P1 over `c4d20e4..L2′` for L2's set, P2 (merges skipped). (3) **L3′** = L3 + merge of L2′ → `qa/landing-l3-launcher`: G, P1/P2. (4) **L4′** = L4 + merge of L3′ → `qa/landing-l4-model-move`: G, P1/P2, **P3 `--move` at L4′ against R-2** with the enlarged `EXCL` (§10 D-4), P5. (5) **K10′** = `feature/log-level-console-v2` + merge of L1′ → `qa/log-level-console`: G (the reduction count drops by the removed tests). Each step merges only a tip the Integrator has passed; a FAIL stops the chain there, with the layer's `todo.md`. |
| B6 | **Proofs:** `Reverts:` accepted by P2 (A-157); `EXCL` = the 12 files, `tests/test_warning_hygiene.py`, `tests/unit/lr_reduction/test_output.py`, `.pre-commit-config.yaml`, `tests/test_noqa_tags.py` (A-158: `pyproject.toml` dropped — it stays identical to R-2, and an excluded-but-identical file fails (b)); P3 (b) strict against that set; the Integrator reads the L4′↔R-2 diffs of `.pre-commit-config.yaml` (only the 12 paths and the comment) and `tests/test_noqa_tags.py` (only the skip and the guard) by hand. `landing-proof.sh` legs (a) and `--move` read `EXCL` (A-158, I-117's gap closed and regression-checked). P1: L1's set gains the frozen launcher paths (`launcher/scripts/{off_spec,quick_reduce,refracted_beam,xrr_reduction}.py`, `launcher/apps/roi_selector.py` — only #14's exception commit had touched them, so the freeze was a STRAY; A-159, D-117) and P2 accepts `Freeze:` — B1 stays a checked commit, not an exception. |

## 4. Files to change

| File | Change |
|---|---|
| the 12 frozen files | content = `c4d20e4`'s (B1) |
| `.pre-commit-config.yaml` | the `ruff-check` hook's `exclude` += the 12 paths, dated comment (B2) |
| `tests/test_noqa_tags.py` | skips what the hook's `exclude` matches; the guard assertion on the frozen block (B2) |
| `pyproject.toml` | **untouched** (D-116) |
| `tests/test_warning_hygiene.py` | v1 deleted it (wrong); v2 restores it at the four-test shape (B3) |
| `tests/unit/lr_reduction/test_output.py` | content = `c4d20e4`'s (B3) |
| `feature/landing-reference-2` (new branch) | R-2 (B5.1) |
| `feature/landing-l2-reduction`, `-l3-launcher`, `-l4-model-move`, `feature/log-level-console-v2` | one merge commit each (B5.2–5) |
| ledger `scripts/landing-sanitize-check.sh`, `scripts/landing-purity.sh` (`EXCL`, read by `landing-proof.sh`) | done at dispatch (A-157) |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: the freeze commit | the 12 files byte-equal to `c4d20e4`; G green | T1, T4 |
| 2 | common: lint after the revert | pre-commit green only because of the hook's `exclude`; shown load-bearing | T2 |
| 2b | pathological: a regex-shaped widening of the hook's `exclude` (`.*` line, `(?x)` opener, an alternative after the close) | the compiled check in the guard reds | T2c |
| 2c | edge: the retained pyparsing filter in `pyproject.toml` | its two #24 guards stay and go red if the filter is removed or widened | T3b |
| 3 | edge: a hook would rewrite a frozen file at commit | the exclusion commit comes first (B2 → B1 → B3); T1 stays empty | T1 |
| 3b | pathological: the hook's `exclude` widened to a non-frozen file (a typo, or hiding real lint) | the guard in `test_noqa_tags.py` fails | T2b |
| 4 | edge: `web_report.py` after `reduction_template_reader.py` returns to upstream | its three repaired tests still pass (they test `web_report.py`) | G |
| 5 | edge: `test_output.py` returned, `output.py` frozen | the upstream tests pass against upstream's code | G |
| 6 | pathological: a frozen file's old lint is a real error (`F821`) | hidden by the exclusion; upstream runs that code today; named in the PR body | documented |
| 7 | pathological: the human's `exp-landing-l1-core` not fast-forwarded | #219 reviews the old tip; the push is the human's step | B4 |
| 8 | pathological: P3 run with the old `EXCL` | fails loudly on the frozen paths; the enlarged list is on the ledger before the build | B6 |
| 9 | Phase 2: a forward merge conflicts | none expected (V5; I-115 merge-tree clean); if one appears the Developer resolves it in the merge commit and states the resolution — never a rebase | T6 |
| 10 | Phase 2: L2′'s harness differs from R-2 | a real finding (the `arctan` change is in both sides; the freeze is output-identical) → STOP, the Integrator's todo; not auto-resolved. Coverage caveat (I-122): S0–S5 and the 8-column set run with `useCalcTheta: false` and are blind to `c4d20e4`'s path; only `S6ct` (A-162) sees it | T7, T7b |
| 11 | Phase 2: R-2's conflict resolution differs from R's | P3 noise at L4′; the Developer records R-2's resolution in its commit body and the Integrator compares `git diff da2b889 <R-2> -- <the resolved files>` to upstream's own change | T8 |
| 12 | Phase 2: K10′'s count | 10 + (197 − the removed tests); the Developer reports the number | T9 |
| 13 | out of scope: groups 2/3 deletion; K12; K13 | the scientist's/human's PRs; tabled | — |

## 6. Red-Green seed (the checks)

- **T1** `git diff --stat c4d20e4 <L1′> -- <the 12 files>` → empty.
- **T2** `pixi run pre-commit run --all-files` → green; `pixi run ruff check <a frozen file>` → non-empty (the hook exclusion is load-bearing). **T2b** `pytest tests/test_noqa_tags.py` green at L1′; with the hook's `exclude` widened to one non-frozen file that carries a blanket `# noqa`, red (the guard).
- **T2c** (v2) the compiled-exclusion guard: green at L1′; red for each of the four regex-shaped widenings and for drop-one (the test review's prototype).
- **T3b** (v2) `tests/test_warning_hygiene.py` at L1′ holds exactly `test_no_pyparsing_warning_from_mathtext`, `test_first_party_deprecation_still_visible`, `test_resetting_the_registries_runs_no_module_hook`, `test_resetting_the_registries_with_mpmath_loaded_warns_nothing` (4 passed, ruff clean); the `filterwarnings` line removed → the first red; widened to `ignore::DeprecationWarning` → the second red.
- **T3** `git diff c4d20e4 <L1′> -- src/lr_reduction/template.py src/lr_reduction/new_reduction_from_template.py tests/test_template_paths.py tests/test_template_file_handles.py` → L1's hunks intact (the kept fix); `tests/test_warning_hygiene.py` holds only the four retained tests (T3b; v2 — I-121's correction of v1's "absent"); `git diff c4d20e4 <L1′> -- tests/unit/lr_reduction/test_output.py` → empty; `git diff 7f0a4ad <L1′> -- pyproject.toml pixi.lock` → empty (untouched by the freeze).
- **T4** G at L1′: install --locked, the lock check, `test-reduction`, `test-launcher`, each EXIT 0; the reduction count reported (172 − the removed tests).
- **T5** `git log --format=%s c4d20e4..<L1′>` = L1's twelve replay subjects + the base merge + the three freeze commits; no `todo.md`; `7f0a4ad` an ancestor.
- **T6** (Phase 2) each forward merge: `git merge-tree --write-tree <layer> <previous gated tip>` clean before the merge; the merge commit's tree equals it.
- **T7** (Phase 2) L2′: the harness byte-identity against R-2 on the eight scenarios, the must-fail proven (as I-98 B). **Done at I-122: 0 DIFFER on 8, must-fail red.**
- **T7b** (added A-162, after the fact — the Integrator's call whether now or at the next L2 gate): `S6ct` on R (`da2b889`) vs R-2 (`b3f9c75`) must DIFFER (the calc-theta coverage's must-fail); `S6ct` on L2′ vs R-2 must be identical.
- **T8** (Phase 2) L4′: `landing-proof.sh --move <L4′> <R-2>` → (a) no difference outside `EXCL`, (b) the name-only diff equals R-2's excluded set; P5 on R-2 complete.
- **T9** (Phase 2) K10′: G green; the two K10 files unchanged by the merge.

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| one frozen file left at L1's content, or re-linted by a hook | T1 |
| the hook `exclude` omitted | T2, G |
| the hook `exclude` widened beyond the 12 | T2b |
| B1 committed before B2 | T1 (the revert commit's hook re-lints) |
| `test_warning_hygiene.py` deleted outright (v1) or #24's guards dropped | T3b |
| the noqa guard literal-only (regex-shaped widening hides a file) | T2c |
| `template.py` frozen by mistake (D-1 not applied) | T3 |
| the W1–W3 tests of frozen files left in `test_warning_hygiene.py` (v1's wording: the file "left in place") | T4 (they fail against the frozen code) or T3b |
| a layer merged from an ungated tip | T6's provenance (the merged sha is not the Integrator's PASS sha) |
| L2′ measured against R instead of R-2 | T7 **only with `S6ct`** — the eight original scenarios cannot tell R from R-2 (I-122 measured identical data on every scenario; the masked DIFFERs were the day folder in `# Config:`, now masked); without `S6ct` this mutation is silent |

## 8. Acceptance criteria

1. Phase 1: T1–T5 green; the three commits with the model trailer and the `Reverts:` line, no ledger URL or campaign identifier; the Integrator's PASS on `qa/landing-l1-legacy-freeze`; #54 shows the freeze; the human pushes L1′ to `exp-landing-l1-core`.
2. The PR body (the Integrator's) answers the scientist file by file: the 12 frozen (byte-equal to upstream, the exclusion explained); `template.py` and `new_reduction_from_template.py` **kept on the human's decision** — the `FileNotFoundError` fix is real and the module is shared with the new workflow — their call to revert; groups 2/3 returned to upstream's content, deletion their call.
3. Phase 2: T6–T9 green; the Integrator's PASS per layer (L2′, L3′, L4′, K10′); #51/#52/#53/#55 fast-forwarded; R-2 pushed once and named in the group plan's revision history.
4. The ledger tools (B6) and the group plan's exclusion list updated (A-157, corrected A-158).

## 9. Learnings relied on

V1-67 (the file classification and the shared imports); `plans/stratified-landing-plan.md` (replay purity, `EXCL` as the one source, P3's strictness, R re-derived not updated —
A-155); I-114/I-115 (a base merge re-measures the layer; the harness against the rebuilt reference); A-149/A-151 (a plan's base and prescriptions are the Analyst's to get right).

## 10. Assumptions and decisions

- **D-1 — resolved by the human (2026-10-21): take the fix.** `template.py` and `new_reduction_from_template.py` keep L1's content (#23's `FileNotFoundError` instead of a `TypeError` four frames later, #26's closed file handle) with their tests. The PR body says so to the scientist, whose list named `template.py`.
- **D-2 — groups 2 and 3:** returned to upstream's content where L1 touched them (`new_reduction_template_reader.py`, `roi_selector.py`); `new_reduction_from_template.py` stays with the fix (D-1); deletion is the scientist's or the human's PR.
- **D-3 — K12 tabled** by the human; the removed content lives in git (6234dcc) for a later PR of the scientist's.
- **D-4 — proofs (amended A-158):** `EXCL` = `.github/workflows/test_and_deploy.yml`, `scripts/test/measure_fit_path_dependence.py`, the 12 frozen files, `tests/test_warning_hygiene.py`, `tests/unit/lr_reduction/test_output.py`, `.pre-commit-config.yaml`, `tests/test_noqa_tags.py`; P3 (b) strict; the two config/test diffs read by hand (B6). Option B (a hand-stamped lock) is not gateable (I-118); C breaks the pedantic posture.
- **D-5 — K13 tabled** by the human.
- **D-6 — reverts and merges, never rewrites:** no history rewrite of any layer (the reviews on #219 and the fork drafts stay attached; the pre-push guard forbids it anyway).
- **D-7 — Phase 2 order:** gate L1′ first; each layer merges only a gated tip; a FAIL stops the chain at that layer.
- **D-8 — R-2:** a new branch by the group plan's rule; R stays as the record of the gates.
- **D-9 — the rejection record of an in-place leaf lives on the ledger (I-120's question, answered):** a leaf that amends a shared branch in place (`feature/landing-l1-core` is #54's head, #51/#55's base and what the human carries to #219) gets its rejection record as `plans/<slug>-v<N>-todo.md` on the ledger, never a `todo.md` on the branch; the `review/<slug>` tag points at the rejected tip; the Analyst reads the ledger file. The rule for in-place leaves from here; a kit pin folds it into `Integrator.md` step 4 (`todo-in-place-leaf-rejection-record-on-the-ledger.md`).

## Revision history

- **v1 — 2026-10-20 (A-156):** staged from the scientist's #219 comment and V1-67; not dispatched. Sealed against L1 @ `7f0a4ad` / upstream `exp` @ `c4d20e4`.
- **v1 dispatched — 2026-10-21 (A-157):** on the human's word (§1): D-1 = take the fix (the frozen set is 12 files; `template.py`, `new_reduction_from_template.py` and their tests kept); K12/K13 tabled; Phase 2 (R-2 and the gated forward merges of L2–L4 and K10) in scope; re-sealed (the fork's `exp` synced to `c4d20e4`). The ledger tools updated in the same act.
- **v1 amended at build — 2026-10-21 (A-158), on D-116:** option A — the lint exclusion in the pre-commit hook, `pyproject.toml` untouched (pixi's manifest; the lock), `tests/test_noqa_tags.py` skipping what the hook excludes with a guard (I-118's mutation); commit order B2 → B1 → B3; `EXCL` corrected (drop `pyproject.toml`, add `.pre-commit-config.yaml` and `tests/test_noqa_tags.py`); `landing-proof.sh` legs (a)/`--move` read `EXCL` (I-117). Not a new attempt: the plan's own B2 was the defect.
- **v1 amended at build — 2026-10-21 (A-159), on D-117:** the freeze commits carry `Freeze: PR #219 review, 2026-10-20` (B2's new content had no provenance form; B1/B3 keep their `Reverts:`); P1's L1 set gains the five frozen launcher paths so B1 is checked rather than excepted. Trees unchanged (B2 `60fbbe2`, B1 `a9fc272`, B3 `a4365d1` re-made with the lines); G measured at the final trees: 10 + 139, exit 0.

### v2 — 2026-10-21 (A-160): I-120's REJECT of v1 @ `d8630d4` (attempt 1 of 3; record `plans/landing-l1-legacy-freeze-v1-todo.md`, ledger `8b214ea`)

Cause: **B1 blocking** — v1's B3 deleted `tests/test_warning_hygiene.py` on the plan's wrong premise ("new in 6234dcc"); the file was created by fork #24 and its two guards pin the
retained pyparsing `filterwarnings` entry (plus W4's two helper tests); after `d8630d4` nothing pinned the filter and `pyproject.toml:231-232`'s comment pointed at nothing. **Fix as
behaviour:** the file exists at L1′ with exactly the four retained tests and their helpers (B3), the guard measured both ways. **R2** (a body claim failed its check): the noqa guard
was blind to regex-shaped widenings — it now compiles the exclusion and checks it against the 12 and against every tracked `.py` (B2). The cheap advisories ride along (the hook
comment's lint-by-pre-commit and exit-condition lines; the stale docstring; v2's body qualifies a0f7ce3's `Reverts:`). Everything else at `d8630d4` was green (T1, T3, T5, P1, P2,
G 10 + 139, scope 16 files). **Shape:** commits on top of `d8630d4`; nothing rewritten; `qa/landing-l1-legacy-freeze` again. Attempt 2 of 3; a third rejection escalates.

**Phase 1 PASS — 2026-10-21 (I-121):** v2 @ `81acc87` (`fc99453` + `81acc87` on `d8630d4`): #24's guards back and live both ways, the noqa guard compiled (red on every regex shape, drop-one, a typo'd extra path, `[e]`, `\.py?`, `.+`, an inline comment under `(?x)`), T1, T3 (as corrected), G 10 + 143, pre-commit rc 0; #54 fast-forwarded to `81acc87` with a file-by-file section answering the scientist's #219 list; no `review/` or `qa/` tag left. **Phase 2 (D-122):** R-2 = `feature/landing-reference-2` @ `b3f9c75` (R + upstream's `8971999..c4d20e4` exactly; P5 complete); L2′ = `3c906fc` (clean stack merge; G 10 + 345; P1 clean) at `qa/landing-l2-reduction` — the Integrator's T7 (the harness against R-2) next; P2's one red in L2′'s range is the pre-existing `5390872` markup, now allowed by name in the sanitize check (A-161). The plan's T3 wording corrected (A-161).

**Phase 2, L2′ PASS — 2026-10-21 (I-122):** R-2 verified (tree = merge-tree(R, `c4d20e4`); its name-only diff from R exactly `c4d20e4`'s three files); L2′ `3c906fc` — tree = git's merge, L2's own diff from L1′ unchanged (14 files), P1 clean, P2 clean with the named allowance (regression-checked both ways), G 10 + 345, harness 0 DIFFER on 8 vs R-2 with the must-fail red; #51 fast-forwarded, `MERGEABLE`. **Finding (not blocking):** the harness is blind to `c4d20e4`'s change (`useCalcTheta: false`) — V8, §5 row 10 and the §7 "loud" row corrected; `S6ct` added to the scenarios and the day folder added to the mask (A-162). Next: L3′, then L4′ (T8 `--move` against R-2), then K10′ (T9).
