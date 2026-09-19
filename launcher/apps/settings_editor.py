#!/usr/bin/python3
"""Settings-editor tab: author a reduction settings JSON with guidance.

A thin view over :class:`~lr_reduction.settings_document.SettingsDocument`.
Every widget here is built from :mod:`lr_reduction.field_spec`, so the fields
the editor offers, the prompts it shows and the values it accepts all come from
one table rather than from hand-written widget code that drifts from the config
class.

Supersedes the never-existent ``JSONSettingsBuilderTab`` that
``new_launcher.py`` carried as a commented-out import.

**The row-index rule.** Every per-angle write goes through
``SettingsDocument.set_angle_field(row, name, value)`` with the row Qt reports
for the edited cell. Nothing here consults ``currentRow()`` to decide *what* to
edit — the selection is used only to choose which row the Remove button
deletes, where it is the actual input rather than a hidden one. Reading config
from the selected row instead of the acted-on row is a known reduction-GUI bug
class, and this table is new code, so the trap would be introduced here.
"""

import functools
import traceback
from pathlib import Path

from qtpy import QtCore, QtGui, QtWidgets

from launcher.app_identity import ensure_identity
from launcher.apps.combo_display import show_in_combo
from launcher.apps.global_settings import load_global_settings
from lr_reduction import field_spec as fs
from lr_reduction.settings_document import SettingsDocument
from lr_reduction.settings_resolver import (
    PREVIOUS_RUN_LAYER,
    Resolved,
    SettingsResolver,
    discover_ipts_settings,
    load_resolution,
    provenance_path,
    save_resolution,
)

#: Above this, populating the table freezes the GUI thread for seconds and
#: costs ~1100x the file size in memory. A settings file with more angles than
#: this is a mistake, not a workload.
MAX_TABLE_ROWS = 500


