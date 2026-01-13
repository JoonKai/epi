import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMdiSubWindow
from PySide6.QtCore import Qt
# from controller.pltrend_controller import PLTrendController
from controller.macro.fmmacro_controller import FMMacroController
from controller.equipments.susmaker_controller import SUSMakerController
from controller.equipments.pltrend_controller import PLTrendController
from controller.epidatabase.mariadb_controller import MariaDBController
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
        self.mn_pltrend.triggered.connect(self.open_sub_pltrend)
        self.mn_mariadb.triggered.connect(self.open_sub_mariadb)

    """##########################설정##############################"""
    def open_settings_window(self):
        dlg = SettingsDialog(self)
        dlg.exec()


    """##########################매크로탭##############################"""
    #팩토리모델러
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


    """##########################설비탭##############################"""
    #########
    #측정
    #########

    #SUSMaker
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
    
    #PLTrend
    def open_sub_pltrend(self): 
        for sub in self.mdiArea.subWindowList(): 
            if isinstance(sub.widget(), PLTrendController):
                sub.activateWindow() 
                self.mdiArea.setActiveSubWindow(sub) 
                return
        
        sub_widget = PLTrendController(self) 
        sub = QMdiSubWindow() 
        sub.setWidget(sub_widget) 
        sub.setAttribute(Qt.WA_DeleteOnClose, True) 
        sub.resize(900, 600)
        self.mdiArea.addSubWindow(sub) 
        sub.show()
    """##########################데이터베이스##############################"""
    #DB
    def open_sub_mariadb(self): 
        for sub in self.mdiArea.subWindowList(): 
            if isinstance(sub.widget(), MariaDBController):
                sub.activateWindow() 
                self.mdiArea.setActiveSubWindow(sub) 
                return
        
        sub_widget = MariaDBController(self) 
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