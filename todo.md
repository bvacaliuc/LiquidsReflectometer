# todo.md — Integrator rejection, `shared-deploy-exp-review` v2 (series @ ledger 655c180, 15 patches; attempt 2 of 3 — the next is the last)

**Verdict: REJECT — two findings; every v1 blocker is fixed.** A fresh deploy can fail its own C7 depending on where
`TMPDIR` lives, C7 cannot see a tree in the wrong group (and no test can fail on either), and the README's "a re-run changes
nothing" is falsified by the verifier the deploy runs. Both fixes are small and the plan already points at them. Cross-repo:
the series is revised in the ledger and signalled here as before. Not infrastructure.

## What passed (do not redo)

- **Signal** `48bb42f`/`787a079` empty against `exp-review`; the 15 sha256s match `crossrepo.md`; `git am --3way` on a fresh
  `git clone --branch FY26B git@code.ornl.gov:ref_l/shared.git` (91e5c8f, push URL disabled) → exactly tree `223ce5e`; the
  verifier byte-identical to the ledger's canonical copy; `--exp-review-with-197` untouched; 8 files, in scope.
- **v1 B-1 fixed:** shim tests **90 ok / 0 not ok** on this analysis node (`/usr/bin/pixi` 0.60.0) under umask 077 and 022; the
  `SYSTEM_PIXI` seam; design: the seam both ways and its rows red (V1, V1b, F14).
- **v1 B-2 fixed:** `bash nr_launcher.sh --exp-review -- --help` from a foreign cwd holding a planted `lr_reduction/exp-review/
  activate.sh`, `LR_SHARE=<scratch share>`: the planted file is not sourced; `PIXI_PREFIX` = the share; the launcher is exec'd
  from the env's `bin/` (no `pixi run`), still running at 45 s; nothing in the trace names `/SNS/REF_L`. T3: six start forms.
- **v1 B-3 fixed for scientist runs:** after that launcher run, `conda-meta/{pixi,history,pixi_env_prefix}` mtimes and the
  count of files newer than `DEPLOYED.txt` unchanged.
- **v1 B-4 fixed:** a planted `exp-review@b86237b/` without a marker → "exists and was not made by this script … not deployed
  into", exit 1, link unchanged; the README's `.in-place` + `mv` rollback.
- **Real deploy** (scratch share made setgid `sns_ref_l_team`, as the real one): `exp-review@2324e5c` 15 PASS / 0 WARN /
  0 FAIL (a tree first created in a non-setgid share — see B-5), `DEPLOYED.txt` with the full SHA and `PIXI=/usr/bin/pixi`;
  re-run "nothing to install"; an update with a process running from the old tree leaves both alone and keeps the link when
  verification fails. C7 correctly FAILs a non-setgid share (v1 security A4 adopted).
- **Battery:** 42 rows, 42 red, restore 3/3 (design; counts as recorded but M3 42 vs 43).

## BLOCKING — B-5: a foreign-group file can land in a fresh tree; C7 cannot see a tree in the wrong group; no test can fail on either

