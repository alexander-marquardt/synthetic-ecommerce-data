"""Three channels of the catalog's own drawings, each measured on its own (#10).

``tests/test_sku_drawings.py::test_the_committed_catalog_rebuilds_into_its_recorded_drawings``
answers for every channel at once: break any of them and the digests move. That is a
tripwire, not a guard. A republished catalog moves the digests too, so the one test that
notices a channel gone wrong notices it in the same words as a deliberate change, and the
review that follows has nothing to point at. Each channel below is measured from the
figure the SKU's drawing function returns, or from the pattern in the SVG it writes, so a
failure names the channel.

* **The flute count of the end view** is a second drawing of a value the record states.
  An end mill's elevation shows its flutes edge on; the end view is where two flutes are
  visibly two. A page whose title says three beside an end view of four contradicts itself.
* **The hand** a record publishes. The sweep is read off the records the catalog builds,
  not off a list written out here: a type that starts publishing a direction is in the
  sweep the day it does, and a type whose drawing ignores it has to be named.
* **Which hatch belongs to which material.** The table is injective (a test elsewhere
  holds that), which a permutation of its values leaves true. What a permutation breaks
  is the convention the table's comment states: carbide the cross-hatch, powdered metal
  the stipple, the tool steels plain diagonals.

The figure falls back to nominal proportions when the published dimensions cannot be drawn
(a ball nose with a corner radius, a diameter that does not parse). A fallback may take an
extent from the nominal shape, never the flute count or the hand the record publishes, so
the sweeps meet every record the catalog has (not one for each way it was read: the
fallbacks are where a published value was lost) and ``ROUTES`` names each fallback outright.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.drawing import FIGURES, draw_sku
from synthetic_ecommerce_data.core.drawing.model import Disc, Lines
from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, generate

CATALOG = generate(SMALL)

FLUTES = "Number of Flutes"
CUTTING_DIRECTION = "Cutting Direction"
HANDS = ("Left Hand", "Right Hand")

#: The types whose published direction their drawing does not show, each with the attribute.
#: Not a list to grow: a pair here is a published value the picture does not keep. The
#: last test below fails the day one starts drawing it (take it out) and the day a type
#: publishes a direction its drawing ignores (name it, or draw it).
HAND_NOT_DRAWN = frozenset(
    {
        ("bolt_hex", "Thread Direction"),
        ("drill_jobber", CUTTING_DIRECTION),
        ("lock_nuts_nylon_insert", "Thread Direction"),
        ("nut_hex", "Thread Direction"),
        ("screw_button_head", "Thread Direction"),
        ("screw_flat_head", "Thread Direction"),
        ("screw_low_head", "Thread Direction"),
        ("screw_socket_head", "Thread Direction"),
        ("set_screws_hex_socket", "Thread Direction"),
        ("tap_spiral_point", "Thread Direction"),
        ("threaded_rod", "Thread Direction"),
    }
)

#: Each way a published end mill record fails to draw as published, and the type that
#: exposes it (the routes of ``tests/test_end_mill_ends_drawn_9.py``).
BASE = {
    "Milling Dia.": '1/4"',
    "Shank Dia.": '1/4"',
    "Length of Cut": '3/4"',
    "Overall Length": '3"',
    "Number of Flutes": "4",
    "Helix Angle": "30 Degrees",
}
ROUTES = {
    "dimensions that draw as published": ("end_mill_square", {}),
    "two lengths of cut as long as the tool": (
        "end_mill_square",
        {"Length of Cut": '1"', "Overall Length": '1-1/2"'},
    ),
    "a ball nose publishing a corner radius": ("end_mill_ball", {"Corner Radius": '1/64"'}),
    "a diameter that does not parse": ("end_mill_square", {"Milling Dia.": "about a quarter"}),
}


def _records():
    for line, child in CATALOG.all_skus():
        if line.type_key in FIGURES:
            yield line.type_key, emit.drawing_record(CATALOG, line, child)


def _figure(type_key: str, record: dict[str, str]):
    return FIGURES[type_key][0](dict(record)).figure


#: Every record of each (type, flute count) the catalog publishes whose figure has an end view.
FLUTE_CASES: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
#: Every record of each (type, direction attribute) the catalog publishes a hand for.
HAND_CASES: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
#: How each of those records was read: ``record``, ``partial`` or ``nominal``.
SOURCES: set[str] = set()
PUBLISHED_HANDS: set[str] = set()
for _type, _record in _records():
    SOURCES.add(FIGURES[_type][0](dict(_record)).source)
    # Only a figure with an end view draws the count: a tap states its flutes and draws none,
    # which is a different gap, not this channel.
    if FLUTES in _record and any(isinstance(s, Disc) for s in _figure(_type, _record).shapes):
        FLUTE_CASES[(_type, _record[FLUTES])].append(_record)
    for _name, _value in _record.items():
        if _value in HANDS:
            HAND_CASES[(_type, _name)].append(_record)
            PUBLISHED_HANDS.add(_value)


def _end_view(figure) -> tuple[Disc, Lines]:
    """The end view: the figure's one disc and the line work drawn right after it."""
    discs = [s for s in figure.shapes if isinstance(s, Disc)]
    assert len(discs) == 1, f"{len(discs)} discs; the end view is the figure's only one"
    lines = figure.shapes[figure.shapes.index(discs[0]) + 1]
    assert isinstance(lines, Lines)
    return discs[0], lines


