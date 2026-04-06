import math

import numpy as np

from app import config
from app.utils.math3d import look_at, perspective


class Camera:
    DRAG_SENSITIVITY = 0.005  # radians per pixel

    def __init__(self):
        self.camera_distance = config.CAMERA_DISTANCE
        self.shift_depth = 0.0
        # Initial eye = normalize([1, 1, 1]) * distance
        self.azimuth = math.pi / 4                       # 45 deg
        self.elevation = math.asin(1.0 / math.sqrt(3))  # ≈35.26 deg

    def orbit(self, dx: int, dy: int) -> None:
        """Rotate camera on the sphere by screen-space drag (pixels)."""
        self.azimuth += dx * self.DRAG_SENSITIVITY
        self.elevation -= dy * self.DRAG_SENSITIVITY
        # Clamp elevation away from poles to avoid flipping
        limit = math.pi / 2 - 0.01
        self.elevation = max(-limit, min(limit, self.elevation))

    @property
    def view_matrix(self) -> np.ndarray:
        dist = self.camera_distance + self.shift_depth
        elev, azim = self.elevation, self.azimuth
        eye = np.array([
            dist * math.cos(elev) * math.cos(azim),
            dist * math.cos(elev) * math.sin(azim),
            dist * math.sin(elev),
        ], dtype=np.float32)
        return look_at(
            eye,
            np.zeros(3, dtype=np.float32),
            np.array([0.0, 0.0, 1.0], dtype=np.float32),
        )

    @property
    def projection_matrix(self) -> np.ndarray:
        aspect = config.WINDOW_WIDTH / max(1, config.WINDOW_HEIGHT)
        return perspective(config.FOV, aspect, config.NEAR_CLIP, config.FAR_CLIP)
