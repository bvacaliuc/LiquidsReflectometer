"""The "Time resolved" tab (upstream add-time-slicing, intake time-slicing-reconcile, plan T8).

The tab follows the launcher's conventions: every validation failure and every reduction error is reported in its
panel, never in a modal box, and never swallowed; the Reduce button is disabled while a reduction runs; the inputs
round-trip through QSettings; the tab is reachable from the launcher. The reductions themselves are stand-ins that
record their arguments (the library has its own tests): this file is about the tab.
"""

from types import SimpleNamespace

import pytest
from qtpy import QtCore, QtWidgets
from qtpy.QtTest import QTest

GOOD = {"experiment": "IPTS-00001", "run": "230001", "settings": "/tmp/reduce_settings.json"}


@pytest.fixture
def boxes(monkeypatch):
    """Every QMessageBox use, recorded rather than shown: the tab reports in its panel."""
    seen = []
    for name in ("warning", "information", "critical", "question", "about"):
        monkeypatch.setattr(QtWidgets.QMessageBox, name,
                            staticmethod(lambda *_args, _name=name, **_kwargs: seen.append(_name)))
    monkeypatch.setattr(QtWidgets.QMessageBox, "exec_", lambda _box: seen.append("exec_"))
    return seen


@pytest.fixture
def tab(isolated_qapp, monkeypatch, boxes):  # noqa: ARG001 -- isolated_qapp: a QApplication and a per-test QSettings
    """The tab, with both reductions replaced by stand-ins that record their arguments and whether Reduce was
    enabled while they ran."""
    from launcher.apps import time_resolved

    calls, result = [], {"value": ([["slice 1"], ["slice 2"]], None)}

    def stand_in(kind):
        def reduce(*args, **kwargs):
            calls.append({"kind": kind, "args": args, "kwargs": kwargs, "enabled": widget.process_btn.isEnabled()})
            if isinstance(result["value"], Exception):
                raise result["value"]
            return result["value"]
        return reduce

    monkeypatch.setattr(time_resolved, "reduce_time_slices", stand_in("slices"))
    monkeypatch.setattr(time_resolved, "reduce_time_list", stand_in("list"))
    widget = time_resolved.TimeResolvedTab()
    yield SimpleNamespace(widget=widget, calls=calls, result=result, boxes=boxes)
    widget.close()


def fill(widget, mode="Number of slices", starts="", ends="", **fields):
    values = {**GOOD, **fields}
    widget.experiment_edit.setText(values["experiment"])
    widget.run_edit.setText(values["run"])
    widget.settings_edit.setText(values["settings"])
    widget.mode_combo.setCurrentIndex(widget.mode_combo.findText(mode))
    widget.start_times_edit.setText(starts)
    widget.end_times_edit.setText(ends)


def panel(widget):
    return widget.log_edit.toPlainText()


@pytest.mark.parametrize("fields, message", [
    ({"run": ""}, "run number"),
    ({"run": "two hundred"}, "integer"),
    ({"experiment": ""}, "experiment"),
    ({"settings": ""}, "settings"),
    ({"mode": "Time values"}, "start and end time"),
    ({"mode": "Time values", "starts": "0, 80", "ends": "80"}, "same length"),
], ids=["missing run", "bad run number", "missing experiment", "missing settings", "missing time ranges",
        "mismatched time lists"])
def test_every_validation_failure_is_a_panel_message(tab, fields, message):
    """T8a: each missing or malformed input is named in the panel; nothing is reduced, no box opens, and Reduce
    stays available."""
    fill(tab.widget, **fields)
    QTest.mouseClick(tab.widget.process_btn, QtCore.Qt.LeftButton)
    assert message in panel(tab.widget), panel(tab.widget)
    assert tab.calls == [] and tab.boxes == []
    assert tab.widget.process_btn.isEnabled()


