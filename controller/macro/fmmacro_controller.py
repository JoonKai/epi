from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from mdis.macro.ui_mdi_fmmacro_widget import Ui_FMMacro


class FMMacroController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FMMacro()
        self.ui.setupUi(self)
        self.resize(800, 600)
        self.setWindowTitle("팩토리 모델러 매크로")
        self.apply_styles()# qss 스타일 적용

    def apply_styles(self):
        qss_path = "styles/fmmacro_style.qss"  # 상대경로 또는 절대경로
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except Exception as e:
            print(f"QSS 로드 오류: {e}")