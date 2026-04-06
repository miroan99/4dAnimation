import numpy as np

from app.render.cube import Cube
from app.render.axes import WorldAxes, RotationAxes
from app.render.grid import Grid
from app.render.tesseract import Tesseract
from app.render.hypersphere import HyperSphere


class Scene:
    def __init__(self):
        self.cube = Cube()
        self.world_axes = WorldAxes()
        self.rotation_axes = RotationAxes()
        self.grid = Grid()
        self.tesseract = Tesseract()
        self.hypersphere = HyperSphere()

    def draw(self, renderer,
             angle_x: float, angle_y: float, angle_z: float,
             rotation_mode: int,
             selected_body: str,
             show_cube_faces: bool,
             show_grid: bool, show_world_axes: bool, show_rotation_axes: bool,
             rotation_4d: np.ndarray,
             cross_section_mode: bool = False,
             slice_w: float = 0.0):
        self.cube.rotation[:] = [angle_x, angle_y, angle_z]

        if show_grid:
            self.grid.draw(renderer)
        if show_world_axes:
            self.world_axes.draw(renderer)
        if show_rotation_axes and rotation_mode > 0 and selected_body == "cube":
            self.rotation_axes.draw(renderer, rotation_mode, self.cube.model_matrix)

        if selected_body == "cube":
            self.cube.draw(renderer, show_faces=show_cube_faces)
        elif selected_body == "tesseract":
            if cross_section_mode:
                # Ghost wireframe gives spatial context; bright cross-section on top.
                self.tesseract.draw(renderer, rotation_4d, ghost=True)
                self.tesseract.draw_cross_section(renderer, rotation_4d, slice_w)
            else:
                self.tesseract.draw(renderer, rotation_4d)
        elif selected_body == "hypersphere":
            if cross_section_mode:
                self.hypersphere.draw(renderer, rotation_4d, ghost=True)
                self.hypersphere.draw_cross_section(renderer, rotation_4d, slice_w)
            else:
                self.hypersphere.draw(renderer, rotation_4d)
