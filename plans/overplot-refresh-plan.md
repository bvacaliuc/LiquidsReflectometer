# Plan: overplot-refresh — Overplot tab needs a refresh button

**Slug:** `overplot-refresh`
**Effort:** `new_workflow-repairs-2026-04`
**Base branch:** `new_workflow_ui_plan`
**Plan revision:** v1 (initial)

## Symptom

When data files in the Overplot tab's chosen folder change on disk —
typically because an autoreduce run has just rewritten a
`REFL_<run>_combined_data_auto.txt` — the Overplot canvas continues
to show the *old* contents. The only current way to pick up the
update is to click `Choose folder` and re-select the same folder,
which clears every checked-file selection. The user wants a single
button that refreshes the file list against the disk, preserves
selection, and redraws checked files.

## Verified root cause

`launcher/apps/overplot.py` has no UI affordance to re-read. The
existing path:

- `populate_file_list(folder)` at `launcher/apps/overplot.py:192-208`
  always *clears* the list (`self.file_list.clear()`) and rebuilds
  from `os.listdir`. Calling it on the same folder a second time
  loses every check state.
- `plot_selected()` at `launcher/apps/overplot.py:295-352` does the
  read-from-disk + plot work, but is wired only to the `Plot
  selected` button. There is no public method that re-reads disk for
  *currently checked* files without re-collecting selection.
- `choose_folder()` at `launcher/apps/overplot.py:183-190` is the
  only path that triggers a list rebuild today; it loses selection
  by design (clears the list, sets all items unchecked).

Issues.md cited line ranges `120-126`, `157-161`, `190-206`; current
file has `120-126` (button row exact match), `156-161` (signal
connections), and `192-208` (`populate_file_list`). Drift small;
hypothesis intact.

## Files to change

| File | Lines | Change |
|---|---|---|
| `launcher/apps/overplot.py` | 120-126 (button row, after `Clear plot`) | Add `self.refresh_btn = QPushButton("Refresh")` with a tooltip describing both phases. |
| `launcher/apps/overplot.py` | 156-162 (connections) | Wire `self.refresh_btn.clicked.connect(self.refresh)` |
| `launcher/apps/overplot.py` | new method between `populate_file_list` and `apply_filter` | Add `def refresh(self)` and `def _merge_files(self, folder, current_checked) -> set[str]:` (helper). See pseudocode below. |
| `launcher/apps/overplot.py` | 192-208 (`populate_file_list`) | Kept as the **first-time-population** path (called from `choose_folder`). Refresh does *not* go through it. The two paths share `_scan_folder(folder) -> list[str]` to avoid drift. |
| `launcher/apps/overplot.py` | (no change required) | `_prepare_data` and the actual canvas-plot loop already re-read from disk — `refresh` simply calls `plot_selected()` after the merge step. |
| `launcher/tests/test_overplot_refresh.py` | (new) | Unit tests per the TDD seed below. |

### Refresh method pseudocode

```python
def refresh(self):
    """Two-phase refresh: rescan folder (preserving check state),
    then redraw any currently-checked files from disk."""
    folder = self.folder_label.text()
    if not folder or not os.path.isdir(folder):
        QMessageBox.warning(self, "Refresh",
                            "Choose a folder first, or the previous folder "
                            "is no longer accessible.")
        return

    # Phase 1: rescan, preserving check state of files still present
    pre_checked = {
        self.file_list.item(i).text()
        for i in range(self.file_list.count())
        if self.file_list.item(i).checkState() == QtCore.Qt.Checked
    }

    try:
        on_disk = sorted(
            f for f in os.listdir(folder)
            if f.lower().endswith(".dat") or f.lower().endswith(".txt")
        )
    except OSError as e:
        QMessageBox.critical(self, "Refresh failed",
                             f"Could not list {folder}: {e}")
        return  # leave UI as-is — existing plot remains visible

    self._files = on_disk
    self.file_list.clear()
    for f in on_disk:
        item = QListWidgetItem(f)
        item.setCheckState(
            QtCore.Qt.Checked if f in pre_checked else QtCore.Qt.Unchecked
        )
        self.file_list.addItem(item)

    # Phase 2: re-plot whatever's still checked
    still_checked = pre_checked & set(on_disk)
    dropped = pre_checked - still_checked
    if still_checked:
        self.plot_selected()
        if dropped:
            # Quietly note in the status bar (or a one-line warning) that
            # some previously-plotted files are gone.
            QMessageBox.information(
                self, "Refresh",
                f"{len(dropped)} previously-plotted file(s) no longer "
                f"present on disk:\n" + "\n".join(sorted(dropped)),
            )
```

## Preferred design (robust)

Per `~/.claude/CLAUDE.md` `[ALWAYS] Design framing` — detection
complete, auto-resolution minimal:

