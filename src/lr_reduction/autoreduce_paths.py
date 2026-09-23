"""Picking the up/down variant of an autoreduce file, in one place.

The reduction and the autoreduction each carried their own copy of the same
rule — ``<stem>_up`` when the detector is above the sample, ``<stem>_down``
otherwise, falling back to an unsuffixed file — for templates and for settings
respectively. Two copies of one rule drift; a third, written from memory in
:mod:`lr_reduction.settings_resolver`, already had: it took
``sorted(glob("template*.xml"))[0]``, so ``template_down.xml`` won every time,
including for an up-geometry run.

**Stdlib only, on purpose.** The callers of this rule live in modules that
import Mantid, so borrowing the rule used to mean importing Mantid — 2.6 s and
a network version check — to make a filename decision. Discovery in a
Mantid-free launcher could not afford that, and paid for it with a copy.
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
