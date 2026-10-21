# Plan: `launcher-suite-crash-isolation` — one native crash or hang in the launcher suite fails one test or one task, never the whole gate; the crashing test and signal are always recorded

**Campaign:** `exp-review-fixes` · **Leaf:** `launcher-suite-crash-isolation` (K8; refs `triage/launcher-suite-crash-isolation`, `feature/launcher-suite-crash-isolation`,
`qa/launcher-suite-crash-isolation`) · **Status:** **DISPATCHED — v1 (attempt 1 of N = 3)**, 2026-10-21 (A-170) on the human's addressed word `[human, 2026-10-21 (to the Analyst): "you may dispatch K8, K9, K14 and K15. Let us hold K16 until after L4 lands to upstream:exp-next - thank you!"]`; staged at A-168 on the human's relayed words `[human, 2026-10-21 (to the Advisor, V1-69): "On {K8, K9, K14},
prepare them for dispatch."]` — input under `b059f14`; **not dispatched**: "dispatch K8" dispatches it ·
**Base:** `feature/landing-l4-model-move` @ **`f8dbf86`** (the stack tip: L3/L4 changed `launcher/tests/conftest.py` and `test_harness.py`, and L4 moved the Qt-free model tests
and the real-data battery under `launcher/`; cutting below L4 would conflict at every forward merge — V1-69) — its own branch from `f8dbf86`, stacked on #53; or, on the human's
word, after the landing on `exp-next` · **PR:** the fork, `--base feature/landing-l4-model-move`, draft · **Reviews:** design, test (block); numerical-diagnostics n/a ·
**Gate:** G with the new task layout (every task EXIT 0); the isolation must-fail (§6 T3); N ≥ 20 fresh-process runs under a controlled load with 0 session aborts (§6 T5).

Campaign: exp-review-fixes

## Declared scope

