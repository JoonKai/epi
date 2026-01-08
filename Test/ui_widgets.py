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
        import math
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        MM = Constants.MM_PER_INCH
        
        root = ET.Element("SusceptorMgr", {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
        })

        wafer_sets = ET.SubElement(root, "WaferSets")
        
        global_wafer_no = 1
        if self.spec.start_from_zero:
            global_wafer_no = 0

        for r_idx, ring in enumerate(self.spec.rings):
            item_node = ET.SubElement(wafer_sets, "Item", type="EMPL.susceptor.WaferSetRing, EMPL")
            ws_ring = ET.SubElement(item_node, "WaferSetRing")
            
            ET.SubElement(ws_ring, "Count").text = str(ring.wafer_count)
            ET.SubElement(ws_ring, "bSelected").text = "true"
            ET.SubElement(ws_ring, "WaferNumber").text = str(ring.wafer_count)
            ET.SubElement(ws_ring, "RotationDirection").text = "DIR_CW" if ring.rotation_dir.value == "CW" else "DIR_CCW"
            ET.SubElement(ws_ring, "RingNumberShift").text = "0"
            
            # [수정됨] 좌표 회전 보정으로 인해 Flat 방향이 반전되어야 함.
            # 화면상 IN(중심)을 원하면 XML에는 OUT으로 저장해야 상용 툴 로직상 맞음.
            if ring.flat_direction.value == "IN":
                flat_str = "FLAT_OUT" # IN -> OUT으로 저장
            else:
                flat_str = "FLAT_IN"  # OUT -> IN으로 저장
                
            ET.SubElement(ws_ring, "FlatDirection").text = flat_str
            
            wafer_r_mm = (self.spec.wafer_diameter_inch / 2.0) * MM
            ring_r_mm = ring.ring_radius_inch * MM
            
            ET.SubElement(ws_ring, "WaferRadius").text = f"{wafer_r_mm:.3f}"
            ET.SubElement(ws_ring, "InitialAngle").text = "0"
            ET.SubElement(ws_ring, "SetRadius").text = f"{ring_r_mm:.14f}"

            wafer_list_node = ET.SubElement(ws_ring, "WaferList")
            
            cnt = max(1, ring.wafer_count)
            step = 360.0 / cnt
            
            for i in range(cnt):
                # 1. Visual Angle (12시=0, CW)
                if ring.rotation_dir.value == "CW":
                    visual_angle = ring.initial_angle_deg + (i * step)
                else:
                    visual_angle = ring.initial_angle_deg - (i * step)
                
                # 2. Save Angle (Visual + 180) -> C# Load (+90) -> Result (270/Top)
                save_angle_deg = visual_angle + 180.0
                rad = math.radians(save_angle_deg)
                
                # 3. Coordinates
                final_x = ring_r_mm * math.cos(rad)
                final_y = ring_r_mm * math.sin(rad)

                w_item = ET.SubElement(wafer_list_node, "Item", type="EMPL.susceptor.WaferDummy, EMPL")
                w_dummy = ET.SubElement(w_item, "WaferDummy")
                
                ET.SubElement(w_dummy, "X").text = f"{final_x:.14f}"
                ET.SubElement(w_dummy, "Y").text = f"{final_y:.14f}"
                ET.SubElement(w_dummy, "Radius").text = f"{wafer_r_mm:.3f}"
                ET.SubElement(w_dummy, "Enable").text = "true"
                ET.SubElement(w_dummy, "Number").text = str(global_wafer_no)
                ET.SubElement(w_dummy, "Angle").text = "0"
                ET.SubElement(w_dummy, "IsEmptyCell").text = "false"
                ET.SubElement(w_dummy, "IsSeleected").text = "false"
                
                global_wafer_no += 1

            ET.SubElement(ws_ring, "NotSharingEdgePoint").text = "false"
            ET.SubElement(ws_ring, "XStand").text = "0"
            ET.SubElement(ws_ring, "YStand").text = "0"
            ET.SubElement(ws_ring, "RingOrder").text = str(r_idx)

        # Global Info
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

        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
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
        self._selected_index = -1
        
        # 스타일
        self._pen_black = QPen(QColor("#111"), 1)
        self._pen_wafer = QPen(QColor("black"), 1)     # 기본 웨이퍼
        self._pen_select = QPen(QColor("#8bc4eaff"), 3)    # 선택된 웨이퍼 (파란색 강조)
        self._pen_flat = QPen(QColor("Red"), 2)          # 플랫존 (빨간색)
        self._brush_sus = QColor("#e0e0e0")
        self._font_num = QFont("Tahoma", 10, QFont.Bold)

    def setSpec(self, spec: SusceptorSpec):
        self._spec = spec
        self.update()

    def setSelectedIndex(self, idx: int):
        self._selected_index = idx
        self.update()

    def paintEvent(self, event):
        if not self._spec: return
        
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # 1. 뷰포트 계산
        w_mm = self._spec.susceptor_width_mm
        h_mm = self._spec.susceptor_height_mm
        if w_mm <= 0 or h_mm <= 0: return

        margin_px = 30
        view_w = self.width() - 2 * margin_px
        view_h = self.height() - 2 * margin_px

        scale = min(view_w / w_mm, view_h / h_mm)
        cx_px, cy_px = self.width() / 2, self.height() / 2

        # 서셉터 시작점
        sus_w_px = w_mm * scale
        sus_h_px = h_mm * scale
        start_x = cx_px - (sus_w_px / 2)
        start_y = cy_px - (sus_h_px / 2)

        # 2. 직사각형 서셉터 그리기
        sus_rect = QRectF(start_x, start_y, sus_w_px, sus_h_px)
        
        p.setPen(self._pen_black)       # 검은색 테두리
        p.setBrush(Qt.NoBrush)          # <--- [수정됨] 내부 색상 없음 (투명)
        p.drawRect(sus_rect)

        # 3. 웨이퍼 배치 및 그리기
        wafer_d_mm = self._spec.wafer_diameter_inch * Constants.MM_PER_INCH
        wafer_r_mm = wafer_d_mm / 2.0
        gap_mm = 5.0

        current_x_mm = gap_mm + wafer_r_mm
        center_y_mm = h_mm / 2.0
        
        for idx, ring in enumerate(self._spec.rings):
            # 좌표 변환
            wx_px = start_x + (current_x_mm * scale)
            wy_px = start_y + (center_y_mm * scale)
            wr_px = wafer_r_mm * scale
            
            w_rect = QRectF(wx_px - wr_px, wy_px - wr_px, wr_px * 2, wr_px * 2)

            # 웨이퍼 원형
            is_selected = (idx == self._selected_index)
            
            # 웨이퍼 내부도 투명하게 할지, 선택시 색상을 넣을지 결정
            # MultiRing과 동일하게 하려면 기본은 NoBrush, 선택시에만 색상 적용
            if is_selected:
                # 선택된 경우 연한 파란색 등으로 채우기 (선택 식별용)
                p.setBrush(QColor(41, 128, 185, 50)) 
            else:
                p.setBrush(Qt.NoBrush) # 기본 웨이퍼도 투명

            p.setPen(self._pen_select if is_selected else self._pen_wafer)
            p.drawEllipse(w_rect)

            # 번호
            p.setPen(self._pen_black)
            p.setFont(self._font_num)
            p.drawText(w_rect, Qt.AlignCenter, str(idx + 1))

            # --- 플랫존(Red Arc) 그리기 ---
            base_angle = 0.0
            if ring.flat_direction.value == "IN":
                base_angle = 90.0  # 아래쪽 (IN)
            else:
                base_angle = 270.0 # 위쪽 (OUT)
            
            final_angle = base_angle + ring.initial_angle_deg
            
            qt_start_angle = int(-final_angle * 16) 
            span_angle = int(-20 * 16) 
            qt_start_angle += int(10 * 16)

            p.setPen(self._pen_flat)
            # 플랫 그릴 때는 Brush 없어야 함 (선만 그리기)
            p.setBrush(Qt.NoBrush) 
            p.drawArc(w_rect, qt_start_angle, span_angle)

            # 다음 위치로
            current_x_mm += wafer_d_mm + gap_mm


