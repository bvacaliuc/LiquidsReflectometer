# Plan: port-overplot-axes-refresh (S2)

**Campaign:** `exp-settings-roi` · base `exp` @ `a4ae8b8` · charter §3 PRs
#9 + #10 ("port, adapted — one overplot series") · seeds
`agentic/feature/overplot-axes` @ `300d040`,
`agentic/feature/overplot-refresh` @ `7bc34b2`
**Retry attempt:** 1

Review domains: ui-aspects-reviewer (advisory — matplotlib-in-Qt axes +
widget state), test-reviewer (advisory).

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
  charter §3).
