# Plan: launcher-test-harness (S0)

**Campaign:** `exp-settings-roi` · base `exp` @ `dccd093` · charter §4 slug 1 (P-2)
**Retry attempt:** 1

Review domains: test-reviewer (advisory)

## Symptom

`exp` has **no launcher test harness**: no `launcher/tests/`, no
`test-launcher` pixi task, no `pytest-timeout`, no modal-dialog
neutralization. Every GUI-touching slug in this campaign (the three
ports, T2, T3, T1-A1) needs one to run red-green; without it, a single
`QMessageBox.exec_()` under offscreen Qt hangs pytest forever with zero
stdout (the PoC's 10-hour orphan, Developer-Retrospective §B).

## Verified state (against `agentic/exp` @ `dccd093`)

- `launcher/` exists (`launcher/new_launcher.py`, `launcher/apps/*.py`,
  incl. `roi_selector.py`); **`launcher/tests/` absent**.
- Qt binding is **qtpy** (`launcher/new_launcher.py:5-6`) — the PoC
  conftest (also qtpy) ports without binding changes.
- `pyproject.toml`: `[tool.pixi.feature.developer.dependencies]` has
  `pytest`/`pytest-cov` but **no `pytest-timeout`**; `[tool.pixi.tasks]`
  has `test-reduction` (line ~180) with **no `depends-on` chain** and no
  `test-launcher` task.
- Seed source verified present:
  `agentic/feature/cd-dialog-resize:launcher/tests/conftest.py`
  (`ebbd689`) — offscreen env + `isolated_qapp` fixture (isolated
  org/app QSettings + `XDG_CONFIG_HOME` redirect). It lacks
  `no_qmessagebox`; this plan adds it.

## Files to change (all on `feature/launcher-test-harness` from `exp`)

1. `launcher/tests/__init__.py` — new, empty (module namespace keeps
   collection names distinct from the top-level `tests/`).
2. `launcher/tests/conftest.py` — new; port the PoC conftest verbatim
   (offscreen env set **before** any qtpy import; `isolated_qapp`), then
   add:

   ```python
   @pytest.fixture
   def no_qmessagebox(monkeypatch):
       """Neutralize modal QMessageBox calls that hang under offscreen Qt."""
       from qtpy import QtWidgets

       for name in ("warning", "information", "critical", "question"):
           monkeypatch.setattr(
               QtWidgets.QMessageBox, name, staticmethod(lambda *a, **k: None)
           )
   ```

3. `launcher/tests/test_harness.py` — the RED-first seed, **verbatim**:

   ```python
   # launcher/tests/test_harness.py
   from qtpy import QtCore, QtWidgets


   def test_no_qmessagebox_fixture_neutralizes_modals(isolated_qapp, no_qmessagebox):
       # Without the fixture this call blocks forever under offscreen Qt
       # (the 10-hour-orphan class); with it, it returns immediately.
       assert QtWidgets.QMessageBox.warning(None, "t", "must not block") is None


   def test_isolated_qsettings_roundtrip(isolated_qapp):
       settings = QtCore.QSettings()
       settings.setValue("harness/probe", "x")
       settings.sync()
       assert settings.value("harness/probe") == "x"
       assert "test-org" in QtCore.QCoreApplication.organizationName()
   ```

   RED = both tests fail/hang before conftest exists (run first without
   the fixtures to demonstrate; the modal test must be observed to hang
   and be killed by `--timeout`, proving the plugin gate). GREEN = both
   pass with conftest in place.

4. `pyproject.toml`:
   - `[tool.pixi.feature.developer.dependencies]` +
     `pytest-timeout = ">=2.4.0,<3"` (PoC-proven pin).
   - `[tool.pixi.tasks]` +
     `test-launcher = { cmd = "python -m pytest -vv --timeout=120 launcher/tests/", description = "Run launcher UI tests (headless Qt)" }`
   - `test-reduction` gains `depends-on = ["test-launcher"]` (PoC-proven
     chain; note for readers: the launcher banner printing first is
     chain output, not a failure — Integrator-Retrospective §B-4.2).
5. `pixi.lock` — regenerated (dependency added); stage it with the
   pyproject commit or the `pixi-lock-check` hook bounces.

Do **not** port `todo.md`/`pixi.lock` hunks or any versioningit hunk
from the PoC branch (charter §3 strip list); the P-1 glob is already at
source on `exp`.

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Modal dialog blocks a test (common) | `--timeout=120` kills it loudly | `no_qmessagebox` fixture (prevention) + timeout (backstop) |
| Test writes the user's real launcher QSettings (edge) | roundtrip test asserts isolated org name | `isolated_qapp` org/app + `XDG_CONFIG_HOME` redirect |
| Name collision with top-level `tests/` collection (edge) | pytest collection error | `__init__.py` + unique module names (`test_harness.py`) |
| `pytest-timeout` missing at runtime (edge) | `--timeout` arg-parse error, exit 4 | dev-dependency pin; initialization.md §11 step 3 is the standing probe |
| `test-reduction` chain masks launcher failure origin (edge) | task banner shows which stage ran | plan note + §B-4.2 citation; chain failing fast is intended |
| Offscreen platform not set before Qt import (pathological) | X-server error on headless host | conftest sets `QT_QPA_PLATFORM` before any qtpy import, PoC-proven |

## Acceptance criteria

- `pixi run test-launcher` green on the feature branch; both seed tests
  pass; the modal test demonstrably hangs-then-times-out when the
  fixture is removed (RED evidence in the commit body).
- `pixi run test-reduction` still green (281 tests) and now runs the
  launcher suite first via `depends-on`.
- `pixi run test-reduction -- --collect-only --timeout=1 -k test_does_not_exist`
  exits clean (initialization.md §11 step 3 form).
- Pre-commit clean; `pixi.lock` staged with the dependency change.

## Downstream note (Analyst → human, recorded for the record)

The three port slugs and T2/T3/T1-A1 stage **after** this slug's draft
PR **merges** into `exp` (their launcher tests need the harness at the
tip they branch from). Triage branches for S1–S3 will be pushed when
`exp` contains this harness — staged triage per the charter §4 DAG, not
a stall.