# ---------------------------------------------------------
# 5. FreePanel (리스트 & 상세 설정 추가)
# ---------------------------------------------------------
class FreePanel(QWidget):
    def __init__(self, viewer: FreeViewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.spec = SusceptorSpec()
        self.spec.rings = [] 

        self._block_signals = False
        self._build_ui()
        self._refresh_all(0)
        
        # 뷰어 클릭 연동은 FreeViewer에 mousePress 구현이 필요하나 
        # 일단 리스트 -> 뷰어 단방향 동기화만 구현
        
    def _build_ui(self):
        root = QVBoxLayout(self)
        
        # 1. 서셉터 크기
        g_size = QGroupBox("Box Size & Global")
        f_size = QFormLayout(g_size)
        self.sp_w = QDoubleSpinBox(); self.sp_w.setRange(10, 5000); self.sp_w.setValue(500.0)
        self.sp_h = QDoubleSpinBox(); self.sp_h.setRange(10, 2000); self.sp_h.setValue(100.0)
        self.sp_wd = QDoubleSpinBox(); self.sp_wd.setRange(0.1, 20.0); self.sp_wd.setValue(2.0)
        f_size.addRow("Width (mm)", self.sp_w)
        f_size.addRow("Height (mm)", self.sp_h)
        f_size.addRow("Wafer Diam (in)", self.sp_wd)
        root.addWidget(g_size)

        # 2. 웨이퍼 리스트 & 추가/삭제
        g_list = QGroupBox("Wafer List")
        h_list = QHBoxLayout(g_list)
        
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_list_select)
        
        v_btns = QVBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_del = QPushButton("Del")
        self.btn_clr = QPushButton("Clear")
        for b in (self.btn_add, self.btn_del, self.btn_clr):
            v_btns.addWidget(b)
        v_btns.addStretch()
        
        h_list.addWidget(self.list_widget, 1)
        h_list.addLayout(v_btns)
        root.addWidget(g_list)

        # 3. 개별 웨이퍼 상세 설정 (Flat Zone)
        g_detail = QGroupBox("Selected Wafer Settings")
        f_detail = QFormLayout(g_detail)
        
        self.cb_flat = QComboBox()
        self.cb_flat.addItems([e.value for e in FlatDir]) # IN / OUT
        
        self.sp_angle = QDoubleSpinBox()
        self.sp_angle.setRange(-360, 360)
        self.sp_angle.setSingleStep(10)
        
        f_detail.addRow("Flat Direction", self.cb_flat)
        f_detail.addRow("Rotation Angle", self.sp_angle)
        root.addWidget(g_detail)

        root.addStretch()

        # 4. 저장 버튼
        self.btn_save = QPushButton("Save .sus File")
        root.addWidget(self.btn_save)

        # 이벤트 연결
        self.sp_w.valueChanged.connect(self._on_global_change)
        self.sp_h.valueChanged.connect(self._on_global_change)
        self.sp_wd.valueChanged.connect(self._on_global_change)
        
        self.btn_add.clicked.connect(self._on_add)
        self.btn_del.clicked.connect(self._on_del)
        self.btn_clr.clicked.connect(self._on_clear)
        self.btn_save.clicked.connect(self._on_save)

        self.cb_flat.currentIndexChanged.connect(self._on_detail_change)
        self.sp_angle.valueChanged.connect(self._on_detail_change)

    # --- Logic ---

    def _on_global_change(self):
        if self._block_signals: return
        self.spec.susceptor_width_mm = self.sp_w.value()
        self.spec.susceptor_height_mm = self.sp_h.value()
        self.spec.wafer_diameter_inch = self.sp_wd.value()
        self.viewer.setSpec(self.spec)

    def _on_add(self):
        # 새 웨이퍼 추가 (기본값)
        self.spec.rings.append(RingSpec(wafer_count=1, flat_direction=FlatDir.IN, initial_angle_deg=0))
        self._refresh_all(len(self.spec.rings)-1)

    def _on_del(self):
        idx = self.list_widget.currentRow()
        if 0 <= idx < len(self.spec.rings):
            self.spec.rings.pop(idx)
            self._refresh_all(max(0, idx-1))

    def _on_clear(self):
        self.spec.rings = []
        self._refresh_all(-1)

    def _on_list_select(self, row):
        if self._block_signals: return
        
        self.viewer.setSelectedIndex(row)
        
        # 상세 설정 패널 업데이트
        if 0 <= row < len(self.spec.rings):
            ring = self.spec.rings[row]
            self.cb_flat.setEnabled(True)
            self.sp_angle.setEnabled(True)
            
            self._block_signals = True
            self.cb_flat.setCurrentText(ring.flat_direction.value)
            self.sp_angle.setValue(ring.initial_angle_deg)
            self._block_signals = False
        else:
            self.cb_flat.setEnabled(False)
            self.sp_angle.setEnabled(False)

    def _on_detail_change(self):
        if self._block_signals: return
        
        idx = self.list_widget.currentRow()
        if 0 <= idx < len(self.spec.rings):
            ring = self.spec.rings[idx]
            ring.flat_direction = FlatDir(self.cb_flat.currentText())
            ring.initial_angle_deg = self.sp_angle.value()
            
            self.viewer.setSpec(self.spec)

    def _refresh_all(self, select_row):
        self._block_signals = True
        self.list_widget.clear()
        for i in range(len(self.spec.rings)):
            self.list_widget.addItem(f"Wafer {i+1}")
        
        if 0 <= select_row < self.list_widget.count():
            self.list_widget.setCurrentRow(select_row)
        else:
            self.list_widget.setCurrentRow(-1)
            
        self._block_signals = False
        
        self._on_list_select(self.list_widget.currentRow())
        self.viewer.setSpec(self.spec)

    # --- Save Logic (XML) ---
    def _on_save(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save", "", "Susceptor (*.sus)")
        if filename:
            try:
                self._save_xml(filename)
                QMessageBox.information(self, "OK", f"Saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _save_xml(self, filename):
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        root = ET.Element("SusceptorMgr", {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
        })
        
        wafer_sets = ET.SubElement(root, "WaferSets")
        total = len(self.spec.rings)
        
        if total > 0:
            item = ET.SubElement(wafer_sets, "Item", type="EMPL.susceptor.WaferSetRing, EMPL")
            ws = ET.SubElement(item, "WaferSetRing")
            
            # 대표값 설정 (첫 번째 웨이퍼 기준 혹은 공통값)
            first = self.spec.rings[0]
            wafer_r = (self.spec.wafer_diameter_inch * Constants.MM_PER_INCH) / 2.0
            
            ET.SubElement(ws, "Count").text = str(total)
            ET.SubElement(ws, "bSelected").text = "true"
            ET.SubElement(ws, "WaferNumber").text = str(total)
            ET.SubElement(ws, "RotationDirection").text = "DIR_CW"
            ET.SubElement(ws, "RingNumberShift").text = "0"
            ET.SubElement(ws, "FlatDirection").text = "FLAT_" + first.flat_direction.value
            ET.SubElement(ws, "WaferRadius").text = f"{wafer_r:.3f}"
            ET.SubElement(ws, "InitialAngle").text = "0"
            ET.SubElement(ws, "SetRadius").text = "0"
            
            w_list = ET.SubElement(ws, "WaferList")
            
            # 좌표 계산
            gap = 5.0
            start_x = -(self.spec.susceptor_width_mm / 2.0)
            curr_x = start_x + gap + wafer_r
            
            for i, r in enumerate(self.spec.rings):
                dummy_item = ET.SubElement(w_list, "Item", type="EMPL.susceptor.WaferDummy, EMPL")
                d = ET.SubElement(dummy_item, "WaferDummy")
                
                ET.SubElement(d, "X").text = f"{curr_x:.14f}"
                ET.SubElement(d, "Y").text = "0"
                ET.SubElement(d, "Radius").text = f"{wafer_r:.3f}"
                ET.SubElement(d, "Enable").text = "true"
                ET.SubElement(d, "Number").text = str(i+1)
                
                # 개별 Angle/Flat 저장 (XML 구조상 Angle 필드 활용)
                # 보통 Flat IN/OUT과 Angle을 조합해서 쓰므로 여기에 저장
                ET.SubElement(d, "Angle").text = str(r.initial_angle_deg)
                
                ET.SubElement(d, "IsEmptyCell").text = "false"
                ET.SubElement(d, "IsSeleected").text = "false"
                
                curr_x += (wafer_r * 2 + gap)

            ET.SubElement(ws, "NotSharingEdgePoint").text = "false"
            ET.SubElement(ws, "XStand").text = "0"
            ET.SubElement(ws, "YStand").text = "0"
            ET.SubElement(ws, "RingOrder").text = "0"

        # Global
        ET.SubElement(root, "SusceptorType").text = "SUS_RECTANGULAR"
        ET.SubElement(root, "Count").text = "1"
        
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        xml_str = '\n'.join([l for l in xml_str.split('\n') if l.strip()])
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_str)