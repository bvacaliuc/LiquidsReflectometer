# Plan: `log-level-console` — the package's Python logging reaches the console **on by default, at INFO, on stdout** (the scientists' opt-out posture); `LR_REDUCTION_LOG_LEVEL` sets the level or switches it off with `NOTSET`; no value can make `import lr_reduction` fail

**Campaign:** `exp-review-fixes` · **Leaf:** `log-level-console` (refs `triage/log-level-console-v2`, `feature/log-level-console`, `qa/log-level-console`; K10 in `dispatch-queue.md`) ·
**Status:** **v4 DISPATCHED 2026-10-22 (A-200, attempt 4 of 4 — the cap extended by the human's word for this version; a rejection escalates)** on the human's addressed word `[human, 2026-10-22 (to the Analyst): "Dispatch K10 v4 per requests/k10-v4-stderr-preserving-console-logging.md. I extend K10's retry cap to 4 for this version. Converted print() calls go to stdout; everything upstream sent to stderr — our WARNING/ERROR logs, logged exceptions, uncaught exceptions — stays on stderr. Include the L2 amendment (d313313's three converted warnings logged at info) and re-gate the stack."]` — base `feature/log-level-console-v2` @ `1fbc900` (K10‴, PASS I-150), refs `triage/log-level-console-v4`, `qa/log-level-console` (re-set at the v4 tip); v3 PASS (I-127 @ `4fb8c05`), K15's pins PASS (I-134 @ `02e5a45`), re-gated as K10″/K10‴ (I-144 @ `ceb77ff`, I-150 @ `1fbc900`); earlier: v2 PASS (I-113) → draft PR #55; **v3 DISPATCHED 2026-10-21 (A-166, attempt 3 of 3 — a rejection escalates)** on the human's addressed word `[human, 2026-10-21 (to the Analyst): "dispatch K10 v3"]` (staged at A-160 on the #55 comment): the simplification per V1-68, the 25 tests unchanged except the two-line fixture fix (F1); refs `triage/log-level-console-v3`, `feature/log-level-console-v2` (commits on top of `c95cfb5`, no rewrite), `qa/log-level-console`; at PASS the Integrator fast-forwards #55 — no new PR · v2: **DISPATCHED — v2 (attempt 2 of N = 3)**, 2026-10-20 (A-150), on the Integrator's REJECT of v1 @ `7041087` (I-110; the canonical record is `todo.md` at
`feature/log-level-console` @ `b01758f`) **and on the human's changed requirement** (the body of the human's own commit `14ca2b0` on `feature/add-lr-reduction-log-level`,
2026-10-20 12:06 EDT — §1). v1: A-148, amended at build A-149 ·
**Base:** **`feature/landing-l1-core` @ `c5ef58d`** (L1's tip = upstream `exp-landing-l1-core`, #219's head; green: I-97 10 + 172, I-108, I-110's G). **Rebuild v2 from the base**
(RED + GREEN again, as at D-108): the `todo.md` commit `b01758f` and its later clearing are campaign bookkeeping and stay out of the upstream-bound branch (I-110, history hygiene).
The two files are touched by no layer and not by `exp-review` (I-109), so the commits apply cleanly on any base (§10 D-2) ·
**PR target:** the fork's `feature/landing-l1-core`, **draft**, stacked on #54 (GitHub retargets it to `exp` when L1 lands), opened by the Integrator at PASS; where the switch
finally lands is the human's (§10 D-2) · **Reviews (charter §5):** design, test (block); numerical-diagnostics and ui-aspects n/a ·
**Gate:** G literal at the tip — `pixi install --locked`, the lock check, `pixi run test-reduction` and `pixi run test-launcher`, each EXIT 0 (I-109's reading); scope
`git diff c5ef58d..<tip> --stat` = the two files; no landing proof applies (this is not a replay).

Campaign: exp-review-fixes

## Declared scope

**In:** `configure_console_logging(value: str | None) -> logging.Handler | None` in `src/lr_reduction/__init__.py`, called once at import with
`os.environ.get("LR_REDUCTION_LOG_LEVEL")`; the test module `tests/unit/test_log_level_console.py`. **Out:** every `print(` in `src/` (157) and `launcher/` (44); Mantid's
own logger and its console level; the autoreduce scripts; the launcher's code (it imports the package in-process and inherits the switch); any `basicConfig` or root-logger
change; the landing layers' content (§10 D-2); the human's branch `feature/add-lr-reduction-log-level` (the human's to replace, §10 D-2 (iii)).

## 1. Request and symptom — and the requirement that changed between v1 and v2

**The word that chartered K10** `[human, 2026-10-20 (to the Advisor, verbatim in V1-64): "many print() diagnostics have been distributed to log.info()/log.warning() …
'swallowed by the UI'. Would it be possible to make a variation on feature/landing-l2-reduction before I push it upstream (and without damaging the stack plan) to allow a
configuration (perhaps simply via environment-variable injection) to make log levels also emitted on the console? Default/Unset can remain off as it is now."]`

**The requirement that supersedes its last sentence** — the human's own commit `14ca2b0` (`feature/add-lr-reduction-log-level` on the fork, on upstream `exp` @ `8971999`,
2026-10-20 12:06 EDT; its body, verbatim): *"suggested by Advisior (V1) on campaign exp-review-fixes — Recorded as V1-64 … — Discussion with scientist asked for an opt-out
posture wherein the default is to emit output (to stdout) and the choice is to suppress. Chose to suppress via NOTSET keyword as documented"*; and in its code: *"NB:
autoreduction \*FAILS\* if any characters show up on stderr…"*. **Correct-and-flag:** V1-64 said "Default/Unset can remain off"; the later statement — the scientists' ask,
recorded by the human after a discussion with them — outranks it (the Integrator's reading too, I-110). v2 follows the later statement: **on by default at INFO, on stdout,
`NOTSET` to switch off.** One word from the human ("keep opt-in") restores v1's posture; the rest of v2 stands either way.

**The human's variant does nothing** — measured by the Integrator (I-110) and by this seat (the file loaded in isolation under the pixi interpreter: unset, `INFO`, `DEBUG`,
`NOTSET` all leave 0 handlers, level 0; an INFO record is dropped). `import logging, os` omits `sys`, so `logging.StreamHandler(sys.stdout)` raises `NameError`, and the
`except Exception: pass` around the block swallows it: one missing import, invisible by the guard's own design. Its body also carries the ledger's URL and campaign
identifiers (not for an upstream PR). v2 is the tested form of the human's intent; which branch carries it is §10 D-2.

**v1's rejection** (I-110; `todo.md` @ `b01758f`): everything in G green (10 + 188), scope exact, acceptance 2–3 reproduced; **B1 blocking** —
`LR_REDUCTION_LOG_LEVEL='²'` (also `'①'`) makes `import lr_reduction` raise `ValueError` from `__init__.py:28-29` (`str.isdigit()` is True for superscripts and circled
digits, `int()` accepts only `Nd` digits), the case D-4 ruled out and B4 claimed to cover; advisories R2 (T6 does not pin the handler's level), R3 (the fixture lets a
root-logger mutation leak across tests, so T9 misses it), R4 (T8's unset case cannot catch "unset at WARNING"); and `'0'`/`'NOTSET'` silently showing less than DEBUG, for
the Analyst — decided in §10 D-7.

## 2. Verified facts at `feature/landing-l1-core` @ `c5ef58d` (I-110, D-108, this seat)

- `src/lr_reduction/__init__.py` at the base is the `__version__` import only; every module logger is `logging.getLogger(__name__)` under `lr_reduction`; no handler is configured
  anywhere; `Logger.callHandlers` uses `lastResort` (WARNING+ to **stderr**, bare `%(message)s`) only when no handler is found on the chain. `requires-python >= 3.11`.
- G at the base and at v1's tip: `pixi install --locked` rc 0, `scripts/pixi_lock_check.sh` rc 0, `test-reduction` 188 (172 + 16 new), `test-launcher` 10, `pixi.lock` unchanged (D-108, I-110).
- `str.isdigit()` vs `int()`: `'²'`, `'①'` → `isdigit()` True, `int()` raises; `'１０'` (full-width) → both accept → 10 (I-110, measured). `logging.getLevelName("NOTSET")` → 0;
  a package logger at level 0 defers to root's WARNING, so `'0'`/`'NOTSET'` with v1's handler attached showed WARNING+ only, silently (I-110).
- Under pytest the root logger carries handlers, so `lastResort` never runs in-process; it is observable only in a fresh process (I-110 R4).
- **Amended at gate (I-112's design review; A-151):** at the base `c5ef58d` no `src/lr_reduction` module uses Python `logging` (0 modules; every `logger` there is Mantid's); the 3 modules / 18 calls
  are L2's (`3ea92cf`). So on L1 alone the switch prints only its own invalid-value WARNING; its work begins where the human wants it, with L2 — consistent with "before I push L2 upstream".
- The reduction suite runs as `cd tests/ && python -m pytest …`; `test-reduction` depends on `test-launcher`; unit tests live in `tests/unit/`.
- Autoreduce and stderr: *"autoreduction FAILS if any characters show up on stderr"* is the human's statement in `14ca2b0`, recorded here as the requirement's ground, not
  re-measured by this seat (the autoreduce runner is outside the campaign's clones).

## 3. Design — behaviours v2 (types first: amendment 18)

The input is **`str | None`** (an environment value is a `str`; absent is `None`). `value` is stripped; `None` or an empty/whitespace string is **unset**.

| # | Behaviour | Type and value |
|---|---|---|
| B1 | **Unset → ON at INFO, on stdout** (the opt-out posture). The handler attaches at import; every `lr_reduction.*` record at INFO or above prints `LEVEL name: message` on **stdout**; nothing on stderr. WARNINGs therefore move from stderr (`lastResort`) to stdout — for autoreduce the intended effect (§1's NB). | handler at `logging.INFO` |
| B2 | **`NOTSET` (any case) or `0` → OFF** (the opt-out keyword, the human's choice; `0` is NOTSET's number). No handler; the package logger's level untouched; exactly today's behaviour (`lastResort`: WARNING+ on stderr, INFO/DEBUG dropped). On a logger that already has the named handler, this call **detaches** it and resets the package level to NOTSET (symmetric with B5, for a later explicit call). | `None` returned |
| B3 | **Level parsing.** A level **name** (any case; whatever `logging` knows: `DEBUG`, `INFO`, `WARNING`/`WARN`, `ERROR`, `CRITICAL`/`FATAL`) or a string `int()` accepts with a **positive** value (`"10"` → 10; full-width `"１０"` → 10). | `int > 0` |
| B4 | **Invalid → INFO, loudly, never raising.** Every other `str` — `'verbose'`, `'²'`, `'①'`, `'-5'`, `'1.5'`, `' 7 x'` — attaches the handler at **INFO** and emits exactly one WARNING through the package logger naming the value and the accepted forms (`LR_REDUCTION_LOG_LEVEL='²' is not a level name (DEBUG, INFO, WARNING, ERROR, CRITICAL, a positive integer, or NOTSET to switch off); using INFO`). **`configure_console_logging` never raises for any `str`, and no environment value can make the import fail.** The guarantee comes from a type-complete parse (`try: int(text) except ValueError` → the name lookup → the invalid path), **not from a blanket `except`** — a blanket `except` is what hid the human's variant's own `NameError` (§10 D-8). | `logging.INFO` + 1 WARNING |
| B5 | **Idempotent and symmetric.** One handler named `lr_reduction.console`; a second call finds it by name and updates **both the handler's and the logger's level** (R2); `NOTSET`/`0` detaches it (B2). | one handler |
| B6 | **Scope.** Only `lr_reduction.*` loggers print through it; the root logger and every other package untouched; Mantid's logger untouched. | — |
| B7 | **Import time.** `__init__.py` calls `configure_console_logging(os.environ.get("LR_REDUCTION_LOG_LEVEL"))` once; the stream is `sys.stdout` as it is at that moment; `sys` is imported at the top of the module (the human's defect, as a §7 mutation). | — |

Format: `%(levelname)s %(name)s: %(message)s` (the same in v1 and in the human's variant). Why the package logger and not `basicConfig`: root would make matplotlib, Qt
and every library print; the package logger is the narrowest handle that covers all 39 existing calls.

## 4. Files to change

| File | Change |
|---|---|
| `src/lr_reduction/__init__.py` | `import logging, os, sys` at the top; `_HANDLER_NAME`, `_FORMAT`, `_ACCEPTED`; `configure_console_logging(value)` per §3 (about 40 lines); the import-time call after the `__version__` block, which stays as is. |
| `tests/unit/test_log_level_console.py` | rewritten for v2 (§6); the fixture removes the named handler from **both** `lr_reduction` and the root logger and resets the package level to `NOTSET` after each test (R3). |

No other file. No new dependency. No `.github/` change.

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: variable unset (the launcher from a terminal; a script; autoreduce) | INFO+ records on stdout as `INFO lr_reduction.x: …`; stderr empty | T1, T3, T8 |
| 2 | common: `DEBUG` / `WARNING` / `ERROR` | that level on stdout | T4 |
| 3 | common: `NOTSET` or `0` (the opt-out) | nothing attached; INFO dropped; WARNING+ on **stderr** by `lastResort` as today — the user's choice restores today's stderr | T2, T8 |
| 4 | edge: blank / lower case / `WARN` / `'１０'` | unset / name / 30 / 10 | T1, T4 |
| 5 | edge: a second call (`INFO` then `DEBUG`; then `NOTSET`) | one handler, level DEBUG on handler **and** logger; then detached | T6 |
| 6 | edge: a WARNING with the handler attached | printed **once**, on stdout; nothing on stderr | T7 |
| 7 | pathological: `'²'`, `'①'`, `'-5'`, `'1.5'`, `'verbose'` (the blocking finding's family) | attached at INFO + one WARNING naming the value; import succeeds, rc 0 | T5, T8 |
| 8 | pathological: the host application configures the root logger too | records print twice (ours + root's) — loud, not auto-resolved (§10 D-3) | documented |
| 9 | pathological: a tool parses the package's stdout | sees the new INFO lines — the accepted cost of the opt-out posture; `NOTSET` restores the old stdout | documented (§10 D-5) |
| 10 | pathological: another test in the suite asserts its own exact stdout | the gate shows it; fix that test's expectation or call `NOTSET` in that test only — never a suite-wide `NOTSET` in `conftest.py`, which would hide B1 from the suite | the Developer reports |
| 11 | pathological: a `spawn`ed worker (`binary_processing`) | re-reads the inherited variable: the same posture as the parent | §2; not tested |
| 12 | pathological: stdout closed or replaced (a daemonised process) | `StreamHandler` writes to whatever `sys.stdout` is at import; a closed stream raises inside `emit`, which `logging` reports via `handleError` (stderr) and does not propagate — no crash; not this slug's to fix | documented |
| 13 | out of scope: Mantid `logger.information/notice` lines | unchanged | — |

## 6. Red-Green TDD seed (`tests/unit/test_log_level_console.py`; written first, failing on the base, then §4)

A fixture `reset` runs **before and after** each test (amended at gate, A-151 — I-112's F1: the import-time call binds the handler to pytest's session-capture stdout, so a test run alone or first must start from a clean logger; v2 as built reset only after, exactly as this line prescribed, and T3/T5/T7 went red when run alone): remove any handler named `lr_reduction.console` from `logging.getLogger("lr_reduction")` **and** from `logging.getLogger()` (R3), and set the
package logger's level to `NOTSET`. Tests call `configure_console_logging(...)` explicitly (the import-time call already ran once, at import).

- **T1** `test_unset_or_blank_turns_on_at_info_on_stdout` (parametrised `None`, `""`, `"  "`): returns a `StreamHandler` named `lr_reduction.console`, `stream is sys.stdout`, formatter `_fmt == "%(levelname)s %(name)s: %(message)s"`, handler level and package level `INFO`.
- **T2** `test_notset_or_zero_switches_off` (parametrised `"NOTSET"`, `"notset"`, `"0"`): returns `None`; no handler named `lr_reduction.console` on the package logger; package level `NOTSET`; and after `("INFO")` then `("NOTSET")`: the handler is gone and the level is `NOTSET`.
- **T3** `test_child_info_reaches_stdout_only` (`capsys`): configure `"INFO"` inside the test; `logging.getLogger("lr_reduction.unit_probe").info("ping")` → stdout contains exactly `INFO lr_reduction.unit_probe: ping`; stderr empty.
- **T4** `test_level_names_and_integers` (parametrised): `"debug"`→10, `"WARNING"`→30, `"WARN"`→30, `"error"`→40, `"10"`→10, `"１０"`→10 (both the handler's and the logger's level).
- **T5** `test_invalid_values_use_info_and_warn_once_and_never_raise` (parametrised over at least `"²"`, `"①"`, `"-5"`, `"1.5"`, `"verbose"`, `" 7 x"`; `capsys`): no exception; level `INFO`; stdout has exactly one `WARNING lr_reduction: …` line naming the value (repr) and the accepted forms; stderr empty.
- **T6** `test_second_call_updates_both_levels_without_a_second_handler`: `("INFO")` then `("DEBUG")` → one named handler; **handler level DEBUG** (R2) and package level DEBUG.
- **T7** `test_a_warning_is_printed_once_on_stdout`: with `"INFO"` configured, `warning("w")` → stdout contains `WARNING lr_reduction.unit_probe: w` exactly once; stderr empty.
- **T8** `test_fresh_process_posture` (subprocess, `sys.executable -c "import logging, lr_reduction; L=logging.getLogger('lr_reduction.probe'); L.info('ping'); L.warning('w')"`), three cases: (a) the variable **absent** → rc 0, stdout contains `INFO lr_reduction.probe: ping` and `WARNING lr_reduction.probe: w`, stderr **empty**; (b) `LR_REDUCTION_LOG_LEVEL=NOTSET` → rc 0, stdout empty, stderr **exactly** `"w\n"` (lastResort's bare form — R4's pin of today's behaviour); (c) `LR_REDUCTION_LOG_LEVEL=²` → rc 0, stdout has the one WARNING naming `'²'` and then the INFO line.
- **T9** `test_other_packages_are_untouched` (`capsys`): with `"INFO"` configured, `logging.getLogger("not_lr_reduction").info("x")` prints nothing (with the R3 fixture this catches a root-logger handler).

RED on the base: T1–T7, T9 fail at import (`configure_console_logging` missing); T8 (a) fails (no output), (c) fails. GREEN after §4.

## 7. Mutate-once gate (the Developer's GREEN body records each mutation and its `<test> -> N failed`)

| Mutation | Must be caught by |
|---|---|
| `import sys` removed (the human's `14ca2b0` defect) | T8 (a) — the fresh-process path; in-process tests may not see it (the test module imports `sys` itself) |
| the import-time call removed | T8 (a), (c) |
| `isdigit()` before `int()` (v1's code) | T5 (`'²'`, `'①'` raise) |
| handler attached to the root logger instead of `lr_reduction` | T1 (not on the package logger), T9 (with the R3 fixture) |
| by-name idempotency guard dropped | T6 (two handlers) |
| `handler.setLevel` only inside `if handler is None` (R2) | T6 (handler level stays INFO) |
| `NOTSET` attaches anyway, or does not detach | T2 |
| default off (`None` → no handler; v1's B1) | T1, T8 (a) |
| stream `sys.stderr` (v1's choice) | T3, T7, T8 (a) (stderr must be empty) |
| invalid value → WARNING silently, or raises | T5 |
| level set on the handler only, not the logger | T3 (nothing on stdout) |
| a blanket `try/except` around the function body | not catchable by a test that passes; the design review checks the GREEN diff for it (§10 D-8) |

## 8. Acceptance criteria

1. G green at the tip on L1's base: `pixi install --locked` and the lock check EXIT 0; `pixi run test-reduction` (the new tests included) and `pixi run test-launcher` EXIT 0; counts ≥ L1's 10 + 172 plus the new tests; no other test's expectation changed except as §5 row 10 says, reported.
2. Shell, unset: `python -c "import logging, lr_reduction; L=logging.getLogger('lr_reduction.x'); L.info('ping'); L.warning('w')"` → stdout `INFO lr_reduction.x: ping` and `WARNING lr_reduction.x: w`; stderr empty.
3. Shell, `LR_REDUCTION_LOG_LEVEL=NOTSET` → stdout empty, stderr `w` once (today's behaviour); `=DEBUG` adds the DEBUG lines; `='²'` → rc 0, one WARNING naming `'²'`, then INFO.
4. `git diff c5ef58d..<tip> --stat` names exactly the two files of §4; no new dependency; no `.github/` change; no `todo.md` in the branch (rebuilt from the base).
5. The two commits (RED, GREEN) carry the model trailer; the GREEN body records the §7 mutations with their failing counts; **no ledger URL, campaign identifier or seat name in either body** (upstream-bound; I-110's note on `14ca2b0`).
6. Design and test reviews without a blocking finding; the Integrator's draft PR on the fork `--base feature/landing-l1-core`.

## 9. Learnings relied on

- I-110's `todo.md` @ `b01758f`: the type-domain argument (`isdigit` ≠ `int`), R2–R4, and "rebuild from the base" (history hygiene) — all adopted; amendment 18 (a fix is a
  behaviour over the whole type domain, and the guard varies the dimension the fix freezes).
- The human's `14ca2b0`: the opt-out posture and the stdout ground (§1); its defect as a §7 mutation.
- A-149: the base is L1's tip because upstream `exp` @ `8971999` is red on its own; V1-64: the mechanism (no handler anywhere; `lastResort`).

## 10. Assumptions and decisions (defaults in force unless the human says otherwise)

- **D-1 — the variable's name:** `LR_REDUCTION_LOG_LEVEL` (the same in the human's variant). A rename before the upstream PR is one line.
- **D-2 — where it lands (the human's; after PASS; additive):** the two files are disjoint from every layer, so: **(i)** the campaign's branch (L1 + v2) as `exp-log-level-console`
  upstream, stacked on #219 (the Integrator's draft PR on the fork is stacked on #54); **(ii)** also cherry-picked onto `feature/landing-l2-reduction` on the word "cherry-pick
  onto L2" (one declared non-replay change, a P1 exception; L3/L4 merge forward; L2 re-gated); **(iii)** the human's own branch name: replace `14ca2b0` on
  `feature/add-lr-reduction-log-level` with v2's two commits (they apply cleanly on `8971999`; the human's act — seats do not push to the human's branch) — recommended if the
  human wants that name upstream, since `14ca2b0` does nothing and its body carries the ledger's URL.
- **D-3 — propagation:** the package logger keeps `propagate = True` (library convention); §5 row 8 is loud.
- **D-4 — an invalid value:** INFO + one warning, never raise, never silent — now over the whole `str` domain (the blocking finding).
- **D-5 — the posture: opt-out (on by default at INFO)** — the human's `14ca2b0` after the scientists' discussion, superseding V1-64's "unset = off". Reversible by one word
  ("keep opt-in"): then B1 becomes v1's (unset → nothing) and nothing else changes.
- **D-6 — the stream: stdout** — the human's NB on autoreduce and stderr; v1's stderr dropped. Consequence accepted: WARNINGs leave stderr while ON.
- **D-7 — `'0'` / `'NOTSET'` (the Integrator's question):** they are the **off** switch, not an invalid value and not "clamp to 1" — the human chose `NOTSET` as the opt-out keyword,
  and `0` is its number. Negative or non-integer strings are invalid (D-4).
- **D-8 — no blanket `except`:** the no-raise guarantee is the parse's completeness (§3 B4), checked by T5's parametrisation and the design review; a blanket `except` hides the
  next missing import exactly as it hid this one.
- **D-9 — history hygiene:** rebuild from `c5ef58d`; the rejected tip `7041087` and the `todo.md` commit `b01758f` stay out of the branch (the Integrator's advice).
- **D-10 — not in this slug:** a GUI toggle; converting the remaining `print` calls; a deploy-side `export` (no longer needed for "on by default"; `NOTSET` is the scientists' off).

## Revision history

- **v1 — 2026-10-20 (A-148):** authored and dispatched on the human's word (V1-64). Sealed against upstream `exp` @ `8971999`.
- **v1 amended at build — 2026-10-20 (A-149):** on D-107's decision request (the declared base red on its own) and I-109's reading of G, option A: the base is `feature/landing-l1-core` @ `c5ef58d`.

### v2 — 2026-10-20 (A-150): the Integrator's REJECT of v1 @ `7041087` (I-110; `todo.md` @ `b01758f`) and the human's changed requirement (`14ca2b0`)

Cause: **B1 blocking** — `LR_REDUCTION_LOG_LEVEL='²'` raises at import (`isdigit()` ≠ `int()`); the fix as behaviour over the whole `str` domain (B4, D-4, D-8), the guard
parametrised over `'²'`, `'①'`, `'１０'` and more (T5, T4). R2 (handler level on a second call — B5, T6), R3 (the fixture clears root too — §4, T9), R4 (T8's fresh-process
pin of `lastResort`'s bare `w`) adopted. `'0'`/`'NOTSET'` decided: the off switch (D-7). **Requirement change:** the opt-out posture on stdout (D-5, D-6) from the human's
`14ca2b0`, which itself is a silent no-op (§1) and becomes a §7 mutation (`import sys` removed). Base unchanged (`c5ef58d`); rebuilt from the base (D-9). Attempt 2 of 3; a
third rejection escalates.
- **v2 amended at gate — 2026-10-20 (A-151, under the human's STOP):** §6's fixture resets before **and** after (I-112's F1 — the plan's own prescription was the defect, not the build; the Integrator's
  reading, PASS with F1 as the first advisory, concurred); §2 gains the L1-base fact. Not a new attempt. The analysis-branch copy follows when the STOP lifts (no subject push until then).

### v3 — staged 2026-10-21 (A-160) on the human's #55 comment; **dispatched 2026-10-21 (A-166) on the human's addressed word "dispatch K10 v3" — attempt 3 of 3**

**The ask** (#55, 2026-10-21 01:05Z, verbatim): *"I find that the implementation in `src/lr_reduction/__init__.py` is far too heavy for my taste. I have read the concern and made a
change to my manual branch `feature/add-lr-reduction-log-level`. Would you have a look at it and see if the implementation of this feature could be \*very\* simple in
`src/lr_reduction/__init__.py`? I am OK with tests being elaborate (_thank you for them!_)."* — and to the Advisor (V1-68): *"would you have a look and see if my concern can be addressed?"*
A question, so staged (the addressed-word rule, `b059f14`); one addressed word dispatches it.

**The human's `a799915` on `feature/add-lr-reduction-log-level`, measured by the Advisor (V1-68, fresh processes):** unset → INFO on stdout ✓; `20` ✓; **`INFO`, `DEBUG`, `NOTSET`, `0` →
0 handlers, `w` on stderr** — `int(_level)` raises `ValueError` on every level *name* inside `except Exception: pass`, so every name silently switches the console **off**, the
opposite of the opt-out posture; the blanket except hides it as it hid `14ca2b0`'s `NameError`. Also ruff I001 (unsorted imports), and no function for the tests to call.

**v3 scope (the Advisor's candidate, V1-68, measured: 41 lines with docstring, 18 of logic; v2's `tests/unit/test_log_level_console.py` unchanged → 25 passed; ruff `--extend-select
RUF100` clean):** `src/lr_reduction/__init__.py` only, on top of `feature/log-level-console-v2` @ `9cb0fbf` (#55 fast-forwards). Keeps `configure_console_logging(value)` (the tests'
handle and the import-time call), the handler name, the format and the `_ACCEPTED` text. Drops `_parse_level` by one fact: **`str.isdecimal()` is exactly the unsigned domain `int()`
accepts** (`'²'`/`'①'` False, `'１０'` True → 10, `'-5'`/`'1.5'` False), so `level = int(text) if text.isdecimal() else logging.getLevelNamesMapping().get(text)` cannot raise (3.11+;
`requires-python >= 3.11`) and needs no `try`; a second call **replaces** the named handler (one list comprehension) instead of re-levelling it; `NOTSET`/`0` → `setLevel(0)`, return
`None`; invalid → INFO + the one WARNING; no blanket `except` anywhere — nothing in the body can raise. Behaviours B1–B7 unchanged; **F1's fixture fix** (reset before and after, A-151)
rides in the same pass, so T3/T5/T7 pass when run alone. Mutation rows added: `int()` under a blanket `except` (a799915's defect — every name → off: T4/T8 red), `isdigit` for
`isdecimal` (T5 red), the second call re-levelling instead of replacing (T6). Gate: G literal (10 + 197) on L1's base as before; the Integrator's PASS fast-forwards #55. The
candidate, verbatim from V1-68, is the Developer's starting point:

```python
import logging
import os
import sys

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

_HANDLER_NAME = "lr_reduction.console"
_ACCEPTED = "DEBUG, INFO, WARNING, ERROR, CRITICAL, a positive integer, or NOTSET to switch off"


def configure_console_logging(value: str | None) -> logging.Handler | None:
    """Print the package's own log records on stdout (autoreduction treats anything on stderr as a failure).

    ``value`` is ``LR_REDUCTION_LOG_LEVEL``: unset or blank is INFO; a level name or a number sets the level;
    ``NOTSET`` or ``0`` switches it off (Python's default: WARNING and above on stderr). Never raises.
    """
    package = logging.getLogger(__name__)
    for old in [h for h in package.handlers if h.get_name() == _HANDLER_NAME]:
        package.removeHandler(old)
    text = (value or "").strip().upper() or "INFO"
    # str.isdecimal() is exactly what int() accepts as an unsigned number, so neither call can raise.
    level = int(text) if text.isdecimal() else logging.getLevelNamesMapping().get(text)
    invalid = level is None
    level = logging.INFO if invalid else level
    package.setLevel(level)
    if level == logging.NOTSET:
        return None
    handler = logging.StreamHandler(sys.stdout)
    handler.set_name(_HANDLER_NAME)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    package.addHandler(handler)
    if invalid:
        package.warning("LR_REDUCTION_LOG_LEVEL=%r is not a level name (%s); using INFO", value, _ACCEPTED)
    return handler


configure_console_logging(os.environ.get("LR_REDUCTION_LOG_LEVEL"))
```

**Dispatch (A-166, re-sealed 2026-10-21 13:29Z).** Base: `feature/log-level-console-v2` @ **`c95cfb5`** (K10′ = v2 `9cb0fbf` + the stack merge of the gated L1′ `81acc87`, I-126; #55's head,
`MERGEABLE`); L1 @ `81acc87`; no `qa/`, `review/` or `triage/` refs on the fork. **Commits on top of `c95cfb5`, no rewrite.** The Developer: (1) `src/lr_reduction/__init__.py` ← the
candidate above as the starting point — B1–B7 unchanged in behaviour (`getLevelNamesMapping` and `str.isdecimal` are 3.11+, within `requires-python >= 3.11`); no `try`, no blanket
`except`, nothing in the body can raise; (2) `tests/unit/test_log_level_console.py` ← **only** the fixture change: reset the named handler and the package level **before and after**
each test (F1, A-151/I-112); the 25 tests otherwise unchanged and all passing. **RED/GREEN here:** RED = T3/T5/T7 run alone (`-k child_info`, `--lf`) red on the after-only fixture;
GREEN = green alone and whole after the fixture fix; the candidate then passes all 25 unchanged. **§7 rows for v3** (the GREEN body records each with its failing count): `int()`
under a blanket `except` (the human's `a799915` defect — every level name → off: T4/T8 red); `isdigit()` for `isdecimal()` (T5: `'²'`/`'①'` raise or pass wrongly); a second call
re-levelling the old handler instead of replacing it (T6); the fixture reset after-only (T3/T5/T7 run alone red); the import-time call removed (T8). **Gate:** G literal on L1′'s
base — `pixi install --locked`, the lock check, `test-reduction` and `test-launcher` each EXIT 0; expected launcher 10, reduction 168; ruff `--extend-select RUF100` clean (the human's
own `a799915` had I001); `git diff c95cfb5..<tip> --stat` = exactly the two files; bodies with the model trailer, no ledger URL or campaign identifier (upstream-bound); the
Integrator's PASS fast-forwards #55 and its body says what v3 changed (smaller `__init__.py`, same behaviour, the fixture fix in). **Attempt 3 of 3:** a REJECT escalates
(`plans/log-level-console-escalate.md`, the `review/log-level-console-escalate` tag) and the human decides.

**v3 PASS — 2026-10-21 (I-127; attempt 3 of 3; #55 fast-forwarded to `4fb8c05`, `MERGEABLE`/clean).** v3 = `675bd4c` (the fixture resets before and after; RED measured
with each of T3/T5/T7 run alone on the after-only fixture, GREEN after) + `4fb8c05` (`__init__.py` 42 lines, no `try`/`except`; B1–B7 unchanged) on K10′ `c95cfb5`. G 10 + 168,
ruff RUF100 clean, the two-file scope, clean bodies; shell acceptance 2–3 reproduced. **Correct-and-flag on this plan's v3 text:** the candidate's "`str.isdecimal()` is exactly what
`int()` accepts, so neither call can raise" is **false for long strings** — Python 3.11's `int()` refuses more than `sys.get_int_max_str_digits()` = 4300 digits, so a 4301-digit value
made `import lr_reduction` raise (the same class as v1's blocking finding; measured by the Developer and the Integrator). v3 reads a number only when `text.isdecimal() and
len(text) < 10` (no level needs ten digits); longer digit strings take B4's path. **The §7 rows for v3, as measured** (I-127/D-127): `int()` under a blanket `except`
(a799915's shape) → 21 failed; `isdigit` for `isdecimal` → 3; the import-time call removed → 2; the old-handler removal dropped → 4; **the two rows the plan wrote at A-166 were
wrong on v3's source** — "a re-levelled rather than replaced handler → T6" is caught by nothing (v3 replaces the handler each call, so T6 passes either way), and "the after-only
fixture → T3/T5/T7 red" cannot be shown on v3 (same reason); struck. **Unpinned (advisory, not blocking):** the length guard (removed → 25 passed; one T5 case would pin it),
`.strip()` (a padded `" debug\n"` → INFO + warning), `propagate = False`, re-levelling vs replacing. **Behaviour notes vs v2** (D-128): `'+5'`, `'1_0'`, `'+0'`/`'-0'` and ≥10-digit
values now take B4's loud path where v2 accepted them; `__init__.py:24`'s comment and the GREEN body overstate ("isdecimal is exactly what int accepts"; "the behaviour is the
previous one") — reword before upstream. **Follow-up for the human's word (K15 in the queue):** the four pins, the save-and-restore fixture, the comment rewording — small, before
the upstream carry; or the human's edit. No attempt is spent: v3 PASSED.

### v4 — 2026-10-22 (A-200): the human's clarified requirement, the retry cap extended to 4 for this version (`requests/k10-v4-stderr-preserving-console-logging.md`, V1-87/V1-88) — attempt 4 of 4

**Cause: a requirement clarified, not a rejection.** `[human, 2026-10-22 (to the Advisor): "… what if there is a real exception during reduction? It would normally have been
written to stderr (and thus autoreduction would declare the reduction 'failed'). We *want* to keep that behavior … What we *want* is for what used to be print() calls in the
upstream:exp that have been converted to log.*() to be converted *properly* to use a logging level that will *not* go to stderr, rather go to stdout … It does *not* want to suppress
all output to stderr."]` The Advisor measured (V1-87, fresh processes): v3 puts **every** package record at or above INFO on stdout, upstream's own 19 WARNING/ERROR calls included
(`dead_time_correction.py:118`, `LRDirectBeamSort.py:201`, `calculate.py:74`/`:232`, `web_report.py`, `workflow.py`), so records that marked failed or degraded output on stderr
under upstream move to stdout and autoreduction no longer sees them; uncaught exceptions were already right; the docs said "nothing reaches stderr".

**The requirement, testable (the request's table):**

| record | upstream `exp` `c4d20e4` | v4 |
|---|---|---|
| the converted `print()`s (L2's replay of `d313313`: 2 `debug`, 11 `info`, 3 `warning`) | `print()` → stdout | **stdout** (below WARNING, when enabled) |
| upstream's `logger.warning`/`logger.error` (19 calls) | stderr — Python's last-resort handler, bare `%(message)s` (no `basicConfig` anywhere) | **stderr, byte-identical** |
| a caught exception logged with `log.exception` | stderr | **stderr, unchanged** |
| an uncaught exception | traceback on stderr, rc 1 | **unchanged** |

**Verified fact that changes the hand-off's shape (A-200, measured; `scripts/lastresort-probe.py` on the ledger, stdlib only):** the request's shape (1) — "a level filter on the
stdout handler; WARNING and above are left to Python's default, stderr" — **does not work as written.** `Logger.callHandlers` counts a handler as *found* for every handler on
the logger and its ancestors, whether or not its level or filter passes the record (`found += 1` before the level test; Python 3.9 source, unchanged since 3.2), and
`lastResort` runs only when `found == 0`. So a filtered stdout handler alone makes upstream's WARNING/ERROR records **vanish** — stderr empty (the probe: INFO on stdout, nothing on
stderr). With a second handler at WARNING on the same logger, bare `%(message)s`, writing to `sys.stderr`, the stderr output is **byte-identical to the last-resort handler's**
(the probe: `WARN-MSG`/`ERR-MSG` on stderr, as the no-handler run). The design below has two handlers.

**v4 scope — `src/lr_reduction/__init__.py` and `tests/unit/test_log_level_console.py` only, commits on `1fbc900` (no rewrite; #55 fast-forwards at PASS):**
- **B1 (stdout):** the `lr_reduction.console` handler keeps its stream (the `sys.stdout` of the moment, K15's pin), format and level, **and gains a filter `record.levelno <
  logging.WARNING`**: it writes the package's DEBUG/INFO records (the converted prints) and nothing at WARNING or above.
- **B2 (stderr, upstream's last resort reproduced):** a second handler, named `lr_reduction.stderr`, level WARNING, formatter `%(message)s`, whose stream resolves `sys.stderr` **at
  emit time** (as `logging.lastResort`, a `_StderrHandler`, does — a four-line `StreamHandler` subclass with a `stream` property; not the private class), so a swapped or
  redirected stderr is honoured, and so autoreduction's "anything on stderr is a failure" reading is exactly upstream's. `configure_console_logging` removes both named handlers on
  reconfigure; **`NOTSET`/`0` removes both** (upstream's behaviour exactly: the last-resort handler, D-7); `propagate` stays True (D-3) — root has no handlers, so nothing is
  duplicated; a caller's own root handler sees what it would under upstream.
- **B3 (levels):** `LR_REDUCTION_LOG_LEVEL` still sets the package level; at WARNING or above the stdout handler passes nothing and the stderr handler carries the rest —
  upstream's shape; at DEBUG/INFO (the default INFO) the converted prints appear on stdout.
- **B4 (our own notice):** the invalid-value notice (`LR_REDUCTION_LOG_LEVEL=%r is not a level name …; using INFO`) is **logged at INFO**, not WARNING — a configuration notice is
  not a reduction failure and must not put a run on stderr (D-v4-2; v2/v3's "one warning on stdout" becomes "one INFO line on stdout").
- **B5 (docs):** the docstring, the module comment, the `_ACCEPTED` text and the #55 body lose "nothing reaches stderr" and state the table: stdout for the package's records
  below WARNING; WARNING and above on stderr exactly as upstream; uncaught exceptions untouched.
- **B6 (K15's pins kept):** the 35 tests stay green, adjusted only where a second handler is now expected — the name filters (`_console_handlers()` by name sees the stdout one; a
  sibling helper for the stderr one), `_clear` removes both names, `_isolated_package_logger` already saves/restores all handlers; T4's identity/stream pins apply to the stdout
  handler; the module-scoped teardown assertion unchanged.

**Tests (fresh processes, the existing `_fresh_process` helper extended to emit `info`, `warning`, `error`, a caught exception with `log.exception`, and an uncaught one):**
- **T1** default (unset): `info` → stdout only; `warning`/`error`/`log.exception` → **stderr only**, nothing on stdout; the stderr bytes equal a no-handler run's (the last-resort
  format: the bare message; the traceback text for `log.exception`).
- **T2** uncaught exception → traceback on stderr, rc 1, stdout untouched (already true — pinned).
- **T3** `NOTSET`/`0` → the no-handler run byte-for-byte on both streams (`info` dropped, `warning` on stderr bare).
- **T4** `WARNING` → nothing on stdout, `warning`/`error` on stderr bare; `DEBUG` → debug and info on stdout.
- **T5** invalid value → one INFO notice on stdout, stderr empty; the package at INFO.
- **T6 — the must-fails** (each on a copy, restored in a `finally`): the stdout filter removed → T1's warning/error rows red (they appear on stdout); **the stderr handler removed →
  T1's stderr rows red (nothing on stderr — the `found` effect, the finding above)**; the stderr handler's stream bound at configure time → a test that swaps `sys.stderr` after
  configuring sees nothing in the new stream (red); the formatter given a prefix → the byte-equality with the no-handler run red.
- **T7** G at the v4 tip alone on the host (10 + 151 + the new tests; items measured); ruff `--extend-select RUF100` clean; D-83 (no lock change); P2; `git diff --stat 1fbc900 <tip>`
  = the two files.

**Phase 2 — the L2 amendment and the stack re-gate (the human's word "include the L2 amendment … and re-gate the stack"):** one commit on L2‴ `b9efb8f` (PASS I-150) taking
the replay of `d313313`'s three `warning` conversions to `info` — "converted properly", they were `print()`s to stdout: `binary_processing.py:348` ("Cannot process %s because %s
fails to extract"), `binary_processing.py:381` ("Run missing the chopper moderator log value"), `direct_beam_maker.py:213` ("Using 1.0 as scale multiplier because …") — L2⁗; then
L3⁗ = L3‴ `ee4d2f8` + merge of L2⁗, L4⁗ = L4‴ `41a8be4` + merge of L3⁗, each gated (G alone on the host — K19 D-8; P1/P2; P5). **The reference: R-6 = R-5 `fee87c7` + the same
three-line change applied identically** (a new immutable branch `feature/landing-reference-6`, the rule of K17 D-4/K19 D-3 — R-5 carries `d313313`'s `warning` calls through
`exp-review`), so P3 at L3⁗ and L4⁗ `--move` stays exact with K11's `EXCL`; L2⁗'s harness against R-6 (nine scenarios) identical — the change routes three log lines, it touches
no reduction output. The side PRs (#55 after v4, #56, #57, #58, #59) re-checked `MERGEABLE` at the new tips. Upstream: L2 is not yet carried, so no re-push; K10's #55 and the L2
amendment travel separately (the request's default). **Order:** Phase 1 (v4) and Phase 2 (the L2 commit) build in parallel; Phase 2's gates run on gated predecessors only.

**Decisions (v4):**
- **D-v4-1 — two handlers, not one** (the finding above): the stderr handler reproduces the last-resort handler byte-for-byte; the stdout handler is filtered below WARNING.
- **D-v4-2 — our own notices are INFO** (the invalid-value notice); nothing of this package's own goes to stderr unless upstream's code logged it at WARNING or above.
- **D-v4-3 — the converted prints at `info`** (the request's default; the human's word): L2's three `warning` calls → `info`.
- **D-v4-4 — attempt 4 of 4 by the human's word**; a rejection of v4 escalates to the human (no v5 without a word).
- **D-v4-5 — R-6 for the stack's proof**, as every deliberate stack change has had its reference.
- **Expected counts:** the v4 tip 10 + 151 + the new tests; L2⁗ 10 + 318, L3⁗ 801 + 1045, L4⁗ 1528 + 318 (I-150's, unchanged by a log-routing edit).

Sealed against `feature/log-level-console-v2` @ `1fbc900`, L2‴/L3‴/L4‴ `b9efb8f`/`ee4d2f8`/`41a8be4`, R-5 `fee87c7`, upstream `exp` `c4d20e4`; the probe run on this host's
Python 3.9 (the `callHandlers` logic is unchanged in 3.11+, which the gate's environment uses — the Developer re-runs the probe there as T6's second must-fail).
