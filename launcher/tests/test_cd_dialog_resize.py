def test_cd_dialog_is_qdialog(isolated_qapp):
    from apps.direct_beam import CdSettingsDialog
    from qtpy.QtWidgets import QDialog, QMessageBox

    dlg = CdSettingsDialog()
    assert isinstance(dlg, QDialog)
    assert not isinstance(dlg, QMessageBox)


def test_cd_edit_minimum_width(isolated_qapp):
    from apps.direct_beam import CdSettingsDialog

    dlg = CdSettingsDialog(
        defaults={"mu_file": "", "Cd": [5, 126.5, 249.5, 499.0], "flip_atten": False}
    )
    assert dlg.cd_edit.minimumWidth() >= 320


def test_cd_dialog_size_hint(isolated_qapp):
    from apps.direct_beam import CdSettingsDialog

    dlg = CdSettingsDialog(
        defaults={"mu_file": "/x/y", "Cd": [5, 126.5, 249.5, 499.0], "flip_atten": False}
    )
    fm = dlg.cd_edit.fontMetrics()
    needed = fm.horizontalAdvance("5, 126.5, 249.5, 499.0") + 16
    assert dlg.sizeHint().width() >= needed


def test_moderator_dialog_is_qdialog(isolated_qapp):
    from apps.direct_beam import ModeratorDialog
    from qtpy.QtWidgets import QDialog, QMessageBox

    dlg = ModeratorDialog()
    assert isinstance(dlg, QDialog)
    assert not isinstance(dlg, QMessageBox)


def test_get_values_round_trip(isolated_qapp):
    from apps.direct_beam import CdSettingsDialog

    dlg = CdSettingsDialog(
        defaults={"mu_file": "/x/y", "Cd": [5, 126.5, 249.5, 499.0], "flip_atten": True}
    )
    vals = dlg.get_values()
    assert vals["mu_file"] == "/x/y"
    assert vals["Cd"] == [5.0, 126.5, 249.5, 499.0]
    assert vals["flip_atten"] is True


def test_reset_defaults(isolated_qapp):
    from apps.direct_beam import CdSettingsDialog

    initial = {"mu_file": "/initial", "Cd": [1.0], "flip_atten": False}
    working = {"mu_file": "/working", "Cd": [9.0], "flip_atten": True}
    dlg = CdSettingsDialog(defaults=working, initial_defaults=initial)
    dlg._reset_defaults()
    vals = dlg.get_values()
    assert vals["mu_file"] == "/initial"
    assert vals["Cd"] == [1.0]
    assert vals["flip_atten"] is False
