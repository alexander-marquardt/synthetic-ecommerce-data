"""The hand-written beers, wines and soft drinks draw their real can or bottle (gen#1127).

The grocery build's drinks moved to ``beer`` and ``soft_drink`` first; the five rows of
:mod:`class_rows` (class 10, "beer") still drew the generic ``tin`` and ``bottle``, a 1.5L root
beer as a tin. Such a row sells its sizes as ``net_volume_ml``, so its SKU's container comes from
that. The six one-size drinks of :mod:`color_word_brand_rows` and the plural decoys followed:
two red wines, three sparkling waters and a wheat beer. Cover and height span are measured as the
soft drinks test measures them.
"""

from __future__ import annotations

import pytest

from retail_templates import templates as shared_templates
from synthetic_ecommerce_data.domains.retail import (
    class_rows,
    kit_beer,
    kit_drinks,
    kit_soft_drinks,
    pack_scale,
)
from synthetic_ecommerce_data.domains.retail.kit import Fill
from test_soft_drinks_1127 import _classes, _cover, _span, _svg

#: (style code, ml) -> the container that size is sold in.
CONTAINERS = {
    ("BRTROP", 440): "can",
    ("BRTABL", 330): "can",
    ("BRWHET", 330): "bottle",
    ("BRWHET", 500): "bottle",
    ("BRWHET", 750): "bottle",
    ("GNGBER", 200): "glass",
    ("GNGBER", 330): "glass",
    ("GNGBER", 1000): "pet",
    ("RTBEER", 330): "can",
    ("RTBEER", 500): "pet",
    ("RTBEER", 1500): "pet",
}
#: The cover each size had on main f30d5748, where it stood smaller than the frame. A size that
#: filled the frame as the generic bottle (0.269) covers less at its real proportions.
BEFORE = {
    ("BRWHET", 330): 0.154,
    ("BRWHET", 500): 0.201,
    ("GNGBER", 200): 0.093,
    ("GNGBER", 330): 0.126,
}
#: A 330ml can covers half the area, a 440ml can what its slimmer outline holds, and a bottle
#: that is its line's largest at least this share of the area (the grocery drinks' floors).
CAN = {330: 0.50, 440: 0.38}
LARGEST = 0.20
FULL, STEP = 0.95, 0.8


def _rows() -> list[tuple[str, dict, dict, int]]:
    styles = [*class_rows.BEERS, *(style for style, _ in class_rows.NOT_BEER)]
    codes = {code for code, _ in CONTAINERS}
    out = []
    for style in styles:
        if style.code not in codes:
            continue
        rec = style.doc()
        for sku in rec["skus"]:
            out.append((style.code, rec, sku, int(sku.get("net_volume_ml") or rec["unit_size"])))
    assert {(code, ml) for code, _, _, ml in out} == set(CONTAINERS)
    return out


@pytest.fixture(scope="module")
def rows() -> list[tuple[str, dict, dict, int]]:
    return _rows()


def _largest(code: str) -> int:
    return max(ml for c, ml in CONTAINERS if c == code)


def test_each_hand_written_drink_draws_the_container_its_size_is_sold_in(
    rows: list[tuple[str, dict, dict, int]],
) -> None:
    for code, rec, sku, ml in rows:
        want = CONTAINERS[(code, ml)]
        svg = _svg(rec, sku)
        shape = "beer" if rec["product_type"] == "Beer" else "soft_drink"
        assert rec["drawing"]["shape"] == shape, code
        assert len(_classes(svg, "can" if want == "can" else "bottle")) == 1, (code, ml)
        assert len(_classes(svg, "ring-pull")) == (want == "can"), (code, ml)
        assert len(_classes(svg, "foot")) == (want == "pet"), (code, ml)


def test_each_hand_written_drink_covers_its_floor_and_spans_the_height(
    rows: list[tuple[str, dict, dict, int]],
) -> None:
    low = []
    for code, rec, sku, ml in rows:
        svg = _svg(rec, sku)
        form, top = CONTAINERS[(code, ml)], ml == _largest(code)
        floor = CAN[ml] if form == "can" else LARGEST if top else 0.0
        floor = max(floor, BEFORE.get((code, ml), 0.0))
        tall = FULL if form == "can" or top else FULL * STEP
        if _cover(svg) < floor or _span(svg) < tall:
            low.append(f"{code} {ml}ml: {_cover(svg):.3f} < {floor} or {_span(svg):.2f} < {tall}")
    assert not low, "\n".join(low)


def test_each_hand_written_drink_shows_its_own_color_and_its_label(
    rows: list[tuple[str, dict, dict, int]],
) -> None:
    liquid = {"GNGBER": "Fiery Ginger Beer", "RTBEER": "Root Beer"}
    for code, rec, sku, ml in rows:
        svg, form = _svg(rec, sku), CONTAINERS[(code, ml)]
        base = rec["drawing"]["base"]
        color = kit_soft_drinks.LIQUIDS[liquid[code]] if code in liquid else base
        if form == "can":
            want = color
        elif rec["product_type"] == "Beer":
            want = kit_beer.through(color, "brown")
        else:
            want = kit_soft_drinks.through_clear(color)
        (drink,) = _classes(svg, "livery" if form == "can" else "drink")
        assert drink.get("fill") == want, (code, ml)
        assert rec["drawing"]["label"], code
        assert rec["drawing"]["label"].split()[0] in svg, code


