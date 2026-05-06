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


def test_refresh_button_exists(isolated_qapp):
    from apps.overplot import Overplot

    tab = Overplot()
    assert hasattr(tab, "refresh_btn")
    assert tab.refresh_btn.text() == "Refresh"
    assert tab.refresh_btn.toolTip()


def test_refresh_no_folder(isolated_qapp):
    from apps.overplot import Overplot

    tab = Overplot()
    tab.folder_label.setText("")
    tab.refresh()
    assert tab.folder_label.text() == ""


def test_refresh_preserves_check_state(isolated_qapp, tmp_path):
    from apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("0.01 0.5\n")
    b = tmp_path / "b.dat"
    b.write_text("0.01 0.7\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    _check(tab, "a.dat")
    tab.refresh()
    states = _states(tab)
    assert states["a.dat"] == QtCore.Qt.Checked
    assert states["b.dat"] == QtCore.Qt.Unchecked


def test_refresh_picks_up_new_files(isolated_qapp, tmp_path):
    from apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("0.01 0.5\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    (tmp_path / "c.dat").write_text("0.01 0.9\n")
    tab.refresh()
    items = [tab.file_list.item(i).text() for i in range(tab.file_list.count())]
    assert "c.dat" in items


def test_refresh_drops_removed(isolated_qapp, tmp_path, monkeypatch):
    from apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("0.01 0.5\n")
    b = tmp_path / "b.dat"
    b.write_text("0.01 0.7\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    _check(tab, "b.dat")
    b.unlink()
    captured = {}
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: captured.setdefault("info", a))
    tab.refresh()
    items = [tab.file_list.item(i).text() for i in range(tab.file_list.count())]
    assert "b.dat" not in items
    assert "info" in captured


def test_refresh_rereads_content(isolated_qapp, tmp_path):
    from apps.overplot import Overplot

    a = tmp_path / "a.dat"
    a.write_text("# Q R dR\n0.01 0.5 0.05\n0.02 0.4 0.04\n")
    tab = Overplot()
    tab.folder_label.setText(str(tmp_path))
    tab.populate_file_list(str(tmp_path))
    _check(tab, "a.dat")
    tab.plot_selected()
    a.write_text("# Q R dR\n0.01 0.9 0.09\n0.02 0.7 0.07\n")
    tab.refresh()
    ax = tab.figure.axes[0]
    line = ax.lines[0]
    ydata = line.get_ydata()
    assert ydata[0] == pytest.approx(0.9)


def test_refresh_unmounted_folder(isolated_qapp, monkeypatch):
    from apps.overplot import Overplot

    tab = Overplot()
    tab.folder_label.setText("/nonexistent/path/12345")
    captured = {}
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: captured.setdefault("crit", a))
    tab.refresh()
    assert "crit" in captured
    assert tab.folder_label.text() == "/nonexistent/path/12345"
