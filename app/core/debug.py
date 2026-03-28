import OpenGL.GL as gl


class DebugOverlay:
    def draw(self, fps: float):
        self._poll_gl_errors()

    def _poll_gl_errors(self):
        while True:
            err = gl.glGetError()
            if err == gl.GL_NO_ERROR:
                break
            print(f"[GL ERROR] 0x{err:04X}")
