# Plan: overplot-axes — Overplot tab axes wrong for Direct Beam files

**Slug:** `overplot-axes`
**Effort:** `new_workflow-repairs-2026-04`
**Base branch:** `new_workflow_ui_plan`
**Plan revision:** v1 (initial)

## Symptom

The Overplot tab in `new_launcher` always labels axes `Q` (x) and `R`
(y) and offers a `R*Q^4` Y transform, even when the loaded files are
Direct-Beam intensity-vs-wavelength files (`I(λ)`). Users plotting DB
files therefore see meaningless axis labels and a meaningless transform
choice.

The Overplot tab is meant to handle two distinct file kinds in
`/SNS/REF_L/IPTS-*`:

- **Reflectivity files** (autoreduce output), e.g.
  `/SNS/REF_L/IPTS-36776/shared/autoreduce/REFL_*_combined_data_auto.txt`
  — header line `# Q [1/Angstrom]   R   dR   dQ [FWHM]`, 4 columns,
  units Q in Å⁻¹, R dimensionless.
  *(Note: the original effort prompt referenced
   `REF_L_*_combined_data_auto.txt`; the actual filename pattern is
   `REFL_*` — single underscore after `REFL`. Treat this as the
   canonical pattern.)*
- **Direct-Beam transmission files**, e.g.
  `/SNS/REF_L/IPTS-36776/shared/transmission/DB_*.txt` — header line
  `# columns = lambda intensity error`, 3 columns, units λ in Å,
  intensity in counts.

## Verified root cause

`launcher/apps/overplot.py` was written under the assumption that all
plotted files are reflectivity. There is no plot-mode selector and no
detection of file kind. Specifically:

- **Hardcoded labels** at `launcher/apps/overplot.py:348-349` (issues.md
  hypothesis cited 341-342; the file has grown by 7 lines since the
  hypothesis was authored — root cause unchanged):

  ```python
  ax.set_xlabel("Q")
  ax.set_ylabel("R" if transform == "None" else "R*Q^4")
  ```

  The fallback (no Qt backend) external-pyplot path at lines 387-388
  uses generic `"x"` / `"y"` labels — also not informative.

- **Y-transform combo hardcodes reflectivity-only options** at
  `launcher/apps/overplot.py:107-110`:

  ```python
  self.ytransform_combo.addItems(["None", "R*Q^4"])
  ```

  `R*Q^4` is meaningless for `I(λ)` data; offering it is misleading.

- **`save_settings` / `read_settings`** at `launcher/apps/overplot.py:166-181`
  persist `overplot_folder` and `overplot_xscale`, plus restore (but do
  not save — see `settings-persistence-plan.md`) `overplot_ytransform`.
  No plot-mode key exists.

## Files to change

| File | Lines | Change |
|---|---|---|
| `launcher/apps/overplot.py` | 60-130 (controls layout, before file list) | Add a `Plot mode` selector (`Auto` / `Reflectivity` / `Direct Beam`) populated as a `QComboBox`. |
| `launcher/apps/overplot.py` | 165-181 (`read_settings`/`save_settings`) | Add `overplot_mode` to the persisted-settings set. Default to `Auto`. |
| `launcher/apps/overplot.py` | 237-293 (`_prepare_data`) | Refactor signature to take a *resolved* mode and a transform; raise on the `Reflectivity`+ambiguous-input combination. The transform branch (`R*Q^4`) is gated to `mode == "Reflectivity"`. |
| `launcher/apps/overplot.py` | 295-390 (`plot_selected`, both canvas and pyplot fallback) | (a) Resolve mode per-file: if combo is `Auto`, classify each file by header inspection; if combo is `Reflectivity` or `Direct Beam`, use that. (b) Set axes labels and yscale per resolved mode. (c) Disable / gray out the `R*Q^4` choice when the resolved mode for the *whole selection* is `Direct Beam`. |
| `launcher/apps/overplot.py` (new helper) | (top of file or new module-private function) | `def classify_file(path) -> {"reflectivity"|"direct_beam"|"unknown"}` — read the first ~10 lines of the file, look for `Q [1/Angstrom]` (→ reflectivity) or `columns = lambda intensity error` (→ direct_beam), else unknown. |
| `launcher/tests/__init__.py` | (new) | Empty package marker. |
| `launcher/tests/test_overplot_axes.py` | (new) | Unit tests per the TDD seed below. |
| `launcher/tests/data/db_fixture.txt` | (new) | Synthetic 3-column DB-format fixture, 5 rows, with the canonical `# columns = lambda intensity error` header. |
| `launcher/tests/data/refl_fixture.txt` | (new) | Synthetic 4-column REFL-format fixture, 5 rows, with the canonical `# Q [1/Angstrom]   R   dR   dQ [FWHM]` header. |
| `lr_reduction/pyproject.toml` | `[tool.pytest.ini_options]` `testpaths` (or new pixi `test-launcher` task) | Ensure `launcher/tests/` is collected by `pixi run test-reduction`, OR add a `test-launcher` pixi task. Developer chooses based on what fits cleanest in the existing test config. |

