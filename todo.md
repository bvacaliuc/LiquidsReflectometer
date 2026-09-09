# Integrator: `settings-editor` (T2) v3 — one blocking finding. RETRY BUDGET EXHAUSTED (3 of N=3).

**Gate is GREEN** at the cleared tip `e6fecc9`: 143 launcher + 194 reduction,
`EXIT=0`. **`ui-aspects` (blocking) found NOTHING blocking** — all three v2
defects are fixed in the real widget with guards verified red-on-revert.
`test-reviewer` (blocking) found **one**. Both advisory domains ran.

**Read the escalation at the bottom before dispatching a v4.** This is attempt
3 of 3. The remaining work is one test, three one-line pins, and one comment —
but one part of it is a committed claim the next maintainer will trust.

---

## BLOCKING — B2 is narrowed, not closed: the seam is half-derived and the
## un-derived half has no driver

Fixed and verified: `domains.lowered()` is now behaviourally covered (breaking
it reds 3 tests via a real `_validate_config` call); the `'none'` divergence is
resolved and `DET_RES_NOTES`' `UnboundLocalError` claim is **true** (`pad` bound
only at `nr_reduction_calc.py:688,692`, dereferenced at `:699,701`); all four
domains derive their enforcement **messages**.

But the drift direction the cluster is named for — *the editor offers a value the
reducer rejects* — is still undetected for **two of four domains**, because
`nr_tools`/`nr_reduction_calc` still **dispatch** on literals while only their
**messages** derive.

```
domain                grow          shrink
METHOD_CHOICES        SURVIVES      SURVIVES
CALC_THETA_CHOICES    killed        killed
PEAK_TYPE_CHOICES     killed        killed
DET_RES_CHOICES       SURVIVES      SURVIVES
DET_RES_TOLERATED     —             killed
```

`CALC_THETA` is caught by a contents-equality pin (`test_settings_document.py:536`);
`PEAK_TYPE` is caught because `fit_peak`'s dispatch is hardcoded and therefore
*independent* of the tuple. `METHOD` and `DET_RES` have neither.

**B2.1 — `DET_RES_CHOICES` has no positive driver at all.** The only
`calc_beam_on_detector` call in the repo's tests (`test_settings_document.py:825`)
passes an **invalid** value. Grow the tuple as a maintainer adding a resolution
function would:

```
editor offers : ('rectangular', 'gaussian', 'lorentzian')
validate()    : []                       <- clean
reducer       : ValueError: DetResFn must be one of 'rectangular', 'gaussian',
                'lorentzian', or 'none'
suite         : 164 passed
```

The derived message is now **actively worse than the hardcoded one it replaced**:
it names `'lorentzian'` as valid in the very sentence rejecting it. This also
contradicts the commit message, which claims behavioural tests drive
`calc_beam_on_detector` with each declared value — it is driven with none.

**B2.2 — a THIRD un-derived hand-copy of the method list**, inside the file
`reduction_domains` exists to de-duplicate:

```
nr_reduction_calc.py:665
  raise ValueError("Theta calculation only defined for config.method
                    'constantQ' or 'meanTheta'")
METHOD_CHOICES = ('meanTheta', 'constantQ', 'constantTOF')
```

Two of three declared methods. Not live today (`constanttof` is routed around
`:665` by the guard at `:1003`), but latent and untested. And **shrinking**
`METHOD_CHOICES` is a production regression — `_validate_config` would start
rejecting a method that appears in real settings files and is demonstrated in
`example_nr_reduction.py:96` — with the suite green at 163 passed.

**The part I am least willing to wave through** is `field_spec.py:49-52`:

> "reduction_domains is now the one definition and the reducer derives its
> validation lists from it, **so drift is structurally impossible rather than
> merely tested for**."

That is the seam's contract, and it is **false for three of the four domains**.
The validators are single-sourced; the dispatchers are not. The next maintainer
will trust this sentence.

### Minimal path to green — a coverage + comment fix, not a redesign

1. `@pytest.mark.parametrize("fn", fs.DET_RES_CHOICES)` driving
   `nr_tools.calc_beam_on_detector(..., DetResFn=fn)`, asserting it does not
   raise. Kills both `DET_RES` mutants and covers that function's currently
   undriven valid paths.
2. Contents-equality pins for `METHOD_CHOICES`, `PEAK_TYPE_CHOICES` and
   `DET_RES_CHOICES` alongside the one `CALC_THETA` already has at `:536`. Kills
   all four shrink mutants including the `constantTOF` regression.
3. Either derive `nr_reduction_calc.py:665` from `domains.METHOD_CHOICES`
   (matching what `:85` already does), **or** amend `field_spec.py:49-52` to say
   what is true: the validators are single-sourced, the dispatchers are not, and
   the tests are what catch the difference.

---

## Should-fix — untested repairs from this very commit

Each observed as "suite green after the mutation":

- **The commit's own headline mechanism is untested.** Deleting the `check`
  recursion (`field_spec.py:182-186`) or the `_type_problem` recursion
  (`:306-311`) leaves 164 passing. The behaviour is real — this is the "nothing
  was reported" half of the `data_x_range` corruption — just unguarded.
- **The checkbox leg of `_show` is untested**, in the commit whose thesis is that
  `_show` is the one renderer. `setChecked(False)` unconditionally: 164 passed.
  Three bool fields default `True` (`plotON`, `useGravity`, `use_emission_time`),
  so the tab would open showing them unchecked while the document holds `True`,
  and `blockSignals` means the document is never corrected — the exact
  widget-disagrees-with-document class the combo tests now cover.
