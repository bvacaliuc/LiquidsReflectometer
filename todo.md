# todo.md — cd-dialog-resize, Integrator cycle 1

**Verdict:** infrastructure failure (not a code-test failure). Both
the initial run and the protocol-prescribed retry (after
`__pycache__` clean) failed identically before any test could be
collected, with `pixi run test-reduction` exiting 1 during
environment preparation.

The root cause is **systemic to this protocol** and will repro on
every slug for every Developer cycle until fixed — the
`feature/{slug}` HEAD and the protocol's `qa/{slug}` lightweight
tag share a SHA by design (Developer tags qa at the feature tip),
and `versioningit` describes that SHA as the most recent reachable
tag. So this is escalated to the Analyst now rather than retried
further.

## Failing tests

None. The environment build failed before pytest collection.

## Exact error (from `pixi run test-reduction`, both runs)

```
✨ Pixi task (test-launcher in default): python -m pytest -vv launcher/tests/: (Run launcher UI tests (headless Qt))
Error:   × Failed to update PyPI packages for environment 'default'
  ├─▶ Failed to prepare distributions
  ├─▶ Failed to build `lr-reduction @ file:///media/ssd2/Projects/Claude/3/lr_reduction`
  ├─▶ The build backend returned an error
  ╰─▶ Call to `hatchling.build.build_editable` failed (exit status: 1)

      [WARNING ] versioningit: Version extracted from tag 'qa/cd-dialog-resize'
                  is not PEP 440-compliant
      ...
      versioningit.errors.InvalidVersionError: Error getting the version from
      source `versioningit`: Cannot parse version 'qa/cd-dialog-resize'
