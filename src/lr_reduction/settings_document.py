"""The editable settings model behind the settings-editor tab (T2).

Wraps one :class:`~lr_reduction.nr_reduction_config.NRReductionConfig` and the
operations an editor needs: seed it from a JSON settings file, a pre-reduced
``.dat`` header, or defaults; add and remove angles; validate against
:mod:`lr_reduction.field_spec`; report what changed; and normalize for handing
back to the reduction.

**Qt-free on purpose** — see the note in :mod:`lr_reduction.field_spec`. The
view is a thin layer over this class, so nearly all of the editor's behaviour
is testable without a display.

Two design points worth stating, because both differ from the obvious reading:

*Angles grow together.* ``add_angle`` mutates **every** per-angle field in one
operation. Growing only the obvious ones leaves the others short, and a short
array shifts every subsequent angle's settings by one — silently, since nothing
in the config class enforces equal lengths.

*Validation is not the same as the equal-length invariant.* The reducer
deliberately broadcasts a single ``method_per_run`` entry across all angles
(``nr_reduction_calc.py:76-78``) and defaults an empty one to ``meanTheta``
(``:41-42``). A validator that demanded strict equal lengths everywhere would
reject configurations the reducer accepts, so the broadcastable cases are
exempted here rather than "fixed".
"""

import copy
import json
from pathlib import Path

from lr_reduction import field_spec as fs
from lr_reduction.new_reduction_from_file import json_to_config, load_from_file
from lr_reduction.nr_reduction_config import NRReductionConfig
from lr_reduction.save_reduced_data import make_json_safe


