"""Cut-resistant gloves are drawn as the pair they are sold as, large and lit (#1217).

Every size in every coating and shell, at every angle its orientation allows, is measured with
#1129's sweep (``picture_fill_1129.sheet_measures``): the share of the figure area it paints,
its highlight and shadow. Gloves have no pack axis (they are sold as one pair)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.core import brands, domain, drawing  # noqa: E402
from synthetic_ecommerce_data.core.drawing import product_look  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.product_types.safety import (  # noqa: E402
    cut_resistant_gloves,
)

KEY = "cut_resistant_gloves"
FLOORS: dict[int, float] = {}


def _records() -> list[dict[str, str]]:
    looks = {(line.material, line.coating) for line in cut_resistant_gloves.MODEL_LINES}
    return [
        {"Size": size.name, "Material": material, "Coating": coating}
        for size in cut_resistant_gloves.HAND_SIZES
        for material, coating in sorted(looks)
    ]


def test_every_pair_fills_its_floor_with_a_highlight_and_a_shadow():
    # One test over every angle, so its id is the same whatever the orientation's angles are.
    records = _records()
    assert len(records) > 60
    angles = product_look.ORIENTATIONS[domain.orientation(KEY)]
    assert len(angles) == 24, "gloves read at any angle (#860)"
    for angle in angles:
        scale = drawing.product_scale_for(KEY, [], angle)
        for record in records:
            svg, source = drawing._draw(KEY, brands.BRANDS[0], record, scale, angle)
            assert source == "record" and drawing.svg_problems(svg) == [], record
            _, area = pf.sheet_measures(svg)
            assert area.cover >= FLOORS.get(angle % 180, 0.30), (angle, record, area)
            assert area.highlight and area.shadow and not area.flat, (angle, record, area)
