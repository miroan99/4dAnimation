import numpy as np
import pygame

from app import config
from app.utils.math3d import look_at, perspective


class Camera:
    def __init__(self):
        self.position = np.array([0.0, 2.0, 5.0], dtype=np.float32)
        self.yaw = -90.0
        self.pitch = -20.0
        self.speed = 5.0
        self.sensitivity = 0.1

        self._update_vectors()

    def _update_vectors(self):
        yaw_r = np.radians(self.yaw)
        pitch_r = np.radians(self.pitch)
        self.front = np.array([
            np.cos(yaw_r) * np.cos(pitch_r),
            np.sin(pitch_r),
            np.sin(yaw_r) * np.cos(pitch_r),
        ], dtype=np.float32)
        self.front /= np.linalg.norm(self.front)
        world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.right = np.cross(self.front, world_up)
        self.right /= np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)

    def update(self, input_handler, delta: float):
        vel = self.speed * delta
        if input_handler.is_key_held(pygame.K_w):
            self.position += self.front * vel
        if input_handler.is_key_held(pygame.K_s):
            self.position -= self.front * vel
        if input_handler.is_key_held(pygame.K_a):
            self.position -= self.right * vel
        if input_handler.is_key_held(pygame.K_d):
            self.position += self.right * vel

        if input_handler.mouse_buttons.get(3):
            dx, dy = input_handler.mouse_delta
            self.yaw += dx * self.sensitivity
            self.pitch -= dy * self.sensitivity
            self.pitch = max(-89.0, min(89.0, self.pitch))
            self._update_vectors()

    @property
    def view_matrix(self) -> np.ndarray:
        return look_at(self.position, self.position + self.front, self.up)

    @property
    def projection_matrix(self) -> np.ndarray:
        aspect = config.WINDOW_WIDTH / config.WINDOW_HEIGHT
        return perspective(config.FOV, aspect, config.NEAR_CLIP, config.FAR_CLIP)
