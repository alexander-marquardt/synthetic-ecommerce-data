"""Mens clothing depth (gen#310, the Mens slice): data only.

The Mens tree held no trousers, chinos, polo shirts, coats, jackets, blazers or suits, three
products per shirt leaf and a handful of underwear and socks, so ranking, facets and policies had
nothing to choose between and "mens chinos" or "mens coat" found an empty page. This module adds,
as distinct products (a product is a style; its colors times its sizes are its SKUs):

=============================  ======================================================  =====
group                          leaves                                                  floor
=============================  ======================================================  =====
trousers and chinos            Mens/Trousers: Chinos, Formal Trousers, Cargo Trousers      80
shirts (with ``shirt_rows``)   Mens/Tops/Shirts: the four shirt leaves, Formal, Check,    120
                               Short Sleeve
polo shirts                    Mens/Tops/Polos                                             50
coats and jackets              Mens/Coats & Jackets: Wool, Trench, Pea, Puffer, Bomber,    80
                               Waterproof
suits, blazers and tailoring   Mens/Suits & Tailoring: Blazers, Suit Jackets, Suit         60
                               Trousers
underwear and socks            Mens/Underwear/Boxers, Mens/Socks (with the old ones)       60
=============================  ======================================================  =====

Knitwear is gen#309's and is not added here. Every title reads as a shop's own ("Pure Linen
Relaxed Fit Shirt"), and each product carries its fit, material and, where it applies, collar and
sleeve length.

**Text-match decoys (gen#294, maintainer ruling 2026-10-14).** Every product type this module
adds carries at least three decoys of each of the seven classes: a title whose words mislead a
text search while the structured fields stay true. :data:`TABLE` lists each one with its class,
the query it targets and the policy that repairs it; ``tests/test_retail_mens_depth_310.py`` pins
the three per class per type and their truth. (gen PR #306 holds the shared ``decoy_rows.TABLE``;
until it merges these rows are registered here, and move to it afterwards.)

1. **color**: "Mens White Chinos with Red Stripes" is white.
2. **category word**: "Mens Dress Shirt", "Mens Jumper Knit Polo Shirt".
3. **audience word**: "Mens Boyfriend Fit Chinos".
4. **feature absent**: "Mens Wool-Free Coat" has no wool.
5. **shade in the description only**: "Mens Moonbeam Chinos" are Ivory.
6. **incidental word in a short title** (a range name): "Mens Kettle Hill Chinos" are not kettles.
7. **invented brand** holding a color or category word: "Black Curlew", "Yellow Plover",
   "Jacket Wren", each with its own house style (``house_styles.py``) so the drawing's logo reads
   the brand's name; the garment is drawn in its true color.

The rows are templates only: :func:`scale.derivable` leaves them out (``scale.MENS_DEPTH_IDS``),
so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import zlib
from dataclasses import dataclass
from itertools import product as _product

import kit_suits  # noqa: F401 -- registers suit_jacket, suit_trousers, waistcoat, dinner_suit, formal_accessory
import named_parts
import type_colors
import type_registry
from breadth_rows import OWNERS
from class_model import BRAND_OWNER
from decoy_apparel import DETAIL_HEX
from lowerbody_rows import LRow
from main_color_hex import MAIN_COLORS
from place_ranges import place_range
from variants import cw

#: The shop's own brands these rows sell, owned as the rest of the clothing tree states.
_BRANDS = ("Harbour & Pine", "Larkmoor", "Wrenfield", "Calderby & Lune", "Bramblewood")
OWNERS.update({b: BRAND_OWNER[b] for b in _BRANDS})
#: The invented class-7 brands: a color or a category word in the name (not real shops).
NEW_BRANDS = ("Black Curlew", "Yellow Plover", "Jacket Wren")
OWNERS.update(dict.fromkeys(NEW_BRANDS, "third_party"))

_C = "Clothing"
_LING = "Lingerie & Nightwear"

#: The colors, as (plain word, swatch): the six main colors and the usual menswear shades.
HEX = {
    **MAIN_COLORS, "Navy": "#26365c", "Charcoal": "#4a4a50", "Khaki": "#b8a36a",
    "Stone": "#bdb5a6", "Grey": "#9a9a9a", "Brown": "#6b4a32", "Camel": "#b5835a",
    "Olive": "#6b6b2f", "Burgundy": "#6d1f2f", "Cream": "#efe4cf", "Ivory": "#f3ecd9",
    "Off White": "#f4f1ea",
}  # fmt: skip


def _col(name: str):
    return cw(name, HEX[name])


#: One palette per kind; a row takes two or three of its colors, rotating with its index.
_PALETTE = ("Navy", "Black", "White", "Blue", "Grey", "Green", "Red", "Khaki", "Charcoal",
            "Yellow", "Stone", "Burgundy", "Olive", "Brown")  # fmt: skip
_TAILORED = ("Navy", "Charcoal", "Black", "Grey", "Blue", "Brown", "Green", "Burgundy", "Red",
             "White", "Yellow", "Stone")  # fmt: skip

#: Socks: yellow is among the first picks, so complete() never has to give a decoy the gap.
_SOCKS = ("Yellow", "Navy", "Black", "White", "Blue", "Green", "Red", "Grey", "Charcoal", "Khaki")

LETTER = ("S", "M", "L", "XL", "XXL")
WAIST = ("28", "30", "32", "34", "36", "38")
CHEST = ("S", "M", "L", "XL", "XXL")


def _sizes(price: float, names: tuple[str, ...]) -> tuple[tuple[str, float], ...]:
    return tuple((n, price) for n in names)


def _colors(i: int, palette: tuple[str, ...] = _PALETTE):
    n = len(palette)
    picks = [palette[(2 * i) % n], palette[(2 * i + 1) % n]]
    if i % 3 == 0:
        picks.append(palette[(5 * i + 3) % n])
    return tuple(_col(c) for c in dict.fromkeys(picks))


def _choose(combos: list[tuple], n: int) -> list[tuple]:
    """``n`` of the combinations, spread by a digest of each so no one kind takes the first n."""
    ranked = sorted(combos, key=lambda c: zlib.crc32("|".join(map(str, c)).encode()))
    return ranked[:n]


@dataclass(frozen=True)
class Kind:
    """What a product type is: where it lives, how it is drawn and sold, its decoy nouns."""

    ptype: str
    noun: str
    shape: str
    sizes: tuple[str, ...]
    size_key: str
    dept: str
    base_price: float
    material: str  # a decoy's true material: none of the words a class-4 decoy names
    facts: tuple = ()
    params: tuple = ()
    borrow: tuple[str, ...] = ()  # class 2: another category's noun, three of them
    absent: tuple[str, ...] = ()  # class 4: a feature named, three of them
    path: tuple[str, ...] = ()  # where a class-4 decoy sits: a leaf named for no material
    spread: tuple[tuple[str, ...], ...] = ()  # the leaves the other decoys spread over
    fitted: bool = True  # a garment has a fit; a tie does not
    item: str | None = None  # a decoy of an accessory kind is still this accessory_type
    decoy_attrs: tuple = ()  # attributes the decoys of classes 1-3 and 5-7 carry as the type's
    decoy_params: tuple = ()  # the drawing params those decoys carry beyond ``params``
    absent_noun: str = ""  # class 4: the noun of the leaf it sits in, when it is not ``noun``
    absent_attrs: tuple = ()  # attributes a class 4 decoy carries instead of ``decoy_attrs``
    absent_text: str = ""  # class 4 description, "{f}" the feature named; "" for the default


_SR = ("size_range", ["regular"])
KINDS = {
    "Mens Trousers": Kind("Mens Trousers", "Chinos", "trousers", WAIST, "waist", _C, 22.0, "Cotton",
                     params=(("fit", "straight"), ("rise", "mid")),
                     borrow=("shirt", "blazer", "jumper"),
                     absent=("Linen-Look", "Leather-Look", "Wool-Free"),
                     path=("Mens", "Trousers", "Chinos")),
    "Shirt": Kind("Shirt", "Shirt", "blouse", CHEST, "size", _C, 22.0, "Polyester",
                  facts=(("neckline", "collared"), _SR), borrow=("dress", "blazer", "coat"),
                  absent=("Silk-Feel", "Linen-Look", "Cashmere-Feel"),
                  path=("Mens", "Tops", "Shirts", "Formal Shirts"),
                  spread=(("Mens", "Tops", "Shirts", "Formal Shirts"),
                          ("Mens", "Tops", "Shirts", "Short Sleeve Shirts"))),
    "Polo Shirt": Kind("Polo Shirt", "Polo Shirt", "tshirt", CHEST, "size", _C, 16.0, "Cotton",
                       facts=(("neckline", "collared"), _SR), borrow=("shirt", "jumper", "blazer"),
                       absent=("Wool-Free", "Cashmere-Feel", "Leather-Look"),
                       path=("Mens", "Tops", "Polos")),
    "Coat": Kind("Coat", "Coat", "coat", CHEST, "size", _C, 70.0, "Polyester", facts=(_SR,),
                 borrow=("shirt", "blazer", "jumper"),
                 absent=("Wool-Free", "Down-Free", "Fur-Free"),
                 path=("Mens", "Coats & Jackets", "Trench Coats"),
                 spread=(("Mens", "Coats & Jackets", "Trench Coats"),
                         ("Mens", "Coats & Jackets", "Pea Coats"))),
    "Jacket": Kind("Jacket", "Jacket", "coat", CHEST, "size", _C, 48.0, "Nylon", facts=(_SR,),
                   borrow=("shirt", "jumper", "trouser"),
                   absent=("Leather-Look", "Down-Free", "Suede-Feel"),
                   path=("Mens", "Coats & Jackets", "Waterproof Jackets"),
                   spread=(("Mens", "Coats & Jackets", "Bomber Jackets"),
                           ("Mens", "Coats & Jackets", "Puffer Jackets"),
                           ("Mens", "Coats & Jackets", "Waterproof Jackets"))),
    "Suit Jacket": Kind("Suit Jacket", "Blazer", "suit_jacket", CHEST, "size", _C, 60.0, "Polyester",
                        facts=(_SR,), params=(("fit", "regular"), ("lapel", "notch"), ("buttons", "2")),
                        borrow=("jumper", "shirt", "coat"),
                        absent=("Wool-Free", "Silk-Feel", "Linen-Look"),
                        path=("Mens", "Suits & Tailoring", "Blazers")),
    "Suit Trousers": Kind("Suit Trousers", "Suit Trousers", "suit_trousers", WAIST, "waist", _C,
                          36.0, "Polyester", facts=(_SR,), params=(("fit", "regular"), ("leg", "regular")),
                          borrow=("shirt", "jumper", "coat"),
                          absent=("Wool-Free", "Silk-Feel", "Linen-Look"),
                          path=("Mens", "Suits & Tailoring", "Suit Trousers")),
    "Waistcoat": Kind("Waistcoat", "Waistcoat", "waistcoat", CHEST, "size", _C, 30.0, "Polyester",
                      facts=(_SR,), params=(("fit", "regular"), ("buttons", "5")),
                      borrow=("shirt", "jumper", "dress"),
                      absent=("Wool-Free", "Silk-Feel", "Linen-Look"),
                      path=("Mens", "Suits & Tailoring", "Waistcoats")),
    "Dinner Suit": Kind("Dinner Suit", "Dinner Suit", "dinner_suit", CHEST, "size", _C, 120.0,
                        "Polyester", facts=(_SR,), params=(("fit", "regular"), ("lapel", "shawl")),
                        borrow=("shirt", "jumper", "dress"),
                        absent=("Wool-Free", "Silk-Feel", "Linen-Look"),
                        path=("Mens", "Suits & Tailoring", "Dinner Suits")),
    "Formal Accessories": Kind("Formal Accessories", "Tie", "formal_accessory", (),
                               "size", _C, 12.0, "Polyester", params=(("item", "tie"),),
                               borrow=("shirt", "jumper", "dress"),
                               absent=("Leather-Look", "Cashmere-Feel", "Linen-Look"),
                               path=("Mens", "Suits & Tailoring", "Formal Accessories"),
                               fitted=False, item="Tie"),
    "Boxers": Kind("Boxers", "Boxers", "boxers", CHEST, "size", _LING, 5.0, "Cotton",
                   params=(("fit", "boxer"),), borrow=("shirt", "trouser", "sock"),
                   absent=("Silk-Feel", "Lace-Free", "Cashmere-Feel"),
                   path=("Mens", "Underwear", "Boxers")),
    "Socks": Kind("Socks", "Socks", "socks", ("S/M", "M/L", "L/XL"), "size", _C, 9.0, "Cotton",
                  params=(("pairs", "3"),), borrow=("trouser", "jumper", "boxer"),
                  absent=("Wool-Free", "Cashmere-Feel", "Silk-Feel"),
                  path=("Mens", "Socks", "Everyday Socks"),
                  spread=(("Mens", "Socks", "Everyday Socks"), ("Mens", "Socks", "Ankle Socks"),
                          ("Mens", "Socks", "Sports Socks"))),
}  # fmt: skip


def _row(code, title, brand, kind: Kind, path, desc, colors, attrs, *, price, params=None,
         shape=None, facts=None) -> LRow:
    return LRow(
        code, title, brand, kind.dept, path, kind.ptype, price, shape or kind.shape, desc, colors,
        attrs=attrs, sizes=_sizes(price, kind.sizes),
        params=kind.params if params is None else params, size_key=kind.size_key,
        facts=kind.facts if facts is None else facts,
    )  # fmt: skip


def _an(phrase: str) -> str:
    """The phrase, lowercased, behind its own article ("an organic cotton", "a slim")."""
    word = phrase.lower()
    return f"{'an' if word[:1] in 'aeiou' else 'a'} {word}"


def _plural(noun: str) -> bool:
    """Whether the noun is a plural that takes no article: chinos, trousers, boxers, socks."""
    word = noun.lower().split()[-1]
    return word.endswith("s") and not word.endswith(("ss", "us"))


def _np(lead: str, noun: str) -> str:
    """A capitalised noun phrase, behind its article when the noun is singular: "A black polo
    shirt", but "Black suit trousers" (a plural takes no article, gen#448)."""
    phrase = f"{lead} {noun}".strip().lower()
    return phrase.capitalize() if _plural(noun) else _an(phrase).capitalize()