def _spokes(figure) -> int:
    """How many flutes the end view shows: the segments that start at its centre."""
    disc, lines = _end_view(figure)
    return sum(1 for a, _b in lines.segments if math.dist(a, disc.centre) < 1e-9)


def _key(segments, flip=None):
    """A set of rounded segments, optionally mirrored about ``("x", x0)`` or ``("y", y0)``."""

    def put(p):
        if flip is None:
            return p
        axis, about = flip
        return (2 * about - p[0], p[1]) if axis == "x" else (p[0], 2 * about - p[1])

    return {tuple(round(v, 9) for p in seg for v in put(p)) for seg in segments}


def _middle(segments, axis: str) -> float:
    """The middle of the segments' extent across ``axis``: the tool's own axis line."""
    values = [p[0 if axis == "x" else 1] for seg in segments for p in seg]
    return (min(values) + max(values)) / 2


def _mirror_faults(type_key: str, record: dict[str, str], name: str) -> list[str]:
    """How the record's Left Hand drawing fails to be the mirror of its Right Hand one."""
    left = _figure(type_key, {**record, name: "Left Hand"})
    right = _figure(type_key, {**record, name: "Right Hand"})
    if left == right:
        return ["Left Hand and Right Hand are drawn alike"]
    faults = []
    edges_left = next(s for s in left.shapes if isinstance(s, Lines)).segments
    edges_right = next(s for s in right.shapes if isinstance(s, Lines)).segments
    if not edges_left or not any(
        _key(edges_left) == _key(edges_right, (axis, _middle(edges_right, axis))) for axis in "xy"
    ):
        faults.append("the flute edges are not mirrored left to right")
    disc, end_left = _end_view(left)
    _, end_right = _end_view(right)
    if _key(end_left.segments) != _key(end_right.segments, ("y", disc.centre[1])):
        faults.append("the end view is not mirrored top to bottom")
    if _key(end_left.segments) == _key(end_right.segments):
        faults.append("the end view does not bend")
    return faults


def test_the_sweeps_found_something_to_sweep():
    """The control for every derived sweep here: an empty one proves nothing."""
    assert len({count for (_, count) in FLUTE_CASES}) >= 3, sorted(FLUTE_CASES)
    assert {"record", "partial"} <= SOURCES, "no record of the catalog takes a fallback"
    assert set(HANDS) <= PUBLISHED_HANDS, "the catalog publishes no Left Hand: nothing to mirror"
    assert {t for (t, _), rs in HAND_CASES.items() if len(rs) > 1} >= {"end_mill_square"}


@pytest.mark.parametrize("case", sorted(FLUTE_CASES), ids="-".join)
def test_the_end_view_shows_as_many_flutes_as_the_catalog_records_state(case):
    """Every record of the catalog, however its figure was read, draws the flutes it states."""
    type_key, count = case
    wrong = [r for r in FLUTE_CASES[case] if _spokes(_figure(type_key, r)) != int(count)]
    assert not wrong, f"{len(wrong)} of {len(FLUTE_CASES[case])} end views do not show {count}"


