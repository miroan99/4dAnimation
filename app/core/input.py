import pygame
from pygame.locals import KMOD_SHIFT


class InputHandler:
    def __init__(self):
        self.quit_requested = False
        self.keys = {}
        self.mouse_delta = (0, 0)
        self.mouse_buttons = {}

        # Per-frame events (reset each process() call)
        self.left_clicked = False
        self.right_clicked = False
        self.shift_held = False
        self.scroll_y = 0
        self.resize_event = None  # (w, h) or None

    def process(self):
        self.mouse_delta = (0, 0)
        self.left_clicked = False
        self.right_clicked = False
        self.scroll_y = 0
        self.resize_event = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_requested = True
                self.keys[event.key] = True
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_delta = event.rel
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons[event.button] = True
                if event.button == 1:
                    self.left_clicked = True
                    self.shift_held = bool(pygame.key.get_mods() & KMOD_SHIFT)
                elif event.button == 3:
                    self.right_clicked = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons[event.button] = False
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_y = event.y
            elif event.type == pygame.VIDEORESIZE:
                self.resize_event = (event.w, event.h)

    def is_key_held(self, key: int) -> bool:
        return self.keys.get(key, False)

    @property
    def mouse_pos(self):
        return pygame.mouse.get_pos()