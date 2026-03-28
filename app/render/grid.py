import numpy as np
import OpenGL.GL as gl

from app.render.mesh import Mesh
from app.render.shader import Shader


def _build_grid(size: int = 10, step: float = 1.0) -> np.ndarray:
    lines = []
    for i in range(-size, size + 1):
        v = i * step
        lines += [[-size * step, 0, v, 0.5, 0.5, 0.5],
                  [ size * step, 0, v, 0.5, 0.5, 0.5]]
        lines += [[v, 0, -size * step, 0.5, 0.5, 0.5],
                  [v, 0,  size * step, 0.5, 0.5, 0.5]]
    return np.array(lines, dtype=np.float32)


class Grid:
    def __init__(self, size: int = 10):
        self.mesh = Mesh(_build_grid(size))
        self.shader = Shader("unlit.vert", "unlit.frag")

    def draw(self, renderer):
        self.shader.use()
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)
        self.mesh.draw(mode=gl.GL_LINES)
