"""Model tests for the settings resolver (T3).

Qt-free and fast, like T2's model suite: the whole layer taxonomy is exercised
without a display, so the GUI tests only have to cover wiring.

Every assertion about precedence keys on **`source_layer`**, not on the value.
Two layers holding the same number is the normal case — an experiment file that
agrees with the built-in default — and a value-keyed assertion cannot tell which
one is in force, which is the exact confusion this slug exists to end.
"""

import json
import subprocess
import sys
import textwrap

import pytest

from lr_reduction import field_spec as fs
from lr_reduction.settings_resolver import (
    DISCOVERY_LAYERS,
    GLOBAL_WHITELIST,
    LAYER_ORDER,
    NotWhitelistedError,
    ResolutionContext,
    Resolved,
    SettingsResolver,
    discover_ipts_settings,
    load_resolution,
    provenance_path,
    save_resolution,
    user_chosen,
)


def _context_with_every_layer(name="qmax"):
    """One field present in all of (a)-(e), each with a distinguishable value."""
    return ResolutionContext(
        global_settings={name: 0.1},
        ui_overrides={name: 0.2},
        json_settings={name: 0.3},
        json_detail="reduce_settings_up.json",
        xml_settings={name: 0.4},
        xml_detail="template_up.xml",
        dataset_probe=lambda field: 0.5 if field == name else None,
    )


# --------------------------------------------------------------------------
# Precedence — the human's decision of 2026-09-12
# --------------------------------------------------------------------------


def test_precedence_order_is_b_c_d_a_e_f():
    """Peel the layers off one at a time; the winner must change in order.

    Asserts the layer, not only the value. A swapped pair can leave every value
    assertion passing if the fixtures happen to agree.

    The order is the human's: this-run beats a standing preference (an override
    that is overridden is not an override), the experiment's own file beats a
    user-general preference, and a preference still beats a guess and a default.
    """
    ctx = _context_with_every_layer()
    resolver = SettingsResolver(ctx)

    expected = [
        ("b", 0.2),
        ("c", 0.3),
        ("d", 0.4),
        ("a", 0.1),
        ("e", 0.5),
    ]
    peel = [
        lambda c: c.ui_overrides.clear(),
        lambda c: c.json_settings.clear(),
        lambda c: c.xml_settings.clear(),
        lambda c: c.global_settings.clear(),
        lambda c: setattr(c, "dataset_probe", None),
    ]
    for (layer, value), remove in zip(expected, peel):
        resolved = resolver.resolve("qmax")
        assert resolved.source_layer == layer
        assert resolved.value == value
        remove(ctx)

    final = resolver.resolve("qmax")
    assert final.source_layer == "f"
    assert final.value == fs.get("qmax").default


@pytest.mark.parametrize(
    "higher, lower, higher_kwargs, lower_kwargs",
    [
        pytest.param("b", "c", {"ui_overrides": {"qmax": 1.0}},
                     {"json_settings": {"qmax": 2.0}, "json_detail": "f.json"},
                     id="this-run-beats-experiment-file"),
        pytest.param("c", "d", {"json_settings": {"qmax": 1.0}, "json_detail": "f.json"},
                     {"xml_settings": {"qmax": 2.0}, "xml_detail": "t.xml"},
                     id="experiment-file-beats-template"),
        pytest.param("d", "a", {"xml_settings": {"qmax": 1.0}, "xml_detail": "t.xml"},
                     {"global_settings": {"qmax": 2.0}},
                     id="experiment-template-beats-preference"),
        pytest.param("a", "e", {"global_settings": {"qmax": 1.0}},
                     {"dataset_probe": lambda _name: 2.0}, id="preference-beats-guess"),
    ],
)
def test_each_precedence_boundary(higher, lower, higher_kwargs, lower_kwargs):  # noqa: ARG001
    """One test per boundary, so a swap reds the boundary it broke.

    A single blanket precedence test tells you something is wrong; these tell
    you which pair.
    """
    ctx = ResolutionContext(**{**higher_kwargs, **lower_kwargs})
    assert SettingsResolver(ctx).resolve("qmax").source_layer == higher