## Preferred design (robust)

Per `~/.claude/CLAUDE.md` `[ALWAYS] Design framing` (robust over
simple, detection complete, auto-resolution minimal):

1. **Detection is complete.** Every loaded file is classified by its
   header into one of `reflectivity`, `direct_beam`, or `unknown`. The
   classifier is the source of truth; the combobox is the override.

2. **Auto-resolution is minimal.** When the user selects `Auto` (the
   default), each file's header decides axes/transform behavior. When
   the user selects an explicit mode (`Reflectivity` or `Direct Beam`),
   that mode is used for the entire selection — files whose header
   does not match are still plotted, but a one-line `QMessageBox`
   warning enumerates the mismatched filenames so the user can choose
   to filter them out. We do **not** silently skip mismatched files.

3. **Plot-mode coupling.** The resolved mode drives:
   - `ax.set_xlabel`: `"Q [1/Å]"` for reflectivity, `"λ [Å]"` for
     direct beam, `"x"` for unknown.
   - `ax.set_ylabel`: `"R"` for reflectivity (or `"R · Q⁴"` if the
     R*Q^4 transform is active), `"I"` (intensity, counts) for direct
     beam, `"y"` for unknown.
   - `ax.set_yscale`: `"log"` in both — both quantities are
     positive-only and span multiple decades. Existing `set_yscale("log")`
     is correct; don't change it.
   - The `R*Q^4` combo entry is **disabled** when the resolved
     selection mode is direct beam (Qt's `QComboBox::setItemData` with
     `Qt::ItemIsEnabled` removed). When in `Auto` mode and the
     selection contains *any* direct-beam files, the transform is
     forced to `None` and the combo is disabled — all-or-nothing
     transform application is the only sane policy across mixed files.

4. **Mixed selections.** If the user selects files of both kinds while
   in `Auto`, the plot title gets a parenthetical
   `(mixed: 2 reflectivity, 1 direct beam)` and each curve's label
   includes its detected kind in brackets, e.g.
   `REFL_42213_combined_data_auto.txt [reflectivity]`. The mismatched
   y-axis problem is irreducible — the user is the only one who can
   say which axis they meant — but at least the plot is honest about
   its contents.

5. **Mode persistence.** The `Plot mode` combo selection persists
   alongside `overplot_xscale` via `QSettings` (key
   `overplot_mode`). Default on first launch is `Auto`.

## Failure-mode matrix

| Case | Detection | Behavior |
|---|---|---|
| All selected files are DB (header `lambda intensity error`) | All `direct_beam` | Mode = Direct Beam; axes "λ [Å]" / "I"; transform combo locked at `None` |
| All selected files are REFL (header `Q [1/Angstrom]`) | All `reflectivity` | Mode = Reflectivity; axes "Q [1/Å]" / "R"; transform `None` or `R*Q^4` allowed |
| Mixed selection in `Auto` | Per-file classification | Plot mode = `mixed`; axes `"x"` / `"y"`; transform forced to `None`, combo disabled; warning dialog with mismatched count |
| Combo set to Direct Beam, file is REFL header | User-override mode | Plot file with DB axes; warn once with the mismatched filenames |
| Combo set to Reflectivity, file is DB header | User-override mode | Same: plot with REFL axes; warn once with the mismatched filenames |
| Header absent or unrecognized | `unknown` | Treat as the *current combo selection* (or `reflectivity` if combo is `Auto` for backwards compat); log path to stdout for debug |
| File with comment-only line (`#` lines but no canonical header) | `unknown` | Same as above |
| File where `np.loadtxt` raises (truncated, garbled) | n/a | Existing `_prepare_data` raises `RuntimeError` — keep that path, no regression |
| First-launch `QSettings` empty | — | Combo defaults to `Auto`; existing reflectivity-only behavior of the user's saved folder is preserved |
| Combo set to Direct Beam, user picks `R*Q^4` | — | Combo entry is disabled (grayed out); user *cannot* select it. If a stale `overplot_ytransform = R*Q^4` is loaded under a DB mode, force to `None` and re-save. |