@pytest.mark.parametrize("flutes", ["1", "2", "3", "5", "6", "8"])
@pytest.mark.parametrize("route", sorted(ROUTES))
def test_the_end_view_shows_the_published_flutes_whatever_route_the_figure_was_read_by(
    route, flutes
):
    type_key, change = ROUTES[route]
    record = {**BASE, **change, FLUTES: flutes}
    assert _spokes(_figure(type_key, record)) == int(flutes)


@pytest.mark.parametrize("flutes", ["abc", "0", "-2", ""])
def test_a_flute_count_that_is_not_a_count_is_not_drawn(flutes):
    """A published value that names no count is never carried into the fallback."""
    record = {**BASE, "Milling Dia.": "about a quarter", FLUTES: flutes}
    assert _spokes(_figure("end_mill_square", record)) == 4


@pytest.mark.parametrize(
    "case",
    sorted(case for case in HAND_CASES if case not in HAND_NOT_DRAWN),
    ids="-".join,
)
def test_every_published_left_hand_of_the_catalog_is_drawn_as_the_mirror_of_a_right_hand(case):
    """Each (type, attribute) whose hand the drawing shows, drawn both ways for each record.

    The flute edges across the body must be mirrored left to right and the end view's
    bend mirrored top to bottom. A drawing that read the hand and drew one for both
    fails both halves; one that read it for the edges only fails the second.
    """
    type_key, name = case
    faults = {
        tuple(faults)
        for record in HAND_CASES[case]
        if (faults := _mirror_faults(type_key, record, name))
    }
    assert not faults, (len(HAND_CASES[case]), sorted(faults))


@pytest.mark.parametrize("route", sorted(ROUTES))
def test_a_published_left_hand_is_the_mirror_of_a_right_hand_whatever_route_the_figure_was_read_by(
    route,
):
    type_key, change = ROUTES[route]
    assert _mirror_faults(type_key, {**BASE, **change}, CUTTING_DIRECTION) == []


def test_a_cutting_direction_that_is_not_a_hand_is_not_drawn():
    """A published value naming no hand is never carried into the fallback."""
    record = {**BASE, "Milling Dia.": "about a quarter"}
    assert _figure("end_mill_square", {**record, CUTTING_DIRECTION: "Sideways"}) == _figure(
        "end_mill_square", {**record, CUTTING_DIRECTION: "Right Hand"}
    )


def test_a_direction_the_drawing_ignores_is_named_and_only_that():
    """The list of ignored directions is exact: both of its edges are guarded.

    A type missing from it that ignores its direction fails here, so a hand-written
    parametrize list cannot leave a type out unseen; a type in it that now draws its
    direction fails here too, so the list cannot go on excusing a drawing that is fixed.
    """

    def drawn(case) -> bool:
        type_key, name = case
        return any(
            _figure(type_key, {**r, name: HANDS[0]}) != _figure(type_key, {**r, name: HANDS[1]})
            for r in HAND_CASES[case]
        )

    assert {case for case in HAND_CASES if not drawn(case)} == HAND_NOT_DRAWN


# --- which hatch belongs to which material ---------------------------------------------

#: What the table's comment says, as the pattern each material draws: its line angles (a
#: cross-hatch has two) and whether it carries dots.
CONVENTION = {
    "Solid Carbide": ((45, 135), False),
    "Powdered Metal": ((), True),
    "High Speed Steel": ((45,), False),
    "Cobalt": ((135,), False),
}


def _drawn_hatch(material: str) -> tuple[tuple[int, ...], bool]:
    """The pattern a ``material`` part is painted with, read back off the SVG it is in."""
    data, _source = draw_sku("end_mill_square", BRANDS[0], {**BASE, "Material": material})
    ns = "{http://www.w3.org/2000/svg}"
    used = set(re.findall(r"url\(#([^)]+)\)", data.decode()))
    patterns = [p for p in ET.fromstring(data).iter(f"{ns}pattern") if p.get("id") in used]
    assert len(patterns) == 1, f"{material}: {len(patterns)} hatch patterns painted on the part"
    angles = tuple(
        int(float(m.group(1)))
        for path in patterns[0].iter(f"{ns}path")
        if (m := re.match(r"rotate\((-?[\d.]+)", path.get("transform", "")))
    )
    return angles, any(True for _ in patterns[0].iter(f"{ns}circle"))


@pytest.mark.parametrize("material", sorted(CONVENTION))
def test_a_material_is_hatched_the_way_its_convention_says(material):
    assert _drawn_hatch(material) == CONVENTION[material]
