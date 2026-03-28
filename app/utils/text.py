import pygame


class TextRenderer:
    def __init__(self, font_path: str | None = None, size: int = 18):
        pygame.font.init()
        if font_path:
            self.font = pygame.font.Font(font_path, size)
        else:
            self.font = pygame.font.SysFont("monospace", size)

    def render(self, surface: pygame.Surface, text: str, x: int, y: int,
               color=(255, 255, 255)):
        surf = self.font.render(text, True, color)
        surface.blit(surf, (x, y))
