"""Nails and false nails (gen#751): the word ``nails`` has two real meanings.

Three hardware types under ``Fasteners > Nails`` and one beauty type under ``Beauty > Nails``. The
hardware tables are restated here, not read from the modules, so a row typed wrong in a module goes
red. They are the steel rows of the supplier charts the modules cite, read on 2026-10-31. Those
charts name no standard, so a nail claims none, and its provenance says so.

The per-type gates of ``tests/test_type_cotter_pins.py`` run here over all three keys. Regenerate
the slices with ``uv run python tests/test_nails_751.py``.
"""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path

import pytest

import table_gates
import type_gates
from published import authored_attributes
from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.drawing import svg_problems
from synthetic_ecommerce_data.domains.industrial import names, tabletype, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from synthetic_ecommerce_data.domains.industrial.product_types.fasteners import nail_framing
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

SLICES = Path(__file__).parent / "data" / "golden_slices"
COLUMNS = ("Length", "Shank Dia.", "Head Dia.")
MM = table_gates.MM
#: A build large enough to reach every row in every pack.
LARGE_LINES = 39000


def _mm(*rows: tuple[float, float, float]) -> set[tuple[float, ...]]:
    return {tuple(round(value * MM, 2) for value in row) for row in rows}


#: key -> (leaf, title item, material, finish, packs, the chart's rows in inches).
HARDWARE = {
    "nail_framing": (
        "Framing Nails", "Framing Nail", "Steel", "Plain", {50, 250},
        _mm((2.0, 0.113, 17 / 64), (2.5, 0.131, 9 / 32), (3.0, 0.148, 5 / 16),
            (3.25, 0.148, 5 / 16), (3.5, 0.162, 11 / 32), (4.0, 0.192, 13 / 32)),
    ),
    "nail_finishing": (
        "Finishing Nails", "Finishing Nail", "Steel", "Plain", {100, 500},
        _mm((1.25, 0.067, 1 / 8), (1.5, 0.072, 1 / 8), (2.0, 0.091, 1 / 8),
            (2.5, 0.095, 1 / 8), (3.0, 0.113, 3 / 16)),
    ),
    "nail_masonry": (
        "Masonry Nails", "Masonry Nail", "Steel", "Zinc Plated", {25, 100},
        _mm((0.75, 0.13, 3 / 8), (1.0, 0.16, 7 / 16), (1.25, 0.19, 1 / 2),
            (1.5, 0.25, 9 / 16), (2.0, 0.25, 9 / 16), (2.5, 0.25, 9 / 16)),
    ),
}  # fmt: skip
KEYS = tuple(HARDWARE)
FALSE_NAILS = ("Beauty", "Nails", "False Nails")
#: The fewest and the most products a hardware type holds at the default build (the issue asks
#: for no massive new range) and the most styles of the false nails.
PRODUCTS = (15, 45)
FALSE_NAIL_STYLES = 8
#: USD for one pack. Not a fit: a price outside it is a broken ladder.
SANITY_BAND = (0.50, 1500.0)


def _words(title: str) -> set[str]:
    return set(re.findall(r"[a-z]+", title.lower()))


def _default_docs(key: str) -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(key)]


@pytest.fixture(scope="module")
def retail() -> list[dict]:
    return ceiling_build().records


@pytest.fixture(scope="module")
def false_nails(retail) -> list[dict]:
    return [r for r in retail if tuple(r["category_path"]) == FALSE_NAILS]


@pytest.fixture(scope="module")
def built() -> dict[str, list[dict]]:
    """Each hardware leaf's flat documents in the whole default build, by leaf."""
    catalog = generate(GeneratorConfig(defect_scale=0.0))
    held: dict[str, list[dict]] = {}
    for doc in table_gates.docs(catalog):
        if doc["category_path"][:2] == ["Fasteners", "Nails"]:
            held.setdefault(doc["category_path"][2].lower(), []).append(doc)
    return held


@pytest.fixture(scope="module")
def large_docs() -> dict[str, list[dict]]:
    return {key: table_gates.docs(table_gates.catalog(key, LARGE_LINES)) for key in KEYS}


# --- what the issue asks -------------------------------------------------------------


