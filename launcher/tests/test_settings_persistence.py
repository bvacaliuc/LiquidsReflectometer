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
def test_isolation_from_legacy_launcher():
    bare = QtCore.QSettings()
    bare.setValue("any_key", "legacy_value")
    bare.sync()

    QtCore.QCoreApplication.setOrganizationName("ORNL")
    QtCore.QCoreApplication.setApplicationName("lr_reduction_new_launcher")
    new = QtCore.QSettings()
    assert new.fileName() != bare.fileName()


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_direct_beam_first_launch_defaults():
    from launcher.apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    assert tab.ipts_edit.text() == ""
    assert tab.tofbin_spin.value() == pytest.approx(50.0)
    assert tab.tofmin_spin.value() == pytest.approx(0.0)
    assert tab.tofmax_spin.value() == pytest.approx(100000.0)
