"""Three channels of the catalog's own drawings, each measured on its own (#10).

``tests/test_sku_drawings.py::test_the_committed_catalog_rebuilds_into_its_recorded_drawings``
answers for every channel at once: break any of them and the digests move. That is a
tripwire, not a guard. A republished catalog moves the digests too, so the one test that
notices a channel gone wrong notices it in the same words as a deliberate change, and the
review that follows has nothing to point at. Each channel below is measured from the
figure the SKU's drawing function returns, or the pattern in the SVG it writes, so a
failure names the channel.

* **The flute count of the end view** is a second drawing of a value the record states.
  An end mill's elevation shows its flutes edge on; the end view is where two flutes are
  visibly two. A page whose title says three beside an end view of four contradicts
  itself.
* **The hand** a record publishes. The sweep is read off the catalog's own vocabulary,
  not off a list written out here: a type that starts publishing ``Left Hand`` is in the
  sweep the day it does.
* **Which hatch belongs to which material.** The table is injective (a test elsewhere
  holds that), which a permutation of its values leaves true. What a permutation breaks
  is the convention the table's comment states: carbide the cross-hatch, powdered metal
  the stipple, the tool steels plain diagonals.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.drawing import FIGURES, draw_sku
from synthetic_ecommerce_data.core.drawing.model import Disc, Lines
from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, generate
from synthetic_ecommerce_data.domains.industrial.render.marking import DIRECTION_ATTRIBUTES

CATALOG = generate(SMALL)

FLUTES = "Number of Flutes"


def _records():
    for line, child in CATALOG.all_skus():
        if line.type_key in FIGURES:
            yield line.type_key, emit.drawing_record(CATALOG, line, child)


#: One record for each (type, flute count) the catalog publishes: derived, not listed.
FLUTE_CASES: dict[tuple[str, str], dict[str, str]] = {}
#: One record for each (type, direction attribute) the catalog publishes as Left Hand.
LEFT_CASES: dict[tuple[str, str], dict[str, str]] = {}
for _type, _record in _records():
    # Only a figure with an end view draws the count: a tap states its flutes and draws none,
    # which is a different gap, not this channel.
    if (
        FLUTES in _record
        and (_type, _record[FLUTES]) not in FLUTE_CASES
        and any(isinstance(s, Disc) for s in FIGURES[_type][0](dict(_record)).figure.shapes)
    ):
        FLUTE_CASES[(_type, _record[FLUTES])] = _record
    for _name in DIRECTION_ATTRIBUTES:
        if _record.get(_name) == "Left Hand":
            LEFT_CASES.setdefault((_type, _name), _record)


def _figure(type_key: str, record: dict[str, str]):
    return FIGURES[type_key][0](dict(record)).figure


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
    """A set of rounded segments, optionally mirrored: ``("x", 0)`` or ``("y", y0)``."""

    def put(p):
        if flip is None:
            return p
        axis, about = flip
        return (-p[0], p[1]) if axis == "x" else (p[0], 2 * about - p[1])

    return {tuple(round(v, 9) for p in seg for v in put(p)) for seg in segments}


def test_the_sweeps_found_something_to_sweep():
    """The control for every derived sweep here: an empty one proves nothing."""
    counts = {count for (_, count) in FLUTE_CASES}
    assert len(counts) >= 3, sorted(counts)
    assert LEFT_CASES, "the catalog publishes no Left Hand, so the hand sweep is empty"


@pytest.mark.parametrize("case", sorted(FLUTE_CASES), ids=lambda c: f"{c[0]}-{c[1]}-flutes")
def test_the_end_view_shows_as_many_flutes_as_the_record_states(case):
    assert _spokes(_figure(case[0], FLUTE_CASES[case])) == int(case[1])


@pytest.mark.parametrize("case", sorted(LEFT_CASES), ids=lambda c: f"{c[0]}-{c[1]}")
def test_a_published_left_hand_is_drawn_as_the_mirror_of_a_right_hand(case):
    """Each (type, attribute) the catalog publishes as Left Hand, drawn both ways.

    The flute edges across the body must be mirrored left to right and the end view's
    bend mirrored top to bottom. A drawing that read the hand and drew one for both
    fails both halves; one that read it for the edges only fails the second.
    """
    type_key, name = case
    record = LEFT_CASES[case]
    left = _figure(type_key, {**record, name: "Left Hand"})
    right = _figure(type_key, {**record, name: "Right Hand"})
    assert left != right, f"{type_key} draws {name} Left Hand and Right Hand alike"
    edges_left = next(s for s in left.shapes if isinstance(s, Lines)).segments
    edges_right = next(s for s in right.shapes if isinstance(s, Lines)).segments
    assert edges_left, "the control: the elevation draws flute edges at all"
    assert _key(edges_left) == _key(edges_right, ("x", 0.0))
    disc, end_left = _end_view(left)
    _, end_right = _end_view(right)
    assert _key(end_left.segments) == _key(end_right.segments, ("y", disc.centre[1]))
    assert _key(end_left.segments) != _key(end_right.segments), "the end view does not bend"


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
    record = {**next(r for (t, _), r in FLUTE_CASES.items() if t == "end_mill_square")}
    data, _source = draw_sku("end_mill_square", BRANDS[0], {**record, "Material": material})
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
