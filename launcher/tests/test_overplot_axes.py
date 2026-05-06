import os
import shutil


def _seed_folder(folder, *fixture_names):
    """Copy named fixture files from launcher/tests/data into folder."""
    fixture_root = os.path.join(os.path.dirname(__file__), "data")
    for name in fixture_names:
        shutil.copy(os.path.join(fixture_root, name), os.path.join(folder, name))


def _select_files(widget, *filenames):
    from qtpy import QtCore

    targets = set(filenames)
    for i in range(widget.file_list.count()):
        item = widget.file_list.item(i)
        if item.text() in targets:
            item.setCheckState(QtCore.Qt.Checked)


def _rq4_is_enabled(combo):
    from qtpy import QtCore

    idx = combo.findText("R*Q^4")
    if idx < 0:
        return False
    item = combo.model().item(idx)
    return bool(item.flags() & QtCore.Qt.ItemIsEnabled)


def test_classify_db_fixture(tmp_path):
    from apps.overplot import classify_file

    p = tmp_path / "DB_test.txt"
    p.write_text(
        "# Header\n# columns = lambda intensity error\n1.0 100.0 1.0\n2.0 200.0 1.4\n"
    )
    assert classify_file(str(p)) == "direct_beam"


def test_classify_refl_fixture(tmp_path):
    from apps.overplot import classify_file

    p = tmp_path / "REFL_test.txt"
    p.write_text(
        "# header line A\n"
        "# Q [1/Angstrom] R dR dQ [FWHM]\n"
        "0.01 0.5 0.05 0.001\n0.02 0.4 0.04 0.001\n"
    )
    assert classify_file(str(p)) == "reflectivity"


def test_classify_unknown_no_header(tmp_path):
    from apps.overplot import classify_file

    p = tmp_path / "garbled.txt"
    p.write_text("0.01 0.5\n0.02 0.4\n")
    assert classify_file(str(p)) == "unknown"


def test_overplot_db_labels(isolated_qapp, tmp_path):
    from apps.overplot import Overplot

    _seed_folder(tmp_path, "db_fixture.txt")
    w = Overplot()
    w.folder_label.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "db_fixture.txt")
    w.plot_selected()
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "λ [Å]"
    assert ax.get_ylabel() == "I"


def test_overplot_refl_labels(isolated_qapp, tmp_path):
    from apps.overplot import Overplot

    _seed_folder(tmp_path, "refl_fixture.txt")
    w = Overplot()
    w.folder_label.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "refl_fixture.txt")
    w.plot_selected()
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "Q [1/Å]"
    assert ax.get_ylabel() == "R"


def test_rq4_disabled_for_db(isolated_qapp, tmp_path):
    from apps.overplot import Overplot

    _seed_folder(tmp_path, "db_fixture.txt")
    w = Overplot()
    w.folder_label.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "db_fixture.txt")
    w.plot_selected()
    assert not _rq4_is_enabled(w.ytransform_combo)


def test_mixed_selection(isolated_qapp, tmp_path):
    from apps.overplot import Overplot

    _seed_folder(tmp_path, "db_fixture.txt", "refl_fixture.txt")
    w = Overplot()
    w.folder_label.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "db_fixture.txt", "refl_fixture.txt")
    w.plot_selected()
    assert w._last_sel_mode == "mixed"
    assert not _rq4_is_enabled(w.ytransform_combo)
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"


def test_mode_persists(isolated_qapp):
    from apps.overplot import Overplot

    w = Overplot()
    w.plot_mode_combo.setCurrentText("Direct Beam")
    w.save_settings()
    w.deleteLater()

    w2 = Overplot()
    assert w2.plot_mode_combo.currentText() == "Direct Beam"
