"""Every styled SKU image of the default catalogue draws its product clear of its logo and licence
line, every shape (gen#932, slice 2).

``tests/test_product_clear_of_logo_932.py`` pins the hoodie and all-in-one shapes, where the
crossing was found. Before #973's fix in ``house_styles.product_transform``, 3,249 of the default
build's images crossed a band, most of them other shapes; this file measures them all, with that
file's band check. About 121,600 SKUs draw 83,300 drawings, 110 s on one local core, so the
templates are dealt into :data:`CHUNKS` tests that xdist spreads over its workers. A drawing
belongs to one product (``export.drawing_id`` starts with the product id), so a chunk of whole
products renders each of its drawings once, as a single pass would.
"""

from __future__ import annotations

import functools

import pytest

from synthetic_ecommerce_data.domains.retail import export, house_styles, image_release, scale
from test_product_clear_of_logo_932 import SLACK, _free_rows, _product_rows

#: Independent tests, each building its own share: spread over the workers (tests/xdist_groups.py).
XDIST_SPREAD = True
CHUNKS = 12


@functools.cache
def _templates() -> tuple[dict, ...]:
    return tuple(scale.templates())


@pytest.mark.parametrize("chunk", range(CHUNKS))
def test_every_styled_image_is_drawn_clear_of_the_logo_and_licence_line(chunk: int) -> None:
    docs = _templates()[chunk::CHUNKS]
    drawn: dict[str, tuple[float, float]] = {}
    skus = 0
    crossing = []
    for d in docs:
        if house_styles.HOUSE_STYLES[d["brand"]].mark == house_styles.NO_MARK:
            continue
        lo, hi = _free_rows(d)
        for s in d["skus"]:
            key = export.drawing_id(d, s)
            if key not in drawn:
                drawn[key] = _product_rows(image_release.render(d, s).decode())
            y0, y1 = drawn[key]
            skus += 1
            if y0 < lo - SLACK or y1 > hi + SLACK:
                shape = d["drawing"]["shape"]
                box = (round(y0, 1), round(y1, 1))
                crossing.append((shape, s["sku"], s.get("size"), *box, lo, hi))
    # The default build has about 121,600 styled SKUs, so each twelfth holds thousands.
    assert skus > 5000
    assert crossing[:20] == [], f"{len(crossing)} images cross a band"
