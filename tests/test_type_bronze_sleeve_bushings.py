"""Per-type gates for ``bronze_sleeve_bushings``, deepened from breadth (#833).

The gates of ``test_type_lock_nuts_nylon_insert.py``, the template (#53 step 3):

* uniqueness: no two SKUs of one (type, brand) are the same product;
* census conformance: every name the type publishes passes the census gate;
* provenance: each record says which table its dimensions were read from;
* byte-determinism: two builds of the type, in two processes under two hash
  seeds, serialise identically;
* a golden slice: the type's committed records, reviewed in its own file;
* independence: every other type's output is byte-identical with this type
  built or left out, and every other type still builds as the committed
  golden has it.

And this type's own: every bushing a record publishes is a row of the table
its line reads, and every catalogue row is the size its catalogue number says.
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

KEY = "bronze_sleeve_bushings"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's SKUs, rounded down to a ten
#: (docs/adding-a-type.md "SKU floor"): it catches a collapse back to the
#: breadth row's 2 SKUs, and is not a target.
DEFAULT_SKU_FLOOR = 50

DIMENSIONS = ("Bore Dia.", "Outside Dia.", "Length", "Flange Dia.", "Flange Thickness")


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _module():
    """The type's module, read in the tests that need it: until it exists the
    first two gates red on their assertions, not on an import."""
    return importlib.import_module(
        "synthetic_ecommerce_data.domains.industrial.product_types.motion." + KEY
    )


def _values(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in authored_attributes(doc)}


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
    bushings = _module()
    problems, checked = type_gates.provenance_problems(
        _default_docs(), (bushings.ISO_2795,), DIMENSIONS
    )
    assert problems == [], problems[:10]
    assert checked > 0, "no metric line was built"


def test_every_bushing_is_a_row_of_its_lines_table():
    """The bore, outside diameter, length and flange a record publishes are
    one size of the table its form, material and unit system name."""
    bushings = _module()
    seen = set()
    for doc in _default_docs():
        v = _values(doc)
        line = (v["Type"], v["Material"], "mm" if "mm" in v["Bore Dia."] else "in")
        sizes = [
            s for t in bushings.series() if (t.form, t.material, t.system) == line for s in t.sizes
        ]
        assert sizes, (doc["sku"], line)
        got = tuple(parse_length(v[name]).inches if name in v else 0.0 for name in DIMENSIONS)
        assert any(
            all(abs(a - b) < 0.0006 for a, b in zip(got, size, strict=True)) for size in sizes
        ), (doc["sku"], got)
        seen.add(line)
    assert len(seen) >= 3, seen


def test_every_row_is_its_catalogue_number():
    """B46-2 1/2 is 4/16" x 6/16" x 2-1/2/8": the number's digits split into
    the printed inside and outside diameters in sixteenths."""
    bushings = _module()
    for text in (bushings._SINTERED_PLAIN, bushings._SINTERED_FLANGED, bushings._CAST_PLAIN):
        rows = bushings.parse_table(text)
        assert rows
        for row in rows:
            digits = row.number.lstrip("BFM")
            assert digits == f"{row.bore * 16}{row.outside * 16}", row.number
            assert row.bore < row.outside, row.number
            assert list(row.lengths) == sorted(set(row.lengths)), row.number
            if row.flange is not None:
                assert row.flange[0] > row.outside and row.flange[1] < Fraction(1, 4), row.number


def test_the_iso_2795_rows_are_the_libraries_and_the_thin_wall_footnote_holds():
    bushings = _module()
    normal, thin = bushings.iso_2795()
    assert len(normal) == 102
    # Footnote a: up to d 20 mm the last length is not a thin-wall one.
    d20 = [s for s in thin if abs(s.bore * 25.4 - 20) < 1e-9]
    assert sorted(round(s.length * 25.4) for s in d20) == [15, 20, 25]
    d22 = [s for s in thin if abs(s.bore * 25.4 - 22) < 1e-9]
    assert sorted(round(s.length * 25.4) for s in d22) == [15, 20, 25, 30]


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_bronze_sleeve_bushings.py``."""
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
