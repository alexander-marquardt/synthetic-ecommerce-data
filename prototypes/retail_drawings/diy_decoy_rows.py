"""Cross-department text-match decoys for the DIY drill family (gen#191, the rule of gen#294).

Each of the nine types (see :mod:`diy_tools`) has two decoys here, each from another department, so
a text search for the type meets a product that is not one:

* a **category word** decoy (class 2): a cushion or an apron whose title holds the type's words;
* an **incidental word** decoy (class 6): a scented candle that holds one word of the type in its
  title and the other in its description.

Their structured fields tell the truth (department, category path, product type, drawing), so a
department or category policy drops them. The third decoy of each type, an *absent feature* one
(class 4: "Corded Drill, Cordless Free"), is a real product of the type and lives in the type's
spec. The rows are templates: the scaled build neither derives from them nor completes their colors.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from breadth_rows import Row
from variants import cw

HOME = "Home"
_CREAM = cw("Cream", "#efe8d8")
_SAGE = cw("Sage", "#9bb08f")
_SMOKE = cw("Smoke", "#6f6a66")
_HEARTH, _LANTERN = "Hearth & Table", "Lanternby"
_CUSH = (HOME, "Soft Furnishings", "Cushions")
_APRON = (HOME, "Kitchen & Dining", "Aprons")
_CANDLE = ("Gifts", "Home Fragrance", "Scented Candles")
_FABRIC = (("fabric", "Fabric", "Cotton"),)

#: (the type's phrase, (code, title, kind of sibling), (code, title, description of the candle)).
TABLE = (
    (
        "combi drill",
        ("DCCBSH", "Combi Drill Workshop Cushion", "cushion"),
        (
            "DCCBCN",
            "Combi Lock Candle",
            "A woody scent of a cabinet shop, with a hint of drill dust.",
        ),
    ),
    (
        "corded drill",
        ("DCCDSH", "Corded Drill Garage Cushion", "cushion"),
        (
            "DCCDCN",
            "Corded Cabin Candle",
            "A pine scent from a cabin, with a hint of a drill left on the bench.",
        ),
    ),
    (
        "drill bit set",
        ("DCBSAP", "Drill Bit Set Workshop Apron", "apron"),
        (
            "DCBSCN",
            "Bit of Sawdust Candle",
            "A woody scent of a joiner's bench, with a drill set into the lid.",
        ),
    ),
    (
        "drill driver",
        ("DCDDSH", "Drill Driver Workshop Cushion", "cushion"),
        (
            "DCDDCN",
            "Driver Hall Candle",
            "A smoky scent of an old drill hall, kept for quiet evenings.",
        ),
    ),
    (
        "hammer drill",
        ("DCHDAP", "Hammer Drill Pro Apron", "apron"),
        (
            "DCHDCN",
            "Hammer Dusk Candle",
            "A warm scent of a smithy at dusk, with a drill of rain on the roof.",
        ),
    ),
    (
        "impact driver",
        ("DCIDAP", "Impact Driver Garage Apron", "apron"),
        (
            "DCIDCN",
            "Impact Crater Candle",
            "A mineral scent of a quiet lake, named for a driver who loved it.",
        ),
    ),
    (
        "sds hammer drill",
        ("DCSDSH", "SDS Hammer Drill Site Cushion", "cushion"),
        (
            "DCSDCN",
            "Hammer Hill Candle",
            "A grassy scent of a hill, with a drill of rain on the slope.",
        ),
    ),
    (
        "step ladder",
        ("DCSLSH", "Step Ladder Library Cushion", "cushion"),
        (
            "DCSLCN",
            "Step Lively Candle",
            "A woody scent of a hayloft, with a ladder to the loft on the label.",
        ),
    ),
    (
        "tool kit",
        ("DCTKCU", "Tool Kit Garage Cushion", "cushion"),
        (
            "DCTKCN",
            "Tool Shed Candle",
            "A resin scent from a garden shed, kept in a kit of three candles.",
        ),
    ),
)


def _sibling(words: str, code: str, title: str, kind: str) -> Row:
    desc = f"A cotton {kind} printed with the words '{words}' and a joke about the weekend."
    if kind == "cushion":
        return Row(
            code,
            title,
            _HEARTH,
            HOME,
            _CUSH,
            "Cushion",
            16.0,
            "cushion",
            desc,
            (_CREAM, _SAGE),
            _FABRIC,
            (("45 x 45cm", 16.0),),
        )
    return Row(
        code, title, _HEARTH, HOME, _APRON, "Apron", 12.0, "apron", desc, (_CREAM, _SAGE), _FABRIC
    )


def _candle(code: str, title: str, desc: str) -> Row:
    return Row(
        code,
        title,
        _LANTERN,
        "Gifts",
        _CANDLE,
        "Scented Candle",
        12.0,
        "jar",
        desc,
        (_SMOKE,),
        (("fragrance", "Fragrance", "Woody"),),
        label="Candle",
    )


ROWS = tuple(
    row
    for words, (sc, st, kind), (oc, ot, od) in TABLE
    for row in (_sibling(words, sc, st, kind), _candle(oc, ot, od))
)


def product_ids() -> frozenset[str]:
    """The decoys' product ids: derivation and color completion leave them as authored."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)


def docs() -> list[dict]:
    """Every decoy's catalog document."""
    return [r.doc() for r in ROWS]
