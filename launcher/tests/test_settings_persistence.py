from qtpy import QtCore


def test_direct_beam_ipts_persists(isolated_qapp):
    from apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    tab.ipts_edit.setText("36776")
    tab.save_settings()
    tab.deleteLater()

    tab2 = DirectBeamTab()
    assert tab2.ipts_edit.text() == "36776"


def test_direct_beam_cd_vals_round_trip(isolated_qapp):
    from apps.direct_beam import DirectBeamTab

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


def test_direct_beam_corrupt_cd_vals_tolerated(isolated_qapp):
    from apps.direct_beam import DirectBeamTab

    s = QtCore.QSettings()
    s.setValue("direct_beam_cd_vals", "not valid json {{")
    s.sync()
    tab = DirectBeamTab()
    assert isinstance(tab.cd_vals, dict)


def test_overplot_saves_ytransform(isolated_qapp):
    from apps.overplot import Overplot

    tab = Overplot()
    tab.ytransform_combo.setCurrentText("R*Q^4")
    tab.save_settings()
    s = QtCore.QSettings()
    assert s.value("overplot_ytransform") == "R*Q^4"


def test_roi_selector_ipts_persists(isolated_qapp):
    from apps.roi_selector import ROISelector

    tab = ROISelector()
    tab.ipts_edit.setText("36776")
    tab.save_settings()
    tab.deleteLater()

    tab2 = ROISelector()
    assert tab2.ipts_edit.text() == "36776"


def test_isolation_from_legacy_launcher(isolated_qapp, tmp_path):
    bare = QtCore.QSettings()
    bare.setValue("any_key", "legacy_value")
    bare.sync()

    QtCore.QCoreApplication.setOrganizationName("ORNL")
    QtCore.QCoreApplication.setApplicationName("lr_reduction_new_launcher")
    new = QtCore.QSettings()
    assert new.fileName() != bare.fileName()


def test_direct_beam_first_launch_defaults(isolated_qapp):
    from apps.direct_beam import DirectBeamTab

    tab = DirectBeamTab()
    assert tab.ipts_edit.text() == ""
