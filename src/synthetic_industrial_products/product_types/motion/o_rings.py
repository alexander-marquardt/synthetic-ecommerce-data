"""O-rings: the SAE AS568 inch sizes, deepened from breadth (#53).

Every size is a row of the AS568 dash-number table, read from
``data/as568_sizes.json``, which says where the rows were transcribed from:
the actual inside diameter and cross-section (published as ``Width``), each
with its tolerance, and the nominal inside diameter (published as ``Size``).
Left out: the -001 1/2 row, the -9xx straight-thread boss series and the
ISO 3601-1 metric sizes, for which no readable table was found.

A line is one series (one cross-section: -0xx, -1xx, -2xx, -3xx, -4xx) in
one compound. The compounds are the four the chart's materials table gives a
standard durometer for: Buna-N 70, FKM 75, EPDM 70 and silicone 70, each by
its generic name. No pack quantity is published (#14): one ring per SKU.
"""

from __future__ import annotations

import json
from fractions import Fraction
from functools import cache
from importlib import resources
from typing import TYPE_CHECKING, Any, NamedTuple

from ...catalog.formats import LengthStyle, format_length_best
from ...catalog.model import keyword_attribute, length_attribute
from ...catalog.newtypes import _window, feed_style, table_provenance
from ...catalog.typespec import TypeSpec
from ...catalog.vocab import AttrSpec
from ...dimensions import DimensionParseError, parse_length
from ...drawing.figures import Drawn
from ...drawing.model import Figure

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...catalog.generate import LineDraft

KEY = "o_rings"
STANDARD = "SAE AS568"
ITEM = "O-Ring"


class Row(NamedTuple):
    """One AS568 dash number, in inches."""

    dash: str
    inside: float
    inside_tol: float
    width: float
    width_tol: float
    #: The nominal inside diameter, as the chart writes it (``1 1/16``).
    nominal: str


@cache
def rows() -> tuple[Row, ...]:
    """Every AS568 row the type offers, in dash order."""
    text = resources.files("synthetic_industrial_products.data").joinpath("as568_sizes.json")
    return tuple(Row(*row) for row in json.loads(text.read_text("utf-8"))["rows"])


def series() -> dict[str, tuple[Row, ...]]:
    """The rows by series, the dash number's first digit: one cross-section each
    (-0xx holds four small ones)."""
    out: dict[str, list[Row]] = {}
    for row in rows():
        out.setdefault(row.dash[0], []).append(row)
    return {name: tuple(members) for name, members in out.items()}


#: (Material, Hardness): the compounds a line is made in.
COMPOUNDS: tuple[tuple[str, str], ...] = (
    ("Buna-N", "70 Shore A"),
    ("FKM", "75 Shore A"),
    ("EPDM", "70 Shore A"),
    ("Silicone", "70 Shore A"),
)

PROVENANCE = table_provenance(
    ("Inside Dia.", STANDARD),
    ("Width", STANDARD),
    ("Inside Dia. Tolerance", STANDARD),
    ("Width Tolerance", STANDARD),
)

#: ``Width`` is the census's name for a ring's cross-section; ``Dash Number``
#: and ``Width Tolerance`` are excepted in ``names.NAME_EXCEPTIONS``.
VOCAB = (
    AttrSpec("Item", "line"),
    AttrSpec("Material", "line"),
    AttrSpec("Hardness", "line", 0.9),
    AttrSpec("Size", "sku", kind="length"),
    AttrSpec("Dash Number", "sku", 0.9),
    AttrSpec("Inside Dia.", "sku", kind="length"),
    AttrSpec("Width", "sku", kind="length"),
    AttrSpec("Inside Dia. Tolerance", "sku", 0.7),
    AttrSpec("Width Tolerance", "sku", 0.7),
)


def _decimal(inches: float, style: LengthStyle) -> str:
    """An actual dimension as the chart states it: three decimal places."""
    return format_length_best(inches, LengthStyle(style.system, style.suffix, "decimal", places=3))