def guarded(method):
    """Report an exception into the panel instead of letting it leave the slot.

    An unhandled exception in a Qt slot under PyQt5 reaches ``qFatal()``, which
    calls ``abort()``: the whole launcher dies and every other tab loses its
    unsaved state. A settings editor reads files it did not write, so a
    malformed one must be a message, never a process death.
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as exc:  # noqa: BLE001 -- the point is to catch everything
            self.report_problem(exc)
            return None

    return wrapper


#: Workers deliberately kept alive past teardown.
#:
#: "Leak rather than abort" is not achieved by dropping the reference — that is
#: what *causes* the abort. An unparented QThread is owned by Python, so
#: releasing the last reference deletes the C++ object, and deleting a running
#: QThread is precisely `QThread: Destroyed while thread is still running`
#: followed by `abort()`. Measured: exit -6 on the stalled-mount teardown.
#:
#: To leak on purpose the object has to be *held*. A stalled worker is parked
#: here and the process exits with the thread still blocked in its read — the
#: outcome we chose: a leak ends with the process; an abort takes every other
#: tab's unsaved state with it. Parking is not permanent by intent, only in
#: effect: `_reclaim_parked` takes a worker off this list if it turns out to
#: finish after all, so only the genuinely stuck ones are held to the end.
_PARKED_WORKERS = []


def _reclaim_parked(worker):
    """Release a parked worker that turned out to finish after all.

    Parking is for a worker still blocked when the window goes away. Most of
    those are stalled forever, but a merely-slow one completes a moment later
    and there is no reason to hold it for the life of the process. Without this
    the removal below was unreachable — `shutdown` disconnected `finished`
    before parking, so nothing could ever take a worker off the list.
    """
    if worker in _PARKED_WORKERS:
        _PARKED_WORKERS.remove(worker)


class _DiscoveryWorker(QtCore.QThread):
    """Runs `discover_ipts_settings` off the GUI thread.

    Not defensive tidiness. `/SNS` is an sshfs/FUSE mount, and a stalled one
    blocks in D-state — it does **not** raise, so `except OSError` and the slot
    guard are both irrelevant to it. Measured on the synchronous version with a
    2 s stub: the GUI thread blocked for the full 2.00 s and delivered zero
    timer ticks. This is the first place a button press reaches the facility
    filesystem, so the blocking axis is time, not breadth.
    """

    finished_with = QtCore.Signal(object)

    def __init__(self, ipts, tthd, discover, parent=None):
        super().__init__(parent)
        self._ipts = ipts
        self._tthd = tthd
        self._discover = discover

    def run(self):
        try:
            result = self._discover(self._ipts, tthd=self._tthd)
        except BaseException as exc:  # noqa: BLE001 -- carried to the GUI thread
            result = exc
        self.finished_with.emit(result)


class SettingsEditorTab(QtWidgets.QWidget):
    """Editor for one :class:`SettingsDocument`."""

    def __init__(self, document=None, parent=None):
        # First, before any QSettings is constructed: QSettings derives its
        # path from the application identity, so a tab that builds one before
        # the identity is installed would resolve to a different store than the
        # rest of the launcher (S3's adoption contract).
        ensure_identity()
        super().__init__(parent)

        self.document = document if document is not None else SettingsDocument()
        self.settings = QtCore.QSettings()
        self.editors = {}
        self.badges = {}
        self.provenance = {}
        # Guards the table's cellChanged signal while the view writes into it,
        # so repopulating from the document does not echo back as user edits.
        self._populating = False
        # Injectable so a test can redirect the facility root without patching a
        # module global out from under a running worker.
        self._discover = discover_ipts_settings
        self._discovery_worker = None
        self._busy = False
        self._rows_hidden = 0
        self._last_error = None

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._build_toolbar())

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self._build_angle_panel())
        splitter.addWidget(self._build_scalar_panel())
        splitter.addWidget(self._build_report_panel())
        layout.addWidget(splitter)

        # Render whatever the document already holds. __init__ used to call only
        # refresh_report(), so an injected document — the exact path a
        # resolution layer uses — displayed zero angle rows.
        self.set_document(self.document)

    # -- construction ------------------------------------------------------

    def _build_toolbar(self):
        bar = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout()
        bar.setLayout(row)

        # The production entry point for the resolver. Without this the whole
        # layer machinery had no caller: every badge rendered empty and the
        # muddle T3 exists to replace was untouched beside a second unreached
        # mechanism.
        row.addWidget(QtWidgets.QLabel("IPTS"))
        self.ipts_edit = QtWidgets.QLineEdit()
        # Per-angle edits belong to the experiment they were typed for — the
        # arrays index THAT experiment's runs, so carrying them into another
        # IPTS would apply one experiment's per-angle settings to a different
        # set of measurements. Scalar choices ("for this run, use qmax=0.4") are
        # not experiment-bound and survive.
        self.ipts_edit.setPlaceholderText("IPTS-30101")
        self.ipts_edit.setToolTip(
            "Experiment to resolve settings for. Reads shared/autoreduce read-only."
        )
        self.ipts_edit.setMaximumWidth(140)
        row.addWidget(self.ipts_edit)

        row.addWidget(QtWidgets.QLabel("tthd"))
        self.tthd_edit = QtWidgets.QLineEdit("1.0")
        self.tthd_edit.setValidator(QtGui.QDoubleValidator())
        self.tthd_edit.setToolTip(
            "Detector two-theta. Its sign selects the up/down settings file."
        )
        self.tthd_edit.setMaximumWidth(70)
        row.addWidget(self.tthd_edit)

        self.resolve_button = QtWidgets.QPushButton("Resolve from experiment")
        self.resolve_button.setToolTip(
            "Resolve every setting from its layers and show where each one came from"
        )
        self.resolve_button.clicked.connect(lambda _checked=False: self.resolve_for_experiment())
        row.addWidget(self.resolve_button)

        self.load_button = QtWidgets.QPushButton("Load settings...")
        self.load_button.setToolTip(
            "Seed from a settings JSON, or from the header of a pre-reduced .dat"
        )
        self.load_button.clicked.connect(lambda _checked=False: self.load_settings())
        row.addWidget(self.load_button)

        self.save_button = QtWidgets.QPushButton("Save settings...")
        self.save_button.clicked.connect(lambda _checked=False: self.save_settings())
        row.addWidget(self.save_button)

        row.addStretch(1)
        return bar

    def _build_angle_panel(self):
        panel = QtWidgets.QGroupBox("Angles")
        box = QtWidgets.QVBoxLayout()
        panel.setLayout(box)

        self.angle_table = QtWidgets.QTableWidget(0, len(fs.PER_ANGLE_NAMES))
        self.angle_table.setHorizontalHeaderLabels(
            [fs.get(name).label for name in fs.PER_ANGLE_NAMES]
        )
        for column, name in enumerate(fs.PER_ANGLE_NAMES):
            self.angle_table.horizontalHeaderItem(column).setToolTip(fs.get(name).help)
        # Explicitly off, and asserted in the row-isolation test. The header is
        # clickable, and a single sortItems() would decouple visual row order
        # from document index — re-introducing the active-row bug this slug is
        # built to avoid, through the back door.
        self.angle_table.setSortingEnabled(False)
        self.angle_table.cellChanged.connect(self._on_cell_changed)
        box.addWidget(self.angle_table)

        buttons = QtWidgets.QHBoxLayout()
        self.add_angle_button = QtWidgets.QPushButton("Add angle")
        self.add_angle_button.clicked.connect(lambda _checked=False: self.add_angle())
        buttons.addWidget(self.add_angle_button)

        self.remove_angle_button = QtWidgets.QPushButton("Remove angle")
        self.remove_angle_button.clicked.connect(lambda _checked=False: self.remove_selected_angle())
        buttons.addWidget(self.remove_angle_button)
        buttons.addStretch(1)
        box.addLayout(buttons)
        return panel

    def _build_scalar_panel(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QtWidgets.QWidget()
        column = QtWidgets.QVBoxLayout()
        inner.setLayout(column)

        for group in fs.GROUPS:
            scalars = [f for f in fs.fields_in(group) if not f.per_angle]
            if not scalars:
                continue
            box = QtWidgets.QGroupBox(group)
            grid = QtWidgets.QFormLayout()
            box.setLayout(grid)
            for field in scalars:
                editor = self._build_editor(field)
                editor.setToolTip(f"{field.name} — {field.help}")
                self.editors[field.name] = editor
                badge = QtWidgets.QLabel("")
                badge.setEnabled(False)
                self.badges[field.name] = badge
                row = QtWidgets.QWidget()
                row_layout = QtWidgets.QHBoxLayout()
                row_layout.setContentsMargins(0, 0, 0, 0)
                row.setLayout(row_layout)
                row_layout.addWidget(editor, 1)
                row_layout.addWidget(badge)
                grid.addRow(field.label, row)
            column.addWidget(box)

        column.addStretch(1)
        scroll.setWidget(inner)
        return scroll

    def _build_editor(self, field):
        """One widget per field, chosen from the declared type and allowed set."""
        value = self.document.get(field.name)

        if field.type == "bool":
            editor = QtWidgets.QCheckBox()
            # A text-less QCheckBox responds to clicks only within its ~14 px
            # indicator (SE_CheckBoxClickRect), but a form layout will happily
            # stretch the widget to the column width. That leaves most of a
            # visibly-wide control inert, which reads as a broken checkbox.
            # Measured: stretched to 174 px, a click at the widget centre does
            # nothing. Fixing the size to the hint makes the clickable area and
            # the visible extent the same thing.
            editor.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            editor.toggled.connect(
                lambda checked, name=field.name: self._set_scalar(name, bool(checked))
            )
            self._show(field, editor, value)
            return editor

        if field.allowed:
            editor = QtWidgets.QComboBox()
            # A blank first entry for the tri-state fields, where a falsy value
            # means "off" and is the class default.
            if field.falsy_means_off:
                editor.addItem("")
            editor.addItems([str(a) for a in field.allowed])
            editor.currentTextChanged.connect(
                lambda text, name=field.name: self._set_scalar(
                    name, fs.get(name).coerce(text) if text else False
                )
            )
            self._show(field, editor, value)
            return editor

        editor = QtWidgets.QLineEdit()
        if field.type in ("int", "float"):
            validator = (
                QtGui.QIntValidator() if field.type == "int" else QtGui.QDoubleValidator()
            )
            editor.setValidator(validator)
        # editingFinished, not textChanged: a partially typed number ("0.", "-")
        # is not a value to store, and writing on every keystroke would put the
        # document through states the user never asked for.
        editor.editingFinished.connect(
            lambda name=field.name, widget=editor: self._on_scalar_edited(name, widget)
        )
        self._show(field, editor, value)
        return editor

    @staticmethod
    def _show(field, editor, value):
        """Put `value` into `editor`. The ONLY place a value becomes widget state.

        Construction and refresh each used to implement this, and they
        disagreed: construction rendered a list through `_as_text`
        ("50, 200"), the refresh through `str()` ("[50, 200]"), and only the
        first survives being read back by `Field.coerce`. Since `__init__` now
        routes through `set_document` -> `refresh_scalars`, the divergent one
        ran on every tab open — so `data_x_range`, the first editor in tab
        order, was corrupted by a bare focus-out with no typing at all.

        Signals are blocked throughout: displaying a value is not an edit, and
        letting it echo back would rewrite the document from its own rendering.
        """
        was = editor.blockSignals(True)
        try:
            if isinstance(editor, QtWidgets.QCheckBox):
                editor.setChecked(bool(value))
            elif isinstance(editor, QtWidgets.QComboBox):
                SettingsEditorTab._show_in_combo(editor, field, value)
            else:
                editor.setText(SettingsEditorTab._as_text(value))
        finally:
            editor.blockSignals(was)

    @staticmethod
    def _show_in_combo(editor, field, value):
        """Thin alias; the logic is shared (launcher.apps.combo_display)."""
        show_in_combo(editor, field, value)

    @staticmethod
    def _as_text(value):
        """Thin alias; the rendering itself is shared (field_spec.render_value)."""
        return fs.render_value(value)

    def _build_report_panel(self):
        panel = QtWidgets.QGroupBox("Validation and changes")
        box = QtWidgets.QVBoxLayout()
        panel.setLayout(box)
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        box.addWidget(self.status_label)

        self.report = QtWidgets.QPlainTextEdit()
        self.report.setReadOnly(True)
        box.addWidget(self.report)
        return panel

    # -- editing -----------------------------------------------------------

    def _set_scalar(self, name, value):
        """Store a scalar and refresh the panel, reporting rather than aborting."""
        try:
            self.document.set(name, value)
            self._reattribute(name)
            self.refresh_report()
        except Exception as exc:  # noqa: BLE001
            self.report_problem(exc)

    @guarded
    def _on_scalar_edited(self, name, widget):
        self.document.set(name, fs.get(name).coerce(widget.text()))
        self._reattribute(name)
        self.refresh_report()

    @guarded
    def _on_cell_changed(self, row, column):
        """Write one per-angle value, to the row Qt says was edited.

        `row` comes from the signal — the cell that actually changed. Using
        `self.angle_table.currentRow()` here instead would be the active-row
        bug: with row 2 selected, editing row 0 would write to row 2.

        Coercion goes through the field's ELEMENT type. Every per-angle field is
        a `list[...]`, so a coercer that only understood "int" and "float" left
        every cell as text — `useBS` holding the string "False", which is truthy,
        subtracts background the scientist switched off.
        """
        if self._populating:
            return
        name = fs.PER_ANGLE_NAMES[column]
        item = self.angle_table.item(row, column)
        value = fs.get(name).coerce_element(item.text() if item is not None else "")
        self.document.set_angle_field(row, name, value)
        self._reattribute(name)
        self.refresh_report()

    @guarded
    def add_angle(self):
        self.document.add_angle()
        self.refresh_angles()
        # A row change makes every per-angle column this run's doing: the array
        # the experiment file supplied is not the array we now hold. Re-drawing
        # the old attribution would have the header still naming
        # reduce_settings_up.json for a column the scientist just changed.
        self._record_structural_change()
        self.refresh_report()

    @guarded
    def remove_selected_angle(self):
        """Remove the selected row.

        Here the selection IS the input — the user is saying "this one" — which
        is different from consulting it to decide where an edit lands.
        """
        row = self.angle_table.currentRow()
        if row < 0:
            return
        self.document.remove_angle(row)
        self.refresh_angles()
        self._record_structural_change()
        self.refresh_report()

    # -- refresh -----------------------------------------------------------

    def _reattribute(self, name):
        """A person just changed this value here: stop crediting the old source.

        Marked `PREVIOUS_RUN_LAYER`, never `"b"`. With the layer-(b) pre-run
        override deferred to its own slug, an edit made here is exactly what
        that label means — *a run-level choice that is not authoritative now*:
        it lives in this document, and the next Resolve will not honour it.
        Saying so on the badge is the honest reading, and it warns the scientist
        that Resolve will discard the value, which `"b"` would have implied the
        opposite of.

        Not a survivor of `_record_edit`: it records nothing, grants nothing,
        and touches no `ui_overrides`. What it keeps is the property
        `_record_edit`'s own docstring named — "an origin that stops tracking
        the value is worse than none" — which the acceptance bar's "provenance
        intact" requires and which four tests pin.
        """
        self.provenance[name] = Resolved(
            self.document.get(name), PREVIOUS_RUN_LAYER, "changed in this session"
        )
        self.refresh_badges()

    def _record_structural_change(self):
        """A row was added or removed: re-attribute the columns, grant nothing.

        The array is no longer the one the experiment file supplied, so leaving
        the old attribution would have the header naming a file that never said
        this. But nobody typed a value — an "Add angle" click used to mint
        `Resolved(..., "b")` for **all 13** per-angle fields, which is authority
        conjured from a click. The columns are marked as previous-run instead:
        truthful on screen, powerless in the walk.

        This survived the layer-(b) removal deliberately. `PREVIOUS_RUN_LAYER`
        is not layer (b): it is not in `LAYER_ORDER`, it never enters
        `ui_overrides`, and its whole purpose is to keep a badge honest WITHOUT
        granting authority. Dropping it would leave the header still naming an
        experiment file for a column the scientist has just changed — a
        regression in the provenance this slug keeps.
        """
        for name in fs.PER_ANGLE_NAMES:
            self.provenance[name] = Resolved(
                self.document.get(name), PREVIOUS_RUN_LAYER, "row count changed here"
            )
        self.refresh_badges()

    def refresh_badges(self):
        """Show where each value came from, reading the resolver's own record.

        Never a re-derivation: the badge reports the `Resolved` the document was
        built from, so it cannot claim a different origin than the one that won.
        """
        # Per-angle fields resolve as a whole array from one layer, so their
        # provenance belongs on the column header, not on each cell. Inventing a
        # per-cell origin would be a re-derivation of something the resolver
        # never produced.
        for column, name in enumerate(fs.PER_ANGLE_NAMES):
            header = self.angle_table.horizontalHeaderItem(column)
            if header is None:
                continue
            field = fs.get(name)
            resolved = self.provenance.get(name)
            if resolved is None:
                header.setText(field.label)
                header.setToolTip(field.help)
            else:
                header.setText(f"{field.label} [{resolved.source_layer}]")
                header.setToolTip(f"{field.help}\n\nValue came from: {resolved.label}")

        for name, badge in self.badges.items():
            resolved = self.provenance.get(name)
            if resolved is None:
                badge.setText("")
                badge.setToolTip("")
                continue
            badge.setText(f"[{resolved.source_layer}]")
            badge.setToolTip(f"Value came from: {resolved.label}")

    @guarded
    def set_document(self, document, provenance=None):
        """Adopt a document and render all of it.

        The single entry point a resolution layer uses: replacing the document
        without the three refreshes leaves the view showing the previous one.
        """
        self.document = document
        # Provenance arrives with the document it describes, never separately.
        self.provenance = dict(provenance) if provenance is not None else {}
        self.refresh_angles()
        self.refresh_scalars()
        self.refresh_badges()
        self.refresh_report()

    def report_problem(self, exc):
        """Show a failure in the panel instead of letting it kill the process."""
        self._last_error = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
        self.report.setPlainText(
            f"Could not complete that action.\n\n  {self._last_error}\n\n"
            f"The settings in this tab are unchanged."
        )

    def refresh_angles(self):
        self._populating = True
        try:
            shown = min(self.document.n_angles, MAX_TABLE_ROWS)
            self._rows_hidden = self.document.n_angles - shown
            self.angle_table.setRowCount(shown)
            for row in range(shown):
                values = self.document.angle_row(row)
                for column, name in enumerate(fs.PER_ANGLE_NAMES):
                    value = values[name]
                    # _as_text, not str(): repr of a nested list ("[120, 130]")
                    # is re-parsed by coerce_element into ['[120', '130]'], so
                    # BkgROI was corrupted by any edit to its row.
                    self.angle_table.setItem(
                        row, column, QtWidgets.QTableWidgetItem(self._as_text(value))
                    )
        finally:
            self._populating = False

    def refresh_scalars(self):
        for name, editor in self.editors.items():
            self._show(fs.get(name), editor, self.document.get(name))

    def refresh_report(self):
        lines = []
        if self._rows_hidden:
            lines.append(
                f"Showing the first {MAX_TABLE_ROWS} of {self.document.n_angles} angles; "
                f"{self._rows_hidden} are not displayed."
            )
            lines.append("")
        problems = self.document.validate()
        if problems:
            lines.append("Problems:")
            lines.extend(f"  - {message}" for message in problems)
        else:
            lines.append("No problems found.")

        changed = self.document.changed_vs_seed()
        if changed:
            lines.append("")
            lines.append("Changed from the seed:")
            for name in sorted(changed):
                before, after = changed[name]
                lines.append(f"  - {name}: {before!r} -> {after!r}")
        self.report.setPlainText("\n".join(lines))

    # -- files -------------------------------------------------------------

    @guarded
    def resolve_for_experiment(self):
        """Start resolving for the IPTS in the toolbar.

        Returns immediately; discovery runs on a worker and
        `_discovery_finished` completes the resolution.
        """
        ipts = self.ipts_edit.text().strip()
        if not ipts:
            self.set_status("Enter an IPTS to resolve settings for it.")
            return

        text = self.tthd_edit.text().strip()
        try:
            tthd = float(text)
        except ValueError:
            # Not silently 1.0: the sign of tthd chooses the up or down settings
            # file, so guessing it would resolve a scientist's run from the
            # wrong geometry without saying so.
            self.set_status(f"tthd {text!r} is not a number — enter the detector two-theta.")
            return

        self.resolve_button.setEnabled(False)
        self.set_status(f"Resolving {ipts}...")
        self._busy = True
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        # Unparented, deliberately. A QThread destroyed while running aborts the
        # process (SIGABRT; measured exit -6), and the launcher used to do that
        # on EVERY teardown with a resolve in flight — the very stalled-mount
        # case the worker was added for, trading v2's freeze for a crash.
        #
        # Holding the only reference here means a worker that COMPLETES is
        # released by `_forget_worker` when it reports `finished`. Nothing calls
        # deleteLater: releasing the last reference to an unparented QThread is
        # itself what deletes it, which is safe only once it has stopped. A
        # worker still running at teardown never reports `finished`, so
        # `shutdown` parks it in `_PARKED_WORKERS` instead — for that one,
        # releasing the reference is the abort, not the cure. It **leaks one
        # thread**, which is the right trade: a leak ends with the process, an
        # abort takes the other tabs' unsaved state with it.
        worker = _DiscoveryWorker(ipts, tthd, self._discover)
        worker.finished_with.connect(self._discovery_finished)
        worker.finished.connect(self._forget_worker)
        self._discovery_worker = worker
        worker.start()

    @guarded
    def _discovery_finished(self, result):
        """Finish resolving on the GUI thread, or report why we could not."""
        self._release_busy()

        if isinstance(result, BaseException):
            self.report_problem(result)
            return

        result.global_settings = load_global_settings()
        # Layer (b) is declared but not populated — the pre-run UI override was
        # removed with the amendment-20 decompose and is deferred to its own
        # slug. `ui_overrides` stays empty here exactly as `xml_settings` (d)
        # does: the resolver honours the layer if a caller supplies it, and
        # nothing supplies it yet.
        document, provenance = SettingsResolver(result).resolve_all()
        self.set_document(document, provenance)

        found = bool(result.json_settings) or bool(result.global_settings)
        headline = (
            f"Resolved {result.ipts}."
            if found
            else f"Nothing found for {result.ipts} — every value is a built-in default."
        )
        self.set_status(f"{headline}\n\nDiscovery: {result.discovery_status}")

    def _release_busy(self):
        """Undo the busy state exactly once.

        `restoreOverrideCursor` is unreachable if the worker never returns, and
        an override cursor that is never restored is application-wide and lasts
        the life of the process.
        """
        if self._busy:
            self._busy = False
            QtWidgets.QApplication.restoreOverrideCursor()
        self.resolve_button.setEnabled(True)

    def _forget_worker(self):
        """Release a worker that has finished."""
        self._discovery_worker = None

    def shutdown(self):
        """Let go of a running worker without destroying it. Safe to call twice.

        **Called from the window**, because this tab's own `closeEvent` does not
        fire on the path that actually quits the application — a tab inside a
        QTabWidget inside a QMainWindow is torn down without one, which is why
        the guard added in v4 never ran where it mattered.

        Disconnect first, so a late result cannot touch a widget that is going
        away. Then *park* a still-running worker rather than dropping it: see
        `_PARKED_WORKERS` — releasing the reference is what aborts.
        """
        worker = self._discovery_worker
        if worker is not None:
            for signal, slot in (
                (worker.finished_with, self._discovery_finished),
                (worker.finished, self._forget_worker),
            ):
                try:
                    signal.disconnect(slot)
                except (TypeError, RuntimeError):
                    # Already disconnected, or the C++ object is gone.
                    pass
            try:
                still_running = worker.isRunning()
            except RuntimeError:
                still_running = False
            if still_running and worker not in _PARKED_WORKERS:
                _PARKED_WORKERS.append(worker)
                # Reclaim it if it ever finishes; see _reclaim_parked.
                worker.finished.connect(lambda w=worker: _reclaim_parked(w))
            self._discovery_worker = None
        self._release_busy()

    def closeEvent(self, event):
        """Defensive: the real teardown comes through `shutdown` from the window."""
        self.shutdown()
        super().closeEvent(event)

    def set_status(self, text):
        """Show discovery status in its own persistent field.

        Kept out of the validation report: that is rebuilt on every edit, so the
        status of the resolution — which file the values came from — used to
        vanish the moment anyone typed.
        """
        self.status_label.setText(text)

    @guarded
    def load_settings(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load reduction settings",
            self.settings.value("settings_editor_dir", ""),
            "Settings (*.json *.dat);;All files (*)",
        )
        if not path:
            return
        # The refreshes are INSIDE the try. They were outside it, and the catch
        # was only (ValueError, OSError), so a file whose per-angle value is not
        # a sequence ({"tof_min": 5}) raised TypeError out of the slot and
        # aborted the launcher.
        try:
            document = SettingsDocument.from_file(path)
            # Read the sidecar if one is beside the file. Without this a
            # Resolve -> Save -> reopen cycle showed blank badges for settings
            # whose origins had just been written next to them: a persisted
            # round-trip wired on the write side only.
            provenance = None
            if provenance_path(path).exists():
                _, provenance = load_resolution(path)
                # A "b" in a file on disk was set for a PREVIOUS run. Displayed,
                # never authoritative — see PREVIOUS_RUN_LAYER.
                provenance = {
                    name: (
                        Resolved(r.value, PREVIOUS_RUN_LAYER, r.source_detail)
                        if r.source_layer == "b"
                        else r
                    )
                    for name, r in provenance.items()
                }
            self.set_document(document, provenance)
        except Exception as exc:  # noqa: BLE001
            QtWidgets.QMessageBox.warning(self, "Could not load settings", str(exc))
            self.report_problem(exc)
            return
        self.settings.setValue("settings_editor_dir", str(Path(path).parent))

    @guarded
    def save_settings(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save reduction settings",
            self.settings.value("settings_editor_dir", ""),
            "Settings (*.json);;All files (*)",
        )
        if not path:
            return
        # load_from_file dispatches on the suffix, so a name saved without a
        # recognised one cannot be reloaded. Checked against the accepted set
        # rather than "has a suffix": "settings_0.5deg" has suffix ".5deg",
        # which is not a suffix anyone meant.
        if Path(path).suffix.lower() not in (".json", ".dat"):
            path = path + ".json"
        problems = fs.refusals(self.document.to_dict())
        if problems:
            # The same gate the preference dialog uses. This file can land in
            # shared/autoreduce, where autoreduction reads it.
            QtWidgets.QMessageBox.warning(
                self, "Cannot save", "\n".join(problems[:10])
            )
            self.set_status("Not saved — fix the problems listed in the report.")
            return
        try:
            # save_resolution writes the WHOLE document (to_dict, not
            # normalize) plus a provenance sidecar beside it. One policy, stated
            # once: a settings file the scientist saves keeps every field they
            # can see — normalize() dropped RBnum, which has an editable column
            # whose values were silently discarded on save.
            save_resolution(path, self.document, self.provenance)
        except Exception as exc:  # noqa: BLE001
            QtWidgets.QMessageBox.warning(self, "Could not save settings", str(exc))
            return
        self.settings.setValue("settings_editor_dir", str(Path(path).parent))
