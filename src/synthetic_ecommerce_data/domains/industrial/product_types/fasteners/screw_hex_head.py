"""Hex head cap screws: ASME B18.2.1, SAE J429 Grade 2, 5 and 8 (#819).

Not the hex bolt. A hex cap screw is made to closer tolerances, has a washer
face under the head and a chamfered point, and is tightened by turning its
head, into a tapped hole as well as into a nut; industrial catalogs list the
two as separate lines. This one sits beside the socket cap screws, under
Cap Screws.

The head dimensions, the washer face, the thread length and the offered
lengths are one cited table of the standards library
(``asme_b18_2_1_hex_cap_screws_in``); the threads per inch are ASME B1.1's
(``asme_b1_1_unified_threads``). Its builder is its own, as the hex bolt's
branches on its standard and metric gradings this type does not have.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length, parse_thread
from synthetic_ecommerce_data.core.model import Attribute, keyword_attribute
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import ChildDraft, LineDraft
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, Record, fastener
from synthetic_ecommerce_data.domains.industrial.newtypes import feed_style, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import STANDARDS_NAME, AttrSpec

STANDARD = "ASME B18.2.1"

ITEM = "Hex Head Cap Screw"

#: The head rows, 1/4" to 1", as the library holds them.
HEADS: dict[str, dict] = {
    row["size"]: row for row in library.table("asme_b18_2_1_hex_cap_screws_in").rows
}

#: The coarse sizes a line is built in, smallest first.
SIZES: tuple[str, ...] = tuple(HEADS)

#: UNC and UNF threads per inch of those sizes (ASME B1.1).
THREADS: dict[str, dict] = {
    row["size"]: row for row in library.table("asme_b1_1_unified_threads").select(list(SIZES))
}

#: Where each published dimension was read from: the head table, and ASME
#: B1.1 for the thread.
PROVENANCE = table_provenance(
    ("Width Across Flats", STANDARD),
    ("Head Height", STANDARD),
    ("Thread Length", STANDARD),
    ("Threads per Inch", "ASME B1.1"),
)

#: The lengths a line stocks, in inches: the standard's offered lengths of a
#: size, inside the 1/2" to 6" a distributor's cap screw page carries.
LENGTH_SPAN = (0.5, 6.0)

#: The stocked grade and finish pairs, as the sequence a line rotates through.
#: SAE J429's three inch grades; a Grade 8 screw is sold plain or zinc yellow
#: (its hardness is why it is not hot-dip galvanized), Grade 2 plain or clear
#: zinc. Seven pairs against nine sizes: the two wheels never share a period,
#: so every pair reaches every size.
COMBOS: tuple[tuple[str, str], ...] = (
    ("Grade 5 Steel", "Zinc Plated"),
    ("Grade 8 Alloy Steel", "Zinc Yellow"),
    ("Grade 2 Steel", "Plain"),
    ("Grade 5 Steel", "Zinc Yellow"),
    ("Grade 8 Alloy Steel", "Plain"),
    ("Grade 2 Steel", "Zinc Plated"),
    ("Grade 5 Steel", "Plain"),
)

#: Every fourth line of a size is the Unified fine thread: ASME B18.2.1 covers
#: UNF hex cap screws in every size this type stocks.
FINE_PERIOD = 4

VOCAB = (
    AttrSpec("Head Type", "line"),
    AttrSpec("Drive Type", "line"),
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line"),
    AttrSpec("Thread Direction", "line", 0.64),
    AttrSpec("Thread Type", "line"),
    AttrSpec(STANDARDS_NAME, "line"),
    # Unconditional, as on the hex bolt whose price model this type borrows:
    # the shown price is a pack's.
    AttrSpec("Units per Pack", "line", kind="count"),
    AttrSpec("Dia./Thread Size", "sku"),
    AttrSpec("Threads per Inch", "sku"),
    AttrSpec("Length", "sku", kind="length"),
    AttrSpec("Thread Length", "sku", kind="length"),
    AttrSpec("Width Across Flats", "sku", kind="length"),
    AttrSpec("Head Height", "sku", kind="length"),
)

#: The widest head with its end view (a 1" screw's 1.73" across corners and
#: the end view beside it, 3.6"), and the hex bolt's height: a longer part is
#: drawn broken, so the 1/4-20 x 1/2" is not drawn needlessly small.
EXTENT = (3.7, 5.35)


def offered_lengths_in(size: str) -> list[float]:
    """The size's offered lengths inside :data:`LENGTH_SPAN`, smallest first."""
    lo, hi = LENGTH_SPAN
    lengths = (parse_length(str(v)).inches for v in HEADS[size]["offered_lengths_in"])
    return [inches for inches in lengths if lo <= inches <= hi]


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a size, a grade and finish, a thread series and a run of lengths."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    # The size and the grade-and-finish pair turn off ONE line counter, so
    # which combinations exist is not left to a draw (the hex bolt's lesson).
    step = gen._rotation_step(f"line:{type_key}")
    size = SIZES[step % len(SIZES)]
    material, finish = COMBOS[step % len(COMBOS)]
    fine = gen._rotate(f"fine:{size}", FINE_PERIOD) == FINE_PERIOD - 1
    tpi = THREADS[size]["unf_tpi" if fine else "unc_tpi"]
    designation = f"{size}-{tpi}"
    head = HEADS[size]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"HCS{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
        standard=STANDARD,
    )
    draft.line_attrs = [
        keyword_attribute("Head Type", "Hex"),
        keyword_attribute("Drive Type", "External Hex"),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Direction", "Right Hand"),
        keyword_attribute("Thread Type", "UNF" if fine else "UNC"),
        keyword_attribute(STANDARDS_NAME, STANDARD),
        gen._pack(
            type_key,
            f"{size}:{brand}:{draft.series}",
            THREADS[size]["major_dia_in"],
            (THREADS[s]["major_dia_in"] for s in SIZES),
        ),
    ]
    draft.descriptors = [("Material", material)]

    lengths = offered_lengths_in(size)
    count = min(gen._variant_count(), len(lengths))
    style = feed_style(brand, "in", BRANDS)
    for length_in in gen._offered_run(f"lengths:{size}", lengths, count):
        child = ChildDraft(system="in")
        # Fully threaded when shorter than the standard's thread length.
        thread_len_in = min(length_in, head["thread_length_in"])
        child.primary = keyword_attribute("Dia./Thread Size", designation)
        length_attr = gen._length("Length", length_in, style)
        thread_attr = gen._length("Thread Length", thread_len_in, style)
        child.attrs = [
            child.primary,
            Attribute("Threads per Inch", str(tpi), bare_unit="TPI"),
            length_attr,
            thread_attr,
            gen._length("Width Across Flats", head["width_across_flats_in"], style),
            gen._length("Head Height", head["head_height_in"], style),
        ]
        child.secondary = {"other_length": length_attr, "length_of_cut": thread_attr}
        draft.children.append(child)
    return draft


