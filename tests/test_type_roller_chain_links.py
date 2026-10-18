"""Per-type gates for ``roller_chain_links``, a table-driven type (#101).

The template's gates (uniqueness, census names, provenance, byte-determinism
under two hash seeds, a golden slice, independence from every other type), and
on top of them what a table type promises (:mod:`table_gates`): every size it
builds is a row of its table, its declared prices keep their orders, and every
row has a drawing scaled from that row.

Two things are this type's own. It is two products, a connecting link and an
offset link, so every material and pack must be built as both. And it shares
three attributes with
``roller_chain``, so a link must publish each of them exactly as the chain of
its number does: one filter value has to find both.

The table is restated here, not read from the module, so a row typed wrong in
the module goes red. It is the single strand table of the chart at
https://usarollerchain.com/pages/roller-chain-size-chart as the module's
author read it on 2026-10-07; the page presents it as ASME B29.1's series and
the standard was not read.

No price LEVEL is asserted beyond a wide sanity band: the prices are declared
estimates, and ``tests/test_price.py`` finds the type as not measured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import table_gates
import type_gates
from published import authored_attributes, authored_entries
from synthetic_ecommerce_data.core import brands, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.drawing import FIGURES, draw_sku, svg_problems
from synthetic_ecommerce_data.core.drawing.model import Disc
from synthetic_ecommerce_data.domains.industrial import names, tabletype, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "roller_chain_links"
CHAIN = "roller_chain"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

DIMENSIONAL = {"ASME B29.1"}
COLUMNS = ("Pitch", "Inside Width")
#: Chain number -> ``(pitch, roller width)`` in inches, as the chart prints
#: them: ten of its fourteen single strand sizes.
CHART = {
    "25": (0.250, 0.125), "35": (0.375, 0.188), "40": (0.500, 0.312), "50": (0.625, 0.375),
    "60": (0.750, 0.500), "80": (1.000, 0.625), "100": (1.250, 0.750), "120": (1.500, 1.000),
    "140": (1.750, 1.000), "160": (2.000, 1.250),
}  # fmt: skip
#: Chain number -> the chart's ``(plate height, plate thickness, pin
#: diameter)`` in inches: drawn, not published.
PLATE = {
    "25": (0.228, 0.029, 0.091), "35": (0.356, 0.050, 0.141), "40": (0.475, 0.058, 0.156),
    "50": (0.594, 0.079, 0.200), "60": (0.712, 0.093, 0.234), "80": (0.950, 0.125, 0.312),
    "100": (1.188, 0.157, 0.375), "120": (1.425, 0.189, 0.437), "140": (1.663, 0.219, 0.500),
    "160": (1.901, 0.255, 0.563),
}  # fmt: skip
#: The chart prints three decimals of an inch (0.312 for 5/16).
PRINTED = 0.0006

CONNECTING = "Roller Chain Connecting Link"
OFFSET = "Roller Chain Offset Link"
#: Cheapest first.
MATERIALS = ("Steel", "18-8 Stainless Steel")
PACKS = {1, 2, 5}
#: The three attributes a link shares with the chain of its number.
SHARED = ("Pitch", "ANSI Number", "Inside Width")

#: A build large enough to reach every row in every material and pack, as
#: both links.
LARGE_LINES = 39000
#: What the default build holds: a move is a change to the table or its share.
DEFAULT_SKUS = 94
#: USD for one pack, any size, material, pack, link and brand tier. Not a fit:
#: a price outside it is a broken ladder, not a wrong estimate.
SANITY_BAND = (1.0, 600.0)
#: The drawing's nominal proportions: the gap between its two views in plate
#: heights, and a pin's stub past each plate in plate thicknesses.
GAP = 0.3
STUB = 1.0
#: The chart's rows as the inch fractions its printed decimals stand for,
#: which is what a record publishes.
FRACTIONS = {
    "25": (1 / 4, 1 / 8), "35": (3 / 8, 3 / 16), "40": (1 / 2, 5 / 16), "50": (5 / 8, 3 / 8),
    "60": (3 / 4, 1 / 2), "80": (1.0, 5 / 8), "100": (5 / 4, 3 / 4), "120": (3 / 2, 1.0),
    "140": (7 / 4, 1.0), "160": (2.0, 5 / 4),
}  # fmt: skip
#: Any brand of the book: a drawing needs one's house style.
BRAND = sorted(brands.BY_NAME)[0]

MM = table_gates.MM


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


def _number(doc: dict) -> str:
    return table_gates.values(doc)["ANSI Number"]["value"]


def _item(doc: dict) -> str:
    return table_gates.values(doc)["Item"]["value"]


@pytest.fixture(scope="module")
def large():
    return table_gates.catalog(KEY, LARGE_LINES)


@pytest.fixture(scope="module")
def large_docs(large) -> list[dict]:
    return table_gates.docs(large)


@pytest.fixture(scope="module")
def drawn(large):
    return table_gates.drawings(large, KEY, COLUMNS)


# --- the template's gates ---------------------------------------------------------


def test_the_type_is_modelled_in_its_own_module():
    assert KEY in typespec.modelled(), f"{KEY} is still a breadth row"


def test_the_type_does_not_also_exist_as_a_breadth_row():
    from synthetic_ecommerce_data.domains.industrial import breadth

    assert [row.key for row in breadth.rows() if row.key == KEY] == []


def test_the_type_is_found_as_a_table_type():
    """Its ``make`` wraps the table's own, and the registry keeps a table type
    by its key: a type it missed would be asked for a measured price."""
    assert tabletype.tables()[KEY].cells == 60


def test_the_default_build_holds_the_declared_count():
    docs = _default_docs()
    assert len(docs) == DEFAULT_SKUS
    assert len({doc["product_id"] for doc in docs}) == 52


def test_no_two_skus_of_one_brand_are_the_same_product():
    docs = _default_docs()
    assert docs, f"{KEY} built nothing"
    assert same_product_duplicates(docs) == []


def test_every_published_name_passes_the_census_gate():
    (path,) = taxonomy.LEAVES[KEY]
    emitted = {a["name"] for doc in _default_docs() for a in authored_attributes(doc)}
    assert emitted, f"{KEY} published no attribute"
    assert names.name_problems(emitted, OBSERVED, CENSUS, names.own_nouns(path)) == []


def test_the_provenance_names_where_each_published_dimension_came_from(large_docs):
    problems, checked = type_gates.provenance_problems(large_docs, DIMENSIONAL, COLUMNS)
    assert problems == [], problems[:10]
    assert (checked, len(large_docs)) == (401, 769)


def test_the_provenance_does_not_say_the_standard_was_read(large_docs):
    """Only a distributor's chart of B29.1's dimensions was read."""
    (provenance,) = {doc["dimension_provenance"] for doc in large_docs}
    assert "usarollerchain.com/pages/roller-chain-size-chart" in provenance
    assert "read from" not in provenance


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_roller_chain_links.py``."""
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


