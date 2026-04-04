import pygame

from app.utils.text import draw_gl_text


class Menu:
    def __init__(self):
        self._font = pygame.font.SysFont("consolas", 16)
        self._rects: dict[str, pygame.Rect] = {}

    def handle_click(self, mouse_pos, engine) -> bool:
        """Check if the click hit a menu item and toggle the matching flag. Returns True if consumed."""
        for key, rect in self._rects.items():
            if rect.collidepoint(mouse_pos):
                if key == "grid":
                    engine.show_grid = not engine.show_grid
                elif key == "world_axes":
                    engine.show_world_axes = not engine.show_world_axes
                elif key == "rotation_axes":
                    engine.show_rotation_axes = not engine.show_rotation_axes
                elif key == "tesseract":
                    engine.show_tesseract = not engine.show_tesseract
                elif key == "cube":
                    engine.show_cube = not engine.show_cube
                elif key == "cube_faces":
                    engine.show_cube_faces = not engine.show_cube_faces
                elif key == "reset":
                    engine.reset_rotation()
                return True
        return False

    def draw(self, show_grid: bool, show_world_axes: bool, show_rotation_axes: bool,
             show_tesseract: bool = True, show_cube: bool = True,
             show_cube_faces: bool = True):
        from app import config
        self._rects.clear()

        toggles = [
            ("cube",          f"[{'X' if show_cube else ' '}] 3D Cube"),
            ("cube_faces",    f"[{'X' if show_cube_faces else ' '}] Cube faces"),
            ("grid",          f"[{'X' if show_grid else ' '}] Grid"),
            ("world_axes",    f"[{'X' if show_world_axes else ' '}] Axis"),
            ("rotation_axes", f"[{'X' if show_rotation_axes else ' '}] Rotation axis"),
            ("tesseract",     f"[{'X' if show_tesseract else ' '}] 4D Tesseract"),
        ]

        title_x = config.WINDOW_WIDTH - 210
        draw_gl_text(self._font, "Menu", title_x, 12)

        for i, (key, label) in enumerate(toggles):
            item_y = 34 + i * 22
            surf = self._font.render(label, True, (255, 255, 255))
            self._rects[key] = pygame.Rect(title_x, item_y, surf.get_width(), surf.get_height())
            draw_gl_text(self._font, label, title_x, item_y)

        # Reset button — separated by one row gap from the toggles
        reset_y = 34 + len(toggles) * 22 + 10
        reset_label = "[ Reset rotation ]"
        surf = self._font.render(reset_label, True, (255, 255, 255))
        self._rects["reset"] = pygame.Rect(title_x, reset_y, surf.get_width(), surf.get_height())
        draw_gl_text(self._font, reset_label, title_x, reset_y)
