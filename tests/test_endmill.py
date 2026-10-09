from __future__ import annotations

import math

import numpy as np
import pytest

from helpers import (
    color_mask,
    figure_pixels,
    longest_row_runs,
    pixels_per_inch,
    rows_from_top,
    within_axes,
)
from synthetic_ecommerce_data.core.dimensions import DimensionParseError
from synthetic_ecommerce_data.domains.industrial.records import BUNDLED, FIXTURES
from synthetic_ecommerce_data.domains.industrial.render import CARD, DETAIL, endmill
from synthetic_ecommerce_data.domains.industrial.render.canvas import DIM, FLUTE, INK

#: The observed reference end mills do not publish ``End Mill Style``, and the
#: renderer requires it -- see records.py -- so the dimensioned drawing is
#: exercised against generated records, which do. 33TN24's contribution, a tool
#: whose two diameters carry the same value, is reproduced by 52BN29.
REC = BUNDLED["26VW40"]
DIMENSIONED_SKUS = ["26VW40", "52BN29", "77VV89", "60AR50", "83LZ75"]


def test_the_geometry_is_read_off_the_record():
    geom = endmill.geometry_from_record(REC)
    assert geom.cut_d.inches == 9 / 32
    assert geom.shank_d.inches == 5 / 16
    assert geom.loc.inches == 0.875
    assert geom.oal.inches == 1.625
    assert geom.flutes == 4
    assert geom.helix_deg == 45.0
    assert geom.style == "square"
    assert geom.hand == 1
    assert geom.double_end is False


def test_the_cutting_end_comes_from_the_record_and_is_required():
    """The defect this attribute was added for: 486 ball nose mills drawn square.

    ``End Mill Style`` was published on every generated end mill and read by
    nothing, so a record saying "Ball Nose" produced a drawing with a flat
    bottom -- a picture contradicting its own data, which is the one failure
    this renderer is built to make impossible.
    """
    assert endmill.geometry_from_record(BUNDLED["52BN29"]).style == "ball"
    assert endmill.geometry_from_record(BUNDLED["26VW40"]).style == "square"
    with pytest.raises(endmill.MissingAttributeError):
        endmill.geometry_from_record({k: v for k, v in REC.items() if k != "End Mill Style"})
    with pytest.raises(endmill.UnsupportedFeatureError):
        endmill.geometry_from_record({**REC, "End Mill Style": "Corner Chamfer"})


def test_a_ball_nose_and_a_square_end_are_different_drawings(tmp_path):
    square = endmill.render(BUNDLED["52BN29"] | {"End Mill Style": "Square"}, tmp_path / "a.png")
    ball = endmill.render(BUNDLED["52BN29"], tmp_path / "b.png")
    assert square.read_bytes() != ball.read_bytes()


def test_the_hand_of_the_helix_comes_from_the_record(tmp_path):
    assert endmill.geometry_from_record(BUNDLED["83LZ75"]).hand == -1
    right = {**BUNDLED["83LZ75"], "Cutting Direction": "Right Hand"}
    assert endmill.geometry_from_record(right).hand == 1
    assert (
        endmill.render(BUNDLED["83LZ75"], tmp_path / "a.png").read_bytes()
        != endmill.render(right, tmp_path / "b.png").read_bytes()
    )


def test_a_double_ended_mill_is_drawn_with_two_cutting_ends(tmp_path):
    """And the shank is what is left between them.

    Drawing a double-end tool as a single-end one puts a plain shank where a
    second set of flutes is, which is a different tool.
    """
    geom = endmill.geometry_from_record(BUNDLED["77VV89"])
    assert geom.double_end
    single = {**BUNDLED["77VV89"], "Single End/Double End": "Single End"}
    assert (
        endmill.render(BUNDLED["77VV89"], tmp_path / "a.png").read_bytes()
        != endmill.render(single, tmp_path / "b.png").read_bytes()
    )
    # Two cutting ends need two lengths of cut to fit inside the tool.
    with pytest.raises(endmill.ImpossibleGeometryError):
        endmill.geometry_from_record({**BUNDLED["77VV89"], "Length of Cut": "20.00mm"})


