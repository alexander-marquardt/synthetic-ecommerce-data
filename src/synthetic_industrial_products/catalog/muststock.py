"""The MUST-STOCK list: products the catalog guarantees, whatever the random streams draw.

Maintainer ruling on elastic/prism-industrial-products#103 (2026-09-28): the
inventory must stock a product for every requirement example the search
scorecard runs, so an example query is judged against a product that exists
rather than against an empty Best tier. One entry per requirement example
(R1-R8), each naming the product type(s) it may be and the published values a
SKU must carry, exactly as the catalog spells them.

HOW IT COEXISTS WITH THE RANDOM CATALOG AND THE 1-5 VARIANT RULE. The main
generation runs first and is untouched, so no id, dimension or price anywhere
else moves. Then, for each entry no generated SKU already satisfies, a line is
built by that type's OWN builder -- so its naming, title and every derived
dimension follow the same rules as every other line -- from a stream seeded
by the entry alone, trying successive lines until one carries a matching SKU.
That line is added whole: it has the 1-5 variants its builder drew like any
other line, one of which is the required SKU. An entry the random catalog
already satisfies adds nothing. ``tests/test_catalog_must_stock.py`` asserts
every entry is stocked on the committed catalog, and that the pass is what
stocks them.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

END_MILLS = ("end_mill_square", "end_mill_ball")
CAP_SCREWS = (
    "screw_socket_head",
    "screw_button_head",
    "screw_flat_head",
    "screw_low_head",
    "bolt_hex",
)


@dataclass(frozen=True)
class MustStock:
    """A requirement example, and the SKU that has to exist for it."""

    example: str  # the example query, for the reader and the test ids
    types: tuple[str, ...]
    values: Mapping[str, str]  # attribute -> the published value, verbatim
    #: Builder choices the entry fixes, where the builder's own series cannot
    #: reach the example: an end mill's length-of-cut multiple (the series
    #: offers 1.5x, 3x and 4x, and ``1/2" x 1"`` is 2x). Read only by the
    #: must-stock pass; the main generation never sees one.
    pins: Mapping[str, float] = field(default_factory=dict)

    def matches(self, type_key: str, record: Mapping[str, str]) -> bool:
        return type_key in self.types and all(
            record.get(name) == value for name, value in self.values.items()
        )


def _em(example: str, types=END_MILLS, multiple: float | None = None, **values: str) -> MustStock:
    names = {"dia": "Milling Dia.", "loc": "Length of Cut", "material": "Material"}
    pins = {} if multiple is None else {"length_multiple": multiple}
    return MustStock(example, types, {names[k]: v for k, v in values.items()}, pins)


def _screw(example: str, types, thread: str, length: str | None = None, **extra: str) -> MustStock:
    values = {"Dia./Thread Size": thread}
    if length is not None:
        values["Length under Head"] = length
    values.update(extra)
    return MustStock(example, types, values)


MUST_STOCK: tuple[MustStock, ...] = (
    # R1: inch end-mill sizes, with the style a query names.
    _em("1/2 end mill", dia='1/2"'),
    _em("3/8 square end mills", ("end_mill_square",), dia='3/8"'),
    _em("1/8 ball end mills", ("end_mill_ball",), dia='1/8"'),
    _em("3/16 square end mills", ("end_mill_square",), dia='3/16"'),
    _em("1 inch square end mills", ("end_mill_square",), dia='1"'),
    _em("1/16 ball end mills", ("end_mill_ball",), dia='1/16"'),
    # R2: metric end-mill sizes.
    _em("4mm end mill", dia="4mm"),
    _em("15 mm ball end mills", ("end_mill_ball",), dia="15mm"),
    _em("11 mm end mills", dia="11mm"),
    _em("2.5mm end mill", dia="2.50mm"),
    _em("25mm end mill", dia="25mm"),
    _em("4mm carbide end mill", dia="4mm", material="Solid Carbide"),
    # R1 / R2: a diameter with a length of cut.
    _em('1/2" x 1" end mill', multiple=2.0, dia='1/2"', loc='1"'),
    _em(
        "1/2 x 2 1/4 square end mill", ("end_mill_square",), multiple=4.5, dia='1/2"', loc='2-1/4"'
    ),
    _em("10mm x 22mm end mill", multiple=2.2, dia="10mm", loc="22mm"),
    _em("12 x 36mm end mill", dia="12mm", loc="36mm"),
    _em(
        "6 x 13mm carbide end mill",
        multiple=13 / 6,
        dia="6mm",
        loc="13mm",
        material="Solid Carbide",
    ),
    _em('1 x 3" end mill', dia='1"', loc='3"'),
    # R4: a thread designation or size with a length under head.
    _screw("5/16-18 x 3/4 button head cap screw", ("screw_button_head",), "5/16-18", '3/4"'),
    _screw("5/16-18x3/4 low socket head cap screw", ("screw_low_head",), "5/16-18", '3/4"'),
    _screw("1/4 x 3 1/4 cap screws", CAP_SCREWS, "1/4-20", '3-1/4"'),
    # R5 / R6: a designation alone.
    _screw("1/4-20 screws", CAP_SCREWS, "1/4-20"),
    _screw("m12x1.75 socket cap screws", ("screw_socket_head",), "M12x1.75"),
    # R8: the parametric example, every clause.
    _screw(
        'hex head cap screw: 7/16-14, 1-3/4" length under head, grade 8 steel, zinc finish',
        ("bolt_hex",),
        "7/16-14",
        '1-3/4"',
        Grade="Grade 8",
        Finish="Zinc Plated",
    ),
)

#: How many lines the pass may build for one entry before it refuses. A cap,
#: not a tuning knob: every entry is met within a few dozen lines, and a
#: builder that can never produce an entry's values must fail loudly.
MAX_ATTEMPTS = 3000


class MustStockUnmetError(RuntimeError):
    """A must-stock entry that no line of its type could be built to carry."""
