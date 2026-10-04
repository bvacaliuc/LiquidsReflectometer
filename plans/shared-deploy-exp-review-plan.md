# Plan: `shared-deploy-exp-review` — deploy and run the review branch from `/SNS/REF_L/shared` (cross-repo slug, ledger-carried series)

## Dispatch header (Analyst, 2026-10-04 — v1; supersedes the "agents never push … the human pushes" line below, which it keeps as the model)

**Campaign:** `exp-review-fixes` · **Leaf:** `shared-deploy-exp-review` (refs on the **subject** repo: `triage/shared-deploy-exp-review`,
`feature/shared-deploy-exp-review`, `qa/shared-deploy-exp-review`) · **Status:** v2 (attempt 2 of N = 3; v1 rejected at `review/shared-deploy-exp-review` @ `10ed77e` — four findings, B-1…B-4, all on the
series; the deploy itself passed the Integrator's real scratch acceptance; see Revision history and "v2 re-specification") — v1 dispatched
2026-10-04 the moment the human's third answer landed (V1-28); v2 continues on the ledger series (`plans/shared-deploy-exp-review-series/`,
revised in place by the Developer in the same read-only clone) and on the subject's `feature/shared-deploy-exp-review` (the Integrator's
`todo.md` on top, @ `10ed77e`; the next signalling commit names the revised series) ·
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

## v2 re-specification (Analyst, 2026-10-04 — from the Integrator's four findings; the Developer revises the series in place)

| # | Behaviour (v2) | Domain / types (amendment 18) |
|---|---|---|
| N1 | **One seam for the system pixi, and tests that can fail.** `make-shared-deploy.sh` resolves the pixi it will install with **and** name in `activate.sh` as: `SYSTEM_PIXI=${SYSTEM_PIXI-/usr/bin/pixi}` when that path is an executable file, else `$PIXI` (the caller's); the choice is recorded in `DEPLOYED.txt` and C8 checks `activate.sh`'s pixi **is** the install pixi (security A9 / design A5 adopted). The shim suite passes on a host **with** a system pixi (the analysis nodes, `/usr/bin/pixi` 0.60.0) and **without** one, because the tests set the seam; one test plants a group-runnable system stub and a private pixi first on `PATH` and asserts the system one is chosen and `PIXI_EXE` names it (its battery row: `HOOK_PIXI=$PIXI` must red); T1h restores the symlink it removes (or T2/T4 address the tree directly) so no cascade. | the pixi executable: {system executable, system present but not executable (bash `command -v` returns it), absent, private-first-on-PATH} × host umask {077, 022, 002} |
| N2 | **`PIXI_PREFIX` is never chosen by the caller's cwd** (CWE-426/427 — v1's departure 5 was a regression). `nr_launcher.sh` uses the **fixed** `/SNS/REF_L/shared/lr_reduction` unless `LR_SHARE` is set — an absolute path the caller sets deliberately, to the share's parent (`$LR_SHARE/lr_reduction` must exist); `$0`/`BASH_SOURCE`-derived paths are not used. Every start form resolves the same prefix: absolute path, `PATH` exec, `bash <name>` from a foreign cwd (with and without a planted `<cwd>/../lr_reduction/exp-review/activate.sh`), `./`, a symlink, a copy outside the share. The warning text names `XDG_CACHE_HOME`; `"$@"` forwarded; `PIXI_PREFIX` exported — v1's P6 kept. | start form ∈ {abs, PATH, `bash name`, `./`, symlink, copy} × `LR_SHARE` ∈ {unset, set valid, set invalid} × a planted decoy tree {absent, present} |
| N3 | **A scientist's run writes nothing into the shared tree** — P10 adopted (the Integrator's B-3 route (a)): `nr_launcher.sh --exp-review` sources the sanitized `activate.sh` and **`exec`s the env's own `bin/new_launcher`** (no `pixi run` at run time; `pixi run --frozen` stays the deployer's verification path, C5/C8). After a run by any user, every file under `<tag>@<sha7>/` has the owner, mode and mtime it had after the deploy (`conda-meta/pixi`, `history`, `pixi_env_prefix` included). The README says what is true: *the deploy never changes a tree once it is switched to; running the tier writes nothing into it.* The second-user row becomes an **acceptance the human can execute** (§Acceptance v2). | the files pixi rewrites at run time (measured: `conda-meta/{pixi,history,pixi_env_prefix}`, `.cache/uv-cache`) × user ∈ {deployer, member with umask 077, member with umask 022} |
| N4 | **The deploy adopts only directories it created, and the legacy tree is restored by `mv`, never by the symlink.** Before cloning, the deploy writes a marker (`.deploying` with the deploy's pid/host/start) into the new `<tag>@<sha7>/`; a directory at that name **without** `DEPLOYED.txt` **and without the marker** is refused with a message naming it (a moved legacy tree, or anything else the deploy did not make); an interrupted deploy of its own (marker present, no `DEPLOYED.txt`) is resumed or wiped **only after** the marker's pid is gone. The README's "Once" migration and "Roll back" sections state that pixi keys a detached env by its **physical path** (measured: `lr_reduction-5958…` → `-1252…` after `mv`), so the first rollback is `mv exp-review@<sha7> exp-review` (restoring the path), not a symlink; a shim test plants a moved legacy tree under `<tag>@<sha7>` and asserts refusal. | directory at `<tag>@<sha7>`: {absent, deploy-made complete, deploy-made interrupted (marker, pid alive / dead), foreign (no marker, no `DEPLOYED.txt`), legacy moved} |
| N5 | **Adopted advisories (small, security-relevant, in declared files):** the lock is taken on the **share directory's fd** (`exec 9< "$SHARE"` + `flock`), never on a file path a planted symlink can redirect (security A1); `TAG` is validated — `^[A-Za-z0-9][A-Za-z0-9._-]*$` — before any `pgrep`/path use (A8: a regex error must not read as "no process"); `SHA` is **full** (40 hex) in `DEPLOYED.txt`, the gitlink and the human's commands, 7-hex accepted only as input and resolved (A6); the verifier's C7 **refuses** unless `SHARE` is setgid to the team group and prints the group it saw (A4); C3 prints a `SKIP` line when it has nothing to compare (Integrator's note); `SHARE` defaults to the script's own directory (`$HERE`), not the cwd (design A4); the migration order builds and verifies first and switches the symlink last, so `exp-review` resolves throughout (design A3). | — |

