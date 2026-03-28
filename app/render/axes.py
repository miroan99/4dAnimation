import numpy as np
import OpenGL.GL as gl

from app.render.mesh import Mesh
from app.render.shader import Shader


_VERTICES = np.array([
    # X axis — red
    [0, 0, 0,  1, 0, 0],
    [1, 0, 0,  1, 0, 0],
    # Y axis — green
    [0, 0, 0,  0, 1, 0],
    [0, 1, 0,  0, 1, 0],
    # Z axis — blue
    [0, 0, 0,  0, 0, 1],
    [0, 0, 1,  0, 0, 1],
], dtype=np.float32)


class Axes:
    def __init__(self):
        self.mesh = Mesh(_VERTICES)
        self.shader = Shader("unlit.vert", "unlit.frag")

    def draw(self, renderer):
        self.shader.use()
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)
        self.mesh.draw(mode=gl.GL_LINES)
