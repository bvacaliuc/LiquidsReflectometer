# Learnings — `scaling-factor-path-anchor` (campaign `exp-settings-roi`)

## 1. A gate command that changes directory hides every cwd-dependent defect behind it

**Rule.** When a project's sanctioned test command begins with `cd`, treat that
`cd` as part of the code under test. Anything the suite resolves relative to the
working directory is unverified by that gate, however green it is, and the first
person to run the tests any other way finds out.

**Why.** `pixi run test-reduction` is `cd tests/ && pytest …`, and the fixture
template declares `<scaling_factor_file>data/sf_197912_Si_auto.cfg</...>`. From
`tests/` that resolves; from the repository root it does not. So the campaign
gate was 107 green on the same commit where the human's `pixi run pytest`
produced **9 failed**, and both results were honest. Nothing was
campaign-introduced — the human's invocation had never been green on any commit
of `exp`.

The failure did not present as a missing file, which is what made it expensive:
`scaling_factor()` printed a message and returned the workspace, and its single
call site unpacks a 4-tuple, so what surfaced four frames later was
`TypeError: cannot unpack non-iterable EventWorkspace object`. A branch that
cannot succeed is not error handling; it is a delayed, disguised crash. It now
raises `FileNotFoundError` at the point of detection.

**How to apply.** Read the gate task's command line before trusting its verdict.
If it changes directory, sets environment, or narrows paths, then at least one
committed test must run from somewhere else — otherwise CI structurally cannot
see the regression. The two tests added here `monkeypatch.chdir` deliberately
for exactly that reason: they fail under the gate command too, where a
"run pytest from the root" reproduction never would.

## 2. Verify which anchor actually resolves before writing the resolver

**Rule.** When a plan says "resolve relative to X", construct the path and test
it before implementing. Path-anchoring specifications are easy to state and easy
to get off by one directory.

**Why.** The plan prescribed anchoring "relative to the template file's own
directory", which sounds obviously right and does not work here. The template is
`tests/data/template.xml` and declares `data/sf_197912_Si_auto.cfg`, so the
template-dir anchor is `tests/data/data/sf_197912_Si_auto.cfg`. Measured before
writing any code:

```
cwd-relative (repo root)   tests/../data/sf_197912_Si_auto.cfg   missing
template-dir anchor        tests/data/data/sf_197912_...cfg      MISSING  <- as planned
template-parent anchor     tests/data/sf_197912_Si_auto.cfg      EXISTS
```

The path is anchored one level *above* the template, at the directory the gate's
`cd tests/` makes current — which is the giveaway that these relative paths were
written for a particular working directory rather than for the template. The
implementation therefore walks up from the template's directory a bounded number
of levels instead of assuming one, and reports what it tried.

**How to apply.** Four `test -f` invocations settled this in one command. The
general form: before implementing a resolution rule, enumerate the candidate
paths it would produce for the real fixture and check which exist.

## 3. "The tests are correct" is a claim to verify, not a scope guard to obey

**Rule.** A plan's scope guard protects intent, not a factual assertion. When the
assertion behind the guard turns out to be false and the acceptance criterion
depends on it, fix the smallest thing that makes the criterion reachable and say
so.

**Why.** The plan stated the nine failing tests were correct and out of scope —
the product code was wrong. Eight of them were. `test_full_reduction` also
carried `np.loadtxt("data/reference_rq.txt")`, its own cwd-relative literal, and
no amount of product-side anchoring reaches it. After the src fix the suite went
9 failed → 1 failed, and the remaining failure was that line. The acceptance
criterion — the human's exact command, all green — was unreachable while it
stood.

The distinction that makes touching it legitimate: the guard exists to stop
"fixing" a red suite by weakening its assertions. Replacing a cwd-relative
literal with `os.path.join(template_dir, ...)` — a fixture already in that test's
signature, and how every other reference path in the file is built — changes no
assertion. The test checks exactly what it checked before, from any directory.

**How to apply.** When a guard blocks the acceptance criterion, ask whether the
guard's *premise* still holds. If it does, stop and route it back. If it does
not, do the minimal thing and flag the deviation with the evidence — the plan's
author gets to disagree, but with the finding in front of them.