def _fabric(fabric: str, base: str) -> tuple[str, str, tuple]:
    """(the words that lead the description, the Material value, the attributes beyond it) of a
    pool entry. The pools mix cloths with finishes ("Crease Resistant"), patterns ("Checked")
    and sourcing claims ("Recycled"): the cloth is the leaf's base, the rest its own attribute
    (gen#448)."""
    key = fabric.lower()
    if key in type_colors.MATERIAL_OF:
        material = type_colors.MATERIAL_OF[key]
        return material, material, ()
    if key in type_colors.CARRIED_AS:
        return f"{fabric} {base}", base, (type_colors.CARRIED_AS[key],)
    return fabric, fabric, ()


def _case(material: str) -> str:
    """The catalogue's spelling of a blend: "Linen blend", never "Linen Blend"."""
    return material.replace(" Blend", " blend")


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


# --------------------------------------------------------------------------
# The floor rows: a leaf is a fabric x fit x detail product, a digest-spread n of them.
# --------------------------------------------------------------------------

_FITS3 = ("Slim", "Regular", "Relaxed")
_FIT_PARAM = {"Skinny": "skinny", "Slim": "slim", "Straight": "straight", "Tapered": "tapered",
              "Relaxed": "relaxed", "Regular": "straight"}  # fmt: skip


