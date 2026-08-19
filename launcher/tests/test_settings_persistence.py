import pytest
from qtpy import QtCore


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_ipts_persists():
    from launcher.apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    tab.ipts_edit.setText("36776")
    tab.save_settings()
    tab.deleteLater()

    tab2 = DirectBeamTab()
    assert tab2.ipts_edit.text() == "36776"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_cd_vals_round_trip():
    from launcher.apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    tab.cd_vals = {"mu_file": "/x/y", "Cd": [5.0, 126.5, 249.5, 499.0], "flip_atten": True}
    tab.save_settings()
    tab.deleteLater()

    tab2 = DirectBeamTab()
    assert tab2.cd_vals == {
        "mu_file": "/x/y",
        "Cd": [5.0, 126.5, 249.5, 499.0],
        "flip_atten": True,
    }


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_corrupt_cd_vals_tolerated():
    from launcher.apps.direct_beam import DirectBeamTab

    s = QtCore.QSettings()
    s.setValue("direct_beam_cd_vals", "not valid json {{")
    s.sync()
    tab = DirectBeamTab()
    assert isinstance(tab.cd_vals, dict)


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_tof_spins_persist():
    """The #155/#156 TOF-rebin spinboxes postdate PR #11; guard them too."""
    from launcher.apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    tab.tofbin_spin.setValue(125.0)
    tab.tofmin_spin.setValue(3000.0)
    tab.tofmax_spin.setValue(55000.0)
    tab.save_settings()
    tab.deleteLater()

    tab2 = DirectBeamTab()
    assert tab2.tofbin_spin.value() == pytest.approx(125.0)
    assert tab2.tofmin_spin.value() == pytest.approx(3000.0)
    assert tab2.tofmax_spin.value() == pytest.approx(55000.0)


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_overplot_saves_ytransform():
    from launcher.apps.overplot import Overplot

    tab = Overplot()
    tab.ytransform_combo.setCurrentText("R*Q^4")
    tab.save_settings()
    s = QtCore.QSettings()
    assert s.value("overplot_ytransform") == "R*Q^4"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_first_launch_defaults():
    from launcher.apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    assert tab.ipts_edit.text() == ""
    assert tab.tofbin_spin.value() == pytest.approx(50.0)
    assert tab.tofmin_spin.value() == pytest.approx(0.0)
    assert tab.tofmax_spin.value() == pytest.approx(100000.0)
    # exp's deployed first-launch behaviour: the toggle starts unchecked and
    # the manual path fields are therefore editable.
    assert tab.ipts_toggle.isChecked() is False
    assert tab.nexus_edit.isEnabled() is True
    assert tab.savepath_edit.isEnabled() is True


