import numpy as np
import pytest
from app.utils.math3d import translate, scale, rotate_y, look_at, perspective


def test_translate():
    m = translate([1, 2, 3])
    assert m[0, 3] == pytest.approx(1.0)
    assert m[1, 3] == pytest.approx(2.0)
    assert m[2, 3] == pytest.approx(3.0)
    assert m[3, 3] == pytest.approx(1.0)


def test_scale():
    m = scale([2, 3, 4])
    assert m[0, 0] == pytest.approx(2.0)
    assert m[1, 1] == pytest.approx(3.0)
    assert m[2, 2] == pytest.approx(4.0)


def test_rotate_y_identity_at_zero():
    m = rotate_y(0.0)
    np.testing.assert_allclose(m, np.eye(4, dtype=np.float32), atol=1e-6)


def test_rotate_y_90():
    m = rotate_y(90.0)
    # forward (0,0,-1) should rotate to (-1,0,0) approximately
    fwd = m[:3, :3] @ np.array([0, 0, -1], dtype=np.float32)
    np.testing.assert_allclose(fwd, [-1, 0, 0], atol=1e-6)


def test_perspective_shape():
    m = perspective(45.0, 16 / 9, 0.1, 1000.0)
    assert m.shape == (4, 4)
    assert m[3, 2] == pytest.approx(-1.0)


def test_look_at_identity():
    eye = np.array([0, 0, 5], dtype=np.float32)
    center = np.array([0, 0, 0], dtype=np.float32)
    up = np.array([0, 1, 0], dtype=np.float32)
    m = look_at(eye, center, up)
    assert m.shape == (4, 4)
