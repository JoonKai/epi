# ui_widgets.py
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Optional
from contextlib import contextmanager
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox, QComboBox, QMessageBox, QLabel, QFileDialog
)

from constants import Constants, FlatDir, RotDir
from models import SusceptorSpec, RingSpec
from logic import SusceptorMath

# --- 1. SusceptorViewer ---
class SusceptorViewer(QWidget):
    ringSelected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._spec: Optional[SusceptorSpec] = None
        self._selected_ring_idx: int = -1
        
        self._pen_black = QPen(QColor("#111"), 1)
        self._pen_red = QPen(QColor("red"), 2)
        self._pen_highlight = QPen(QColor("#f39c12"), 2.5)
        self._font_num = QFont("Tahoma", 10, QFont.Bold)

    def setSpec(self, spec: SusceptorSpec):
        self._spec = spec
        self.update()

    def selectRing(self, index: int):
        self._selected_ring_idx = index
        self.update()

    def _get_transform(self):
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        sus_r_inch = self._spec.susceptor_diameter_inch / 2.0 if self._spec else 5.5
        view_size = max(10, min(w, h) - 2 * Constants.SUSCEPTOR_SIDE_GAP_PX)
        scale = (view_size / 2.0) / sus_r_inch if sus_r_inch > 0 else 1.0
        return cx, cy, scale

    def paintEvent(self, event):
        if not self._spec: return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy, scale = self._get_transform()
        
        # Susceptor
        sus_r = self._spec.susceptor_diameter_inch / 2.0
        r_px = sus_r * scale
        sus_rect = QRectF(cx - r_px, cy - r_px, r_px * 2, r_px * 2)
        p.setPen(self._pen_black)
        p.drawEllipse(sus_rect)
        p.setPen(self._pen_red)
        p.drawArc(sus_rect, SusceptorMath.gdi_angle_to_qt_span16(Constants.SUSCEPTOR_BASIS_ANGLE_DEG - 5), int(-10 * 16))

        # Wafers
        layout = SusceptorMath.build_layout(self._spec)
        for r_idx, no, wx, wy, wr, flat_ang in layout:
            rx, ry = SusceptorMath.rotate_cw_ydown(wx, wy, Constants.SUSCEPTOR_BASIS_ANGLE_DEG)
            px = cx + rx * scale
            py = cy + ry * scale
            wr_px = wr * scale
            w_rect = QRectF(px - wr_px, py - wr_px, wr_px * 2, wr_px * 2)
            
            p.setPen(self._pen_highlight if r_idx == self._selected_ring_idx else self._pen_black)
            p.drawEllipse(w_rect)
            p.setPen(self._pen_black)
            p.setFont(self._font_num)
            p.drawText(w_rect, Qt.AlignCenter, str(no))
            
            p.setPen(self._pen_red)
            draw_angle = Constants.SUSCEPTOR_BASIS_ANGLE_DEG + flat_ang
            p.drawArc(w_rect, SusceptorMath.gdi_angle_to_qt_span16(draw_angle - 10), int(-20 * 16))

    def mousePressEvent(self, e):
        if not self._spec or e.button() != Qt.LeftButton: return
        mx, my = e.position().x(), e.position().y()
        cx, cy, scale = self._get_transform()
        layout = SusceptorMath.build_layout(self._spec)
        
        clicked_ring = -1
        for r_idx, _, wx, wy, wr, _ in layout:
            rx, ry = SusceptorMath.rotate_cw_ydown(wx, wy, Constants.SUSCEPTOR_BASIS_ANGLE_DEG)
            px, py = cx + rx * scale, cy + ry * scale
            pr = wr * scale
            if (mx - px)**2 + (my - py)**2 <= pr**2:
                clicked_ring = r_idx
                break
        
        if clicked_ring != -1:
            self._selected_ring_idx = clicked_ring
            self.ringSelected.emit(clicked_ring)
            self.update()

