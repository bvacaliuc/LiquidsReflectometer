"""Model-level tests for the settings editor (T2).

Deliberately Qt-free and fast: `SettingsDocument` and `FIELD_SPEC` import no
Qt, so the whole editing model — load, validate, normalize, add/remove angle —
is exercised here in milliseconds without a display. The view's tests
(`launcher/tests/test_settings_editor.py`) then only have to cover wiring.
"""

import ast
import json
import pathlib

import pytest

from lr_reduction import field_spec as fs
from lr_reduction.new_reduction_from_file import json_to_config
from lr_reduction.nr_reduction_config import NRReductionConfig
from lr_reduction.settings_document import SettingsDocument

# --------------------------------------------------------------------------
# FIELD_SPEC must mirror the real class, in both directions
# --------------------------------------------------------------------------


def test_field_spec_names_are_real_config_attributes():
    """A name that is not an attribute is a hard failure at load, not a warning.

    `json_to_config` raises `AttributeError` for any key the config does not
    carry, so a typo in FIELD_SPEC would surface as a broken settings file
    rather than as a mislabelled widget.
    """
    attributes = set(NRReductionConfig().__dict__)
    assert {f.name for f in fs.FIELD_SPEC} <= attributes


def test_field_spec_covers_every_config_attribute():
    """The other direction: a field nobody tabled is a field the editor hides."""
    attributes = set(NRReductionConfig().__dict__)
    assert attributes <= {f.name for f in fs.FIELD_SPEC}


def test_field_spec_defaults_match_the_config():
    """Defaults are copied from the class; drift here misinforms every prompt."""
    config = NRReductionConfig()
    mismatched = {
        f.name: (f.default, getattr(config, f.name))
        for f in fs.FIELD_SPEC
        if f.default != getattr(config, f.name)
    }
    assert not mismatched


def test_field_spec_excludes_base_path():
    """`base_path` passes `hasattr` and raises on `setattr` — it must not be tabled.

    This is the trap the name-coverage guard alone would not catch: it is a
    property with no setter, so a "mirror every attribute" loop that used
    `dir()` instead of `__dict__` would include it and then fail at load.
    """
    assert "base_path" not in fs.BY_NAME
    with pytest.raises(AttributeError):
        setattr(NRReductionConfig(), "base_path", "/tmp")


def test_normalized_document_loads_back_through_json_to_config():
    """The end-to-end contract: what we save, the reducer can read."""
    doc = SettingsDocument()
    doc.add_angle(DBname="db.dat", RB_Ymin=100, RB_Ymax=150)
    reloaded = json_to_config(doc.normalize())
    assert isinstance(reloaded, NRReductionConfig)


def test_per_angle_names_match_the_config_shape():
    """The 13 per-angle fields, pinned against the class rather than a comment."""
    config = NRReductionConfig()
    list_valued = {k for k, v in config.__dict__.items() if isinstance(v, list)}
    # data_x_range is a two-element detector range, not one entry per angle.
    assert set(fs.PER_ANGLE_NAMES) - set(fs.OPTIONAL_LIST_NAMES) == list_valued - {"data_x_range"}
    assert len(fs.PER_ANGLE_NAMES) == 13


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def test_defaults_match_a_fresh_config():
    assert SettingsDocument().to_dict() == NRReductionConfig().__dict__


def test_json_seed_round_trips(tmp_path):
    seed = tmp_path / "settings.json"
    doc = SettingsDocument()
    doc.set("Sname", "my_reduction")
    doc.set("qmax", 0.25)
    doc.save(seed)

    assert SettingsDocument.from_file(seed).to_dict() == doc.to_dict()
    assert json.loads(seed.read_text())["Sname"] == "my_reduction"


def test_dat_header_seed(tmp_path):
    """A pre-reduced .dat carries its config in a `# Config:` header line."""
    dat = tmp_path / "reduced.dat"
    config = {"Sname": "from_dat", "qmax": 0.42}
    dat.write_text(
        "# y\n# Config: %s\n# columns = Q, R, dR, dQ\n0.01 1.0 0.1 0.001\n" % json.dumps(config)
    )
    doc = SettingsDocument.from_file(dat)
    assert doc.get("Sname") == "from_dat"
    assert doc.get("qmax") == 0.42


def test_unknown_key_in_a_seed_is_reported_by_name(tmp_path):
    seed = tmp_path / "bad.json"
    seed.write_text(json.dumps({"Snam": "typo"}))
    with pytest.raises(ValueError, match="Snam"):
        SettingsDocument.from_file(seed)


# --------------------------------------------------------------------------
# Angles
# --------------------------------------------------------------------------


def test_add_angle_grows_every_per_angle_field():
    """All 13 move together, or the arrays silently desynchronise.

    Growing only the obvious eight is the defect this slug exists to prevent:
    `RBnum` and `ScaleFactor` are easy to forget, and a short array shifts every
    subsequent angle's settings by one.
    """
    doc = SettingsDocument()
    doc.add_angle()
    doc.add_angle()
    lengths = {name: len(doc.get(name)) for name in fs.PER_ANGLE_NAMES if doc.get(name) is not None}
    assert set(lengths.values()) == {2}
    assert doc.n_angles == 2


def test_add_angle_leaves_an_unset_optional_list_unset():
    """`LambdaMin=None` means "derive from the choppers" — a real state, not a gap.

    `nr_reduction_calc.py:381-383` derives the bound when it is None, and
    `:70-71` raises if a supplied list is shorter than the run count. So
    materialising `[None, None]` on the first add would convert a valid
    "derive it" config into one that reports a length but carries no values,
    which `web_report.py:547` then indexes.
    """
    doc = SettingsDocument()
    doc.add_angle()
    assert doc.get("LambdaMin") is None
    assert doc.get("LambdaMax") is None


