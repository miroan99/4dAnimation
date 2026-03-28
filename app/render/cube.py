import numpy as np

from app.render.mesh import Mesh
from app.render.shader import Shader
from app.scene.object3d import Object3D


_VERTICES = np.array([
    # position          normal
    [-0.5, -0.5,  0.5,  0,  0,  1],
    [ 0.5, -0.5,  0.5,  0,  0,  1],
    [ 0.5,  0.5,  0.5,  0,  0,  1],
    [-0.5,  0.5,  0.5,  0,  0,  1],
    [-0.5, -0.5, -0.5,  0,  0, -1],
    [ 0.5, -0.5, -0.5,  0,  0, -1],
    [ 0.5,  0.5, -0.5,  0,  0, -1],
    [-0.5,  0.5, -0.5,  0,  0, -1],
], dtype=np.float32)

_INDICES = np.array([
    0, 1, 2, 2, 3, 0,
    4, 5, 6, 6, 7, 4,
    0, 4, 7, 7, 3, 0,
    1, 5, 6, 6, 2, 1,
    3, 2, 6, 6, 7, 3,
    0, 1, 5, 5, 4, 0,
], dtype=np.uint32)


class Cube(Object3D):
    def __init__(self):
        super().__init__()
        self.mesh = Mesh(_VERTICES, _INDICES)
        self.shader = Shader("default.vert", "default.frag")

    def draw(self, renderer):
        self.shader.use()
        self.shader.set_mat4("model", self.model_matrix)
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)
        self.mesh.draw()
