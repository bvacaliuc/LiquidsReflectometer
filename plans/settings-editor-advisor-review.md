# Advisor review — `settings-editor` (T2) at the retry cap (2026-09-09)

Written for the human's decision on `review/settings-editor` @ `493c81c`
(Integrator: "one blocking finding, RETRY BUDGET EXHAUSTED"). Read the plan's
three revision entries, both learnings files, all three Integrator `todo.md`s
(`27710bd`, `e904196`, `493c81c`), the three Developer commits (`371fe57`,
`e9b9e68`, `15a5dda`), and verified the v3 finding against the source at
`15a5dda` before writing this.

## 1. Trajectory: converging, and fast

| Attempt | Gate | Blocking clusters | Character of what was wrong |
|---|---|---|---|
| v1 `371fe57` | green 128+145 | 6 | two launcher-abort paths from valid files; every `list[...]` cell stored a raw string (`useBS="False"` truthy → background subtracted when off); save truncated before writing; `useCalcTheta` a checkbox where the reducer wants an enum; three tests that could not fail; T3 interface gaps |
| v2 `e9b9e68` | green 140+179 | 4 | v2 fixed the construction path and not the refresh path, and its own `set_document` fix moved startup onto the stale path (bare focus-out corrupted `data_x_range` silently); domain seam half-derived; `doc.config` unpinned; two new tautologies while fixing tautologies |
| v3 `15a5dda` | green 143+194 | 1 | `ui-aspects` cleared with nothing blocking; `test-reviewer`: the seam is still half-derived and the un-derived half has no positive driver, plus a false contract sentence |

Six, four, one. Every v1 and v2 defect is confirmed fixed by the gate and
falsifiable. v3 is the first slug in five with no new tautology. This is the
shape the retry cap was not designed for: the cap bounds a plan that is not
converging, and this one is.

## 2. The v3 finding, verified

- **`field_spec.py:46-51`** says: *"reduction_domains is now the one
  definition and the reducer derives its validation lists from it, so drift
  is structurally impossible rather than merely tested for."* False for three
  of four domains. `nr_reduction_calc.py:85,91` derive their lists; but
  `nr_tools.py:195,209,238,387,395` dispatch on string literals and derive
  only their *error messages*, and `nr_reduction_calc.py:665` carries a
  third hand-copy of the method list (two of three methods).
- **`DET_RES_CHOICES` has no positive driver.** The only
  `calc_beam_on_detector` call in the tests (`test_settings_document.py:825`)
  passes `"sombrero"` inside `pytest.raises`. Growing the tuple with
  `'lorentzian'` leaves `validate()` clean, the reducer raising, and the
  suite green. The derived message then names `'lorentzian'` as valid in the
  sentence rejecting it.
- **Shrinking `METHOD_CHOICES`** is a silent production regression
  (`_validate_config` would reject a method real settings files use) with
  the suite green. Only `CALC_THETA` has a contents pin (`:536`).
- The v3 commit message claims behavioural tests drive
  `calc_beam_on_detector` with each declared value. They do not.

The v3 plan's own acceptance said *"all four domains single-sourced from
the reducer; one behavioural acceptance test per domain."* The delivery met
neither for `DET_RES`, so the rejection is inside the plan's contract, not a
new preference. The Integrator was right to block: the sentence is the
contract of the seam T3 builds on, and it is untrue.

## 3. Why v3 fell short: "derive the dispatch" was the wrong ask

`if peaktype == "gauss": ... elif peaktype == "supergauss": ...` cannot be
derived from a tuple without restructuring into a dict dispatch, which is a
refactor of reducer code the slug has no mandate for. The Developer derived
what could be derived (messages), left the literals, and then wrote the
claim the plan wanted rather than the one the code supports. The honest
resolution is the Integrator's option 3b: state what is true — validators
are single-sourced, dispatchers are literal, contents pins are what catch
divergence — and add the pins. Do not restructure `nr_tools`.

## 4. Recommendation: extend the cap to N=4 for this slug, v4 bounded

Same reasoning as `check-results-fields` (plan `### v4`, escalate.md): a
converged slug at the cap is a cap-policy problem, not a slug problem.
Scope, in priority order:

1. **Truthful contract.** Rewrite `field_spec.py:46-51` to say validators
   derive from `reduction_domains`, dispatch in `nr_tools` and
   `nr_reduction_calc` stays literal, and the contents pins below are what
   catch drift. Derive the message at `nr_reduction_calc.py:665` from
   `domains.METHOD_CHOICES` (one line; the dispatch above it stays).
2. **Positive driver for `DET_RES_CHOICES`.**
   `@pytest.mark.parametrize("fn", fs.DET_RES_CHOICES)` calling
   `nr_tools.calc_beam_on_detector(..., DetResFn=fn)` and asserting no raise.
3. **Contents-equality pins** for `METHOD_CHOICES`, `PEAK_TYPE_CHOICES`,
   `DET_RES_CHOICES`, beside the existing `CALC_THETA` pin.
4. **Case convention** (advisory in three consecutive reviews; a
   correctness defect in the editor's core promise): `Field.check` accepts
   `"Gaussian"` for `DetResFn` and `peak_type`, `nr_tools` compares exactly,
   the reduction dies partway. Either normalize to the declared spelling in
   `coerce_element` for those two domains or check case-sensitively where
   the reducer does. One behaviour, one test.
5. **Pins for v3's own untested repairs** (each observed "suite green after
   mutation"): `check`/`_type_problem` list recursion; the checkbox leg of
   `_show`; `no_separators` on the four `subname` siblings; an absolute
   `_*_override` path accepted; the `DET_RES_TOLERATED` branch in
   `nr_tools`.

Every new or changed guard records its mutation and observed red in the
commit body (charter §9 amendment 16). **Final-gate bar for the Integrator:**
PASS when items 1–3 are present and their mutations red. Items 4–5 missing
or imperfect are advisory, recorded in the draft-PR body, not grounds for
rejection. Anything else new rides the PR body.

Left for follow-up slugs or the PR body, deliberately: the `@guarded
set_document` silent-success path (needs the pre-existing `__dict__` hole
closed in `json_to_config`); combo items accumulating across Loads;
`save_settings` accepting `.dat`; the `''`/`None` asymmetry on
`experiment_id`; capping `refresh_report()`.

## 5. For T3

T3's `SettingsResolver` consumes `SettingsDocument`, `FIELD_SPEC`, and the
domains module. Item 1 above is the sentence T3 will read first; it must be
true before T3 is staged. Items 2–3 are the guards T3 inherits. Nothing else
in this slug blocks T3's plan.

## 6. Process note

Two slugs have now reached the cap converged, one on prose and one on a
coverage gap plus prose. The proposed charter amendment (transcript Prompt
27, Advisor): at the cap, a rejection whose only blocking finding is prose
or a coverage gap on substance every declared reviewer has confirmed sound
is a *convergence amendment* — the Analyst emits `triage/{slug}-v{N+1}`
scoped to the named items, it does not consume the budget, and the
Integrator passes when the items match the measurement. Findings stay
blocking; only the counting changes. Without it the human is the relief
valve every time a slug converges at N.
