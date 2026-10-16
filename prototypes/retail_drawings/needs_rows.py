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

Chinos, lamp shades and the post-surgery and nursing bras already exist; what the issue still
lists (plimsolls, mastectomy and period-wear lingerie, women's elasticated trousers) stays open
on gen#329.

The rows are templates only: :func:`scale.derivable` leaves them out (``scale.NEEDS_IDS``).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import mens_depth_rows as m

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

_DECOY_ROWS, _TABLE = m._decoys(KINDS, _TAIL, "NX")
_FLOOR_ROWS = m._floor_rows(_LEAVES, KINDS, _TAIL, "NE")
ROWS = (*_FLOOR_ROWS, *_DECOY_ROWS)
#: Every decoy, with its class, word, query and policy: the docs table is generated from it.
TABLE = tuple(_TABLE)


def docs() -> list[dict]:
    """Every row's catalog document, floor rows then decoys."""
    return [r.doc() for r in ROWS]


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: ``main_colors.complete`` leaves them as authored."""
    return frozenset(f"BRD-{d.code}" for d in TABLE)


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