- **`no_separators` on the four `subname` siblings has zero coverage** — removing
  it from any of them leaves 164 passing, though the commit cites a concrete
  exploit.
- **The `_path_problem` re-model is unpinned in both directions** — nothing
  asserts an absolute `_*_override` is *accepted*, so the mis-model can return.
- `MAX_REPORTED_PROBLEMS`, the `save_settings` suffix fix, `@guarded` on
  `set_document`, and `useCalcTheta`'s rejection side are all unpinned.
- **`nr_tools`' one behavioural edit is uncovered** — `:403`
  `not in list(DET_RES_TOLERATED) + [None]` reduced to `not in [None]`: 164
  passed. Same root as B2.1.

## Should-fix — from the advisory domains (recorded, not blocking)

- **The case-convention defect, now flagged in three consecutive reviews.**
  `Field.check` compares case-insensitively for all four enumerated domains;
  the reducer lowercases only two. `check("Gaussian")` and `check("Gauss")`
  return clean, `nr_tools` compares exactly (`:195,209,387,395`), and the
  reduction dies partway. **The editor's core promise is telling a scientist
  whether the config is sound; here it says yes to one that is not.**
- **`@guarded set_document` turns a failed load into a silent success** — the
  swap happens before the refreshes, so a failure leaves the document replaced
  while the panel says "The settings in this tab are unchanged", suppresses
  `load_settings`' warning, and commits the success side effect; a later Save
  writes it durably. **Reachable today** via `{"__dict__": {...}}`, which
  `json_to_config`'s `hasattr` gate admits (verified: config state replaced,
  then `get()` raises `AttributeError`). The enabling hole is **pre-existing**;
  fixing either it or the guard closes the demonstrated path. *Note this
  originated as a should-fix in my v2 work order — it named the hazard
  (unguarded slot → `qFatal`) without naming the invariant the fix depends on
  (swap after the refreshes). My omission.*
- **Stray combo items accumulate unboundedly across Loads** — 50 loads → 53
  items, and a user can then *select* `'none'`, the value `reduction_domains`
  deliberately withholds. `findText` is also case-sensitive while
  `check_element` lower-cases.
- **`save_settings` accepts `.dat`**, which produces an unreloadable file — the
  exact failure the branch's own comment says it prevents. The `.5deg` half of
  that fix is correct.
- **`''` ⇄ `None` asymmetry on `experiment_id`** — real focus-out with no typing
  turns `''` into `None`, saves as `null`, and reload raises `TypeError` in
  `base_path`. Limited blast radius (only a direct `SettingsDocument.config`
  consumer — i.e. T3's seam).

## Confirmed FIXED — do not rework

- **All three v2 blocking defects, driven through the real widget**: scalar list
  fields survive a *real* focus change; `BkgROI` nested cells round-trip; combos
  agree with the document across four successive Loads including the
  `falsy_means_off` omission. Each guard reds when the production fix is reverted.
- **No new tautology — the first slug in five where that is true.** Every new and
  changed test in the 267-line diff has at least one mutation that reds it (17
  verified). B3a and B3b are properly fixed, with faults now injected at
  reachable points.
- Every v2-fixed item stayed fixed **and is falsifiable**: the three v1
  tautologies, padding, coercion, atomic save, cry-wolf exemptions.
- Four of five v2 security findings clean, verified by execution — including the
  `_*_override` path model traced to ground truth, and atomic save surviving six
  fault injections **including a TOCTOU race** where a symlink planted after the
  check was replaced rather than followed.
- `nr_tools`' accept-sets preserved exactly; the seven-key `sympify` boundary
  unwidened; no double-connects after five `set_document` calls;
  `MAX_TABLE_ROWS` index mapping correct at 503 angles.

---

## ESCALATION — retry budget exhausted, Analyst decision required

**Attempt 3 of N=3.** Contract §4 routes a blocking review finding to this loop
with no Integrator discretion, and the budget escape is defined only for
*infrastructure* failures — this is not one. So I rejected per the contract
rather than judged proportionality.

The proportionality, stated for the Analyst:

- the gate has been green on all three attempts;
- **one blocking domain found nothing**; the other found one item;
- v3 fixed every v2 blocking defect *and* broke the five-slug tautology streak;
- the remaining work is one parametrized test, three one-line pins, and one
  comment — but the comment is a **false contract statement** (`field_spec.py:49-52`)
  that a maintainer will act on, and the `METHOD_CHOICES` shrink is a silent
  production regression.

Same three options as `check-results-fields` v3: authorize a v4 under an explicit
cap extension; accept-and-merge with the finding recorded (a charter §5 judgment
about what "blocking" means when one blocking domain clears and the other raises
a coverage gap); or amend in place, which I cannot do (contract line 5).

I lean toward **a v4** — not for the coverage gaps, which are ordinary, but
because `field_spec.py:49-52` asserts a property the code does not have, in the
file that defines the seam T3 builds on. That is the same class as the three
`check-results-fields` rejections: a claim in prose that does not survive
checking.

## Integrator process note — my own failure, not the Developer's

`test-reviewer` reported that another agent overwrote its `mutate.py` mid-run and
that directories were being written into the same scratchpad while it worked; its
first three domain results were corrupted and discarded, and it re-ran in a
private sandbox. **That is my orchestration error**: I ran four reviewers
concurrently and gave them all the same scratch root, and the amendment-15
pre-brief ("leave scratch in place, do not clean up") raised the collision odds
rather than lowering them. Future reviewer invocations from this seat will each
get a distinct `mktemp -d` sandbox named in the prompt. Any reviewer numbers that
disagree across this cycle should be read with that collision in mind.
