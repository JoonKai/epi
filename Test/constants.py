# constants.py
from enum import Enum

class Constants:
    SUSCEPTOR_SIDE_GAP_PX = 3
    SUSCEPTOR_BASIS_ANGLE_DEG = 90.0
    MM_PER_INCH = 25.4
    GAP_MM = 2.0
    GAP_INCH = GAP_MM / MM_PER_INCH

class FlatDir(str, Enum):
    IN = "IN"
    OUT = "OUT"

class RotDir(str, Enum):
    CW = "CW"
    CCW = "CCW"