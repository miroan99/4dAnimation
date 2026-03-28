import numpy as np
import OpenGL.GL as gl


class Mesh:
    def __init__(self, vertices: np.ndarray, indices: np.ndarray | None = None):
        self._indexed = indices is not None
        self._count = len(indices) if self._indexed else len(vertices)

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1) if self._indexed else None

        gl.glBindVertexArray(self.vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        if self._indexed:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

        # layout(location=0): position (3 floats)
        stride = vertices.shape[1] * vertices.itemsize
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        # layout(location=1): normal (3 floats) if available
        if vertices.shape[1] >= 6:
            gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, gl.ctypes.c_void_p(12))
            gl.glEnableVertexAttribArray(1)

        gl.glBindVertexArray(0)

    def draw(self, mode=gl.GL_TRIANGLES):
        gl.glBindVertexArray(self.vao)
        if self._indexed:
            gl.glDrawElements(mode, self._count, gl.GL_UNSIGNED_INT, None)
        else:
            gl.glDrawArrays(mode, 0, self._count)
        gl.glBindVertexArray(0)

    def __del__(self):
        try:
            gl.glDeleteVertexArrays(1, [self.vao])
            gl.glDeleteBuffers(1, [self.vbo])
            if self.ebo is not None:
                gl.glDeleteBuffers(1, [self.ebo])
        except Exception:
            pass
