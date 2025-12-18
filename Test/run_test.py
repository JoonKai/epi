import sys
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QSplitter,
    QGroupBox, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox, QComboBox,
    QFileDialog, QMessageBox, QLabel, QSizePolicy
)

# ------------------------------------------------------------
# Commercial-like constants
# ------------------------------------------------------------
SUSCEPTOR_SIDE_GAP_PX = 3
SUSCEPTOR_BASIS_ANGLE_DEG = 90.0      # 상용 표시 방향과 맞추기 위한 베이스 회전

MM_PER_INCH = 25.4
GAP_MM = 2.0                          # ★ 상용(22/4에서 4.079, 8.157 맞추려면 2mm)
GAP_INCH = GAP_MM / MM_PER_INCH

def deg2rad(d: float) -> float:
    return d * math.pi / 180.0

def angle2point(radius: float, angle_deg_clockwise: float) -> Tuple[float, float]:
    """
    GDI+ 느낌: 0deg = +X(오른쪽), +deg = 시계방향, y는 아래로 증가하는 좌표계
    """
    r = deg2rad(angle_deg_clockwise)
    return radius * math.cos(r), radius * math.sin(r)

def rotate_cw_ydown(x: float, y: float, deg_clockwise: float) -> Tuple[float, float]:
    """
    y-down 좌표계에서 시계방향 회전(+deg)
    """
    r = deg2rad(deg_clockwise)
    c, s = math.cos(r), math.sin(r)
    xr = x * c + y * s
    yr = -x * s + y * c
    return xr, yr

def gdi_angle_to_qt_start16(gdi_start_deg: float) -> int:
    """
    GDI+: 0° at 3 o'clock, + is clockwise
    Qt:   0° at 3 o'clock, + is counter-clockwise, unit=1/16 deg
    => qt = -gdi
    """
    return int((-gdi_start_deg) * 16)

# ------------------------------------------------------------
# Data model
# ------------------------------------------------------------
@dataclass
class RingSpec:
    wafer_count: int = 1
    ring_radius_inch: float = 0.0
    flat_direction: str = "IN"        # IN / OUT
    initial_angle_deg: float = 0.0
    rotation_dir: str = "CW"          # CW / CCW

@dataclass
class SusceptorSpec:
    wafer_diameter_inch: float = 2.0
    susceptor_diameter_inch: float = 11.0
    start_from_zero: bool = False
    rings: List[RingSpec] = field(default_factory=list)

# ------------------------------------------------------------
# Commercial-like auto ring rule (맞춰서 구현)
# ------------------------------------------------------------
def wafer_radius_inch(spec: SusceptorSpec) -> float:
    return spec.wafer_diameter_inch / 2.0

def get_max_radius_inch(spec: SusceptorSpec) -> float:
    """
    C# SusceptorMgr.GetMaxRadius():
      max(SetRadius) + 2*WaferRadius
    (CreateRing에서 +2.0 추가로 GAP 줌)
    """
    if not spec.rings:
        return 0.0
    wr = wafer_radius_inch(spec)
    max_set = max(r.ring_radius_inch for r in spec.rings)
    return max_set + 2.0 * wr

def create_ring_auto(spec: SusceptorSpec) -> RingSpec:
    """
    C# SusceptorMgr.CreateRing(bAutoPosition=True) + 상용 동작 보정
    - SetRadius = GetMaxRadius() + (GetMaxRadius()>0 ? GAP : 0)
    - WaferNumber = (maxRadius>0)? int(3*maxRadius/waferRadius) : 1
    - 단, 상용 UI는 "센터 다음 링"만 5개로 보이는 동작(스크린샷 기준) → 그대로 맞춤
    """
    wr = wafer_radius_inch(spec)
    max_r = get_max_radius_inch(spec)

    # wafer count
    if wr <= 0:
        cnt = 1
    else:
        cnt = 1 if max_r <= 0 else int(3.0 * max_r / wr)
        cnt = max(1, cnt)

    # ★ 상용 동일: "센터(1개, 반경0) 다음 링"만 5개로 강제
    if (
        len(spec.rings) == 1 and
        spec.rings[0].wafer_count == 1 and
        abs(spec.rings[0].ring_radius_inch) < 1e-9
    ):
        cnt = 5

    # set radius
    set_radius = max_r + (GAP_INCH if max_r > 0 else 0.0)

    return RingSpec(
        wafer_count=cnt,
        ring_radius_inch=set_radius,
        flat_direction="IN",
        initial_angle_deg=0.0,
        rotation_dir="CW",
    )

