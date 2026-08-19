# Plan: port-overplot-axes-refresh (S2)

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` · charter §3 PRs
#9 + #10 ("port, adapted — one overplot series") · seeds
`agentic/feature/overplot-axes` @ `300d040`,
`agentic/feature/overplot-refresh` @ `7bc34b2`
**Retry attempt:** 3 (final — N=3; the next rejection escalates)

Review domains: ui-aspects-reviewer (**blocking** — upgraded at the v1
rejection: charter §5 ties blocking to bug-fix phases, and v1 proved this
slug is one; the v1 "advisory" premise — reviewed PoC code, tests catch
adaptation slips — was falsified by four verified functional findings on a
green suite), test-reviewer (advisory).

## Symptom

Two related gaps in `launcher/apps/overplot.py` on `exp`:

1. **Axes lie for non-reflectivity data** (PR #9): `plot_selected()`
   hardcodes `ax.set_xlabel('Q')` / `ax.set_ylabel('R' …)` (lines 355–356;
   `'x'`/`'y'` in the popout path, 394–395). A direct-beam `.txt`
   (λ/intensity) plots under Q/R labels, and `R*Q^4` stays selectable for
   data where it is meaningless.
2. **Folder rescans discard selection** (PR #10): re-populating via
   `folder_changed()` → `populate_file_list()` clears every check-state, and
   there is no refresh affordance at all — exactly the gap the PoC Refresh
   button closes (rescan preserving checks, replot, report dropped files).

Both PRs live on the retired `ui_plan` lineage and cannot merge (charter
§3); port both as one series — they edit the same file and #10's refresh
replots through #9's mode-resolution path.

## Verified state (against `agentic/exp` @ `a4ae8b8`, 2026-08-18)

- **Widget adaptation confirmed**: `exp` has `self.folder_edit` (QLineEdit,
  line 71; `editingFinished` → `folder_changed`, line 162). The PoC code and
  tests reference `folder_label` (QLabel) throughout — **every occurrence
  adapts to `folder_edit`**; `exp` reads the folder as
  `self.folder_edit.text().strip()` (line 314) — keep the `.strip()` idiom
  where exp already has it.
- `read_settings` (167) already reads `overplot_folder`, `overplot_xscale`,
  **and `overplot_ytransform`** (line 176); `save_settings` (180) writes only
  folder + xscale. So #9's settings delta here is: read+clamp
  `overplot_mode`, save `overplot_mode` — and note `overplot_ytransform`'s
  *save* half belongs to S3 (PR #11), not this slug.
- Landing zones clean: no `classify_file`, `_axis_labels`, `plot_mode_combo`,
  `refresh_btn`, `_scan_folder` on `exp`. `populate_file_list(folder)` (191)
  and `apply_filter(text)` (209) signatures match the PoC's.
- Post-lint file (PR #14): single-quote style at the label lines — **semantic
  re-apply, not raw hunks**.
- PR diffs: `git fetch agentic refs/heads/feature/overplot-axes
  refs/heads/feature/overplot-refresh`; each PR's own change is
  `git diff 3b599c7..agentic/feature/<name> -- launcher/` (shared
  merge-base `3b599c7` with `ui_plan`).

## Files to change (on `feature/port-overplot-axes-refresh` from `agentic/exp`)

Implement as two commits in PR order (axes, then refresh) so each maps to
its seed PR; they overlap only additively in `__init__`.

**Commit A — axes/classification (PR #9 content, adapted):**

1. `launcher/apps/overplot.py`:
   - Module level: `REFLECTIVITY_HEADER_MARKER`, `DIRECT_BEAM_HEADER_MARKER`,
     `classify_file(path)`, `_axis_labels(mode, transform)` — pure functions,
     copy verbatim.
   - `__init__`: `self._last_sel_mode = None`; Plot-mode row
     (`plot_mode_combo`: Auto/Reflectivity/Direct Beam) after the folder row;
     connect `currentTextChanged` → `_on_plot_mode_changed`; after
     `read_settings()` call `_on_plot_mode_changed(currentText())`.
   - Methods: `_set_rq4_enabled`, `_on_plot_mode_changed`, `_resolve_modes`
     verbatim from the PR.
   - `plot_selected()`: per-file modes + `sel_mode` resolution, the
     override-mismatch `QMessageBox.warning`, transform forced to `"None"`
     off-reflectivity, `[kind]` label suffix for mixed selections, and both
     label sites become `ax.set_xlabel(xlabel)` / `ax.set_ylabel(ylabel)`
     from `_axis_labels` (embedded + popout paths).
   - `read_settings`/`save_settings`: `overplot_mode` (read with the
     Auto/Reflectivity/Direct-Beam clamp; save).
2. `launcher/tests/data/{db_fixture.txt,refl_fixture.txt}` — the PR's two
   7-line synthetic fixtures, verbatim. (They are *header/classification*
   fixtures for a GUI file-list, not reflectivity measurements — nothing
   here renders as an R(Q) result.)
3. `launcher/tests/test_overplot_axes.py` — the PR's 8 tests, adapted:
   `launcher.apps.overplot` imports, `folder_edit` for `folder_label`,
   `usefixtures("isolated_qapp", "no_qmessagebox")` marks on the
   widget-driving tests (`classify_*` ones are pure-function tests and need
   no fixtures). `no_qmessagebox` is mandatory here: `plot_selected` can
   raise `QMessageBox.warning` (load errors, override mismatch) — unfixed,
   that is the 10-hour-orphan class under offscreen Qt.

**Commit B — refresh (PR #10 content, adapted):**

1. `launcher/apps/overplot.py`:
   - `__init__`: Refresh button + `_refresh_tooltip_base` +
     `_update_refresh_tooltip(self._read_last_refresh())` after the Clear
     button; connect to `self.refresh`.
   - `populate_file_list` refactor: extract `_scan_folder(folder)` (sorted
     `.dat`/`.txt`; raises `OSError`), catch `OSError` (not blanket
     `Exception`) for the critical dialog.
   - `_read_last_refresh`, `_update_refresh_tooltip`, `refresh()` verbatim
     modulo `folder_edit`: two-phase (snapshot checks → rescan →
     `apply_filter(self.filter_edit.text())` rebuild → restore checks →
     stamp `overplot_last_refresh` + tooltip → replot if anything still
     checked → `QMessageBox.information` listing dropped files).
2. `launcher/tests/test_overplot_refresh.py` — the PR's 7 tests, adapted as
   above (imports, `folder_edit`, fixture marks). Tests that *capture* a
   specific dialog keep their own `monkeypatch.setattr(QMessageBox, …)` —
   test-local patches override the fixture's neutralization, so capture
   still works; the fixture remains as backstop for the paths the test does
   not patch.

**Strip list:** `todo.md` (both PRs carry the PoC versioningit escalation —
historical), `pixi.lock`, `pyproject.toml` hunks, PoC `conftest.py`/
`__init__.py` (S0's landed versions stand).

**pixi.lock caveat:** identical to S1 — no dependency change in this slug;
restore any hook-side v7 rewrite (`git checkout -- pixi.lock`); never commit
a lock not starting `version: 6`.

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| `folder_label` reference survives the port (common) | AttributeError at collection/run — RED catches | global adapt rule; seal grep before qa |
| Raw hunks over post-lint file (common) | patch reject / ruff | semantic re-apply |
| Modal fires in a test (`plot_selected` warning path) (common) | thread-method timeout at 120 s | `no_qmessagebox` marks + test-local captures |
| Mixed selection mislabeled (edge) | `test_mixed_selection` asserts `x`/`y` labels + disabled R*Q⁴ | ported logic + test |
| Refresh on dead mount (edge) | `test_refresh_unmounted_folder` (captures `critical`) | `_scan_folder` raises `OSError`, caught |
| Refresh drops files silently (edge) | `test_refresh_drops_removed` asserts the info dialog | dropped-set report ported |
| `folder_changed` vs `refresh` interplay (edge) | `test_refresh_preserves_check_state` | refresh path never routes through `folder_changed` |
| Settings key collision with S3 (edge) | S3 owns `overplot_ytransform` *save*; this slug owns `overplot_mode`, `overplot_last_refresh` | disjoint keys, noted in both plans |
| `pixi.lock` v7 staged (edge) | first line ≠ `version: 6` | caveat |

## Red-Green seed

- RED: land both test files + fixtures first (adapted); `pixi run
  test-launcher`: every widget test fails (`AttributeError:
  plot_mode_combo` / `refresh_btn`; `classify_file` ImportError); commit
  enumerates them.
- GREEN A: commit A turns the axes tests green (`test_overplot_refresh.py`
  still red); GREEN B: commit B completes the suite. `pixi run
  test-reduction` green at the tip.

## Acceptance criteria

- `pixi run test-launcher` green: harness 2 + S1's 6 (if S1 merged; else on
  this branch just harness 2) + these 15.
- `pixi run test-reduction` green; pre-commit clean; `pixi.lock` untouched.
- Diff touches exactly `launcher/apps/overplot.py`,
  `launcher/tests/test_overplot_axes.py`,
  `launcher/tests/test_overplot_refresh.py`, `launcher/tests/data/*` (2
  files).
- Draft PR body notes: supersedes PRs #9 + #10 (human closes both per
  charter §3), and calls out the B3 chosen-semantics change (below) as a
  deliberate change to pre-existing `exp` behavior.

## Revision history

### v2 — 2026-08-19 (after v1 rejection; todo.md @ `1c0fc43`)

Tests were green (17 launcher + 107 reduction); the rejection is entirely
from the review gate. The Integrator departed from v1's advisory
declaration and the **Analyst upholds the blocking disposition**: B1/B2
mean the feature fails its stated purpose on every real reflectivity file
in the repo (and B2 puts confidently-wrong λ/I axes on real R(Q) — the
exact trust surface scientists read at face value), B3 reports a stale
plot as refreshed, B4 is a new regression that destroys the user's saved
folder when the app starts before `/SNS` mounts. All four verified in
source by the Integrator AND re-verified by the Analyst against
`a4ae8b8` (`output.py` writes the Q-marker after a 12–19-line preamble;
`save_reduced_data.py` is a second writer with a different marker;
the checked-OR-highlighted semantics predates the port). The green-suite
finding stands too: v1's tests could not discriminate — the named partial
reverts all pass. v2 adds the discrimination tests as mandatory.
Cause class: v1 ported the PoC logic verbatim where the PoC logic itself
was defective on real data formats — "seed PR" does not mean "verified
against facility data". Review-domains line upgraded (ui-aspects →
blocking). Fix directions in "## v2 fixes" below; the v2 source branch is
the EXISTING `feature/port-overplot-axes-refresh` with the Integrator's
todo.md on top (never re-branch from `exp`).

## v2 fixes (B1–B4, in the todo's order) + mandatory discrimination tests

**B1 — classify the real formats** (`launcher/apps/overplot.py`):
replace the fixed 10-line window with a leading-comment-block scan and a
marker *set* covering both facility writers:

```python
REFLECTIVITY_MARKERS = ("q [1/angstrom]", "columns = q, r, dr, dq")
DIRECT_BEAM_HEADER_MARKER = "lambda intensity error"


def classify_file(path):
    """Classify by the leading comment block ('#' lines, capped at 200)."""
    try:
        with open(path) as fh:
            for _ in range(200):
                line = fh.readline()
                if not line or not line.startswith("#"):
                    break
                low = line.lower()
                if any(marker in low for marker in REFLECTIVITY_MARKERS):
                    return "reflectivity"
                if DIRECT_BEAM_HEADER_MARKER in low:
                    return "direct_beam"
    except (OSError, UnicodeDecodeError):
        return "unknown"
    return "unknown"
```

(`output.py:236` writes `# Q [1/Angstrom] R dR dQ [FWHM]` after the
preamble — real files carry it at lines 13–20; `save_reduced_data.py`
`_build_header` writes `columns = Q, R, dR, dQ (sigma)[, L, dL, T, dT]`,
matched by the second marker's prefix. Keep the narrow exception tuple —
a binary file must classify `unknown`, not crash, and blanket `except`
bounces off ruff BLE-discipline in `src/`-style review even though
`launcher/**` ignores BLE001.)

RED-first mandatory test: parametrize `classify_file` over the real
**tracked** corpus — exactly `tests/data/reference_rq.txt`,
`reference_rq_201282.txt`, `reference_rq_avg.txt`,
`reference_rq_avg_overlap.txt`, `reference_short_nobck.txt` →
`"reflectivity"` (markers sit at lines 13–20; all five classify
`unknown` under v1 — red first), plus a 3-line synthetic in the
`save_reduced_data` format, plus the existing fixtures.
*(Correct-and-flag on the todo's file list: the `REFL_*.txt` files it
also cites are **gitignored test-run byproducts** — present only after
a `test-reduction` run, so a glob over them collects zero cases on a
fresh clone/CI. The five tracked files cover the same marker depths;
do not parametrize over untracked paths.)*

**B2 — unknown is a kind** (`_resolve_modes`): the homogeneity test must
not drop `unknown`:

```python
per = [classify_file(p) for p in paths]
kinds = set(per)
if not kinds or kinds == {"unknown"}:
    return per, "unknown"
if len(kinds) == 1:
    return per, next(iter(kinds))
return per, "mixed"
```

Test: one classified-DB file + one headerless file → `sel_mode ==
"mixed"` (v1 returns `"direct_beam"` — red first).

**B4 — never persist an empty folder** (`save_settings`): write
`overplot_folder` only when `self.folder_edit.text().strip()` is
non-empty, and store it stripped (aligns the one unstripped site).
Keep the mode save-on-change. Test: pre-seed `QSettings`
`overplot_folder=/nonexistent/xyz`, construct `Overplot` (isdir fails →
field empty), assert the stored value is unchanged after `__init__`.

**B3 — checkbox is the single "chosen" notion** (robust form, per the
ui-aspects hidden-input trap): set `file_list` selection mode to
`NoSelection`, connect `itemClicked` to toggle the item's `checkState`
*(the `itemClicked` half is **superseded by v3** — it double-toggles
indicator clicks; see the v3 revision entry)*,
and drop `or item.isSelected()` from `plot_selected`. This changes
pre-existing `exp` behavior (highlight-only rows used to plot) —
deliberate, PR-body callout required. `refresh()`'s check-only snapshot
is then coherent by construction. Tests: a row click toggles the check
(drive the `itemClicked` handler); an unchecked row never plots; check
preservation across a sort-order-shifting insert (drop an `0aaa.dat`
into the folder between populate and refresh — kills the index-keyed
revert).

**Remaining mandatory discrimination tests** (each kills a named v1
revert): popout label path (monkeypatch module `plt`, `canvas=None`,
assert `_axis_labels` output reaches `set_xlabel/set_ylabel` — close the
figure in the test); `test_refresh_no_folder` upgraded to capture the
`QMessageBox.warning` call and assert it fired; R*Q⁴ re-enabled after a
real-format reflectivity plot (kills the hardcoded-`False` revert);
refresh via `refresh_btn.click()` picks up a new file (kills the
dropped-connect revert). Strongly recommended, not gating: the
override-mismatch warning test and the `[kind]` legend-suffix test.

**Advisory items:** recorded, not gated: the R*Q⁴→None reset consumes
the user's stored transform once S3 saves `overplot_ytransform` — flagged
into S3's plan (addendum on the analysis branch); pyplot fallback leaks a
figure per refresh; check-state has no memory across disappear/reappear.
Do not expand v2 scope for these.

### v3 — 2026-08-19 (after v2 rejection; todo.md @ `d09c16b`; FINAL retry)

All four v1 findings are RESOLVED and Integrator-verified (15/15 real
reflectivity files classify; six behavior-level reverts now pinned;
suite 17 → 32 tests). The v2 rejection is a single new defect **in this
plan's own prescribed mechanism, owned here**: v2 directed
`itemClicked` → toggle under `NoSelection`, but Qt's
`QStyledItemDelegate::editorEvent` already toggles `checkState` for a
release in the indicator rect, and the view emits `clicked` *before*
its edited-check — so the slot toggles the state straight back and
**the check box itself became unclickable** (proved by `QTest`
probes at indicator vs text coordinates plus a control run without the
connection; the emit-based v2 test bypassed the delegate and could not
see it). Same defect class the harness cycle named: a mechanism
specified from intent, not from measured event dispatch. The blocking
route worked exactly as declared — ui-aspects returned it under this
plan's own blocking flag.

## v3 fixes (final retry — minimal, each half provable)

1. **F1 (the one blocking item):** delete the `itemClicked` connection
   (`:228`) and `_toggle_item_checked` (`:358-364`) entirely. Keep
   `NoSelection` and the `isSelected()` removal — the Integrator's
   control run proves the native delegate then handles indicator
   clicks correctly, keyboard Space still toggles, and `refresh()`'s
   check-only snapshot stays coherent. Do NOT add the
   viewport-event-filter whole-row variant on the last retry — text
   clicks not toggling matches deployed `exp`. Tests: replace the
   emit-based test with real `QTest.mouseClick` probes — indicator
   rect toggles (`style().subElementRect(SE_ItemViewItemCheckIndicator,
   …)`), text-area click does not, and pin the B3 halves separately:
   `assert tab.file_list.selectedItems() == []` after
   `setSelected(True)` under `NoSelection`, plus a forced-
   `MultiSelection` regression probe.
2. **F3:** the folder save guard gains validity:
   `if folder and os.path.isdir(folder):` — same data-loss class as
   v1's B4, one condition. Test: seed a good stored folder, type a bad
   one (field keeps text per `folder_changed`), touch the plot-mode
   combo, assert the stored value is still the good folder.
3. **F5:** `classify_file` opens with `encoding="utf-8",
   errors="replace"` (both real writers emit `Å` above the marker —
   locale-dependent decode reproduces B1's symptom), and terminates on
   the first non-blank non-`#` line (`if line.strip() and not
   line.startswith("#"): break`; EOF still breaks).
4. **F6:** the corpus parametrization becomes
   `sorted((Path("tests/data")).glob("reference_*.txt"))` — all six are
   tracked and the hand-list already drifted by one.
5. **F2 (small, measured, same freshness-lie class):**
   `canvas.draw()` before `plot_selected`'s all-failed early return,
   and move the `overplot_last_refresh` stamp/tooltip to after the
   replot call. Test: two checked files deleted from disk between
   populate and refresh → canvas cleared AND stamp still updates only
   with the post-replot ordering.
6. **Discrimination pins (named by the gate, all cheap):**
   deep-preamble fixture (~40 `#` lines, marker below line 20) and a
   marker-in-data-body fixture that must classify `unknown` (pins the
   window removal AND the termination rule); writer-2 fixture built by
   calling `save_reduced_data._build_header(...)` at test time instead
   of a hand-written imitation; one test each for the explicit-override
   mismatch warning and the filter-preserving rebuild; drop the
   redundant `_last_sel_mode` private asserts where the axis-label
   assert exists.
7. **F4 — optional, drop first if anything wobbles:** in `mixed`
   selections suffix the *unrecognized* files too (`[unknown]`), so the
   file that broke homogeneity is identifiable.

Unchanged: strip list, pixi.lock caveat, source branch = the EXISTING
feature branch with the Integrator's todo.md on top. The authoritative
clean `test-reduction` run belongs at the v3 tip (this cycle's single
failure was the known cross-clone /tmp race, third occurrence).
