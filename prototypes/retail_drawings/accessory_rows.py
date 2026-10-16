"""Bag, umbrella and jewelry templates for the scaled retail catalog (gen#207): data only.

The catalog had earrings, a watch, a belt and a keyring in accessories and nothing for bags,
umbrellas or other jewelry, so a search for a handbag, a backpack, an umbrella or a necklace
found a make-up bag or nothing. Each type here is a leaf under ``Womens > Accessories``, with its
own drawing (:mod:`kit_accessories`), its shopper attributes as structured entries, and SKUs over
the color or metal and the type's own axis: a bag's size, a backpack's capacity, an umbrella's
canopy, a necklace's length, a bracelet's size, a ring's size.

A measured axis (``capacity_l``, ``canopy_cm``, ``length_cm``) is on the SKUs alone, which the
export states with its unit (``export.OPTIONS``). A jewelry SKU's metal is its color's metal
(:class:`ARow`): one gold plated style sells gold, silver and rose gold SKUs, each a metal
entry, and each drawn in its metal. A count the row states (pockets, card slots, ribs, layers,
charms, stacked bands) is the count its drawing shows. These styles are templates only:
:func:`scale.derivable` leaves them out, as it does the shirts and the household rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import audience
import kit_accessories  # noqa: F401 -- registers handbag, backpack, tote_bag, ...
from breadth_rows import OWNERS, Row
from variants import cw

for _brand, _owner in {"Marrowgate": "third_party", "Pellbrook": "third_party",
                       "Osier & Vane": "third_party", "Tallow Street": "third_party",
                       "Wrenfield": "own", "Harbour & Pine": "own"}.items():  # fmt: skip
    OWNERS.setdefault(_brand, _owner)

_CL = "Clothing"
_M, _P, _O, _T, _W, _H = ("Marrowgate", "Pellbrook", "Osier & Vane", "Tallow Street", "Wrenfield",
                          "Harbour & Pine")  # fmt: skip
#: A bag, purse or umbrella sits under ``Womens > Accessories`` (gen#248), one product in one place.
#: The path is the department, not the audience: a backpack, a tote and an umbrella are unisex, and
#: say so in ``facets.audience``, declared here the way every worn SKU has one (:mod:`audience`).
WOMENS, UNISEX = audience.WOMENS, audience.UNISEX
_BAGS = ("Womens", "Accessories", "Bags")
_JEW = ("Womens", "Jewellery")


@dataclass(frozen=True)
class ARow(Row):
    """A row whose SKUs carry more than a size: ``metals`` names each color's metal (jewelry),
    and ``extra`` maps a size to the other fields that SKU holds (a US ring size beside the UK
    letter)."""

    metals: tuple[str, ...] = ()
    extra: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = ()

    def skus(self) -> list[dict]:
        more = {s: dict(kv) for s, kv in self.extra}
        out = []
        for ci, color in enumerate(self.colors):
            for sku in super().skus():
                if sku.get("color") != color[0]:
                    continue
                if self.metals:
                    sku["metal"] = self.metals[ci]
                sku.update(more.get(sku.get(self.size_key, ""), {}))
                out.append(sku)
        return out


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _who(attrs: tuple, who: str) -> tuple:
    """``attrs`` plus the audience facet this row's SKUs carry."""
    return (*attrs, _a("audience", "Audience", who))


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    return (key, name, str(n), "C62")


def _inch(key: str, name: str, v: float) -> tuple[str, str, str, str, float]:
    """A length in inches: the canonical value is in millimetres, as the core's ``INH`` says."""
    return (key, name, f"{v:g}", "INH", float(Fraction(f"{v:g}") * Fraction(127, 5)))


def _sizes(*pairs: tuple[str, float]) -> tuple[tuple[str, float], ...]:
    return tuple(pairs)


