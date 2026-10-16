"""Soft furnishings (gen#204): curtains, blinds, rugs, throws, bath mats and shower curtains.

The catalog had cushions, duvets and towels and no window dressing, no floor coverings and no
throws, so a search for a curtain, a rug or a throw found nothing or a cushion, and size,
heading, pile and room filters had nothing to narrow. Each type here is a leaf of its own under
``Home/Soft Furnishings`` (curtains, blinds, rugs, throws) or ``Home/Bathroom`` (bath mats,
shower curtains), typed by its name, with at least three styles from at least three brands, and
draws with its own shape in :mod:`kit_softfurn`.

A style's SKUs are its colors times its sizes. A size is two measured SKU fields, in centimetres
(``width_cm`` and ``drop_cm``, or ``width_cm`` and ``length_cm``), or one (``diameter_cm`` for a
round rug), so a width and a drop are each a structured attribute, never a word in a title:

==============  ======================  =============================================
type            sizes                   key attributes (each a structured entry)
==============  ======================  =============================================
Curtains        width x drop            heading, lining, material, panels
Blind           width x drop            blind type, material, blackout, cordless, fits
Rug             width x length          shape, pile, material, washable, indoor/outdoor
Throw           width x length          material, use, reversible, edge
Bath Mat        width x length          material, non-slip, quick-dry, texture
Shower Curtain  width x drop            material, waterproof, weighted hem
==============  ======================  =============================================

A drawing param is the value of the attribute that names it, lowercased, so two styles that
differ on it draw differently (``heading``, ``lined``, ``kind``, ``form``, ``pile``, ``edge``,
``texture``, ``hem``). These styles are templates only: :func:`scale.derivable` leaves them out,
as it does the sports and accessory rows, so the range grows by authored rows.
"""

from __future__ import annotations

from dataclasses import dataclass

import kit_softfurn  # noqa: F401 -- registers curtains, blind, rug, draped_throw, bath_mat, ...
from breadth_rows import Row
from variants import cw

_SOFT = ("Home", "Soft Furnishings")
_BATH = ("Home", "Bathroom")
CURTAINS_PATH = (*_SOFT, "Curtains")
BLINDS_PATH = (*_SOFT, "Blinds")
RUGS_PATH = (*_SOFT, "Rugs")
THROWS_PATH = (*_SOFT, "Throws")
BATH_MATS_PATH = (*_BATH, "Bath Mats")
SHOWER_PATH = (*_BATH, "Shower Curtains")
_HT, _BM, _LB, _CL, _HP = "Hearth & Table", "Brackenmere Home", "Lanternby", "Calderby & Lune", "Harbour & Pine"

RED, BLUE, GREEN = cw("Red", "#c8312e"), cw("Blue", "#3f6fb5"), cw("Green", "#4f8a3a")
YELLOW, BLACK = cw("Yellow", "#f2c230"), cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
GREY, CREAM, NAVY = cw("Grey", "#9a9ca0"), cw("Cream", "#efe6cf"), cw("Navy", "#26365c")
MAIN = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


@dataclass(frozen=True)
class SoftRow(Row):
    """A style whose size is two measured SKU fields (``size_keys``), written ``"117x137"``."""

    size_keys: tuple[str, ...] = ("width_cm", "drop_cm")

    def skus(self) -> list[dict]:
        out = []
        for c in self.colors:
            for size, price in self.sizes:
                dims = dict(zip(self.size_keys, size.split("x"), strict=True))
                out.append({"color": c[0], **dims, "price": price, "in_stock": True})
        return out


def _a(key: str, name: str, value: str) -> tuple[str, str, str]:
    return (key, name, value)


def _yes(key: str, name: str) -> tuple[str, str, str]:
    return (key, name, "Yes")


def _p(**params: str) -> tuple[tuple[str, str], ...]:
    return tuple(params.items())


def _stripe(name: str, accent: str):
    return cw(name, "#f6f3ea", "stripe", accent)


