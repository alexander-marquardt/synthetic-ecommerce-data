from __future__ import annotations

import math

import numpy as np
import pytest

from helpers import (
    colour_mask,
    figure_pixels,
    longest_row_runs,
    pixels_per_inch,
    rows_from_top,
    within_axes,
)
from synthetic_industrial_products.dimensions import DimensionParseError
from synthetic_industrial_products.records import FIXTURES
from synthetic_industrial_products.render import CARD, DETAIL, endmill
from synthetic_industrial_products.render.canvas import DIM, FLUTE

REC = FIXTURES["4LU10"]


def test_the_geometry_is_read_off_the_record():
    geom = endmill.geometry_from_record(REC)
    assert geom.cut_d.inches == 0.25
    assert geom.shank_d.inches == 0.375
    assert geom.loc.inches == 0.625
    assert geom.oal.inches == 3.375
    assert geom.flutes == 4
    assert geom.helix_deg == 30.0


def test_the_flute_pitch_is_the_helix_lead_divided_by_the_flute_count():
    geom = endmill.geometry_from_record(REC)
    lead = math.pi * 0.25 / math.tan(math.radians(30))
    assert geom.axial_flute_pitch == pytest.approx(lead / 4)
    # Both inputs move it, which is why the flutes are not decoration.
    slower = endmill.geometry_from_record({**REC, "Helix Angle": "45 Degrees"})
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
    """33TN24 publishes the same value for both diameters -- a real collision.

    It must not render as a featureless bar: the length-of-cut boundary is a
    real feature of the tool and stays visible when the step does not.
    """
    geom = endmill.geometry_from_record(FIXTURES["33TN24"])
    assert geom.cut_d.inches == geom.shank_d.inches
    fig, ax, _ = endmill.build(FIXTURES["33TN24"], CARD)
    rows = _flute_rows(fig, ax)
    assert rows.size, "no flutes drawn on the cutting portion"


def _flute_rows(fig, ax):
    """Rows carrying flute hatching, inside the elevation axes only.

    The detail profile draws the end view in the same flute colour in its own
    axes; counting those would make this test pass for the wrong reason.
    """
    image = figure_pixels(fig)
    mask = colour_mask(image, FLUTE) & within_axes(fig, ax, image.shape[:2])
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


@pytest.mark.parametrize("sku", ["4LU10", "438D34", "33TN24", "35AM34"])
def test_each_diameter_label_sits_against_the_feature_it_measures(sku):
    """The milling callout is on the cutting portion, the shank callout on the shank.

    Two labels that measure different features of the same tool are the whole
    point of the drawing; swapping them would still produce a picture that
    changed when the data changed, so nothing else in the suite would notice.
    """
    record = FIXTURES[sku]
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


@pytest.mark.parametrize("sku", ["4LU10", "438D34", "33TN24", "35AM34"])
def test_each_diameter_arrow_spans_the_diameter_it_measures(sku):
    """Measured off the pixels: the two arrows differ by the two diameters' difference.

    Both arrows overhang the silhouette by the same amount, so the overhang
    cancels and what is left is the thing the drawing claims.
    """
    record = FIXTURES[sku]
    fig, ax, geom = endmill.build(record, CARD)
    image = figure_pixels(fig)
    mask = colour_mask(image, DIM, tol=0.08) & within_axes(fig, ax, image.shape[:2])
    runs = longest_row_runs(mask)
    shoulder_row = int(rows_from_top(fig, ax, -geom.oal.inches / 2 + geom.loc.inches))

    shank_arrow = runs[:shoulder_row].max()
    milling_arrow = runs[shoulder_row:].max()
    expected = (geom.shank_d.inches - geom.cut_d.inches) * pixels_per_inch(ax)
    assert shank_arrow - milling_arrow == pytest.approx(expected, abs=3.0)