def test_the_layer_table_actually_drives_the_walk():
    """LAYER_ORDER was inert: reversing it changed nothing.

    A declared order that its implementation ignores is worse than none,
    because it is believed.
    """
    import lr_reduction.settings_resolver as module

    ctx = ResolutionContext(global_settings={"qmax": 0.1}, ui_overrides={"qmax": 0.2})
    assert SettingsResolver(ctx).resolve("qmax").source_layer == "b"

    original = module.LAYER_ORDER
    try:
        module.LAYER_ORDER = ("a", "b", "c", "d", "e", "f")
        assert SettingsResolver(ctx).resolve("qmax").source_layer == "a"
    finally:
        module.LAYER_ORDER = original


def test_layer_order_is_the_humans_decision():
    assert LAYER_ORDER == ("b", "c", "d", "a", "e", "f")


def test_per_field_fallthrough_reaches_the_dataset_probe():
    """(a)-(d) all miss for this field, so layer (e) must be consulted."""
    probed = []

    def probe(name):
        probed.append(name)
        return 4.5 if name == "IncidentTheta" else None

    ctx = ResolutionContext(global_settings={"qmax": 0.9}, dataset_probe=probe)
    resolved = SettingsResolver(ctx).resolve("IncidentTheta")
    assert resolved.source_layer == "e"
    assert resolved.value == 4.5
    assert "IncidentTheta" in probed


def test_per_field_fallthrough_reaches_the_default():
    ctx = ResolutionContext()
    resolved = SettingsResolver(ctx).resolve("dqbin")
    assert resolved.source_layer == "f"
    assert resolved.value == fs.get("dqbin").default


def test_the_dataset_probe_is_not_consulted_for_a_field_already_set():
    """Layer (e) is lazy: an expensive analysis must not run for a set field."""
    probed = []
    ctx = ResolutionContext(
        global_settings={"qmax": 0.9},
        dataset_probe=lambda name: probed.append(name) or 1.0,
    )
    SettingsResolver(ctx).resolve("qmax")
    assert probed == []


def test_json_shadows_xml():
    """A field defined in the settings JSON never comes from the template."""
    ctx = ResolutionContext(
        json_settings={"qmax": 0.3},
        json_detail="reduce_settings_up.json",
        xml_settings={"qmax": 0.4, "qmin": 0.002},
        xml_detail="template_up.xml",
    )
    resolver = SettingsResolver(ctx)
    assert resolver.resolve("qmax").source_layer == "c"
    # A field the JSON does NOT define still comes from the template, so the
    # test cannot pass merely by ignoring layer (d).
    assert resolver.resolve("qmin").source_layer == "d"


def test_a_value_that_coincides_across_layers_still_reports_the_winner():
    """The case a value-keyed assertion cannot see."""
    ctx = ResolutionContext(
        global_settings={"qmax": 0.5},
        json_settings={"qmax": 0.5},
        json_detail="reduce_settings.json",
    )
    resolved = SettingsResolver(ctx).resolve("qmax")
    assert resolved.value == 0.5
    assert resolved.source_layer == "c"


def test_a_none_in_a_layer_does_not_win():
    """An explicit null is 'not set here', not 'set to nothing'."""
    ctx = ResolutionContext(global_settings={"qmax": None}, json_settings={"qmax": 0.3})
    assert SettingsResolver(ctx).resolve("qmax").source_layer == "c"


# --------------------------------------------------------------------------
# resolve_all
# --------------------------------------------------------------------------


def test_resolve_all_covers_every_field():
    document, provenance = SettingsResolver(ResolutionContext()).resolve_all()
    assert set(provenance) == {f.name for f in fs.FIELD_SPEC}
    assert all(isinstance(r, Resolved) for r in provenance.values())
    assert document.get("qmax") == fs.get("qmax").default


def test_resolve_all_keeps_per_angle_arrays_length_consistent():
    """Layers resolve independently, so one can be shorter than another.

    A short array does not fail — it shifts every later angle's settings by one,
    silently. The editor's add_angle was built to prevent that; the resolver
    could otherwise reintroduce it one layer at a time.
    """
    ctx = ResolutionContext(
        json_settings={"DBname": ["a.dat", "b.dat", "c.dat"]},
        json_detail="reduce_settings.json",
        xml_settings={"RB_Ymin": [100, 110]},
        xml_detail="template.xml",
    )
    document, _ = SettingsResolver(ctx).resolve_all()
    assert document.n_angles == 3
    assert len(document.get("RB_Ymin")) == 3
    assert document.get("RB_Ymin") == [100, 110, None]


