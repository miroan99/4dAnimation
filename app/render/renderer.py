import OpenGL.GL as gl

from app.core.camera import Camera


class Renderer:
    def __init__(self, camera: Camera):
        self.camera = camera
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def begin_frame(self):
        gl.glClearColor(0.1, 0.1, 0.15, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def end_frame(self):
        import pygame
        pygame.display.flip()
