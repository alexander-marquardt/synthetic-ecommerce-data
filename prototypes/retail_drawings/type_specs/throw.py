"""Throws (gen#204): three styles from three brands, drawn by :func:`kit_softfurn.draped_throw` with
the edge they state (fringe, bound or pom-pom). A throw's size is a width x length. Hand-authored
text-match decoys sit in the same node.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from softfurn_rows import (
    BLUE,
    BM,
    CREAM,
    GREY,
    HT,
    LB,
    MAIN,
    THROWS_PATH,
    SoftRow,
    attr,
    decoy,
    params,
    row,
    yes,
)
from type_registry import TypeSpec


def _throw(code: str, title: str, brand: str, price: float, description: str, material: str, use: str,
           edge: str, colors: tuple, reversible: bool = False) -> SoftRow:  # fmt: skip
    attrs = [
        attr("material", "Material", material),
        attr("use", "Use", use),
        attr("edge", "Edge", edge),
    ]
    if reversible:
        attrs.append(yes("reversible", "Reversible"))
    sizes = (("130x170", price), ("150x200", price + 8.0), ("200x230", price + 18.0))
    prm = params(edge={"Fringed": "fringe", "Bound": "bound", "Pom-Pom": "pompom"}[edge])
    return row(code, title, brand, THROWS_PATH, "Throws", price, "draped_throw", description, colors,
                tuple(attrs), sizes, prm, ("width_cm", "length_cm"))  # fmt: skip


ROWS = (
    _throw(
        "HSFTFLC",
        "Fleece Sofa Throw",
        HT,
        12.0,
        "A soft fleece throw for the arm of a sofa, with a bound edge that will not fray.",
        "Fleece",
        "Sofa",
        "Bound",
        (*MAIN, GREY),
        reversible=True,
    ),
    _throw(
        "HSFTKNT",
        "Chunky Knit Throw with Tassels",
        LB,
        24.0,
        "A thick knitted throw with a tassel fringe, to drape over a bed or a sofa.",
        "Knit",
        "Bed",
        "Fringed",
        (*MAIN, CREAM),
    ),
    _throw(
        "HSFTFUR",
        "Faux Fur Throw with Pom-Poms",
        BM,
        28.0,
        "A faux fur throw with a velvet back and pom-poms round the edge, for a sofa.",
        "Faux Fur",
        "Sofa",
        "Pom-Pom",
        (*MAIN, GREY),
        reversible=True,
    ),
)


SPEC = TypeSpec(
    key="throw",
    department="Home",
    product_type="Throws",
    rows=ROWS,
    decoys=(
        decoy(1, "red throw", ROWS[0], 10, "Red Stitch Fleece Sofa Throw",
              "A grey fleece throw with a red stitch round the edge; the throw itself is grey.", color=GREY),
        decoy(3, "kids throw", ROWS[1], 11, "Kids Room Style Chunky Knit Throw with Tassels",
              "A throw in a muted adult shade, styled for a bedroom; it is sold for the whole house, not for children.",
              color=CREAM),
        decoy(4, "reversible throw", ROWS[2], 12, "Reversible Look Faux Fur Throw with Pom-Poms",
              "A faux fur throw with a velvet back that looks the same both ways; it is a single sided throw.",
              attrs=(attr("material", "Material", "Faux Fur"), attr("use", "Use", "Sofa"),
                     attr("edge", "Edge", "Pom-Pom")),
              color=BLUE),
    ),
)  # fmt: skip
