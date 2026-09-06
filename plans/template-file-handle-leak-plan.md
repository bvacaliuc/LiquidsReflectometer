# Plan: template-file-handle-leak

**Campaign:** `exp-settings-roi` · base `exp` @ `308a020` (#24/#25 merged) ·
mid-effort addition 2026-09-06, human-approved (from
`todo-template-file-handle-leak.md`; staged first of the two bug-fix slugs)
· DAG-independent
**Retry attempt:** 1

Review domains: test-reviewer (advisory — product-code hygiene, no behavior
change).

## Symptom

`read_template` opens the template file and returns without closing it —
`fd = open(template_file, "r")` at **`src/lr_reduction/template.py:66`** and,
identically, at the fork copy **`src/lr_reduction/new_reduction_from_template.py:466`**
(both verified present on `agentic/exp` @ `308a020`). One
`pixi run test-reduction` leaked 46 unclosed-file ResourceWarnings on
`tests/data/template.xml` alone (Developer measurement under the
warnings-as-errors probe, `todo-*`).

## Root cause + the honest verification caveat

```python
def read_template(template_file: str, sequence_number: int) -> ReductionParameters:
    fd = open(template_file, "r")      # never closed
    xml_str = fd.read()
    ...
    return data_set
```

**Why a pure-unit RED is not reliably constructible — and why that IS the
lesson.** In CPython the local `fd`'s refcount hits zero at `return`, so the
handle *is* usually closed promptly; a `.closed`-after-return assertion
would pass on the buggy code. The leak only bites when a frame is kept
alive (an exception's traceback holding the frame — exactly the failing-test
context where the 46 warnings appeared), under PyPy, or when the object is
captured. So the deterministic evidence is the **suite-level
ResourceWarning count**, not a unit assertion — do not fake a unit RED that
CPython masks; measure the real signal.

## Files to change (on `feature/template-file-handle-leak` from `agentic/exp`)

1. `src/lr_reduction/template.py:66` and
   `src/lr_reduction/new_reduction_from_template.py:466` — each becomes
   `with open(template_file, "r") as fd:` with the read re-indented under it.
   Behavior-neutral: the file is read fully before use at both sites. Keep
   the two in step (the fork copy carries the standing unification TODO).
2. `tests/` — verification, primary form is the measurement:
   - **Primary (deterministic at suite scope):** run
     `pixi run python -m pytest tests/ -W error::ResourceWarning
     -p no:cacheprovider` (or a scoped subset that calls `read_template`),
     record the unclosed-`template*.xml` ResourceWarning count **before**
     the edit (expect the reported ~46+9+8+2+2) and **0 after**, in the
     commit body.
   - **Regression guard (unit, keeps the `with` from being reverted):** a
     test that wraps `builtins.open` to capture the returned handle, calls
     `read_template(<a fixture template>, 7)`, forces `gc.collect()`, and
     asserts the captured handle `.closed is True` **while also keeping a
     reference to a raised frame** — i.e. call it inside a
     `try/except`-captured path so the CPython-masking is defeated. If a
     reliable frame-capture form proves fiddly, fall back to asserting the
     source uses a `with` via `inspect.getsource` (brittle but honest as a
     guard, not as the RED). Implementer's judgment; the suite measurement
     above is the load-bearing proof either way.

**Scope guards:** the two `open` sites only; do **not** fold in the parked
warnings-as-errors flip (that is its own decision, gated on the residual
Runtime/Deprecation counts once this leak is gone — sequence in the `todo-*`).
No `pixi.lock` change (amendment 14: restore any hook re-stamp, keep
`version: 6`).

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Handle leaks under a live traceback (the 46-warning reality) | suite ResourceWarning count | `with` closes deterministically regardless of frame lifetime |
| Fork copy left un-fixed, drifts from template.py | both sites named; grep at seal | fix both in one commit |
| Re-indent drops a line of the read/parse | `test-reduction` parses templates | full suite green is the check |
| pixi.lock re-stamp | first line ≠ `version: 6` | restore, never commit |

## Acceptance criteria

- Both sites use `with open(...)`; `git grep -n 'fd = open(template_file'`
  returns nothing.
- Suite ResourceWarning count for `template*.xml` drops to **0**
  (before/after in the commit body); `pixi run test-reduction` +
  `test-launcher` green; pre-commit clean; diff is the two `src/` files +
  the guard test; no `pixi.lock` change.
- Draft PR body: product code that runs at the facility on every reduction;
  behavior-neutral; unblocks the parked warnings-as-errors flip (re-measure
  the flip's residual after this lands — next todo step).
