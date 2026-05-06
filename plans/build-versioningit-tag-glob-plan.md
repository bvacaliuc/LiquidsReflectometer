# Plan: build-versioningit-tag-glob — versioningit consumes protocol-internal `qa/*` tag

**Slug:** `build-versioningit-tag-glob`
**Effort:** `new_workflow-repairs-2026-04`
**Base branch:** `new_workflow_ui_plan`
**Plan revision:** v1 (initial)

**Origin.** Surfaced by the Integrator on cycle 1 of `cd-dialog-resize`
(`feature/cd-dialog-resize:todo.md` at SHA
`f4e057fdaeadd10949ccb2ca3fdc053704b5729c`). This is **not** a UI
defect from the original `issues.md` defect set — it is an
orchestration-wide build-side blocker discovered at runtime. Adding
it as a new slug is permitted by `issues.md` §"How the Analyst uses
this file" ("If the reported defect list changes mid-effort,
update this file on the analysis branch so future revisions work
from a single source of truth.").

## Symptom

`pixi run test-reduction` (and any pixi task that depends on the
editable install) fails during environment preparation, **before any
test is collected**, with:

```
versioningit.errors.InvalidVersionError: Error getting the version from
source `versioningit`: Cannot parse version 'qa/cd-dialog-resize'
[WARNING ] versioningit: Version extracted from tag 'qa/cd-dialog-resize'
            is not PEP 440-compliant
```

This blocks the Integrator's test cycle for **every** slug the
Developer pushes a `qa/{slug}` tag for — i.e. every initial
implementation in this orchestration. Without the fix, no
`qa/{slug}` tag will ever produce a passing build.

## Verified root cause

`pyproject.toml` declares:

```toml
[tool.versioningit.vcs]
method = "git"
default-tag = "0.0.1"
```

There is **no `match` (or `exclude`) glob.** versioningit's underlying
call therefore reduces to `git describe --tags HEAD` with no filter,
which returns whichever tag is closest to HEAD — including the
protocol's lightweight `qa/{slug}` tag pushed at the feature-branch
HEAD by the Developer (per orchestration.md §6 Developer loop).
Because `qa/cd-dialog-resize` is not PEP 440-compatible,
versioningit's parser throws `InvalidVersionError` and hatchling's
`build_editable` aborts.

Direct evidence (collected by the Integrator on cycle 1 and re-verified
by the Analyst on `analysis/new_workflow-repairs-2026-04` tip):

```
$ git describe --tags HEAD                                  # at qa/cd-dialog-resize tip
qa/cd-dialog-resize

$ git describe --tags --exclude='qa/*' --exclude='review/*' \
                       --exclude='triage/*' HEAD            # would-be after-fix
v2.9.0rc3-101-g78ea717
```

The history is healthy; the breakage is entirely the
protocol-tag-namespace ↔ versioningit-default-glob interaction.

## Files to change

| File | Lines | Change |
|---|---|---|
| `pyproject.toml` | the `[tool.versioningit.vcs]` block (currently 50-52) | Add a `match` filter that selects only release tags (`v[0-9]*`). |

**Resulting block:**

```toml
[tool.versioningit.vcs]
method = "git"
default-tag = "0.0.1"
match = ["v[0-9]*"]
```

That is the entire functional change — one new line.

### Why `match` and not `exclude`

`versioningit`'s `[tool.versioningit.vcs]` accepts both `match` and
`exclude`; either works to skip protocol tags, but `match` is the more
robust choice:

- **`match = ["v[0-9]*"]`** — *positive* allow-list. Only tags that
  look like release versions are eligible. Any future
  protocol-internal namespace (e.g. `dry-run-*` from a rehearsal,
  `init-check-*` from Initialization, or a brand-new orchestration
  ref pattern not yet invented) is automatically excluded. This is
  *detection complete* per `[ALWAYS] Design framing` — every
  non-release tag is filtered, not just the four currently in use.
- **`exclude = ["qa/*", "review/*", "triage/*", "analysis/*", ...]`** —
  *negative* deny-list. Captures the four current protocol prefixes
  but leaves any future prefix open. Less robust; would need
  amendment whenever the protocol grows a new ref namespace.

The user's standing `[ALWAYS] Design framing` rule (robust over
simple, detection complete) prefers the positive allow-list.

## Failure-mode matrix

| Case | Expected behavior |
|---|---|
| HEAD reachable from a `v*` release tag (normal case) | versioningit resolves the version correctly via `git describe --tags --match='v[0-9]*'` (e.g. `v2.9.0rc3-101-g78ea717`); build succeeds |
| HEAD has no reachable `v*` tag (very early commit, or a brand-new long-running branch) | versioningit falls back to `default-tag = "0.0.1"`; build succeeds with a sentinel version |
| HEAD has a `qa/*`, `review/*`, `triage/*`, or `analysis/*` tag (protocol cycle) | The protocol tag is now invisible to versioningit; the most recent `v*` tag wins; build succeeds |
| Future protocol introduces a new ref pattern (e.g. `qa-dry-run/*`) | Still excluded by the positive allow-list; build succeeds |
| Tag is a pre-release like `v2.9.0rc3` (PEP 440 valid) | `match=["v[0-9]*"]` accepts it (`v2` starts with `v` followed by a digit); versioningit normalises the rc segment; build succeeds |
| Maintainer cuts a non-numeric release tag (e.g. `release-2.9`) | `v[0-9]*` does NOT match; versioningit falls back to `default-tag`. Project would need to adjust the glob; document this as a known constraint |
| Empty repo / no tags | `default-tag = "0.0.1"` already covers this case; no regression |
| `pixi run sync-version` (the canonical exercise of the same versioningit code path) | Works after the fix; before the fix it fails with the same error as the test build |

