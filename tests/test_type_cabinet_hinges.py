"""Per-type gates for ``cabinet_hinges``, home hardware (#958, slice 2).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says where its length came from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: it is filed under ``Hardware``; every length is one its style stocks;
every style, material and main color (gen#275) is built; and some titles are text-match
decoys (gen#294) that name the furniture a hinge goes on while every attribute stays true.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

import pinned
import type_gates
from published import authored_attributes
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "cabinet_hinges"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse, and is not a target.
DEFAULT_SKU_FLOOR = 10

#: The slice's floor at the large build (#958): 95% of a sixth of the issue's 1,564 SKUs, one
#: share for each of the six home-hardware types it plans.
LARGE_BUILD_FLOOR = 248

#: The six main colors every color-bearing type offers (gen#275).
MAIN_COLORS = {"Red", "Blue", "Green", "Yellow", "Black", "White"}

#: The lengths each style is stocked in, in inches.
INCHES = {
    "Butt": (1.5, 2.0, 2.5, 3.0, 3.5),
    "Flush": (2.0, 2.5, 3.0),
    "Surface Mount": (2.0, 2.5, 3.0, 3.5),
    "Overlay": (2.0, 2.25, 2.5, 2.75),
}


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.fasteners." + KEY
    )


def _value(doc: dict, name: str) -> str:
    return next(a["value"] for a in authored_attributes(doc) if a["name"] == name)


def _inches(doc: dict) -> float:
    """The length in inches: the published entry is inches (``INH``) and its canonical
    value is millimeters."""
    entry = next(a for a in doc["attributes"] if a["key"] == "length")
    assert entry["unit_code"] == "INH", doc["sku"]
    return round(entry["value_canonical"] / 25.4, 3)


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is not a modelled type"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_the_large_build_holds_the_slice_floor():
    """The large build's count of this type, from ``measured_builds.json``: the merge script's
    rebuild writes it and ``test_measured_figures.py`` refuses it stale, so no module builds its
    own 39,000-line copy (``test_shared_builds_140.py``)."""
    assert pinned.hundred_k_skus(KEY) >= LARGE_BUILD_FLOOR


def test_the_type_is_filed_under_hardware():
    assert taxonomy.LEAVES[KEY] == (("Fasteners", "Cabinet Hardware", "Cabinet Hinges"),)
    paths = {tuple(doc["category_path"]) for doc in _default_docs()}
    assert paths == {("Hardware", "Fasteners", "Cabinet hardware", "Cabinet hinges")}


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert unexplained_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_length_came_from():
    assert {doc["dimension_provenance"] for doc in _default_docs()} == {_module().PROVENANCE}


def test_every_length_is_one_its_style_stocks():
    for doc in _default_docs():
        assert _inches(doc) in INCHES[_value(doc, "Style")], doc["sku"]


def test_the_modules_stocked_lengths_are_the_ones_listed_here():
    assert _module().INCH_LENGTHS == INCHES


def test_every_style_material_and_main_color_is_built():
    hinges = _module()
    docs = _default_docs()
    assert {_value(d, "Style") for d in docs} == set(hinges.STYLES)
    assert {_value(d, "Material") for d in docs} == set(hinges.MATERIALS)
    assert {_value(d, "Color") for d in docs} == MAIN_COLORS
    assert len(set(hinges.COMBOS)) == len(hinges.STYLES) * len(hinges.MATERIALS)


def test_some_titles_name_a_piece_of_furniture_and_every_title_names_the_item():
    """The decoys (gen#294): the furniture's word before the item, never a hinge's attribute."""
    hinges = _module()
    docs = _default_docs()
    decoys = {
        doc["product_id"]
        for doc in docs
        if any(f"{noun} Series Cabinet Hinge" in doc["title"] for noun in hinges.DECOY_NOUNS)
    }
    products = {doc["product_id"] for doc in docs}
    assert decoys, "no decoy title was built"
    assert len(decoys) < len(products)
    assert all("Cabinet Hinge" in doc["title"] for doc in docs)


def test_each_style_is_drawn_its_own_way():
    hinges = _module()
    drawings = {
        repr(hinges.figure({"Style": style, "Length": '2-1/2"'}).figure.shapes)
        for style in hinges.STYLES
    }
    assert len(drawings) == len(hinges.STYLES)


def test_a_longer_hinge_is_a_bigger_drawing():
    hinges = _module()
    small = hinges.figure({"Style": "Butt", "Length": '1-1/2"'})
    large = hinges.figure({"Style": "Butt", "Length": '3-1/2"'})
    assert (small.source, large.source) == ("record", "record")
    assert large.figure.size_in > small.figure.size_in


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_cabinet_hinges.py``."""
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
