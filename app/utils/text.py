import pygame
import numpy as np
import OpenGL.GL as gl
from pathlib import Path


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


# --- module-level lazy-initialized GL resources for draw_gl_text ---
_program = None
_vao = None
_vbo = None


def _ensure_initialized():
    global _program, _vao, _vbo
    if _program is not None:
        return

    from app import config
    shader_dir = Path(config.SHADER_DIR)
    vert_src = (shader_dir / "text.vert").read_text()
    frag_src = (shader_dir / "text.frag").read_text()

    def _compile(src, kind):
        s = gl.glCreateShader(kind)
        gl.glShaderSource(s, src)
        gl.glCompileShader(s)
        if not gl.glGetShaderiv(s, gl.GL_COMPILE_STATUS):
            raise RuntimeError(gl.glGetShaderInfoLog(s).decode())
        return s

    vert = _compile(vert_src, gl.GL_VERTEX_SHADER)
    frag = _compile(frag_src, gl.GL_FRAGMENT_SHADER)
    _program = gl.glCreateProgram()
    gl.glAttachShader(_program, vert)
    gl.glAttachShader(_program, frag)
    gl.glLinkProgram(_program)
    gl.glDeleteShader(vert)
    gl.glDeleteShader(frag)
    if not gl.glGetProgramiv(_program, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(_program).decode())

    _vao = gl.glGenVertexArrays(1)
    _vbo = gl.glGenBuffers(1)
    gl.glBindVertexArray(_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, _vbo)
    # 6 vertices × (2 pos + 2 uv) × 4 bytes; dynamic so we can update each call
    gl.glBufferData(gl.GL_ARRAY_BUFFER, 6 * 4 * 4, None, gl.GL_DYNAMIC_DRAW)
    stride = 4 * 4  # 4 floats
    gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, gl.ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, gl.ctypes.c_void_p(8))
    gl.glEnableVertexAttribArray(1)
    gl.glBindVertexArray(0)


def draw_gl_text(font: pygame.font.Font, text: str, x: int, y: int,
                 fg=(255, 255, 255), bg=None):
    """Draw text at window pixel (x, y) from top-left using a texture quad."""
    from app import config
    _ensure_initialized()

    surf = font.render(text, True, fg)
    w, h = surf.get_size()
    tex_data = pygame.image.tostring(surf, "RGBA", False)

    tex = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0,
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, tex_data)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    # Convert pixel coords (top-left origin) → NDC
    W, H = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
    x0 = 2 * x / W - 1
    x1 = 2 * (x + w) / W - 1
    y0 = 1 - 2 * y / H        # top edge in NDC
    y1 = 1 - 2 * (y + h) / H  # bottom edge in NDC

    verts = np.array([
        x0, y0, 0.0, 0.0,
        x1, y0, 1.0, 0.0,
        x1, y1, 1.0, 1.0,
        x0, y0, 0.0, 0.0,
        x1, y1, 1.0, 1.0,
        x0, y1, 0.0, 1.0,
    ], dtype=np.float32)

    prev_prog = gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM)
    prev_depth = gl.glIsEnabled(gl.GL_DEPTH_TEST)

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    gl.glUseProgram(_program)
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    loc = gl.glGetUniformLocation(_program, "uTexture")
    gl.glUniform1i(loc, 0)

    gl.glBindVertexArray(_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, _vbo)
    gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
    gl.glBindVertexArray(0)

    gl.glDeleteTextures([tex])
    gl.glUseProgram(prev_prog)
    if prev_depth:
        gl.glEnable(gl.GL_DEPTH_TEST)
