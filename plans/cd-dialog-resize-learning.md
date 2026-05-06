# Learning: cd-dialog-resize cycle 1 retry — versioningit tag glob

**Source slug:** `cd-dialog-resize` (cycle 1 → v2 retry, this effort)

## Rule

versioningit's default tag-glob accepts every reachable tag, including
protocol-internal lightweight tags (`qa/*`, `review/*`, `triage/*`,
`analysis/*`).

## Why

The default `git describe --tags HEAD` invocation has no `--match`
filter, so any non-PEP-440 tag at HEAD breaks
`hatchling.build.build_editable`. Found on cycle 1 of `cd-dialog-resize`
2026-05-05; cost the orchestration one full
Developer→Integrator→Analyst retry cycle.

## How to apply

Any project using versioningit + this orchestration MUST set
`[tool.versioningit.vcs] match = ["v[0-9]*"]` (or equivalent positive
allow-list) before running the protocol. Add this check to the
Initialization agent's §11 (Target-branch dependency verification) for
future efforts.

## Cross-reference

The canonical, fuller treatment of this rule (including why a
positive allow-list is preferred over an exclude list, the
setuptools_scm equivalent, and the build-system-tooling implications)
lives in `plans/build-versioningit-tag-glob-learning.md` on this same
branch. This file exists to satisfy `cd-dialog-resize-plan.md`'s v2
revision-history acceptance addendum without duplicating the
explanation.
