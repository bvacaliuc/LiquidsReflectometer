# todo.md — Integrator rejection, `shared-deploy-exp-review` v1 (series @ ledger 63ec500; attempt 1 of 3; review gate: design + security)

**Verdict: REJECT — four findings.** The deploy itself works on the target host class (a real scratch deploy of the fork's
`2324e5c`: verifier 12 PASS / 0 WARN / 0 FAIL; idempotent; update, running-tree and rollback cells as declared; the launcher
option starts the launcher). But the series' own tests fail 20 of 43 on that host, the launcher can source an
`activate.sh` chosen by the current directory, a README guarantee is falsified by a normal run, and the first rollback the
README prescribes lands on a tree whose environment pixi can no longer find. This is a cross-repo slug: the series is
revised in the ledger (`plans/shared-deploy-exp-review-series/`), signalled here as before. Not infrastructure.

## What passed (do not redo)

- **Signal:** `05cb88a` is empty against `exp-review` (no subject source change). **Series:** the 10 sha256s match
  `crossrepo.md`; `git am --3way` on a fresh `git clone --branch FY26B git@code.ornl.gov:ref_l/shared.git` (91e5c8f, push
  URL disabled) applies clean and gives exactly tree `07f9eb2`; the verifier is byte-identical to the ledger's canonical
  copy; `--exp-review-with-197` untouched; 8 files, all in the declared scope.
