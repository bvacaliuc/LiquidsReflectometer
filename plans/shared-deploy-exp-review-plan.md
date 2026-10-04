# Plan: `shared-deploy-exp-review` — deploy and run the review branch from `/SNS/REF_L/shared` (cross-repo slug, ledger-carried series)

## Dispatch header (Analyst, 2026-10-04 — v1; supersedes the "agents never push … the human pushes" line below, which it keeps as the model)

**Campaign:** `exp-review-fixes` · **Leaf:** `shared-deploy-exp-review` (refs on the **subject** repo: `triage/shared-deploy-exp-review`,
`feature/shared-deploy-exp-review`, `qa/shared-deploy-exp-review`) · **Status:** READY — v1 (attempt 1 of N = 3) — dispatched 2026-10-04,
the moment the human's third answer landed (V1-28) ·
**Base (the deploy repository):** `git@code.ornl.gov:ref_l/shared.git` **`FY26B` @ `91e5c8f`** (`ls-remote` 2026-10-04: the remote tip; the
facility checkout `/SNS/REF_L/shared` is this branch) `[human, 2026-10-04: "S-2: P4; the series against FY26B."]` · **Subject base:**
`exp-review` @ `2324e5c` (the tree the review tier deploys; P1's `SHA`) ·
**Transport — the ledger-carried patch series** `[human, 2026-10-04: "… No new remote, no new switch, no kit change, and the human stays
the only party that writes the deployment repository …"]`: the Developer works in a **read-only clone** of `ref_l/shared` at `FY26B` @
`91e5c8f` (`git clone --branch FY26B`; **no `agentic` remote, no push**), commits on a local `feature/shared-deploy-exp-review` there, and
exports the series with `git format-patch 91e5c8f..HEAD -o <ledger>/plans/shared-deploy-exp-review-series/` (`0001-….patch` …) plus
`plans/shared-deploy-exp-review-crossrepo.md` (base sha, the patch list with sha256s, the exact `git am` line, the deployed subject sha);
both committed on the **ledger**. **Signalling on the subject** as for every slug: the Developer cuts `feature/shared-deploy-exp-review`
`--no-track` from `agentic/exp-review` @ `2324e5c` and pushes `--allow-empty` commits whose message names the ledger series commit (`series @
<ledger sha>, N patches, base FY26B @ 91e5c8f`); `qa/shared-deploy-exp-review` tags that commit; a rejection's `todo.md` lands on that
branch as usual. **No subject source file changes** (a non-empty diff against `exp-review` other than `todo.md` is a scope violation). ·
**Target:** the human applies the series to `FY26B` on code.ornl.gov (`git am` from the ledger copy) and re-deploys; the draft "PR" is the
`crossrepo.md` + the series — the Integrator's PASS commit on the ledger is the human's cue · **S-2 = P4** with P3's fetch and `pixi install
--frozen` `[human]` · **Review domains:** design, security (block); test (advise) · **Kind:** cross-repo deploy — not reduction-path.

**Declared scope (files, all in `ref_l/shared` @ `FY26B`):** `lr_reduction/make-shared-deploy.sh` (27 lines today, byte-identical to the
ledger's `scripts/make-shared-deploy.sh`), `launcher/nr_launcher.sh` (**the `--exp-review` case only**, `:46-64`), a new
`lr_reduction/verify-shared-deploy.sh` (= the ledger's `scripts/verify-shared-deploy.sh`, 7 693 bytes, byte-for-byte — the canonical copy
stays in the ledger `[human]`), a new `lr_reduction/README-shared-deploy.md`, a new `lr_reduction/.gitignore` (`.cache/`, `activate.sh`, the
`<tag>@<sha7>/` trees), and the submodule registration of `lr_reduction/exp-review` (`.gitmodules` + the gitlink at `2324e5c`, P2).
**Behaviours in:** P1–P8 below as re-specified here. **Explicitly OUT:** the `--exp-review-with-197` case (`:31-45`) and its tree
`[human, 2026-10-02]`; the two dirty gitlinks (`new_workflow*`, listed in P2, the human's); `main` of `ref_l/shared` (V1-28: do not merge
`main → FY26B`; the verifier reaches `FY26B` by this series); the Puppet hook (`fix/external/puppet`); **`MPLCONFIGDIR`** — see P6.

**Re-sealed facts at `FY26B` @ `91e5c8f`** (Analyst, 2026-10-04, read-only shallow clone, removed after): `make-shared-deploy.sh:2`
`REPO` defaults to **upstream** (`[human]`: the shared area is always deployed from upstream unless `REPO` is injected — **P1 is
re-specified below**); `:7-11` `checkout`/`clone` with no fetch (F4); `:16` `pixi install` without `--frozen`; `:17` `pixi shell-hook >
activate.sh` with the deployer's environment (F3); no `umask`, no post-install `chmod` (F7); `nr_launcher.sh:46-63` the `--exp-review`
case: `PIXI_PREFIX` set, not exported (`:51`), `.cache` test (`:55`), `source activate.sh` (`:58`), `pixi run --frozen new_launcher` with
**no `"$@"`** (`:59`), `LAUNCHER_WARNING=true` on the fallback (`:62`); `.gitmodules` has `new_workflow`, `new_workflow_scale_multiplier`,
`exp-review-with-197` — **no `exp-review`** (F2); no `lr_reduction/verify-shared-deploy.sh`, no README, no `lr_reduction/.gitignore`.

**P1 — re-specified at dispatch `[human, 2026-10-04: "the deploy to the shared area will always be from upstream (unless overridden, hence
the REPO env injection)"]`:** `REPO` keeps its upstream default; the **review tier is deployed with `REPO=<fork> TAG=exp-review
SHA=2324e5c`** (the README's documented command for review tiers), and the script records `REPO`, `TAG` and the resolved `SHA` in the
tree (`DEPLOYED.txt`) so the verifier's C3 compares against what was asked, not a guess. P1's RED (C3 FAIL on the live tree: upstream
`a4efd95`) is closed by the human's re-deploy after the series lands — the slug ships the script, the human runs it.

**P6 — re-specified at dispatch (security A1 from `launcher-env-outside-xdg-cache`'s gate, HIGH):** `nr_launcher.sh` **must not** export
`MPLCONFIGDIR` — the launcher now sets it itself with ownership/symlink checks (`launcher-env-outside-xdg-cache`, at QA); an unconditional
shell preset lets a squatted `/var/tmp/mpl-$USER` control the victim's `matplotlibrc`. P6 is: forward `"$@"` (`-- --help` reaches the
launcher); `export PIXI_PREFIX` or drop the fallback; fix the warning text (`XDG_CACHE_HOME`). The verifier's C5d stays as the *deployment's*
exposure check (env under the hook's target → FAIL); its `MPLCONFIGDIR`-exported leg becomes **informational** until the subject half is
deployed.

**Operation × state (the Integrator's gate drives every cell on a scratch `SHARE` outside `/SNS/REF_L/shared`, from the applied series, on
an internet node):**

| Operation | fresh `SHARE` | `SHARE` with a prior `<tag>@<sha7>` | running launcher from the prior tree |
|---|---|---|---|
| deploy `REPO=<fork> TAG=exp-review SHA=2324e5c` | `exp-review@2324e5c/` created; `exp-review` → symlink; env installed `--frozen`; `activate.sh` sanitized (C6); whole tree group-readable (C7 PASS, no owner-only path); `DEPLOYED.txt`; gitlink line printed (P2) | new `<tag>@<sha7>/` beside the old; symlink repointed with `ln -sfn`; old tree untouched | the running process keeps its tree (P4: nothing deleted) |
| re-run the same deploy | idempotent: no second tree, symlink unchanged, lock untouched (C5c) | same | same |
| update to a moved branch (`TAG` only) | fetch + `checkout -B`/`--detach <sha>` (P3) into a **new** `<tag>@<sha7>/`; symlink moves | same | the old tree stays |
| roll back | `ln -sfn <tag>@<old sha7> <tag>` — documented in the README | — | — |
| `nr_launcher.sh --exp-review -- --help` | reaches `new_launcher --help` through the symlink (P6) | same | — |
| verifier on the result | **0 FAIL / 0 WARN** (C5d's `MPLCONFIGDIR` leg informational) | same | — |
| run as a second user (group `sns_ref_l_team`, no write) | starts; writes nothing into the tree | same | — |

**Red-Green seed (shim tests in the series, run by the Integrator; the live `SHARE` is never the test bed):** T1 the deploy script against
stubbed `git`/`pixi` on `PATH` (a fake `pixi install` that writes a 600 file → the sweep makes it `g+r`; a fake `shell-hook` echoing `$PATH`
→ sanitized); T2 the verifier against a fabricated tree (one 600 file → C7 FAIL; fixed → PASS; a missing gitlink → C2); T3 `nr_launcher.sh
--exp-review -- --help` with `PIXI_PREFIX` pointed at a fake tree whose `pixi` echoes its arguments → `"$@"` forwarded, `PIXI_PREFIX`
exported; T4 `DEPLOYED.txt` round-trip (C3 reads it). **Mutate-once:** `--frozen` dropped → T1/C5c; the `chmod g+rX` sweep removed → T2/C7;
`ln -sfn` replaced by in-place checkout → P4's cell (old tree gone); `"$@"` dropped → T3; `MPLCONFIGDIR` export added → a grep test in T3
(P6 negative).

**Acceptance (Integrator):** the series applies with `git am` on a fresh `FY26B` @ `91e5c8f` clone (no conflicts); the scratch deploy +
verifier **0 FAIL / 0 WARN** (C5d leg informational); the launcher option against the scratch tree; design + security reviewers on the
applied tree (security: the whole-tree readability, the sanitized `activate.sh`, no `MPLCONFIGDIR` preset, `git am` of the series does not
touch `--exp-review-with-197`); the `crossrepo.md` names base, patches, sha256s, the `git am` line and the deploy command for the human.
**PASS → the Integrator's ledger commit is the human's cue**; the human applies to `FY26B`, pushes, re-deploys, and the scientists'
`nr_launcher.sh --exp-review` runs the fork's `2324e5c` (C3 PASS with `REPO=<fork>`).

**The original header (kept as the model):** **Kind:** cross-repo (charter §6): the code lands in
`REF_L/shared` (`git@code.ornl.gov:ref_l/shared.git`, branch `FY26B`), which agents never push;
the Developer commits locally on a branch there, records `plans/shared-deploy-exp-review-crossrepo.md`,
and the human pushes. **Out of scope:** the `--exp-review-with-197` option and its tree — the human retires them outside the campaign `[human, 2026-10-02: "Drop the with-197 option in the campaign documents"]`. **Declared scope:** `lr_reduction/make-shared-deploy.sh`,
`launcher/nr_launcher.sh` (`--exp-review` option only), a new `lr_reduction/verify-shared-deploy.sh`
(seed: this ledger's `scripts/verify-shared-deploy.sh`), a new `lr_reduction/README-shared-deploy.md`,
and the submodule registration of `lr_reduction/exp-review`. **Review domains:** design, security
(block); test (advise). **Runtime-environment owner:** Integrator (D-19), with Advisor V1.

## 1. What the human built (reviewed 2026-10-02 on analysis-node21)

`make-shared-deploy.sh` clones a branch into `<share>/<tag>/`, installs the pixi environment
with `PIXI_CACHE_DIR` inside the tree, and writes `activate.sh`; `nr_launcher.sh --exp-review`
exports that cache dir, sources the activation script, and runs `pixi run --frozen new_launcher`.
**Measured:** a frozen run with the network blocked succeeds in 0.7 s, imports the package from the
deployed source, writes nothing to the per-user cache, and leaves `pixi.lock` untouched; the
launcher imports offscreen in 2–4 s from GPFS, no slower than the local-disk `/usr/local/pixi`
tier (3.4–7 s measured). The design is sound: one build serves every node, no per-user rebuild,
nothing under `$XDG_CACHE_HOME`, and a restricted user or an internet-restricted node only needs
read access. The remaining items are hardening, not redesign.

## 2. Findings (from `scripts/verify-shared-deploy.sh`, run 2026-10-02)

| # | Finding | Severity |
|---|---|---|
| F1 | **Deployed from upstream, not the fork:** HEAD a4efd95 (`neutrons/…`), while the campaign base is the fork's `exp-review` @ 7b6d6b9 (adds the merged `save_config_json` fix and the CI change). Scientists evaluating this tree are not evaluating the review branch | blocking for the campaign's deploy model |
| F2 | **The deployed commit is unrecorded:** `lr_reduction/exp-review/` is untracked in `REF_L/shared`, whereas earlier deployments are submodules pinned by gitlink (`new_workflow`, `exp-review-with-197`); two of those gitlinks are also dirty (checked out ahead of the committed pin) | correctness of the record |
| F3 | `activate.sh` embeds the deployer's `PATH` (`/SNS/users/6ov/.cargo/bin`): `pixi shell-hook` captures the current environment; another user inherits a private path | hygiene |
| F4 | Re-running the script does not update: `git -C $TAG checkout $TAG` without fetch/reset; `pixi install` without `--frozen` (works today because the lock matched; not guaranteed) | robustness |
| F5 | In-place update of a running deployment recreates the deleted-environment hang (login-hook class) for anyone mid-session | safety on update |
| F6 | `--exp-review` fallback (no `.cache`) sets `PIXI_PREFIX` without exporting it, so `nsd-app-wrap` looks under `/usr/local/pixi/exp-review` and fails; the direct path drops the user's extra arguments (`"$@"` not forwarded); the warning text says `XDG_CACHE_DIR` (the variable is `XDG_CACHE_HOME`) | minor |
| F7 | ~~One env file not group-readable (`conda-meta/conda-26.3.2-….json`, umask at install); `chmod -R 2775` ran on the empty cache dir only~~ **Re-measured 2026-10-03 (§6): all 510 `conda-meta/<pkg>.json` prefix records are mode 620 — unreadable by anyone but the deployer — because pixi 0.60.0 writes them at 600 regardless of umask (reproduced with a fresh install), and a later `chmod g+w` (ctime 2026-10-02 16:45) added write without read. Every other file is 664/775, every dir 2775, all group `sns_ref_l_team`. The verifier's C7 looked only six levels deep and reported a warning on one example; the deployer's own runs cannot see it (owner bits).** A scientist's `nr_launcher.sh --exp-review` fails with *"failed to collect prefix records … Permission denied"* | **blocker** for every non-owner |

## 3. Items (each independently testable; RED = the verifier line fails before, passes after)

- **P1 — deploy from the review branch's home.** `REPO` defaults to the fork
  (`https://github.com/bvacaliuc/LiquidsReflectometer.git`) for review tiers; the production tier
  names upstream explicitly. Re-deploy `exp-review` at 7b6d6b9. Verifier C3.
- **P2 — record the deployment:** `git submodule add -b exp-review <fork> lr_reduction/exp-review`
  pinned at the deployed SHA; the script ends by printing the gitlink line to commit; `.cache/`,
  `activate.sh` ignored via `lr_reduction/.gitignore`. Verifier C2. (The two dirty gitlinks are
  the human's to commit or reset — listed, not changed.)
- **P3 — update path:** `git fetch origin && git checkout -B $TAG origin/$TAG` (or `--detach <sha>`
  when `SHA` is given); `pixi install --frozen`; refuse to run while a `new_launcher` process from
  this tree is running (`pgrep -f` on the env's python, with the `[p]attern` guard). Verifier: a
  second run on a moved branch updates HEAD; C5c lock untouched.
- **P4 — immutable deployments:** deploy into `<tag>@<sha7>/` and point a `<tag>` symlink at it
  (`ln -sfn`); `nr_launcher.sh` follows the symlink; the previous tree stays until the human removes
  it. Closes F5 without a code change in the launcher. Verifier: C1 on the symlink target.
- **P5 — sanitized `activate.sh`:** generate with `env -i PATH=/usr/bin:/bin HOME=/nonexistent
  pixi shell-hook` (keeps only the env's own paths and conda activate scripts). Verifier C6.
- **P6 — launcher option:** forward `"$@"`; export `PIXI_PREFIX` or drop the fallback; fix the
  warning text; set `MPLCONFIGDIR=/var/tmp/mpl-$USER` (node-local, survives the login hook's wipe
  of `$XDG_CACHE_HOME` only if outside it — it is). Verifier C9 + a shell test that `--exp-review -- --help`
  reaches the launcher.
- **P7 — permissions (re-specified 2026-10-03, now the first item to land):** the deploy script
  runs under `umask 002` **and, after `pixi install`, repairs what pixi itself writes private:**
  `find "$SHARE/$TAG" \( -type f ! -perm -g+r \) -o \( -type d ! -perm -g+rx \) -print0 | xargs -0 -r
  chmod g+rX` (equivalently `chmod -R g+rX "$SHARE/$TAG"`; dirs already setgid). The sweep is on the
  whole tree, not the cache dir alone, and runs on every deploy and update, because every
  `pixi install` writes new 600 records. Verifier C7 is now a **FAIL-class, whole-tree check of
  non-owner readability** (`scripts/verify-shared-deploy.sh`, 2026-10-03) — the deployer's own
  `pixi run` succeeding is not evidence, since owner bits apply to it. RED today: C7 FAIL, 510 paths.
  Immediate repair of the live deployment (the human runs it; reversible, metadata only):
  `chmod -R g+rX /SNS/REF_L/shared/lr_reduction/exp-review` — then the verifier → C7 PASS, and the
  scientist's command works unchanged.
- **P8 — verifier + docs:** `verify-shared-deploy.sh` committed beside the deploy script and run
  at the end of every deploy; `README-shared-deploy.md`: deploy, update, roll back (switch the
  symlink), run on an internet-restricted node (`--exp-review` with no network), run as another
  user (group membership `sns_ref_l_team` is the only requirement), and the one rule for agents
  on analysis nodes (`PIXI_CACHE_DIR` under the checkout; never edit the tracked `.pixi/config.toml`).

## 4. Acceptance

`verify-shared-deploy.sh` reports 0 FAIL and 0 WARN on the re-deployed tree; a `new_launcher`
started via `nr_launcher.sh --exp-review` on a second analysis node (and, if available, as a
second team member) opens the Settings editor and the Overplot tab with a log axis without console
errors after a fresh login in another terminal (the login-hook scenario); the `crossrepo` record
names the `REF_L/shared` branch and SHA for the human to push. Deploy consequence: none to
autoreduction (the shared tree is launcher-only); the review tier is what scientists evaluate.

## 5. Decisions

| # | Decision | Owner |
|---|---|---|
| S-1 | Deploy review tiers from the fork (P1) — confirms the two-branch model (charter §5) | human |
| S-2 | Immutable `<tag>@<sha7>` directories with a symlink (P4) vs in-place update with a running-process guard (P3 only) | human |

## 6. 2026-10-03 — a scientist could not start the review tier: measured `[Advisor V1]`

`[human, 2026-10-03]`: *"the scientist was not able to run the launcher due to a permission denial …
`failed to collect prefix records from '…/.cache/envs/lr_reduction-7509171706107696221/envs/default'
Permission denied (os error 13)` … Having tested the `exp-review` deploy myself on both machines, I
was at a loss to explain how the scientist's environment failed with a permissions problem. Both of
our logins are part of the 'sns_ref_l_team' group."*

**Cause (measured on analysis-node, read-only):** over the deployed environment's 97,321 entries,
every directory is `2775`, every file `664`/`775`, everything group `sns_ref_l_team` — **except the
510 `conda-meta/<pkg>.json` records, mode `620`** (`rw--w----`): owner read/write, group *write*
only. Those records are exactly what pixi reads first ("prefix records") to check the environment
against the lock, so a group member fails before anything runs. The owner reads them under the
owner bits, which is why the deployer's tests on both machines passed: the test was run by the one
account that cannot see the problem.

**Why 620:** a fresh `pixi install` with the same pixi (0.60.0), `umask 0002`, and a `PIXI_CACHE_DIR`
inside the tree writes every record at **600** — pixi/rattler creates them through a private
temporary file, so no umask or setgid directory can open them. The records' ctime
(2026-10-02 16:45:52) is a day after their mtime (2026-10-01 18:43:25): a later `chmod g+w` sweep
added write without read. The deploy script's `chmod -R 2775` runs only on the empty cache dir,
before `pixi install`, so it never touches them (F7, re-rated to blocker).

**Repair, now:** `chmod -R g+rX /SNS/REF_L/shared/lr_reduction/exp-review` (the human; metadata only,
reversible; dirs already setgid). Then `scripts/verify-shared-deploy.sh` → C7 PASS, and the
scientist's `nr_launcher.sh --exp-review` works unchanged. **Prevent:** P7 as re-specified — the
sweep after every `pixi install`, and C7 as the FAIL-class whole-tree check it now is.

**The mechanism for restricted nodes (bl4b-analysis1 and the like, no internet):** no redesign is
needed, and the `.pixi/config.toml` `detached-environments` convention is not what this deployment
relies on. What a node needs at *run* time is only the deployed tree, readable: the environment is
complete on GPFS (a full copy, no links into any cache; `pixi run --frozen` with `PIXI_CACHE_DIR`
inside the tree was measured to make no network request and write nothing per-user, §1). Two ways
to start it, both already provided by the deploy's own notes:

| Launch | Needs on the node | Reads/writes in the deployment |
|---|---|---|
| `pixi run --frozen new_launcher` (what `nr_launcher.sh --exp-review` does today) | `/usr/bin/pixi` installed; no network | reads the 510 prefix records (hence this failure); rewrites `conda-meta/pixi` (664, group-writable — fine) |
| `source activate.sh && new_launcher` — `new_launcher` is a console-script entry point (`pyproject.toml:23`), so it is a binary in the env's `bin/` | **nothing**: no pixi, no network | reads the tree; writes nothing |

**Recommendation (P10):** `nr_launcher.sh --exp-review` sources the sanitized `activate.sh` (P5) and
execs `new_launcher` directly, keeping `pixi run --frozen` only as the deployer's verification path
(C5/C8). A node without pixi, without internet, or without group write anywhere can then run the
tier; the only requirement left is the one P8's README already states — membership of
`sns_ref_l_team` — and C7 now proves it rather than assumes it. Pixi stays the *build* tool, run on
an internet node by the deployer; it is not needed to *run*.

Acceptance for this section: C7 PASS after the repair; a run of `nr_launcher.sh --exp-review` by a
non-owner team member on an internet-restricted node (the human asks the scientist, or a second
account) — the one measurement no agent here can take, since every seat runs as the deployer.

## Revision history

v1 — the Advisor's review and items P1–P8 (2026-10-02/03, §1–§6), the actionability measurement (§7, 2026-10-04); **dispatch header
added and dispatched by the Analyst 2026-10-04** against `ref_l/shared` `FY26B` @ `91e5c8f` once the human's three answers were on the bus
(transport = ledger-carried series; S-2 = P4; the series against `FY26B` — `requests/shared-deploy-transport-decision.md` "Decided"; A-53):
facts re-sealed from a read-only clone; P1 re-specified (upstream default kept, review tier by `REPO`/`SHA` injection + `DEPLOYED.txt`); P6
re-specified (no `MPLCONFIGDIR` preset — security A1); the operation × state table, the shim-test seed and the Integrator's acceptance
written; the subject-side signalling (`--allow-empty` commits) defined.

## 7. 2026-10-04 — actionable once three lines are on the bus `[Advisor V1]`

The human's go (verbatim) and the three answers the Analyst needs — transport, S-2, target branch — with recommended
values and the facts behind them: [`requests/shared-deploy-transport-decision.md`](../requests/shared-deploy-transport-decision.md).
Measured this morning:

| Item | State |
|---|---|
| P1 deploy from the fork at the tip | **not done** — live tier still upstream `a4efd95`; fork `exp-review` @ `2324e5c` (a fast-forward of `a4efd95`; upstream still `a4efd95`) |
| P2 record the deployment (gitlink) | not done (C2 WARN) |
| P3 / P4 update path, immutable dirs (S-2) | undecided — recommended P4 with P3's fetch/frozen install |
| P5 sanitized `activate.sh` | not done (C6 WARN: one deployer-private path) |
| P6 launcher: forward `"$@"`, `MPLCONFIGDIR` outside `$XDG_CACHE_HOME` | not done (new C5d WARN) — this is `launcher-env-outside-xdg-cache`'s `REF_L/shared` half |
| P7 permissions | **not done on the live tree** (C7 FAIL, 510 paths); the sweep is not yet in `make-shared-deploy.sh` (`main` and `FY26B` identical, no `umask`/post-install `chmod`) |
| P8 verifier + docs | **the verifier is on the deploy repo's `main` (`469cecb`..`5b61e0a`, the human's usability edits: `DEPLOY_DIR [BRANCH_TAG] [EXPECTED_SHA]`, `REPO` env)** — absent on `FY26B`, the branch the facility runs; README not yet |

**The branch fact that changes the plan's `Base:`:** `/SNS/REF_L/shared` is a checkout of **`FY26B`** (`91e5c8f`),
`main` has diverged from it since 2025-12-07 (60 vs 83 commits), and only `FY26B`'s `nr_launcher.sh` has
`--exp-review`. The slug targets `FY26B`; the verifier reaches it by cherry-pick of `5b61e0a` or as part of P8.

**The human's verifier, reviewed:** three adjustments, as a patch against `main @ 5b61e0a`
([`plans/verify-shared-deploy-adjustments.patch`](verify-shared-deploy-adjustments.patch), applies cleanly) and
folded into this ledger's seed `scripts/verify-shared-deploy.sh`: (a) C5d tested for
`/etc/profile.d/fontcache-worka**g**ound.sh` — a typo, so it never fired — and compared the caller's shell to the
hook's default, which a `~/.bashrc` remap hides; it now tests the *deployment's* exposure (env under the hook's
target → FAIL; `MPLCONFIGDIR` not exported by the launcher → WARN); (b) `EXPECTED_SHA=${3:-skip}` made C3
unreachable with the documented defaults (the `ls-remote` branch was dead); `BRANCH_TAG` alone now resolves the
tip, an explicit `skip` still skips; (c) `REPO` defaulted to upstream; the review tier is deployed from the fork
(S-1), so the fork is the default, overridable. Run form unchanged. On the live tree now:
`7 PASS, 3 WARN, 2 FAIL` (C3, C7; C5d WARN).

**The login hook, read on this node:** `/etc/profile.d/fontcache-workaround.sh` (Puppet-managed) sets
`XDG_CACHE_HOME=/var/tmp/xdgcache-$USER` and `rm -rf`s it on **every** login shell — its own comment says the
purpose is caches off NFS homes, and the wipe is broader than the fontconfig/matplotlib caches it targets. The
human's `~/.bashrc` remaps `XDG_CACHE_HOME=/tmp/$USER-$(hostname)` after the hook: a correct personal workaround
that no scientist has. The deployment is immune by design where C4 holds (env under `DEPLOY/.cache`); P6 closes
the last exposure (`MPLCONFIGDIR`); the Puppet half (`fix/external/puppet`: scope the `rm -rf`) stays the human's
ticket and is not needed for the tier to work.
