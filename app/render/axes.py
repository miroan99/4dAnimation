import numpy as np
import OpenGL.GL as gl

from app import config
from app.render.mesh import Mesh
from app.render.shader import Shader

_IDENTITY = np.eye(4, dtype=np.float32)

# World axes: ±2.4 in each direction, pos(3) + color(3)
_AXIS_LEN = 2.4
_WORLD_VERTICES = np.array([
    [-_AXIS_LEN, 0, 0,  1, 0, 0], [ _AXIS_LEN, 0, 0,  1, 0, 0],  # ±X red
    [0, -_AXIS_LEN, 0,  0, 1, 0], [0,  _AXIS_LEN, 0,  0, 1, 0],  # ±Y green
    [0, 0, -_AXIS_LEN,  0, 0, 1], [0, 0,  _AXIS_LEN,  0, 0, 1],  # ±Z blue
], dtype=np.float32)


def _rotation_axis_verts(axis: str) -> list:
    """Build line vertices (pos3 + yellow color3) for one rotation axis."""
    L = 1.2
    a = 0.08
    y = [1.0, 1.0, 0.0]
    if axis == "x":
        return [
            [-L, 0, 0, *y], [ L, 0, 0, *y],
            [ L, 0, 0, *y], [ L - 0.12,  a, 0, *y],
            [ L, 0, 0, *y], [ L - 0.12, -a, 0, *y],
            [-L, 0, 0, *y], [-L + 0.12,  a, 0, *y],
            [-L, 0, 0, *y], [-L + 0.12, -a, 0, *y],
        ]
    elif axis == "y":
        return [
            [0, -L, 0, *y], [0,  L, 0, *y],
            [0,  L, 0, *y], [ a,  L - 0.12, 0, *y],
            [0,  L, 0, *y], [-a,  L - 0.12, 0, *y],
            [0, -L, 0, *y], [ a, -L + 0.12, 0, *y],
            [0, -L, 0, *y], [-a, -L + 0.12, 0, *y],
        ]
    else:  # z
        return [
            [0, 0, -L, *y], [0, 0,  L, *y],
            [0, 0,  L, *y], [ a, 0,  L - 0.12, *y],
            [0, 0,  L, *y], [-a, 0,  L - 0.12, *y],
            [0, 0, -L, *y], [ a, 0, -L + 0.12, *y],
            [0, 0, -L, *y], [-a, 0, -L + 0.12, *y],
        ]


_ROT_AXIS_MESHES: dict[str, np.ndarray] = {
    ax: np.array(_rotation_axis_verts(ax), dtype=np.float32)
    for ax in ("x", "y", "z")
}


class WorldAxes:
    def __init__(self):
        self.mesh = Mesh(_WORLD_VERTICES)
        self.shader = Shader("unlit.vert", "unlit.frag")

    def draw(self, renderer):
        gl.glLineWidth(2.5)
        self.shader.use()
        self.shader.set_mat4("model", _IDENTITY)
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)
        self.mesh.draw(mode=gl.GL_LINES)


class RotationAxes:
    def __init__(self):
        self._meshes = {ax: Mesh(verts) for ax, verts in _ROT_AXIS_MESHES.items()}
        self.shader = Shader("unlit.vert", "unlit.frag")

    def draw(self, renderer, rotation_mode: int, model_matrix: np.ndarray):
        active = config.MODE_AXES[rotation_mode]
        if not active:
            return
        gl.glLineWidth(4.0)
        self.shader.use()
        self.shader.set_mat4("model", model_matrix)
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)
        for ax in active:
            self._meshes[ax].draw(mode=gl.GL_LINES)
