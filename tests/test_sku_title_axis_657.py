"""A SKU title MAY carry the variant axis value, a product name NEVER does (#657).

The rule, stated once:

* **The product name** (``parent_title``) heads a whole product, and the product is every
  value of its axes. A name that said ``4-1/4" L`` would head a card that also holds the
  1" and the 2" screw. Pinned for every product with variants, industrial and retail.
* **A SKU title** may name the axis value but is not required to. A title without it is
  still found by its axis field (``variant_axes`` / ``facets``), which is what a shopper's
  selector reads. The generator therefore names it on most SKUs and leaves it off on some,
  and the share is held inside :data:`BAND` so it is neither always there (every title
  reads as a rewording of the selector) nor never there.
* **Separators**: a comma in a title is always followed by a space (``L, Alloy Steel``,
  never ``L,Alloy Steel``).

Each industrial property runs against the committed ``golden-catalog/`` and against a fresh
build (see ``test_catalog_titles.SOURCES`` for why both).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core.naming import states_value

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = ROOT / "golden-catalog"
RETAIL = ROOT / "prototypes" / "retail_drawings"

#: The share of industrial SKU titles (of products with variants) that state at least one of
#: their axis values. The generator targets 0.70 (``finishing.AXIS_IN_TITLE``): most titles
#: name the size, because a title that never did would read as a different product, and about
#: three in ten leave it to the axis field, the way a distributor's listing is uneven. The
#: band is wide enough that a re-seed (a spread of about one point over 8,500 SKUs) never
#: leaves it, and narrow enough that "always" (0.987 before this) and "never" both fail.
BAND = (0.60, 0.80)

#: A bare number inside a retail product name that is the model's own, and happens to equal
#: one value of an axis: ``(product name, axis key, value)``. The name does not state the
#: axis there ("SPF 50" is the sun factor, not 50 ml). Exact triples, so a new coincidence
#: is a new line in this list that someone has to read.
RETAIL_COINCIDENCES = {
    ("SPF 50 Face Sun Cream", "net_volume", "50"),
    ("Stridewell Speed 4 Neutral Road Running Shoes", "size_uk", "4"),
}

#: A comma not followed by a space; between two digits it is a thousands separator.
TIGHT_COMMA = re.compile(r"(?<!\d),(?!\s)|,(?!\s|\d)")

SOURCES = ("committed", "generated")


@pytest.fixture(scope="module", params=SOURCES)
def industrial(request) -> list[dict]:
    if request.param == "committed":
        with (GOLDEN_DIR / "flat.jsonl").open(encoding="utf-8") as handle:
            return [json.loads(line) for line in handle]

    from synthetic_ecommerce_data.core import emit
    from synthetic_ecommerce_data.core.config import GeneratorConfig
    from synthetic_ecommerce_data.domains.industrial.generate import generate

    return list(emit.iter_flat(generate(GeneratorConfig())))


@pytest.fixture(scope="module")
def retail() -> list[dict]:
    if str(RETAIL) not in sys.path:
        sys.path.insert(0, str(RETAIL))
    import export

    return export.flat_documents()


def _axis_values(doc: dict) -> list[tuple[str, str]]:
    """``(axis key, value)`` for every published value of each of the SKU's variant axes."""
    return [(axis, value) for axis in doc["variant_axes"] for value in doc["facets"].get(axis, [])]


Triple = tuple[str, str, str]


def _name_carries(docs: list[dict], exempt: set[Triple]) -> list[Triple]:
    found = {
        (doc["parent_title"], axis, value)
        for doc in docs
        for axis, value in _axis_values(doc)
        if states_value(doc["parent_title"], value)
    }
    return sorted(found - exempt)


def test_no_industrial_product_name_carries_the_value_of_one_of_its_axes(
    industrial: list[dict],
) -> None:
    assert sum(1 for doc in industrial if doc["variant_axes"]) > 1000
    carrying = _name_carries(industrial, set())
    assert carrying == [], f"{len(carrying)} product name(s) state an axis value: {carrying[:3]}"


def test_no_retail_product_name_carries_the_value_of_one_of_its_axes(retail: list[dict]) -> None:
    assert sum(1 for doc in retail if doc["variant_axes"]) > 1000
    carrying = _name_carries(retail, RETAIL_COINCIDENCES)
    assert carrying == [], f"{len(carrying)} product name(s) state an axis value: {carrying[:3]}"


def test_the_retail_coincidences_are_still_coincidences(retail: list[dict]) -> None:
    """An exemption that matches nothing any more is a stale line in :data:`RETAIL_COINCIDENCES`."""
    present = _name_carries(retail, set())
    assert set(present) == RETAIL_COINCIDENCES


def test_a_share_of_industrial_sku_titles_carry_an_axis_value_but_not_all(
    industrial: list[dict],
) -> None:
    with_axes = [doc for doc in industrial if doc["variant_axes"]]
    carrying = sum(
        1 for doc in with_axes if any(states_value(doc["title"], v) for _, v in _axis_values(doc))
    )
    share = carrying / len(with_axes)
    low, high = BAND
    assert low <= share <= high, (
        f"{carrying} of {len(with_axes)} SKU titles ({share:.3f}) state an axis value; "
        f"the band is {low}-{high}: neither always nor never"
    )


def test_some_lines_have_a_title_that_carries_the_axis_and_one_that_does_not(
    industrial: list[dict],
) -> None:
    """The mix is inside a product, not a split between products."""
    by_line: dict[str, set[bool]] = {}
    for doc in industrial:
        if doc["variant_axes"]:
            carries = any(states_value(doc["title"], v) for _, v in _axis_values(doc))
            by_line.setdefault(doc["product_id"], set()).add(carries)
    mixed = sum(1 for kinds in by_line.values() if len(kinds) == 2)
    assert mixed > len(by_line) * 0.2, f"only {mixed} of {len(by_line)} products mix both"


def test_an_industrial_title_comma_is_always_followed_by_a_space(industrial: list[dict]) -> None:
    tight = [doc["title"] for doc in industrial if TIGHT_COMMA.search(doc["title"])]
    assert tight == [], f"{len(tight)} title(s) have a comma with no space, e.g. {tight[:3]}"


def test_a_retail_title_comma_is_always_followed_by_a_space(retail: list[dict]) -> None:
    tight = [doc["title"] for doc in retail if TIGHT_COMMA.search(doc["title"])]
    assert tight == [], f"{len(tight)} title(s) have a comma with no space, e.g. {tight[:3]}"
