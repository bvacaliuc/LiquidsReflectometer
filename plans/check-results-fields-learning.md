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

## 5. Check your baselines are distinct before deriving a tolerance from them

**Rule.** Before trusting any number measured by comparing outputs against a
set of reference files, verify the references are **pairwise distinct**. A
duplicated baseline does not fail — it silently answers a different question
than the one you asked.

**Why.** v1 of this slug derived its entire fitted-parameter tolerance budget
from measurement, recorded the measurement next to the number, and was still
wrong, because two of the four references were byte-identical:

```
14d3e256da9dee40e9b575e322754a5e  sf_197912_Si_dt_par_46_200.cfg
14d3e256da9dee40e9b575e322754a5e  sf_197912_Si_dt_par_46_300.cfg
```

So `test_compute_sf_with_deadtime_tof_300` compared a **300**-step computation
against a **200**-step reference. Regenerating the 300 reference and diffing it
against the 200 output reproduces v1's "worst observed delta" table exactly —
b 6.748e-04, a 5.648e-05, error_a 3.046e-05, error_b 2.268e-05. Not close: the
same numbers. Four of the five cases reproduce to ≤1e-11; 100% of the budget
came from the one contaminated case, read as fit noise.

**Two lessons, and the second is the sharper one.**

*Measuring is not enough; you must know what you measured against.* "Derived
from measurement" felt like rigour and was the vehicle for the error. The
measurement was real — it measured the difference between two TOF binnings.

*A rationale invented to explain a number is worse than no rationale.* v1
explained b's large delta as "a near-zero slope, so relative error is
inherently noisier". That is plausible, it is physics-flavoured, and it is
false — b is simply the parameter most sensitive to the TOF binning change.
A comment that instructs future maintainers with a fabricated cause is more
durable damage than a loose constant, because the constant can be re-measured
while the explanation gets believed. When a number surprises you, the honest
options are "diagnosed, here is the cause" or "not yet diagnosed" — never a
story that fits.

**How to apply.** `md5sum` the reference set — that was the whole cost of
catching this. Better, encode it: this slug now carries a guard asserting each
reference pair differs on at least one field the comparator actually looks at,
which is stronger than distinct bytes (a header-only difference would not
count). And ask of any passing test: *what would have to break for this to
fail?* Hard-coding `DeadTimeTOFStep = 200` and running `-k tof_300` answered
that in 50 seconds — it passed under v1, and fails now.

## 6. A regenerated baseline pins regressions; it does not validate physics

**Rule.** When no independent ground truth exists, regenerating a reference
from the code under test is still worth doing — but say plainly which of the
two jobs it does.

**Why.** For `S1W` there *was* ground truth: the run log. For the fitted
parameters at 300 there is none — the only way to obtain a 300 baseline is to
run the code. That makes it self-fulfilling for correctness, and the temptation
is to conclude the test is therefore worthless and `xfail` it.

That is wrong. The regenerated baseline restores the property that actually
matters to a regression suite: with it, hard-coding `DeadTimeTOFStep = 200`
makes the test **fail**; without it, the test passed no matter what the code
did with its own parameter. It cannot tell you today's 300 output is right; it
can tell you tomorrow's differs from today's.

**How to apply.** Commit the writer's verbatim output, header and all —
`# Version:`, `# Generated on`, `#    deadtime_tof_step: 300.0`. None of the
four committed references carried that block; they had been hand-trimmed, and
that is exactly how a duplicate hid in plain sight for as long as it did.
Then state in the commit body which job the baseline does, so nobody later
mistakes "the test is green" for "the physics is verified".

## 7. Ask your own new test what would have to break for it to fail

**Rule.** A test written to prove a guard works must be constructed so that
**only that guard** can make it fail. Inject the minimum defect, not a
convenient one.

**Why.** v2 added a duplicate-key guard to the cfg parser and a test for it
that appended `a=999999.0` as the duplicate. The duplicate guard caught it —
and so did the value comparison, because 999999.0 is also wrong. Deleting the
guard entirely left the test passing:

```
guard removed, v2 form:  1 passed     <- cannot fail for its stated reason
guard removed, v3 form:  1 failed
```

The fix is to inject the **reference** value, so the value comparison has
nothing to say and only the duplicate check can raise.

The irony is the lesson. v2's own headline finding was a test that could not
fail (a 300-step computation compared against a 200-step reference), and the
confirming experiment it introduced — hard-code the parameter, watch the test
go red — is exactly the technique that would have caught this. It was applied
to the code under test and not to the new test. **A guard's test is code too,
and it deserves the same question.**

**How to apply.** For every test asserting that something raises: delete the
mechanism you believe is raising, and re-run. If it still passes, the test is
measuring something else. This takes seconds and is the cheapest verification
in this entire slug's history — cheaper even than the `md5sum` of §5.

## 8. Say which number you are quoting

**Rule.** When a tolerance is justified by "N× headroom", state the quantity
N is computed from, because several plausible ones differ by orders.

**Why.** v2 described its bars as "~200× headroom", meaning
`rtol / worst-relative-delta`. But what actually governs whether the suite goes
red is the **tightest single comparison** in it: `min(bar / |delta|)` over every
field of every row of every case. Those are different numbers, and a maintainer
told "200×" would go looking for a margin they could not reproduce.

Measured on the final v3 bars, the governing figure is **2336×** — at
`error_a`, row 0, `_42_200`: `|delta|` 1.998e-13 against a bar of 4.668e-10.
It also moved during v3 for a non-obvious reason: relaxing `b` from 1e-8 to
1e-7 did not change `b`'s status as the loosest field, but it lifted `b` out of
the binding position and handed it to `error_a`. The review predicted 1678×
from the pre-change bars; the number is a property of the whole configuration,
not of any one field.

**How to apply.** Compute and quote the tightest actual comparison. And give a
widened bar a documented **ceiling** where widening would start destroying a
different guard — `b` here cannot exceed 6.7e-04, the physical 200→300 binning
difference, without making the pairwise-distinguishability test vacuous. An
escape hatch with no stop is how a tolerance ratchets open one measurement at a
time.
