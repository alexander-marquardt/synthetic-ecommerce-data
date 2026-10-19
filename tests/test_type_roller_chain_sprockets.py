"""Per-type gates for ``roller_chain_sprockets``, a table-driven type (#101).

The template's gates (uniqueness, census names, provenance, byte-determinism
under two hash seeds, a golden slice, independence from every other type), and
on top of them what a table type promises (:mod:`table_gates`): every size it
builds is a row of its table, its declared prices rise with size, and every
row has a drawing scaled from that row.

The table is restated here, not read from the module, so a row typed wrong in
the module goes red. The bore, hub diameter and length through bore are those
of twenty product pages of a chain distributor, as the module's author read
them on 2026-10-07 (``roller_chain_sprockets.SOURCE_URL`` is one). The outside
diameter is computed, and is held against the one each page prints.

No price LEVEL is asserted beyond a wide sanity band and the declared base:
the prices are declared estimates, and ``tests/test_price.py`` lists the type
as not measured.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import table_gates
import type_gates
from published import authored_attributes, authored_entries
from synthetic_ecommerce_data.core import brands, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.drawing import svg_problems
from synthetic_ecommerce_data.core.drawing.model import Poly
from synthetic_ecommerce_data.domains.industrial import names, tabletype, taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate, generate_type
from synthetic_ecommerce_data.domains.industrial.product_types.motion import roller_chain_sprockets
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_type_seam import _by_type, _moved_by_removing

KEY = "roller_chain_sprockets"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

DIMENSIONAL = {"ASME B29.1"}
COLUMNS = ("Outside Dia.", "Pitch", "Bore Dia.", "Hub Diameter", "Length Through Bore")
#: ``(chain number, teeth, computed outside diameter, the outside diameter the
#: page prints, pitch, bore, hub diameter, length through bore)``, inches.
SPROCKETS = (
    ("35", 12, 1.625, 1.63, 3 / 8, 5 / 8, 39 / 32, 3 / 4),
    ("35", 15, 1.989, 1.99, 3 / 8, 5 / 8, 43 / 32, 3 / 4),
    ("35", 18, 2.352, 2.35, 3 / 8, 5 / 8, 55 / 32, 3 / 4),
    ("35", 20, 2.593, 2.59, 3 / 8, 5 / 8, 31 / 16, 3 / 4),
    ("35", 24, 3.073, 3.07, 3 / 8, 5 / 8, 2.0, 7 / 8),
    ("40", 12, 2.166, 2.17, 1 / 2, 3 / 4, 25 / 16, 7 / 8),
    ("40", 15, 2.652, 2.65, 1 / 2, 3 / 4, 29 / 16, 7 / 8),
    ("40", 18, 3.136, 3.14, 1 / 2, 3 / 4, 37 / 16, 1.0),
    ("40", 20, 3.457, 3.46, 1 / 2, 3 / 4, 21 / 8, 1.0),
    ("40", 24, 4.098, 4.10, 1 / 2, 3 / 4, 13 / 4, 1.0),
    ("50", 12, 2.708, 2.71, 5 / 8, 1.0, 127 / 64, 1.0),
    ("50", 15, 3.315, 3.32, 5 / 8, 1.0, 19 / 8, 1.0),
    ("50", 18, 3.920, 3.92, 5 / 8, 1.0, 23 / 8, 1.0),
    ("50", 20, 4.321, 4.32, 5 / 8, 1.0, 3.0, 1.0),
    ("50", 24, 5.122, 5.12, 5 / 8, 1.0, 3.0, 5 / 4),
    ("60", 12, 3.249, 3.25, 3 / 4, 5 / 4, 19 / 8, 5 / 4),
    ("60", 15, 3.978, 3.98, 3 / 4, 5 / 4, 23 / 8, 5 / 4),
    ("60", 18, 4.703, 4.70, 3 / 4, 5 / 4, 7 / 2, 5 / 4),
    ("60", 20, 5.185, 5.19, 3 / 4, 5 / 4, 31 / 8, 5 / 4),
    ("60", 24, 6.147, 6.15, 3 / 4, 5 / 4, 4.0, 5 / 4),
)
MM = table_gates.MM


def _mm(*inches: float) -> tuple[float, ...]:
    return tuple(round(value * MM, 3) for value in inches)


#: Each table row in millimetres, as ``table_gates.row`` reads a document,
#: with the chain number and tooth count it belongs to.
IDENTITY = {_mm(outside, *rest): (number, teeth) for number, teeth, outside, _, *rest in SPROCKETS}
ROWS = set(IDENTITY)
#: The restated row, in inches, of each outside diameter in millimetres. No
#: outside diameter is a half thousandth of a millimetre, so this key rounds
#: one way however the value was computed; a bore of 1-13/16" (46.0375 mm) does not.
BY_OUTSIDE = {
    _mm(outside)[0]: (number, teeth, outside, *rest)
    for number, teeth, outside, _, *rest in SPROCKETS
}
#: Each table row in inches, to a millionth.
ROWS_IN = {tuple(round(v, 6) for v in (outside, *rest)) for _, _, outside, _, *rest in SPROCKETS}
#: Each chain number's pitch as the roller chain type spells it.
PITCH_OF = {"35": "3/8", "40": "1/2", "50": "5/8", "60": "3/4"}

#: A build large enough to reach every row.
LARGE_LINES = 39000
#: What the default build holds: a move is a change to the table or its share.
DEFAULT_LINES = 54
DEFAULT_SKUS = 102
#: USD for one sprocket, any size and brand tier. Not a fit: a price outside
#: it is a broken ladder, not a wrong estimate.
SANITY_BAND = (5.0, 600.0)


#: The sprockets of the default build whose pitch the unit-mixing defect
#: restates in millimetres when it is applied to every record.
MILLIMETRE_PITCHES = 23


def _inches(doc: dict) -> tuple[float, ...]:
    """The row a document publishes, in inches to a millionth."""
    published = table_gates.values(doc)
    return tuple(round(float(published[name]["value_canonical"]) / MM, 6) for name in COLUMNS)


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


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


def test_the_registry_knows_it_as_a_table_type():
    """Its ``make`` wraps the table's own, and the registry keeps a table type
    by its key: a type it missed would be asked for a measured price."""
    assert tabletype.tables()[KEY] is roller_chain_sprockets.TABLE


def test_the_default_build_holds_the_declared_count():
    assert len(generate_type(GeneratorConfig(), KEY)) == DEFAULT_LINES
    assert len(_default_docs()) == DEFAULT_SKUS


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
    assert checked > 20, f"only {checked} dimensional claims were checked"


def test_the_provenance_does_not_say_the_standard_was_read(large_docs):
    assert {doc["dimension_provenance"] for doc in large_docs} == {
        "Outside Dia. computed from Pitch and Number of Teeth by the ASME B29.1 "
        "sprocket relation; Pitch is the ASME B29.1 dimension of the chain number; "
        "Bore Dia. and Hub Diameter and Length Through Bore as published on a "
        "distributor's product pages, for instance "
        "https://usarollerchain.com/products/40bs15-34-sprocket (retrieved 2026-10-07)"
    }


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_roller_chain_sprockets.py``."""
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
    assert len(ROWS_IN) == 20
    assert {_inches(doc) for doc in large_docs} == ROWS_IN


