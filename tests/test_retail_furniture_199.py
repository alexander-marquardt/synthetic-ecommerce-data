"""Furniture for the rest of the house (gen#199): the range, its structured attributes, its
drawings and its place in the scaled build.

``prototypes/retail_drawings/furniture_rows.py`` holds the rows and ``kit_furniture.py`` the
shapes. A type is searched by room, material, size and finish, so each key the issue lists is a
structured attribute in the export, not only a word in the title, and the drawing shows what
the attributes say: a table's seats, a bookcase's shelves, a wardrobe's doors, a chest's drawers.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import breadth_rows  # noqa: E402
import export  # noqa: E402
import furniture_rows  # noqa: E402
import image_release  # noqa: E402
import kit  # noqa: E402
import scale  # noqa: E402
from retail_figures import committed  # noqa: E402

#: product type -> its leaf and the keys a shopper narrows it on (each a product attribute).
KEYS = {
    "Dining Table": ("Dining Tables", {"seat_count", "shape", "extending", "top_material", "room"}),
    "Dining Chair": ("Dining Chairs", {"chair_style", "seat_material", "leg_finish", "room"}),
    "Coffee Table": ("Coffee Tables", {"shape", "material", "room"}),
    "Side Table": ("Side Tables", {"table_type", "material", "room"}),
    "Bookcase": ("Bookcases", {"bookcase_style", "material", "room"}),
    "Wardrobe": ("Wardrobes", {"door_count", "mirrored", "door_type", "material", "item_width",
                               "item_height", "room"}),
    "Chest of Drawers": ("Chests of Drawers", {"drawer_count", "chest_style", "material",
                                               "handles", "item_width", "item_height", "room"}),
    "Mirror": ("Mirrors", {"mirror_type", "shape", "material", "room"}),
}  # fmt: skip
#: product type -> the variant keys its SKUs carry beyond color.
SKU_KEYS = {
    "Dining Table": {"size", "item_width", "item_length"},
    "Dining Chair": {"pack_size", "units_per_pack"},
    "Bookcase": {"size", "item_height"},
    "Mirror": {"size", "item_width", "item_height"},
}


def _docs() -> list[dict]:
    return furniture_rows.docs()


def _attrs(entries: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for e in entries:
        out.setdefault(e["key"], []).append(e)
    return out


def _one(doc: dict, key: str) -> str:
    return next(str(a["value"]) for a in doc["attributes"] if a["key"] == key)


def test_every_type_has_three_styles_from_three_brands_under_its_own_leaf() -> None:
    assert set(furniture_rows.TYPES) == set(KEYS)
    for ptype, rows in furniture_rows.TYPES.items():
        assert len(rows) >= 3, ptype
        assert len({r.brand for r in rows}) >= 3, ptype
        assert {r.product_type for r in rows} == {ptype}
        assert {r.path[-1] for r in rows} == {KEYS[ptype][0]}, ptype
        assert all(r.path[0] == r.department == "Home" for r in rows), ptype


def test_every_brand_has_an_owner_and_a_house_style() -> None:
    import house_styles

    brands = {r.brand for r in furniture_rows.ROWS}
    assert brands <= set(breadth_rows.OWNERS)
    assert brands <= set(house_styles.HOUSE_STYLES)


def test_every_key_attribute_is_a_structured_entry_in_the_export() -> None:
    for doc in _docs():
        std = export.standard_document(doc)
        keys = set(_attrs(std["attributes"]))
        assert KEYS[doc["product_type"]][1] <= keys, (doc["product_id"], keys)
        variant_keys = {a["key"] for v in std["variants"] for a in v["attributes"]}
        assert {"color"} | SKU_KEYS.get(doc["product_type"], set()) <= variant_keys, doc["title"]


def test_a_measurement_is_in_centimeters_with_a_millimeter_canonical() -> None:
    for doc in _docs():
        std = export.standard_document(doc)
        entries = [*std["attributes"], *(a for v in std["variants"] for a in v["attributes"])]
        for e in entries:
            if e["key"].startswith("item_"):
                assert e["unit_code"] == "CMT", e
                assert e["value_canonical"] == float(e["value"]) * 10, e


def test_a_table_size_names_the_measurements_its_sku_carries() -> None:
    for row in furniture_rows.ROWS:
        for sku in row.skus():
            if "length_cm" in sku:
                w, n = sku["width_cm"], sku["length_cm"]
                assert sku["size"] == (f"{n} x {w} cm" if n != w else f"{w} cm"), row.code
            if "units_per_pack" in sku:
                n = sku["units_per_pack"]
                assert sku["pack_size"] == ("Single" if n == 1 else f"Set of {n}"), row.code


def test_a_set_of_n_in_the_title_is_the_pack_or_piece_count() -> None:
    for row in furniture_rows.ROWS:
        m = re.search(r"Set of (\d+)", row.title)
        if not m:
            continue
        doc = row.doc()
        pieces = {a["value"] for a in doc["attributes"] if a["key"] == "piece_count"}
        packs = {str(s.get("units_per_pack")) for s in doc["skus"]}
        assert {m[1]} in (pieces, packs), row.code


#: drawing param -> the attribute it draws, and how the attribute's value is spelled there.
DRAWN = {
    "dining_table": {"outline": "shape", "seats": "seat_count", "extending": "extending"},
    "dining_chair": {"style": "chair_style"},
    "coffee_table": {"outline": "shape", "pieces": "piece_count"},
    "side_table": {"drawers": "drawer_count"},
    "bookcase": {"shelves": ("shelf_count", "cube_count")},
    "wardrobe": {"doors": "door_count", "mirrored": "mirrored", "door": "door_type"},
    "chest_of_drawers": {"drawers": "drawer_count", "form": "chest_style"},
    "mirror": {"outline": "shape"},
}


FILL = kit.Fill("solid", "#c9a06a", "#333333", "#f2d14b")


def _spelled(v: str) -> str:
    return v.lower().replace("-", "_").replace(" ", "_")


def test_every_drawing_param_says_what_the_attributes_say() -> None:
    """The picture is the data: a 6 seater draws six chairs, a 5 drawer chest five fronts."""
    for doc in _docs():
        d = doc["drawing"]
        assert d["shape"] in kit.SHAPES, doc["product_id"]
        attrs = {a["key"]: str(a["value"]) for a in doc["attributes"]}
        for param, keys in DRAWN[d["shape"]].items():
            value = d["params"][param]
            keys = keys if isinstance(keys, tuple) else (keys,)
            held = [attrs[k] for k in keys if k in attrs]
            if not held:  # a count the row omits is none (no drawers) or one (one table)
                assert value in ("0", "1"), (doc["product_id"], param)
                continue
            assert _spelled(held[0]) == _spelled(value), (doc["product_id"], param)


@pytest.mark.parametrize(("shape", "params", "cls", "n"), [
    ("chest_of_drawers", {"drawers": "5", "form": "tall"}, "drawer", 5),
    ("chest_of_drawers", {"drawers": "6", "form": "wide"}, "drawer", 6),
    ("wardrobe", {"doors": "3", "mirrored": "yes", "door": "hinged"}, "door", 3),
    ("bookcase", {"shelves": "5", "style": "standard"}, "shelf", 5),
    ("dining_chair", {"style": "cantilever", "count": "2"}, "chair", 2),
])  # fmt: skip
def test_a_drawn_count_is_the_count_in_the_params(shape, params, cls, n) -> None:
    svg = kit.render(shape, FILL, params=params)
    assert len(re.findall(rf'class="{cls}"', svg)) == n


def test_styles_that_differ_on_a_drawn_param_draw_differently() -> None:
    by_shape: dict[str, dict[tuple, str]] = {}
    for doc in _docs():
        d = doc["drawing"]
        params = tuple(sorted(d["params"].items()))
        drawn = kit.render(d["shape"], FILL, params=d["params"])
        by_shape.setdefault(d["shape"], {})[params] = drawn
    for shape, bodies in by_shape.items():
        assert len(set(bodies.values())) == len(bodies), shape


def test_every_style_and_colorway_renders_its_image() -> None:
    for doc in _docs():
        for sku in doc["skus"]:
            assert image_release.render(doc, sku).startswith(b"<svg"), sku["sku"]


def test_the_furniture_is_in_the_scaled_build_and_no_style_derives_from_it() -> None:
    ids = {f"BRD-{r.code}" for r in furniture_rows.ROWS}
    built = scale.build(committed()["ceiling"]["skus"])
    assert ids <= {r["product_id"] for r in built.records}
    assert not ids & {r["product_id"] for r in scale.derivable(built.records)}
    furniture = {r.path for r in furniture_rows.ROWS}
    derived = [r for r in built.records if tuple(r["category_path"]) in furniture]
    assert {r["product_id"] for r in derived} == ids
