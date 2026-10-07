# Plan: `noqa-sweep` — every `noqa` tag classified; dead ones removed; mislabelled blankets made precise; masked defects routed

**Campaign:** `exp-review-fixes` · **Leaf:** `noqa-sweep` (refs `triage/noqa-sweep`, `feature/noqa-sweep`, `qa/noqa-sweep`) ·
**Status:** READY — **v2 (attempt 2 of N = 3)** — v1 REJECTED 2026-10-07 at `3275fc4` (I-67; the record is `plans/noqa-sweep-v1-rejection.md` **on the ledger** — the fork's `pixi-lock-check` pre-push guard refused the Integrator's rejection commit `53f9728`, so there is no `review/` tag and `qa/noqa-sweep` @ `3275fc4` stands unconsumed; **one block, B-1:** the committed `pixi.lock` is stale against `pyproject.toml` once `RUF100` is added to `select` — `pyproject.toml` is also the pixi self-package manifest; everything else passed — comments-only by tokenize on 17 files, same(masked) vs #48 in all 8 scenarios, 50 tags classified, battery 17 rows red, security and design PASS) — **v2 = N5 restated as N5′: `RUF100` is enabled where ruff runs in this repository (the pre-commit `ruff-check` hook's `args` and U2's call); `pyproject.toml` is NOT edited; the lock is untouched; plus D-2's one-sentence correction in the findings doc. No production line, no tag change.** The Developer continues on `feature/noqa-sweep` @ `3275fc4` — v1 was **DISPATCHED 2026-10-07 (A-111)** on the posture's trigger (take line (3): `time-slicing-reconcile`'s draft PR open — I-66, PR #48); the original triggers (`editor-sections` #40 and `test-suite-warnings` #41 merged) also met; **re-sealed at dispatch** — see "Re-seal at dispatch" below (the ruff measurements F2/F3 are the Developer's first act, per §2's "re-run at dispatch") ·
**Base (clause (4)):** **`agentic/feature/time-slicing-reconcile` @ `4e5987a`** — the reduction stack's tip (#34 → #46 → #48; it contains #42 merged forward) — **with `agentic/feature/roi-popout-dialog` @ `18059cc` merged forward at cut** (the editor/ROI stack's tip: #43 → #45 → #47 on #44; the trial merge of the two tips is **conflict-free**, measured 2026-10-07) and before every `qa/` push; every open feature branch is thereby in the sweep's tree — the sweep classifies the files the intake adds lines to (the human's reason). Overlap census at `exp-review` `c39efe9`: the sweep's tag-bearing files ∩ the reduction stack {`binary_processing.py`, `nr_reduction_calc.py`, `save_reduced_data.py`, `direct_beam_maker.py`, `time_resolved.py` (new)} ∩ the editor/ROI stack {`settings_editor.py`, `roi_dialog.py` (new)} ∩ #42 ∅ · **PR target:** `feature/time-slicing-reconcile` on the fork, **draft** (the Integrator names the full stack and the merged-forward ROI stack; **clause (3a)** → `exp-review` if the base's tip is an ancestor of `exp-review` at open) ·
**Review domains:** design, security (block) · **Kind:** library + launcher, **not reduction-path** (no expression changes; a
tag's removal or re-spelling changes no behaviour — a defect found behind a tag is **not fixed here**, §3 N4) ·
**Sources:** `[human, 2026-10-04, PR #37 comment: "we should also do a sweep of existing 'NOQA' tags to see if those are still
needed or if they are masking an underlying defect in the code"]` via `requests/test-suite-warnings-and-noqa-sweep.md`; charter §3 row.

## Declared scope

**Files in:** the 17 files holding a `noqa` tag at `2324e5c` (F1's list — re-listed at dispatch), **`.pre-commit-config.yaml` (v2: the
`ruff-check` hook's `args` gain `--extend-select, RUF100`; v1's `pyproject.toml` `select` edit is withdrawn — I-67 B-1, that file is the pixi
self-package manifest and any edit to it stales `pixi.lock`)**, a new `plans/noqa-sweep-findings.md` **on the ledger** (the Developer writes it beside the learning file;
the PR body carries the table).

**Behaviours in** (N1–N5, §3). **Explicitly OUT:** fixing any defect a tag turns out to mask (each becomes a child leaf with
`Seed:` this findings doc — the termination rule's out-of-scope route); changing what a guarded `except` does; the ruff `ignore`
list and the `launcher/**` per-file ignore (their rationale stands; this slug reads them, it does not relitigate them); tags in
`.pixi`, docs, or notebooks.

## 1. Request

> In addition, we should also do a sweep of existing "NOQA" tags to see if those are still needed or if they are masking an
> underlying defect in the code. `[human, 2026-10-04, PR #37 comment]`

## 2. Verified facts at `2324e5c` (measured 2026-10-04; re-run at dispatch)

| # | Fact | Evidence |
|---|---|---|
| F1 | **37 tags in 17 files.** By declared rule: `BLE001` 14 (4 in `settings_editor.py`, 10 in `src/`), `E722` 7 (5 in `web_report.py`, 2 in the template readers), `ARG001` 4, `E402` 3 (`scripts/test/measure_fit_path_dependence.py`), `N801` 2, `E501` 2, `S307` 1, `N815` 1, `F841` 1, `ARG002` 1. | `grep -rn --include='*.py' -iE '#\s*noqa' src launcher tests scripts` (full `file:line rule` list in the courier's companion, reproduced in the findings doc). |
| F2 | **Ten tags are dead — ruff's own detector says so.** `ruff check --extend-select RUF100 --no-fix src launcher tests scripts` (ruff 0.15.11, the repo's selection kept) → 10 × `RUF100`: the four `BLE001` in `launcher/apps/settings_editor.py:428,728,952,976` (non-enabled there — `per-file-ignores "launcher/**" = ["BLE001"]`, `pyproject.toml:270`), `launcher/tests/test_harness.py:236` `S307` (never selected), `instrument_settings.py:31` `N815` (globally ignored, `:259`), the two `E722` in `reduction_template_reader.py:20` / `new_reduction_template_reader.py:36` (`E722` ignored, `:249`), and two **blanket** directives at `web_report.py:362,447`. | Run 2026-10-04. `RUF100` is not in the repo's `select` (`pyproject.toml:245`), so nothing fails today when a tag goes dead. |
| F3 | **Seven tags are mislabelled blankets, and five of them mask a live rule.** `# noqa E722` (no colon) is not a code-scoped directive: ruff reads it as a **blanket** `# noqa`. At `web_report.py:592,630,658,687,705` the line is `except Exception:  # noqa E722` — `E722` is globally ignored, but the blanket silences **`BLE001`** (blind except, enforced in `src/` — `pyproject.toml:267-269`: "the few blind excepts carry per-line noqa with the reason"), with **no reason given**. The two at `:362,447` (`# noqa E501`) are blankets on lines where nothing fires (F2). | `RUF100` reports the latter two as "Unused blanket `noqa` directive" and the former five as *used* — used by a rule they do not name. |
| F4 | The remaining **20 live, code-scoped tags** each silence a rule that would otherwise fire: `BLE001` ×10 in `src/` (`nr_reduction_calc.py:350`, `web_report.py:203,208,244`, `binary_processing.py:160`, `direct_beam_maker.py:192`, `gravity_correction.py:74`, `save_reduced_data.py:128`, `new_reduce_REF_L.py:217`, `reduce_REF_L.py:175`), `ARG001` ×4, `ARG002` ×1, `N801` ×2, `E402` ×3, `F841` ×1 (`test_settings_document.py:945`, a walrus whose target is intentionally unused). Whether each carries a **reason** on the line or nearby is part of the sweep (N2). | F1 − F2 − F3's five; re-derived at dispatch. |
| F5 | The repo's stated contract for a blind except in library code: "carry per-line noqa **with the reason**". | `pyproject.toml:263-270`. |
| F6 | `scripts/**` is **excluded from ruff** (`pyproject.toml:242` `exclude = ["notebooks/**", "**/*.ipynb", "scripts/**", "tests/data/**"]`), so the three `E402` tags in `scripts/test/measure_fit_path_dependence.py:25-27` are dead by construction — ruff never reads the file, which is also why `RUF100` did not list them (F2). Dead count by measure + construction: **13**. | Read at `2324e5c`. |

## v2 — the lock, not the sweep (read this first; everything else stands)

**The rejection** (I-67; `plans/noqa-sweep-v1-rejection.md` — the fork's own pre-push guard, `scripts/pixi_lock_check.sh`, refused the
Integrator's rejection commit `53f9728`, so the work order is carried on the ledger and no `review/` tag exists), in its own words:
*"REJECT, one block: the committed `pixi.lock` is not up to date with the committed `pyproject.toml`. The sweep itself passes every check.
It changes comments only, all 50 tags are classified, both reviews pass, and reduction output is byte-identical. But its one non-comment
line, `RUF100` added to `[tool.ruff.lint] select`, changes `pyproject.toml`, and the lock was not brought along with it. On this tree,
`pixi install --locked` fails, and re-locking pulls a newer `regex`. The base passes both."* Measured at `3275fc4`: `pixi install --locked`
→ exit 1 (`lock-file not up-to-date with the workspace`); `bash scripts/pixi_lock_check.sh` → exit 1 (drift: `regex` 2026.9.3 → 2026.9.29);
the base `4e5987a` passes both. Reachable: CI's `setup-pixi` (`test_and_deploy.yml:44`) installs `--locked` and would refuse the tree; the
shared deploy's plain `pixi install` would re-solve and deploy a `regex` the review never saw.

**The Analyst's call between the two routes I-67 names: route (ii) — keep `pyproject.toml` unchanged; enable `RUF100` where ruff is run.**
Why not route (i), a re-lock with `regex` held: `pyproject.toml` is the editable self-package's manifest, so *any* edit to it changes the
manifest hash and forces a re-solve; holding `regex` at the base's version is a hand-managed exception to the repository's push-time contract
("a push never carries dependency drift"), the lock must stay format v6 for analysis.sns.gov's older pixi, and the gate's own `pixi run`
re-locked the Integrator's checkout as a side effect — that coupling is the debt, and a comments-only sweep has no reason to carry it.
Where ruff runs in this repository (verified at `3275fc4`): **the pre-commit hook `ruff-check`** (`.pre-commit-config.yaml:20-26`,
`astral-sh/ruff-pre-commit` rev `v0.15.0`, `args: [--fix, --exit-non-zero-on-fix]`) — **no CI step runs ruff** (`test_and_deploy.yml` installs
pixi and runs the tests) and there is no `ruff.toml`. So "the repository's selection carries `RUF100`" is stated honestly as: **the hook's
args carry it, and U2 runs the same command.**

**N5′ (replaces N5).** *Fail loudly from now on: `RUF100` is enabled wherever this repository runs ruff — the pre-commit `ruff-check` hook's
`args` become `[--fix, --exit-non-zero-on-fix, --extend-select, RUF100]`, and U2's test shells out with the same `--extend-select RUF100` —
so a tag that goes dead (a rule later ignored, a line later fixed) fails the hook and the test instead of lingering. `pyproject.toml` is
**not** edited (I-67 B-1). Stated limit: a developer who runs a bare `ruff check` outside the hook does not get `RUF100`; the PR body says so,
and moving the selection into `pyproject.toml` is a one-line follow-up for a slug that re-locks deliberately.* The two global-`ignore`
entries that make tags dead today (`E722`, `N815`) are still not changed.

**What else moves with N5′:** §4's `pyproject.toml` row → `.pre-commit-config.yaml`; §5's common row reads `ruff check --extend-select RUF100`;
§7's last row → "`RUF100` dropped from the hook's args → U2's 'hook selection' leg reds"; §8.1 adds I-67's lock checks; §9's third bullet
reads "`RUF100` where ruff runs". **U2 gains a second leg** (U2b): the test reads `.pre-commit-config.yaml`, finds the `ruff-check` hook and
asserts `--extend-select` + `RUF100` are in its `args` — the leg that makes "the pre-commit would not see dead tags" a failing-capable claim
(L7). I-67's S-5 (U2's `subprocess.run` has no `timeout`) is taken in passing: `timeout=300`.

**D-2 (the seed's correction, I-67):** in `plans/noqa-sweep-findings.md`, child leaf 2's sentence "The defaults agree … so it shows only
when a settings file makes them differ" is wrong for the direct-beam path — `Direct_Beam` defaults to `tofbin=50` and `tof_step=100`
(`direct_beam_maker.py:52, 56`) and passes `tof_step` at `:160`, so the ignored `tof_step` matters there even at the defaults. One sentence,
corrected on the ledger by the Developer; the PR body's copy follows.

**v2 recipe (no production line, no tag change, no lock change).** On `feature/noqa-sweep` @ `3275fc4`: (1) revert the `pyproject.toml`
hunk (`git diff 4e5987a..<tip> -- pyproject.toml` empty); (2) `.pre-commit-config.yaml`: the `ruff-check` hook's `args` gain
`--extend-select, RUF100`; (3) `tests/test_noqa_tags.py`: U2's ruff call carries `--extend-select RUF100` and `timeout=300`; U2b added, RED
first with the arg absent; (4) in a **clean worktree** of the tip: `pixi install --locked` → 0 and `bash scripts/pixi_lock_check.sh` → 0,
`git status --porcelain pixi.lock` empty afterwards — all three in the commit body (I-67: "add a check that would have caught this");
(5) `pre-commit run ruff-check --all-files` green (the hook with `RUF100` is now the lint); (6) the battery's two tables again, with two rows
added — "`--extend-select RUF100` dropped from the hook's args → U2b reds" and "`RUF100` dropped from U2's ruff call → U2 passes only if a dead
tag is also re-added; record it as the pair" — each `<mutation> → <test> -> N failed`, N ≥ 1; (7) D-2's sentence on the ledger; (8) merge the
predecessors forward if they moved (`feature/time-slicing-reconcile`, `feature/roi-popout-dialog`); gate; **retag `qa/noqa-sweep`** (the v1 tag
at `3275fc4` is the Developer's to move, with the usual record). The push going through the fork's guard is itself the proof that B-1 is closed.

**Advisory D-1** (a later bare `# noqa: BLE001` passes CI — reasons are enforced only by the one-off U1) and D-3/D-4, S-1–S-4 ride the PR body
as I-67 wrote them; none is taken here (N4: a classifier slug).

## Re-seal at dispatch (2026-10-07, A-111) — the census on the dispatch tree (`4e5987a` + `18059cc` merged), by `grep`; ruff's RUF100 pass is the Developer's first act

**36 `noqa` tags in 15 non-test files under `src/` + `launcher/`** (was 32 at `2324e5c`), plus **15 in `tests/`, `launcher/tests/`, `scripts/`**
(the `RUF100` selection reaches tests; `scripts/**` stays excluded, F6). By file: `web_report.py` 10 (unchanged: 3 `BLE001`, 2 `E501` blanket-form,
5 `E722` blanket-form); `settings_editor.py` **7** (was 4 dead `BLE001` at `:428,728,952,976` — the stack #38–#40/#43/#45 rewrote the file: now
`N802` `:519` (K2's `eventFilter`, "Qt's name"), `BLE001` `:529,562,979,990,1387,1415` — **whether these are still dead under `per-file-ignores` is
F2's ruff measurement, to be re-run**); `binary_processing.py` 4 (3 `ARG001` with reasons, 1 `BLE001` with a reason; the intake widened two
signatures on tagged lines — the tags stand); `nr_reduction_calc.py` 3 (`N801`, `BLE001`, `ARG002` — all with reasons; the `ARG002` line now also
carries the intake's `start_times`/`end_times`); `direct_beam_maker.py` 2 (`N801`, `BLE001`, reasons); one each in `save_reduced_data.py` (`BLE001`
reason), `reduction_template_reader.py` / `new_reduction_template_reader.py` (`E722`, code-scoped), `new_reduction_from_template.py` (`ARG001` reason),
`instrument_settings.py` (`N815`), `gravity_correction.py` (`BLE001`, no reason), `reduce_REF_L.py` / `new_reduce_REF_L.py` (`BLE001`, "deliberately
broad"); **new since `2324e5c`:** `launcher/apps/roi_dialog.py:84` `BLE001` with a reason (R2), and **`src/lr_reduction/time_resolved.py:25` `# noqa ARG001`
— no colon, a blanket-form tag of F3's class, from the intake** (N2's re-spelling rule applies: `# noqa: ARG001 -- <reason>` or the argument removed).
The `tests/` set: `launcher/tests/test_time_resolved.py` ×3 `ARG001` (fixtures), the rest as at `2324e5c`.

**What changes in §2–§4 by this census:** F1's "37 in 17" → **36 in 15** (+15 test-side); F2's four dead `settings_editor.py` tags → re-measure the six
`BLE001` and the `N802` with ruff on the dispatch tree (the K-slugs' `@guarded` pattern may make some live); F3's seven blanket-form tags → **eight**
(+ `time_resolved.py:25`); F4's live set + `roi_dialog.py:84`. §4 "the 17 tag-bearing files" → the 15 + the test files `RUF100` flags. The
reduction-path files touched are tag lines only (N4: no expression changes) — the Integrator's masked harness against the base tip is the proof
(§8: same(masked) in all scenarios, as for the intake).

**Developer's first act at cut:** `ruff check --extend-select RUF100 --no-fix src launcher tests` on the merged tree; record F2/F3/F4's counts in
the commit body as the sealed facts; where they differ from this grep census, the ruff numbers govern and the plan's N1 table (`plans/noqa-sweep-findings.md`)
records both.

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| N1 | **Every tag is classified, once, in `plans/noqa-sweep-findings.md`** — one row per tag: `file:line`, the rule named, what ruff says (`RUF100` dead / blanket / live), the code the tag guards, the classification (**dead** · **blanket-mislabelled** · **live, reasoned** · **live, unreasoned** · **masking a defect**), and the disposition (removed / re-spelled with a reason / kept / child leaf). The table is complete: its row count equals the grep count at the base, and the PR body carries it. |
| N2 | **Dead tags are removed** (F2's ten by measure + F6's three by construction, re-measured at dispatch), and nothing else on those lines changes. |
| N3 | **Blanket directives are made precise:** each `# noqa <CODE>` without a colon becomes `# noqa: <the rule that actually fires>` **with a one-clause reason** (F5's contract) — for the five `web_report.py` excepts, `BLE001` and why that handler must not raise — or, if no rule fires on the line, the tag is removed (F3's two). A blanket `# noqa` with no code never survives the sweep. |
| N4 | **A tag that masks a defect is a finding, not a fix.** If reading the guarded code shows the suppressed rule was pointing at a real problem (a blind except swallowing an error the caller needs; an unused variable that was meant to be used; an argument the function should honour), the row says so with the evidence, the tag **stays as it is** in this slug, and a child leaf is proposed in the findings doc (`Seed:` the row) for the Analyst to plan — behaviour change rides its own slug and its own gate. |
| N5 | **(v1 wording — superseded by N5′ in the "v2" section: `RUF100` where ruff runs, `pyproject.toml` untouched.)** ~~**Fail loudly from now on:** `RUF100` joins the ruff `select`~~, so a tag that goes dead (a rule later ignored, a line later fixed) fails lint instead of lingering; the pre-commit `ruff check` and the gate both see it. The two global-`ignore` entries that make tags dead today (`E722`, `N815`) are **not** changed — their rationale is the config's. |

**Types and states** (per tag): rule ∈ {selected and firing, selected and not firing, ignored globally, ignored per-file, never
selected} × spelling ∈ {`# noqa: CODE`, `# noqa CODE` (blanket), `# noqa` (blanket), multi-code} × reason ∈ {on the line, in a
nearby comment, none}. Each combination maps to exactly one N1 classification; the findings doc states the mapping once and the
Integrator checks every row against it.

**Operation × state (each cell a required outcome, named by a test or by the findings table — U1–U4):**

| Tag state | Disposition | Lint after | Behaviour after |
|---|---|---|---|
| dead (`RUF100`) | removed | green (and `RUF100` would now red if re-added) | identical |
| blanket, a rule fires | `# noqa: <RULE>` + reason | green | identical |
| blanket, nothing fires | removed | green | identical |
| live, reasoned | kept | green | identical |
| live, unreasoned | reason added (one clause) | green | identical |
| masking a defect | kept; findings row + child leaf | green | identical (the fix is the child's) |

## 4. Files to change

| File | Change |
|---|---|
| the 17 tag-bearing files | per N2/N3 — tag lines only; **no statement changes** |
| `.pre-commit-config.yaml` (**v2**; was `pyproject.toml` `select` += `"RUF100"` — withdrawn, I-67 B-1) | the `ruff-check` hook's `args` gain `--extend-select, RUF100` |
| `plans/noqa-sweep-findings.md` (ledger) | N1's table |
| tests | U1–U4 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | `ruff check --extend-select RUF100` at the feature tip (**v2**: as the hook runs it) | green |
| common | `pixi install --locked` and `scripts/pixi_lock_check.sh` in a clean worktree of the tip (**v2**, I-67) | both exit 0; `pixi.lock` unmodified after the gate |
| common | `pixi run test-reduction` | identical results and warnings to the base — nothing but comments changed |
| edge | a `web_report.py` blind except that swallows an error the report page needs | **finding** (N4), tag kept, child leaf proposed — not fixed here |
| edge | a tag whose rule is ignored globally but which documents intent (`N801` on a class name the scientists know) | dead by ruff's measure → removed; the intent, if worth keeping, becomes a plain comment |
| pathological | a tag re-spelled to a code that does not fire | `RUF100` reds the lint — U2 |
| pathological | a statement changed "while there" | the diff review reds it (U4) |
| pathological | the findings table misses a tag | U1 reds (row count vs grep) |

## 6. Red-Green TDD seed

| # | Test | RED at the base |
|---|---|---|
| U1 | the findings table's row count equals the tag count at the base (a test that greps the base's listing committed beside the doc and compares) | no doc |
| U2 | `ruff check --extend-select RUF100` (the repo's selection plus `RUF100`, **v2**: exactly the hook's command) over `src launcher tests scripts` reports nothing (a pytest that shells out, like the pre-commit hook; `timeout=300`, I-67 S-5) | 10 findings |
| U2b (**v2**) | `.pre-commit-config.yaml`'s `ruff-check` hook has `--extend-select` and `RUF100` in its `args` (the test parses the YAML) | the arg absent |
| U3 | no `# noqa` without a colon-separated code remains (`grep -rnE '#\s*noqa(\s|$)(?!:)'`-equivalent in Python) | 7 blankets |
| U4 | **the diff is comments-only:** every changed line in the 17 files differs from the base only in its `# noqa…` comment — a test that walks `git diff <base>` for those files and asserts code-token equality (strip the comment, compare) | — (guard) |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| one dead tag left in place | U2 |
| a blanket re-spelled without a colon | U3 |
| a blanket re-spelled to a rule that does not fire | U2 |
| a row dropped from the findings table | U1 |
| a guarded statement edited along the way | U4 |
| `--extend-select RUF100` dropped from the hook's args (**v2**; was "`RUF100` not added to `select`") | U2b (the pre-commit would not see dead tags) |
| `RUF100` dropped from U2's ruff call (**v2**) | U2 goes blind — record the pair: with a dead tag re-added, U2 must still red only while the arg is present |

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero; `ruff check --extend-select RUF100` green, as the hook runs it (**v2**). **In a clean worktree of the tip:
   `pixi install --locked` exits 0 and `bash scripts/pixi_lock_check.sh` exits 0; `pixi.lock` is unmodified after the gate run — a re-lock is a
   finding, not a fix (I-67 B-1). `git diff <base>..<tip> -- pyproject.toml pixi.lock` is empty.**
2. §6 RED→GREEN; §7 per row.
3. The findings table is in the PR body; every "masking a defect" row names its proposed child leaf; the Analyst plans those
   leaves after the merge (they are the human's to add to the charter — the PR body lists them as proposals).
4. Security reviewer reads every blind-except row (F4's ten + F3's five) for what is swallowed and whether a caller depends on
   it; design reviewer reads the `ARG*`/`F841`/`N801` rows for dead code.
5. PR body: comments-only change (U4), the table, the child-leaf proposals.

## 9. Learnings relied on

- The termination rule: out-of-scope findings → advisories or a child leaf — N4 makes this slug a *classifier*, so its gate is crisp.
- `pyproject.toml:263-270`: the repo already states the contract for a blind except ("noqa with the reason"); the sweep enforces it.
- Detection complete, resolution minimal (CPKT design framing): `RUF100` where ruff runs (**v2**: the hook's args; was "in `select`") detects every future dead tag; the sweep
  resolves only what is mechanical (dead, blanket) and routes the rest.
- **L16 (v2):** before declaring an edit to a config file, ask *what else reads this file* — `pyproject.toml` here is both ruff's config and
  the pixi self-package manifest, so a one-token lint change stales the lock; the plan's §2 should have measured `pixi install --locked` on
  the intended edit. The repository's guard found it, as a guard should; the plan should not have needed it to.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | `scripts/test/measure_fit_path_dependence.py`'s three `E402` tags. | Dead by construction (F6: `scripts/**` excluded) — removed under N2; whether `scripts/` *should* be linted is a question for the PR body, not this slug. |
| A2 | Whether to turn the five `web_report.py` blind excepts into narrower excepts. | **Not here** (N4). If the security reviewer finds a swallowed error a caller needs, that is a child leaf. |

## Revision history

### v2 — 2026-10-07, after the Integrator's rejection of v1 @ `3275fc4` (I-67; ledger-carried record `plans/noqa-sweep-v1-rejection.md`; attempt 1 of 3)

Rejection quoted in full in the "v2" section. One block (B-1: the committed lock vs the committed manifest); the sweep itself passed every
check. What v2 changes: N5 → N5′ (`RUF100` where ruff runs — the pre-commit hook's args and U2; `pyproject.toml` untouched); U2b and S-5's
timeout; §4, §5, §7, §8.1, §9 accordingly; D-2's sentence in the findings doc; L16. **Plan error owned:** N5 declared a `pyproject.toml` edit
without asking what else reads that file — it is the pixi self-package manifest, so the edit staled `pixi.lock`; the route choice (ii over a
hand-held re-lock) is the Analyst's, as I-67 left it. Unchanged: scope, Base (`4e5987a` + `18059cc` forward), the PR target, N1–N4, the
findings table, every tag disposition. The Developer continues on `feature/noqa-sweep` @ `3275fc4`; the stale `qa/noqa-sweep` tag is theirs
to move at v2.

v1 — **dispatched 2026-10-07 (A-111)** on the posture trigger (the intake's draft PR #48 open, I-66), stacked under clause (4) on `feature/time-slicing-reconcile` @ `4e5987a` with `feature/roi-popout-dialog` @ `18059cc` merged forward at cut (conflict-free), re-sealed by grep census (ruff's pass the Developer's first act). Authored 2026-10-04 against `exp-review` @ `2324e5c` (`[human, 2026-10-04, PR #37 comment]`, couriered; A-46), **staged** behind
`editor-sections` and `test-suite-warnings` merged; the tag census (F1–F4) measured with ruff 0.15.11's `RUF100` before authoring.