## Red-Green TDD seed

New test file `launcher/tests/test_overplot_axes.py`. Tests run with
`QT_QPA_PLATFORM=offscreen` so a display is not required.

```python
# test 1 — RED first: classifier returns "direct_beam" for the DB header
def test_classify_db_fixture(tmp_path):
    p = tmp_path / "DB_test.txt"
    p.write_text("# Header\n# columns = lambda intensity error\n"
                 "1.0 100.0 1.0\n2.0 200.0 1.4\n")
    assert classify_file(str(p)) == "direct_beam"

# test 2 — RED first: classifier returns "reflectivity" for the REFL header
def test_classify_refl_fixture(tmp_path):
    p = tmp_path / "REFL_test.txt"
    p.write_text("# header line A\n# Q [1/Angstrom] R dR dQ [FWHM]\n"
                 "0.01 0.5 0.05 0.001\n0.02 0.4 0.04 0.001\n")
    assert classify_file(str(p)) == "reflectivity"

# test 3 — RED first: classifier returns "unknown" on missing header
def test_classify_unknown_no_header(tmp_path):
    p = tmp_path / "garbled.txt"
    p.write_text("0.01 0.5\n0.02 0.4\n")
    assert classify_file(str(p)) == "unknown"

# test 4 — RED first: Overplot resolves x/y labels for DB selection
def test_overplot_db_labels(qapp, tmp_path):
    # populate fixture, drive Overplot's plot_selected with combo=Auto,
    # assert ax.get_xlabel() == "λ [Å]" and ax.get_ylabel() == "I"
    ...

# test 5 — RED first: Overplot resolves x/y labels for REFL selection
def test_overplot_refl_labels(qapp, tmp_path):
    ...

# test 6 — RED first: R*Q^4 entry is disabled when DB selected
def test_rq4_disabled_for_db(qapp, tmp_path):
    # load DB fixture, assert ytransform_combo's R*Q^4 item flags
    # have the Qt::ItemIsEnabled bit cleared.
    ...

# test 7 — Mixed selection emits "mixed" mode and disables R*Q^4
def test_mixed_selection(qapp, tmp_path):
    ...

# test 8 — overplot_mode round-trips through QSettings
def test_mode_persists(qapp_with_isolated_settings):
    # under a test-only QCoreApplication org/app (see
    # settings-persistence-plan.md), set Plot mode = Direct Beam,
    # destroy and recreate Overplot, assert combo loaded as Direct Beam.
    ...
```

`qapp` and `qapp_with_isolated_settings` are pytest fixtures the
Developer adds to `launcher/tests/conftest.py`. Use the headless Qt
stack (no `pytest-qt` if avoidable per orchestration §11).

## Acceptance

The Developer's `feature/overplot-axes` branch must:

1. Pass all 8 tests in `launcher/tests/test_overplot_axes.py`
   (Red-Green progression visible in commits).
2. Pass the existing `pixi run test-reduction` suite with no
   regressions.
3. Manually: launching `python launcher/new_launcher.py` against
   `IPTS-36776/shared/transmission/` shows λ-vs-I axes; against
   `IPTS-36776/shared/autoreduce/` shows Q-vs-R axes; in `Auto` mode
   no manual switch is required between the two folders.
4. The legacy `launcher.py` (the *old* launcher) is untouched.

## Notes for the Integrator (when running tests)

- The new `launcher/tests/` directory must be collected by the
  pytest invocation. If `pyproject.toml` `testpaths = ["tests"]`
  excludes it, either widen `testpaths` or add a parallel pixi task
  `test-launcher = { cmd = "python -m pytest -vv launcher/tests" }`.
- `QT_QPA_PLATFORM=offscreen` should be set in the test env so the
  tests can construct `QWidget`s headlessly. A `conftest.py` `os.environ`
  setting in `launcher/tests/conftest.py` is the cleanest place.
- No `/SNS/` mount access is required by the tests — fixtures are
  synthetic.

## Cross-references

- `~/.claude/CLAUDE.md` `[ALWAYS] Design framing` — robust default;
  detection complete.
- `setup/patterns/ui-aspects.md` — matplotlib-inside-Qt conventions
  (relevant for the canvas branch).
- `settings-persistence-plan.md` — the QSettings org/app isolation
  fix that test 8 above relies on.
- `overplot-refresh-plan.md` — the refresh-button feature shares the
  classifier helper introduced here; if both plans land
  independently, the refresh feature should reuse `classify_file`
  rather than re-derive it.