## Red-Green TDD seed

This is a **build-system** change rather than a Python-code change,
so the test discipline is *invocation-level*, not pytest-level. The
Developer adds two distinct verifications:

1. **Pre-fix RED proof (one-shot, captured in commit message — not a
   committed test):** at the head of `feature/build-versioningit-tag-glob`,
   *before* the `pyproject.toml` edit, push a synthetic
   `qa/build-versioningit-tag-glob-redproof` lightweight tag at HEAD,
   run `pixi run sync-version`, and confirm the exit-1 with
   `InvalidVersionError`. Delete the synthetic tag immediately.
   Capture the failing output as evidence in the commit body — this
   is the RED that the GREEN below removes.

2. **Post-fix GREEN, captured as a checked-in script-style test under
   `tests/test_versioningit_config.py`:** a pytest-level test that
   *parses the configured `match` glob* and asserts:
   - `pyproject.toml`'s `[tool.versioningit.vcs]` has a `match` key.
   - The `match` value is a list containing `"v[0-9]*"`.
   - A subprocess invocation of
     `git describe --tags --match='v[0-9]*' HEAD` exits 0 (i.e. the
     glob actually matches *something* in the current repo's tag
     pile).

```python
# tests/test_versioningit_config.py — RED (file does not exist) → GREEN
import re
import subprocess
import tomllib  # py3.11+; or tomli on older

def test_versioningit_match_glob_present():
    """The protocol-internal tag namespace (qa/*, review/*, triage/*,
    analysis/*) must be invisible to versioningit. The robust way is
    a positive 'match' allow-list pinned to release tags."""
    with open("pyproject.toml", "rb") as fh:
        cfg = tomllib.load(fh)
    vcs = cfg["tool"]["versioningit"]["vcs"]
    assert "match" in vcs, (
        "[tool.versioningit.vcs].match is required so versioningit "
        "ignores protocol-internal qa/*, review/*, triage/*, "
        "analysis/* tags. See plans/build-versioningit-tag-glob-plan.md."
    )
    assert any("v" in g and "[0-9]" in g for g in vcs["match"]), (
        f"Unexpected match glob: {vcs['match']!r}; expected something "
        f"like ['v[0-9]*']."
    )

def test_versioningit_match_glob_finds_release_tag():
    """Sanity: the configured glob actually matches at least one tag
    in this repo's history. Catches a future glob typo."""
    out = subprocess.run(
        ["git", "describe", "--tags", "--match=v[0-9]*", "HEAD"],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, (
        f"git describe --match='v[0-9]*' failed: {out.stderr!r}. "
        f"Either no v* release tags are reachable from HEAD or the "
        f"glob is wrong."
    )
    assert re.match(r"^v\d+", out.stdout), (
        f"Unexpected git describe output: {out.stdout!r}"
    )
```

These tests exercise the *configuration*, not versioningit's
internals — they pass under any future versioningit version that
honours `match` and stay green when more release tags are added.

## Acceptance

The Developer's `feature/build-versioningit-tag-glob` branch must:

1. Pass both new tests in `tests/test_versioningit_config.py`.
2. Reproduce the original RED case in the commit body (see the
   Red-Green TDD seed above).
3. Pass `pixi run test-reduction` end-to-end with the **synthetic
   `qa/build-versioningit-tag-glob` tag pushed by the Developer at
   the feature HEAD** — this is the live demonstration that the fix
   resolves the systemic issue. (The Integrator's normal cycle does
   the qa-tag push for free; if that build succeeds, this acceptance
   is satisfied.)
4. Not introduce any other change in `pyproject.toml`, `pixi.lock`,
   or anywhere else. The diff is a single line; the PR is intended
   to be small and merge-fast precisely so it can unblock the rest
   of the orchestration.

## Notes for the Integrator

- This is the **smallest** triage in the effort by file count and
  diff size (1 file, 1 line). Land it first when picking up the
  Developer's qa tag.
- Once this PR is merged into `{base-branch}`, all subsequent
  `feature/{slug}` branches that the Developer creates from
  `{remote}/{base-branch}` will inherit the fix. The remaining
  `cd-dialog-resize`, `settings-persistence`, `overplot-axes`, and
  `overplot-refresh` cycles will then build cleanly without any
  per-slug build patch.
- `cd-dialog-resize` v2 (parallel cycle) is amended to *also* apply
  the same `pyproject.toml` patch on its feature branch so it
  unblocks even before this PR is merged — this is intentional
  duplication. When both PRs eventually merge, the duplicate
  pyproject change in cd-dialog-resize is a no-op against the
  fixed base.

## Cross-references

- `~/.claude/CLAUDE.md` `[ALWAYS] Design framing` — robust over
  simple; detection complete (positive allow-list excludes any
  future protocol-internal tag namespace).
- `setup/patterns/build-and-tooling.md` — Python build-system
  conventions in this codebase.
- `plans/cd-dialog-resize-plan.md` "## Revision history" v2 entry —
  references this slug as the systemic fix.
- `feature/cd-dialog-resize:todo.md` at SHA `f4e057f` — the
  Integrator's analysis that surfaced this issue, including the
  ranked-hypothesis text and the direct evidence run (kept on the
  feature branch as historical record).
- versioningit `match` documentation:
  https://versioningit.readthedocs.io/en/stable/configuration.html#the-vcs-section