# --- 2. RingDetailWidget ---
class RingDetailWidget(QGroupBox):
    valueChanged = Signal()

    def __init__(self, title="Current Ring"):
        super().__init__(title)
        self._block_signals = False
        self._setup_ui()

    def _setup_ui(self):
        lay = QFormLayout(self)
        self.sp_count = QSpinBox()
        self.sp_count.setRange(1, 400)
        self.sp_radius = QDoubleSpinBox()
        self.sp_radius.setRange(0.0, 200.0); self.sp_radius.setDecimals(4)
        self.cb_flat = QComboBox(); self.cb_flat.addItems([e.value for e in FlatDir])
        self.sp_angle = QDoubleSpinBox(); self.sp_angle.setRange(-360.0, 360.0)
        self.cb_rot = QComboBox(); self.cb_rot.addItems([e.value for e in RotDir])

        lay.addRow("Count", self.sp_count)
        lay.addRow("Radius (in)", self.sp_radius)
        lay.addRow("Flat", self.cb_flat)
        lay.addRow("Init Angle", self.sp_angle)
        lay.addRow("Rot Dir", self.cb_rot)

        for w in (self.sp_count, self.sp_radius, self.sp_angle): w.valueChanged.connect(self._on_change)
        for w in (self.cb_flat, self.cb_rot): w.currentIndexChanged.connect(self._on_change)

    @contextmanager
    def no_signals(self):
        old = self._block_signals; self._block_signals = True
        yield
        self._block_signals = old

    def _on_change(self):
        if not self._block_signals: self.valueChanged.emit()

    def load_ring(self, ring: Optional[RingSpec]):
        with self.no_signals():
            self.setEnabled(ring is not None)
            if not ring:
                self.sp_count.setValue(1); self.sp_radius.setValue(0)
                return
            self.sp_count.setValue(ring.wafer_count)
            self.sp_radius.setValue(ring.ring_radius_inch)
            self.cb_flat.setCurrentText(ring.flat_direction.value)
            self.sp_angle.setValue(ring.initial_angle_deg)
            self.cb_rot.setCurrentText(ring.rotation_dir.value)

    def apply_to_ring(self, ring: RingSpec):
        ring.wafer_count = self.sp_count.value()
        ring.ring_radius_inch = self.sp_radius.value()
        ring.flat_direction = FlatDir(self.cb_flat.currentText())
        ring.initial_angle_deg = self.sp_angle.value()
        ring.rotation_dir = RotDir(self.cb_rot.currentText())

