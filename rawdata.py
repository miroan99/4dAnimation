import math
import sys

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
ROTATION_SPEED_DEG = 45.0

MODE_NAMES = [
    "None",
    "X",
    "Y",
    "Z",
    "XY",
    "XZ",
    "YZ",
    "XYZ",
]

MODE_AXES = {
    0: (),
    1: ("x",),
    2: ("y",),
    3: ("z",),
    4: ("x", "y"),
    5: ("x", "z"),
    6: ("y", "z"),
    7: ("x", "y", "z"),
}

FACE_COLORS = {
    "+x": (1.0, 0.0, 0.0),
    "-x": (0.55, 0.0, 0.0),
    "+y": (0.0, 1.0, 0.0),
    "-y": (0.0, 0.55, 0.0),
    "+z": (0.0, 0.0, 1.0),
    "-z": (0.0, 0.0, 0.55),
}


class AppState:
    """Holds mutable application state."""

    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.rotation_mode = 0
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.shift_depth = 0.0
        self.camera_distance = 4.0
        self.show_grid = True
        self.show_world_axes = True
        self.show_rotation_axes = True
        self.running = True
        self.font = None
        self.small_font = None
        self.menu_rects = {}


def normalize(v):
    """Returns a normalized 3D vector."""
    length = math.sqrt(sum(c * c for c in v))
    if length == 0:
        return (0.0, 0.0, 0.0)
    return tuple(c / length for c in v)


def init_pygame():
    """Initializes pygame and the OpenGL window."""
    pygame.init()
    pygame.display.set_caption("Rotating Unit Cube")
    pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        DOUBLEBUF | OPENGL | RESIZABLE,
    )


def init_fonts(state):
    """Initializes pygame fonts used for HUD and labels."""
    pygame.font.init()
    state.font = pygame.font.SysFont("consolas", 20, bold=False)
    state.small_font = pygame.font.SysFont("consolas", 16, bold=False)


def setup_opengl(state):
    """Configures the fixed-function OpenGL pipeline."""
    glViewport(0, 0, state.width, state.height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, state.width / max(1, state.height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glShadeModel(GL_SMOOTH)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    ambient = (0.18, 0.18, 0.18, 1.0)
    diffuse = (0.95, 0.95, 0.95, 1.0)
    specular = (1.0, 1.0, 1.0, 1.0)
    light_pos = (1.0, 2.0, 1.5, 0.0)

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

    mat_specular = (0.35, 0.35, 0.35, 1.0)
    mat_shininess = 24.0
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat_shininess)

    glClearColor(0.0, 0.0, 0.0, 1.0)


def reset_alignment(state):
    """Resets cube rotation so faces align with world axes and center stays at origin."""
    state.angle_x = 0.0
    state.angle_y = 0.0
    state.angle_z = 0.0


def resize(state, width, height):
    """Handles window resize and updates projection."""
    state.width = max(1, width)
    state.height = max(1, height)
    setup_opengl(state)


def update_rotation(state, dt):
    """Updates cube rotation angles according to the active rotation mode."""
    axes = MODE_AXES[state.rotation_mode]
    delta = ROTATION_SPEED_DEG * dt

    if "x" in axes:
        state.angle_x = (state.angle_x + delta) % 360.0
    if "y" in axes:
        state.angle_y = (state.angle_y + delta) % 360.0
    if "z" in axes:
        state.angle_z = (state.angle_z + delta) % 360.0


def set_camera(state):
    """Sets the camera from the (1,1,1) direction with Z as the vertical axis."""
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    dist = state.camera_distance + state.shift_depth
    eye = normalize((1.0, 1.0, 1.0))
    eye = tuple(c * dist for c in eye)

    gluLookAt(
        eye[0], eye[1], eye[2],
        0.0, 0.0, 0.0,
        0.0, 0.0, 1.0,
    )

    light_pos = (1.0, 2.0, 1.5, 0.0)
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)


def draw_grid():
    """Draws a grid in the XY plane below the cube."""
    glDisable(GL_LIGHTING)
    glColor3f(0.35, 0.35, 0.35)
    glLineWidth(1.0)

    z = -0.75
    extent = 3.0
    step = 0.5

    glBegin(GL_LINES)
    i = -extent
    while i <= extent + 1e-6:
        glVertex3f(i, -extent, z)
        glVertex3f(i, extent, z)

        glVertex3f(-extent, i, z)
        glVertex3f(extent, i, z)
        i += step
    glEnd()

    glEnable(GL_LIGHTING)