def test_add_angle_materializes_an_optional_list_when_given_a_value():
    doc = SettingsDocument()
    doc.add_angle()
    doc.add_angle(LambdaMin=2.5)
    assert doc.get("LambdaMin") == [None, 2.5]
    assert len(doc.get("LambdaMin")) == doc.n_angles


def test_remove_angle_shrinks_every_per_angle_field():
    doc = SettingsDocument()
    doc.add_angle(DBname="a.dat")
    doc.add_angle(DBname="b.dat")
    doc.add_angle(DBname="c.dat")
    doc.remove_angle(1)
    assert doc.get("DBname") == ["a.dat", "c.dat"]
    assert doc.n_angles == 2


def test_set_angle_field_uses_the_index_it_is_given():
    """The active-row trap, pinned at the model layer.

    The view must pass the row being edited, never the row that happens to be
    selected. Enforced here by construction: the model has no notion of a
    current row to fall back on.
    """
    doc = SettingsDocument()
    for name in ("a.dat", "b.dat", "c.dat"):
        doc.add_angle(DBname=name)
    doc.set_angle_field(0, "DBname", "edited.dat")
    assert doc.get("DBname") == ["edited.dat", "b.dat", "c.dat"]


def test_set_angle_field_rejects_an_out_of_range_index():
    doc = SettingsDocument()
    doc.add_angle()
    with pytest.raises(IndexError):
        doc.set_angle_field(5, "DBname", "x.dat")


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------


def test_validate_accepts_a_fresh_document():
    assert SettingsDocument().validate() == []


def test_validate_rejects_an_unknown_method():
    doc = SettingsDocument()
    doc.add_angle(method_per_run="constantBanana")
    assert any("constantBanana" in m for m in doc.validate())


def test_validate_accepts_methods_case_insensitively():
    """`nr_reduction_calc.py:81` lowercases before checking `:84`."""
    doc = SettingsDocument()
    doc.add_angle(method_per_run="CONSTANTQ")
    assert doc.validate() == []


def test_validate_accepts_a_broadcast_method_per_run():
    """A single entry is broadcast to every angle (`nr_reduction_calc.py:76-78`).

    A strict equal-length rule over all per-angle fields would reject this
    valid configuration.
    """
    doc = SettingsDocument()
    doc.add_angle()
    doc.add_angle()
    doc.set("method_per_run", ["meanTheta"])
    assert doc.validate() == []


def test_validate_flags_a_short_non_broadcast_array():
    doc = SettingsDocument()
    doc.add_angle()
    doc.add_angle()
    doc.set("DBname", ["only_one.dat"])
    assert any("DBname" in m for m in doc.validate())


def test_validate_flags_a_partially_specified_optional_list():
    """Detection is complete even though the fix is the scientist's."""
    doc = SettingsDocument()
    doc.add_angle()
    doc.add_angle(LambdaMin=2.5)
    messages = doc.validate()
    assert any("LambdaMin" in m for m in messages)


def test_validate_flags_a_value_outside_its_range():
    doc = SettingsDocument()
    doc.set("Qline_threshold", 4.0)
    assert any("Qline_threshold" in m for m in doc.validate())


def test_validate_rejects_an_unknown_enumerated_value():
    doc = SettingsDocument()
    doc.set("peak_type", "triangle")
    assert any("peak_type" in m for m in doc.validate())


def test_set_rejects_an_unknown_field_name():
    with pytest.raises(KeyError):
        SettingsDocument().set("Snam", "typo")


# --------------------------------------------------------------------------
# Normalization and diffing
# --------------------------------------------------------------------------


def test_normalize_drops_runtime_owned_fields():
    doc = SettingsDocument()
    doc.add_angle(RBnum=197912)
    normalized = doc.normalize()
    for name in fs.RUNTIME_OWNED_NAMES:
        assert name not in normalized
    assert "Sname" in normalized


def test_changed_vs_seed_reports_only_what_moved():
    doc = SettingsDocument()
    assert doc.changed_vs_seed() == {}
    doc.set("Sname", "changed")
    assert doc.changed_vs_seed() == {"Sname": ("reduction_output", "changed")}


def test_changed_vs_seed_is_relative_to_the_loaded_seed(tmp_path):
    seed = tmp_path / "seed.json"
    seed.write_text(json.dumps({"Sname": "seeded"}))
    doc = SettingsDocument.from_file(seed)
    assert doc.changed_vs_seed() == {}
    doc.set("Sname", "edited")
    assert doc.changed_vs_seed() == {"Sname": ("seeded", "edited")}


# --------------------------------------------------------------------------
# The seam
# --------------------------------------------------------------------------


@pytest.mark.parametrize("module", ["settings_document", "field_spec"])
def test_model_modules_import_no_qt(module):
    """T3 builds on this seam; a stray Qt import would cost it the fast tests.

    Parsed rather than grepped. A substring search reports the word "qtpy"
    wherever it appears — including in the docstring that explains the module
    is Qt-free — so the first version of this guard failed on prose. `ast` sees
    only actual import statements.
    """
    source = (pathlib.Path(__file__).parents[3] / "src" / "lr_reduction" / f"{module}.py").read_text()
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    offenders = {name for name in imported if name.split(".")[0] in {"qtpy", "PyQt5", "PyQt6", "PySide2", "PySide6"}}
    assert not offenders