def test_resolve_all_produces_a_document_the_reduction_can_read():
    from lr_reduction.new_reduction_from_file import json_to_config

    document, _ = SettingsResolver(ResolutionContext()).resolve_all()
    json_to_config(document.normalize())


# --------------------------------------------------------------------------
# The global-preference whitelist
# --------------------------------------------------------------------------


def test_global_whitelist_enforced():
    ctx = ResolutionContext()
    with pytest.raises(NotWhitelistedError, match="RB_Ymin"):
        ctx.set_global("RB_Ymin", 100)
    assert "RB_Ymin" not in ctx.global_settings


def test_a_whitelisted_preference_is_accepted():
    ctx = ResolutionContext()
    ctx.set_global("qmax", 0.42)
    assert SettingsResolver(ctx).resolve("qmax").source_layer == "a"


def test_the_whitelist_excludes_per_angle_and_runtime_owned_fields():
    """Derived from FIELD_SPEC by group, so it cannot drift from the field set."""
    for name in GLOBAL_WHITELIST:
        field = fs.get(name)
        assert not field.per_angle
        assert not field.runtime_owned
    assert "experiment_id" not in GLOBAL_WHITELIST
    assert "Sname" not in GLOBAL_WHITELIST
    assert "qmax" in GLOBAL_WHITELIST


# --------------------------------------------------------------------------
# Discovery — degrades, never raises
# --------------------------------------------------------------------------


def test_discovery_missing_mount(tmp_path):
    """/SNS may be down. That is a status note, not an exception.

    Asserts the OUTCOME, not just that the IPTS number appears in the status —
    an earlier version was satisfied by the number alone, so a status reading
    "loaded every layer" would have passed it.
    """
    ctx = discover_ipts_settings("IPTS-99999", root=str(tmp_path / "nowhere"))
    assert ctx.json_settings == {}
    assert ctx.xml_settings == {}
    assert ctx.template_path is None
    assert "no autoreduce directory" in ctx.discovery_status


def test_discovery_reports_an_absent_settings_file(tmp_path):
    autoreduce = tmp_path / "IPTS-1" / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    ctx = discover_ipts_settings("IPTS-1", root=str(tmp_path))
    assert ctx.json_settings == {}
    assert "no reduce_settings" in ctx.discovery_status


def test_discovery_survives_a_malformed_settings_file(tmp_path):
    autoreduce = tmp_path / "IPTS-2" / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    (autoreduce / "reduce_settings.json").write_text("{not json")
    ctx = discover_ipts_settings("IPTS-2", root=str(tmp_path))
    assert ctx.json_settings == {}
    assert "unreadable" in ctx.discovery_status


@pytest.mark.parametrize(
    "tthd, expected",
    [
        pytest.param(1.0, "reduce_settings_up.json", id="tthd-positive-selects-up"),
        pytest.param(-1.0, "reduce_settings_down.json", id="tthd-negative-selects-down"),
    ],
)
def test_updown_selection_matches_the_shared_helper(tmp_path, tthd, expected):
    """The up/down rule is the autoreduction's, not a second copy of it."""
    from lr_autoreduce.new_reduce_REF_L import get_default_setting_file

    autoreduce = tmp_path / "IPTS-3" / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    (autoreduce / "reduce_settings_up.json").write_text(json.dumps({"qmax": 0.11}))
    (autoreduce / "reduce_settings_down.json").write_text(json.dumps({"qmax": 0.22}))

    ctx = discover_ipts_settings("IPTS-3", tthd=tthd, root=str(tmp_path))
    assert ctx.json_detail == expected
    # The same fixture tree through the helper itself must agree.
    assert get_default_setting_file(str(autoreduce), tthd).endswith(expected)