@pytest.mark.parametrize("key", KEYS)
def test_the_fasteners_node_sells_each_kind_of_nail(built, key):
    leaf, item, *_ = HARDWARE[key]
    docs = built.get(leaf.lower(), [])
    assert docs, f"no document under Fasteners > Nails > {leaf}"
    assert all(item in doc["title"] for doc in docs)


def test_the_beauty_department_sells_false_nails(false_nails):
    assert false_nails, "no style under Beauty > Nails > False Nails"
    assert len(false_nails) <= FALSE_NAIL_STYLES
    assert len({r["brand"] for r in false_nails}) >= 3


def test_a_shopper_word_for_a_false_nail_is_in_true_text(false_nails):
    text = " ".join(f"{r['title']} {r['description']}" for r in false_nails).lower()
    for word in ("press-on nails", "fake nails", "false nails"):
        assert word in text, word


def test_the_false_nails_are_sold_in_packs(false_nails):
    assert false_nails, "no false nails"
    for record in false_nails:
        packs = {s.get("units_per_pack") for s in record["skus"]}
        assert None not in packs and len(packs) >= 2, record["title"]


def test_nail_and_nails_are_both_title_words_of_the_false_nails(false_nails):
    seen = set().union(*(_words(r["title"]) for r in false_nails)) if false_nails else set()
    assert {"nail", "nails"} <= seen


def test_nail_is_a_title_word_of_the_hardware_and_each_pack_word_is_its_field(built):
    docs = [doc for held in built.values() for doc in held]
    assert docs, "no hardware nail"
    for doc in docs:
        assert "nail" in _words(doc["title"]), doc["title"]
        pack = re.search(r"(\d[\d,]*) (?:Pack|Pk|per Pack)\b", doc["title"])
        if pack:
            published = table_gates.values(doc)[table_gates.PACK]
            assert float(pack[1].replace(",", "")) == float(published["value_canonical"])


# --- the range stays small -----------------------------------------------------------


@pytest.mark.parametrize("key", KEYS)
def test_the_default_build_holds_no_massive_range(key):
    products = {doc["product_id"] for doc in _default_docs(key)}
    assert PRODUCTS[0] <= len(products) <= PRODUCTS[1], len(products)


# --- the per-type gates --------------------------------------------------------------


@pytest.mark.parametrize("key", KEYS)
def test_the_type_is_modelled_in_its_own_module(key):
    assert key in typespec.modelled(), f"{key} is not built"


@pytest.mark.parametrize("key", KEYS)
def test_no_two_skus_of_one_brand_are_the_same_product(key):
    docs = _default_docs(key)
    assert docs, f"{key} built nothing"
    assert same_product_duplicates(docs) == []


@pytest.mark.parametrize("key", KEYS)
def test_every_published_name_passes_the_census_gate(key):
    (path,) = taxonomy.LEAVES[key]
    emitted = {a["name"] for doc in _default_docs(key) for a in authored_attributes(doc)}
    assert emitted, f"{key} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


@pytest.mark.parametrize("key", KEYS)
def test_a_nail_claims_no_standard_and_names_its_chart(key, large_docs):
    """The charts name no standard: a record that said it read one would be a false fact."""
    docs = large_docs[key]
    assert docs, f"{key} built nothing"
    problems, _ = type_gates.provenance_problems(docs, set(), COLUMNS)
    assert problems == [], problems[:10]
    assert {a["name"] for doc in docs for a in authored_attributes(doc)}.isdisjoint({"Standards"})
    assert all("supplier" in doc["dimension_provenance"] for doc in docs)


@pytest.mark.parametrize("key", KEYS)
def test_two_builds_are_byte_identical(key):
    first, second = type_gates.builds_under_two_hash_seeds(key)
    assert first, f"{key} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{key} builds differently under two hash seeds: {report}")


@pytest.mark.parametrize("key", KEYS)
def test_the_committed_golden_slice_is_a_fresh_build(key):
    path = SLICES / f"{key}.jsonl"
    assert path.is_file(), f"no golden slice at {path}"
    committed = path.read_text(encoding="utf-8").splitlines()
    report = type_gates.difference(committed, type_gates.default_records(key))
    if report:
        pytest.fail(f"{path.name} is not a fresh build: {report}")


