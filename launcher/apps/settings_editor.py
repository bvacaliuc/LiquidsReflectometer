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

from pathlib import Path

from qtpy import QtCore, QtGui, QtWidgets

from launcher.app_identity import ensure_identity
from lr_reduction import field_spec as fs
from lr_reduction.settings_document import SettingsDocument


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
        # Guards the table's cellChanged signal while the view writes into it,
        # so repopulating from the document does not echo back as user edits.
        self._populating = False

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._build_toolbar())

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self._build_angle_panel())
        splitter.addWidget(self._build_scalar_panel())
        splitter.addWidget(self._build_report_panel())
        layout.addWidget(splitter)

        self.refresh_report()

    # -- construction ------------------------------------------------------

    def _build_toolbar(self):
        bar = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout()
        bar.setLayout(row)

        self.load_button = QtWidgets.QPushButton("Load settings...")
        self.load_button.setToolTip(
            "Seed from a settings JSON, or from the header of a pre-reduced .dat"
        )
        self.load_button.clicked.connect(self.load_settings)
        row.addWidget(self.load_button)

        self.save_button = QtWidgets.QPushButton("Save settings...")
        self.save_button.clicked.connect(self.save_settings)
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
        self.angle_table.cellChanged.connect(self._on_cell_changed)
        box.addWidget(self.angle_table)

        buttons = QtWidgets.QHBoxLayout()
        self.add_angle_button = QtWidgets.QPushButton("Add angle")
        self.add_angle_button.clicked.connect(self.add_angle)
        buttons.addWidget(self.add_angle_button)

        self.remove_angle_button = QtWidgets.QPushButton("Remove angle")
        self.remove_angle_button.clicked.connect(self.remove_selected_angle)
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
                grid.addRow(field.label, editor)
            column.addWidget(box)

        column.addStretch(1)
        scroll.setWidget(inner)
        return scroll

    def _build_editor(self, field):
        """One widget per field, chosen from the declared type and allowed set."""
        value = self.document.get(field.name)

        if field.type == "bool":
            editor = QtWidgets.QCheckBox()
            editor.setChecked(bool(value))
            # A text-less QCheckBox responds to clicks only within its ~14 px
            # indicator (SE_CheckBoxClickRect), but a form layout will happily
            # stretch the widget to the column width. That leaves most of a
            # visibly-wide control inert, which reads as a broken checkbox.
            # Measured: stretched to 174 px, a click at the widget centre does
            # nothing. Fixing the size to the hint makes the clickable area and
            # the visible extent the same thing.
            editor.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            editor.toggled.connect(
                lambda checked, name=field.name: self.document.set(name, bool(checked))
            )
            return editor

        if field.allowed:
            editor = QtWidgets.QComboBox()
            editor.addItems([str(a) for a in field.allowed])
            if value is not None:
                editor.setCurrentText(str(value))
            editor.currentTextChanged.connect(
                lambda text, name=field.name: self.document.set(name, text)
            )
            return editor

        editor = QtWidgets.QLineEdit("" if value is None else str(value))
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
        return editor

    def _build_report_panel(self):
        panel = QtWidgets.QGroupBox("Validation and changes")
        box = QtWidgets.QVBoxLayout()
        panel.setLayout(box)
        self.report = QtWidgets.QPlainTextEdit()
        self.report.setReadOnly(True)
        box.addWidget(self.report)
        return panel

    # -- editing -----------------------------------------------------------

    def _on_scalar_edited(self, name, widget):
        self.document.set(name, self._coerce(fs.get(name), widget.text()))
        self.refresh_report()

    @staticmethod
    def _coerce(field, text):
        """Turn editor text into the value the config expects.

        An empty box means "unset" and stores ``None``, which for the optional
        geometry fields is exactly the documented "read it from the instrument
        settings" state — not a zero.
        """
        text = text.strip()
        if text == "":
            return None
        if field.type == "int":
            try:
                return int(text)
            except ValueError:
                return text
        if field.type == "float":
            try:
                return float(text)
            except ValueError:
                return text
        return text

    def _on_cell_changed(self, row, column):
        """Write one per-angle value, to the row Qt says was edited.

        `row` comes from the signal — the cell that actually changed. Using
        `self.angle_table.currentRow()` here instead would be the active-row
        bug: with row 2 selected, editing row 0 would write to row 2.
        """
        if self._populating:
            return
        name = fs.PER_ANGLE_NAMES[column]
        item = self.angle_table.item(row, column)
        value = self._coerce(fs.get(name), item.text() if item is not None else "")
        self.document.set_angle_field(row, name, value)
        self.refresh_report()

    def add_angle(self):
        self.document.add_angle()
        self.refresh_angles()
        self.refresh_report()

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
        self.refresh_report()

    # -- refresh -----------------------------------------------------------

    def refresh_angles(self):
        self._populating = True
        try:
            self.angle_table.setRowCount(self.document.n_angles)
            for row in range(self.document.n_angles):
                values = self.document.angle_row(row)
                for column, name in enumerate(fs.PER_ANGLE_NAMES):
                    value = values[name]
                    self.angle_table.setItem(
                        row, column, QtWidgets.QTableWidgetItem("" if value is None else str(value))
                    )
        finally:
            self._populating = False

    def refresh_scalars(self):
        for name, editor in self.editors.items():
            value = self.document.get(name)
            was = editor.blockSignals(True)
            try:
                if isinstance(editor, QtWidgets.QCheckBox):
                    editor.setChecked(bool(value))
                elif isinstance(editor, QtWidgets.QComboBox):
                    if value is not None:
                        editor.setCurrentText(str(value))
                else:
                    editor.setText("" if value is None else str(value))
            finally:
                editor.blockSignals(was)

    def refresh_report(self):
        lines = []
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

    def load_settings(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load reduction settings",
            self.settings.value("settings_editor_dir", ""),
            "Settings (*.json *.dat);;All files (*)",
        )
        if not path:
            return
        try:
            self.document = SettingsDocument.from_file(path)
        except (ValueError, OSError) as exc:
            QtWidgets.QMessageBox.warning(self, "Could not load settings", str(exc))
            return
        self.settings.setValue("settings_editor_dir", str(Path(path).parent))
        self.refresh_angles()
        self.refresh_scalars()
        self.refresh_report()

    def save_settings(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save reduction settings",
            self.settings.value("settings_editor_dir", ""),
            "Settings (*.json);;All files (*)",
        )
        if not path:
            return
        try:
            self.document.save(path)
        except OSError as exc:
            QtWidgets.QMessageBox.warning(self, "Could not save settings", str(exc))
            return
        self.settings.setValue("settings_editor_dir", str(Path(path).parent))