# ------------------------------------------------------------
# Build wafers (WaferSet.AdjustWaferPosition)
# ------------------------------------------------------------
def build_wafers_with_ring_index(spec: SusceptorSpec) -> List[Tuple[int, int, float, float, float, float]]:
    """
    returns: [(ring_idx, wafer_no, wx, wy, wafer_radius_inch, flat_angle_gdi_cw), ...]
    wx, wy: world coords(y-down), ring 배치만. draw에서 base angle(SUSCEPTOR_BASIS_ANGLE) 회전 적용.
    """
    wr = wafer_radius_inch(spec)
    start_no = 0 if spec.start_from_zero else 1
    no = start_no
    out: List[Tuple[int, int, float, float, float, float]] = []

    for ring_idx, ring in enumerate(spec.rings):
        cnt = max(1, int(ring.wafer_count))
        rr = float(ring.ring_radius_inch)
        init = float(ring.initial_angle_deg)
        step = 360.0 / float(cnt)

        for i in range(cnt):
            k = i if ring.rotation_dir == "CW" else -i
            ang = (k * step) + init  # clockwise
            wx, wy = angle2point(rr, ang)

            flat_ang = ang + (180.0 if ring.flat_direction == "OUT" else 0.0)
            out.append((ring_idx, no, wx, wy, wr, flat_ang))
            no += 1

    return out

# ------------------------------------------------------------
# Viewer
# ------------------------------------------------------------
class SusceptorViewer(QWidget):
    ringSelected = Signal(int)  # ring index

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._spec: Optional[SusceptorSpec] = None
        self._selected_ring_index: int = -1

        self._pen_black = QPen(QColor("#111"), 1)
        self._pen_red2 = QPen(QColor("red"), 2)
        self._pen_ring = QPen(QColor("#f39c12"), 2.5)  # 링 선택(상용 느낌의 주황)
        self._font_num = QFont("Tahoma", 10)
        self._font_num.setBold(True)

    def setSpec(self, spec: SusceptorSpec):
        self._spec = spec
        self.update()

    def setSelectedRing(self, ring_index: int):
        self._selected_ring_index = ring_index
        self.update()

    def _calc_view(self):
        W, H = self.width(), self.height()
        cx, cy = W / 2.0, H / 2.0
        size = max(10, min(W, H) - 2 * SUSCEPTOR_SIDE_GAP_PX)

        sus_r = (self._spec.susceptor_diameter_inch / 2.0)
        scale = (size / 2.0) / sus_r if sus_r > 0 else 1.0

        def world_to_px(wx: float, wy: float) -> QPointF:
            return QPointF(cx + wx * scale, cy + wy * scale)

        def r_to_px(r_inch: float) -> float:
            return r_inch * scale

        return cx, cy, world_to_px, r_to_px

    def paintEvent(self, e):
        if not self._spec:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        cx, cy, world_to_px, r_to_px = self._calc_view()

        # Susceptor circle
        sus_r = self._spec.susceptor_diameter_inch / 2.0
        sr_px = r_to_px(sus_r)
        sus_rect = QRectF(cx - sr_px, cy - sr_px, sr_px * 2, sr_px * 2)

        p.setPen(self._pen_black)
        p.drawEllipse(sus_rect)

        # susceptor red mark
        gap = 5.0
        gdi_start = SUSCEPTOR_BASIS_ANGLE_DEG - gap
        gdi_span = gap * 2.0
        p.setPen(self._pen_red2)
        p.drawArc(sus_rect, gdi_angle_to_qt_start16(gdi_start), int((-gdi_span) * 16))

        wafers = build_wafers_with_ring_index(self._spec)
        if not wafers:
            return

        for ring_idx, no, wx, wy, wr, flat_ang in wafers:
            # base rotation (commercial viewer 느낌)
            rx, ry = rotate_cw_ydown(wx, wy, SUSCEPTOR_BASIS_ANGLE_DEG)
            cpt = world_to_px(rx, ry)

            rp = r_to_px(wr)
            rect = QRectF(cpt.x() - rp, cpt.y() - rp, rp * 2, rp * 2)

            # wafer circle
            p.setPen(self._pen_ring if ring_idx == self._selected_ring_index else self._pen_black)
            p.drawEllipse(rect)

            # number
            p.setPen(self._pen_black)
            p.setFont(self._font_num)
            text = str(no)
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(text)
            th = fm.height()
            p.drawText(QPointF(cpt.x() - tw / 2, cpt.y() + th / 2 - fm.descent()), text)

            # flat red arc
            gdi_dir = SUSCEPTOR_BASIS_ANGLE_DEG + flat_ang
            g = 10.0
            p.setPen(self._pen_red2)
            p.drawArc(rect, gdi_angle_to_qt_start16(gdi_dir - g), int((-g * 2.0) * 16))

    def mousePressEvent(self, e):
        if not self._spec or e.button() != Qt.LeftButton:
            return

        mx = float(e.position().x())
        my = float(e.position().y())

        _, _, world_to_px, r_to_px = self._calc_view()
        wafers = build_wafers_with_ring_index(self._spec)
        if not wafers:
            return

        hit_ring = -1
        for ring_idx, no, wx, wy, wr, flat_ang in wafers:
            rx, ry = rotate_cw_ydown(wx, wy, SUSCEPTOR_BASIS_ANGLE_DEG)
            cpt = world_to_px(rx, ry)
            rp = r_to_px(wr)
            dx = mx - cpt.x()
            dy = my - cpt.y()
            if dx * dx + dy * dy <= rp * rp:
                hit_ring = ring_idx
                break

        if hit_ring != -1:
            self._selected_ring_index = hit_ring
            self.ringSelected.emit(hit_ring)   # ★ 좌측 리스트도 링 선택으로 동기화
            self.update()

