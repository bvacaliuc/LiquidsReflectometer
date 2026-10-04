# Plan: `launcher-env-outside-xdg-cache` (subject half) — the launcher's matplotlib cache lives node-local, outside `$XDG_CACHE_HOME`, however the launcher is started

**Campaign:** `exp-review-fixes` · **Leaf:** `launcher-env-outside-xdg-cache` (refs `triage/launcher-env-outside-xdg-cache`,
`feature/launcher-env-outside-xdg-cache`, `qa/launcher-env-outside-xdg-cache`) · **Status:** READY — v1 (attempt 1 of N = 3) —
dispatched 2026-10-04 against `exp-review` @ `2324e5c` (files disjoint from every open PR; no transport question — this is the
**subject half** the Advisor separated out in V1-26, `requests/shared-deploy-transport-decision.md` §1) ·
**Base:** `agentic/exp-review` @ `2324e5c` · **PR target:** `exp-review` on the fork, **draft** · **Not stacked.** ·
**Review domains:** design, security (block) · **Kind:** launcher — not reduction-path ·
**Sources:** charter §3 row `launcher-env-outside-xdg-cache` (reference F18; `todo-login-hook-deletes-running-pixi-env`);
`[human, 2026-10-04: "Will you make sure the slugs are actionable and then let the Administrator know that they can be executed while I
am reviewing the stacked PRs."]` (verbatim in `requests/shared-deploy-transport-decision.md`); the Advisor's split (V1-26): the
`REF_L/shared` half stays P6 of `plans/shared-deploy-exp-review-plan.md` (then only `"$@"` forwarding), the Puppet half stays
`fix/external/puppet`.

## Declared scope

**Files in:** `launcher/new_launcher.py`; one small Qt-free, matplotlib-free module for the decision (suggested
`launcher/runtime_env.py`; `launcher/app_identity.py` is acceptable if the Developer prefers one "before anything else" module —
one site either way); a new `launcher/tests/test_runtime_env.py`.

**Behaviours in** (L1–L5, §3). **Explicitly OUT:** the deploy repository (`nr_launcher.sh`, `make-shared-deploy.sh` — P6/P7 of
the deploy plan); the Puppet hook; **fontconfig's cache** (`$XDG_CACHE_HOME/fontconfig` is the hook's own stated target — "caches
off NFS homes" — and fontconfig rebuilds a missing cache without failing; moving it is the facility's call, recorded in §10 A2);
Qt's `QStandardPaths::CacheLocation` (the launcher stores nothing there; `QSettings` is config, under `$HOME/.config/ORNL/…` —
measured by the Integrator, I-27); the pixi environment's location (deploy half, C4); any other tab, file or behaviour.

## 1. Request

Reference F18 / `todo-login-hook-deletes-running-pixi-env`: the analysis nodes' login hook (`/etc/profile.d/fontcache-workaround.sh`,
Puppet-managed) sets `XDG_CACHE_HOME=/var/tmp/xdgcache-$USER` and **`rm -rf`s it on every login shell**. Anything the launcher keeps
under `$XDG_CACHE_HOME` is deleted the moment the scientist opens a second terminal. The Advisor (V1-26): *"`launcher/new_launcher.py`
`main()` sets `MPLCONFIGDIR` (and any other per-user cache the launcher uses) to a node-local path outside `$XDG_CACHE_HOME` before Qt
and matplotlib initialise … That protects every way the launcher is started, not only `nr_launcher.sh`."*

## 2. Verified facts at `2324e5c` (measured 2026-10-04 on `uvdl3` in the subject's pixi environment unless noted)

