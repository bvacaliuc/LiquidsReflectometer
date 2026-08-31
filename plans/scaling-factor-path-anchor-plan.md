# Plan: scaling-factor-path-anchor

**Campaign:** `exp-settings-roi` · base `exp` @ `11170ff` · mid-effort
addition 2026-08-29 (human-reported: `pixi run pytest` from the repo root
fails 9 tests on every clone of `exp`, blocking comfortable merging of
PRs #16–#18) · DAG-independent, **stage immediately** — it gates the
human's merge confidence and every future bare-pytest run
**Retry attempt:** 3 (final — N=3; the next rejection escalates)

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

## Revision history

### v2 — 2026-08-30 (after v1 rejection; todo.md @ `aac75a9`)

The fix core is RATIFIED by the gate (both halves red-green against the
structural blindness; the raise-over-`1,0,0,0` call verified correct —
the tidy alternative silently produces unscaled-but-plausible R(Q);
blast radius traced clean). The rejection is about verification
honesty, and **one finding revises this plan's own acceptance
criterion and root-cause statement, owned here**: v1's "bare pytest →
107 passed" was satisfiable *accidentally* — `test_reduction.py:230`
(`test_reduce_functional_bck`) does an **unrestored `os.chdir` into
`tests/`**, so every later test inherits the gate's cwd regardless of
invocation. That leak is also the missing half of the original
root-cause: the nine failures are exactly the sf-path tests defined
BEFORE line 229 (1 in test_dead_time + 8 in test_reduction, with the
×4 parametrization), while the two sf-tests after it passed. The
Integrator also corrected its own first "109 passed" report in the
same document — both sides of this cycle practiced the
stated-vs-measured discipline. Advisory 1 matters most: v1's upward
anchoring walk can silently bind a same-named sf file the template
author never declared — the *same* silent-wrong-number hazard the
raise half closes, re-opened by the fallback. v2 removes the walk.

## v2 fixes (the gate's order, plus the walk removal)

1. **Fix the leak, then measure honestly**: `test_reduction.py:230`
   restores cwd (`monkeypatch.chdir(...)` — pytest restores
   automatically — or `try/finally os.chdir(old)`), then re-run bare
   `pytest` from the repo root and state the REAL number in the commit
   body before fixing anything it surfaces.
2. **Anchoring = the template's own directory, exactly — no upward
   walk.** Delete `_SCALING_FACTOR_ANCHOR_DEPTH` and the parent
   traversal; precedence stays absolute → as-given-cwd →
   `dirname(template_path)` → raise listing all candidates tried. This
   kills the silent wrong-file binding (advisory 1's probe found a
   stale same-named cfg two levels up in an IPTS-shaped layout), the
   depth off-by-one, and most of B2's decoy surface in one stroke.
3. **Make the tests pin the feature (B2, B3)**:
   - the cwd-independence test asserts the *precondition* (the fixture
     template still declares a non-absolute path) and the *identity*
     (`os.path.samefile(resolved, "tests/data/sf_197912_Si_auto.cfg")`),
     not bare `isfile`;
   - a precedence test with decoys at BOTH the cwd-relative and the
     template-dir locations asserts as-given-cwd wins (deleting
     as-given-first must go red);
   - keep the missing-file raise test.
4. **Auditability (advisories 1–3, adopted)**: when the winning
   candidate differs from the declared string, `logger.notice` both
   (declared → resolved); record the resolved path in the output
   metadata (`meta_data["scaling_factor_file"]`); add a
   `logger.warning` on the pre-existing silent no-match
   `return 1, 0, 0, 0` at `template.py:207` (same
   plausible-unscaled-R(Q) axis; log only — behavior unchanged).
5. **Reader parity (advisory 5)**: apply the same anchoring call in
   `new_reduction_from_template.py:460`'s forked `read_template` (one
   line; the fork's unification TODO stays parked — a refactor does not
   ride a bug-fix retry).
6. **Residual cwd-relative sites — fixed, not renegotiated**: the
   gate's enumerated list (reads `test_time_resolved.py:19-20,56-57`,
   `test_scaling_factors_workflow.py:72,91,119,147,176`; writes via
   `output.py:185` at `test_reduction.py:370,406`,
   `test_time_resolved.py:18,55`) — each the same one-line
   `template_dir`/`tmp_path` substitution already applied once at
   `test_reduction.py:159`. This makes the acceptance criterion honest
   rather than narrower.
