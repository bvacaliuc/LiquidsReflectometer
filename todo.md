# todo.md — overplot-refresh, Integrator cycle 1

**Verdict:** infrastructure failure — **third data point** of the
same protocol↔versioningit interaction documented in
`feature/cd-dialog-resize:todo.md` and re-stated for
`feature/overplot-axes:todo.md`. Both runs (initial + post-
`__pycache__`-clean retry) exited 1 with the identical
`versioningit.errors.InvalidVersionError: Cannot parse version
'qa/overplot-refresh'` traceback.

## Failing tests

None. Environment build failed before pytest collection.

## Root cause

Unchanged from the first two cycles. `pyproject.toml:50-52` has
`[tool.versioningit.vcs]` with no `match` filter, so versioningit's
`git describe --tags HEAD` accepts the protocol's lightweight
`qa/{slug}` tag as the most recent tag. Verified on this branch:

```
$ git describe --tags HEAD
qa/overplot-refresh

$ git describe --tags --exclude='qa/*' --exclude='review/*' HEAD
v2.9.0rc3-101-g0f9a0ca   # PEP 440-compliant
```

Three structurally unrelated feature branches (`direct_beam.py`,
`overplot.py` axes, `overplot.py` refresh) now all hit identical
build-stage failures. The protocol cannot make forward progress on
any slug until the project-side versioningit `match` filter lands.

## Recommended fix (unchanged)

Edit `pyproject.toml:50-53`:

```toml
[tool.versioningit.vcs]
method = "git"
default-tag = "0.0.1"
match = ["v[0-9]*"]
```

See `feature/cd-dialog-resize:todo.md` (long form) for the
implementation/validation guide and the standalone-slug-vs-coupled-
scope discussion.

## Recommended Analyst action this round

Three identical infrastructure failures across three slugs is
sufficient signal that the **next plan revision should not be a
per-slug retry**. The structurally correct response is the
standalone fix slug:

1. **Pause the per-slug retry loop.** Re-pushing
   `triage/cd-dialog-resize-v2`, `triage/overplot-axes-v2`,
   `triage/overplot-refresh-v2` would each consume Developer +
   Integrator cycles and **all three would re-hit the same build
   error** unless their plan revisions explicitly include the
   `pyproject.toml` change. That is wasted retry budget.
2. **Spin a `triage/build-versioningit-tag-glob` slug** whose entire
   plan is the 1-2 line `pyproject.toml` change above. Its qa tag
   will trigger the same build error on first push (its own qa tag
   appears as the describe target!) — so the slug must include a
   self-validation step: `git describe --tags --match='v[0-9]*'
   HEAD` returns a `v*` tag *with the patched pyproject.toml in
   place*, confirming versioningit's read of `tool.versioningit.vcs`
   gets the new `match` filter before the editable build runs.
3. **After that slug merges to `{base-branch}`,** the existing
   `feature/{slug}` branches need to incorporate the fix. Two paths:
   - Developer rebases each `feature/{slug}` onto the updated
     `{base-branch}` and re-pushes / re-tags `qa/{slug}` (a new
     SHA, hence new (SHA, ref-name) tuple per dedup contract — fresh
     event for the Integrator).
   - Or merge updated `{base-branch}` into each feature branch (a
     regular merge commit — preserves history per `~/.claude/CLAUDE.md`
     `[ALWAYS] Git discipline: regular merges only`).

Either path is acceptable; rebase keeps the feature commits clean
relative to the new base, merge keeps the audit trail of when the
fix integrated.

## Why I am still NOT auto-deleting the local qa tag as a workaround

Same reason as cycles 1 and 2: detection complete, auto-resolution
minimal. Three identical reviews are stronger evidence to the
Analyst than three silent passes that masked the bug.

---

Pushed `feature/overplot-refresh` with this todo.md and
`review/overplot-refresh` tag per orchestration.md §8 allowlist.
Deleted `qa/overplot-refresh` (local + remote) per consume-and-
delete contract.
