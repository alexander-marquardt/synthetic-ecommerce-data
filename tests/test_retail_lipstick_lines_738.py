"""The lipstick lines of the ceiling build keep their looks apart (gen#738).

Apart from ``test_retail_lipstick_looks_738.py`` because the build costs minutes: the tests there
read a line's look from its name, and these read the lines the catalog holds.
"""

from __future__ import annotations

import copy

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import export, image_release


def _picture(rec: dict) -> str:
    """What ``rec``'s first SKU draws on the plain sheet, in one shade, with no id of its own."""
    rec = copy.deepcopy(rec)
    sku = rec["skus"][0]
    svg = image_release.render(rec, sku, styled=False).decode()
    svg = svg.replace(image_release.colorway_drawing(rec, sku)["base"], "SHADE")
    return svg.replace(rec["product_id"], "ID")


def _spec(rec: dict) -> dict:
    return export.drawing_spec(rec, rec["skus"][0]).get("params", {})


def test_every_lipstick_line_of_the_ceiling_build_draws_its_own_picture() -> None:
    lips = [r for r in ceiling_build().records if r["product_type"] == "Lipstick"]
    lines = {r.get("product_line") or r["title"]: r for r in lips}
    assert len(lines) > 50
    assert len({_picture(r) for r in lines.values()}) == len(lines)


def test_no_two_lines_of_one_brand_share_a_case_and_its_color() -> None:
    """A brand's products fill a page together. A new line that lands on a taken case and color
    needs a new ``lipstick_looks.SALT``."""
    by_brand: dict[str, dict[str, tuple[str, str]]] = {}
    for rec in ceiling_build().records:
        if rec["drawing"]["shape"] == "lipstick":
            look = _spec(rec)
            line = rec.get("product_line") or rec["title"]
            by_brand.setdefault(rec["brand"], {})[line] = (look.get("case"), look.get("case_color"))
    assert sum(len(lines) for lines in by_brand.values()) > 50
    for brand, lines in by_brand.items():
        assert len(set(lines.values())) == len(lines), brand
