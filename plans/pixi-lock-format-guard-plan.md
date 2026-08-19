# Plan: pixi-lock-format-guard

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` · charter §9
**amendment 14** / §4 mid-effort addition (2026-08-18, human-ratified) ·
DAG-independent
**Retry attempt:** 1

Review domains: design-reviewer (advisory). No GUI surface.

## Symptom

`pixi.lock` must stay lock-format **`version: 6`** until analysis.sns.gov's
pixi is upgraded: format v7 (pixi 0.68.0, 2026-05-07) is unreadable by
pre-0.68 pixi, and no newer pixi can write v6. Amendment 14 pins the dev
machines (uvdl3 → 0.67.2, done), but nothing repo-side stops an unpinned
machine (node23-class fresh installs, a maintainer's laptop) from silently
flipping the format — S0 demonstrated exactly that (12,235-line v7 rewrite;
the human hand-reverted in `a4ae8b8`). Worse, the repo's own
`pixi-lock-check` pre-push hook runs `pixi lock --check`, which **writes
despite its name**: on ≥0.68 it converts v6→v7 and exits 0; measured on
0.67.2 (2026-08-18, Analyst) it still re-stamps the editable self-package
record (versioningit timestamp `dev20260610…+gf5b8e45` →
`dev20260819…+ga4ae8b8`, and drops `editable: true` while the installed env
verifiably stays editable) and exits 0 — every push dirties the tree.

## Verified state (against `agentic/exp` @ `a4ae8b8`, 2026-08-18)

- `.pre-commit-config.yaml`: `pixi-lock-check` is a `repo: local`,
  `language: system` hook, `stages: [pre-push]`, entry
  `bash -c "PATH=$HOME/.pixi/bin:$PATH pixi lock --check"`; pre-commit.ci
  skips it (`ci: skip: [pixi-lock-check]`).
- `.github/workflows/test_and_deploy.yml`: three
  `prefix-dev/setup-pixi@v0.9.4` steps (lines 33/83/122), **no
  `pixi-version` pin** — CI floats to latest (reads v7; never commits).
- `pixi.lock` first line: `version: 6`. `pyproject.toml:111-112`:
  `lr_reduction = { path = ".", editable = true }`.
- The repo's `scripts/` directory is excluded from pre-commit's file
  checks (`exclude:` glob) — a hook helper script there is not linted by
  ruff, which is acceptable for bash.
- Measured 0.67.2 behavior (Analyst, this clone): `pixi lock --check` on
  the committed lock → exit 0, file mutated (self-package stamp), lock
  stays v6; `pixi run python -c "import lr_reduction"` resolves to `src/`
  (editable intact).

## Files to change (on `feature/pixi-lock-format-guard` from `agentic/exp`)

1. **`scripts/pixi_lock_check.sh`** — new, mode 755; the non-mutating
   wrapper the pre-push hook will call:

   ```bash
   #!/usr/bin/env bash
   # pixi lock --check is not read-only (charter amendment 14, campaign
   # exp-settings-roi): even at exit 0 it re-stamps the editable
   # self-package record, and on pixi >= 0.68 it would rewrite the whole
   # lock to format v7. Snapshot and restore any mutation the check makes
   # so a push never dirties the tree; the exit code is still the check.
   set -u
   PATH="$HOME/.pixi/bin:$PATH"
   snap=$(mktemp) && cp pixi.lock "$snap"
   pixi lock --check
   rc=$?
   if ! cmp -s pixi.lock "$snap"; then
       cp "$snap" pixi.lock
       echo "pixi-lock-check: restored pixi.lock (the check mutated it)"
   fi
   rm -f "$snap"
   exit $rc
   ```

2. **`.pre-commit-config.yaml`** — two edits in the `repo: local` block:
   - New hook **before** `pixi-lock-check`:

     ```yaml
     - id: pixi-lock-format
       name: pixi-lock-format (lock stays v6 — analysis.sns.gov pixi < 0.68)
       entry: bash -c "head -1 pixi.lock | grep -qx 'version: 6' || { echo 'pixi.lock is not lock-format v6; the facility pixi cannot read v7 (charter amendment 14)'; exit 1; }"
       language: system
       always_run: true
       pass_filenames: false
       stages: [pre-commit, pre-push]
     ```

   - `pixi-lock-check`'s entry becomes
     `bash scripts/pixi_lock_check.sh` (same `stages: [pre-push]`,
     `language: system`). Add `pixi-lock-format` to the `ci: skip:` list
     alongside `pixi-lock-check`? **No** — leave it running on
     pre-commit.ci: it is pure shell, cheap, and guards autoupdate PRs
     too. Only `pixi-lock-check` (needs pixi) stays skipped.

3. **`.github/workflows/test_and_deploy.yml`** — add
   `pixi-version: v0.67.2` to the `with:` block of all three
   `prefix-dev/setup-pixi@v0.9.4` steps (CI then exercises exactly the
   toolchain the repo is pinned to; today's floating install is a silent
   skew). Match the file's existing `with:` indentation.

**Explicitly NOT in this slug** (recorded so nobody adds them):
- `requires-pixi = ">=0.39,<0.68"` in `[tool.pixi.workspace]` — deferred
  until the human reports analysis.sns.gov's `pixi --version` (if the
  facility pixi predates the field it may reject the manifest; and the cap
  errors CI unless the CI pin lands first — this slug lands that pin).
- Regenerating `pixi.lock` — the committed splice is validated working
  (S0 gate 2+107 green, editable env verified); the self-package stamp
  refreshes on the next dependency-touching slug under the pinned pixi.
- Any lock content change at all: **this slug's diff must not touch
  `pixi.lock`.**

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Unpinned machine regenerates lock as v7 and commits (common, off-uvdl3) | `pixi-lock-format` fails at pre-commit AND pre-push | tripwire hook (both stages, always_run) |
| Push mutates the tree via `pixi lock --check` (common, every push today) | wrapper detects via snapshot compare | exact-restore (`cp` back, not `git checkout` — preserves any deliberate uncommitted lock edits) |
| Genuine manifest/lock drift at push (edge) | wrapper preserves the check's exit code | push blocked; rc semantics verified by injection (below) |
| `pixi lock --check` exits 0 on genuine drift (pathological — would make the hook vacuous) | the injection test below observes it | if observed: record in todo.md via the review loop — the hook then needs `--check`'s rc replaced by an explicit diff test; do not silently accept |
| pre-commit.ci autoupdate flips the lock (edge) | `pixi-lock-format` runs on ci (not skipped) | fails the autoupdate PR loudly |
| CI floats to a pixi with new behavior (edge) | CI pinned v0.67.2 | drift becomes a deliberate bump |
| Facility upgrades pixi ≥0.68 later (planned) | amendment 14 exit ramp | remove pin+guard+CI pins in ONE commit (todo) |

## Red-Green verification (hooks/config — failure-injection, not pytest)

Record every transcript in the commit bodies:

1. **Format tripwire** — RED: `sed -i '1s/.*/version: 7/' pixi.lock;
   pre-commit run pixi-lock-format --all-files` → hook FAILS;
   `git checkout -- pixi.lock`. GREEN: same command on the real lock →
   passes.
2. **Wrapper restore** — `pre-commit run pixi-lock-check --hook-stage
   pre-push --all-files` → exit 0, "restored pixi.lock" line printed,
   `git status --porcelain pixi.lock` empty afterward.
3. **Genuine-drift rc probe** — append a junk dependency to
   `[tool.pixi.feature.developer.dependencies]` (uncommitted), run the
   wrapper → EXPECT nonzero exit (push would be blocked) and an unchanged
   committed lock; revert pyproject. If exit is 0, see the pathological
   row above — flag, do not ship a vacuous check silently.
4. `bash -n scripts/pixi_lock_check.sh` clean; `pixi run pre-commit
   run --all-files` clean; `pixi run test-reduction` green (hooks must
   not affect tests).

## Acceptance criteria

- All four verification transcripts recorded; hook order in the config is
  format-check first, then the wrapped `pixi-lock-check`.
- Diff touches exactly `scripts/pixi_lock_check.sh`,
  `.pre-commit-config.yaml`, `.github/workflows/test_and_deploy.yml` —
  and NOT `pixi.lock`.
- `pixi run test-reduction` green; draft PR body states the CI-pin
  consequence (workflow runs now install pixi v0.67.2) and cites
  amendment 14.
