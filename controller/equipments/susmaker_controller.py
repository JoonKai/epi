from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QToolButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from mdis.equipments.mdi_susrmaker_widget_ui import Ui_SUSMaker


class SUSMakerController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SUSMaker()
        self.ui.setupUi(self)
        self.resize(800, 600)
        self.setWindowTitle("Susceptor Maker")
        self.apply_styles()# qss 스타일 적용

    def apply_styles(self):
        qss_path = "styles/susmaker_style.qss"  # 상대경로 또는 절대경로
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except Exception as e:
            print(f"QSS 로드 오류: {e}")