import pytest
from qtpy import QtCore
from qtpy.QtWidgets import QMessageBox


def _check(widget, name, state=QtCore.Qt.Checked):
    for i in range(widget.file_list.count()):
        item = widget.file_list.item(i)
        if item.text() == name:
            item.setCheckState(state)


def _states(widget):
    return {
        widget.file_list.item(i).text(): widget.file_list.item(i).checkState()
        for i in range(widget.file_list.count())
    }


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_refresh_button_exists():
    from launcher.apps.overplot import Overplot

    tab = Overplot()
    assert hasattr(tab, "refresh_btn")
    assert tab.refresh_btn.text() == "Refresh"
    assert tab.refresh_btn.toolTip()


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_refresh_no_folder(monkeypatch):
    from launcher.apps.overplot import Overplot

    monkeypatch.setattr(QMessageBox, "warning", lambda *_a, **_k: None)
    tab = Overplot()
    tab.folder_edit.setText("")
    tab.refresh()
    assert tab.folder_edit.text() == ""


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_refresh_preserves_check_state(tmp_path):
    from launcher.apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("0.01 0.5\n")
    b = tmp_path / "b.dat"
    b.write_text("0.01 0.7\n")
    tab = Overplot()
    tab.folder_edit.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    _check(tab, "a.dat")
    tab.refresh()
    states = _states(tab)
    assert states["a.dat"] == QtCore.Qt.Checked
    assert states["b.dat"] == QtCore.Qt.Unchecked


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_refresh_picks_up_new_files(tmp_path):
    from launcher.apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("0.01 0.5\n")
    tab = Overplot()
    tab.folder_edit.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    (tmp_path / "c.dat").write_text("0.01 0.9\n")
    tab.refresh()
    items = [tab.file_list.item(i).text() for i in range(tab.file_list.count())]
    assert "c.dat" in items


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_refresh_drops_removed(tmp_path, monkeypatch):
    from launcher.apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("0.01 0.5\n")
    b = tmp_path / "b.dat"
    b.write_text("0.01 0.7\n")
    tab = Overplot()
    tab.folder_edit.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    _check(tab, "b.dat")
    b.unlink()
    captured = {}
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **_k: captured.setdefault("info", a))
    tab.refresh()
    items = [tab.file_list.item(i).text() for i in range(tab.file_list.count())]
    assert "b.dat" not in items
    assert "info" in captured


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_refresh_rereads_content(tmp_path):
    from launcher.apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("# Q R dR\n0.01 0.5 0.05\n0.02 0.4 0.04\n")
    tab = Overplot()
    tab.folder_edit.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    _check(tab, "a.dat")
    tab.plot_selected()
    a.write_text("# Q R dR\n0.01 0.9 0.09\n0.02 0.7 0.07\n")
    tab.refresh()
    ax = tab.figure.axes[0]
    line = ax.lines[0]
    ydata = line.get_ydata()
    assert ydata[0] == pytest.approx(0.9)


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_refresh_unmounted_folder(monkeypatch):
    from launcher.apps.overplot import Overplot

    tab = Overplot()
    tab.folder_edit.setText("/nonexistent/path/12345")
    captured = {}
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **_k: captured.setdefault("crit", a))
    tab.refresh()
    assert "crit" in captured
    assert tab.folder_edit.text() == "/nonexistent/path/12345"
