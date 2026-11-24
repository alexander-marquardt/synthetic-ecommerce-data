"""Household tool sets, picture hangers and assortment kits are drawn large and lit (#1215).

Each type is drawn in every container, style, color, count and rating it sells, at the angles its
orientation allows, and measured with #1129's sweep (``picture_fill_1129.sheet_measures``): the
share of the figure area it paints, its highlight and its shadow. None of them has a pack axis."""

from __future__ import annotations

import functools
import sys
from itertools import product
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.core import brands, domain, drawing  # noqa: E402
from synthetic_ecommerce_data.core.drawing import product_look  # noqa: E402
from synthetic_ecommerce_data.domains.industrial import newtypes  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.product_types.fasteners import (  # noqa: E402
    picture_hangers as hangers,
)
from synthetic_ecommerce_data.domains.industrial.product_types.hand_tools import (  # noqa: E402
    household_tool_sets as sets,
)

FLOOR = 0.50
#: The named exceptions: a true outline that cannot reach the floor, at its own measured one.
FLOORS: dict[tuple[str, str], float] = {}


def _set_records():
    for container, color, pieces in product(sets.CONTAINERS, sets.COLORS, sets.PIECE_COUNTS):
        record = {"Container Type": container, "Color": color, "Piece Count": str(pieces)}
        yield container, {**record, "Material": sets.MATERIALS[0]}


def _hanger_records():
    for style, ratings in hangers.LB_RATINGS.items():
        for color, pounds in product(hangers.COLORS, ratings):
            record = {"Style": style, "Color": color, "Load Capacity": f"{pounds} lbf"}
            yield style, {**record, "Material": hangers.MATERIALS[0]}


def _kit_records():
    for kit, container in product(newtypes.KITS, newtypes._KIT_CONTAINER):
        sizes = kit.designations or kit.sizes
        for finish in newtypes._KIT_FINISH[kit.part_type]:
            record = {
                "Type": kit.item,
                "Finish": finish,
                "Container Type": container,
                "Piece Count": str(kit.per_size * len(sizes)),
                "Sizes Included": ", ".join(str(s) for s in sizes),
            }
            yield container, {**record, "Material": newtypes._KIT_MATERIAL[kit.part_type][0]}


RECORDS = {
    "household_tool_sets": _set_records,
    "picture_hangers": _hanger_records,
    "kit_assortment": _kit_records,
}


@functools.cache
def _areas(key):
    """Every (shape name, record, angle, area measure) of a type."""
    out = []
    for angle in product_look.ORIENTATIONS[domain.orientation(key)]:
        scale = drawing.product_scale_for(key, [], angle)
        for name, record in RECORDS[key]():
            svg, source = drawing._draw(key, brands.BRANDS[0], record, scale, angle)
            assert source == "record" and drawing.svg_problems(svg) == [], record
            out.append((name, record, angle, pf.sheet_measures(svg)[1]))
    return out


@pytest.mark.parametrize("key", sorted(RECORDS))
def test_every_record_and_angle_fills_the_floor_with_a_highlight_and_a_shadow(key):
    bad = [
        (name, record, angle, area)
        for name, record, angle, area in _areas(key)
        if area.cover < FLOORS.get((key, name), FLOOR)
        or not (area.highlight and area.shadow)
        or area.flat
    ]
    assert not bad, (len(bad), len(_areas(key)), min(bad, key=lambda b: b[3].cover))


def test_every_named_exception_is_under_the_floor():
    """An exception that reaches the floor is an exception no longer."""
    for (key, shape), floor in FLOORS.items():
        least = min(area.cover for name, _, _, area in _areas(key) if name == shape)
        assert floor <= least < FLOOR, (key, shape, least)