@dataclass(frozen=True)
class Leaf:
    abbr: str
    path: tuple[str, ...]
    kind: str
    n: int
    fabrics: tuple[str, ...]
    fits: tuple[str, ...]
    details: tuple[str, ...]  # a title word each ("" for none), also the description's tail
    title: str  # "{fabric} {fit} Fit {detail}{noun}": the pattern of the title
    palette: tuple[str, ...] = _PALETTE
    sleeve: str | None = None
    pattern: str = "plain"
    extra_price: float = 0.0
    stripe_accent: bool = False
    waist: str | None = None  # the waist_type attribute, and the drawing's waist when "Elastic"
    noun: str = ""  # the description's noun when it is not the kind's: the leaf's own ("formal trousers")
    base: str = ""  # the cloth a finish or pattern entry of ``fabrics`` is made in, when not the kind's


_LEAVES = (
    Leaf("CH", ("Mens", "Trousers", "Chinos"), "Mens Trousers", 36,
         ("Stretch Cotton", "Cotton Twill", "Garment Dyed", "Brushed Cotton", "Linen Blend",
          "Organic Cotton", "Washed Cotton", "Lightweight Cotton"),
         ("Skinny", "Slim", "Straight", "Tapered", "Relaxed"), ("",), "{f} {fit} Fit Chinos",
         noun="chinos"),
    Leaf("FT", ("Mens", "Trousers", "Formal Trousers"), "Mens Trousers", 20,
         ("Wool Blend", "Twill", "Flannel", "Stretch Suiting", "Herringbone", "Crease Resistant",
          "Cotton Stretch"), ("Slim", "Regular", "Tapered"), ("",),
         "{f} {fit} Fit Formal Trousers", palette=_TAILORED, extra_price=10.0,
         noun="formal trousers", base="Polyester Blend"),
    Leaf("CG", ("Mens", "Trousers", "Cargo Trousers"), "Mens Trousers", 10,
         ("Ripstop", "Cotton Twill", "Washed Canvas", "Stretch Cotton", "Lightweight Nylon"),
         ("Relaxed", "Tapered"), ("",), "{f} {fit} Fit Cargo Trousers", extra_price=4.0,
         noun="cargo trousers"),
    Leaf("ST", ("Mens", "Suits & Tailoring", "Suit Trousers"), "Suit Trousers", 24,
         ("Wool Blend", "Birdseye", "Twill", "Stretch", "Herringbone", "Flannel"),
         ("Slim", "Tailored", "Regular"), ("Short", "Regular", "Long"),
         "{f} {fit} Fit {d} Leg Suit Trousers", palette=_TAILORED, extra_price=14.0),
    Leaf("SF", ("Mens", "Tops", "Shirts", "Formal Shirts"), "Shirt", 24,
         ("Poplin", "Twill", "Herringbone", "Easy Iron Cotton", "Stretch Cotton", "Pinpoint",
          "Brushed Twill"), ("Slim", "Regular", "Tailored"),
         ("Cutaway Collar", "Classic Collar", "Spread Collar"),
         "{f} {fit} Fit {d} Shirt", palette=("White", "Blue", "Black", "Navy", "Grey", "Red",
                                             "Green", "Yellow", "Stone", "Burgundy"),
         sleeve="Long"),
    Leaf("SO", ("Mens", "Tops", "Shirts", "Oxford Shirts"), "Shirt", 14,
         ("Washed Oxford", "Pinpoint Oxford", "Royal Oxford", "Stretch Oxford",
          "Garment Dyed Oxford", "Brushed Oxford"), _FITS3,
         ("Button Down Collar", "Classic Collar"), "{f} {fit} Fit {d} Shirt", sleeve="Long"),
    Leaf("SL", ("Mens", "Tops", "Shirts", "Linen Shirts"), "Shirt", 14,
         ("Pure Linen", "Linen Blend", "Washed Linen", "Cotton Linen", "Linen Viscose"), _FITS3,
         ("Grandad Collar", "Classic Collar", "Camp Collar"), "{f} {fit} Fit Shirt",
         sleeve="Long"),
    Leaf("SN", ("Mens", "Tops", "Shirts", "Flannel Shirts"), "Shirt", 10,
         ("Brushed Cotton", "Heavy Flannel", "Organic Flannel", "Soft Flannel"), _FITS3,
         ("Classic Collar", "Button Down Collar"), "{f} {fit} Fit Flannel Shirt", sleeve="Long"),
    Leaf("SD", ("Mens", "Tops", "Shirts", "Denim Shirts"), "Shirt", 10,
         ("Mid Weight Denim", "Light Wash Denim", "Stonewashed Denim", "Chambray",
          "Stretch Denim"), _FITS3, ("Classic Collar", "Western Yoke"),
         "{f} {fit} Fit Denim Shirt", palette=("Blue", "Navy", "Black", "Grey", "Stone", "White",
                                               "Red", "Green", "Yellow"), sleeve="Long"),
    Leaf("SC", ("Mens", "Tops", "Shirts", "Check Shirts"), "Shirt", 14,
         ("Gingham", "Tattersall", "Windowpane", "Madras", "Buffalo", "Micro Check",
          "Brushed Check"), ("Slim", "Regular"), ("Classic Collar", "Button Down Collar"),
         "{f} {fit} Fit Shirt", sleeve="Long", pattern="check"),
    Leaf("SS", ("Mens", "Tops", "Shirts", "Short Sleeve Shirts"), "Shirt", 14,
         ("Cotton Poplin", "Linen Blend", "Seersucker", "Printed Viscose", "Cotton Oxford",
          "Camp Collar Cotton"), _FITS3, ("Camp Collar", "Classic Collar"),
         "{f} {fit} Fit Short Sleeve Shirt", sleeve="Short"),
    Leaf("PO", ("Mens", "Tops", "Polos"), "Polo Shirt", 32,
         ("Pique Cotton", "Cotton Jersey", "Stretch Pique", "Organic Cotton", "Performance",
          "Linen Cotton", "Textured Cotton"), _FITS3,
         ("Tipped", "Plain", "Striped", "Button Down"), "{f} {fit} Fit {d} Polo Shirt",
         sleeve="Short"),
    Leaf("WC", ("Mens", "Coats & Jackets", "Wool Coats"), "Coat", 12,
         ("Wool Blend", "Pure Wool", "Wool Cashmere Blend", "Melton Wool"), ("Slim", "Regular"),
         ("Single Breasted", "Double Breasted", "Longline"), "{f} {d} Coat",
         palette=_TAILORED, sleeve="Long", extra_price=30.0),
    Leaf("TC", ("Mens", "Coats & Jackets", "Trench Coats"), "Coat", 8,
         ("Cotton Gabardine", "Showerproof", "Belted", "Lightweight"), ("Classic", "Slim Fit"),
         ("",), "{fit} {f} Trench Coat", palette=("Stone", "Navy", "Black", "Khaki", "Green",
                                                  "Red", "Blue", "Yellow"), sleeve="Long",
         extra_price=20.0),
    Leaf("PC", ("Mens", "Coats & Jackets", "Pea Coats"), "Coat", 6,
         ("Wool Blend", "Navy Melton", "Heavy Wool"), ("Classic", "Slim Fit"), ("",),
         "{fit} {f} Pea Coat", palette=_TAILORED, sleeve="Long", extra_price=25.0),
    Leaf("PJ", ("Mens", "Coats & Jackets", "Puffer Jackets"), "Jacket", 8,
         ("Lightweight", "Hooded", "Quilted", "Recycled Fill", "Water Repellent", "Down Fill",
          "Packable", "Longline"), ("",), ("",), "{f} Puffer Jacket", sleeve="Long",
         extra_price=12.0),
    Leaf("BJ", ("Mens", "Coats & Jackets", "Bomber Jackets"), "Jacket", 6,
         ("Classic", "Quilted", "Satin Finish", "Ripstop", "Reversible", "Padded"), ("",), ("",),
         "{f} Bomber Jacket", sleeve="Long"),
    Leaf("WJ", ("Mens", "Coats & Jackets", "Waterproof Jackets"), "Jacket", 8,
         ("Lightweight", "Packable", "Hooded", "Breathable", "Taped Seam", "Insulated",
          "Mountain", "Rain Mac"), ("",), ("",), "{f} Waterproof Jacket", sleeve="Long",
         extra_price=6.0),
    Leaf("BL", ("Mens", "Suits & Tailoring", "Blazers"), "Suit Jacket", 20,
         ("Wool Blend", "Linen Blend", "Cotton Stretch", "Textured", "Herringbone",
          "Unstructured", "Checked"), _FITS3, ("Notch", "Peak"), "{f} {fit} Fit {d} Lapel Blazer",
         palette=_TAILORED, sleeve="Long", base="Wool Blend"),
    Leaf("SJ", ("Mens", "Suits & Tailoring", "Suit Jackets"), "Suit Jacket", 24,
         ("Wool Blend", "Birdseye", "Twill", "Stretch", "Herringbone", "Tonic"),
         ("Slim", "Tailored", "Regular"), ("Notch", "Peak"), "{f} {fit} Fit {d} Lapel Suit Jacket",
         palette=_TAILORED, sleeve="Long", extra_price=15.0),
    Leaf("WA", ("Mens", "Suits & Tailoring", "Waistcoats"), "Waistcoat", 18,
         ("Wool Blend", "Herringbone", "Tweed", "Stretch", "Linen Blend", "Velvet"),
         ("Slim", "Tailored", "Regular"), ("Four Button", "Five Button", "Six Button"),
         "{f} {fit} Fit {d} Waistcoat", palette=_TAILORED, extra_price=4.0),
    Leaf("DS", ("Mens", "Suits & Tailoring", "Dinner Suits"), "Dinner Suit", 14,
         ("Wool Blend", "Barathea", "Mohair Blend", "Velvet", "Wool Crepe", "Stretch Wool"),
         ("Slim", "Tailored", "Regular"), ("Peak", "Shawl"), "{f} {fit} Fit {d} Lapel Dinner Suit",
         palette=("Black", "Navy", "White", "Red", "Blue", "Green", "Yellow", "Burgundy", "Charcoal"),
         extra_price=20.0),
    Leaf("FA", ("Mens", "Suits & Tailoring", "Formal Accessories"), "Formal Accessories", 20,
         ("Silk", "Satin", "Wool", "Knitted", "Cotton", "Velvet"),
         ("",), ("Tie", "Bow Tie", "Braces", "Cummerbund", "Pocket Square"), "{f} {d}",
         palette=_TAILORED),
    Leaf("BX", ("Mens", "Underwear", "Boxers"), "Boxers", 24,
         ("Cotton Stretch", "Bamboo", "Organic Cotton", "Jersey", "Woven Cotton", "Modal",
          "Microfibre", "Recycled"), ("Trunks", "Boxer Shorts", "Briefs"), ("",),
         "{f} {fit}"),
    Leaf("SK", ("Mens", "Socks", "Ankle Socks"), "Socks", 4,
         ("Cotton Rich", "Bamboo", "Sports Cushioned", "Organic Cotton"), ("",), ("",),
         "{f} Ankle Socks", palette=_SOCKS),
    Leaf("SE", ("Mens", "Socks", "Everyday Socks"), "Socks", 4,
         ("Combed Cotton", "Merino Blend", "Ribbed Cotton", "Soft Top"), ("",), ("",),
         "{f} Everyday Socks", palette=_SOCKS),
    Leaf("SP", ("Mens", "Socks", "Sports Socks"), "Socks", 4,
         ("Arch Support", "Padded Sole", "Moisture Wicking", "Running"), ("",), ("",),
         "{f} Sports Socks", palette=_SOCKS),
)  # fmt: skip

