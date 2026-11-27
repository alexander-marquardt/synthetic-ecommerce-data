"""A chocolate pack carries its brand's mark and colors, its flavour the accent (gen#1125).

Before this, every wrapper was the flavour's color, so two brands' Milk bars drew one brown
wrapper and the brand showed only in the sheet's frame. Each pack is now printed in its brand's
color (``chocolate_brands.LOOKS``) with the brand's own house mark on it and the flavour's color
as an accent. Read through ``image_release.render`` of the built products, as they are served.
"""

from __future__ import annotations

import functools
import itertools
import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    chocolate_brands,
    export,
    grocery,
    image_release,
    kit,
    kit_chocolate,
    scale,
    sheet_cover,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.chocolate_brands import LOOKS, SHAPES
from synthetic_ecommerce_data.domains.retail.house_marks import MARKS
from synthetic_ecommerce_data.domains.retail.house_styles import HOUSE_STYLES, TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import Fill

FLOOR = 0.5


@functools.lru_cache(maxsize=1)
def _records() -> tuple[dict, ...]:
    """Every chocolate product: the grocery build's, and the hand-written rows' (gen#1125's
    cherries, coated fruit, calendar and white and dark bars)."""
    recs = [*grocery.build(grocery.TARGET), *scale.build(100_000).records]
    chocolates = (r for r in recs if r["drawing"]["shape"] in SHAPES)
    return tuple({r["product_id"]: r for r in chocolates}.values())


def _svg(rec: dict, sku: dict) -> str:
    return image_release.render(rec, sku, styled=False).decode()


def _wrapper(svg: str) -> str:
    return re.search(r'class="wrapper"[^>]*? fill="([^"]+)"', svg)[1]


def _mark(brand: str) -> str:
    """The brand's house mark as its packs draw it."""
    return "".join(MARKS[HOUSE_STYLES[brand].mark](LOOKS[brand].wrapper))


def _milk_bars() -> dict[str, str]:
    """Each brand's 100g Milk bar."""
    bars: dict[str, str] = {}
    for rec in _records():
        for sku in rec["skus"]:
            milk = rec["product_id"].startswith("GRC-CHB-") and sku["flavor"] == "Milk"
            if milk and sku["pack_size"] == "100g":
                bars.setdefault(rec["brand"], _svg(rec, sku))
    return bars


def test_two_brands_milk_bars_draw_different_wrappers_each_with_its_own_mark() -> None:
    bars = _milk_bars()
    assert len(bars) == 4
    for (one, a), (two, b) in itertools.combinations(bars.items(), 2):
        assert _wrapper(a) != _wrapper(b), f"{one} and {two} draw one wrapper"
    for brand, svg in bars.items():
        assert _wrapper(svg) == LOOKS[brand].wrapper
        assert [b for b in bars if _mark(b) in svg] == [brand]


def test_every_chocolate_pack_carries_its_brands_mark_color_and_flavour_accent() -> None:
    assert {r["drawing"]["shape"] for r in _records()} == SHAPES
    for rec in _records():
        svg = _svg(rec, rec["skus"][0])
        where = f"{rec['product_id']} {rec['drawing']['shape']} {rec['brand']}"
        assert svg.count('<g class="brand-mark">') == 1, where
        assert _mark(rec["brand"]) in svg, where
        assert _wrapper(svg) == LOOKS[rec["brand"]].wrapper, where
        accents = re.findall(r'class="accent"[^>]*? (?:fill|stroke)="(#[0-9a-f]{6})"', svg)
        assert rec["drawing"]["base"] in accents, where


def test_every_brand_of_a_chocolate_has_a_look_no_other_reads_like() -> None:
    assert {r["brand"] for r in _records()} == set(LOOKS)
    for one, two in itertools.combinations(LOOKS.values(), 2):
        channels = [[int(c.wrapper[i : i + 2], 16) for i in (1, 3, 5)] for c in (one, two)]
        assert sum(abs(a - b) for a, b in zip(*channels, strict=True)) >= 90, (one, two)
    for look in LOOKS.values():
        assert kit_chocolate.wrapper_color(look.wrapper) == look.wrapper, look


def test_a_branded_pack_fills_half_its_product_area_and_stays_on_its_sheet() -> None:
    seen = set()
    for rec in _records():
        for sku in rec["skus"]:
            d = image_release.colorway_drawing(rec, sku)
            key = (d["shape"], rec["brand"], d["params"].get("pack_size"), d["params"].get("piece"))
            if key in seen:
                continue
            seen.add(key)
            own = {k: v for k, v in d["params"].items() if k not in kit.MARK_KEYS}
            assert own.get("brand") == rec["brand"], key
            fill = Fill("solid", d["base"], d["accent"])
            parts = kit.shapes()[d["shape"]](d["base"], fill, d["label"], **own)
            body = "".join(parts)
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{body}</svg>'
            assert sheet_cover.cover(svg, TURN_AREA, step=4.0, skip=("ground",)) >= FLOOR, key
            x0, y0, x1, y1 = sheet_extent.reach(svg)
            assert min(x0, y0) >= 0 and max(x1, y1) <= 400, (key, x0, y0, x1, y1)


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_a_pack_of_no_brand_keeps_its_flavours_color_and_carries_no_mark(shape: str) -> None:
    base = "#b07a3c"
    body = "".join(kit.shapes()[shape](base, Fill("solid", base, "#ffffff"), "Chocolate"))
    assert "brand-mark" not in body and 'class="accent"' not in body
    assert _wrapper(body) == kit_chocolate.wrapper_color(base)


def test_the_drawing_id_names_the_brand_and_a_shape_of_another_kind_none() -> None:
    rec = next(r for r in _records() if r["drawing"]["shape"] == "chocolate_bar")
    spec = export.drawing_spec(rec, rec["skus"][0])
    assert spec["params"].get("brand") == rec["brand"]
    other = rec | {"drawing": rec["drawing"] | {"shape": "bar"}}
    assert chocolate_brands.params(other) == {}
    assert chocolate_brands.params(rec | {"brand": "Nobody"}) == {}