def test_a_corner_radius_is_drawn_and_a_ball_nose_cannot_have_one(tmp_path):
    geom = endmill.geometry_from_record(BUNDLED["60AR50"])
    assert geom.corner_radius is not None
    sharp = {k: v for k, v in BUNDLED["60AR50"].items() if k != "Corner Radius"}
    assert (
        endmill.render(BUNDLED["60AR50"], tmp_path / "a.png").read_bytes()
        != endmill.render(sharp, tmp_path / "b.png").read_bytes()
    )
    with pytest.raises(endmill.ImpossibleGeometryError):
        endmill.geometry_from_record({**BUNDLED["52BN29"], "Corner Radius": '1/32"'})
    with pytest.raises(endmill.ImpossibleGeometryError):
        endmill.geometry_from_record({**BUNDLED["60AR50"], "Corner Radius": "9.00mm"})


def test_the_flute_pitch_is_the_helix_lead_divided_by_the_flute_count():
    geom = endmill.geometry_from_record(REC)
    lead = math.pi * (9 / 32) / math.tan(math.radians(45))
    assert geom.helix_lead == pytest.approx(lead)
    assert geom.axial_flute_pitch == pytest.approx(lead / 4)
    # Half a turn is what the visible face shows, so one flute rises half a
    # lead across it. Drawing d/tan(h) instead -- which is what this did --
    # is short by pi/2 and renders a 30 degree helix at 42.2 degrees.
    assert geom.face_rise == pytest.approx(lead / 2)
    # Both inputs move it, which is why the flutes are not decoration.
    slower = endmill.geometry_from_record({**REC, "Helix Angle": "60 Degrees"})
    fewer = endmill.geometry_from_record({**REC, "Number of Flutes": "2"})
    assert slower.axial_flute_pitch < geom.axial_flute_pitch
    assert fewer.axial_flute_pitch > geom.axial_flute_pitch


@pytest.mark.parametrize(
    "attribute",
    [
        "Milling Dia.",
        "Shank Dia.",
        "Length of Cut",
        "Overall Length",
        "Number of Flutes",
        "Helix Angle",
    ],
)
def test_a_missing_attribute_raises_instead_of_being_assumed(attribute):
    record = {k: v for k, v in REC.items() if k != attribute}
    with pytest.raises(endmill.MissingAttributeError):
        endmill.geometry_from_record(record)


@pytest.mark.parametrize("bad", ['1/0"', "banana", "", "3/8"])
def test_an_unreadable_value_raises_at_render_time(bad, tmp_path):
    with pytest.raises(DimensionParseError):
        endmill.render({**REC, "Milling Dia.": bad}, tmp_path / "x.png", CARD)


@pytest.mark.parametrize(("loc", "oal"), [('3-3/8"', '3-3/8"'), ('4"', '3-3/8"')])
def test_a_cut_longer_than_the_tool_is_refused(loc, oal, tmp_path):
    # This record is internally impossible. Drawing it would mean inventing a
    # tool that the catalog does not describe, so the renderer refuses.
    with pytest.raises(endmill.ImpossibleGeometryError):
        endmill.render(
            {**REC, "Length of Cut": loc, "Overall Length": oal}, tmp_path / "x.png", CARD
        )


def test_equal_diameters_still_draw_a_flute_boundary():
    """52BN29 publishes the same value for both diameters -- a real collision.

    It must not render as a featureless bar: the length-of-cut boundary is a
    real feature of the tool and stays visible when the step does not.
    """
    geom = endmill.geometry_from_record(BUNDLED["52BN29"])
    assert geom.cut_d.inches == geom.shank_d.inches
    fig, ax, _ = endmill.build(BUNDLED["52BN29"], CARD)
    rows = _flute_rows(fig, ax)
    assert rows.size, "no flutes drawn on the cutting portion"


