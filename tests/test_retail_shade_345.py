"""Complexion products are sold by shade, never by color (gen#345).

A foundation, a concealer and a tinted moisturiser write their shade ("6N", "Porcelain") to a
``shade`` entry, and its ``shade_depth`` (fair, light, medium, tan, deep) and ``undertone``
(cool, neutral, warm) with it; they carry no ``color`` at all. So a clothing query that reads the
color facet no longer meets "6N", and "foundation for medium skin, warm undertone" has fields to
match. Lip, nail and eye products keep their ``color``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402

from synthetic_ecommerce_data.core import standard  # noqa: E402

#: The shade-code shape (depth 1-14, cool / neutral / warm): a color value never matches it.
CODE = re.compile(r"^\d{1,2}[CNW]$")
DEPTHS = {"fair", "light", "medium", "tan", "deep"}
UNDERTONES = {"cool", "neutral", "warm"}
#: The products sold by shade: the product types the issue names, and the tinted moisturiser.
BY_SHADE_TYPES = {"Foundation", "Concealer"}
TINTED_MOISTURISER = "BEA-TNTMST"


@pytest.fixture(scope="module")
def docs() -> list[dict[str, Any]]:
    return export.documents()


def _values(entries: list[dict[str, Any]], key: str) -> list[str]:
    return [e["value"] for e in entries if e["key"] == key]


def _by_shade(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = [
        d
        for d in docs
        if d["product_type"] in BY_SHADE_TYPES or d["product_id"] == TINTED_MOISTURISER
    ]
    assert len(out) >= 4, [d["product_id"] for d in out]
    return out


def _entries(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return doc["attributes"] + [e for v in doc["variants"] for e in v["attributes"]]


def test_no_color_value_is_a_shade_code(docs: list[dict[str, Any]]) -> None:
    bad = {
        (d["product_id"], v) for d in docs for v in _values(_entries(d), "color") if CODE.match(v)
    }
    assert sorted(bad) == []


def test_no_flat_color_value_is_a_shade_code(docs: list[dict[str, Any]]) -> None:
    flat = [row for d in docs for row in standard.flat_documents(d, export.NUMERIC_FACTS)]
    bad = {
        str(v)
        for row in flat
        for v in (row.get("facets", {}).get("color") or [])
        if CODE.match(str(v))
    }
    assert sorted(bad) == []


def test_a_complexion_product_has_no_color_at_all(docs: list[dict[str, Any]]) -> None:
    for d in _by_shade(docs):
        assert _values(_entries(d), "color") == [], d["product_id"]


def test_every_complexion_row_has_shade_depth_and_undertone(docs: list[dict[str, Any]]) -> None:
    for d in _by_shade(docs):
        for v in d["variants"]:
            for key in ("shade", "shade_depth", "undertone"):
                assert len(_values(v["attributes"], key)) == 1, (d["product_id"], v["sku"], key)
            assert _values(v["attributes"], "shade_depth")[0] in DEPTHS
            assert _values(v["attributes"], "undertone")[0] in UNDERTONES


def test_the_product_lists_the_shades_its_variants_sell(docs: list[dict[str, Any]]) -> None:
    for d in _by_shade(docs):
        sold = {s for v in d["variants"] for s in _values(v["attributes"], "shade")}
        assert sold and set(_values(d["attributes"], "shade")) == sold, d["product_id"]


@pytest.mark.parametrize(
    ("code", "depth", "undertone"),
    [
        ("1C", "fair", "cool"),
        ("2W", "fair", "warm"),
        ("3C", "light", "cool"),
        ("4N", "light", "neutral"),
        ("5N", "light", "neutral"),
        ("6N", "medium", "neutral"),
        ("8C", "medium", "cool"),
        ("9W", "tan", "warm"),
        ("11N", "tan", "neutral"),
        ("12W", "deep", "warm"),
        ("13C", "deep", "cool"),
        ("14N", "deep", "neutral"),
    ],
)
def test_a_code_derives_its_depth_and_undertone(
    docs: list[dict[str, Any]], code: str, depth: str, undertone: str
) -> None:
    variants = [
        v
        for d in _by_shade(docs)
        for v in d["variants"]
        if _values(v["attributes"], "shade") == [code]
    ]
    assert variants, code
    for v in variants:
        assert _values(v["attributes"], "shade_depth") == [depth], (v["sku"], code)
        assert _values(v["attributes"], "undertone") == [undertone], (v["sku"], code)


@pytest.mark.parametrize(
    ("name", "depth", "undertone"),
    [
        ("Porcelain", "fair", "neutral"),
        ("Caramel", "tan", "warm"),
        ("Toffee", "tan", "warm"),
        ("Espresso", "deep", "neutral"),
    ],
)
def test_a_named_shade_states_its_depth_and_undertone(
    docs: list[dict[str, Any]], name: str, depth: str, undertone: str
) -> None:
    soft_veil = next(d for d in docs if d["title"] == "Soft Veil Foundation")
    rows = [v for v in soft_veil["variants"] if _values(v["attributes"], "shade") == [name]]
    assert rows, name
    for v in rows:
        assert _values(v["attributes"], "shade_depth") == [depth], name
        assert _values(v["attributes"], "undertone") == [undertone], name


def test_an_unknown_shade_name_is_refused() -> None:
    import shades  # noqa: PLC0415 -- the prototype's own directory is its import root

    with pytest.raises(KeyError, match="neither a code"):
        shades.classify("Mocha")


def test_a_named_shade_is_kept_as_authored(docs: list[dict[str, Any]]) -> None:
    soft_veil = next(d for d in docs if d["title"] == "Soft Veil Foundation")
    shades = {s for v in soft_veil["variants"] for s in _values(v["attributes"], "shade")}
    assert shades == {"Porcelain", "Caramel", "Toffee", "Espresso"}


def test_shade_keys_are_declared_options() -> None:
    declared = {key for key, _name, _unit in export.OPTIONS.values()}
    assert {"shade", "shade_depth", "undertone"} <= declared


def test_a_foundation_is_picked_by_its_shade(docs: list[dict[str, Any]]) -> None:
    for d in _by_shade(docs):
        axes = [a for a in d["variant_axes"] if a != "net_volume"]
        assert axes == ["shade"], (d["product_id"], d["variant_axes"])


def test_lip_products_keep_their_color(docs: list[dict[str, Any]]) -> None:
    lips = [d for d in docs if d["product_type"] in {"Lipstick", "Lip Balm"}]
    assert lips
    for d in lips:
        assert _values(_entries(d), "color"), d["product_id"]
        assert _values(_entries(d), "shade_depth") == [], d["product_id"]
