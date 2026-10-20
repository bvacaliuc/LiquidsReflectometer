# Plan: `landing-l4-model-move` — layer 4 of `stratified-landing`: the three Qt-free model modules moved out of `src/lr_reduction/` under `launcher/model/`, their tests beside the launcher's, every importer re-pointed; the tree differs from the reference by exactly the move

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l4-model-move` (refs `triage/landing-l4-model-move`, `feature/landing-l4-model-move`, `qa/landing-l4-model-move`) ·
**Status:** READY — v1 (attempt 1 of N = 3) — **dispatched 2026-10-20 (A-139) on L3's Integrator PASS** (I-102: `landing-l3-launcher` v1 @ `941be51` PASS — the
stack equals R except the two excluded files, census 0 UNASSIGNED, G 801 + 1101; draft PR #52 on L2); the three tool adjustments of §Tools applied on the ledger at
this dispatch for the Integrator's re-validation; authored staged 2026-10-20 (A-137). The group plan is
**`plans/stratified-landing-plan.md`**; this file is the leaf's work order ·
**Base:** `agentic/feature/landing-l3-launcher` @ **`941be51`** (the PASS tip, I-102; re-sealed at dispatch: unmoved since `qa/`) — cut: `git checkout -B feature/landing-l4-model-move --no-track agentic/feature/landing-l3-launcher` ·
**Overlap at dispatch:** the stack only · **PR target:** `feature/landing-l3-launcher` on the fork, **draft** (stacked) · **Depends on:** L3's PASS; R =
`feature/landing-reference` @ `da2b889` · **Review domains:** design, test (block); ui-aspects (advise) · **Kind:** launcher packaging — not reduction-path
(V7: nothing in the reduction imports the moved modules; `reduction_domains.py` stays in `src/lr_reduction/`).

Campaign: exp-review-fixes

## Declared scope

**Files in.** `src/lr_reduction/{settings_document, field_spec, roi_estimate}.py` → `launcher/model/{settings_document, field_spec, roi_estimate}.py`
(+ `launcher/model/__init__.py`, empty); `tests/unit/lr_reduction/{test_settings_document, test_roi_estimate}.py` → `launcher/tests/{test_settings_document,
test_roi_estimate}.py` (D-10); the importers: `launcher/apps/settings_editor.py` (3 import lines), `launcher/apps/roi_dialog.py` (1), `launcher/tests/test_settings_editor.py`
(2), `launcher/tests/test_roi_dialog.py` (2), the two moved test modules (3 + 1), `scripts/test/roi_estimate_mutations.py` and `scripts/test/README.md`
(their `lr_reduction.roi_estimate` references); the moved modules' own imports (`settings_document.py:44` `from lr_reduction import field_spec` →
`from launcher.model import field_spec`; `field_spec.py:38` keeps `lr_reduction.reduction_domains`; `roi_estimate.py:31` keeps `lr_reduction.nr_tools`;
`settings_document.py:45-47` keep their `lr_reduction` imports). **The site list the Integrator measured at `941be51` (I-102, for commit iii):**
`launcher/apps/roi_dialog.py:40`; `launcher/apps/settings_editor.py:43-45`; `launcher/tests/test_roi_dialog.py:19,20,579`; `launcher/tests/test_settings_editor.py:26,29,39,…,3563`
and **`:2962` (loads `test_roi_estimate.py` by path — follows D-10's move)**; `scripts/test/roi_estimate_mutations.py:6,37,38`; `tests/unit/lr_reduction/test_roi_estimate.py:582-624`
(`_battery_copy`) and **`:478` (a `parents[3]` anchor to the repository root — from `launcher/tests/` it is `parents[2]`)**; `tests/unit/lr_reduction/test_settings_document.py:341`
(the AST guard's path to the module). A site the Developer finds beyond this list is stated in commit iii's body; M3's `git grep` is the completeness check. `pyproject.toml` only if the `launcher` package line needs it (V: `packages = ["src/lr_reduction",
"src/lr_autoreduce", "launcher"]` already ships `launcher/**`; expected: no change).

**Behaviours in.** (1) **Three commits, in this order** (`git-history-preserving-refactors`: `git mv` in its own commit before any edit, so git sees renames):
(i) `git mv` the three modules + add `launcher/model/__init__.py` — content byte-identical (`git diff -M100% --stat` shows three 100% renames and one new empty file);
(ii) `git mv` the two test modules to `launcher/tests/` — 100% renames; (iii) the import edits (the list above) and nothing else. Each commit's body carries a
`Move: <what>` line (its provenance for P2, §Tools). (2) **The tree differs from R by exactly the move:** `scripts/landing-proof.sh --move <tip> da2b889` → only the
moved modules (old and new paths), the two moved tests, the seven importers and the battery/README differ; `git diff --name-status --find-renames` shows the five
renames. (3) `git grep -l "settings_document\|field_spec\|roi_estimate" src/` → empty before and after (V7); `git grep -n "lr_reduction\.\(settings_document\|field_spec\|roi_estimate\)\|from lr_reduction import \(field_spec\|roi_estimate\|settings_document\)"` → empty after. (4) The gate green: the full suite — the two moved test
modules now run under `test-launcher` (`launcher/tests/`, `--timeout=120`); `test-reduction` loses them (its count drops by exactly their test count, stated in
the PR body). (5) P1 (L4's set), P2, P4 (unchanged: 0 UNASSIGNED — L4 replays nothing) clean.

**Explicitly OUT.** Any content change inside the moved modules beyond the one import line in `settings_document.py`; `reduction_domains.py` (stays: the
reduction imports it); the `lr_reduction` imports the moved modules keep; any test logic change (a moved test that needs a fixture path fixed is an import/path
edit, stated in (iii)); `pyproject.toml` beyond packaging; the review tier and `nr_launcher.sh`.

## Decisions (defaults in force unless the human says otherwise before dispatch)
- **D-7 — the target package:** `launcher/model/` (group plan D-7). Alternatives (`launcher/settings/`, flat `launcher/`) change only the paths in this file.
- **D-10 — the two test modules move too** (compartmentalization: a launcher module's tests belong beside the launcher's; `test-launcher` runs them). Alternative:
  keep them under `tests/unit/lr_reduction/` with import edits only — then (4)'s count statement is moot and `test-reduction` keeps them.
- **D-11 — the battery** (`scripts/test/roi_estimate_mutations.py`, in L3 by A-136): its references follow the move (an edit in commit iii); its three tests move with
  `test_roi_estimate.py` and keep running it.

## Tools (applied at this leaf's dispatch — A-139, on the ledger with the reason — for the Integrator's re-validation, I-96's rule)
1. `scripts/landing-sanitize-check.sh`: the provenance rule accepts `^Move: ` beside `Replays:` / `reference:` / `upstream base merge` (L4's commits replay nothing).
2. `scripts/landing-proof.sh --move`: `MOVED` gains `^scripts/test/(roi_estimate_mutations\.py|README\.md)$` (the battery and README reference the module and change in
   commit iii) and `^launcher/model/__init__\.py$`.
3. `scripts/landing-purity.sh`: L4's set gains `scripts/test/(roi_estimate_mutations\.py|README\.md)` and the old module paths are deletions (a deleted file is listed
   by `diff-tree`; the set already allows `src/lr_reduction/(settings_document|field_spec|roi_estimate)\.py` via `$MODEL`).

## Red-Green seed (the checks)

| # | Check | RED at the start |
|---|---|---|
| M1 | commit (i): `git diff -M100% --name-status <base> <i>` → `R100` ×3 + `A launcher/model/__init__.py`; no `M` | — |
| M2 | commit (ii): `R100` ×2 | — |
| M3 | after (iii): `git grep` for the old import forms → empty; `python -c 'import launcher.model.settings_document, launcher.model.field_spec, launcher.model.roi_estimate'` in the env → ok | the old forms present; imports fail |
| P3 | `scripts/landing-proof.sh --move <tip> da2b889` → only the move's files differ; renames shown | fails at the base (nothing moved) and after (i)/(ii) (imports still point at `lr_reduction`) — no: (a) passes once only moved files differ; the gate is M3 + G |
| P1/P2/P4 | clean; P4 0 UNASSIGNED | — |
| G | `pixi run test-reduction` green; the launcher suite's count grows by the two moved modules' tests, the reduction suite's drops by the same; `pixi install --locked` + `scripts/pixi_lock_check.sh` exit 0 in a clean worktree | — |
| V7 | `git grep -l "settings_document\|field_spec\|roi_estimate" src/` → empty | — |

## Mutate-once gate

| Mutation | Must red |
|---|---|
| ~~the move done as delete + add (no `git mv`)~~ — **unfalsifiable (I-103):** git records no rename; a delete+add commit's tree is byte-identical to commit i's, so `--find-renames` reports `R100` either way. Dropped; the renames are a property of the diff, not of how the commit was made | — |
| `settings_document.py:44` left as `from lr_reduction import field_spec` | M3 (`git grep`), G (ImportError at import time once `lr_reduction.field_spec` is gone) |
| the battery's reference left at `lr_reduction.roi_estimate` | G (the three battery tests red: the mutated module path does not exist) |
| a content edit smuggled into commit (i) | M1 (an `M` or a `R<100`) |
| `reduction_domains.py` moved too | V7's inverse: `nr_reduction_calc.py` imports fail — G red at import |
| a commit without `Move:` | P2 NO-PROVENANCE |

## Acceptance criteria
1. Three commits as (i)–(iii); `Move:` lines; the renames at 100 %.
2. M1–M3, P1, P2, P4, V7 clean; P3 `--move` lists exactly the move's files; G green with the counts stated.
3. The `qa/landing-l4-model-move` tag at the tip; the mutation evidence on the ledger.
4. The Integrator re-validates the three tool changes (§Tools) before the gate, re-runs the checks from the ledger, and opens the draft PR `--base feature/landing-l3-launcher`
   naming the whole stack (L1 → L2 → L3 → this); the body shows `git diff --stat --find-renames <tip> da2b889` as the proof that the stack is R plus the move.
5. The PR body: the three commits, the import table, D-7/D-10/D-11 as taken, the suggested upstream order (L4 of four — last, so the scientists can take L1–L3 without it).

## Revision history
v1 — authored 2026-10-20 (A-137), **staged**, dispatching on L3's PASS with the base re-sealed and the three tool adjustments applied then (not now: L3's gate runs
against the tools as pinned in I-101). Inputs: V7 and the importer census at `c7741b2` (`git grep`), the modules' own imports, `pyproject.toml`'s package line.

v1 dispatched 2026-10-20 (A-139) on I-102 (L3 PASS @ `941be51`); base re-sealed at that SHA; the three tool adjustments applied with the dispatch commit.

v1 gated 2026-10-20 (I-103 PASS @ `82b0854`, draft PR #53); the "delete + add" mutation row struck as unfalsifiable at the Integrator's advisory (A-140). The record copy on
`analysis/exp-review-fixes` follows at the next analysis push.