def _flute_rows(fig, ax):
    """Rows carrying flute hatching, inside the elevation axes only.

    The detail profile draws the end view in the same flute color in its own
    axes; counting those would make this test pass for the wrong reason.
    """
    image = figure_pixels(fig)
    mask = color_mask(image, FLUTE) & within_axes(fig, ax, image.shape[:2])
    return np.nonzero(mask.any(axis=1))[0]


@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_the_flutes_stop_at_the_shoulder(profile):
    """Hatching is clipped to the cutting portion.

    Flutes running on into the shank is what the landscape prototype did, and
    it draws a tool that cannot exist: the shank is the plain ground cylinder
    the holder grips.
    """
    geom = endmill.geometry_from_record(REC)
    fig, ax, _ = endmill.build(REC, profile)
    rows = _flute_rows(fig, ax)
    assert rows.size, "no flutes drawn at all"

    shoulder_y = -geom.oal.inches / 2 + geom.loc.inches
    shoulder_row = rows_from_top(fig, ax, shoulder_y)
    assert rows.min() >= shoulder_row - 1.5, (
        "flute hatching reaches above the shoulder, into the shank"
    )

    tip_row = rows_from_top(fig, ax, -geom.oal.inches / 2)
    assert rows.max() <= tip_row + 1.5, "flute hatching reaches below the cutting tip"


@pytest.mark.parametrize("sku", DIMENSIONED_SKUS)
def test_each_diameter_label_sits_against_the_feature_it_measures(sku):
    """The milling callout is on the cutting portion, the shank callout on the shank.

    Two labels that measure different features of the same tool are the whole
    point of the drawing; swapping them would still produce a picture that
    changed when the data changed, so nothing else in the suite would notice.
    """
    record = BUNDLED[sku]
    fig, ax, geom = endmill.build(record, CARD)
    shoulder = -geom.oal.inches / 2 + geom.loc.inches
    milling = [t for t in ax.texts if t.get_text().strip() == "milling"]
    shank = [t for t in ax.texts if t.get_text().strip() == "shank"]
    assert len(milling) == len(shank) == 1
    assert milling[0].get_position()[1] < shoulder < shank[0].get_position()[1]

    # 33TN24 publishes the same string for both roles, so the two callouts are
    # collected per label: one of them still has to sit on each feature.
    values: dict[str, list[float]] = {}
    for text in ax.texts:
        if text.get_text().startswith("Ø"):
            values.setdefault(text.get_text(), []).append(text.get_position()[1])
    assert min(values[f"Ø{geom.cut_d.display()}"]) < shoulder
    assert max(values[f"Ø{geom.shank_d.display()}"]) > shoulder


@pytest.mark.parametrize("sku", DIMENSIONED_SKUS)
def test_each_diameter_arrow_spans_the_diameter_it_measures(sku):
    """Measured off the pixels: the two arrows differ by the two diameters' difference.

    Both arrows overhang the silhouette by the same amount, so the overhang
    cancels and what is left is the thing the drawing claims.
    """
    record = BUNDLED[sku]
    fig, ax, geom = endmill.build(record, CARD)
    image = figure_pixels(fig)
    mask = color_mask(image, DIM, tol=0.08) & within_axes(fig, ax, image.shape[:2])
    runs = longest_row_runs(mask)
    shoulder_row = int(rows_from_top(fig, ax, -geom.oal.inches / 2 + geom.loc.inches))

    shank_arrow = runs[:shoulder_row].max()
    milling_arrow = runs[shoulder_row:].max()
    expected = (geom.shank_d.inches - geom.cut_d.inches) * pixels_per_inch(ax)
    assert shank_arrow - milling_arrow == pytest.approx(expected, abs=3.0)


