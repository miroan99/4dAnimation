import pygame

from app import config
from app.utils.text import draw_gl_text


class HUD:
    def __init__(self):
        self._font = pygame.font.SysFont("consolas", 20)

    def draw(self, rotation_mode: int, shift_depth: float,
             rotation4d=None, selected_body: str = "cube"):
        y = 18

        if selected_body == "cube":
            draw_gl_text(self._font, f"3D:  {config.MODE_NAMES[rotation_mode]}", 20, y)
            y += 24
        elif rotation4d is not None:
            draw_gl_text(self._font, f"4D:  {rotation4d.mode_name}", 20, y)
            y += 24
            if rotation4d.mode == config.CROSS_SECTION_MODE:
                draw_gl_text(
                    self._font,
                    f"W:   {rotation4d.cross_section.slice_w:+.3f}",
                    20, y,
                )
                y += 24

        draw_gl_text(self._font, f"Depth: {shift_depth:.2f}", 20, y)
