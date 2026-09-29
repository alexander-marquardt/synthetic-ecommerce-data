"""Every value the catalog claims to offer reaches at least one document.

The defect class this exists to catch is a **silent hole**: the generator
offers a list of sizes, draws from it once per line, and a value that never
happens to be drawn simply is not in the catalog. Nothing fails, nothing is
logged, and the only way anyone finds out is a shopper asking for it.

Measured before the rotations in
:meth:`~synthetic_industrial_products.catalog.generate.Generator._rotate` went
in, on the committed catalog, over ``facets_num.milling_dia`` at +/- 0.02 mm::

    11 mm ->  0 documents        control   2.5 mm ->  5
    15 mm ->  0 documents                  4 mm   -> 33
    25 mm ->  0 documents                  20 mm  -> 31

Three of the reference distributor's twelve end-mill patterns therefore had no correct
answer available, one of them -- ``25mm end mill`` -- the demo's own headline
case. The thread size ``7/16-14`` was absent for the same reason on the other
side of the catalog, blocking the one query the reference distributor singled out as hard.

So the assertions here are stated over the WHOLE catalog and derived from the
offered lists rather than from a copy of them: the series in
:mod:`~synthetic_industrial_products.catalog.series` and the extracted tables
in :mod:`~synthetic_industrial_products.catalog.standards` are the same lists
the generator draws from, so a value added to either is checked the day it
appears and not the day somebody remembers to add it here.

Every one of them runs twice, against the committed files and against a fresh
build -- see ``SOURCES`` below for why neither alone is enough.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import compat, series, standards

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden-catalog"
REBUILD = "uv run sip-generate build --out golden-catalog"

MM_PER_INCH = 25.4

#: The tolerance the issue measured at: a published 11.00 mm and a published
#: 7/16" (11.1125 mm) are different sizes and must not answer for each other.
MM_TOLERANCE = 0.02

#: The three sizes the reference distributor's own patterns name. Pinned BESIDE the derived
#: sweep rather than instead of it: the sweep proves every offered size
#: reaches a document, and these three prove the offered list is the one the
#: reference distributor asks for. A sweep alone stays green if all three are deleted from
#: the series.
REFERENCE_METRIC_DIAS = (11.0, 15.0, 25.0)

#: And the thread size, on the product type the reference distributor's query names.
REFERENCE_THREAD = "7/16-14"
HEX_BOLT_TYPE = "bolt_hex"


#: Every property here is asserted against TWO sources, and both are needed.
#:
#: ``committed`` is ``golden-catalog/``, the artifact anyone can read without
#: running a build. Asserting against it is what stops a careless
#: ``sip-generate build && git commit -a`` from a broken generator sailing
#: through, and it is why ``test_catalog_golden`` states its headline numbers
#: that way too.
#:
#: ``generated`` is a fresh build in memory. Without it every property here
#: would be unprovable by mutation: a defect planted in the generator does not
#: move the committed bytes, so a test reading only those stays green while the
#: generator is broken -- which is exactly the shape of the failure this
#: repository keeps finding.
SOURCES = ("committed", "generated")


@pytest.fixture(scope="module", params=SOURCES)
def catalog(request) -> tuple[list[dict], list[dict]]:
    if request.param == "committed":
        def read(name: str) -> list[dict]:
            with (GOLDEN_DIR / name).open(encoding="utf-8") as handle:
                return [json.loads(line) for line in handle]

        return read("flat.jsonl"), read("nested.jsonl")

    from synthetic_industrial_products.catalog import emit
    from synthetic_industrial_products.catalog.config import GeneratorConfig
    from synthetic_industrial_products.catalog.generate import generate

    built = generate(GeneratorConfig())
    return list(emit.iter_flat(built)), list(emit.iter_nested(built))


@pytest.fixture(scope="module")
def flat_docs(catalog: tuple[list[dict], list[dict]]) -> list[dict]:
    return catalog[0]


def _milling_dias_mm(docs: list[dict]) -> list[tuple[float, str]]:
    """Every published cutting diameter, in millimetres, with its product type.

    Read out of ``facets_num``, which the emitter parses back out of the
    published STRING -- so this is the magnitude a range facet would actually
    filter on, not the magnitude the generator started from.
    """
    return [
        (doc["facets_num"]["milling_dia"] * MM_PER_INCH, doc["product_type"])
        for doc in docs
        if "milling_dia" in doc.get("facets_num", {})
    ]


def test_every_offered_metric_cutting_diameter_reaches_a_document(flat_docs: list[dict]) -> None:
    published = _milling_dias_mm(flat_docs)
    assert published, "no document publishes a cutting diameter at all"
    missing = [
        dia
        for dia in series.METRIC_CUTTING_DIAS
        if not any(abs(value - dia) < MM_TOLERANCE for value, _ in published)
    ]
    assert missing == [], (
        f"{len(missing)} metric cutting diameter(s) the series offers reach no "
        f"document: {missing}. A size in the series and not in the catalog is a "
        f"query with no correct answer, and nothing else in this suite notices. "
        f"Regenerate with `{REBUILD}`."
    )


def test_every_offered_imperial_cutting_diameter_reaches_a_document(flat_docs: list[dict]) -> None:
    published = [value for value, _ in _milling_dias_mm(flat_docs)]
    missing = [
        str(dia)
        for dia in series.IMPERIAL_CUTTING_DIAS
        if not any(
            abs(value - float(dia) * MM_PER_INCH) < MM_TOLERANCE for value in published
        )
    ]
    assert missing == [], (
        f"{len(missing)} inch cutting diameter(s) the series offers reach no document: {missing}"
    )


@pytest.mark.parametrize("dia", REFERENCE_METRIC_DIAS)
@pytest.mark.parametrize("type_key", ["end_mill_square", "end_mill_ball"])
def test_the_sizes_the_reference_distributor_asks_for_exist_in_both_end_mill_styles(
    flat_docs: list[dict], dia: float, type_key: str
) -> None:
    """Both styles, because two of the three patterns name one.

    ``15 mm ball end mills`` is a style and a size together, and a catalog
    that carries the size only as a square end mill answers it with the wrong
    product rather than with nothing -- which is worse, because it looks like
    an answer.
    """
    count = sum(
        1
        for value, published_type in _milling_dias_mm(flat_docs)
        if published_type == type_key and abs(value - dia) < MM_TOLERANCE
    )
    assert count > 0, (
        f"no {type_key} document publishes a {dia:g} mm cutting diameter. "
        f"The reference distributor's pattern for this size has no correct answer."
    )


def test_a_25_mm_cutting_diameter_has_exactly_one_spelling(
    flat_docs: list[dict],
) -> None:
    """``25mm``, and nothing else -- the shopper's own spelling.

    This test used to assert the OPPOSITE: that the catalog spelled this
    diameter ``25.00mm`` while a shopper typed ``25mm``, on the reasoning that
    the mismatch was the defect the rewrite policy demonstrated bridging. The
    ruling on elastic/prism#9284 removed that premise. The spelling variation
    was never the reference distributor's -- their facet values carry one spelling per
    value -- so it was a defect we invented and then built a bridge over.

    What replaces it is stronger than the old assertion, because it counts
    rather than looks up: **one** spelling, not "``25mm`` is among them". A
    catalog that published both would satisfy an ``in`` check and still split
    this size across two facet buckets.
    """
    spellings = {
        value
        for doc in flat_docs
        if "milling_dia" in doc.get("facets_num", {})
        and abs(doc["facets_num"]["milling_dia"] * MM_PER_INCH - 25.0) < MM_TOLERANCE
        for value in doc["facets"].get("milling_dia", [])
    }
    assert spellings == {"25mm"}, (
        f"a 25 mm cutting diameter is published as {sorted(spellings)}. Exactly "
        f"one spelling is the property: every extra spelling is an extra facet "
        f"bucket for one size."
    )


def _sizes_by_standard(docs: list[dict]) -> dict[str, set[str]]:
    """Which thread sizes each standard's lines actually published.

    The published designation is ``M6x1`` or ``7/16-14``; the standard's own
    size is ``M6`` or ``7/16``, so the designation is cut back to it rather
    than compared against a second table of designations.
    """
    seen: dict[str, set[str]] = {}
    for doc in docs:
        standard = doc["dimension_provenance"]
        for value in doc["facets"].get("dia_thread_size", []):
            size = value.split("x")[0] if value.startswith("M") else value.rsplit("-", 1)[0]
            # A fine-pitch line is the near-miss sibling of a standard's size,
            # not one of the sizes the (coarse-thread) standard offers; its
            # provenance names the fine-pitch standard or says it claims none.
            if value in compat.fine_threads(size, value.startswith("M")):
                continue
            seen.setdefault(standard, set()).add(size)
    return seen


def test_every_size_every_fastener_standard_offers_reaches_a_document(
    flat_docs: list[dict],
) -> None:
    """Derived from the extraction, so a size added upstream is swept at once.

    ``available_sizes`` already excludes what the source does not carry -- the
    ``M20`` button head is recorded ``present_in_source: false`` and is not
    expected here -- so this asserts exactly the set the catalog claims.
    """
    published = _sizes_by_standard(flat_docs)
    assert published, "no document carries a thread size"
    problems: list[str] = []
    for standard, sizes in sorted(published.items()):
        offered = set(standards.available_sizes(standard))
        if not offered:
            continue
        missing = sorted(offered - sizes)
        if missing:
            problems.append(f"{standard}: {missing}")
    assert problems == [], (
        "a standard offers sizes no line was ever built to: "
        + "; ".join(problems)
        + f". Regenerate with `{REBUILD}`."
    )


def test_the_thread_size_the_reference_parametric_query_names_exists(
    flat_docs: list[dict],
) -> None:
    rows = [
        doc
        for doc in flat_docs
        if REFERENCE_THREAD in doc["facets"].get("dia_thread_size", [])
    ]
    assert rows, f"no document publishes {REFERENCE_THREAD}"
    hex_rows = [doc for doc in rows if doc["product_type"] == HEX_BOLT_TYPE]
    assert hex_rows, (
        f"{len(rows)} document(s) publish {REFERENCE_THREAD} and none of them is a "
        f"hex head bolt, which is the product the reference distributor's query names"
    )


def test_the_lengths_published_for_that_size_are_the_standards_own(
    flat_docs: list[dict],
) -> None:
    """Not an arithmetic series invented to fill the gap.

    Every ``Length`` a 7/16 hex bolt publishes has to be one of the lengths
    ``ASME B18.2.1`` offers at that size -- the nominal list filtered to the
    per-size range, exactly as the upstream workbench computes it.
    """
    from synthetic_industrial_products.dimensions import DimensionParseError, parse_length

    offered = standards.offered_lengths_in("ASME B18.2.1", "7/16")
    assert offered, "the extraction carries no offered lengths for a 7/16 hex bolt"
    stray: list[tuple[str, str]] = []
    checked = 0
    for doc in flat_docs:
        if doc["product_type"] != HEX_BOLT_TYPE:
            continue
        if REFERENCE_THREAD not in doc["facets"].get("dia_thread_size", []):
            continue
        for value in doc["facets"].get("length", []):
            try:
                inches = parse_length(value).inches
            except DimensionParseError:
                continue  # a deliberately malformed value; another SKU will do
            checked += 1
            if not any(abs(inches - length) < 0.002 for length in offered):
                stray.append((doc["sku"], value))
    assert checked > 0, "no 7/16 hex bolt publishes a parseable length"
    assert stray == [], (
        f"{len(stray)} 7/16 hex bolt length(s) are not lengths the standard "
        f"offers: {stray[:5]}"
    )


def test_the_reference_parametric_query_has_an_answer(flat_docs: list[dict]) -> None:
    """All four attribute-value pairs on ONE record, not four counts.

        hex head cap screw: 7/16-14, 1-3/4" length under head,
        grade 8 steel, zinc finish

    A parametric query ANDs its terms, so a catalog carrying 116 Grade 8
    records and 547 Zinc Plated ones answers nothing unless some record
    carries both -- beside the thread size, beside a length under head, on a
    hex head. The length is asserted as "publishes one at all" rather than as
    1-3/4" exactly, because which lengths a line stocks is a property of the
    line; that the four attributes CO-OCCUR is the property this checks.
    """
    answers = [
        doc
        for doc in flat_docs
        if doc["product_type"] == HEX_BOLT_TYPE
        and REFERENCE_THREAD in doc["facets"].get("dia_thread_size", [])
        and "Grade 8" in doc["facets"].get("grade", [])
        and "Zinc Plated" in doc["facets"].get("finish", [])
        and doc["facets"].get("length_under_head")
        and "Hex" in doc["facets"].get("head_type", [])
    ]
    assert answers, (
        "no record carries 7/16-14, Grade 8, Zinc Plated and a length under head "
        "together on a hex head, so the reference distributor's parametric example resolves to "
        "an empty set however good the rewriting is"
    )


@pytest.mark.parametrize("facet", ["grade", "finish"])
def test_one_thread_size_is_not_locked_to_one_grading_or_one_finish(
    flat_docs: list[dict], facet: str
) -> None:
    """The aliasing the hex bolt rotation's phase offsets exist to prevent.

    A hex bolt line's size, grading and finish all turn on one line counter.
    When those wheels stay in step their periods -- six or nine sizes, two
    gradings, three finishes -- divide each other, and every line at one size
    comes out with the SAME grading and the SAME finish::

        M6x1     ['Class 10.9']  ['Zinc Plated']
        M8x1.25  ['Class 8.8']   ['Plain']

    one value each, on every line of that size. The catalog-wide counts stay
    healthy -- all four gradings and all three finishes keep their documents --
    so nothing a global sweep asks would notice. What a shopper meets is two
    facets that cannot narrow anything: filter to one thread size and the
    Grade control offers a single value.

    **Grouped by PUBLISHED SIZE, not by (standard, size).** The first version
    of this grouped by both and measured nothing worth measuring: each of the
    three metric standards offers nine sizes and gets nine lines, so every
    (standard, size) group held exactly one line and was skipped, and the
    check ran on the six inch sizes -- the half that was not broken -- while
    9 of 9 metric sizes were locked on both facets. A shopper filters by
    thread size; ``dimension_provenance`` is faceted too, but narrowing by
    size alone is the natural action and the one this is about.
    """
    lines: dict[str, dict[str, set[str]]] = {}
    for doc in flat_docs:
        if doc["product_type"] != HEX_BOLT_TYPE:
            continue
        sizes = doc["facets"].get("dia_thread_size", [])
        if not sizes:
            continue
        lines.setdefault(sizes[0], {}).setdefault(doc["product_id"], set()).update(
            doc["facets"].get(facet, [])
        )

    checked = 0
    locked: list[tuple[str, list[str]]] = []
    for size, by_line in sorted(lines.items()):
        publishing = [values for values in by_line.values() if values]
        if len(publishing) < 2:
            continue
        checked += 1
        values = sorted({value for published in publishing for value in published})
        if len(values) < 2:
            locked.append((size, values))
    assert checked >= 15, (
        f"only {checked} thread size(s) are carried by two hex bolt lines that "
        f"both publish {facet}; the catalog offers fifteen and this proves "
        f"little about the ones it skipped"
    )
    assert locked == [], (
        f"{len(locked)} of {checked} thread size(s) publish exactly one {facet} "
        f"across every line that carries them: {locked[:5]}"
    )


def test_a_bolt_never_carries_a_grading_from_the_other_measurement_system(
    flat_docs: list[dict],
) -> None:
    """``Class 10.9`` is a metric property class and ``Grade 8`` an SAE one.

    A ``7/16-14`` bolt graded ``Class 10.9`` is a designation that does not
    exist, and the catalog published them: the grade was drawn from one pool
    of four regardless of which standard the line was built to. The reference distributor's
    own query lands on exactly this pair of fields, which is how it surfaced.
    """
    from synthetic_industrial_products.catalog.generate import INCH_GRADES, METRIC_GRADES

    wrong: list[tuple[str, str, str]] = []
    for doc in flat_docs:
        if doc["product_type"] != HEX_BOLT_TYPE:
            continue
        grades = doc["facets"].get("grade", [])
        if not grades:
            continue
        metric = doc["dimension_provenance"] != "ASME B18.2.1"
        allowed = METRIC_GRADES if metric else INCH_GRADES
        for grade in grades:
            if grade not in allowed:
                wrong.append((doc["sku"], doc["dimension_provenance"], grade))
    assert wrong == [], (
        f"{len(wrong)} hex bolt(s) carry a grading from the other measurement "
        f"system: {wrong[:5]}"
    )
