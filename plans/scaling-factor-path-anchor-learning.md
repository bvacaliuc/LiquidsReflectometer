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

## 4. An unrestored `os.chdir` in one test invalidates every measurement after it

*Added after the v1 rejection; sections 1-3 are from the v1 cycle, and this one
corrects section 1's evidence.*

**Rule.** Before trusting a suite-wide number, check whether any test changes
global process state without restoring it. A single bare `os.chdir` converts
"the suite passes" into "the suite passes in this order, from this directory",
and nothing in the output says so.

**Why.** `test_reduce_functional_bck` did `os.chdir(Path(template_dir).parent)`
— into `tests/` — and never restored it. Every test collected after line 229
therefore inherited the gate's working directory no matter how pytest was
invoked. Two consequences, and the second is the one worth remembering:

1. It completed the root cause. The nine original failures were exactly the
   sf-path tests defined *before* the leak (lines 53-202, plus `test_dead_time`,
   which sorts first). The sf-tests *after* it passed on borrowed cwd. That
   distribution looked arbitrary until the leak explained it.
2. **It made this slug's own acceptance criterion satisfiable by accident.** v1
   reported "bare pytest from the repo root: 109 passed" as proof the fix
   worked. With the leak repaired and the same product fix in place, the honest
   number was **9 failed, 100 passed** — two more in `test_reduction`, five in
   `test_scaling_factors_workflow`, two in `test_time_resolved`, none of which
   v1 could see.

The v1 verification was not sloppy in execution — the command was right, the
output was read correctly, the number was real. It was measuring a suite whose
state had been mutated out from under it, which is a failure of *what* was
trusted rather than *how* it was run.

**How to apply.** `grep -rn 'os.chdir' tests/` before believing a whole-suite
result, and prefer `monkeypatch.chdir`, which pytest restores at teardown. When
a fix's acceptance criterion is "the whole suite goes green", confirm that at
least one affected test still fails *individually* before the fix and passes
individually after — a per-test check cannot be laundered by ordering. The
criterion here now includes running a late test alone from the repo root, which
is exactly the check the leak used to defeat.

## 5. A fallback that guesses is the failure it was meant to prevent

**Rule.** When a fix's purpose is to stop a program silently using the wrong
data, do not give it a search path. Resolution should be exact and few; where
nothing matches, say what was tried and stop.

**Why.** v1 anchored relative scaling-factor paths by walking up from the
template's directory, bounded at three levels. It resolved the fixture, and it
also meant any same-named `.cfg` sitting above a template could be bound
silently — in an IPTS-shaped layout the reviewer found a stale one two levels
up. That is the same class of defect as the branch this slug removed: a
reduction that produces a plausible, wrong R(Q) without a word. Closing a
silent-wrong-number hole with a fallback that can open another one is not a fix,
it is a relocation.

v2 anchors at the template's own directory and nowhere else, and where nothing
resolves it logs every candidate it tried. Making that work required the fixture
templates to declare their scaling-factor file relative to themselves — which
is the more honest arrangement anyway: a template that names a sibling file
should say so, rather than relying on the reader's working directory.

**How to apply.** Count the candidate paths a resolver can produce. One or two
that are each explainable in a sentence is a resolution rule; a loop is a
search, and a search that silently accepts its first hit is a guess. If a
fixture only resolves under a search, fix the fixture.