def test_every_sprocket_names_the_chain_number_and_tooth_count_of_its_row(large_docs):
    for doc in large_docs:
        published = table_gates.values(doc)
        stated = (published["ANSI Number"]["value"], int(published["Number of Teeth"]["value"]))
        assert stated == BY_OUTSIDE[table_gates.row(doc, COLUMNS)[0]][:2], doc["sku"]


def test_one_sprocket_publishes_exactly_its_row(large_docs):
    doc = next(d for d in large_docs if table_gates.row(d, COLUMNS)[0] == 67.361)
    published = {a["name"]: a["value"] for a in authored_entries(doc)}
    # A line may or may not state its finish, its standard and its measurement
    # system (the product's one draw, gen#63).
    for sparse in ("Finish", "Standards", "Measurement System"):
        published.pop(sparse, None)
    assert published == {
        "Material": "Steel",
        "Units per Pack": "1",
        "Outside Dia.": "2.6520",
        "Pitch": "1/2",
        "Bore Dia.": "3/4",
        "Hub Diameter": "1-13/16",
        "Length Through Bore": "7/8",
        "ANSI Number": "40",
        "Number of Teeth": "15",
    }


def test_the_material_finish_and_pack_are_the_declared_ones(large_docs):
    published = [table_gates.values(doc) for doc in large_docs]
    assert {v["Material"]["value"] for v in published} == {"Steel"}
    assert {v["Finish"]["value"] for v in published if "Finish" in v} == {"Black Oxide"}
    assert {int(v[table_gates.PACK]["value_canonical"]) for v in published} == {1}


