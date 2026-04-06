"""Tests for the W-hyperplane cross-section feature.

All tests use pure Python / NumPy only — no OpenGL context required.
"""

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _identity() -> np.ndarray:
    return np.eye(4, dtype=np.float32)


# ---------------------------------------------------------------------------
# compute_cross_section
# ---------------------------------------------------------------------------

class TestComputeCrossSection:
    """Tests for the module-level pure-math helper."""

    def test_empty_when_slice_w_above_object(self):
        """slice_w > all vertex W coords → no intersections."""
        from app.render.hyperobject import compute_cross_section
        from app.render.tesseract import _VERTICES, _EDGES

        result = compute_cross_section(_VERTICES, _EDGES, _identity(), slice_w=2.0)
        assert result == []

    def test_empty_when_slice_w_below_object(self):
        """slice_w < all vertex W coords → no intersections."""
        from app.render.hyperobject import compute_cross_section
        from app.render.tesseract import _VERTICES, _EDGES

        result = compute_cross_section(_VERTICES, _EDGES, _identity(), slice_w=-2.0)
        assert result == []

    def test_slice_at_w_zero_unit_tesseract(self):
        """Identity rotation, slice at w=0 → exactly 8 intersection points.

        Tesseract vertices lie at w = ±0.5.  The 8 edges crossing w=0 are
        those that differ only in the W bit (XOR = 8 = 2³), producing one
        interpolated 3-D point each.
        """
        from app.render.hyperobject import compute_cross_section
        from app.render.tesseract import _VERTICES, _EDGES

        result = compute_cross_section(_VERTICES, _EDGES, _identity(), slice_w=0.0)
        assert len(result) == 8

    def test_intersection_points_are_float32_arrays(self):
        """Returned points must be (3,) float32 numpy arrays."""
        from app.render.hyperobject import compute_cross_section
        from app.render.tesseract import _VERTICES, _EDGES

        result = compute_cross_section(_VERTICES, _EDGES, _identity(), slice_w=0.0)
        for pt in result:
            assert isinstance(pt, np.ndarray)
            assert pt.shape == (3,)
            assert pt.dtype == np.float32

    def test_interpolated_point_lies_on_hyperplane(self):
        """Each returned 3-D point must originate from w = slice_w in 4-D space.

        Verify by reconstructing the W coordinate from the interpolation
        parameter stored implicitly: for a crossing edge (i, j) with
        slice_w in (w_i, w_j), the interpolated 3-D point's z values must
        equal z_i + t*(z_j - z_i) where t = (slice_w - w_i)/(w_j - w_i).
        """
        from app.render.hyperobject import compute_cross_section
        from app.render.tesseract import _VERTICES, _EDGES

        slice_w = 0.3
        rotated = _VERTICES @ _identity().T
        expected: list[np.ndarray] = []
        for i, j in _EDGES:
            wi, wj = float(rotated[i, 3]), float(rotated[j, 3])
            di, dj = wi - slice_w, wj - slice_w
            if di * dj < 0.0:
                t = di / (di - dj)
                expected.append((rotated[i, :3] + t * (rotated[j, :3] - rotated[i, :3])).astype(np.float32))

        result = compute_cross_section(_VERTICES, _EDGES, _identity(), slice_w=slice_w)
        assert len(result) == len(expected)
        for pt, exp in zip(result, expected):
            np.testing.assert_allclose(pt, exp, atol=1e-6)


# ---------------------------------------------------------------------------
# CrossSectionState / update_cross_section
# ---------------------------------------------------------------------------

class TestCrossSectionAnimation:
    """Tests for the direction-reversal and bounds-clamping logic."""

    def test_direction_reverses_at_upper_bound(self):
        """slice_w pushed above +1.0 → clamped to 1.0, direction becomes -1."""
        from app.core.rotation4d import Rotation4D

        r = Rotation4D()
        r.cross_section.slice_w = 0.95
        r.cross_section.direction = 1
        r.cross_section.speed = 0.5
        r.update_cross_section(dt=0.2)  # 0.95 + 0.5*1*0.2 = 1.05 → clamp

        assert r.cross_section.direction == -1
        assert r.cross_section.slice_w == pytest.approx(1.0)

    def test_direction_reverses_at_lower_bound(self):
        """slice_w pushed below -1.0 → clamped to -1.0, direction becomes +1."""
        from app.core.rotation4d import Rotation4D

        r = Rotation4D()
        r.cross_section.slice_w = -0.95
        r.cross_section.direction = -1
        r.cross_section.speed = 0.5
        r.update_cross_section(dt=0.2)  # -0.95 - 0.1 = -1.05 → clamp

        assert r.cross_section.direction == 1
        assert r.cross_section.slice_w == pytest.approx(-1.0)

    def test_normal_advance_does_not_reverse(self):
        """Small dt with direction +1 → slice_w increases, direction unchanged."""
        from app.core.rotation4d import Rotation4D

        r = Rotation4D()
        r.cross_section.slice_w = 0.0
        r.cross_section.direction = 1
        r.cross_section.speed = 0.5
        r.update_cross_section(dt=0.1)

        assert r.cross_section.direction == 1
        assert r.cross_section.slice_w == pytest.approx(0.05)

    def test_cross_section_state_defaults(self):
        """CrossSectionState initialises with sensible defaults."""
        from app.core.rotation4d import CrossSectionState

        cs = CrossSectionState()
        assert cs.slice_w == 0.0
        assert cs.speed > 0.0
        assert cs.direction in (1, -1)


# ---------------------------------------------------------------------------
# _slice_w_color gradient
# ---------------------------------------------------------------------------

class TestSliceWColor:
    def test_color_at_minus_one_is_blue(self):
        from app.render.hyperobject import _slice_w_color
        c = _slice_w_color(-1.0)
        np.testing.assert_allclose(c, [0.0, 0.4, 1.0], atol=1e-6)

    def test_color_at_zero_is_white(self):
        from app.render.hyperobject import _slice_w_color
        c = _slice_w_color(0.0)
        np.testing.assert_allclose(c, [1.0, 1.0, 1.0], atol=1e-6)

    def test_color_at_plus_one_is_red(self):
        from app.render.hyperobject import _slice_w_color
        c = _slice_w_color(1.0)
        np.testing.assert_allclose(c, [1.0, 0.2, 0.0], atol=1e-6)

    def test_color_is_float32(self):
        from app.render.hyperobject import _slice_w_color
        c = _slice_w_color(0.5)
        assert c.dtype == np.float32