- **Integrator acceptance, real (an internet analysis node, `/usr/bin/pixi` 0.60.0; scratch clone of the applied share,
  never `/SNS/REF_L/shared`):** `REPO=<fork> TAG=exp-review SHA=2324e5c make-shared-deploy.sh` in `share/lr_reduction` →
  `exp-review@2324e5c/` cloned into the recorded gitlink's empty directory, `pixi install --frozen`, verifier **12 PASS /
  0 WARN / 0 FAIL** (C6: `activate.sh`'s pixi is `/usr/bin/pixi`, group-runnable; C7 whole tree group-readable), symlink
  moved, exit 0. Re-run: exit 0, nothing installed, `DEPLOYED.txt` unchanged. With a process "running" from the tree
  (argv naming it), `SHA=b86237b` → a new `exp-review@b86237b/`, symlink moved, the old tree and the process untouched
  (C2 WARN: the new tree unrecorded — expected). README roll back (rename) → link back on `@2324e5c`, verifier 0 FAIL /
  0 WARN. `nr_launcher.sh --exp-review -- --help` (absolute path, offscreen, config in scratch): `PIXI_PREFIX` exported,
  `--help` forwarded, `/usr/bin/pixi run --frozen new_launcher --help`, no `MPLCONFIGDIR`, the launcher still running at
  60 s. Not driven: a second user (no second account) — see B-3.
- **Design:** the departures hold (gitlink at the tree path — a gitlink at a symlink path errors; the `-print0` grouping;
  `PIXI_PREFIX` / own_checkout rows); `shellcheck -S warning` clean but the pre-existing SC2105; with `/usr/bin` hidden
  (a private namespace) 43/43 and the 20-row battery all red.

## BLOCKING — B-1: the tests cannot control the system-pixi lookup; 20 of 43 fail on the deploy host (rule a + d)

`make-shared-deploy.sh:92` `HOOK_PIXI=$(PATH=/usr/bin:/bin command -v pixi || echo "$PIXI")` runs the **real** system pixi's
`shell-hook` in the shim tests, against the fake repository ("could not find pixi.toml"). **Reproduced here:** `bash
lr_reduction/test-shared-deploy.sh` → **23 ok / 20 not ok** under umask 077, 022 and 002 (the analysis nodes, where the human
runs it, have `/usr/bin/pixi`); `crossrepo.md`'s `# 43 ok` and the README's Tests section are falsified there. Design
reviewer: with a group-runnable stub over `/usr/bin/pixi` 36/7 — T1h (#19, #20) tests the fallback branch only and cannot
pass with a system pixi, and its `rm -rf` leaves the symlink dangling so #29, #32–#34, #42 fail in cascade; the mutant
`HOOK_PIXI=$PIXI` (the declared preference removed) passes 43/43 on every host — the behaviour P5/departure 7 declare has
no test that can fail; bash `command -v` returns a non-executable `/usr/bin/pixi`.
**Fix (behaviour; domain = the pixi the deploy installs with and the pixi `activate.sh` names):** one seam the tests set
(e.g. `SYSTEM_PIXI=${SYSTEM_PIXI-/usr/bin/pixi}`, used only when it is executable, else `$PIXI`); the shim suite passes 43
(+ new) on a host with and without a system pixi; a test with a group-runnable system stub and a private pixi first on PATH
asserts `PIXI_EXE` is the system one and the switch happens (and its battery row); T1h restores the symlink (or T2/T4
address the tree directly). Consider installing with the same pixi `activate.sh` names (security A9 / design A5).

## BLOCKING — B-2: `bash nr_launcher.sh` derives `PIXI_PREFIX` from the current directory and sources its `activate.sh` (CWE-426/427; regression)

`launcher/nr_launcher.sh:51-63`: `PIXI_PREFIX=$(cd "$(dirname "$(realpath "$0")")/../lr_reduction" …)`. Started as
`bash nr_launcher.sh` (found on `PATH`), `$0` is the bare name; GNU `realpath` does not require it to exist, so the prefix
is `<parent of cwd>/lr_reduction`, and line 63 sources that directory's `exp-review/activate.sh` **as the user**.
**Reproduced here (scratch only):** a planted `<A>/lr_reduction/exp-review/{.cache,activate.sh}`, `cd <A>/cwd`,
`PATH=<share>/launcher:$PATH bash nr_launcher.sh --exp-review` → "Running new_launcher in <A>/lr_reduction/exp-review
directly" and `ATTACKER activate.sh ran as 6ov`; the absolute-path form resolves the share. Any local user can create
`/tmp/lr_reduction`; the base used the fixed path (departure 5 introduced this).
**Fix (behaviour; domain = every way the script is started — absolute path, `PATH` exec, `bash <name>`, `./`, a symlink, a
copy):** `PIXI_PREFIX` is the share's own `lr_reduction` or the fixed `/SNS/REF_L/shared/lr_reduction`, never a directory
chosen by the caller's cwd (e.g. derive from `realpath -e -- "$0"` only when that file `-ef` the share's launcher, else the
fixed path; or keep the fixed path with an explicit test override); a T3 row per start form, including `bash <name>` from a
foreign cwd.

## BLOCKING — B-3: "never changed after it is made" is falsified by a normal run (rule d; CWE-732)

`README-shared-deploy.md:13` ("never changed after it is made"), `:47` ("never touched"), crossrepo P4 ("immutable").
**Measured here:** in both scratch trees `conda-meta/pixi` and `conda-meta/history` were rewritten after the install by a
later `pixi run` (`@2324e5c`: install 15:06:13, rewrite 15:08:24; `@b86237b`: 15:07:31 → 15:07:40) — every scientist's
`pixi run --frozen new_launcher` writes into the shared env as that scientist. Consequence to settle (suspected, not
reproduced — no second account): a member with umask 077 rewriting those files could recreate the mode-600 lockout this
series fixes.
**Fix (either; the plan's call):** (a) run the tier without `pixi run` (source `activate.sh`, exec the env's
`bin/new_launcher` — the plan's §6 P10), so a run writes nothing; or (b) correct the wording ("the deploy never changes
it; pixi rewrites its env metadata at run time") **and** make the second-user run an acceptance row the human can
execute: user B (umask 077) starts the tier, then user C starts it; owner and mode of `conda-meta/pixi`, and C succeeds.

## BLOCKING — B-4: the first rollback the README prescribes lands on a tree pixi cannot find (rule d / e)

The migration (`crossrepo.md` step 2, README "Once") renames the in-place tree to `exp-review@<sha7>`. Design reviewer,
measured with `/usr/bin/pixi info --json` on a scratch project: pixi 0.60.0 names a detached env from a hash of the
project's **physical path** (`lr_reduction-5958026393026832092` before the `mv`, `-12523626091302242055` after). So the
README's "Roll back: point the symlink at the earlier tree" applied to the first deploy's only earlier tree makes `pixi
run --frozen` look for an env that does not exist (an install on the network, as the first scientist, under their umask).
`crossrepo.md`'s "mv it back" restores the path and is correct; the README does not say it. Also: the moved tree's name is
exactly what `SHA=<that sha7>` deploys into — the deploy would take it for an interrupted tree and fetch/install **into**
it, changing it in place (P4).
**Fix (behaviour):** the README and crossrepo state how the pre-immutable tree is restored (by `mv` back, not the symlink),
or the migration keeps its env reachable; the deploy never adopts a directory it did not create (no `DEPLOYED.txt` and not
an interrupted deploy of its own — e.g. a marker written before the clone) — a shim test for a moved legacy tree under the
`<tag>@<sha7>` name.

## Advisories (non-blocking; for v2 and the human)

Security (the group is already the trust boundary — `launcher/` 2775, `nr_launcher.sh` 775, `lr_reduction/` 2775 without
sticky, the share's `.git` group-writable — so these give no actor a new capability today): **A1** the lock
`exec 9> "$SHARE/.$TAG.deploy.lock"` follows a planted symlink and truncates its target (shown in scratch) — lock the
directory fd instead; **A2** the `g+rX` sweep follows a symlink swapped in mid-walk (reasoned) — sweep only a fresh install;
**A3** 124 720 of 178 627 files are g+w (`src/**/*.py`, `site-packages`); C1 cannot see `.cache` (as the base); **A4** C7
accepts whatever group the tree got — in a non-setgid SHARE the deployer's primary `users` (everyone) passes; refuse unless
SHARE is setgid to the team group; **A5** C6 walks the symlink's directories, not the target's (`readlink -f` first); the
private-path grep misses `/tmp`, `/var/tmp`, `/gpfs/*/users`; **A6** 7-hex SHAs throughout (`deployed()`, C2, C3), no
`origin == REPO` check — pass the full SHA in the human's commands; **A7** `pgrep` sees one node (the share is GPFS on every
node); `flock` on GPFS unverified; **A8** `TAG` allows a leading `-`, spaces, regex characters (a `pgrep` regex error reads as
"no process" — fails open); **A9** install pixi (PATH) ≠ runtime pixi (`PIXI_EXE`); C5/C8 test the former; **A10** another
member cannot run the verifier on a tree they do not own (git "dubious ownership") — the README's rollback "verify" step;
**A11** rollback does not take the lock; `ignore = untracked` hides planted files; `${TIER}` unquoted; `bash -ex` traces REPO.
Design: **A2** pgrep blind spot (as A7); **A3** the migration order leaves no `exp-review` during the whole first install —
build and verify first, refuse only at the switch; **A4** `SHARE` defaults to the cwd — default to `$HERE`; **A6** "git
status in /SNS/REF_L/shared is then clean" — two dirty gitlinks (`new_workflow*`) already exist; **A7** `mutate_once.py`
never checks a green baseline (10 of 20 rows indistinguishable from it on this host); **A9** C5c cannot fail in the shims
(no `pixi.lock` in the fixture); **A10** an interrupted tree whose `origin` is not `REPO` is fetched from `origin`; a partial
clone is refused with no recovery step in the README.
Integrator: the verifier skips C3 silently when called without `BRANCH_TAG` (the README's form passes it) — print a SKIP line.

## Incident (to the human; recorded in the ledger)

The security reviewer, probing B-2's fallback, ran a **copy** of the launcher outside a share: it fell back to the live
`/SNS/REF_L/shared/lr_reduction` and ran `pixi run --frozen new_launcher` from the live in-place `exp-review/` as 6ov for
~2 minutes (15:12–15:14; stopped; a GUI may have opened). It rewrote three pixi metadata files in the live env
(`conda-meta/{pixi,history,pixi_env_prefix}`, now 664 6ov:sns_ref_l_team — the 510 other files there are 660, same owner)
and `.cache/uv-cache` — the same bookkeeping any scientist's run writes (B-3). Nothing else; no process remains. The
human's migration step moves that tree aside anyway.

— Integrator, Claude Opus 5.5