# Every persisted Direct-beam field: a setter, a reader, and a non-default
# value. Parametrized so a broken key is named individually rather than hidden
# behind one composite assertion.
FIELD_SPECS = {
    "run_list": (lambda t, v: t.run_list_edit.setText(v), lambda t: t.run_list_edit.text(), "12345, 12346"),
    "ipts": (lambda t, v: t.ipts_edit.setText(v), lambda t: t.ipts_edit.text(), "36776"),
    "use_ipts_path_structure": (
        lambda t, v: t.ipts_toggle.setChecked(v),
        lambda t: t.ipts_toggle.isChecked(),
        True,
    ),
    "nexus_path": (lambda t, v: t.nexus_edit.setText(v), lambda t: t.nexus_edit.text(), "/tmp/nexus/"),
    "save_path": (lambda t, v: t.savepath_edit.setText(v), lambda t: t.savepath_edit.text(), "/tmp/out/"),
    "save_name": (lambda t, v: t.savename_edit.setText(v), lambda t: t.savename_edit.text(), "db_custom"),
    "DTCcut": (lambda t, v: t.DTCcut_spin.setValue(v), lambda t: t.DTCcut_spin.value(), 7.5),
    "DTCcut_config1": (lambda t, v: t.DTCcut1_spin.setValue(v), lambda t: t.DTCcut1_spin.value(), 8.25),
    "Icut": (lambda t, v: t.Icut_spin.setValue(v), lambda t: t.Icut_spin.value(), 3.5),
    "chopper_cut_offset": (lambda t, v: t.CutOffset_spin.setValue(v), lambda t: t.CutOffset_spin.value(), 2.25),
    "tofbin": (lambda t, v: t.tofbin_spin.setValue(v), lambda t: t.tofbin_spin.value(), 125.0),
    "tofmin": (lambda t, v: t.tofmin_spin.setValue(v), lambda t: t.tofmin_spin.value(), 3000.0),
    "tofmax": (lambda t, v: t.tofmax_spin.setValue(v), lambda t: t.tofmax_spin.value(), 55000.0),
    "y_ROI": (lambda t, v: t.yroi_edit.setText(v), lambda t: t.yroi_edit.text(), "110,160"),
    "x_ROI": (lambda t, v: t.lowres_edit.setText(v), lambda t: t.lowres_edit.text(), "60,200"),
    "plot": (lambda t, v: t.plot_cb.setChecked(v), lambda t: t.plot_cb.isChecked(), False),
    "cd_vals": (
        lambda t, v: setattr(t, "cd_vals", v),
        lambda t: t.cd_vals,
        {"mu_file": "/x", "Cd": [5.0], "flip_atten": True},
    ),
    "mod_vals": (
        lambda t, v: setattr(t, "mod_vals", v),
        lambda t: t.mod_vals,
        {"Chop2_cut_fn": [1.0, 2.0], "dMod": 15500.0, "t0": [3.0, 4.0]},
    ),
}


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
@pytest.mark.parametrize("field", sorted(FIELD_SPECS))
def test_direct_beam_field_round_trip(field):
    """Every persisted key survives a tab restart, named individually."""
    from launcher.apps.direct_beam import DirectBeamTab

    setter, getter, value = FIELD_SPECS[field]
    tab = DirectBeamTab()
    setter(tab, value)
    tab.save_settings()
    tab.deleteLater()

    tab2 = DirectBeamTab()
    read_back = getter(tab2)
    if isinstance(value, float):
        assert read_back == pytest.approx(value)
    else:
        assert read_back == value


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_saves_without_explicit_call():
    """The defense-in-depth wiring, not just save_settings() itself."""
    from launcher.apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    tab.ipts_edit.setText("36776")
    tab.ipts_edit.editingFinished.emit()
    tab.deleteLater()

    tab2 = DirectBeamTab()
    assert tab2.ipts_edit.text() == "36776"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_settings_reach_disk():
    """A store that never lands on disk persists nothing across a restart."""
    import os

    from launcher.apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    tab.ipts_edit.setText("36776")
    tab.save_settings()
    path = tab.settings.fileName()
    assert os.path.isfile(path), f"settings file not written: {path}"
    with open(path, encoding="utf-8") as handle:
        assert "36776" in handle.read()


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
@pytest.mark.parametrize("stored,expect_enabled", [(True, False), (False, True)])
def test_ipts_mode_applied_on_restore(stored, expect_enabled):
    """B1: the restored toggle must also apply its enable/disable mode.

    Without this the checkbox reads "use IPTS path structure" while the two
    manual path fields stay editable — the scientist types paths that
    _run_create_db never reads and the values are silently discarded.
    """
    from launcher.apps.direct_beam import DirectBeamTab

    s = QtCore.QSettings()
    s.setValue("direct_beam_use_ipts_path_structure", stored)
    s.sync()
    tab = DirectBeamTab()
    assert tab.ipts_toggle.isChecked() is stored
    assert tab.nexus_edit.isEnabled() is expect_enabled
    assert tab.savepath_edit.isEnabled() is expect_enabled
