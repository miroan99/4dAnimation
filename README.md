# 4d-animation-python

A Python + OpenGL 4D animation project template using Pygame and PyOpenGL.

## Structure

```
app/
  core/
    camera.py       Orbital (arcball) camera
    debug.py        Debug overlay
    engine.py       Main engine loop
    input.py        Input handling
    rotation4d.py   4D rotation math
  render/
    axes.py         Axes renderer
    cube.py         3D cube mesh
    grid.py         Grid renderer
    hyperobject.py  4D hyperobject base
    lighting.py     Lighting setup
    mesh.py         Generic mesh
    renderer.py     Main renderer
    shader.py       Shader management
    tesseract.py    4D tesseract projection
  scene/
    object3d.py     3D scene object base class
    scene.py        Scene graph
  ui/
    hud.py          HUD overlay
    menu.py         In-app menu
  utils/
    gl_utils.py     OpenGL helpers
    math3d.py       3D math utilities
    math4d.py       4D math utilities
    text.py         Text rendering
  config.py         App configuration
  main.py           Entry point
shaders/
  default.vert/frag Phong-lit shader
  text.vert/frag    Text shader
  unlit.vert/frag   Unlit shader
assets/
  fonts/            Font files
  textures/         Texture files
tests/
  test_math3d.py    3D math tests
  test_mesh.py      Mesh tests
  test_shader.py    Shader tests
scripts/
  setup.ps1         Environment setup
  run.ps1           Run the app
rawdata.py          Raw data / scratch file
pyproject.toml      Project metadata
requirements.txt    Python dependencies
```

## Requirements

- Python 3.11+
- See `requirements.txt`

## Setup

```powershell
.\scripts\setup.ps1
```

## Run

```powershell
.\scripts\run.ps1
```

Or directly:

```bash
python -m app.main
```

## Controls

| Key / Button | Action |
|---|---|
| Left drag | Orbit camera around the object |
| Scroll wheel | Zoom in / out |
| Left click (menu) | Select body, movement axis, or 4D mode |
| Escape | Quit |

## Tests

```bash
pytest
```

## Menu

The right-side menu has three groups of radio buttons:

- **Body** — switch between 3D Cube, 4D Tesseract, and 4D Hypersphere.
- **Movement** — select which 3D rotation axes animate (None, X, Y, Z, XY, XZ, YZ, XYZ). Always visible.
- **Mode** — select the 4D rendering mode (visible only when a hyper-object is selected).

Checkboxes toggle the grid, world axes, rotation axes, and cube faces. A **Reset rotation** button resets the current object to its default orientation.

## Enhancements

### Cross-Section Mode (4D objects)

When a 4D object (Tesseract or Hypersphere) is selected, the **Mode**
panel includes **Cross-Section** mode (highlighted in yellow).

Instead of projecting the full 4D geometry into 3D, a hyperplane at
`w = slice_w` slices through the object.  Only geometry that intersects
the hyperplane is rendered.  `slice_w` animates automatically between
`-1.0` and `+1.0`, so the 3D cross-section of the 4D shape evolves
continuously:

- **Tesseract** — a cube appears, expands, contracts, and disappears,
  then repeats.
- **Hypersphere** — great circles flash in and out as the hyperplane
  sweeps through.

Intersection points are coloured by W-depth:

| W position | Colour |
|---|---|
| -1.0 | Blue `(0.0, 0.4, 1.0)` |
|  0.0 | White `(1.0, 1.0, 1.0)` |
| +1.0 | Red `(1.0, 0.2, 0.0)` |

The current `slice_w` value is shown in the **HUD** (top-left) and in
the **Menu** panel (top-right) whenever cross-section mode is active.
