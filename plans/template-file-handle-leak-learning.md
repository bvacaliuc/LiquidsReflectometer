# Learnings — `template-file-handle-leak` (campaign `exp-settings-roi`)

## 1. A parity edit needs the other side's data model, not just its shape

**Rule.** Before copying a line into a forked implementation "so the two behave
the same", check that the fork's types carry the fields the line touches. Two
functions with identical signatures can parse into different classes.

**Why.** In `scaling-factor-path-anchor` v2 I added one line to the fork's
`read_template` so it would resolve scaling-factor paths the same way as
`template.py`:

```python
data_set.scaling_factor_file = _resolve_scaling_factor_file(data_set.scaling_factor_file, template_file)
```

The two functions look alike, take the same arguments and return the same-named
type — but the fork parses with `new_reduction_template_reader`, whose
`ReductionParameters` has **no `scaling_factor_file` at all**. So the line
raises on every call. Reproduced against `exp` as merged:

```
AttributeError: 'ReductionParameters' object has no attribute 'scaling_factor_file'
```

`new_reduction_from_template.read_template` is called from that module's line 59,
so the new-workflow path was broken from the moment PR #23 merged until this
slug. Nothing caught it in between: the v3 plan recorded "the fork's parity call
is untested" as a known gap, and a known gap in a test suite is a defect waiting
for someone to walk into it.

**How to apply.** When editing a fork for parity, `grep` the attribute in the
fork's *own* reader/model before assigning it, and add a test that calls the
forked function — one call would have failed immediately. Where the field may
legitimately be absent, guard with `getattr(obj, "field", None)` so the parity
line is a no-op rather than an exception.

## 2. Measure the leak under the conditions that expose it, and say which

**Rule.** For a resource leak in CPython, the count you get depends on whether
frames stay alive. Report the condition alongside the number, and build the
regression test to reproduce the exposing condition rather than the average one.

**Why.** The same bug produced two very different measurements:

| condition | unclosed `template*.xml` handles |
|---|---|
| warnings-as-errors probe, 25 tests failing | 46 on `template.xml` (+9, +8, +2, +2 elsewhere) |
| passing suite, `-W always::ResourceWarning` | 9 total |
| after the fix, same passing suite | **0** |

Neither figure is wrong. A failing test's traceback retains the frame, the local
`fd` keeps its reference, and refcount cleanup never runs — which is precisely
why the leak was loudest in the run that was already red. On a green suite
CPython closes most handles at return and the bug nearly hides.

That is also why the naive regression test is useless here: asserting
`handle.closed` after a plain call passes against the buggy code. The committed
guards call `read_template` inside a `try/except` that keeps `sys.exc_info()[2]`
bound, so the frame survives and an unclosed handle is observable.

**How to apply.** State the measurement condition next to any leak count. When
writing the guard, ask what keeps the object alive in the real failure and
reproduce that; if the test passes against the unfixed code, it is measuring
CPython's garbage collector, not your fix.
