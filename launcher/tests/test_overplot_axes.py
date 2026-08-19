import os
import shutil
from pathlib import Path

import pytest


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
    from launcher.apps.overplot import classify_file

    p = tmp_path / "DB_test.txt"
    p.write_text("# Header\n# columns = lambda intensity error\n1.0 100.0 1.0\n2.0 200.0 1.4\n")
    assert classify_file(str(p)) == "direct_beam"


def test_classify_refl_fixture(tmp_path):
    from launcher.apps.overplot import classify_file

    p = tmp_path / "REFL_test.txt"
    p.write_text("# header line A\n# Q [1/Angstrom] R dR dQ [FWHM]\n0.01 0.5 0.05 0.001\n0.02 0.4 0.04 0.001\n")
    assert classify_file(str(p)) == "reflectivity"


def test_classify_unknown_no_header(tmp_path):
    from launcher.apps.overplot import classify_file

    p = tmp_path / "garbled.txt"
    p.write_text("0.01 0.5\n0.02 0.4\n")
    assert classify_file(str(p)) == "unknown"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_overplot_db_labels(tmp_path):
    from launcher.apps.overplot import Overplot

    _seed_folder(tmp_path, "db_fixture.txt")
    w = Overplot()
    w.folder_edit.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "db_fixture.txt")
    w.plot_selected()
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "λ [Å]"
    assert ax.get_ylabel() == "I"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_overplot_refl_labels(tmp_path):
    from launcher.apps.overplot import Overplot

    _seed_folder(tmp_path, "refl_fixture.txt")
    w = Overplot()
    w.folder_edit.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "refl_fixture.txt")
    w.plot_selected()
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "Q [1/Å]"
    assert ax.get_ylabel() == "R"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_rq4_disabled_for_db(tmp_path):
    from launcher.apps.overplot import Overplot

    _seed_folder(tmp_path, "db_fixture.txt")
    w = Overplot()
    w.folder_edit.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "db_fixture.txt")
    w.plot_selected()
    assert not _rq4_is_enabled(w.ytransform_combo)


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_mixed_selection(tmp_path):
    from launcher.apps.overplot import Overplot

    _seed_folder(tmp_path, "db_fixture.txt", "refl_fixture.txt")
    w = Overplot()
    w.folder_edit.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "db_fixture.txt", "refl_fixture.txt")
    w.plot_selected()
    assert w._last_sel_mode == "mixed"
    assert not _rq4_is_enabled(w.ytransform_combo)
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_mode_persists():
    from launcher.apps.overplot import Overplot

    w = Overplot()
    w.plot_mode_combo.setCurrentText("Direct Beam")
    w.save_settings()
    w.deleteLater()

    w2 = Overplot()
    assert w2.plot_mode_combo.currentText() == "Direct Beam"


# The reduction writers put the reflectivity marker after a metadata preamble,
# so these tracked files carry it at lines 13-20 — outside any fixed-size
# window. Deliberately NOT globbed: the REFL_*.txt siblings are gitignored
# test-run byproducts and collect zero cases on a fresh clone.
REAL_REFLECTIVITY_FILES = (
    "reference_rq.txt",
    "reference_rq_201282.txt",
    "reference_rq_avg.txt",
    "reference_rq_avg_overlap.txt",
    "reference_short_nobck.txt",
)


def _repo_data(name):
    return Path(__file__).resolve().parents[2] / "tests" / "data" / name


@pytest.mark.parametrize("name", REAL_REFLECTIVITY_FILES)
def test_classify_real_reflectivity_corpus(name):
    """B1: the formats the tab actually consumes, not a synthetic stand-in."""
    from launcher.apps.overplot import classify_file

    path = _repo_data(name)
    assert path.is_file(), f"tracked fixture missing: {path}"
    assert classify_file(str(path)) == "reflectivity"


def test_classify_save_reduced_data_format(tmp_path):
    """B1: save_reduced_data.py is a second writer with a different marker."""
    from launcher.apps.overplot import classify_file

    p = tmp_path / "second_writer.txt"
    p.write_text("# Datafile created by lr_reduction\n# columns = Q, R, dR, dQ (sigma)\n0.01 0.5 0.05 0.001\n")
    assert classify_file(str(p)) == "reflectivity"


def test_classify_binary_file_is_unknown(tmp_path):
    """B1: a non-text file must classify unknown, not raise."""
    from launcher.apps.overplot import classify_file

    p = tmp_path / "blob.dat"
    p.write_bytes(b"\x00\x01\x02\xff\xfe")
    assert classify_file(str(p)) == "unknown"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_unknown_is_a_kind_in_homogeneity(tmp_path):
    """B2: one recognized DB file must not drag headerless files onto λ/I."""
    from launcher.apps.overplot import Overplot

    _seed_folder(tmp_path, "db_fixture.txt")
    (tmp_path / "headerless.dat").write_text("0.01 0.5\n0.02 0.4\n")
    w = Overplot()
    w.folder_edit.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "db_fixture.txt", "headerless.dat")
    w.plot_selected()
    assert w._last_sel_mode == "mixed"
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_rq4_reenabled_for_real_reflectivity(tmp_path):
    """B1 consequence: the primary case must not be worse than before the slug."""
    from launcher.apps.overplot import Overplot

    shutil.copy(_repo_data("reference_rq.txt"), tmp_path / "reference_rq.txt")
    w = Overplot()
    w.folder_edit.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "reference_rq.txt")
    w.plot_selected()
    assert w._last_sel_mode == "reflectivity"
    assert _rq4_is_enabled(w.ytransform_combo)
    ax = w.figure.axes[0]
    assert ax.get_xlabel() == "Q [1/Å]"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_popout_path_uses_resolved_labels(tmp_path, monkeypatch):
    """Kills the named revert: popout labels hardcoded back to 'x'/'y'."""
    from launcher.apps import overplot as overplot_module
    from launcher.apps.overplot import Overplot

    class _FakeAx:
        def __init__(self):
            self.xlabel = None
            self.ylabel = None

        def errorbar(self, *_a, **_k):
            pass

        def plot(self, *_a, **_k):
            pass

        def set_yscale(self, *_a, **_k):
            pass

        def set_xscale(self, *_a, **_k):
            pass

        def legend(self, *_a, **_k):
            pass

        def set_xlabel(self, value):
            self.xlabel = value

        def set_ylabel(self, value):
            self.ylabel = value

    class _FakePlt:
        def __init__(self):
            self.ax = _FakeAx()

        def figure(self, *_a, **_k):
            pass

        def gca(self):
            return self.ax

        def tight_layout(self, *_a, **_k):
            pass

        def show(self, *_a, **_k):
            pass

        def close(self, *_a, **_k):
            pass

    fake = _FakePlt()
    monkeypatch.setattr(overplot_module, "plt", fake)
    shutil.copy(_repo_data("reference_rq.txt"), tmp_path / "reference_rq.txt")
    w = Overplot()
    w.folder_edit.setText(str(tmp_path))
    w.populate_file_list(str(tmp_path))
    _select_files(w, "reference_rq.txt")
    w.canvas = None
    w.plot_selected()
    assert fake.ax.xlabel == "Q [1/Å]"
    assert fake.ax.ylabel == "R"


@pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")
def test_unreachable_saved_folder_is_not_erased():
    """B4: starting before /SNS mounts must not destroy the stored path."""
    from qtpy import QtCore

    from launcher.apps.overplot import Overplot

    s = QtCore.QSettings()
    s.setValue("overplot_folder", "/nonexistent/xyz")
    s.sync()
    Overplot()
    assert QtCore.QSettings().value("overplot_folder") == "/nonexistent/xyz"
