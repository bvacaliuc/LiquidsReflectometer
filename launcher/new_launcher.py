#!/usr/bin/env python
import sys

from qtpy.QtWidgets import QApplication, QGridLayout, QMainWindow, QTabWidget, QWidget

from launcher.app_identity import ensure_identity, migrate_legacy_settings
from launcher.apps.direct_beam import DirectBeamTab
from launcher.apps.file_batch import FileBatchTab
from launcher.apps.global_settings import GlobalSettingsDialog
from launcher.apps.overplot import Overplot
from launcher.apps.settings_editor import SettingsEditorTab
from launcher.apps.sld_calculator import SLD

#REFERENCE_DIRECTIVE = "Click to choose a 60Hz reference R(Q) file"
#TEMPLATE_DIRECTIVE = "Click to choose a 30Hz template"
#OUTPUT_DIR_DIRECTIVE = "Click to choose an output directory"

class ReductionInterface(QTabWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("New Reflectometry Launcher")
        layout = QGridLayout()
        self.setLayout(layout)

        # Overplot tab
        tab_id = 0
        self.overplot_tab = Overplot()
        self.addTab(self.overplot_tab, "Overplot")
        self.setTabText(tab_id, "Overplot")

        # Direct beam processing tab
        tab_id += 1
        self.direct_beam_tab = DirectBeamTab()
        self.addTab(self.direct_beam_tab, "Direct beam")
        self.setTabText(tab_id, "Direct beam")

        # Batch file-driven reduction tab (DAT/JSON)
        tab_id += 1
        self.file_batch_tab = FileBatchTab()
        self.addTab(self.file_batch_tab, "Batch file")
        self.setTabText(tab_id, "Batch file")

        ## ROI selector
        #tab_id += 1
        #self.roi_tab = ROISelector()
        #self.addTab(self.roi_tab, "ROI selector")
        #self.setTabText(tab_id, "ROI selector")

        # Reduction settings editor. Supersedes the JSONSettingsBuilderTab this
        # module imported in a comment for a module that never existed
        # (`git log --all -S json_settings_builder` finds only the comment).
        tab_id += 1
        self.settings_editor_tab = SettingsEditorTab()
        self.addTab(self.settings_editor_tab, "Settings editor")
        self.setTabText(tab_id, "Settings editor")

        # SLD calculator
        tab_id += 1
        self.sld_tab = SLD()
        self.addTab(self.sld_tab, "SLD calculator")
        self.setTabText(tab_id, "SLD calculator")

        ## Batch template reduction tab
        #tab_id += 1
        #self.template_batch_tab = TemplateBatchTab()
        #self.addTab(self.template_batch_tab, "Batch template")
        #self.setTabText(tab_id, "Batch template")

class LauncherWindow(QMainWindow):
    """Menu bar around the tab widget.

    ReductionInterface stays a QTabWidget: it is what the tests construct, and
    turning it into a QMainWindow to hang one menu off would change the shape
    every existing caller depends on. The shell is additive instead.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Reflectometry Launcher")
        self.tabs = ReductionInterface()
        self.setCentralWidget(self.tabs)

        settings_menu = self.menuBar().addMenu("&Settings")
        self.global_settings_action = settings_menu.addAction("&Global reduction settings...")
        self.global_settings_action.setStatusTip(
            "Your personal defaults, applied to every experiment unless something more specific overrides them"
        )
        self.global_settings_action.triggered.connect(self.open_global_settings)

    def open_global_settings(self):
        """Open the dialog, and dispose of it.

        Without the deleteLater a dialog and its several hundred widgets are
        retained for the life of the process, once per invocation.
        """
        dialog = GlobalSettingsDialog(self)
        try:
            dialog.exec_()
        finally:
            dialog.deleteLater()


# referenced by pyproject.toml, part of the GUI system
def main():
    # One QSettings identity for every layer of the launcher, established
    # before anything can construct a QSettings. T2/T3 adopt launcher's
    # app_identity module rather than repeating the literals.
    ensure_identity()
    migrate_legacy_settings()
    app = QApplication([])
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