| # | Fact | Evidence |
|---|---|---|
| F1 | **matplotlib puts its cache under `$XDG_CACHE_HOME` when `MPLCONFIGDIR` is unset, and `MPLCONFIGDIR` wins when set.** | `matplotlib 3.9.4`; `python -c "import matplotlib; print(matplotlib.get_cachedir())"` → `~/.cache/matplotlib`; with `XDG_CACHE_HOME=/var/tmp/xdgcache-probe` → `/var/tmp/xdgcache-probe/matplotlib`; with `MPLCONFIGDIR=/var/tmp/mpl-probe` as well → `/var/tmp/mpl-probe`. `matplotlib._get_config_or_cache_dir`: `MPLCONFIGDIR` first, else `xdg_base_getter()/"matplotlib"`; the directory is created; if it is not writable matplotlib falls back to `tempfile.mkdtemp(prefix="matplotlib-")` with a warning, and raises `OSError` only if that fails too. |
| F2 | **The cache directory is resolved at import of the launcher's tabs, before `main()` runs.** | `launcher/new_launcher.py:1-11` imports `launcher.apps.direct_beam`, `file_batch`, `overplot`, `settings_editor`, `sld_calculator` at module top; `overplot.py`, `file_batch.py`, `direct_beam.py`, `template_batch.py`, `roi_selector.py` import matplotlib (`grep -rln 'import matplotlib' launcher/apps`); matplotlib's font manager resolves `get_cachedir()` when it loads. So a decision made inside `main()` (`:67-76`) is **too late** for the module-import start paths. |
| F3 | The launcher has three start paths. | `python -m launcher.new_launcher` / `python launcher/new_launcher.py` (`:78-79` `if __name__ == "__main__": main()`); the gui-script `new_launcher = "launcher.new_launcher:main"` (`pyproject.toml:23`); the deploy wrapper `nr_launcher.sh` (deploy repo; OUT) — all three import the module first. |
| F4 | `main()` already has a "before anything else" step. | `:67-72`: `ensure_identity()` then `migrate_legacy_settings()` before `QApplication([])` — `launcher/app_identity.py` (`ORG_NAME = "ORNL"`, `APP_NAME = "lr_reduction_new_launcher"`, `:21-23`) is the module that exists to run first; it imports `qtpy.QtCore` (`:19`), not matplotlib. |
| F5 | **The hook** (measured by the Advisor on the analysis node, `plans/shared-deploy-exp-review-plan.md` §7, 2026-10-04): `/etc/profile.d/fontcache-workaround.sh` sets `XDG_CACHE_HOME=/var/tmp/xdgcache-$USER` and runs `rm -rf "$XDG_CACHE_HOME"` on **every** login shell; its own comment gives the purpose as caches off NFS homes. The human's `~/.bashrc` remaps `XDG_CACHE_HOME=/tmp/$USER-$(hostname)` afterwards — a personal workaround no scientist has. **Not present on `uvdl3`** (`ls /etc/profile.d | grep -i font` → nothing), so the tests cannot rely on the hook; they set the variables themselves. |
| F6 | No launcher or library code touches `MPLCONFIGDIR` or `XDG_CACHE_HOME` today. | `grep -rn 'MPLCONFIGDIR\|XDG_CACHE' launcher src --include='*.py'` → nothing. |
| F7 | The deploy plan's P6 chose `/var/tmp/mpl-$USER` for the wrapper. | `plans/shared-deploy-exp-review-plan.md:54-57`. The subject half uses the **same** path so the two halves agree and a scientist sees one cache. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| L1 | **If `MPLCONFIGDIR` is already set, the launcher leaves it alone** — the wrapper's or the user's choice wins. |
| L2 | **Otherwise the launcher sets `MPLCONFIGDIR` to a node-local, per-user directory outside `$XDG_CACHE_HOME`: `/var/tmp/mpl-<user>`**, created `0700` if absent (`<user>` from `getpass.getuser()`, which honours `$USER`/`$LOGNAME` and falls back to the uid). This holds whether `XDG_CACHE_HOME` is unset (the default would be the NFS home — the hook's own reason to move caches) or set (to the hook's target or to anything else): detection is complete — the launcher never depends on *which* wiper is installed. |
| L3 | **The decision is made before the first matplotlib cache resolution on every start path** (F2/F3): `python -m launcher.new_launcher`, `python launcher/new_launcher.py`, and the `new_launcher` gui-script. The site is one function (`prepare_runtime_env(environ=os.environ)` suggested), **imported from a module that imports neither matplotlib nor Qt**, called from the top of `launcher/new_launcher.py` before the `launcher.apps` imports — or from `launcher/__init__.py`; the Developer picks one and the test (V1) proves it for all three paths by subprocess. `E402` is globally ignored (`pyproject.toml:247`), so a call above the imports is lint-clean; if the Developer prefers to keep imports first, the module-level call must still precede the `launcher.apps` imports. |
| L4 | **Failure leaves the launcher starting.** If the directory cannot be created or is not a writable directory owned by the user (an unwritable `/var/tmp`, a pre-existing file or another user's directory at that path), the function sets nothing, logs one line (`logging`, the launcher's logger) and returns — matplotlib then applies its own fallback (F1). No exception leaves the function; it never deletes or chmods anything that exists. |
| L5 | **Pure and testable:** the function takes the environment mapping and the base directory as parameters (`environ`, `base="/var/tmp"`), returns what it decided (the path set, or `None` with the reason), and is the **only** place the path is spelled. `main()`'s behaviour is otherwise unchanged. |

