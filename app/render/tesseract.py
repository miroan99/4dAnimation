import numpy as np

from app.render.hyperobject import HyperObject


def _build_tesseract() -> tuple[np.ndarray, list[tuple[int, int]]]:
    """Generate the 16 vertices and 32 edges of a unit tesseract.

    Vertices: all 2^4 = 16 combinations of (±0.5) in four dimensions.
    Edges: pairs of vertices that differ in exactly one coordinate
           (i.e. are connected by an edge of a unit hypercube).

    The XOR trick:
        vertex index i encoded as 4 bits → each bit selects +0.5 or −0.5
        per axis.  Two vertices share an edge iff their indices differ by
        exactly one bit (XOR is a power of two).
    """
    verts = np.array(
        [[0.5 if (i >> b) & 1 else -0.5 for b in range(4)] for i in range(16)],
        dtype=np.float32,
    )

    edges = [
        (i, j)
        for i in range(16)
        for j in range(i + 1, 16)
        if _is_power_of_two(i ^ j)
    ]  # exactly 32 edges

    return verts, edges


def _is_power_of_two(n: int) -> bool:
    return n != 0 and (n & (n - 1)) == 0


_VERTICES, _EDGES = _build_tesseract()


class Tesseract(HyperObject):
    """A 4D hypercube (tesseract) with 16 vertices and 32 edges.

    When projected into 3D using 4D perspective projection it produces the
    familiar "cube within a cube" shape.  As it rotates in the XW and YW
    planes the inner and outer cubes continuously exchange roles in a way
    that is impossible in 3D geometry.
    """

    def __init__(self):
        super().__init__(_VERTICES, _EDGES)