@pytest.mark.parametrize("helix", ["30 Degrees", "45 Degrees"])
def test_the_flute_slope_is_the_helix_angle(helix):
    """Each flute line rises half a lead across the cutting diameter.

    The visible face is HALF A TURN of the helix -- the flute enters at one
    silhouette edge and leaves at the other -- so the rise between those two
    points is ``lead / 2``, not the ``d / tan(h)`` that unrolling the diameter
    rather than the circumference gives. This asserted the second of those
    until it was worked through: short by pi/2, which draws a published 30
    degree helix at 42.2 degrees, and a test written from the code agreed with
    it. The relation below is derived from the helix, not from the drawing.
    """
    record = {**REC, "Helix Angle": helix}
    fig, ax, geom = endmill.build(record, CARD)
    flutes = [line for line in ax.lines if line.get_color() == FLUTE]
    assert flutes, "no flute lines drawn"
    expected = math.pi * geom.cut_d.inches / math.tan(math.radians(geom.helix_deg)) / 2
    for line in flutes:
        xs, ys = line.get_data()
        run, rise = xs[1] - xs[0], ys[1] - ys[0]
        assert run == pytest.approx(geom.cut_d.inches)
        assert rise == pytest.approx(expected)


def test_an_end_mill_that_does_not_say_which_end_it_has_is_refused(tmp_path):
    """The four observed reference end mills are exactly this case.

    They were transcribed for their dimensions and carry no ``End Mill Style``,
    so they get the type drawing rather than a square end nothing asserts.
    """
    for sku in ("4LU10", "438D34", "33TN24", "35AM34"):
        assert "End Mill Style" not in FIXTURES[sku]
        with pytest.raises(endmill.MissingAttributeError):
            endmill.geometry_from_record(FIXTURES[sku])


@pytest.mark.parametrize("sku", DIMENSIONED_SKUS)
def test_the_tool_is_scaled_from_its_own_length(sku):
    """The silhouette fills the same share of the card whatever the tool measures.

    A frame sized from anything other than this tool -- a constant, or another
    record's length -- still produces a drawing that changes when the data
    changes, and would pass every other test here while drawing a 6" tool off
    the bottom of the card.
    """
    from synthetic_ecommerce_data.domains.industrial.render.endmill import FILL_V

    fig, _ax, _geom = endmill.build(BUNDLED[sku], CARD)
    image = figure_pixels(fig)
    rows = np.nonzero(color_mask(image, INK, tol=0.15).any(axis=1))[0]
    assert rows.size
    assert (rows.max() - rows.min()) / image.shape[0] == pytest.approx(FILL_V, abs=0.02)


@pytest.mark.parametrize("sku", DIMENSIONED_SKUS)
def test_the_silhouette_is_drawn_to_the_published_diameters(sku):
    """The body itself measures what the callouts say, not just the arrows.

    A silhouette drawn at some other width still moves when the record moves,
    so the byte comparisons would not notice -- and the drawing would be
    showing a tool whose proportions contradict its own dimension labels.
    """
    from synthetic_ecommerce_data.domains.industrial.render.canvas import LW_BODY

    fig, ax, geom = endmill.build(BUNDLED[sku], CARD)
    image = figure_pixels(fig)
    black = color_mask(image, INK, tol=0.15)
    scale = pixels_per_inch(ax)
    stroke = LW_BODY * CARD.dpi / 72  # the outline straddles the edge
    y_tip = -geom.oal.inches / 2

    for y, diameter in (
        (y_tip + geom.loc.inches * 0.33, geom.cut_d.inches),
        (y_tip + geom.loc.inches + (geom.oal.inches - geom.loc.inches) * 0.5, geom.shank_d.inches),
    ):
        columns = np.nonzero(black[int(rows_from_top(fig, ax, y))])[0]
        assert columns.size, "no silhouette on this row"
        measured = columns.max() - columns.min() + 1
        assert measured == pytest.approx(diameter * scale + stroke, abs=2.0)
