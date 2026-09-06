# Learnings — `check-results-fields` (campaign `exp-settings-roi`)

## 1. A test helper that cannot fail is worse than no test

**Rule.** When a helper is the *only* thing standing between a computation and
its reference, give the helper its own tests. Coverage of the helper's callers
is not coverage of the helper.

**Why.** `check_results` looked like a ten-field row comparison and was a
one-field comparison of `error_b` against itself:

```python
for t in toks:
    kv = t.split("=")        # bare rebind — only the LAST token survives
for j in range(len(kv_ref)): # j never used
    v_calc = float(kv[1]); v_ref = float(kv_ref[1])
```

Five tests named `test_compute_sf*` reported green for a path whose `a` — the
scaling factor that multiplies every R(Q) produced from it — was never
compared to anything. The suite was not merely thin here; it was reporting
assurance it did not have, which is worse, because it stops anyone from
looking. Setting `a` to 999999.0 passed.

**How to apply.** For any comparison/assertion helper, write mutation guards:
perturb each field the helper claims to check and assert it *raises*. They are
cheap (11 tests, 0.06 s here, no data files, no Mantid) and they are the only
thing that can catch a helper that has quietly stopped comparing. Add a
positive control on an identical input so the guards fail for the right reason.
Include a *subtle* mutation next to the gross one — 1% high on `a` — because
that is what proves the tolerance is load-bearing rather than decorative.

## 2. Measure the tolerance; never inherit it, never widen it to get green

**Rule.** A comparison tolerance is a claim about how much variation is
physically expected. Derive it per field from measurement, and record the
measurement next to the number.

**Why.** The single `0.02` bar in this helper had only ever been exercised
against `error_b`. Applying it to the other nine fields would have been a
guess wearing the costume of a decision: it is ~350x too loose for `a`, and
meaningless for the instrument metadata, which is copied verbatim out of the
run logs and should round-trip exactly. Measured over 45 row-comparisons:

| field | worst relative delta | bar chosen |
|---|---|---|
| `LambdaRequested`, `S1H`, `S2iH` | 0.0 (45/45 bit-exact) | 1e-12 |
| `S1W`, `S2iW` | 0.0 after the stale row was repaired | 1e-12 |
| `a` | 5.6e-05 | 1e-3 |
| `error_a` | 3.0e-05 | 1e-3 |
| `error_b` | 2.3e-05 | 1e-3 |
| `b` | 6.7e-04 | 5e-3 |

Metadata gets 1e-12 rather than exact equality only so a one-ulp difference
from another Mantid build is not a failure; anything physical is caught nine
orders of magnitude sooner. `b` is looser than its siblings for a stated
reason — it is a near-zero slope (~1e-06 against `a` ~1-9), so its *relative*
error is inherently noisier. Each number carries its justification, so the next
person to touch it argues with the evidence rather than with a magic constant.

**How to apply.** If CI on another platform exceeds one of these, widen it from
a new measurement and say so in the commit. Never widen it to turn a suite
green — that converts a finding into a permanent blind spot, which is exactly
how this helper's `0.02` survived.

## 3. Adjudicate a failing reference against ground truth, not against consensus

**Rule.** When switching a comparison on makes a reference fail, find the
*source* the value is derived from and check against that. Agreement among
sibling files is corroboration, not proof.

**Why.** Turning the comparison on failed exactly one row: `sf_197912_Si_auto.cfg`
row 1 carried `S1W=19.992`, the code computed `19.952` — a clean 0.04 mm,
which by the numerical-diagnostics rule means "suspect a mundane parameter
mismatch", not novel behaviour. Three signals lined up:

1. the three sibling references all carry `19.952`;
2. a deadtime correction cannot change a slit width, so all four *must* agree;
3. — the decisive one — `S1W` is read verbatim from the run log
   (`abs(run.getProperty("S1HWidth").value[0])`), and `REF_L_197919` logs
   `19.952000000000005`. No run in the set logs `19.992`.

(1) and (2) are consensus and could both have been wrong together. (3) is
ground truth, and it is what turns "probably stale" into "stale". The reference
had not been regenerated since it was added.

**How to apply.** Repair *surgically*. Only the two stale metadata values were
changed; `a`, `b`, `error_a`, `error_b` were left alone so the reference stays
an **independent** baseline. Regenerating the file wholesale is the tempting
one-liner and it launders the very numbers the test exists to check — the
recipe-is-the-baseline pattern only works while the baseline was produced
independently of the code under test.

## 4. Repairing a shared fixture is a change to every consumer of it

**Rule.** Before editing a test data file, find who else reads it, and measure
the effect on them — not just whether their tests still pass.

**Why.** `sf_197912_Si_auto.cfg` is not only a reference; it is also the
scaling-factor file named by `tests/data/template_fbck.xml`, and that lookup
matches rows on slit widths with a fixed absolute `TOLERANCE = 0.07`. Run
198412 logs `S1W=20.000000`, so making the cfg *correct* moved it *further*
from the run it is applied to:

| field | before | after | budget |
|---|---|---|---|
| `S1W` | 0.008 | 0.048 | 0.07 (11% -> 69%) |
| `S2iW` | 0.009 | 0.049 | 0.07 (13% -> 71%) |

`test_reduce_functional_bck` still passes, so a "did the tests go green" check
would have reported nothing. But the margin went from comfortable to thin, and
the failure mode on the other side of that 0.07 is not a red test — it is a
silent fall-through that returns an **unscaled** reflectivity which looks
entirely plausible. Filed as a finding
(`tasking:plan/todo-scaling-factor-slit-match-margin.md`) rather than folded
into this diff.

**How to apply.** `grep` the fixture's name across `tests/`, `src/` and data
files before editing it. For anything that survives on a tolerance, compute the
margin before and after and put both numbers in the commit body — "still
passes" is not the same claim as "still has headroom".
