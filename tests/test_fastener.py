from __future__ import annotations

import numpy as np
import pytest

from synthetic_industrial_products.records import FIXTURES
from synthetic_industrial_products.render import CARD, fastener

REC = FIXTURES["26LD37"]


def test_the_geometry_is_read_off_the_record():
    geom = fastener.geometry_from_record(REC)
    assert geom.thread.designation == "#10-32"
    assert geom.thread.major.inches == pytest.approx(0.190)
    assert geom.head_dia.inches == 0.411
    assert geom.head_height.inches == 0.127
    assert geom.drive_size is not None
    assert geom.drive_size.inches == 0.125


def test_a_countersunk_length_is_measured_over_the_head():
    # ASME measures a flat head screw's length to the top of the head, so the
    # shank is shorter than the published length by the head height.
    geom = fastener.geometry_from_record(REC)
    assert geom.countersunk
    assert geom.total_height == pytest.approx(0.5)
    assert geom.shank_length == pytest.approx(0.5 - 0.127)


def test_a_non_countersunk_length_is_measured_under_the_head():
    geom = fastener.geometry_from_record({**REC, "Screw Head Type": "Socket"})
    assert not geom.countersunk
    assert geom.total_height == pytest.approx(0.5 + 0.127)


def test_the_countersink_angle_falls_out_of_the_published_dimensions():
    """82 degrees included, from head diameter, head height and thread size.

    Nothing supplies that angle -- it is arithmetic on three published values,
    and it lands on the inch flat-head standard. If a record's own numbers
    implied a different cone, the drawing would show that cone.
    """
    geom = fastener.geometry_from_record(REC)
    assert geom.countersink_included_angle == pytest.approx(82.0, abs=0.5)

    steeper = fastener.geometry_from_record({**REC, "Head Height": "0.090 in"})
    assert steeper.countersink_included_angle > geom.countersink_included_angle


def test_a_cylindrical_head_has_no_cone_angle():
    geom = fastener.geometry_from_record({**REC, "Screw Head Type": "Socket"})
    with pytest.raises(fastener.UnsupportedHeadError):
        geom.countersink_included_angle  # noqa: B018


def test_a_head_style_whose_profile_is_not_implied_is_refused():
    # A button head is a dome. Head diameter and head height do not give its
    # radius, and inventing one would be the only line in the drawing that the
    # record could not defend.
    with pytest.raises(fastener.UnsupportedHeadError):
        fastener.geometry_from_record({**REC, "Screw Head Type": "Button"})


def test_a_fully_threaded_countersunk_screw_threads_up_to_the_head():
    geom = fastener.geometry_from_record(REC)
    assert geom.thread_length.inches == 0.5
    assert geom.threaded_length == pytest.approx(geom.shank_length)


def test_a_partial_thread_is_drawn_at_its_published_length():
    geom = fastener.geometry_from_record({**REC, "Thread Length": "1/4 in"})
    assert geom.threaded_length == pytest.approx(0.25)


@pytest.mark.parametrize(
    "attribute",
    ["Screw Head Type", "Dia./Thread Size", "Length", "Thread Length", "Head Dia.", "Head Height"],
)
def test_a_missing_attribute_raises_instead_of_being_assumed(attribute):
    record = {k: v for k, v in REC.items() if k != attribute}
    with pytest.raises((fastener.MissingAttributeError, fastener.UnsupportedHeadError)):
        fastener.geometry_from_record(record)


def test_a_hex_socket_is_drawn_across_its_published_flats():
    geom = fastener.geometry_from_record(REC)
    outline = fastener.drive_outline(geom)
    assert outline is not None
    assert len(outline) == 6
    points = np.array(outline)
    across_flats = points[:, 0].max() - points[:, 0].min()
    assert across_flats == pytest.approx(0.125)
    assert fastener.drive_mouth_width(geom) == pytest.approx(0.125)


def test_a_square_socket_is_drawn_across_its_published_flats():
    geom = fastener.geometry_from_record({**REC, "Drive Type": "Square Socket"})
    outline = fastener.drive_outline(geom)
    assert outline is not None and len(outline) == 4
    points = np.array(outline)
    assert points[:, 0].max() - points[:, 0].min() == pytest.approx(0.125)


@pytest.mark.parametrize("drive", ["Torx", "Phillips", "Cross Recess"])
def test_a_lobed_drive_is_not_drawn_rather_than_guessed(drive):
    """One across-size does not determine a Torx or a Phillips.

    Those shapes are not derivable from anything the record publishes, so the
    drawing leaves the recess out -- and leaves the head's top face unbroken --
    instead of showing a shape that would merely look plausible.
    """
    geom = fastener.geometry_from_record({**REC, "Drive Type": drive})
    assert fastener.drive_outline(geom) is None
    assert fastener.drive_mouth_width(geom) is None


def test_a_drive_with_no_published_size_is_not_drawn():
    record = {k: v for k, v in REC.items() if k != "Drive Size"}
    geom = fastener.geometry_from_record(record)
    assert geom.drive_size is None
    assert fastener.drive_outline(geom) is None


def test_the_thread_form_comes_from_the_designation(tmp_path):
    geom = fastener.geometry_from_record(REC)
    coarse = fastener.geometry_from_record({**REC, "Dia./Thread Size": "#10-24"})
    assert coarse.thread.pitch_in > geom.thread.pitch_in
    assert coarse.thread.minor_in < geom.thread.minor_in
    # and the coarser thread reaches the drawing
    fine_png = fastener.render(REC, tmp_path / "fine.png", CARD).read_bytes()
    coarse_png = fastener.render(
        {**REC, "Dia./Thread Size": "#10-24"}, tmp_path / "coarse.png", CARD
    ).read_bytes()
    assert fine_png != coarse_png


def test_the_screw_is_scaled_from_its_own_head_diameter():
    """A squat part fills the card's width; the frame follows the part, not a constant."""
    from helpers import colour_mask, figure_pixels
    from synthetic_industrial_products.render.canvas import INK
    from synthetic_industrial_products.render.fastener import FILL_H

    fig, _ax, _geom = fastener.build(REC, CARD)
    image = figure_pixels(fig)
    columns = np.nonzero(colour_mask(image, INK, tol=0.15).any(axis=0))[0]
    assert columns.size
    assert (columns.max() - columns.min()) / image.shape[1] == pytest.approx(FILL_H, abs=0.02)
