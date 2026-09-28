"""The brand book: every manufacturer the catalog sells, what it makes, how big
it is, how its drawings look and how its copy reads.

ONE table, so a brand's name, product range, market share, house style and
voice cannot drift apart across modules. Every name is INVENTED. Each of the
names added for the 100K catalog was checked with a web search against real
industrial, tool, fastener, abrasive and bearing companies and trademarks
before it went in; names that turned up a real company of any kind were
dropped (elastic/prism-industrial-products, 100K catalog, 2026-09-28).

Why a long tail. A marketplace carries a few broad-line houses that make
something in every family and many small makers that make one or two
families. Ten brands that each made all sixteen types put ~10,000 SKUs under
every brand at 100K, which no real catalog looks like. The weights below give
the largest brand well under a tenth of the catalog and the smallest a few
hundred SKUs; ``tests/test_catalog_brands.py`` pins both ends.

A few names are ordinary English words ("Vantage Edge", "Lark & Lathe", "Tall
Mast", "Salt Meadow Works", "Morrow Anvil", "Crooked Birch", "Quiet River",
"Plumb Orchard") on purpose: a brand filter has to tell the brand from the
word, and a catalog with no such name never exercises that.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .vocab import STANDARDS_FAMILY

#: The product families a brand can make, as ``vocab.STANDARDS_FAMILY`` names them.
FAMILIES: tuple[str, ...] = ("cutting_tool", "fastener", "abrasive", "hand_tool", "motion")
ALL = frozenset(FAMILIES)

#: Outline inks. Twelve hues dark enough to read as line work at thumbnail
#: size, pairwise far enough apart that an antialiased stroke in one never
#: passes through another (``render.marking.MIN_INK_SEPARATION``). The first
#: ten are the original ten brands' inks, unchanged.
INKS: tuple[str, ...] = (
    "#1f6fb0",
    "#7a4a12",
    "#c0392b",
    "#1e7a3c",
    "#7a2fa8",
    "#0f8f8f",
    "#8a8200",
    "#b0227a",
    "#1b2a6b",
    "#e07b10",
    "#3a3a3a",
    "#6a1b4d",
)

#: The frame treatments of a sheet. Distinct at a 180px thumbnail: nothing, a
#: square rule, a rounded border, or four corner marks.
FRAMES: tuple[str, ...] = ("none", "rule", "rounded", "corners")

#: Qualifiers a product NAME or title may carry before the item, by family.
#: NON-FACTUAL on purpose: none names a material, finish, dimension, grade,
#: rating, standard, process or compatibility, because anything factual
#: needs a field on the record to back it. ("Heavy" is out for a second
#: reason: a heavy hex nut is a different product from the ones made here.)
PRODUCT_WORDS: dict[str, tuple[str, ...]] = {
    # Not "General Purpose" here: end mills publish it as a VALUE of
    # "Material Grade - Machining", so a title saying it could contradict one.
    "cutting_tool": ("Shop", "Industrial", "Workshop"),
    "fastener": ("General Purpose", "Industrial", "Shop"),
    "abrasive": ("General Purpose", "Industrial", "Shop"),
    "hand_tool": ("General Purpose", "Professional", "Workshop"),
    "motion": ("General Purpose", "Industrial", "Replacement"),
}

#: Range names a brand may give a product line: ordinary words, none a value
#: any attribute publishes.
RANGE_WORDS: tuple[str, ...] = (
    "Select",
    "Pro",
    "Shop",
    "Classic",
    "Value",
    "Signature",
    "Workshop",
    "Prime",
    "Core",
    "Elite",
)


@dataclass(frozen=True)
class Brand:
    name: str
    #: Three letters that open this brand's product ids; unique across the book.
    code: str
    #: Relative share of the lines of a type this brand makes.
    weight: float
    families: frozenset[str]
    #: House style: an index into ``INKS`` and ``FRAMES``. The PAIR is unique.
    ink: int
    frame: int
    #: Title voice, fixed per brand (a brand's catalog section reads
    #: uniformly) and chosen among census-observed variants only: whether the
    #: brand's name opens every title, and descriptive or terse (terse
    #: abbreviates: "HSS", "SGL"). The rest of the voice is :mod:`.voice`.
    brand_first: bool = False
    descriptive: bool = True

    def makes(self, type_key: str) -> bool:
        return STANDARDS_FAMILY[type_key] in self.families


def _b(name, code, weight, families, ink, frame, brand_first, descriptive):
    return Brand(name, code, weight, frozenset(families), ink, frame, brand_first, descriptive)


C, F, A, H, M = "cutting_tool", "fastener", "abrasive", "hand_tool", "motion"

#: The brand book. ``brand_first`` and ``descriptive`` are set so the
#: catalog-wide shares stay where the single draw put them before brands had
#: voices -- about 0.35 of titles open with the brand, and the census's
#: 0.6835 descriptive share (``GeneratorConfig.title_descriptive_share``) --
#: measured on the 100K build and reported in the README.
#:
#: The first ten keep their names, inks and frames (a brand's
#: frame was its position modulo four), so their drawings look as they did.
BRAND_BOOK: tuple[Brand, ...] = (
    _b("Corvane", "COR", 1.3, ALL, 0, 0, True, True),
    _b("Halstead Tool", "HAL", 2.2, (C, H), 1, 1, False, False),
    _b("Ferrox", "FER", 2.0, (F, A), 2, 2, False, True),
    _b("Bracknell", "BRA", 2.0, (F,), 3, 3, True, False),
    _b("Osterlund", "OST", 2.0, (C,), 4, 0, False, True),
    _b("Vantage Edge", "VAN", 1.8, (C, A), 5, 1, True, True),
    _b("Kelbrook", "KEL", 1.1, ALL, 6, 2, False, True),
    _b("Marrow & Sons", "MAR", 1.6, (H, F), 7, 3, False, True),
    _b("Tyndall", "TYN", 1.0, ALL, 8, 0, False, False),
    _b("Redmoor", "RED", 1.6, (M, F), 9, 1, False, True),
    # Cutting-tool specialists.
    _b("Quillon Carbide", "QUI", 1.4, (C,), 10, 0, True, True),
    _b("Tessaly Cutters", "TES", 1.1, (C,), 11, 1, False, False),
    _b("Orrinford", "ORR", 0.9, (C,), 0, 1, True, True),
    _b("Kaldermark", "KAL", 0.8, (C,), 1, 2, False, True),
    _b("Pellanor", "PEL", 0.6, (C,), 2, 3, True, False),
    _b("Wendlow Tool", "WEN", 0.5, (C,), 3, 0, True, False),
    _b("Varrick Precision", "VRK", 0.7, (C,), 4, 1, False, True),
    _b("Lark & Lathe", "LAR", 0.4, (C,), 5, 2, True, True),
    # Fastener specialists.
    _b("Rivenhall", "RIV", 1.5, (F,), 6, 3, False, True),
    _b("Boltrane", "BOL", 1.2, (F,), 7, 0, True, False),
    _b("Dunmere", "DUN", 1.0, (F,), 8, 1, False, True),
    _b("Cobbet & Pryce", "COB", 0.8, (F,), 9, 2, True, True),
    _b("Lintmoor", "LIN", 0.7, (F,), 10, 3, False, True),
    _b("Nethercott", "NET", 0.6, (F,), 11, 0, False, False),
    _b("Fallowmere", "FAL", 0.5, (F,), 0, 2, True, True),
    _b("Tall Mast", "TAL", 0.4, (F,), 1, 3, True, False),
    # Abrasive specialists.
    _b("Grisenne", "GRI", 1.2, (A,), 2, 0, False, True),
    _b("Emberlin Abrasives", "EMB", 1.0, (A,), 3, 1, True, False),
    _b("Tannerby", "TAN", 0.7, (A,), 4, 2, False, False),
    _b("Velbrook", "VEL", 0.6, (A,), 5, 3, False, True),
    _b("Salt Meadow Works", "SAL", 0.4, (A,), 6, 0, False, True),
    # Hand-tool specialists.
    _b("Ashcombe Forge", "ASH", 1.1, (H,), 7, 1, True, True),
    _b("Pennock & Hale", "PEN", 0.9, (H,), 8, 2, False, True),
    _b("Brindlecote", "BRI", 0.7, (H,), 9, 3, True, False),
    _b("Morrow Anvil", "MOR", 0.6, (H,), 10, 1, False, True),
    _b("Crooked Birch", "CRO", 0.4, (H,), 11, 2, True, True),
    # Bearing specialists.
    _b("Rolvane", "ROL", 1.4, (M,), 0, 3, False, True),
    _b("Kinnerly", "KIN", 1.1, (M,), 1, 0, True, True),
    _b("Orbelle", "ORB", 0.9, (M,), 2, 1, False, False),
    _b("Spindlewick", "SPI", 0.7, (M,), 3, 2, True, False),
    _b("Quiet River", "QRV", 0.5, (M,), 4, 3, False, True),
    _b("Harnell", "HAR", 0.4, (M,), 5, 0, True, False),
    # Two-and-three-family makers.
    _b("Maddox & Vail", "MAD", 1.0, (F, H), 6, 1, False, True),
    _b("Crennick Works", "CRE", 0.9, (C, A), 7, 2, False, False),
    _b("Plumb Orchard", "PLU", 0.8, (F, H, A), 8, 3, False, True),
)

BRANDS: tuple[str, ...] = tuple(brand.name for brand in BRAND_BOOK)
BY_NAME: dict[str, Brand] = {brand.name: brand for brand in BRAND_BOOK}


def brands_for(type_key: str) -> tuple[Brand, ...]:
    """The brands that make ``type_key``, in book order."""
    return tuple(brand for brand in BRAND_BOOK if brand.makes(type_key))


def pick_brand(rng: random.Random, type_key: str) -> str:
    """One brand for a new product of ``type_key``, by market weight."""
    candidates = brands_for(type_key)
    return rng.choices(candidates, weights=[b.weight for b in candidates], k=1)[0].name


def ink_of(brand: str) -> str:
    return INKS[BY_NAME[brand].ink]


def frame_of(brand: str) -> str:
    return FRAMES[BY_NAME[brand].frame]