# --- 3. MultiRingPanel ---
class MultiRingPanel(QWidget):
    def __init__(self, viewer: SusceptorViewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.spec = SusceptorSpec()
        self._is_internal_update = False
        
        self._build_ui()
        
        # 초기 상태 로드
        self._refresh_all(0)
        
        # 뷰어 선택 동기화
        self.viewer.ringSelected.connect(self._on_viewer_selection)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)
        
        # --- 1. 상단: 링 목록 및 편집 버튼 ---
        g1 = QGroupBox("Susceptor Configuration")
        h1 = QHBoxLayout(g1)
        
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(120)
        self.list_widget.currentRowChanged.connect(self._on_list_selection)
        
        # 우측 버튼 컬럼
        btn_col = QVBoxLayout()
        
        self.btn_up = QPushButton("↑")
        self.btn_dn = QPushButton("↓")
        self.btn_add = QPushButton("ADD Ring")
        self.btn_del = QPushButton("DEL Ring")
        self.btn_clear = QPushButton("Clear All") # Cancel 대신 Clear 기능
        
        # 버튼 스타일 및 레이아웃 추가
        for b in (self.btn_up, self.btn_dn, self.btn_add, self.btn_del, self.btn_clear):
            b.setMinimumWidth(100)
            btn_col.addWidget(b)
        btn_col.addStretch(1)

        h1.addWidget(self.list_widget, 1)
        h1.addLayout(btn_col)
        root.addWidget(g1)

        # 버튼 이벤트 연결
        self.btn_add.clicked.connect(self._action_add)
        self.btn_del.clicked.connect(self._action_del)
        self.btn_clear.clicked.connect(self._action_clear)
        self.btn_up.clicked.connect(lambda: self._action_move(-1))
        self.btn_dn.clicked.connect(lambda: self._action_move(1))

        # --- 2. 중단: 전역 설정 (Spec) ---
        g_spec = QGroupBox("Global Spec")
        f_spec = QFormLayout(g_spec)
        
        self.sp_wafer_d = QDoubleSpinBox()
        self.sp_wafer_d.setRange(0.1, 20.0); self.sp_wafer_d.setValue(2.0)
        
        self.sp_sus_d = QDoubleSpinBox()
        self.sp_sus_d.setRange(1.0, 50.0); self.sp_sus_d.setValue(11.0)
        
        self.chk_start0 = QCheckBox("Start number from zero (0)")
        
        f_spec.addRow("Wafer Diameter", self._with_unit(self.sp_wafer_d, "inch"))
        f_spec.addRow("Susceptor Diam", self._with_unit(self.sp_sus_d, "inch"))
        f_spec.addRow("", self.chk_start0)
        root.addWidget(g_spec)

        # 이벤트 연결
        for w in (self.sp_wafer_d, self.sp_sus_d): 
            w.valueChanged.connect(self._on_global_spec_changed)
        self.chk_start0.toggled.connect(self._on_global_spec_changed)

        # --- 3. 하단: 개별 링 상세 설정 (Detail) ---
        self.ring_detail = RingDetailWidget()
        self.ring_detail.valueChanged.connect(self._on_ring_detail_changed)
        root.addWidget(self.ring_detail)

        # --- 빈 공간 채우기 (버튼을 맨 아래로 밀기 위함) ---
        root.addStretch(1)

        # --- 4. 최하단: Open / Save 버튼 (복구됨) ---
        row_io = QHBoxLayout()
        row_io.addStretch(1)
        
        self.btn_open = QPushButton("Open")
        self.btn_save = QPushButton("Save")
        # 원래 코드처럼 조금 넓게
        self.btn_open.setMinimumWidth(90)
        self.btn_save.setMinimumWidth(90)
        
        row_io.addWidget(self.btn_open)
        row_io.addWidget(self.btn_save)
        row_io.addStretch(1)
        
        root.addLayout(row_io)

        # IO 버튼 이벤트 (일단 메시지박스로 연결)
        self.btn_open.clicked.connect(self._on_open_click)
        self.btn_save.clicked.connect(self._on_save_click)

    def _with_unit(self, widget, unit):
        """단위 라벨을 붙여주는 헬퍼"""
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        l.addWidget(widget, 1)
        l.addWidget(QLabel(unit))
        return w

    # --- Actions ---
    def _action_add(self):
        self.spec.rings.append(SusceptorMath.create_auto_ring(self.spec))
        self._refresh_all(len(self.spec.rings)-1)

    def _action_del(self):
        idx = self.list_widget.currentRow()
        if 0 <= idx < len(self.spec.rings):
            self.spec.rings.pop(idx)
            if not self.spec.rings: # 다 지워지면 기본 1개 생성
                self.spec.rings.append(RingSpec(1, 0.0))
            self._refresh_all(min(idx, len(self.spec.rings)-1))

    def _action_clear(self):
        # Cancel 대신 전체 초기화 기능
        self.spec.rings = [RingSpec(1, 0.0)]
        self._refresh_all(0)

    def _action_move(self, d):
        idx = self.list_widget.currentRow(); n_idx = idx + d
        if 0 <= idx < len(self.spec.rings) and 0 <= n_idx < len(self.spec.rings):
            self.spec.rings[idx], self.spec.rings[n_idx] = self.spec.rings[n_idx], self.spec.rings[idx]
            self._refresh_all(n_idx)

    # --- IO Placeholders ---
    def _on_open_click(self):
        QMessageBox.information(self, "Open", "JSON 불러오기 기능 구현 위치")

    def _on_save_click(self):
        QMessageBox.information(self, "Save", "JSON 저장 기능 구현 위치")

    # --- UI Sync Logic ---
    def _refresh_all(self, keep_row=0):
        self._is_internal_update = True
        self.list_widget.clear()
        for i, r in enumerate(self.spec.rings):
            self.list_widget.addItem(f"Ring {i+1} : N={r.wafer_count}, R={r.ring_radius_inch:.3f}")
        
        row = keep_row if 0 <= keep_row < self.list_widget.count() else 0
        self.list_widget.setCurrentRow(row)
        
        self.sp_wafer_d.setValue(self.spec.wafer_diameter_inch)
        self.sp_sus_d.setValue(self.spec.susceptor_diameter_inch)
        self.chk_start0.setChecked(self.spec.start_from_zero)
        
        self._is_internal_update = False
        self._on_list_selection(self.list_widget.currentRow())

    def _on_list_selection(self, row):
        if self._is_internal_update: return
        self.ring_detail.load_ring(self.spec.rings[row] if 0 <= row < len(self.spec.rings) else None)
        self.viewer.selectRing(row)
        self.viewer.setSpec(self.spec)

    def _on_viewer_selection(self, idx):
        if 0 <= idx < self.list_widget.count(): 
            self.list_widget.setCurrentRow(idx)

    def _on_global_spec_changed(self):
        if self._is_internal_update: return
        self.spec.wafer_diameter_inch = self.sp_wafer_d.value()
        self.spec.susceptor_diameter_inch = self.sp_sus_d.value()
        self.spec.start_from_zero = self.chk_start0.isChecked()
        self.viewer.setSpec(self.spec)

    def _on_ring_detail_changed(self):
        if self._is_internal_update: return
        idx = self.list_widget.currentRow()
        if 0 <= idx < len(self.spec.rings):
            self.ring_detail.apply_to_ring(self.spec.rings[idx])
            # 리스트 아이템 텍스트 갱신
            self.list_widget.item(idx).setText(
                f"Ring {idx+1} : N={self.spec.rings[idx].wafer_count}, R={self.spec.rings[idx].ring_radius_inch:.3f}"
            )
            self.viewer.setSpec(self.spec)
    def _on_save_click(self):
        # 파일 저장 다이얼로그 띄우기
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Susceptor File", 
            "", 
            "Susceptor Files (*.sus);;All Files (*.*)"
        )
        
        if filename:
            try:
                self._save_to_xml_file(filename)
                QMessageBox.information(self, "Success", f"Saved successfully:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def _save_to_xml_file(self, filename: str):
        """Spec 데이터를 .sus (XML) 포맷으로 변환하여 저장"""
        
        # 1. 단위 변환 상수 (Inch -> mm)
        MM = Constants.MM_PER_INCH
        
        # 2. Root Element 생성
        root = ET.Element("SusceptorMgr", {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
        })

        # 3. WaferSets (Ring 목록)
        wafer_sets = ET.SubElement(root, "WaferSets")
        
        global_wafer_no = 1  # 웨이퍼 번호는 링을 넘어서 계속 증가 [cite: 2, 20]
        if self.spec.start_from_zero:
            global_wafer_no = 0

        for r_idx, ring in enumerate(self.spec.rings):
            # Ring Item 생성
            item_node = ET.SubElement(wafer_sets, "Item", type="EMPL.susceptor.WaferSetRing, EMPL")
            ws_ring = ET.SubElement(item_node, "WaferSetRing")
            
            # Ring 기본 정보
            ET.SubElement(ws_ring, "Count").text = str(ring.wafer_count)
            ET.SubElement(ws_ring, "bSelected").text = "true"  # 기본값
            ET.SubElement(ws_ring, "WaferNumber").text = str(ring.wafer_count)
            
            # Enum 변환 (GUI Enum -> XML String)
            # GUI: CW/CCW -> XML: DIR_CW/DIR_CCW
            rot_str = "DIR_CW" if ring.rotation_dir.value == "CW" else "DIR_CCW"
            ET.SubElement(ws_ring, "RotationDirection").text = rot_str
            
            ET.SubElement(ws_ring, "RingNumberShift").text = "0"
            
            # GUI: IN/OUT -> XML: FLAT_IN/FLAT_OUT
            flat_str = "FLAT_IN" if ring.flat_direction.value == "IN" else "FLAT_OUT"
            ET.SubElement(ws_ring, "FlatDirection").text = flat_str
            
            # Radius 변환 (Inch -> mm) 
            wafer_r_mm = (self.spec.wafer_diameter_inch / 2.0) * MM
            ring_r_mm = ring.ring_radius_inch * MM
            
            ET.SubElement(ws_ring, "WaferRadius").text = f"{wafer_r_mm:.3f}"
            ET.SubElement(ws_ring, "InitialAngle").text = str(ring.initial_angle_deg)
            ET.SubElement(ws_ring, "SetRadius").text = f"{ring_r_mm:.14f}" # 정밀도 유지

            # 4. 개별 웨이퍼 좌표 계산 및 WaferList 생성
            wafer_list_node = ET.SubElement(ws_ring, "WaferList")
            
            # 좌표 계산 로직 (Logic 클래스 활용 대신 여기서 mm 단위로 직접 계산)
            import math
            cnt = max(1, ring.wafer_count)
            step = 360.0 / cnt
            
            for i in range(cnt):
                # 각도 계산
                k = i if ring.rotation_dir.value == "CW" else -i
                ang_deg = (k * step) + ring.initial_angle_deg
                ang_rad = math.radians(ang_deg)
                
                # 좌표 계산 (수학적 좌표계: 0도 = 3시 방향, 반시계+, 하지만 여기선 CW가 기준일 수 있음)
                # XML 예제 분석 결과: Initial 180도일 때 X가 음수(-173). 
                # 즉, 일반적인 cos, sin 좌표계를 따름.
                wx = ring_r_mm * math.cos(ang_rad)
                wy = ring_r_mm * math.sin(ang_rad)
                
                # WaferDummy Item 생성 [cite: 2]
                w_item = ET.SubElement(wafer_list_node, "Item", type="EMPL.susceptor.WaferDummy, EMPL")
                w_dummy = ET.SubElement(w_item, "WaferDummy")
                
                ET.SubElement(w_dummy, "X").text = f"{wx:.14f}"
                ET.SubElement(w_dummy, "Y").text = f"{wy:.14f}"
                ET.SubElement(w_dummy, "Radius").text = f"{wafer_r_mm:.3f}"
                ET.SubElement(w_dummy, "Enable").text = "true"
                ET.SubElement(w_dummy, "Number").text = str(global_wafer_no)
                ET.SubElement(w_dummy, "Angle").text = "0" # 개별 회전은 보통 0
                ET.SubElement(w_dummy, "IsEmptyCell").text = "false"
                ET.SubElement(w_dummy, "IsSeleected").text = "false"
                
                global_wafer_no += 1

            ET.SubElement(ws_ring, "NotSharingEdgePoint").text = "false"
            ET.SubElement(ws_ring, "XStand").text = "0"
            ET.SubElement(ws_ring, "YStand").text = "0"
            ET.SubElement(ws_ring, "RingOrder").text = str(r_idx)

    
        # 5. Global Susceptor Info [cite: 26]
        wafer_r_global = (self.spec.wafer_diameter_inch / 2.0) * MM
        sus_r_global = (self.spec.susceptor_diameter_inch / 2.0) * MM
        
        ET.SubElement(root, "WaferRadius").text = f"{wafer_r_global:.3f}"
        ET.SubElement(root, "SusceptorRadius").text = f"{sus_r_global:.14f}"
        ET.SubElement(root, "Count").text = str(len(self.spec.rings))
        ET.SubElement(root, "SusceptorType").text = "SUS_MULTIRING"
        ET.SubElement(root, "StartFromZero").text = "true" if self.spec.start_from_zero else "false"
        ET.SubElement(root, "UseCustomNumber").text = "false"
        ET.SubElement(root, "SubSatelliteFilename").text = ""
        ET.SubElement(root, "PerimeterRadius").text = "0"
        ET.SubElement(root, "InitialAngle").text = "0"
        ET.SubElement(root, "NeighborDistance").text = "0"
        ET.SubElement(root, "MapMode").text = "false"

        # 6. Pretty Print (들여쓰기 적용) 및 저장
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # toprettyxml이 추가하는 상단 빈 줄 제거용 hack
        xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])

        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_str)
