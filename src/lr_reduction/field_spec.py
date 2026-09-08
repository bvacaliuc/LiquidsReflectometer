"""Declarative description of every :class:`NRReductionConfig` field.

One table drives widget construction, the prompts the scientist reads,
validation messages, and the runtime-owned list used when normalizing a
document for saving. Without it each of those grows its own copy of "what
fields exist and what may they hold", and they drift.

**Qt-free on purpose.** This module and :mod:`lr_reduction.settings_document`
import nothing from ``qtpy``/``PyQt``. That seam is what lets the settings
model be tested in milliseconds without a display, and T3's resolution layer
builds on it.

**Names are storage names, not display names.** Every ``Field.name`` is exactly
a key of ``NRReductionConfig().__dict__`` — including the four private
``_*_override`` path fields. That is deliberate:

* ``json_to_config`` (``new_reduction_from_file.py:441``) gates on
  ``hasattr(config, key)`` and raises ``AttributeError`` on anything else, so a
  name that is not a real attribute is a hard failure at load, not a warning;
* the saved JSON is written from ``config.__dict__``
  (``new_reduction_from_file.py:145-151``), so ``__dict__`` keys are what a
  settings file actually contains;
* ``Spath``/``NEXUSpathRB``/``DBpath``/``BINpath`` are properties backed by
  those private names. Naming the public property instead would mean carrying a
  public-to-private mapping that can drift from the class — the exact failure
  this table exists to prevent.

The user-facing name lives in ``Field.label``.

``base_path`` is deliberately absent: it is a property with **no setter**, so
``hasattr`` passes and ``setattr`` raises. Any "mirror every attribute" loop
must exclude it.
"""

from dataclasses import dataclass
from typing import Any, Optional, Tuple

# Mirrors the validated set at nr_reduction_calc.py:84, which is matched AFTER
# lowercasing (:81) — so comparison here is case-insensitive too. The canonical
# spellings below are what the examples and templates use.
METHOD_CHOICES = ("meanTheta", "constantQ", "constantTOF")

DET_RES_CHOICES = ("rectangular", "gaussian")
PEAK_TYPE_CHOICES = ("gauss", "supergauss")


@dataclass(frozen=True)
class Field:
    """One configuration field.

    Attributes
    ----------
    name
        Exact ``NRReductionConfig.__dict__`` key. Pinned by a guard test.
    label
        User-facing name, shown in the editor.
    group
        Section the editor groups this field under.
    type
        Vocabulary term describing the value shape (see ``TYPES``).
    default
        The value a fresh ``NRReductionConfig`` carries.
    help
        The prompt shown to the scientist. Written to say what the field
        *does*, not to restate its name.
    allowed
        Permitted values, for enumerated fields. Empty means unconstrained.
    minimum, maximum
        Inclusive numeric bounds, where a bound is physically meaningful.
    per_angle
        True when the value is one entry per angle. ``add_angle`` grows every
        such field together.
    broadcast_ok
        Per-angle fields the reducer will broadcast from a single entry, so a
        length of 1 is valid rather than a mismatch.
    optional_list
        Per-angle fields initialised to ``None`` rather than ``[]``, where
        ``None`` means "derive it" and is a first-class state, not a missing
        value.
    runtime_owned
        Filled in by the reduction run, not authored by the scientist. Dropped
        by ``SettingsDocument.normalize()``.
    """

    name: str
    label: str
    group: str
    type: str
    default: Any
    help: str
    allowed: Tuple[Any, ...] = ()
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    per_angle: bool = False
    broadcast_ok: bool = False
    optional_list: bool = False
    runtime_owned: bool = False


TYPES = (
    "str", "int", "float", "bool", "path",
    "list[str]", "list[int]", "list[float]", "list[bool]", "list[list[int]]",
)

RUNS = "Runs and angles"
PATHS = "Paths"
NAMING = "Output naming"
PROCESSING = "Processing"
BACKGROUND = "Background"
QSPACE = "Q-space"
WAVELENGTH = "Wavelength and TOF"
THETA = "Theta and scaling"
GEOMETRY = "Instrument geometry"
DEADTIME = "Dead time"
RESOLUTION = "Detector resolution"
PEAK = "Peak fitting"
RUNTIME = "Runtime record"


