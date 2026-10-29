"""Blinds (gen#204): four styles from four brands, drawn by :func:`kit_softfurn.blind` with the type
they state (roller, roman, venetian or vertical). A style is its colors times its width x drop
sizes. Hand-authored text-match decoys sit in the same node.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.softfurn_rows import (
    BLINDS_PATH,
    BM,
    CL,
    CREAM,
    GREEN,
    GREY,
    HT,
    LB,
    MAIN,
    RED,
    WHITE,
    SoftRow,
    attr,
    decoy,
    params,
    row,
    yes,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec


def _blind(code: str, title: str, brand: str, price: float, description: str, kind: str,
           material: str, fits: str, colors: tuple, blackout: bool = False,
           cordless: bool = False) -> SoftRow:  # fmt: skip
    attrs = [attr("blind_type", "Blind type", kind), attr("material", "Material", material),
             attr("fits", "Fits", fits)]  # fmt: skip
    if blackout:
        attrs.append(yes("blackout", "Blackout"))
    if cordless:
        attrs.append(yes("cordless", "Cordless"))
    sizes = (("60x160", price), ("90x160", price + 6.0), ("120x160", price + 12.0))
    return row(code, title, brand, BLINDS_PATH, "Blind", price, "blind", description, colors,
                tuple(attrs), sizes, params(kind=kind.lower()))  # fmt: skip


ROWS = (
    _blind(
        "HSFBROL",
        "Blackout Roller Blind",
        HT,
        12.0,
        "A blackout roller blind with a bottom bar and a side chain. It cuts to fit the window.",
        "Roller",
        "Fabric",
        "Inside Recess",
        (*MAIN, GREY),
        blackout=True,
    ),
    _blind(
        "HSFBROM",
        "Cordless Roman Blind",
        BM,
        28.0,
        "A lined Roman blind that folds up in soft pleats. Pull it up by hand, with no cord to hang.",
        "Roman",
        "Fabric",
        "Inside Recess",
        (*MAIN, CREAM),
        cordless=True,
    ),
    _blind(
        "HSFBVEN",
        "Faux Wood Venetian Blind",
        CL,
        24.0,
        "A moisture-proof venetian blind with wide slats that tilt, for a kitchen or a bathroom.",
        "Venetian",
        "Faux Wood",
        "Outside Recess",
        (*MAIN, GREY),
    ),
    _blind(
        "HSFBVER",
        "Vertical Blind with Louvres",
        LB,
        30.0,
        "A vertical blind with louvres that turn and draw back, for a patio door or a wide window.",
        "Vertical",
        "Fabric",
        "Outside Recess",
        (*MAIN, CREAM),
    ),
)


SPEC = TypeSpec(
    key="blind",
    department="Home",
    product_type="Blind",
    rows=ROWS,
    options=(Option("drop_cm", "drop_length", "Drop length", "CMT"),),
    decoys=(
        decoy(1, "green blind", ROWS[0], 4, "Green Cord Roller Blind",
              "A white roller blind with a green pull cord; the blind itself is white.", color=WHITE),
        decoy(4, "cordless blind", ROWS[1], 5, "Cordless Look Roman Blind",
              "A Roman blind that looks neat and uncluttered, but it is pulled up on a cord at the side.",
              attrs=(attr("blind_type", "Blind type", "Roman"), attr("material", "Material", "Fabric"),
                     attr("fits", "Fits", "Inside Recess")),
              color=RED),
        decoy(6, "wood", ROWS[2], 6, "Woodland Print Venetian Blind",
              "Named for the tree print on the slats; the slats are faux wood effect plastic.",
              color=GREEN),
    ),
)  # fmt: skip
