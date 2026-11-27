"""A sideboard ships in the retail build with products of its own (gen#1022 slice 5, Done-when 3).

Slices 1 to 4 drew the home types the issue names; none of them had a product. ``sideboard``
(slice 2's ``kit_storage_furniture`` shape) is now a retail type of its own,
``type_specs/sideboard.py``, and these tests hold its products in the ceiling build (the build
the release publishes, ``docs/releasing.md``) to the issue's two audits:

- **product split**: a product's SKUs agree on every product attribute and differ only in
  color, and no two products of one brand differ only in color;
- **non-copying**: no SKU's full attribute tuple and no SKU code is in the reference set
  :mod:`synthetic_ecommerce_data.core.noncopy` holds.
"""

from __future__ import annotations

import re
from collections import Counter

import pytest

from retail_ceiling import ceiling_build  # noqa: E402
from synthetic_ecommerce_data.core import noncopy
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import (
    image_release,
    picture_products,
    scale,
    type_registry,
)
from synthetic_ecommerce_data.domains.retail.type_specs import sideboard

#: The fields a sideboard SKU may carry: its code, its color, its price and its stock.
SKU_FIELDS = {"sku", "color", "price", "in_stock"}


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


@pytest.fixture(scope="module")
def sideboards(ceiling) -> list[dict]:
    """The sideboard rows and their derived styles; the wands-inspired sideboards (gen#1093)
    are ``tests/test_picture_products_ship_1093.py``'s."""
    pictured = picture_products.ids()
    return [
        r
        for r in ceiling.records
        if r["product_type"] == "Sideboard" and r["product_id"] not in pictured
    ]


def _attrs(rec: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in rec["attributes"]}


def split_problems(recs: list[dict]) -> list[str]:
    """The product-split audit: a SKU that carries more than its color, a color sold twice, and
    two products of one brand that differ only in color."""
    out = []
    for r in recs:
        extra = sorted({k for s in r["skus"] for k in s} - SKU_FIELDS)
        if extra:
            out.append(f"{r['product_id']}: a SKU carries {extra}, not only its color")
        twice = [c for c, n in Counter(s.get("color") for s in r["skus"]).items() if n > 1]
        if twice:
            out.append(f"{r['product_id']}: sells {twice} twice")
    seen: dict[tuple, str] = {}
    for r in recs:
        params = tuple(sorted((r["drawing"].get("params") or {}).items()))
        key = (r["brand"], tuple(sorted(_attrs(r).items())), params)
        if key in seen:
            out.append(f"{seen[key]} and {r['product_id']} are one product split by color")
        seen.setdefault(key, r["product_id"])
    return out


def copy_problems(recs: list[dict]) -> list[str]:
    """The non-copying audit: a SKU whose full attribute tuple or code is a reference one."""
    tuples, out = noncopy.reference_tuple_hashes(), []
    for r in recs:
        for s in r["skus"]:
            named = {a["name"]: str(a["value"]) for a in r["attributes"]}
            for merged in (named, named | {"Color": str(s.get("color"))}):
                if noncopy.fingerprint_mapping(merged) in tuples:
                    out.append(f"{s['sku']}: its attribute tuple is a reference one")
            if s["sku"] in noncopy.REFERENCE_SKUS:
                out.append(f"{s['sku']}: its code is a reference SKU")
    return out


def test_the_registry_holds_a_sideboard_type_under_home():
    spec = type_registry.specs()["sideboard"]
    assert (spec.department, spec.product_type) == ("Home", "Sideboard")
    assert len(spec.rows) >= 5
    assert {r.shape for r in spec.rows} == {"sideboard"}
    assert {r.path for r in spec.rows} == {("Home", "Furniture", "Sideboards")}
    assert len({r.brand for r in spec.rows}) >= 3


def test_the_ceiling_build_carries_every_sideboard_row_and_meets_the_output_standard(sideboards):
    rows = {r.product_id for r in sideboard.SPEC.rows}
    assert rows <= {r["product_id"] for r in sideboards}
    assert {tuple(r["category_path"]) for r in sideboards} == {sideboard.PATH}
    docs = scale.documents(scale.Scaled(sideboards, {}))
    assert check_catalog(docs, text_exempt=scale.TEXT_EXEMPT) == []


def test_the_templates_carry_them_too():
    rows = {r.product_id for r in sideboard.SPEC.rows}
    assert rows <= {r["product_id"] for r in scale.templates()}


def test_each_sku_draws_the_sideboard_shape_with_its_own_parts_in_its_color(sideboards):
    drawn = 0
    for r in sideboards:
        attrs = _attrs(r)
        for s in r["skus"]:
            d = image_release.colorway_drawing(r, s)
            assert d["shape"] == "sideboard", r["product_id"]
            assert d["params"]["doors"] == attrs["door_count"], r["product_id"]
            assert d["params"]["drawers"] == attrs["drawer_count"], r["product_id"]
            assert sideboard.BASES[d["params"]["legs"]] == attrs["base_style"], r["product_id"]
            svg = image_release.render(r, s).decode()
            assert len(re.findall(r'class="door"', svg)) == int(attrs["door_count"]), s["sku"]
            assert len(re.findall(r'class="drawer"', svg)) == int(attrs["drawer_count"]), s["sku"]
            assert d["base"].lower() in svg.lower(), s["sku"]
            drawn += 1
    assert drawn >= 10


def test_each_style_draws_a_picture_of_its_own(sideboards):
    pictures = {image_release.render(r, r["skus"][0], styled=False) for r in sideboards}
    assert len(pictures) == len(sideboards)


def test_the_sideboards_pass_the_product_split_audit(sideboards):
    assert split_problems(sideboards) == []


def test_the_product_split_audit_catches_a_product_split_by_color(sideboards):
    r = sideboards[0]
    twin = r | {
        "product_id": "BRD-SPLIT1",
        "skus": [s | {"sku": "BRD-SPLIT1-X"} for s in r["skus"][:1]],
    }
    assert split_problems([r, twin]) == [
        f"{r['product_id']} and BRD-SPLIT1 are one product split by color"
    ]
    sized = r | {"skus": [s | {"item_width": "90"} for s in r["skus"]]}
    assert split_problems([sized]) == [
        f"{r['product_id']}: a SKU carries ['item_width'], not only its color"
    ]


def test_the_sideboards_pass_the_non_copying_audit(sideboards):
    assert copy_problems(sideboards) == []


def test_the_non_copying_audit_catches_a_reference_tuple_and_a_reference_sku(
    sideboards, monkeypatch
):
    r = sideboards[0]
    named = {a["name"]: str(a["value"]) for a in r["attributes"]}
    planted = frozenset({noncopy.fingerprint_mapping(named)})
    monkeypatch.setattr(noncopy, "reference_tuple_hashes", lambda: planted)
    monkeypatch.setattr(noncopy, "REFERENCE_SKUS", frozenset({r["skus"][0]["sku"]}))
    found = copy_problems([r])
    assert f"{r['skus'][0]['sku']}: its code is a reference SKU" in found
    assert sum("attribute tuple is a reference one" in p for p in found) == len(r["skus"])
