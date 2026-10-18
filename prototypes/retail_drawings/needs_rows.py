"""Product types the failure classes need (gen#329): data only.

The demo probe of 2026-10-15 found types a general retailer's failure classes need and the
catalogue lacked. This module holds the clothing slice, built on :mod:`mens_depth_rows`' floor and
decoy machinery:

=======================  ===============================================  =====  =====
type                     leaf                                              floor  decoys
=======================  ===============================================  =====  =====
elasticated trousers     Mens/Trousers/Elasticated Waist Trousers             14     21
=======================  ===============================================  =====  =====

Each product states ``waist_type`` Elastic, the one name the joggers and the shorts already use
for it, and is drawn with the gathered band (``waist="elasticated"``), so the picture, the title
and the attribute say the same.

**Text-match decoys (gen#294).** Three decoys of each of the seven classes. Classes 1 to 3 and 5
to 7 are elasticated-waist trousers whose title or description misleads on another word (a color
in a trim, a borrowed noun, an audience word, a fancy name, a range name, a brand). Class 4 is the
word "elasticated" on a product whose waist is NOT elastic: "Elasticated Cuff Cargo Trousers" has a
belted waist, so the "garment attribute treated as keyword" class has the near miss it needs.

The lingerie slice is :data:`BRAS`: four mastectomy, three post-surgery and three nursing bras
(the ``Mastectomy Bras`` leaf is new). They live here, not in :mod:`scale_rows`, because that
module's rows each open a title value their leaf lacked and a medical bra is non-wired by nature:
a derived "Wired Mastectomy Bra" would be false. Period pants are a type spec
(``type_specs/period_pants.py``) and the "Lamp Shade" titles are in :mod:`lighting_rows`.

Chinos and the lamps that carry "shade" in a title already exist; women's elasticated trousers
are not in the issue's done-when and stay out.

The rows are templates only: :func:`scale.derivable` leaves them out (``scale.NEEDS_IDS``).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import mens_depth_rows as m
from scale_rows import Bra
from variants import cw, style_docs

KINDS = {
    "Mens Elasticated Trousers": m.Kind(
        "Mens Trousers", "Elasticated Trousers", "trousers", m.CHEST, "size", "Clothing", 24.0,
        "Cotton", params=(("fit", "straight"), ("rise", "mid")),
        borrow=("shirt", "blazer", "jumper"),
        absent=("Elasticated Cuff", "Elasticated Hem", "Elasticated Ankle"),
        path=("Mens", "Trousers", "Cargo Trousers"),
        spread=(("Mens", "Trousers", "Elasticated Waist Trousers"),),
        decoy_attrs=(m._a("waist_type", "Waist type", "Elastic"),),
        decoy_params=(("waist", "elasticated"),),
        absent_noun="Cargo Trousers",
        absent_attrs=(m._a("waist_type", "Waist type", "Belted"),),
        absent_text="Cotton cargo trousers with a belt loop waist and an {f}.",
    ),
}  # fmt: skip

_TAIL = {"Mens Elasticated Trousers": "with an elasticated waist and two side pockets"}

_LEAVES = (
    m.Leaf("EW", ("Mens", "Trousers", "Elasticated Waist Trousers"), "Mens Elasticated Trousers",
           14, ("Cotton Jersey", "Fleece Back", "Linen Blend", "Stretch Twill", "Ripstop",
                "Brushed Cotton", "Lightweight Nylon"),
           ("Relaxed", "Tapered"), ("Pull-On", "Zip Pocket"),
           "{f} {fit} Fit {d} Elasticated Waist Trousers", waist="Elastic", extra_price=2.0),
)  # fmt: skip

_BLACK, _WHITE, _NUDE = cw("Black", "#2a2a2e"), cw("White", "#ffffff"), cw("Almond", "#d9b79a")

#: Medical and nursing bras, each a :class:`scale_rows.Bra` that names its own straps and fastening.
BRAS = (
    # A mastectomy bra holds a breast form in a pocket in each cup; a post-surgery bra is worn
    # first, for the weeks after an operation.
    Bra("MARSKE", "Marske", "Saltmarsh", "Mastectomy", (32, 46), ("A", "G"),
        (cw("Soft Grey", "#b9bbbe"), _NUDE, _BLACK), 26.0, wired=False, fabric="Cotton, Elastane",
        fitting="soft wide straps, a front hook and eye fastening and pocketed cups for a breast form"),
    Bra("KILDALE", "Kildale", "Bramblewood", "Mastectomy", (34, 48), ("B", "H"),
        (cw("Almond", "#d9b79a"), _WHITE, _BLACK), 29.0, wired=False, fabric="Cotton, Elastane",
        fitting="adjustable straps, a three-row hook and eye back and pocketed cups that hold a breast form"),
    Bra("ROSEDALE", "Rosedale", "Saltmarsh", "Mastectomy", (32, 44), ("A", "F"),
        (_NUDE, _BLACK, cw("Mink", "#8a7266")), 31.0, wired=False,
        fitting="a pull-on stretch band with no fastening and pocketed cups for a breast form"),
    Bra("UGTHORPE", "Ugthorpe", "Bramblewood", "Mastectomy", (34, 46), ("B", "G"),
        (_WHITE, _NUDE), 33.0, wired=False, fabric="Cotton, Elastane",
        fitting="padded straps, a wide hook and eye back and pocketed cups with a gentle lift"),
    Bra("AINTHORPE", "Ainthorpe", "Saltmarsh", "Post-Surgery", (32, 46), ("A", "G"),
        (_WHITE, _NUDE, _BLACK), 24.0, wired=False, fabric="Cotton, Elastane",
        fitting="soft seam-free cups, a front zip and room for a dressing, worn after a mastectomy"),
    Bra("STOKESLEY", "Stokesley", "Bramblewood", "Post-Surgery", (34, 48), ("B", "H"),
        (cw("Soft Grey", "#b9bbbe"), _NUDE), 27.0, wired=False, fabric="Cotton, Elastane",
        fitting="drain-pocket sides, wide straps and a front hook and eye fastening for after a mastectomy"),
    Bra("DANBY", "Danby", "Saltmarsh", "Post-Surgery", (32, 44), ("A", "F"),
        (_BLACK, _WHITE, cw("Latte", "#c8a98a")), 23.0, wired=False,
        fitting="a smooth wrap front, a soft band and no wires or seams for the first weeks after surgery"),
    Bra("LEALHOLM", "Lealholm", "Bramblewood", "Nursing", (32, 44), ("B", "H"),
        (_BLACK, _WHITE, cw("Mink", "#8a7266")), 25.0, wired=False, fabric="Cotton, Elastane",
        fitting="drop-down cups with one-hand clips and a soft stretch band"),
    Bra("EGTON", "Egton", "Saltmarsh", "Nursing", (30, 42), ("A", "F"),
        (_NUDE, _BLACK, _WHITE), 23.0, wired=False, fabric="Modal, Elastane",
        fitting="a crossover front that opens for feeding and a pull-on band with no hook"),
    Bra("LOFTUS", "Loftus", "Bramblewood", "Nursing", (32, 44), ("C", "G"),
        (_BLACK, cw("Navy", "#26365c"), _NUDE), 29.0,
        fitting="clip-down cups with a light underwire, adjustable straps and a three-row hook and eye back"),
)  # fmt: skip

_DECOY_ROWS, _TABLE = m._decoys(KINDS, _TAIL, "NX")
_FLOOR_ROWS = m._floor_rows(_LEAVES, KINDS, _TAIL, "NE")
ROWS = (*_FLOOR_ROWS, *_DECOY_ROWS)
#: Every decoy, with its class, word, query and policy: the docs table is generated from it.
TABLE = tuple(_TABLE)


def docs() -> list[dict]:
    """Every row's catalog document, floor rows then decoys, then the bras."""
    return [*(r.doc() for r in ROWS), *(d for s in BRAS for d in style_docs("Bras", s))]


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: ``main_colors.complete`` leaves them as authored."""
    return frozenset(f"BRD-{d.code}" for d in TABLE)


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset([*(f"BRD-{r.code}" for r in ROWS), *(f"BRA-{s.code}" for s in BRAS)])
