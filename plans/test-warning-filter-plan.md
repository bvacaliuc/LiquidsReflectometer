# Plan: test-warning-filter

**Campaign:** `exp-settings-roi` · base `exp` @ `c14f54b` (#18 merged) ·
mid-effort addition 2026-09-05, human-approved (from
`todo-test-warning-cleanup.md`; staged **before T2** to protect
new-warning signal) · DAG-independent
**Retry attempt:** 1

Review domains: test-reviewer (advisory — no behavior change, output
hygiene + regression guard).

## Symptom

`pixi run test-launcher` emits ~383 warnings, **100 %
`PyparsingDeprecationWarning`**, all third-party (matplotlib's
`_mathtext.py` / `_fontconfig_pattern.py` call pyparsing's deprecated
camelCase API when rendering mathtext — e.g. the overplot `R*Q^4` label).
lr_reduction owns **zero** first-party warnings today. The noise buries any
*new* first-party warning a future slug (T2/T3) would introduce.

## Root cause — corrected against the source (Analyst, 2026-09-05)

**The `todo-*` summary's premise is wrong and is not carried into this
plan.** It says "matplotlib < 3.6 predates its migration off pyparsing's
deprecated API… fix at the source by bumping matplotlib." Measured in the
actual env: **matplotlib is `3.9.4`** (the current pin, `pyproject.toml:120`
`matplotlib = "==3.9.4"`), **pyparsing `3.3.2`**, and 3.9.4 *still* calls
`parseString`/`resetCache`/`oneOf`/… in `_mathtext.py` (120 warns) and
`_fontconfig_pattern.py` (50) while parsing `classic.mplstyle` and mathtext.
So **there is no available matplotlib bump that removes these** — 3.9.4 is
recent and still lags pyparsing. The `filterwarnings` scoping is therefore
**the fix, not a stopgap**; the "bump matplotlib" item is retired (revisit
only if a future matplotlib migrates *and* is co-installable with the
facility Mantid conda — tracked, not scheduled).

## Files to change (on `feature/test-warning-filter` from `agentic/exp`)

1. `pyproject.toml`, `[tool.pytest.ini_options]` (line ~200): add a
   `filterwarnings` list. **Use the pyparsing-category filter — Analyst
   measured all three candidate scopings, and this is the only complete
   one that is also safe here:**

   ```toml
   filterwarnings = [
     # matplotlib 3.9.4's _mathtext / _fontconfig_pattern still call
     # pyparsing's deprecated camelCase API (pyparsing 3.3.2 warns) when
     # rendering mathtext. Third-party, no available bump removes it.
     # Scoped to pyparsing's OWN category, which this repo never triggers
     # first-party (only transitively via matplotlib), so our own code's
     # DeprecationWarnings still surface unmasked.
     "ignore::pyparsing.warnings.PyparsingDeprecationWarning",
   ]
   ```

   Measured evidence (2026-09-05, `pixi run python`, mathtext render of
   `R·Q⁴`): the two `todo-*`-suggested scopings are **incomplete** — the
   module-scope `ignore::DeprecationWarning:matplotlib._{mathtext,fontconfig_pattern}`
   leaks **1** (pyparsing's own `util.py`, attributed to pyparsing not
   matplotlib), and the message-regex `.*deprecated - use .*` leaks **3**
   (not every message has that shape). The category filter leaks **0**,
   and a synthetic first-party `DeprecationWarning` remains visible under
   it (different category). This is the "never bare category" exception
   the `todo-*` gestured at, resolved by measurement: the *pyparsing*
   category is safe precisely because the repo has no first-party
   pyparsing use — confirm that assumption still holds at implementation
   (`git grep -l "import pyparsing" src launcher` → empty).

2. `tests/` — a small guard test (new file
   `tests/test_warning_hygiene.py` or into an existing unit file):
   - `test_no_pyparsing_warning_from_mathtext`: render a mathtext label
     under `warnings.catch_warnings(record=True)` +
     `simplefilter("always")` and assert **zero** `PyparsingDeprecationWarning`
     escape *the ini filter* — i.e. run it the way pytest runs (the ini
     `filterwarnings` is active), so the test passes only when the scoping
     works. (RED before the ini edit: the warnings escape and the assert
     fails.)
   - `test_first_party_deprecation_still_visible`: issue a synthetic
     `warnings.warn("probe", DeprecationWarning)` from a helper under this
     package's module path and assert it is **not** suppressed — pins that
     the scoping did not over-broaden (RED if someone later widens the
     filter to a bare category ignore).

## Optional — the regression guard (advisory in this plan, land if clean)

Fix #3 from the `todo-*`: flip to warnings-as-errors behind the allowlist —
`filterwarnings = ["error", <the two ignores>]` — so a NEW first-party
warning fails the suite loudly, locking in today's zero-first-party state.
**Caveat, do not force it:** `error` mode trips the first time *any* other
third-party lib (Mantid, numpy, h5py) warns, and this suite imports Mantid
heavily. If a measured `pixi run test-reduction` under `error` surfaces
third-party warns beyond the two matplotlib modules, either widen the
allowlist for each with a cited reason or drop the `error` flip this slug
and park it — do not blanket-ignore to force green. Record the decision in
the commit body either way.

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Module-scope/message-regex chosen instead (both measured incomplete: 1 and 3 leaks) | `test_no_pyparsing_warning_from_mathtext` stays RED | use the pyparsing-category filter (0 leaks, measured) |
| Repo gains first-party pyparsing use later (would then be masked) | the `git grep import pyparsing` check at implementation | re-scope to module+message if that ever becomes non-empty |
| `error` mode trips on Mantid/numpy (if the guard is attempted) | a `test-reduction` run errors on a third-party warn | allowlist-with-reason or drop the guard this slug |
| A future matplotlib bump silently makes the ignore dead | harmless; the ignore matches nothing | comment notes it is bump-retirable |
| pixi.lock re-stamp on any pixi run | first line ≠ `version: 6` | amendment 14: restore, never commit non-v6 |

## Red-Green seed

- RED: add both guard tests before the ini edit; `pixi run test-launcher`
  → `test_no_pyparsing_warning_from_mathtext` fails (warnings escape).
- GREEN: add the `filterwarnings` block; both guard tests pass, and the
  suite's warning summary drops from ~383 to **0 pyparsing** (record the
  before/after count in the commit body — the measurement is the proof).

## Acceptance criteria

- `pixi run test-launcher` and `pixi run test-reduction` green; the
  warning summary shows **0 `PyparsingDeprecationWarning`** (before/after
  counts in the commit body).
- Both guard tests present and green; the first-party-visibility test
  demonstrably RED if the filter is widened to a bare category ignore.
- Diff touches exactly `pyproject.toml` + the guard test file; **no
  `pixi.lock` change** (no dependency moved — this is config, not a bump;
  restore any hook re-stamp, keep `version: 6`).
- Draft PR body: notes the corrected root cause (3.9.4 still warns; no
  bump available), that the matplotlib bump is retired-not-deferred, and
  no deploy consequence (config-only, env unchanged).
