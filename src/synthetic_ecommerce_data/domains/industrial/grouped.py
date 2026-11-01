"""The GROUPED pass (#710, #766): product lines with a run of variants, most of a type.

``variants_per_product`` (1 to 5, about half single-SKU) fits marketplace-like types. A
distributor, though, sells one cap screw (thread, material, finish) in a run of standard
lengths, and one end-mill line (``<brand> <series> square end mills``) in a run of
diameters. Under the one knob such a type's search page had almost nothing to group:
``m6x1 set screws`` returned 141 products for 260 SKUs, most of them single-SKU. #710 added
a few such lines beside the flat products, and they sat among thousands of single-SKU tiles.

HOW IT COEXISTS WITH THE FLAT CATALOG (maintainer, 2026-10-28: "I'm ok to have a mixture
.. some that are grouped, and others that follow the existing flat format"). The SKUs MOVE.
For each type in :data:`VARIANTS` the main generation builds :data:`FLAT_SHARE` of the
type's products, the first of its stream, so each keeps its id, title and attributes. The
pass runs after that and the must-stock pass, on streams of its own, and adds:

* for each :data:`TARGETS` entry the type owns, products until :func:`wanted` of the pass's
  products carry the entry's values. These are the reference queries whose rows were thin
  (#710, 2026-10-28 comment).
* then products until the type holds its :func:`sku_budget`, each built by the type's OWN
  builder (so naming, titles and derived dimensions follow the same rules as every other
  line), with its SKU count drawn from the type's table instead of the global knob. A
  fastener builder takes a contiguous run of its thread's standard lengths, and an end-mill
  or drill builder of its system's diameters (``Generator._offered_run``). The series pool
  still caps a draw, because a size offers only so many lengths.

A type joins :data:`VARIANTS` only if its spec space holds a run. "Every SKU is different"
rejects a SKU its brand already made, so a type with few specs loses the middle of its runs:
measured at ``--lines 39000``, a hex key run line kept too few SKUs (2,210 of 4,314 products
single-SKU), and taps lost 42% of their run SKUs. Hex nuts and hex keys stay on the knob, as
do bearings, whose line is one bearing number in three closures.

``tests/test_catalog_grouped.py`` holds the pass to the tables, to the targets, to the SKU
total and to the flat products that stay.
"""

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.industrial.muststock import CAP_SCREWS, MustStock

#: A run of variants: 6 to 15, skewed to the middle, as a distributor's length or diameter
#: series runs for one line.
RUN: tuple[tuple[int, float], ...] = (
    (6, 0.10),
    (7, 0.11),
    (8, 0.13),
    (9, 0.13),
    (10, 0.12),
    (11, 0.10),
    (12, 0.09),
    (13, 0.08),
    (14, 0.07),
    (15, 0.07),
)

#: Each grouped type's own ``(count, weight)`` table. A type not listed here has no grouped
#: products and draws only ``variants_per_product``.
VARIANTS: dict[str, tuple[tuple[int, float], ...]] = {
    "set_screws_hex_socket": RUN,
    "screw_socket_head": RUN,
    "screw_button_head": RUN,
    "screw_low_head": RUN,
    "screw_flat_head": RUN,
    "bolt_hex": RUN,
    "end_mill_square": RUN,
    "end_mill_ball": RUN,
    "drill_jobber": RUN,
}

#: The flat products a grouped type keeps, as a share of the products it would otherwise
#: have. They are the first of the type's stream, so each keeps its id and every attribute,
#: and they leave the type a mixture with some single-SKU products.
FLAT_SHARE = 0.10

#: The fewest flat products a grouped type keeps. Each product is one size of one standard,
#: and a rotation has to reach every size a standard offers: a run line holds ten SKUs but
#: one size, so a small build of run lines alone leaves sizes on no line at all. Set screws
#: need the most: eight standards of about twelve sizes each. At ``--lines 39000`` every
#: type's share is past its floor.
FLAT_FLOOR = 50
FLAT_FLOORS = {"set_screws_hex_socket": 150}


#: A grouped type's SKUs against the type built flat. #710's families grew these types by
#: about 14%, and the catalog keeps most of that: the end mills stay within 3% of their SKUs.
SKU_SCALE = 1.10


def flat_products(key: str, count: int) -> int:
    """How many of grouped type ``key``'s ``count`` products stay flat."""
    return min(count, max(FLAT_FLOORS.get(key, FLAT_FLOOR), round(count * FLAT_SHARE)))


def sku_budget(flat_skus: int, flat_lines: int, count: int) -> int:
    """The SKUs a type of ``count`` products holds, measured on its flat products, whose
    SKUs per product are the type's whole flat build's: moving SKUs into runs adds none."""
    return round(flat_skus / flat_lines * count * SKU_SCALE) if flat_lines else 0


#: The grouped products each target needs: at least :data:`TARGET_PRODUCTS`, and
#: :data:`TARGET_SHARE` of the type's flat products that already carry it.
TARGET_PRODUCTS = 5
TARGET_SHARE = 0.10


def wanted(carrying: int) -> int:
    """The grouped products a target needs, given ``carrying`` products that already carry it."""
    return max(TARGET_PRODUCTS, math.ceil(carrying * TARGET_SHARE))


#: How many lines the pass may build for one target before it refuses. As
#: :data:`.muststock.MAX_ATTEMPTS`: a cap, not a tuning knob.
MAX_ATTEMPTS = 20000

_END_MILLS = ("end_mill_square", "end_mill_ball")


def _target(example: str, types: tuple[str, ...], **values: str) -> MustStock:
    names = {"thread": "Dia./Thread Size", "length": "Length", "dia": "Milling Dia."}
    return MustStock(example, types, {names.get(k, k): v for k, v in values.items()})


#: The reference queries the grouped products must answer. An entry belongs to its FIRST type,
#: as a must-stock entry does: the products it adds are of that type.
TARGETS: tuple[MustStock, ...] = (
    _target("m6x1 set screws", ("set_screws_hex_socket",), thread="M6x1"),
    _target("m12x1.75 socket cap screws", ("screw_socket_head",), thread="M12x1.75"),
    _target("1/4-20 screws", CAP_SCREWS, thread="1/4-20"),
    _target(
        "5/16-18 x 3/4 button head cap screw",
        ("screw_button_head",),
        thread="5/16-18",
        length='3/4"',
    ),
    _target(
        "5/16-18x3/4 low socket head cap screw",
        ("screw_low_head",),
        thread="5/16-18",
        length='3/4"',
    ),
    _target("1/4 x 3 1/4 cap screws", CAP_SCREWS, thread="1/4-20", length='3-1/4"'),
    _target(
        'hex head cap screw: 7/16-14, 1-3/4" length under head, grade 8 steel, zinc finish',
        ("bolt_hex",),
        thread="7/16-14",
        length='1-3/4"',
        Grade="Grade 8",
        Finish="Zinc Plated",
    ),
    _target("1/8 ball end mills", ("end_mill_ball",), dia='1/8"'),
    _target("1/16 ball end mills", ("end_mill_ball",), dia='1/16"'),
    _target("15 mm ball end mills", ("end_mill_ball",), dia="15mm"),
    _target("4mm carbide end mill", _END_MILLS, dia="4mm", Material="Solid Carbide"),
)


class GroupedUnmetError(RuntimeError):
    """A grouped target that no line of its type could be built to carry."""