# ---------------------------------------------------------
# 4. FreeViewer (직사각형 & 선형 배치 뷰어)
# ---------------------------------------------------------
class FreeViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._spec: Optional[SusceptorSpec] = None
        
        # 스타일
        self._pen_black = QPen(QColor("#111"), 1)
        self._pen_wafer = QPen(QColor("#f39c12"), 2)
        self._brush_sus = QColor("#e0e0e0")
        self._font_num = QFont("Tahoma", 10, QFont.Bold)

    def setSpec(self, spec: SusceptorSpec):
        self._spec = spec
        self.update()

    def paintEvent(self, event):
        if not self._spec: return
        
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # 1. 뷰포트 계산 (화면 중앙 정렬 및 스케일링)
        w_mm = self._spec.susceptor_width_mm
        h_mm = self._spec.susceptor_height_mm
        if w_mm <= 0 or h_mm <= 0: return

        # 화면 크기 대비 여유 공간(padding)
        margin_px = 20
        view_w = self.width() - 2 * margin_px
        view_h = self.height() - 2 * margin_px

        # 스케일 비율 계산 (Fit to Screen)
        scale_x = view_w / w_mm
        scale_y = view_h / h_mm
        scale = min(scale_x, scale_y) # 비율 유지

        # 화면 중앙 좌표
        cx_px = self.width() / 2
        cy_px = self.height() / 2

        # 서셉터(직사각형) 그리기 시작점 (좌상단)
        sus_w_px = w_mm * scale
        sus_h_px = h_mm * scale
        start_x = cx_px - (sus_w_px / 2)
        start_y = cy_px - (sus_h_px / 2)

        # 2. 직사각형 서셉터 그리기
        sus_rect = QRectF(start_x, start_y, sus_w_px, sus_h_px)
        p.setPen(self._pen_black)
        p.setBrush(self._brush_sus)
        p.drawRect(sus_rect)

        # 3. 웨이퍼 선형(Linear) 배치 그리기
        # 규칙: 왼쪽에서 오른쪽으로 순차 배치, 수직은 중앙 정렬
        wafer_d_mm = self._spec.wafer_diameter_inch * Constants.MM_PER_INCH
        wafer_r_mm = wafer_d_mm / 2.0
        gap_mm = 5.0 # 웨이퍼 간 간격 (5mm 고정 혹은 설정 가능)

        # 배치 시작 X 좌표 (서셉터 왼쪽 끝 + 약간의 여백)
        current_x_mm = gap_mm + wafer_r_mm
        center_y_mm = h_mm / 2.0

        wafer_no = 0 if self._spec.start_from_zero else 1

        for ring in self._spec.rings:
            # Free 모드에서는 Ring 1개가 웨이퍼 1개라고 가정 (혹은 count만큼 반복)
            count = max(1, ring.wafer_count)
            
            for _ in range(count):
                # 좌표 변환 (mm -> px)
                # 서셉터 내부 로컬 좌표 -> 화면 글로벌 좌표
                wx_px = start_x + (current_x_mm * scale)
                wy_px = start_y + (center_y_mm * scale)
                wr_px = wafer_r_mm * scale

                # 웨이퍼 그리기
                w_rect = QRectF(wx_px - wr_px, wy_px - wr_px, wr_px * 2, wr_px * 2)
                p.setBrush(Qt.NoBrush)
                p.setPen(self._pen_wafer)
                p.drawEllipse(w_rect)

                # 번호 그리기
                p.setPen(self._pen_black)
                p.setFont(self._font_num)
                p.drawText(w_rect, Qt.AlignCenter, str(wafer_no))

                # 다음 위치로 이동
                current_x_mm += wafer_d_mm + gap_mm
                wafer_no += 1


