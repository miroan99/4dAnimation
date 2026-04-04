import numpy as np
import OpenGL.GL as gl

from app.render.mesh import Mesh
from app.render.shader import Shader

_IDENTITY = np.eye(4, dtype=np.float32)


def _build_grid(extent: float = 3.0, step: float = 0.5) -> np.ndarray:
    """XY-plane grid matching rawdata.py: lines at z=0, extent ±3, step 0.5."""
    lines = []
    i = -extent
    while i <= extent + 1e-6:
        lines += [[i, -extent, 0, 0.35, 0.35, 0.35],
                  [i,  extent, 0, 0.35, 0.35, 0.35]]
        lines += [[-extent, i, 0, 0.35, 0.35, 0.35],
                  [ extent, i, 0, 0.35, 0.35, 0.35]]
        i += step
    return np.array(lines, dtype=np.float32)


class Grid:
    def __init__(self):
        self.mesh = Mesh(_build_grid())
        self.shader = Shader("unlit.vert", "unlit.frag")

    def draw(self, renderer):
        gl.glLineWidth(1.0)
        self.shader.use()
        self.shader.set_mat4("model", _IDENTITY)
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)
        self.mesh.draw(mode=gl.GL_LINES)
