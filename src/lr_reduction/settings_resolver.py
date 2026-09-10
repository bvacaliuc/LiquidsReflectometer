"""Resolve every reduction setting from its layers, and say where it came from.

Reduction settings used to arrive from a muddle of sources with no defined
precedence and no record of which one won. This module gives that a taxonomy —
six layers in preference order — and a single resolver that walks them:

===== ================================================================
layer  source
===== ================================================================
``a``  user-global preferences (the shared QSettings store)
``b``  pre-run override typed into the UI for this reduction
``c``  the IPTS ``reduce_settings*.json``
``d``  the IPTS ``template*.xml``
``e``  guessed from the dataset itself
``f``  the built-in default in ``FIELD_SPEC``
===== ================================================================

**Every resolved value carries its origin.** ``resolve()`` returns a
:class:`Resolved`, never a bare value, because a value with no recorded origin
is exactly the condition this slug exists to end: when two layers hold the same
number, the value alone cannot tell you which one is in force, and a settings
file that looks right can be right for the wrong reason.

**Qt-free**, like :mod:`lr_reduction.settings_document` and
:mod:`lr_reduction.field_spec` — a script or a test imports the resolver without
pulling in a GUI toolkit, and a subprocess test asserts it rather than trusting
an import-grep, which a transitive import defeats.

**Discovery degrades, never raises.** ``/SNS/REF_L`` is read-only and may be
down; a resolver that raised when the mount was unavailable would take the
launcher with it. A failed scan leaves layers (c)/(d) empty, records why in
``ResolutionContext.discovery_status``, and resolution continues from the layers
that are available.
"""

import json
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from lr_reduction import field_spec as fs
from lr_reduction.settings_document import SettingsDocument

#: Layers in preference order. First one holding a value wins.
LAYERS = ("a", "b", "c", "d", "e", "f")

#: What to call each layer in a provenance badge or a report.
LAYER_LABELS = {
    "a": "user preference",
    "b": "set for this run",
    "c": "experiment settings file",
    "d": "experiment template",
    "e": "measured from the data",
    "f": "built-in default",
}

#: Groups whose scalar fields a user may set as a personal default.
#:
#: Chosen by group rather than listed by name so the whitelist cannot drift from
#: FIELD_SPEC: a new field in one of these groups is covered automatically, and
#: a new group is excluded until someone decides otherwise. Naming, paths and
#: run identity are excluded because they belong to an experiment, not a person.
GLOBAL_GROUPS = (
    fs.PROCESSING,
    fs.QSPACE,
    fs.WAVELENGTH,
    fs.GEOMETRY,
    fs.DEADTIME,
    fs.RESOLUTION,
    fs.PEAK,
)

#: Fields a user may set globally. Per-angle and runtime-owned fields are
#: excluded by construction — they describe one measurement, not a preference.
GLOBAL_WHITELIST = tuple(
    f.name
    for f in fs.FIELD_SPEC
    if f.group in GLOBAL_GROUPS and not f.per_angle and not f.runtime_owned
)


class NotWhitelistedError(ValueError):
    """Raised when a field that is not a personal preference is set globally."""


@dataclass(frozen=True)
class Resolved:
    """One resolved value and where it came from."""

    value: Any
    source_layer: str
    source_detail: str = ""

    @property
    def label(self):
        """Human-facing origin, for a provenance badge."""
        base = LAYER_LABELS.get(self.source_layer, self.source_layer)
        return f"{base} ({self.source_detail})" if self.source_detail else base

    def as_record(self):
        """A JSON-safe record, so provenance survives being saved and reloaded."""
        return {
            "value": self.value,
            "source_layer": self.source_layer,
            "source_detail": self.source_detail,
        }

    @classmethod
    def from_record(cls, record):
        return cls(
            value=record["value"],
            source_layer=record["source_layer"],
            source_detail=record.get("source_detail", ""),
        )


