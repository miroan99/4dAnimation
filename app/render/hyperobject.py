import numpy as np
import OpenGL.GL as gl

from app.render.shader import Shader
from app.utils.math4d import project_4d_to_3d


# ---------------------------------------------------------------------------
# Pure-Python helpers (no GL required — safe to call from tests)
# ---------------------------------------------------------------------------

def compute_cross_section_edges(
    vertices_4d: np.ndarray,
    faces: list[list[int]],
    rotation_4d: np.ndarray,
    slice_w: float,
    tolerance: float = 0.05,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Return 3D line segments where the rotated 4D object crosses w=slice_w.

    For each 4D face (polygon of vertex indices listed in cyclic order),
    collects the intersection points produced by its edges and connects
    them into a polygon.  This yields a proper connected cross-section
    instead of isolated dots.

    Args:
        vertices_4d: N×4 float32 array of 4D vertex positions.
        faces:       List of vertex-index cycles, each defining a flat 4D face.
        rotation_4d: 4×4 rotation matrix applied before slicing.
        slice_w:     W coordinate of the slicing hyperplane.
        tolerance:   Proximity threshold for a vertex touching the hyperplane.

    Returns:
        List of (p0, p1) pairs of (3,) float32 arrays representing line segments.
    """
    rotated: np.ndarray = vertices_4d @ rotation_4d.T  # N×4
    result: list[tuple[np.ndarray, np.ndarray]] = []

    for face in faces:
        n = len(face)
        pts: list[np.ndarray] = []

        for k in range(n):
            i = face[k]
            j = face[(k + 1) % n]
            wi = float(rotated[i, 3])
            wj = float(rotated[j, 3])
            di = wi - slice_w
            dj = wj - slice_w

            # Only test vertex i to avoid double-counting shared vertices.
            # Vertex j will be captured as vertex i of the next edge.
            if abs(di) <= tolerance:
                pts.append(rotated[i, :3].astype(np.float32))
            elif di * dj < 0.0:          # edge straddles the hyperplane
                t = di / (di - dj)
                pt = rotated[i, :3] + t * (rotated[j, :3] - rotated[i, :3])
                pts.append(pt.astype(np.float32))

        # Connect intersection points into line segments.
        # 2 points → 1 segment; ≥3 points → close the polygon.
        if len(pts) >= 2:
            for k in range(len(pts) - 1):
                result.append((pts[k], pts[k + 1]))
            if len(pts) >= 3:
                result.append((pts[-1], pts[0]))

    return result


def compute_cross_section(
    vertices_4d: np.ndarray,
    edges: list[tuple[int, int]],
    rotation_4d: np.ndarray,
    slice_w: float,
    tolerance: float = 0.05,
) -> list[np.ndarray]:
    """Return 3D intersection points where the rotated 4D object crosses w=slice_w.

    For each edge, checks whether it straddles or touches the hyperplane
    w = *slice_w* (within *tolerance*) and, if so, linearly interpolates to
    find the exact crossing point, returning its (x, y, z) coordinates.

    Args:
        vertices_4d: N×4 float32 array of 4D vertex positions.
        edges:       List of (i, j) index pairs defining the edges.
        rotation_4d: 4×4 rotation matrix applied before slicing.
        slice_w:     W coordinate of the slicing hyperplane.
        tolerance:   How close a vertex's w must be to slice_w to count as
                     touching the hyperplane (avoids floating-point gaps).

    Returns:
        List of (3,) float32 arrays, one per intersecting edge.
    """
    rotated: np.ndarray = vertices_4d @ rotation_4d.T  # N×4
    points: list[np.ndarray] = []

    for i, j in edges:
        wi = float(rotated[i, 3])
        wj = float(rotated[j, 3])
        di = wi - slice_w
        dj = wj - slice_w

        if abs(di) <= tolerance:
            points.append(rotated[i, :3].astype(np.float32))
        elif abs(dj) <= tolerance:
            points.append(rotated[j, :3].astype(np.float32))
        elif di * dj < 0.0:  # edge straddles the hyperplane
            t = di / (di - dj)
            pt = rotated[i, :3] + t * (rotated[j, :3] - rotated[i, :3])
            points.append(pt.astype(np.float32))

    return points


def _slice_w_color(slice_w: float) -> np.ndarray:
    """Map slice_w ∈ [-1, 1] to a blue → white → red gradient (3,) float32.

    w = -1.0  →  blue  (0.0, 0.4, 1.0)
    w =  0.0  →  white (1.0, 1.0, 1.0)
    w = +1.0  →  red   (1.0, 0.2, 0.0)
    """
    t = float(np.clip((slice_w + 1.0) / 2.0, 0.0, 1.0))
    blue  = np.array([0.0, 0.4, 1.0], dtype=np.float32)
    white = np.array([1.0, 1.0, 1.0], dtype=np.float32)
    red   = np.array([1.0, 0.2, 0.0], dtype=np.float32)
    if t <= 0.5:
        s = t * 2.0
        return (blue + s * (white - blue)).astype(np.float32)
    s = (t - 0.5) * 2.0
    return (white + s * (red - white)).astype(np.float32)


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

    def __init__(
        self,
        vertices_4d: np.ndarray,
        edges: list[tuple[int, int]],
        faces: list[list[int]] | None = None,
    ):
        self.vertices_4d = vertices_4d.astype(np.float32)  # N×4
        self.edges = edges                                   # M×2 index pairs
        self.faces = faces                                   # optional face cycles
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

        # Cross-section VAO/VBO — same attribute layout; data uploaded dynamically.
        self._cs_vao = gl.glGenVertexArrays(1)
        self._cs_vbo = gl.glGenBuffers(1)
        gl.glBindVertexArray(self._cs_vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._cs_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, stride, None, gl.GL_DYNAMIC_DRAW)
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

    def draw(self, renderer, rotation_4d: np.ndarray, ghost: bool = False) -> None:
        """Project and render the 4D object as a wireframe.

        Args:
            renderer:    Active :class:`Renderer` (provides camera matrices).
            rotation_4d: 4×4 rotation matrix for the current frame.
            ghost:       When True, draws with a uniform dim grey colour
                         instead of the W-depth gradient.  Used to show a
                         faint reference outline during cross-section mode.
        """
        # 1. Rotate all vertices in 4D
        rotated = self.vertices_4d @ rotation_4d.T  # N×4

        # 2. Project 4D → 3D
        xyz, w_vals = project_4d_to_3d(rotated)  # N×3, N

        # 3. Compute per-vertex colours (dim grey for ghost, gradient otherwise)
        if ghost:
            colors = np.full((len(rotated), 3), 0.12, dtype=np.float32)
        else:
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

    # ------------------------------------------------------------------
    def get_cross_section(
        self,
        rotation_4d: np.ndarray,
        slice_w: float,
        tolerance: float = 0.05,
    ) -> list[tuple[np.ndarray, np.ndarray]] | list[np.ndarray]:
        """Return the cross-section of this object at w=slice_w.

        When face data is available, returns a list of (p0, p1) edge pairs
        forming a proper connected polygon.  Otherwise falls back to returning
        a flat list of (3,) intersection points (one per edge).

        Args:
            rotation_4d: 4×4 rotation matrix for the current frame.
            slice_w:     W coordinate of the slicing hyperplane.
            tolerance:   Proximity threshold for touching the hyperplane.
        """
        if self.faces is not None:
            return compute_cross_section_edges(
                self.vertices_4d, self.faces, rotation_4d, slice_w, tolerance
            )
        return compute_cross_section(
            self.vertices_4d, self.edges, rotation_4d, slice_w, tolerance
        )

    def draw_cross_section(
        self,
        renderer,
        rotation_4d: np.ndarray,
        slice_w: float,
        tolerance: float = 0.05,
    ) -> None:
        """Render the W-hyperplane cross-section as connected GL_LINES.

        When face data is present (e.g. Tesseract), each 4D face's
        intersection points are connected into a polygon, producing a proper
        3D solid cross-section.  Without face data (e.g. HyperSphere) the
        method falls back to rendering adjacency lines between intersection
        points that share a 4D vertex.

        Args:
            renderer:    The active :class:`Renderer` (provides camera matrices).
            rotation_4d: 4×4 rotation matrix for the current frame.
            slice_w:     W coordinate of the slicing hyperplane.
            tolerance:   Proximity threshold for touching the hyperplane.
        """
        color = _slice_w_color(slice_w)

        self.shader.use()
        self.shader.set_mat4("model", np.eye(4, dtype=np.float32))
        self.shader.set_mat4("view", renderer.camera.view_matrix)
        self.shader.set_mat4("projection", renderer.camera.projection_matrix)

        gl.glBindVertexArray(self._cs_vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._cs_vbo)

        if self.faces is not None:
            # Face-based: get connected edge pairs and render as GL_LINES.
            seg_pairs = compute_cross_section_edges(
                self.vertices_4d, self.faces, rotation_4d, slice_w, tolerance
            )
            if not seg_pairs:
                gl.glBindVertexArray(0)
                return

            buf = np.empty((len(seg_pairs) * 2, 6), dtype=np.float32)
            for k, (p0, p1) in enumerate(seg_pairs):
                buf[k * 2,     :3] = p0
                buf[k * 2,     3:] = color
                buf[k * 2 + 1, :3] = p1
                buf[k * 2 + 1, 3:] = color

            gl.glBufferData(gl.GL_ARRAY_BUFFER, buf.nbytes, buf, gl.GL_DYNAMIC_DRAW)
            gl.glLineWidth(3.0)
            gl.glDrawArrays(gl.GL_LINES, 0, len(seg_pairs) * 2)
        else:
            # Fallback: adjacency lines between edge-intersection points that
            # share a 4D vertex (used by HyperSphere and other face-free objects).
            rotated: np.ndarray = self.vertices_4d @ rotation_4d.T
            edge_hits: list[tuple[tuple[int, int], np.ndarray]] = []
            for i, j in self.edges:
                wi = float(rotated[i, 3])
                wj = float(rotated[j, 3])
                di = wi - slice_w
                dj = wj - slice_w
                if abs(di) <= tolerance:
                    edge_hits.append(((i, j), rotated[i, :3].astype(np.float32)))
                elif abs(dj) <= tolerance:
                    edge_hits.append(((i, j), rotated[j, :3].astype(np.float32)))
                elif di * dj < 0.0:
                    t = di / (di - dj)
                    pt = (rotated[i, :3] + t * (rotated[j, :3] - rotated[i, :3])).astype(np.float32)
                    edge_hits.append(((i, j), pt))

            if not edge_hits:
                gl.glBindVertexArray(0)
                return

            line_rows: list[np.ndarray] = []
            n = len(edge_hits)
            for a in range(n):
                for b in range(a + 1, n):
                    if set(edge_hits[a][0]) & set(edge_hits[b][0]):
                        line_rows.append(np.concatenate([edge_hits[a][1], color]))
                        line_rows.append(np.concatenate([edge_hits[b][1], color]))

            if line_rows:
                ln_buf = np.array(line_rows, dtype=np.float32)
                gl.glBufferData(gl.GL_ARRAY_BUFFER, ln_buf.nbytes, ln_buf, gl.GL_DYNAMIC_DRAW)
                gl.glLineWidth(2.0)
                gl.glDrawArrays(gl.GL_LINES, 0, len(line_rows))

        gl.glBindVertexArray(0)

    def __del__(self):
        try:
            gl.glDeleteVertexArrays(1, [self._vao])
            gl.glDeleteBuffers(1, [self._vbo])
            gl.glDeleteVertexArrays(1, [self._cs_vao])
            gl.glDeleteBuffers(1, [self._cs_vbo])
        except Exception:
            pass
