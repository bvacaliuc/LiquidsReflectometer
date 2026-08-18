# Learnings — `launcher-test-harness` (S0, campaign `exp-settings-roi`)

Discovered while implementing the slug; both generalize beyond this repo.

## 1. `pytest-timeout`'s default `signal` method cannot interrupt a test blocked in native code

**Rule.** Any pytest suite whose tests can block inside a C/C++ call —
a Qt modal or event loop, a native library, a blocking syscall in an
extension — must run with `--timeout-method=thread`. The default
`signal` method is not a backstop there; it silently never fires.

**Why.** The `signal` method arms `SIGALRM` and raises from a Python
signal handler. CPython runs signal handlers only between bytecodes, so
if the interpreter is parked inside a C++ call that never returns to the
eval loop, the alarm is deferred indefinitely. `thread` instead runs a
watchdog thread that dumps every thread's stack and calls `os._exit`,
which is independent of what the main thread is doing.

Measured on `feature/launcher-test-harness` with a throwaway probe
(`isolated_qapp`, no `no_qmessagebox`, `QMessageBox.warning`) under
`QT_QPA_PLATFORM=offscreen`:

| Invocation | Result |
|---|---|
| `--timeout=20` (method `signal`, the default) | no timeout ever fired; still blocked when an external 150 s kill ended it (exit 124) |
| `--timeout=20 --timeout-method=thread` | fired at exactly 20 s; Timeout banner + stack ending at the `QMessageBox.warning` line; exit 1 |

This matters here because the campaign's whole reason for P-2 is the
PoC's 10-hour `QMessageBox` orphan (Developer-Retrospective §B). With
the default method the harness has **prevention only** (the
`no_qmessagebox` fixture); the moment a future GUI slug forgets the
fixture, the suite hangs forever with zero stdout — exactly the failure
the harness exists to stop. The plan's failure-mode matrix asserted
`--timeout=120` "kills it loudly"; that assertion was wrong, and the
plan's own acceptance criterion ("demonstrably hangs-then-times-out")
is what exposed it.

**How to apply.** For any GUI/native-touching pytest task, put
`--timeout-method=thread` in the task definition next to `--timeout=N`,
not in a developer's shell history. When writing a plan that claims a
timeout is a backstop, require the plan's RED step to *observe* the kill
rather than assume it — an unobserved backstop is an assumption, and
this one was false. Pairs with
`setup/patterns/native-crash-and-hang-diagnosis.md` (a hang in native
code needs a mechanism that does not depend on the Python main thread)
and with the always-run-experiments-under-an-external-`timeout` habit
that kept these probes from becoming orphans themselves.

## 2. `pixi lock --check` is not read-only: it rewrites an older-format lock and exits 0

**Rule.** Do not treat `pixi lock --check` as a verification-only
command, and do not assume a `pixi.lock` diff's size reflects the
dependency change. Measure the semantic delta by generating a
same-format baseline and diffing that.

**Why.** pixi 0.70.1 against a v6 lock prints `the lock file is
up-to-date but uses an older format (v6), re-solving all environments
using locked content to upgrade to v7`, **writes** the upgraded file,
and exits **0** — despite `--check` being documented as "Check if any
changes have been made to the lock file. If yes, exit with a non-zero
code." On this repo that command is the `pixi-lock-check` **pre-push**
hook, so a push mutates the working tree as a side effect.

Consequences seen on this slug: adding one dependency produced a
12,235-line `pixi.lock` diff. Isolating it (generate a v7 baseline from
unmodified `exp`, diff the two v7 files) showed the real change is **14
lines** — one environment entry plus one package record for
`pytest-timeout-2.4.0`. Everything else was the format upgrade.
Hand-pinning v6 to keep the diff small is futile: the repo's own
pre-push hook re-upgrades it.

Note `pixi lock --no-install` is not a workaround for inspecting the
outcome — on a project with pypi source dependencies it panics
(`build dispatch initialization failed: installation of conda
environment is required to solve PyPI source dependencies but
`--no-install` flag has been set`).

**How to apply.** (a) When a lock diff dwarfs the change, isolate the
semantic delta before asking a human to review it, and put the number in
the commit body. (b) Treat a lock **format** bump as a deploy-compat
question, not a formatting detail: verify every consumer's tool version
before it merges. Here CI is safe (`prefix-dev/setup-pixi@v0.9.4`, no
version pin, so it installs a pixi that reads v7), but a facility
consumer pinned to an older pixi — the `lr_reduction_exp-pixi-deploy`
tail — is a human check before merge. (c) A `--check`-style flag that
writes is worth verifying once per tool rather than trusting.
