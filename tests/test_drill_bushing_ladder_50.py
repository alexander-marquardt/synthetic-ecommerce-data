"""No two drill bushings of one line draw alike (#50, slice 5).

Seed 20260918 built two lines of ``1/8, #30, #29, #28, 9/64`` bores: a ``#28`` drill is 0.1405"
and a ``9/64`` one 0.1406", and the figure, which writes its bore lines at one decimal of a sheet
unit, drew the two alike. ``tests/test_sku_drawings.py::
test_siblings_whose_drawn_values_differ_never_draw_alike`` caught it over that seed's golden
catalog, where it is judged on the default seed only; this holds it on any seed.
"""

from __future__ import annotations

import dataclasses

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.drawing import draw_product
from synthetic_ecommerce_data.domains.industrial.generate import generate

#: The moved seed of #50's proof that built the two lines.
SEED = 20260918


def test_no_drill_bushing_line_of_the_moved_seed_has_siblings_drawn_alike():
    catalog = generate(dataclasses.replace(SMALL, seed=SEED))
    alike = []
    lines = [line for line in catalog.lines if line.type_key == "drill_bushings"]
    for line in lines:
        records = [emit.drawing_record(catalog, line, child) for child in line.children]
        drawn = draw_product(line.type_key, line.brand, records, line.product_id)
        drawn = [data for data, _ in drawn]
        if len(set(drawn)) < len(drawn):
            alike.append((line.product_id, [record.get("Drill Size") for record in records]))
    assert len(lines) > 1
    assert alike == []
