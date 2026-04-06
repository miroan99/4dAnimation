import pygame

from app.utils.text import draw_gl_text


class Menu:
    def __init__(self):
        self._font = pygame.font.SysFont("consolas", 16)
        self._rects: dict[str, pygame.Rect] = {}

    def handle_click(self, mouse_pos, engine) -> bool:
        """Check if the click hit a menu item and act accordingly. Returns True if consumed."""
        for key, rect in self._rects.items():
            if rect.collidepoint(mouse_pos):
                if key == "grid":
                    engine.show_grid = not engine.show_grid
                elif key == "world_axes":
                    engine.show_world_axes = not engine.show_world_axes
                elif key == "rotation_axes":
                    engine.show_rotation_axes = not engine.show_rotation_axes
                elif key == "cube_faces":
                    engine.show_cube_faces = not engine.show_cube_faces
                elif key.startswith("body_"):
                    engine.selected_body = key[5:]   # strip "body_" prefix
                elif key.startswith("mode3d_"):
                    engine.rotation_mode = int(key[7:])
                elif key.startswith("mode4d_"):
                    engine.rotation4d.mode = int(key[7:])
                elif key == "reset":
                    engine.reset_rotation()
                return True
        return False

    def draw(
        self,
        show_grid: bool,
        show_world_axes: bool,
        show_rotation_axes: bool,
        selected_body: str = "cube",
        show_cube_faces: bool = True,
        cross_section_mode: bool = False,
        slice_w: float = 0.0,
        rotation_mode: int = 0,
        rotation4d_mode: int = 4,
    ):
        from app import config
        self._rects.clear()

        title_x = config.WINDOW_WIDTH - 210
        draw_gl_text(self._font, "Menu", title_x, 12)

        y = 34
        step = 20  # compact vertical spacing for radio lists

        # ----------------------------------------------------------------
        # Body radio buttons
        # ----------------------------------------------------------------
        draw_gl_text(self._font, "Body:", title_x, y)
        y += step + 2

        bodies = [
            ("body_cube",        "cube",        "3D Cube"),
            ("body_tesseract",   "tesseract",   "4D Tesseract"),
            ("body_hypersphere", "hypersphere", "4D Hypersphere"),
        ]
        for key, value, label in bodies:
            marker = "(*)" if selected_body == value else "( )"
            text = f"{marker} {label}"
            surf = self._font.render(text, True, (255, 255, 255))
            self._rects[key] = pygame.Rect(title_x, y, surf.get_width(), surf.get_height())
            draw_gl_text(self._font, text, title_x, y)
            y += step

        y += 8  # separator gap

        # ----------------------------------------------------------------
        # Movement radio buttons — 3D rotation axes (always shown)
        # ----------------------------------------------------------------
        draw_gl_text(self._font, "Movement:", title_x, y)
        y += step + 2

        for i, name in enumerate(config.MODE_NAMES):
            marker = "(*)" if rotation_mode == i else "( )"
            text = f"{marker} {name}"
            surf = self._font.render(text, True, (255, 255, 255))
            self._rects[f"mode3d_{i}"] = pygame.Rect(
                title_x, y, surf.get_width(), surf.get_height()
            )
            draw_gl_text(self._font, text, title_x, y)
            y += step

        # ----------------------------------------------------------------
        # Mode radio buttons — 4D modes (only for hyper-objects)
        # ----------------------------------------------------------------
        if selected_body != "cube":
            y += 8
            draw_gl_text(self._font, "Mode:", title_x, y)
            y += step + 2

            for i, name in enumerate(config.ROTATION4D_MODE_NAMES):
                is_selected = rotation4d_mode == i
                is_cs_entry = i == config.CROSS_SECTION_MODE
                marker = "(*)" if is_selected else "( )"
                text = f"{marker} {name}"
                color = (255, 220, 80) if is_cs_entry else (255, 255, 255)
                surf = self._font.render(text, True, color)
                self._rects[f"mode4d_{i}"] = pygame.Rect(
                    title_x, y, surf.get_width(), surf.get_height()
                )
                draw_gl_text(self._font, text, title_x, y, fg=color)
                y += step

            # Show live W position when cross-section mode is active
            if cross_section_mode:
                draw_gl_text(
                    self._font,
                    f"  W: {slice_w:+.3f}",
                    title_x, y,
                    fg=(255, 220, 80),
                )
                y += step

        y += 8  # separator gap

        # ----------------------------------------------------------------
        # Checkboxes
        # ----------------------------------------------------------------
        checkboxes = [
            ("cube_faces",    f"[{'X' if show_cube_faces else ' '}] Cube faces"),
            ("grid",          f"[{'X' if show_grid else ' '}] Grid"),
            ("world_axes",    f"[{'X' if show_world_axes else ' '}] Axis"),
            ("rotation_axes", f"[{'X' if show_rotation_axes else ' '}] Rotation axis"),
        ]
        for key, label in checkboxes:
            surf = self._font.render(label, True, (255, 255, 255))
            self._rects[key] = pygame.Rect(title_x, y, surf.get_width(), surf.get_height())
            draw_gl_text(self._font, label, title_x, y)
            y += step + 2

        # ----------------------------------------------------------------
        # Reset button
        # ----------------------------------------------------------------
        y += 8
        reset_label = "[ Reset rotation ]"
        surf = self._font.render(reset_label, True, (255, 255, 255))
        self._rects["reset"] = pygame.Rect(title_x, y, surf.get_width(), surf.get_height())
        draw_gl_text(self._font, reset_label, title_x, y)
