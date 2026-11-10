"""Every shoe is one product sold in UK sizes and colors (gen#935).

Footwear is a ``Mens``, ``Womens`` or ``Kids`` path whose second node is ``Shoes``. Over the
ceiling build (the one a release ships, :func:`retail_figures.ceiling`) every such product is one
product whose SKUs vary on ``size_uk`` and ``color``: at least two of each, a UK size one size
(never a slipper's letter range "7-8"), and every SKU its own image. A decoy keeps its decoy
property: the Blue Bull boots are never sold in blue, and "Brogues with Blue Sole" never in blue.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import retail_figures, shoe_grid
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
        if v["title"] != d["title"] and v["title"] in own
    )
    assert any(v["title"] != d["title"] for d in map(standard_document, shoes)
               for v in d["variants"])  # fmt: skip
    assert clash == []


def _row(pid: str = "PLT-T1", title: str = "Blue Bull Trainers", color: str = "Black",
         root: str = "Mens", **skus: object) -> dict:  # fmt: skip
    """A planted shoe row as :mod:`decoy_rows` makes one: one SKU, no size, one color."""
    sku = {"sku": f"{pid}-X", "color": color, "price": 40.0, "in_stock": True, **skus}
    return {
        "product_id": pid, "title": title, "brand": "Blue Bull",
        "description": f"{color} trainers by Blue Bull.", "product_type": "Trainers",
        "category_path": [root, "Shoes", "Trainers"], "drawing": {"accent": "#333333"},
        "price": 40.0, "sku_count": 1, "skus": [sku],
        "color_options": [{"color": color, "hex": "#2a2a2e", "pattern": "solid",
                           "family": color.lower()}],
    }  # fmt: skip


def test_a_row_without_sizes_takes_its_audiences_whole_uk_run() -> None:
    runs = (("Mens", "6", "12"), ("Womens", "3", "8"), ("Kids", "8 Infant", "2 Junior"))
    for root, lo, hi in runs:
        rec = shoe_grid.apply_one(_row(root=root))
        sizes = list(dict.fromkeys(s["size_uk"] for s in rec["skus"]))
        assert sizes[0] == lo and sizes[-1] == hi
        assert len(sizes) >= 5
        assert not any(".5" in s for s in sizes)
        assert all(s["size_eu"] and s["size_us"] for s in rec["skus"])


def test_one_inner_size_is_left_out_of_some_rows_never_an_end() -> None:
    runs = [shoe_grid.ladder(_row(pid=f"PLT-T{i}")) for i in range(60)]
    full = max(map(len, runs))
    gapped = [r for r in runs if len(r) == full - 1]
    assert 0 < len(gapped) < len(runs)
    assert all(r[0] == "6" and r[-1] == "12" for r in runs)


def test_a_one_color_row_takes_two_to_five_colors_none_its_text_names() -> None:
    counts = set()
    for i in range(40):
        rec = shoe_grid.apply_one(_row(pid=f"PLT-T{i}"))
        colors = list(dict.fromkeys(s["color"] for s in rec["skus"]))
        counts.add(len(colors))
        assert colors[0] == "Black"
        assert "Blue" not in colors
        assert [o["color"] for o in rec["color_options"]] == colors
        assert rec["sku_count"] == len(rec["skus"]) == len(colors) * len(shoe_grid.ladder(rec))
    assert min(counts) == shoe_grid.MIN_COLORS and max(counts) == shoe_grid.MAX_COLORS


def test_an_added_color_whose_title_is_another_rows_is_left_out() -> None:
    rec = _row(title="Black Trainers")
    held = shoe_grid.colors_for(rec, ["Black"], frozenset({"White Trainers", "Red Trainers"}))
    assert "White" not in held and "Red" not in held
    assert len(held) >= shoe_grid.MIN_COLORS


def test_a_title_naming_no_color_is_never_its_own_twin() -> None:
    rec = _row(title="Dress for Success Brogues")
    held = shoe_grid.colors_for(rec, ["Black"], frozenset({rec["title"]}))
    assert len(held) >= shoe_grid.MIN_COLORS


def test_a_title_naming_its_color_is_each_added_colors_own() -> None:
    row = _row(title="Black Canvas Trainers") | {"description": "Canvas trainers in black."}
    rec = shoe_grid.apply_one(row)
    for color, copy in rec[shoe_grid.COLOR_COPY].items():
        assert copy == {"title": f"{color} Canvas Trainers",
                        "description": f"Canvas trainers in {color.lower()}."}  # fmt: skip
    assert rec[shoe_grid.COLOR_COPY] and "Black" not in rec[shoe_grid.COLOR_COPY]


def test_a_row_already_in_two_colors_keeps_them() -> None:
    held = ["Black", "Grey", "Red"]
    assert shoe_grid.colors_for(_row(), held) == held


def test_a_slipper_letter_row_lends_its_stock_to_the_uk_sizes_it_spans() -> None:
    rec = _row(size="M", size_uk="7-8", size_eu="41-42", size_us="8-9")
    rec["skus"][0]["in_stock"] = False
    rec["skus"].append({"sku": "PLT-T1-Y", "color": "Black", "price": 40.0, "in_stock": True,
                        "size": "L", "size_uk": "9-10", "size_eu": "43-44", "size_us": "10-11"})
    out = shoe_grid.apply_one(rec)
    stock = {s["size_uk"]: s["in_stock"] for s in out["skus"] if s["color"] == "Black"}
    assert "size" not in out["skus"][0]
    assert stock.get("7") is False and stock.get("10") is True


def test_a_color_whose_every_letter_row_is_sold_out_still_has_one_size_in_stock() -> None:
    rec = _row(size="M", size_uk="7-8", size_eu="41-42", size_us="8-9")
    rec["skus"][0]["in_stock"] = False
    out = shoe_grid.apply_one(rec)
    assert any(s["in_stock"] for s in out["skus"] if s["color"] == "Black")


def test_a_sized_row_in_two_colors_and_any_other_row_is_left_as_it_is() -> None:
    rec = _row(size_uk="7", size_eu="41", size_us="8")
    rec["skus"].append(rec["skus"][0] | {"sku": "PLT-T1-Y", "color": "Grey"})
    rec["color_options"].append(rec["color_options"][0] | {"color": "Grey", "family": "grey"})
    assert shoe_grid.apply_one(rec) is rec
    bag = _row() | {"category_path": ["Womens", "Accessories", "Bags"]}
    assert shoe_grid.apply_one(bag) is bag
