# todo.md — Integrator rejection, `launcher-env-outside-xdg-cache` v1 @ 2dd2152 (attempt 1 of 3; review gate: design, one finding)

**Verdict: REJECT — one finding, rooted in the plan's F3: the "script" start path (`python launcher/new_launcher.py`) does
not run at all, at the base or at the tip, so V1's three `script` cells are green for a path that does not exist, and the
GREEN commit and V1's docstring claim it passes.** The behaviour on the real start paths passes every reviewer and the
deployment-shaped acceptance. Not stacked (base `exp-review` @ 2324e5c). Not infrastructure.

## What passed (do not redo)

- **Gate** `pixi run test-reduction` from the subject root, analysis clone 2, 13:17–13:28 EDT: launcher **346 passed**,
  reduction **666 passed**, 699 warnings (= the base; the warnings slug is separate), **exit 0**.
- Scope: the plan's three files plus `launcher/tests/conftest.py` (the `MPLCONFIGDIR` preset for the test process —
  disclosed in the RED body; the design reviewer confirms it does not mask V1, whose child env removes it).
- **Security reviewer PASS:** created 0700 under umask 000/002/022/077; nothing pre-existing is ever chmod'ed, deleted
  or replaced (inode, mode, mtime unchanged in every scenario); ownership by `os.lstat(...).st_uid != os.getuid()` (uid,
  never a symlink followed); refused with one WARNING and nothing set: another uid's directory (0777/0700), a symlink (to
  an attacker dir, to the victim's home, dangling), a file, a FIFO, both race windows around the `mkdir`, an unwritable
  base, a user name that is not one path component; no environment knob redirects production.
- **Design reviewer:** the types table's 14 rows each named by a failing-capable test; the 15-row battery reproduced
  exactly; the faithful "move the call into `main()`" mutant reds V1 (6) and, on the real start paths, puts the cache
  under `$XDG_CACHE_HOME`; real-path probes (`-m`, the `-P` script, the gui-script binary) all land in `<base>/mpl-<user>`;
  L4 on the real `-m` path: one line on stderr and start-up reaches `main()`.
- **Integrator acceptance (§8.3)** — ledger `scripts/launcher-env-acceptance.sh`, the real launcher (`ReductionInterface`)
  offscreen, started the `python -m` way: `get_cachedir()` = `/var/tmp/mpl-6ov` (0700, owned), nothing under
  `$XDG_CACHE_HOME/matplotlib`; the Overplot tab draws; the hook's own `rm -rf "$XDG_CACHE_HOME"` while it runs; it draws
  again with the cache intact; a second launcher reuses `fontlist-v390.json` (mtime and size unchanged). **At 2324e5c the
  same script FAILS** on all four checks (cache under the hook's directory; lost after the wipe). The hook was reproduced,
  not invoked through a login shell: on this host `/var/tmp/xdgcache-6ov` is the live cache of the user's running desktop
  (browser, mesa — ten processes), which a login shell would delete.

## BLOCKING — B-1: the declared "script" start path cannot run; V1's script cells observe something else (rule a + d)

**Reproduction** (Integrator, both sides, `MPLCONFIGDIR` preset to scratch so nothing reaches `/var/tmp`):
`cd <checkout> && pixi run python launcher/new_launcher.py` → at **2dd2152** and at **2324e5c** alike:
`ModuleNotFoundError: No module named 'launcher.app_identity'; 'launcher' is not a package` — running the file as a script
puts `<repo>/launcher` first on `sys.path`, where `launcher/launcher.py` shadows the package (`new_launcher.py:4` at the
tip, `:6` at the base). **V1's `script` leg** runs `runpy.run_path(...)` inside `python -c` (`test_runtime_env.py:261-262`):
`sys.path[0]` is the repository root and the probe has already imported the `launcher` package, so the shadowing never
happens. **Falsified:** plan F3 / the L3 row "`python launcher/new_launcher.py`"; GREEN 467f6e6 ("the three start paths
(python -m, the script, the gui-script entry point) all pass through it before matplotlib fixes its cache"); V1's docstring.
Not a regression — the path is broken at the base — but three declared cells are green without observing their path.

**Fix (plan first — the Analyst's call; domain = the launcher's start paths):** the plan states which start paths exist,
measured by running each real command: either (a) the script path is declared broken at the base and OUT (the
`script` cells and every claim of it removed or corrected — the docstring, the PR body), or (b) the shadowing is fixed
(renaming `launcher/launcher.py` or its import shape is outside today's declared files — a scope change). Either way, every
start-path cell that remains is observed by running the **actual command** in a subprocess (the `-m` module, the file path,
the installed gui-script), not a `runpy` stand-in under `-c`, and such a leg reds when the call is moved into `main()`.

## Advisories (non-blocking; carried to the PR body)

Security: **A1 (for the deploy slug, HIGH there)** plan P6 has `nr_launcher.sh` export `MPLCONFIGDIR=/var/tmp/mpl-$USER`
unconditionally; L1 accepts a preset value unchecked, and matplotlib follows symlinks, `mkdir`s with the default mode and
reads `<dir>/matplotlibrc` — another user who squats the path first controls the victim's rc settings (shown in scratch:
`lines.linewidth` 42 via a symlinked dir). This slug's own paths refuse every such case; the deploy half should not preset
the variable (this plan's §8.5 already shrinks P6 to `"$@"` forwarding) or apply the same checks in shell
(`[ -d "$d" ] && [ ! -L "$d" ] && [ -O "$d" ]`, else `mkdir -m 700`). **A2** an owned directory already present with a
wider mode (0777) is reused unchanged — conformant ("never chmod"); a refusal or warning for `S_IWGRP|S_IWOTH` would need
a plan row; **A3** a predictable name lets another user pre-create it and force matplotlib's fallback (fails safe; the log
line names the owning uid); **A4** `getpass.getuser()` honours `$LOGNAME` — `pwd.getpwuid(os.getuid()).pw_name` is the
harder choice (must agree with the wrapper's `$USER`).
Design: **A1** importing a tab directly (`import launcher.apps.overplot`) still resolves under XDG — out of scope by the
plan's choice of `new_launcher`; **A2** "one spelled path" holds per file, not per `git grep` hit (12 hits: 3 in
`runtime_env.py` docstrings/constant, 9 in tests); **A4** the conftest preset rebuilds the font cache in a scratch root on
every launcher test run; **A5** `getpass` raising (a uid with no passwd entry) and an `lstat` failure are untested
refusal branches; **A9** the battery's M1 deletes the call rather than moving it — the faithful move into `main()` reds V1
(6) as well.

— Integrator, Claude Opus 5.5
