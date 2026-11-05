"""A published ``Thread Type`` holds on a rod or stud drawn at its crest cap (#9).

Coarse or fine is a form, not an extent: at one diameter a fine thread has more crests than the
coarse one. A long threaded rod or double-end stud is drawn compressed, and its crests are
spread so that at most a set number fit the drawing. That cap used to be a fixed pitch, so a
5/16-18 UNC rod and a 5/16-24 UNF rod of one length drew the same crests, and the words "UNF"
in the record were the only thing that told them apart.

The cap now spreads the crests by one factor for every thread of a diameter, taken from that
diameter's coarse pitch, so a fine thread stays finer than the coarse one at the true ratio.
The pitch is measured off the figure's crest strokes: each one rises half a pitch across the
body.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.core.dimensions import parse_thread
from synthetic_ecommerce_data.core.drawing.model import Lines
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

#: The two types whose figure caps its crests, and a length past each one's cap.
CAPPED = {"threaded_rod": '36"', "studs_double_end": '6"'}

#: Coarse and fine designations of one diameter, inch and metric.
PAIRS = [
    ("5/16-18", "5/16-24"),
    ("3/8-16", "3/8-24"),
    ("1/2-13", "1/2-20"),
    ("M8x1.25", "M8x1"),
    ("M12x1.75", "M12x1.25"),
]


def drawn_pitch(type_key: str, record: dict[str, str]) -> float:
    """The one axial spacing of the figure's crest strokes, in inches."""
    figure = FIGURES[type_key][0](record).figure
    pitches = {
        round(2 * (y1 - y0), 9)
        for shape in figure.shapes
        if isinstance(shape, Lines) and shape.role == "line"
        for (x0, y0), (x1, y1) in shape.segments
        if x0 < 0 < x1 and abs(x0 + x1) < 1e-9 and y1 > y0
    }
    assert len(pitches) == 1, (type_key, record, pitches)
    return pitches.pop()


@pytest.mark.parametrize("type_key", sorted(CAPPED))
@pytest.mark.parametrize(("coarse", "fine"), PAIRS)
def test_a_fine_thread_is_drawn_finer_than_the_coarse_one_at_the_cap(type_key, coarse, fine):
    length = CAPPED[type_key]
    drawn_coarse = drawn_pitch(type_key, {"Thread Size": coarse, "Length": length})
    drawn_fine = drawn_pitch(type_key, {"Thread Size": fine, "Length": length})
    true_ratio = parse_thread(fine).pitch_in / parse_thread(coarse).pitch_in
    assert drawn_fine < drawn_coarse, (coarse, fine)
    assert drawn_fine / drawn_coarse == pytest.approx(true_ratio, rel=1e-6), (coarse, fine)


@pytest.mark.parametrize("type_key", sorted(CAPPED))
@pytest.mark.parametrize(("coarse", "fine"), PAIRS)
def test_a_short_part_is_drawn_at_its_true_pitch(type_key, coarse, fine):
    """Below the cap and the compression nothing is spread: the crests are the published pitch."""
    for designation in (coarse, fine):
        published = parse_thread(designation).pitch_in
        drawn = drawn_pitch(type_key, {"Thread Size": designation, "Length": '2"'})
        assert drawn == pytest.approx(published, rel=1e-6), designation


@pytest.mark.parametrize("type_key", sorted(CAPPED))
def test_every_part_in_the_committed_catalog_keeps_its_pitch_ratio_to_its_siblings(type_key):
    """At one diameter and length, the drawn pitches are the published ones times one factor."""
    facets = bundle.flat_facets(GOLDEN)
    groups: dict[tuple[float, str], dict[float, float]] = defaultdict(dict)
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        if parent["product_type"] != type_key:
            continue
        for variant in parent["variants"]:
            record = bundle._record(
                parent, variant, facets[variant["sku"]], facets.authored.get(type_key)
            )
            thread = parse_thread(record["Thread Size"])
            factor = drawn_pitch(type_key, record) / thread.pitch_in
            groups[(round(thread.major.inches, 4), record["Length"])][thread.pitch_in] = factor
    assert len(groups) > 10, len(groups)
    spread = {key: factors for key, factors in groups.items() if len(set(factors.values())) > 1}
    assert not spread, spread
