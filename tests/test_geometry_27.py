"""``domains/industrial/geometry``: what the drawings read off a record (#27).

The module turns a record's published attributes into measurements, or refuses.
It draws nothing, so these checks are on numbers. They carry over the
geometry-only checks of the retired text renderer's tests: the refusals, the
dome's arc, the corner radius and the palette's ink separation.
"""

from __future__ import annotations

import itertools

import pytest

from synthetic_ecommerce_data.core.brands import BRAND_BOOK, INKS
from synthetic_ecommerce_data.domains.industrial.geometry import drill, endmill, fastener
from synthetic_ecommerce_data.domains.industrial.geometry.attrs import (
    REFUSALS,
    ImpossibleGeometryError,
    MissingAttributeError,
    UnsupportedFeatureError,
)
from synthetic_ecommerce_data.domains.industrial.geometry.palette import (
    BRAND_INK,
    MIN_INK_SEPARATION,
)
from synthetic_ecommerce_data.domains.industrial.records import FIXTURES

MILL = {**FIXTURES["4LU10"], "End Mill Style": "Square"}
SCREW = FIXTURES["26LD37"]


def test_an_end_mill_is_read_off_its_record():
    geometry = endmill.geometry_from_record(MILL)
    assert geometry.cut_d.inches == pytest.approx(0.25)
    assert geometry.oal.inches == pytest.approx(3 + 3 / 8)
    assert geometry.flutes == 4
    assert geometry.corner_radius is None


def test_a_metric_end_mill_is_read_in_inches():
    geometry = endmill.geometry_from_record({**FIXTURES["35AM34"], "End Mill Style": "Square"})
    assert geometry.oal.inches == pytest.approx(57 / 25.4)


def test_a_published_corner_radius_is_read():
    geometry = endmill.geometry_from_record({**MILL, "Corner Radius": '1/32"'})
    assert geometry.corner_radius.inches == pytest.approx(1 / 32)


def test_a_corner_radius_wider_than_the_cutter_is_refused():
    with pytest.raises(ImpossibleGeometryError, match="does not fit"):
        endmill.geometry_from_record({**MILL, "Corner Radius": '1/2"'})


def test_a_ball_nose_has_no_corner_radius():
    record = {**MILL, "End Mill Style": "Ball", "Corner Radius": '1/32"'}
    with pytest.raises(ImpossibleGeometryError, match="ball nose has no corners"):
        endmill.geometry_from_record(record)


def test_a_length_of_cut_that_leaves_no_shank_is_refused():
    with pytest.raises(ImpossibleGeometryError, match="no shank"):
        endmill.geometry_from_record({**MILL, "Length of Cut": '3-3/8"'})


def test_a_missing_dimension_is_refused_by_name():
    record = {k: v for k, v in MILL.items() if k != "Shank Dia."}
    with pytest.raises(MissingAttributeError, match="Shank Dia."):
        endmill.geometry_from_record(record)


def test_a_value_that_does_not_parse_is_a_refusal_too():
    with pytest.raises(REFUSALS):
        endmill.geometry_from_record({**MILL, "Overall Length": "long"})


def test_a_cutting_direction_that_is_neither_hand_is_refused():
    with pytest.raises(UnsupportedFeatureError):
        endmill.geometry_from_record({**MILL, "Cutting Direction": "Sideways"})


def test_every_refusal_is_one_of_the_listed_ones():
    raised = []
    for record in (
        {**MILL, "Length of Cut": '3-3/8"'},
        {k: v for k, v in MILL.items() if k != "Shank Dia."},
        {**MILL, "Cutting Direction": "Sideways"},
        {**MILL, "Overall Length": "long"},
    ):
        with pytest.raises(REFUSALS) as caught:
            endmill.geometry_from_record(record)
        raised.append(type(caught.value))
    assert len(set(raised)) == len(REFUSALS)


DRILL = {
    "sku": "D1",
    "Size": '1/4"',
    "Shank Dia.": '1/4"',
    "Flute Length": '2"',
    "Overall Length": '4"',
    "Point Angle": "118 Degrees",
}


def test_a_drill_is_read_off_its_record():
    geometry = drill.geometry_from_record(DRILL)
    assert geometry.oal.inches == pytest.approx(4)
    assert geometry.point_deg == pytest.approx(118)


def test_a_flute_as_long_as_the_drill_is_refused():
    with pytest.raises(ImpossibleGeometryError, match="no shank"):
        drill.geometry_from_record({**DRILL, "Flute Length": '4"'})


def test_a_flat_head_screw_is_read_and_is_countersunk():
    geometry = fastener.geometry_from_record(SCREW)
    assert geometry.countersunk
    assert not geometry.domed
    assert geometry.length.inches == pytest.approx(0.5)
    assert geometry.head_dia.inches == pytest.approx(0.411)
    assert geometry.head_height.inches == pytest.approx(0.127)


def test_a_head_style_no_attribute_determines_is_refused():
    record = {**SCREW, "Screw Head Type": "Mushroom", "Head Type": "Mushroom"}
    with pytest.raises(fastener.UnsupportedHeadError):
        fastener.geometry_from_record(record)


@pytest.mark.parametrize("rise", [0.05, 0.127, 0.3, 0.9])
def test_the_dome_stands_on_the_rim_and_reaches_the_crown(rise):
    """Its ends are the head's rim and its top is the crown, a tall dome included.

    A rise taller than the head's radius is the case where taking the rim angle
    with ``asin`` draws the minor arc, whose ends are not on the rim.
    """
    r_head, seat = 0.25, 0.1
    points = fastener.dome_profile(r_head, rise, seat)
    (x0, y0), (x1, y1) = points[0], points[-1]
    assert (abs(x0), abs(x1)) == (pytest.approx(r_head), pytest.approx(r_head))
    assert (y0, y1) == (pytest.approx(seat), pytest.approx(seat))
    assert max(y for _, y in points) == pytest.approx(seat + rise)


def _separation(color: str, other: str) -> float:
    """Closest a stroke in ``color`` fades, towards white, to ``other``."""

    def rgb(value: str) -> tuple[float, ...]:
        return tuple(int(value[i : i + 2], 16) / 255 for i in (1, 3, 5))

    start, target = rgb(color), rgb(other)
    steps = 200
    return min(
        max(abs(s + (1 - s) * k / steps - t) for s, t in zip(start, target, strict=True))
        for k in range(steps + 1)
    )


def test_no_brand_ink_fades_through_another_brands_ink():
    worst = min((_separation(a, b), a, b) for a, b in itertools.permutations(INKS, 2))
    assert worst[0] >= MIN_INK_SEPARATION, f"{worst[1]} fades through {worst[2]} ({worst[0]:.3f})"


def test_the_separation_measure_sees_a_fade():
    assert _separation("#000000", "#7f7f7f") == pytest.approx(0, abs=0.01)
    assert _separation("#000000", "#ffffff") == pytest.approx(0)
    assert _separation("#ff0000", "#00ffff") == pytest.approx(1)


def test_every_brands_ink_is_its_brand_book_ink():
    for book in BRAND_BOOK:
        assert BRAND_INK[book.name] == INKS[book.ink]
