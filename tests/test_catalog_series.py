"""Tool geometry has to be coherent by construction, not by luck.

The reference statistics are explicit that the four cutting-tool dimensions
cannot be sampled independently -- doing so produces tools that could not be
manufactured. These tests pin the constructor's guarantee: whatever diameter
and length class you ask for, the tuple that comes back describes a tool that
could exist.
"""

from __future__ import annotations

import math
from fractions import Fraction

import pytest

from synthetic_ecommerce_data.core.dimensions import MM_PER_INCH
from synthetic_ecommerce_data.domains.industrial.series import (
    FLUTE_WEIGHTS,
    HELIX_ANGLES,
    IMPERIAL_CUTTING_DIAS,
    IMPERIAL_SHANKS,
    LENGTH_CLASSES,
    METRIC_CUTTING_DIAS,
    METRIC_SHANKS,
    GeometryError,
    ToolGeometry,
    build_imperial,
    build_metric,
    nearest_shank_imperial,
    nearest_shank_metric,
    snap_imperial,
)


@pytest.mark.parametrize("dia", IMPERIAL_CUTTING_DIAS)
@pytest.mark.parametrize("length_class,multiple", LENGTH_CLASSES)
def test_every_imperial_tool_has_a_shank_to_hold(dia: Fraction, length_class: str, multiple: float):
    shank = nearest_shank_imperial(float(dia))
    geom = build_imperial(dia, length_class, multiple, shank)
    assert geom.length_of_cut_in < geom.overall_length_in
    assert geom.cutting_dia_in > 0 and geom.shank_dia_in > 0


@pytest.mark.parametrize("dia_mm", METRIC_CUTTING_DIAS)
@pytest.mark.parametrize("length_class,multiple", LENGTH_CLASSES)
def test_every_metric_tool_has_a_shank_to_hold(dia_mm: float, length_class: str, multiple: float):
    shank = nearest_shank_metric(dia_mm)
    geom = build_metric(dia_mm, length_class, multiple, shank)
    assert geom.length_of_cut_in < geom.overall_length_in


def test_a_tool_whose_cut_runs_past_its_end_is_refused():
    with pytest.raises(GeometryError):
        ToolGeometry(
            system="in",
            cutting_dia_in=0.5,
            length_of_cut_in=3.0,
            overall_length_in=2.5,
            shank_dia_in=0.5,
            length_class="Long",
        )


def test_a_tool_with_no_diameter_is_refused():
    with pytest.raises(GeometryError):
        ToolGeometry(
            system="in",
            cutting_dia_in=0.0,
            length_of_cut_in=1.0,
            overall_length_in=3.0,
            shank_dia_in=0.5,
            length_class="Regular",
        )


def test_the_length_class_drives_the_length_of_cut():
    """A long tool cuts further than a stub tool of the same diameter."""
    dia = Fraction(1, 2)
    shank = Fraction(1, 2)
    stub = build_imperial(dia, "Stub", 1.5, shank)
    regular = build_imperial(dia, "Regular", 3.0, shank)
    long_ = build_imperial(dia, "Long", 4.0, shank)
    assert stub.length_of_cut_in < regular.length_of_cut_in < long_.length_of_cut_in
    assert stub.overall_length_in <= regular.overall_length_in <= long_.overall_length_in


def test_shank_equality_is_detected():
    dia = Fraction(3, 8)
    same = build_imperial(dia, "Regular", 3.0, Fraction(3, 8))
    different = build_imperial(dia, "Regular", 3.0, Fraction(1, 2))
    assert same.shank_equals_cutting
    assert not different.shank_equals_cutting


def test_snapping_lands_on_the_printable_grid():
    assert snap_imperial(0.51, 16) == Fraction(1, 2)
    assert snap_imperial(0.78, 16) == Fraction(3, 4)
    assert snap_imperial(0.78, 32) == Fraction(25, 32)
    # Everything the snapper emits has an exact fractional spelling.
    for raw in (0.13, 0.49, 1.01, 2.77):
        value = snap_imperial(raw, 16)
        assert value.denominator <= 16


def test_the_offered_shank_series_are_the_ones_the_brief_names():
    imperial = {float(s) for s in IMPERIAL_SHANKS}
    assert imperial == {0.125, 0.1875, 0.25, 0.3125, 0.375, 0.5, 0.625, 0.75, 1.0}
    assert set(METRIC_SHANKS) == {3, 3.175, 4, 6, 6.35, 8, 10, 12, 12.7, 16, 20, 25}


def test_the_inch_shanks_in_the_metric_series_really_are_inch_sizes():
    """3.175, 6.35 and 12.7 mm are 1/8", 1/4" and 1/2" -- the unit-mixing seed."""
    for mm, inches in ((3.175, 0.125), (6.35, 0.25), (12.7, 0.5)):
        assert mm in METRIC_SHANKS
        assert math.isclose(mm / MM_PER_INCH, inches, abs_tol=1e-9)


def test_flute_weights_match_the_measured_marginal():
    counts = dict(FLUTE_WEIGHTS)
    assert set(counts) == {2, 3, 4, 6}
    # 4 flutes is the most common in the corpus (55 of 131), 2 next (49).
    assert counts[4] > counts[2] > counts[6] > counts[3]
    assert math.isclose(sum(counts.values()), 1.0, abs_tol=1e-9)


def test_helix_angles_are_the_conventional_series():
    assert set(HELIX_ANGLES) == {30.0, 35.0, 38.0, 45.0}
