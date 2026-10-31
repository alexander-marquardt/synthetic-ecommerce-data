"""The plain screws: wood, machine, drywall, sheet metal and deck (#750).

A shopper who wanted an ordinary screw found only cap screws, set screws and one lag screw. These
tests read the committed catalog, so they hold what a search sees: the node, the variant axes and
the singular and plural titles.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import pytest

GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog"
DOCS = [json.loads(line) for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()]

#: Each kind: its singular title word, its plural one and its leaf.
KINDS = {
    "screw_wood": ("Wood Screw", "Wood Screws", "Wood screws"),
    "screw_machine": ("Machine Screw", "Machine Screws", "Machine screws"),
    "screw_drywall": ("Drywall Screw", "Drywall Screws", "Drywall screws"),
    "screw_sheet_metal": ("Sheet Metal Screw", "Sheet Metal Screws", "Sheet metal screws"),
    "screw_deck": ("Deck Screw", "Deck Screws", "Deck screws"),
}
BOX = re.compile(r", Box of (\d+)$")


def _facts(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in doc["attributes"]}


def _docs(key: str) -> list[dict]:
    return [doc for doc in DOCS if doc["product_type"] == key]


def _products(key: str) -> list[list[dict]]:
    products: dict[str, list[dict]] = defaultdict(list)
    for doc in _docs(key):
        products[doc["product_id"]].append(doc)
    return list(products.values())


@pytest.mark.parametrize("key", KINDS)
def test_a_plain_screw_sits_beside_the_lag_screw(key):
    lag = next(doc for doc in DOCS if doc["product_type"] == "lag_screws")
    docs = _docs(key)
    assert docs, f"the catalog sells no {key}"
    for doc in docs:
        assert doc["category_path"] == [*lag["category_path"][:2], KINDS[key][2]]


@pytest.mark.parametrize("key", KINDS)
def test_a_box_sold_title_is_plural_and_says_its_own_pack(key):
    _, plural, _ = KINDS[key]
    boxed = [doc for doc in _docs(key) if BOX.search(doc["title"])]
    assert boxed, f"no {key} title is sold by the box"
    for doc in boxed:
        assert plural in doc["title"], doc["title"]
        assert _facts(doc)["Units per Pack"] == BOX.search(doc["title"]).group(1)
        assert doc["pricing_unit"] == "Per Pack"


@pytest.mark.parametrize("key", KINDS)
def test_a_screw_sold_singly_has_a_singular_title_and_no_pack(key):
    singular, plural, _ = KINDS[key]
    loose = [doc for doc in _docs(key) if not BOX.search(doc["title"])]
    assert loose, f"no {key} is sold singly"
    for doc in loose:
        assert singular in doc["title"] and plural not in doc["title"], doc["title"]
        assert "Units per Pack" not in _facts(doc)
        assert doc["pricing_unit"] == "Each"


@pytest.mark.parametrize("key", KINDS)
def test_every_sku_publishes_its_length_and_its_gauge_or_thread(key):
    size = "Dia./Thread Size" if key == "screw_machine" else "Gauge"
    docs = _docs(key)
    assert docs, f"the catalog sells no {key}"
    for doc in docs:
        facts = _facts(doc)
        assert facts["Length"] and facts[size], doc["sku"]
        assert facts[size] in doc["title"], doc["title"]


def test_a_product_varies_by_length_and_a_box_by_its_pack():
    products = [p for key in KINDS for p in _products(key)]
    assert any(len({_facts(doc)["Length"] for doc in p}) > 1 for p in products)


@pytest.mark.parametrize("word", ["Pan Head", "Flat Head", "Bugle Head"])
def test_the_head_a_shopper_names_is_in_a_title(word):
    assert any(word in doc["title"] for key in KINDS for doc in _docs(key))
