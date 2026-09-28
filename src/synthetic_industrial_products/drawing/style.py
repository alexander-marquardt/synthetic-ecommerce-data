"""How a drawing looks: the brand's house style, the finish's colour, the material's hatch.

Every visual channel is a function of a published property, never of the SKU,
the product id or chance (elastic/prism-industrial-products#103, rulings of
2026-09-26): a reader who sees two drawings differ concludes the products
differ, and driven by the record that conclusion is right.

=====================  ==============================================
outline colour         the brand (one hue per brand, invertible)
paper tone             the brand (a faint tint of its hue)
frame                  the brand (one of four frame treatments)
part fill              the published finish; else the material's colour
section hatch          the published material
=====================  ==============================================

The brand channels are its HOUSE STYLE: consistent within a brand, different
across brands, the way each manufacturer's photography has a recognisable look.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..render.marking import BRAND_INK, FINISH_TINT

#: The four frame treatments a brand's sheets use.
FRAMES: tuple[str, ...] = ("none", "rule", "rounded", "corners")

#: Brands in a fixed order; a brand's frame is chosen by its position, so the
#: assignment is part of the code, reviewable, and never re-rolled.
BRAND_ORDER: tuple[str, ...] = tuple(BRAND_INK)

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
}

#: Finishes the original twelve types never published, and their colours.
EXTRA_FINISH_TINT: dict[str, str] = {
    "Zinc Yellow": "#ecdf8f",
    "Chrome Plated": "#f0f3f6",
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
    try:
        ink = BRAND_INK[brand]
    except KeyError as exc:
        raise UnknownStyleError(f"no house style for brand {brand!r}") from exc
    frame = FRAMES[BRAND_ORDER.index(brand) % len(FRAMES)]
    return HouseStyle(ink=ink, paper=_mix(ink, "#ffffff", 0.06), frame=frame)


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