def _num(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    return tuple((f"{v:g}", p) for v, p in pairs)


BLACK = cw("Black", "#2d2d33")
TAN = cw("Tan", "#b8864f")
NAVY = cw("Navy", "#26365c")
BURGUNDY = cw("Burgundy", "#6e2233")
CREAM = cw("Cream", "#efe6d2", "solid", "#b9b4a6")
PINK = cw("Pink", "#e8a5b5")
GREEN = cw("Green", "#4f7a3a")
RED = cw("Red", "#c8312e")
GREY = cw("Grey", "#9a9ca0")
KHAKI = cw("Khaki", "#a8a070")
BLUE = cw("Blue", "#3f6fb5")
TEAL = cw("Teal", "#1c7c7d")
CAMEL = cw("Camel", "#c19a62")
LILAC = cw("Lilac", "#b9a2d4")
NATURAL = cw("Natural", "#d8c8a0", "solid", "#8a7a52")
GOLD = cw("Gold", "#d4af37", "solid", "#8a6a22")
SILVER = cw("Silver", "#cfd5da", "solid", "#8f989f")
ROSE_GOLD = cw("Rose Gold", "#d8a28f", "solid", "#8a5a48")
STRIPE = cw("Navy Stripe", "#ffffff", "stripe", "#26365c")
RED_STRIPE = cw("Red Stripe", "#ffffff", "stripe", "#c8312e")
GINGHAM = cw("Blue Gingham", "#ffffff", "gingham", "#3f6fb5")
POLKA = cw("Pink Polka Dot", "#f6dfe6", "polka", "#c8312e")

# --------------------------------------------------------------------------
# Handbags: the style, the flap and the strap are drawn; the size is the SKU.
# --------------------------------------------------------------------------

_HB = (*_BAGS, "Handbags")


def _hb(material: str, closure: str, strap: str | None, style: str, *more: tuple) -> tuple:
    return (_a("bag_style", "Bag style", style), _a("material", "Material", material),
            _a("closure", "Closure", closure),
            *((_a("strap", "Strap", strap),) if strap else ()), *more)  # fmt: skip


def _hrow(code, title, brand, price, desc, colors, attrs, sizes, style, flap, strap="leather") -> ARow:  # fmt: skip
    return ARow(code, title, brand, _CL, _HB, "Handbag", price, "handbag", desc, colors, _who(attrs, WOMENS),
                sizes, params=(("style", style), ("flap", flap), ("strap", strap)))


#: A bag size is a letter size, as every other bag states it: "Mini" matches no size system the
#: Combined loader declares (gen#279), so the crossbody that is cut small sells Small and Medium.
_SMALL_MED_COMPACT = _sizes(("Small", 28.0), ("Medium", 34.0))
_SMALL_MED = _sizes(("Small", 30.0), ("Medium", 38.0))

HANDBAGS = (
    _hrow("HBGSHL", "Quilted Faux Leather Shoulder Bag", _M, 30.0,
          "A quilted shoulder bag in soft faux leather with a magnetic flap, a zipped inner "
          "pocket and an adjustable strap.",
          (BLACK, TAN, BURGUNDY),
          _hb("Faux Leather", "Magnetic", "Adjustable", "Shoulder", _a("finish", "Finish", "Quilted")),
          _SMALL_MED, "shoulder", "flap"),
    _hrow("HBGXBL", "Leather Crossbody Bag with Chain Strap", _P, 58.0,
          "A leather crossbody bag with a zip top and a metal chain strap that you can wear "
          "across the body or on the shoulder.",
          (BLACK, RED, CREAM),
          _hb("Leather", "Zip", "Chain", "Crossbody"), _SMALL_MED_COMPACT, "crossbody", "open", "chain"),
    _hrow("HBGXBC", "Canvas Crossbody Bag", _T, 24.0,
          "A hard-wearing canvas crossbody bag with a front flap, a zipped back pocket and an "
          "adjustable webbing strap.",
          (NAVY, GREEN, KHAKI),
          _hb("Canvas", "Flap", "Adjustable", "Crossbody"), _SMALL_MED, "crossbody", "flap",
          "adjustable"),
    _hrow("HBGTOP", "Structured Top Handle Bag", _O, 44.0,
          "A structured faux leather top handle bag with a magnetic flap, metal feet and a "
          "lined interior.",
          (BLACK, CAMEL, PINK),
          _hb("Faux Leather", "Magnetic", None, "Top Handle"),
          _sizes(("Small", 36.0), ("Medium", 44.0), ("Large", 52.0)), "top handle", "flap"),
    _hrow("HBGTHL", "Leather Top Handle Tote Bag", _P, 85.0,
          "A leather top handle bag with a zip top, a long inside pocket and a removable "
          "shoulder strap.",
          (BLACK, TAN),
          _hb("Leather", "Zip", "Adjustable", "Top Handle"),
          _sizes(("Medium", 85.0), ("Large", 98.0)), "top handle", "open"),
    _hrow("HBGCLT", "Satin Envelope Clutch Bag", _M, 22.0,
          "A satin envelope clutch with a magnetic flap, big enough for a phone and cards, for "
          "evenings and weddings.",
          (BLACK, GOLD, NAVY),
          _hb("Satin", "Magnetic", None, "Clutch"), (), "clutch", "flap"),
    _hrow("HBGCLZ", "Faux Leather Zip Clutch Bag", _W, 18.0,
          "A slim faux leather clutch with a zip top and a card slot, small enough for a phone, "
          "keys and a lipstick.",
          (BLACK, PINK, GREY),
          _hb("Faux Leather", "Zip", None, "Clutch"), (), "clutch", "open"),
    _hrow("HBGBKT", "Drawstring Bucket Bag", _T, 36.0,
          "A leather bucket bag with a drawstring top and an adjustable shoulder strap, roomy "
          "enough for a day out.",
          (TAN, BLACK, GREEN),
          _hb("Leather", "Drawstring", "Adjustable", "Bucket"), _SMALL_MED, "bucket", "open"),
    _hrow("HBGBKC", "Canvas Bucket Bag", _H, 26.0,
          "A canvas bucket bag with a drawstring closure and a shoulder strap, light to carry "
          "and easy to wash.",
          (CREAM, NAVY, TEAL),
          _hb("Canvas", "Drawstring", "Adjustable", "Bucket"), _SMALL_MED, "bucket", "open"),
)

# --------------------------------------------------------------------------
# Backpacks: the use and the front pockets are drawn; the capacity is the SKU.
# --------------------------------------------------------------------------

_BP = (*_BAGS, "Backpacks")


def _bp(use: str, material: str, pockets: int, waterproof: bool, laptop: float | None) -> tuple:
    return (_a("use", "Use", use), _a("material", "Material", material),
            _count("pocket_count", "Pocket count", pockets),
            _a("waterproof", "Waterproof", "Yes" if waterproof else "No"),
            *((_inch("laptop_size", "Laptop size", laptop),) if laptop else ()))  # fmt: skip


def _brow(code, title, brand, price, desc, colors, attrs, caps, use, pockets) -> ARow:  # fmt: skip
    return ARow(code, title, brand, _CL, _BP, "Backpack", price, "backpack", desc, colors, _who(attrs, UNISEX),
                caps, params=(("use", use), ("pockets", str(pockets))), size_key="capacity_l")


BACKPACKS = (
    _brow("BPKSCH", "Everyday School Backpack", _T, 22.0,
          "A padded school backpack with a roomy main compartment, a front pocket and a "
          "bottle pocket on each side. Easy to wipe clean.",
          (NAVY, RED, GREEN),
          _bp("School", "Polyester", 1, False, None), _num((16, 22.0), (22, 27.0)), "school", 1),
    _brow("BPKSTW", "Water-Resistant School Backpack", _H, 29.0,
          "A school backpack in a water-resistant fabric with two front pockets, padded "
          "straps and a reflective strip.",
          (BLACK, BLUE, PINK),
          _bp("School", "Nylon", 2, True, 13.3), _num((20, 29.0), (26, 34.0)), "school", 2),
    _brow("BPKLPT", "Padded Laptop Backpack", _P, 38.0,
          "A slim laptop backpack with a padded sleeve for a 15.6 inch laptop, a charging "
          "port and a hidden back pocket.",
          (BLACK, GREY, NAVY),
          _bp("Laptop", "Polyester", 2, True, 15.6), _num((18, 38.0), (24, 44.0)), "laptop", 2),
    _brow("BPKLPL", "Faux Leather Laptop Backpack", _O, 52.0,
          "A smart faux leather backpack for work, with a padded 14 inch laptop sleeve and "
          "a zipped front pocket.",
          (BLACK, TAN),
          _bp("Laptop", "Faux Leather", 1, False, 14.0), _num((14, 52.0), (20, 58.0)), "laptop", 1),
    _brow("BPKRUC", "Roll Top Rucksack", _M, 42.0,
          "A roll top rucksack in coated canvas with buckled straps and three front "
          "pockets for day trips and travel.",
          (KHAKI, BLACK, BURGUNDY),
          _bp("Rucksack", "Coated Canvas", 3, True, None), _num((20, 42.0), (28, 50.0)), "rucksack", 3),
    _brow("BPKTRV", "Travel Rucksack", _W, 48.0,
          "A large travel rucksack with a roll top, padded straps and a waterproof lining, big "
          "enough for a weekend away.",
          (GREEN, NAVY),
          _bp("Travel", "Nylon", 2, True, 15.0), _num((28, 48.0), (40, 62.0)), "rucksack", 2),
)

# --------------------------------------------------------------------------
# Tote bags: the gusset and the pocket are drawn; the colorway is the SKU.
# --------------------------------------------------------------------------

_TB = (*_BAGS, "Tote Bags")


def _tb(size: str, material: str, closure: str, pocket: bool, *more: tuple) -> tuple:
    return (_a("size", "Size", size), _a("material", "Material", material),
            _a("closure", "Closure", closure), _a("pocket", "Pocket", "Yes" if pocket else "No"),
            *more)  # fmt: skip


def _trow(code, title, brand, price, desc, colors, attrs, gusset, pocket) -> ARow:  # fmt: skip
    return ARow(code, title, brand, _CL, _TB, "Tote Bag", price, "tote_bag", desc, colors, _who(attrs, UNISEX),
                params=(("gusset", gusset), ("pocket", "yes" if pocket else "no")))


TOTES = (
    _trow("TTBCNV", "Canvas Shopper Tote Bag", _T, 9.0,
          "A sturdy cotton canvas tote with long handles and a wide base, strong enough for "
          "the weekly shop.",
          (NATURAL, NAVY, BLACK), _tb("Large", "Canvas", "Open", False), "wide", False),
    _trow("TTBPKT", "Canvas Tote Bag with Pocket", _H, 12.0,
          "A canvas tote with an outside patch pocket for your keys and a pocket inside.",
          (CREAM, GREEN), _tb("Medium", "Canvas", "Open", True), "standard", True),
    _trow("TTBJUT", "Natural Jute Tote Bag", _O, 14.0,
          "A woven jute tote with a cotton lining and a zip fastening, made for the beach "
          "and the market.",
          (NATURAL, BLACK), _tb("Large", "Jute", "Zip", False), "wide", False),
    _trow("TTBNYL", "Foldable Nylon Tote Bag", _W, 8.0,
          "A lightweight nylon tote that folds into a small pouch, for the bottom of a "
          "handbag.",
          (BLACK, BLUE, RED), _tb("Medium", "Nylon", "Open", False), "flat", False),
    _trow("TTBSTR", "Striped Cotton Tote Bag", _M, 10.0,
          "A printed cotton tote with a bold stripe, a flat base and a zip top.",
          (STRIPE, RED_STRIPE),
          _tb("Medium", "Cotton", "Zip", False, _a("pattern", "Pattern", "Striped")),
          "standard", False),
    _trow("TTBGNG", "Gingham Cotton Tote Bag", _P, 11.0,
          "A gingham cotton tote with a pocket on the front and long handles.",
          (GINGHAM,),
          _tb("Medium", "Cotton", "Open", True, _a("pattern", "Pattern", "Gingham")),
          "standard", True),
)

# --------------------------------------------------------------------------
# Purses: the type, the closure and the card slots are drawn.
# --------------------------------------------------------------------------

_PU = ("Womens", "Accessories", "Purses & Wallets", "Purses")


def _pu(kind: str, material: str, rfid: bool, closure: str, slots: int = 0) -> tuple:
    return (_a("purse_type", "Purse type", kind), _a("material", "Material", material),
            _a("rfid_blocking", "RFID blocking", "Yes" if rfid else "No"),
            _a("closure", "Closure", closure),
            *((_count("card_slots", "Card slots", slots),) if slots else ()))  # fmt: skip


def _prow(code, title, brand, price, desc, colors, attrs, kind, closure, slots=0) -> ARow:  # fmt: skip
    return ARow(code, title, brand, _CL, _PU, "Purse", price, "purse", desc, colors, _who(attrs, WOMENS),
                params=(("type", kind), ("closure", closure), ("slots", str(slots))))


PURSES = (
    _prow("PRSCOI", "Leather Coin Purse", _P, 9.0,
          "A small leather coin purse with a zip top, a keyring loop and room for notes and a "
          "few cards.",
          (BLACK, TAN, RED), _pu("Coin Purse", "Leather", False, "Zip"), "coin", "zip"),
    _prow("PRSCOF", "Faux Leather Clasp Coin Purse", _W, 7.0,
          "A faux leather coin purse with a metal clasp that snaps shut, small enough for a "
          "pocket.",
          (PINK, BURGUNDY, NAVY), _pu("Coin Purse", "Faux Leather", False, "Clasp"), "coin",
          "clasp"),
    _prow("PRSCRD", "RFID Blocking Card Holder", _H, 12.0,
          "A slim card holder with four card slots and RFID blocking lining, small enough "
          "for a back pocket.",
          (BLACK, NAVY, GREY), _pu("Card Holder", "Faux Leather", True, "Open", 4), "card",
          "zip", 4),
    _prow("PRSCRL", "Leather Card Holder", _O, 16.0,
          "A leather card holder with six card slots and a middle pocket for notes.",
          (TAN, BLACK), _pu("Card Holder", "Leather", False, "Open", 6), "card", "zip", 6),
    _prow("PRSZIP", "Zip Around Purse", _M, 19.0,
          "A long zip around purse with a card section, a coin pocket and a note compartment.",
          (RED, BLACK, TEAL), _pu("Zip Around Wallet", "Faux Leather", False, "Zip", 6), "wallet",
          "zip", 6),
    _prow("PRSRFD", "RFID Zip Around Purse", _T, 28.0,
          "A leather zip around purse lined with RFID blocking fabric, with five card slots and "
          "a zipped coin pocket.",
          (BLACK, BURGUNDY, CAMEL), _pu("Zip Around Wallet", "Leather", True, "Zip", 5), "wallet",
          "zip", 5),
    _prow("PRSFLP", "Flap Over Purse", _H, 15.0,
          "A long purse with a clasp flap, three card slots, a coin pocket and a note "
          "compartment.",
          (PINK, NAVY, GREEN), _pu("Wallet", "Faux Leather", False, "Clasp", 3), "wallet", "clasp",
          3),
)

# --------------------------------------------------------------------------
# Umbrellas: the state, the handle and the ribs are drawn; the canopy is the SKU.
# --------------------------------------------------------------------------

_UM = ("Womens", "Accessories", "Umbrellas")


def _um(kind: str, auto: bool, windproof: bool, uv: bool, ribs: int, *more: tuple) -> tuple:
    return (_a("umbrella_type", "Umbrella type", kind),
            _a("automatic_open", "Automatic open", "Yes" if auto else "No"),
            _a("windproof", "Windproof", "Yes" if windproof else "No"),
            _a("uv_protection", "UV protection", "Yes" if uv else "No"),
            _count("ribs", "Ribs", ribs), *more)  # fmt: skip


def _urow(code, title, brand, price, desc, colors, attrs, canopy, state, handle, ribs) -> ARow:  # fmt: skip
    return ARow(code, title, brand, _CL, _UM, "Umbrella", price, "umbrella", desc, colors, _who(attrs, UNISEX),
                canopy, params=(("state", state), ("handle", handle), ("ribs", str(ribs))),
                size_key="canopy_cm")


UMBRELLAS = (
    _urow("UMBCMP", "Automatic Compact Umbrella", _T, 14.0,
          "A compact folding umbrella that opens and closes at the press of a button, with a "
          "vented windproof canopy.",
          (BLACK, NAVY, RED, PINK), _um("Compact", True, True, False, 8),
          _num((95, 14.0), (105, 16.0)), "closed", "straight", 8),
    _urow("UMBTEL", "Telescopic Umbrella with UV Protection", _H, 18.0,
          "A telescopic umbrella that folds to fit a handbag, with a coating that blocks UV "
          "rays and shades you from the sun.",
          (GREEN, LILAC, BLUE), _um("Telescopic", False, False, True, 8), _num((98, 18.0),),
          "closed", "straight", 8),
    _urow("UMBGLF", "Windproof Golf Umbrella", _O, 32.0,
          "A large golf umbrella with a double canopy and a fiberglass frame that flexes in "
          "the wind.",
          (BLACK, NAVY, GREEN, BURGUNDY), _um("Golf", True, True, False, 16),
          _num((125, 32.0), (135, 36.0)), "open", "straight", 16),
    _urow("UMBSTK", "Classic Stick Umbrella", _P, 26.0,
          "A classic stick umbrella with a hook handle and a wide canopy, for walks in "
          "the rain.",
          (BLACK, NAVY, TAN), _um("Stick", False, False, False, 8),
          _num((100, 26.0), (110, 29.0)), "open", "curved", 8),
    _urow("UMBPOL", "Polka Dot Stick Umbrella", _M, 22.0,
          "A stick umbrella with a polka dot canopy, a curved handle and an automatic open "
          "button.",
          (POLKA, cw("Navy Polka Dot", "#26365c", "polka", "#ffffff")),
          _um("Stick", True, False, False, 8, _a("pattern", "Pattern", "Polka Dot")),
          _num((95, 22.0),), "open", "curved", 8),
    _urow("UMBSTR", "Striped Windproof Stick Umbrella", _W, 24.0,
          "A striped stick umbrella with a vented canopy and sixteen ribs that hold in a "
          "gale.",
          (STRIPE, RED_STRIPE), _um("Stick", False, True, False, 16, _a("pattern", "Pattern", "Striped")),
          _num((105, 24.0),), "open", "curved", 16),
)

# --------------------------------------------------------------------------
# Jewelry: the type is drawn in the metal; the metal and the length or size are the SKUs.
# --------------------------------------------------------------------------

_METALS = {"Gold": "Gold Plated", "Silver": "Sterling Silver", "Rose Gold": "Rose Gold Plated"}
_STEEL = {"Gold": "Gold Plated Stainless Steel", "Silver": "Stainless Steel",
          "Rose Gold": "Rose Gold Plated Stainless Steel"}  # fmt: skip
_MT = (GOLD, SILVER, ROSE_GOLD)


def _j(metals: dict[str, str], colors: tuple, kind_attr: tuple, *more: tuple) -> tuple:
    """The attributes of a jewelry style: its type, then one ``metal`` entry per metal sold."""
    return (kind_attr, *(_a("metal", "Metal", metals[c[0]]) for c in colors), *more)


def _stone(v: str) -> tuple:
    return (_a("stone", "Stone", v),)


def _jrow(code, title, brand, price, desc, colors, metals, attrs, leaf, ptype, shape, params,
          sizes=(), size_key="size", extra=()) -> ARow:  # fmt: skip
    return ARow(code, title, brand, _CL, (*_JEW, leaf), ptype, price, shape, desc, colors, attrs,
                sizes, params=params, size_key=size_key, metals=tuple(metals[c[0]] for c in colors),
                extra=extra)  # fmt: skip


_LEN = {"pendant": _num((40, 16.0), (45, 18.0)), "chain": _num((45, 14.0), (50, 16.0), (55, 18.0)),
        "choker": _num((33, 12.0), (36, 13.0)), "layered": _num((40, 22.0), (45, 24.0))}  # fmt: skip

NECKLACES = (
    _jrow("NCKPND", "Teardrop Pendant Necklace", _P, 16.0,
          "A fine chain necklace with a polished teardrop pendant and a lobster clasp with a "
          "five centimeter extender.",
          _MT, _METALS, _j(_METALS, _MT, _a("necklace_type", "Necklace type", "Pendant")),
          "Necklaces", "Necklace", "necklace", (("kind", "pendant"),), _LEN["pendant"],
          "length_cm"),
    _jrow("NCKRBY", "Ruby Pendant Necklace", _O, 26.0,
          "A pendant necklace with a faceted ruby set in a round bezel, on a fine belcher "
          "chain. Ruby is the birthstone for July.",
          (GOLD, SILVER), _METALS,
          _j(_METALS, (GOLD, SILVER), _a("necklace_type", "Necklace type", "Pendant"),
             *_stone("Ruby"), _a("birthstone", "Birthstone", "July")),
          "Necklaces", "Necklace", "necklace", (("kind", "pendant"), ("stone", "ruby")),
          _LEN["pendant"], "length_cm"),
    _jrow("NCKSPH", "Sapphire Pendant Necklace", _M, 28.0,
          "A pendant necklace with a faceted sapphire set in a round bezel, on a fine chain. "
          "Sapphire is the birthstone for September.",
          (SILVER, ROSE_GOLD), _METALS,
          _j(_METALS, (SILVER, ROSE_GOLD), _a("necklace_type", "Necklace type", "Pendant"),
             *_stone("Sapphire"), _a("birthstone", "Birthstone", "September")),
          "Necklaces", "Necklace", "necklace", (("kind", "pendant"), ("stone", "sapphire")),
          _LEN["pendant"], "length_cm"),
    _jrow("NCKCHN", "Stainless Steel Chain Necklace", _T, 14.0,
          "A classic stainless steel chain with a lobster clasp, plain enough to wear alone or "
          "to hang a pendant from.",
          (GOLD, SILVER), _STEEL,
          _j(_STEEL, (GOLD, SILVER), _a("necklace_type", "Necklace type", "Chain")),
          "Necklaces", "Necklace", "necklace", (("kind", "chain"),), _LEN["chain"], "length_cm"),
    _jrow("NCKCHK", "Choker Necklace", _W, 11.0,
          "A short choker with a flat woven band and a small round charm, with an adjustable "
          "clasp that sits close to the neck.",
          _MT, _METALS, _j(_METALS, _MT, _a("necklace_type", "Necklace type", "Choker")),
          "Necklaces", "Necklace", "necklace", (("kind", "choker"),), _LEN["choker"], "length_cm"),
    _jrow("NCKLYR", "Layered Chain Necklace", _H, 21.0,
          "Three fine chains of different lengths on one clasp, for the layered look without "
          "the tangle.",
          (GOLD, SILVER), _METALS,
          _j(_METALS, (GOLD, SILVER), _a("necklace_type", "Necklace type", "Layered"),
             _count("layers", "Layers", 3)),
          "Necklaces", "Necklace", "necklace", (("kind", "layered"), ("layers", "3")),
          _LEN["layered"], "length_cm"),
    _jrow("NCKLY2", "Double Layered Pendant Necklace", _M, 19.0,
          "Two chains of different lengths on one clasp, the shorter plain and the longer "
          "hung with a small charm.",
          (GOLD, ROSE_GOLD), _METALS,
          _j(_METALS, (GOLD, ROSE_GOLD), _a("necklace_type", "Necklace type", "Layered"),
             _count("layers", "Layers", 2)),
          "Necklaces", "Necklace", "necklace", (("kind", "layered"), ("layers", "2")),
          _LEN["layered"], "length_cm"),
)

_BS = _sizes(("Small", 12.0), ("Medium", 12.0), ("Large", 13.0))


def _bk(kind: str) -> tuple:
    return _a("bracelet_type", "Bracelet type", kind)


BRACELETS = (
    _jrow("BRCBNG", "Plain Bangle Bracelet", _P, 12.0,
          "A smooth round bangle in a polished finish, slim enough to stack with others.",
          _MT, _METALS, _j(_METALS, _MT, _bk("Bangle")), "Bracelets", "Bracelet", "bracelet",
          (("kind", "bangle"),), _BS),
    _jrow("BRCSTN", "Crystal Bangle Bracelet", _O, 18.0,
          "A polished bangle with a single clear crystal set at the front.",
          (GOLD, SILVER), _METALS,
          _j(_METALS, (GOLD, SILVER), _bk("Bangle"), *_stone("Clear Crystal")), "Bracelets",
          "Bracelet", "bracelet", (("kind", "bangle"), ("stone", "clear crystal")), _BS),
    _jrow("BRCCUF", "Open Cuff Bracelet", _M, 14.0,
          "A wide open cuff with a smooth finish that you slip over the wrist and press to fit.",
          (GOLD, SILVER, ROSE_GOLD), _METALS, _j(_METALS, _MT, _bk("Cuff")), "Bracelets",
          "Bracelet", "bracelet", (("kind", "cuff"),), _sizes(("Small", 14.0), ("Large", 15.0))),
    _jrow("BRCCHN", "Stainless Steel Chain Bracelet", _T, 11.0,
          "A fine stainless steel chain bracelet with a lobster clasp, plain or worn with a "
          "charm.",
          (GOLD, SILVER), _STEEL, _j(_STEEL, (GOLD, SILVER), _bk("Chain")), "Bracelets",
          "Bracelet", "bracelet", (("kind", "chain"),), _BS),
    _jrow("BRCCHM", "Charm Bracelet with Hearts and Stars", _W, 20.0,
          "A bracelet on a fine link band hung with four charms, hearts, stars and a round "
          "bead, on a lobster clasp.",
          (GOLD, SILVER), _METALS,
          _j(_METALS, (GOLD, SILVER), _bk("Charm"), _count("charms", "Charms", 4)), "Bracelets",
          "Bracelet", "bracelet", (("kind", "charm"), ("charms", "4")), _BS),
    _jrow("BRCBDD", "Beaded Stretch Bracelet", _H, 9.0,
          "A stretch bracelet of polished metal beads that slips on over the hand, with no "
          "clasp to fiddle with.",
          (GOLD, SILVER, ROSE_GOLD), _METALS, _j(_METALS, _MT, _bk("Beaded")), "Bracelets",
          "Bracelet", "bracelet", (("kind", "beaded"),), _sizes(("Small", 9.0), ("Large", 10.0))),
)

#: UK ring size (a letter) -> US size, as the two are sold side by side. Their keys are
#: ``ring_size_uk`` and ``ring_size_us``, never the garment and footwear ``size_uk``/``size_us``
#: (gen#249).
_US = {"J": "5", "L": "6", "N": "7", "P": "8", "R": "9"}


def _rs(*letters: str, base: float) -> tuple[tuple[str, float], ...]:
    return tuple((s, base) for s in letters)


def _rx(*letters: str) -> tuple:
    return tuple((s, (("ring_size_us", _US[s]),)) for s in letters)


def _rk(kind: str) -> tuple:
    return _a("ring_type", "Ring type", kind)


_L4 = ("J", "L", "N", "P")

RINGS = (
    _jrow("RNGBND", "Plain Band Ring", _P, 10.0,
          "A slim polished band, comfortable enough to wear every day.",
          _MT, _METALS, _j(_METALS, _MT, _rk("Band")), "Rings", "Ring", "ring",
          (("kind", "band"),), _rs(*_L4, base=10.0), "ring_size_uk", _rx(*_L4)),
    _jrow("RNGSGN", "Oval Signet Ring", _O, 18.0,
          "A classic oval signet ring with a flat polished face, worn on the little finger.",
          (GOLD, SILVER), _METALS, _j(_METALS, (GOLD, SILVER), _rk("Signet")), "Rings", "Ring",
          "ring", (("kind", "signet"),), _rs("L", "N", "P", "R", base=18.0), "ring_size_uk",
          _rx("L", "N", "P", "R")),
    _jrow("RNGSTK", "Set of Three Stacking Rings", _M, 15.0,
          "Three slim rings to wear together or apart, with a polished finish.",
          (GOLD, SILVER, ROSE_GOLD), _METALS,
          _j(_METALS, _MT, _rk("Stacking"), _count("piece_count", "Piece count", 3)), "Rings",
          "Ring", "ring", (("kind", "stacking"), ("pieces", "3")), _rs(*_L4, base=15.0),
          "ring_size_uk", _rx(*_L4)),
    _jrow("RNGSOL", "Solitaire Cubic Zirconia Ring", _T, 20.0,
          "A solitaire ring with one cubic zirconia in a four prong setting on a slim band.",
          (GOLD, SILVER), _METALS,
          _j(_METALS, (GOLD, SILVER), _rk("Solitaire"), *_stone("Cubic Zirconia")), "Rings",
          "Ring", "ring", (("kind", "stone"), ("stone", "cubic zirconia")),
          _rs("J", "L", "N", "P", "R", base=20.0), "ring_size_uk", _rx("J", "L", "N", "P", "R")),
    _jrow("RNGEMD", "Emerald Solitaire Ring", _H, 32.0,
          "A solitaire ring with a faceted emerald in a four prong setting. Emerald is the "
          "birthstone for May.",
          (GOLD, SILVER), _METALS,
          _j(_METALS, (GOLD, SILVER), _rk("Solitaire"), *_stone("Emerald"),
             _a("birthstone", "Birthstone", "May")), "Rings", "Ring", "ring",
          (("kind", "stone"), ("stone", "emerald")), _rs(*_L4, base=32.0), "ring_size_uk",
          _rx(*_L4)),
    _jrow("RNGSTM", "Sapphire Halo Statement Ring", _W, 36.0,
          "A statement ring with a large sapphire ringed by small clear stones, for evenings "
          "and weddings.",
          (SILVER, ROSE_GOLD), _METALS,
          _j(_METALS, (SILVER, ROSE_GOLD), _rk("Statement"), *_stone("Sapphire")), "Rings",
          "Ring", "ring", (("kind", "statement"), ("stone", "sapphire")),
          _rs("L", "N", "P", "R", base=36.0), "ring_size_uk", _rx("L", "N", "P", "R")),
)

ROWS = (*HANDBAGS, *BACKPACKS, *TOTES, *PURSES, *UMBRELLAS, *NECKLACES, *BRACELETS, *RINGS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
