from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QDialog, QVBoxLayout, QLabel
from windows.ui_settings_dialog import Ui_Settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Settings() 
        self.ui.setupUi(self)  
        self.setWindowTitle("환경 설정")
        self.resize(800, 500)