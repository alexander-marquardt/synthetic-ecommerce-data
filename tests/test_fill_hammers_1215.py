"""Every hammer is drawn as its real kind, large and lit (#1215).

Each kind is drawn in every size, handle, grip and face it sells, at the angles its orientation
allows, and measured with #1129's sweep (``picture_fill_1129.sheet_measures``): the share of the
figure area it paints, its highlight and its shadow. A hammer has no pack axis."""

from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.core import brands, domain, drawing  # noqa: E402
from synthetic_ecommerce_data.core.drawing import product_look  # noqa: E402
from synthetic_ecommerce_data.domains.industrial import hammers, series  # noqa: E402

FLOOR = 0.50
#: The named exceptions: a true outline that cannot reach the floor, at its own measured one.
FLOORS: dict[str, float] = {}


def _record(kind, ounces, handle, grip, face) -> dict[str, str]:
    oal = float(series.snap_imperial(kind.oal_base + ounces * kind.oal_per_oz, 16))
    return {
        "Material": kind.material,
        "Handle Material": handle,
        "Handle Grip Material": grip,
        "Face Type": face,
        "Head Weight": f"{ounces} oz",
        "Overall Length": f'{oal}"',
        "Face Dia.": f'{kind.face_base + ounces * kind.face_per_oz:.4f}"',
        "Handle Length": f'{oal - kind.head_trim}"',
    }


def _measured(key, sizes, handles, angles):
    kind = hammers.KINDS[key]
    for angle in angles:
        scale = drawing.product_scale_for(key, [], angle)
        for ounces, (handle, grip), face in product(sizes, handles, kind.faces):
            record = _record(kind, ounces, handle, grip, face)
            svg, source = drawing._draw(key, brands.BRANDS[0], record, scale, angle)
            assert source == "record" and drawing.svg_problems(svg) == [], record
            yield angle, record, pf.sheet_measures(svg)[1]


def _angles(key):
    return product_look.ORIENTATIONS[domain.orientation(key)]


def _handles(key):
    return [(h, g) for h in hammers.KINDS[key].handles for g in hammers.HAMMER_GRIPS[h]]


@pytest.mark.parametrize("key", sorted(hammers.KINDS))
def test_every_size_handle_and_angle_fills_the_floor_with_a_highlight_and_a_shadow(key):
    kind, handles = hammers.KINDS[key], _handles(key)
    every_size = _measured(key, kind.ounces, handles[:1], _angles(key))
    every_handle = _measured(key, (min(kind.ounces), max(kind.ounces)), handles, _angles(key)[:1])
    for angle, record, area in (*every_size, *every_handle):
        assert area.cover >= FLOORS.get(key, FLOOR), (angle, record, area)
        assert area.highlight and area.shadow and not area.flat, (angle, record, area)