#: leaf path -> its sleeve length: a decoy takes its leaf's.
_SLEEVE = {leaf.path: leaf.sleeve for leaf in _LEAVES}

_TAIL = {
    "Mens Trousers": "with a belt loop waist and two side pockets",
    "Shirt": "with a button front and a chest pocket",
    "Polo Shirt": "with a ribbed collar and a two button placket",
    "Coat": "with a full lining and two front pockets",
    "Jacket": "with a zip front and two side pockets",
    "Suit Jacket": "with a lapel, two flap pockets and a button fastening",
    "Suit Trousers": "with a pleat front, belt loops and a pressed crease",
    "Waistcoat": "with a V neck, a buttoned front and two welt pockets",
    "Dinner Suit": "with satin faced lapels and a side stripe on the trousers, for evening wear",
    "Formal Accessories": "for formal wear",
    "Boxers": "with a soft covered waistband",
    "Socks": "with a cushioned foot and a stretch top",
}


#: fit -> the shape param (the kit draws slim, tailored and regular); relaxed is a regular cut.
_SUIT_FIT = {"Slim": "slim", "Tailored": "tailored", "Regular": "regular", "Relaxed": "regular"}
_OCCASIONS = ("Business", "Wedding", "Formal", "Smart Casual")
_BUTTONS = {"Four Button": "4", "Five Button": "5", "Six Button": "6"}


