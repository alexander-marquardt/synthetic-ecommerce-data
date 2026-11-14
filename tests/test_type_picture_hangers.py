"""Per-type gates for ``picture_hangers``, home hardware (#958, slice 1).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says where its rating came from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: it is filed under ``Hardware``; every rating is one its style stocks in
its unit system, and carries its value in pounds; every style, material, unit system and main
colour (gen#275) is built; and some titles are text-match decoys (gen#294) that name a thing a
hanger holds while every attribute stays true.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

import type_gates
from published import authored_attributes
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "picture_hangers"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse, and is not a target.
DEFAULT_SKU_FLOOR = 20

#: The six main colours every colour-bearing type offers (gen#275).
MAIN_COLORS = {"Red", "Blue", "Green", "Yellow", "Black", "White"}

#: The ratings each style is stocked in: pounds, then kilograms.
LB = {
    "Nail Hook": (10, 20, 30, 50, 75, 100),
    "Sawtooth Hanger": (10, 15, 20, 25, 30),
    "D-Ring Hanger": (20, 30, 50, 75, 100),
    "Hanging Kit": (20, 30, 50, 75, 100),
}
KG = {
    "Nail Hook": (5, 10, 15, 25, 35, 45),
    "Sawtooth Hanger": (5, 7, 9, 11, 14),
    "D-Ring Hanger": (10, 15, 25, 35, 45),
    "Hanging Kit": (10, 15, 25, 35, 45),
}


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.fasteners." + KEY
    )


def _attribute(doc: dict, name: str) -> dict:
    return next(a for a in authored_attributes(doc) if a["name"] == name)


def _value(doc: dict, name: str) -> str:
    return _attribute(doc, name)["value"]


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is not a modelled type"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_the_type_is_filed_under_hardware():
    assert taxonomy.LEAVES[KEY] == (("Fasteners", "Picture Hanging", "Picture Hangers"),)
    paths = {tuple(doc["category_path"]) for doc in _default_docs()}
    assert paths == {("Hardware", "Fasteners", "Picture hanging", "Picture hangers")}


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert unexplained_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_rating_came_from():
    assert {doc["dimension_provenance"] for doc in _default_docs()} == {_module().PROVENANCE}


def test_every_rating_is_one_its_style_stocks():
    for doc in _default_docs():
        size, unit = _value(doc, "Load Capacity").split()
        table = KG if unit == "kg" else LB
        assert unit in {"lb", "kg"}, doc["sku"]
        assert int(size) in table[_value(doc, "Style")], doc["sku"]


def test_the_modules_stocked_ratings_are_the_ones_listed_here():
    hangers = _module()
    assert hangers.LB_RATINGS == LB
    assert hangers.KG_RATINGS == KG


def test_every_style_material_system_and_main_color_is_built():
    hangers = _module()
    docs = _default_docs()
    assert {_value(d, "Style") for d in docs} == set(hangers.STYLES)
    assert {_value(d, "Material") for d in docs} == set(hangers.MATERIALS)
    assert {_value(d, "Load Capacity").split()[1] for d in docs} == {"lb", "kg"}
    assert {_value(d, "Color") for d in docs} == MAIN_COLORS
    assert len(set(hangers.COMBOS)) == len(hangers.STYLES) * len(hangers.MATERIALS) * 2


def test_a_rating_ranges_in_pounds():
    """A rating is published in pounds or kilograms and still ranges in pounds."""
    hangers = _module()
    assert hangers.rating("lb", 30) == ("30 lb", 30.0)
    published, pounds = hangers.rating("kg", 10)
    assert published == "10 kg"
    assert pounds == pytest.approx(22.05, abs=0.01)
    for doc in _default_docs():
        size, unit = _value(doc, "Load Capacity").split()
        expected = int(size) * (2.20462 if unit == "kg" else 1.0)
        assert _attribute(doc, "Load Capacity")["value_num"] == pytest.approx(expected, abs=0.01)


def test_some_titles_name_a_held_thing_and_every_title_names_the_item():
    """The decoys (gen#294): a held thing's word before the item, never a hanger's attribute."""
    hangers = _module()
    docs = _default_docs()
    decoys = {
        doc["product_id"]
        for doc in docs
        if any(f"{noun} Series Picture Hanger" in doc["title"] for noun in hangers.DECOY_NOUNS)
    }
    products = {doc["product_id"] for doc in docs}
    assert decoys, "no decoy title was built"
    assert len(decoys) < len(products)
    assert all("Picture Hanger" in doc["title"] for doc in docs)


def test_each_style_is_drawn_its_own_way():
    hangers = _module()
    shapes = {
        style: len(hangers.figure({"Style": style, "Load Capacity": "30 lb"}).fig.shapes)
        for style in hangers.STYLES
    }
    assert len(set(shapes.values())) == len(hangers.STYLES), shapes


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_picture_hangers.py``."""
    assert SLICE.is_file(), f"no golden slice at {SLICE}"
    committed = SLICE.read_text(encoding="utf-8").splitlines()
    report = type_gates.difference(committed, type_gates.default_records(KEY))
    if report:
        pytest.fail(f"{SLICE.name} is not a fresh build: {report}")


def test_every_other_type_is_byte_identical_with_this_type_left_out():
    moved = _moved_by_removing(KEY)
    assert not moved, f"building {KEY} changed {moved[:8]}"


def test_every_other_type_builds_as_the_committed_golden_has_it():
    report = type_gates.others_moved_from_the_golden(KEY)
    if report:
        pytest.fail(report)


def test_the_whole_build_carries_exactly_this_types_own_build():
    whole = _by_type(generate().lines)
    alone = _by_type(generate_type(GeneratorConfig(), KEY))
    assert whole[KEY] == alone[KEY]


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
