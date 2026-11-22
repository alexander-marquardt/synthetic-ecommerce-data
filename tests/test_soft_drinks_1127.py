"""A soft drink is drawn as its real can or bottle, a multipack as its cans (gen#1127, slice 2).

Before gen#1127 every soft drink (SFT, GNB ginger and root beer) drew the generic ``bottle``,
shrunk by :mod:`pack_scale`, and a 6 x 330ml was six copies of that bottle. ``soft_drink``
(:mod:`kit_soft_drinks`) draws a PET bottle, a glass bottle or ring-pull cans from the SKU's own
pack and flavor. Cover is the share of the house style's product area (``TURN_AREA``) the
drawing paints, its ground shadow left out (:mod:`sheet_cover`), as the wine test measures it.
"""

# ruff: noqa: E501 -- one drawing call per line reads better whole than wrapped.

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    grocery,
    kit,
    kit_soft_drinks,
    pack_copies,
    pack_scale,
    sheet_cover,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import Fill

ARC = re.compile(r"[Aa]\s*[-\d.]")
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{}</svg>'


def _svg(rec: dict, sku: dict) -> str:
    """The SKU's drawing on the plain sheet, with its own params and any pack factor."""
    spec = export.drawing_spec(rec, sku)
    d = spec["drawing"]
    params = {**(d.get("params") or {}), **(spec.get("params") or {})}
    fill = Fill(d["pattern"], d["base"], d["accent"], d["third"])
    parts = kit._drawn(kit._draw(d["shape"]), d["base"], fill, d["label"], params)
    return SVG.format(kit._shrunk(parts, "".join(parts), spec.get("pack_scale", 1.0)))


def _bottle(svg: str) -> str:
    """The drawing without its ground shadow and without a path drawn with arcs (a label wrapped
    round the glass: it lies inside the body, and :mod:`sheet_cover` reads no arc)."""
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


#: Each single's cover on main 23ccb28c (the generic bottle at its pack_scale factor): no SKU
#: of that pack covers less now.
BEFORE = {"500ml": 0.105, "1.5L": 0.220, "1L": 0.170, "330ml": 0.093}
#: A can and a multipack of cans paint at least this share of the product area.
CAN_FLOOR = 0.50
#: The line's largest single spans this share of the area's height, a smaller one this share
#: of it (the wine bottle's floors).
FULL, STEP = 0.95, 0.8


@pytest.fixture(scope="module")
def drinks() -> list[tuple[dict, dict]]:
    rows = [
        (rec, sku)
        for rec in grocery.build(grocery.TARGET)
        if rec["product_type"] == "Soft Drink"
        for sku in rec["skus"]
    ]
    assert rows, "no soft drink in the grocery build"
    return rows


def _cover(svg: str) -> float:
    return sheet_cover.cover(_bottle(svg), TURN_AREA, step=2.0)


def _classes(svg: str, name: str) -> list[ET.Element]:
    return [el for el in ET.fromstring(svg).iter() if el.get("class") == name]


def _single(pack: str) -> bool:
    return " x " not in pack


def test_every_soft_drink_draws_the_soft_drink_shape(drinks: list[tuple[dict, dict]]) -> None:
    assert {rec["drawing"]["shape"] for rec, _ in drinks} == {"soft_drink"}
    flavors = {sku["flavor"] for _, sku in drinks}
    assert flavors <= set(kit_soft_drinks.LIQUIDS)


def test_every_pack_fills_no_less_than_before_and_a_multipack_half(
    drinks: list[tuple[dict, dict]],
) -> None:
    low = []
    for rec, sku in drinks:
        pack = sku["pack_size"]
        share = _cover(_svg(rec, sku))
        floor = BEFORE[pack] if _single(pack) else CAN_FLOOR
        if share < floor:
            low.append(f"{rec['product_id']} {pack}: {share:.3f} < {floor}")
    assert not low, "\n".join(low)


def test_the_largest_single_spans_the_area_and_a_smaller_one_steps_down_a_little(
    drinks: list[tuple[dict, dict]],
) -> None:
    short = []
    for rec, sku in drinks:
        singles = [s["pack_size"] for s in rec["skus"] if _single(s["pack_size"])]
        if not _single(sku["pack_size"]):
            continue
        largest = max(singles, key=kit_soft_drinks.millilitres)
        span = _span(_svg(rec, sku))
        floor = FULL if sku["pack_size"] == largest else FULL * STEP
        if span < floor:
            short.append(f"{rec['product_id']} {sku['pack_size']} of {largest}: {span:.3f}")
    assert not short, "\n".join(short)


def test_a_multipack_draws_its_count_of_cans_and_no_copies(drinks: list[tuple[dict, dict]]) -> None:
    packs = [(rec, sku) for rec, sku in drinks if not _single(sku["pack_size"])]
    assert packs
    for rec, sku in packs:
        n = int(sku["pack_size"].split(" x ")[0])
        svg = _svg(rec, sku)
        assert len(_classes(svg, "can")) == n == sku["units_per_pack"]
        assert len(_classes(svg, "ring-pull")) == n
        assert "pack_count" not in export.drawing_spec(rec, sku)


def test_a_330ml_single_is_a_glass_bottle_in_a_ginger_beer_line_and_a_can_elsewhere() -> None:
    fill = Fill("solid", "#3b1c10", "#ffffff")
    glass = SVG.format("".join(kit_soft_drinks.soft_drink("#d9b26a", fill, "Ginger Beer", flavor="Ginger Beer", pack_size="330ml", largest="1L", small="glass")))  # fmt: skip
    assert _classes(glass, "bottle") and _classes(glass, "drink") and not _classes(glass, "can")
    can = SVG.format("".join(kit_soft_drinks.soft_drink("#3b1c10", fill, "Cola", flavor="Cola", pack_size="330ml", largest="1.5L")))  # fmt: skip
    assert len(_classes(can, "can")) == 1 and _classes(can, "ring-pull")
    assert _cover(can) >= CAN_FLOOR


@pytest.mark.parametrize("pack", ["4 x 440ml", "4 x 500ml", "6 x 330ml"])
def test_any_multipack_of_cans_fills_half_the_area(pack: str) -> None:
    fill = Fill("solid", "#3b1c10", "#ffffff")
    svg = SVG.format("".join(kit_soft_drinks.soft_drink("#3b1c10", fill, "Cola", flavor="Cola", pack_size=pack)))  # fmt: skip
    assert len(_classes(svg, "can")) == int(pack.split(" x ")[0])
    assert _cover(svg) >= CAN_FLOOR


def test_each_flavor_shows_its_own_drink_through_the_bottle(
    drinks: list[tuple[dict, dict]],
) -> None:
    seen: dict[str, str] = {}
    for rec, sku in drinks:
        if sku["pack_size"] != "500ml":
            continue
        (drink,) = _classes(_svg(rec, sku), "drink")
        assert drink.get("fill") == kit_soft_drinks.through_clear(
            kit_soft_drinks.LIQUIDS[sku["flavor"]]
        )
        seen[sku["flavor"]] = drink.get("fill") or ""
    assert len(seen) > 1 and len(set(seen.values())) == len(seen)


def test_a_soft_drink_takes_no_pack_scale_factor_and_draws_its_own_pack(
    drinks: list[tuple[dict, dict]],
) -> None:
    assert "soft_drink" in pack_scale.SELF_SIZED
    assert all(pack_scale.factor(rec, sku) is None for rec, sku in drinks)
    rec, _ = drinks[0]
    assert pack_copies.self_drawn(rec, 6)
    assert kit.SHAPES["soft_drink"] is kit_soft_drinks.soft_drink
