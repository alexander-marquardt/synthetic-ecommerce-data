"""Retail luggage and travel (gen#209): the catalog had no suitcase, holdall or neck pillow.

A demo search for a suitcase or a cabin bag found a make-up bag or nothing, so size, shell and
wheel filters could not be shown for a high-volume family. Seven specs under ``type_specs/``
hold the types and :mod:`kit_luggage` draws them. These checks hold what the issue asked for:
every type has at least three styles from three invented brands, a product type that names it
and a category path, each key attribute as a structured entry in the export, a drawing of its
own whose params change the picture, the six main colors, text-match decoys (one of them an
incidental word), a place in the scaled build, and the figures the generic queries need.
"""

# ruff: noqa: E501 -- the type table reads better whole than wrapped.

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402

PATH = ("Womens", "Accessories", "Travel")
#: key -> (product type, category leaf, shape, structured attributes each style states, the
#: drawing param and two readings that must draw differently).
TYPES = {
    "suitcase": ("Suitcase", "Suitcases", "suitcase",
                 {"shell", "wheels", "lock", "expandable", "material", "capacity", "luggage_size", "weight", "color"},
                 ("shell", "hard", "soft")),
    "cabin_case": ("Cabin Case", "Cabin Cases", "cabin_case",
                   {"shell", "wheels", "airline_allowance", "dimensions", "capacity", "weight", "color"},
                   ("kind", "carry-on", "under-seat")),
    "holdall": ("Holdall", "Holdalls", "holdall",
                {"material", "wheels", "shoulder_strap", "use", "capacity", "color"},
                ("wheels", "no", "yes")),
    "weekend_bag": ("Weekend Bag", "Weekend Bags", "weekend_bag",
                    {"material", "compartments", "trolley_sleeve", "capacity", "color"},
                    ("compartments", "1", "3")),
    "luggage_set": ("Luggage Set", "Luggage Sets", "luggage_set",
                    {"shell", "wheels", "piece_count", "sizes_included", "color"},
                    ("pieces", "2", "3")),
    "travel_organizer": ("Travel Organizer", "Travel Organizers", "travel_organizer",
                         {"organizer_type", "piece_count", "material", "color"},
                         ("kind", "packing cubes", "passport holder")),
    "neck_pillow": ("Neck Pillow", "Neck Pillows", "neck_pillow",
                    {"fill", "cover", "hood", "color"},
                    ("hood", "no", "yes")),
}  # fmt: skip
KEYS = sorted(TYPES)


def _spec(key: str):
    specs = type_registry.specs()
    assert key in specs, f"no spec named {key}"
    return specs[key]


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _entries(row) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


@pytest.mark.parametrize("key", KEYS)
def test_a_type_has_three_styles_from_three_invented_brands(key: str) -> None:
    rows = _spec(key).rows
    assert len(rows) >= 3
    assert len({r.brand for r in rows}) >= 3
    assert len({r.title for r in rows}) == len(rows)


@pytest.mark.parametrize("key", KEYS)
def test_the_product_type_names_the_type_and_the_path_is_under_travel(key: str) -> None:
    ptype, leaf, *_ = TYPES[key]
    spec = _spec(key)
    assert spec.product_type == ptype
    assert {r.product_type for r in spec.rows} == {ptype}
    assert {r.path for r in spec.rows} == {(*PATH, leaf)}


@pytest.mark.parametrize("key", KEYS)
def test_every_key_attribute_is_a_structured_entry_in_the_export(key: str) -> None:
    keys = TYPES[key][3]
    rows = _spec(key).rows
    assert rows
    missing = {r.code: sorted(keys - _entries(r)) for r in rows if keys - _entries(r)}
    assert missing == {}


@pytest.mark.parametrize("key", KEYS)
def test_a_type_draws_its_own_shape_and_the_variant_param_changes_the_picture(key: str) -> None:
    _, _, shape, _, (param, one, two) = TYPES[key]
    rows = _spec(key).rows
    assert rows
    assert {r.shape for r in rows} == {shape}
    assert shape in kit.SHAPES
    assert _svg(shape, **{param: one}) != _svg(shape, **{param: two})
    seen = {dict(r.params).get(param) for r in rows}
    assert len(seen) >= 2, f"the styles all draw the same {param}"


@pytest.mark.parametrize("key", KEYS)
def test_a_type_offers_the_six_main_colors_with_no_exception(key: str) -> None:
    ptype = TYPES[key][0]
    assert ptype not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in _spec(key).rows for c in r.colors}


@pytest.mark.parametrize("key", KEYS)
def test_a_type_carries_three_decoys_one_of_them_an_incidental_word(key: str) -> None:
    decoys = _spec(key).decoys
    assert len(decoys) >= 3
    assert any(d.cls == 6 for d in decoys), "no incidental-word decoy (class 6)"
    assert len({d.row.code for d in decoys}) == len(decoys)


