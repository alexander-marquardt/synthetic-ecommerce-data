"""Per-type gates for ``hex_bit_sockets``, deepened from breadth (#836, slice 1).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says which table its hex size was read from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: every hex size a record publishes is a size of the hex
key table its line reads, on a drive that carries it.
"""

from __future__ import annotations

import importlib
import json
from fractions import Fraction
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

KEY = "hex_bit_sockets"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 76 SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 50


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
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


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
    problems, checked = type_gates.provenance_problems(_default_docs(), (), ("Size",))
    assert problems == [], problems[:10]
    docs = _default_docs()
    hex_bit_sockets = _module()
    assert all(
        hex_bit_sockets.B18_3 in doc["dimension_provenance"]
        or hex_bit_sockets.ISO_2936 in doc["dimension_provenance"]
        for doc in docs
    )


def test_every_hex_size_is_a_hex_key_size_its_drive_carries():
    """A metric size is an ISO 2936 key on a drive that carries it, an inch
    size an ASME B18.3 one; the line states its drive and the SKU its size."""
    docs = _default_docs()
    hex_bit_sockets = _module()
    drives = {drive for drive, _, _ in hex_bit_sockets.LADDERS}
    for doc in docs:
        drive = _value(doc, "Drive Size")
        assert drive in drives, (doc["sku"], drive)
        size = parse_length(_value(doc, "Size")).inches
        offered = hex_bit_sockets.sizes_in(drive, "mm" in _value(doc, "Size"))
        assert any(abs(size - s) < 0.0006 for s in offered), (doc["sku"], drive, size)
    assert {_value(doc, "Drive Size") for doc in docs} == drives


def test_the_ladders_are_read_from_the_hex_key_tables():
    hex_bit_sockets = _module()
    for drive, inch, mm in hex_bit_sockets.LADDERS:
        assert set(inch) <= set(hex_bit_sockets.INCH_KEYS), drive
        assert set(mm) <= set(hex_bit_sockets.MM_KEYS), drive
        assert [Fraction(s) for s in inch] == sorted(Fraction(s) for s in inch), drive
        assert list(mm) == sorted(mm), drive


def test_the_borrowed_price_is_held_to_the_hex_keys_the_model_was_fitted_on():
    """A bit past the hex key builder's largest key is priced as that key."""
    from synthetic_ecommerce_data.core import price
    from synthetic_ecommerce_data.domains.industrial import newtypes

    assert price.BORROWS[KEY] == "hex_key"
    keys = (*newtypes._KEY_INCH, *(k / newtypes.MM_PER_INCH for k in newtypes._KEY_MM))
    assert price.MEASURED_SPANS["hex_key"] == pytest.approx((min(keys), max(keys)))
    assert max(s for _, _, mm in _module().LADDERS for s in mm) / 25.4 > max(keys)


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_hex_bit_sockets.py``."""
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
