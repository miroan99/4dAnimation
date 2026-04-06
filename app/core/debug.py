import pygame
import OpenGL.GL as gl

from app.utils.text import draw_gl_text


class DebugOverlay:
    """Polls OpenGL errors each frame and optionally renders debug overlays."""

    def __init__(self):
        self._font = pygame.font.SysFont("consolas", 16)

    def draw(
        self,
        fps: float,
        cross_section_mode: bool = False,
        slice_w: float = 0.0,
    ) -> None:
        """Poll GL errors and, when cross-section mode is active, display slice_w.

        Args:
            fps:                Current frames per second (reserved for future use).
            cross_section_mode: Whether cross-section mode is currently active.
            slice_w:            Current W position of the slicing hyperplane.
        """
        self._poll_gl_errors()
        if cross_section_mode:
            from app import config
            draw_gl_text(
                self._font,
                f"slice_w: {slice_w:+.4f}",
                20,
                config.WINDOW_HEIGHT - 30,
            )

    def _poll_gl_errors(self) -> None:
        while True:
            err = gl.glGetError()
            if err == gl.GL_NO_ERROR:
                break
            print(f"[GL ERROR] 0x{err:04X}")