def draw_world_axes(state):
    """Draws fixed world axes with labels, extending into positive and negative directions."""
    if not state.show_world_axes:
        return

    glDisable(GL_LIGHTING)
    glLineWidth(2.5)

    axis_len = 2.4

    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-axis_len, 0.0, 0.0)
    glVertex3f(axis_len, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -axis_len, 0.0)
    glVertex3f(0.0, axis_len, 0.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -axis_len)
    glVertex3f(0.0, 0.0, axis_len)
    glEnd()

    glEnable(GL_LIGHTING)

    draw_3d_text(state, "X", (axis_len + 0.08, 0.0, 0.0))
    draw_3d_text(state, "-X", (-axis_len - 0.22, 0.0, 0.0))
    draw_3d_text(state, "Y", (0.0, axis_len + 0.08, 0.0))
    draw_3d_text(state, "-Y", (0.0, -axis_len - 0.22, 0.0))
    draw_3d_text(state, "Z", (0.0, 0.0, axis_len + 0.08))
    draw_3d_text(state, "-Z", (0.0, 0.0, -axis_len - 0.22))


def draw_rotation_axes(state):
    """Draws the currently active rotation axis indicators in cube-local space so they follow the cube."""
    if not state.show_rotation_axes:
        return

    active = MODE_AXES[state.rotation_mode]
    if not active:
        return

    glDisable(GL_LIGHTING)
    glLineWidth(4.0)
    glColor3f(1.0, 1.0, 0.0)

    axis_len = 1.2
    arrow = 0.08

    for axis in active:
        glBegin(GL_LINES)
        if axis == "x":
            glVertex3f(-axis_len, 0.0, 0.0)
            glVertex3f(axis_len, 0.0, 0.0)

            glVertex3f(axis_len, 0.0, 0.0)
            glVertex3f(axis_len - 0.12, arrow, 0.0)
            glVertex3f(axis_len, 0.0, 0.0)
            glVertex3f(axis_len - 0.12, -arrow, 0.0)

            glVertex3f(-axis_len, 0.0, 0.0)
            glVertex3f(-axis_len + 0.12, arrow, 0.0)
            glVertex3f(-axis_len, 0.0, 0.0)
            glVertex3f(-axis_len + 0.12, -arrow, 0.0)
        elif axis == "y":
            glVertex3f(0.0, -axis_len, 0.0)
            glVertex3f(0.0, axis_len, 0.0)

            glVertex3f(0.0, axis_len, 0.0)
            glVertex3f(arrow, axis_len - 0.12, 0.0)
            glVertex3f(0.0, axis_len, 0.0)
            glVertex3f(-arrow, axis_len - 0.12, 0.0)

            glVertex3f(0.0, -axis_len, 0.0)
            glVertex3f(arrow, -axis_len + 0.12, 0.0)
            glVertex3f(0.0, -axis_len, 0.0)
            glVertex3f(-arrow, -axis_len + 0.12, 0.0)
        elif axis == "z":
            glVertex3f(0.0, 0.0, -axis_len)
            glVertex3f(0.0, 0.0, axis_len)

            glVertex3f(0.0, 0.0, axis_len)
            glVertex3f(arrow, 0.0, axis_len - 0.12)
            glVertex3f(0.0, 0.0, axis_len)
            glVertex3f(-arrow, 0.0, axis_len - 0.12)

            glVertex3f(0.0, 0.0, -axis_len)
            glVertex3f(arrow, 0.0, -axis_len + 0.12)
            glVertex3f(0.0, 0.0, -axis_len)
            glVertex3f(-arrow, 0.0, -axis_len + 0.12)
        glEnd()

    glEnable(GL_LIGHTING)

    for axis in active:
        if axis == "x":
            draw_3d_text(state, "+X", (axis_len + 0.04, 0.0, 0.0))
            draw_3d_text(state, "-X", (-axis_len - 0.20, 0.0, 0.0))
        elif axis == "y":
            draw_3d_text(state, "+Y", (0.0, axis_len + 0.04, 0.0))
            draw_3d_text(state, "-Y", (0.0, -axis_len - 0.20, 0.0))
        elif axis == "z":
            draw_3d_text(state, "+Z", (0.0, 0.0, axis_len + 0.04))
            draw_3d_text(state, "-Z", (0.0, 0.0, -axis_len - 0.20))