def _suit(ptype: str, fit: str, detail: str, i: int) -> tuple[tuple, tuple]:
    """The structured attributes (beyond fit and material) and the drawing params of a tailoring
    product, each a choice the drawing shows: the lapel, the leg length, the buttons, the item."""
    f = _SUIT_FIT.get(fit, "regular")
    if ptype == "Suit Jacket":
        lapel = detail or "Notch"
        n = i % 2
        return ((_a("lapel", "Lapel", lapel), _a("buttons", "Buttons", ("Two Button", "Three Button")[n]),
                 _a("occasion", "Occasion", _OCCASIONS[i % 4])),
                (("fit", f), ("lapel", lapel.lower()), ("buttons", ("2", "3")[n])))  # fmt: skip
    if ptype == "Suit Trousers":
        return (_a("leg_length", "Leg length", detail),), (("fit", f), ("leg", detail.lower()))
    if ptype == "Waistcoat":
        return (_a("buttons", "Buttons", detail),), (("fit", f), ("buttons", _BUTTONS[detail]))
    if ptype == "Dinner Suit":
        return (_a("lapel", "Lapel", detail),), (("fit", f), ("lapel", detail.lower()))
    if ptype == "Formal Accessories":
        return ((_a("accessory_type", "Accessory type", detail),),
                (("item", detail.lower().replace(" ", "_")),))  # fmt: skip
    return (), ()