```

Note: `test-reduction` chains into `test-launcher` first via
`depends-on = ["test-launcher"]` (`pyproject.toml:166`), so the
build error surfaces from the launcher step before reduction tests
are even reached.

## Hypotheses ranked by likelihood

### H1 (most likely; supported by direct evidence) — versioningit consumes the `qa/*` lightweight tag because `[tool.versioningit.vcs]` lacks a tag filter

`pyproject.toml:50-52` declares:

```toml
[tool.versioningit.vcs]
method = "git"
default-tag = "0.0.1"
```

There is **no `match` (or `exclude`) glob**, so versioningit's
underlying `git describe --tags HEAD` accepts any tag, including
the protocol's lightweight `qa/{slug}` tag pushed at the feature
HEAD. Direct evidence:

```
$ git describe --tags HEAD
qa/cd-dialog-resize

$ git describe --tags --exclude='qa/*' --exclude='review/*' HEAD
v2.9.0rc3-101-g78ea717        # PEP 440 compliant; would build cleanly
```

This will repro for every `qa/{slug}` the Developer pushes — every
cycle of every issue in `issues.md` — until versioningit is
configured to ignore protocol-internal tags.

**Recommended fix (project-side, on `{base-branch}` or via the
`triage` plan revision):** add a `match` filter to
`[tool.versioningit.vcs]`:

```toml
[tool.versioningit.vcs]
method = "git"
default-tag = "0.0.1"
match = ["v[0-9]*"]
```

This makes versioningit consider only release tags
(`v2.0.1`, `v2.9.0rc3`, etc.) and is the canonical way to scope
versioningit's tag search. See
https://versioningit.readthedocs.io/en/stable/configuration.html#the-vcs-section
for the `match` semantics (passed to `git describe --match=…`).

This fix is **load-bearing for the whole orchestration**: without
it, no `qa/*` tag will ever produce a passing build on this branch.

### H2 (unlikely; ruled out by H1 evidence) — pre-existing unrelated `versioningit` breakage on `{base-branch}`

`git describe --tags --exclude='qa/*' --exclude='review/*' HEAD`
yields a clean PEP 440-compatible version (`v2.9.0rc3-101-g78ea717`),
so the underlying VCS history is healthy. The breakage is entirely
attributable to the protocol's tag scheme intersecting versioningit's
default tag-glob behaviour.

### H3 (unlikely; ruled out by error message) — editable build broken for another reason (mantid, conda channel, native extension)

The hatchling traceback terminates squarely in
`metadata.core:_get_version` with `InvalidVersionError`. No native
build, no Mantid import, no channel-resolve step is involved. If the
version were resolvable, the build would proceed.

## Suggested next investigation steps for the Analyst

Order by *cheapness to verify* (not by likelihood — H1 is already
nailed by the evidence above).

1. **Validate H1 locally on a fresh checkout (1 min):**
   ```bash
   cd lr_reduction
   git checkout new_workflow_ui_plan
   git fetch agentic refs/tags/qa/cd-dialog-resize
   # without fix:
   git describe --tags HEAD                    # expect: qa/cd-dialog-resize
   # apply the fix in pyproject.toml as above
   git describe --tags --match='v[0-9]*' HEAD   # expect: v2.9.0rc3-101-…
   pixi run sync-version                        # exercises the same code
                                                #  path as the build
   ```

2. **Encode the fix into a small triage plan amendment.** This is a
   `pyproject.toml`-only change (1-2 lines added). It is independent
   of the cd-dialog-resize UI change, but it must land on
   `{base-branch}` (or be merged into `feature/cd-dialog-resize`)
   before any qa tag will pass. Two paths:
   - **(preferred)** A standalone `triage/build-versioningit-tag-glob`
     slug that lands the `pyproject.toml` fix on its own
     `feature/build-versioningit-tag-glob` branch. PR it to
     `{base-branch}` first; subsequent UI slugs branch off the
     fixed `{base-branch}`.
   - **(coupled)** Add the `pyproject.toml` change to the
     cd-dialog-resize triage plan as scope creep. Smaller diff but
     bundles unrelated scope into a UI fix.

3. **Confirm whether other long-lived feature branches are affected.**
   `git describe --tags HEAD` on `feature/add-pytest-html` (the only
   other feature branch on the remote) will tell you whether the
   issue is triggered only by `qa/*` tags or by any non-`v*` tag.

4. **Write a `plans/cd-dialog-resize-learning.md`** capturing this
   protocol↔versioningit interaction so future efforts on this
   project don't rediscover it (per orchestration.md §6 Developer
   loop, "if cross-project learnings found: write
   plans/{slug}-learning.md"). Suggested filename and one-line
   summary:
   ```
   plans/cd-dialog-resize-learning.md
   "versioningit's default tag-glob accepts protocol-internal
    `qa/*` and `review/*` tags; the `match = ['v[0-9]*']` filter
    in `[tool.versioningit.vcs]` is required for any orchestration
    that pushes non-`v*` tags."
   ```

## Why no `--timeout=2` infrastructure-fail probe was applied

The opening prompt's infrastructure-failure path mentions
`--timeout=2` for the dry-run delta scenario. That path is for a
test-runtime probe that exercises pytest-timeout. Here the failure
is **before pytest is invoked** (build-stage versioningit error),
so a `--timeout=…` probe has no surface to act on. Cleaning
`__pycache__` between runs (the only protocol-level retry hook
that's applicable to a build-stage failure) was performed; no
change.

## What I am NOT doing (out of Integrator scope)

- I am NOT modifying `pyproject.toml` from the Integrator session.
  That is a code change requiring the Analyst's plan and the
  Developer's TDD cycle.
- I am NOT deleting the local `qa/cd-dialog-resize` tag as a
  workaround to make tests pass under this Integrator session. That
  would mask the bug from the Analyst on every subsequent cycle and
  silently violate the "robust over simple" framing.

---

Pushed `feature/cd-dialog-resize` with this todo.md and
`review/cd-dialog-resize` tag per orchestration.md §8 allowlist.
Deleted `qa/cd-dialog-resize` (local + remote) per the consume-and-
delete contract.