def test_discovery_reports_a_template_without_pretending_to_use_it(tmp_path):
    """Layer (d) is declared and honoured, but discovery does not populate it.

    Mapping a template's vocabulary onto config fields is
    `new_reduction_from_template.config_from_template`'s job; reproducing it
    here would be a second copy of a mapping, or would pull Mantid into the one
    module whose value is not needing it. So the template is *reported* and the
    layer stays empty — declared, not pretended.
    """
    autoreduce = tmp_path / "IPTS-4" / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    (autoreduce / "template_up.xml").write_text("<Reduction/>")
    ctx = discover_ipts_settings("IPTS-4", tthd=1.0, root=str(tmp_path))
    assert ctx.template_path.endswith("template_up.xml")
    assert ctx.xml_settings == {}
    assert "not consumed" in ctx.discovery_status
    assert "d" not in DISCOVERY_LAYERS


def test_a_caller_supplied_template_layer_is_still_honoured():
    """The mechanism is real; only the automatic population is deferred."""
    ctx = ResolutionContext(xml_settings={"qmax": 0.4}, xml_detail="template_up.xml")
    assert SettingsResolver(ctx).resolve("qmax").source_layer == "d"


# --------------------------------------------------------------------------
# Provenance survives being saved
# --------------------------------------------------------------------------


def test_provenance_survives_store_and_save(tmp_path):
    ctx = ResolutionContext(
        global_settings={"qmax": 0.9},
        ui_overrides={"Sname": "run_1"},
        json_settings={"qmin": 0.002},
        json_detail="reduce_settings_up.json",
    )
    document, provenance = SettingsResolver(ctx).resolve_all()
    target = tmp_path / "resolved.json"
    save_resolution(target, document, provenance)

    settings, restored = load_resolution(target)
    assert settings["qmax"] == 0.9
    assert restored["qmax"].source_layer == "a"
    assert restored["qmax"].value == 0.9  # rehydrated from the document, stored once
    assert restored["qmin"].source_layer == "c"
    assert restored["qmin"].source_detail == "reduce_settings_up.json"
    assert restored["dqbin"].source_layer == "f"


def test_user_chosen_separates_people_from_defaults(tmp_path):
    """The question the reduction record could not answer before."""
    ctx = ResolutionContext(
        global_settings={"qmax": 0.9},
        ui_overrides={"Sname": "run_1"},
        json_settings={"qmin": 0.002},
        json_detail="reduce_settings.json",
    )
    document, provenance = SettingsResolver(ctx).resolve_all()
    target = tmp_path / "resolved.json"
    save_resolution(target, document, provenance)
    _, restored = load_resolution(target)

    chosen = set(user_chosen(restored))
    assert {"qmax", "Sname"} <= chosen
    assert "qmin" not in chosen
    assert "dqbin" not in chosen


def test_a_settings_file_without_provenance_still_loads(tmp_path):
    """The facility has files that predate this module."""
    legacy = tmp_path / "legacy.json"
    legacy.write_text(json.dumps({"qmax": 0.7}))
    settings, provenance = load_resolution(legacy)
    assert settings == {"qmax": 0.7}
    assert provenance == {}


def test_saving_does_not_destroy_a_previous_file_on_failure(tmp_path, monkeypatch):
    import os

    target = tmp_path / "resolved.json"
    target.write_text('{"good": "settings"}')

    def explode(*_args, **_kwargs):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(os, "replace", explode)
    document, provenance = SettingsResolver(ResolutionContext()).resolve_all()
    with pytest.raises(OSError):
        save_resolution(target, document, provenance)
    assert json.loads(target.read_text()) == {"good": "settings"}


# --------------------------------------------------------------------------
# The seam
# --------------------------------------------------------------------------