@dataclass
class ResolutionContext:
    """Everything the resolver needs, with each layer kept separate.

    The layers stay distinct all the way through: merging them early is how the
    origin gets lost, which is the defect this module addresses.
    """

    ipts: Optional[str] = None
    runs: Tuple[int, ...] = ()
    global_settings: Dict[str, Any] = dataclass_field(default_factory=dict)
    ui_overrides: Dict[str, Any] = dataclass_field(default_factory=dict)
    json_settings: Dict[str, Any] = dataclass_field(default_factory=dict)
    json_detail: str = ""
    xml_settings: Dict[str, Any] = dataclass_field(default_factory=dict)
    xml_detail: str = ""
    #: Layer (e). Called only when layers (a)-(d) all miss, so an expensive
    #: dataset analysis is never paid for a field somebody already set.
    dataset_probe: Optional[Callable[[str], Any]] = None
    dataset_detail: str = "dataset"
    #: Why discovery found what it found — including "the mount was unavailable".
    discovery_status: str = "not attempted"

    def set_global(self, name, value):
        """Set a user-global preference, refusing anything outside the whitelist."""
        if name not in GLOBAL_WHITELIST:
            raise NotWhitelistedError(
                f"{name} is not a user-global preference — it belongs to one "
                f"experiment or one measurement, not to a person"
            )
        self.global_settings[name] = value


class SettingsResolver:
    """Walks the layers for one field, or for every field."""

    def __init__(self, context=None):
        self.context = context if context is not None else ResolutionContext()

    # -- one field ---------------------------------------------------------

    def resolve(self, name, context=None):
        """Return the :class:`Resolved` value of ``name``.

        One walk, in one place. The provenance badge later reads the very
        object produced here rather than re-deriving where a value came from —
        two implementations of "which layer won" would drift, and a badge that
        disagrees with the value is worse than no badge.
        """
        ctx = context if context is not None else self.context
        field = fs.get(name)

        for layer, mapping, detail in (
            # (a) and (b) carry no detail: LAYER_LABELS already names them,
            # and a detail that repeats the label renders as
            # "user preference (user preference)" on a badge.
            ("a", ctx.global_settings, ""),
            ("b", ctx.ui_overrides, ""),
            ("c", ctx.json_settings, ctx.json_detail),
            ("d", ctx.xml_settings, ctx.xml_detail),
        ):
            if name in mapping and mapping[name] is not None:
                return Resolved(mapping[name], layer, detail)

        if ctx.dataset_probe is not None:
            guessed = ctx.dataset_probe(name)
            if guessed is not None:
                return Resolved(guessed, "e", ctx.dataset_detail)

        return Resolved(field.default_value(), "f", "")

    # -- every field -------------------------------------------------------

    def resolve_all(self, context=None):
        """Resolve every field.

        Returns ``(document, provenance)`` — a
        :class:`~lr_reduction.settings_document.SettingsDocument` carrying the
        values, and ``{name: Resolved}`` carrying their origins. The document is
        what the reduction consumes; the provenance is what the editor displays,
        and they are produced together from one walk so they cannot disagree.
        """
        ctx = context if context is not None else self.context
        provenance = {f.name: self.resolve(f.name, ctx) for f in fs.FIELD_SPEC}

        document = SettingsDocument()
        for name, resolved in provenance.items():
            document.set(name, resolved.value)
        self._equalise_angles(document)
        return document, provenance

    @staticmethod
    def _equalise_angles(document):
        """Pad every per-angle array to the longest one.

        Layers resolve independently, so one may supply three angles' worth of
        `DBname` while another supplies two of `RB_Ymin`. A short array does not
        fail — it silently shifts every later angle's settings by one, which is
        the defect the editor's `add_angle` was built to prevent and which the
        resolver could otherwise reintroduce one layer at a time.
        """
        length = document.n_angles
        for name in fs.PER_ANGLE_NAMES:
            current = document.get(name)
            if not isinstance(current, list) or len(current) >= length:
                continue
            document.set(name, list(current) + [None] * (length - len(current)))


# -- discovery -------------------------------------------------------------


def _read_json(path):
    with open(path, "r") as handle:
        return json.load(handle)


