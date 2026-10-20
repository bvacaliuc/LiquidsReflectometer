# todo — log-level-console v1 @ 7041087: REJECTED (attempt 1 of 3) — one blocking finding: a level value can make `import lr_reduction` raise

Integrator gate, 2026-10-20. Everything else in the gate is green: `pixi install --locked` rc 0, `scripts/pixi_lock_check.sh` rc 0,
`pixi run test-reduction` → launcher 10 passed, reduction 188 passed (L1's 172 + the 16 new), rc 0, `pixi.lock` unchanged; scope
`git diff --stat c5ef58d 7041087` = exactly `src/lr_reduction/__init__.py` and `tests/unit/test_log_level_console.py`; acceptance 2–3
reproduced (unset → INFO dropped and `w` printed once by lastResort; `INFO` → `INFO lr_reduction.x: ping` on stderr; Mantid not
imported). Reviews: design and test, neither marked blocking — the finding below is the gate's (declared behaviour B4 / decision D-4,
and demonstrated reachable harm).

## B1 (blocking) — a value that `str.isdigit()` accepts and `int()` rejects raises at import

**Reproduction** (worktree at 7041087, `pixi run`):

```
$ LR_REDUCTION_LOG_LEVEL='²' python -c "import lr_reduction"
ValueError: invalid literal for int() with base 10: '²'          # exit 1, raised from src/lr_reduction/__init__.py:29
```

Also `'①'` (the test reviewer's run). `src/lr_reduction/__init__.py:28-29`: `if text.isdigit(): level = int(text)`. `str.isdigit()`
is True for superscripts and circled digits; `int()` accepts only Unicode decimal digits (`Nd`), so it raises. Because the call runs at
import (B7), every consumer fails to import — the launcher, the reduce scripts, a spawned worker, and the test suite's collection.
This is the case D-4 rules out ("raise at import breaks every consumer for a typo") and B4 covers ("any other string → INFO + one
WARNING; never silent, never off").

**Fix — behaviour, not code (amendment 18).** The type domain is `str` (an environment value) or `None`. The domain this check
governs: the strings that are not a level name. Required behaviour: **every `str` that is neither blank, nor a level name, nor
something `int()` accepts takes B4's invalid path — handler at INFO plus exactly one WARNING — and nothing in
`configure_console_logging` raises for any `str` input.** Strings `int()` *does* accept must keep working: `'10'` → 10 and the
full-width `'１０'` → 10 parse today, measured. The reproduction covered `'²'` (superscript) and `'①'` (circled). **The guard must vary
the dimension the fix freezes:** a parametrised case over at least `'²'`, `'①'` (expect INFO + one WARNING naming the value) and
`'１０'` (expect 10), so a fix that merely special-cases the superscript cannot pass. Either `isdecimal()`, or `try: int(text)
except ValueError:` falling through to the name lookup, meets this; which one is yours.

## Recommended in the same v2 (advisory — not reasons for this rejection; the PR body will carry whatever is left)

- **R2: T6 does not pin the handler's level.** Move `handler.setLevel(level)` inside `if handler is None:` and all 16 tests still pass
  (test reviewer, verified), yet after `("INFO")` then `("DEBUG")` the handler stays at 20 and DEBUG records are silently dropped — B5's
  "updates its level and the logger's". One line after `test_log_level_console.py:91`: `assert _console_handlers()[0].level == logging.DEBUG`.
- **R3: §7's root-logger row is not caught by T9**, as your GREEN body says. The cause is the fixture: it removes the named handler
  only from `lr_reduction`, so under the mutation the handler leaks on root across tests, bound to an earlier capture stream. Removing
  the named handler from `logging.getLogger()` as well in `reset()` makes T9 catch it (test reviewer, verified: 9 failed, T9 among them).
- **R4: §7's unset-at-WARNING row is not caught by T8's unset case.** INFO is dropped at WARNING too. Have the child also call
  `warning('w')`, and assert the unset stderr is exactly `"w\n"` (lastResort's bare form, not `WARNING lr_reduction.probe: w`): it
  catches the mutation (verified) and pins "today's behaviour" in the one place lastResort is observable (under pytest, root carries
  handlers, so lastResort never runs in-process).
- **Not yours to decide alone — `'0'` / `'NOTSET'`** are accepted silently and show *less* than DEBUG (the logger at NOTSET defers to
  root's WARNING; measured: INFO dropped, rc 0, no message). The plan's B3 ("whatever `logging` knows") admits them; D-4's intent
  ("never silent") does not. The Analyst's call: treat level ≤ 0 as invalid (INFO + warning), or clamp to 1. If the Analyst does not
  amend the plan, leave the behaviour as it is.

## History hygiene (the branch is upstream-bound)

This `todo.md` commit and its later "clear resolved todo.md" are campaign bookkeeping. Rebuilding v2 from `c5ef58d` (RED + GREEN again,
as you did at D-108) keeps both out of the branch that goes upstream as `exp-log-level-console`; stacking on this commit works too, but
then the Integrator clears the todo before the PR and both commits stay in history.
