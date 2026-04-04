import numpy as np

# The 6 independent planes of rotation in 4D space.
# In 3D there are 3 rotation axes; in 4D there are 6 rotation planes.
PLANES = ('xy', 'xz', 'xw', 'yz', 'yw', 'zw')

_PLANE_INDICES: dict[str, tuple[int, int]] = {
    'xy': (0, 1), 'xz': (0, 2), 'xw': (0, 3),
    'yz': (1, 2), 'yw': (1, 3), 'zw': (2, 3),
}


def rotate_4d(plane: str, deg: float) -> np.ndarray:
    """Return a 4×4 rotation matrix for the given plane in 4D space.

    Works exactly like rotate_x/y/z in math3d, but operates on 4D vectors
    (x, y, z, w).  The two indices of the plane are the axes that rotate;
    all other axes are unaffected.
    """
    r = np.radians(deg)
    c, s = float(np.cos(r)), float(np.sin(r))
    m = np.eye(4, dtype=np.float32)
    i, j = _PLANE_INDICES[plane]
    m[i, i] =  c;  m[i, j] = -s
    m[j, i] =  s;  m[j, j] =  c
    return m


def build_rotation_4d(angles: dict[str, float]) -> np.ndarray:
    """Compose all 6 plane rotations into a single 4×4 rotation matrix."""
    m = np.eye(4, dtype=np.float32)
    for plane in PLANES:
        deg = angles.get(plane, 0.0)
        if deg:
            m = m @ rotate_4d(plane, deg)
    return m


def project_4d_to_3d(
    vertices: np.ndarray, w_dist: float = 2.0
) -> tuple[np.ndarray, np.ndarray]:
    """Perspective-project N×4 vertices from 4D to 3D.

    Exactly analogous to the 3D→2D perspective divide:
        scale = w_dist / (w_dist - w)
        (x3d, y3d, z3d) = (x, y, z) * scale

    Returns:
        projected : N×3 float32 array of 3D positions
        w_vals    : N float32 array of original W coordinates (used for colour)
    """
    w = vertices[:, 3]
    denom = np.clip(w_dist - w, 1e-4, None)
    scale = (w_dist / denom)[:, np.newaxis]
    projected = vertices[:, :3] * scale
    return projected.astype(np.float32), w.astype(np.float32)
