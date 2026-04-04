import OpenGL.GL as gl

from app import config
from pathlib import Path


class Shader:
    def __init__(self, vert_name: str, frag_name: str):
        shader_dir = Path(config.SHADER_DIR)
        vert_src = (shader_dir / vert_name).read_text()
        frag_src = (shader_dir / frag_name).read_text()
        self.program = self._link(
            self._compile(vert_src, gl.GL_VERTEX_SHADER),
            self._compile(frag_src, gl.GL_FRAGMENT_SHADER),
        )

    def _compile(self, source: str, shader_type: int) -> int:
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, source)
        gl.glCompileShader(shader)
        if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
            log = gl.glGetShaderInfoLog(shader).decode()
            gl.glDeleteShader(shader)
            raise RuntimeError(f"Shader compile error:\n{log}")
        return shader

    def _link(self, vert: int, frag: int) -> int:
        program = gl.glCreateProgram()
        gl.glAttachShader(program, vert)
        gl.glAttachShader(program, frag)
        gl.glLinkProgram(program)
        gl.glDeleteShader(vert)
        gl.glDeleteShader(frag)
        if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
            log = gl.glGetProgramInfoLog(program).decode()
            raise RuntimeError(f"Shader link error:\n{log}")
        return program

    def use(self):
        gl.glUseProgram(self.program)

    def set_mat4(self, name: str, matrix):
        loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniformMatrix4fv(loc, 1, gl.GL_TRUE, matrix)

    def set_vec3(self, name: str, value):
        loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform3fv(loc, 1, value)

    def set_float(self, name: str, value: float):
        loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1f(loc, value)

    def __del__(self):
        try:
            gl.glDeleteProgram(self.program)
        except Exception:
            pass
