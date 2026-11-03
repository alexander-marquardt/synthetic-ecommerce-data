"""Per-type gates for ``screw_hex_head``, the hex head cap screw (#819).

The lock nut's template (uniqueness, census names, provenance, two builds,
the golden slice, independence), and this type's own facts: the attribute
shape the issue names, the sizes and lengths it stocks, and the washer face
its drawing carries.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import type_gates
from published import authored_attributes
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.core.drawing.model import Disc, Poly
from synthetic_ecommerce_data.domains.industrial import names, taxonomy
from synthetic_ecommerce_data.domains.industrial.drawing.figures import fastener
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from synthetic_ecommerce_data.domains.industrial.product_types.fasteners import screw_hex_head
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import unexplained_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "screw_hex_head"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: Two thirds of the default build's 72 SKUs, rounded down to a ten.
DEFAULT_SKU_FLOOR = 40

DIMENSIONAL = {screw_hex_head.STANDARD}
DIMENSIONS = ("Width Across Flats", "Head Height", "Thread Length", "Threads per Inch")

#: What every record publishes, and the values a line-constant one may take.
ALWAYS = {
    "Head Type": {"Hex"},
    "Drive Type": {"External Hex"},
    "Material": {"Grade 2 Steel", "Grade 5 Steel", "Grade 8 Alloy Steel"},
    "Finish": {"Plain", "Zinc Plated", "Zinc Yellow"},
    "Thread Type": {"UNC", "UNF"},
    "Standards": {"ASME B18.2.1", "SAE J429"},
}
MEASURED = (
    "Dia./Thread Size",
    "Threads per Inch",
    "Length",
    "Thread Length",
    "Width Across Flats",
    "Head Height",
    "Units per Pack",
)


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _published(doc: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for a in authored_attributes(doc):
        out.setdefault(a["name"], set()).add(a["value"])
    return out


def _skus() -> list[dict[str, str]]:
    """The default build's SKUs, each as its line's and its own attributes."""
    return [
        {a.name: a.value for a in (*line.attributes, *child.attributes)}
        for line in generate_type(GeneratorConfig(), KEY)
        for child in line.children
    ]


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled()


def test_the_type_sits_beside_the_socket_cap_screws():
    (path,) = taxonomy.LEAVES[KEY]
    (socket,) = taxonomy.LEAVES["screw_socket_head"]
    assert path[:-1] == socket[:-1]
    assert path[-1] == "Hex Head Cap Screws"


def test_the_default_build_is_deep():
    assert len(_default_docs()) >= DEFAULT_SKU_FLOOR


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert unexplained_duplicates(docs, share=0.0) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_every_record_carries_the_hex_cap_screw_shape():
    for doc in _default_docs():
        published = _published(doc)
        for name, allowed in ALWAYS.items():
            assert published.get(name), (doc["sku"], f"no {name}")
            assert published[name] <= allowed, (doc["sku"], name, published[name])
        for name in MEASURED:
            assert published.get(name), (doc["sku"], f"no {name}")


def test_every_grade_and_finish_pair_and_both_thread_series_are_stocked():
    skus = _skus()
    assert {(s["Material"], s["Finish"]) for s in skus} == set(screw_hex_head.COMBOS)
    assert {s["Thread Type"] for s in skus} == {"UNC", "UNF"}


def test_the_sizes_run_from_quarter_twenty_to_one_eight_coarse_and_fine():
    threads = {s["Dia./Thread Size"] for s in _skus()}
    coarse = {f"{s}-{screw_hex_head.THREADS[s]['unc_tpi']}" for s in screw_hex_head.SIZES}
    fine = {f"{s}-{screw_hex_head.THREADS[s]['unf_tpi']}" for s in screw_hex_head.SIZES}
    assert {"1/4-20", "7/16-14", "1-8"} <= coarse
    assert coarse <= threads
    assert threads <= coarse | fine
    assert threads & fine


def test_every_length_is_one_the_standard_offers_inside_half_an_inch_to_six():
    for sku in _skus():
        size = sku["Dia./Thread Size"].rsplit("-", 1)[0]
        length = parse_length(sku["Length"]).inches
        assert 0.5 <= length <= 6.0, sku
        assert any(abs(length - x) < 1e-6 for x in screw_hex_head.offered_lengths_in(size)), sku


def test_the_drawing_puts_the_hex_head_on_its_washer_face():
    sku = next(s for s in _skus() if s["Dia./Thread Size"] == "7/16-14")
    row = screw_hex_head.HEADS["7/16"]
    face_dia, face_thickness = row["washer_face_dia_in"], row["washer_face_thickness_in"]
    drawn = screw_hex_head.figure(sku)
    bare = fastener(sku, max_height=screw_hex_head.EXTENT[1])
    assert drawn.source == "record"

    def spans(fig) -> set[tuple[float, float]]:
        return {
            (round(max(x for x, _ in s.points) - min(x for x, _ in s.points), 4),
             round(max(y for _, y in s.points) - min(y for _, y in s.points), 4))
            for s in fig.shapes
            if isinstance(s, Poly)
        }  # fmt: skip

    collar = (round(face_dia, 4), round(face_thickness, 4))
    assert collar in spans(drawn.figure)
    assert collar not in spans(bare.figure)
    assert any(
        isinstance(s, Disc) and abs(s.radius - face_dia / 2) < 1e-9 for s in drawn.figure.shapes
    )


def test_the_provenance_names_where_each_published_dimension_came_from():
    problems, checked = type_gates.provenance_problems(_default_docs(), DIMENSIONAL, DIMENSIONS)
    assert problems == [], problems[:10]
    assert checked > 20, f"only {checked} dimensional claims were checked"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_screw_hex_head.py``."""
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