def _gingham(name: str, accent: str):
    return cw(name, "#f6f3ea", "gingham", accent)


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple,
         params: tuple, size_keys: tuple[str, ...] = ("width_cm", "drop_cm")) -> SoftRow:  # fmt: skip
    return SoftRow(code, title, brand, "Home", path, ptype, price, shape, description, colors,
                   attrs, sizes, params=params, size_keys=size_keys)  # fmt: skip


def _curtain(code: str, title: str, brand: str, price: float, description: str, heading: str,
             lining: str, material: str, panels: str, colors: tuple) -> SoftRow:  # fmt: skip
    head = {"Eyelet": "eyelet", "Pencil Pleat": "pencil", "Tab Top": "tab"}[heading]
    sizes = (("117x137", price), ("167x183", price + 14.0), ("229x183", price + 28.0))
    return _row(code, title, brand, CURTAINS_PATH, "Curtains", price, "curtains", description, colors,
                (_a("heading", "Heading", heading), _a("lining", "Lining", lining),
                 _a("material", "Material", material), _a("panels", "Panels", panels)),
                sizes, _p(heading=head, lined="no" if lining == "Unlined" else "yes"))  # fmt: skip


CURTAINS = (
    _curtain("HSFCEYE", "Eyelet Curtains, Thermal Lined", _HT, 26.0,
             "Ready made eyelet curtains with a thermal lining that keeps a room warm. Sold as a pair.",
             "Eyelet", "Thermal", "Polyester", "Pair", (*MAIN, GREY, NAVY)),
    _curtain("HSFCPNC", "Velvet Pencil Pleat Curtains", _BM, 38.0,
             "Heavy velvet curtains with a pencil pleat tape, for a pole or a track. Sold as a pair.",
             "Pencil Pleat", "Thermal", "Velvet", "Pair", MAIN),
    _curtain("HSFCTAB", "Linen-Look Tab Top Curtains", _LB, 22.0,
             "Light, loose woven curtains that hang from fabric tabs on a pole. Unlined, one panel.",
             "Tab Top", "Unlined", "Linen-Look", "Single Panel", (*MAIN, CREAM)),
    _curtain("HSFCBLK", "Blackout Eyelet Curtains", _CL, 32.0,
             "Triple-weave blackout curtains for a bedroom or a nursery that block out the light. Sold as a pair.",
             "Eyelet", "Blackout", "Cotton", "Pair", (*MAIN, GREY)),
)


def _blind(code: str, title: str, brand: str, price: float, description: str, kind: str,
           material: str, fits: str, colors: tuple, blackout: bool = False,
           cordless: bool = False) -> SoftRow:  # fmt: skip
    attrs = [_a("blind_type", "Blind type", kind), _a("material", "Material", material),
             _a("fits", "Fits", fits)]  # fmt: skip
    if blackout:
        attrs.append(_yes("blackout", "Blackout"))
    if cordless:
        attrs.append(_yes("cordless", "Cordless"))
    sizes = (("60x160", price), ("90x160", price + 6.0), ("120x160", price + 12.0))
    return _row(code, title, brand, BLINDS_PATH, "Blind", price, "blind", description, colors,
                tuple(attrs), sizes, _p(kind=kind.lower()))  # fmt: skip


BLINDS = (
    _blind("HSFBROL", "Blackout Roller Blind", _HT, 12.0,
           "A blackout roller blind with a bottom bar and a side chain. It cuts to fit the window.",
           "Roller", "Fabric", "Inside Recess", (*MAIN, GREY), blackout=True),
    _blind("HSFBROM", "Cordless Roman Blind", _BM, 28.0,
           "A lined Roman blind that folds up in soft pleats. Pull it up by hand, with no cord to hang.",
           "Roman", "Fabric", "Inside Recess", (*MAIN, CREAM), cordless=True),
    _blind("HSFBVEN", "Faux Wood Venetian Blind", _CL, 24.0,
           "A moisture-proof venetian blind with wide slats that tilt, for a kitchen or a bathroom.",
           "Venetian", "Faux Wood", "Outside Recess", (*MAIN, GREY)),
    _blind("HSFBVER", "Vertical Blind with Louvres", _LB, 30.0,
           "A vertical blind with louvres that turn and draw back, for a patio door or a wide window.",
           "Vertical", "Fabric", "Outside Recess", (*MAIN, CREAM)),
)