# ---------------------------------------------------------
# 5. FreePanel (직사각형 제어 패널)
# ---------------------------------------------------------
class FreePanel(QWidget):
    def __init__(self, viewer: FreeViewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        # Free 모드용 독립적인 Spec 객체를 쓸 수도 있지만, 여기선 공유한다고 가정하거나 새로 생성
        self.spec = SusceptorSpec()
        self.spec.rings = [] # 초기엔 빈 상태

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. 서셉터 크기 설정
        g_size = QGroupBox("Rectangular Box Size (mm)")
        f_size = QFormLayout(g_size)
        
        self.sp_w = QDoubleSpinBox(); self.sp_w.setRange(10, 5000); self.sp_w.setValue(500.0)
        self.sp_h = QDoubleSpinBox(); self.sp_h.setRange(10, 2000); self.sp_h.setValue(100.0)
        self.sp_wd = QDoubleSpinBox(); self.sp_wd.setRange(0.1, 20.0); self.sp_wd.setValue(2.0)
        
        f_size.addRow("Width (mm)", self.sp_w)
        f_size.addRow("Height (mm)", self.sp_h)
        f_size.addRow("Wafer Diam (inch)", self.sp_wd)
        
        layout.addWidget(g_size)

        # 2. 버튼
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Wafer")
        self.btn_clear = QPushButton("Clear All")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        layout.addStretch()

        # 연결
        self.sp_w.valueChanged.connect(self._on_spec_change)
        self.sp_h.valueChanged.connect(self._on_spec_change)
        self.sp_wd.valueChanged.connect(self._on_spec_change)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_clear.clicked.connect(self._on_clear)

    def _on_spec_change(self):
        self.spec.susceptor_width_mm = self.sp_w.value()
        self.spec.susceptor_height_mm = self.sp_h.value()
        self.spec.wafer_diameter_inch = self.sp_wd.value()
        self.viewer.setSpec(self.spec)

    def _on_add(self):
        # Free 모드에서는 RingSpec을 하나의 웨이퍼 단위로 봅니다.
        # (wafer_count=1)
        self.spec.rings.append(RingSpec(wafer_count=1))
        self._refresh()

    def _on_clear(self):
        self.spec.rings = []
        self._refresh()

    def _refresh(self):
        self.viewer.setSpec(self.spec)
# ---------------------------------------------------------
# 4. FreeViewer (직사각형 & 선형 배치 뷰어)
# ---------------------------------------------------------
class FreeViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._spec: Optional[SusceptorSpec] = None
        
        # 스타일
        self._pen_black = QPen(QColor("#111"), 1)
        self._pen_wafer = QPen(QColor("#f39c12"), 2)
        self._brush_sus = QColor("#e0e0e0")
        self._font_num = QFont("Tahoma", 10, QFont.Bold)

    def setSpec(self, spec: SusceptorSpec):
        self._spec = spec
        self.update()

    def paintEvent(self, event):
        if not self._spec: return
        
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # 1. 뷰포트 계산 (화면 중앙 정렬 및 스케일링)
        w_mm = self._spec.susceptor_width_mm
        h_mm = self._spec.susceptor_height_mm
        if w_mm <= 0 or h_mm <= 0: return

        # 화면 크기 대비 여유 공간(padding)
        margin_px = 20
        view_w = self.width() - 2 * margin_px
        view_h = self.height() - 2 * margin_px

        # 스케일 비율 계산 (Fit to Screen)
        scale_x = view_w / w_mm
        scale_y = view_h / h_mm
        scale = min(scale_x, scale_y) # 비율 유지

        # 화면 중앙 좌표
        cx_px = self.width() / 2
        cy_px = self.height() / 2

        # 서셉터(직사각형) 그리기 시작점 (좌상단)
        sus_w_px = w_mm * scale
        sus_h_px = h_mm * scale
        start_x = cx_px - (sus_w_px / 2)
        start_y = cy_px - (sus_h_px / 2)

        # 2. 직사각형 서셉터 그리기
        sus_rect = QRectF(start_x, start_y, sus_w_px, sus_h_px)
        p.setPen(self._pen_black)
        p.setBrush(self._brush_sus)
        p.drawRect(sus_rect)

        # 3. 웨이퍼 선형(Linear) 배치 그리기
        # 규칙: 왼쪽에서 오른쪽으로 순차 배치, 수직은 중앙 정렬
        wafer_d_mm = self._spec.wafer_diameter_inch * Constants.MM_PER_INCH
        wafer_r_mm = wafer_d_mm / 2.0
        gap_mm = 5.0 # 웨이퍼 간 간격 (5mm 고정 혹은 설정 가능)

        # 배치 시작 X 좌표 (서셉터 왼쪽 끝 + 약간의 여백)
        current_x_mm = gap_mm + wafer_r_mm
        center_y_mm = h_mm / 2.0

        wafer_no = 0 if self._spec.start_from_zero else 1

        for ring in self._spec.rings:
            # Free 모드에서는 Ring 1개가 웨이퍼 1개라고 가정 (혹은 count만큼 반복)
            count = max(1, ring.wafer_count)
            
            for _ in range(count):
                # 좌표 변환 (mm -> px)
                # 서셉터 내부 로컬 좌표 -> 화면 글로벌 좌표
                wx_px = start_x + (current_x_mm * scale)
                wy_px = start_y + (center_y_mm * scale)
                wr_px = wafer_r_mm * scale

                # 웨이퍼 그리기
                w_rect = QRectF(wx_px - wr_px, wy_px - wr_px, wr_px * 2, wr_px * 2)
                p.setBrush(Qt.NoBrush)
                p.setPen(self._pen_wafer)
                p.drawEllipse(w_rect)

                # 번호 그리기
                p.setPen(self._pen_black)
                p.setFont(self._font_num)
                p.drawText(w_rect, Qt.AlignCenter, str(wafer_no))

                # 다음 위치로 이동
                current_x_mm += wafer_d_mm + gap_mm
                wafer_no += 1


# ---------------------------------------------------------
# 5. FreePanel (직사각형 제어 패널)
# ---------------------------------------------------------
class FreePanel(QWidget):
    def __init__(self, viewer: FreeViewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        # Free 모드용 독립적인 Spec 객체를 쓸 수도 있지만, 여기선 공유한다고 가정하거나 새로 생성
        self.spec = SusceptorSpec()
        self.spec.rings = [] # 초기엔 빈 상태

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. 서셉터 크기 설정
        g_size = QGroupBox("Rectangular Box Size (mm)")
        f_size = QFormLayout(g_size)
        
        self.sp_w = QDoubleSpinBox(); self.sp_w.setRange(10, 5000); self.sp_w.setValue(500.0)
        self.sp_h = QDoubleSpinBox(); self.sp_h.setRange(10, 2000); self.sp_h.setValue(100.0)
        self.sp_wd = QDoubleSpinBox(); self.sp_wd.setRange(0.1, 20.0); self.sp_wd.setValue(2.0)
        
        f_size.addRow("Width (mm)", self.sp_w)
        f_size.addRow("Height (mm)", self.sp_h)
        f_size.addRow("Wafer Diam (inch)", self.sp_wd)
        
        layout.addWidget(g_size)

        # 2. 버튼
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Wafer")
        self.btn_clear = QPushButton("Clear All")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        layout.addStretch()

        # 연결
        self.sp_w.valueChanged.connect(self._on_spec_change)
        self.sp_h.valueChanged.connect(self._on_spec_change)
        self.sp_wd.valueChanged.connect(self._on_spec_change)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_clear.clicked.connect(self._on_clear)

    def _on_spec_change(self):
        self.spec.susceptor_width_mm = self.sp_w.value()
        self.spec.susceptor_height_mm = self.sp_h.value()
        self.spec.wafer_diameter_inch = self.sp_wd.value()
        self.viewer.setSpec(self.spec)

    def _on_add(self):
        # Free 모드에서는 RingSpec을 하나의 웨이퍼 단위로 봅니다.
        # (wafer_count=1)
        self.spec.rings.append(RingSpec(wafer_count=1))
        self._refresh()

    def _on_clear(self):
        self.spec.rings = []
        self._refresh()

    def _refresh(self):
        self.viewer.setSpec(self.spec)