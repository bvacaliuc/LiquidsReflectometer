# Plan: pixi-lock-format-guard

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` · charter §9
**amendment 14** / §4 mid-effort addition (2026-08-18, human-ratified) ·
DAG-independent
**Retry attempt:** 3 (final — N=3; the next rejection escalates. The v2
gate's own read: a converging slug, both new findings six lines apart in
one fix — but the last retry lands the trap rewrite WITH the plan
correction, not ahead of it.)

Review domains: design-reviewer (**blocking** — upgraded at the v1
rejection, same logic the harness slug ratified: when the slug's entire
deliverable is a guard, the domain that judges whether the guard guards
must gate it). No GUI surface.

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

## Revision history

### v2 — 2026-08-19 (after v1 rejection; todo.md @ `3c1808b`)

Gate green; rejection entirely from review. The Integrator departed
from v1's advisory declaration and the **Analyst upholds it** (domains
line upgraded): three findings show the guard permitting, causing, or
instructing the harm it exists to prevent — the drift failure message
tells a ≥0.68 user to run `pixi lock` (the v7 rewrite itself,
reproduced); the missing-lock path fails OPEN and writes a 0-byte
`pixi.lock` in the cwd (no repo-root or file assertion; reproduced from
a subdirectory, and with real pixi the parent-dir manifest search makes
it rewrite the REAL lock while restoring nothing); no `trap`, so an
interrupt during the network solve — an everyday event this commit's
own body reports hitting — leaves the tree converted to v7 with the
snapshot lost in an anonymous tmp file. B4 is the campaign's
stated-vs-measured class in a new costume: the script comment asserts
as "Measured on 0.67.2" a drift-rc experiment the SAME commit's body
says was never completed. Two v1-Developer judgment calls are ratified
and must survive v2 unchanged: exact-`cp` restore (never
`git checkout`), and content-based drift classification (never trust
the unverified rc). **Framing decision (the gate asked for one): this
guard's contract is "a push never carries a non-v6 lock" — achievable;
"the tree is never dirty" is NOT the contract** (everyday pixi
activity restamps; amendment 14's restore-don't-stage discipline covers
that) — the script header and comments must say so.

## v2 fixes (the gate's order; all reviewer-verified)

1. **B2 + B3 (~4 lines, the fail-open and the interrupt hole):** at the
   top —

   ```bash
   cd "$(git rev-parse --show-toplevel)" || exit 1
   [ -f pixi.lock ] || { echo "pixi-lock-check: no pixi.lock at repo root (fail closed)"; exit 1; }
   snap=$(mktemp) || exit 1
   trap 'cp "$snap" pixi.lock 2>/dev/null; rm -f "$snap"' EXIT INT TERM
   cp pixi.lock "$snap" || exit 1
   ```

   *(**Superseded by v3** — this ordering arms the restore trap over the
   still-empty mktemp file: any exit before the `cp` populates it copies
   emptiness onto the tracked lock. The v2 gate reproduced repo-root
   truncation from it. See the v3 entry for the corrected form.)*

   With the EXIT trap owning restore+cleanup, delete the end-of-script
   restore/rm so there is exactly one restore path. Re-run the interrupt
   injection (kill mid-check → tree byte-identical, no tmp litter) and
   the subdirectory injection (immediate loud failure, no file created).
2. **B1:** immediately after `pixi lock --check`, branch on
   `head -1 pixi.lock | grep -qx 'version: 6'` BEFORE any generic drift
   handling; the v7 branch restores from the snapshot and fails with:
   "your pixi wrote lock-format v7 — analysis.sns.gov pixi (< 0.68)
   cannot read it. Do NOT commit this lock; pin instead:
   `pixi self-update --version 0.67.2`". The generic drift message
   loses the "run 'pixi lock' and commit" instruction — replace with
   "regenerate UNDER A ≤0.67.x PIXI and commit" wording.
3. **B4:** rewrite the header comment to the honest record: the restamp
   at exit 0 IS measured (0.67.2, twice, plus the campaign's live
   observations); the rc under genuine drift is **UNVERIFIED** (three
   probe attempts, three different walls — cite the v1 commit body) —
   and that uncertainty is itself the justification for content-based
   classification. Never state an untaken measurement as taken.
4. **Reach the machines that need it (promoted advisory):** a two-line
   format check step BEFORE the first `setup-pixi` in each workflow job
   that touches the lock (`head -1 pixi.lock | grep -qx 'version: 6' ||
   { echo "pixi.lock is lock-format v7 — unreadable by the facility
   pixi (< 0.68); regenerate under 0.67.x"; exit 1; }`) — the pin alone
   turns a v7 lock into an inscrutable CI parse error;
   `docs/developer/developer.rst` hook line becomes
   `pre-commit install --hook-type pre-commit --hook-type pre-push`
   (today's doc installs no pre-push hook at all, making the wrapper
   dead code for doc-followers), and document the escape hatch
   `SKIP=pixi-lock-check git push` for network-wedged pushes (an
   undocumented wedge invites `--no-verify`, which kills the tripwire
   too).
5. **Smaller promoted items:** reinstate the restore-notice echo (a
   silent restore hides a mutating toolchain — and v1's commit body
   cited that line as output it could not have produced;
   correct-and-flag it in the v2 body); narrow the awk strip to the
   `version:`/`sha256:` lines *within* the `- pypi: ./` stanza (today
   any real change inside the stanza — `requires_dist`,
   `editable: true` — is invisible); compute the classification diff
   once; drop the `head -20` truncation (print the full format hunk or
   name the line count); replace both dead "charter amendment 14"
   citations with the self-contained inline condition ("analysis.sns.gov
   pixi < 0.68 cannot read lock v7"), keeping the amendment name as a
   provenance note only; comment each of the three workflow
   `v0.67.2` pins with the same one-liner.
6. **Verification additions:** all v1 injection transcripts re-run at
   the v2 tip, plus the two new injections (interrupt, subdirectory)
   and a ≥0.68-shim run demonstrating the v7-specific message;
   `bash -n` both scripts and note in the PR body that `scripts/` is
   excluded from pre-commit lint (shellcheck manually if available).

### v3 — 2026-08-19 (after v2 rejection; todo.md @ `ff91bd4`; FINAL retry)

All four v1 findings closed and closed well (the gate calls the B4
honest-uncertainty fix exemplary; the classifier narrowing and the
plan-wording deviation were correct-and-flagged properly). Both new
blocking findings live in one fix — the trap — and **B5 is owned as a
plan defect**: the v2 fix sketch above prescribed arming the restore
trap BEFORE populating the snapshot, so any exit in that two-line
window copies a 0-byte mktemp file onto the tracked repo-root
`pixi.lock`. The gate reproduced it two ways (ENOSPC-class snapshot-cp
failure → 327276 → 0 bytes; `ulimit -f` → a 1024-byte truncation whose
first line still reads `version: 6`, sailing past ALL THREE tripwires
this slug ships). Strictly worse than the v1 fail-open it replaced. B6:
a bash INT/TERM trap returns to the script unless it exits — the v2
handler restored, deleted the snapshot, then execution continued into
the classifier against a nonexistent file, ending in a fabricated
drift accusation plus an 8k-line spew (the `--no-verify` inducer), and
made the ":One restore path, survives an interrupt" comment the
stated-vs-measured defect one line below the B4 fix for it.

## v3 fixes (final retry — the gate's order; its rewrite adopted verbatim)

1. **B5 + B6 — the six-line trap form, exactly as gate-verified:**

   ```bash
   snap=$(mktemp) || exit 1
   # Snapshot BEFORE arming the trap: an EXIT trap installed over an
   # empty mktemp file would copy that emptiness onto pixi.lock if this
   # cp failed.
   cp pixi.lock "$snap" || { rm -f "$snap"; exit 1; }
   restore() { cp "$snap" pixi.lock 2>/dev/null; rm -f "$snap"; }
   trap restore EXIT
   trap 'restore; trap - EXIT; exit 130' INT
   trap 'restore; trap - EXIT; exit 143' TERM
   ```

   Re-run the full injection matrix at the v3 tip: snapshot-cp failure
   (lock intact, exit 1), SIGINT mid-solve (exit 130, zero output, lock
   byte-identical), subdirectory, no-repo, benign, ≥0.68 v7 shim, drift
   stub. Reword the restore echo to future tense or move it into
   `restore()` (v2's printed "has been restored" before the trap ran).
2. **Single-source the pin (what makes retirement one deletion):** new
   `scripts/check_lock_format.sh` holding the `version: 6` test and the
   facility rationale once; the `pixi-lock-format` pre-commit hook
   (`entry:`) and all three CI steps (`run:`) invoke it. `0.67.2`
   stays in exactly two places (workflow pin lines + the wrapper's
   message), each carrying the same one-line rationale comment.
3. **Retirement block** — five lines in the wrapper's header: the
   trigger ("analysis.sns.gov pixi upgraded to ≥ 0.68"), the four files
   to touch (`scripts/pixi_lock_check.sh`, `scripts/check_lock_format.sh`,
   `.pre-commit-config.yaml`, `.github/workflows/test_and_deploy.yml`),
   and "remove in ONE commit; the campaign control plane's amendment 14
   tracks the trigger" — written for a maintainer who has never seen
   the campaign docs.
4. **Hardening trio:**
   `root=$(git rev-parse --show-toplevel) && [ -n "$root" ] && cd "$root" || exit 1`
   (a bash `cd ""` is a successful no-op — v2's `|| exit 1` never
   fired; the file test was carrying the failure); print the
   `SKIP=pixi-lock-check git push` hint exactly when `rc != 0` AND the
   lock is unchanged-and-v6 (the wedged-network path where the
   alternative is `--no-verify`);
   `default_install_hook_types: [pre-commit, pre-push]` in the config
   so plain `pre-commit install` arms both stages for already-onboarded
   developers, and `always_run: true` added to `pixi-lock-check` for
   symmetry with its sibling.
5. **Recorded, not scoped:** at pre-push the hooks check the working
   tree, not the pushed ref (`git push agentic other:branch` validates
   the wrong artifact) — the CI format check is the structural backstop
   and earns its place for exactly this; state it in the wrapper header
   and PR body.
