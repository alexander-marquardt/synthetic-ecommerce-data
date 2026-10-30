"""The sportswear brand is invented: Knacks and Breeze Max, not a real name (gen#722).

The maintainer's ruling (2026-10-30) replaces the 2026-10-15 one (gen#341): the 22 products that
sold under a real sportswear brand keep their ids, types, prices, colors and sizes under an
invented brand and invented line names, and the guard refuses the old names.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import real_brands, scale

#: Each former product by id, recorded from main before the rename: what gen#722 keeps.
PIN = json.loads((Path(__file__).parent / "data" / "knacks_722_products.json").read_text("utf-8"))
FORMER = ("Nike", "Air Max", "Pegasus", "Dri-FIT")
FORMER_WORD = re.compile(rf"(?<![a-z0-9])(?:{'|'.join(map(re.escape, FORMER))})(?![a-z0-9])", re.I)


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return scale.templates()


def _kept(doc: dict) -> dict:
    """What a former product keeps: the digest holds every SKU's id, color, size and price."""
    skus = sorted(doc["skus"], key=lambda s: s["sku"])
    return {
        "product_type": doc["product_type"],
        "category_path": doc["category_path"],
        "price": doc["price"],
        "colors": sorted({s["color"] for s in skus}),
        "skus": len(skus),
        "sku_digest": hashlib.sha256(json.dumps(skus, sort_keys=True).encode()).hexdigest(),
    }


def test_no_document_names_a_former_name_in_any_field(catalog) -> None:
    found = {d["product_id"]: FORMER_WORD.findall(json.dumps(d)) for d in catalog}
    assert {pid: names for pid, names in found.items() if names} == {}


def test_a_generated_catalogue_names_no_former_name() -> None:
    records = ceiling_build().records
    assert [r["product_id"] for r in records if FORMER_WORD.search(json.dumps(r))] == []


@pytest.mark.parametrize("name", FORMER)
@pytest.mark.parametrize("field", ["brand", "title", "description"])
def test_the_guard_refuses_a_former_name(name: str, field: str) -> None:
    doc = {"product_id": "X", "brand": "Wrenfield", "title": "Tee", "description": "A tee."}
    assert len(real_brands.check([{**doc, field: f"Fits {name} trainers"}])) == 1


def test_each_former_product_is_a_knacks_product_with_what_it_had(catalog) -> None:
    by_id = {d["product_id"]: d for d in catalog}
    assert {pid: by_id[pid]["brand"] for pid in PIN} == dict.fromkeys(PIN, "Knacks")
    assert {pid: _kept(by_id[pid]) for pid in PIN} == PIN


def test_no_other_product_is_a_knacks_product(catalog) -> None:
    assert {d["product_id"] for d in catalog if d["brand"] == "Knacks"} == set(PIN)
