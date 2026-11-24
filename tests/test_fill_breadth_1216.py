"""Breadth types drawn as their own product fill at least half of the product area (#1216).

Each type of ``BREADTH_PRODUCTS`` is drawn at every angle its orientation allows, at every size it
sells, and measured with #1129's sweep (``picture_fill_1129.sheet_measures``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.core import brands, domain, drawing  # noqa: E402
from synthetic_ecommerce_data.core.drawing import product_look  # noqa: E402
from synthetic_ecommerce_data.domains.industrial import breadth  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.drawing import breadth_rungs  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_products import (  # noqa: E402
    BREADTH_PRODUCTS,
)

FLOOR = 0.50
#: The named exceptions: a true outline that cannot reach the floor, at its own measured one.
FLOORS: dict[str, float] = {
    "c_clamps": 0.42,  # its throat is open
    "chain_lubricants": 0.41,  # an aerosol is a narrow can
    "compound_cutters": 0.39,  # its handles stand apart
    "eye_bolts": 0.43,  # an open eye over a narrower shank
    "replacement_pins": 0.36,  # an eye, a collar and a narrower shank
    # Rods, laid corner to corner.
    "magnetic_bit_holders": 0.23,
    "pin_pullers": 0.20,
    "sds_drill_bits": 0.18,
    "tap_extractors": 0.24,
    "thread_plug_gages": 0.26,
}


def test_every_named_exception_is_under_the_floor():
    """An exception that reaches the floor is an exception no longer."""
    for key, floor in FLOORS.items():
        assert floor <= min(area.cover for _, _, area in _measured(key)) < FLOOR, key


def _measured(key):
    row = breadth.row_for(key)
    common = {name: values[0] for name, values in row.attributes.items()}
    records = [{**common, row.size_attr: value} for value in row.size_values]
    ratios = breadth_rungs.ratios(key, records)
    for angle in product_look.ORIENTATIONS[domain.orientation(key)]:
        scale = drawing.product_scale_for(key, records, angle)
        for record, ratio in zip(records, ratios, strict=True):
            svg, _ = drawing._draw(key, brands.BRANDS[0], record, scale * ratio, angle)
            assert drawing.svg_problems(svg) == [], (key, record)
            _, area = pf.sheet_measures(svg)
            yield angle, record, area


@pytest.mark.parametrize("key", sorted(BREADTH_PRODUCTS))
def test_every_size_and_angle_fills_the_floor_with_a_highlight_and_a_shadow(key):
    for angle, record, area in _measured(key):
        assert area.cover >= FLOORS.get(key, FLOOR), (angle, record, area)
        assert area.highlight and area.shadow and not area.flat, (angle, record, area)
