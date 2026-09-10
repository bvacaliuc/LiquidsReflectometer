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
    GLOBAL_WHITELIST,
    LAYERS,
    NotWhitelistedError,
    ResolutionContext,
    Resolved,
    SettingsResolver,
    discover_ipts_settings,
    load_resolution,
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
# Precedence
# --------------------------------------------------------------------------


def test_precedence_order_abcdef():
    """Peel the layers off one at a time; the winner must change in order.

    Asserts the layer, not only the value. A swapped pair of layers can leave
    every value assertion passing if the fixtures happen to agree.
    """
    ctx = _context_with_every_layer()
    resolver = SettingsResolver(ctx)

    expected = [
        ("a", 0.1),
        ("b", 0.2),
        ("c", 0.3),
        ("d", 0.4),
        ("e", 0.5),
    ]
    peel = [
        lambda c: c.global_settings.clear(),
        lambda c: c.ui_overrides.clear(),
        lambda c: c.json_settings.clear(),
        lambda c: c.xml_settings.clear(),
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


def test_layer_order_is_the_declared_one():
    assert LAYERS == ("a", "b", "c", "d", "e", "f")


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
    assert resolved.source_layer == "a"


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
    """/SNS may be down. That is a status note, not an exception."""
    ctx = discover_ipts_settings("IPTS-99999", root=str(tmp_path / "nowhere"))
    assert ctx.json_settings == {}
    assert ctx.xml_settings == {}
    assert "IPTS-99999" in ctx.discovery_status


def test_discovery_reports_an_absent_settings_file(tmp_path):
    autoreduce = tmp_path / "IPTS-1" / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    ctx = discover_ipts_settings("IPTS-1", root=str(tmp_path))
    assert ctx.json_settings == {}
    assert "settings file" in ctx.discovery_status.lower()


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


def test_discovery_arms_the_template_layer(tmp_path):
    autoreduce = tmp_path / "IPTS-4" / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    (autoreduce / "template_up.xml").write_text("<Reduction/>")
    ctx = discover_ipts_settings("IPTS-4", root=str(tmp_path))
    assert ctx.xml_detail == "template_up.xml"


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