**Phase 0 — measure before designing** (the pattern `setup/patterns/native-crash-and-hang-diagnosis.md`): the one test that has failed three times under concurrent load,
`launcher/tests/test_harness.py::test_teardown_survives_an_open_menu` (I-103 a segfault in `isolated_qapp` after it, I-126 a 120 s timeout of its inner pytest, A-165's count),
run alone and in the suite with `PYTHONFAULTHANDLER=1` and `faulthandler.dump_traceback_later`, under the same load shape (a second suite running), until the crash or hang
reproduces or N ≥ 20 says it does not; the stale-sip-wrapper hypothesis of I-104 (`labelForField` returning a `QWidget`) confirmed or refuted with `sip.isdeleted` checks around the
harness teardown. The measurement decides which isolation below is built; a Phase-0 finding that names a product defect becomes its own slug.
**Phase 1 — isolation without new dependencies** (the lock stays v6; `pytest-xdist`/`pytest-forked` are not in the lock and a new dependency would re-lock): the launcher suite split
into pixi tasks by process risk — `test-launcher-model` (the Qt-free model tests under `launcher/tests/`: no `QApplication`), `test-launcher-data` (the Mantid-heavy real-data tests,
`test_roi_estimate.py`'s `LoadEventNexus` battery, in their own process), `test-launcher-ui` (the Qt session) — each its own `pytest` process with `--timeout` and
`-p faulthandler`; `test-reduction` no longer `depends-on` one launcher session but on the three; a crash or hang in one task fails that task and the others still report.
**Detection complete:** `PYTHONFAULTHANDLER=1` in every task, so a native crash prints the failing test and the signal to the task's log; the gate's record names them.
**Out:** the gate-policy half (rerun on a quiet machine, record both runs — the Administrator's, kit); any product fix the measurement reveals (its own slug); CI workflow changes
(`.github/`, D-2); the deploy.

## 1. Request and symptom

`todo-launcher-suite-intermittent-native-crash-under-load.md` (I-103): at L4's first gate `test-reduction` died in the launcher suite — `test_harness.py::test_teardown_survives_an_open_menu`
FAILED, then a segmentation fault in `isolated_qapp` (`conftest.py:93`, `QApplication([])`); separately a moved test segfaulted inside Mantid's `LoadEventNexus`
(`test_roi_estimate.py:701`, exit 139) in 1 of 3 runs. I-104 measured 0 segfaults in 40 fresh-process runs under load (rate < ~7.5 %/run) and one non-crash wrong-type failure (a
stale sip wrapper, unproven). I-126: the same test timed out (120 s) at L4′'s gate under concurrent load; the files identical to the gated L4; 3/3 green isolated. Three failures of one
test under load; one native crash in the shared session ends the whole gate because `test-reduction` depends on `test-launcher`.

## 2. Verified facts at `f8dbf86` (2026-10-21 14:3xZ; this clone)

| # | Fact | Evidence |
|---|---|---|
| V1 | `pyproject.toml:181-182`: `test-reduction` (`cd tests/ && python -m pytest -vv --cov=…`) `depends-on = ["test-launcher"]`; `test-launcher` = `python -m pytest -vv --timeout=120 --timeout-method=thread launcher/tests/` — one process for the whole launcher suite (1528 tests at L4′) | `git show f8dbf86:pyproject.toml` |
| V2 | `pytest-timeout` 2.4.0 is in the lock; `pytest-xdist` and `pytest-forked` are not | `pixi.lock` |
| V3 | `launcher/tests/conftest.py:79` `isolated_qapp(tmp_path, monkeypatch)` — a per-test `QApplication` with a per-test QSettings root; teardown restores org/app/domain names, deliberately not `defaultFormat` | `git show f8dbf86:launcher/tests/conftest.py` |
| V4 | At `f8dbf86` the Qt-free model lives in `launcher/model/{settings_document,field_spec,roi_estimate}.py`, the real-data battery in `launcher/tests/test_roi_estimate.py` with `scripts/test/roi_estimate_mutations.py` (L4, D-7/D-10/D-11) | `git ls-tree` |
| V5 | The three failures: I-103 (segfault after the test, `conftest.py:93`), I-126 (`TimeoutExpired` of the inner pytest at 120 s, concurrent with a harness run, no segfault), the design reviewer's `LoadEventNexus` exit 139 (1 of 3); 0 of 40 under I-104's load; 3/3 isolated green each time | the todo; I-104; I-126 |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B0 | **Phase 0 first.** The measurement (scope above) is a deliverable: a `plans/launcher-suite-crash-isolation-measurement.md` on the ledger with the runs, the load, faulthandler output, and the sip verdict. If a reproducible product defect appears, STOP and file it (its own slug); Phase 1 proceeds regardless, since the blast radius is the slug's problem whatever the cause. |
| B1 | **Three tasks by process risk** in `pyproject.toml` (`[tool.pixi.tasks]`): `test-launcher-model` — the Qt-free tests (`launcher/tests/test_settings_document.py`, `test_field_spec.py`, the Qt-free part of `test_roi_estimate.py`) with `-p no:…` nothing special, no `QApplication`; `test-launcher-data` — the real-data tests (markers: `@pytest.mark.realdata` on the `LoadEventNexus` battery, selected with `-m realdata`); `test-launcher-ui` — the rest (`-m "not realdata"` on the Qt modules); `test-launcher` becomes an aggregate `depends-on` the three; `test-reduction` `depends-on` the three. Each task: `--timeout=120 --timeout-method=thread -p faulthandler`, `PYTHONFAULTHANDLER=1` in the task's `env`. |
| B2 | **A crash fails one task.** pixi runs dependent tasks in order and stops at the first failure — so the ordering puts `test-launcher-ui` (the risky session) last among the three, and the task runner's exit reports which task died with the faulthandler trace in its log. |
| B3 | **The record is complete:** every task's log carries the test id and the signal on a native crash (faulthandler), and the timeout's traceback on a hang (pytest-timeout's thread method). |
| B4 | **Test ids conserved:** the union of the three tasks' collected ids equals `test-launcher`'s today (1528 at `f8dbf86`); no test runs twice; no test is lost (a collection census as L4's). |
| B5 | **Behaviour of the tests unchanged:** this slug moves no test and changes no assertion; markers and task definitions only. |

## 4. Files to change

| File | Change |
|---|---|
| `pyproject.toml` | the three tasks, the aggregate, `test-reduction`'s `depends-on`; the `realdata` marker registered under `[tool.pytest.ini_options] markers` (B1) — **note D-116:** a `pyproject.toml` edit outside the pixi sections may still stale the lock (the manifest hash); the Developer measures `pixi install --locked` first and, if it stales, re-locks with `pixi lock` under the lock-format guard (a legitimate re-lock, not a hand stamp) — the lock stays v6 |
| `launcher/tests/test_roi_estimate.py` (markers only) | `@pytest.mark.realdata` on the battery's tests (B1) |
| `launcher/tests/conftest.py` | `faulthandler` registration if `-p faulthandler` is not enough under pytest's capture (B3) |
| ledger `plans/launcher-suite-crash-isolation-measurement.md` | Phase 0's record (B0) |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: a green run | three tasks green, the aggregate green, `test-reduction` runs after them | T1 |
| 2 | common: a segfault in the Qt session | `test-launcher-ui` fails with the test id and signal in its log; the other two tasks' results stand | T3 |
| 3 | common: a `LoadEventNexus` crash | `test-launcher-data` fails alone | T3 |
| 4 | edge: a hang | pytest-timeout's thread method dumps the stack after 120 s; the task fails, not the gate's shell | T4 |
| 5 | edge: a test collected by two tasks, or by none | the census (B4) reds | T2 |
| 6 | pathological: the `pyproject.toml` edit stales the lock | measured first; a proper re-lock under the format guard, or the markers moved to a `pytest.ini`-free form (`-k`/paths) if the human prefers no lock change | T1, D-83 |
| 7 | pathological: the measurement reproduces a product defect | STOP, its own slug; the isolation still lands | B0 |
| 8 | out of scope: the gate policy (rerun on a quiet machine) | the Administrator's | — |

## 6. Red-Green seed

- **T1** `pixi run test-launcher` (aggregate) and `pixi run test-reduction` EXIT 0; each sub-task EXIT 0; counts reported per task.
- **T2** Census: the sorted union of `--collect-only -q` ids of the three tasks equals `test-launcher`'s at `f8dbf86` (1528), with no duplicates.
- **T3** Must-fail: a throwaway test that calls `os.kill(os.getpid(), signal.SIGSEGV)` (or `ctypes` null deref) added to the `data` group → only `test-launcher-data` fails, with the faulthandler trace naming the test; the other tasks report their own results (not pushed; recorded in the body).
- **T4** Must-fail: a throwaway test that sleeps 200 s in the `ui` group → the task fails on the timeout with the dumped stack; the other tasks unaffected.
- **T5** N ≥ 20 fresh-process runs of the aggregate under a controlled load (a second suite running): 0 session aborts; any task failure recorded with its test id and signal.
- **T6** Phase 0's record exists on the ledger with the runs and the sip verdict.

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| `test-reduction` still depends on the single session | T3 (the whole gate dies) |
| a real-data test left in the ui task | T2 (the census) or T3 |
| faulthandler off | T3 (no test id in the log) |
| the timeout dropped | T4 |

## 8. Acceptance criteria

T1–T6; the files of §4 only; bodies with the trailer and no campaign identifiers; the Integrator's draft PR `--base feature/landing-l4-model-move`; the gate's own run with the new tasks.

## 9. Learnings relied on

I-104 (the 0/40 measurement, the sip hypothesis), I-126 (the timeout shape and the "rerun does not pass alone" diagnosis), `plans/launcher-test-teardown-learning.md` §2 (hash-ordered
teardown crashes, measured over fresh processes), `setup/patterns/native-crash-and-hang-diagnosis.md`, D-116 (the lock), L4's census method (A-139/I-103).

## 10. Decisions

- **D-1 — no new dependency:** isolation by tasks and processes, not `pytest-forked`/`xdist` (a re-lock and a facility pixi constraint). Reversible if the human wants per-test forking: then the dependency is added with a proper re-lock.
- **D-2 — base the stack tip** (or `exp-next` after the landing, the human's word); never below L4.
- **D-3 — measure first:** Phase 0 is a deliverable and may change Phase 1's grouping; it may also name a product defect, which is not this slug's to fix.
- **D-4 — the gate-policy half stays the Administrator's.**

## Revision history

- **v1 — 2026-10-21 (A-168):** staged on the human's relayed words (V1-69); not dispatched. Sealed against the stack tip `f8dbf86`.
