import OpenGL.GL as gl

from app import config
from app.core.camera import Camera
from app.render.lighting import DirectionalLight


class Renderer:
    def __init__(self, camera: Camera):
        self.camera = camera
        self.light = DirectionalLight()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)

    def resize(self, width: int, height: int):
        config.WINDOW_WIDTH = max(1, width)
        config.WINDOW_HEIGHT = max(1, height)
        gl.glViewport(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    def begin_frame(self):
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def end_frame(self):
        import pygame
        pygame.display.flip()