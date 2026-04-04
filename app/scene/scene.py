import numpy as np

from app.render.cube import Cube
from app.render.axes import WorldAxes, RotationAxes
from app.render.grid import Grid
from app.render.tesseract import Tesseract


class Scene:
    def __init__(self):
        self.cube = Cube()
        self.world_axes = WorldAxes()
        self.rotation_axes = RotationAxes()
        self.grid = Grid()
        self.tesseract = Tesseract()

    def draw(self, renderer,
             angle_x: float, angle_y: float, angle_z: float,
             rotation_mode: int,
             show_cube: bool, show_cube_faces: bool,
             show_grid: bool, show_world_axes: bool, show_rotation_axes: bool,
             show_tesseract: bool, rotation_4d: np.ndarray):
        self.cube.rotation[:] = [angle_x, angle_y, angle_z]

        if show_grid:
            self.grid.draw(renderer)
        if show_world_axes:
            self.world_axes.draw(renderer)
        if show_rotation_axes and rotation_mode > 0:
            self.rotation_axes.draw(renderer, rotation_mode, self.cube.model_matrix)
        if show_cube:
            self.cube.draw(renderer, show_faces=show_cube_faces)
        if show_tesseract:
            self.tesseract.draw(renderer, rotation_4d)