**Measured here:** a **fresh** deploy into a scratch share setgid to `sns_ref_l_team` → **`FAIL C7 … 1 path(s) not group
sns_ref_l_team`**, the switch refused: `.cache/uv-cache/sdists-v9/editable/<h>/<r>/lr_reduction-…whl` is `6ov:users 0644`
(reproduced twice, `@b86237b` and `@2324e5c`). **Mechanism (design, traced with uv 0.12.17 + hatchling):** the editable
wheel is built in `$TMPDIR` and moved into the cache — a rename when `$TMPDIR` is on the share's filesystem (keeps `$TMPDIR`'s
group), a copy when it is not (inherits the setgid group). **Correction to this seat's first statement:** on the real share
(GPFS) with `TMPDIR` unset (`/tmp` on `/`) the wheel is copied and C7 most likely PASSes — the live tree built 2026-10-01 with
the same pixi has 0 paths outside the team group. It FAILs wherever `TMPDIR` shares the share's filesystem: every scratch
acceptance on `/`, any deployer with `TMPDIR` on GPFS. **Also:** C7 compares paths with the tree's own group, never with
`TEAM` — a tree `chgrp -R users` inside a setgid team share PASSes both C7 lines (design repro; here, a tree first made in a
non-setgid share kept group `users` with 155 898 g+w paths and PASSed after the share was fixed). A faithful mutant survives:
C7's group leg blinded (`wg_n=0`) → 0 tests fail (the shims use `TEAM=$(id -gn)`, the primary group, so no fixture ever makes
a foreign group). And `DEPLOYED.txt` is written before verification: a FAILed tree counts as complete, a re-run only
re-verifies it, and the README has no recovery for "deployed but FAILed".
**Fix (behaviour; domain = every path the deploy creates or a tool moves into the tree):** the deploy refuses a SHARE that is
not setgid to the team group before cloning; every path of a new tree ends in the team group (a `chgrp -h` sweep with the
`g+rX` sweep, and/or `TMPDIR` inside the tree's `.cache` for the install); C7 FAILs when the tree's group is not `TEAM`; a
FAILed verification leaves the tree recoverable (not "complete"), with a README step. **Tests:** a share in a supplementary
group of the runner that is not the primary one (SKIP line if none), a stub install that renames in a file made in a non-setgid
directory on the same filesystem, `REPO=file://…` (a local-path clone hardlinks `.git/objects` and carries the upstream's
group), and a T2 row "a tree in another group inside a team share → C7 FAIL" — each red at v2.

## BLOCKING — S-1: "a re-run changes nothing" / "never changes a complete tree" falsified by the deploy's own verifier (rule d)

`make-shared-deploy.sh:21`, `README-shared-deploy.md:22` ("never changes a complete tree") and `:61` ("Running it again for the
same commit installs nothing and changes nothing"). The deploy always runs the verifier (`:156`), and its C5/C8 `pixi run
--frozen` rewrite the env's bookkeeping. **Measured here:** `exp-review@2324e5c`: `DEPLOYED.txt` 17:01:09; the re-run logged
"deployed already: nothing to install" and closed at 17:02:56.806 — `conda-meta/history` 17:02:55.719 and `conda-meta/pixi`
17:02:55.733 were rewritten in that window (design: also `.git/index` by C1's `git status`; the README's rollback "verify"
step does the same). A `pixi run` inside a tree launchers run from installs into it in place if pixi judges the env stale.
**Fix (preferred):** the verifier's run checks (C5/C8) exercise the runtime path itself — `source activate.sh` and the env's
`bin/python` / `bin/new_launcher` with `PYTHONDONTWRITEBYTECODE=1`, no `pixi run` — so verifying writes nothing (and tests what
scientists run); a listing/mtime snapshot test across a re-run; **or** reword the three claims to what is true.

## Advisories (non-blocking; for v2's successor and the human)

Security: **(1)** = B-5's C7 tree-group leg; reachable today via the README rollback (`ln -sfn` to any `@sha` dir is unchecked);
**(2)** the uv wheel itself is 0644 — no exposure, functional only; prefer `chgrp -h` (plain chgrp/chmod follow a final symlink)
or delete `.cache/uv-cache` after install; **(3)** the `.deploying` marker is plain text — a group member can forge
`host`+dead pid in a group-writable dir at `<tag>@<sha7>` and have it adopted (fetch/checkout/install as the deployer; its
`.git/config`/hooks run then); require `-O` on tree and marker, or build in a 0700 incoming dir and open after the sweep
(also closes A2's residue); **(4)** the verifier executes `PIXI=` from group-writable `DEPLOYED.txt` — require it equal
`SYSTEM_PIXI` or root-owned; **(5)** `LR_SHARE` is validated and no worse than `PATH`; a stale export to a deleted `/tmp` path
could be recreated by another user — require user/root/team ownership, no o+w; `TIER` not contained under the share; **(6)**
run-time writes: Mantid's geometry cache may write `.vtp` beside an IDF read from the env's group-writable `instrument/`
(suspected; cover a **reduction** in the acceptance listing-diff, not only a start); `export PYTHONDONTWRITEBYTECODE=1` comes
after `source activate.sh` (which sources `activate.d/*` and completions) — move it before; activate.sh replaces PATH and sets
`LD_PRELOAD` (behaviour change for subprocesses); **(7)** any local user can `flock` the share dir (o+r) and block deploys;
the fd is inherited by descendants; **(8)** C2/C3 still compare 7 hex; `origin == REPO` unchecked; **(9)** README rollback
switches first and verifies after (verify the target first); no lock; README:154 cites `launcher/runtime_env.py`, absent from
`2324e5c`; **(10)** `bash -ex` traces REPO, which is also written to world-readable `DEPLOYED.txt`/`.git/config` — refuse
userinfo in REPO.
Design: **A2** "exp-review works throughout" (README:90, crossrepo step 2) — between `mv … .in-place` and the switch,
`--exp-review` falls through to "Manfest path does not exist" for the re-verify's duration; **A3** the setgid precondition is
asserted, not checked (B-5's fix); **A4** `SHARE=$(… pwd -P)` gives `/gpfs/…` on the real share — the `fonts.conf` edit is
untested on a physical≠logical path (every real deploy so far ran in `/tmp`); **A5** `TIER` left an unresolved symlink
survives (the running-tree cell is the acceptance's only); **A6** T2b's `^PASS C7 ` grep is satisfied by the share line —
grep the readability line; **A7** the test's fixed `/tmp/shared-deploy-system-pixi.*`; `test-shared-deploy.sh` 473 lines; the
verifier runs C7's `find` and the `PIXI=` sed twice; **A8** battery M3 42 vs the record's 43.
**For the human (machine-local, not this series):** the deploying account's global git config has `safe.directory = *`
(plus `/SNS/REF_L/shared/lr_reduction/exp-review-with-197` appended five times — that option's `git config --global --add` on
each run). `*` disables git's dubious-ownership guard, so another member's `.git/config`/hooks in a tree would run as the
deployer (security advisory 3). Not changed here.

— Integrator, Claude Opus 5.5
