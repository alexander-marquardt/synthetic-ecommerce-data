"""A published ``Single End/Double End`` is the number of cutting ends the drawing shows (#9).

``Single End/Double End`` is a form, not an extent: how many cutting ends a tool has. The
drawing counts them off its own shapes, so a double-end mill drawn with one cutting end and
the words "Double End" in the record is a picture contradicting its data.

The figure falls back to nominal proportions when the published dimensions cannot be drawn
(a ball nose with a corner radius, two lengths of cut as long as the whole tool, a diameter
that does not parse). The fallback may take an extent from the nominal shape, never the
number of ends the record publishes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.core.drawing import FIGURES
from synthetic_ecommerce_data.core.drawing.model import Poly

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

BASE = {
    "Milling Dia.": '1/4"',
    "Shank Dia.": '1/4"',
    "Length of Cut": '3/4"',
    "Overall Length": '3"',
    "Number of Flutes": "4",
    "Helix Angle": "30 Degrees",
}
ENDS = "Single End/Double End"
WANT = {"Single End": 1, "Double End": 2}

#: Each way a published record fails to draw as published, and the type that exposes it.
ROUTES = {
    "dimensions that draw as published": ("end_mill_square", {}),
    "two lengths of cut as long as the tool": (
        "end_mill_square",
        {"Length of Cut": '1"', "Overall Length": '1-1/2"'},
    ),
    "a ball nose publishing a corner radius": ("end_mill_ball", {"Corner Radius": '1/64"'}),
    "a diameter that does not parse": ("end_mill_square", {"Milling Dia.": "about a quarter"}),
}


def cutting_ends(type_key: str, record: dict[str, str]) -> int:
    """The cutting bodies in the figure: one ``part`` polygon per end the tool has."""
    figure = FIGURES[type_key][0](record).figure
    return sum(1 for shape in figure.shapes if isinstance(shape, Poly) and shape.role == "part")


@pytest.mark.parametrize("route", sorted(ROUTES))
@pytest.mark.parametrize("ends", sorted(WANT))
def test_the_published_number_of_ends_is_the_number_drawn_however_the_figure_was_read(route, ends):
    type_key, change = ROUTES[route]
    record = {**BASE, **change, ENDS: ends}
    assert cutting_ends(type_key, record) == WANT[ends], (route, ends)


def test_a_record_that_publishes_no_number_of_ends_is_drawn_with_one():
    assert cutting_ends("end_mill_square", dict(BASE)) == 1


def test_every_end_mill_in_the_committed_catalog_is_drawn_with_the_ends_it_publishes():
    facets = bundle.flat_facets(GOLDEN)
    drawn = {"Single End": 0, "Double End": 0}
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
            ends = record.get(ENDS)
            if ends not in WANT:
                continue
            drawn[ends] += 1
            if cutting_ends(parent["product_type"], record) != WANT[ends]:
                wrong.append((variant["sku"], ends))
    assert min(drawn.values()) > 50, drawn
    assert not wrong, (len(wrong), wrong[:5])
