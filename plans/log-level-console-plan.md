# Plan: `log-level-console` — when `LR_REDUCTION_LOG_LEVEL` is set, the package's Python logging reaches the console (stderr) at that level; unset, nothing changes

**Campaign:** `exp-review-fixes` · **Leaf:** `log-level-console` (refs `triage/log-level-console`, `feature/log-level-console`, `qa/log-level-console`; K10 in `dispatch-queue.md`) ·
**Status:** **DISPATCHED** — v1 (attempt 1 of N = 3), authored and dispatched 2026-10-20 (A-148) on the human's word of 2026-10-20 (verbatim in V1-64, charter §3) ·
**Base:** **upstream `exp` @ `8971999`** (= the fork's `exp` since the human's reset, I-105; the stack's base) — cut `feature/log-level-console` from `8971999`, **not** from
`exp-review` and **not** from a landing layer: the two files are touched by no layer (`git diff 8971999 <L1..L4,exp-review> -- src/lr_reduction/__init__.py` empty on all five, V1-64),
so the branch is file-disjoint from the stack and can land in any order (§10 D-2) · **PR target:** the fork's `exp`, **draft**, opened by the Integrator at PASS (as #54 for L1);
the human carries it to upstream as `exp-log-level-console` (V1-63's convention) · **Reviews (charter §5):** design, test (block); numerical-diagnostics and ui-aspects n/a (no
numbers, no Qt) · **Gate:** G = `pixi run test-reduction` + `pixi run test-launcher` green at the tip, plus the new tests; no landing proof applies (this is not a replay).

## Declared scope

Campaign: exp-review-fixes

**In:** one public function in `src/lr_reduction/__init__.py`, `configure_console_logging(value: str | None) -> logging.Handler | None`, called once at import with
`os.environ.get("LR_REDUCTION_LOG_LEVEL")`; one new test module `tests/unit/test_log_level_console.py`. **Out:** every `print(` in `src/` (157) and `launcher/` (44);
Mantid's own logger and its console level; the autoreduce path (`reduce_REF_L.py`); the launcher's code (it imports the package in-process, so it inherits the switch
without a change); exporting the variable for the scientists in `nr_launcher.sh` or a deploy wrapper (a deploy choice — the `shared-deploy` slug, charter D-9); any
`logging.basicConfig` or root-logger change; the landing layers' content (§10 D-2 names the two ways the layers can carry it, both after PASS).

## 1. Request and symptom

`[human, 2026-10-20 (to the Advisor, verbatim in V1-64): "many print() diagnostics have been distributed to log.info()/log.warning() … 'swallowed by the UI'. Would it be possible
to make a variation on feature/landing-l2-reduction before I push it upstream (and without damaging the stack plan) to allow a configuration (perhaps simply via
environment-variable injection) to make log levels also emitted on the console? Default/Unset can remain off as it is now."]`

Correct-and-flag (V1-64): "many" is one commit — `d313313` (fork #46 `time-slicing-reconcile`, its T9 convention commit, in L2) turned 17 `print` into 16 `logger.*` calls
(11 INFO, 2 DEBUG, 3 WARNING) in `new_reduction_time_resolved.py`, `direct_beam_maker.py`, `binary_processing.py`. Nothing in the UI captures anything: **no handler is
configured anywhere in the tree** (no `basicConfig`, `StreamHandler` or `addHandler` outside tests at `3ea92cf`, re-checked here; `import mantid.simpleapi` installs none), so
Python's `lastResort` handler writes WARNING and above to stderr and drops INFO/DEBUG. A `print` used to reach the launcher's terminal because both tabs import those modules
in-process (`launcher/apps/direct_beam.py:41`, `time_resolved.py:34`). The ask is therefore: an opt-in console handler for the package's loggers, off when unset.

## 2. Verified facts at upstream `exp` @ `8971999` (2026-10-20 15:3xZ; V1-64's measurements, re-checked in this clone)

- `src/lr_reduction/__init__.py` is four lines: the `__version__` import with its `ImportError` fallback. No `os.environ`/`getenv` read exists anywhere in `src/` or `launcher/`;
  `LR_REDUCTION_LOG_LEVEL` is the package's first environment switch. `requires-python = ">=3.11"` (`str | None` is fine).
- Every module logger is `logging.getLogger(__name__)` (`lr_reduction.<module>`), so all of them are children of the `lr_reduction` logger and propagate to it: 39 logging
  calls in `src/` at L2's tip, the 16 of `d313313` among them; the rest (upstream's 19 + L1's 2) are WARNING/ERROR in `web_report.py`, `template.py`, `scaling_factors/`,
  `data_info.py`, `dead_time_correction.py`.
- `Logger.callHandlers` uses `lastResort` only when **no handler is found along the propagation chain**; a handler on `lr_reduction` is found for every child record, so
  attaching one does not duplicate the WARNINGs that `lastResort` prints today (§5 row 7 tests it).
- The reduction suite runs as `cd tests/ && python -m pytest …` (`pyproject.toml:180`); unit tests live in `tests/unit/`. Importing `lr_reduction` does not import Mantid.
- Multiprocessing: a child started by `spawn` re-imports the package and re-reads the environment it inherited; one started by `fork` inherits the configured handler. Either
  way the child's behaviour equals the parent's.

## 3. Design — behaviours (types first: amendment 18)

The input is **`str | None`** (an environment value is a `str`; absent is `None`). `value` is stripped; `None` or an empty/whitespace string is **unset**.

| # | Behaviour | Type and value |
|---|---|---|
| B1 | **Unset → no-op.** `configure_console_logging(None)` and `("")` return `None`, attach nothing, change no level. Today's behaviour byte-for-byte (`lastResort`: WARNING+ to stderr, INFO/DEBUG dropped). | `None` |
| B2 | **Set → one handler.** A `logging.StreamHandler(sys.stderr)` named `lr_reduction.console`, formatter `%(levelname)s %(name)s: %(message)s`, attached to `logging.getLogger("lr_reduction")`; that logger's level set to the parsed level; the handler returned. The package logger keeps `propagate = True` (§10 D-3). | `logging.StreamHandler` |
| B3 | **Level parsing.** A level **name** (case-insensitive, whatever `logging` knows: `DEBUG`, `INFO`, `WARNING`/`WARN`, `ERROR`, `CRITICAL`/`FATAL`) or a **decimal integer** (`"10"` → 10). | `int` |
| B4 | **Invalid → INFO, loudly.** Any other string: the handler is attached at **INFO** and one WARNING record goes through the package logger naming the value and the accepted forms (`LR_REDUCTION_LOG_LEVEL='verbose' is not a level name (DEBUG, INFO, WARNING, ERROR, CRITICAL, or an integer); using INFO`). Never silent, never off (§10 D-4). | `logging.INFO` + 1 WARNING |
| B5 | **Idempotent.** A second call with a value finds the handler by name and updates its level and the logger's; never a second handler (reload, double import, an explicit call from the launcher later). A second call with `None` after a set is a no-op (it does not detach). | one handler |
| B6 | **Scope.** Only `lr_reduction.*` loggers print through it (`logging.getLogger("other").info(...)` stays silent); no root-logger change; Mantid's logger untouched. | — |
| B7 | **Import time.** `__init__.py` calls `configure_console_logging(os.environ.get("LR_REDUCTION_LOG_LEVEL"))` once at import, so every consumer — the launcher's in-process tabs, a script, autoreduce's Python side — gets it by setting the variable before Python starts; the stream is `sys.stderr` as it is at that moment. | — |

Why the package logger and not `basicConfig`: `basicConfig` configures root — matplotlib, Qt bindings and every other library would start printing; the package logger is the
narrowest handle that covers all 39 existing calls (and the 13 the human means) with no other change.

## 4. Files to change

| File | Change |
|---|---|
| `src/lr_reduction/__init__.py` | `import logging, os, sys`; `configure_console_logging(value)` per §3 (about 25 lines; `_HANDLER_NAME = "lr_reduction.console"`, `_FORMAT = "%(levelname)s %(name)s: %(message)s"`); the import-time call after the `__version__` block. Keep the `__version__` block as is. |
| `tests/unit/test_log_level_console.py` | new; §6. A fixture detaches `lr_reduction.console` and resets the package logger's level to `NOTSET` after each test. |

No other file. No new dependency. No `.github/` change (D-2 of the group plan is untouched by construction).

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: variable unset | nothing attached; INFO/DEBUG dropped; WARNING+ via `lastResort` as today | T1, T8 (unset case) |
| 2 | common: `INFO` | the 11 INFO lines of `d313313` and every `lr_reduction.*` INFO+ record on stderr as `INFO lr_reduction.x: …` | T2, T3, T8 |
| 3 | common: `DEBUG` | the 2 DEBUG lines too | T4 |
| 4 | common: `WARNING` | warnings only, formatted; no change in what is shown, only in form | T4, T7 |
| 5 | edge: empty / whitespace / lower case / integer / `WARN` | unset / unset / `INFO` / 10 / 30 | T1, T4 |
| 6 | edge: called twice, or the package re-imported | one handler, the later level wins | T5-idempotent (T6) |
| 7 | edge: a WARNING with the handler attached | printed **once** (lastResort not used) | T7 |
| 8 | pathological: `verbose` (invalid) | attached at INFO + one WARNING naming the accepted forms; nothing silent | T5 |
| 9 | pathological: the host application configures the root logger too | records print twice (ours + root's) — loud and visible, not auto-resolved (§10 D-3) | documented, not tested |
| 10 | pathological: a `spawn`ed worker (`binary_processing` multiprocessing) | the child re-reads the inherited variable and prints the same way | §2 fact; not tested (process-start method is the host's) |
| 11 | pathological: stdout captured by a tool | nothing on stdout — the handler writes stderr only | T3 |
| 12 | out of scope: Mantid `logger.information/notice` lines | unchanged (Mantid's console level) | — |

## 6. Red-Green TDD seed (`tests/unit/test_log_level_console.py`; the Developer writes these first, sees them fail on the base, then implements)

- **T1** `test_unset_or_blank_attaches_nothing`: `configure_console_logging(None)`, `("")`, `("  ")` each return `None`; `logging.getLogger("lr_reduction")` has no handler named `lr_reduction.console`; its level is `NOTSET`.
- **T2** `test_set_attaches_one_stderr_handler_at_the_level`: `("INFO")` returns a `StreamHandler` named `lr_reduction.console`, `stream is sys.stderr`, formatter `_fmt == "%(levelname)s %(name)s: %(message)s"`, the package logger's level `INFO`.
- **T3** `test_child_logger_info_reaches_stderr_only` (`capsys`): configure `INFO` inside the test; `logging.getLogger("lr_reduction.unit_probe").info("ping")` → stderr contains exactly the line `INFO lr_reduction.unit_probe: ping`; stdout is empty.
- **T4** `test_level_names_and_integers` (parametrised): `"debug"`→10, `"WARNING"`→30, `"WARN"`→30, `"10"`→10, `"error"`→40.
- **T5** `test_invalid_value_uses_info_and_warns_once` (`capsys`): `("verbose")` → level `INFO`; stderr has one `WARNING lr_reduction: …'verbose'…` line naming `DEBUG, INFO, WARNING, ERROR, CRITICAL` and `integer`.
- **T6** `test_second_call_updates_the_level_without_a_second_handler`: `("INFO")` then `("DEBUG")` → exactly one handler named `lr_reduction.console`; level `DEBUG`; then `(None)` → still one handler (no detach).
- **T7** `test_a_warning_is_printed_once_not_twice` (`capsys`): with `INFO` configured, `logging.getLogger("lr_reduction.unit_probe").warning("w")` → stderr contains `WARNING lr_reduction.unit_probe: w` exactly once.
- **T8** `test_import_time_switch_in_a_fresh_process` (subprocess, `sys.executable -c "import logging, lr_reduction; logging.getLogger('lr_reduction.probe').info('ping')"`): with `LR_REDUCTION_LOG_LEVEL=INFO` in the child's environment → returncode 0 and stderr contains `INFO lr_reduction.probe: ping`; with the variable removed from the environment → returncode 0 and stderr empty.
- **T9** `test_other_packages_are_untouched` (`capsys`): with `INFO` configured, `logging.getLogger("not_lr_reduction").info("x")` prints nothing (root has no handler; `lastResort` drops INFO).

RED on the base: T1–T7, T9 fail with `AttributeError`/`ImportError` (no `configure_console_logging`); T8's set case fails (stderr empty). GREEN after §4.

## 7. Mutate-once gate (the Developer's commit bodies record each mutation and its `<test> -> N failed`)

| Mutation | Must be caught by |
|---|---|
| remove the import-time call | T8 (set case) |
| attach the handler to the root logger instead of `lr_reduction` | T2 (not on the package logger), T9 (`not_lr_reduction` prints) |
| drop the by-name idempotency guard | T6 (two handlers) |
| invalid value → WARNING silently (or raise) | T5 |
| formatter `%(message)s` only, or stream `sys.stdout` | T3 |
| unset path attaches at WARNING anyway | T1, T8 (unset case) |
| level set on the handler only, not on the logger (INFO records never created) | T3 (nothing on stderr) |

## 8. Acceptance criteria

1. G green at the tip: `pixi run test-reduction` (the new 9 tests included) and `pixi run test-launcher`, both EXIT 0, counts ≥ the base's.
2. Unset: `python -c "import logging, lr_reduction; logging.getLogger('lr_reduction.x').info('ping')"` prints nothing; `…warning('w')` prints `w` once via `lastResort` (today's behaviour).
3. `LR_REDUCTION_LOG_LEVEL=INFO python -c …info('ping')` prints `INFO lr_reduction.x: ping` on stderr, nothing on stdout; `…=DEBUG` adds the DEBUG lines; `…=verbose` prints the one WARNING and then behaves as INFO.
4. `git diff 8971999..<tip> --stat` names exactly the two files of §4; no new dependency in `pyproject.toml`/`pixi.lock`; no `.github/` change.
5. The two commits (RED, GREEN) carry the model trailer; the GREEN body records the §7 mutations with their failing counts; no ledger URL or campaign identifier in bodies (the branch is upstream-bound).
6. Design and test reviews without a blocking finding; the Integrator's draft PR on the fork `--base exp`.

## 9. Learnings relied on

- V1-64's measurement (the mechanism and the counts) — the whole §1/§2; `plans/stratified-landing-plan.md` D-2 (`.github/` excluded) and its base `8971999` (the stack's base,
  the same here so the result lands anywhere); `scripts/landing-sanitize-check.sh` accepts `upstream base merge` provenance (relevant to §10 D-2 (i)'s follow-up);
  `plans/landing-l2-reduction-plan.md` (the P1 purity proof, which (ii) extends by a declared exception).

## 10. Assumptions and decisions (defaults in force unless the human says otherwise)

- **D-1 — the variable's name:** `LR_REDUCTION_LOG_LEVEL` (the Advisor's; no other environment switch exists in the package). A rename before the upstream PR is one line.
- **D-2 — where it lands (the human's; default (i); (ii) is additive, not instead):** the branch is file-disjoint from every layer, so after PASS:
  **(i) standalone — default:** the Integrator's draft PR on the fork `--base exp`; the human carries it to upstream as `exp-log-level-console` and merges it there; each layer
  picks it up at its next upstream base merge (a merge commit, provenance `upstream base merge`, which the sanitize check already accepts); L2's reviewers' deployment
  (`compare-versions.sh exp exp-landing-l2-reduction`) shows the diagnostics only once L2 has merged that `exp`. The Advisor's recommendation: no re-stack, no re-gate, no
  change to any layer's "replay of …" claim.
  **(ii) onto L2 now — on the human's word ("cherry-pick onto L2"):** the Developer cherry-picks the two gated commits onto `feature/landing-l2-reduction` (one non-replay
  change, stated in #51's body and declared as a P1 exception for the two files), `feature/landing-l3-launcher` merges L2's new tip and `feature/landing-l4-model-move` merges
  L3's (two merge commits, no rewriting; #51–#53 follow their heads); the Integrator re-gates L2 (G + the proofs with the exception) and checks L3/L4 by their merge checks
  (§5a); the human pushes `exp-landing-l2-reduction`. This is the immediate route to "before I push it upstream"; (i) alone waits on upstream's merge. The word can come at
  any time after PASS; the build does not change.
- **D-3 — propagation:** the package logger keeps `propagate = True` (library convention: do not cut a host application off from the records). The only cost is §5 row 9, loud.
- **D-4 — an invalid value:** attach at INFO and warn once, rather than ignore (silent, defeats the user's intent) or raise at import (breaks every consumer for a typo).
- **D-5 — not in this slug:** turning the switch on by default for the scientists (an `export` in `nr_launcher.sh` or the deploy wrapper — the `shared-deploy` slug, D-9);
  a GUI setting; converting the remaining `print` calls.

## Revision history

- **v1 — 2026-10-20 (A-148):** authored and dispatched on the human's word (V1-64). Sealed against upstream `exp` @ `8971999` (= the fork's `exp`).
