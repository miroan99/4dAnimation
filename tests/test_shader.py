import pytest
from pathlib import Path


SHADER_DIR = Path("shaders")


def _read(name: str) -> str:
    return (SHADER_DIR / name).read_text()


def test_default_vert_exists():
    assert (SHADER_DIR / "default.vert").exists()


def test_default_frag_exists():
    assert (SHADER_DIR / "default.frag").exists()


def test_unlit_vert_exists():
    assert (SHADER_DIR / "unlit.vert").exists()


def test_unlit_frag_exists():
    assert (SHADER_DIR / "unlit.frag").exists()


def test_default_vert_has_version():
    src = _read("default.vert")
    assert src.startswith("#version")


def test_default_frag_has_version():
    src = _read("default.frag")
    assert src.startswith("#version")
