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
FLOORS: dict[str, float] = {}


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