1. **Two-phase, single button.** The button performs (a) folder rescan
   that preserves check state for files still present and (b) a
   re-plot of currently-checked files. One button is the right
   ergonomic; "Rescan" + "Replot" as separate buttons is overkill for
   the actual user action of "the autoreduce run finished, pull it in."

2. **Detection is complete.** Every disk state is detected and
   surfaced:
   - File still present + still checked → re-plotted from disk.
   - File still present + unchecked → kept in list, unchecked.
   - File added since last scan → appears in list, unchecked (so the
     user can choose to plot the new run).
   - File removed since last scan → dropped from list with a one-line
     `QMessageBox.information` enumerating what disappeared (so the
     user is not silently left with a stale plot legend).
   - Folder unmounted / inaccessible → `QMessageBox.critical`, return
     without touching the existing UI; the previous plot stays
     visible.
   - Read race during refresh (file rewritten mid-`np.loadtxt`) → the
     existing `_prepare_data` `RuntimeError` path catches it; the
     `plot_selected` loop already shows a `QMessageBox.warning` and
     skips the offending file.

3. **Auto-resolution is minimal.** Refresh does *not* try to recover
   from a deleted folder by walking up the path; it does *not*
   silently re-add a file that came back; it does *not* move
   currently-checked items to the top of the list. Just: rescan,
   redraw checked, warn on dropped.

4. **No background polling.** The user-controlled button is the only
   trigger. Auto-refresh on file-system events is out of scope —
   adds Qt `QFileSystemWatcher` complexity, race conditions with
   autoreduce's atomic-write-and-rename, and surprise re-plots while
   the user is reading the current canvas.

5. **Tooltip and last-refresh timestamp.** The button's tooltip
   reads:
   `"Re-read this folder. Keeps current selection where files still
   exist; replots checked files. Last refreshed: never."` The trailing
   timestamp updates after each successful refresh and persists across
   sessions via `QSettings` key `overplot_last_refresh` (purely
   informational; safe to drop on corrupt-value read).

## Failure-mode matrix

| Case | Expected behavior |
|---|---|
| No folder chosen | Refresh button shows a warning ("Choose a folder first…"); UI otherwise unchanged |
| Folder still mounted, no files changed | List rebuilt with same items, same check states; checked files re-plotted (cheap, since `np.loadtxt` is the same data) |
| Folder unmounted / removed | `QMessageBox.critical` with the OS error; existing list and plot stay visible (do **not** clear the plot) |
| One file deleted between refreshes | File silently dropped from list; if it was checked, an information dialog enumerates the dropped names. The plot is redrawn without that file's curve. |
| One new file appears (e.g. a new autoreduce output) | Appears in list, unchecked. User can check + Plot selected to bring it into the plot. |
| One file's content changed (the canonical autoreduce-finished case) | Already-checked file re-read from disk and re-plotted with new content. This is the golden path. |
| Concurrent write race during `np.loadtxt` | `_prepare_data` raises; `plot_selected` shows a `QMessageBox.warning` and skips that file (existing behavior, no regression) |
| User has a filter typed in the filter box | Refresh respects the existing filter — but rescans the underlying `self._files`. After rescan, `apply_filter` is invoked on the in-memory text so filtered view stays consistent. |
| User runs Refresh while a plot is already on screen | Existing plot is replaced after Phase 2 (`plot_selected` clears `self.figure` then redraws). |
| Refresh on first launch (folder restored from QSettings, list populated by `read_settings`) | Works; restores from disk just as if user had clicked Choose folder + checked items |

## Red-Green TDD seed

New test file `launcher/tests/test_overplot_refresh.py`. Reuses the
`isolated_qapp` fixture from `settings-persistence-plan.md`'s conftest.

