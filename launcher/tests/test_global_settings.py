"""GUI tests for the global-settings layer and the provenance badges (T3).

Thin, like T2's: the layer taxonomy is tested without Qt in
`tests/test_settings_resolver.py`. What is here is the wiring — that the dialog
reaches the shared store, that the launcher offers it, and that a badge reports
the origin the resolver actually recorded.
"""

import json
import subprocess
import sys
import textwrap

import pytest
from qtpy import QtCore, QtWidgets
from qtpy.QtTest import QTest

from launcher.apps.global_settings import (
    SETTINGS_GROUP,
    GlobalSettingsDialog,
    load_global_settings,
    save_global_settings,
)
from launcher.apps.settings_editor import SettingsEditorTab
from lr_reduction import field_spec as fs
from lr_reduction.settings_document import SettingsDocument
from lr_reduction.settings_resolver import (
    GLOBAL_WHITELIST,
    NotWhitelistedError,
    ResolutionContext,
    SettingsResolver,
)

pytestmark = pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")


def test_a_whitelisted_preference_round_trips_through_the_shared_store():
    save_global_settings({"qmax": 0.42})
    assert load_global_settings()["qmax"] == 0.42


def test_a_boolean_preference_survives_a_restart(tmp_path):
    """Read in a FRESH process, because that is where the bug lives.

    Measured: QSettings returns the cached typed value in the process that wrote
    it (`False`, a bool), but a new process reading the Ini file from disk gets
    the string `'false'` — and `bool('false')` is True. So a user who turns
    plotting off, then restarts the launcher, gets it back on.

    An in-process round trip cannot see this: it reads the cache, not the file.
    The first version of this test did exactly that and stayed green with the
    coercion removed.
    """
    save_global_settings({"plotON": False, "qmax": 0.42})
    root = QtCore.QSettings().fileName()

    program = textwrap.dedent(
        f"""
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from qtpy import QtCore
        QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
        settings = QtCore.QSettings({root!r}, QtCore.QSettings.IniFormat)
        QtCore.QCoreApplication.setOrganizationName({QtCore.QCoreApplication.organizationName()!r})
        QtCore.QCoreApplication.setApplicationName({QtCore.QCoreApplication.applicationName()!r})
        raw = settings.value("{SETTINGS_GROUP}/plotON")
        assert isinstance(raw, str), f"expected the on-disk string form, got {{type(raw).__name__}}"

        from lr_reduction import field_spec as fs
        coerced = fs.get("plotON").coerce(raw)
        assert coerced is False, f"a restart turned plotON into {{coerced!r}}"
        print("restart-clean")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, timeout=300
    )
    assert result.returncode == 0, result.stderr
    assert "restart-clean" in result.stdout


def test_the_loader_coerces_whatever_the_store_hands_back(monkeypatch):
    """The in-process half: force the on-disk string form and check the loader.

    Pairs with the restart test above — that one proves the string form really
    occurs, this one proves `load_global_settings` handles it.
    """
    save_global_settings({"plotON": False})
    real_value = QtCore.QSettings.value

    def as_stored_on_disk(self, key, *args, **kwargs):
        value = real_value(self, key, *args, **kwargs)
        return "false" if value is False else value

    monkeypatch.setattr(QtCore.QSettings, "value", as_stored_on_disk)
    restored = load_global_settings()["plotON"]
    assert restored is False
    assert isinstance(restored, bool)


def test_saving_a_non_whitelisted_field_is_refused():
    with pytest.raises(NotWhitelistedError, match="RB_Ymin"):
        save_global_settings({"RB_Ymin": [100]})
    assert "RB_Ymin" not in load_global_settings()


def test_clearing_a_preference_removes_it_from_the_store():
    """Blank means "let a later layer decide", not "store an empty value"."""
    save_global_settings({"qmax": 0.42})
    save_global_settings({})
    assert "qmax" not in load_global_settings()


def test_the_dialog_offers_exactly_the_whitelist():
    dialog = GlobalSettingsDialog()
    assert set(dialog.editors) == set(GLOBAL_WHITELIST)
    assert "RB_Ymin" not in dialog.editors


def test_the_dialog_saves_what_was_typed():
    dialog = GlobalSettingsDialog()
    editor = dialog.editors["qmax"]
    editor.clear()
    QTest.keyClicks(editor, "0.33")
    dialog.accept()
    assert load_global_settings()["qmax"] == 0.33


def test_a_blank_boolean_stays_unset():
    """A checkbox cannot express "unset", which is why booleans are combos.

    If it could not, opening the dialog once would set every boolean to False
    and silently outrank every experiment file.
    """
    dialog = GlobalSettingsDialog()
    assert dialog.editors["plotON"].currentText() == ""
    dialog.accept()
    assert "plotON" not in load_global_settings()


def test_the_dialog_loads_the_stored_value():
    save_global_settings({"peak_type": "gauss"})
    dialog = GlobalSettingsDialog()
    assert dialog.editors["peak_type"].currentText() == "gauss"


# --------------------------------------------------------------------------
# Provenance badges
# --------------------------------------------------------------------------


def _resolved_tab(**context):
    document, provenance = SettingsResolver(ResolutionContext(**context)).resolve_all()
    tab = SettingsEditorTab()
    tab.set_document(document, provenance)
    return tab, provenance


def test_a_badge_reports_the_layer_the_resolver_recorded():
    tab, provenance = _resolved_tab(
        global_settings={"qmax": 0.9},
        json_settings={"qmin": 0.002},
        json_detail="reduce_settings_up.json",
    )
    assert provenance["qmax"].source_layer == "a"
    assert tab.badges["qmax"].text() == "[a]"
    assert tab.badges["qmin"].text() == "[c]"
    assert tab.badges["dqbin"].text() == "[f]"


def test_a_badge_names_the_file_a_value_came_from():
    tab, _ = _resolved_tab(
        json_settings={"qmin": 0.002}, json_detail="reduce_settings_up.json"
    )
    assert "reduce_settings_up.json" in tab.badges["qmin"].toolTip()


def test_a_per_angle_column_header_carries_its_layer():
    """Arrays resolve as a unit, so provenance goes on the header, not the cell."""
    tab, _ = _resolved_tab(
        json_settings={"DBname": ["a.dat"]}, json_detail="reduce_settings.json"
    )
    column = fs.PER_ANGLE_NAMES.index("DBname")
    header = tab.angle_table.horizontalHeaderItem(column)
    assert header.text().endswith("[c]")
    assert "reduce_settings.json" in header.toolTip()


def test_badges_follow_a_replaced_resolution():
    tab, _ = _resolved_tab(global_settings={"qmax": 0.9})
    assert tab.badges["qmax"].text() == "[a]"

    document, provenance = SettingsResolver(
        ResolutionContext(json_settings={"qmax": 0.3}, json_detail="reduce_settings.json")
    ).resolve_all()
    tab.set_document(document, provenance)
    assert tab.badges["qmax"].text() == "[c]"


def test_the_badge_agrees_with_the_value_beside_it():
    """The pairing that makes a badge worth having."""
    tab, provenance = _resolved_tab(global_settings={"qmax": 0.9})
    assert tab.editors["qmax"].text() == "0.9"
    assert tab.badges["qmax"].text() == f"[{provenance['qmax'].source_layer}]"


# --------------------------------------------------------------------------
# The launcher offers it
# --------------------------------------------------------------------------


def test_the_launcher_has_a_global_settings_menu_entry():
    from launcher.new_launcher import LauncherWindow

    window = LauncherWindow()
    menus = [a.text() for a in window.menuBar().actions()]
    assert "&Settings" in menus
    assert "Global" in window.global_settings_action.text()


def test_the_menu_entry_opens_the_dialog(monkeypatch):
    """Measured through the action's own trigger, not by calling the slot."""
    from launcher.new_launcher import LauncherWindow

    opened = []
    monkeypatch.setattr(
        QtWidgets.QDialog, "exec_", lambda self: opened.append(type(self).__name__)
    )
    window = LauncherWindow()
    window.global_settings_action.trigger()
    assert opened == ["GlobalSettingsDialog"]


def test_the_launcher_still_carries_the_tabs():
    from launcher.new_launcher import LauncherWindow, ReductionInterface

    window = LauncherWindow()
    assert isinstance(window.centralWidget(), ReductionInterface)
    titles = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert "Settings editor" in titles


# --------------------------------------------------------------------------
# C1 — the resolver must actually be reachable from the shipped app
# --------------------------------------------------------------------------


def _resolve_and_wait(tab, timeout_ms=10000):
    """Press Resolve and let the worker finish.

    Discovery runs off the GUI thread, so a test has to wait for it — the same
    reason a stalled mount no longer freezes the launcher.
    """
    QTest.mouseClick(tab.resolve_button, QtCore.Qt.LeftButton)
    worker = tab._discovery_worker
    assert worker is not None, "Resolve did not start a worker"
    assert worker.wait(timeout_ms), "discovery worker did not finish"
    QtWidgets.QApplication.instance().processEvents()
    return tab


def _full_experiment_tree(tmp_path, ipts="IPTS-30101"):
    """ONE realistic tree, parametrized over tthd — not one tree per assertion.

    Holds both settings files, both templates and an unreadable file, so the
    up/down choice, the tthd==0 boundary, the two-note status path and the
    permission-denied guard are all exercised against the same fixture. The v2
    trees were each shaped to the single assertion they served, which is how a
    hardcoded tthd and a sorted-glob both survived.
    """
    autoreduce = tmp_path / ipts / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    (autoreduce / "reduce_settings_up.json").write_text(json.dumps({"qmin": 0.002}))
    (autoreduce / "reduce_settings_down.json").write_text(json.dumps({"qmin": 0.004}))
    (autoreduce / "template_up.xml").write_text("<Reduction/>")
    (autoreduce / "template_down.xml").write_text("<Reduction/>")
    return tmp_path


def _experiment_tree(tmp_path, ipts="IPTS-30101", tthd_up=True):
    autoreduce = tmp_path / ipts / "shared" / "autoreduce"
    autoreduce.mkdir(parents=True)
    name = "reduce_settings_up.json" if tthd_up else "reduce_settings_down.json"
    (autoreduce / name).write_text(json.dumps({"qmin": 0.002, "Sname": "from_experiment"}))
    return tmp_path


def test_the_production_path_resolves_and_populates_the_badges(tmp_path, monkeypatch):
    """The defect this whole cluster was about: nothing in the app called it.

    42 tests were green while `resolve_all` had zero production callers, so
    every badge rendered empty in the running launcher. This drives the button a
    scientist presses.
    """
    import lr_reduction.settings_resolver as resolver_module

    root = _experiment_tree(tmp_path)
    real_discover = resolver_module.discover_ipts_settings
    monkeypatch.setattr(
        "launcher.apps.settings_editor.discover_ipts_settings",
        lambda ipts, tthd=1.0, **_kw: real_discover(ipts, tthd=tthd, root=str(root)),
    )
    save_global_settings({"qmax": 0.42})

    tab = SettingsEditorTab()
    tab.ipts_edit.setText("IPTS-30101")
    _resolve_and_wait(tab)

    assert tab.provenance, "the resolver produced no provenance"
    assert tab.document.get("qmin") == 0.002
    assert tab.badges["qmin"].text() == "[c]"
    assert tab.badges["qmax"].text() == "[a]"
    assert tab.badges["dqbin"].text() == "[f]"
    assert "reduce_settings_up.json" in tab.status_label.text()


def test_saving_after_resolving_writes_the_provenance_sidecar(tmp_path, monkeypatch):
    """Save must route through save_resolution, not a bare document.save()."""
    from lr_reduction.settings_resolver import provenance_path

    target = tmp_path / "out.json"
    monkeypatch.setattr(
        QtWidgets.QFileDialog, "getSaveFileName",
        staticmethod(lambda *_a, **_k: (str(target), "")),
    )
    document, provenance = SettingsResolver(
        ResolutionContext(global_settings={"qmax": 0.42})
    ).resolve_all()
    tab = SettingsEditorTab()
    tab.set_document(document, provenance)
    tab.save_settings()

    assert target.exists()
    assert provenance_path(target).exists()
    assert json.loads(provenance_path(target).read_text())["qmax"]["source_layer"] == "a"


def test_editing_a_resolved_field_flips_its_badge_to_this_run():
    """C2c: an origin that stops tracking the value is worse than none.

    The badge used to keep naming the experiment file after the value had been
    replaced by hand — and named the wrong file at that.
    """
    document, provenance = SettingsResolver(
        ResolutionContext(json_settings={"qmax": 0.3}, json_detail="reduce_settings.json")
    ).resolve_all()
    tab = SettingsEditorTab()
    tab.set_document(document, provenance)
    assert tab.badges["qmax"].text() == "[c]"

    editor = tab.editors["qmax"]
    editor.setText("0.77")
    QTest.keyClick(editor, QtCore.Qt.Key_Return)

    assert tab.document.get("qmax") == 0.77
    assert tab.badges["qmax"].text() == "[b]"


def test_removing_an_angle_redraws_the_column_attributions():
    """A removal shifts every per-angle column the headers attribute."""
    document, provenance = SettingsResolver(
        ResolutionContext(
            json_settings={"DBname": ["a.dat", "b.dat"]}, json_detail="reduce_settings.json"
        )
    ).resolve_all()
    tab = SettingsEditorTab()
    tab.set_document(document, provenance)
    column = fs.PER_ANGLE_NAMES.index("DBname")
    assert tab.angle_table.horizontalHeaderItem(column).text().endswith("[c]")

    tab.angle_table.setCurrentCell(0, column)
    QTest.mouseClick(tab.remove_angle_button, QtCore.Qt.LeftButton)
    assert tab.document.get("DBname") == ["b.dat"]
    # AFTER, which is the whole point: the array is no longer the one the
    # experiment file supplied, so a header still naming reduce_settings.json
    # attributes this run's edit to a file that never said it. Asserting only
    # the before-state let the re-record be deleted with the test green.
    assert tab.angle_table.horizontalHeaderItem(column).text().endswith("[b]")


def test_adding_an_angle_reattributes_the_columns():
    """add_angle had no test at all."""
    document, provenance = SettingsResolver(
        ResolutionContext(
            json_settings={"DBname": ["a.dat"]}, json_detail="reduce_settings.json"
        )
    ).resolve_all()
    tab = SettingsEditorTab()
    tab.set_document(document, provenance)
    column = fs.PER_ANGLE_NAMES.index("DBname")
    assert tab.angle_table.horizontalHeaderItem(column).text().endswith("[c]")

    QTest.mouseClick(tab.add_angle_button, QtCore.Qt.LeftButton)
    assert tab.document.n_angles == 2
    assert tab.angle_table.horizontalHeaderItem(column).text().endswith("[b]")


# --------------------------------------------------------------------------
# C3 — the extracted renderer, and a validated dialog
# --------------------------------------------------------------------------


def test_the_dialog_uses_the_shared_renderer(monkeypatch):
    """C3: the fix must be the one T2 made, not a second copy of it.

    `str([50, 200])` is `"[50, 200]"`, which `coerce` reads back as the strings
    `'[50'` and `'200]'`. T2 fixed that in the settings tab, but the fix lived
    in a private method — so this file grew its own `str(value)`. No whitelisted
    field is list-typed *today* (the geometry group, which held the only one,
    was excluded by the C4(ii) decision), so the bug is currently unreachable
    through this dialog. That makes the property worth pinning rather than the
    symptom: this file must call the shared renderer, so a future whitelisted
    list field cannot resurrect it a third time.
    """
    calls = []
    real = fs.render_value
    monkeypatch.setattr(fs, "render_value", lambda value: calls.append(value) or real(value))

    save_global_settings({"qmax": 0.42})
    GlobalSettingsDialog()
    assert 0.42 in calls, "the dialog rendered a value without the shared renderer"


def test_the_shared_renderer_round_trips_a_list():
    """The property itself, independent of who calls it."""
    assert fs.render_value([50, 200]) == "50, 200"
    assert fs.get("data_x_range").coerce(fs.render_value([50, 200])) == [50, 200]


def test_the_dialog_refuses_a_value_that_fails_validation():
    """A preference outranks a guess and the default, so it must be valid.

    `dead_time=-5.0` used to persist and then outrank a measurement for every
    future experiment.
    """
    dialog = GlobalSettingsDialog()
    editor = dialog.editors["dead_time"]
    editor.clear()
    QTest.keyClicks(editor, "-5.0")
    dialog.accept()
    assert "dead_time" not in load_global_settings()


def test_a_raising_dialog_slot_does_not_abort(monkeypatch):
    dialog = GlobalSettingsDialog()
    monkeypatch.setattr(
        "launcher.apps.global_settings.save_global_settings",
        lambda _values: (_ for _ in ()).throw(RuntimeError("synthetic")),
    )
    dialog.accept()  # must not raise


# --------------------------------------------------------------------------
# v3 guards
# --------------------------------------------------------------------------


def test_the_gui_thread_stays_responsive_while_discovery_blocks(monkeypatch):
    """C7: a stalled FUSE mount BLOCKS — it does not raise.

    So `except OSError` and the slot guard are both irrelevant to it. Measured
    on the synchronous version with a 2 s stub: zero timer ticks in 2.00 s. This
    asserts the tick fires, which only happens if discovery is off the thread.
    """
    import time

    from lr_reduction.settings_resolver import ResolutionContext

    def slow(ipts, tthd=1.0, **_kw):
        time.sleep(0.75)
        return ResolutionContext(ipts=ipts, discovery_status="slow stub")

    tab = SettingsEditorTab()
    tab._discover = slow
    tab.ipts_edit.setText("IPTS-1")

    ticks = []
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start(50)

    QTest.mouseClick(tab.resolve_button, QtCore.Qt.LeftButton)
    assert tab.resolve_button.isEnabled() is False, "the button should be disabled while busy"

    deadline = time.monotonic() + 5.0
    while not ticks and time.monotonic() < deadline:
        QtWidgets.QApplication.instance().processEvents()
    timer.stop()

    assert ticks, "the GUI thread was blocked by discovery"
    assert tab._discovery_worker.wait(10000)
    QtWidgets.QApplication.instance().processEvents()
    assert tab.resolve_button.isEnabled() is True


@pytest.mark.parametrize(
    "tthd, expected",
    [
        pytest.param(1.0, "reduce_settings_up.json", id="up"),
        pytest.param(-1.0, "reduce_settings_down.json", id="down"),
        pytest.param(0.0, "reduce_settings_down.json", id="zero-is-down"),
    ],
)
def test_the_tthd_field_reaches_discovery(tmp_path, monkeypatch, tthd, expected):
    """C10: the UI field was ignored — discovery was called with a hardcoded 1.0.

    A scientist typing tthd=-1 silently resolved from the *up* file. The v2
    fixture never exercised it because its `tthd_up=False` parameter had no
    call site.
    """
    import lr_reduction.settings_resolver as resolver_module

    root = _full_experiment_tree(tmp_path)
    real = resolver_module.discover_ipts_settings
    tab = SettingsEditorTab()
    tab._discover = lambda ipts, tthd=1.0, **_kw: real(ipts, tthd=tthd, root=str(root))
    tab.ipts_edit.setText("IPTS-30101")
    tab.tthd_edit.setText(str(tthd))
    _resolve_and_wait(tab)

    assert expected in tab.status_label.text()


def test_an_unparseable_tthd_is_surfaced_not_guessed(tmp_path):
    """Its sign chooses the geometry, so guessing 1.0 resolves the wrong file."""
    tab = SettingsEditorTab()
    tab.ipts_edit.setText("IPTS-1")
    tab.tthd_edit.setText("banana")
    QTest.mouseClick(tab.resolve_button, QtCore.Qt.LeftButton)
    assert tab._discovery_worker is None
    assert "banana" in tab.status_label.text()


def test_an_edit_made_before_resolving_ranks_as_this_run(tmp_path):
    """C8: layer (b) had no production writer — pre-Resolve edits were discarded.

    Not outranked. Discarded, though (b) is the top of the taxonomy.
    """
    import lr_reduction.settings_resolver as resolver_module

    root = _full_experiment_tree(tmp_path)
    real = resolver_module.discover_ipts_settings
    tab = SettingsEditorTab()
    tab._discover = lambda ipts, tthd=1.0, **_kw: real(ipts, tthd=tthd, root=str(root))

    editor = tab.editors["qmin"]
    editor.setText("0.123")
    QTest.keyClick(editor, QtCore.Qt.Key_Return)
    assert tab.badges["qmin"].text() == "[b]"

    tab.ipts_edit.setText("IPTS-30101")
    _resolve_and_wait(tab)

    assert tab.document.get("qmin") == 0.123
    assert tab.badges["qmin"].text() == "[b]"


def test_reopening_a_saved_file_restores_its_badges(tmp_path, monkeypatch):
    """C8: the sidecar was written and never read back."""
    target = tmp_path / "saved.json"
    monkeypatch.setattr(
        QtWidgets.QFileDialog, "getSaveFileName",
        staticmethod(lambda *_a, **_k: (str(target), "")),
    )
    monkeypatch.setattr(
        QtWidgets.QFileDialog, "getOpenFileName",
        staticmethod(lambda *_a, **_k: (str(target), "")),
    )
    document, provenance = SettingsResolver(
        ResolutionContext(json_settings={"qmin": 0.002}, json_detail="reduce_settings.json")
    ).resolve_all()
    tab = SettingsEditorTab()
    tab.set_document(document, provenance)
    tab.save_settings()

    reopened = SettingsEditorTab()
    reopened.load_settings()
    assert reopened.provenance, "the sidecar beside the file was ignored"
    assert reopened.badges["qmin"].text() == "[c]"


def test_saving_keeps_every_field_the_editor_shows(tmp_path, monkeypatch):
    """C3: Save wrote normalize(), dropping fields that have editable columns.

    RBnum is runtime_owned AND per_angle, so it gets a table column a scientist
    can type into — and Save discarded it with no message.
    """
    target = tmp_path / "kept.json"
    monkeypatch.setattr(
        QtWidgets.QFileDialog, "getSaveFileName",
        staticmethod(lambda *_a, **_k: (str(target), "")),
    )
    document = SettingsDocument()
    document.add_angle(RBnum=197912, DBname="db.dat")
    tab = SettingsEditorTab()
    tab.set_document(document)
    tab.save_settings()

    written = json.loads(target.read_text())
    assert written["RBnum"] == [197912]
    for name in ("RBnum", "LambdaMinUse", "LambdaMaxUse"):
        assert name in written


def test_an_untouched_save_keeps_an_out_of_set_preference():
    """C6: setCurrentText is a no-op on a non-editable combo.

    So a stored value from an older version displayed blank, and a Save nobody
    touched coerced the blank to None and DELETED the preference — reverting to
    a default, which is different reduced data.
    """
    save_global_settings({"DetResFn": "rectangular"})
    settings = QtCore.QSettings()
    settings.setValue(f"{SETTINGS_GROUP}/DetResFn", "bogus_from_older_version")
    settings.sync()

    dialog = GlobalSettingsDialog()
    assert dialog.editors["DetResFn"].currentText() == "bogus_from_older_version"
    dialog.accept()
    assert load_global_settings().get("DetResFn") == "bogus_from_older_version"


def test_a_list_valued_preference_survives_as_numbers(monkeypatch):
    """C4: QSettings returns a multi-entry value as a LIST of str.

    The old guard coerced only the `str` branch, so a list-valued preference
    entered layer (a) as strings and was written to the settings file, where the
    reduction did arithmetic on them.
    """
    real_value = QtCore.QSettings.value
    real_contains = QtCore.QSettings.contains

    def as_stored_list(self, key, *args, **kwargs):
        if key.endswith("data_x_range"):
            return ["50", "200"]
        return real_value(self, key, *args, **kwargs)

    def contains(self, key):
        return True if key.endswith("data_x_range") else real_contains(self, key)

    monkeypatch.setattr(QtCore.QSettings, "value", as_stored_list)
    monkeypatch.setattr(QtCore.QSettings, "contains", contains)
    monkeypatch.setattr(
        "launcher.apps.global_settings.GLOBAL_WHITELIST",
        tuple(GLOBAL_WHITELIST) + ("data_x_range",),
    )
    restored = load_global_settings()["data_x_range"]
    assert restored == [50, 200]
    assert all(isinstance(entry, int) for entry in restored)


def test_the_ui_label_does_not_claim_the_data_outranks_a_preference():
    """C2: the label told a scientist the opposite of the resolution order.

    A string assertion is fair here — the label is the artifact under test.
    """
    dialog = GlobalSettingsDialog()
    labels = [
        w.text() for w in dialog.findChildren(QtWidgets.QLabel) if "personal defaults" in w.text()
    ]
    assert labels, "the explanatory label is gone"
    text = labels[0]
    assert "or the data itself" not in text
    assert "outrank" in text
