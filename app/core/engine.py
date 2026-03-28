import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from app import config
from app.core.input import InputHandler
from app.core.camera import Camera
from app.core.debug import DebugOverlay
from app.render.renderer import Renderer
from app.scene.scene import Scene
from app.utils.gl_utils import log_gl_info


class Engine:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
            DOUBLEBUF | OPENGL,
        )
        pygame.display.set_caption(config.WINDOW_TITLE)

        log_gl_info()

        self.clock = pygame.time.Clock()
        self.running = False

        self.input = InputHandler()
        self.camera = Camera()
        self.renderer = Renderer(self.camera)
        self.scene = Scene()
        self.debug = DebugOverlay()

    def run(self):
        self.running = True
        while self.running:
            delta = self.clock.tick(config.TARGET_FPS) / 1000.0

            self.input.process()
            if self.input.quit_requested:
                self.running = False

            self.camera.update(self.input, delta)
            self.scene.update(delta)

            self.renderer.begin_frame()
            self.scene.draw(self.renderer)
            self.debug.draw(self.clock.get_fps())
            self.renderer.end_frame()

        pygame.quit()
