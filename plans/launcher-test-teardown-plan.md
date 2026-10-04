# Plan: `launcher-test-teardown` — the launcher tests' teardown deletes only the windows nothing else owns

**Campaign:** `exp-review-fixes` · **Leaf:** `launcher-test-teardown` (refs `triage/launcher-test-teardown`,
`feature/launcher-test-teardown`, `qa/launcher-test-teardown`) · **Status:** READY (v1) — re-sealed 2026-10-04 against `exp-review` @ `b86237b` (PR #36 merged; `launcher/tests/conftest.py` and `test_harness.py` are byte-identical to `e313f38`; the probe re-run at the tip: 2 of 4 runs abort) ·
**Base:** `agentic/exp-review` @ `b86237b` · **PR target:** `exp-review` on the fork, **draft** ·
**Depends on:** `editor-combos` merged (order only — the files are disjoint); `editor-defaults-and-theta` now waits for
**this** slug · **Review domains:** test (block); design (advise) · **Kind:** test infrastructure — not reduction-path,
not operator-facing (no deployment-shaped run; the gate is the acceptance) ·
**Seed:** `todo-launcher-test-teardown-frees-owned-popups.md` (Developer, found while building `editor-combos` v2) ·
**Authority:** `[human, 2026-10-04: "add fix/launcher-test-teardown to the charter and plan it, before editor-defaults-and-theta."]`

Canonical copy: ledger `plans/launcher-test-teardown-plan.md`; the copy on `triage/launcher-test-teardown` is byte-identical
at dispatch.

## Declared scope

**Files in:** `launcher/tests/conftest.py` (the `isolated_qapp` teardown only), `launcher/tests/test_harness.py`.

**Behaviours in** (H1–H4, §3). **Explicitly OUT:** every production module; every other fixture (`no_qmessagebox`,
`no_qfiledialog`, the import-scope `QSettings` redirect, the timeout hook); the completer the editor uses
(`_CandidatesDelegate` stays inline — whether it may open a pop-up later is `editor-combos`' or a successor's call);
`tests/conftest.py` (the reduction suite has no Qt teardown).

## 1. Request and symptom

A test that opens a `QCompleter` pop-up — or any other top-level window its opener owns — aborts the whole launcher
suite at teardown, intermittently, with the traceback pointing nowhere near the fixture: `Fatal Python error: Aborted`
in `QCompleter::~QCompleter()`. `editor-combos` v2 met it in 5 of 5 runs and worked around it (an inline completer).
Every later editor slug runs its view tests under this fixture.

## 2. Verified facts at `b86237b` (uvdl3 clone 1, 2026-10-04; first measured at `e313f38` — both files unchanged between the two tips)

| # | Fact | Command → observation |
|---|---|---|
| F1 | The teardown deletes every top-level widget. | `launcher/tests/conftest.py:66-77` (the loop at `:66`): `for widget in QtWidgets.QApplication.topLevelWidgets(): widget.close(); widget.deleteLater()`, then `app.processEvents()` and `app.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)`. |
| F2 | A completer's pop-up is a parentless top-level window of type `Popup`, owned by the completer. | Offscreen probe, Qt 5.15.15: after `completer.complete()`, `topLevelWidgets()` → `[('QListView', windowType 9, parent None), ('QWidget', 1, parent None)]`; `Qt.Popup == 9`, `Qt.ToolTip == 13`. Qt's `QCompleter::setPopup` reparents the view to `nullptr` and deletes it in the destructor (the todo's reading of `qcompleter.cpp`; the abort site below confirms it). |
| F3 | **Reproduced:** the fixture's drain double-frees it, intermittently. | `scratchpad probe_teardown.py all` (a `QLineEdit` + `QCompleter`, `complete()`, then F1's exact sequence): **4 of 8 runs exit 134 (SIGABRT)**, earlier 1 of 3. The Developer's `gdb` backtrace places it in `QCompleter::~QCompleter()` under `sendPostedEvents(DeferredDelete)` (`conftest.py:76`). |
| F4 | **Skipping pop-up windows removes it.** | Same probe, `skip-popups` (leave a top-level whose `windowType() & Qt.Popup == Qt.Popup` alone): **0 of 8 aborts**, earlier 0 of 3. The owner deletes the pop-up when it is deleted itself (the completer is a child of the edit, the edit of the window). |
| F5 | The harness already has subprocess-driven self-tests to pattern on. | `launcher/tests/test_harness.py`: `test_timeout_backstop_fires` writes a test file and runs `pytest` in a subprocess; the file's other tests pin `isolated_qapp`, `no_qmessagebox`, `no_qfiledialog`, the collection hook. |
| F6 | Not reduction-path, no operator surface. | Only `launcher/tests/` changes; nothing under `src/` or `launcher/apps/`. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| H1 | **The teardown deletes only windows nothing else owns.** A top-level widget is closed and `deleteLater`-ed only if it has no parent **and** its window type is one a test created as a window (`Qt.Window`, `Qt.Dialog`, `Qt.Tool`, `Qt.Sheet`, `Qt.Drawer`). A `Qt.Popup`, `Qt.ToolTip` or `Qt.SplashScreen` top-level, or any widget with a parent, is left to its owner. |
| H2 | **Everything else the drain did, it still does**: identity restored first; the remaining windows closed and deleted; `processEvents` and the `DeferredDelete` flush kept; a `RuntimeError` on an already-destroyed widget still swallowed. |
| H3 | **Opening an owned pop-up in a test is safe.** A test under `isolated_qapp` that opens a `QCompleter` pop-up (and one that opens a `QMenu`) survives teardown every time — proven in subprocesses, because the defect is intermittent in-process. |
| H4 | **The rule is stated where it bites.** The fixture's comment names the owned-pop-up case and the probe count, so the next reader does not "simplify" it back. |

**Types and states the teardown acts on** (every top-level widget at teardown): parent `None` / parent set × window
type `Window`, `Dialog`, `Tool`, `Sheet`, `Drawer` (delete) / `Popup`, `ToolTip`, `SplashScreen`, `SubWindow` (leave) ×
already destroyed on the C++ side (swallow) × hidden or visible (both handled). A pop-up whose owner has already been
deleted in the same drain is gone by the time the flush runs — not touched twice.

## 4. Files to change

| File | Change |
|---|---|
| `launcher/tests/conftest.py` | the ownership rule in the `isolated_qapp` teardown (H1, H4) |
| `launcher/tests/test_harness.py` | the subprocess guard (H3) and a pin on the rule's table (H1) |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | a test opens a completer pop-up and returns | teardown survives; the next test is isolated as before |
| common | a test opens a `QMenu` (`popup()`) and returns | same |
| common | a test leaves a plain window and a dialog open | both closed and deleted, as today |
| edge | a pop-up still visible at teardown | left to its owner; the owner is deleted with its window |
| edge | a widget already destroyed on the C++ side | `RuntimeError` swallowed, as today |
| edge | the shared-`QApplication` case the fixture's comment describes | the drain still frees the test's windows |
| pathological | a parentless `Qt.Popup` nothing owns (a test created one and forgot it) | left alone; it dies with the process — a leak, not an abort; the pin names this trade |
| pathological | a `Qt.Tool` window owned through a raw pointer by some object | deleted (it is in the delete set); if a real case appears it is a `fix/` with its own evidence |

## 6. Red-Green TDD seed

| # | Test (names are suggestions) | RED at `e313f38` |
|---|---|---|
| T1 | `test_teardown_survives_an_open_completer_popup` — writes a test module that, under `isolated_qapp`, opens a `QCompleter` pop-up and returns; runs `pytest` on it in a subprocess **N = 12 times**; asserts every exit is 0 and no `Aborted`/`134` (the F5 pattern) | several of the 12 exit 134 (F3: ~½) |
| T2 | the same with a `QMenu.popup()` | measure at RED; if green at the base, keep as a pin and say so |
| T3 | a plain `QWidget` and a `QDialog` left open are gone after teardown (`topLevelWidgets()` filtered to those types is empty in the next test) | passes — the H2 pin |
| T4 | the rule's table: for each window type, a parentless widget of that type is deleted or kept as H1 says (drive the teardown helper directly if the Developer extracts one — recommended, so the rule is a function, not a loop body) | helper absent |

The suite's own 120 s per-test timeout (`conftest.py`) bounds T1/T2; each subprocess run is ~1–2 s.

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| ownership rule removed (every top-level deleted again) | T1 (expect ≥ 1 abort in 12; record the count — a 0 would be a `(½)^12` event, so a green here means re-run, not pass) |
| `Popup` kept but `ToolTip` deleted (type set wrong by one) | T4 |
| parent check removed (parented top-levels deleted) | T4 |
| the delete set emptied (nothing deleted) | T3 |
| the `DeferredDelete` flush removed | T3 |

Frame: one helper (if extracted) with one call site; the subprocess runner in `test_harness.py` reused from
`test_timeout_backstop_fires` or factored — one row per call site if factored.

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root (the launcher stage runs under the new teardown —
   itself the broadest check).
2. §6 RED→GREEN with the subprocess counts quoted (RED: aborts of 12; GREEN: 0 of 12, twice); §7 recorded per row.
3. Prose claims verified: the fixture comment's statement about pop-up ownership cites the probe and its counts.
4. No change under `src/` or `launcher/apps/`; no ledger-shaped path.
5. PR body: test infrastructure only; no deploy consequence; the Developer's `gdb` evidence and the probe counts quoted.

## 9. Learnings relied on

- CPKT `setup/patterns/ui-aspects.md` § "Dispose dialogs with `deleteLater()`, never `QWidget.destroy()`": "it
  crashes only on … teardown"; "Definitive diagnosis: a native (gdb) backtrace" — the Developer's method here.
- `launcher/tests/conftest.py` (base): "On this environment the fixture drops its reference to the QApplication, so
  the common case is a fresh one per test" — why the drain is defense-in-depth, and why it must not kill the process.
- `test_harness.py` `test_timeout_backstop_fires`: a harness property proven in a subprocess, not in-process.
- This campaign: a defect that is intermittent in-process needs a deterministic RED — repeat in subprocesses and count.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | N = 12 subprocess runs. | A ½-per-run abort rate makes a false GREEN under the mutation a `(½)^12 ≈ 0.02 %` event; the plan says re-run on an unexpected green. |
| A2 | `Qt.Tool` windows are in the delete set. | Yes — the launcher's own tool windows are test-created. |
| A3 | The slug runs between `editor-combos` and `editor-defaults-and-theta`, as the human placed it. | Yes; files disjoint from both. |

## Revision history

v1 — authored 2026-10-04 against `e313f38` (staged); re-sealed and dispatched the same day against `b86237b` after PR #36 merged (the two files unchanged; the abort reproduced again at the tip, 2 of 4).
