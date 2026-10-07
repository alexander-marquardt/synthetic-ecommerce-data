"""Per-type gates for ``roller_chain``, deepened from breadth (#53), and the
``Pitch`` key split it needs (#36).

The gates are the lock nuts' (:mod:`test_type_lock_nuts_nylon_insert` says
what each one catches) with this type's ``KEY`` and floor.

#36: a roller chain's ``Pitch`` is the spacing of its links, an inch length,
and a metric tap's ``Pitch`` is its thread pitch. Real catalogs print both as
``Pitch``, so the display name stays, but the machine key differs: the chain's
is ``chain_pitch``, the tap's stays ``pitch``. Without the split the facet
derivation measures one ``pitch`` over both types and buckets a chain's
``1/2"`` beside a tap's ``1.25 mm``.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

import pytest

import type_gates
from published import published_attributes
from synthetic_industrial_products.catalog import brands, emit, names, taxonomy, typespec
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate, generate_type
from synthetic_industrial_products.drawing import draw_sku, svg_problems
from synthetic_industrial_products.drawing.model import Bars, Disc, Poly
from synthetic_industrial_products.prism import derive
from synthetic_industrial_products.product_types.motion import roller_chain
from test_attribute_names import CENSUS, OBSERVED
from test_catalog_brands_voice import same_product_duplicates
from test_sku_drawings import MAX_DRAWING_BYTES
from test_type_seam import _by_type, _moved_by_removing

KEY = "roller_chain"

#: The committed slice: this type's flat records at the default build.
SLICE = Path(__file__).parent / "data" / "golden_slices" / f"{KEY}.jsonl"

#: The default build makes 81 SKUs; a floor that catches a collapse back to a
#: breadth row's one or two, not a target.
DEFAULT_SKU_FLOOR = 50

#: The dimensional standard every line claims, and the dimensions read from it.
DIMENSIONAL = {"ASME B29.1"}
DIMENSIONS = ("Pitch", "Roller Dia.", "Inside Width")


def _default_docs() -> list[dict]:
    return [json.loads(line) for line in type_gates.default_records(KEY)]


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
    assert checked > 30, f"only {checked} dimensional claims were checked"


def test_two_builds_are_byte_identical():
    """In two processes: a set-order draw agrees with itself in one."""
    first, second = type_gates.builds_under_two_hash_seeds(KEY)
    assert first, f"{KEY} built nothing"
    report = type_gates.difference(first, second)
    if report:
        pytest.fail(f"{KEY} builds differently under two hash seeds: {report}")


def test_the_committed_golden_slice_is_a_fresh_build():
    """Regenerate with ``uv run python tests/test_type_roller_chain.py``."""
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


# --- #36: a chain's Pitch is not a tap's Pitch --------------------------------


@pytest.fixture(scope="module")
def default_rows() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


def _pitch_entries(rows: list[dict], type_key: str) -> list[dict]:
    return [
        a
        for row in rows
        if row["product_type"] == type_key
        for a in row["attributes"]
        if a["name"] == "Pitch"
    ]


def test_a_chains_pitch_is_keyed_chain_pitch_in_inches(default_rows):
    entries = _pitch_entries(default_rows, KEY)
    chains = [row for row in default_rows if row["product_type"] == KEY]
    assert len(entries) == len(chains), (len(entries), len(chains))
    assert {a["key"] for a in entries} == {"chain_pitch"}
    assert {a["unit_code"] for a in entries} == {"INH"}
    assert all("chain_pitch" in row["facets"] for row in chains)
    assert not any("pitch" in row["facets"] for row in chains)


def test_a_taps_pitch_keeps_the_key_pitch(default_rows):
    entries = _pitch_entries(default_rows, "tap_spiral_point")
    assert entries, "no tap published a Pitch"
    assert {a["key"] for a in entries} == {"pitch"}
    assert {a["unit_code"] for a in entries} == {"MMT"}


def test_the_facet_derivation_measures_the_two_pitches_apart(default_rows):
    stats = derive.measure(default_rows)
    pitches = {key: s for key, s in stats.items() if s.name == "Pitch"}
    assert sorted(pitches) == ["chain_pitch", "pitch"]
    assert pitches["chain_pitch"].product_types == (KEY,)
    assert pitches["pitch"].product_types == ("tap_spiral_point",)
    decisions = [derive.decide(s) for s in pitches.values()]
    assert sorted(d.stats.key for d in decisions) == ["chain_pitch", "pitch"]


# --- the chain number is B29.1's own rule, and the table is the standard's ----

#: B29.1's standard series restated from the printed decimals of the size chart
#: the module cites (``roller_chain.SOURCE_URL``, retrieved 2026-10-07), not
#: from the module: chain number -> (pitch, roller diameter, width between the
#: roller link plates), inches. Chains 25 and 35 are rollerless.
B29_1 = {
    "25": (0.250, None, 0.125), "35": (0.375, None, 0.188), "40": (0.500, 0.312, 0.312),
    "50": (0.625, 0.400, 0.375), "60": (0.750, 0.469, 0.500), "80": (1.000, 0.625, 0.625),
    "100": (1.250, 0.750, 0.750), "120": (1.500, 0.875, 1.000), "140": (1.750, 1.000, 1.000),
    "160": (2.000, 1.125, 1.250), "180": (2.250, 1.406, 1.406), "200": (2.500, 1.562, 1.500),
    "240": (3.000, 1.875, 1.875),
}  # fmt: skip
STRAND_SUFFIX = {"Single Strand": "", "Double Strand": "-2", "Triple Strand": "-3"}
LARGE_LINES = 39000
MM = 25.4


def _clean_docs(lines: int | None = None) -> list[dict]:
    """The type's documents with no injected defect, so each value is the builder's."""
    config = GeneratorConfig(defect_scale=0.0, **({"lines": lines} if lines else {}))
    catalog = generate(config, types=[KEY])
    return [doc for line in catalog.lines for doc in emit.flat_documents(catalog, line)]


@pytest.fixture(scope="module", params=[None, LARGE_LINES], ids=["default", "100k"])
def clean_docs(request) -> list[dict]:
    return _clean_docs(request.param)


def _attrs(doc: dict) -> dict[str, dict]:
    return {a["name"]: a for a in doc["attributes"]}


def _inches(attribute: dict) -> float:
    """``value_canonical`` is millimetres whatever unit the value is written in."""
    return float(attribute["value_canonical"]) / MM


def test_a_chains_pitch_is_its_chain_numbers_leading_digits_in_eighths(clean_docs):
    """B29.1's numbering rule: the digits left of the last one count eighths
    of an inch of pitch, and a multiple strand chain adds ``-2`` or ``-3``."""
    numbers = set()
    for doc in clean_docs:
        attrs = _attrs(doc)
        number, _, strands = attrs["ANSI Number"]["value"].partition("-")
        numbers.add(number)
        assert _inches(attrs["Pitch"]) == pytest.approx(int(number[:-1]) / 8, abs=1e-6), number
        suffix = f"-{strands}" if strands else ""
        assert suffix == STRAND_SUFFIX[attrs["Style"]["value"]], attrs["ANSI Number"]["value"]
    assert numbers <= set(B29_1)
    assert len(numbers) >= 11, sorted(numbers)


def test_every_published_dimension_is_the_standards_own_row(clean_docs):
    checked = 0
    for doc in clean_docs:
        attrs = _attrs(doc)
        number = attrs["ANSI Number"]["value"].partition("-")[0]
        pitch, roller, width = B29_1[number]
        assert _inches(attrs["Pitch"]) == pytest.approx(pitch, abs=1e-6), number
        if roller is None:
            assert "Roller Dia." not in attrs, number
        for name, expected in (("Roller Dia.", roller), ("Inside Width", width)):
            if name in attrs:
                # The standard prints three decimals of an inch fraction.
                assert abs(_inches(attrs[name]) - expected) < 0.0006, (number, name)
                checked += 1
    assert checked > 100, f"only {checked} dimensions were checked"


# --- the drawing shows links ---------------------------------------------------


@pytest.mark.parametrize("strands", sorted(STRAND_SUFFIX))
def test_the_side_view_draws_link_plates_one_pitch_long(strands):
    """A link plate spans ONE pitch, round about its two pins, and roller
    links alternate with pin links: three plates over four pins, each one
    pitch between centres, the middle one of the other kind."""
    record = {"Pitch": '1"', "Roller Dia.": '5/8"', "Inside Width": '5/8"', "Style": strands}
    drawn = roller_chain.chain(record)
    assert drawn.source == "record"
    figure = drawn.figure
    # The side view straddles the chain's centre line; the top view lies clear of it.
    plates = sorted(
        (min(x for x, _ in s.points), s)
        for s in figure.shapes
        if isinstance(s, Poly) and min(y for _, y in s.points) < 0 < max(y for _, y in s.points)
    )
    assert len(plates) == 3, len(plates)
    heights = []
    for k, (left, plate) in enumerate(plates):
        height = max(y for _, y in plate.points) - min(y for _, y in plate.points)
        length = max(x for x, _ in plate.points) - left
        # Round ended about each pin: centre to centre is the length less the height.
        assert length - height == pytest.approx(1.0), (k, length, height)
        assert left + height / 2 == pytest.approx(float(k)), (k, left)
        heights.append(round(height, 6))
    assert heights[0] == heights[2] != heights[1], heights
    pins = sorted(s.centre for s in figure.shapes if isinstance(s, Disc) and s.role == "hole")
    assert pins == [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)]


#: Rectangles one strand shows from above: two plates a link over three links,
#: and a roller at each of four pins.
RECTS_A_STRAND = 10


@pytest.mark.parametrize(
    ("style", "count"), [("Single Strand", 1), ("Double Strand", 2), ("Triple Strand", 3)]
)
def test_every_strand_from_above_is_the_first_one_repeated_in_one_path(style, count):
    record = {"Pitch": '1"', "Roller Dia.": '5/8"', "Inside Width": '5/8"', "Style": style}
    bars = [s for s in roller_chain.chain(record).figure.shapes if isinstance(s, Bars)]
    assert len(bars) == 1, len(bars)
    rects = bars[0].rects
    assert len(rects) == RECTS_A_STRAND * count
    first = rects[:RECTS_A_STRAND]
    # A strand is its inside width and four plate thicknesses further down.
    step = 0.625 + 4 * roller_chain._PLATE_THICKNESS
    for k in range(count):
        for (x0, y0, x1, y1), (a0, b0, a1, b1) in zip(
            first, rects[k * RECTS_A_STRAND : (k + 1) * RECTS_A_STRAND], strict=True
        ):
            assert (a0, a1) == (x0, x1)
            assert (b0 - y0, b1 - y1) == pytest.approx((k * step, k * step))


def test_no_chain_any_brand_could_offer_draws_past_the_size_cap():
    """The cap ``test_sku_drawings`` holds the committed catalog to, held here
    for every table row in three strands, in every material and brand's house
    style: the committed catalog shows only the chains one seed happened to
    stock, and the first three-link view was 14,267 bytes in it."""
    materials = sorted({offer.material for offer, _ in roller_chain.OFFERS})
    largest, drawn = 0, 0
    for _, pitch, roller, width in roller_chain.ANSI:
        record = {"Pitch": f'{float(pitch)}"', "Inside Width": f'{float(width)}"'}
        if roller is not None:
            record["Roller Dia."] = f'{float(roller)}"'
        for material in materials:
            for brand in brands.BRANDS:
                data, _ = draw_sku(
                    KEY, brand, {**record, "Style": "Triple Strand", "Material": material}
                )
                assert svg_problems(data) == [], (brand, record)
                largest = max(largest, len(data))
                drawn += 1
    assert drawn == len(roller_chain.ANSI) * len(materials) * len(brands.BRANDS)
    assert largest < MAX_DRAWING_BYTES, largest


# --- the strand count moves the price -----------------------------------------

STRANDS_IN_ORDER = ("Single Strand", "Double Strand", "Triple Strand")
#: The same-spec sets each build holds: one chain number in one material and
#: length, offered in two or three strand counts.
STRAND_SETS = {None: 10, LARGE_LINES: 13}


def _strand_sets(docs: list[dict]) -> dict[tuple, dict[str, list[float]]]:
    """Same-spec sets: (chain number, material, length) -> strand count -> prices.

    The finish is left out: it is not published on every line, and no finish
    moves a price.
    """
    cells: dict[tuple, dict[str, list[float]]] = {}
    for doc in docs:
        attrs = _attrs(doc)
        spec = (
            attrs["ANSI Number"]["value"].partition("-")[0],
            attrs["Material"]["value"],
            attrs["Length"]["value"],
        )
        cells.setdefault(spec, {}).setdefault(attrs["Style"]["value"], []).append(doc["price_usd"])
    return {spec: by for spec, by in cells.items() if len(by) > 1}


@pytest.mark.parametrize("lines", [None, LARGE_LINES], ids=["default", "100k"])
def test_more_strands_cost_more_in_every_same_spec_set(lines):
    """A double strand chain is about twice the steel of a single strand one of
    its pitch, material and length, and a triple strand one three times: the
    median price of every such set rises with the strand count. Read off the
    build as it ships, defects included, so the sets are the catalog's own."""
    config = GeneratorConfig(**({"lines": lines} if lines else {}))
    catalog = generate(config, types=[KEY])
    docs = [doc for line in catalog.lines for doc in emit.flat_documents(catalog, line)]
    sets = _strand_sets(docs)
    assert len(sets) == STRAND_SETS[lines], len(sets)
    falling = []
    for spec, by in sorted(sets.items()):
        medians = [statistics.median(by[s]) for s in STRANDS_IN_ORDER if s in by]
        if any(low >= high for low, high in zip(medians, medians[1:], strict=False)):
            falling.append((spec, medians))
    assert falling == [], falling


def test_the_provenance_says_where_the_dimensions_were_read():
    """ASME's own text was not read: the record must not claim it was."""
    assert roller_chain.PROVENANCE == (
        "Pitch and Roller Dia. and Inside Width are ASME B29.1 dimensions as "
        "published in the size chart at " + roller_chain.SOURCE_URL + " (retrieved 2026-10-07)"
    )


if __name__ == "__main__":
    SLICE.parent.mkdir(parents=True, exist_ok=True)
    SLICE.write_text(
        "".join(line + "\n" for line in type_gates.default_records(KEY)), encoding="utf-8"
    )
