import numpy as np


class DirectionalLight:
    def __init__(self):
        self.direction = np.array([-0.5, -1.0, -0.5], dtype=np.float32)
        self.color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.ambient = 0.2
        self.diffuse = 0.8

    def apply(self, shader):
        shader.set_vec3("light.direction", self.direction)
        shader.set_vec3("light.color", self.color)
        shader.set_float("light.ambient", self.ambient)
        shader.set_float("light.diffuse", self.diffuse)