def test_a_hand_written_drink_takes_no_pack_scale_factor(
    rows: list[tuple[str, dict, dict, int]],
) -> None:
    assert [(c, ml) for c, rec, sku, ml in rows if pack_scale.factor(rec, sku) is not None] == []


def test_a_bottle_line_sells_a_750ml_in_glass_and_a_can_line_in_a_can() -> None:
    assert kit_beer.container("750ml", "bottle") == ("bottle", 1, 750.0)
    assert kit_beer.container("750ml", "can") == ("can", 1, 750.0)


def test_a_net_volume_is_the_pack_and_nothing_else_changes() -> None:
    fill = Fill("solid", "#e8b04a", "#ffffff")
    assert kit_beer.beer("#e8b04a", fill, "Ale", pack_size="330ml", net_volume_ml="500.0",
                         sold_in="bottle") == kit_beer.beer(
        "#e8b04a", fill, "Ale", pack_size="500ml", sold_in="bottle")  # fmt: skip
    assert kit_soft_drinks.soft_drink("#e8b04a", fill, "Cola", flavor="Cola",
                                      net_volume_ml="1500.0") == kit_soft_drinks.soft_drink(
        "#e8b04a", fill, "Cola", flavor="Cola", pack_size="1.5L")  # fmt: skip


#: The one-size hand rows: product id -> (shape, the class of its container, the class that shows
#: its drink, the drink's fill, the cover floor of that container in the earlier slices).
WINE_750, PET_500, CAN_330 = 0.170, 0.20, CAN[330]
ONE_SIZE = {
    "BRD-CW06": (
        "wine_bottle",
        "bottle",
        "wine",
        kit_drinks.through_glass("#6a1f3a", "green"),
        WINE_750,
    ),
    "BRD-CW07": (
        "wine_bottle",
        "bottle",
        "wine",
        kit_drinks.through_glass("#5a1a2a", "green"),
        WINE_750,
    ),
    "BRD-CW11": (
        "soft_drink",
        "bottle",
        "drink",
        kit_soft_drinks.through_clear("#dbeaf0"),
        PET_500,
    ),
    "PLT-DXQ05": (
        "soft_drink",
        "bottle",
        "drink",
        kit_soft_drinks.through_clear("#f1f0d2"),
        PET_500,
    ),
    "PLT-DXQ09": (
        "soft_drink",
        "bottle",
        "drink",
        kit_soft_drinks.through_clear("#dfeccb"),
        PET_500,
    ),
    "BRD-CW12": ("beer", "can", "livery", "#e0a040", CAN_330),
}
#: The whisky rows of the same table, which keep the generic bottle at the cover it had.
SPIRITS, SPIRIT_COVER = {"BRD-CW08", "BRD-CW09", "BRD-CW10"}, 0.269
#: The types drawn as their own container, wherever they are sold.
DRINKS = frozenset({"Beer", "Cider", "Perry", "Wine", "Champagne", "Soft Drink", "Ginger Beer",
                    "Root Beer"})  # fmt: skip


@pytest.fixture(scope="module")
def templates() -> dict[str, dict]:
    return {rec["product_id"]: rec for rec in shared_templates()}


def test_each_one_size_hand_drink_draws_its_container_and_shows_its_drink(
    templates: dict[str, dict],
) -> None:
    for pid, (shape, body, shown, want, _) in ONE_SIZE.items():
        rec = templates[pid]
        (sku,) = rec["skus"]
        svg = _svg(rec, sku)
        assert rec["drawing"]["shape"] == shape, pid
        assert len(_classes(svg, body)) == 1, pid
        assert len(_classes(svg, "foot")) == (shape == "soft_drink"), pid
        assert len(_classes(svg, "ring-pull")) == (body == "can"), pid
        (drink,) = _classes(svg, shown)
        assert drink.get("fill") == want, pid
        assert rec["drawing"]["label"], pid
        assert rec["drawing"]["label"].split()[0] in svg, pid
        assert pack_scale.factor(rec, sku) is None, pid


def test_each_one_size_hand_drink_covers_its_floor_and_spans_the_height(
    templates: dict[str, dict],
) -> None:
    low = []
    for pid, (*_, floor) in ONE_SIZE.items():
        svg = _svg(templates[pid], templates[pid]["skus"][0])
        if _cover(svg) < floor or _span(svg) < FULL:
            low.append(f"{pid}: {_cover(svg):.3f} < {floor} or {_span(svg):.2f} < {FULL}")
    assert not low, "\n".join(low)


def test_no_template_drink_is_left_on_the_generic_bottle_or_tin(
    templates: dict[str, dict],
) -> None:
    drinks = {pid: r["drawing"]["shape"] for pid, r in templates.items()
              if r["product_type"] in DRINKS}  # fmt: skip
    assert set(ONE_SIZE) <= set(drinks)
    assert {p: s for p, s in drinks.items() if s in ("bottle", "tin")} == {}


def test_the_whisky_rows_beside_them_keep_their_bottle(templates: dict[str, dict]) -> None:
    for pid in SPIRITS:
        rec = templates[pid]
        assert rec["drawing"]["shape"] == "bottle", pid
        assert _cover(_svg(rec, rec["skus"][0])) >= SPIRIT_COVER - 0.001, pid
