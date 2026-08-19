# Learnings — `harness-hardening` (campaign `exp-settings-roi`)

Written after the v1 rejection, whose findings were *measured* rather than
argued — which is itself the lesson worth keeping.

## 1. Verify a patch against the attribute that actually exists

**Rule.** Before monkeypatching a method to neutralize it, confirm the class
you are patching is the one that defines it, and that the production call sites
go through that class. Otherwise the patch shadows an inherited attribute
nothing reaches, and the suite goes green while the hazard is untouched.

**Why.** v1 patched `QMessageBox.exec_` to stop modal dialogs blocking under
offscreen Qt. Probed on this environment (qtpy 2.4.3 / PyQt5 5.15.11):

```
QDialog      'exec_' in __dict__: True    'exec': True    'open': True
QMessageBox  'exec_' in __dict__: False   'exec': False   'open': True
```

`exec_` is defined on `QDialog` and merely inherited by `QMessageBox`, and
every blocking site in `launcher/` is a plain `QDialog(...).exec_()`. So the
patch covered a surface with no production callers, and the self-test written
alongside it was satisfied by that same dead surface. A test and a fix derived
from the same wrong model agree with each other.

Second-order trap in the correction: patch the base class and the *return
value* starts to matter. `QDialog.Accepted` is 1; `QMessageBox.Ok` is 1024.
Call sites compare against 1, so a base-class patch returning `Ok` would
silently convert every accept path into a cancel — a worse failure than the
hang, because it is silent.

**How to apply.** One `__dict__` probe answers it. When neutralizing modals in
a Qt suite, patch `QDialog.exec_`/`exec`/`open` and return `QDialog.Accepted`;
keep the `QMessageBox` static convenience methods patched separately, because
those *are* defined on `QMessageBox`.

## 2. A test that cannot fail is not a backstop — check by breaking the thing

**Rule.** For any self-test whose job is to prove a safety mechanism is armed,
disarm the mechanism once and watch the test go red. If it stays green, it is
guarding nothing.

**Why.** The obvious hanging-test self-test uses `while True: pass`. That does
not discriminate the timeout *method*: SIGALRM interrupts a pure-Python loop
fine, so the default `signal` method kills a busy loop and the test passes
straight through the regression it exists to catch. The case that matters —
and the case the whole harness exists for — is a hang inside C++ code, where
CPython cannot run the handler until control returns to the eval loop.

Measured on one scratch tree with only the method changed:

| `timeout_method` | outcome |
|---|---|
| `thread` | killed at 10 s, Timeout banner, non-zero rc |
| `signal` | never killed; ended by an external 45 s kill (rc 124) |

The self-test now blocks in `QMessageBox.warning` instead, and carries its own
`timeout(10)` marker so it costs about ten seconds rather than the harness's
120 s default.

**How to apply.** Write the disarm probe as a throwaway, run it, and put the
two-row table in the commit body. It costs a minute and converts "this test
should catch a regression" from a claim into evidence.

## 3. Scope a claim to the invocation you actually tested

**Rule.** When you verify a property, state it for the configuration you ran,
not for the mechanism in general — or run the other configurations.

**Why.** v1 added a `pytest_collection_modifyitems` hook and my commit said the
reduction suite was "verifiably untouched", citing a chained `pixi run
test-reduction` where no timeout banner appeared under the reduction stage.
True — and irrelevant to the risk, because that chain runs two separate pytest
processes. In a single combined invocation the hook was session-global and
would have armed a 120 s timeout on all 107 reduction tests, where a firing
thread-method timeout is `os._exit` in the middle of the suite. The reviewer
found it by running the combination I had not.

The v2 hook filters on the item's path and on an explicit `--timeout`, and the
evidence is now the combined run:

```
pytest tests launcher/tests --collect-only   ->  115 collected
reduction items carrying a timeout marker:   0 of 107
launcher items carrying timeout=(120,):      8 of 8
```

**How to apply.** Ask which invocations exist (chained task, bare pytest,
combined paths, CI) and either test each or name the one you tested. A negative
property — "X is *not* affected" — is worth an explicit probe, because the
evidence for it is silence, and silence is also what a broken check produces.

## 4. Where a process-global default cannot be restored, do not restore it

**Rule.** When isolation depends on a process-global setting with no undo,
leave it installed at teardown. Restoring the surrounding state to look tidy
can re-open the hole the setting was closing.

**Why.** Qt caches the settings root at the first `QSettings` construction in a
process, so a fixture that redirects at first use has already lost to any
module that constructed one at import. v1 redirected `IniFormat` via `setPath`
but its teardown restored `defaultFormat` to `NativeFormat` — and
`NativeFormat` was never redirected, so a subsequent construction resolved to
the developer's real `~/.config`, which the reviewer reproduced against the new
fixture. The redirect is installed at conftest **import** now, for both
formats, into a session scratch root; the per-test fixture only narrows it to
`tmp_path`; teardown restores the organization/application names (which do have
an undo and do need one) and never the format.

**How to apply.** Separate the parts of an isolation setup that are per-test
from the parts that must hold for the process lifetime, and put the latter at
import scope. Then ask, for each thing teardown restores, what a later
construction resolves to — the answer is what the next test inherits.