def draw_cube():
    """Draws a unit cube centered at the origin with lit faces and white edges."""
    h = 0.5

    glBegin(GL_QUADS)

    glColor3f(*FACE_COLORS["+x"])
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(h, -h, -h)
    glVertex3f(h, h, -h)
    glVertex3f(h, h, h)
    glVertex3f(h, -h, h)

    glColor3f(*FACE_COLORS["-x"])
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-h, -h, -h)
    glVertex3f(-h, -h, h)
    glVertex3f(-h, h, h)
    glVertex3f(-h, h, -h)

    glColor3f(*FACE_COLORS["+y"])
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-h, h, -h)
    glVertex3f(-h, h, h)
    glVertex3f(h, h, h)
    glVertex3f(h, h, -h)

    glColor3f(*FACE_COLORS["-y"])
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-h, -h, -h)
    glVertex3f(h, -h, -h)
    glVertex3f(h, -h, h)
    glVertex3f(-h, -h, h)

    glColor3f(*FACE_COLORS["+z"])
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-h, -h, h)
    glVertex3f(h, -h, h)
    glVertex3f(h, h, h)
    glVertex3f(-h, h, h)

    glColor3f(*FACE_COLORS["-z"])
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-h, -h, -h)
    glVertex3f(-h, h, -h)
    glVertex3f(h, h, -h)
    glVertex3f(h, -h, -h)

    glEnd()

    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)

    edges = [
        ((-h, -h, -h), (h, -h, -h)),
        ((h, -h, -h), (h, h, -h)),
        ((h, h, -h), (-h, h, -h)),
        ((-h, h, -h), (-h, -h, -h)),
        ((-h, -h, h), (h, -h, h)),
        ((h, -h, h), (h, h, h)),
        ((h, h, h), (-h, h, h)),
        ((-h, h, h), (-h, -h, h)),
        ((-h, -h, -h), (-h, -h, h)),
        ((h, -h, -h), (h, -h, h)),
        ((h, h, -h), (h, h, h)),
        ((-h, h, -h), (-h, h, h)),
    ]

    glBegin(GL_LINES)
    for a, b in edges:
        glVertex3f(*a)
        glVertex3f(*b)
    glEnd()

    glEnable(GL_LIGHTING)


def draw_shadow():
    """No-op placeholder because projected cube shadows are intentionally disabled."""
    return


