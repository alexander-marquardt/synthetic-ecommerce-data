"""Per-type gates for ``set_screws_hex_socket``, deepened from breadth (#53).

The template is ``tests/test_type_lock_nuts_nylon_insert.py``: uniqueness,
census conformance, provenance, byte-determinism under two hash seeds, a golden
slice, and independence from every other type. On top of it, the gates the
PR #59 review asked for: every dimension the type publishes is the value the
standard's table gives, checked against the tables restated here, so a table
copied from a secondary source that disagrees with the standard goes red.

Every byte comparison goes through :mod:`type_gates`, which compares digests
and then names the first differing SKU, so a red reports in seconds.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import emit, names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from synthetic_industrial_products.product_types.fasteners import set_screws_hex_socket
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "set_screws_hex_socket"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: A deep type, not a breadth row's one or two SKUs: the default build makes
#: hundreds. A floor that catches a collapse back to breadth, not a target.
DEFAULT_SKU_FLOOR = 300

#: The dimensional standards this type's lines claim, and the dimensions it publishes.
DIMENSIONAL = {"ISO 4026", "ISO 4027", "ISO 4028", "ISO 4029", "ASME B18.3"}
DIMENSIONS = ("Length", "Drive Size", "Point Dia.")

#: A build large enough to reach the long end of every size's length range:
#: at this size the FastenersWB ranges emitted 37 metric SKUs ISO does not define.
LARGE_LINES = 39000

MM = 25.4

# --- the standards' tables, restated from the documents, not from the module ---

#: ISO 4026, 4027 and 4029:2003 Table 1: the shortest and longest l per size, mm.
ISO_LENGTH_RANGE = {
    "M1.6": (2, 8), "M2": (2, 10), "M2.5": (2.5, 12), "M3": (3, 16), "M4": (4, 20),
    "M5": (5, 25), "M6": (6, 30), "M8": (8, 40), "M10": (10, 50), "M12": (12, 60),
    "M16": (16, 60), "M20": (20, 60), "M24": (25, 60),
}  # fmt: skip
#: ISO 4028:2003 Table 1 (dog point): the same, mm.
ISO_4028_LENGTH_RANGE = {
    "M1.6": (2, 8), "M2": (2.5, 10), "M2.5": (3, 12), "M3": (4, 16), "M4": (5, 20),
    "M5": (6, 25), "M6": (8, 30), "M8": (8, 40), "M10": (10, 50), "M12": (12, 60),
    "M16": (16, 60), "M20": (20, 60), "M24": (25, 60),
}  # fmt: skip
#: ASME B18.3, hexagon socket set screws: J (the nominal key), C max (cup and
#: flat point diameter) and P max (dog point diameter), inches.
B18_3 = {
    "#0": ("0.028", 0.033, 0.040), "#1": ("0.035", 0.040, 0.049),
    "#2": ("0.035", 0.047, 0.057), "#3": ("0.050", 0.054, 0.066),
    "#4": ("0.050", 0.061, 0.075), "#5": ("1/16", 0.067, 0.083),
    "#6": ("1/16", 0.074, 0.092), "#8": ("5/64", 0.087, 0.109),
    "#10": ("3/32", 0.102, 0.127), "1/4": ("1/8", 0.132, 0.156),
    "5/16": ("5/32", 0.172, 0.203), "3/8": ("3/16", 0.212, 0.250),
    "7/16": ("7/32", 0.252, 0.297), "1/2": ("1/4", 0.291, 0.344),
    "5/8": ("5/16", 0.371, 0.469), "3/4": ("3/8", 0.450, 0.562),
    "7/8": ("1/2", 0.530, 0.656), "1": ("9/16", 0.609, 0.750),
}  # fmt: skip
#: The decimal a feed falls back to when a value is no fraction it can write
#: ("0.1560" for 5/32): right for a toleranced dimension, wrong for a key.
FALLBACK_DECIMAL = re.compile(r"^\d*\.\d{4}$")


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _clean_docs(lines: int | None = None) -> list[dict]:
    """The type's documents with no injected defect, so each value is the builder's."""
    config = GeneratorConfig(defect_scale=0.0, **({"lines": lines} if lines else {}))
    catalog = generate(config, types=[KEY])
    return [doc for line in catalog.lines for doc in emit.flat_documents(catalog, line)]


def _values(doc: dict) -> dict[str, dict]:
    return {a["name"]: a for a in doc["attributes"]}


def _inches(attribute: dict) -> float:
    """``value_canonical`` is millimetres whatever unit the value is written in."""
    return attribute["value_canonical"] / MM


def _size(thread: str) -> str:
    """``M6x1`` -> ``M6``; ``1/4-20`` -> ``1/4``; ``#10-24`` -> ``#10``."""
    return thread.split("x")[0] if thread.startswith("M") else thread.rsplit("-", 1)[0]


