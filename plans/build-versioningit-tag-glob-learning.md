# Learning: protocol tag namespaces vs. build-system version derivation

**Source slug:** `build-versioningit-tag-glob` (cycle 1, this effort)

## Rule

When a project uses `versioningit` (or any tool that calls
`git describe --tags HEAD`) to derive its package version, **always pin
the tag glob to release tags only**. The protocol-internal tag
namespaces this orchestration uses (`qa/*`, `review/*`, `triage/*`,
`analysis/*`, `init-check/*`) are not PEP 440 compliant and the build
will refuse to install in editable mode the moment one is reachable
from `HEAD`.

The robust expression of the rule, in `pyproject.toml`:

```toml
[tool.versioningit.vcs]
method = "git"
default-tag = "0.0.1"
match = ["v[0-9]*"]   # positive allow-list, not exclude
```

## Why

* **Why a single dirty tag breaks the whole pipeline.** The Developer
  pushes `qa/{slug}` at the feature-branch HEAD by design (orchestration
  §6, §8 allowlist). `git describe --tags HEAD` with no filter returns
  whichever tag is closest to `HEAD`, which is the freshly-pushed
  `qa/{slug}`. versioningit then tries to parse that as a version,
  raises `InvalidVersionError`, and `hatchling.build_editable` aborts
  during `pixi install`. **No test ever runs.** The Integrator on cycle
  1 of `cd-dialog-resize` hit this and escalated as a new slug rather
  than fight it slug-by-slug.

* **Why `match` (positive) and not `exclude` (negative).** Per
  `~/.claude/CLAUDE.md` `[ALWAYS] Design framing`: detection complete,
  not just the four current cases. A future protocol that adds (e.g.)
  `qa-dry-run/*` is automatically excluded by `match=["v[0-9]*"]`; an
  exclude-list would silently accept it and fail again.

* **Why this is a cross-project pattern.** Any agentic protocol that
  uses git tags to signal work-item state (qa, review, triage, etc.)
  on the **same SHA the build derives its version from** will hit
  this. Build tools that consult `git describe`:
  * `versioningit` (this case).
  * `setuptools_scm` (same `git describe` underneath; the equivalent
    fix is `tag_regex` or `version_scheme="post-release"` plus
    `local_scheme="no-local-version"`).
  * Any custom hatchling/setup.py that calls `git describe` directly.

  The mitigation is the same in all cases: pin to release tags by glob
  or regex; never let a non-version tag into the description path.

## How to apply

1. **In any project that uses `versioningit` AND is targeted by this
   orchestration** (or any successor protocol that pushes annotated
   or lightweight tags into the working repo):
   * Audit `pyproject.toml`'s `[tool.versioningit.vcs]` block.
   * If `match` is missing, add `match = ["v[0-9]*"]` (or whatever
     glob matches the project's release-tag convention — adjust for
     `release-1.0`-style schemes that don't begin with `v`).
   * Confirm with: `git tag {arbitrary protocol tag} HEAD; pixi run
     python -c 'import versioningit; print(versioningit.get_version("."))';
     git tag -d {tag}`. Successful output ⇒ the protocol tag is
     filtered.

2. **For setuptools_scm-based projects**, the equivalent is:

   ```toml
   [tool.setuptools_scm]
   tag_regex = "^v(?P<version>\\d.*)$"
   ```

3. **For any orchestration that designs a new tag namespace**, treat
   "does this tag namespace get exposed to `git describe --tags`?" as
   a first-class question of the design. If yes, reach for the
   positive allow-list at the build-tool layer; do not rely on the
   tag namespace being "obviously not a version" to keep the parser
   happy.

## Out of scope here

Whether `qa/`, `review/`, `triage/`, `analysis/` should themselves be
namespaced under `protocol/qa/...` etc. for additional clarity. That
is an orchestration-design question; the build-side fix is
independently necessary regardless.
