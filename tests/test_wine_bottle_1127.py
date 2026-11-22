"""A wine is drawn as its real bottle, filling the picture (gen#1127, slice 1).

Before gen#1127 every wine, port, sherry and vermouth shared the generic ``bottle`` shape, shrunk
by :mod:`pack_scale`, so a half bottle stood at 0.63 of the frame's height and covered about a
tenth of the product area. ``wine_bottle`` (:mod:`kit_drinks`) draws the style's own bottle
(Bordeaux, Burgundy, sparkling) at that size's real proportions, the line's largest at nearly the
product area's full height and a smaller size never below 0.8 of it. Cover is the share of the
house style's product area (``TURN_AREA``) the drawing paints, its ground shadow left out
(:mod:`sheet_cover`).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    grocery,
    kit,
    kit_drinks,
    pack_scale,
    sheet_cover,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import Fill

ARC = re.compile(r"[Aa]\s*[-\d.]")
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{}</svg>'
#: A 750ml covered at least 0.169 before gen#1127, a half bottle 0.104: every wine SKU now covers
#: at least ``FLOOR``, and a 750ml at least ``FLOOR_750``.
FLOOR, FLOOR_750 = 0.145, 0.170
#: The line's largest spans this share of the product area's height, a smaller size this share
#: of it.
FULL, STEP = 0.95, 0.8
#: The leaves of the eight wine families (``grocery.WINE_STYLES``).
LEAVES = {
    "Red Wine", "White Wine", "Rosé Wine", "Sparkling Wine", "Champagne", "Port", "Sherry",
    "Vermouth",
}  # fmt: skip


@pytest.fixture(scope="module")
def wines() -> list[tuple[dict, dict]]:
    rows = [
        (rec, sku)
        for rec in grocery.build(grocery.TARGET)
        if rec["category_path"][-1] in LEAVES
        for sku in rec["skus"]
    ]
    assert rows, "no wine record in the grocery build"
    return rows


def _svg(rec: dict, sku: dict) -> str:
    spec = export.drawing_spec(rec, sku)
    d = spec["drawing"]
    params = {**(d.get("params") or {}), **(spec.get("params") or {})}
    fill = Fill(d["pattern"], d["base"], d["accent"], d["third"])
    parts = kit._drawn(kit._draw(d["shape"]), d["base"], fill, d["label"], params)
    return SVG.format(kit._shrunk(parts, "".join(parts), spec.get("pack_scale", 1.0)))


def _bottle(svg: str) -> str:
    """The drawing without its ground shadow, which is no part of the bottle, and without a
    path drawn with arcs (a label's rounded panel): it lies inside the body, so it adds no cover,
    and :mod:`sheet_cover` reads no arc."""
    root = ET.fromstring(svg)
    for parent in list(root.iter()):
        dropped = [e for e in parent if e.get("class") == "ground" or ARC.search(e.get("d", ""))]
        for el in dropped:
            parent.remove(el)
    return ET.tostring(root, encoding="unicode")


def _span(svg: str) -> float:
    box = sheet_extent.reach(_bottle(svg))
    assert box is not None
    return (box[3] - box[1]) / (TURN_AREA[3] - TURN_AREA[1])


def test_every_wine_family_draws_the_wine_bottle() -> None:
    assert set(grocery.WINE_STYLES.values()) <= set(kit_drinks.STYLES)
    shapes = {
        r["category_path"][-1]: r["drawing"]["shape"]
        for r in grocery.build(grocery.TARGET)
        if r["category_path"][-1] in LEAVES
    }
    assert shapes == dict.fromkeys(LEAVES, "wine_bottle")


def test_a_wine_bottle_fills_the_product_area(wines: list[tuple[dict, dict]]) -> None:
    low = []
    for rec, sku in wines:
        share = sheet_cover.cover(_bottle(_svg(rec, sku)), TURN_AREA, step=2.0)
        floor = FLOOR_750 if sku["pack_size"] == "750ml" else FLOOR
        if share < floor:
            low.append(f"{rec['category_path'][-1]} {sku['pack_size']}: {share:.3f} < {floor}")
    assert not low, "\n".join(low)


def test_the_largest_spans_the_area_and_a_smaller_size_steps_down_a_little(
    wines: list[tuple[dict, dict]],
) -> None:
    short = []
    for rec, sku in wines:
        sizes = [s["pack_size"] for s in rec["skus"]]
        largest = max(sizes, key=kit_drinks.millilitres)
        span = _span(_svg(rec, sku))
        floor = FULL if sku["pack_size"] == largest else FULL * STEP
        if span < floor:
            short.append(f"{rec['category_path'][-1]} {sku['pack_size']} of {largest}: {span:.3f}")
    assert not short, "\n".join(short)


def test_a_smaller_size_is_drawn_shorter_than_the_largest() -> None:
    big = kit_drinks.drawn_height("bordeaux", "750ml", "750ml")
    half = kit_drinks.drawn_height("bordeaux", "375ml", "750ml")
    assert kit_drinks.MIN_SHARE * big <= half < big


def test_the_wine_shows_its_own_color_through_the_glass() -> None:
    def wine_fill(base: str) -> str:
        fill = Fill("solid", base, "#ffffff")
        svg = SVG.format("".join(kit_drinks.wine_bottle(base, fill, "Rioja", wine="red")))
        (el,) = [el for el in ET.fromstring(svg).iter() if el.get("class") == "wine"]
        return el.get("fill") or ""

    glass = kit_drinks.STYLES["red"].glass
    assert wine_fill("#5b1a3a") == kit_drinks.through_glass("#5b1a3a", glass)
    assert wine_fill("#5b1a3a") != wine_fill("#9a2b2b")


def test_the_shoulder_is_smooth_and_never_overshoots() -> None:
    """A monotone cubic: between two profile points the radius stays between them."""
    for form in kit_drinks.FORMS.values():
        for (t0, r0), (t1, r1) in zip(form.profile, form.profile[1:], strict=False):
            for i in range(1, 10):
                r = kit_drinks._radius(form, t0 + (t1 - t0) * i / 10)
                assert min(r0, r1) - 1e-9 <= r <= max(r0, r1) + 1e-9


def test_a_wine_bottle_takes_no_pack_scale_factor_and_a_spirit_keeps_its_bottle() -> None:
    recs = grocery.build(grocery.TARGET)
    wine = next(r for r in recs if r["category_path"][-1] in LEAVES and len(r["skus"]) > 1)
    assert all(pack_scale.factor(wine, sku) is None for sku in wine["skus"])
    whisky = [r for r in recs if r["category_path"][-1] == "Whisky"]
    assert whisky and all(r["drawing"]["shape"] == "bottle" for r in whisky)
    scaled = [pack_scale.factor(r, s) for r in whisky if len(r["skus"]) > 1 for s in r["skus"]]
    assert any(f is not None and f < 1 for f in scaled)
