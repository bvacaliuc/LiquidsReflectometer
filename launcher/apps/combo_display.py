#!/usr/bin/python3
"""Showing a value in a QComboBox without silently changing it.

`QComboBox.setCurrentText` is a **no-op** on a non-editable combo when the text
is not one of the items. That is the whole reason this exists: a stored value
the combo does not offer — a spelling from an older version, say — displays as
whatever was already selected, so the widget and the document disagree with no
sign. In the global-settings dialog the consequence was worse than cosmetic: the
value showed blank, and a Save the user never touched coerced the blank to
``None`` and **deleted the preference**.

Extracted rather than copied. The settings tab had this logic and the dialog,
written later, grew a plain `setCurrentText` instead — the same recurrence that
made `render_value` a module function. A fix living in a private method of a Qt
widget is a fix the next widget cannot have.
"""


def show_in_combo(editor, field, value, blank_first=False):
    """Display ``value`` in ``editor``, even when it is not one of the choices.

    A stray value is added as an entry so what is shown equals what is held;
    validation is what reports it as a problem. Nothing is silently substituted,
    and nothing is silently dropped.

    ``blank_first`` says the combo carries a leading empty entry meaning "unset"
    — true for a preference dialog, where blank means "let a later layer
    decide", and for the tri-state fields in the settings tab.
    """
    if value is None or value is False or value == "":
        editor.setCurrentIndex(0 if (blank_first or field.falsy_means_off) else -1)
        return
    text = str(value)
    if editor.findText(text) < 0:
        editor.addItem(text)
    editor.setCurrentText(text)
