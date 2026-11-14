"""Per-type gates for ``utility_knives``, a homeowner tool (#971, slice 3).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says where its blade width came from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: it is filed under ``Tools``; every blade width is one its style is
sold with (a snap-off knife in 9, 18 or 25 mm, every other style on the 19 mm trapezoid
blade); every style, material, blade count and main color (gen#275) is built; and some
titles are text-match decoys (gen#294) that name another tool while every attribute stays
true.
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
from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "utility_knives"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse, and is not a target.
DEFAULT_SKU_FLOOR = 20

#: The six main colors every color-bearing type offers (gen#275).
MAIN_COLORS = {"Red", "Blue", "Green", "Yellow", "Black", "White"}

#: The blade widths each style is sold with, in mm: snap-off knives take the three
#: segmented-blade widths, every other style the trapezoid blade.
WIDTHS_MM = {"Snap-Off": {9, 18, 25}, "Retractable": {19}, "Folding": {19}, "Fixed Blade": {19}}

#: The spare-blade counts a knife is sold with.
BLADE_COUNTS = {1, 3, 5, 10}


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.hand_tools." + KEY
    )


def _value(doc: dict, name: str) -> str:
    return next(a["value"] for a in authored_attributes(doc) if a["name"] == name)


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is not a modelled type"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_the_type_is_filed_under_tools():
    assert taxonomy.LEAVES[KEY] == (("Hand Tools", "Cutters", "Utility Knives"),)
    paths = {tuple(doc["category_path"]) for doc in _default_docs()}
    assert paths == {("Tools", "Hand tools", "Cutters", "Utility knives")}


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert unexplained_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from():
    problems, checked = type_gates.provenance_problems(_default_docs(), (), ("Width",))
    assert problems == [], problems[:10]
    assert {doc["dimension_provenance"] for doc in _default_docs()} == {_module().PROVENANCE}


def test_every_blade_width_is_one_its_style_is_sold_with():
    for doc in _default_docs():
        width_mm = parse_length(_value(doc, "Width")).inches * 25.4
        allowed = WIDTHS_MM[_value(doc, "Style")]
        assert any(width_mm == pytest.approx(mm, abs=0.05) for mm in allowed), doc["sku"]
        assert int(_value(doc, "Number of Blades")) in BLADE_COUNTS, doc["sku"]


def test_the_modules_styles_and_counts_are_the_ones_listed_here():
    knives = _module()
    built: dict[str, set[int]] = {}
    for style, mm in knives.KINDS:
        built.setdefault(style, set()).add(mm)
    assert built == WIDTHS_MM
    assert set(knives.BLADE_COUNTS) == BLADE_COUNTS


def test_every_style_width_material_count_and_main_color_is_built():
    knives = _module()
    docs = _default_docs()
    assert {_value(d, "Style") for d in docs} == set(WIDTHS_MM)
    assert {_value(d, "Width") for d in docs} == {"9 mm", "18 mm", "19 mm", "25 mm"}
    assert {_value(d, "Material") for d in docs} == set(knives.MATERIALS)
    assert {int(_value(d, "Number of Blades")) for d in docs} == BLADE_COUNTS
    assert {_value(d, "Color") for d in docs} == MAIN_COLORS
    assert len(set(knives.COMBOS)) == len(knives.KINDS) * len(knives.MATERIALS)


def test_some_titles_name_another_tool_and_every_title_names_the_item():
    """The decoys (gen#294): another tool's word before the item, never a knife's attribute."""
    knives = _module()
    docs = _default_docs()
    decoys = {
        doc["product_id"]
        for doc in docs
        if any(f"{noun} Series Utility Knife" in doc["title"] for noun in knives.DECOY_NOUNS)
    }
    products = {doc["product_id"] for doc in docs}
    assert decoys, "no decoy title was built"
    assert len(decoys) < len(products)
    assert all("Utility Knife" in doc["title"] for doc in docs)


def test_siblings_draw_differently():
    """A line's SKUs differ only in their spare blades, which the drawing lays out."""
    knives = _module()
    record = {"Style": "Retractable", "Width": "19 mm", "Color": "Red", "Material": "Aluminum"}
    shapes = {
        repr(knives.figure({**record, "Number of Blades": str(n)}).figure.shapes)
        for n in sorted(BLADE_COUNTS)
    }
    assert len(shapes) == len(BLADE_COUNTS)


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_utility_knives.py``."""
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