FIELD_SPEC = (
    # ---- per-angle -------------------------------------------------------
    Field("method_per_run", "Q method", RUNS, "list[str]", [],
          "Lambda-to-Q conversion used for each angle. One entry per angle; a "
          "single entry is broadcast to all angles, and an empty list defaults "
          "to meanTheta.",
          allowed=METHOD_CHOICES, per_angle=True, broadcast_ok=True),
    Field("DBname", "Direct-beam file", RUNS, "list[str]", [],
          "Pre-processed direct-beam file backing each angle.", per_angle=True),
    Field("RBnum", "Run numbers", RUNS, "list[int]", [],
          "Run numbers reduced at each angle. Supplied by the reduction run, "
          "not authored here.",
          per_angle=True, runtime_owned=True),
    Field("RB_Ymin", "Peak Y min (pixel)", RUNS, "list[int]", [],
          "Lower edge of the specular peak window, in detector pixels.",
          per_angle=True),
    Field("RB_Ymax", "Peak Y max (pixel)", RUNS, "list[int]", [],
          "Upper edge of the specular peak window, in detector pixels.",
          per_angle=True),
    Field("BkgROI", "Background ROI", BACKGROUND, "list[list[int]]", [],
          "Background region per angle, as pixel bounds.", per_angle=True),
    Field("useBS", "Subtract background", BACKGROUND, "list[bool]", [],
          "Whether to subtract background at each angle.", per_angle=True),
    Field("tof_min", "TOF min", WAVELENGTH, "list[float]", [],
          "Lower time-of-flight bound per angle.", per_angle=True),
    Field("tof_max", "TOF max", WAVELENGTH, "list[float]", [],
          "Upper time-of-flight bound per angle.", per_angle=True),
    Field("LambdaMin", "Lambda min", WAVELENGTH, "list[float]", None,
          "Lower wavelength bound per angle. Leave unset to derive it from the "
          "chopper ranges; if set, every angle needs a value.",
          per_angle=True, optional_list=True),
    Field("LambdaMax", "Lambda max", WAVELENGTH, "list[float]", None,
          "Upper wavelength bound per angle. Leave unset to derive it from the "
          "chopper ranges; if set, every angle needs a value.",
          per_angle=True, optional_list=True),
    Field("ThetaShift", "Theta shift (deg)", THETA, "list[float]", [],
          "Correction added to the measured theta at each angle.", per_angle=True),
    Field("ScaleFactor", "Scale factor", THETA, "list[float]", [],
          "Multiplier applied to each angle's reflectivity before stitching.",
          per_angle=True),

    # ---- scalars ---------------------------------------------------------
    Field("Sname", "Output name", NAMING, "str", "reduction_output",
          "Base name for the reduced output files."),
    Field("experiment_id", "IPTS", NAMING, "str", "",
          "IPTS identifier. Also the root of every default path."),
    Field("subname", "Output subtitle", NAMING, "str", None,
          "Optional subtitle appended to saved file names."),
    Field("DTCsubname", "Dead-time-corrected suffix", NAMING, "str", "_DTC",
          "Suffix for dead-time-corrected outputs."),
    Field("BINsubname", "Binned suffix", NAMING, "str", "_DTC",
          "Suffix for binned outputs."),
    Field("errBINsubname", "Binned-error suffix", NAMING, "str", "_err_DTC",
          "Suffix for binned uncertainty outputs."),
    Field("data_x_range", "Detector X range", RUNS, "list[int]", [50, 200],
          "Detector pixel range integrated over in X. Two values, not per angle."),

    Field("_Spath_override", "Output path", PATHS, "path", None,
          "Where reduced data is written. Unset uses <IPTS>/shared/reduced."),
    Field("_NEXUSpathRB_override", "NeXus path", PATHS, "path", None,
          "Where run NeXus files are read from. Unset uses <IPTS>/nexus."),
    Field("_DBpath_override", "Direct-beam path", PATHS, "path", None,
          "Where direct-beam files are read from. Unset uses "
          "<IPTS>/shared/transmission."),
    Field("_BINpath_override", "Binned-output path", PATHS, "path", None,
          "Where binned output is written. Unset uses <IPTS>/shared/reduced."),

    Field("Normalize", "Normalize to critical edge", PROCESSING, "bool", False,
          "Scale reflectivity to 1 over the critical-edge region set by Qnorm."),
    Field("AutoScale", "Auto-scale between angles", PROCESSING, "bool", False,
          "Scale each angle to its neighbour using the overlap region."),
    Field("useCalcTheta", "Use fitted theta", PROCESSING, "bool", False,
          "Use the fitted specular peak position for theta, overriding THS/THI."),
    Field("plotON", "Show plots", PROCESSING, "bool", True,
          "Display plots during reduction. Turn off for batch processing."),
    Field("plotQ4", "Plot as R*Q^4", PROCESSING, "bool", False,
          "Plot R*Q^4 instead of R."),
    Field("save8col", "Save 8-column output", PROCESSING, "bool", False,
          "Also write the 8-column form, adding L, dL, T and dT."),
    Field("useGravity", "Gravity correction", PROCESSING, "bool", True,
          "Apply the gravity correction to the neutron trajectory."),
    Field("use_emission_time", "Emission-time correction", PROCESSING, "bool", True,
          "Apply the moderator emission-time correction."),

    Field("qmin", "Q min", QSPACE, "float", 0.001,
          "Lower edge of the output Q range.", minimum=0.0),
    Field("qmax", "Q max", QSPACE, "float", 0.5,
          "Upper edge of the output Q range.", minimum=0.0),
    Field("dqbin", "Q bin width", QSPACE, "float", 0.005,
          "Width of the output Q bins.", minimum=0.0),
    Field("Qline_threshold", "Q-line threshold", QSPACE, "float", 1.0,
          "Fraction of a Q-line that must fall inside a bin for it to count, "
          "outside constantTOF mode.", minimum=0.0, maximum=1.0),
    Field("Qnorm", "Normalization Q", QSPACE, "float", 0.015,
          "Q below which data is treated as the critical-edge plateau when "
          "normalizing.", minimum=0.0),
    Field("tof_bin", "TOF bin width", WAVELENGTH, "float", 50,
          "Width of the time-of-flight bins.", minimum=0.0),

    Field("mmpix", "Pixel size (mm)", GEOMETRY, "float", None,
          "Detector pixel size. Unset reads it from the instrument settings."),
    Field("dSampDet", "Sample-detector distance", GEOMETRY, "float", None,
          "Unset reads it from the instrument settings."),
    Field("ny", "Vertical pixels", GEOMETRY, "int", None,
          "Number of pixels in Y. Unset reads it from the instrument settings."),
    # The source comments both ny and nx as "number of vertical pixels"; nx is
    # the horizontal count. Described correctly here rather than copying the
    # slip into the scientist-facing prompt.
    Field("nx", "Horizontal pixels", GEOMETRY, "int", None,
          "Number of pixels in X. Unset reads it from the instrument settings."),
    Field("dMod", "Moderator-detector distance", GEOMETRY, "float", None,
          "Unset reads it from the instrument settings."),
    Field("xi_ref", "xi reference distance", GEOMETRY, "float", None,
          "Distance defining xi = 0. Unset reads it from the instrument settings."),
    Field("dS1Samp", "S1-sample distance", GEOMETRY, "float", None,
          "Unset reads it from the instrument settings."),
    Field("IncidentTheta", "Incident theta (deg)", GEOMETRY, "float", None,
          "Beamline angle relative to earth, positive downwards. Unset reads "
          "the PV, falling back to 4.0 for older runs."),
    Field("emission_coefficients", "Emission-time coefficients", GEOMETRY,
          "list[float]", None,
          "Coefficients of the TOF emission-time correction."),

    Field("dead_time", "Dead time (us)", DEADTIME, "float", 4.2,
          "Detector dead time.", minimum=0.0),
    Field("dead_time_tof_step", "Dead-time TOF step", DEADTIME, "float", 50,
          "TOF bin width used when computing the dead-time correction.",
          minimum=0.0),

    Field("DetResFn", "Resolution function", RESOLUTION, "str", "rectangular",
          "Shape of the detector resolution function.", allowed=DET_RES_CHOICES),
    Field("DetSigma", "Resolution sigma", RESOLUTION, "float", 0.8,
          "Width of the detector resolution function.", minimum=0.0),

    Field("peak_pad", "Peak fit padding (pixels)", PEAK, "int", 1,
          "Extra pixels included outside the background range when fitting the "
          "peak.", minimum=0),
    Field("peak_type", "Peak shape", PEAK, "str", "supergauss",
          "Function fitted to the specular peak.", allowed=PEAK_TYPE_CHOICES),

    Field("LambdaMinUse", "Lambda min used", RUNTIME, "list[float]", None,
          "Wavelength bound the run actually used. Recorded by the reduction.",
          runtime_owned=True),
    Field("LambdaMaxUse", "Lambda max used", RUNTIME, "list[float]", None,
          "Wavelength bound the run actually used. Recorded by the reduction.",
          runtime_owned=True),
)


BY_NAME = {f.name: f for f in FIELD_SPEC}

#: Storage names of every per-angle field, in FIELD_SPEC order. ``add_angle``
#: grows all of them together; a field missing from here is a field that
#: silently ends up a different length from its siblings.
PER_ANGLE_NAMES = tuple(f.name for f in FIELD_SPEC if f.per_angle)

#: Per-angle fields whose default is ``None`` rather than ``[]``.
OPTIONAL_LIST_NAMES = tuple(f.name for f in FIELD_SPEC if f.optional_list)

#: Fields the reduction run fills in, dropped when normalizing for save.
RUNTIME_OWNED_NAMES = tuple(f.name for f in FIELD_SPEC if f.runtime_owned)

#: Groups in the order the editor should present them.
GROUPS = tuple(dict.fromkeys(f.group for f in FIELD_SPEC))


def get(name):
    """Return the :class:`Field` named ``name``."""
    return BY_NAME[name]


def fields_in(group):
    """Return the fields belonging to ``group``, in table order."""
    return tuple(f for f in FIELD_SPEC if f.group == group)
