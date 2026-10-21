# Plan: `stratified-landing` — the fork's `exp-review` work re-derived as four sanitized, by-area layers on upstream `exp` (L1 core + harness, L2 reduction, L3 launcher, L4 the model-module move), each green on its own gate, the L3 tip tree-identical to the reference

**Campaign:** `exp-review-fixes` · **Leaves:** `landing-l1-core` → `landing-l2-reduction` → `landing-l3-launcher` → `landing-l4-model-move`
(refs `triage/<leaf>`, `feature/<leaf>`, `qa/<leaf>`; one plan, four work orders — each leaf's `Declared scope` is its own block below) ·
**Status:** **L1 DISPATCHED 2026-10-20 (A-128)** — `triage/landing-l1-core` on the K6 trigger (#49 merged 2026-10-20 01:56Z, `c7741b2`, tree `cfe18ef`, I-94); L2–L4 staged, each
dispatching on the previous leaf's PASS — v1 (attempt 1 of N = 3 per leaf), authored 2026-10-19 (A-126) on the human's charter word; the
trigger was **#49 merged or closed** (`[human, 2026-10-19 (V1-58): "This work can be staged and started after #49 is merged."]`), (K5 `launcher-tab-order-test`
is **superseded** by the human's direct fix `1bffee1`, I-93 — R carries it, §10 D-5). On the trigger: re-seal §2 against the then-current `exp-review`
and upstream `exp` tips, the human syncs the fork's `exp` to upstream's tip (§3 R0 i), dispatch L1; each later leaf dispatches on the previous leaf's Integrator PASS (stacking rule, clause 3) ·
**Base:** L1 cut `--no-track` from **upstream `exp` at its tip** (`8971999` on 2026-10-19, fetched by URL — upstream is read-only; the fork's own
`exp` branch fast-forwarded to that tip by the human before dispatch, §3 R0 i — the branch L1's draft PR targets); L2 on `feature/landing-l1-core` at its PASS tip; L3 on
`feature/landing-l2-reduction`; L4 on `feature/landing-l3-launcher` · **PR target:** draft PRs on the fork, each `--base` the previous layer's branch
(L1 `--base exp` — the fork's `exp`, synced to upstream's tip by the human, §3 R0 i), stacked; the upstream PRs
are the human's acts (charter: upstream read-only; `[human, 2026-10-02]`) · **Depends on:** #49's fate (D-4); K5 before L3 (D-5) ·
**Review domains:** design, test (block); numerical-diagnostics (advise: L2's outputs byte-identical to the reference's) · **Kind:** **reduction-path**
(L2 rewrites the reduction's history; charter §4's baseline rule applies to L2) + launcher (L3, L4) + harness (L1) ·
**Sources:** `[human, 2026-10-19 (to the Advisor, verbatim in V1-58): "I am willing [to] engage the campaign to generate these stratified branches as part
of the campaign work. The branches should be *sanitized* on the fork so that they can be turned into acceptable pull requests against upstream:exp.
*definitely* starting from the current upstream exp and continuing. … I have recently received approval notification for 'exp-qa' … and 'exp-next' …
This work can be staged and started after #49 is merged."]`; V1-57 (the scientists' compartmentalization questions; the three strata; the by-area
shape; the empty-diff gate); `todo-upstream-exp-review-carries-fork-ci-config.md` (what "sanitized" excludes); charter §3 row (A-125).

Campaign: exp-review-fixes

## Declared scope (the group)

**Behaviours in.** (1) Four branches on the fork, each based on the previous (L1 on upstream `exp`'s tip), each carrying one area of the fork's work
since the upstream merge base, **sanitized**: no fork-only CI configuration, no campaign artefacts (`todo.md`, `plans/`, learnings documents, mutation
batteries unless D-3 keeps them), no protocol refs or merge noise (the only refs are `exp`, `feature/landing-reference` and the four leaves' `feature/`·`qa/` refs); every commit attributed (the original authors' trailers carried). (2) Each layer is
**green on its own gate** (`pixi run test-reduction`, which depends on `test-launcher`, from the layer's tip). (3) The L3 tip is **tree-identical to the
reference R outside the exclusion list, and differs from R by exactly that list** (§3 R0: `exp-review` at its tip at dispatch — `1bffee1` on 2026-10-19 — merged with upstream `exp` @ `8971999`, conflicts resolved once,
pushed by the Developer as `feature/landing-reference`, immutable by convention) — the proof is `scripts/landing-proof.sh <L3 tip> <R>`
(P3: (a) no difference outside the exclusion list, (b) the name-only diff is exactly the excluded paths); L4 differs from R by exactly the module move. (4) Each layer's diff touches only its area's files
(`scripts/landing-purity.sh`, §6 P1), with the exceptions §2 names (the mechanical ruff baseline; `reduction_domains` and its two call sites).

**Explicitly OUT.** Pushing to upstream, opening upstream PRs, or touching upstream `exp-review`/`exp-qa`/`exp-next` (the human's); the review
tier's deployment and `nr_launcher.sh` (`exp-qa`/`exp-next` retire `--exp-review`: a later deploy slug, charter §5); any behaviour change in any file
(a replayed hunk is the fork's hunk; a conflict resolution against #215/#216 is justified in the commit body and is the *only* new content); the
open draft PRs #22, #29, #32 (tabled/not campaign); changing what the fork's `exp-review` is (it stays the campaign base).

### `landing-l1-core` — Declared scope
**Files in.** The harness and configuration: `pyproject.toml` (test tasks, `pytest-timeout`, ruff config, versioningit glob), `pixi.lock` (as the
replayed PRs left it), `.pre-commit-config.yaml`, `scripts/check_lock_format.sh`, `scripts/pixi_lock_check.sh`, `docs/developer/developer.rst` (#20's hook
documentation), `launcher/tests/__init__.py` (#15's package), `launcher/tests/conftest.py`, `launcher/tests/test_harness.py`, `tests/conftest.py`,
`tests/test_noqa_tags.py` (#49); **the core files no later layer owns** (D-93): `src/lr_autoreduce/{new_reduce_REF_L.py, reduce_REF_L.py}`,
`src/lr_reduction/{instrument_settings.py, new_reduction_template_reader.py, reduction_template_reader.py, time_resolved.py, web_report.py}` (#49's
comment-only hunks; `time_resolved.py` is upstream's, PR #96 — not the fork's `new_reduction_time_resolved.py`, which is L2's); the core fixes: `src/lr_reduction/{template.py, new_reduction_from_template.py, background.py,
dead_time_correction.py, output.py, peak_finding.py}`; `src/lr_reduction/reduction_domains.py` with the two call-site hunks in `nr_reduction_calc.py`
and `nr_tools.py` (split from #28, §2 row a4efd95); #14's mechanical ruff baseline across `launcher/` and `src/` (the one lane-purity exception, §2).
**Entries replayed:** 2127343 (#14), d1a3bab…a4ae8b8 (#15), fff2b92…05c964f (#19), 11170ff (#20, minus `.github/`), 633950c (#21), 04c6e53/547dc14/3fb6019
(#23), 0d3c73b + 376a616 (#24), d0599f9 (#26), 508f70d (#27), c39efe9 (#41), the `reduction_domains` part of a4efd95 (#28). **Not:** `.github/workflows/*`
(D-2), `dc84af7`/`e6e4e27`/`ba14217`/`7497b28` (campaign `todo.md` commits: nothing to replay), `f5bd6d2` (an upstream merge: nothing to replay).

### `landing-l2-reduction` — Declared scope
**Files in.** `src/lr_reduction/{new_reduction_from_file.py, nr_reduction_calc.py, nr_tools.py, save_reduced_data.py, binary_processing.py,
direct_beam_maker.py, new_reduction_time_resolved.py, example_direct_beam.py, example_time_slices.py, example_nr_reduction.py}`, `tests/unit/lr_reduction/*`
and `tests/test_time_resolved.py`. **Entries replayed:** bb98bf3 (#30, the `src` + test half; its synthesis document excluded), 93f6ed6 (#34), 8a31b67 (#46),
34dc1b9 (#48 — **its reduction half**: `src/` + `tests/`; the launcher half goes to L3), with the #215/#216 conflicts in `direct_beam_maker.py` /
`example_direct_beam.py` resolved as in R (§3 R0). **Byte-identity:** the reference baseline rule (charter §4) — the Integrator's `compare_columns.sh`
and `check_headers.py` between R and the L2 tip on the harness scenarios: identical.

### `landing-l3-launcher` — Declared scope
**Files in.** `launcher/**` (apps, `new_launcher.py`, `launcher/tests/*` beyond the harness files L1 owns), the three Qt-free model modules
`src/lr_reduction/{settings_document.py, field_spec.py, roi_estimate.py}` (created by #28, grown by the editor lane; moved in L4),
`scripts/test/*` if D-3 keeps them. **Entries replayed:** 246a0da (#16), 3810314 (#17), 3e0fda5 (#18), a4efd95 (#28, the editor half), 4e5f669, c34c8c5
(#33), e313f38 (#35), b86237b (#36), 2324e5c (#37), 8bec251 (#38), 5a8742d (#39), b6b9381 (#40), d1a9b3a (#43), e7b8524 (#44), eb255b4 (#45), 35e52b2 (#47),
#42 and the launcher half of 34dc1b9 (#48: `launcher/apps/time_resolved.py`, `new_launcher.py`, `launcher/tests/test_time_resolved.py`), 62e21d1,
`1bffee1` (the human's tab-order test fix, I-93), then #49's launcher, model and launcher-test hunks (`c7741b2`, split by file — D-4; its L1 hunks
went with L1's last commit, its L2 test hunks go with L2's). **The proof** lives here: `git diff --stat feature/landing-l3-launcher <R>` → empty.

### `landing-l4-model-move` — Declared scope
**Files in.** `git mv src/lr_reduction/{settings_document.py, field_spec.py, roi_estimate.py} launcher/model/` (the target package name is D-7) in its
own commit; the two import sites (`launcher/apps/settings_editor.py`, `launcher/apps/roi_dialog.py`) and the tests that import them; `pyproject.toml`
only if packaging needs it (`launcher` is already a package). **Behaviour:** `git grep -l "settings_document\|field_spec\|roi_estimate" src/` empty before
and after (nothing in the reduction imports them — V1-57, verified §2); the suite green; `git diff --stat <L4 tip> <R>` lists exactly the moved files
and the import sites (renames shown as renames: `--find-renames`).

## 1. Request and symptom

The scientists reviewing `/SNS/REF_L/shared/lr_reduction/exp-review` are uncomfortable with "the depth of changes to the core reduction code" and want
the launcher work compartmentalized under `launcher/**`. The fork's `exp-review` is one chronological history mixing three strata (V1-57): the
scientists' own new-workflow modules (theirs), the campaign's reduction features on those modules (~700 lines, requested), the campaign-new Qt-free
model modules (2,511 lines, imported only by the launcher) and the launcher. The human's decision (V1-58): the campaign re-derives the work as
sanitized by-area layers on current upstream `exp`, from which the human opens upstream PRs; `exp-qa`/`exp-next` will replace the `--exp-review`
special case.

## 2. Verified facts (2026-10-19; fork `exp-review` @ `62e21d1` = upstream `exp-review` at the census, `1bffee1` since 19:23 EDT — the human's direct test fix, I-93; **re-sealed at L1's dispatch 2026-10-20 02:0xZ: `exp-review` @ `c7741b2` (#49 merged), upstream `exp` still `8971999`**, fetched by URL into `refs/upstream/exp`, no remote added)

| # | Fact | Command → observation |
|---|---|---|
| V1 | The upstream merge base and what upstream has beyond it | `git merge-base agentic/exp-review refs/upstream/exp` → **`9aaaefa`** (upstream `exp` as merged into the fork's stage branch on 2026-08-31, `f5bd6d2`); upstream `exp` is **2 commits** past it: `fa5fb4f` #215 "fixing bug with direct beam ROI and detector arrays", `8971999` #216 "fixing autoreduction error in plotly-js" |
| V2 | The fork's history to layer | `git log --first-parent 9aaaefa..agentic/exp-review` → **46 entries**: 27 merges (one per fork PR or per September staged branch; never squashed), 19 direct commits (the August harness work, #15/#19 fast-forwarded in; `0d3c73b`, `633950c`, `4e5f669`, `7b6d6b9`, `62e21d1`; four campaign `todo.md` commits) |
| V3 | Lane purity per entry — **amended at build (D-93/A-130):** nine files of R were in no set: `.github/workflows/test_and_deploy.yml` (excluded), `docs/developer/developer.rst` (#20 → L1), and seven core `src/` files #49 touched with comment-only hunks (→ L1, the default owner of core files); `launcher/tests/__init__.py` (#15) was L3-only (→ L1). Now `scripts/landing-purity.sh --complete 8971999 <R>` → 88 owned + 4 excluded = every path (files by area: `launcher/`, the three model modules, `src/lr_reduction/` upstream-existing, `src/`-new, `tests/`, config) | pure-launcher: #16, #17, #18, #33, #35–#40, #43, #45, #47, `4e5f669`, `62e21d1`; pure-reduction: #34, #46; pure-core/harness: #15, #19, #20, #21, #23, #24, #26, #27, #41, `0d3c73b`, `633950c`; **mixed:** `2127343` (#14: 8 launcher + 6 src + cfg — a mechanical ruff baseline), `a4efd95` (#28: launcher 2, model 2, **`nr_reduction_calc.py`, `nr_tools.py`, `reduction_domains.py`** — the choice lists moved to a shared module and two call sites switched), `34dc1b9` (#48: launcher 3, src 6 + 2 new, tests 6 — the time-resolved tab beside the reduction), `bb98bf3` (#30: src 2, cfg 1, one campaign document), `e7b8524` (#44: model 1 + `scripts/test/` battery 2) |
| V4 | PR ↔ entry map | `gh pr list --state merged`: #33–#48 merge at the entries named above; #14 `2127343`, #15 `a4ae8b8`, #19 `05c964f`, #20 `11170ff`, #21 `633950c`, #23 `04c6e53` are on the first-parent line; **#16, #17, #18, #24, #25, #26, #27, #28, #30** were merged into the fork's `exp` (Sep 2–22) and reached `exp-review` through the human's staged `origin/exp-*` branch merges (`246a0da`, `3810314`, `3e0fda5`, `376a616`, `d501caf`→`.github`, `d0599f9`, `508f70d`, `a4efd95`, `bb98bf3`) — the replay unit for them is the staged-branch merge entry, not the PR |
| V5 | #42 is inside #48 | `61fb6eb` (#42's merge) is not on the first-parent line: #42's branch was merged into `feature/time-slicing-reconcile` (V1-47, I-84); its files (`new_launcher.py`'s `MPLCONFIGDIR`, `launcher/tests/test_runtime_env.py`) arrive with `34dc1b9` — L3 |
| V6 | What "sanitized" excludes (**the `scripts/test/` half amended by D-3, A-136**) | `git diff refs/upstream/exp agentic/exp-review -- .github/` → one file, `.github/workflows/test_and_deploy.yml` +34/−3: the "Ensure release tags exist" fetch from upstream (#25, fork-only), two "Check pixi.lock format" steps and the `pixi-version: v0.67.2` pin (#20) — the change `todo-upstream-exp-review-carries-fork-ci-config.md` records the human's intent to keep out of upstream (D-2). Other non-code differences: `scripts/check_lock_format.sh`, `scripts/pixi_lock_check.sh` (#20, hooks the fork's pre-commit runs — kept, D-2), `scripts/test/{README.md, measure_fit_path_dependence.py, roi_estimate_mutations.py}` (campaign batteries, D-3), `pyproject.toml` ±32, `pixi.lock` ±27 |
| V7 | Nothing in the reduction imports the model modules | `git grep -l "settings_document\|field_spec\|roi_estimate" src/` at `62e21d1` → empty; importers: `launcher/apps/settings_editor.py`, `launcher/apps/roi_dialog.py`, tests (V1-57, re-run) |
| V8 | `reduction_domains.py` is the one campaign-new module the reduction imports | `nr_reduction_calc.py` and `nr_tools.py` take their choice lists from it (#28); it must sit in L1 or L2 for L3's editor to import it — L1 (the core layer, V1-57's "minimal core cut") |
| V9 | The stale fork `exp` | the fork's `exp` branch stopped at #30 (2026-09-22) and is not the base of anything here; L1's base is upstream's tip, mirrored (§3 R0) |
| V10 | The September stack is already in front of the scientists | upstream open PRs #181 → #188–#193 → #196 → #198 (+#202) carry the pre-October layers chronologically (V1-57); L1/L3 supersede or re-base them — the human's call (D-6) |
| V11 | The base-branch test failure — **closed** | `test_the_launcher_carries_the_tab_after_the_others` failed at `62e21d1` (I-85); the human's direct commit `1bffee1` (2026-10-19 19:23 EDT) fixes the expectation — 798 passed, 3 skipped (I-93). R built from `exp-review` at or after `1bffee1` carries it, so L3's faithful replay passes its gate; K5 is superseded (D-5) |
| V12 | #49 straddles the lanes — **merged 2026-10-20 01:56Z** (`c7741b2`, tree `cfe18ef` as I-93 predicted) | `feature/noqa-sweep` @ `4eec8d5` changes 19 files across launcher, src, `src/lr_autoreduce`, tests, `.pre-commit-config.yaml` and adds `tests/test_noqa_tags.py` (A-118's census); **split by file** (D-4, the Developer's reading, A-130): each hunk goes with the last commit of the layer that owns its file — L1 took `.pre-commit-config.yaml`, `launcher/tests/test_harness.py`, `tests/test_noqa_tags.py` and the seven core `src/` files (D-93/D-94); L2 and L3 take theirs. No purity exception needed |

## 3. Design

**R0 — the reference, first.** (i) **The human**, before dispatch: fast-forward the fork's `exp` branch to upstream's tip (`git push <fork> <upstream-sha>:refs/heads/exp`
— a non-protocol branch the human owns, one command, as `exp-review` was synced; the plan names the SHA at re-seal). No mirrored campaign ref is needed
and none is pushed by a seat. (ii) **The Developer**, L1's first act: produce **R** = `git merge` of `exp-review`'s tip (**`c7741b2`**, #49 merged) into that base on
`feature/landing-reference`, resolving the #215/#216 ↔ #48 hunks in `direct_beam_maker.py` / `example_direct_beam.py` with a justified commit body, and push
that branch — a `feature/*` ref, **inside the Developer's §8.1 manifest** (`todo-landing-reference-ref-outside-developer-manifest.md`, D-90: v1's `landing/*`
refs would have needed a human grant; retired). `feature/landing-reference` is immutable by convention: never moved or deleted by a seat; a re-derivation
(upstream `exp` moving before L3's gate) is a new branch `feature/landing-reference-2`, named in the plan's revision history — never a silent update. R is
what the human's own merge of `exp-review` into `exp` will be; every proof compares trees against R.

**R1 — the replay unit and granularity (D-1, default (a)).** Each first-parent entry of V2 that belongs to a layer is replayed as **one commit per
entry**, whose content is the entry's merge diff (`git diff M^1 M`, split by file where an entry spans layers — V3's mixed rows) applied with
`git apply --3way` onto the layer's tip, and whose message is the PR's title and number, the fork merge SHA, and the **union of the original commits'
`Co-Authored-By:` trailers plus the human authors** (`git log --format=%an%n%b M^1..M^2 | grep -i co-authored` → de-duplicated). The alternative (b)
— cherry-picking every non-merge commit (~500, with their forward-merge conflict resolutions re-fought) — is offered in §10 and taken only where the
human names a layer whose RED/GREEN history must survive upstream. (a) is deterministic, keeps authorship, and makes the empty-diff proof the only
correctness question; the fork keeps the archaeological record either way.

**R2 — the four layers** (membership in the Declared scopes; order inside a layer = the fork's chronological order, so later entries' hunks apply onto
earlier ones as they did). Mixed entries are split by file: `2127343` (#14) is replayed whole in L1 as a mechanical baseline (the one purity exception,
stated in L1's PR body); `a4efd95` (#28) → `reduction_domains.py` + the two call-site hunks in L1, the editor in L3; `34dc1b9` (#48) → `src/` + `tests/`
in L2, `launcher/` in L3; `bb98bf3` (#30) → `src/` + tests in L2, the campaign document dropped; `e7b8524` (#44) → model + tests in L3, `scripts/test/`
per D-3. Entries that only carry campaign artefacts (`todo.md`, `7b6d6b9`'s artefact removal, `dc84af7`) are not replayed; the upstream merge
`f5bd6d2` is not replayed (its first-parent diff *is* upstream's content).

**R3 — sanitization rules** (checked by `scripts/landing-sanitize-check.sh`, §6 P2, run at every layer's gate). **The exclusion list, one source**
(`EXCL` in `scripts/landing-purity.sh`, read by `landing-proof.sh`; change it here, there and in D-2/D-3 together): `.github/workflows/test_and_deploy.yml`
(D-2) and `scripts/test/measure_fit_path_dependence.py` (D-3 as amended). No change under `.github/`; no `todo.md`, `plans/`, `*-learning*.md`, battery logs; no `Claude-Session`/URL trailers (the commit rule); no protocol refs pushed except the two
campaign refs of R0; `pixi.lock` only as the replayed PRs left it (the Developer runs `pixi install --locked` + `scripts/pixi_lock_check.sh` in a
clean worktree before every `qa/`, D-83's checklist); commit messages name the fork PR they replay.

**R4 — the per-layer gate** (the Integrator, unchanged mechanics): `pixi run test-reduction` from the layer's tip (L1: the harness self-tests and
upstream's launcher apps; L2: + the reduction tests, byte-identity vs R on the harness scenarios; L3: the full suite; L4: the full suite after the move),
plus P1 (purity) and P2 (sanitization) green, plus the **proof** at L3 (`git diff --stat feature/landing-l3-launcher feature/landing-reference` → empty)
and at L4 (the diff is exactly the move). A gate rejection is a `review/<leaf>` work order as usual; the retry cap is per leaf.

**R5 — the PRs.** Draft PRs on the fork: L1 `--base exp` (the fork's `exp` at upstream's tip, R0 i), L2 `--base feature/landing-l1-core`,
L3 `--base feature/landing-l2-reduction`, L4 `--base feature/landing-l3-launcher`; each body lists the replayed fork PRs (number → new commit), the
split and excluded items, the proof output, and the deploy consequence (none: nothing deploys from these branches; the human carries them to upstream
`exp`, then `exp-qa`/`exp-next` per the new deployment scheme).

**Types and states the replay acts on** (amendment 18): a first-parent entry is one of {merge with one PR behind it, merge of a staged branch holding
several PRs, fast-forwarded PR (commits on the line), direct human commit, upstream merge, artefact-only commit}; a hunk is one of {pure to a layer,
mixed (split by file), conflicting with #215/#216 (resolved as in R), conflicting with a later layer's earlier replay (impossible by construction —
layers are ordered as the fork was; a file's hunks stay in chronological order within its layer)}. §5 enumerates the failures of each.

## 4. Files to change

| Leaf | Files |
|---|---|
| L1 | the harness/config set, the six core files, `reduction_domains.py` + two call-site hunks, #14's baseline (Declared scope) |
| L2 | the reduction set + `tests/unit/lr_reduction/*`, `tests/test_time_resolved.py` |
| L3 | `launcher/**`, the three model modules (in place), `scripts/test/*` per D-3 |
| L4 | the three modules → `launcher/model/` (D-7), two import sites, their tests |
| ledger | `plans/stratified-landing-plan.md` (this), `scripts/landing-purity.sh` (P1, P4 `--census`, P5 `--complete`), `scripts/landing-sanitize-check.sh` (P2), `scripts/landing-proof.sh` (P3), `scripts/landing-replay.sh` (R1's one-commit-per-entry helper, the Developer's, D-94) — the checks the gate runs, in the repo, not in a session |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | a pure-lane PR replayed onto its layer | one commit, `git apply --3way` clean, authorship carried; P1/P2 green |
| common | the L3 tip vs R | `scripts/landing-proof.sh <L3> <R>`: (a) `git diff --stat` **outside the exclusion list** empty, and (b) the name-only diff **exactly** the excluded paths present in R — the exclusion proven, not assumed (D-93 proposal 2); a non-empty (a) names the entry whose hunk is missing or doubled (the Developer bisects by replaying entries one at a time with a running `diff --stat` against R restricted to the entry's files) |
| common | L2's outputs vs R's on the harness scenarios | byte-identical (the reduction's history changed, its code did not) |
| edge | a mixed entry (#14, #28, #30, #44, #48) | split by file into the owning layers; the sum of the splits equals the entry's diff (P1 asserts no file of the entry is unassigned) |
| edge | #28's call-site hunks in L1 before the editor exists | L1 imports `reduction_domains`; the editor arrives in L3 — L1/L2 gates must pass without it (V7: nothing in `src/` imports the model modules) |
| edge | #215/#216 conflict with #48 in `direct_beam_maker.py` | resolved once in R (R0, justified); L2 replays #48's hunk and resolves identically — the proof catches any divergence |
| edge | upstream `exp` moves during the build | R re-derived as a new immutable ref, the plan's revision history names it; layers already gated are re-gated only if the moved files intersect theirs |
| edge | #49 merged before dispatch (D-4) | its per-file hunks are appended to the owning layers' last entries (L1/L2/L3), the proof unchanged (R contains #49) |
| edge | #49 closed instead (D-4) | nothing to replay; R excludes it; the fork's `exp-review` keeps the open PR until the human closes it |
| edge | R built from an `exp-review` older than `1bffee1` (D-5) | L3's faithful replay would fail `test_the_launcher_carries_the_tab_after_the_others` at its gate — R0 ii takes the tip at dispatch, which carries the human's fix |
| edge | the fork's `exp` branch (stale at #30) | never used; L1's base is upstream's tip mirrored (V9) |
| pathological | an entry whose merge diff applies cleanly but reorders hunks across files that a later entry expects | the per-entry running proof (common case 2) localizes it; chronological order within a layer prevents it by construction |
| pathological | a trailer with a session URL in some original commit | P2 reds; the replayed message is rewritten without it (the rule) |
| pathological | the fork's `exp` is not synced when L1 reaches its draft PR | R0 i is needed by the **PR step only** (the Developer cuts from the SHA fetched by URL; the gate needs no branch): the Integrator records the PASS on the ledger and opens the PR once `git ls-remote agentic refs/heads/exp` = upstream's tip — the human's one command; nothing else waits (amended at dispatch, A-128: v1's "checked before the triage is cut" would have blocked the human's own word on the human) |
| pathological | the human merges a layer PR on the fork (they are drafts; merges are the human's) | nothing changes: the layers target each other, not `exp-review`; §5a (the Integrator) checks the merged tree as usual |

## 6. Red-Green TDD seed (a landing slug's "tests" are its proofs and checks; each is a committed script)

| # | Check | RED at the start |
|---|---|---|
| P1 | `scripts/landing-purity.sh <leaf> <base> <tip>`: every file in `git diff --name-only base..tip` belongs to the leaf's declared set (L1's exceptions listed in the script); exit 1 naming the stray file otherwise | fails on an empty layer? No — passes vacuously; **RED form:** run on `exp-review` itself as "L3" → fails on `src/` files (the mixed history), which is the condition the layers remove |
| P2 | `scripts/landing-sanitize-check.sh <base> <tip>`: no `.github/` change, no artefact paths, no URL trailers, every commit subject names a fork PR or "upstream base merge"; exit 1 with the offender | fails on `exp-review` (the `.github` change, the `todo.md` commits) |
| P3 | `scripts/landing-proof.sh <L3 tip> <R>` → (a) no difference outside the exclusion list and (b) the name-only diff is exactly the excluded paths; `--move <L4 tip> <R>` → only the moved modules, their importers and tests differ (renames shown) | fails on `exp-review` vs R (the #215/#216 hunks) and until L3 is complete (any missing entry shows); since A-136 (b) is strict — the green shape is a tip that lacks exactly the reference's excluded set, so R vs R fails (b) by design |
| P5 | `scripts/landing-purity.sh --complete <base> <R>`: every path of `git diff --name-only base R` is owned by some layer's set or is on the exclusion list (the union test of D-93, committed) | before A-130: 9 UNOWNED; after: 88 owned + 4 excluded |
| P4 | per-entry coverage: every first-parent entry of V2 is either replayed into exactly one layer (or split across named layers) or listed as excluded with a reason — a table in the L1 PR body, generated by `scripts/landing-purity.sh --census` | the table has unassigned rows before the plan's membership is applied |
| G | each layer's gate command green (R4); L2's harness byte-identity; L1's `test-launcher` green without the editor | — |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| an entry dropped from its layer | P3 (the proof), P4 (coverage) |
| an entry replayed twice (once per layer) | P3 (doubled hunks), P1 (a file outside the second layer's set) |
| #48's launcher half left in L2 | P1 (L2) |
| `reduction_domains.py` put in L3 | L1/L2's gate (import error in `nr_reduction_calc.py`) |
| the `.github` change replayed | P2 |
| a replayed commit message without the fork PR number | P2 |
| a trailer dropped from a replayed commit | P2's authorship leg (every original `Co-Authored-By` present) |
| R re-derived silently (a different conflict resolution) | P3 at L2's byte-identity and at L3 |
| L4's move done with delete+add instead of `git mv` | P3's `--find-renames` leg (no rename detected → the diff is not "exactly the move") |

**Frame:** two scripts (P1, P2), one proof command (P3), one coverage table (P4); no decorators or sentinels; the Integrator's gate adds nothing
new mechanically.

## 8. Acceptance criteria

1. **Per leaf:** the gate command green at the `qa/` tip; P1, P2 green; L2: the Integrator's baseline from R and `compare_columns.sh` /
   `check_headers.py` identical on the standard scenarios; L3: P3 empty; L4: P3's rename-only diff.
2. **Developer:** R0's merge justified in its commit body; one commit per replayed entry with the message shape of R1; the split of each mixed
   entry stated in the layer's first commit; `pixi install --locked` + `pixi_lock_check.sh` in a clean worktree before each `qa/`; the running
   per-entry proof recorded (the sequence of `diff --stat` sizes shrinking to 0 for L3) in the PR body.
3. **Integrator:** the gate per layer; P1/P2/P3 re-run independently (not trusted from the Developer's body); §5a on nothing (no merge into
   `exp-review` happens here).
4. **Claims:** "sanitized" is P2's output, quoted; "green on its own" is the gate's exit code per layer, quoted; "tree-identical" is P3's empty
   output, quoted.
5. **PRs:** four drafts on the fork, stacked (R5), bodies carrying the replay table (P4), the split/excluded list, the proof, the deploy
   consequence (none), and — for the human — the suggested upstream order (L1 → L2 → L3 → L4) and what supersedes upstream's open #181–#202 (D-6).

## 9. Learnings relied on

- `time-slicing-reconcile` (the intake procedure): an immutable campaign ref for an external input (`contrib/…@sha`); conflicts resolved with a
  justification in the commit body; the gate re-run independently.
- `plans/stacking-by-file-overlap-proposal.md`: lanes E and M were kept file-disjoint by the rule, which is why by-area layers cost little; the
  only shared touches are `reduction_domains` (#28) and #49.
- `git-history-preserving-refactors` (CPKT): `git mv` in its own commit before editing; verify with `--find-renames`.
- The Integrator's §5a practice (I-79…I-86): tree identity by `merge-tree`/`diff --stat`, predicted before and checked after.
- `todo-upstream-exp-review-carries-fork-ci-config.md`: the CI change is the human's named exclusion.
- A-118/M-72's finding, applied: a proof that lives in a session is lost; P1–P4 are repository scripts.

## 10. Assumptions and decisions (defaults in force unless the human says otherwise before dispatch)

- **D-1 — replay granularity:** (a) one commit per fork PR/entry with aggregated trailers (default); (b) full commit replay for a named layer
  (the human's). (b) costs an order of magnitude more conflict work and makes the proof harder to localize.
- **D-2 — `.github/`:** excluded entirely (the human's recorded intent). If the `pixi-version` pin or the lock-format check is wanted upstream, the
  human names it and L1 carries that hunk alone. `scripts/check_lock_format.sh` and `scripts/pixi_lock_check.sh` (pre-commit hooks) are kept
  (they are repository tooling, not CI).
- **D-3 — `scripts/test/*` batteries (#44, #49): amended 2026-10-20 (A-136, on D-100's measurement).** The premise "no consumer" was false for
  `roi_estimate_mutations.py`: three tests of #44 run it, so it is part of the tested tree and **L3 carries it with its README** (entry 13 whole).
  `measure_fit_path_dependence.py` (#49; one comment names it, nothing runs it) stays **excluded**. The three places changed together: `EXCL` in
  `landing-purity.sh`, the artefact rule in `landing-sanitize-check.sh`, L3's allow set. The human may reverse this (option B of the decision request:
  drop the three tests — a scope word, a v2 of L3).
- **D-4 — #49: merged 2026-10-20 (`c7741b2`), split by file.** Each of its hunks goes with the last commit of the layer that owns the file (the Developer's
  reading of the earlier D-4 text, D-93; accepted at A-130 over the re-seal's "whole in L3" — a one-line-tag hunk in a core file belongs with that file, and
  the completeness check now guarantees every file has an owner). L1 carried its hunks as the twelfth commit; L2 and L3 carry theirs.
- **D-5 — K5 before L3: satisfied 2026-10-19.** The human's direct commit `1bffee1` fixed the I-85 expectation (I-93: 798 passed); K5 is superseded and
  R (built from the tip at dispatch) carries the fix. No layer waits for anything here.
- **D-6 — upstream's open September PRs (#181–#202):** superseded by L1/L3 or re-based — the human's upstream coordination; the L1/L3 PR bodies
  name the overlap so the human can close or retarget.
- **D-7 — L4's target:** `launcher/model/` (a new package with `__init__.py`); alternatives `launcher/settings/` or flat `launcher/`. Named in the
  Developer's move commit; nothing else depends on the name.
- **D-8 — ref spelling: retired (A-127).** v1 named two campaign refs in two spellings (D-90's finding); there are none now — the base is the fork's
  `exp` (the human's branch), the reference is `feature/landing-reference` (the Developer's manifest). The snapshot convention `contrib/…@sha` stays for
  contributions, pushed by the Analyst under a posture grant as before.
- **D-9 — the deploy half:** `exp-qa`/`exp-next` and `nr_launcher.sh`'s `--exp-review` retirement are a separate slug against those names once the
  human's deployment scheme exists; this plan deploys nothing.
- **Re-seal at dispatch:** V1 (upstream `exp`'s tip), V2's count, V3's purity map, V6's exclusions, V12 (#49's state), V11 (K5's state).

## Revision history

v1 — authored 2026-10-19 (A-126) on the human's charter word of 2026-10-19 (V1-58, verbatim in charter §3); **staged, not dispatched** (trigger: #49
merged or closed; K5 before L3). Built from a census of the fork's 46 first-parent entries since the upstream merge base `9aaaefa` (V2–V5), V1-57's
layer shape, and the recorded sanitization exclusions (V6). The reference R and the two campaign refs (R0), the one-commit-per-entry replay with
aggregated trailers (R1, D-1), the per-file splits of the five mixed entries (R2), and the four repository-held checks (P1–P4) are this plan's
additions.

v1 revised 2026-10-19 (A-127), still staged: (1) `exp-review` moved to `1bffee1` — the human's own fix of the I-85 test (I-93) — so K5 is superseded and D-5 is
satisfied; V11, the L3 entry list and the reference tip updated. (2) D-90 (`todo-landing-reference-ref-outside-developer-manifest.md`): v1 had the Developer push a
`landing/*` ref outside its manifest and spelled the refs two ways — both retired: the base is the fork's `exp`, fast-forwarded to upstream's tip by the human
before dispatch (R0 i), and R is `feature/landing-reference`, pushed by the Developer inside its manifest (R0 ii); no new grant, one spelling. I-92's readiness
(upstream `exp`'s lock is v6; pixi 0.60.0 builds every layer) noted. The membership, the replay method and the checks are unchanged.

v1 re-sealed and **L1 dispatched 2026-10-20 (A-128)**: #49 merged (`c7741b2`, tree `cfe18ef`, I-94) — the trigger; upstream `exp` unmoved at `8971999`;
R's input is `c7741b2`; #49 replayed whole as L3's last entry (D-4 resolved, V12); R0 i (the fork's `exp` sync, the human's) moved from a pre-cut check to a
PR-step precondition so the human's word is not blocked on the human; `scripts/landing-purity.sh` and `scripts/landing-sanitize-check.sh` committed on the
ledger (P1, P2, P4); the leaf work order is `plans/landing-l1-core-plan.md`. L2–L4 leaf plans are written at their dispatch from the same census.

v1 amended at L1's build 2026-10-20 (A-130; `todo-landing-layer-sets-miss-files-and-proof-ignores-exclusions.md`, D-93, I-95): nine files of R were in no
layer's set and P3 could not be empty while R carries the exclusions. The L1 set now owns the core files no later layer lists (and `docs/`, `launcher/tests/__init__.py`,
`src/lr_autoreduce/`); `scripts/landing-purity.sh --complete` (P5) proves every path of R owned or excluded (88 + 4); P3 is `scripts/landing-proof.sh`, exclusion-scoped
and proven; the exclusion list has one source; D-4 is the per-file split the Developer applied; the L3 purity exception for #49 is retired. Membership otherwise unchanged.

v1 amended 2026-10-20 (A-136) at L3's build: D-3 narrowed on D-100's measurement (the suite runs #44's battery) — see the L3 leaf plan's revision; P3 (b) made strict
(the diff must equal the reference's excluded set); the exclusion list is two paths.

v1 amended 2026-10-20 (A-155), after the four gates — **upstream `exp` moved and L1 was base-merged**: (1) upstream `exp` advanced `8971999` → `c4d20e4` (the human's merge of
welbournR's three commits: the RB fit's pixel range padded after the DB pixel and clamped, `alpha` by `arctan` instead of `arcsin`, the expected profile centred at
`DBpixel − calc_pixel_diff`; `settings.json` gains a time-indexed entry; I-114: `merge-tree` clean for L1–L4 and K10, the only overlap `nr_reduction_calc.py` with disjoint hunks).
(2) The human merged it into L1: `feature/landing-l1-core` `c5ef58d` → **`7f0a4ad`** (I-115: the tree is git's own merge `47280df`, no content of its own; P1 clean over the new
base `c4d20e4..7f0a4ad` with the declared #14 exception; P2 clean — merges skipped, every non-merge commit with provenance; G 10 + 172 rc 0; #54 and #55 `MERGEABLE`/clean,
#51 `MERGEABLE`). **The base facts of §2 now read with `c4d20e4` as L1's base** for everything measured after this line; the layers' gated tips (`c5ef58d`, `3ea92cf`, `941be51`,
`82b0854`) and their proofs against R @ `da2b889` stand as the record of the gates. (3) **R is re-derived, not updated** (this plan's rule, §3 R0): the reference for the
merged stack is a new branch **`feature/landing-reference-2`** = `exp-review` @ `c7741b2` merged onto `c4d20e4` by the D-92 recipe (the same #215/#216 ↔ #48 resolution, plus
upstream's new `nr_reduction_calc.py` hunks, which are disjoint from the fork's), pushed by the Developer inside its manifest **on the human's word**, when the human base-merges
L2 (I-114/I-115: L2's harness byte-identity must then be measured against R-2, never against R — reductions differ by design, `arctan`). P3 at the stack tip and P5 are re-run
against R-2; P1 over `c4d20e4..<tip>`; P2 as before. Until that word nothing moves: L2–L4 stay at their gated tips and their stacked PRs stay valid (#51 → L1's new tip merges
cleanly, I-115). (4) Upstream `exp-landing-l1-core` is still `c5ef58d`; if the human pushes `7f0a4ad` there, #219 carries the measured tree. The fork's `exp` is still `8971999`
(#54's diff therefore shows upstream's four commits until the human moves it).

v1 amended 2026-10-21 (A-157), K11 `landing-l1-legacy-freeze` dispatched on the human's word: the exclusion list (`EXCL` in `scripts/landing-purity.sh`, read by `landing-proof.sh`) gains the **frozen set** — the 12 legacy-reduction files the scientist named on #219 (byte-equal to upstream on L1′), `tests/test_warning_hygiene.py`, `tests/unit/lr_reduction/test_output.py`, and `pyproject.toml` (its only permitted difference the ruff `extend-exclude` block); P3 (b) stays strict against the enlarged set. `scripts/landing-sanitize-check.sh` accepts `Reverts:` and `stack merge:` provenance. **R-2** (`feature/landing-reference-2`, A-155's rule) is built in K11's Phase 2 by the Developer, and L2′, L3′, L4′ (and K10′) merge the previous gated tip forward and are re-gated — L2′'s harness against R-2, L4′'s P3 against R-2. The record copy on `analysis/exp-review-fixes` follows at the next analysis push.
