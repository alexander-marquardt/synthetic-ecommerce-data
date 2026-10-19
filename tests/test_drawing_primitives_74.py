"""The drawing primitives (#74): a sibling type's figure is composed from shared parts.

Four promises:

* each primitive draws the part it is named for, to the dimensions it is given;
* a figure is declared as primitives plus parameters (``compose.Spec``), and a
  spec that names no such primitive is refused when it is checked;
* the figures that moved onto the primitives (a screw or bolt, a drill) draw the
  same SVG bytes as before;
* a new figure composed from primitives alone scales with the record's own
  published dimensions (the planted proof), and says so when it falls back.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from drawing_pins import pin_digests
from synthetic_ecommerce_data.core.drawing.model import ROLES, Disc, Dots, Figure, Lines, Poly
from synthetic_ecommerce_data.domains.industrial.drawing import compose, figures, primitives
from synthetic_ecommerce_data.domains.industrial.drawing.compose import (
    CompositionError,
    Dim,
    Ref,
    Spec,
    part,
)

REPO = Path(__file__).resolve().parents[1]

# --- helpers -----------------------------------------------------------------------


def polys(fig: Figure, role: str | None = None) -> list[Poly]:
    return [s for s in fig.shapes if isinstance(s, Poly) and role in (None, s.role)]


def discs(fig: Figure, role: str | None = None) -> list[Disc]:
    return [s for s in fig.shapes if isinstance(s, Disc) and role in (None, s.role)]


def strokes(fig: Figure) -> int:
    return sum(len(s.segments) for s in fig.shapes if isinstance(s, Lines))


def box(shape: Poly) -> tuple[float, float, float, float]:
    xs = [p[0] for p in shape.points]
    ys = [p[1] for p in shape.points]
    return min(xs), min(ys), max(xs), max(ys)


def fresh() -> Figure:
    return Figure()


def exactly(items: list, n: int, what: str = "shape") -> list:
    """The items, once there are n of them: a missing shape fails an assertion."""
    assert len(items) == n, f"expected {n} {what}(s), drew {len(items)}"
    return items


def only(items: list, what: str = "shape"):
    return exactly(items, 1, what)[0]


def first(items: list, what: str = "shape"):
    assert items, f"expected at least one {what}, drew none"
    return items[0]


def bounds(fig: Figure) -> tuple[float, float, float, float]:
    assert fig.shapes, "the figure is empty: nothing was drawn"
    return fig.bounds()


# --- the primitives ------------------------------------------------------------------


def test_every_primitive_is_listed_and_named():
    """``compose.PRIMITIVES`` is the public set of ``primitives``: nothing is left out."""
    public = {
        n
        for n, f in vars(primitives).items()
        if callable(f)
        and getattr(f, "__module__", "") == primitives.__name__
        and n[0] != "_"
        and n != "thread_crests"  # a helper that returns the strokes, it draws nothing
    }
    assert set(compose.PRIMITIVES) == public
    for needed in (
        "thread",
        "head_hex",
        "head_socket",
        "head_button",
        "head_flat",
        "head_pan",
        "drive_recess",
        "helix_flutes",
        "shank",
        "hex_body",
        "round_body",
        "ring",
        "tube",
        "plate",
        "chamfer",
    ):
        assert needed in compose.PRIMITIVES


#: One call of every primitive: ``(name, args after the figure)``.
CALLS = {
    "shank": dict(r=0.1, y0=0.0, y1=1.0),
    "round_body": dict(dia=0.2, y0=0.0, y1=1.0),
    "hex_body": dict(across_flats=0.3, y0=0.0, y1=0.2),
    "chamfer": dict(r=0.1, y0=0.0, y1=1.0, length=0.05),
    "thread": dict(r=0.1, y0=0.2, y1=1.0, pitch=0.05, chamfer_length=0.05),
    "break_mark": dict(r=0.1, y=0.5, amplitude=0.01),
    "conical_end": dict(r=0.1, y0=0.0, y_shoulder=0.8, y_tip=1.0),
    "head_flat": dict(head_d=0.4, shank_r=0.1, height=0.1),
    "head_button": dict(head_d=0.4, height=0.1),
    "head_pan": dict(head_d=0.4, height=0.2),
    "head_socket": dict(head_d=0.4, height=0.2),
    "head_hex": dict(across_flats=0.4, height=0.2),
    "round_face": dict(centre=(1.0, 0.2), radius=0.2),
    "hex_face": dict(centre=(1.0, 0.2), corner_radius=0.2),
    "drive_recess": dict(centre=(1.0, 0.2), key=0.1),
    "helix_flutes": dict(dia=0.5, y0=0.0, y1=2.0, flutes=4, helix_deg=30.0),
    "flute_end_view": dict(centre=(1.0, 0.2), radius=0.25, flutes=4),
    "ring": dict(centre=(0.0, 0.0), r_out=0.5, r_in=0.2),
    "tube": dict(r_out=0.5, y0=0.0, y1=1.0, r_in=0.4),
    "plate": dict(x0=0.0, y0=0.0, x1=2.0, y1=1.0, holes=(((0.5, 0.5), 0.1),)),
}


def test_the_calls_table_covers_every_primitive():
    assert set(CALLS) == set(compose.PRIMITIVES)


@pytest.mark.parametrize("name", sorted(CALLS))
def test_a_primitive_adds_shapes_with_known_roles(name):
    fig = fresh()
    assert name in compose.PRIMITIVES, f"{name} is not registered"
    compose.PRIMITIVES[name](fig, **CALLS[name])
    assert fig.shapes, f"{name} drew nothing"
    for shape in fig.shapes:
        if not isinstance(shape, Dots):
            assert getattr(shape, "role", "part") in ROLES
    x0, y0, x1, y1 = bounds(fig)
    assert all(math.isfinite(v) for v in (x0, y0, x1, y1))


def test_shank_is_a_plain_rectangle_of_its_radius_and_length():
    fig = fresh()
    primitives.shank(fig, 0.1, 0.5, 2.0)
    shape = only(polys(fig))
    assert shape.role == "plain"
    assert box(shape) == (-0.1, 0.5, 0.1, 2.0)


def test_round_body_is_its_diameter_wide_in_the_part_role():
    fig = fresh()
    primitives.round_body(fig, 0.5, 1.0, 3.0)
    shape = only(polys(fig))
    assert shape.role == "part"
    assert box(shape) == (-0.25, 1.0, 0.25, 3.0)


def test_hex_body_is_as_wide_as_the_corners_with_two_face_lines():
    fig = fresh()
    primitives.hex_body(fig, 0.5, 0.0, 0.3)
    shape = only(polys(fig))
    corners = 0.5 * 2 / math.sqrt(3)
    assert box(shape)[2] - box(shape)[0] == pytest.approx(corners)
    assert strokes(fig) == 2


def test_chamfer_narrows_only_the_far_end_by_the_inset():
    fig = fresh()
    primitives.chamfer(fig, 0.2, 0.0, 1.0, length=0.1, inset=0.05)
    shape = only(polys(fig))
    xs_at_tip = sorted(x for x, y in shape.points if y == 1.0)
    assert xs_at_tip == pytest.approx([-0.15, 0.15])
    xs_at_base = sorted(x for x, y in shape.points if y == 0.0)
    assert xs_at_base == pytest.approx([-0.2, 0.2])
    shoulders = {y for x, y in shape.points if abs(x) == 0.2 and y > 0.0}
    assert sorted(shoulders) == pytest.approx([0.9])


def test_default_chamfer_is_forty_five_degrees():
    fig = fresh()
    primitives.chamfer(fig, 0.2, 0.0, 1.0, length=0.1)
    shape = only(polys(fig))
    assert sorted(x for x, y in shape.points if y == 1.0) == pytest.approx([-0.1, 0.1])


def test_a_finer_pitch_draws_more_crests():
    coarse, fine = fresh(), fresh()
    primitives.thread(coarse, 0.1, 0.0, 1.0, 0.1)
    primitives.thread(fine, 0.1, 0.0, 1.0, 0.05)
    assert strokes(coarse) == 10
    assert strokes(fine) == 20


def test_thread_crests_stop_where_the_chamfer_starts():
    fig = fresh()
    primitives.thread(fig, 0.1, 0.0, 1.0, 0.125, chamfer_length=0.25)
    assert strokes(fig) == 6
    top = max(b[1] for s in fig.shapes if isinstance(s, Lines) for _, b in s.segments)
    assert top <= 0.75


def test_drop_draws_a_section_that_far_toward_the_origin():
    plain, dropped = fresh(), fresh()
    primitives.thread(plain, 0.1, 2.0, 3.0, 0.1, 0.05)
    primitives.thread(dropped, 0.1, 2.0, 3.0, 0.1, 0.05, drop=1.5)
    assert bounds(dropped)[1] == pytest.approx(bounds(plain)[1] - 1.5)
    assert bounds(dropped)[3] == pytest.approx(bounds(plain)[3] - 1.5)


def test_break_mark_is_a_zigzag_of_six_strokes_wider_than_the_shank():
    fig = fresh()
    primitives.break_mark(fig, 0.1, 0.5, 0.01)
    assert strokes(fig) == 6
    x0, _, x1, _ = bounds(fig)
    assert x1 - x0 == pytest.approx(0.23)


def test_conical_end_comes_to_a_point_on_the_axis():
    fig = fresh()
    primitives.conical_end(fig, 0.1, 0.0, 0.8, 1.0)
    shape = only(polys(fig))
    assert (0, 1.0) in shape.points
    assert box(shape) == (-0.1, 0.0, 0.1, 1.0)


def test_flat_head_is_a_cone_from_the_head_to_the_shank():
    fig = fresh()
    primitives.head_flat(fig, 0.4, 0.1, 0.12)
    shape = only(polys(fig))
    top = sorted(x for x, y in shape.points if y == 0.0)
    seat = sorted(x for x, y in shape.points if y == 0.12)
    assert top == pytest.approx([-0.2, 0.2])
    assert seat == pytest.approx([-0.1, 0.1])


def test_button_head_is_a_dome_to_its_rise_and_its_rim():
    fig = fresh()
    primitives.head_button(fig, 0.4, 0.1)
    shape = only(polys(fig))
    x0, y0, x1, y1 = box(shape)
    assert (x0, x1) == pytest.approx((-0.2, 0.2))
    assert (y0, y1) == pytest.approx((0.0, 0.1))
    crown = min(shape.points, key=lambda p: p[1])
    assert crown[0] == pytest.approx(0.0, abs=0.02)


def test_pan_head_has_a_straight_wall_under_a_lower_crown_than_the_button():
    pan, button = fresh(), fresh()
    primitives.head_pan(pan, 0.4, 0.2)
    primitives.head_button(button, 0.4, 0.2)
    p, b = only(polys(pan)), only(polys(button))
    assert box(p) == pytest.approx((-0.2, 0.0, 0.2, 0.2))

    def has_rim_at(shape: Poly, y: float) -> bool:
        return any(abs(abs(px) - 0.2) < 1e-9 and abs(py - y) < 1e-9 for px, py in shape.points)

    crown = primitives.PAN_CROWN * 0.2
    assert has_rim_at(p, crown)
    assert not has_rim_at(b, crown)


def test_socket_head_is_a_rectangle_and_hex_head_a_hex_body():
    socket, hexed = fresh(), fresh()
    primitives.head_socket(socket, 0.4, 0.25, top=1.0)
    primitives.head_hex(hexed, 0.4, 0.25, top=1.0)
    assert box(first(polys(socket))) == (-0.2, 1.0, 0.2, 1.25)
    assert box(first(polys(hexed)))[1:4:2] == (1.0, 1.25)
    assert strokes(hexed) == 2 and strokes(socket) == 0


def test_a_head_sits_with_its_top_at_top():
    low, high = fresh(), fresh()
    primitives.head_button(low, 0.4, 0.1)
    primitives.head_button(high, 0.4, 0.1, top=2.0)
    assert bounds(high)[1] == pytest.approx(bounds(low)[1] + 2.0)


def test_drive_recess_is_a_dark_hex_whose_flats_are_the_key_size():
    fig = fresh()
    primitives.drive_recess(fig, (1.0, 0.5), 0.2)
    shape = only(polys(fig))
    assert shape.role == "dark"
    ys = sorted(y for _, y in shape.points)
    # Corner-up orientation of regular_polygon(..., 30): the flats are the left and right sides.
    xs = sorted(x for x, _ in shape.points)
    assert xs[-1] - xs[0] == pytest.approx(0.2)
    assert len(ys) == 6


def test_round_and_hex_faces_are_centred_where_asked():
    fig = fresh()
    primitives.round_face(fig, (2.0, 3.0), 0.5)
    primitives.hex_face(fig, (2.0, 3.0), 0.5)
    disc = only(discs(fig))
    assert (disc.centre, disc.radius) == ((2.0, 3.0), 0.5)
    hexagon = only(polys(fig))
    cx = sum(x for x, _ in hexagon.points) / 6
    assert cx == pytest.approx(2.0)


def test_a_steeper_helix_draws_more_flute_strokes():
    shallow, steep = fresh(), fresh()
    primitives.helix_flutes(shallow, 0.5, 0.0, 6.0, 4, 20.0)
    primitives.helix_flutes(steep, 0.5, 0.0, 6.0, 4, 45.0)
    assert strokes(steep) > strokes(shallow) > 0


def test_flute_hand_mirrors_the_strokes():
    right, left = fresh(), fresh()
    primitives.helix_flutes(right, 0.5, 0.0, 3.0, 2, 30.0, hand=1)
    primitives.helix_flutes(left, 0.5, 0.0, 3.0, 2, 30.0, hand=-1)
    r = only([s for s in right.shapes if isinstance(s, Lines)])
    l_ = only([s for s in left.shapes if isinstance(s, Lines)])
    assert [((a[0], a[1]), (b[0], b[1])) for a, b in r.segments] == [
        ((-a[0], a[1]), (-b[0], b[1])) for a, b in l_.segments
    ]


def test_flute_end_view_draws_two_strokes_per_flute_in_a_disc():
    fig = fresh()
    primitives.flute_end_view(fig, (1.0, 1.0), 0.3, 3)
    assert len(discs(fig)) == 1
    assert strokes(fig) == 6


def test_ring_is_a_disc_with_a_hole():
    fig = fresh()
    primitives.ring(fig, (0.0, 0.0), 0.5, 0.2)
    assert [(d.role, d.radius) for d in discs(fig)] == [("part", 0.5), ("hole", 0.2)]


def test_tube_is_two_walls_each_as_thick_as_the_wall():
    fig = fresh()
    primitives.tube(fig, 0.5, 0.4, 0.0, 2.0)
    left, right = exactly(polys(fig), 2)
    assert box(left) == (-0.5, 0.0, -0.4, 2.0)
    assert box(right) == (0.4, 0.0, 0.5, 2.0)


def test_plate_has_one_hole_per_hole_given():
    fig = fresh()
    primitives.plate(fig, 0.0, 0.0, 2.0, 1.0, holes=(((0.5, 0.5), 0.1), ((1.5, 0.5), 0.1)))
    assert box(first(polys(fig))) == (0.0, 0.0, 2.0, 1.0)
    assert [d.role for d in discs(fig)] == ["hole", "hole"]


# --- the declarative layer ---------------------------------------------------------


def test_an_expression_is_evaluated_over_named_dimensions():
    values = {"a": 3.0, "b": 2.0}
    assert compose.evaluate(Ref("a") * 2 + Ref("b"), values) == 8.0
    assert compose.evaluate(1 - Ref("b") / 4, values) == 0.5
    assert compose.evaluate(-Ref("a"), values) == -3.0
    assert compose.evaluate("plain", values) == "plain"
    assert compose.evaluate(((Ref("a"), 1), 0.5), values) == ((3.0, 1), 0.5)


def test_a_spec_that_names_no_such_primitive_is_refused():
    bad = Spec(dims=(), parts=(part("sprocket_tooth", r=1.0),), size=1.0)
    with pytest.raises(CompositionError, match="sprocket_tooth"):
        compose.check(bad)


def test_a_spec_that_gives_a_primitive_the_wrong_parameters_is_refused():
    missing = Spec(dims=(), parts=(part("shank", r=1.0, y0=0.0),), size=1.0)
    extra = Spec(dims=(), parts=(part("shank", r=1.0, y0=0.0, y1=1.0, bore=2),), size=1.0)
    for bad in (missing, extra):
        with pytest.raises(CompositionError, match="shank"):
            compose.check(bad)


def test_a_spec_that_refers_to_an_undeclared_dimension_is_refused():
    bad = Spec(dims=(), parts=(part("shank", r=Ref("nope"), y0=0.0, y1=1.0),), size=1.0)
    with pytest.raises(CompositionError, match="nope"):
        compose.check(bad)


def test_a_dimension_may_only_exceed_one_declared_before_it():
    bad = Spec(
        dims=(Dim("od", "Outside Dia.", 1.0, above="bore"), Dim("bore", "Bore Dia.", 0.5)),
        parts=(),
        size=1.0,
    )
    with pytest.raises(CompositionError, match="bore"):
        compose.check(bad)


def test_a_spec_is_plain_data_it_can_be_hashed_and_compared():
    one = Spec(
        dims=(Dim("d", "Dia.", 1.0),),
        parts=(part("ring", centre=(0.0, 0.0), r_out=Ref("d"), r_in=0.1),),
        size=Ref("d"),
    )
    two = Spec(
        dims=(Dim("d", "Dia.", 1.0),),
        parts=(part("ring", centre=(0.0, 0.0), r_out=Ref("d"), r_in=0.1),),
        size=Ref("d"),
    )
    assert one == two and hash(one) == hash(two)


# The planted proof: a figure that exists nowhere in figures.py, composed from the
# primitives and parameters alone.
PAN_SCREW = Spec(
    dims=(
        Dim("major", "Dia./Thread Size", 0.25, reader="thread_major"),
        Dim("pitch", "Dia./Thread Size", Ref("major") * 0.2, reader="thread_pitch"),
        Dim("length", "Length", Ref("major") * 4),
        Dim("head_d", "Head Dia.", Ref("major") * 1.9),
        Dim("head_h", "Head Height", Ref("major") * 0.7),
        Dim("key", "Drive Size", Ref("major") * 0.5),
    ),
    derived=(
        ("end", Ref("head_h") + Ref("length")),
        ("face_x", Ref("head_d") * 1.25),
    ),
    parts=(
        part("head_pan", head_d=Ref("head_d"), height=Ref("head_h")),
        part(
            "thread",
            r=Ref("major") / 2,
            y0=Ref("head_h"),
            y1=Ref("end"),
            pitch=Ref("pitch"),
            chamfer_length=Ref("pitch"),
        ),
        part("round_face", centre=(Ref("face_x"), Ref("head_d") / 2), radius=Ref("head_d") / 2),
        part("drive_recess", centre=(Ref("face_x"), Ref("head_d") / 2), key=Ref("key")),
    ),
    size=Ref("end"),
)

PAN_RECORD = {
    "Dia./Thread Size": "1/4-20",
    "Length": '1"',
    "Head Dia.": '0.4"',
    "Head Height": '0.15"',
    "Drive Size": '0.125"',
}


def draw_pan(**changes: str) -> tuple[Figure, str]:
    return compose.compose(PAN_SCREW, {**PAN_RECORD, **changes})


def test_a_figure_composed_from_primitives_alone_draws_every_part():
    compose.check(PAN_SCREW)
    assert {p.primitive for p in PAN_SCREW.parts} <= set(compose.PRIMITIVES)
    fig, source = draw_pan()
    assert source == "record"
    assert len(polys(fig, "part")) >= 2  # the head and the threaded shank
    assert len(polys(fig, "dark")) == 1  # the drive recess
    assert strokes(fig) > 0  # the thread crests
    assert fig.size_in == pytest.approx(1.15)


def test_the_composed_figure_grows_by_exactly_the_length_published():
    short, _ = draw_pan(Length='1"')
    long, _ = draw_pan(Length='3"')
    assert bounds(long)[3] - bounds(short)[3] == pytest.approx(2.0)
    assert long.size_in - short.size_in == pytest.approx(2.0)
    assert strokes(long) > 2.5 * strokes(short)


def test_the_composed_figure_is_as_wide_as_the_head_published():
    narrow, _ = draw_pan(**{"Head Dia.": '0.4"'})
    wide, _ = draw_pan(**{"Head Dia.": '0.8"'})
    head = lambda fig: box(first(polys(fig)))  # noqa: E731
    assert head(narrow)[2] - head(narrow)[0] == pytest.approx(0.4)
    assert head(wide)[2] - head(wide)[0] == pytest.approx(0.8)


def test_the_composed_figure_is_as_tall_in_the_head_as_published():
    low, _ = draw_pan(**{"Head Height": '0.1"'})
    tall, _ = draw_pan(**{"Head Height": '0.3"'})
    assert box(first(polys(tall)))[3] - box(first(polys(low)))[3] == pytest.approx(0.2)


def test_a_dimension_the_record_omits_takes_a_nominal_proportion_and_says_so():
    full, source_full = draw_pan()
    record = {k: v for k, v in PAN_RECORD.items() if k != "Head Height"}
    fig, source = compose.compose(PAN_SCREW, record)
    assert source_full == "record" and source == "partial"
    # 0.7 of the 1/4" major diameter, not any published height.
    assert box(first(polys(fig)))[3] == pytest.approx(0.7 * 0.25)
    # ... and a published value still wins over the nominal one.
    assert box(first(polys(full)))[3] == pytest.approx(0.15)


def test_a_nominal_proportion_scales_with_the_dimension_it_is_a_proportion_of():
    small = {"Dia./Thread Size": "1/4-20"}
    large = {"Dia./Thread Size": "1/2-13"}
    a, source_a = compose.compose(PAN_SCREW, small)
    b, source_b = compose.compose(PAN_SCREW, large)
    assert source_a == source_b == "partial"
    assert box(first(polys(b)))[3] / box(first(polys(a)))[3] == pytest.approx(2.0)
    assert b.size_in / a.size_in == pytest.approx(2.0)


def test_a_record_with_nothing_readable_is_drawn_nominal():
    fig, source = compose.compose(PAN_SCREW, {})
    assert source == "nominal"
    assert fig.shapes


def test_a_pair_that_contradicts_itself_falls_back_to_the_nominal_value():
    spec = Spec(
        dims=(
            Dim("bore", "Bore Dia.", 0.5),
            Dim("od", "Outside Dia.", Ref("bore") * 2.4, above="bore"),
        ),
        parts=(part("ring", centre=(0.0, 0.0), r_out=Ref("od") / 2, r_in=Ref("bore") / 2),),
        size=Ref("od"),
    )
    ok, source_ok = compose.compose(spec, {"Bore Dia.": '0.5"', "Outside Dia.": '1.5"'})
    bad, source_bad = compose.compose(spec, {"Bore Dia.": '0.5"', "Outside Dia.": '0.4"'})
    assert source_ok == "record" and source_bad == "partial"
    assert ok.size_in == pytest.approx(1.5)
    assert bad.size_in == pytest.approx(1.2)


# --- the figures moved onto the primitives ---------------------------------------------


def test_the_screw_is_composed_of_head_shank_thread_and_end_view_primitives(monkeypatch):
    called: list[str] = []
    for name in compose.PRIMITIVES:
        original = getattr(primitives, name)

        def spy(*args, __name=name, __original=original, **kwargs):
            called.append(__name)
            return __original(*args, **kwargs)

        monkeypatch.setattr(primitives, name, spy)
    record = {
        "Dia./Thread Size": "1/4-20",
        "Length": '1"',
        "Head Type": "Socket",
        "Thread Length": '0.5"',
        "Drive Size": '0.1875"',
    }
    figures.fastener(record)
    assert {"shank", "thread", "drive_recess"} <= set(called)
    assert any(n.startswith("head_") for n in called)


def test_the_drill_is_a_declared_spec_of_registered_primitives():
    spec = getattr(figures, "DRILL_SPEC", None)
    assert isinstance(spec, Spec)
    compose.check(spec)
    assert {p.primitive for p in spec.parts} == {
        "shank",
        "conical_end",
        "helix_flutes",
    }


PINNED = {
    "end_mill_square": "75:19666fdf434d89778780a972c52d170bc15085e624ab62d7eb07446fcdeb305c",
    "end_mill_ball": "44:41777bba8f09eb4a2dff814eb92026118cce904e885a5fb93fe9834f7cd60cfe",
    "drill_jobber": "37:314a201c0d810636d30d6d4e2ce313f227981de767fbd49a352869990f5c4249",
    "tap_spiral_point": "31:a573394f5f232dd76c86ec12176ecf893dcc4bf822ac060fd1578425d57a8b84",
    "screw_flat_head": "23:29052f7315ee8fe1f2d51f79658741b56de5351eed692aeff14f42ab08f51285",
    "screw_button_head": "21:993c2b30ce7bb290a3db9e1c8bb3b311b5eb417f0554df0b61c2e99bf696936a",
    "screw_low_head": "18:19a56605e9d5d9b25ea5335d246c9820908520e15c050012c63f9f3b49387aaf",
    "bolt_hex": "32:4b864dcd6c2b82f8bb044b74914cecc00827fb5d6b309a3b96ba5bfccf716bb9",
    "washer_flat": "25:591f3ece432799789834037f99a33a566f18696896c84025381d6ee6e8ea2649",
    "nut_hex": "65:c5fcf14fd19e4b2fec365984ff6795812217a6a4f94e09a2d51460ce419c56ce",
}


def test_the_moved_figures_draw_the_same_svg_bytes_as_before():
    """Taken from main before the first figure moved: a moved figure is byte-identical."""
    assert pin_digests() == PINNED


# --- the docs ----------------------------------------------------------------------


def test_docs_say_how_to_compose_a_figure_and_name_every_primitive():
    text = (REPO / "docs" / "drawings.md").read_text()
    assert "## Composing a figure from primitives" in text
    missing = [name for name in compose.PRIMITIVES if f"`{name}`" not in text]
    assert not missing, f"docs/drawings.md does not name {missing}"