**Not adopted (PR body, for the human):** security A2 (sweep follows a symlink swapped mid-walk — sweep only the fresh install: **adopt if cheap**, else state), A3 (124 720 g+w files — the group is the trust boundary), A5, A7 (GPFS `flock`/`pgrep` one-node blind spot — stated in the README), A10 (verifier needs ownership — the README's rollback verify step is the deployer's), A11; design A6/A7/A9/A10.

**Tests (v2, shim + real):** the shim suite runs green on **both** host classes (T0: a CI-style run with `/usr/bin` hidden *and* a run with a group-runnable system stub); N1 seam rows; N2 one T3 row per start form × decoy; N3 a shim that records every write under the tree during a `--exp-review -- --help` run (none) and the README wording test (grep for "never changed" → gone); N4 the foreign/legacy/interrupted directory rows; N5 the lock-on-symlink row (planted symlink untouched), the `TAG` rows (`-x`, `a b`, `.*`), the C7 non-setgid row, the C3 SKIP row. **Mutate-once (added):** seam removed (`HOOK_PIXI=$PIXI`) → N1 row; prefix from `$0` again → N2 `bash name` + decoy row; `pixi run` restored at run time → N3 write-recorder; marker check removed → N4 foreign-directory row; lock on a file path → N5 symlink row; `TAG` check removed → N5 rows.

