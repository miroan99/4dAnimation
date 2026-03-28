import numpy as np

from app.utils.math3d import translate, rotate_x, rotate_y, rotate_z, scale


class Object3D:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.rotation = np.array([0.0, 0.0, 0.0], dtype=np.float32)  # degrees
        self.scale_vec = np.array([1.0, 1.0, 1.0], dtype=np.float32)

    @property
    def model_matrix(self) -> np.ndarray:
        m = translate(self.position)
        m = m @ rotate_x(self.rotation[0])
        m = m @ rotate_y(self.rotation[1])
        m = m @ rotate_z(self.rotation[2])
        m = m @ scale(self.scale_vec)
        return m

    def update(self, delta: float):
        pass

    def draw(self, renderer):
        pass
