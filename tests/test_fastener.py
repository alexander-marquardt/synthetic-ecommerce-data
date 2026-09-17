from __future__ import annotations

import numpy as np
import pytest

from helpers import colour_mask, figure_pixels, within_axes
from synthetic_industrial_products.dimensions import parse_length
from synthetic_industrial_products.records import FIXTURES
from synthetic_industrial_products.render import CARD, DETAIL, fastener
from synthetic_industrial_products.render import canvas as cv

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
    # A twelve-point head is a lobed shape. One head diameter does not give
    # the across-flats it alternates with, and inventing one would be the only
    # line in the drawing the record could not defend -- the same reason a
    # Torx recess is left out rather than approximated.
    with pytest.raises(fastener.UnsupportedHeadError):
        fastener.geometry_from_record({**REC, "Screw Head Type": "Twelve Point"})


def test_a_button_head_is_the_dome_its_two_published_dimensions_describe():
    """A chord and a rise determine exactly one arc, so the dome is derived.

    This test replaced one asserting the opposite -- that a button head could
    not be built from ``Head Dia.`` and ``Head Height`` -- which was wrong:
    the sphere through a head's rim and its crown is unique, and its radius is
    ``(r**2 + h**2) / 2h``. Refusing the style meant a real fastener the
    customer asks for by name had no drawing and, before that, no record.
    """
    geom = fastener.geometry_from_record({**REC, "Screw Head Type": "Button"})
    assert geom.domed
    assert not geom.countersunk and not geom.hex_headed

    seat, rise = 0.0, geom.head_height.inches
    r_head = geom.head_dia.inches / 2
    arc = np.array(fastener.dome_profile(r_head, rise, seat))
    # It passes through the rim at both ends and the crown in the middle.
    assert arc[0] == pytest.approx([-r_head, seat], abs=1e-9)
    assert arc[-1] == pytest.approx([r_head, seat], abs=1e-9)
    assert arc[:, 1].max() == pytest.approx(seat + rise, abs=1e-9)
    # And it is an arc rather than the chord: every interior point is above
    # the seat, and the crown is the top.
    assert (arc[1:-1, 1] > seat).all()
    assert arc[len(arc) // 2][0] == pytest.approx(0.0, abs=1e-9)


def test_a_button_heads_length_is_measured_under_its_head():
    """It sits proud of the work, so it is not a countersunk length."""
    geom = fastener.geometry_from_record({**REC, "Screw Head Type": "Button"})
    assert geom.total_height == pytest.approx(0.5 + 0.127)
    assert geom.length_seat == pytest.approx(0.5)


def test_a_low_head_is_a_cylinder_drawn_to_its_own_two_dimensions():
    """No head OUTLINE of its own, and that is the point.

    A low head socket cap screw differs from a full socket head in its
    published head height and (barely) its head diameter, so a drawing built
    from those already shows the squat head DIN 7984 describes. A separate
    silhouette invented to make the two look different would be asserting
    something no attribute says.
    """
    low = fastener.geometry_from_record(
        {**REC, "Screw Head Type": "Low Socket", "Head Height": "0.070 in"}
    )
    assert not low.domed and not low.countersunk and not low.hex_headed
    full = fastener.geometry_from_record({**REC, "Screw Head Type": "Socket"})
    assert low.total_height < full.total_height


@pytest.mark.parametrize(
    ("style", "extra"),
    [
        ("Socket", {}),
        ("Flat", {}),
        ("Button", {}),
        ("Low Socket", {"Head Height": "0.070 in"}),
        ("Hex", {"Width Across Flats": "0.500 in"}),
    ],
)
def test_each_head_style_draws_its_own_picture(style, extra, tmp_path):
    """Measured on the CARD, which carries no attribute table at all.

    The card is the silhouette, the two callouts and the SKU -- so two cards
    that differ differ in the drawing. That matters here because the style is
    the attribute whose last defect was exactly this: ``Socket`` and ``Hex``
    produced the same picture, and 524 hex bolts were drawn with round heads.
    """
    drawn = {}
    for other, other_extra in (
        ("Socket", {}),
        ("Flat", {}),
        ("Button", {}),
        ("Low Socket", {"Head Height": "0.070 in"}),
        ("Hex", {"Width Across Flats": "0.500 in"}),
    ):
        record = {**REC, "Screw Head Type": other, **other_extra}
        drawn[other] = fastener.render(record, tmp_path / f"{other}.png", CARD).read_bytes()
    mine = drawn.pop(style)
    assert mine not in drawn.values(), (
        f"a {style} head card is byte for byte another style's: "
        f"{[k for k, v in drawn.items() if v == mine]}"
    )


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


def _end_view_head(record: dict) -> str:
    """"hexagon" or "circle": what the head is drawn as in the end view."""
    from matplotlib.patches import Circle, Polygon

    fig, _ax, geom = fastener.build(record, DETAIL)
    end_axes = fig.axes[1]
    for patch in end_axes.patches:
        if isinstance(patch, Polygon):
            # The drive recess is a polygon too; the head is the big one.
            corners = patch.get_xy()
            width = corners[:, 0].max() - corners[:, 0].min()
            if width > geom.across_flats * 0.9:
                return "hexagon" if len(set(map(tuple, corners))) == 6 else "polygon"
        if isinstance(patch, Circle) and patch.get_radius() == pytest.approx(
            geom.head_dia.inches / 2
        ):
            return "circle"
    return "nothing"


def test_the_length_dimension_spans_the_published_length_and_not_more():
    """A countersunk length is measured over the head; every other under it.

    ``total_height`` had always known that and the dimension LINE had not: it
    ran tip to top on both styles, so a socket cap screw's drawing put the
    label "1/2 in" against a span of one half inch PLUS the head height. The
    attribute-coverage sweep is what surfaced it, by way of Screw Head Type
    moving nothing.
    """
    countersunk = fastener.geometry_from_record(REC)
    assert countersunk.countersunk
    assert countersunk.length_seat == pytest.approx(countersunk.total_height)

    cylindrical = fastener.geometry_from_record({**REC, "Screw Head Type": "Socket"})
    assert cylindrical.length_seat == pytest.approx(cylindrical.length.inches)
    assert cylindrical.length_seat < cylindrical.total_height
    assert cylindrical.total_height - cylindrical.length_seat == pytest.approx(
        cylindrical.head_height.inches
    )


def test_a_hex_head_is_drawn_hexagonal_and_a_socket_head_round(tmp_path):
    """The end view is the only place the two differ, and it is the place that
    tells a shopper which spanner to reach for."""
    hex_record = {**REC, "Screw Head Type": "Hex", "Width Across Flats": "0.500 in"}
    assert fastener.geometry_from_record(hex_record).hex_headed
    assert not fastener.geometry_from_record(REC).hex_headed
    assert fastener.geometry_from_record(hex_record).across_flats == pytest.approx(0.5)

    hexagonal = fastener.render(hex_record, tmp_path / "a.png", DETAIL).read_bytes()
    round_head = fastener.render(
        {**REC, "Screw Head Type": "Socket"}, tmp_path / "b.png", DETAIL
    ).read_bytes()
    assert hexagonal != round_head

    # Measured on the SHAPE in the end view, not on the file. Two whole
    # drawings differ for a dozen reasons -- the label under the end view says
    # "hex head", the elevation gains its two face edges -- so comparing files
    # would go on passing with a round head in the end view, which is the thing
    # the shopper reads to know which spanner to reach for.
    assert _end_view_head(hex_record) == "hexagon"
    assert _end_view_head({**REC, "Screw Head Type": "Socket"}) == "circle"
    assert _end_view_head(REC) == "circle"


def test_a_hex_head_falls_back_to_head_dia_when_across_flats_is_not_published():
    """Which for a hex head IS the across-flats dimension, and is what the
    elevation is already drawn to."""
    geom = fastener.geometry_from_record({**REC, "Screw Head Type": "Hex"})
    assert geom.across_flats == pytest.approx(geom.head_dia.inches)


# --- Length Under Head, which is a DRAWN dimension and not only a table row --
#
# The distinction matters and is the reason these tests measure the elevation
# rather than the sheet. A value printed in the attribute table makes no claim
# the drawing could contradict -- it is the record's own text, set beside the
# record. A dimension LINE claims that this span of this picture is that value,
# so it is the half that can go wrong silently, and the half issue #10 is about:
# three channels there can be broken with the whole suite green because the
# stamp answers for them.

#: The record with the attribute added, which the bundled reference records
#: predate. 1/2" over the head less a 0.127" head leaves 0.373" under it.
REC_UNDER_HEAD = {**REC, "Length Under Head": "0.3730 in"}


def _elevation_dimension_spans(record: dict, profile=DETAIL) -> list[float]:
    """Every vertical dimension line on the elevation, in inches.

    Read off the arrows actually added to the DRAWING's axes -- the same
    artists that get rasterised -- rather than off the figure's text, which is
    where the attribute table lives. A span measured in pixels instead cannot
    be separated from the diameter callouts' labels, which are set in the same
    colour and cross the same columns.
    """
    _fig, ax, _geom = fastener.build(record, profile)
    spans = []
    for text in ax.texts:
        arrow = getattr(text, "arrow_patch", None)
        if arrow is None:
            continue
        (x0, y0), (x1, y1) = text.xyann, text.xy
        if abs(x0 - x1) < 1e-9:
            spans.append(abs(y1 - y0))
    return sorted(spans)


def _dimension_ink(record: dict, profile=DETAIL) -> int:
    """Pixels of the dimension colour inside the elevation's own axes box."""
    fig, ax, _geom = fastener.build(record, profile)
    image = figure_pixels(fig)
    return int((colour_mask(image, cv.DIM, tol=0.10) & within_axes(fig, ax, image.shape[:2])).sum())


def test_the_length_under_head_dimension_spans_the_value_the_record_publishes():
    """Not the total height, not the length, not the thread run.

    Those are the three spans already on the page and every one of them is
    wrong for this label: on this countersunk screw the published length is a
    head height longer, the total height is the same again, and the thread run
    is whatever the record says it is.
    """
    published = parse_length(REC_UNDER_HEAD["Length Under Head"]).inches
    spans = _elevation_dimension_spans(REC_UNDER_HEAD)
    assert any(span == pytest.approx(published, abs=1e-6) for span in spans), spans

    geom = fastener.geometry_from_record(REC_UNDER_HEAD)
    assert published != pytest.approx(geom.total_height)
    assert published != pytest.approx(geom.length.inches)


def test_the_three_published_lengths_are_three_spans_on_the_elevation():
    """A countersunk screw is where they come apart, so it is where it is checked."""
    geom = fastener.geometry_from_record(REC_UNDER_HEAD)
    assert geom.countersunk
    assert geom.length_under_head is not None
    assert _elevation_dimension_spans(REC_UNDER_HEAD) == pytest.approx(
        sorted([geom.length.inches, geom.length_under_head.inches, geom.threaded_length])
    )


def test_a_record_that_does_not_publish_it_gets_no_such_dimension():
    """Silence draws nothing rather than a span computed from the neighbours.

    The drawing may only contain numbers the record contains, and the shank
    the other attributes leave is not one the record published.
    """
    assert "Length Under Head" not in REC
    assert fastener.geometry_from_record(REC).length_under_head is None
    assert (
        len(_elevation_dimension_spans(REC)) == len(_elevation_dimension_spans(REC_UNDER_HEAD)) - 1
    )


def test_the_dimension_is_inked_in_the_drawing_and_not_only_in_the_table():
    """The control for the span test above: an arrow that draws nothing would pass it."""
    assert _dimension_ink(REC_UNDER_HEAD) > _dimension_ink(REC) + 500


@pytest.mark.parametrize("published", ["1/2 in", "0.2000 in"])
def test_a_length_under_head_the_other_lengths_contradict_is_refused(published):
    """Both directions: too long for the shank, and too short for it.

    A record whose own numbers disagree is refused rather than drawn to one of
    them, because a drawing that picked a winner would be a picture saying the
    record is something it is not -- and the defect would then look corroborated.
    """
    with pytest.raises(fastener.ImpossibleGeometryError):
        fastener.geometry_from_record({**REC, "Length Under Head": published})


def test_the_refusal_leaves_room_for_the_rounding_the_catalog_publishes():
    """A tolerance that refused consistent records would empty the catalog.

    The published strings are exact to four decimal inches or two decimal
    millimetres, so a consistent record's three lengths agree far inside the
    tolerance -- and one unit out of that last place must not be a refusal.
    """
    fastener.geometry_from_record({**REC, "Length Under Head": "0.3731 in"})
    fastener.geometry_from_record({**REC, "Length Under Head": "9.47 mm"})
    assert fastener.UNDER_HEAD_TOLERANCE_IN < 0.127, (
        "a tolerance as wide as this screw's head height would accept a length "
        "under head that was really the length over it"
    )
