"""Cut-resistant gloves are drawn as the pair they are sold as, large and lit (#1217).

Every size in every coating and shell, at every angle its orientation allows, is measured with
#1129's sweep (``picture_fill_1129.sheet_measures``): the share of the figure area it paints,
its highlight and shadow. Gloves have no pack axis (they are sold as one pair)."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.core import brands, domain, drawing  # noqa: E402
from synthetic_ecommerce_data.core.drawing import product_look, sheet  # noqa: E402
from synthetic_ecommerce_data.core.drawing.model import Dots, Poly  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.product_types.safety import (  # noqa: E402
    cut_resistant_gloves,
)

KEY = "cut_resistant_gloves"
#: The floor at each angle (and at the angle half a turn on, which paints the same). Where it is
#: under 50% it is the named exception: a pair is nearly square, and a solid square turned to 45
#: degrees covers 41% of the 164 x 200 area, before the gaps between the fingers.
FLOORS = {
    0: 0.50, 15: 0.50, 30: 0.50, 45: 0.43, 60: 0.40, 75: 0.42,
    90: 0.49, 105: 0.40, 120: 0.39, 135: 0.40, 150: 0.47, 165: 0.50,
}  # fmt: skip


def _records() -> list[dict[str, str]]:
    looks = {(line.material, line.coating) for line in cut_resistant_gloves.MODEL_LINES}
    return [
        {"Size": size.name, "Material": material, "Coating": coating}
        for size in cut_resistant_gloves.HAND_SIZES
        for material, coating in sorted(looks)
    ]


def _outlines(svg: bytes) -> tuple[list[float], list[list[tuple[float, float]]]]:
    """The turn of a drawing's figure, and each hatched outline's points as the sheet shows them."""
    text = svg.decode()
    turn = re.search(r'<g transform="rotate\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)">', text)
    angle, cx, cy = (float(v) for v in turn.groups()) if turn else (0.0, 0.0, 0.0)
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    outlines = []
    for points in re.findall(r'<path d="([^"]+)"[^>]*fill="url\(#h', text):
        outlines.append([])
        for x, y in re.findall(r"[ML]([-\d.]+) ([-\d.]+)", points):
            dx, dy = float(x) - cx, float(y) - cy
            outlines[-1].append((cx + dx * c - dy * s, cy + dx * s + dy * c))
    return [angle, cx, cy], outlines


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
            assert area.cover >= FLOORS[angle % 180], (angle, record, area)
            assert area.highlight and area.shadow and not area.flat, (angle, record, area)


def test_the_pair_is_centred_and_inside_the_figure_area_at_every_angle():
    for size in cut_resistant_gloves.HAND_SIZES:
        figure = cut_resistant_gloves.figure({"Size": size.name}).figure
        for angle in product_look.ORIENTATIONS["any"]:
            scale = sheet.outline_scale(figure, angle)
            ((x0, y0, x1, y1),) = sheet.figure_boxes(figure, scale, 0.0, angle)
            record = {"Size": size.name, "Material": "HPPE"}
            svg, _ = drawing._draw(KEY, brands.BRANDS[0], record, scale, angle)
            (turn, *_), outlines = _outlines(svg)
            assert turn == angle % 360
            xs, ys = zip(*(p for outline in outlines for p in outline), strict=True)
            # The outlines, as drawn: they fill the area one way, and sit in its middle.
            assert min(xs) >= sheet.MARGIN - 0.3 and max(xs) <= 200 - sheet.MARGIN + 0.3
            assert min(ys) >= sheet.MARGIN - 0.3
            assert max(ys) <= sheet.FIGURE_HEIGHT - sheet.MARGIN + 0.3
            assert abs((min(xs) + max(xs)) / 2 - 100) < 0.3, (size, angle)
            assert abs((min(ys) + max(ys)) / 2 - sheet.FIGURE_HEIGHT / 2) < 0.3, (size, angle)
            assert abs((x1 - x0) - (max(xs) - min(xs))) < 0.5, "figure_boxes reads the outline"
            assert abs((y1 - y0) - (max(ys) - min(ys))) < 0.5, "figure_boxes reads the outline"


def test_the_palm_wears_its_coating_and_a_pair_is_two_gloves():
    def shapes(coating: str):
        return cut_resistant_gloves.figure({"Size": "Large", "Coating": coating}).figure.shapes

    def polys(coating: str, role: str):
        return [s for s in shapes(coating) if isinstance(s, Poly) and s.role == role]

    assert {line.coating for line in cut_resistant_gloves.MODEL_LINES} == {
        "Uncoated", "PVC Dots", *cut_resistant_gloves.COATING_FILL,
    }  # fmt: skip
    for coating, fill in cut_resistant_gloves.COATING_FILL.items():
        assert len(polys(coating, "part")) == 2
        assert [s.fill for s in polys(coating, "grip")] == [fill], "one palm shows"
    for bare in ("Uncoated", "PVC Dots"):
        assert polys(bare, "grip") == []
    dotted = [s for s in shapes("PVC Dots") if isinstance(s, Dots)]
    assert len(dotted) == 1 and not [s for s in shapes("Uncoated") if isinstance(s, Dots)]
