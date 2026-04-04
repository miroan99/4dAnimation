WINDOW_TITLE = "Rotating Unit Cube"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

FOV = 45.0
NEAR_CLIP = 0.1
FAR_CLIP = 100.0

TARGET_FPS = 60
ROTATION_SPEED_DEG = 45.0

from pathlib import Path
_ROOT = Path(__file__).parent.parent
SHADER_DIR = _ROOT / "shaders"
ASSET_DIR = _ROOT / "assets"

CAMERA_DISTANCE = 4.0

MODE_NAMES = [
    "None", "X", "Y", "Z", "XY", "XZ", "YZ", "XYZ",
]

MODE_AXES = {
    0: (),
    1: ("x",),
    2: ("y",),
    3: ("z",),
    4: ("x", "y"),
    5: ("x", "z"),
    6: ("y", "z"),
    7: ("x", "y", "z"),
}

# 4D viewer distance along the W axis (analogous to eye distance in 3D→2D).
# Smaller values exaggerate the perspective distortion of the projection.
W_DISTANCE = 2.0

# 4D rotation modes — which planes are animated at any given time.
# Only W-involving planes (XW, YW, ZW) produce "impossible" 4D movement;
# the others are essentially normal 3D rotations seen from a 4D perspective.
ROTATION4D_MODE_NAMES = [
    "None", "XW", "YW", "ZW", "XW+YW", "XW+ZW", "YW+ZW", "XW+YW+ZW",
]

ROTATION4D_MODE_PLANES: dict[int, frozenset] = {
    0: frozenset(),
    1: frozenset({"xw"}),
    2: frozenset({"yw"}),
    3: frozenset({"zw"}),
    4: frozenset({"xw", "yw"}),
    5: frozenset({"xw", "zw"}),
    6: frozenset({"yw", "zw"}),
    7: frozenset({"xw", "yw", "zw"}),
}

# Per-plane angular speeds (deg/s).  Coprime values keep the pattern from
# ever exactly repeating, producing a richer visual over time.
ROTATION4D_PLANE_SPEEDS: dict[str, float] = {
    "xy": 11.0, "xz": 13.0, "xw": 23.0,
    "yz": 17.0, "yw": 19.0, "zw": 29.0,
}

FACE_COLORS = {
    "+x": (1.0, 0.0, 0.0),
    "-x": (0.55, 0.0, 0.0),
    "+y": (0.0, 1.0, 0.0),
    "-y": (0.0, 0.55, 0.0),
    "+z": (0.0, 0.0, 1.0),
    "-z": (0.0, 0.0, 0.55),
}