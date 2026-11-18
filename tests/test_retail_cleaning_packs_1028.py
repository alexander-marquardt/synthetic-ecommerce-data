"""Cleaning products are drawn as their real packs (gen#1028, slice 2).

The maintainer, 2026-11-15: "laundry detergent should look different than a cup .. so should
dish soap". Liquid laundry detergent and fabric softener drew the plain ``bottle``, and so did
dish soap and the grocery glass cleaners. Wipes, toilet tablets, scent beads and dishwasher
tablets drew the cup-like ``tub``. Now:

* liquid laundry detergent and fabric softener (and the beads' handled bottle) draw ``jug``;
* dish soap draws ``squeeze_bottle``, except the pump, which stays a ``bottle``;
* glass cleaner draws ``trigger_spray``, except the refill and the concentrate (bottles) and
  the wipes (``wipes_pack``);
* toilet tablets come in a ``box``, and the 60-pack dishwasher tablets in ``dishwasher_tablets``.

Laundry pods and capsules stay on ``tub``: they are real tubs, which slice 3 redraws.
"""

from __future__ import annotations

import collections
import json
import re

import pytest

from synthetic_ecommerce_data.domains.retail import kit, scale

CLEANING_TYPES = (
    "Dish Soap", "Laundry Detergent", "Fabric Softener", "Glass Cleaner", "Toilet Cleaner",
    "Air Freshener",
)  # fmt: skip

#: The products whose real pack is not the one their type mostly draws.
NOT_JUG = re.compile(r"Powder|Sheets|Pods|Capsules|Machine Cleaner|Descaler|Softening Cream")
SPRAY_EXCEPTIONS = {
    "BRD-GLSREF": "bottle", "BRD-GLSLEM": "bottle", "BRD-GLSWIP": "wipes_pack",
    "PLT-DXW03": "bottle",  # a bottle of stain remover
}  # fmt: skip
SQUEEZE_EXCEPTIONS = {
    "BRD-DSHPMP": "bottle",  # a pump bottle
    "PLT-DY301": "dishwasher_tablets",
    "PLT-DY703": "dishwasher_tablets",
    "PLT-DY302": "pouch",  # dishwasher salt
    "PLT-DY303": "bottle",  # rinse aid
}

ORANGE = kit.Fill("solid", "#e8823a", "#1c4f8a")


def _fill_of(svg: str, part: str) -> str:
    """The fill of the element of class ``part`` in ``svg``."""
    element = re.search(rf'<[^>]*class="{part}"[^>]*>', svg)
    assert element, f"no {part}"
    return re.search(r'fill="([^"]+)"', element.group(0)).group(1)


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    return [r for r in scale.templates() if r["product_type"] in CLEANING_TYPES]


def _shapes(rows: list[dict], product_type: str) -> dict[str, str]:
    return {
        r["product_id"]: r["drawing"]["shape"] for r in rows if r["product_type"] == product_type
    }


def test_liquid_laundry_detergent_and_softener_are_drawn_as_a_jug(rows) -> None:
    liquids = [
        r for r in rows
        if r["product_type"] in ("Laundry Detergent", "Fabric Softener")
        and not NOT_JUG.search(r["title"])
    ]  # fmt: skip
    wrong = [
        (r["product_id"], r["title"], r["drawing"]["shape"])
        for r in liquids
        if r["drawing"]["shape"] != "jug"
    ]
    assert len(liquids) >= 50
    assert wrong == []


def test_dish_soap_is_drawn_as_a_squeeze_bottle(rows) -> None:
    shapes = _shapes(rows, "Dish Soap")
    want = {pid: SQUEEZE_EXCEPTIONS.get(pid, "squeeze_bottle") for pid in shapes}
    assert len(shapes) >= 50
    assert shapes == want


def test_glass_cleaner_is_drawn_as_a_trigger_spray(rows) -> None:
    shapes = _shapes(rows, "Glass Cleaner")
    want = {pid: SPRAY_EXCEPTIONS.get(pid, "trigger_spray") for pid in shapes}
    assert len(shapes) >= 50
    assert shapes == want


def test_no_cleaning_product_but_a_real_tub_draws_tub(rows) -> None:
    """The pods, the capsules and the gel pot are tubs of something; nothing else here is."""
    tubs = sorted(r["product_id"] for r in rows if r["drawing"]["shape"] == "tub")
    assert tubs == ["BRD-AIRGEL", "BRD-LDRCAP", "BRD-LDRPOD"]


def test_no_two_products_of_one_brand_share_a_picture_in_a_cleaning_leaf(rows) -> None:
    """Every different product has a different picture in its leaf (the rulings); each picture
    carries its brand's tag, so the key holds the brand (as slice 1's does)."""
    pictures = collections.defaultdict(list)
    for r in rows:
        pictures[(r["category_leaf"], r["brand"], json.dumps(r["drawing"], sort_keys=True))].append(
            r["product_id"]
        )
    assert [ids for ids in pictures.values() if len(ids) > 1] == []


def _render(shape: str, label: str) -> str:
    """A shape the kit does not draw yet is a failed assertion, not a lookup error."""
    try:
        return kit.render(shape, ORANGE, label)
    except KeyError as exc:
        raise AssertionError(f"the kit draws no {shape!r} shape") from exc


def test_the_jug_has_a_grip_hole_and_a_cap_in_the_accent() -> None:
    svg = _render("jug", "Detergent")
    assert _fill_of(svg, "jug") == "#e8823a"
    assert _fill_of(svg, "cap") == "#1c4f8a"
    assert _fill_of(svg, "handle") == kit.PAPER  # the grip hole shows the paper through it
    assert ">Detergent<" in svg


def test_the_squeeze_bottle_has_a_flip_cap_in_the_accent() -> None:
    svg = _render("squeeze_bottle", "Dish Soap")
    assert _fill_of(svg, "bottle") == "#e8823a"
    assert _fill_of(svg, "cap") == "#1c4f8a"
    assert 'class="flip"' in svg
    assert "Dish Soap" in svg


@pytest.mark.parametrize("shape", ["jug", "squeeze_bottle"])
def test_a_new_pack_is_not_the_old_cup_or_the_plain_bottle(shape: str) -> None:
    svg = _render(shape, "Soap")
    assert "M112,118 L288,118 L262,356" not in svg  # the tub's tapered pot
    assert "M142,366 L142,186 Q142,138 178,116" not in svg  # the plain bottle's body
