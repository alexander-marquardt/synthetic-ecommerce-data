"""An authored range name is a plain word of its family, with no number or sub-model (#851).

The derived ranges dropped their numbers (``tests/test_retail_scale_range_names_851.py``), but
the authored rows kept theirs: "Bramblewood Comfort Pro 3 Underwired Lace Plunge Bra", "Ottery
Denim Original Pro 101 High Rise Cigarette Jeans", "Stridewell Summit 2 Waterproof Walking
Boots". A number or a sub-model word after a range word reads as synthetic, and two bras of one
brand, wiring and style ("Comfort Lite 7", "Comfort Lite 8") were told apart by it alone. Each
authored line is now one lead word of its family; a brand's second bra of one wiring and style
takes another. The cleaning and beauty models keep their numbers until the grocery build drops
them too (the issue's Remaining line).
"""

from __future__ import annotations

import collections
import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import bicycle_model_numbers as bmn
from synthetic_ecommerce_data.domains.retail import line_grammar, scale

#: A bare number as a word of a range name ("Comfort 2", "Original Pro 101").
BARE_NUMBER = re.compile(r"\b\d+\b")


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


@pytest.fixture(scope="module")
def authored() -> list[dict]:
    return [t for t in scale.templates() if not t["product_id"].startswith(scale.GROCERY_PREFIX)]


def _outside_care(rec: dict) -> bool:
    return line_grammar.family(rec) not in line_grammar.CARE


def test_no_product_outside_care_has_a_numbered_range(ceiling):
    """Guard (#851): "Comfort 2", "Speed 4", "Summit 2" on an authored row. Metric: ceiling
    products outside the cleaning and beauty families whose range name has a bare number."""
    numbered = [
        (r["product_type"], scale._line(r))
        for r in ceiling.records
        if _outside_care(r) and BARE_NUMBER.search(scale._line(r) or "")
    ]
    assert numbered == [], f"{len(numbered)}: {sorted(set(numbered))[:10]}"


def _lined(authored: list[dict]) -> list[tuple[dict, str]]:
    """The authored clothing and footwear rows that state a model of the grammar, a bike series
    its brand owns aside (#718). An appliance, tool or garden model ("Torque Pro Drill Driver")
    keeps its sub-model word: no number follows it, and a retailer names such a model so."""
    out = []
    for t in authored:
        fam, line = line_grammar.family(t), scale._line(t)
        if fam not in CLOTHING or not line or line in bmn.SERIES.get(t["brand"], {}).values():
            continue
        if line_grammar.is_model(fam, t["brand"], line):
            out.append((t, line))
    return out


#: The families whose authored lines carried a number: bras, jeans, running shoes, walking boots.
CLOTHING = ("bra", "jeans", "sport", "boots")


def test_an_authored_clothing_line_is_one_lead_word(authored):
    """Guard (#851): "Comfort Pro" or "Support Lite" is a range set apart by a modifier alone.
    Metric: authored bra, jeans, sport and boot rows whose model is more than one lead word."""
    long = [(t["product_type"], line) for t, line in _lined(authored) if len(line.split()) > 1]
    assert _lined(authored)
    assert long == [], f"{len(long)}: {sorted(set(long))[:10]}"


def test_no_two_authored_lined_products_share_a_brand_title_and_path(authored):
    """Guard (#851): with the number gone, two bras of one brand, wiring and style ("Comfort
    Lite 7", "Comfort Lite 8", both Non-Wired Mastectomy) read as one product split in two.
    Metric: (brand, title, category path) shared by two authored rows that state a model."""
    seen = collections.Counter(
        (t["brand"], t["title"], tuple(t["category_path"])) for t, _ in _lined(authored)
    )
    assert [k for k, n in seen.items() if n > 1] == []
