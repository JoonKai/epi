# main.py
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTabWidget, 
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)

# [수정] FreeViewer, FreePanel 임포트 추가
from ui_widgets import SusceptorViewer, MultiRingPanel, FreeViewer, FreePanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Susceptor Designer (Multi & Free)")
        self.resize(1280, 800)
        
        # Style (이전과 동일)
        self.setStyleSheet("""
            QMainWindow { background: #f0f0f0; }
            QTabWidget::pane { border: 1px solid #ccc; background: white; }
            QTabBar::tab { padding: 8px 16px; background: #e0e0e0; border: 1px solid #ccc; border-bottom: none; }
            QTabBar::tab:selected { background: white; font-weight: bold; }
            QGroupBox { font-weight: bold; border: 1px solid #ccc; margin-top: 10px; background: white; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QListWidget { border: 1px solid #ccc; font-size: 11pt; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 1. MultiRing Tab
        self.tabs.addTab(self._build_multiring_tab(), "MultiRing (Circle)")
        
        # 2. Free Tab (Linear Rectangle)
        self.tabs.addTab(self._build_free_tab(), "Free (Rect Linear)")
        
        # Others
        self.tabs.addTab(self._create_placeholder("Satellites"), "Satellites")
        self.tabs.addTab(self._create_placeholder("Hexagons"), "Hexagons")

    def _build_multiring_tab(self) -> QWidget:
        # (기존 코드와 동일)
        page = QWidget()
        layout = QHBoxLayout(page); layout.setContentsMargins(0,0,0,0)
        viewer = SusceptorViewer()
        panel = MultiRingPanel(viewer)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(panel); splitter.addWidget(viewer)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        return page

    # [NEW] Free 탭 빌드 함수
    def _build_free_tab(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        # Free 전용 뷰어 및 패널 생성
        viewer = FreeViewer()
        panel = FreePanel(viewer)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(panel)
        splitter.addWidget(viewer)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        return page

    def _create_placeholder(self, name: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        label = QLabel(f"'{name}' 기능은 추후 구현 예정입니다.")
        label.setAlignment(Qt.AlignCenter)
        l.addWidget(label)
        return w

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())