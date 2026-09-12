#!/usr/bin/python3
"""User-global reduction preferences: the (a) layer, and the dialog that edits it.

Layer (a) of :mod:`lr_reduction.settings_resolver` — the settings a person
carries between experiments, as distinct from the ones an experiment carries
between people. Persisted to the launcher's shared QSettings store through
:mod:`launcher.app_identity`, so every layer of the application resolves to the
same file (the S3 contract).

The editable set is `settings_resolver.GLOBAL_WHITELIST`, derived from
FIELD_SPEC by group rather than hand-listed, so a new field is covered without
anyone remembering to add it. Per-angle and runtime-owned fields are excluded by
construction: they describe one measurement, not a preference.

Values round-trip through `Field.coerce`, the same coercion the editor uses.
QSettings hands back strings under the Ini format, so a bare read would turn
`plotON = False` into the string `"False"` — which is truthy, and would switch
plotting on for someone who had turned it off. That is the identical defect T2
was rejected for, arriving through a different door.
"""

from qtpy import QtCore, QtGui, QtWidgets

from launcher.app_identity import ensure_identity
from launcher.apps.combo_display import show_in_combo
from lr_reduction import field_spec as fs
from lr_reduction.settings_resolver import GLOBAL_WHITELIST, NotWhitelistedError

#: QSettings group holding the (a) layer.
SETTINGS_GROUP = "global_reduction_settings"


def load_global_settings():
    """Read the (a) layer, coerced back to the declared types.

    Only whitelisted names are returned even if the store holds others, so a
    stale key from an older version cannot re-enter the resolver as a
    preference.
    """
    ensure_identity()
    settings = QtCore.QSettings()
    settings.beginGroup(SETTINGS_GROUP)
    try:
        values = {}
        for name in GLOBAL_WHITELIST:
            if not settings.contains(name):
                continue
            stored = settings.value(name)
            if stored is None or stored == "":
                continue
            # Coerce UNCONDITIONALLY. QSettings hands a single value back as a
            # str after a restart and a multi-entry one back as a LIST of str —
            # and the earlier `if isinstance(stored, str)` guard covered only the
            # first, so a list-valued preference entered layer (a) as strings and
            # was written into the settings file, where the reduction did
            # arithmetic on them. No whitelisted field is list-typed today, but
            # the whitelist is derived: `_may_be_a_preference` admits any new
            # field in an included group and does not exclude lists.
            field = fs.get(name)
            if isinstance(stored, (list, tuple)):
                values[name] = [field.coerce_element(entry) for entry in stored]
            else:
                values[name] = field.coerce(stored)
        return values
    finally:
        settings.endGroup()


def save_global_settings(values):
    """Write the (a) layer, refusing anything outside the whitelist.

    The check is here as well as in `ResolutionContext.set_global` because this
    is the other door into the layer; a whitelist enforced on one path only is
    not a whitelist.
    """
    outside = sorted(set(values) - set(GLOBAL_WHITELIST))
    if outside:
        raise NotWhitelistedError(
            f"not user-global preferences: {', '.join(outside)} — these belong "
            f"to one experiment or one measurement"
        )
    ensure_identity()
    settings = QtCore.QSettings()
    settings.beginGroup(SETTINGS_GROUP)
    try:
        for name in GLOBAL_WHITELIST:
            if name in values and values[name] is not None:
                settings.setValue(name, values[name])
            else:
                settings.remove(name)
    finally:
        settings.endGroup()
    settings.sync()


class GlobalSettingsDialog(QtWidgets.QDialog):
    """Edit the user-global preferences."""

    def __init__(self, parent=None):
        ensure_identity()
        super().__init__(parent)
        self.setWindowTitle("Global reduction settings")
        self.editors = {}

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        explanation = QtWidgets.QLabel(
            "Your personal defaults. A value here is used unless this run or "
            "the experiment's own settings file provides one — it does outrank "
            "anything measured from the data and the built-in default. Leave a "
            "field blank to let those decide.\n\n"
            "Instrument geometry is deliberately not listed: those values come "
            "from the instrument, and a preference must never override a "
            "measurement."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QtWidgets.QWidget()
        column = QtWidgets.QVBoxLayout()
        inner.setLayout(column)

        stored = load_global_settings()
        for group in fs.GROUPS:
            names = [f.name for f in fs.fields_in(group) if f.name in GLOBAL_WHITELIST]
            if not names:
                continue
            box = QtWidgets.QGroupBox(group)
            form = QtWidgets.QFormLayout()
            box.setLayout(form)
            for name in names:
                field = fs.get(name)
                editor = self._build_editor(field, stored.get(name))
                editor.setToolTip(f"{field.name} — {field.help}")
                self.editors[name] = editor
                form.addRow(field.label, editor)
            column.addWidget(box)
        column.addStretch(1)
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _build_editor(field, value):
        """A tri-state editor: unset means "let a later layer decide".

        A checkbox cannot express "unset", so a boolean preference is a combo
        with a blank entry. Without it, opening the dialog once would set every
        boolean to False and silently outrank every experiment file.
        """
        if field.type == "bool" or field.allowed:
            editor = QtWidgets.QComboBox()
            editor.addItem("")
            choices = ("true", "false") if field.type == "bool" else field.allowed
            editor.addItems([str(c) for c in choices])
            # show_in_combo, not setCurrentText: the latter is a silent no-op on
            # a non-editable combo, so a stored value from an older version
            # ("DetResFn: bogus") displayed blank — and a Save the user never
            # touched then coerced "" to None and DELETED the preference. The
            # shared helper adds the stray value so what is shown is what is
            # held, and validation reports it.
            shown = str(value).lower() if field.type == "bool" and value is not None else value
            show_in_combo(editor, field, shown, blank_first=True)
            return editor
        # The shared renderer, not str(): str([50, 200]) is "[50, 200]", which
        # coerce reads back as the strings '[50' and '200]'. T2 fixed this in
        # the settings tab; the fix lived in a private method, so this file grew
        # the bug again.
        editor = QtWidgets.QLineEdit(fs.render_value(value))
        if field.type in ("int", "float"):
            editor.setValidator(
                QtGui.QIntValidator() if field.type == "int" else QtGui.QDoubleValidator()
            )
        return editor

    def values(self):
        """The dialog's contents, coerced, with blanks omitted."""
        values = {}
        for name, editor in self.editors.items():
            text = (
                editor.currentText()
                if isinstance(editor, QtWidgets.QComboBox)
                else editor.text()
            )
            coerced = fs.get(name).coerce(text)
            if coerced is not None:
                values[name] = coerced
        return values

    def accept(self):
        """Validate, save, and never let an exception leave the slot.

        A raise here reaches qFatal() and takes the whole launcher down. And a
        preference is the layer that outranks a dataset guess and the built-in
        default, so an unvalidated one — `qmax='abc'`, `dead_time=-5.0` — would
        persist and outrank a measurement for every future experiment.
        """
        try:
            values = self.values()
            problems = [
                problem
                for problem in (fs.get(name).check(value) for name, value in values.items())
                if problem
            ]
            if problems:
                QtWidgets.QMessageBox.warning(
                    self, "Cannot save", "\n".join(problems)
                )
                return
            save_global_settings(values)
        except Exception as exc:  # noqa: BLE001 -- a slot must not abort the process
            QtWidgets.QMessageBox.warning(self, "Cannot save", str(exc))
            return
        super().accept()
