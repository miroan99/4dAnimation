# template-3d-animation-python

A Python + OpenGL 3D animation project template using Pygame and PyOpenGL.

## Structure

```
app/
  core/       Engine, camera, input, debug overlay
  render/     Shader, Mesh, Cube, Axes, Grid, Lighting
  scene/      Scene graph, Object3D base class
  ui/         HUD, Menu
  utils/      math3d, text, gl_utils
shaders/      GLSL vertex + fragment shaders
assets/       Fonts, textures
tests/        Pytest unit tests
scripts/      PowerShell helpers
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
| W / A / S / D | Move camera |
| Right mouse drag | Look around |
| Escape | Quit |

## Tests

```bash
pytest
```
## Project structur

