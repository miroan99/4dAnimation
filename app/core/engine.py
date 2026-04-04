import pygame
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

from app import config
from app.core.input import InputHandler
from app.core.camera import Camera
from app.core.debug import DebugOverlay
from app.core.rotation4d import Rotation4D
from app.render.renderer import Renderer
from app.scene.scene import Scene
from app.ui.hud import HUD
from app.ui.menu import Menu
from app.utils.gl_utils import log_gl_info


class Engine:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
            DOUBLEBUF | OPENGL | RESIZABLE,
        )
        pygame.display.set_caption(config.WINDOW_TITLE)

        log_gl_info()

        self.clock = pygame.time.Clock()
        self.running = False

        # App state from rawdata.py
        self.rotation_mode = 0
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.shift_depth = 0.0
        self.show_cube = True
        self.show_cube_faces = True
        self.show_grid = True
        self.show_world_axes = True
        self.show_rotation_axes = True
        self.show_tesseract = True

        self.rotation4d = Rotation4D()

        self.input = InputHandler()
        self.camera = Camera()
        self.renderer = Renderer(self.camera)
        self.scene = Scene()
        self.debug = DebugOverlay()
        self.hud = HUD()
        self.menu = Menu()

    def _handle_input(self):
        inp = self.input

        if inp.resize_event:
            w, h = inp.resize_event
            pygame.display.set_mode((w, h), DOUBLEBUF | OPENGL | RESIZABLE)
            self.renderer.resize(w, h)

        if inp.scroll_y:
            self.shift_depth = max(-2.5, min(4.0, self.shift_depth - inp.scroll_y * 0.1))

        if inp.right_clicked:
            self.shift_depth = max(-2.5, self.shift_depth - 0.25)

        if inp.left_clicked:
            if self.menu.handle_click(inp.mouse_pos, self):
                pass  # menu consumed the click
            elif inp.shift_held:
                self.shift_depth = min(4.0, self.shift_depth + 0.25)
            else:
                both_visible = self.show_cube and self.show_tesseract
                if not both_visible:
                    if self.show_cube:
                        self.rotation_mode = (self.rotation_mode + 1) % len(config.MODE_NAMES)
                    elif self.show_tesseract:
                        n = len(config.ROTATION4D_MODE_NAMES)
                        self.rotation4d.mode = (self.rotation4d.mode + 1) % n

        self.shift_depth = max(-2.5, min(4.0, self.shift_depth))
        self.camera.shift_depth = self.shift_depth

    def reset_rotation(self) -> None:
        """Reset visible object(s) to their default orientation (zero angles)."""
        if self.show_cube:
            self.angle_x = self.angle_y = self.angle_z = 0.0
        if self.show_tesseract:
            for plane in self.rotation4d.angles:
                self.rotation4d.angles[plane] = 0.0

    def _update_rotation(self, dt: float):
        axes = config.MODE_AXES[self.rotation_mode]
        delta = config.ROTATION_SPEED_DEG * dt
        if "x" in axes:
            self.angle_x = (self.angle_x + delta) % 360.0
        if "y" in axes:
            self.angle_y = (self.angle_y + delta) % 360.0
        if "z" in axes:
            self.angle_z = (self.angle_z + delta) % 360.0
        if self.show_tesseract:
            self.rotation4d.update(dt)

    def run(self):
        self.running = True
        while self.running:
            delta = self.clock.tick(config.TARGET_FPS) / 1000.0

            self.input.process()
            if self.input.quit_requested:
                self.running = False

            self._handle_input()
            self._update_rotation(delta)

            self.renderer.begin_frame()
            self.scene.draw(
                self.renderer,
                self.angle_x, self.angle_y, self.angle_z,
                self.rotation_mode,
                self.show_cube, self.show_cube_faces,
                self.show_grid, self.show_world_axes, self.show_rotation_axes,
                self.show_tesseract, self.rotation4d.matrix,
            )
            self.hud.draw(
                self.rotation_mode, self.shift_depth, self.rotation4d,
                self.show_cube, self.show_tesseract,
            )
            self.menu.draw(
                self.show_grid, self.show_world_axes, self.show_rotation_axes,
                self.show_tesseract, self.show_cube, self.show_cube_faces,
            )
            self.debug.draw(self.clock.get_fps())
            self.renderer.end_frame()

        pygame.quit()