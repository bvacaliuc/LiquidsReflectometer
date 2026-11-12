"""Picking the up/down variant of an autoreduce file, in one place.

The rule: ``<stem>_up`` when the detector is above the sample, ``<stem>_down``
otherwise, falling back to an unsuffixed file. The autoreduction holds it twice
(``get_default_template_file`` and ``get_default_setting_file`` of
``lr_autoreduce.new_reduce_REF_L``), and both live in a module that imports
Mantid: borrowing the rule from there means importing Mantid to make a filename
decision, which a Mantid-free launcher cannot afford. This is the rule alone,
for the settings resolver (``launcher.model.settings_resolver``); moving the
autoreduction's two copies onto it is a change to code the facility runs and is
not made here.

**Stdlib only, on purpose.**
"""

from pathlib import Path

#: Suffixes tried in order, before the unsuffixed fallback.
UP = "_up"
DOWN = "_down"


def select_by_geometry(directory, stem, suffix, tthd):
    """Return the ``stem`` file in ``directory`` matching the detector geometry.

    ``tthd`` above zero selects ``<stem>_up<suffix>``, otherwise
    ``<stem>_down<suffix>``; an unsuffixed ``<stem><suffix>`` is the fallback.
    Returns ``None`` when nothing matches — the caller decides whether that is
    fatal, because it is for autoreduction and merely a missing layer for the
    settings editor.
    """
    directory = Path(directory)
    variant = directory / f"{stem}{UP if tthd > 0 else DOWN}{suffix}"
    if variant.exists():
        return str(variant)
    fallback = directory / f"{stem}{suffix}"
    if fallback.exists():
        return str(fallback)
    return None
