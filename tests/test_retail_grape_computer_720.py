"""Grape Computer replaces Apple, iPhone and iPad (gen#720).

The maintainer's ruling (2026-10-30) replaces the one of 2026-10-15: the catalogue sells no invented
product under a real company's name. The ten devices keep their type, price, colors and specs under
``Grape Computer``, ``GrapePhone`` and ``GrapePad``, the accessories name the new lines, and the
fruit stays, so ``apple`` is a fruit word from here on and ``grape`` meets a brand and a fruit.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped.

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    build_preview,
    decoy_product_words,
    real_brands,
    scale,
)
from synthetic_ecommerce_data.domains.retail import house_styles as hs

GRAPE = "Grape Computer"
#: product id -> (line, type, price, colors, screen, connectivity, storage sizes), read from the
#: Apple rows before the rename.
FORMER_APPLE = {
    "BRD-EPH001": ("GrapePhone 15", "Smartphone", 799.0, ("Black", "Blue", "Gold", "Pink"), "6.1", "5G", ("128", "256", "512")),
    "BRD-EPH002": ("GrapePhone 15 Plus", "Smartphone", 899.0, ("Black", "Blue", "Green", "Pink"), "6.7", "5G", ("128", "256", "512")),
    "BRD-EPH003": ("GrapePhone 15 Pro", "Smartphone", 999.0, ("Black", "Blue", "Grey", "Silver"), "6.1", "5G", ("128", "256", "512")),
    "BRD-EPH004": ("GrapePhone 14", "Smartphone", 649.0, ("Black", "Blue", "Red", "White"), "6.1", "5G", ("128", "256")),
    "BRD-EPH005": ("GrapePhone 13", "Smartphone", 549.0, ("Black", "Blue", "Green", "Pink"), "6.1", "5G", ("128", "256")),
    "BRD-EPH006": ("GrapePhone SE", "Smartphone", 429.0, ("Black", "Red", "White"), "4.7", "5G", ("128", "256", "512")),
    "BRD-ETB001": ("GrapePad", "Tablet", 349.0, ("Blue", "Pink", "Silver", "White", "Yellow"), "10.9", None, ("128", "256", "64")),
    "BRD-ETB002": ("GrapePad Air", "Tablet", 599.0, ("Blue", "Gold", "Grey", "Purple"), "10.9", None, ("128", "256", "64")),
    "BRD-ETB003": ("GrapePad Pro", "Tablet", 1099.0, ("Black", "Silver"), "12.9", None, ("128", "256", "64")),
    "BRD-ETB004": ("GrapePad mini", "Tablet", 499.0, ("Gold", "Grey", "Pink", "Purple"), "8.3", None, ("128", "256", "64")),
}  # fmt: skip
FRUIT_IDS = ("PLT-DY716", "PLT-DY717", "PLT-DY718")


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def by_id(templates: list[dict]) -> dict[str, dict]:
    return {d["product_id"]: d for d in templates}


def _text(d: dict) -> str:
    values = [str(a["value"]) for a in d["attributes"]]
    return " ".join([d["brand"], d["title"], d["description"], *values])


def _attrs(d: dict) -> dict[str, str]:
    return {a["key"]: str(a["value"]) for a in d["attributes"]}


def test_no_document_has_brand_apple_or_names_iphone_or_ipad(templates: list[dict]) -> None:
    assert [d["product_id"] for d in templates if d["brand"] == "Apple"] == []
    named = [d["product_id"] for d in templates if re.search("iphone|ipad", _text(d), re.I)]
    assert named == []


def test_the_guard_refuses_the_brand_apple_and_passes_the_fruit() -> None:
    assert real_brands.check([{"product_id": "x", "brand": "Apple", "title": "A Phone"}]) == [
        "x: brand names the real brand 'Apple'"
    ]
    juice = {
        "product_id": "y",
        "brand": "Pantry Mill",
        "title": "Pressed Apple Juice, 1 L",
        "description": "Cloudy juice from pressed apples, in a carton.",
    }
    assert real_brands.check([juice]) == []


@pytest.mark.parametrize("name", ["iPhone", "iPad"])
@pytest.mark.parametrize("field", ["brand", "title", "description"])
def test_the_guard_refuses_a_former_line_name_in_every_field(name: str, field: str) -> None:
    assert name not in real_brands.ALLOWED
    assert len(real_brands.check([{"product_id": "x", field: f"Case for {name} 15"}])) == 1


def test_the_real_brand_exceptions_lose_apple_and_keep_nike() -> None:
    assert not {"Apple", "iPhone", "iPad"} & set(real_brands.ALLOWED)
    assert "Nike" in real_brands.ALLOWED


@pytest.mark.parametrize("product_id", sorted(FORMER_APPLE))
def test_a_former_apple_product_keeps_its_type_price_colors_and_specs(
    by_id: dict[str, dict], product_id: str
) -> None:
    line, ptype, price, colors, screen, connectivity, storage = FORMER_APPLE[product_id]
    d = by_id[product_id]
    attrs = _attrs(d)
    assert d["brand"] == GRAPE
    assert d["title"] == f"{line} {ptype}"
    assert (d["product_type"], d["price"]) == (ptype, price)
    assert tuple(sorted({s["color"] for s in d["skus"]})) == colors
    assert tuple(sorted({s["storage_gb"] for s in d["skus"]})) == storage
    assert (attrs["model_line"], attrs["operating_system"]) == (line, "Grape OS")
    assert (attrs["screen_size"], attrs.get("connectivity")) == (screen, connectivity)


def test_an_accessory_names_the_new_line_it_fits(templates: list[dict]) -> None:
    fits = {_attrs(d).get("compatible_with", "") for d in templates}
    assert {"GrapePhone 15", "GrapePhone SE", "GrapePad Air"} <= fits
    titles = {d["title"] for d in templates}
    assert "Clear Case for GrapePhone 15" in titles


def test_grape_meets_a_brand_and_a_fruit(templates: list[dict]) -> None:
    grape = [d for d in templates if "grape" in re.findall(r"[a-z]+", _text(d).lower())]
    assert {d["product_type"] for d in grape} >= {"Smartphone", "Tablet", "Juice"}
    assert sum(d["brand"] == GRAPE for d in grape) == len(FORMER_APPLE)


def test_the_fruit_rows_stay_and_are_no_decoys(by_id: dict[str, dict]) -> None:
    assert [by_id.get(i, {}).get("title") for i in FRUIT_IDS] == [
        "Pressed Apple Juice, 1 L",
        "Apple Blossom Candle",
        "Crab Apple Tree, Potted",
    ]
    assert not any(decoy_product_words.BY_ID[i].decoy for i in FRUIT_IDS)
    assert [r.code for r in decoy_product_words.TABLE if "apple" in r.query.split()] == []


def test_grape_computer_draws_a_mark_no_other_brand_uses(by_id: dict[str, dict]) -> None:
    assert GRAPE in hs.HOUSE_STYLES
    mark = hs.HOUSE_STYLES[GRAPE].mark
    assert mark != hs.NO_MARK
    assert [b for b, s in hs.HOUSE_STYLES.items() if s.mark == mark] == [GRAPE]
    brand_layer = build_preview.drawing_svg(by_id["BRD-EPH001"]).split('<g class="brand">', 1)[1]
    assert 'class="mark"' in brand_layer
