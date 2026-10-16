"""Retail ``promotion`` replaces the boolean ``offer`` (gen#189).

``offer`` was true for a was-price or a multi-buy, and its facet showed "Offer: yes / no". A
shopper does not read "Offer" as "reduced", and a boolean cannot name a campaign. Now:

- a product with a ``was_price`` carries the keyword ``promotion`` value "On sale" (label "Sale");
- a product in the seeded campaign also carries its name; the campaign never replaces "On sale";
- a product with no ``was_price`` has no ``promotion`` key at all (no "no" value);
- no retail document, at any layer, has an ``offer`` key.

Checked at every layer a document passes through, as gen#186 and gen#277 do for the fields they
removed: the build records, the nested standard documents, the flat per-SKU documents, the
authored export, the exported field list (:data:`export.FACTS`) and the class docs.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_apparel  # noqa: E402 -- the prototype's own directory is its import root
import export  # noqa: E402 -- the prototype's own directory is its import root
import real_classes as rc  # noqa: E402
import scale  # noqa: E402

ON_SALE = "On sale"


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    """Every template, then a few thousand SKUs of derived styles."""
    return scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)


@pytest.fixture(scope="module")
def nested(built: scale.Scaled) -> list[dict[str, Any]]:
    return scale.documents(built)


@pytest.fixture(scope="module")
def authored() -> list[dict[str, Any]]:
    return export.documents()


def _values(doc: dict[str, Any], key: str) -> list[Any]:
    return [e["value"] for e in doc["attributes"] if e["key"] == key]


def _reduced(doc: dict[str, Any]) -> bool:
    return bool(_values(doc, "was_price"))


def test_the_corpus_holds_reduced_and_unreduced_products(authored: list[dict[str, Any]]) -> None:
    """Guard against a vacuous pass: both kinds are in the export the other tests read."""
    assert any(_reduced(d) for d in authored)
    assert any(not _reduced(d) for d in authored)


@pytest.mark.parametrize("layer", ["authored", "nested"])
def test_every_reduced_document_carries_on_sale(layer: str, request: Any) -> None:
    docs = request.getfixturevalue(layer)
    reduced = [d for d in docs if _reduced(d)]
    assert reduced
    assert [d["product_id"] for d in reduced if ON_SALE not in _values(d, "promotion")] == []


@pytest.mark.parametrize("layer", ["authored", "nested"])
def test_an_unreduced_document_has_no_promotion_key(layer: str, request: Any) -> None:
    docs = request.getfixturevalue(layer)
    plain = [d for d in docs if not _reduced(d)]
    assert plain
    assert [d["product_id"] for d in plain if _values(d, "promotion")] == []
    for d in plain:  # not on a SKU's own entries either
        own = [e for v in d["variants"] for e in v["attributes"] if e["key"] == "promotion"]
        assert own == [], d["product_id"]


def test_the_flat_documents_follow_the_nested_ones(nested: list[dict[str, Any]]) -> None:
    flat = scale.flat(nested)
    assert flat
    for row in flat:
        if "was_price" in row["facets"]:
            assert ON_SALE in row["facets"].get("promotion", []), row["product_id"]
        else:
            assert "promotion" not in row["facets"], row["product_id"]


def test_promotion_is_labelled_sale_and_holds_only_known_values(
    authored: list[dict[str, Any]],
) -> None:
    entries = [e for d in authored for e in d["attributes"] if e["key"] == "promotion"]
    assert entries
    assert {e["name"] for e in entries} == {"Sale"}
    assert {e["value"] for e in entries} <= {ON_SALE, export.CAMPAIGN}
    for d in authored:  # one entry per value
        values = _values(d, "promotion")
        assert len(values) == len(set(values)), d["product_id"]


def test_a_campaign_exists_and_every_carrier_also_carries_on_sale(
    authored: list[dict[str, Any]],
) -> None:
    carriers = [d for d in authored if export.CAMPAIGN in _values(d, "promotion")]
    assert carriers
    assert all(ON_SALE in _values(d, "promotion") for d in carriers)
    # a subset of the reduced products, so the demo shows both values
    assert len(carriers) < sum(_reduced(d) for d in authored)


def test_no_layer_carries_an_offer_key(
    built: scale.Scaled, nested: list[dict[str, Any]], authored: list[dict[str, Any]]
) -> None:
    assert [r["product_id"] for r in built.records if "offer" in r] == []
    for docs in (nested, authored):
        assert [d["product_id"] for d in docs if "offer" in d] == []
        assert [d["product_id"] for d in docs if _values(d, "offer")] == []
    assert [r["sku"] for r in scale.flat(nested) if "offer" in r["facets"]] == []
    assert "offer" not in export.FACTS
    assert "promotion" in export.FACTS
    assert export.FACTS["promotion"][:2] == ("promotion", "Sale")


def test_the_class_docs_and_their_mapping_follow(authored: list[dict[str, Any]]) -> None:
    docs = rc.class_docs()
    assert docs
    assert [d["product_id"] for d in docs if "offer" in d] == []
    for d in docs:
        if "was_price" in d:
            assert ON_SALE in d["promotion"], d["product_id"]
        else:
            assert "promotion" not in d, d["product_id"]
    props = rc.index_body()["mappings"]["properties"]
    assert "offer" not in props
    assert props.get("promotion") == {"type": "keyword"}


def test_a_decoy_clone_of_a_reduced_style_is_not_reduced() -> None:
    """A decoy is re-priced and drops the was-price, so it drops the promotion that follows it."""
    reduced = next(d for d in rc.class_docs() if "was_price" in d)
    assert "promotion" in reduced
    clone = decoy_apparel._clone(reduced, "ZZ", "Title", "Text", "Red", "#ff0000", "red")
    assert "was_price" not in clone
    assert "promotion" not in clone
