"""Every people department carries a share of reduced products (gen#359).

Only Womens products were reduced: 1,585 SKUs of the seed-0 ceiling build, all on styles a template
authored, and no Mens, Kids or Baby one. Since prism-industrial-products#250 made the ``sale`` word
the exact on-offer filter (``promotion`` = "On sale", gen#189), "mens sale shirts" and "kids sale
shoes" found nothing. The ask: at least a few hundred products carry the sale marker in each of
Womens, Mens, Kids and Baby, across at least three product types each.

The wanted numbers are written out here on purpose, as the issue states them; the test does not
read the module that makes the share. A product is a SKU (one flat document each), as in the
loaded catalogue the issue measured.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import sale_share  # noqa: E402 -- the prototype's own directory is its import root
import scale  # noqa: E402

ON_SALE = "On sale"
#: "At least a few hundred products ... across at least three product types each" (the issue).
FEW_HUNDRED = 300
THREE_TYPES = 3
#: A share, not a clearance: no department puts more than this fraction of its SKUs on sale.
MOST_ON_SALE = 0.4
GROUPS = ("Womens", "Mens", "Kids", "Baby")


@pytest.fixture(scope="module")
def nested() -> list[dict[str, Any]]:
    return scale.documents(scale.build(10_000_000))


@pytest.fixture(scope="module")
def rows(nested: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return scale.flat(nested)


def _group(row: dict[str, Any]) -> str | None:
    """The department of the issue: Baby is the audience, Kids the other Kids-root SKUs."""
    audience = (row["facets"].get("audience") or [None])[0]
    root = row["category_path"][0]
    if audience == "Baby":
        return "Baby"
    return root if root in ("Womens", "Mens", "Kids") else None


def _values(doc: dict[str, Any], key: str) -> list[Any]:
    return [e["value"] for e in doc["attributes"] if e["key"] == key]


def test_the_groups_are_not_empty_so_the_shares_below_are_not_vacuous(
    rows: list[dict[str, Any]],
) -> None:
    seen = collections.Counter(g for r in rows if (g := _group(r)))
    assert sorted(seen) == sorted(GROUPS)
    assert min(seen.values()) > 4 * FEW_HUNDRED


@pytest.mark.parametrize("group", GROUPS)
def test_each_department_has_a_few_hundred_reduced_skus_across_three_types(
    group: str, rows: list[dict[str, Any]]
) -> None:
    reduced = [
        r for r in rows if _group(r) == group and ON_SALE in r["facets"].get("promotion", [])
    ]
    assert len(reduced) >= FEW_HUNDRED, len(reduced)
    types = {r["product_type"] for r in reduced}
    assert len(types) >= THREE_TYPES, sorted(types)


@pytest.mark.parametrize("group", GROUPS)
def test_a_department_is_not_mostly_on_sale(group: str, rows: list[dict[str, Any]]) -> None:
    own = [r for r in rows if _group(r) == group]
    reduced = [r for r in own if ON_SALE in r["facets"].get("promotion", [])]
    assert len(reduced) / len(own) < MOST_ON_SALE


def test_derived_styles_are_reduced_too_not_only_the_authored_ones(
    nested: list[dict[str, Any]],
) -> None:
    """A derived style drops its template's was-price; a share of them is reduced again."""
    authored = {t["product_id"] for t in scale.templates()}
    derived = [d for d in nested if d["product_id"] not in authored]
    reduced = [d for d in derived if ON_SALE in _values(d, "promotion")]
    assert len(derived) > 1000
    assert len(reduced) >= 100, len(reduced)


def test_a_reduced_document_is_marked_the_same_way_whoever_made_it(
    nested: list[dict[str, Any]],
) -> None:
    """The gen#189 rule on the whole ceiling build, not only the authored export: a was-price
    sits over the price, the discount follows from the two, and "On sale" goes with the was-price
    and with nothing else."""
    bad: list[str] = []
    for d in nested:
        was = _values(d, "was_price")
        discount = _values(d, "discount")
        promo = _values(d, "promotion")
        if not was:
            if discount or promo:
                bad.append(d["product_id"])
            continue
        was_price = float(was[0])
        cheapest = min(s["price"] for s in d["variants"])
        want = [round(100 * (was_price - cheapest) / was_price)]
        if not (was_price > cheapest and ON_SALE in promo) or [int(x) for x in discount] != want:
            bad.append(d["product_id"])
    assert bad == []


def test_every_sku_of_a_reduced_style_is_priced_under_its_was_price(
    nested: list[dict[str, Any]],
) -> None:
    """The sale filter is ``price < was_price`` (gen#359): the was-price states the dearest size's
    price, not only the cheapest's, so no SKU of a reduced style is at or over it."""
    bad = [
        (d["product_id"], v["sku"])
        for d in nested
        if (was := _values(d, "was_price"))
        for v in d["variants"]
        if v["price"] >= float(was[0])
    ]
    assert bad == [], len(bad)


def test_no_planted_row_carries_a_was_price() -> None:
    """A failure-class or planted-distractor row keeps its price (gen#359)."""
    sections = scale.samples()
    planted = {d["product_id"] for k in scale.PLANTED_SECTIONS for d in sections[k]}
    reduced = {t["product_id"] for t in scale.templates() if "was_price" in t}
    authored = {d["product_id"] for k in scale.PLANTED_SECTIONS for d in sections[k]
                if "was_price" in d}
    assert (planted & reduced) <= authored


@pytest.mark.parametrize(
    ("size_range", "title"),
    [
        (["petite"], "Wrap Midi Dress"),
        (["regular"], "Petite Wrap Midi Dress"),
        (["regular"], "Wrap Midi Dress"),
    ],
)
def test_a_petite_style_is_never_in_the_share_a_regular_one_may_be(
    size_range: list[str], title: str
) -> None:
    """"Petite sale" stays a pair only a policy may honour (gen#125, gen#275): a style that is
    petite by its size range, or says so in its title, is not eligible."""
    rec = {
        "product_id": "PLT-X",
        "category_path": ["Womens", "Dresses", "Wrap dresses"],
        "attributes": [],
        "title": title,
        "description": "A dress.",
        "size_range": size_range,
    }
    assert sale_share.eligible(rec) is (title == "Wrap Midi Dress" and size_range == ["regular"])
