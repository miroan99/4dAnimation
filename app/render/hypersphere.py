import numpy as np

from app.render.hyperobject import HyperObject


def _build_hypersphere(r: float = 0.5, n_alpha: int = 5, n_beta: int = 4, n_seg: int = 24):
    """Build a wireframe 3-sphere using a family of great circles.

    Each great circle is parametrized as:
        v(t) = r * (cos α · cos t,  sin α · cos t,  cos β · sin t,  sin β · sin t)

    Verifying |v| = r for all t:
        |v|² = r² (cos²α cos²t + sin²α cos²t + cos²β sin²t + sin²β sin²t)
             = r² (cos²t + sin²t) = r²  ✓

    Sweeping over a grid of (α, β) ∈ [0, π) × [0, π) samples the hypersphere
    from many angles, producing the familiar "sphere of spheres" projection.
    """
    alpha_vals = np.linspace(0, np.pi, n_alpha + 1)[:-1]
    beta_vals  = np.linspace(0, np.pi, n_beta  + 1)[:-1]
    t_vals     = np.linspace(0, 2.0 * np.pi, n_seg, endpoint=False)

    verts: list[list[float]] = []
    edges: list[tuple[int, int]] = []

    for alpha in alpha_vals:
        ca, sa = float(np.cos(alpha)), float(np.sin(alpha))
        for beta in beta_vals:
            cb, sb = float(np.cos(beta)), float(np.sin(beta))
            base = len(verts)
            for t in t_vals:
                ct, st = float(np.cos(t)), float(np.sin(t))
                verts.append([r * ca * ct, r * sa * ct, r * cb * st, r * sb * st])
            for k in range(n_seg):
                edges.append((base + k, base + (k + 1) % n_seg))

    return np.array(verts, dtype=np.float32), edges


_VERTICES, _EDGES = _build_hypersphere()


class HyperSphere(HyperObject):
    """A 4D hypersphere (3-sphere) rendered as great circles projected to 3D."""

    def __init__(self):
        super().__init__(_VERTICES, _EDGES)