class SettingsDocument:
    """One editable reduction configuration."""

    def __init__(self, config=None):
        self._config = config if config is not None else NRReductionConfig()
        # The state this document was seeded from, for changed_vs_seed(). Copied
        # so later edits cannot reach back and rewrite the baseline.
        self._seed = copy.deepcopy(self._config.__dict__)

    # -- construction ------------------------------------------------------

    @classmethod
    def from_dict(cls, values):
        """Build from a settings mapping, reporting an unknown key by name.

        ``json_to_config`` raises a bare ``AttributeError`` naming the key; it
        is re-raised as ``ValueError`` because from the editor's point of view
        this is a bad *file*, not a programming error, and the message has to
        reach the scientist.
        """
        try:
            config = json_to_config(values)
        except AttributeError as exc:
            raise ValueError(f"Not a valid reduction setting: {exc}") from exc
        return cls(config)

    @classmethod
    def from_file(cls, path):
        """Seed from a ``.json`` settings file or a pre-reduced ``.dat`` header.

        Both are read through the existing ``load_from_file`` rather than
        reimplemented here: the ``.dat`` seed is the ``# Config:`` header line
        the reduction itself writes, and duplicating that parser is how the two
        would drift apart.
        """
        loaded = load_from_file(Path(path))
        values = loaded.get("config")
        if values is None:
            raise ValueError(f"No reduction settings found in {path}")
        return cls.from_dict(values)

    # -- scalar access -----------------------------------------------------

    @property
    def config(self):
        """The wrapped config. The reduction takes this object."""
        return self._config

    def get(self, name):
        return getattr(self._config, fs.get(name).name)

    def set(self, name, value):
        """Set a field. Unknown names raise rather than being silently stored."""
        setattr(self._config, fs.get(name).name, value)

    def to_dict(self):
        """The document's in-memory state, as a plain dict."""
        return dict(self._config.__dict__)

    # -- angles ------------------------------------------------------------

    @property
    def n_angles(self):
        """Number of angles, taken as the longest per-angle field."""
        lengths = [
            len(self.get(name))
            for name in fs.PER_ANGLE_NAMES
            if isinstance(self.get(name), list)
        ]
        return max(lengths) if lengths else 0

    def add_angle(self, **values):
        """Append one angle, growing every per-angle field together.

        Unsupplied entries are ``None`` — "not filled in yet", which an editor
        must be able to represent. The exception is the optional lists
        (``LambdaMin``/``LambdaMax``): while they are ``None`` the whole field
        means "derive it from the chopper ranges"
        (``nr_reduction_calc.py:381-383``), which is a valid configuration, not
        a missing one. Materialising them into ``[None, None]`` on the first add
        would turn that into a list that reports a length but carries no values
        — and ``web_report.py:547`` indexes it. So they are left alone until a
        value is actually supplied, at which point the list is created at full
        length and ``validate()`` reports the angles still lacking a value.
        """
        n = self.n_angles
        for name in fs.PER_ANGLE_NAMES:
            current = self.get(name)
            if current is None:
                if name not in values:
                    continue
                self.set(name, [None] * n + [values[name]])
            else:
                self.set(name, list(current) + [values.get(name)])

    def remove_angle(self, index):
        """Remove one angle from every per-angle field."""
        if not 0 <= index < self.n_angles:
            raise IndexError(f"No angle at index {index} (have {self.n_angles})")
        for name in fs.PER_ANGLE_NAMES:
            current = self.get(name)
            if isinstance(current, list) and index < len(current):
                self.set(name, current[:index] + current[index + 1 :])

    def set_angle_field(self, index, name, value):
        """Set one angle's value for one field.

        The index is explicit and mandatory. The editor's table must pass the
        row it is acting on; there is deliberately no notion of a "current row"
        here to fall back on, which is the shape the active-row-as-hidden-input
        bug takes in reduction GUIs.
        """
        field = fs.get(name)
        if not field.per_angle:
            raise KeyError(f"{name} is not a per-angle field")
        current = self.get(name)
        if current is None:
            current = [None] * self.n_angles
        if not 0 <= index < len(current):
            raise IndexError(f"No angle at index {index} (have {len(current)})")
        updated = list(current)
        updated[index] = value
        self.set(name, updated)

    def angle_row(self, index):
        """Every per-angle value for one angle, as a dict."""
        if not 0 <= index < self.n_angles:
            raise IndexError(f"No angle at index {index} (have {self.n_angles})")
        row = {}
        for name in fs.PER_ANGLE_NAMES:
            current = self.get(name)
            row[name] = current[index] if isinstance(current, list) and index < len(current) else None
        return row

    # -- validation --------------------------------------------------------

    def validate(self):
        """Return a list of human-readable problems; empty means clean.

        Reports rather than raises: an editor has to show every problem at
        once, and a partly-filled document is a normal intermediate state, not
        an error. Unset (``None``) entries are therefore not flagged — except
        in an optional list, where a half-specified field is genuinely broken.
        """
        messages = []
        n = self.n_angles

        for field in fs.FIELD_SPEC:
            value = self.get(field.name)

            if field.per_angle:
                if value is None:
                    continue
                if field.optional_list and any(entry is None for entry in value):
                    missing = [i for i, entry in enumerate(value) if entry is None]
                    messages.append(
                        f"{field.label} ({field.name}) is set for some angles but not "
                        f"angles {missing}: either give every angle a value or clear "
                        f"the field to derive it from the chopper ranges"
                    )
                if len(value) != n and not (field.broadcast_ok and len(value) in (0, 1)):
                    messages.append(
                        f"{field.label} ({field.name}) has {len(value)} entries "
                        f"for {n} angles"
                    )
                messages.extend(
                    self._check_value(field, entry, f" at angle {i}")
                    for i, entry in enumerate(value)
                    if entry is not None
                )
            elif value is not None:
                messages.append(self._check_value(field, value, ""))

        return [m for m in messages if m]

    @staticmethod
    def _check_value(field, value, where):
        """Check one value against its allowed set and range. Returns a message or ''."""
        if field.allowed:
            # nr_reduction_calc.py:81 lowercases before checking :84, so the
            # stored spelling need not match the canonical one exactly.
            if str(value).lower() not in {str(a).lower() for a in field.allowed}:
                return (
                    f"{field.label} ({field.name}){where}: {value!r} is not one of "
                    f"{', '.join(str(a) for a in field.allowed)}"
                )
            return ""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return ""
        if field.minimum is not None and value < field.minimum:
            return f"{field.label} ({field.name}){where}: {value} is below {field.minimum}"
        if field.maximum is not None and value > field.maximum:
            return f"{field.label} ({field.name}){where}: {value} is above {field.maximum}"
        return ""

    # -- output ------------------------------------------------------------

    def normalize(self):
        """JSON-safe settings with the runtime-owned fields dropped.

        Those fields (``RBnum`` and the ``Lambda*Use`` record) are filled in by
        the reduction from the runs it is given; carrying an authored value for
        them would silently override the run.
        """
        return {
            key: value
            for key, value in make_json_safe(self.to_dict()).items()
            if key not in fs.RUNTIME_OWNED_NAMES
        }

    def save(self, path):
        """Write the full document as a JSON settings file.

        The whole document, not ``normalize()``: this is the scientist's file
        and round-tripping it must not quietly drop fields. Use ``normalize()``
        when handing settings to a reduction.
        """
        path = Path(path)
        with open(path, "w") as fd:
            json.dump(make_json_safe(self.to_dict()), fd, indent=2)
        return path

    def changed_vs_seed(self):
        """``{name: (seed_value, current_value)}`` for every field that moved."""
        current = self.to_dict()
        return {
            key: (self._seed[key], current[key])
            for key in current
            if key in self._seed and current[key] != self._seed[key]
        }
