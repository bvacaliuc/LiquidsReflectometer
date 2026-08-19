# Plan: harness-hardening

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` · charter §4
mid-effort addition (2026-08-18) from the S0 gate's advisory findings
(PR #15 body, test-reviewer; Integrator recommendation: fold in before more
slugs build on the fixtures) · DAG-independent, **land before T2**
**Retry attempt:** 2

Review domains: test-reviewer (**blocking** — upgraded at the v1
rejection: the slug's deliverable is self-tested guarantees, so the
domain that measures whether the guarantees hold must gate it; the v1
"advisory — it authored the findings" premise inverted the logic),
ui-aspects-reviewer (advisory).

## Symptom (the three verified findings + tail items)

1. **`isolated_qapp` isolation is accidental.** Qt caches the settings
   root at the first `QSettings` construction per process, so only the
   first test's `XDG_CONFIG_HOME` redirect is honored; separation survives
   only via the `test-org-{tmp_path.name}` suffix. If any launcher module
   constructs `QSettings` before the first fixture runs, the cached root is
   the developer's real `~/.config` for the whole session. Org/app names
   are never restored after yield.
2. **The modal backstop misses call forms.** `no_qmessagebox` patches four
   static methods only; instance `.exec_()`/`.exec()` calls and the 26
   `QFileDialog.get*` sites in `launcher/` route around it. (The PoC-era
   `QMessageBox`-subclass dialogs with overridden `exec_` are removed by
   S1; direct instance-exec and file dialogs remain uncovered.)
3. **The timeout backstop lives only in the pixi task string.**
   `testpaths = ["tests"]` excludes `launcher/tests`, and ini options carry
   no `timeout_method` — a bare `pytest launcher/tests/test_x.py -k …`
   (the inner loop every slug author actually types) has **no timeout at
   all**, which is the 10-hour-orphan class this harness exists to kill.

Tail items from the same review: no `fileName()` assertion (the roundtrip
test passes even with isolation broken); no self-test proves the backstop
fires; no top-level-widget drain between tests; no `ARG001`
per-file-ignore for `launcher/tests/**` (pushes authors into the
marks-vs-args trap where a dropped mark produces a hang, not a failure).

## Verified state (against `agentic/exp` @ `a4ae8b8`, 2026-08-18)

- `launcher/tests/conftest.py` = S0's version: offscreen env,
  `isolated_qapp` (org/app suffix + `XDG_CONFIG_HOME`), `no_qmessagebox`
  (four statics). `launcher/tests/test_harness.py` = the two seed tests.
- `pyproject.toml`: `[tool.pytest.ini_options]` has `testpaths = ["tests"]`
  and no `timeout_method`; ruff `[tool.ruff.lint.per-file-ignores]` has
  exactly one entry (`"launcher/**" = ["BLE001"]`, line ~246);
  `test-launcher` task carries `--timeout=120 --timeout-method=thread`
  (S0's landed form — keep as documentation and belt).
- Fixture consumers in flight: S1 (at the Integrator), S2/S3 (triage
  pushed). **This slug must stay additive** — fixture names
  `isolated_qapp` / `no_qmessagebox` keep their signatures; S1–S3 tests
  written against them must pass unmodified.

## Files to change (on `feature/harness-hardening` from `agentic/exp`)

1. `launcher/tests/conftest.py`:
   - `isolated_qapp` gains real isolation:
     `QtCore.QSettings.setPath(QtCore.QSettings.IniFormat,
     QtCore.QSettings.UserScope, str(tmp_path))` **and**
     `QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)`
     (setPath is honored per-construction, unlike the cached
     `XDG_CONFIG_HOME` root; IniFormat is deterministic across platforms).
     Keep the org/app suffix (belt) and the env redirect (braces).
     Teardown after `yield`: restore prior org/domain/app names and
     default format; drain widgets —
     `for w in QtWidgets.QApplication.topLevelWidgets(): w.close();
     w.deleteLater()` then `app.processEvents()`.
   - `no_qmessagebox` extended in place (same name — additive): besides
     the four statics, patch instance execs:
     `monkeypatch.setattr(QtWidgets.QMessageBox, "exec_", lambda _self:
     QtWidgets.QMessageBox.Ok)` and likewise `"exec"` (guard with
     `hasattr` — qtpy/Qt6 naming).
   - New fixture `no_qfiledialog`: patch `QFileDialog` statics
     `getOpenFileName` → `("", "")`, `getSaveFileName` → `("", "")`,
     `getOpenFileNames` → `([], "")`, `getExistingDirectory` → `""`
     (staticmethod lambdas, underscore params — `ARG` discipline until the
     per-file-ignore lands in this same slug).
   - Scoped timeout default:

     ```python
     def pytest_collection_modifyitems(items):
         for item in items:
             if item.get_closest_marker("timeout") is None:
                 item.add_marker(pytest.mark.timeout(120))
     ```

     (This conftest governs only `launcher/tests/`, so `tests/` reduction
     timings are untouched.)
2. `pyproject.toml`:
   - `[tool.pytest.ini_options]` += `timeout_method = "thread"` (selects
     the method wherever a timeout is armed; arms nothing by itself, so
     the reduction suite is unaffected).
   - `[tool.ruff.lint.per-file-ignores]` += `"launcher/tests/**" =
     ["ARG001"]` with a one-line comment (fixture params in signatures are
     the pytest idiom; the ignore removes the marks-vs-args trap).
3. `launcher/tests/test_harness.py` — three additions:
   - `test_qsettings_file_lands_in_tmp(isolated_qapp, tmp_path)`:
     construct `QSettings()`, `setValue`, `sync()`, assert
     `QtCore.QSettings().fileName().startswith(str(tmp_path))` — the
     assertion finding 1 says would have caught the cached-root bug.
   - `test_instance_exec_neutralized`
     (`usefixtures("isolated_qapp", "no_qmessagebox")`): construct
     `QtWidgets.QMessageBox()` and assert `.exec_()` returns immediately
     (== `QMessageBox.Ok`).
   - `test_timeout_backstop_fires`: write a one-test hanging file
     (`while True: pass` inside a test) to `tmp_path`, run
     `[sys.executable, "-m", "pytest", str(f), "--timeout=5",
     "--timeout-method=thread", "-p", "no:cacheprovider"]` via
     `subprocess.run(..., timeout=60, capture_output=True)`, assert
     returncode != 0 and `b"Timeout" in` combined output — the disarm
     self-test the review asked for (if pytest-timeout is absent or the
     method regresses, THIS fails rather than a future slug hanging).

**Not in scope:** changing fixture names/signatures; adding timeouts to
the reduction suite (`tests/`); retrofitting S1–S3's test files (they
benefit automatically at their next branch-from-exp); the `pixi.lock`
(no dependency changes — the format caveat from the port plans applies).

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Later test inherits an earlier root (the cached-root bug) (common) | `test_qsettings_file_lands_in_tmp` per-test | `setPath` + default-format, per-construction semantics |
| Launcher module constructs QSettings at import/instantiation before fixtures (edge) | same test, plus real-`~/.config` writes become impossible under `setPath` | setPath applies process-wide once set by the first fixture use |
| Org/app leak across tests (edge) | teardown restore; existing roundtrip test still passes | snapshot-and-restore in teardown |
| Instance `.exec_()` modal (common in future slugs) | `test_instance_exec_neutralized` | extended `no_qmessagebox` |
| `QFileDialog.get*` modal (26 sites) (common, T2+) | timeout backstop + new fixture available | `no_qfiledialog` opt-in |
| Inner-loop bare `pytest` hang (common) | conftest marker default + `timeout_method` in ini | scoped to `launcher/tests` |
| Backstop silently disarmed (pathological) | `test_timeout_backstop_fires` goes red | subprocess self-test with outer timeout |
| Reduction tests suddenly time-limited (regression this slug must not cause) | `pixi run test-reduction` green in acceptance | method-only in ini; marker default scoped to launcher conftest |
| S1–S3 tests break against extended fixtures (regression) | their suites at the tip | additive-only rule; same names/signatures |

## Red-Green seed

- RED: add the three `test_harness.py` tests first;
  `pixi run test-launcher`: `test_qsettings_file_lands_in_tmp` FAILS
  (cached root — the measured finding), `test_instance_exec_neutralized`
  must be observed to hang-then-die under the task's 120 s thread
  backstop (run it with `--timeout=10` locally to keep RED cheap;
  the kill IS the red evidence, per the S0 learning's observe-the-kill
  rule), `test_timeout_backstop_fires` passes already (backstop exists)
  — note that in the commit body rather than faking a red for it.
- GREEN: land the conftest + pyproject changes; full
  `pixi run test-launcher` green (2 seed + 3 new), `pixi run
  test-reduction` green, `pixi run ruff check` / pre-commit clean.

## Acceptance criteria

- All launcher tests green including the three new ones; reduction suite
  green (its runtime profile unchanged — no new per-test timeouts there).
- Ruff clean with the new per-file-ignore; pre-commit clean; `pixi.lock`
  untouched (`version: 6`).
- Diff touches exactly `launcher/tests/conftest.py`,
  `launcher/tests/test_harness.py`, `pyproject.toml`.
- Draft PR body cites PR #15's advisory findings as the origin and states
  the deploy consequence per charter §7.

## Revision history

### v2 — 2026-08-19 (after v1 rejection; todo.md @ `7497b28`)

Tests green; rejection entirely from the gate, and the Analyst
**upholds the blocking departure**: measured probes (qtpy 2.4.3 →
PyQt5 5.15.11) showed F1 only partially closed (the `setPath` redirect
covers `IniFormat` while teardown restores `defaultFormat` to
`NativeFormat` — a real-config write was reproduced *against the new
fixture*; v1's matrix row "setPath applies process-wide once set" is
false as implemented and is superseded), F2 not closed for any
production call site (`'exec_' not in QMessageBox.__dict__` — the patch
shadows a class whose instances are never exec'd in `launcher/`, while
`QDialog().exec_()` at `roi_selector.py:230`/`:2038` — **T1's own
sites** — blocks), F3 closed for the inner loop but the collection hook
is session-global (adds `timeout(120)` to the reduction suite in any
combined invocation; with the thread method a firing timeout is
`os._exit` mid-suite), the teardown can skip its own restores (drain
precedes them, unguarded) and the drain never dispatches
`DeferredDelete`, and **all three self-tests are defective** (the
subprocess timeout test never loads the repo ini — passes with both F3
changes deleted; the settings test is order-dependent; the exec test
guards a dead surface). Same defect shape as S3's B1: stated
justifications contradicted by measured ordering. v1's additive-only
"no autouse" line is consciously revised (see fixes). Also recorded,
out of scope: `launcher/` configures 8 `QMessageBox` instances it never
shows — a pre-existing error-dialogs-never-appear bug, parked for the
campaign backlog.

## v2 fixes (the todo's order; each self-test must be able to fail)

1. **Modal backstop targets the base class**
   (`launcher/tests/conftest.py`): patch
   `QtWidgets.QDialog.exec_`/`exec`/`open` (with `hasattr` guards —
   distinct slots in PyQt5), **returning `QtWidgets.QDialog.Accepted`**
   — never `QMessageBox.Ok` (1024): every production comparison is
   `== 1` / `== QDialog.Accepted` / `!= QDialog.Accepted`, so a 1024
   return silently turns accept paths into cancel paths the moment the
   base-class patch lands. Keep the four `QMessageBox` statics.
   `monkeypatch` handles the inherited-attribute case cleanly
   (`notset` → `delattr`). Make `no_qfiledialog` **`autouse=True`**
   (deviation from v1's no-autouse line, directed by the gate: 26
   uncovered sites and nothing opts in; a test wanting a real path
   overrides locally). Fix the shared-list nit: return a fresh list per
   call for `getOpenFileNames`.
2. **Isolation becomes process-wide** — at conftest **import** scope
   (before any collection-time construction):
   `QSettings.setDefaultFormat(IniFormat)` and `QSettings.setPath` for
   **both** `IniFormat` and `NativeFormat` (`UserScope`) into a
   session-scoped scratch root; per-test `tmp_path` refinement stays in
   the fixture. Teardown restores **org/app/domain only** — never
   `defaultFormat` (setPath has no undo; the permanent half is the
   harmless half, and restoring the format is what re-opened the
   window).
3. **Timeout hook scoped and polite**: in
   `pytest_collection_modifyitems`, add the marker only when
   `item.path.is_relative_to(Path(__file__).parent)` AND
   `item.config.getoption("timeout", None) is None` (an explicit
   `--timeout` — the documented RED technique — must win).
4. **Teardown that cannot skip itself**: `try/finally`; identity
   restores first inside `finally`; then the drain with per-widget
   `except RuntimeError` guards, and
   `sendPostedEvents(None, QEvent.DeferredDelete)` after
   `processEvents()` (measured: without it nothing is ever deleted).
5. **Self-tests made falsifiable**:
   - timeout: run the hanging file in a `tmp_path` tree that contains a
     **copy of the shipped conftest** and a minimal ini carrying
     `timeout_method = "thread"`, pass **no** `--timeout` on the CLI;
     assert the `timeout: 120.0s`/`method: thread` header, nonzero rc,
     and the Timeout banner. (The copied conftest's own path filter
     then applies to the copied tree — this test exercises fix 3
     positively; deleting either F3 half turns it red.)
   - settings: construct one `QSettings()` at `test_harness.py`
     **module import** (deterministically poisons the cached root
     before any fixture) and keep the `fileName().startswith(tmp_path)`
     assertion — order-independent redness against the v1 defect.
   - exec: retarget at `QDialog().exec_()` under the fixture, assert it
     returns `QDialog.Accepted` immediately — the surface with the four
     production sites, T1's included.
6. Tail (directed): convert `test_harness.py`'s remaining
   `usefixtures`-mark tests to fixture-argument form (the `ARG001`
   ignore blesses it) and state the one convention in the PR body.

**v2 acceptance additions**: transcript of a combined-session probe
`pixi run python -m pytest tests launcher/tests --collect-only -q`
plus an assertion (grep) that no `tests/` item gained a timeout marker
(the B3 discrimination check); `pixi run test-reduction` green and
`test-launcher` green as before.
