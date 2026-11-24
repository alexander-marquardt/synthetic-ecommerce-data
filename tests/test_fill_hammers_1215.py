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
#: A head thinner than its sheet is wide, over a handle narrower than the head.
FLOORS: dict[str, float] = {
    "hammer_ball_pein": 0.39,  # a ball and a neck are narrower than the cheek
    "hammer_claw": 0.40,  # the claw curves away, and its V is open
    "hammer_framing": 0.40,  # the straight claw tapers to its tip
}


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


def _areas(key):
    """Every size in every handle, grip and face, at every angle."""
    yield from _measured(key, hammers.KINDS[key].ounces, _handles(key), _angles(key))


def test_every_named_exception_is_under_the_floor():
    """An exception that reaches the floor is an exception no longer."""
    for key, floor in FLOORS.items():
        assert floor <= min(area.cover for _, _, area in _areas(key)) < FLOOR, key


@pytest.mark.parametrize("key", sorted(hammers.KINDS))
def test_every_size_handle_and_angle_fills_the_floor_with_a_highlight_and_a_shadow(key):
    for angle, record, area in _areas(key):
        assert area.cover >= FLOORS.get(key, FLOOR), (angle, record, area)
        assert area.highlight and area.shadow and not area.flat, (angle, record, area)


@pytest.mark.parametrize("key", sorted(hammers.KINDS))
def test_a_longer_hammer_is_drawn_larger_by_whichever_length_it_publishes(key):
    figure = drawing._figure(key)[0]
    kind, (handle, grip) = hammers.KINDS[key], _handles(key)[0]
    records = [_record(kind, oz, handle, grip, kind.faces[0]) for oz in sorted(kind.ounces)]
    for unpublished in ((), ("Overall Length",), ("Overall Length", "Handle Length")):
        published = [{k: v for k, v in r.items() if k not in unpublished} for r in records]
        drawn = [figure(record) for record in published]
        heights = [d.figure.bounds()[3] for d in drawn]
        assert heights == sorted(set(heights)), unpublished
        assert {d.source for d in drawn} == {"partial" if unpublished else "record"}


def test_the_record_s_handle_grip_and_face_are_drawn():
    """A wood handle, a gripped one and a bare one, and a milled face, each draw apart."""
    figure, kind = drawing._figure("hammer_claw")[0], hammers.KINDS["hammer_claw"]
    drawn = [
        figure(_record(kind, 16, handle, grip, face)).figure.shapes
        for handle, grip, face in (
            ("Hickory", "None", "Smooth"),
            ("Steel", "None", "Smooth"),
            ("Steel", "Rubber", "Smooth"),
            ("Steel", "Rubber", "Milled"),
        )
    ]
    assert all(a != b for k, a in enumerate(drawn) for b in drawn[k + 1 :])
