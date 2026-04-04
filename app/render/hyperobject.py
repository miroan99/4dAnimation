import numpy as np
import OpenGL.GL as gl

from app.render.shader import Shader
from app.utils.math4d import project_4d_to_3d


class HyperObject:
    """Base class for 4D geometry rendered by projecting into 3D each frame.

    Stores vertices in 4D (x, y, z, w) and a list of edges as index pairs.
    Every draw call:
      1. Applies the supplied 4D rotation matrix to all vertices.
      2. Perspective-projects from 4D → 3D.
      3. Colours each vertex by its W coordinate (blue=near → red=far in W).
      4. Uploads the resulting line segments to the GPU and draws them.

    The model, view, and projection matrices passed to the shader are plain
    4×4 3D matrices — the 4D math is done on the CPU before upload.
    """

    def __init__(self, vertices_4d: np.ndarray, edges: list[tuple[int, int]]):
        self.vertices_4d = vertices_4d.astype(np.float32)  # N×4
        self.edges = edges                                   # M×2 index pairs
        self.shader = Shader("unlit.vert", "unlit.frag")

        # Pre-allocated edge vertex buffer: 2 verts/edge × 6 floats (pos+color)
        n = len(edges) * 2
        self._buf = np.zeros((n, 6), dtype=np.float32)

        self._vao = gl.glGenVertexArrays(1)
        self._vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self._vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self._buf.nbytes,
            self._buf,
            gl.GL_DYNAMIC_DRAW,
        )
        stride = 6 * 4
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, gl.ctypes.c_void_p(12))
        gl.glEnableVertexAttribArray(1)
        gl.glBindVertexArray(0)

    # ------------------------------------------------------------------
    def _w_to_color(self, w_vals: np.ndarray) -> np.ndarray:
        """Map W ∈ [−0.5, 0.5] to a blue→red gradient (N×3)."""
        t = np.clip(w_vals + 0.5, 0.0, 1.0)
        colors = np.empty((len(t), 3), dtype=np.float32)
        colors[:, 0] = t          # red
        colors[:, 1] = 0.15       # green (kept low for vivid gradient)
        colors[:, 2] = 1.0 - t   # blue
        return colors

    def draw(self, renderer, rotation_4d: np.ndarray) -> None:
        # 1. Rotate all vertices in 4D
        rotated = self.vertices_4d @ rotation_4d.T  # N×4

        # 2. Project 4D → 3D
        xyz, w_vals = project_4d_to_3d(rotated)  # N×3, N

        # 3. Compute per-vertex colours from W depth
        colors = self._w_to_color(w_vals)  # N×3

        # 4. Fill edge vertex buffer
        for k, (i, j) in enumerate(self.edges):
            base = k * 2
            self._buf[base,   :3] = xyz[i]
            self._buf[base,   3:] = colors[i]
            self._buf[base+1, :3] = xyz[j]
            self._buf[base+1, 3:] = colors[j]

        # 5. Upload to GPU
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self._buf.nbytes, self._buf)

        # 6. Draw
        self.shader.use()
        self.shader.set_mat4("model", np.eye(4, dtype=np.float32))
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)

        gl.glLineWidth(2.0)
        gl.glBindVertexArray(self._vao)
        gl.glDrawArrays(gl.GL_LINES, 0, len(self.edges) * 2)
        gl.glBindVertexArray(0)

    def __del__(self):
        try:
            gl.glDeleteVertexArrays(1, [self._vao])
            gl.glDeleteBuffers(1, [self._vbo])
        except Exception:
            pass
