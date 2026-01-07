# models.py
from dataclasses import dataclass, field
from typing import List
from constants import FlatDir, RotDir

@dataclass
class RingSpec:
    wafer_count: int = 1
    ring_radius_inch: float = 0.0
    flat_direction: FlatDir = FlatDir.IN
    initial_angle_deg: float = 0.0
    rotation_dir: RotDir = RotDir.CW
    # Free 모드용 좌표 (나중에 자유 배치할 때 사용 대비)
    x_pos_mm: float = 0.0
    y_pos_mm: float = 0.0

@dataclass
class SusceptorSpec:
    wafer_diameter_inch: float = 2.0
    susceptor_diameter_inch: float = 11.0
    
    # [NEW] 직사각형(Free) 모드용 치수 (기본값 설정)
    susceptor_width_mm: float = 500.0
    susceptor_height_mm: float = 100.0
    
    start_from_zero: bool = False
    rings: List[RingSpec] = field(default_factory=lambda: [RingSpec()])