def _floor_rows(leaves=None, kinds=None, tails=None, prefix: str = "MF") -> list[LRow]:
    """The floor rows of ``leaves`` (this module's by default), coded ``<prefix><abbr><n>``."""
    leaves, kinds, tails = leaves or _LEAVES, kinds or KINDS, tails or _TAIL
    out: list[LRow] = []
    for leaf in leaves:
        kind = kinds[leaf.kind]
        combos: dict[str, tuple] = {}
        for fabric, fit, detail in _product(leaf.fabrics, leaf.fits, leaf.details):
            t = "Mens " + " ".join(leaf.title.format(f=fabric, fit=fit, d=detail).split())
            combos.setdefault(t, (fabric, fit, detail))
        pairs = _choose([(t, *c) for t, c in combos.items()], leaf.n)
        assert len(pairs) == leaf.n, (leaf.abbr, len(combos))
        for i, (title, fabric, fit, detail) in enumerate(pairs):
            brand = _BRANDS[(i + len(leaf.abbr)) % len(_BRANDS)]
            price = round(kind.base_price + leaf.extra_price + 2.0 * (i % 7), 2)
            colors = _colors(i, type_colors.palette(leaf.path, leaf.palette))
            lead, material, more = _fabric(fabric, leaf.base or kind.material)
            # a check shirt, or a cloth the pool calls "Checked" (a pattern, gen#448): check colors
            checked = leaf.pattern == "check" or any(m[0] == "pattern" for m in more)  # gen#447
            if checked:
                colors = tuple(cw(f"{c[0]} Check", c[2], "gingham", "#2a2a2e") for c in colors)
            elif detail == "Striped":  # a "Striped Polo Shirt" is drawn striped, not plain
                colors = tuple(cw(f"{c[0]} Stripe", c[2], "stripe", "#f4f1ea") for c in colors)
            fit_an = _an(fit or "regular")
            noun = detail.lower() if kind.item else (leaf.noun or kind.noun).lower()
            if kind.ptype == "Boxers":  # the fit IS the garment: trunks, boxer shorts, briefs
                noun, cut = fit.lower(), ""
            else:
                cut = f" cut to {fit_an} fit" if kind.fitted else ""
            desc = f"{_np(lead, noun)}{cut} {tails[leaf.kind]}."
            attrs = [_a("material", "Material", _case(material)), *(_a(*m) for m in more)]
            if kind.fitted:
                attrs.insert(0, _a("fit", "Fit", fit or "Regular"))
            suit_attrs, suit_params = _suit(kind.ptype, fit, detail, i)
            attrs += suit_attrs
            if leaf.sleeve:
                attrs.append(_a("sleeve_length", "Sleeve length", leaf.sleeve))
            if leaf.waist:
                attrs.append(_a("waist_type", "Waist type", leaf.waist))
            if detail and "Collar" in detail or detail in ("Western Yoke",):
                attrs.append(_a("collar", "Collar", detail.replace(" Collar", "")))
            if kind.ptype == "Polo Shirt":
                attrs.append(_a("collar", "Collar", "Polo"))
            params = kind.params
            if kind.ptype == "Mens Trousers":
                style = "tailored" if "Formal" in leaf.title or "Suit" in leaf.title else "jeans"
                params = (("fit", _FIT_PARAM.get(fit, "straight")), ("rise", "mid"),
                          ("style", style))  # fmt: skip
                if leaf.waist == "Elastic":
                    params += (("waist", "elasticated"),)
            elif kind.ptype == "Boxers":
                params = (("fit", {"Trunks": "trunks", "Boxer Shorts": "boxer",
                                   "Briefs": "brief"}[fit]),)  # fmt: skip
            elif kind.ptype == "Socks":
                params = (("pairs", ("3", "5", "7")[i % 3]),)
                attrs.append(("units_per_pack", "Units per pack", params[0][1], "C62"))
            if suit_params:
                params = suit_params
            facts = list(kind.facts)
            pattern = "check" if checked else "stripe" if detail == "Striped" else leaf.pattern
            if pattern != "plain":
                facts.append(("pattern", pattern))
            out.append(_row(f"{prefix}{leaf.abbr}{i:03d}", title, brand, kind, leaf.path, desc, colors,
                            tuple(attrs), price=price, params=params, facts=tuple(facts)))
    return out


# --------------------------------------------------------------------------
# Matching sets (gen#215): a jacket, trousers and waistcoat cut from one cloth.
# --------------------------------------------------------------------------