# --- the table ----------------------------------------------------------------------


def test_every_row_of_the_table_is_built_and_nothing_else(large_docs):
    built = {(_number(doc), *table_gates.row(doc, COLUMNS)) for doc in large_docs}
    assert sorted(number for number, _, _ in built) == sorted(CHART)
    for number, pitch, width in built:
        assert pitch / MM == pytest.approx(CHART[number][0], abs=PRINTED), number
        assert width / MM == pytest.approx(CHART[number][1], abs=PRINTED), number


def test_every_row_is_built_as_both_links_in_every_material_and_pack(large_docs):
    published = [table_gates.values(doc) for doc in large_docs]
    cells = {
        (
            v["Item"]["value"],
            v["Material"]["value"],
            int(v[table_gates.PACK]["value_canonical"]),
            v["ANSI Number"]["value"],
        )
        for v in published
    }
    assert {cell[0] for cell in cells} == {CONNECTING, OFFSET}
    assert {cell[1] for cell in cells} == set(MATERIALS)
    assert {cell[2] for cell in cells} == PACKS
    assert len(cells) == 2 * len(MATERIALS) * len(PACKS) * len(CHART) == 120


def _is_plain_40(doc: dict) -> bool:
    published = table_gates.values(doc)
    return (
        len(doc["attributes"]) == 9
        and {"Finish", "Standards"} <= set(published)
        and published["ANSI Number"]["value"] == "40"
        and published["Material"]["value"] == "Steel"
    )


def test_one_link_publishes_exactly_these_attributes(large_docs):
    """A steel link for 40 chain: the first that states its finish and its
    standard and nothing sparse besides. Its link and its pack are its own;
    everything it shares with the chain is stated here."""
    doc = min((d for d in large_docs if _is_plain_40(d)), key=lambda d: d["sku"])
    pack = table_gates.values(doc)[table_gates.PACK]["value"]
    assert [(a["key"], a["name"], a["value"]) for a in authored_entries(doc)] == [
        ("item", "Item", _item(doc)),
        ("style", "Style", "Single Strand"),
        ("material", "Material", "Steel"),
        ("finish", "Finish", "Plain"),
        ("package_quantity", "Package Quantity", pack),
        ("standards", "Standards", "ASME B29.1"),
        ("chain_pitch", "Pitch", "1/2"),
        ("ansi_number", "ANSI Number", "40"),
        ("inside_width", "Inside Width", "5/16"),
    ]
    assert (_item(doc) in (CONNECTING, OFFSET), int(pack) in PACKS) == (True, True)
    assert doc["category_path"] == [
        "Motion control & fluid power",
        "Chain & sprockets",
        "Roller chain links",
    ]


