from dataclasses import dataclass, field

import numpy as np

from app.utils.math4d import PLANES, build_rotation_4d


@dataclass
class CrossSectionState:
    """Animation state for the W-hyperplane cross-section mode.

    Attributes:
        slice_w:   Current W coordinate of the slicing hyperplane, in [-1, 1].
        speed:     Animation speed in W-units per second.
        direction: +1 advances towards +1.0, -1 towards -1.0; reverses at bounds.
    """
    slice_w: float = 0.0
    speed: float = 0.5
    direction: int = 1


class Rotation4D:
    """Manages the 4D rotation mode and advances plane angles over time.

    The mode integer indexes into config.ROTATION4D_MODE_PLANES, selecting
    which of the 6 rotation planes are active.  Each active plane advances
    at its own coprime speed so the pattern never exactly repeats.
    """

    def __init__(self):
        self.angles: dict[str, float] = {p: 0.0 for p in PLANES}
        self.mode: int = 4  # default: XW + YW
        self.cross_section: CrossSectionState = CrossSectionState()

    def update(self, dt: float) -> None:
        from app import config
        active = config.ROTATION4D_MODE_PLANES[self.mode]
        for plane in active:
            self.angles[plane] = (
                self.angles[plane] + config.ROTATION4D_PLANE_SPEEDS[plane] * dt
            ) % 360.0

    def update_cross_section(self, dt: float) -> None:
        """Advance the W-hyperplane position, reversing direction at ±1.0.

        Args:
            dt: Elapsed time in seconds since the last frame.
        """
        cs = self.cross_section
        cs.slice_w += cs.speed * cs.direction * dt
        if cs.slice_w >= 1.0:
            cs.slice_w = 1.0
            cs.direction = -1
        elif cs.slice_w <= -1.0:
            cs.slice_w = -1.0
            cs.direction = 1

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
