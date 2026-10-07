# Plan: `noqa-sweep` — every `noqa` tag classified; dead ones removed; mislabelled blankets made precise; masked defects routed

**Campaign:** `exp-review-fixes` · **Leaf:** `noqa-sweep` (refs `triage/noqa-sweep`, `feature/noqa-sweep`, `qa/noqa-sweep`) ·
**Status:** READY — v1 (attempt 1 of N = 3) — **DISPATCHED 2026-10-07 (A-111)** on the posture's trigger (take line (3): `time-slicing-reconcile`'s draft PR open — I-66, PR #48); the original triggers (`editor-sections` #40 and `test-suite-warnings` #41 merged) also met; **re-sealed at dispatch** — see "Re-seal at dispatch" below (the ruff measurements F2/F3 are the Developer's first act, per §2's "re-run at dispatch") ·
**Base (clause (4)):** **`agentic/feature/time-slicing-reconcile` @ `4e5987a`** — the reduction stack's tip (#34 → #46 → #48; it contains #42 merged forward) — **with `agentic/feature/roi-popout-dialog` @ `18059cc` merged forward at cut** (the editor/ROI stack's tip: #43 → #45 → #47 on #44; the trial merge of the two tips is **conflict-free**, measured 2026-10-07) and before every `qa/` push; every open feature branch is thereby in the sweep's tree — the sweep classifies the files the intake adds lines to (the human's reason). Overlap census at `exp-review` `c39efe9`: the sweep's tag-bearing files ∩ the reduction stack {`binary_processing.py`, `nr_reduction_calc.py`, `save_reduced_data.py`, `direct_beam_maker.py`, `time_resolved.py` (new)} ∩ the editor/ROI stack {`settings_editor.py`, `roi_dialog.py` (new)} ∩ #42 ∅ · **PR target:** `feature/time-slicing-reconcile` on the fork, **draft** (the Integrator names the full stack and the merged-forward ROI stack; **clause (3a)** → `exp-review` if the base's tip is an ancestor of `exp-review` at open) ·
**Review domains:** design, security (block) · **Kind:** library + launcher, **not reduction-path** (no expression changes; a
tag's removal or re-spelling changes no behaviour — a defect found behind a tag is **not fixed here**, §3 N4) ·
**Sources:** `[human, 2026-10-04, PR #37 comment: "we should also do a sweep of existing 'NOQA' tags to see if those are still
needed or if they are masking an underlying defect in the code"]` via `requests/test-suite-warnings-and-noqa-sweep.md`; charter §3 row.

## Declared scope

**Files in:** the 17 files holding a `noqa` tag at `2324e5c` (F1's list — re-listed at dispatch), `pyproject.toml` (`[tool.ruff.lint]`
`select` gains `RUF100`), a new `plans/noqa-sweep-findings.md` **on the ledger** (the Developer writes it beside the learning file;
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
| N5 | **Fail loudly from now on:** `RUF100` joins the ruff `select`, so a tag that goes dead (a rule later ignored, a line later fixed) fails lint instead of lingering; the pre-commit `ruff check` and the gate both see it. The two global-`ignore` entries that make tags dead today (`E722`, `N815`) are **not** changed — their rationale is the config's. |

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
| `pyproject.toml` | `select` += `"RUF100"` |
| `plans/noqa-sweep-findings.md` (ledger) | N1's table |
| tests | U1–U4 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | `ruff check` at the feature tip | green with `RUF100` selected |
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
| U2 | `ruff check --select RUF100` (plus the repo's selection) over `src launcher tests scripts` reports nothing (a pytest that shells out, like the pre-commit hook) | 10 findings |
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
| `RUF100` not added to `select` | U2's "repo selection" leg (the pre-commit would not see dead tags) |

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero; `ruff check` green with `RUF100`.
2. §6 RED→GREEN; §7 per row.
3. The findings table is in the PR body; every "masking a defect" row names its proposed child leaf; the Analyst plans those
   leaves after the merge (they are the human's to add to the charter — the PR body lists them as proposals).
4. Security reviewer reads every blind-except row (F4's ten + F3's five) for what is swallowed and whether a caller depends on
   it; design reviewer reads the `ARG*`/`F841`/`N801` rows for dead code.
5. PR body: comments-only change (U4), the table, the child-leaf proposals.

## 9. Learnings relied on

- The termination rule: out-of-scope findings → advisories or a child leaf — N4 makes this slug a *classifier*, so its gate is crisp.
- `pyproject.toml:263-270`: the repo already states the contract for a blind except ("noqa with the reason"); the sweep enforces it.
- Detection complete, resolution minimal (CPKT design framing): `RUF100` in `select` detects every future dead tag; the sweep
  resolves only what is mechanical (dead, blanket) and routes the rest.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | `scripts/test/measure_fit_path_dependence.py`'s three `E402` tags. | Dead by construction (F6: `scripts/**` excluded) — removed under N2; whether `scripts/` *should* be linted is a question for the PR body, not this slug. |
| A2 | Whether to turn the five `web_report.py` blind excepts into narrower excepts. | **Not here** (N4). If the security reviewer finds a swallowed error a caller needs, that is a child leaf. |

## Revision history

v1 — **dispatched 2026-10-07 (A-111)** on the posture trigger (the intake's draft PR #48 open, I-66), stacked under clause (4) on `feature/time-slicing-reconcile` @ `4e5987a` with `feature/roi-popout-dialog` @ `18059cc` merged forward at cut (conflict-free), re-sealed by grep census (ruff's pass the Developer's first act). Authored 2026-10-04 against `exp-review` @ `2324e5c` (`[human, 2026-10-04, PR #37 comment]`, couriered; A-46), **staged** behind
`editor-sections` and `test-suite-warnings` merged; the tag census (F1–F4) measured with ruff 0.15.11's `RUF100` before authoring.