def _rug(code: str, title: str, brand: str, price: float, description: str, shape: str, pile: str,
         material: str, colors: tuple, washable: bool = False, outdoor: bool = False) -> SoftRow:  # fmt: skip
    prm = _p(form={"Rectangular": "rectangle", "Round": "round", "Runner": "runner"}[shape],
             pile={"Flat Weave": "flat", "Shag": "shag", "Short Pile": "short"}[pile])  # fmt: skip
    attrs = [_a("rug_shape", "Shape", shape), _a("pile", "Pile", pile), _a("material", "Material", material),
             _a("indoor_outdoor", "Indoor or outdoor", "Outdoor" if outdoor else "Indoor")]  # fmt: skip
    if washable:
        attrs.append(_yes("washable", "Washable"))
    if shape == "Round":
        sizes = (("100", price), ("150", price + 40.0), ("200", price + 90.0))
        keys = ("diameter_cm",)
    elif shape == "Runner":
        sizes = (("66x200", price), ("66x300", price + 20.0), ("80x400", price + 40.0))
        keys = ("width_cm", "length_cm")
    else:
        sizes = (("120x170", price), ("160x230", price + 60.0), ("200x290", price + 130.0))
        keys = ("width_cm", "length_cm")
    return _row(code, title, brand, RUGS_PATH, "Rug", price, "rug", description, colors,
                tuple(attrs), sizes, prm, keys)  # fmt: skip


RUGS = (
    _rug("HSFRSHG", "Shaggy Deep Pile Rug", _HT, 49.0,
         "A soft, thick shaggy rug for a bedroom or a living room, with a deep pile that sheds little.",
         "Rectangular", "Shag", "Polyester", (*MAIN, GREY, CREAM)),
    _rug("HSFRFLT", "Washable Flatweave Runner", _BM, 39.0,
         "A flat woven runner for a hallway or a kitchen. It goes in the washing machine.",
         "Runner", "Flat Weave", "Cotton", (*MAIN, GREY), washable=True),
    _rug("HSFRJUT", "Round Jute Rug", _LB, 45.0,
         "A natural round jute rug with a braided edge, for a hall or a reading corner.",
         "Round", "Short Pile", "Jute", (*MAIN, CREAM)),
    _rug("HSFROUT", "Outdoor Rug for a Patio", _CL, 35.0,
         "A rug for a patio or a balcony, woven from weatherproof polypropylene that dries fast.",
         "Rectangular", "Short Pile", "Polypropylene", (*MAIN, GREY), outdoor=True),
)


def _throw(code: str, title: str, brand: str, price: float, description: str, material: str, use: str,
           edge: str, colors: tuple, reversible: bool = False) -> SoftRow:  # fmt: skip
    attrs = [_a("material", "Material", material), _a("use", "Use", use), _a("edge", "Edge", edge)]
    if reversible:
        attrs.append(_yes("reversible", "Reversible"))
    sizes = (("130x170", price), ("150x200", price + 8.0), ("200x230", price + 18.0))
    prm = _p(edge={"Fringed": "fringe", "Bound": "bound", "Pom-Pom": "pompom"}[edge])
    return _row(code, title, brand, THROWS_PATH, "Throw", price, "draped_throw", description, colors,
                tuple(attrs), sizes, prm, ("width_cm", "length_cm"))  # fmt: skip


THROWS = (
    _throw("HSFTFLC", "Fleece Sofa Throw", _HT, 12.0,
           "A soft fleece throw for the arm of a sofa, with a bound edge that will not fray.",
           "Fleece", "Sofa", "Bound", (*MAIN, GREY), reversible=True),
    _throw("HSFTKNT", "Chunky Knit Throw with Tassels", _LB, 24.0,
           "A thick knitted throw with a tassel fringe, to drape over a bed or a sofa.",
           "Knit", "Bed", "Fringed", (*MAIN, CREAM)),
    _throw("HSFTFUR", "Faux Fur Throw with Pom-Poms", _BM, 28.0,
           "A faux fur throw with a velvet back and pom-poms round the edge, for a sofa.",
           "Faux Fur", "Sofa", "Pom-Pom", (*MAIN, GREY), reversible=True),
)


