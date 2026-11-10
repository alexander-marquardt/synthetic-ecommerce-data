"""Every shoe is one product sold in UK sizes and colors (gen#935).

Footwear is a ``Mens``, ``Womens`` or ``Kids`` path whose second node is ``Shoes``. Over the
ceiling build (the one a release ships, :func:`retail_figures.ceiling`) every such product is one
product whose SKUs vary on ``size_uk`` and ``color``: at least two of each, a UK size one size
(never a slipper's letter range "7-8"), and every SKU its own image. A decoy keeps its decoy
property: the Blue Bull boots are never sold in blue, and "Brogues with Blue Sole" never in blue.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import retail_figures
from synthetic_ecommerce_data.domains.retail.export import image_id, standard_document

ROOTS = ("Mens", "Womens", "Kids")


def _footwear(rec: dict) -> bool:
    path = rec["category_path"]
    return len(path) > 1 and path[0] in ROOTS and path[1] == "Shoes"


@pytest.fixture(scope="module")
def shoes() -> list[dict]:
    return [r for r in retail_figures.ceiling().records if _footwear(r)]


@pytest.fixture(scope="module")
def by_id(shoes: list[dict]) -> dict[str, dict]:
    return {r["product_id"]: r for r in shoes}


def _colors(rec: dict) -> list[str]:
    return list(dict.fromkeys(s["color"] for s in rec["skus"] if "color" in s))


def test_every_footwear_sku_carries_a_uk_size_and_a_color(shoes: list[dict]) -> None:
    lacking = [s["sku"] for r in shoes for s in r["skus"] if "size_uk" not in s or "color" not in s]
    assert len(shoes) > 900
    assert lacking == []


def test_a_uk_size_is_one_size_never_a_letter_range(shoes: list[dict]) -> None:
    ranged = sorted({r["product_id"] for r in shoes for s in r["skus"]
                     if "-" in str(s.get("size_uk", "")) or "size" in s})  # fmt: skip
    assert ranged == []


def test_every_footwear_product_has_two_sizes_and_two_colors(shoes: list[dict]) -> None:
    few = [r["product_id"] for r in shoes
           if len({s.get("size_uk") for s in r["skus"]}) < 2 or len(_colors(r)) < 2]  # fmt: skip
    assert few == []


def test_size_and_color_are_every_footwear_products_variant_axes(shoes: list[dict]) -> None:
    missing = [d["product_id"] for d in map(standard_document, shoes)
               if not {"size_uk", "color"} <= set(d["variant_axes"])]  # fmt: skip
    assert missing == []


def test_every_footwear_sku_has_its_own_image(shoes: list[dict]) -> None:
    images = [image_id(r, s) for r in shoes for s in r["skus"]]
    assert len(images) == len(set(images))


@pytest.mark.parametrize(
    ("pid", "never"),
    [
        ("PLT-DY41", "Blue"),  # Blue Bull Chelsea Boots: the brand holds the word
        ("PLT-DA32402", "Blue"),  # Red Cashmere-Feel Chelsea Boots, by Blue Bull
        ("PLT-DA31102", "Blue"),  # Brogues with Blue Sole
        ("PLT-DXT01", "Black"),  # White Trainers with Black Sole
    ],
)
def test_a_decoy_is_sold_in_colors_but_never_the_one_its_words_name(
    by_id: dict[str, dict], pid: str, never: str
) -> None:
    colors = _colors(by_id[pid])
    assert len(colors) >= 2
    assert never not in colors


def test_a_sku_in_another_color_names_its_own_color(by_id: dict[str, dict]) -> None:
    """"Red Cashmere-Feel Chelsea Boots" in black is "Black Cashmere-Feel Chelsea Boots"."""
    doc = standard_document(by_id["PLT-DA32402"])
    titles = {}
    for v in doc["variants"]:
        color = next(e["value"] for e in v["attributes"] if e["key"] == "color")
        titles[color] = v["title"]
    assert len(titles) >= 2
    assert all(t == f"{c} Cashmere-Feel Chelsea Boots" for c, t in titles.items())


def test_no_sku_takes_another_products_title(shoes: list[dict]) -> None:
    """A color's own title is never another product's ("Red Trainers with Black Sole")."""
    own = {r["title"]: r["product_id"] for r in shoes}
    clash = sorted(
        (d["product_id"], v["title"])
        for d in map(standard_document, shoes)
        for v in d["variants"]
        if own.get(v["title"], d["product_id"]) != d["product_id"]
    )
    assert clash == []