7. **PR-body notes**: the `time_resolved.py:257/:374` bare excepts
   swallow the new raise into a print (pre-existing; fail-loud is not
   global); the `/tmp` cross-clone race hit its 6th occurrence at this
   gate (parked slug `test-tmp-isolation` awaits the human's nod).

## v2 acceptance criteria (supersede v1's)

- `test_reduction.py` leaks no cwd change (run any later test alone
  from the root: green).
- Bare `pixi run pytest` from the repo root: **all green, honestly** —
  and spot-checks the pollution can no longer mask:
  `pytest tests/test_scaling_factors_workflow.py` and
  `pytest tests/test_time_resolved.py` each green from the root.
- `pixi run test-reduction` and `test-launcher` green as before;
  pre-commit clean; no `pixi.lock` changes.
- Each blocking finding's mutation goes red: fixture absolutized +
  anchoring deleted → red; as-given-first deleted → red.

### v3 — 2026-08-31 (after v2 rejection; todo.md @ `6c34cd7`; FINAL retry)

v2 is ratified in full by the gate: all v1 findings closed
red-on-revert (six mutations), all six advisories taken, the cwd leak's
11 masked tests fixed with checked arithmetic — and the fixture change
made the anchoring load-bearing under `cd tests/` too, so deleting the
fix now reds the campaign gate itself (the gate's structural blindness
to this class is retired; say so in the PR). One blocking finding —
**B1's species, one cycle later**: `tests/test_time_resolved.py` never
sets Mantid's `default.facility` (`amend_config` sets it only when
`new_config` is passed; these tests pass `data_dir` only), so it is
green only when co-collected after a module that sets it. The v2
spot-check ran the two files in ONE invocation and reported the
combined green as standalone — the exact accident class this slug
exists to eliminate. Also reconciled: the gate's closing note on the
`/tmp` write side is already resolved — the human merged PR #21
(`test-tmp-isolation`) after this review was written; `exp` @ `633950c`
carries it.

## v3 fixes (final retry — the gate's order)

1. **B4**: session-scoped autouse fixture in `tests/conftest.py`
   setting `mtd_api.config["default.facility"] = "SNS"` and
   `["default.instrument"] = "REF_L"` (hoisted, per the gate, so no
   module can be silently coupled again — reviewer-verified: 2 passed
   alone from the root). Commit/PR body states the spot-checks as
   SEPARATE invocations with each file's standalone number.
2. **Close the class, not the instance** (both reviewer-verified):
   delete the now-vestigial `chdir` at `tests/test_reduction.py:235`
   (every path in that test is absolute; 1 passed alone from root with
   the line gone — the suite then contains zero cwd mutations), and add
   the four-line `_no_cwd_leak` autouse fixture (before/after
   `os.getcwd()` assert) so a reintroduced leak is caught by the next
   test in the file rather than a human months later.
3. **Guard-file hygiene** (`tests/test_template_paths.py`): refresh the
   stale docstring (pre-v2 fixture path; the "gate structurally cannot
   see" claim v2 made false; "Both tests" → four); precondition uses
   `re.findall` over all `<scaling_factor_file>` occurrences asserting
   none absolute (the current `re.search` reads sequence 1 while the
   test exercises sequence 7); route the two private
   `_resolve_scaling_factor_file` tests through `read_template` so the
   public seam is what is pinned.
4. **Optional — drop first if anything wobbles**: fix the seventh
   template's dead `test/data/sf_186529_Si_auto.cfg` path in
   `tests/data/template_with_instrument_settings.xml` (last
   old-convention template; now emits the new resolve-warning on every
   read — gate noise); guard `meta_data["scaling_factor_file"]` so the
   skip branch does not record a file that was never read; the one-line
   anchor of `template.py:466`'s dead cwd-relative write (behind
   `OUTPUT_NORM_DATA = False`).
5. **PR-body only (recorded, not scoped)**: the `amend_config`
   `datasearch.directories` restore bug (backup taken, never restored —
   14 tests lean on the leak; the PR claims **cwd**-independence, not
   global-state independence generally) is parked as its own proposed
   slug with a todo stub (`plan/todo-amend-config-restore.md` on the
   tasking branch — the convention followed this time);
   `new_reduction_from_template.py` parity untested + its
   `write_template` serializes resolved absolute paths (mixed-convention
   saved templates); `time_resolved.py` bare excepts (confirmed
   non-vacuous by the gate).

## v3 acceptance criteria (supersede v2's spot-check wording)

- `pytest tests/test_time_resolved.py` alone from the repo root: green.
- `pytest tests/test_scaling_factors_workflow.py` alone from the root:
  green. Stated as separate invocations with numbers.
- Bare `pixi run pytest` from the root AND `pixi run test-reduction`:
  green (currently 111 + launcher 10).
- Revert probes: remove the facility fixture → `test_time_resolved.py`
  alone red; reintroduce a bare `os.chdir` in any test → the next
  test's `_no_cwd_leak` fails.
