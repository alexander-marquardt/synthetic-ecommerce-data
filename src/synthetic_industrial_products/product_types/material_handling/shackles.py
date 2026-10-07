"""Screw pin shackles: a table-driven type (#101, :mod:`...catalog.tabletype`).

**Source.** US Federal Specification RR-C-271F, "Chains and attachments,
carbon and alloy steel" (5 July 2011), read on 2026-10-07 as the copy at
https://everyspec.com/FED_SPECS/R/RR-C-271F_35870/. The specification itself
was read, and every figure below is one of its tables':

* table X, "Type IVA, class 2, screw pin anchor shackles", and table XIII,
  "Type IVB, class 2, screw pin chain shackles", for the dimensions;
* table VIII, "Mechanical properties", for the working load limit of a
  grade A (carbon steel) shackle.

Eleven of the 22 trade sizes those tables list are stated, 1/4 in to
1-1/4 in, in both bodies: 22 rows.

The trade size is published as ``Size``, the width between the eyes (W) as
``Inside Width``, the length inside (L) as ``Inside Length`` and the working
load limit as ``Load Capacity``, the census names for those measurements. The
body is published as ``Type`` (``Anchor`` for the bow body, ``Chain`` for the
straight-sided D). The pin diameter (P), the body diameter (D), the width of
the bow (B) and the outside diameter of the eye (R) are in the tables and
only drawn: the census has no name for any of them.

Two bodies and a load are more than :class:`TableType` states (its columns
are lengths and its rows one rising run of sizes), so this module holds one
table per body and adds ``Type`` and ``Load Capacity`` to what they build.

Only grade A, zinc coated, screw pin shackles are built. Bolt type and round
pin shackles (the tables' other classes), grade B alloy shackles and
stainless shackles, which carry other loads, are not.

The price is a declared ladder, not measured (see ``tabletype``): about
11 USD for one 1/4 in shackle, the same for both bodies.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from ...catalog.model import keyword_attribute, numeric_attribute
from ...catalog.newtypes import table_provenance
from ...catalog.tabletype import TableType, Variant, spec
from ...catalog.vocab import AttrSpec
from ...drawing.figures import Drawn
from ...drawing.model import Figure, arc

STANDARD = "RR-C-271"
#: The published name of the body, and of the working load limit.
BODY = "Type"
LOAD = "Load Capacity"
ANCHOR, CHAIN = "Anchor", "Chain"

#: Tables X and XIII share these columns, in inches: trade size, then
#: ``(D min, P min, W, R max)`` -- body diameter, pin diameter, width between
#: the eyes, outside diameter of the eye.
COMMON = {
    0.25: (0.24, 0.30, 0.469, 0.875),
    0.3125: (0.30, 0.37, 0.531, 1.0),
    0.375: (0.36, 0.43, 0.656, 1.125),
    0.4375: (0.42, 0.49, 0.750, 1.25),
    0.5: (0.48, 0.61, 0.812, 1.375),
    0.625: (0.59, 0.73, 1.062, 1.875),
    0.75: (0.71, 0.85, 1.250, 2.125),
    0.875: (0.83, 0.98, 1.438, 2.375),
    1.0: (0.95, 1.10, 1.688, 2.625),
    1.125: (1.07, 1.22, 1.812, 2.875),
    1.25: (1.19, 1.34, 2.031, 3.25),
}
#: Table XIII prints 1.25 for the 3/8 in chain shackle's eye; table X, 1.125.
CHAIN_EYE = {0.375: 1.25}
#: Table X: the anchor shackle's length inside (L) and width of bow (B).
ANCHOR_BOW = {
    0.25: (1.125, 0.75),
    0.3125: (1.250, 0.812),
    0.375: (1.438, 0.938),
    0.4375: (1.688, 1.062),
    0.5: (1.875, 1.188),
    0.625: (2.375, 1.5),
    0.75: (2.812, 1.75),
    0.875: (3.312, 2.0),
    1.0: (3.75, 2.312),
    1.125: (4.25, 2.625),
    1.25: (4.688, 2.875),
}
#: Table XIII: the chain shackle's length inside (L).
CHAIN_LENGTH = {
    0.25: 0.875,
    0.3125: 1.031,
    0.375: 1.125,
    0.4375: 1.438,
    0.5: 1.625,
    0.625: 2.000,
    0.75: 2.375,
    0.875: 2.812,
    1.0: 3.188,
    1.125: 3.562,
    1.25: 3.938,
}
#: Table VIII: the working load limit of a grade A shackle, in pounds.
LOAD_LB = {
    0.25: 1000,
    0.3125: 1500,
    0.375: 2000,
    0.4375: 3000,
    0.5: 4000,
    0.625: 6500,
    0.75: 9500,
    0.875: 13000,
    1.0: 17000,
    1.125: 19000,
    1.25: 24000,
}

#: The drawn pin head, in pin diameters: the tables give the pin's diameter
#: and nothing of its head. A collar against the eye, then the flat tab.
COLLAR_LENGTH, COLLAR_HEIGHT = 0.3, 1.5
TAB_LENGTH, TAB_HEIGHT = 0.9, 1.1
TAB_HOLE = 0.25
#: How far the threaded end stands out of its eye, in pin diameters.
THREAD_END = 0.15


def _trade_size(size: float) -> tuple[float, float]:
    """The table's trade size nearest ``size``, and ``size`` over it: a SKU
    whose size was rewritten off the table is drawn as that row, scaled."""
    nearest = min(COMMON, key=lambda trade: abs(trade - size))
    return nearest, size / nearest


def _draw(values: Mapping[str, float], body: str) -> Figure:
    """The front view, pin down: the body's two legs and crown, an eye at the
    foot of each leg, and the screw pin through both eyes with its head on
    the left. ``Inside Width`` is the gap between the eyes and ``Inside
    Length`` runs from the pin to the inside of the crown."""
    size, width, length = values["Size"], values["Inside Width"], values["Inside Length"]
    trade, scale = _trade_size(size)
    stock, pin, _, eye = (side * scale for side in COMMON[trade])
    if body == CHAIN:
        eye = CHAIN_EYE.get(trade, COMMON[trade][3]) * scale
        # A D: the crown is a half circle on the straight legs.
        bow = width
    else:
        bow = ANCHOR_BOW[trade][1] * scale
    inner, outer = width / 2, width / 2 + stock
    centre = (0.0, pin / 2 + length - bow / 2)

    def crown(radius: float, leg: float) -> list[tuple[float, float]]:
        """From the right leg over the top to the left leg. The widest and
        the highest points are on the outline, so it measures exactly."""
        if radius <= leg:
            return arc(centre, radius, 0.0, 180.0, 18)
        start = -math.degrees(math.acos(leg / radius))
        return [
            *arc(centre, radius, start, 0.0, 4)[:-1],
            *arc(centre, radius, 0.0, 180.0, 18),
            *arc(centre, radius, 180.0, 180.0 - start, 4)[1:],
        ]

    fig = Figure(size_in=size)
    fig.poly(
        [
            (outer, 0.0),
            *crown(bow / 2 + stock, outer),
            (-outer, 0.0),
            (-inner, 0.0),
            *reversed(crown(bow / 2, inner)),
            (inner, 0.0),
        ]
    )
    for side in (-1.0, 1.0):
        x0, x1 = sorted((side * inner, side * outer))
        fig.rect(x0, -eye / 2, x1, eye / 2)
    fig.rect(-outer, -pin / 2, outer + THREAD_END * pin, pin / 2)
    collar = outer + COLLAR_LENGTH * pin
    fig.rect(-collar, -COLLAR_HEIGHT * pin / 2, -outer, COLLAR_HEIGHT * pin / 2)
    tab = collar + TAB_LENGTH * pin
    fig.rect(-tab, -TAB_HEIGHT * pin / 2, -collar, TAB_HEIGHT * pin / 2)
    fig.disc((-(collar + tab) / 2, 0.0), TAB_HOLE * pin, "hole")
    return fig


def draw_anchor(values: Mapping[str, float]) -> Figure:
    return _draw(values, ANCHOR)


def draw_chain(values: Mapping[str, float]) -> Figure:
    return _draw(values, CHAIN)


ANCHOR_TABLE = TableType(
    "shackles",
    category=("Material Handling & Storage", "Rigging Hardware", "Rigging Shackles"),
    item="Screw Pin Anchor Shackle",
    standards_family="fastener",
    standard=STANDARD,
    columns=("Size", "Inside Width", "Inside Length"),
    rows=tuple((size, COMMON[size][2], ANCHOR_BOW[size][0]) for size in COMMON),
    variants=(Variant("Forged Steel", "Hot Dip Galvanized", 1.0),),
    # Sold each.
    packs=(1,),
    base_price=11.00,
    size_slope=1.8,
    pack_slope=0.8,
    draw=draw_anchor,
    extent=(6.55, 8.3),
    share=0.034,
    default_lines=74,
    default_skus=132,
    series="SK",
    use_lines=(
        "Joins a sling, hook or wire rope eye to a lifting point; the pin unscrews by hand.",
        "A removable link in a rigging, towing or tie-down assembly.",
    ),
    unit="in",
)
CHAIN_TABLE = replace(
    ANCHOR_TABLE,
    item="Screw Pin Chain Shackle",
    rows=tuple((size, COMMON[size][2], CHAIN_LENGTH[size]) for size in COMMON),
    draw=draw_chain,
)
#: Every dimension and the load are the one specification's.
PROVENANCE = table_provenance(*((name, STANDARD) for name in (*ANCHOR_TABLE.columns, LOAD)))

_BODIES = ((ANCHOR, spec(ANCHOR_TABLE)), (CHAIN, spec(CHAIN_TABLE)))


def make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    """One body's line as its table builds it, with the body and each size's
    working load limit added. The bodies alternate, so both are built."""
    body, built = _BODIES[gen._rotate(f"body:{type_key}", len(_BODIES))]
    draft = built.make(gen, type_key, category)
    draft.provenance = PROVENANCE
    draft.line_attrs.insert(1, keyword_attribute(BODY, body))
    for child in draft.children:
        trade, _ = _trade_size(child.primary.value_num)
        pounds = LOAD_LB[trade]
        child.attrs.append(numeric_attribute(LOAD, f"{pounds:,} lb", float(pounds)))
    return draft


def figure(record: dict[str, str]) -> Drawn:
    chain = record.get(BODY) == CHAIN or "Chain" in record.get("Item", "")
    return _BODIES[1 if chain else 0][1].figure(record)


SPEC = replace(
    _BODIES[0][1],
    vocab=(
        *_BODIES[0][1].vocab,
        AttrSpec(name=BODY, scope="line", presence=1.0, kind="keyword"),
        AttrSpec(name=LOAD, scope="sku", presence=1.0, kind="count"),
    ),
    make=make,
    figure=figure,
)
