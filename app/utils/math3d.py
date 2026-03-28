import numpy as np


def translate(v) -> np.ndarray:
    m = np.eye(4, dtype=np.float32)
    m[0, 3] = v[0]
    m[1, 3] = v[1]
    m[2, 3] = v[2]
    return m


def scale(v) -> np.ndarray:
    m = np.eye(4, dtype=np.float32)
    m[0, 0] = v[0]
    m[1, 1] = v[1]
    m[2, 2] = v[2]
    return m


def rotate_x(deg: float) -> np.ndarray:
    r = np.radians(deg)
    c, s = np.cos(r), np.sin(r)
    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1],
    ], dtype=np.float32)


def rotate_y(deg: float) -> np.ndarray:
    r = np.radians(deg)
    c, s = np.cos(r), np.sin(r)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1],
    ], dtype=np.float32)


def rotate_z(deg: float) -> np.ndarray:
    r = np.radians(deg)
    c, s = np.cos(r), np.sin(r)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1],
    ], dtype=np.float32)


def look_at(eye, center, up) -> np.ndarray:
    f = center - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return np.array([
        [ r[0],  r[1],  r[2], -np.dot(r, eye)],
        [ u[0],  u[1],  u[2], -np.dot(u, eye)],
        [-f[0], -f[1], -f[2],  np.dot(f, eye)],
        [    0,     0,     0,               1],
    ], dtype=np.float32)


def perspective(fov_deg: float, aspect: float, near: float, far: float) -> np.ndarray:
    f = 1.0 / np.tan(np.radians(fov_deg) / 2.0)
    return np.array([
        [f / aspect, 0,                              0,  0],
        [0,          f,                              0,  0],
        [0,          0,   (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0,          0,                             -1,  0],
    ], dtype=np.float32)
