# Learnings — `test-warning-filter` (campaign `exp-settings-roi`)

## 1. A declined optional item can be worth more than the item

**Rule.** When a plan offers an optional hardening step with a "drop it if it
trips" caveat, run the measurement anyway before dropping it. The trip list is
the finding.

**Why.** This slug's optional step was flipping pytest to warnings-as-errors
behind an allowlist, with an explicit instruction to drop it rather than
blanket-ignore if other third-party libraries warned. Measured on the full
suite:

```
filterwarnings = ["error", <the pyparsing ignore>]
pixi run test-reduction  ->  25 failed, 87 passed, 6 errors
  PytestUnraisableExceptionWarning 177   ResourceWarning 83
  RuntimeWarning 21                      DeprecationWarning 5
```

Correctly declined — allowlisting 25 failures is the blanket-ignore the plan
forbids. But the ResourceWarnings were not third-party at all: they name files
inside this repository, and they trace to `src/lr_reduction/template.py:66`,
where `read_template` does `fd = open(template_file, "r")` and returns without
closing it. One suite run leaks 46 handles on `tests/data/template.xml` alone.

So the step that could not land paid for itself by finding a real defect in
product code, and it also established the ordering for later: fix the leaks
first, and the `error` flip becomes affordable rather than a 25-failure wall.

**How to apply.** Treat "optional, drop if it trips" as an instruction to
*measure and then decide*, not as permission to skip. Record the trip list in
the commit body even when declining — it is the evidence for whoever schedules
the follow-up, and occasionally it is a bug report.

## 2. A test that resets the filters cannot test the filters

**Rule.** When the subject under test is a warning configuration, the test must
run under that configuration. `warnings.simplefilter(...)` inside
`catch_warnings` replaces the filter list, so it discards the very thing being
verified.

**Why.** The plan's test sketch asked for `catch_warnings(record=True)` plus
`simplefilter("always")`, and then to assert that no pyparsing warnings escape
the ini filter. Those cannot both hold: `simplefilter("always")` removes the ini
`ignore`, so the warnings always appear and the assertion can never pass. The
instruction was reaching for something real, though — without `always`, Python's
per-module `__warningregistry__` suppresses repeats, so a warning already
emitted by an earlier test would not fire again and the check would pass
vacuously, red or green.

The way to get both properties is to leave the filters alone and clear
`__warningregistry__` instead:

```python
for module in list(sys.modules.values()):
    registry = getattr(module, "__warningregistry__", None)
    if registry:
        registry.clear()
```

Then the warning can fire, and whether it is *recorded* depends on the
configuration under test — which is the question. Verified in both directions:
170 escapes before the ini entry, 0 after.

**How to apply.** Ask what the test would report if the feature were absent
*and* if it were present. If either answer is "the same", the harness is
overriding the subject. For warning filters specifically: never call
`simplefilter`/`resetwarnings` in a test whose subject is a filter; reset the
registry instead.