@pytest.mark.parametrize("mode", ["Number of slices", "Time values"])
def test_run_reports_completion_in_panel_and_reenables_the_button(tab, mode):
    """T8b: a reduction runs with Reduce disabled, reports its completion in the panel (no box), and leaves Reduce
    enabled again. The slices mode passes the number of slices; the time-values mode the parsed windows."""
    fill(tab.widget, mode=mode, starts="0, 80", ends="80, 136")
    tab.widget.num_slices_spin.setValue(4)
    QTest.mouseClick(tab.widget.process_btn, QtCore.Qt.LeftButton)
    (call,) = tab.calls
    assert call["enabled"] is False
    if mode == "Number of slices":
        assert call["kind"] == "slices" and call["args"] == (230001, GOOD["settings"], GOOD["experiment"], 4)
    else:
        assert call["kind"] == "list"
        assert call["args"] == (230001, GOOD["settings"], GOOD["experiment"], [0.0, 80.0], [80.0, 136.0])
    assert call["kwargs"]["show_plots"] is False
    assert "Completed reduction: 2 output slice(s)" in panel(tab.widget), panel(tab.widget)
    assert tab.boxes == [] and tab.widget.process_btn.isEnabled()


def test_a_reduction_error_is_reported_not_swallowed(tab):
    """T8c: an error inside the reduction reaches the panel with its text (the slot is guarded, nothing swallows
    it), no box opens, and Reduce is enabled again."""
    tab.result["value"] = ValueError("No reduced result data for window [20.0, 30.0) of run 230001")
    fill(tab.widget)
    QTest.mouseClick(tab.widget.process_btn, QtCore.Qt.LeftButton)
    assert "No reduced result data for window [20.0, 30.0)" in panel(tab.widget), panel(tab.widget)
    assert tab.boxes == [] and tab.widget.process_btn.isEnabled()


def test_saving_before_any_plot_is_a_panel_message(tab):
    """T8: with nothing plotted yet, Save figure says so in the panel instead of opening a box."""
    QTest.mouseClick(tab.widget.save_fig_btn, QtCore.Qt.LeftButton)
    assert "no figure" in panel(tab.widget).lower(), panel(tab.widget)
    assert tab.boxes == []


def test_the_inputs_round_trip_through_qsettings(tab):
    """T8: what a reduction was started with is what the next tab opens with."""
    from launcher.apps import time_resolved

    fill(tab.widget, mode="Time values", starts="0, 80", ends="80, 136")
    tab.widget.output_edit.setText("/tmp/out")
    tab.widget.subname_edit.setText("kinetics")
    tab.widget.num_slices_spin.setValue(5)
    QTest.mouseClick(tab.widget.process_btn, QtCore.Qt.LeftButton)
    reopened = time_resolved.TimeResolvedTab()
    try:
        assert (reopened.experiment_edit.text(), reopened.run_edit.text(), reopened.settings_edit.text()) == (
            GOOD["experiment"], GOOD["run"], GOOD["settings"])
        assert (reopened.output_edit.text(), reopened.subname_edit.text()) == ("/tmp/out", "kinetics")
        assert reopened.mode_combo.currentText() == "Time values" and reopened.num_slices_spin.value() == 5
        assert (reopened.start_times_edit.text(), reopened.end_times_edit.text()) == ("0, 80", "80, 136")
    finally:
        reopened.close()


def test_a_stored_slice_count_that_is_not_a_number_keeps_the_default(tab):
    """T8: QSettings holds what was stored; a slice count that is not a number opens with the default, and the tab
    opens."""
    from launcher.apps import time_resolved

    tab.widget.settings.setValue("time_resolved_num_slices", "many")
    reopened = time_resolved.TimeResolvedTab()
    try:
        assert reopened.num_slices_spin.value() == 2
    finally:
        reopened.close()


def test_the_launcher_carries_the_tab_after_the_others(isolated_qapp):  # noqa: ARG001
    """T8: the tab is reachable from the launcher, after the tabs that were there before it."""
    from launcher.apps.time_resolved import TimeResolvedTab
    from launcher.new_launcher import ReductionInterface

    window = ReductionInterface()
    try:
        titles = [window.tabText(i) for i in range(window.count())]
        assert titles == ["Overplot", "Direct beam", "Batch file", "Settings editor", "SLD calculator",
                          "Time resolved"], titles
        assert isinstance(window.time_resolved_tab, TimeResolvedTab)
    finally:
        window.close()
