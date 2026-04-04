import numpy as np

from app import config
from app.utils.math3d import look_at, perspective


def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


class Camera:
    def __init__(self):
        self.camera_distance = config.CAMERA_DISTANCE
        self.shift_depth = 0.0

    def update(self, input_handler, delta: float):
        pass  # fixed camera; shift_depth driven by engine

    @property
    def view_matrix(self) -> np.ndarray:
        dist = self.camera_distance + self.shift_depth
        eye = _normalize(np.array([1.0, 1.0, 1.0], dtype=np.float32)) * dist
        return look_at(
            eye,
            np.zeros(3, dtype=np.float32),
            np.array([0.0, 0.0, 1.0], dtype=np.float32),
        )

    @property
    def projection_matrix(self) -> np.ndarray:
        aspect = config.WINDOW_WIDTH / max(1, config.WINDOW_HEIGHT)
        return perspective(config.FOV, aspect, config.NEAR_CLIP, config.FAR_CLIP)