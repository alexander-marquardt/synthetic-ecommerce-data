"""A published ``Coolant Fed`` is whether the drawing shows coolant outlets (#9).

``Coolant Fed`` is a form, not an extent: whether coolant runs through the tool and leaves at
its cutting end. The end view counts the outlets off its own shapes, one per flute on a
``Coolant Through`` mill and none on a ``Non-Coolant Through`` one, so a coolant-fed mill drawn
with a solid end and the words "Coolant Through" in the record is a picture contradicting its
data.

The figure falls back to nominal proportions when the published dimensions cannot be drawn.
The fallback may take an extent from the nominal shape, never the coolant the record publishes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.core.drawing.model import Disc
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

BASE = {
    "Milling Dia.": '1/4"',
    "Shank Dia.": '1/4"',
    "Length of Cut": '3/4"',
    "Overall Length": '3"',
    "Number of Flutes": "4",
    "Helix Angle": "30 Degrees",
}
COOLANT = "Coolant Fed"
THROUGH = "Coolant Through"
NOT_THROUGH = "Non-Coolant Through"

#: Each way a published record fails to draw as published, and the type that exposes it.
ROUTES = {
    "dimensions that draw as published": ("end_mill_square", {}),
    "a length of cut as long as the tool": (
        "end_mill_square",
        {"Length of Cut": '3"', "Overall Length": '3"'},
    ),
    "a ball nose publishing a corner radius": ("end_mill_ball", {"Corner Radius": '1/64"'}),
    "a diameter that does not parse": ("end_mill_square", {"Milling Dia.": "about a quarter"}),
}


def outlets(type_key: str, record: dict[str, str]) -> int:
    """The coolant outlets in the figure: the ``hole`` discs on the end view."""
    figure = FIGURES[type_key][0](record).figure
    return sum(1 for shape in figure.shapes if isinstance(shape, Disc) and shape.role == "hole")


@pytest.mark.parametrize("route", sorted(ROUTES))
@pytest.mark.parametrize("flutes", ["2", "3", "4"])
def test_a_coolant_through_mill_shows_one_outlet_per_flute_however_the_figure_was_read(
    route, flutes
):
    type_key, change = ROUTES[route]
    record = {**BASE, **change, "Number of Flutes": flutes, COOLANT: THROUGH}
    assert outlets(type_key, record) == int(flutes), route


@pytest.mark.parametrize("route", sorted(ROUTES))
def test_a_non_coolant_through_mill_shows_no_outlet(route):
    type_key, change = ROUTES[route]
    assert outlets(type_key, {**BASE, **change, COOLANT: NOT_THROUGH}) == 0, route


def test_a_record_that_publishes_no_coolant_shows_no_outlet():
    assert outlets("end_mill_square", dict(BASE)) == 0


def test_a_coolant_value_naming_neither_is_not_drawn_as_a_form():
    """A published value that says neither is never carried into the fallback."""
    record = {**BASE, "Milling Dia.": "about a quarter", COOLANT: "Mist"}
    assert outlets("end_mill_square", record) == 0


def test_the_outlets_change_the_drawing_and_nothing_else_does():
    """The coolant is the only difference between the two figures: the end view's outlets."""
    fn = FIGURES["end_mill_square"][0]
    through = fn({**BASE, COOLANT: THROUGH}).figure.shapes
    solid = fn({**BASE, COOLANT: NOT_THROUGH}).figure.shapes
    assert through != solid
    assert [s for s in through if not (isinstance(s, Disc) and s.role == "hole")] == solid


def test_every_end_mill_in_the_committed_catalog_shows_the_coolant_it_publishes():
    facets = bundle.flat_facets(GOLDEN)
    drawn = {THROUGH: 0, NOT_THROUGH: 0}
    wrong = []
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        if parent["product_type"] not in ("end_mill_square", "end_mill_ball"):
            continue
        for variant in parent["variants"]:
            record = bundle._record(
                parent,
                variant,
                facets[variant["sku"]],
                facets.authored.get(parent["product_type"]),
            )
            coolant = record.get(COOLANT)
            if coolant not in drawn:
                continue
            drawn[coolant] += 1
            want = int(record["Number of Flutes"]) if coolant == THROUGH else 0
            if outlets(parent["product_type"], record) != want:
                wrong.append((variant["sku"], coolant))
    assert min(drawn.values()) > 20, drawn
    assert not wrong, (len(wrong), wrong[:5])
