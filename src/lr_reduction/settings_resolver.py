"""Resolve every reduction setting from its layers, and say where it came from.

Reduction settings used to arrive from a muddle of sources with no defined
precedence and no record of which one won. This module gives that a taxonomy —
six layers in preference order — and a single resolver that walks them:

===== ================================================================
layer  source
===== ================================================================
``b``  pre-run override typed into the UI for this reduction
``c``  the IPTS ``reduce_settings*.json``
``d``  the IPTS ``template*.xml``
``a``  user-global preferences (the shared QSettings store)
``e``  guessed from the dataset itself
``f``  the built-in default in ``FIELD_SPEC``
===== ================================================================

The letters are the taxonomy's; the rows are in **resolution order**, which is
not alphabetical. A this-run override beats everything set earlier, the
experiment's own files beat a user-general preference (human decision,
2026-09-12), and a preference still beats a guess and the default. The
instrument-geometry fields have **no** layer (a) at all — see
``GLOBAL_EXCLUDED_GROUPS``.

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

import copy
import json
import os
import stat
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from lr_reduction import field_spec as fs
from lr_reduction.autoreduce_paths import select_by_geometry
from lr_reduction.save_reduced_data import make_json_safe
from lr_reduction.settings_document import SettingsDocument, atomic_write_json

#: Layers in preference order — **the single source of that order**.
#:
#: Note the scope: `_layer_sources` builds the mapping-backed layers from this
#: tuple, and (e)/(f) are the two that are not mappings — a probe and a
#: constant — so they are handled after the walk. They appear here because the
#: tuple is the taxonomy, and their position in it is asserted, but moving them
#: within it would not by itself move them: that is stated rather than left for
#: someone to discover, which is the standard the tuple's own comment sets.
#:
#: `resolve()`, `user_chosen()` and the fall-throughs all read this tuple. An
#: earlier version declared an order here and then hard-coded a separate walk
#: beside it, so reversing this changed nothing: a declaration that its
#: implementation ignores is worse than no declaration, because it is believed.
#:
#: The order is the human's decision of 2026-09-12, and each step has a reason:
#:
#: * **(b) this run** beats everything a person set earlier — an override that
#:   is overridden is not an override;
#: * **(c) experiment file** and **(d) experiment template** beat **(a) user
#:   preference**, because a setting that belongs to *this experiment* is more
#:   specific than one that belongs to *this person*;
#: * **(a)** still beats **(e) a guess from the data** and **(f) the default**
#:   for the fields it is allowed to cover.
LAYER_ORDER = ("b", "c", "d", "a", "e", "f")

#: Layers a *person* set deliberately, as opposed to inherited or derived.
HUMAN_LAYERS = ("a", "b")

#: Layers whose value a *person or a file they control* supplied, as opposed to
#: the instrument or the built-in defaults. The invariant below is expressed
#: against this set, so a future user-authority layer inherits the protection
#: instead of needing its own door closed.
USER_AUTHORITY_LAYERS = ("a", "b")


#: A value that was recorded as someone's run-level choice but is **not
#: authoritative now** — read from a sidecar written for a previous run, or
#: implied by a structural change rather than typed.
#:
#: It exists because three separate fixes composed into a science regression:
#: the sidecar read populated `provenance`, `_pre_resolve_overrides` turned a
#: recorded origin into authority, and `resolve()` gates only layer (a) on the
#: whitelist. So a geometry value — from the group excluded from (a) precisely
#: so *a preference can never override a measurement* — arrived at layer (b)
#: and outranked both the experiment file and the measurement, with nobody
#: typing anything. Marking it keeps the badge truthful without granting it
#: authority: it is displayed, and it never enters `ui_overrides`.
PREVIOUS_RUN_LAYER = "b*"

#: Layers `discover_ipts_settings` can populate today. (d) is declared in the
#: taxonomy and honoured by `resolve()` when a caller supplies `xml_settings`,
#: but nothing populates it automatically yet — mapping a template's vocabulary
#: onto config fields is `new_reduction_from_template.config_from_template`'s
#: job, and doing it here would either duplicate that mapping or pull Mantid
#: into the one module whose value is not needing it. Declared, not pretended:
#: a badge never shows [d] from discovery, and a test pins that.
DISCOVERY_LAYERS = ("c",)

#: What to call each layer in a provenance badge or a report.
LAYER_LABELS = {
    "a": "user preference",
    "b": "set for this run",
    "b*": "set for a previous run (not applied)",
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
    fs.DEADTIME,
    fs.RESOLUTION,
    fs.PEAK,
)

#: Excluded from the global layer by an explicit scientific decision
#: (human, 2026-09-12), not by omission.
#:
#: The instrument-geometry fields — `IncidentTheta`, `mmpix`, `dSampDet`,
#: `dMod`, `xi_ref`, `dS1Samp`, `nx`, `ny` — document their defaults as *"unset
#: reads it from the instrument settings / the PV"*. They are **measurements**.
#: A stored personal preference that outranked one would mean the same UI and
#: the same experiment file producing **different reduced data**, silently.
#:
#: So these fields have no layer (a) at all and resolve (b)->(c)->(d)->(e)->(f).
#: **A preference must never outrank a measurement.** Guarded by name, because
#: an exclusion that only exists as an absent group is an exclusion nobody can
#: see.
GLOBAL_EXCLUDED_GROUPS = (fs.GEOMETRY,)

#: Fields a user may set globally. Per-angle and runtime-owned fields are
#: excluded by construction — they describe one measurement, not a preference.
def _may_be_a_preference(field):
    """Is this field something a person can sensibly carry between experiments?

    Derived rather than listed, so a new field is covered without anyone
    remembering — but every clause is a rule someone can argue with:

    * its group must be one people hold preferences about, and must not be an
      excluded one (geometry: see GLOBAL_EXCLUDED_GROUPS);
    * per-angle and runtime-owned fields describe one measurement, not a person;
    * a path is never a preference — it names a location in one experiment;
    * free text is never a preference either, unless it is a closed choice.
      This keeps a future free-form field (a formula, say) out of the layer that
      outranks a dataset guess, without anyone having to notice it was added.
    """
    if field.group in GLOBAL_EXCLUDED_GROUPS:
        return False
    if field.group not in GLOBAL_GROUPS:
        return False
    if field.per_angle:
        return False
    if field.runtime_owned:
        return False
    if field.type == "path":
        return False
    if field.type == "str" and not field.allowed:
        return False
    return True


GLOBAL_WHITELIST = tuple(f.name for f in fs.FIELD_SPEC if _may_be_a_preference(f))


def _copy(value):
    """Return a value the caller may mutate without rewriting its source layer.

    The resolved document, the layer dict it came from, and the frozen
    `Resolved` were one object: editing a resolved setting rewrote the
    experiment file's in-memory copy, so the next `resolve()` returned the
    edit as though the file had said it. `Resolved` being frozen protects the
    binding, not the list behind it — the same distinction `Field.default_value`
    exists for, which is why layer (f) was already safe and only (f) was.
    """
    return copy.deepcopy(value)


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
        """A JSON-safe record of the ORIGIN. The value lives in the document.

        Storing the value here too meant two copies that could disagree — and
        they did: provenance was snapshotted before per-angle arrays were padded
        to equal length, so a file could carry 55 provenance values against 52
        settings. One fact, one place.
        """
        return {"source_layer": self.source_layer, "source_detail": self.source_detail}

    @classmethod
    def from_record(cls, record, value=None):
        """Rebuild from a stored record; ``value`` comes from the document."""
        return cls(
            value=value,
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
    #: The template discovery saw, if any. Reported, not parsed — see
    #: DISCOVERY_LAYERS for why layer (d) is declared but not populated.
    template_path: Optional[str] = None

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

    def _layer_sources(self, ctx):
        """The (layer, mapping, detail) triples, in the declared order.

        Built from LAYER_ORDER so there is exactly one place the order lives.
        (e) and (f) are not mappings and are handled after this walk.
        """
        available = {
            "a": (ctx.global_settings, ""),
            "b": (ctx.ui_overrides, ""),
            "c": (ctx.json_settings, ctx.json_detail),
            "d": (ctx.xml_settings, ctx.xml_detail),
        }
        return [
            (layer, *available[layer]) for layer in LAYER_ORDER if layer in available
        ]

    def resolve(self, name, context=None):
        """Return the :class:`Resolved` value of ``name``.

        One walk, in one place. The provenance badge later reads the very object
        produced here rather than re-deriving where a value came from — two
        implementations of "which layer won" would drift, and a badge that
        disagrees with the value beside it is worse than no badge.
        """
        ctx = context if context is not None else self.context
        field = fs.get(name)

        for layer, mapping, detail in self._layer_sources(ctx):
            # THE INVARIANT (human's science decision, 2026-09-15):
            #
            #     a field in an excluded group never resolves above layer (e)
            #     from a user-authority layer.
            #
            # Expressed once, over the whole class of user layers, because
            # closing doors one at a time did not hold. v4 closed two — a
            # sidecar seeding `ui_overrides`, and an "Add angle" click minting
            # authority — and a third would have been a third fix. Instrument
            # geometry comes from the instrument: `IncidentTheta`, `dSampDet`
            # and the rest document their defaults as read from the PV, so a
            # value a person or their file supplies must never outrank the
            # measurement. Identical UI and identical experiment file producing
            # different reduced data is the outcome this prevents.
            #
            # A deliberate per-run geometry override is a later, explicit,
            # badged feature. It is not something an edit does as a side effect.
            if layer in USER_AUTHORITY_LAYERS and field.group in GLOBAL_EXCLUDED_GROUPS:
                continue
            # The whitelist is enforced here, at the READER, as well as at both
            # writers. A ResolutionContext can be constructed directly with any
            # dict — a third door — so a whitelist checked only on the way in is
            # not a whitelist.
            if layer == "a" and name not in GLOBAL_WHITELIST:
                continue
            if name not in mapping:
                continue
            value = mapping[name]
            # `None` normally means "this layer does not set it". For the
            # optional lists it is a real value — LambdaMin unset means "derive
            # it from the chopper ranges" — so there the key's presence is what
            # counts, and an explicit null wins.
            if value is None and not field.optional_list:
                continue
            return Resolved(_copy(value), layer, detail)

        if ctx.dataset_probe is not None:
            guessed = ctx.dataset_probe(name)
            if guessed is not None:
                return Resolved(_copy(guessed), "e", ctx.dataset_detail)

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
        walked = {f.name: self.resolve(f.name, ctx) for f in fs.FIELD_SPEC}

        document = SettingsDocument()
        for name, resolved in walked.items():
            document.set(name, resolved.value)
        self._equalise_angles(document)
        # The resolved state is the baseline a later edit is measured against,
        # not itself an edit.
        document.reseed()

        # Provenance is recorded AFTER equalising, from the document's final
        # contents. Snapshotting it before meant the padded arrays and their
        # recorded values disagreed — 55 provenance entries against 52 settings.
        # Copied, not shared. Recording provenance FROM the document fixes the
        # length disagreement (C2b) but would hand back the document's own list
        # objects — so editing a resolved setting would silently rewrite the
        # snapshot that is supposed to describe what was resolved.
        provenance = {
            name: Resolved(_copy(document.get(name)), resolved.source_layer, resolved.source_detail)
            for name, resolved in walked.items()
        }
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


#: Refuse to parse a settings file larger than this. A deeply nested or
#: enormous JSON is a denial of the GUI thread, not a settings file.
MAX_SETTINGS_BYTES = 4 * 1024 * 1024


def _read_json(path):
    """Read a settings file, refusing the shapes that are not one.

    Three gates, each for a failure that has a name:

    * ``O_NOFOLLOW`` — the directory confinement validates the *directory*, and
      this used to ``open()`` whatever the name pointed at, so a symlink out of
      the facility root would be read while the badge reported the in-root
      filename. The write side has refused links since T2; reading through one
      is the same hole facing the other way, in the module whose product is
      truthful provenance.
    * ``O_NONBLOCK`` + ``S_ISREG`` — a FIFO reports ``st_size == 0``, so the size
      cap waves it through, and a blocking ``open()`` on one with no writer
      **waits forever** — on the discovery worker, the thread that exists so the
      GUI does not block. ``O_NONBLOCK`` makes the open itself return rather
      than wait; the rejection is then done by ``S_ISREG`` on the already-open
      descriptor, which also covers directories, devices and sockets. (Measured:
      ``O_RDONLY|O_NONBLOCK`` on a writer-less FIFO *succeeds* — ``ENXIO`` is the
      write-side behaviour — so the non-blocking flag is what avoids the wait
      and ``S_ISREG`` is what refuses the file.) The flag is cleared once the
      type is known, so the read itself behaves normally.
    * a size cap and an object check, so an enormous file or a top-level list
      cannot become a ``TypeError`` several layers away from the file.
    """
    path = Path(path)
    handle_fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(handle_fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"{path.name} is not a regular file")
        if info.st_size > MAX_SETTINGS_BYTES:
            raise ValueError(
                f"{path.name} is {info.st_size} bytes; refusing to parse more "
                f"than {MAX_SETTINGS_BYTES}"
            )
        # Checked as a regular file, so blocking reads are safe again.
        os.set_blocking(handle_fd, True)
        with os.fdopen(handle_fd, "r") as handle:
            handle_fd = None
            payload = json.load(handle)
    finally:
        if handle_fd is not None:
            os.close(handle_fd)
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} holds a {type(payload).__name__}, not an object")
    return payload


#: Returned by :func:`_guarded_step` when the step *failed*, as opposed to
#: succeeding and finding nothing. The two were both ``None``, so after a
#: permission-denied share the caller appended "no reduce_settings*.json" as the
#: last word — a persistent falsehood the scientist then acts on, reducing from
#: defaults while believing the experiment simply had no settings file.
_FAILED = object()


def _guarded_step(notes, description, action):
    """Run one filesystem step; record the failure instead of raising.

    **One guard, every step.** Discovery previously wrapped two of its three
    filesystem touches and left the third bare, so the module's headline promise
    — never take the launcher down when the mount is unavailable, and record why
    — was not delivered for the one that mattered.

    **The exception set is wider than OSError, because the filesystem is.**
    ``Path.resolve()`` raises ``RuntimeError`` on a symlink loop (ELOOP), which
    an sshfs ``/SNS`` tree produces without anyone doing anything unusual;
    ``ValueError`` on a NUL byte in a name; ``TypeError`` on a non-path. Catching
    only ``OSError`` meant the launcher survived solely because
    ``_DiscoveryWorker.run`` catches ``BaseException`` — every non-GUI caller,
    including a script, got the raise.

    Returns ``_FAILED`` on error so the caller can tell "I could not look" from
    "I looked and there was nothing".
    """
    try:
        return action()
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        notes.append(f"{description}: {type(exc).__name__}: {exc}")
        return _FAILED


def discover_ipts_settings(ipts, tthd=1.0, root="/SNS/REF_L", context=None):
    """Arm the experiment layers from an IPTS autoreduce directory.

    Read-only and failure-tolerant by design: the mount may be down or
    permission-denied, the IPTS may not exist, and the files may be unreadable,
    malformed, enormous, deeply nested or not objects at all. Every one is an
    ordinary day at a facility and none is a reason to take the launcher down —
    they leave the layers empty, record the reason in ``discovery_status``, and
    let resolution continue from the layers that are available.

    **Never raises. It can still block**, if the mount is stalled rather than
    absent — a D-state read does not raise, and no `except` reaches it. Callers
    on a GUI thread must not call this synchronously; `SettingsEditorTab` runs
    it on a worker.

    Only layer (c) is populated; see ``DISCOVERY_LAYERS`` for why (d) is
    declared but not filled.
    """
    ctx = context if context is not None else ResolutionContext()
    ctx.ipts = ipts
    notes = []

    resolved_root = _guarded_step(notes, "could not resolve the facility root", lambda: Path(root).resolve())
    if resolved_root is _FAILED:
        ctx.discovery_status = "; ".join(notes)
        return ctx

    directory = _guarded_step(
        notes,
        "could not resolve the experiment directory",
        lambda: (resolved_root / str(ipts) / "shared" / "autoreduce").resolve(),
    )
    if directory is _FAILED:
        ctx.discovery_status = "; ".join(notes)
        return ctx

    # An IPTS carrying "/" or ".." would otherwise walk out of the facility root.
    if not directory.is_relative_to(resolved_root):
        ctx.discovery_status = f"{ipts!r} does not name a directory under {resolved_root}"
        return ctx

    reachable = _guarded_step(notes, f"could not reach {directory}", directory.is_dir)
    if reachable is _FAILED:
        ctx.discovery_status = "; ".join(notes)
        return ctx
    if not reachable:
        ctx.discovery_status = f"no autoreduce directory at {directory}"
        return ctx

    # Layer (c). The up/down rule comes from lr_reduction.autoreduce_paths, the
    # one place it lives — the same function template.py and the autoreduction
    # use.
    settings_path = _guarded_step(
        notes,
        "settings scan failed",
        lambda: select_by_geometry(directory, "reduce_settings", ".json", tthd),
    )
    if settings_path is _FAILED:
        # The scan itself failed; the note already says why. Adding "no
        # reduce_settings*.json" here would overwrite a real error with a
        # confident, false statement of absence.
        pass
    elif settings_path is None:
        notes.append("no reduce_settings*.json")
    else:
        try:
            ctx.json_settings = _read_json(settings_path)
            ctx.json_detail = Path(settings_path).name
            notes.append(f"settings from {ctx.json_detail}")
        except (OSError, ValueError, RecursionError) as exc:
            # ValueError covers json.JSONDecodeError (a subclass), the size cap
            # and the not-an-object check; RecursionError is what deeply nested
            # JSON raises and is not a path anyone expects until it happens.
            notes.append(f"settings file unreadable: {exc}")

    # Layer (d): reported, not consumed.
    template_path = _guarded_step(
        notes,
        "template scan failed",
        lambda: select_by_geometry(directory, "template", ".xml", tthd),
    )
    if template_path is _FAILED:
        pass
    elif template_path is None:
        notes.append("no template*.xml")
    else:
        ctx.template_path = template_path
        notes.append(f"template {Path(template_path).name} present (layer (d) not consumed)")

    ctx.discovery_status = "; ".join(notes)
    return ctx


#: Suffix of the sidecar file holding origins for a settings file.
PROVENANCE_SUFFIX = ".provenance.json"


def provenance_path(path):
    """Sidecar holding the origins for ``path``."""
    path = Path(path)
    return path.with_name(path.stem + PROVENANCE_SUFFIX)


def save_resolution(path, document, provenance):
    """Write the settings, and their origins beside them.

    **Two files, deliberately.** Provenance used to be written into the settings
    JSON under a `_provenance` key, and `json_to_config` raises `AttributeError`
    on any key that is not a config field — so a file written that way and
    dropped into `shared/autoreduce` as `reduce_settings*.json` would **stop
    autoreduction for that experiment**. The "one file" convenience was not
    worth a facility outage, and the alternative — teaching the reduction's
    loader to skip the key — changes code the facility runs to suit a
    convenience of the editor's.

    So the settings file stays exactly what every existing reader expects, and
    the origins live in a sidecar that only this module reads. Both are written
    through the same atomic helper the editor uses.
    """
    path = Path(path)
    # Sidecar FIRST. The pair is not atomic, so if the second write fails the
    # first has already landed — and a saved settings file beside a stale
    # sidecar is worse than a settings file with none, because the badge then
    # attributes values to a resolution that never produced them.
    atomic_write_json(
        provenance_path(path),
        {name: resolved.as_record() for name, resolved in provenance.items()},
    )
    atomic_write_json(path, make_json_safe(document.to_dict()))
    return path


def load_resolution(path):
    """Read back ``(settings, provenance)`` written by :func:`save_resolution`.

    A settings file with no sidecar loads with an empty provenance map rather
    than failing — the facility has files that predate this module, and refusing
    them would make the resolver useless exactly where it is most needed.
    """
    # Through _read_json, not a bare open(): this is the production Open path,
    # and it was the unhardened twin of the discovery read — same FIFO, symlink
    # and not-an-object exposure, on a file a user picks from a dialog.
    settings = _read_json(path)

    sidecar = provenance_path(path)
    provenance = {}
    if sidecar.exists():
        records = _read_json(sidecar)
        provenance = {
            name: Resolved.from_record(record, settings.get(name))
            for name, record in records.items()
        }
    return settings, provenance


def user_chosen(provenance):
    """Names whose value a person actually chose — layers (a) and (b).

    The rest fell through to an experiment file, a guess, or a default. This is
    the distinction a reduction record needs and could not previously make.
    """
    return tuple(
        name for name, resolved in provenance.items() if resolved.source_layer in HUMAN_LAYERS
    )
