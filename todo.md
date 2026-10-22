# Integrator: `legacy-reduction-hygiene` v1 @ 98b3f9b — REJECTED (attempt 1 of 3)

**One blocking finding, prose only. The code passes every gate leg.**

## Passed

- G: 10 + 146, rc 0, **no warnings line** (the base L1‴ `2ab688f` shows 697).
- T1: the four `src/` files and `test_output.py` are byte-equal to `6234dcc`. The freeze lists are unchanged. #24's four guards are AST-identical. P2 is clean.
- T4, the harness, base `2ab688f` vs this tip, 9 scenarios:
  - data columns identical ×9;
  - headers A/B identical;
  - the only masked differences are output-directory names and durations in `transcript.txt`.
- Numerical review: not blocking. Every `np.divide(..., where=)` is element-identical to the base, the masked elements included, and the narrowed `except` handles every input class the base handled.

## Blocking: B-1, a false claim, in two places

1. **`tests/test_warning_hygiene.py:15-19`, the module docstring:** "Each runs its site under an "error" filter with an input that used to warn".
2. **The commit body, ¶3 (line 30):** "…under an "error" filter with an input that used to warn…".

This is false for four of the nine new tests (checked first-hand):

| test | what it actually does |
|---|---|
| `test_a_zero_error_with_counts_still_warns_in_the_background_fit` (`:195`) | `pytest.warns(RuntimeWarning, match="divide by zero")`, on an input that **still** warns |
| `test_the_functional_background_fits_each_bin_with_the_base_weights_of_its_counts` (`:226`) | sets no warnings filter; pins call-site arguments against the base arithmetic; green on the base |
| `test_the_algorithm_applies_the_base_arithmetic_to_the_rate_it_measures` (`:344`) | the same as `:226` |
| `test_reading_a_result_file_without_data_rows_warns_nothing` (`:369`) | records under `simplefilter("always")` and asserts none; it does not raise |

The `no-zero` cases of `:150`, `:183` and `:296` are non-warning controls.

**Accurate wording:** "six of them run their site under an error or record filter with an input that used to warn, and check the values; two pin the call sites' arguments against the base arithmetic; one pins a warning that is deliberately kept (a zero error with counts)."

**Fix shape:** the commit body cannot be changed by a follow-on commit; a pushed branch is never rewritten. Re-cut v2 as a fresh replay of `6234dcc` on L1‴ `2ab688f`, with the corrected docstring and body, on a **new branch name** (the Analyst's call, as with K19's Phase 1c). A follow-on commit fixing only the docstring would leave the false sentence in the history that goes upstream.

## Advisories (for v2's body, or the PR body)

- "697 first-party warnings from four files": plan V5 counts 694 + 2 + 1 from three sites (`peak_finding.py:107`, `dead_time_correction.py:98`, `test_read_file_empty`). The base's summary does not name sources, and `background.py` may contribute to the 694 (a test notes 35 base 1/0s on the functional-background path). Either measure it, or say "from the warning sites in four files".
- "a row that is not four columns raised ValueError" is imprecise: a single column of exactly four rows unpacks, on the base and the tip alike.
- The freeze lists: `.pre-commit-config.yaml:29` says "drop an entry when the file is next intentionally changed", and this is that change. T3 measured 0 ruff findings at base and tip, so un-freezing the four would cost nothing. Un-freeze them in v2, or say in the PR body that it is deferred: the human's call.
- The per-test docstrings carry review IDs ("U7 (v2, test advisory A1)", "Plan A2", "W1b") and a base `2324e5c` that upstream cannot resolve.
- Two real-data tests rely on the Mantid facility being set at import by other modules (`test_reduction.py:18-19`). This is deterministic under pytest (all modules import before any test runs), but fails if the file is run alone. Name it; the cure is the fork's `mantid_facility` fixture (K19 series `0003`).
- The harness template has `two_backgrounds` false, so the 9 scenarios never reach `functional_background`; the tests pin that path element by element instead.
