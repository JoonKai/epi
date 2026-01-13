import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QProgressDialog, QMdiSubWindow
from PySide6.QtCore import Qt
# from controller.pltrend_controller import PLTrendController
from controller.fmmacro_controller import FMMacroController
from controller.susmaker_controller import SUSMakerController
from windows.ui_main_window import Ui_MainWindow
from main_settings import SettingsDialog



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.resize(1200, 700)
        self.setWindowTitle("EPI")
        self.mn_settings_window.triggered.connect(self.open_settings_window)
        self.mn_fmmacro.triggered.connect(self.open_sub_fmmacro)
        self.mn_susceptormaker.triggered.connect(self.open_sub_susmaker)


    def open_settings_window(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def open_sub_fmmacro(self): 
        for sub in self.mdiArea.subWindowList(): 
            if isinstance(sub.widget(), FMMacroController):
                sub.activateWindow() 
                self.mdiArea.setActiveSubWindow(sub) 
                return
        
        sub_widget = FMMacroController(self) 
        sub = QMdiSubWindow() 
        sub.setWidget(sub_widget) 
        sub.setAttribute(Qt.WA_DeleteOnClose, True) 
        self.mdiArea.addSubWindow(sub) 
        sub.show()

    def open_sub_susmaker(self): 
        for sub in self.mdiArea.subWindowList(): 
            if isinstance(sub.widget(), SUSMakerController):
                sub.activateWindow() 
                self.mdiArea.setActiveSubWindow(sub) 
                return
        
        sub_widget = SUSMakerController(self) 
        sub = QMdiSubWindow() 
        sub.setWidget(sub_widget) 
        sub.setAttribute(Qt.WA_DeleteOnClose, True) 
        sub.resize(900, 600)
        self.mdiArea.addSubWindow(sub) 
        sub.show()








app = QApplication(sys.argv)
with open("./styles/susmaker_style.qss", "r", encoding="utf-8") as f:
    app.setStyleSheet(f.read())

window = MainWindow()
window.show()
sys.exit(app.exec())