def test_a_link_publishes_what_it_shares_with_its_chain_exactly_as_the_chain_does(large_docs):
    """Key, name, value, unit and canonical value: a facet value is all five,
    so a link that spelled its pitch 0.5" would sit beside the chain's 1/2"."""
    chains = table_gates.docs(table_gates.catalog(CHAIN, LARGE_LINES))

    def shared(docs: list[dict]) -> dict[str, set[str]]:
        found: dict[str, set[str]] = {}
        for doc in docs:
            published = table_gates.values(doc)
            if published["Style"]["value"] != "Single Strand" or set(SHARED) - set(published):
                continue
            entry = json.dumps([published[name] for name in SHARED], sort_keys=True)
            found.setdefault(published["ANSI Number"]["value"], set()).add(entry)
        return found

    of_chains, of_links = shared(chains), shared(large_docs)
    assert sorted(of_links) == sorted(CHART)
    assert {number: of_chains[number] for number in of_links} == of_links
    assert [len(entries) for entries in of_links.values()] == [1] * len(CHART)


# --- the declared price keeps its orders --------------------------------------------


def test_larger_dearer_material_and_bigger_pack_each_cost_more(large_docs):
    """Over both links at once: the ladder has no term for the link, so one
    size, material, pack and brand tier has one price whichever link it is."""
    wrong, compared = table_gates.price_order(large_docs, KEY, "Pitch", MATERIALS)
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:4]}"
    assert min(compared.values()) > 20, f"too few pairs compared: {compared}"


def test_every_price_is_inside_the_sanity_band(large_docs):
    low, high = SANITY_BAND
    outside = [
        (doc["sku"], doc["price_usd"]) for doc in large_docs if not low <= doc["price_usd"] <= high
    ]
    assert outside == [], outside[:5]


# --- the drawing ---------------------------------------------------------------------


def test_every_row_has_a_drawing_and_no_two_rows_share_one(drawn):
    rows = [tuple(round(value * MM, 3) for value in row) for row in FRACTIONS.values()]
    assert sorted(drawn) == sorted(rows)
    assert len({svg for _, svg in drawn.values()}) == len(CHART)


@pytest.mark.parametrize("kind", [CONNECTING, OFFSET])
def test_each_drawing_is_scaled_from_its_row(kind):
    """A plate height past the pitch wide, and tall by both views: the plate,
    the gap, and the link from above (the roller width, four plates and two
    pin stubs)."""
    figure, _ = FIGURES[KEY]
    for number, (pitch, width) in FRACTIONS.items():
        height, thick, _ = PLATE[number]
        record = {"Item": kind, "Pitch": f'{pitch}"', "Inside Width": f'{width}"'}
        made = figure(record)
        assert made.source == "record", number
        x0, y0, x1, y1 = made.figure.bounds()
        assert x1 - x0 == pytest.approx(CHART[number][0] + height, rel=1e-6), number
        deep = width + 4 * thick + 2 * STUB * thick
        assert y1 - y0 == pytest.approx((1 + GAP) * height + deep, rel=1e-6), number
        assert made.figure.size_in == pitch


def test_the_two_links_are_drawn_apart():
    """An offset link has one pin and an open bushing where a connecting link
    has two pins, and its plates are cranked."""
    figure, _ = FIGURES[KEY]
    record = {"Pitch": '1/2"', "Inside Width": '5/16"'}
    connecting = figure({**record, "Item": CONNECTING}).figure
    offset = figure({**record, "Item": OFFSET}).figure

    def discs(fig) -> list[tuple[float, str]]:
        return [(shape.centre[0], shape.role) for shape in fig.shapes if isinstance(shape, Disc)]

    assert discs(connecting) == [(0.0, "plain"), (0.5, "plain")]
    assert discs(offset) == [(0.0, "hole"), (0.5, "plain")]
    first, _ = draw_sku(KEY, BRAND, {**record, "Item": CONNECTING})
    second, _ = draw_sku(KEY, BRAND, {**record, "Item": OFFSET})
    assert first != second


def test_a_record_naming_no_link_is_drawn_as_a_connecting_link_and_says_so():
    figure, _ = FIGURES[KEY]
    record = {"Pitch": '1/2"', "Inside Width": '5/16"'}
    made = figure({**record, "Item": "Roller Chain"})
    assert made.source == "partial"
    assert made.figure.shapes == figure({**record, "Item": CONNECTING}).figure.shapes


def test_no_drawing_carries_text_and_the_largest_is_small(drawn):
    svgs = [svg for _, svg in drawn.values()]
    for kind in (CONNECTING, OFFSET):
        svg, _ = draw_sku(KEY, BRAND, {"Item": kind, "Pitch": '2"', "Inside Width": '1-1/4"'})
        svgs.append(svg)
    assert [problem for svg in svgs for problem in svg_problems(svg)] == []
    assert max(len(svg) for svg in svgs) < 8000


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
