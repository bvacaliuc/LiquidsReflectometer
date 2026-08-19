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


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_ensure_identity_does_not_clobber_existing():
    """Idempotent and non-clobbering: a test fixture's throwaway identity (or a
    second call) must survive, or tabs would drag every store to the
    production identity mid-session."""
    from launcher.app_identity import ensure_identity

    before = (
        QtCore.QCoreApplication.organizationName(),
        QtCore.QCoreApplication.applicationName(),
    )
    ensure_identity()
    ensure_identity()
    after = (
        QtCore.QCoreApplication.organizationName(),
        QtCore.QCoreApplication.applicationName(),
    )
    assert after == before


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_ensure_identity_installs_when_unset():
    """Restores the identity itself: installing the production org/app
    process-wide and leaving it there is the very leak B2 was rejected for —
    a later test would resolve QSettings to the developer's real config."""
    from launcher import app_identity

    saved = (
        QtCore.QCoreApplication.organizationName(),
        QtCore.QCoreApplication.organizationDomain(),
        QtCore.QCoreApplication.applicationName(),
    )
    try:
        QtCore.QCoreApplication.setOrganizationName("")
        QtCore.QCoreApplication.setOrganizationDomain("")
        QtCore.QCoreApplication.setApplicationName("")
        app_identity.ensure_identity()
        assert QtCore.QCoreApplication.organizationName() == app_identity.ORG_NAME
        assert QtCore.QCoreApplication.organizationDomain() == app_identity.ORG_DOMAIN
        assert QtCore.QCoreApplication.applicationName() == app_identity.APP_NAME
    finally:
        QtCore.QCoreApplication.setOrganizationName(saved[0])
        QtCore.QCoreApplication.setOrganizationDomain(saved[1])
        QtCore.QCoreApplication.setApplicationName(saved[2])


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_migrate_legacy_settings_copies_and_restores_identity():
    """The migration reads an org-less store, so it mutates the process-global
    identity; it must put it back even though it succeeded."""
    from launcher import app_identity

    identity_before = (
        QtCore.QCoreApplication.organizationName(),
        QtCore.QCoreApplication.organizationDomain(),
        QtCore.QCoreApplication.applicationName(),
    )

    org, domain, name = identity_before
    QtCore.QCoreApplication.setOrganizationName("")
    QtCore.QCoreApplication.setOrganizationDomain("")
    QtCore.QCoreApplication.setApplicationName("")
    legacy = QtCore.QSettings()
    legacy.setValue("overplot_folder", "/legacy/folder")
    legacy.setValue("overplot_xscale", "log")
    legacy.sync()
    QtCore.QCoreApplication.setOrganizationName(org)
    QtCore.QCoreApplication.setOrganizationDomain(domain)
    QtCore.QCoreApplication.setApplicationName(name)

    app_identity.migrate_legacy_settings()

    current = QtCore.QSettings()
    assert current.value("overplot_folder") == "/legacy/folder"
    assert current.value("overplot_xscale") == "log"
    identity_after = (
        QtCore.QCoreApplication.organizationName(),
        QtCore.QCoreApplication.organizationDomain(),
        QtCore.QCoreApplication.applicationName(),
    )
    assert identity_after == identity_before


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_migrate_legacy_settings_never_overwrites():
    """One-shot: a value the user has already set in the new store wins."""
    from launcher import app_identity

    current = QtCore.QSettings()
    current.setValue("overplot_folder", "/current/folder")
    current.sync()
    app_identity.migrate_legacy_settings()
    assert QtCore.QSettings().value("overplot_folder") == "/current/folder"