def render_scene(state):
    """Renders the 3D scene."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    set_camera(state)

    if state.show_grid:
        draw_grid()

    draw_world_axes(state)

    glPushMatrix()
    glRotatef(state.angle_x, 1.0, 0.0, 0.0)
    glRotatef(state.angle_y, 0.0, 1.0, 0.0)
    glRotatef(state.angle_z, 0.0, 0.0, 1.0)

    draw_rotation_axes(state)
    draw_cube()
    draw_shadow()

    glPopMatrix()


def make_text_surface(font, text, fg=(255, 255, 255), bg=(0, 0, 0)):
    """Creates a pygame surface for text."""
    return font.render(text, True, fg, bg).convert_alpha()


def draw_surface_2d(surface, x, y):
    """Draws a pygame surface at window pixel coordinates using glDrawPixels."""
    data = pygame.image.tostring(surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)


def draw_3d_text(state, text, position):
    """Draws small text anchored in 3D world space."""
    if state.small_font is None:
        return

    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)

    surf = make_text_surface(state.small_font, text, (255, 255, 255), (0, 0, 0))
    data = pygame.image.tostring(surf, "RGBA", True)

    glRasterPos3f(position[0], position[1], position[2])
    glDrawPixels(surf.get_width(), surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    glEnable(GL_LIGHTING)


def draw_overlay_panel(x, y, w, h, alpha=0.8):
    """Draws a simple black overlay panel in screen space."""
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor4f(0.0, 0.0, 0.0, alpha)
    glBegin(GL_QUADS)
    glVertex2f(x, WINDOW_HEIGHT - y)
    glVertex2f(x + w, WINDOW_HEIGHT - y)
    glVertex2f(x + w, WINDOW_HEIGHT - (y + h))
    glVertex2f(x, WINDOW_HEIGHT - (y + h))
    glEnd()

    glColor4f(1.0, 1.0, 1.0, 1.0)
    glLineWidth(1.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, WINDOW_HEIGHT - y)
    glVertex2f(x + w, WINDOW_HEIGHT - y)
    glVertex2f(x + w, WINDOW_HEIGHT - (y + h))
    glVertex2f(x, WINDOW_HEIGHT - (y + h))
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


def draw_hud(state):
    """Draws the HUD text and toggle menu."""
    mode_text = f"Rotating: {MODE_NAMES[state.rotation_mode]}"
    shift_text = f"Shift depth: {state.shift_depth:.2f}"

    left_panel_x = 10
    left_panel_y = 10
    left_panel_w = 260
    left_panel_h = 68

    draw_overlay_panel(left_panel_x, left_panel_y, left_panel_w, left_panel_h, alpha=0.85)

    text1 = make_text_surface(state.font, mode_text)
    text2 = make_text_surface(state.font, shift_text)
    draw_surface_2d(text1, left_panel_x + 10, state.height - (left_panel_y + 28))
    draw_surface_2d(text2, left_panel_x + 10, state.height - (left_panel_y + 56))

    menu_x = state.width - 220
    menu_y = 10
    menu_w = 210
    menu_h = 115

    draw_overlay_panel(menu_x, menu_y, menu_w, menu_h, alpha=0.85)

    title = make_text_surface(state.font, "Menu")
    draw_surface_2d(title, menu_x + 10, state.height - (menu_y + 28))

    options = [
        ("grid", f"[{'X' if state.show_grid else ' '}] Grid"),
        ("world_axes", f"[{'X' if state.show_world_axes else ' '}] Axis"),
        ("rotation_axes", f"[{'X' if state.show_rotation_axes else ' '}] Rotation axis"),
    ]

    state.menu_rects.clear()

    for i, (key, label) in enumerate(options):
        item_y = menu_y + 35 + i * 24
        state.menu_rects[key] = pygame.Rect(menu_x + 8, item_y - 2, menu_w - 16, 22)
        text = make_text_surface(state.small_font, label)
        draw_surface_2d(text, menu_x + 12, state.height - (item_y + 16))


def handle_menu_click(state, mouse_pos):
    """Handles clicks on the HUD toggle menu."""
    for key, rect in state.menu_rects.items():
        if rect.collidepoint(mouse_pos):
            if key == "grid":
                state.show_grid = not state.show_grid
            elif key == "world_axes":
                state.show_world_axes = not state.show_world_axes
            elif key == "rotation_axes":
                state.show_rotation_axes = not state.show_rotation_axes
            return True
    return False


def handle_input(state):
    """Processes pygame events and updates application state from input."""
    for event in pygame.event.get():
        if event.type == QUIT:
            state.running = False

        elif event.type == VIDEORESIZE:
            pygame.display.set_mode((event.w, event.h), DOUBLEBUF | OPENGL | RESIZABLE)
            resize(state, event.w, event.h)

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                state.running = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if handle_menu_click(state, mouse_pos):
                    continue

                mods = pygame.key.get_mods()
                if mods & KMOD_SHIFT:
                    state.shift_depth += 0.25
                    reset_alignment(state)
                else:
                    state.rotation_mode = (state.rotation_mode + 1) % 8

            elif event.button == 3:
                state.shift_depth = max(-2.5, state.shift_depth - 0.25)
                reset_alignment(state)

        elif event.type == MOUSEWHEEL:
            state.shift_depth = max(-2.5, min(4.0, state.shift_depth - event.y * 0.1))
            reset_alignment(state)

    state.shift_depth = max(-2.5, min(4.0, state.shift_depth))


def main():
    """Runs the application loop."""
    init_pygame()

    state = AppState()
    init_fonts(state)
    setup_opengl(state)

    clock = pygame.time.Clock()

    while state.running:
        dt = clock.tick(FPS) / 1000.0
        handle_input(state)
        update_rotation(state, dt)
        render_scene(state)
        draw_hud(state)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()