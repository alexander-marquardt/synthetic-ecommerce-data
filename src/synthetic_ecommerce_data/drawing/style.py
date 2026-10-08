"""How a drawing looks: the brand's house style, the finish's colour, the material's hatch.

Every visual channel is a function of a published property, never of the SKU,
the product id or chance (elastic/prism-industrial-products#103, rulings of
2026-09-26): a reader who sees two drawings differ concludes the products
differ, and driven by the record that conclusion is right.

=====================  ==============================================
outline colour         the brand (one of twelve inks)
paper tone             the brand (one of six tints, independent of the ink)
frame                  the brand (one of four frame treatments)
(ink, frame)           unique per brand, so the pair names the brand
part fill              the published finish; else the material's colour
section hatch          the published material
=====================  ==============================================

The brand channels are its HOUSE STYLE: consistent within a brand, different
across brands, the way each manufacturer's photography has a recognisable look.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..catalog import brands
from ..render.marking import FINISH_TINT

#: What a part is coloured when the record publishes no finish: the colour of
#: the bare material. Brass is yellow and nylon is off-white whether or not a
#: finish is named.
MATERIAL_FILL: dict[str, str] = {
    "High Speed Steel": "#d9dde0",
    "Cobalt": "#cfd6e0",
    "Solid Carbide": "#b9bcc0",
    "Powdered Metal": "#c8c8c2",
    "Steel": "#dfe3e6",
    "Alloy Steel": "#c9ced2",
    "Grade 12.9 Alloy Steel": "#b8bec3",
    "18-8 Stainless Steel": "#eef1f3",
    "Nylon": "#f4f0e2",
    "Forged Steel": "#c3c7cb",
    "Zirconia Alumina": "#5d8aa8",
    "Ceramic": "#c7613f",
    "Aluminum Oxide": "#8c6d4f",
    "316 Stainless Steel": "#e9eef1",
    "Brass": "#e0c46c",
    "Chrome Steel": "#cdd3d8",
    "440C Stainless Steel": "#e4e9ec",
    "Chrome Vanadium Steel": "#c4ccd3",
    "S2 Tool Steel": "#aeb5bb",
    "Silicon Carbide": "#3f4a55",
    # Generic raw-material words the breadth categories publish
    # (alexander-marquardt/synthetic-ecommerce-data#34): common metals,
    # one elastomer and two PPE materials that the tool- and
    # fastener-specific vocabulary above has no entry for.
    "Aluminum": "#d7dde1",
    "Stainless Steel": "#e6ebee",
    "Cast Iron": "#8a8d8f",
    "Bronze": "#b08d57",
    "Rubber": "#3a3a3a",
    "HPPE": "#9aa08a",
    "PU Foam": "#f2b134",
    # The O-ring compounds (#53): black nitrile and EPDM, brown FKM and the
    # red-orange silicone is commonly moulded in.
    "Buna-N": "#2e2e2e",
    "FKM": "#5a3e33",
    "EPDM": "#3b3f44",
    "Silicone": "#c4553f",
}

#: Finishes the original twelve types never published, and their colours.
EXTRA_FINISH_TINT: dict[str, str] = {
    "Chrome Plated": "#f0f3f6",
    "Painted": "#6f7f8a",
}

#: The fill of anything with no material or finish on the record.
DEFAULT_FILL = "#e3e7ea"


@dataclass(frozen=True)
class Hatch:
    """A section hatch: line angles (degrees) and spacing, and whether dotted."""

    angles: tuple[int, ...]
    spacing: float
    dots: bool = False


#: The section hatch, by material. Engineering drawings denote material by
#: hatch; the steels get plain diagonals, carbide the cross-hatch, sintered
#: powder a stipple, the non-metals a coarse pattern. Distinct across the
#: whole catalog, because the material NAME is now shared across product types.
MATERIAL_HATCH: dict[str, Hatch] = {
    "High Speed Steel": Hatch((45,), 5.0),
    "Cobalt": Hatch((135,), 5.0),
    "Solid Carbide": Hatch((45, 135), 5.0),
    "Powdered Metal": Hatch((), 4.0, dots=True),
    "Steel": Hatch((0,), 5.0),
    "Alloy Steel": Hatch((90,), 5.0),
    "Grade 12.9 Alloy Steel": Hatch((0, 90), 5.0),
    "18-8 Stainless Steel": Hatch((45,), 8.0, dots=True),
    "Nylon": Hatch((), 7.0, dots=True),
    "Forged Steel": Hatch((135,), 8.0, dots=True),
    "Zirconia Alumina": Hatch((60,), 4.0),
    "Ceramic": Hatch((30, 150), 6.0),
    "Aluminum Oxide": Hatch((120,), 6.0, dots=True),
    "316 Stainless Steel": Hatch((135,), 8.0, dots=True),
    "Brass": Hatch((45,), 3.0),
    "Chrome Steel": Hatch((0, 45), 6.0),
    "440C Stainless Steel": Hatch((0, 135), 6.0),
    "Chrome Vanadium Steel": Hatch((90, 45), 6.0),
    "S2 Tool Steel": Hatch((90, 135), 6.0),
    "Silicon Carbide": Hatch((), 3.0, dots=True),
    # See MATERIAL_FILL above for why these seven are here.
    "Aluminum": Hatch((30,), 5.0),
    "Stainless Steel": Hatch((150,), 5.0, dots=True),
    "Cast Iron": Hatch((0, 60), 4.0, dots=True),
    "Bronze": Hatch((60, 120), 3.0),
    "Rubber": Hatch((15,), 2.5, dots=True),
    "HPPE": Hatch((), 6.0, dots=True),
    "PU Foam": Hatch((), 5.0, dots=True),
    # The O-ring compounds: the elastomers' dotted single line, a new angle each.
    "Buna-N": Hatch((75,), 2.5, dots=True),
    "FKM": Hatch((105,), 2.5, dots=True),
    "EPDM": Hatch((165,), 2.5, dots=True),
    "Silicone": Hatch((15,), 3.5, dots=True),
}


@dataclass(frozen=True)
class HouseStyle:
    ink: str
    paper: str
    frame: str


def _mix(hex_colour: str, towards: str, share: float) -> str:
    a = [int(hex_colour[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(towards[i : i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(x * share + y * (1 - share)) for x, y in zip(a, b, strict=True)]
    return "#" + "".join(f"{c:02x}" for c in mixed)


class UnknownStyleError(KeyError):
    """A brand, finish or material the drawing has no colour or hatch for.

    Raised rather than defaulted: a drawing that quietly showed an unknown
    coating as bare steel would assert something the record contradicts.
    """


def house_style(brand: str) -> HouseStyle:
    """The brand's house style, from the brand book: its ink and its frame.

    Assigned in the book, reviewable, never re-rolled. The (ink, frame) pair
    is unique per brand; :func:`brand_for_house_style` reads it back.
    """
    if brand not in brands.BY_NAME:
        raise UnknownStyleError(f"no house style for brand {brand!r}")
    ink = brands.ink_of(brand)
    return HouseStyle(ink=ink, paper=brands.paper_of(brand), frame=brands.frame_of(brand))


def brand_for_house_style(ink: str, frame: str) -> str:
    """The brand an (ink, frame) pair names -- the encoding, read backwards.

    A pair no brand claims raises: a near miss resolved to the closest brand
    would be a confident wrong answer.
    """
    lowered = ink.strip().lower()
    for brand in brands.BRANDS:
        if brands.ink_of(brand).lower() == lowered and brands.frame_of(brand) == frame:
            return brand
    raise UnknownStyleError(f"no brand draws in ink {ink!r} with frame {frame!r}")


def part_fill(finish: str | None, material: str | None) -> str:
    if finish is not None:
        try:
            return {**FINISH_TINT, **EXTRA_FINISH_TINT}[finish]
        except KeyError as exc:
            raise UnknownStyleError(f"no colour for finish {finish!r}") from exc
    if material is not None:
        try:
            return MATERIAL_FILL[material]
        except KeyError as exc:
            raise UnknownStyleError(f"no colour for material {material!r}") from exc
    return DEFAULT_FILL


def material_hatch(material: str | None) -> Hatch | None:
    if material is None:
        return None
    try:
        return MATERIAL_HATCH[material]
    except KeyError as exc:
        raise UnknownStyleError(f"no hatch for material {material!r}") from exc