**Acceptance (v2 — Integrator, scratch share on an analysis node, never `/SNS/REF_L/shared`; every probe of a fallback sets `LR_SHARE` to the
scratch share — the v1 incident's rule):** the series applies clean on a fresh `FY26B` @ `91e5c8f` clone; shim suite green there with the
system pixi present; deploy `REPO=<fork> TAG=exp-review SHA=<full 2324e5c sha>` → verifier 0 FAIL / 0 WARN; `nr_launcher.sh --exp-review --
--help` from each start form resolves the scratch prefix (`LR_SHARE`) and never a planted decoy; after a real `--exp-review` run (offscreen,
stopped), **no file under the tree changed** (owner/mode/mtime listing before and after, diffed); a moved legacy tree under `exp-review@<sha7>`
is refused; the planted-symlink lock case. **The human's acceptance row (B-3, after the re-deploy):** a second member (umask 077) starts the
tier, then a third; `ls -l conda-meta/pixi conda-meta/history` unchanged; both start. The crossrepo record's step 2 says `mv` for the first
rollback and uses full SHAs.

## Revision history

v1 — the Advisor's review and items P1–P8 (2026-10-02/03, §1–§6), the actionability measurement (§7, 2026-10-04); **dispatch header
added and dispatched by the Analyst 2026-10-04** against `ref_l/shared` `FY26B` @ `91e5c8f` once the human's three answers were on the bus
(transport = ledger-carried series; S-2 = P4; the series against `FY26B` — `requests/shared-deploy-transport-decision.md` "Decided"; A-53):
facts re-sealed from a read-only clone; P1 re-specified (upstream default kept, review tier by `REPO`/`SHA` injection + `DEPLOYED.txt`); P6
re-specified (no `MPLCONFIGDIR` preset — security A1); the operation × state table, the shim-test seed and the Integrator's acceptance
written; the subject-side signalling (`--allow-empty` commits) defined. Developer: the 10-patch series @ ledger `63ec500`, signalling commit
`05cb88a`, a real scratch deploy 11/1/0 (D-42). **Rejected** at `review/shared-deploy-exp-review` @ `10ed77e` (the Integrator's `todo.md`).

### v2 — 2026-10-04 (attempt 2 of 3; the work order for `triage/shared-deploy-exp-review-v2`)

**Rejection.** `review/shared-deploy-exp-review` @ `10ed77e` — `todo.md` at that commit (Integrator, Claude Opus 5.5): *"Verdict: REJECT — four
findings. The deploy itself works on the target host class (a real scratch deploy of the fork's `2324e5c`: verifier 12 PASS / 0 WARN / 0 FAIL;
idempotent; update, running-tree and rollback cells as declared; the launcher option starts the launcher). But the series' own tests fail 20 of
43 on that host, the launcher can source an `activate.sh` chosen by the current directory, a README guarantee is falsified by a normal run, and
the first rollback the README prescribes lands on a tree whose environment pixi can no longer find. This is a cross-repo slug: the series is
revised in the ledger (`plans/shared-deploy-exp-review-series/`), signalled here as before. Not infrastructure."* What passed (**the Developer
does not redo it**): the signal is empty against `exp-review`; the 10 sha256s match; `git am --3way` gives tree `07f9eb2`; the verifier is the
ledger's canonical copy; `--exp-review-with-197` untouched; the Integrator's real acceptance (12/0/0, idempotent re-run, update with a
"running" process keeps the old tree, README rollback 0/0, `-- --help` forwarded, no `MPLCONFIGDIR`); the departures hold; `shellcheck` clean.

> **BLOCKING — B-1: the tests cannot control the system-pixi lookup; 20 of 43 fail on the deploy host (rule a + d).** `make-shared-deploy.sh:92`
> `HOOK_PIXI=$(PATH=/usr/bin:/bin command -v pixi || echo "$PIXI")` runs the **real** system pixi's `shell-hook` in the shim tests, against the
> fake repository ("could not find pixi.toml"). Reproduced: `bash lr_reduction/test-shared-deploy.sh` → **23 ok / 20 not ok** under umask 077,
> 022 and 002 … the mutant `HOOK_PIXI=$PIXI` (the declared preference removed) passes 43/43 on every host — the behaviour P5/departure 7
> declare has no test that can fail; bash `command -v` returns a non-executable `/usr/bin/pixi`. **Fix (behaviour; domain = the pixi the deploy
> installs with and the pixi `activate.sh` names):** one seam the tests set (e.g. `SYSTEM_PIXI=${SYSTEM_PIXI-/usr/bin/pixi}`, used only when it
> is executable, else `$PIXI`); the shim suite passes 43 (+ new) on a host with and without a system pixi; a test with a group-runnable system
> stub and a private pixi first on PATH asserts `PIXI_EXE` is the system one and the switch happens (and its battery row); T1h restores the
> symlink (or T2/T4 address the tree directly). Consider installing with the same pixi `activate.sh` names (security A9 / design A5).
>
> **BLOCKING — B-2: `bash nr_launcher.sh` derives `PIXI_PREFIX` from the current directory and sources its `activate.sh` (CWE-426/427;
> regression).** `launcher/nr_launcher.sh:51-63`: `PIXI_PREFIX=$(cd "$(dirname "$(realpath "$0")")/../lr_reduction" …)`. Started as `bash
> nr_launcher.sh` (found on `PATH`), `$0` is the bare name; GNU `realpath` does not require it to exist, so the prefix is `<parent of
> cwd>/lr_reduction`, and line 63 sources that directory's `exp-review/activate.sh` **as the user**. Reproduced (scratch only) … `ATTACKER
> activate.sh ran as 6ov`; the absolute-path form resolves the share. Any local user can create `/tmp/lr_reduction`; the base used the fixed path
> (departure 5 introduced this). **Fix (behaviour; domain = every way the script is started):** `PIXI_PREFIX` is the share's own `lr_reduction`
> or the fixed `/SNS/REF_L/shared/lr_reduction`, never a directory chosen by the caller's cwd … a T3 row per start form, including `bash
> <name>` from a foreign cwd.
>
> **BLOCKING — B-3: "never changed after it is made" is falsified by a normal run (rule d; CWE-732).** `README-shared-deploy.md:13`, `:47`,
> crossrepo P4 ("immutable"). Measured: in both scratch trees `conda-meta/pixi` and `conda-meta/history` were rewritten after the install by a
> later `pixi run` … every scientist's `pixi run --frozen new_launcher` writes into the shared env as that scientist. Consequence to settle
> (suspected, not reproduced — no second account): a member with umask 077 rewriting those files could recreate the mode-600 lockout this
> series fixes. **Fix (either; the plan's call):** (a) run the tier without `pixi run` (source `activate.sh`, exec the env's `bin/new_launcher`
> — the plan's §6 P10), so a run writes nothing; or (b) correct the wording **and** make the second-user run an acceptance row the human can
> execute.
>
> **BLOCKING — B-4: the first rollback the README prescribes lands on a tree pixi cannot find (rule d / e).** The migration renames the
> in-place tree to `exp-review@<sha7>`. Measured with `/usr/bin/pixi info --json`: pixi 0.60.0 names a detached env from a hash of the
> project's **physical path** … So the README's "Roll back: point the symlink at the earlier tree" applied to the first deploy's only earlier
> tree makes `pixi run --frozen` look for an env that does not exist … Also: the moved tree's name is exactly what `SHA=<that sha7>` deploys
> into — the deploy would take it for an interrupted tree and fetch/install **into** it, changing it in place (P4). **Fix (behaviour):** the
> README and crossrepo state how the pre-immutable tree is restored (by `mv` back, not the symlink), or the migration keeps its env reachable;
> the deploy never adopts a directory it did not create … a shim test for a moved legacy tree under the `<tag>@<sha7>` name.
>
> **Incident (to the human; recorded in the ledger):** the security reviewer, probing B-2's fallback, ran a **copy** of the launcher outside a
> share: it fell back to the live `/SNS/REF_L/shared/lr_reduction` and ran `pixi run --frozen new_launcher` from the live in-place `exp-review/`
> as 6ov for ~2 minutes … It rewrote three pixi metadata files in the live env … Nothing else; no process remains.

**What the plan missed (the Analyst's defects).** (1) The shim-test seed named "stubbed `git`/`pixi` on `PATH`" without asking what the
script resolves **outside** `PATH` — the system-pixi preference the Advisor's P5 implied has a hard-coded lookup the shims cannot reach; a
plan that declares a preference must declare its seam. (2) The plan let "departure 5" (`PIXI_PREFIX` from the launcher's location) stand as
a reasonable change without the start-form enumeration: `$0` is caller-controlled under `bash <name>` — the start forms were never a row.
(3) "Immutable" was the plan's word for the *deploy's* behaviour and the README promised it for the *tree*; the plan never asked what `pixi
run` writes at run time, though P10 (the Advisor's own recommendation to run without `pixi run`) was already in §6 — adopted now. (4) The
rollback row said "`ln -sfn <tag>@<old sha7>`" without the fact that pixi keys an env by physical path — a migration that renames a tree
breaks its env, and the deploy could adopt a stranger's directory. **One root:** the operation × state table enumerated the deploy's own
states (fresh / prior / running) and not the *environment's* — host pixi, caller cwd, run-time writes, path-keyed env — the axis a
cross-repo deploy lives on.

**Changes in v2** — "v2 re-specification" above: N1 the pixi seam (install and runtime pixi agree; tests green with and without a system
pixi); N2 fixed prefix or an explicit `LR_SHARE`, never cwd, one row per start form; N3 **P10 adopted** — no `pixi run` at run time, a run
writes nothing, the README says what is true, the second-user run is the human's acceptance; N4 the deploy adopts only what it made (marker +
`DEPLOYED.txt`), the legacy tree is restored by `mv`, a moved legacy tree is refused; N5 the adopted advisories (lock on the directory fd,
`TAG` validation, full SHAs, C7 setgid refusal, C3 SKIP, `SHARE` = `$HERE`, switch-last migration); the write-recorder, start-form and
foreign-directory tests; the mutations; the acceptance rule from the incident — **every probe of a fallback sets `LR_SHARE` to the scratch
share; nothing runs from `/SNS/REF_L/shared`**. **Unchanged:** P1 (as re-specified at v1), P2, P3, P4's `<tag>@<sha7>` + symlink, P5, P7,
P8's canonical-copy rule, the transport, the base (`FY26B` @ `91e5c8f` — re-check at the series' `git am` on a fresh clone; `exp-review` @
`2324e5c`); the Developer revises the series in place in the read-only clone (kept, D-42), re-exports, updates `crossrepo.md` (sha256s, full
SHAs, `mv` rollback), and signals with a new `--allow-empty` commit on `feature/shared-deploy-exp-review` from `10ed77e`. **Retry
arithmetic:** attempts_done = 1 + 1 = 2 → v2 is attempt 2 of 3; a third rejection escalates.

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
