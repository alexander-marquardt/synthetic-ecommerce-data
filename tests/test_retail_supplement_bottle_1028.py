"""Vitamins and minerals are drawn as a capped supplement bottle, not a cup (gen#1028, slice 1).

The maintainer, looking at a "vitamins" search: "make vitamins look more like vitamin bottles
rather than how they currently look, which is like cups". Every vitamin and mineral drew the
retail ``tub`` (a tall tapered open pot), so within a leaf only one of three pot colors told
two products apart. ``supplement_bottle`` (``kit_health.py``) is a capped bottle in the
colorway's color, the cap in its accent, with a wrapped label: a band in the nutrient's color,
the nutrient's name, and a tablet or capsule glyph by ``form``. The nutrient and the form are
drawing params, so a derived style that swaps them is redrawn
(``test_retail_scale.test_a_changed_value_is_redrawn_in_the_picture``).

:data:`TUB_TYPES` lists every product type still drawn as a ``tub``: adding a type to the
``tub`` shape means adding it here, so the choice is seen in review.
"""

from __future__ import annotations

import collections
import json
import re

import pytest

from synthetic_ecommerce_data.domains.retail import kit, kit_health, scale, type_registry

#: Spec key -> the attribute key that names what the bottle holds.
SUPPLEMENTS = {"vitamins": "nutrient", "minerals": "mineral"}

#: Every product type the authored build draws as a ``tub`` (gen#1028): only real tubs. Slice 2
#: took Dish Soap, Fabric Softener, Glass Cleaner and Toilet Cleaner off it
#: (``tests/test_retail_cleaning_packs_1028.py``): Air Freshener and Laundry Detergent stay for
#: their gel pot, pods and capsules. Slice 3 moved Hot Chocolate to a tin and redrew ``tub`` as a
#: lidded tub (``tests/test_retail_tub_redraw_1028.py``).
TUB_TYPES = frozenset({
    "Air Freshener", "Car Wax", "Laundry Detergent", "Yogurt",
})  # fmt: skip

WHITE = kit.Fill("solid", "#f4f4f2", "#2a2a2e")


def _docs(key: str) -> list[dict]:
    return type_registry.specs()[key].docs()


def _value(doc: dict, key: str) -> str:
    return next(str(a["value"]) for a in doc["attributes"] if a["key"] == key)


def _svg(nutrient: str, form: str, fill: kit.Fill = WHITE) -> str:
    return kit.render("supplement_bottle", fill, params={"nutrient": nutrient, "form": form})


@pytest.mark.parametrize("key", sorted(SUPPLEMENTS))
def test_a_supplement_is_drawn_as_a_bottle_of_its_own_nutrient_and_form(key: str) -> None:
    wrong = [
        (d["product_id"], d["drawing"]["shape"], d["drawing"].get("params"))
        for d in _docs(key)
        if d["drawing"]["shape"] != "supplement_bottle"
        or d["drawing"].get("params")
        != {"nutrient": _value(d, SUPPLEMENTS[key]), "form": _value(d, "form")}
    ]
    assert wrong == []


@pytest.mark.parametrize("key", sorted(SUPPLEMENTS))
def test_no_two_products_in_a_supplement_leaf_share_a_picture(key: str) -> None:
    """Every different product has a different picture in its leaf (the rulings). Two brands
    may share a drawing, since each picture carries its own brand's tag; one brand may not."""
    pictures = collections.defaultdict(list)
    for d in _docs(key):
        drawn = json.dumps(d["drawing"], sort_keys=True)
        pictures[(d["category_leaf"], d["brand"], drawn)].append(d["product_id"])
    assert [ids for ids in pictures.values() if len(ids) > 1] == []


@pytest.mark.parametrize("key", sorted(SUPPLEMENTS))
def test_a_supplement_title_and_description_name_the_bottle_it_is_drawn_as(key: str) -> None:
    tub = re.compile(r"\btubs?\b", re.I)
    said = [d["product_id"] for d in _docs(key) if tub.search(f"{d['title']} {d['description']}")]
    assert said == []


def test_the_bottle_carries_the_nutrient_name_and_a_tablet_glyph() -> None:
    svg = _svg("Vitamin C", "Tablets")
    assert ">Vitamin C<" in svg
    assert 'class="tablet"' in svg
    assert 'class="capsule"' not in svg


def test_a_capsule_bottle_draws_a_capsule_glyph() -> None:
    svg = _svg("Vitamin D3", "Capsules")
    assert 'class="capsule"' in svg
    assert 'class="tablet"' not in svg


def test_the_label_band_is_colored_by_nutrient() -> None:
    def band(svg: str) -> str:
        found = re.search(r'class="band"[^>]*fill="(#[0-9a-f]{6})"', svg)
        assert found, "no label band"
        return found.group(1)

    colors = {n: band(_svg(n, "Tablets")) for n in ("Vitamin C", "Zinc", "Magnesium")}
    assert colors == {n: kit_health.band_color(n) for n in colors}
    assert len(set(colors.values())) == 3
    assert band(_svg("Vitamin C", "Capsules")) == colors["Vitamin C"]


def test_the_cap_is_the_colorways_accent_and_the_bottle_its_base() -> None:
    amber = kit.Fill("solid", "#c98a2e", "#ffffff")
    svg = _svg("Iron", "Tablets", amber)
    assert re.search(r'class="cap"[^>]*fill="#ffffff"', svg)
    assert re.search(r'class="bottle"[^>]*fill="#c98a2e"', svg)


def test_the_bottle_is_not_the_old_cup() -> None:
    """The old ``tub`` pot's outline (a tall taper with an open rim) is not in the bottle."""
    assert "M112,118 L288,118 L262,356" not in _svg("Zinc", "Tablets")


def test_every_type_drawn_as_a_tub_is_listed() -> None:
    drawn = {r["product_type"] for r in scale.templates() if r["drawing"]["shape"] == "tub"}
    assert sorted(drawn) == sorted(TUB_TYPES)
