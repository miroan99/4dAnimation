import numpy as np
import OpenGL.GL as gl

from app import config
from app.render.mesh import Mesh
from app.render.shader import Shader
from app.scene.object3d import Object3D


def _build_cube_vertices():
    """24 vertices: 4 per face, each with pos(3) + normal(3) + color(3)."""
    h = 0.5
    faces = [
        ("+x", ( 1, 0, 0), [( h,-h,-h),( h, h,-h),( h, h, h),( h,-h, h)]),
        ("-x", (-1, 0, 0), [(-h,-h,-h),(-h,-h, h),(-h, h, h),(-h, h,-h)]),
        ("+y", ( 0, 1, 0), [(-h, h,-h),(-h, h, h),( h, h, h),( h, h,-h)]),
        ("-y", ( 0,-1, 0), [(-h,-h,-h),( h,-h,-h),( h,-h, h),(-h,-h, h)]),
        ("+z", ( 0, 0, 1), [(-h,-h, h),( h,-h, h),( h, h, h),(-h, h, h)]),
        ("-z", ( 0, 0,-1), [(-h,-h,-h),(-h, h,-h),( h, h,-h),( h,-h,-h)]),
    ]
    vertices, indices = [], []
    for i, (face_key, normal, verts) in enumerate(faces):
        color = config.FACE_COLORS[face_key]
        base = i * 4
        for v in verts:
            vertices.append([*v, *normal, *color])
        indices += [base, base + 1, base + 2, base + 2, base + 3, base]
    return (
        np.array(vertices, dtype=np.float32),
        np.array(indices, dtype=np.uint32),
    )


def _build_edge_vertices():
    """12 edges × 2 verts, white, pos(3) + color(3)."""
    h = 0.5
    edges = [
        ((-h,-h,-h),( h,-h,-h)), (( h,-h,-h),( h, h,-h)),
        (( h, h,-h),(-h, h,-h)), ((-h, h,-h),(-h,-h,-h)),
        ((-h,-h, h),( h,-h, h)), (( h,-h, h),( h, h, h)),
        (( h, h, h),(-h, h, h)), ((-h, h, h),(-h,-h, h)),
        ((-h,-h,-h),(-h,-h, h)), (( h,-h,-h),( h,-h, h)),
        (( h, h,-h),( h, h, h)), ((-h, h,-h),(-h, h, h)),
    ]
    verts = []
    for a, b in edges:
        verts.append([*a, 1.0, 1.0, 1.0])
        verts.append([*b, 1.0, 1.0, 1.0])
    return np.array(verts, dtype=np.float32)


_VERTICES, _INDICES = _build_cube_vertices()
_EDGE_VERTICES = _build_edge_vertices()
_IDENTITY = np.eye(4, dtype=np.float32)


class Cube(Object3D):
    def __init__(self):
        super().__init__()
        self.mesh = Mesh(_VERTICES, _INDICES)
        self.edge_mesh = Mesh(_EDGE_VERTICES)
        self.shader = Shader("default.vert", "default.frag")
        self.edge_shader = Shader("unlit.vert", "unlit.frag")

    def draw(self, renderer, show_faces: bool = True):
        model = self.model_matrix

        # Lit coloured faces
        if show_faces:
            self.shader.use()
            renderer.light.apply(self.shader)
            self.shader.set_mat4("model", model)
            self.shader.set_mat4("view", renderer.camera.view_matrix)
            self.shader.set_mat4("projection", renderer.camera.projection_matrix)
            self.mesh.draw()

        # White edges (always drawn when the cube is visible)
        gl.glLineWidth(2.0)
        self.edge_shader.use()
        self.edge_shader.set_mat4("model", model)
        self.edge_shader.set_mat4("view", renderer.camera.view_matrix)
        self.edge_shader.set_mat4("projection", renderer.camera.projection_matrix)
        self.edge_mesh.draw(mode=gl.GL_LINES)