#: (set name, fabric, fit, brand, colors): one name is one cloth, so the three pieces of a set
#: share the name (the ``suit_set`` attribute), the fabric, the fit, the brand and the colors.
SETS = (
    ("Ashdown", "Wool Blend", "Slim", 0, ("Navy", "Charcoal", "Black")),
    ("Brindley", "Herringbone", "Regular", 1, ("Grey", "Navy", "White")),
    ("Carrow", "Birdseye", "Tailored", 2, ("Grey", "Charcoal", "Navy")),
    ("Dunmere", "Stretch", "Slim", 3, ("Black", "Charcoal", "Navy")),
    ("Elmstead", "Twill", "Regular", 4, ("Charcoal", "Grey", "Black")),
    ("Fenwick", "Flannel", "Tailored", 0, ("Charcoal", "Grey", "Black")),
    ("Garrowby", "Wool Blend", "Regular", 1, ("Stone", "Navy", "Grey")),
    ("Holloway", "Linen Blend", "Slim", 2, ("White", "Stone", "Grey")),
    ("Ingleby", "Tweed", "Regular", 3, ("Grey", "Charcoal", "Navy")),
    ("Kestrel", "Stretch", "Tailored", 4, ("Navy", "Black", "Charcoal")),
)  # fmt: skip
#: piece -> (kind, leaf path, the detail its params take, the title's noun)
_PIECES = (
    ("J", "Suit Jacket", ("Mens", "Suits & Tailoring", "Suit Jackets"), "Notch", "Suit Jacket"),
    ("T", "Suit Trousers", ("Mens", "Suits & Tailoring", "Suit Trousers"), "Regular", "Suit Trousers"),
    ("W", "Waistcoat", ("Mens", "Suits & Tailoring", "Waistcoats"), "Five Button", "Waistcoat"),
)  # fmt: skip


def _set_rows() -> list[LRow]:
    out: list[LRow] = []
    for n, (name, fabric, fit, b, colors) in enumerate(SETS):
        for code, ptype, path, detail, noun in _PIECES:
            kind = KINDS[ptype]
            attrs = [_a("fit", "Fit", fit), _a("material", "Material", _case(fabric)),
                     _a("suit_set", "Suit set", name)]  # fmt: skip
            extra, params = _suit(ptype, fit, detail, n)
            attrs += extra
            if ptype == "Suit Jacket":
                attrs.append(_a("sleeve_length", "Sleeve length", "Long"))
            desc = (f"{_np(fabric, noun)} cut to {_an(fit)} fit "
                    f"{_TAIL[ptype]}. Part of the {name} suit: the jacket, trousers and waistcoat "
                    f"match.")  # fmt: skip
            price = round(kind.base_price + 15.0 + 2.0 * (n % 5), 2)
            out.append(_row(f"MS{n}{code}", f"Mens {name} {fabric} {fit} Fit {noun}", _BRANDS[b],
                            kind, path, desc, tuple(_col(c) for c in colors), tuple(attrs),
                            price=price, params=params))  # fmt: skip
    return out


# --------------------------------------------------------------------------
# The decoys: seven classes, three per type each, every field true.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Decoy:
    """One decoy's table row: the doc is :data:`ROWS`'s, found by ``code``."""

    code: str
    ptype: str
    klass: int
    word: str  # the misleading word: a color, a noun, an audience word, a feature, a brand
    color: str  # the product's true main color
    query: str  # the shopper query its words match
    policy: str  # which kind of policy repairs it


_MAIN_WORDS = ("Red", "Blue", "Green", "Yellow", "Black", "White")
_TRUE = ("White", "Black", "Navy", "Grey", "Stone", "Khaki")
_FANCY = ("Moonbeam", "Candlelight", "Moss Lantern", "Morning Mist", "Sandcastle", "Soft Dune")
_SHADES = ("Ivory", "Cream", "Off White")
_MENS = "men's"
_AUDIENCE = ("Women's-Style Cut", "Boyfriend Fit", "Mini-Me Kids' Style")
_BRAND_TRUE = {"Black Curlew": "White", "Yellow Plover": "Navy", "Jacket Wren": "Grey"}
_BRAND_QUERY = {"Black Curlew": "black", "Yellow Plover": "yellow", "Jacket Wren": "jacket"}