@pytest.mark.parametrize("key", KEYS)
def test_every_other_type_is_byte_identical_with_this_type_left_out(key):
    moved = _moved_by_removing(key)
    assert not moved, f"building {key} changed {moved[:8]}"


@pytest.mark.parametrize("key", KEYS)
def test_every_other_type_builds_as_the_committed_golden_has_it(key):
    report = type_gates.others_moved_from_the_golden(key)
    if report:
        pytest.fail(report)


@pytest.mark.parametrize("key", KEYS)
def test_the_whole_build_carries_exactly_this_types_own_build(key):
    whole = _by_type(generate().lines)
    alone = _by_type(generate_type(GeneratorConfig(), key))
    assert whole[key] == alone[key]


@pytest.mark.parametrize("key", KEYS)
def test_every_row_of_the_table_is_built_and_nothing_else(key, large_docs):
    *_, rows = HARDWARE[key]
    built_rows = sorted({table_gates.row(doc, COLUMNS) for doc in large_docs[key]})
    assert len(built_rows) == len(rows)
    for got, want in zip(built_rows, sorted(rows), strict=True):
        assert got == pytest.approx(want, abs=0.01)


@pytest.mark.parametrize("key", KEYS)
def test_the_material_finish_and_packs_are_the_charts(key, large_docs):
    _, _, material, finish, packs, _ = HARDWARE[key]
    published = [table_gates.values(doc) for doc in large_docs[key]]
    assert {v["Material"]["value"] for v in published} == {material}
    assert {v["Finish"]["value"] for v in published if "Finish" in v} == {finish}
    assert {int(v[table_gates.PACK]["value_canonical"]) for v in published} == packs


@pytest.mark.parametrize("key", KEYS)
def test_larger_and_bigger_pack_each_cost_more(key, large_docs):
    _, _, material, *_ = HARDWARE[key]
    wrong, compared = table_gates.price_order(large_docs[key], key, "Length", (material,))
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:4]}"
    assert compared["size"] > 5 and compared["pack"] > 5, compared


@pytest.mark.parametrize("key", KEYS)
def test_every_price_is_inside_the_sanity_band(key, large_docs):
    prices = [doc["price_usd"] for doc in large_docs[key]]
    assert prices and SANITY_BAND[0] <= min(prices) and max(prices) <= SANITY_BAND[1]


@pytest.mark.parametrize("key", KEYS)
def test_every_row_has_a_valid_drawing_scaled_from_it(key):
    built_type = table_gates.catalog(key, LARGE_LINES)
    drawn = table_gates.drawings(built_type, key, COLUMNS)
    assert len(drawn) == len(HARDWARE[key][-1])
    assert [problem for _, svg in drawn.values() for problem in svg_problems(svg)] == []
    assert len({svg for _, svg in drawn.values()}) == len(drawn)


@pytest.mark.parametrize("key", KEYS)
def test_each_drawing_is_the_rows_length_tall_and_its_head_wide(key):
    drawn = table_gates.drawings(table_gates.catalog(key, LARGE_LINES), key, COLUMNS)
    assert drawn, f"{key} drew nothing"
    for (length, _, head), (figure, _) in drawn.items():
        assert figure.source == "record", (length, figure.source)
        x0, y0, x1, y1 = figure.figure.bounds()
        assert x1 - x0 == pytest.approx(head / MM, rel=1e-3), length
        assert y1 - y0 == pytest.approx(length / MM, rel=1e-3), length


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"source": ""}, "state one of standard and source"),
        ({"standard": "ASTM F1667"}, "state one of standard and source"),
    ],
    ids=["neither", "both"],
)
def test_a_table_states_one_of_standard_and_source(change, message):
    wrong = dataclasses.replace(nail_framing.TABLE, **change)
    assert message in tabletype.problems(wrong)


if __name__ == "__main__":
    SLICES.mkdir(parents=True, exist_ok=True)
    for key in KEYS:
        (SLICES / f"{key}.jsonl").write_text(
            "".join(line + "\n" for line in type_gates.default_records(key)), encoding="utf-8"
        )
