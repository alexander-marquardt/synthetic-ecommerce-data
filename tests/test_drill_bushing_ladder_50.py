"""No two drill bushings of one line draw alike (#50, slice 5).

Seed 20260918 built two lines of ``1/8, #30, #29, #28, 9/64`` bores: a ``#28`` drill is 0.1405"
and a ``9/64`` one 0.1406", and the figure, which writes its bore lines at one decimal of a sheet
unit, drew the two alike. ``tests/test_sku_drawings.py::
test_siblings_whose_drawn_values_differ_never_draw_alike`` caught it over that seed's golden
catalog, where it is judged on the default seed only. A line now draws its bores from
``drill_bushings.ladder``, which keeps a number or letter drill only when the figure draws it
apart from every bore kept before it; these hold that on every line the table can build, at every
angle a bushing turns by, and on the seed that found it.
"""

from __future__ import annotations

import dataclasses
import itertools

import pytest

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.drawing import draw_product, product_look
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.product_types.cutting_tools import (
    drill_bushings as bushings,
)

#: The moved seed of #50's proof that built the two lines.
SEED = 20260918


def test_no_drill_bushing_line_of_the_moved_seed_has_siblings_drawn_alike():
    catalog = generate(dataclasses.replace(SMALL, seed=SEED))
    alike = []
    lines = [line for line in catalog.lines if line.type_key == "drill_bushings"]
    for line in lines:
        records = [emit.drawing_record(catalog, line, child) for child in line.children]
        pairs = draw_product(line.type_key, line.brand, records, line.product_id)
        drawn = [data for data, _ in pairs]
        if len(set(drawn)) < len(drawn):
            alike.append((line.product_id, [record.get("Drill Size") for record in records]))
    assert len(lines) > 1
    assert alike == []


def _product_at(angle: int) -> str:
    """A product id :func:`product_look.angle_of` turns ``angle`` degrees."""
    return next(
        pid
        for pid in (f"bushing-{n}" for n in itertools.count())
        if product_look.angle_of(pid, "any") == angle
    )


@pytest.mark.parametrize("angle", product_look.ORIENTATIONS["any"])
def test_no_two_neighbouring_bores_of_any_line_draw_alike(angle):
    """Every row and length the table builds a line of, its whole ladder, at one angle of the
    type's orientation: a line's SKUs are a run of the ladder, so neighbours drawn apart are
    every two siblings drawn apart."""
    product_id = _product_at(angle)
    alike, pairs = [], 0
    for index, row in enumerate(bushings.ROWS):
        if bushings.is_liner(row):
            continue
        for length in row["lengths"]:
            body = bushings._body_record(row, length)
            records = [
                dict(body, **{"Size": f'{inches:.4f}"', "Drill Size": drill})
                for drill, inches in bushings.ladder(index, length)
            ]
            drawn = draw_product("drill_bushings", "Quarrenby", records, product_id)
            sheets = zip(records, (data for data, _ in drawn), strict=True)
            for (left, a), (right, b) in itertools.pairwise(sheets):
                pairs += 1
                if a == b:
                    alike.append((row["type"], row["body"], length, left["Size"], right["Size"]))
    assert pairs > 4000
    assert alike == [], f"{len(alike)} of {pairs}: {alike[:5]}"


def test_the_ladder_keeps_every_fractional_bore_and_thins_only_number_and_letter_drills():
    """What thinning costs: the fractional sizes, a sixty-fourth apart, all stay, so every
    breadth-row bore is still built; the number and letter drills a body too large for a lens
    loses are the ones nearer than 0.0079" to a kept bore."""
    for index, row in enumerate(bushings.ROWS):
        if bushings.is_liner(row):
            continue
        holes = bushings.holes_of(row)
        for length in row["lengths"]:
            kept = bushings.ladder(index, length)
            assert set(kept) <= set(holes)
            assert [h for h in holes if h[0][0].isdigit()] == [h for h in kept if h[0][0].isdigit()]
            assert bushings.bore_step(index, length) <= 0.0079
