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
from types import SimpleNamespace

import pytest

from shared_builds import hundred_k_flat
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    parse_gauge,
    parse_length,
)
from synthetic_ecommerce_data.domains.industrial import plain_screws
from synthetic_ecommerce_data.domains.industrial.drawing.plain_screw import HEADS, plain_screw
from synthetic_ecommerce_data.domains.industrial.generate import Generator

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
#: The most of the catalog's SKUs the five kinds may be together.
RANGE_CAP = 0.01


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
    boxed = [doc for doc in _docs(key) if _facts(doc)["Units per pack"] != "1"]
    assert boxed, f"no {key} is sold by the box"
    for doc in boxed:
        assert plural in doc["title"], doc["title"]
        assert doc["pricing_unit"] == "Per Pack"
        said = BOX.search(doc["title"])
        assert said is None or said.group(1) == _facts(doc)["Units per pack"], doc["title"]
    assert any(BOX.search(doc["title"]) for doc in boxed), f"no {key} title says its box"


@pytest.mark.parametrize("key", KINDS)
def test_a_screw_sold_singly_has_a_singular_title_and_says_no_pack(key):
    singular, plural, _ = KINDS[key]
    loose = [doc for doc in _docs(key) if _facts(doc)["Units per pack"] == "1"]
    assert loose, f"no {key} is sold singly"
    for doc in loose:
        assert singular in doc["title"] and plural not in doc["title"], doc["title"]
        assert "Box of" not in doc["title"], doc["title"]
        assert doc["pricing_unit"] == "Each"


@pytest.mark.parametrize("key", KINDS)
def test_every_sku_publishes_its_length_and_its_gauge_or_thread(key):
    size = "Thread size" if key == "screw_machine" else "Gauge"
    docs = _docs(key)
    assert docs, f"the catalog sells no {key}"
    for doc in docs:
        facts = _facts(doc)
        assert facts["Length"] and facts[size], doc["sku"]
    assert any(_facts(doc)[size] in doc["title"] for doc in docs)


def test_a_product_varies_by_length_with_its_gauge_or_thread_and_pack():
    """Read from the large build: the committed catalog's few lines are mostly one size."""
    products: dict[str, list[dict]] = defaultdict(list)
    for doc in hundred_k_flat():
        if doc["product_type"] in KINDS:
            products[doc["product_id"]].append(_facts(doc))

    def varies(name: str) -> bool:
        return any(len({facts.get(name) for facts in p}) > 1 for p in products.values())

    assert varies("Length")
    assert varies("Gauge")
    assert varies("Thread size")
    assert varies("Units per pack")


def test_a_walk_past_the_end_of_a_size_carries_on_into_the_next():
    gen = SimpleNamespace(_rotate=lambda key, period: 1)
    pairs = [("#6", 1.0), ("#6", 1.5), ("#8", 1.0), ("#8", 2.0), ("#10", 3.0)]
    assert plain_screws._lengths_of_a_line(gen, "walk", pairs, 3) == [
        ("#6", 1.5),
        ("#8", 1.0),
        ("#8", 2.0),
    ]


def test_a_walk_never_lists_one_length_twice_and_wraps_to_fill_its_count():
    gen = SimpleNamespace(_rotate=lambda key, period: 2)
    pairs = [("#6", 0.5), ("#6", 1.0), ("#8", 1.0), ("#8", 2.0)]
    assert plain_screws._lengths_of_a_line(gen, "walk", pairs, 3) == [
        ("#8", 1.0),
        ("#8", 2.0),
        ("#6", 0.5),
    ]


@pytest.mark.parametrize("key", KINDS)
def test_no_line_lists_one_length_twice(key):
    for product in _products(key):
        lengths = [_facts(doc)["Length"] for doc in product]
        assert len(lengths) == len(set(lengths)), product[0]["product_id"]


@pytest.mark.parametrize(
    ("length_in", "quantity"),
    [(0.5, 200), (1.0, 200), (1.25, 100), (2.0, 100), (2.5, 50), (4.0, 50)],
)
def test_a_box_holds_fewer_of_a_longer_screw(length_in, quantity):
    assert plain_screws.box_of(length_in) == quantity


@pytest.mark.parametrize(("gauge", "inches"), [("#6", 0.138), ("#8", 0.164), ("#12", 0.216)])
def test_a_gauge_reads_as_its_major_diameter(gauge, inches):
    assert parse_gauge(gauge) == pytest.approx(inches)


@pytest.mark.parametrize("value", ["8", "#8-32", "M8", ""])
def test_a_value_that_is_no_gauge_is_refused(value):
    with pytest.raises(DimensionParseError):
        parse_gauge(value)


def _record(**facts: str) -> dict[str, str]:
    return {
        "Gauge": "#8",
        "Length": '2"',
        "Head Type": "Flat Head",
        "Drive Type": "Square",
        **facts,
    }


def test_a_countersunk_screw_is_drawn_its_published_length_overall():
    drawn = plain_screw(_record())
    assert drawn.source == "record"
    assert drawn.figure.size_in == pytest.approx(2.0)


def test_a_raised_head_is_drawn_above_its_published_length():
    head_height = HEADS["Pan"][1] * parse_gauge("#8")
    assert plain_screw(_record(**{"Head Type": "Pan Head"})).figure.size_in == pytest.approx(
        2.0 + head_height
    )


def test_a_machine_screw_is_drawn_from_its_thread():
    record = _record(**{"Thread Size": "1/4-20", "Length": '1"', "Head Type": "Pan Head"})
    del record["Gauge"]
    drawn = plain_screw(record)
    assert drawn.source == "record"
    assert drawn.figure.size_in == pytest.approx(1.0 + HEADS["Pan"][1] * 0.25)


@pytest.mark.parametrize("facts", [{"Gauge": "eight"}, {"Length": "long"}])
def test_a_value_that_does_not_parse_draws_nominal_and_says_so(facts):
    assert plain_screw(_record(**facts)).source == "partial"


def test_two_lines_in_three_are_sold_by_the_box_with_a_box_of_their_own():
    """A kind's own draft, so the rule is held apart from which SKUs the build happens to keep."""
    kind = plain_screws.DRYWALL
    gen = Generator(SMALL, kind.key)
    make = plain_screws.build(kind)
    drafts = [make(gen, kind.key, ("Fasteners",)) for _ in range(6)]
    assert [draft.item == kind.plural for draft in drafts].count(True) == 4
    for draft in drafts:
        for child in draft.children:
            pack = next(a.value for a in child.attrs if a.name == "Units per Pack")
            if draft.item == kind.plural:
                quantity = plain_screws.box_of(parse_length(child.also.value).inches)
                assert (child.pack_phrase, pack) == (f"Box of {quantity}", str(quantity))
            else:
                assert (draft.item, child.pack_phrase, pack) == (kind.item, "", "1")


def test_a_gauge_kind_and_a_thread_kind_each_publish_their_own_size():
    assert plain_screws.MACHINE.size_attribute == "Thread Size"
    assert plain_screws.WOOD.size_attribute == "Gauge"


def test_the_range_stays_small():
    """The issue asks for an everyday range, not a large new one: 1% of the catalog at most."""
    plain = [doc for key in KINDS for doc in _docs(key)]
    assert len(plain) <= RANGE_CAP * len(DOCS)


@pytest.mark.parametrize("word", ["Pan Head", "Flat Head", "Bugle Head"])
def test_the_head_a_shopper_names_is_in_a_title(word):
    assert any(word in doc["title"] for key in KINDS for doc in _docs(key))