```python
# test 1 — RED first: refresh button exists and is connected
def test_refresh_button_exists(isolated_qapp):
    tab = Overplot()
    assert hasattr(tab, "refresh_btn")
    assert tab.refresh_btn.text() == "Refresh"
    # signal is connected by checking receivers count via QObject metainfo

# test 2 — RED first: refresh on empty folder is a no-op warning
def test_refresh_no_folder(isolated_qapp, monkeypatch):
    tab = Overplot()
    monkeypatch.setattr(tab, "folder_label",
                        type(tab.folder_label)(text=""))
    # call refresh directly; assert no crash and folder_label unchanged.
    tab.refresh()

# test 3 — RED first: refresh preserves check state of still-present files
def test_refresh_preserves_check_state(isolated_qapp, tmp_path):
    # populate two files; check one; refresh; assert that one stays checked.
    a = tmp_path / "a.dat"; a.write_text("0.01 0.5\n")
    b = tmp_path / "b.dat"; b.write_text("0.01 0.7\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    # check 'a.dat'
    for i in range(tab.file_list.count()):
        item = tab.file_list.item(i)
        if item.text() == "a.dat":
            item.setCheckState(QtCore.Qt.Checked)
    tab.refresh()
    # find 'a.dat' again; assert still checked
    states = {tab.file_list.item(i).text():
              tab.file_list.item(i).checkState()
              for i in range(tab.file_list.count())}
    assert states["a.dat"] == QtCore.Qt.Checked
    assert states["b.dat"] == QtCore.Qt.Unchecked

# test 4 — RED first: refresh picks up new files added on disk
def test_refresh_picks_up_new_files(isolated_qapp, tmp_path):
    a = tmp_path / "a.dat"; a.write_text("0.01 0.5\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    # add new file after first scan
    c = tmp_path / "c.dat"; c.write_text("0.01 0.9\n")
    tab.refresh()
    items = [tab.file_list.item(i).text() for i in range(tab.file_list.count())]
    assert "c.dat" in items

# test 5 — RED first: refresh drops removed files and reports them
def test_refresh_drops_removed(isolated_qapp, tmp_path, monkeypatch):
    a = tmp_path / "a.dat"; a.write_text("0.01 0.5\n")
    b = tmp_path / "b.dat"; b.write_text("0.01 0.7\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    for i in range(tab.file_list.count()):
        item = tab.file_list.item(i)
        if item.text() == "b.dat":
            item.setCheckState(QtCore.Qt.Checked)
    b.unlink()
    captured = {}
    monkeypatch.setattr(QMessageBox, "information",
                        lambda *a, **k: captured.setdefault("info", a))
    tab.refresh()
    items = [tab.file_list.item(i).text() for i in range(tab.file_list.count())]
    assert "b.dat" not in items
    assert "info" in captured  # user was told 'b.dat' disappeared

# test 6 — RED first: refresh re-reads file content (the golden path)
def test_refresh_rereads_content(isolated_qapp, tmp_path):
    a = tmp_path / "a.dat"; a.write_text("# Q R dR\n0.01 0.5 0.05\n0.02 0.4 0.04\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    for i in range(tab.file_list.count()):
        item = tab.file_list.item(i)
        if item.text() == "a.dat":
            item.setCheckState(QtCore.Qt.Checked)
    tab.plot_selected()
    # rewrite file content
    a.write_text("# Q R dR\n0.01 0.9 0.09\n0.02 0.7 0.07\n")
    tab.refresh()
    # The y-axis line in the figure should now reflect the new values.
    # Read the line data from the matplotlib axes:
    ax = tab.figure.axes[0]
    line = ax.lines[0]
    ydata = line.get_ydata()
    assert pytest.approx(ydata[0]) == 0.9

# test 7 — Inaccessible folder leaves UI intact
def test_refresh_unmounted_folder(isolated_qapp, tmp_path, monkeypatch):
    tab = Overplot()
    tab.folder_label.setText("/nonexistent/path/12345")
    captured = {}
    monkeypatch.setattr(QMessageBox, "critical",
                        lambda *a, **k: captured.setdefault("crit", a))
    tab.refresh()
    assert "crit" in captured
    # No crash; folder_label unchanged
    assert tab.folder_label.text() == "/nonexistent/path/12345"
```

## Acceptance

1. All 7 tests pass with `pixi run test-reduction` (or `test-launcher`).
2. Manual: launch `new_launcher`, open Overplot, choose
   `/SNS/REF_L/IPTS-36776/shared/autoreduce/`, check a `REFL_*` file,
   click Plot. Then `touch` (or wait for autoreduce to overwrite) the
   file's mtime / contents on disk. Click Refresh. The plot updates
   without losing the user's other selections.
3. The button's tooltip mentions both phases.
4. Removing a file on disk and clicking Refresh shows the
   information dialog and the line disappears from the plot.

## Notes for the Integrator

- This plan introduces no new pixi/conda dependency.
- Tests share the conftest from `settings-persistence-plan.md`.
- The `classify_file` helper from `overplot-axes-plan.md` is **not**
  invoked by `refresh()` directly — it is used inside `plot_selected`,
  which `refresh()` calls. Keep that boundary so refresh remains a
  pure list-vs-disk reconciliation.

## Cross-references

- `overplot-axes-plan.md` — `refresh()` indirectly calls `plot_selected`,
  which uses the new `Plot mode` machinery. If overplot-axes lands
  first, refresh inherits the mode-aware behavior for free. If
  refresh lands first, the existing reflectivity-only behavior still
  works; overplot-axes adds correct behavior on top.
- `setup/patterns/ui-aspects.md` — matplotlib-inside-Qt save/redraw
  conventions.
- `~/.claude/CLAUDE.md` `[ALWAYS] Design framing` — robust over
  simple, complete detection of disk-state cases.
