# logic.py
import math
from typing import Tuple, List
from constants import Constants, FlatDir, RotDir
from models import SusceptorSpec, RingSpec

class SusceptorMath:
    @staticmethod
    def deg2rad(d: float) -> float:
        return d * math.pi / 180.0

    @staticmethod
    def angle2point(radius: float, angle_deg_cw: float) -> Tuple[float, float]:
        r = SusceptorMath.deg2rad(angle_deg_cw)
        return radius * math.cos(r), radius * math.sin(r)

    @staticmethod
    def rotate_cw_ydown(x: float, y: float, deg_cw: float) -> Tuple[float, float]:
        r = SusceptorMath.deg2rad(deg_cw)
        c, s = math.cos(r), math.sin(r)
        return (x * c + y * s), (-x * s + y * c)

    @staticmethod
    def gdi_angle_to_qt_span16(deg: float) -> int:
        return int((-deg) * 16)

    @staticmethod
    def get_wafer_radius(spec: SusceptorSpec) -> float:
        return spec.wafer_diameter_inch / 2.0

    @staticmethod
    def get_max_radius(spec: SusceptorSpec) -> float:
        if not spec.rings:
            return 0.0
        wr = SusceptorMath.get_wafer_radius(spec)
        max_set = max(r.ring_radius_inch for r in spec.rings)
        return max_set + 2.0 * wr

    @staticmethod
    def create_auto_ring(spec: SusceptorSpec) -> RingSpec:
        wr = SusceptorMath.get_wafer_radius(spec)
        max_r = SusceptorMath.get_max_radius(spec)

        cnt = 1
        if wr > 0:
            cnt = 1 if max_r <= 0 else int(3.0 * max_r / wr)
            cnt = max(1, cnt)

        # Center ring rule
        if (len(spec.rings) == 1 and 
            spec.rings[0].wafer_count == 1 and 
            abs(spec.rings[0].ring_radius_inch) < 1e-9):
            cnt = 5

        set_radius = max_r + (Constants.GAP_INCH if max_r > 0 else 0.0)
        
        return RingSpec(
            wafer_count=cnt,
            ring_radius_inch=set_radius
        )

    @staticmethod
    def build_layout(spec: SusceptorSpec) -> List[Tuple[int, int, float, float, float, float]]:
        wr = SusceptorMath.get_wafer_radius(spec)
        no = 0 if spec.start_from_zero else 1
        layout = []

        for ring_idx, ring in enumerate(spec.rings):
            cnt = max(1, ring.wafer_count)
            rr = ring.ring_radius_inch
            init_ang = ring.initial_angle_deg
            step = 360.0 / cnt
            
            for i in range(cnt):
                k = i if ring.rotation_dir == RotDir.CW else -i
                ang = (k * step) + init_ang
                wx, wy = SusceptorMath.angle2point(rr, ang)
                
                flat_offset = 180.0 if ring.flat_direction == FlatDir.OUT else 0.0
                flat_ang = ang + flat_offset
                
                layout.append((ring_idx, no, wx, wy, wr, flat_ang))
                no += 1
        return layout