def washer_face(record: Record) -> tuple[float, float] | None:
    """The washer face of the record's size, ``(diameter, thickness)``, or None."""
    try:
        thread = parse_thread(str(record.get("Dia./Thread Size", "")))
    except DimensionParseError:
        return None
    row = next(
        (
            r
            for s, r in HEADS.items()
            if abs(THREADS[s]["major_dia_in"] - thread.major.inches) < 1e-6
        ),
        None,
    )
    if row is None:
        return None
    return row["washer_face_dia_in"], row["washer_face_thickness_in"]


def figure(record: Record) -> Drawn:
    """The hex cap screw: the fastener figure, its hex head on a washer face."""
    return fastener(record, max_height=EXTENT[1], washer_face=washer_face(record))


def claims(facts, *, metric, provenance, standard):
    """ASME B18.2.1's dimensions, and SAE J429 for the grade every line carries."""
    return [STANDARD, "SAE J429"]


SPEC = TypeSpec(
    "screw_hex_head",
    label=ITEM,
    category=("Fasteners", "Cap Screws", "Hex Head Cap Screws"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.015,
    borrows="bolt_hex",
    claims=claims,
    # The provenance names two tables, so the thread-size sweep reads the
    # standard every line is built to from here.
    line_standard=lambda record: STANDARD,
    may_claim=frozenset({STANDARD, "SAE J429"}),
    key_attributes=("Dia./Thread Size",),
    threaded="Dia./Thread Size",
    fastener=True,
    compat=False,
    use_lines=(
        "Tightened by its hex head with a wrench, into a tapped hole or with a nut.",
        "The washer face under the head bears evenly on the work.",
    ),
)