@pytest.fixture(scope="module")
def clean_docs() -> list[dict]:
    return _clean_docs()


@pytest.fixture(scope="module")
def large_docs() -> list[dict]:
    return _clean_docs(LARGE_LINES)


# --- the template's gates ---------------------------------------------------------


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


def test_the_provenance_names_where_each_published_dimension_came_from():
    problems, checked = type_gates.provenance_problems(_default_docs(), DIMENSIONAL, DIMENSIONS)
    assert problems == [], problems[:10]
    assert checked > 50, f"only {checked} dimensional claims were checked"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_set_screws_hex_socket.py``."""
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


def test_every_point_style_and_both_systems_are_built(clean_docs):
    values = {(a["name"], a["value"]) for doc in clean_docs for a in doc["attributes"]}
    for point in ("Cup Point", "Flat Point", "Cone Point", "Dog Point"):
        assert ("Point Type", point) in values
    threads = {v for n, v in values if n == "Dia./Thread Size"}
    assert {t.startswith("M") for t in threads} == {True, False}


# --- the type's dimensions against the standards' tables --------------------------


@pytest.mark.parametrize(
    ("standard", "table"),
    [
        ("ISO 4026", ISO_LENGTH_RANGE),
        ("ISO 4027", ISO_LENGTH_RANGE),
        ("ISO 4028", ISO_4028_LENGTH_RANGE),
        ("ISO 4029", ISO_LENGTH_RANGE),
    ],
)
def test_each_metric_length_range_is_the_iso_table_1_range(standard, table):
    declared = {size: set_screws_hex_socket.length_range_mm(standard, size) for size in table}
    wrong = {size: (declared[size], want) for size, want in table.items() if declared[size] != want}
    assert wrong == {}, f"{standard}: (declared, Table 1) per size: {wrong}"


def test_no_metric_sku_has_a_length_its_standard_does_not_define(large_docs):
    outside = []
    for doc in large_docs:
        values = _values(doc)
        thread = values["Dia./Thread Size"]["value"]
        if not thread.startswith("M"):
            continue
        point = values["Point Type"]["value"]
        low, high = (ISO_4028_LENGTH_RANGE if point == "Dog Point" else ISO_LENGTH_RANGE)[
            _size(thread)
        ]
        length = values["Length"]["value_canonical"]
        if not low <= length <= high:
            outside.append(f"{point} {thread} x {length:g}mm")
    assert outside == [], f"{len(outside)} SKUs outside Table 1, e.g. {sorted(set(outside))[:6]}"


def test_every_inch_drive_size_is_the_b18_3_nominal_key(clean_docs):
    wrong = []
    checked = 0
    for doc in clean_docs:
        values = _values(doc)
        thread = values["Dia./Thread Size"]["value"]
        if thread.startswith("M"):
            continue
        key = Fraction(B18_3[_size(thread)][0])
        published = values["Drive Size"]
        checked += 1
        # A fractional key is written as its fraction, or the Drive Size facet
        # splits: a 5/32 filter would miss a socket published as 0.1560.
        spelled_as_toleranced = key.denominator in (16, 32, 64, 8, 4, 2) and bool(
            FALLBACK_DECIMAL.match(published["value"])
        )
        if abs(_inches(published) - float(key)) > 5e-4 or spelled_as_toleranced:
            wrong.append(f"{thread}: {published['value']} for J = {key}")
    assert checked > 50, f"only {checked} inch SKUs were checked"
    assert wrong == [], f"{len(wrong)} wrong, e.g. {sorted(set(wrong))[:6]}"


@pytest.mark.parametrize(("point", "column"), [("Flat Point", 1), ("Dog Point", 2)])
def test_every_inch_point_diameter_is_the_b18_3_maximum(clean_docs, point, column):
    """C max for a flat point and P max for a dog point: the maximum, as the
    metric rows publish ISO's dp max, so both systems publish one basis."""
    wrong = []
    checked = 0
    for doc in clean_docs:
        values = _values(doc)
        thread = values["Dia./Thread Size"]["value"]
        # ``Point Dia.`` is published on most SKUs, not all (its presence).
        if thread.startswith("M") or values["Point Type"]["value"] != point:
            continue
        if "Point Dia." not in values:
            continue
        want = B18_3[_size(thread)][column]
        checked += 1
        got = _inches(values["Point Dia."])
        if abs(got - want) > 5e-4:
            wrong.append(f"{thread}: {got:.4f} for {want:.3f}")
    assert checked > 10, f"only {checked} inch {point} SKUs were checked"
    assert wrong == [], f"{len(wrong)} wrong, e.g. {sorted(set(wrong))[:6]}"


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