**Types and states** (`environ` is a `Mapping[str, str]`; paths are `str`):

| `MPLCONFIGDIR` | `XDG_CACHE_HOME` | `/var/tmp/mpl-<user>` | Outcome |
|---|---|---|---|
| set (any value, incl. `""`? — **`""` counts as unset**: matplotlib treats a falsy value as unset, F1 `if configdir:`) | any | any | unchanged (set) / treated as unset (`""`) |
| unset | unset | absent | created `0700`; `MPLCONFIGDIR` = it |
| unset | `/var/tmp/xdgcache-<user>` (the hook) | absent | same |
| unset | anything else (e.g. the human's `/tmp/<user>-<host>`) | absent | same — not special-cased |
| unset | any | present, mine, writable dir | reused; mode left as is; `MPLCONFIGDIR` = it |
| unset | any | present, not a directory / not writable / not mine | nothing set; one log line; matplotlib's fallback (F1) |
| unset | any | `base` not writable (`mkdir` raises) | nothing set; one log line |
| unset | `$USER` unset | — | `getpass.getuser()` resolves from the uid; same outcomes |

**Operation × state (each cell a required outcome, named by a test — U1–U3, V1):**

| Start path | hook env (`XDG_CACHE_HOME=<tmp>/xdgcache-u`) | `MPLCONFIGDIR` preset | no `XDG_CACHE_HOME` |
|---|---|---|---|
| `python -m launcher.new_launcher` (import only, `--help`-less: import the module in a subprocess, print `matplotlib.get_cachedir()`) | under `<base>/mpl-<user>`, **not** under `<tmp>/xdgcache-u` | the preset path | under `<base>/mpl-<user>` |
| `python launcher/new_launcher.py` (same subprocess probe via `runpy`/path) | same | same | same |
| the gui-script entry (`importlib.metadata.entry_points` → load `launcher.new_launcher:main`'s module) | same | same | same |

## 4. Files to change

| File | Change |
|---|---|
| `launcher/runtime_env.py` (new; or `app_identity.py`) | `prepare_runtime_env(environ=os.environ, base="/var/tmp") -> str \| None`; no Qt, no matplotlib import |
| `launcher/new_launcher.py` | the call before the `launcher.apps` imports (or in `launcher/__init__.py`); `main()` unchanged otherwise |
| `launcher/tests/test_runtime_env.py` | U1–U3, V1 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | scientist starts the launcher on an analysis node under the hook, then opens a second terminal | the second login's `rm -rf $XDG_CACHE_HOME` does not touch `/var/tmp/mpl-<user>`; plots keep rendering; no font-cache rebuild mid-session |
| common | first start on a node | `/var/tmp/mpl-<user>` created `0700`; the font cache builds there once |
| edge | the deploy wrapper already exported `MPLCONFIGDIR` (P6) | untouched (L1) — the two halves agree on the path anyway (F7) |
| edge | `XDG_CACHE_HOME` unset (a developer's shell on another machine) | still node-local (L2) — the default would be the NFS home |
| edge | tests run in CI / offscreen | the decision is side-effect-free beyond one directory under `base`; tests pass `base=tmp_path` and never touch `/var/tmp` |
| pathological | `/var/tmp/mpl-<user>` exists as a file, or as another user's directory | nothing set; one log line; the launcher starts (matplotlib falls back) |
| pathological | `/var/tmp` read-only | nothing set; one log line; the launcher starts |
| pathological | the function is called after matplotlib resolved its cache (the import-order mutation) | V1 reds — the probe prints a path under the hook target |
| pathological | `MPLCONFIGDIR=""` | treated as unset (F1's `if configdir:`); set to the node-local path |

## 6. Red-Green TDD seed

| # | Test | RED at the base |
|---|---|---|
| U1 | `prepare_runtime_env` × §3's types table rows, with `environ` a dict and `base=tmp_path`: the returned path, the mapping's `MPLCONFIGDIR`, the directory's existence and mode (`0o700` when created), "present and mine" reused without chmod, "present not a directory" / unwritable `base` → `None` + one log record (`caplog`) + mapping unchanged | function absent |
| U2 | `MPLCONFIGDIR=""` → treated as unset; `MPLCONFIGDIR=/x` → untouched and `/x` not created | — |
| U3 | the function module imports neither `matplotlib` nor `qtpy` (`sys.modules` after a fresh import in a subprocess) | — (guard for L3) |
| V1 | **the three start paths, by subprocess** (`sys.executable`), each with `XDG_CACHE_HOME=<tmp>/xdgcache-u`, `MPLCONFIGDIR` unset, `HOME=<tmp>/home`, and the function's `base` redirected through an env knob the module honours **only for tests** (or by `monkeypatch` of the base in a `-c` snippet): the child imports the module the way that path does and prints `matplotlib.get_cachedir()` → under `<base>/mpl-<user>`; a fourth leg with `MPLCONFIGDIR=<tmp>/preset` → `<tmp>/preset` | red: the base prints `<tmp>/xdgcache-u/matplotlib` |
| V2 | `main()`'s sequence is unchanged apart from the call: `ensure_identity()` still precedes `QApplication` (the existing `test_the_launcher_carries_the_tab` and identity tests pass) | passes — pin |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| the call moved into `main()` (after the `launcher.apps` imports) | V1 (all three legs print the hook path) |
| the call placed after the `launcher.apps` imports at module level | V1 |
| path spelled under `$XDG_CACHE_HOME` (`os.path.join(xdg, "mpl")`) | U1, V1 |
| `MPLCONFIGDIR` overwritten when preset | U2, V1 (preset leg) |
| `""` treated as set | U2 |
| `mkdir` without `0o700` / `chmod` applied to an existing directory | U1 (mode leg; "present and mine" leg) |
| exception allowed to escape on an unwritable base | U1 (`None` + log leg) |
| path spelled in two places (module + `main()`) | U1's "only place" grep leg (`git grep -n 'mpl-' launcher` → one hit) |

Frame: one function, one call site, one spelled path; no Qt or matplotlib import in the module that decides (U3).

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root on the feature tip.
2. §6 RED→GREEN; §7 recorded per row.
3. **Deployment-shaped acceptance (Integrator, analysis node, under the real hook):** from a fresh login shell, start the
   launcher from the feature tip (`python -m launcher.new_launcher` in the pixi env — the deploy wrapper is OUT) → in another
   terminal `ls -ld /var/tmp/mpl-$USER` (exists, `0700`, owned by the user) and `ls $XDG_CACHE_HOME/matplotlib` (**absent**);
   open a **second** login shell (the hook wipes `$XDG_CACHE_HOME`) → the running launcher's plot tabs still render (open
   Overplot, draw once); quit; quote the paths.
4. Security reviewer: the directory is created `0700`, never chmod'ed if pre-existing, never deleted; a pre-existing path owned
   by someone else is refused (no symlink following — `os.lstat`/`is_symlink` check recorded).
5. PR body: launcher-only; the deploy half shrinks to `"$@"` forwarding (P6) — one line for the deploy plan; the Puppet half
   unchanged; what a scientist sees (one font-cache build per node, then nothing).

## 9. Learnings relied on

- The campaign's standing lesson (A-16 … A-42): every cell of §3's tables is named by a test; a §7 row's test observes through the
  path its mutation breaks — here the **import-order** mutation is the one that matters, so V1 runs the real start paths by
  subprocess rather than calling the function.
- `launcher/app_identity.py`'s own precedent (F4): a "before anything else" step belongs in one module that imports as little as
  possible, called once; `editor-sections`' S3 note: "Qt caches the settings root at the first QSettings construction in a process" —
  the same class of first-touch state, which is why the decision must precede the first matplotlib import.
- `plans/shared-deploy-exp-review-plan.md` §6–§7 (Advisor): the hook's text, its purpose, and the scientist who could not start the
  review tier — the reason the launcher protects itself rather than trusting the wrapper.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | `/var/tmp` is node-local and persistent across logins on every analysis node. | Yes (the hook itself uses `/var/tmp/xdgcache-$USER`); P6 chose the same base. |
| A2 | fontconfig's cache (`$XDG_CACHE_HOME/fontconfig`) is left where the hook puts it. | Yes — it is the hook's stated target and fontconfig rebuilds without failing; if the Integrator's acceptance shows a visible stall after the second login, that is an advisory for the Puppet ticket, not this slug. |
| A3 | Whether the launcher should also move `XDG_CACHE_HOME` itself for its children. | **No** — too broad for a launcher; the pixi environment's location is the deploy half (C4). |
| A4 | Base directory override for tests. | A parameter (`base=`), and if a subprocess needs it, an env knob read only by the function (named in the test; documented as test-only). |

## Revision history

v1 — authored and dispatched 2026-10-04 against `exp-review` @ `2324e5c` (the subject half separated by the Advisor in V1-26 at the
human's "make sure the slugs are actionable"; A-48). Facts F1–F3, F6 measured in the pixi environment before authoring; F5 cited from
the Advisor's measurement on the analysis node.