def test_each_computed_outside_diameter_is_the_one_its_page_prints():
    """The pages print a hundredth of an inch. The relation and a typed tooth
    count are both held: a 14 for a 15 moves the diameter by over 0.1"."""
    for number, teeth, outside, printed, pitch, *_ in SPROCKETS:
        computed = roller_chain_sprockets.outside_diameter(pitch, teeth)
        assert computed == outside, (number, teeth)
        assert abs(computed - printed) < 0.0056, (number, teeth, computed, printed)
        assert roller_chain_sprockets.teeth_of(computed, pitch) == teeth, (number, teeth)


def test_chain_number_and_pitch_are_the_roller_chains_own(large_docs):
    """One filter value finds a chain and its sprockets: the attribute names,
    the machine keys, the spelling, the unit and the number all agree."""

    def shared(doc: dict) -> tuple | None:
        published = table_gates.values(doc)
        if "ANSI Number" not in published or "Pitch" not in published:
            return None
        number, pitch = published["ANSI Number"], published["Pitch"]
        return (
            number["key"], number["value"],
            pitch["key"], pitch["value"], pitch["unit_code"], pitch["value_canonical"],
        )  # fmt: skip

    chains = {shared(json.loads(line)) for line in type_gates.default_records("roller_chain")}
    sprockets = {shared(doc) for doc in large_docs}
    # The number itself is held by the subset below: the chain's own float.
    assert {found[:5] for found in sprockets} == {
        ("ansi_number", number, "chain_pitch", pitch, "INH") for number, pitch in PITCH_OF.items()
    }
    assert sprockets - chains == set()


def test_a_sprockets_pitch_being_a_length_does_not_make_the_chains_one():
    """A record's unit-mixing defect rewrites one of its OWN type's lengths.
    ``Pitch`` is a length column of this table and is not one of the roller
    chain's lengths, so with that defect on every record, no chain publishes
    its pitch in millimetres. Read every type's lengths instead and declaring
    this table changes what the chain builds."""
    built = generate(GeneratorConfig(defect_scale=1000.0), types=["roller_chain"])
    units = [
        published["Pitch"]["unit_code"]
        for published in map(table_gates.values, table_gates.docs(built))
        if "Pitch" in published
    ]
    assert set(units) == {"INH"}
    assert len(units) == 86


def test_a_pitch_published_in_millimetres_keeps_the_chain_pitch_key():
    """The unit-mixing defect changes a length's unit, never its machine key.
    A sprocket's ``Pitch`` restated as ``12.70mm`` under the name's default
    key would land in ``pitch``, a metric tap's thread pitch, and a thread
    pitch facet would offer a chain's link spacing. With the defect on every
    record, some sprockets publish the pitch in millimetres, and each one is
    still ``chain_pitch``."""
    built = generate(GeneratorConfig(defect_scale=1000.0), types=[KEY])
    pitches = [
        (published["Pitch"]["key"], published["Pitch"]["unit_code"])
        for published in map(table_gates.values, table_gates.docs(built))
        if "Pitch" in published
    ]
    assert sorted(set(pitches)) == [("chain_pitch", "INH"), ("chain_pitch", "MMT")]
    assert len([unit for _, unit in pitches if unit == "MMT"]) == MILLIMETRE_PITCHES