def test_the_resolver_pulls_no_qt_into_a_fresh_interpreter():
    """Executed, not grepped — an AST check cannot see a transitive import."""
    program = textwrap.dedent(
        """
        import sys
        from lr_reduction import settings_resolver
        qt = sorted(m for m in sys.modules
                    if m.split(".")[0] in {"qtpy", "PyQt5", "PyQt6", "PySide2", "PySide6"})
        assert not qt, f"resolver pulled in Qt: {qt}"
        ctx = settings_resolver.ResolutionContext(global_settings={"qmax": 0.9})
        document, provenance = settings_resolver.SettingsResolver(ctx).resolve_all()
        assert provenance["qmax"].source_layer == "a"
        assert document.get("qmax") == 0.9
        print("clean")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, timeout=300
    )
    assert result.returncode == 0, result.stderr
    assert "clean" in result.stdout


# --------------------------------------------------------------------------
# v2 guards
# --------------------------------------------------------------------------


def test_a_written_settings_file_round_trips_the_reduction_loader(tmp_path):
    """The defect that would have stopped autoreduction for an experiment.

    Provenance used to be written into the settings JSON under `_provenance`,
    and `json_to_config` raises `AttributeError` on any key that is not a config
    field. A file written that way and dropped into `shared/autoreduce` as
    `reduce_settings*.json` would have taken that experiment's autoreduction
    down. The origins live in a sidecar now.
    """
    from lr_reduction.new_reduction_from_file import json_to_config

    target = tmp_path / "reduce_settings.json"
    document, provenance = SettingsResolver(
        ResolutionContext(global_settings={"qmax": 0.9})
    ).resolve_all()
    save_resolution(target, document, provenance)

    json_to_config(json.loads(target.read_text()))
    assert "_provenance" not in json.loads(target.read_text())
    assert provenance_path(target).exists()


def test_provenance_and_settings_agree_in_length():
    """Recorded AFTER equalising, so the padded arrays and their origins match.

    Snapshotting before meant a file could carry 55 provenance entries against
    52 settings.
    """
    ctx = ResolutionContext(
        json_settings={"DBname": ["a.dat", "b.dat", "c.dat"], "RB_Ymin": [1, 2]},
        json_detail="reduce_settings.json",
    )
    document, provenance = SettingsResolver(ctx).resolve_all()
    assert len(provenance["RB_Ymin"].value) == len(document.get("RB_Ymin")) == 3
    assert provenance["RB_Ymin"].value == document.get("RB_Ymin")


def test_a_resolved_document_can_be_edited_without_rewriting_its_source():
    """The resolved value, the layer dict and the frozen Resolved were one object.

    Editing a resolved setting rewrote the experiment file's in-memory copy, so
    the next resolve returned the edit as though the file had said it. `frozen`
    protects the binding, not the list behind it.
    """
    layer = {"DBname": ["a.dat"]}
    ctx = ResolutionContext(json_settings=layer, json_detail="reduce_settings.json")
    document, provenance = SettingsResolver(ctx).resolve_all()

    document.get("DBname").append("edited.dat")
    assert layer["DBname"] == ["a.dat"]
    assert provenance["DBname"].value == ["a.dat"]


def test_a_preference_never_outranks_a_measured_geometry():
    """C4(ii), the human's decision: a preference must not beat a measurement."""
    ctx = ResolutionContext(
        global_settings={"IncidentTheta": 9.9},
        dataset_probe=lambda name: 4.0 if name == "IncidentTheta" else None,
    )
    resolved = SettingsResolver(ctx).resolve("IncidentTheta")
    assert resolved.source_layer == "e"
    assert resolved.value == 4.0


def test_the_experiment_file_outranks_a_preference():
    """The other half of C4(ii): (a) sits below (c)."""
    ctx = ResolutionContext(
        global_settings={"qmax": 0.1},
        json_settings={"qmax": 0.3},
        json_detail="reduce_settings.json",
    )
    assert SettingsResolver(ctx).resolve("qmax").source_layer == "c"


@pytest.mark.parametrize("name", ["IncidentTheta", "mmpix", "dSampDet", "dMod", "xi_ref", "dS1Samp", "nx", "ny"])
def test_no_instrument_geometry_field_is_a_preference(name):
    assert name not in GLOBAL_WHITELIST


def test_the_whitelist_is_derived_not_hand_listed():
    """C6a: a hand-list of four names would have passed everything else.

    Asserts a named exemplar from every included group, so dropping a group or
    replacing the derivation with a literal list reds.
    """
    from lr_reduction.settings_resolver import GLOBAL_GROUPS

    exemplars = {
        fs.PROCESSING: "plotON",
        fs.QSPACE: "qmax",
        fs.WAVELENGTH: "tof_bin",
        fs.DEADTIME: "dead_time",
        fs.RESOLUTION: "DetResFn",
        fs.PEAK: "peak_type",
    }
    assert set(exemplars) == set(GLOBAL_GROUPS)
    for group, name in exemplars.items():
        assert name in GLOBAL_WHITELIST, f"{group} contributes nothing"


def test_the_whitelist_is_enforced_at_the_reader_too():
    """The ResolutionContext constructor is a third door past both writers."""
    ctx = ResolutionContext(global_settings={"Sname": "../escape", "RB_Ymin": [1]})
    assert SettingsResolver(ctx).resolve("Sname").source_layer == "f"
    assert SettingsResolver(ctx).resolve("RB_Ymin").source_layer == "f"


def test_discovery_survives_an_unreachable_mount(tmp_path, monkeypatch):  # noqa: ARG001
    """C5a: this guard had no test of its own; deleting it left everything green.

    A stalled sshfs answers is_dir() with an OSError rather than False, which is
    the module's headline promise — never take the launcher down when /SNS is
    unavailable.
    """
    from pathlib import Path as RealPath

    def stalled(self):  # noqa: ARG001
        raise OSError(5, "Input/output error")

    monkeypatch.setattr(RealPath, "is_dir", stalled)
    ctx = discover_ipts_settings("IPTS-7", root=str(tmp_path))
    assert ctx.json_settings == {}
    assert "could not reach" in ctx.discovery_status


def test_discovery_refuses_an_ipts_that_escapes_the_facility_root(tmp_path):
    ctx = discover_ipts_settings("../../etc", root=str(tmp_path))
    assert ctx.json_settings == {}
    assert "does not name a directory under" in ctx.discovery_status


def test_discovery_refuses_an_oversized_settings_file(tmp_path):
    from lr_reduction.settings_resolver import MAX_SETTINGS_BYTES

    autoreduce = tmp_path / "IPTS-8" / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    padding = " " * (MAX_SETTINGS_BYTES + 1)
    (autoreduce / "reduce_settings.json").write_text('{"qmax": 0.1}' + padding)
    ctx = discover_ipts_settings("IPTS-8", root=str(tmp_path))
    assert ctx.json_settings == {}
    assert "unreadable" in ctx.discovery_status


def test_discovery_does_not_import_mantid():
    """The lazy import it used to do cost 2.6 s and a network version check —
    and could not run at all in the Mantid-free launcher it was meant to serve."""
    program = textwrap.dedent(
        """
        import sys, tempfile, pathlib, json
        from lr_reduction.settings_resolver import discover_ipts_settings
        root = pathlib.Path(tempfile.mkdtemp())
        a = root / "IPTS-1" / "shared" / "autoreduce"
        a.mkdir(parents=True)
        (a / "reduce_settings_up.json").write_text(json.dumps({"qmax": 0.1}))
        ctx = discover_ipts_settings("IPTS-1", tthd=1.0, root=str(root))
        assert ctx.json_detail == "reduce_settings_up.json", ctx.discovery_status
        assert not [m for m in sys.modules if m.startswith("mantid")], "mantid imported"
        print("light")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, timeout=300
    )
    assert result.returncode == 0, result.stderr
    assert "light" in result.stdout


def test_a_resolved_document_reports_no_user_edits():
    """The resolved state is the baseline, not itself an edit.

    Without reseeding, changed_vs_seed reported the experiment file's own values
    as though a person had typed them — the exact confusion provenance exists to
    remove.
    """
    ctx = ResolutionContext(
        json_settings={"qmax": 0.3}, json_detail="reduce_settings.json"
    )
    document, _ = SettingsResolver(ctx).resolve_all()
    assert document.changed_vs_seed() == {}


def test_an_explicit_null_wins_for_an_optional_list():
    """LambdaMin=None means "derive from the choppers" — a value, not an absence."""
    ctx = ResolutionContext(
        json_settings={"LambdaMin": None}, json_detail="reduce_settings.json"
    )
    resolved = SettingsResolver(ctx).resolve("LambdaMin")
    assert resolved.source_layer == "c"
    assert resolved.value is None
