from itertools import combinations

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


def _build_faces() -> list[list[int]]:
    """Generate the 24 square faces of the tesseract as vertex index quads.

    A face is formed by choosing 2 of the 4 axes to vary and fixing the
    remaining 2 at each of their 2 values: C(4,2) × 2² = 24 faces.

    Vertex bit-encoding: bit k of the index selects +0.5 (1) or −0.5 (0)
    along axis k.  The four vertices of each face are listed in cyclic order
    so that consecutive pairs differ in exactly one bit — i.e. are connected
    by a tesseract edge.
    """
    faces: list[list[int]] = []
    for a, b in combinations(range(4), 2):
        fixed = [x for x in range(4) if x != a and x != b]
        c, d = fixed
        for fc in range(2):
            for fd in range(2):
                base = (fc << c) | (fd << d)
                v00 = base                      # a=0, b=0
                v10 = base | (1 << a)           # a=1, b=0
                v11 = base | (1 << a) | (1 << b)  # a=1, b=1
                v01 = base | (1 << b)           # a=0, b=1
                faces.append([v00, v10, v11, v01])
    return faces  # 24 faces


_VERTICES, _EDGES = _build_tesseract()
_FACES = _build_faces()


class Tesseract(HyperObject):
    """A 4D hypercube (tesseract) with 16 vertices, 32 edges, and 24 faces.

    When projected into 3D using 4D perspective projection it produces the
    familiar "cube within a cube" shape.  As it rotates in the XW and YW
    planes the inner and outer cubes continuously exchange roles in a way
    that is impossible in 3D geometry.
    """

    def __init__(self):
        super().__init__(_VERTICES, _EDGES, faces=_FACES)
