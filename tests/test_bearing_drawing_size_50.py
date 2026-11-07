"""No ball bearing any brand could offer draws past the drawing size cap (slice 4 of #50).

``tests/test_sku_drawings.py`` holds the drawings of one seed's catalog to ``MAX_DRAWING_BYTES``,
and a type whose figure could approach the cap holds its own worst case to it too. On seed
20260918 the largest drawing was a 6007 bearing at 8588 bytes: a bearing drawn small gets the
magnifier, so its open face's balls are painted twice, and each ball was a styled ``<circle>``
plus a hatch ``<circle>``. The balls are a ``Discs`` now, one painted group for all of them.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.core import brands, domain
from synthetic_ecommerce_data.core.drawing import draw_sku, product_look, svg_problems
from synthetic_ecommerce_data.core.drawing.model import Disc, Discs
from synthetic_ecommerce_data.domains.industrial.drawing.figures import bearing
from synthetic_ecommerce_data.domains.industrial.newtypes import (
    _BEARINGS_INCH,
    _BEARINGS_METRIC,
    _CLOSURES,
)
from test_sku_drawings import MAX_DRAWING_BYTES

KEY = "bearing_radial_ball"
#: The materials ``build_bearing`` draws from.
MATERIALS = ("Chrome Steel", "440C Stainless Steel")
#: The closure that draws the balls; a shield or a seal paints one disc over them.
OPEN = "Open"


def _records():
    for table, unit in ((_BEARINGS_METRIC, "mm"), (_BEARINGS_INCH, '"')):
        for number, bore, od, width in table:
            yield {
                "Bearing Number": number,
                "Bore Dia.": f"{bore}{unit}",
                "Outside Dia.": f"{od}{unit}",
                "Width": f"{width}{unit}",
                "Closure Type": OPEN,
            }


def _angle_per_turned_size() -> list[int]:
    """One angle of the type's orientation per size its box turns to.

    The scale and the magnifier read the angle only through the box it turns to
    (``product_look.turned``), and ``a``, ``180 - a``, ``180 + a`` and ``360 - a`` turn it to the
    same box, so they draw the same shapes. Only the ``rotate`` differs, so the largest angle of
    each, the one with the most digits, stands for them.
    """
    largest: dict[int, int] = {}
    for angle in product_look.ORIENTATIONS[domain.orientation(KEY)]:
        size = min(angle % 180, 180 - angle % 180)
        largest[size] = max(largest.get(size, angle), angle)
    return sorted(largest.values())


def _product_at(angles: list[int]) -> dict[int, str]:
    """A product id the drawing turns to each of ``angles``."""
    orientation = domain.orientation(KEY)
    found: dict[int, str] = {}
    n = 0
    while len(found) < len(angles):
        product_id = f"QRB-RB{n}-2684-0001"
        angle = product_look.angle_of(product_id, orientation)
        if angle in angles:
            found.setdefault(angle, product_id)
        n += 1
    return found


ANGLES = _angle_per_turned_size()


def test_each_turned_size_of_the_any_orientation_has_one_angle():
    assert domain.orientation(KEY) == "any"
    assert ANGLES == [180, 270, 285, 300, 315, 330, 345]


def test_the_open_closure_is_one_the_generator_offers():
    assert OPEN in {name for name, *_ in _CLOSURES}


@pytest.mark.parametrize("material", MATERIALS)
def test_no_bearing_any_brand_could_offer_draws_past_the_size_cap(material):
    """Every table row, open, in each brand's house style, at each size the type's turns give
    its box: the magnifier, which draws the balls twice, depends on the turned size."""
    products = _product_at(ANGLES)
    largest, drawn = (0, ()), 0
    for record in _records():
        for brand in brands.BRANDS:
            for angle, product_id in products.items():
                data, _ = draw_sku(KEY, brand, {**record, "Material": material}, product_id)
                assert svg_problems(data) == [], (brand, record)
                largest = max(largest, (len(data), (record["Bearing Number"], brand, angle)))
                drawn += 1
    rows = len(_BEARINGS_METRIC) + len(_BEARINGS_INCH)
    assert drawn == rows * len(brands.BRANDS) * len(ANGLES)
    assert largest[0] < MAX_DRAWING_BYTES, largest


@pytest.mark.parametrize(("number", "bore", "od", "width"), [_BEARINGS_METRIC[0]])
def test_an_open_bearings_balls_are_one_discs_and_a_closed_ones_are_none(number, bore, od, width):
    record = {"Bore Dia.": f"{bore}mm", "Outside Dia.": f"{od}mm", "Width": f"{width}mm"}
    open_shapes = bearing({**record, "Closure Type": OPEN}).figure.shapes
    balls = [s for s in open_shapes if isinstance(s, Discs)]
    assert len(balls) == 1 and len(balls[0].centres) >= 6
    # The rings stay discs: only the repeated part is grouped.
    assert len([s for s in open_shapes if isinstance(s, Disc)]) == 4
    shielded = bearing({**record, "Closure Type": "Double Shield"}).figure.shapes
    assert not any(isinstance(s, Discs) for s in shielded)