def discover_ipts_settings(ipts, tthd=1.0, root="/SNS/REF_L", context=None):
    """Arm layers (c) and (d) from an experiment's autoreduce directory.

    Read-only and failure-tolerant by design: the mount may be down, the IPTS
    may not exist, and the files may be unreadable or malformed. Every one of
    those is an ordinary Tuesday at a facility, and none of them is a reason to
    stop the launcher — they leave the layers empty and the reason recorded.
    """
    ctx = context if context is not None else ResolutionContext()
    ctx.ipts = ipts
    directory = Path(root) / str(ipts) / "shared" / "autoreduce"

    try:
        if not directory.is_dir():
            ctx.discovery_status = f"no autoreduce directory at {directory}"
            return ctx
    except OSError as exc:  # a stalled or absent mount answers with an error
        ctx.discovery_status = f"could not reach {directory}: {exc}"
        return ctx

    notes = []

    # Layer (c). The up/down choice is the autoreduction's own helper rather
    # than a second copy of the rule — imported lazily because that module
    # pulls in Mantid, which this one otherwise does not need.
    try:
        from lr_autoreduce.new_reduce_REF_L import get_default_setting_file

        settings_path = get_default_setting_file(str(directory), tthd)
        ctx.json_settings = _read_json(settings_path)
        ctx.json_detail = Path(settings_path).name
        notes.append(f"settings from {ctx.json_detail}")
    except (OSError, json.JSONDecodeError) as exc:
        # BEFORE the ValueError clause: JSONDecodeError subclasses ValueError,
        # so the broader clause below would catch a malformed file and label it
        # "no settings file found", which is a different and misleading fact.
        notes.append(f"settings file unreadable: {exc}")
    except ValueError as exc:
        # The helper raises when neither file exists. For autoreduction that is
        # fatal; for the editor it just means layer (c) is inactive.
        notes.append(str(exc))

    # Layer (d).
    try:
        templates = sorted(directory.glob("template*.xml"))
        if templates:
            ctx.xml_settings = {}
            ctx.xml_detail = templates[0].name
            notes.append(f"template {ctx.xml_detail} present")
        else:
            notes.append("no template*.xml")
    except OSError as exc:
        notes.append(f"template scan failed: {exc}")

    ctx.discovery_status = "; ".join(notes)
    return ctx


#: Key the provenance is stored under, alongside the settings themselves.
PROVENANCE_KEY = "_provenance"


def save_resolution(path, document, provenance):
    """Write settings and their origins together, atomically.

    One file, because provenance kept somewhere else stops being updated. The
    write uses the same discipline as :meth:`SettingsDocument.save` — temp file
    in the target directory, fsync, ``os.replace`` — so an interrupted write
    cannot destroy the previous good settings.

    The origins are what let a later reload answer "did a person choose this, or
    did it fall through to a default?" — the question a reduction record could
    not answer before.
    """
    path = Path(path)
    payload = dict(document.normalize())
    payload[PROVENANCE_KEY] = {
        name: resolved.as_record() for name, resolved in provenance.items()
    }
    _atomic_write_json(path, payload)
    return path


def _atomic_write_json(path, payload):
    """Same discipline as SettingsDocument.save: temp file, fsync, replace."""
    import os
    import tempfile

    path = Path(path)
    handle_fd, temporary = tempfile.mkstemp(
        dir=str(path.parent), prefix=path.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(handle_fd, "w") as handle:
            json.dump(payload, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def load_resolution(path):
    """Read back ``(settings, provenance)`` written by :func:`save_resolution`.

    A file without provenance loads with an empty map rather than failing — the
    facility has settings files that predate this module, and refusing to read
    them would make the resolver useless exactly where it is most needed.
    """
    with open(path, "r") as handle:
        stored = json.load(handle)
    records = stored.pop(PROVENANCE_KEY, {})
    provenance = {name: Resolved.from_record(r) for name, r in records.items()}
    return stored, provenance


def user_chosen(provenance):
    """Names whose value a person actually chose — layers (a) and (b).

    The rest fell through to an experiment file, a guess, or a default. This is
    the distinction a reduction record needs and could not previously make.
    """
    return tuple(
        name for name, resolved in provenance.items() if resolved.source_layer in ("a", "b")
    )
