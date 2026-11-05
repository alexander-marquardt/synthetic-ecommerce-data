"""A mug is sold in several glazes or grounds, not as a run of one-color products (#851).

After slices 1 and 2 most mug products still had one SKU: each plain mug of the mug print line
had one glaze, and each graphic mug one ground, and a derived style copies its template's
colors, so every brand's mug had one SKU too. The maintainer asked for different colors within
each product: a brand's mug is one product whose colors are its SKUs.
"""

from __future__ import annotations

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import prints, scale_measures

#: The print line's mug codes: its plains (PLT-MUG1 ...) and prints (PLT-MUG-APPLE ...).
LINE = next(line for line in prints.LINES if line.code == "MUG")


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _line_mugs(ceiling) -> list[dict]:
    def template(r: dict) -> str:
        return ceiling.template_of.get(r["product_id"], r["product_id"])

    prefix = f"PLT-{LINE.code}"
    return [r for r in ceiling.records
            if r["product_type"] == "Mug" and template(r).startswith(prefix)]  # fmt: skip


def test_a_mug_of_the_print_line_sells_more_than_one_color(ceiling):
    """Guard (#851): each plain mug had one glaze and each graphic mug one ground. Metric: mug
    products of the print line, or derived from it, with one SKU."""
    mugs = _line_mugs(ceiling)
    assert len(mugs) > len(LINE.plains) + len(LINE.prints)
    assert [(r["brand"], r["title"]) for r in mugs if len(r["skus"]) == 1] == []


def test_a_plain_mug_sells_three_glazes():
    """Guard (#851): a plain mug is one product in three glazes, its hero first. Metric: the
    color SKUs of each plain mug template."""
    plains = [s for s in prints.styles((LINE,)) if s.pattern == "plain"]
    assert len(plains) == len(LINE.plains)
    assert {s.code: len(s.colors) for s in plains if len(s.colors) != 3} == {}
    assert {s.code: len(s.colors) for s in plains if len({c[0] for c, _ in s.colors}) != 3} == {}


def test_mug_is_not_a_kind_of_one_sku_products(ceiling):
    """Guard (#851): the report named Mug, 29 of its 39 products one SKU. Metric: the
    ``single_sku_kinds`` entry for Mug."""
    assert "Mug" not in scale_measures.single_sku_kinds(ceiling.records)
