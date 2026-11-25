"""Safety glasses are drawn as their real product, large and lit (#1217).

Every model line in every lens tint, at every angle its orientation allows, is measured with
#1129's sweep (``picture_fill_1129.sheet_measures``): the share of the figure area it paints,
its highlight and shadow. A pair has no pack axis (it is sold as one pair)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.core import brands, domain, drawing  # noqa: E402
from synthetic_ecommerce_data.core.drawing import product_look  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.product_types.safety import (  # noqa: E402
    safety_glasses,
)

KEY = "safety_glasses"
#: The named exception to the 50% floor: a pair's front is about 5.9 x 1.9 inches, and a solid
#: box of that shape covers 39% of the 164 x 200 area at its best angle.
FLOORS = {KEY: 0.30}
#: The widest share of the area the old front view painted, at any angle.
OLD_BEST = 0.223


def _records() -> list[dict[str, str]]:
    seen = {}
    for line in safety_glasses.MODEL_LINES:
        for tint in line.tints:
            record = {"Style": line.style, "Material": "Polycarbonate", "Lens Color": tint}
            if line.frame_color:
                record["Frame Color"] = line.frame_color
            seen[(line.style, line.frame_color, tint)] = record
    return list(seen.values())


def test_every_pair_fills_its_floor_with_a_highlight_and_a_shadow():
    # One test over every angle, so its id is the same whatever the orientation's angles are.
    assert FLOORS[KEY] > OLD_BEST
    records = _records()
    assert len(records) > 40
    for angle in product_look.ORIENTATIONS[domain.orientation(KEY)]:
        scale = drawing.product_scale_for(KEY, [], angle)
        for record in records:
            svg, source = drawing._draw(KEY, brands.BRANDS[0], record, scale, angle)
            assert source == "record" and drawing.svg_problems(svg) == [], record
            _, area = pf.sheet_measures(svg)
            assert area.cover >= FLOORS[KEY], (angle, record, area)
            assert area.highlight and area.shadow and not area.flat, (angle, record, area)
