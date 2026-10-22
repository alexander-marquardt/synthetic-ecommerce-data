"""How a drawing looks: the brand's house style, the finish's color, the material's hatch.

Every visual channel is a function of a published property, never of the SKU,
the product id or chance (elastic/prism-industrial-products#103, rulings of
2026-09-26): a reader who sees two drawings differ concludes the products
differ, and driven by the record that conclusion is right.

=====================  ==============================================
outline color         the brand (one of twelve inks)
paper tone             the brand (one of six tints, independent of the ink)
frame                  the brand (one of four frame treatments)
(ink, frame)           unique per brand, so the pair names the brand
brand plate            the brand: its mark (motif + enclosure) and name
part fill              the published finish; else the material's color
section hatch          the published material
=====================  ==============================================

The brand channels are its HOUSE STYLE: consistent within a brand, different
across brands, the way each manufacturer's photography has a recognisable look.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.drawing.brand_mark import Mark, mark_for
from synthetic_ecommerce_data.domains.industrial.render.marking import FINISH_TINT

#: What a part is colored when the record publishes no finish: the color of
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
    "Grade 8 Alloy Steel": "#bdc2c7",
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
    "Urethane": "#c9572b",
    "HPPE": "#9aa08a",
    "PU Foam": "#f2b134",
    # The O-ring compounds (#53): black nitrile and EPDM, brown FKM and the
    # red-orange silicone is commonly moulded in.
    "Buna-N": "#2e2e2e",
    "FKM": "#5a3e33",
    "EPDM": "#3b3f44",
    "Silicone": "#c4553f",
    # The text-match decoys' materials (alexander-marquardt/synthetic-ecommerce-data#462):
    # the tool, wood, plastic and lubricant words their records publish.
    "Bi-Metal": "#c5cbd1",
    "Birch": "#e2c9a0",
    "Carbide": "#aeb2b6",
    "Carbon Steel": "#b5babe",
    "Diamond": "#cfd8dc",
    "Fiberglass": "#cfd9c4",
    "Laminated Steel": "#bfc5ca",
    "Lithium Complex": "#c9a66b",
    "Methacrylate Resin": "#5b6fb0",
    "Nickel": "#d4d7d2",
    "PTFE": "#f5f5f0",
    "Plastic": "#9fb0c0",
    "Sulfurized Oil": "#7a5a2e",
    "Tool Steel": "#a9afb5",
}

#: Finishes the original twelve types never published, and their colors.
EXTRA_FINISH_TINT: dict[str, str] = {
    "Chrome Plated": "#f0f3f6",
    "Painted": "#6f7f8a",
    # The text-match decoys (#462): a zinc coat and a baked-on powder coat.
    "Galvanized": "#c2cdc6",
    "Powder Coated": "#4a6a8a",
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
    "Grade 8 Alloy Steel": Hatch((0, 30), 5.0),
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
    "Urethane": Hatch((), 6.0, dots=True),
    "HPPE": Hatch((), 6.0, dots=True),
    "PU Foam": Hatch((), 5.0, dots=True),
    # The O-ring compounds: the elastomers' dotted single line, a new angle each.
    "Buna-N": Hatch((75,), 2.5, dots=True),
    "FKM": Hatch((105,), 2.5, dots=True),
    "EPDM": Hatch((165,), 2.5, dots=True),
    "Silicone": Hatch((15,), 3.5, dots=True),
    # The text-match decoys' materials (#462): each a pattern no other material uses.
    "Bi-Metal": Hatch((20,), 4.0),
    "Birch": Hatch((80,), 6.0, dots=True),
    "Carbide": Hatch((50, 130), 4.0),
    "Carbon Steel": Hatch((10,), 5.0),
    "Diamond": Hatch((), 2.0, dots=True),
    "Fiberglass": Hatch((25, 115), 6.0, dots=True),
    "Laminated Steel": Hatch((0, 90), 3.0),
    "Lithium Complex": Hatch((), 8.0, dots=True),
    "Methacrylate Resin": Hatch((), 9.0, dots=True),
    "Nickel": Hatch((70,), 4.0),
    "PTFE": Hatch((), 10.0, dots=True),
    "Plastic": Hatch((95,), 7.0, dots=True),
    "Sulfurized Oil": Hatch((), 11.0, dots=True),
    "Tool Steel": Hatch((100,), 5.0),
}


@dataclass(frozen=True)
class HouseStyle:
    ink: str
    paper: str
    frame: str
    #: The brand's name and mark, set in the plate under the figure (#132).
    name: str = ""
    mark: Mark = ()
    #: The text-free levers (#55), resolved from the brand book; the defaults
    #: are the look every brand drew before they existed.
    stroke: float = brands.WEIGHTS[0]
    dash: str = brands.DASHES[0]
    margin: float = brands.MARGINS[0]
    texture: str = brands.TEXTURES[0]


def _mix(hex_color: str, towards: str, share: float) -> str:
    a = [int(hex_color[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(towards[i : i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(x * share + y * (1 - share)) for x, y in zip(a, b, strict=True)]
    return "#" + "".join(f"{c:02x}" for c in mixed)


class UnknownStyleError(KeyError):
    """A brand, finish or material the drawing has no color or hatch for.

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
    stroke, dash, margin, texture = brands.levers_of(brand)
    return HouseStyle(
        ink=ink,
        paper=brands.paper_of(brand),
        frame=brands.frame_of(brand),
        name=brand,
        mark=mark_for(brand),
        stroke=stroke,
        dash=dash,
        margin=margin,
        texture=texture,
    )


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
            raise UnknownStyleError(f"no color for finish {finish!r}") from exc
    if material is not None:
        try:
            return MATERIAL_FILL[material]
        except KeyError as exc:
            raise UnknownStyleError(f"no color for material {material!r}") from exc
    return DEFAULT_FILL


def material_hatch(material: str | None) -> Hatch | None:
    if material is None:
        return None
    try:
        return MATERIAL_HATCH[material]
    except KeyError as exc:
        raise UnknownStyleError(f"no hatch for material {material!r}") from exc
