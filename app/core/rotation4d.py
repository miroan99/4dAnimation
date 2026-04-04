import numpy as np

from app.utils.math4d import PLANES, build_rotation_4d


class Rotation4D:
    """Manages the 4D rotation mode and advances plane angles over time.

    The mode integer indexes into config.ROTATION4D_MODE_PLANES, selecting
    which of the 6 rotation planes are active.  Each active plane advances
    at its own coprime speed so the pattern never exactly repeats.
    """

    def __init__(self):
        self.angles: dict[str, float] = {p: 0.0 for p in PLANES}
        self.mode: int = 4  # default: XW + YW

    def update(self, dt: float) -> None:
        from app import config
        active = config.ROTATION4D_MODE_PLANES[self.mode]
        for plane in active:
            self.angles[plane] = (
                self.angles[plane] + config.ROTATION4D_PLANE_SPEEDS[plane] * dt
            ) % 360.0

    @property
    def matrix(self) -> np.ndarray:
        return build_rotation_4d(self.angles)

    @property
    def mode_name(self) -> str:
        from app import config
        return config.ROTATION4D_MODE_NAMES[self.mode]

    @property
    def active_planes(self) -> list[str]:
        from app import config
        return sorted(config.ROTATION4D_MODE_PLANES[self.mode])