def _mat(code: str, title: str, brand: str, price: float, description: str, material: str,
         texture: str, colors: tuple, quick_dry: bool = False) -> SoftRow:  # fmt: skip
    attrs = [_a("material", "Material", material), _yes("non_slip", "Non-slip"),
             _a("texture", "Texture", texture)]  # fmt: skip
    if quick_dry:
        attrs.append(_yes("quick_dry", "Quick-dry"))
    sizes = (("40x60", price), ("50x80", price + 4.0), ("60x90", price + 8.0))
    return _row(code, title, brand, BATH_MATS_PATH, "Bath Mat", price, "bath_mat", description, colors,
                tuple(attrs), sizes, _p(texture=texture.lower()), ("width_cm", "length_cm"))  # fmt: skip


BATH_MATS = (
    _mat("HSFMRIB", "Ribbed Cotton Bath Mat", _HT, 8.0,
         "A thick ribbed bath mat with a non-slip backing, soft underfoot.", "Cotton", "Ribbed",
         (*MAIN, GREY, CREAM)),
    _mat("HSFMMEM", "Memory Foam Tufted Bath Mat", _BM, 14.0,
         "A tufted memory foam bath mat that springs back, with a non-slip base.", "Memory Foam",
         "Tufted", (*MAIN, GREY), quick_dry=True),
    _mat("HSFMBAM", "Bamboo Slatted Bath Mat", _LB, 16.0,
         "A bamboo duckboard bath mat of slats on two cords, with rubber feet that grip the floor.",
         "Bamboo", "Slatted", (cw("Natural", "#c9a96e"), *MAIN[:4], BLACK, WHITE)),
)


def _shower(code: str, title: str, brand: str, price: float, description: str, material: str,
            colors: tuple, weighted: bool = False, waterproof: bool = True) -> SoftRow:  # fmt: skip
    attrs = [_a("material", "Material", material)]
    if waterproof:
        attrs.append(_yes("waterproof", "Waterproof"))
    if weighted:
        attrs.append(_yes("weighted_hem", "Weighted hem"))
    sizes = (("180x180", price), ("180x200", price + 3.0))
    return _row(code, title, brand, SHOWER_PATH, "Shower Curtain", price, "shower_curtain", description,
                colors, tuple(attrs), sizes, _p(hem="weighted" if weighted else "plain"))  # fmt: skip


SHOWER_CURTAINS = (
    _shower("HSFSPEV", "PEVA Shower Curtain with Weighted Hem", _HP, 9.0,
            "A waterproof PEVA shower curtain with a weighted hem that keeps it from blowing in. "
            "It comes with 12 rings.", "PEVA", (*MAIN, GREY), weighted=True),
    _shower("HSFSPLY", "Polyester Shower Curtain", _CL, 12.0,
            "A heavy polyester shower curtain with a water-repellent finish and reinforced eyelets.",
            "Polyester", (*MAIN, GREY, NAVY)),
    _shower("HSFSCTN", "Cotton Striped Shower Curtain", _BM, 18.0,
            "A cotton shower curtain in a woven stripe, with a plain hem. Use it with a liner.",
            "Cotton", (_stripe("Blue", "#3f6fb5"), _stripe("Red", "#c8312e"), _stripe("Green", "#4f8a3a"),
                       _stripe("Yellow", "#f2c230"), _stripe("Black", "#2d2d33"), WHITE), waterproof=False),
)

ROWS = (*CURTAINS, *BLINDS, *RUGS, *THROWS, *BATH_MATS, *SHOWER_CURTAINS)


def docs() -> list[dict]:
    return [r.doc() for r in ROWS]
