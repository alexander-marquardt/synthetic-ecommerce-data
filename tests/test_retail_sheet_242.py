"""No retail drawing extends past its 400 x 400 sheet (gen#242).

The appliance tests of gen#202 count marks and refuse printed sizes, and a pedestal fan's lower
pole was drawn 148 units tall from y=286, ending at y=434: past its base and off the sheet, in all
four pedestal styles, with every drawing test green. Nothing measured where a drawing ends.

:mod:`sheet_extent` measures the geometry an SVG places (curves at their true extremes, through
every group's transform). The sweep renders every SKU image of every authored retail row on the
plain sheet a shape is drawn on (the house style later scales it into a frame, which would hide an
overrun of up to 28 % behind the shrink), and lists the rows whose drawing leaves it. The unit
tests hold the measure itself, with the pole drawn as the review found it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import image_release  # noqa: E402
import scale  # noqa: E402
import sheet_extent  # noqa: E402

SHEET = 400.0


def _svg(body: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{body}</svg>'


def overruns() -> dict[str, tuple[float, str]]:
    """``product_id -> (worst overrun in units, its shape)`` for each row with a SKU image that
    reaches past the sheet. An image is drawn once, as :func:`image_release.image_files` does."""
    seen: set[str] = set()
    out: dict[str, tuple[float, str]] = {}
    for rec in scale.templates():
        for sku in rec["skus"]:
            image = export.image_id(rec, sku)
            if image in seen:
                continue
            seen.add(image)
            past = sheet_extent.overrun(image_release.render(rec, sku, styled=False), SHEET)
            if past > out.get(rec["product_id"], (0.0, ""))[0]:
                out[rec["product_id"]] = (past, rec["drawing"]["shape"])
    return out


def test_no_retail_drawing_extends_past_its_sheet() -> None:
    found = overruns()
    worst = sorted(found.items(), key=lambda kv: -kv[1][0])
    listing = "; ".join(f"{pid} ({shape}) by {past:.1f}" for pid, (past, shape) in worst)
    assert not found, (
        f"{len(found)} rows draw past the {SHEET:g} x {SHEET:g} sheet: {listing}. "
        "Draw the shape inside the sheet; do not widen the check."
    )


# --------------------------------------------------------------------------
# The measure
# --------------------------------------------------------------------------


def test_the_pedestal_fan_pole_of_the_review_is_off_the_sheet() -> None:
    pole = _svg('<rect x="190" y="286" width="20" height="148"/>')
    assert sheet_extent.reach(pole) == (190, 286, 210, 434)
    assert sheet_extent.overrun(pole) == pytest.approx(34)


def test_a_pole_ending_on_the_sheet_edge_is_inside() -> None:
    assert sheet_extent.overrun(_svg('<rect x="190" y="252" width="20" height="148"/>')) == 0


@pytest.mark.parametrize(
    ("body", "past"),
    [
        ('<rect x="-12" y="10" width="20" height="20"/>', 12),
        ('<rect x="10" y="-7" width="20" height="20"/>', 7),
        ('<rect x="380" y="10" width="30" height="20"/>', 10),
        ('<rect x="10" y="380" width="20" height="45"/>', 25),
    ],
)
def test_every_side_of_the_sheet_counts(body: str, past: float) -> None:
    assert sheet_extent.overrun(_svg(body)) == pytest.approx(past)


def test_rounding_in_the_drawing_numbers_is_not_an_overrun() -> None:
    assert sheet_extent.overrun(_svg('<rect x="390" y="10" width="10.4" height="20"/>')) == 0
    assert sheet_extent.overrun(_svg('<rect x="390" y="10" width="11" height="20"/>')) > 0


def test_a_path_is_measured_through_its_lines_and_relative_moves() -> None:
    assert sheet_extent.reach(_svg('<path d="M10,20 L50,20 l0,30 H5 V60 Z"/>')) == (5, 20, 50, 60)


def test_a_curve_is_measured_at_its_extreme_not_at_its_control_points() -> None:
    # The control points sit at y=-50; the curve itself reaches only y=-12.5.
    bowed = _svg('<path d="M100,100 C100,-50 300,-50 300,100"/>')
    box = sheet_extent.reach(bowed)
    assert box is not None
    assert box[1] == pytest.approx(-12.5)
    # A control point beyond the sheet whose curve stays inside is not an overrun.
    inside = _svg('<path d="M10,200 Q200,420 390,200"/>')
    assert sheet_extent.overrun(inside) == 0
    # A curve whose ends are inside and whose bulge is outside is one.
    assert sheet_extent.overrun(_svg('<path d="M10,300 C10,500 390,500 390,300"/>')) > 0


def test_a_quadratic_and_a_smooth_curve_are_measured() -> None:
    assert sheet_extent.reach(_svg('<path d="M0,0 Q50,100 100,0"/>')) == (0, 0, 100, 50)
    smooth = sheet_extent.reach(_svg('<path d="M0,0 C0,40 40,40 40,0 S80,-40 80,0"/>'))
    assert smooth is not None
    assert smooth[1] == pytest.approx(-30) and smooth[3] == pytest.approx(30)
    chain = sheet_extent.reach(_svg('<path d="M0,0 Q50,100 100,0 T200,0"/>'))
    assert chain is not None
    assert chain[1] == pytest.approx(-50) and chain[3] == pytest.approx(50)


def test_an_arc_is_measured_around_the_circle_it_runs_along() -> None:
    half = sheet_extent.reach(_svg('<path d="M100,200 A100,100 0 0 1 300,200"/>'))
    assert half is not None
    assert half[1] == pytest.approx(100, abs=0.1) and half[3] == pytest.approx(200, abs=0.1)
    assert half[0] == pytest.approx(100) and half[2] == pytest.approx(300)


def test_circles_and_ellipses_are_measured_by_their_radii() -> None:
    assert sheet_extent.reach(_svg('<circle cx="390" cy="50" r="15"/>')) == (375, 35, 405, 65)
    assert sheet_extent.reach(_svg('<ellipse cx="200" cy="200" rx="30" ry="10"/>')) == (
        170, 190, 230, 210)  # fmt: skip


def test_groups_move_and_scale_what_they_hold() -> None:
    moved = _svg('<g transform="translate(300 0)"><rect x="0" y="0" width="150" height="10"/></g>')
    assert sheet_extent.reach(moved) == (300, 0, 450, 10)
    scaled = _svg('<g transform="scale(.5)"><rect x="0" y="0" width="900" height="10"/></g>')
    assert sheet_extent.reach(scaled) == (0, 0, 450, 5)
    nested = _svg('<g transform="translate(100 0)"><g transform="translate(250 0)">'
                  '<rect width="10" height="10"/></g></g>')  # fmt: skip
    assert sheet_extent.reach(nested) == (350, 0, 360, 10)


def test_a_rotated_rect_is_measured_by_its_turned_corners() -> None:
    # A quarter turn clockwise about (200, 200) takes a bar to the right of it to below it.
    turned = _svg(
        '<g transform="rotate(90 200 200)"><rect x="250" y="190" width="100" height="20"/></g>'
    )
    assert sheet_extent.reach(turned) == pytest.approx((190, 250, 210, 350))


def test_an_ellipse_is_measured_through_a_turn() -> None:
    turned = _svg(
        '<g transform="rotate(90 200 200)"><ellipse cx="200" cy="200" rx="30" ry="10"/></g>'
    )
    assert sheet_extent.reach(turned) == pytest.approx((190, 170, 210, 230))
    moved = _svg('<g transform="translate(5 7)"><ellipse cx="50" cy="60" rx="30" ry="10"/></g>')
    assert sheet_extent.reach(moved) == pytest.approx((25, 57, 85, 77))


def test_a_large_arc_is_measured_around_its_own_center() -> None:
    # From (100, 200) to (200, 100) the long way round a circle centered on (100, 100).
    long_way = sheet_extent.reach(_svg('<path d="M100,200 A100,100 0 1 1 200,100"/>'))
    assert long_way == pytest.approx((0, 0, 200, 200), abs=0.1)
    short_way = sheet_extent.reach(_svg('<path d="M100,200 A100,100 0 0 1 200,100"/>'))
    assert short_way == pytest.approx((100, 100, 200, 200), abs=0.1)


def test_a_clipped_path_is_cut_to_its_clip() -> None:
    clipped = _svg('<clipPath id="c"><path d="M80,80 L320,80 L320,320 L80,320 Z"/></clipPath>'
                   '<path d="M-100,100 L500,300" clip-path="url(#c)"/>')  # fmt: skip
    assert sheet_extent.reach(clipped) == (80, 100, 320, 300)
    with pytest.raises(ValueError, match="names no clipPath"):
        sheet_extent.reach(_svg('<path d="M0,0 L9,9" clip-path="url(#nope)"/>'))


def test_a_definition_is_not_a_drawing() -> None:
    tile = _svg('<defs><pattern id="p"><rect width="900" height="900"/></pattern></defs>'
                '<rect width="400" height="400" fill="url(#p)"/>')  # fmt: skip
    assert sheet_extent.reach(tile) == (0, 0, 400, 400)


def test_a_drawing_with_nothing_drawn_reaches_nowhere() -> None:
    assert sheet_extent.reach(_svg("")) is None
    assert sheet_extent.overrun(_svg("")) == 0


@pytest.mark.parametrize(
    "body",
    [
        '<polygon points="0,0 500,0 500,9"/>',
        '<path d="M0,0 R5,5"/>',
        '<g transform="skewX(20)"><rect width="9" height="9"/></g>',
        '<line x1="10" y1="10" x2="450" y2="10"/>',
        '<polyline points="0,0 500,0"/>',
        '<use href="#a"/>',
        '<image href="a.png" width="9" height="9"/>',
        '<svg x="380" y="0" width="100" height="100"><rect width="50" height="50"/></svg>',
        '<rect width="50" height="50" style="fill:red;transform:translate(500px,0)"/>',
        '<clipPath id="c" transform="translate(400 0)"><rect width="400" height="400"/></clipPath>'
        '<rect width="50" height="50" clip-path="url(#c)"/>',
        '<clipPath id="c" clipPathUnits="objectBoundingBox"><rect width="1" height="1"/></clipPath>'
        '<rect width="50" height="50" clip-path="url(#c)"/>',
    ],
)
def test_what_the_measure_cannot_read_is_refused_not_skipped(body: str) -> None:
    with pytest.raises(ValueError, match="not read"):
        sheet_extent.reach(_svg(body))


def test_a_clip_bigger_than_the_sheet_still_flags_what_it_lets_through() -> None:
    wide = _svg('<clipPath id="c"><rect x="-100" y="0" width="900" height="400"/></clipPath>'
                '<rect x="300" y="0" width="300" height="50" clip-path="url(#c)"/>')  # fmt: skip
    assert sheet_extent.overrun(wide) == pytest.approx(200)


def test_text_is_not_measured() -> None:
    # Documented: a label is not geometry a shape places, so it is skipped, not measured.
    assert sheet_extent.reach(_svg('<text x="500" y="20">hi</text>')) is None


def test_a_glow_keeps_the_text_of_every_number_inside_the_sheet() -> None:
    import kit_lighting

    inside = "M246.0,216.0 L346.0,216.0 L300.5,399.5 Z"
    assert f'd="{inside}"' in kit_lighting._glow(inside)
    held = kit_lighting._glow("M246.0,216.0 L451.5,216.0 L-3,410 Z")
    assert 'd="M246.0,216.0 L400,216.0 L0,400 Z"' in held
