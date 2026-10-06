"""Per-type gates for ``lock_nuts_nylon_insert``, deepened from breadth (#53).

The first deepened breadth category. Each gate is about this type alone, so a
second deepened type copies this file and changes ``KEY`` and the floor:

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* byte-determinism: two builds of the type serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out.
"""

from __future__ import annotations

import json
from pathlib import Path

from published import published_attributes
from synthetic_industrial_products.catalog import emit, names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from synthetic_industrial_products.catalog.model import Catalog
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "lock_nuts_nylon_insert"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: A deep type, not a breadth row's one or two SKUs: the default build makes
#: hundreds. A floor that catches a collapse back to breadth, not a target.
DEFAULT_SKU_FLOOR = 300


def _flat(lines) -> list[dict]:
    return list(emit.iter_flat(Catalog(lines=tuple(lines)), emit.DEFAULT_IMAGE_BASE_URL))


def _default_docs() -> list[dict]:
    return _flat(generate_type(GeneratorConfig(), KEY))


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in published_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_two_builds_are_byte_identical():
    first = [json.dumps(d, sort_keys=True) for d in _default_docs()]
    second = [json.dumps(d, sort_keys=True) for d in _default_docs()]
    assert first == second


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_lock_nuts_nylon_insert.py``."""
    fresh = "".join(json.dumps(d, sort_keys=True) + "\n" for d in _default_docs())
    assert SLICE.is_file(), f"no golden slice at {SLICE}"
    assert SLICE.read_text() == fresh


def test_every_other_type_is_byte_identical_with_this_type_left_out():
    moved = _moved_by_removing(KEY)
    assert not moved, f"building {KEY} changed {moved[:8]}"


def test_the_whole_build_carries_exactly_this_types_own_build():
    whole = _by_type(generate().lines)
    alone = _by_type(generate_type(GeneratorConfig(), KEY))
    assert whole[KEY] == alone[KEY]


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text("".join(json.dumps(d, sort_keys=True) + "\n" for d in _default_docs()))
