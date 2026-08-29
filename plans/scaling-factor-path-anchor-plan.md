# Plan: scaling-factor-path-anchor

**Campaign:** `exp-settings-roi` · base `exp` @ `11170ff` · mid-effort
addition 2026-08-29 (human-reported: `pixi run pytest` from the repo root
fails 9 tests on every clone of `exp`, blocking comfortable merging of
PRs #16–#18) · DAG-independent, **stage immediately** — it gates the
human's merge confidence and every future bare-pytest run
**Retry attempt:** 1

Review domains: test-reviewer (**blocking** — bug-fix phase per charter
§5), design-reviewer (advisory).

## Symptom

`pixi run pytest` from the repo root: **9 failed, 98 passed** —
`tests/test_dead_time.py::test_full_reduction` plus 8 in
`tests/test_reduction.py`, all with
`TypeError: cannot unpack non-iterable EventWorkspace object` at
`src/lr_reduction/template.py:385`. Meanwhile `pixi run test-reduction`
(the campaign gate) is green at 107 on the same commit, same clone, same
environment.

## Verified root cause (Analyst, 2026-08-29 — every link checked in source)

Two stacked defects, both **pre-campaign** (identical code at `dccd093`;
the not-found branch dates to the `ce1a3ae` repo reorganization):

1. **cwd-relative fixture path.** `tests/data/template.xml` carries
   `<scaling_factor_file>data/sf_197912_Si_auto.cfg</scaling_factor_file>`
   — resolved against the *current working directory*. The gate task is
   `cd tests/ && pytest …`, where `data/sf_197912_Si_auto.cfg` exists
   (4 `sf_197912*` files tracked under `tests/data/`). Bare
   `pixi run pytest` runs from the repo root, where it does not.
2. **Silent wrong-type error return.** `template.py:74-76`:

   ```
   if not os.path.isfile(scaling_factor_file):
       print("Could not find scaling factor file: %s" % scaling_factor_file)
       return workspace
   ```

   The **single call site in the codebase** (`template.py:385`,
   `a, b, err_a, err_b = scaling_factor(...)`) always unpacks a 4-tuple,
   so this branch can never succeed — it converts a clear
   file-not-found into a baffling TypeError four frames later. The
   captured stdout in the human's transcript shows exactly this pair
   (`Could not find scaling factor file: data/sf_197912_Si_auto.cfg`
   followed by the unpack TypeError).

Answers this establishes: the Integrator's gates were honestly green —
`test-reduction` is the sanctioned command (charter §1, orchestration
§11) and its `cd tests/` makes the relative path resolve; and nothing
here is campaign-introduced — the human's invocation has never been
green on any commit of `exp`.

## Files to change (on `feature/scaling-factor-path-anchor` from `agentic/exp`)

1. `src/lr_reduction/template.py` — two edits:
   - **Anchor the path at read time.** Where the template XML is parsed
     into `ReductionParameters` with a known template path
     (`read_template` / the `from_xml` seam — implementer locates the
     spot where both the template's path and the parameter are in
     scope), resolve a non-absolute `scaling_factor_file` with this
     precedence: absolute → as-given if it exists relative to cwd
     (legacy facility behavior preserved) → relative to the **template
     file's own directory** (makes fixtures invocation-independent) →
     leave as-given (the loud failure below reports what was tried).
     Facility templates use absolute `/SNS/...` paths and are
     untouched; only the relative-and-not-in-cwd case gains the
     template-dir fallback.
   - **Fail loud.** The `template.py:74-76` branch raises
     `FileNotFoundError` naming the path (and, if easily threaded, the
     candidates tried) instead of `return workspace`. Zero behavior
     change for any working path — the branch never returned usefully
     (single 4-tuple-unpacking call site, verified).
2. `tests/` — the RED-first seed:
   - `test_scaling_factor_missing_file_raises`: call
     `template.scaling_factor("/nonexistent/sf.cfg", <any loaded ws or
     stub>)` … if a workspace is needed, reuse the cheapest loaded
     fixture already in the suite; assert `FileNotFoundError` (RED: today
     it returns the workspace).
   - `test_reduction_cwd_independent`: `monkeypatch.chdir(tmp_path)`
     around ONE existing fast scaling-factor-exercising case (pick the
     quickest of the 9 — e.g. a single `test_q_summing_as_option`
     parametrization refactored to a helper, or a minimal
     `process_from_template_ws` invocation) and assert it succeeds
     (RED today with the same TypeError the human saw).
   Both tests must fail before the src edits and pass after; the commit
   bodies enumerate the observed RED strings.

**Strip/scope guards:** do not touch the 9 failing tests themselves (they
are correct — the product code was wrong); do not "fix" by making the
gate command the only blessed invocation or by documenting-around; no
`pixi.lock` changes (amendment 14 caveat applies — restore any re-stamp,
never commit a non-v6 lock).

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Bare `pytest` from repo root (the human's case, common) | today: 9 × TypeError | template-dir anchoring; `test_reduction_cwd_independent` |
| Gate invocation `cd tests/` (common) | must stay green | as-given-cwd precedence preserved ahead of the fallback |
| Facility template with absolute `/SNS/...` path (common, production) | untouched by design | absolute short-circuits first |
| Facility/legacy template with cwd-correct relative path (edge) | must stay working | as-given-cwd checked before template-dir fallback |
| sf file genuinely missing (edge) | today: print + TypeError 4 frames later | `FileNotFoundError` at the source, path(s) named |
| Some unknown caller relied on the workspace return (pathological) | caller search | verified: exactly one call site, always unpacks — none can exist |
| IDE / `pytest tests/test_reduction.py -k …` from arbitrary cwd (edge) | same class as the human's case | same fix; the cwd-independence test pins it |

## Acceptance criteria

- **The human's exact command**: `pixi run pytest` from the repo root →
  **107 passed** (this is the criterion that unblocks the #16–#18
  merges).
- `pixi run test-reduction` green (gate unchanged); `pixi run
  test-launcher` green.
- Both new tests demonstrably RED before the src edits (strings in the
  commit body), green after; pre-commit clean; diff touches exactly
  `src/lr_reduction/template.py` + the new/edited test file(s).
- Draft PR body: states the deploy consequence (charter §7), the
  pre-campaign provenance (`ce1a3ae`-era, identical at `dccd093`), and
  recommends the human merge THIS PR first, then verify their
  invocation, then merge #16–#18 at leisure.