def test_a_size_off_the_table_is_a_row_rewritten_by_an_injected_defect():
    """With its defects on, the build shows sizes the table lacks. Each is a
    row's size within a hundredth of a millimetre: a defect the catalog
    injects on purpose, not a sprocket the table lacks."""
    docs = table_gates.docs(table_gates.catalog(KEY, LARGE_LINES, defects=True))
    sizes = sorted(row[0] for row in ROWS)
    read = [float(table_gates.values(doc)[COLUMNS[0]]["value_canonical"]) for doc in docs]
    assert [size for size in read if min(abs(size - s) for s in sizes) > 0.01] == []
    assert len([size for size in read if round(size, 3) not in sizes]) == 1


# --- the declared price keeps its order ---------------------------------------------


def test_a_larger_sprocket_costs_more_at_every_brand_tier(large_docs):
    wrong, compared = table_gates.price_order(large_docs, KEY, COLUMNS[0], ("Steel",))
    assert wrong == [], f"{len(wrong)} wrong, e.g. {wrong[:4]}"
    assert compared == {"size": 57, "material": 0, "pack": 0}


def test_the_smallest_costs_the_declared_base_at_the_standard_tier(large_docs):
    """The declared 26.00, moved a cent: the ending rule keeps a table price
    off the .00 class."""
    prices = {
        doc["price_usd"]
        for doc in large_docs
        if table_gates.row(doc, COLUMNS)[0] == 41.275
        and brands.tier_of(doc["brand"], KEY) == "standard"
    }
    assert prices == {26.01}


def test_every_price_is_inside_the_sanity_band(large_docs):
    low, high = SANITY_BAND
    outside = [
        (doc["sku"], doc["price_usd"]) for doc in large_docs if not low <= doc["price_usd"] <= high
    ]
    assert outside == [], outside[:5]


# --- the drawing ---------------------------------------------------------------------


def test_every_row_has_a_drawing_and_no_two_rows_share_one(drawn):
    assert set(drawn) == ROWS
    assert len({svg for _, svg in drawn.values()}) == 20


def test_each_drawing_is_scaled_from_its_row(drawn):
    """The disc has the row's tooth count and its outside diameter; the hub
    circle is the hub diameter across; the bore is the bore across, with a
    keyway a quarter of it wide cut into its top."""
    for row, (figure, _) in drawn.items():
        _, teeth, outside, _, bore, hub, _ = BY_OUTSIDE[row[0]]
        assert figure.source == "record", (row, figure.source)
        disc, hub_circle, hole = (s for s in figure.figure.shapes if isinstance(s, Poly))
        radii = [math.hypot(x, y) for x, y in disc.points]
        assert max(radii) == pytest.approx(outside / 2, rel=1e-6), row
        tips = [r for r in radii if r == pytest.approx(outside / 2, rel=1e-6)]
        assert len(tips) == 2 * teeth, row
        assert len(disc.points) == 6 * teeth, row
        assert min(radii) < min(math.hypot(x, y) for x, y in disc.points[2::6]), row
        for x, y in hub_circle.points:
            assert math.hypot(x, y) == pytest.approx(hub / 2, rel=1e-6), row
        *arc_points, right, left = hole.points
        for x, y in arc_points:
            assert math.hypot(x, y) == pytest.approx(bore / 2, rel=1e-6), row
        assert right[0] - left[0] == pytest.approx(bore / 4, rel=1e-6), row
        assert right[1] == left[1] > bore / 2, row


def test_the_teeth_stand_between_the_hub_and_the_outside_diameter(drawn):
    """A hub drawn over the tooth gaps would hide the teeth: on every row the
    gaps' floor is outside the hub circle."""
    for row, (figure, _) in drawn.items():
        disc, hub_circle, _ = (s for s in figure.figure.shapes if isinstance(s, Poly))
        root = min(math.hypot(x, y) for x, y in disc.points)
        assert root > max(math.hypot(x, y) for x, y in hub_circle.points), row


def test_no_drawing_carries_text_and_the_largest_is_small(drawn):
    assert [problem for _, svg in drawn.values() for problem in svg_problems(svg)] == []
    assert max(len(svg) for _, svg in drawn.values()) < 6000


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
