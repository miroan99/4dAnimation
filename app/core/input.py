import pygame


class InputHandler:
    def __init__(self):
        self.quit_requested = False
        self.keys = {}
        self.mouse_delta = (0, 0)
        self.mouse_buttons = {}

    def process(self):
        self.mouse_delta = (0, 0)

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
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons[event.button] = False

    def is_key_held(self, key: int) -> bool:
        return self.keys.get(key, False)
