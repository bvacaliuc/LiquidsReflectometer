# Plan: `log-level-console-pins` — the four unpinned behaviours of K10 v3 get their tests, the fixture saves and restores the package logger, and the comment that overstates the parse is reworded

**Campaign:** `exp-review-fixes` · **Leaf:** `log-level-console-pins` (K15; refs `triage/log-level-console-pins`, `feature/log-level-console-v2` — commits on top of `4fb8c05`, no rewrite;
`qa/log-level-console-pins`) · **Status:** **DISPATCHED — v1 (attempt 1 of N = 3)**, 2026-10-21 (A-170) on the human's addressed word `[human, 2026-10-21 (to the Analyst): "you may dispatch K8, K9, K14 and K15. Let us hold K16 until after L4 lands to upstream:exp-next - thank you!"]`; proposed at A-167 from I-127's test-review advisories ·
**Base:** `feature/log-level-console-v2` @ **`4fb8c05`** (K10 v3, PASS at I-127; #55's head, `MERGEABLE`); L1′ `81acc87` beneath it; a current lock and the fork's guard (pushable) ·
**PR:** none new — the Integrator's PASS fast-forwards #55 · **Reviews:** test (block); design (advise) · **Gate:** G literal on L1′'s base (expected launcher 10, reduction 168 + the new tests);
ruff `--extend-select RUF100` clean; the two-file scope.

Campaign: exp-review-fixes

## Declared scope

**In:** `tests/unit/test_log_level_console.py` — (1) the length guard pinned: a T5 case `"9" * 5000` (INFO + one WARNING, no raise) **and** a fresh-process case
(`LR_REDUCTION_LOG_LEVEL=$(python -c 'print("9"*5000)')` → rc 0, one warning on stdout) — V1-69's endorsement; (2) `.strip()` pinned: `" debug\n"` → DEBUG (not INFO + warning);
(3) `propagate` pinned: after configuration `logging.getLogger("lr_reduction").propagate is True`; (4) replace-vs-relevel pinned: after `("INFO")` then `("DEBUG")`, the handler object
on the package logger is **not** the first one (replaced), there is exactly one, and its level is DEBUG; (5) the `reset` fixture **saves and restores** the package logger's handlers
and level (v3 leaves package logging off for later modules in the session — I-127's note); `src/lr_reduction/__init__.py` — only the comment at line 24 reworded to a true
statement (`isdecimal()` names an unsigned decimal; `len(text) < 10` keeps `int()` within its digit limit; together neither call can raise) — no behaviour change. **Out:** any
behaviour change; the GREEN body of `4fb8c05` (history; the new commit's body states the correction); K10's placement (plan D-2, the human's).

## 1. Request and symptom

I-127 (the test review, not blocking): four behaviours of v3 unpinned — the length guard (removed → 25 passed), `.strip()`, `propagate = False`, re-levelling instead of
replacing; the fixture leaves package logging off for later modules; `__init__.py:24` and the GREEN body overstate ("isdecimal is exactly what int accepts"; "the behaviour is
the previous one"). V1-69 endorsed K15 as a one-pass test addition. The human's word above dispatches it.

## 2. Verified facts at `4fb8c05` (2026-10-21 16:34Z; this clone)

| # | Fact | Evidence |
|---|---|---|
| V1 | `feature/log-level-console-v2` @ `4fb8c05` = #55's head, `MERGEABLE`; no `qa/`, `review/`, `triage/` refs | `ls-remote`, `gh pr view` |
| V2 | v3's `__init__.py`: 42 lines; the number path `text.isdecimal() and len(text) < 10`; a second call removes the named handler(s) then adds a fresh one; `propagate` untouched (True) | D-127/I-127 |
| V3 | The 25 tests pass whole and alone (F1 closed); the length guard, `.strip()`, `propagate`, replace-vs-relevel are caught by no test (I-127 measured each mutation 25 passed) | I-127 |
| V4 | Python 3.11's `int()` refuses > `sys.get_int_max_str_digits()` = 4300 digits; `"9"*4301` is decimal | D-127 |

## 3. Design — behaviours (tests only; the code's behaviour is v3's)

| # | Behaviour pinned |
|---|---|
| B1 | A 5000-digit decimal value → INFO + one WARNING naming the value's shape (the repr truncated is fine), no raise — in-process (T5 case) and in a fresh process (T8 case). |
| B2 | `" debug\n"` → DEBUG (stripped), no warning. |
| B3 | `propagate` stays True after configuration (library convention, plan D-3). |
| B4 | A second call replaces the handler: one handler on the package logger, a different object from the first, level DEBUG. |
| B5 | The fixture saves `(handlers, level)` of `lr_reduction` before each test and restores them after — a later test module sees the import-time state, not "off". |
| B6 | The comment at `__init__.py:24` reworded; the new commit's body states what v3's GREEN body overstated and what is true. |

## 4. Files to change

| File | Change |
|---|---|
| `tests/unit/test_log_level_console.py` | B1–B5 (about five tests and the fixture) |
| `src/lr_reduction/__init__.py` | one comment line (B6); no code change — `git diff` shows comment-only |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | the length guard removed | the 5000-digit cases red (import raises / in-process raises) | T1 |
| 2 | `.strip()` removed | the padded case red | T2 |
| 3 | `propagate = False` added | T3 red | T3 |
| 4 | re-level instead of replace | T4 red (same object) | T4 |
| 5 | the fixture restores nothing | T5 red (a sentinel test module asserts the import-time state) | T5 |
| 6 | a code change slipped into `__init__.py` | T6 (comment-only diff) red | T6 |

## 6. Red-Green seed

- **T1** `"9"*5000` in-process (T5's parametrisation) and the fresh-process case: RED with the guard removed (the Developer shows it on a scratch copy), GREEN at `4fb8c05`.
- **T2** `" debug\n"` → DEBUG. **T3** `propagate is True`. **T4** replace-vs-relevel by object identity. **T5** the fixture's save/restore: a test that configures `NOTSET` then checks, after the fixture, that the package logger has its import-time handler back.
- **T6** `git diff 4fb8c05..<tip> -- src/lr_reduction/__init__.py` is comment-only (`git diff -w --ignore-blank-lines` plus a Python AST comparison of the two files equal).
- **T7** G: 10 + (168 + the new tests), rc 0; ruff clean.

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| the length guard removed | T1 |
| `.strip()` removed | T2 |
| `propagate = False` | T3 |
| re-level instead of replace | T4 |
| the fixture's restore removed | T5 |

## 8. Acceptance criteria

T1–T7; the two files; the bodies with the trailer and no campaign identifiers; the Integrator's PASS fast-forwards #55 and its body notes the pins.

## 9. Learnings relied on

I-127 (the four unpinned behaviours, measured), D-127 (the digit limit), V1-69 (the endorsement and the 5000-digit shape), A-167.

## 10. Decisions

- **D-1 — tests only:** no behaviour change rides in; a behaviour the pins reveal as wrong becomes a todo, not a silent fix.
- **D-2 — on the K10 branch, no rewrite:** the human's placement decision (K10 plan D-2) is untouched.

## Revision history

- **v1 — 2026-10-21 (A-170):** authored and dispatched on the human's word (proposed at A-167). Sealed against `feature/log-level-console-v2` @ `4fb8c05`.