@pytest.mark.parametrize("key", KEYS)
def test_a_type_reaches_the_scaled_build_as_authored_templates(key: str) -> None:
    spec = _spec(key)
    ids = {f"BRD-{r.code}" for r in spec.rows}
    built = {d["product_id"] for d in scale.templates() if d["product_type"] == TYPES[key][0]}
    assert ids and ids <= built
    assert not any(d["product_id"] in ids for d in scale.derivable(scale.templates()))


def test_a_suitcase_sku_states_size_litres_and_weight() -> None:
    for row in _spec("suitcase").rows:
        doc = export.standard_document(row.doc())
        sizes = {
            e["value"]
            for v in doc["variants"]
            for e in v["attributes"]
            if e["key"] == "luggage_size"
        }
        assert sizes == {"Cabin", "Medium", "Large"}, row.code
        weights = [e for v in doc["variants"] for e in v["attributes"] if e["key"] == "weight"]
        assert weights and {e["unit_code"] for e in weights} == {"KGM"}, row.code
        litres = [e for v in doc["variants"] for e in v["attributes"] if e["key"] == "capacity"]
        assert litres and {e["unit_code"] for e in litres} == {"LTR"}, row.code


def test_the_suitcases_cover_hard_and_soft_shells_and_both_wheel_counts() -> None:
    rows = _spec("suitcase").rows
    shells = {dict(r.params)["shell"] for r in rows}
    wheels = {dict(r.params)["wheels"] for r in rows}
    assert shells == {"hard", "soft"}
    assert wheels == {"4", "2"}


def test_the_luggage_sets_come_in_two_and_three_pieces() -> None:
    pieces = {a[2] for r in _spec("luggage_set").rows for a in r.attrs if a[0] == "piece_count"}
    assert pieces == {"2", "3"}


def test_the_travel_organizers_cover_the_four_kinds_the_issue_names() -> None:
    kinds = {
        a[2] for r in _spec("travel_organizer").rows for a in r.attrs if a[0] == "organizer_type"
    }
    assert kinds == {"Packing Cubes", "Passport Holder", "Toiletry Roll", "Adapter Case"}


def test_the_neck_pillows_include_memory_foam() -> None:
    fills = {a[2] for r in _spec("neck_pillow").rows for a in r.attrs if a[0] == "fill"}
    assert {"Memory Foam", "Microbead", "Inflatable"} <= fills


def _attrs(doc: dict) -> dict[str, dict]:
    return {e["key"]: e for e in export.standard_document(doc)["attributes"]}


@pytest.mark.parametrize("key", ["suitcase", "cabin_case", "holdall", "weekend_bag"])
def test_a_capacity_in_litres_carries_its_millilitres_as_the_canonical_value(key: str) -> None:
    """The standard's LTR canonical is millilitres (``core.standard.canonical``), as a pack size's is."""
    seen = 0
    for doc in _spec(key).docs():
        standard = export.standard_document(doc)
        for holder in (standard, *standard["variants"]):  # a suitcase's litres sit on its SKUs
            for entry in holder["attributes"]:
                if entry["key"] == "capacity":
                    seen += 1
                    assert entry["unit_code"] == "LTR"
                    assert entry["value_canonical"] == float(entry["value"]) * 1000.0, doc["product_id"]
    assert seen


def test_a_cabin_case_decoy_holds_the_capacity_its_dimensions_give() -> None:
    """A decoy states its own capacity: two cabin cases of one size hold the same litres."""
    by_dims: dict[str, set[str]] = {}
    for doc in _spec("cabin_case").docs():
        e = _attrs(doc)
        by_dims.setdefault(e["dimensions"]["value"], set()).add(e["capacity"]["value"])
    assert by_dims and all(len(litres) == 1 for litres in by_dims.values()), by_dims


def test_a_weekend_bag_decoy_holds_the_capacity_of_the_bag_in_its_material() -> None:
    by_code = {d["product_id"]: _attrs(d)["capacity"]["value"] for d in _spec("weekend_bag").docs()}
    canvas, leather_look = by_code["BRD-WKBCNV"], by_code["BRD-WKBLTH"]  # the authored bags
    assert by_code["BRD-WKBDRD"] == by_code["BRD-WKBDWB"] == canvas  # the two canvas decoys
    assert by_code["BRD-WKBDLK"] == leather_look  # the faux leather decoy copies the leather-look bag


@pytest.mark.parametrize("brand", ["Tarnwick", "Fenmoor & Co", "Skerry Travel"])
def test_each_new_luggage_brand_has_a_house_style_and_a_mark_of_its_own(brand: str) -> None:
    import house_styles  # noqa: PLC0415

    style = house_styles.HOUSE_STYLES.get(brand)
    assert style is not None, f"{brand} draws no logo: rendering its image raises KeyError"
    assert style.layout != "mark_only"  # a lockup: the wordmark is the brand field
    others = [s for b, s in house_styles.HOUSE_STYLES.items() if b != brand]
    assert style.mark not in {s.mark for s in others}
    assert house_styles.lockup_key(style) not in {house_styles.lockup_key(s) for s in others}
