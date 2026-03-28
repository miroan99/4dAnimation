import OpenGL.GL as gl


def check_gl_error(label: str = ""):
    err = gl.glGetError()
    if err != gl.GL_NO_ERROR:
        tag = f"[{label}] " if label else ""
        print(f"{tag}GL Error: 0x{err:04X}")
        return False
    return True


def log_gl_info():
    vendor = gl.glGetString(gl.GL_VENDOR).decode()
    renderer = gl.glGetString(gl.GL_RENDERER).decode()
    version = gl.glGetString(gl.GL_VERSION).decode()
    glsl = gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION).decode()
    print(f"[GL] Vendor:   {vendor}")
    print(f"[GL] Renderer: {renderer}")
    print(f"[GL] Version:  {version}")
    print(f"[GL] GLSL:     {glsl}")