def _decoys(kinds=None, tails=None, prefix: str = "MD") -> tuple[list[LRow], list[Decoy]]:
    """The decoys of ``kinds`` (this module's by default), coded ``<prefix><tag><class><n>``."""
    kinds, tails = kinds or KINDS, tails or _TAIL
    rows: list[LRow] = []
    table: list[Decoy] = []
    for k, (ptype, kind) in enumerate(kinds.items()):
        noun = kind.noun
        tag = "".join(w[0] for w in ptype.split()) + str(k)

        def add(klass, i, title, desc, true, word, query, policy="generic", kind=kind, tag=tag,
                ptype=ptype, material=None, extra=(), colors=None):  # noqa: PLR0913
            code = f"{prefix}{tag}{klass}{i}"
            brand = word if klass == 7 else _BRANDS[(i + klass) % len(_BRANDS)]
            attrs = ()
            if kind.fitted:
                attrs += (_a("fit", "Fit", "Regular"),)
            attrs += (_a("material", "Material", _case(material or kind.material)),)
            if kind.item:
                attrs += (_a("accessory_type", "Accessory type", kind.item),)
            attrs += extra + (kind.absent_attrs if klass == 4 else kind.decoy_attrs)
            if ptype == "Socks":
                attrs += (("units_per_pack", "Units per pack", "3", "C62"),)
            path = kind.path if klass == 4 or not kind.spread else kind.spread[
                (klass + i) % len(kind.spread)]
            if _SLEEVE.get(path):
                attrs += (_a("sleeve_length", "Sleeve length", _SLEEVE[path]),)
            if ptype == "Polo Shirt":
                attrs += (_a("collar", "Collar", "Polo"),)
            rows.append(_row(code, title, brand, kind, path, desc, colors or (_col(true),), attrs,
                             price=round(kind.base_price + 1.5 * i + klass, 2),
                             params=kind.params + (() if klass == 4 else kind.decoy_params)))
            table.append(Decoy(code, ptype, klass, word, true, query, policy))

        for i in range(3):
            w = _MAIN_WORDS[(2 * k + i) % 6]
            true = _TRUE[(k + i) % 6]
            if true == w:
                true = "Navy"
            # 1: a trim, a stripe or a print names the other color.
            # gen#447: the trim is a part the shape draws (a tie's is its stripes), never piping.
            if kind.shape == "formal_accessory":
                trim, colors = "Stripes", (cw(true, HEX[true], "stripe", DETAIL_HEX[w]),)
            else:
                trim, colors = named_parts.trim_part(ptype, kind.shape, i), None
            add(1, i, f"Mens {true} {noun} with {w} {trim}",
                f"{_np(true, noun)} {tails[ptype]}, finished with "
                f"{named_parts.with_part(w, trim)}.", true, w, f"{w.lower()} {noun.lower()}",
                colors=colors)  # fmt: skip
            # 2: another category's noun used as a modifier.
            b = kind.borrow[i]
            mod = {"shirt": "Shirt Collar", "blazer": "Blazer Style", "jumper": "Jumper Soft",
                   "dress": "Dress", "coat": "Coat Length", "trouser": "Trouser",
                   "sock": "Sock Soft", "boot": "Boot Cut", "boxer": "Boxer Print"}[b]
            add(2, i, f"Mens {mod} {noun}",
                f"{_np('', noun)} named for {'their' if _plural(noun) else 'its'} {b} detail; "
                f"{'they are' if _plural(noun) else 'it is'} not a {b}.",
                _TRUE[(k + i + 1) % 6], b, f"{b} {noun.lower()}")  # fmt: skip
            # 3: an audience word that names a sibling cut.
            a = _AUDIENCE[i]
            if a == "Mini-Me Kids' Style":  # a real listing says what it matches, not "Kids' Style"
                add(3, i, f"Mens Mini-Me {noun}, Kids' Version Sold Separately",
                    f"{_np(_MENS, noun)} with a matching kids' version, sold in men's sizes.",
                    _TRUE[(k + i + 2) % 6], "Mini-Me", f"mini-me {noun.lower()}")  # fmt: skip
            else:
                add(3, i, f"Mens {a} {noun}",
                    f"{_np(_MENS, noun)} in the {a.lower()}, sold in men's sizes.",
                    _TRUE[(k + i + 2) % 6], a, f"{a.split()[0].lower()} {noun.lower()}")  # fmt: skip
            # 4: a material or feature named, and absent.
            f = kind.absent[i]
            n4 = kind.absent_noun or noun
            add(4, i, f"Mens {f} {n4}",
                kind.absent_text.format(f=f.lower()) if kind.absent_text else
                f"{_np('', n4)} that {'are' if _plural(n4) else 'is'} {f.lower()}: made in "
                f"{kind.material.lower()}.", _TRUE[(k + i + 3) % 6], f,
                f"{f.split('-')[0].lower()} {noun.lower()}")  # fmt: skip
            # 5: the title gives a fancy name, the description the shade.
            s = _SHADES[i]
            add(5, i, f"Mens {_FANCY[(k + i) % 6]} {noun}",
                f"{_np('', noun)} in soft {s.lower()}, {tails[ptype]}.", s,
                _FANCY[(k + i) % 6], f"{s.lower()} {noun.lower()}")  # fmt: skip
            # 6: an incidental word in a short title: a range name.
            r, gloss, word = place_range(k + i * 2)
            true6 = _TRUE[(k + i + 4) % 6]
            add(6, i, f"Mens {r} {noun}",
                f"From the {r} range, named for {gloss}; the {noun.lower()} "
                f"{'themselves are' if _plural(noun) else 'itself is'} {true6.lower()}.",
                true6, word, word,
                extra=(_a("range", "Range", r),))  # fmt: skip
            # 7: an invented brand holding a color or category word.
            brand = NEW_BRANDS[i]
            add(7, i, f"Mens {brand} {noun}",
                f"{_np(_BRAND_TRUE[brand], noun)} from {brand}; the name is the "
                f"brand's, not the color.", _BRAND_TRUE[brand], brand,
                f"{_BRAND_QUERY[brand]} {noun.lower()}")  # fmt: skip
    return rows, table


_DECOY_ROWS, _TABLE = _decoys()
_FLOOR_ROWS = _floor_rows()
_SET_ROWS = _set_rows()
#: Every row this module authors (floor, matching sets, decoys): the view the tests read.
ROWS: tuple[LRow, ...] = (*_FLOOR_ROWS, *_SET_ROWS, *_DECOY_ROWS)
#: Every decoy, with its class, word, query and policy: the docs table is generated from it.
TABLE: tuple[Decoy, ...] = tuple(_TABLE)


#: The tailoring types registered through a spec file (``type_specs/<key>.py``, gen#351), not
#: here: their rows are generated by this module's tables (the floor leaves, the matching sets
#: and the decoy classes are combinatorial, so they are not written out row by row) and each
#: spec reads them back with :func:`spec_rows` and :func:`spec_decoys`. :func:`docs` leaves
#: them out, because the registry builds them.
SPEC_TYPES = ("Suit Trousers", "Waistcoat", "Dinner Suit", "Formal Accessories")


def spec_rows(ptype: str) -> tuple[LRow, ...]:
    """The floor and matching-set rows of one of :data:`SPEC_TYPES`, for its spec file."""
    assert ptype in SPEC_TYPES, ptype
    return tuple(r for r in (*_FLOOR_ROWS, *_SET_ROWS) if r.product_type == ptype)


def spec_decoys(ptype: str) -> tuple[type_registry.Decoy, ...]:
    """The decoys of one of :data:`SPEC_TYPES` as registry decoys, for its spec file."""
    assert ptype in SPEC_TYPES, ptype
    by_code = {r.code: r for r in _DECOY_ROWS}
    return tuple(
        type_registry.Decoy(d.klass, d.query, d.policy, by_code[d.code])
        for d in TABLE
        if d.ptype == ptype
    )


def docs() -> list[dict]:
    """The catalog document of every row this module still registers: floor rows, matching
    sets and decoys, less the :data:`SPEC_TYPES` that their spec files register."""
    return [r.doc() for r in ROWS if r.product_type not in SPEC_TYPES]


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: ``main_colors.complete`` leaves them as authored."""
    return frozenset(f"BRD-{d.code}" for d in TABLE)


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