# ------------------------------------------------------------
# Left panel
# ------------------------------------------------------------
class MultiRingPanel(QWidget):
    def __init__(self, viewer: SusceptorViewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.spec = SusceptorSpec(
            wafer_diameter_inch=2.0,
            susceptor_diameter_inch=11.0,
            start_from_zero=False,
            rings=[RingSpec(wafer_count=1, ring_radius_inch=0.0)]  # 상용처럼 기본 center 1개
        )

        self._ui_updating = False
        self._build_ui()
        self._apply_spec()

        # viewer -> list sync
        self.viewer.ringSelected.connect(self._on_viewer_ring_selected)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        g1 = QGroupBox("Susceptor")
        root.addWidget(g1)
        v1 = QHBoxLayout(g1)

        self.list_rings = QListWidget()
        self.list_rings.setMinimumHeight(110)
        v1.addWidget(self.list_rings, 1)

        col_btn = QVBoxLayout()
        v1.addLayout(col_btn)

        self.btn_up = QPushButton("↑")
        self.btn_dn = QPushButton("↓")
        self.btn_add = QPushButton("ADD Ring (Auto)")
        self.btn_del = QPushButton("DEL Ring")
        self.btn_clear = QPushButton("Clear")
        for b in (self.btn_up, self.btn_add, self.btn_del, self.btn_dn, self.btn_clear):
            b.setMinimumWidth(120)
            col_btn.addWidget(b)
        col_btn.addStretch(1)

        form1 = QFormLayout()
        root.addLayout(form1)

        self.sp_wafer_d = QDoubleSpinBox()
        self.sp_wafer_d.setDecimals(3)
        self.sp_wafer_d.setRange(0.1, 20.0)
        self.sp_wafer_d.setValue(self.spec.wafer_diameter_inch)

        self.sp_sus_d = QDoubleSpinBox()
        self.sp_sus_d.setDecimals(3)
        self.sp_sus_d.setRange(1.0, 100.0)
        self.sp_sus_d.setValue(self.spec.susceptor_diameter_inch)

        self.cb_start0 = QCheckBox("Start number from zero(0)")

        form1.addRow("Wafer Diameter", self._with_unit(self.sp_wafer_d, "inch"))
        form1.addRow("Susceptor Diameter", self._with_unit(self.sp_sus_d, "inch"))
        form1.addRow("", self.cb_start0)

        g2 = QGroupBox("Current Ring (Manual edit)")
        root.addWidget(g2)
        f2 = QFormLayout(g2)

        self.sp_wafer_cnt = QSpinBox()
        self.sp_wafer_cnt.setRange(1, 400)

        self.sp_ring_r = QDoubleSpinBox()
        self.sp_ring_r.setDecimals(4)
        self.sp_ring_r.setRange(0.0, 200.0)

        self.cb_flat = QComboBox()
        self.cb_flat.addItems(["IN", "OUT"])

        self.sp_init_ang = QDoubleSpinBox()
        self.sp_init_ang.setDecimals(2)
        self.sp_init_ang.setRange(-360.0, 360.0)

        self.cb_rot = QComboBox()
        self.cb_rot.addItems(["CW", "CCW"])

        f2.addRow("Wafer Count", self.sp_wafer_cnt)
        f2.addRow("Ring Radius", self._with_unit(self.sp_ring_r, "inch"))
        f2.addRow("Flat Direction", self.cb_flat)
        f2.addRow("Initial Angle", self._with_unit(self.sp_init_ang, "°"))
        f2.addRow("Rotation Direction", self.cb_rot)

        root.addStretch(1)

        row = QHBoxLayout()
        root.addLayout(row)
        row.addStretch(1)
        self.btn_open = QPushButton("Open")
        self.btn_save = QPushButton("Save")
        self.btn_open.setMinimumWidth(90)
        self.btn_save.setMinimumWidth(90)
        row.addWidget(self.btn_open)
        row.addWidget(self.btn_save)
        row.addStretch(1)

        # Wiring
        self.btn_add.clicked.connect(self.on_add_ring_auto)
        self.btn_del.clicked.connect(self.on_del_ring)
        self.btn_clear.clicked.connect(self.on_clear)

        self.list_rings.currentRowChanged.connect(self.on_select_ring)
        self.btn_up.clicked.connect(lambda: self._move_ring(-1))
        self.btn_dn.clicked.connect(lambda: self._move_ring(+1))

        for w in (self.sp_wafer_d, self.sp_sus_d):
            w.valueChanged.connect(self._apply_from_controls)
        self.cb_start0.toggled.connect(self._apply_from_controls)

        for w in (self.sp_wafer_cnt, self.sp_ring_r, self.sp_init_ang):
            w.valueChanged.connect(self._apply_from_controls)
        self.cb_flat.currentIndexChanged.connect(self._apply_from_controls)
        self.cb_rot.currentIndexChanged.connect(self._apply_from_controls)

        self.btn_open.clicked.connect(self.on_open)
        self.btn_save.clicked.connect(self.on_save)

    def _with_unit(self, widget: QWidget, unit: str) -> QWidget:
        wrap = QWidget()
        h = QHBoxLayout(wrap)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        h.addWidget(widget, 1)
        lab = QLabel(unit)
        lab.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        lab.setFixedWidth(50)
        h.addWidget(lab, 0)
        return wrap

    def _apply_spec(self):
        self._ui_updating = True
        try:
            self.sp_wafer_d.setValue(self.spec.wafer_diameter_inch)
            self.sp_sus_d.setValue(self.spec.susceptor_diameter_inch)
            self.cb_start0.setChecked(self.spec.start_from_zero)

            self.list_rings.blockSignals(True)
            self.list_rings.clear()
            for i, r in enumerate(self.spec.rings, start=1):
                self.list_rings.addItem(f"Ring {i}  (N={r.wafer_count}, R={r.ring_radius_inch:.4f}in)")
            self.list_rings.blockSignals(False)

            if self.spec.rings:
                # 현재 선택 유지
                row = self.list_rings.currentRow()
                if not (0 <= row < len(self.spec.rings)):
                    row = 0
                self.list_rings.setCurrentRow(row)
                self._load_ring_controls(self.spec.rings[row])
                self.viewer.setSelectedRing(row)
            else:
                self._load_ring_controls(None)
                self.viewer.setSelectedRing(-1)

            self.viewer.setSpec(self.spec)
        finally:
            self._ui_updating = False

    def _load_ring_controls(self, ring: Optional[RingSpec]):
        self._ui_updating = True
        try:
            enabled = ring is not None
            for w in (self.sp_wafer_cnt, self.sp_ring_r, self.cb_flat, self.sp_init_ang, self.cb_rot):
                w.setEnabled(enabled)

            if not ring:
                self.sp_wafer_cnt.setValue(1)
                self.sp_ring_r.setValue(0.0)
                self.cb_flat.setCurrentText("IN")
                self.sp_init_ang.setValue(0.0)
                self.cb_rot.setCurrentText("CW")
                return

            self.sp_wafer_cnt.setValue(ring.wafer_count)
            self.sp_ring_r.setValue(ring.ring_radius_inch)
            self.cb_flat.setCurrentText(ring.flat_direction)
            self.sp_init_ang.setValue(ring.initial_angle_deg)
            self.cb_rot.setCurrentText(ring.rotation_dir)
        finally:
            self._ui_updating = False

    def _apply_from_controls(self):
        if self._ui_updating:
            return

        self.spec.wafer_diameter_inch = float(self.sp_wafer_d.value())
        self.spec.susceptor_diameter_inch = float(self.sp_sus_d.value())
        self.spec.start_from_zero = bool(self.cb_start0.isChecked())

        idx = self.list_rings.currentRow()
        if 0 <= idx < len(self.spec.rings):
            ring = self.spec.rings[idx]
            ring.wafer_count = int(self.sp_wafer_cnt.value())
            ring.ring_radius_inch = float(self.sp_ring_r.value())
            ring.flat_direction = self.cb_flat.currentText()
            ring.initial_angle_deg = float(self.sp_init_ang.value())
            ring.rotation_dir = self.cb_rot.currentText()

        self._apply_spec()

    # -------- viewer -> list sync --------
    def _on_viewer_ring_selected(self, ring_index: int):
        if 0 <= ring_index < self.list_rings.count():
            self.list_rings.setCurrentRow(ring_index)

    # -------- actions --------
    def on_add_ring_auto(self):
        self.spec.rings.append(create_ring_auto(self.spec))
        self._apply_spec()

    def on_del_ring(self):
        idx = self.list_rings.currentRow()
        if 0 <= idx < len(self.spec.rings):
            # 상용처럼 센터 링은 남겨두고 싶으면 여기서 idx==0 삭제 금지 처리 가능
            self.spec.rings.pop(idx)
            if not self.spec.rings:
                self.spec.rings.append(RingSpec(wafer_count=1, ring_radius_inch=0.0))
            self._apply_spec()

    def on_clear(self):
        self.spec.rings = [RingSpec(wafer_count=1, ring_radius_inch=0.0)]
        self._apply_spec()

    def on_select_ring(self, row: int):
        if 0 <= row < len(self.spec.rings):
            self._load_ring_controls(self.spec.rings[row])
            self.viewer.setSelectedRing(row)
        else:
            self._load_ring_controls(None)
            self.viewer.setSelectedRing(-1)

    def _move_ring(self, delta: int):
        i = self.list_rings.currentRow()
        j = i + delta
        if not (0 <= i < len(self.spec.rings) and 0 <= j < len(self.spec.rings)):
            return
        self.spec.rings[i], self.spec.rings[j] = self.spec.rings[j], self.spec.rings[i]
        self._apply_spec()
        self.list_rings.setCurrentRow(j)

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open", "", "JSON (*.json);;All Files (*.*)")
        if not path:
            return
        QMessageBox.information(self, "Open", "여기서 JSON 로드 로직 붙이면 됨")

    def on_save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save", "", "JSON (*.json);;All Files (*.*)")
        if not path:
            return
        QMessageBox.information(self, "Save", "여기서 JSON 저장 로직 붙이면 됨")

# ------------------------------------------------------------
# Main window / Tabs
# ------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Susceptor Maker (PySide6) - Commercial Matched")
        self.resize(1200, 760)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        tabs.addTab(self._build_multiring_tab(), "MultiRing")
        tabs.addTab(self._placeholder("Satellites"), "Satellites")
        tabs.addTab(self._placeholder("Hexagons"), "Hexagons")
        tabs.addTab(self._placeholder("Free"), "Free")

        self.setStyleSheet(APP_QSS)

    def _build_multiring_tab(self) -> QWidget:
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(6, 6, 6, 6)

        splitter = QSplitter(Qt.Horizontal)
        lay.addWidget(splitter)

        viewer = SusceptorViewer()
        viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        left = MultiRingPanel(viewer)
        left.setMinimumWidth(340)

        splitter.addWidget(left)
        splitter.addWidget(viewer)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        return page

    def _placeholder(self, name: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        lab = QLabel(f"{name} 탭은 다음 단계에서 구현")
        lab.setAlignment(Qt.AlignCenter)
        l.addWidget(lab, 1)
        return w

APP_QSS = """
QMainWindow { background: #f6f6f6; }
QTabWidget::pane { border: 1px solid #cfcfcf; background: white; }
QTabBar::tab { padding: 6px 14px; border: 1px solid #cfcfcf; background: #efefef; }
QTabBar::tab:selected { background: white; border-bottom: 1px solid white; }

QGroupBox {
  border: 1px solid #d0d0d0;
  margin-top: 10px;
  background: #fafafa;
}
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }

QPushButton {
  border: 1px solid #bdbdbd;
  background: #f4f4f4;
  padding: 6px 10px;
}
QPushButton:hover { background: #eaeaea; }
QPushButton:pressed { background: #dddddd; }

QListWidget { background: white; border: 1px solid #cfcfcf; }
QDoubleSpinBox, QSpinBox, QComboBox {
  background: white;
  border: 1px solid #cfcfcf;
  padding: 3px 6px;
  min-height: 22px;
}
"""

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
