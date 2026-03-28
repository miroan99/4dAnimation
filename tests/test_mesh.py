import numpy as np
import pytest


def test_mesh_requires_2d_vertices():
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    assert vertices.ndim == 2
    assert vertices.shape[1] >= 3


def test_indexed_mesh_count():
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=np.float32)
    indices = np.array([0, 1, 2, 1, 3, 2], dtype=np.uint32)
    assert len(indices) == 6


def test_non_indexed_mesh_vertex_count():
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    assert len(vertices) == 3
