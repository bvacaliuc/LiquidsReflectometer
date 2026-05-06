# todo.md — overplot-axes, Integrator cycle 1

**Verdict:** infrastructure failure — **same systemic root cause as
`cd-dialog-resize` cycle 1** (see that branch's `todo.md` for the
full diagnosis). Both runs (initial + post-`__pycache__`-clean retry)
exited 1 during environment preparation, before pytest collection.

This is now **two data points** for the same protocol↔versioningit
interaction. The fix is project-side and load-bearing for every
remaining slug in this effort.

## Failing tests

None. Environment build failed before pytest collection.

## Exact error (both runs)

```
versioningit.errors.InvalidVersionError: Error getting the version from
source `versioningit`: Cannot parse version 'qa/overplot-axes'
```

(The qa-tag name in the error is the only thing that differs from
cd-dialog-resize cycle 1 — slug-named, but same hatchling /
versioningit traceback.)

## Root cause (re-stated; cross-reference)

`pyproject.toml:50-52` declares `[tool.versioningit.vcs]` with no
`match` filter, so versioningit's underlying `git describe --tags
HEAD` accepts the protocol's lightweight `qa/{slug}` tag — which the
Developer pushes at the feature HEAD by design. Verified on this
branch:

```
$ git describe --tags HEAD
qa/overplot-axes

$ git describe --tags --exclude='qa/*' --exclude='review/*' HEAD
v2.9.0rc3-101-g78ea717   # PEP 440-compliant; would build cleanly
$ # (HEAD reachable from same v2.9.0rc3 base as feature/cd-dialog-resize)
```

Identical structural defect to cycle 1.

## Recommended fix (unchanged from cd-dialog-resize todo.md)

Edit `pyproject.toml:50-53`:

```toml
[tool.versioningit.vcs]
method = "git"
default-tag = "0.0.1"
match = ["v[0-9]*"]
```

This MUST land on `{base-branch}` (or be merged into every active
`feature/{slug}`) before any `qa/{slug}` will produce a passing
build. See `feature/cd-dialog-resize:todo.md` for the longer
discussion of "standalone fix slug vs. coupled scope-creep" and for
the local-validation procedure.

## What changes for the Analyst this round

Cycle 1 left this as a single data point (could plausibly be unique
to one branch's history). This second cycle on a structurally
unrelated feature branch (`overplot-axes` modifies
`launcher/apps/overplot.py`, not `direct_beam.py`) **proves the
issue is protocol-systemic, not branch-specific**. Recommended
Analyst action:

1. Spin a standalone slug (`triage/build-versioningit-tag-glob` or
   similar) whose plan is the 1-2 line `pyproject.toml` fix above.
2. Land its PR to `{base-branch}` first — it unblocks every other
   slug (`overplot-refresh`, `settings-persistence`, both
   already-pending in `triage/`).
3. After merge, the Developer rebases / re-tags the existing
   `qa/cd-dialog-resize`, `qa/overplot-axes` and any others queued.
   Each re-tag is a new (SHA, ref-name) tuple per the dedup contract
   (orchestration.md §6 / `poll-wrapper-Integrator.sh` line 122),
   so the Integrator's poller picks them up on the next cycle.

Alternatively, fold the fix into each existing `triage/{slug}` plan,
but that bundles unrelated scope into every UI fix and is harder to
revert if it surfaces issues.

## Why I am not auto-deleting the local qa/* tag as a workaround

Same reason as cd-dialog-resize cycle 1: deleting the local qa tag
to make the build succeed would mask the bug from the Analyst on
every subsequent cycle and silently violate the "robust over
simple" framing — detection must be complete; auto-resolution can
be minimal (per `~/.claude/CLAUDE.md` `[ALWAYS] Design framing`).

---

Pushed `feature/overplot-axes` with this todo.md and
`review/overplot-axes` tag per orchestration.md §8 allowlist.
Deleted `qa/overplot-axes` (local + remote) per the consume-and-
delete contract.