def _tolerance(inches: float, style: LengthStyle) -> str:
    return f"+/-{_decimal(inches, style)}"


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a series, one compound, a window of the series' sizes."""
    # Imported here: generate imports the type tables, which discover this module.
    from ...catalog.brands import pick_brand
    from ...catalog.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    by_series = series()
    names = sorted(by_series)
    # Weighted by the series' row count, so every dash number is drafted alike.
    name = rng.choices(names, weights=[len(by_series[n]) for n in names], k=1)[0]
    material, hardness = rng.choice(COMPOUNDS)
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"OR{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
        standard=STANDARD,
    )
    draft.line_attrs = [
        keyword_attribute("Item", ITEM),
        keyword_attribute("Material", material),
        keyword_attribute("Hardness", hardness),
    ]
    draft.descriptors = [("Material", material)]
    style = feed_style(brand, "in", BRANDS)
    for row in _window(gen, f"o-ring:{name}", list(by_series[name]), gen._variant_count()):
        child = ChildDraft(system="in")
        child.primary = length_attribute(
            "Size", gen._publish(float(sum(Fraction(p) for p in row.nominal.split())), style)
        )
        child.attrs = [
            child.primary,
            keyword_attribute("Dash Number", f"AS568-{row.dash}"),
            length_attribute("Inside Dia.", _decimal(row.inside, style)),
            length_attribute("Width", _decimal(row.width, style)),
            keyword_attribute("Inside Dia. Tolerance", _tolerance(row.inside_tol, style)),
            keyword_attribute("Width Tolerance", _tolerance(row.width_tol, style)),
        ]
        draft.children.append(child)
    return draft


#: What a ring is drawn at when the record gives no readable size: an -010.
_NOMINAL = (0.239, 0.070)


def _inches(record: dict[str, str], name: str) -> float | None:
    try:
        value = parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None
    return value if value > 0 else None


def figure(record: dict[str, str]) -> Drawn:
    """The ring's face (a disc with its hole) and, below it, the section a cut
    across it shows: two circles of the cross-section's diameter."""
    inside, width = _inches(record, "Inside Dia."), _inches(record, "Width")
    source = "record" if inside and width else "nominal"
    if inside is None or width is None:
        inside, width = _NOMINAL
    outside = inside + 2 * width
    fig = Figure(size_in=outside)
    fig.disc((0.0, 0.0), outside / 2)
    fig.disc((0.0, 0.0), inside / 2, "hole")
    centre_y = outside / 2 + 0.3 * outside + width / 2
    for x in (-(inside + width) / 2, (inside + width) / 2):
        fig.disc((x, centre_y), width / 2)
    return Drawn(fig, source)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's table: every row is an AS568 dash number, and no compound
    standard is claimed."""
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Hose, Tube, Fittings & Valves", "Seals & Gaskets", "O-Ring Seals"),
    standards_family="motion",
    vocab=VOCAB,
    figure=figure,
    # -475, the largest drawn: 26.49" across, 34.71" tall with its section.
    extent=(26.6, 34.85),
    make=build,
    share=0.015,
    # No census prices: the census has no O-rings. The flat washer's model is
    # borrowed, keyed on the cross-section and held to the span that model
    # was fitted over (``price.MEASURED_SPANS``); generated, NOT MEASURED.
    borrows="washer_flat",
    claims=claims,
    may_claim=frozenset({STANDARD}),
    # The cross-section, not the inside diameter: the borrowed washer model
    # is held to the span it was fitted over, which holds the larger
    # cross-sections and almost none of the inside diameters.
    key_attributes=("Width",),
    title_attributes=("Size",),
    default_lines=38,
    default_skus=66,
    use_lines=(
        "Seats in a gland and seals by squeezing between two surfaces.",
        # No standard's number: a record whose Dash Number is left out has no
        # field to back the 568 (test_every_number_in_the_text_traces_to_a_field).
        "Sized by its dash number.",
    ),
)
