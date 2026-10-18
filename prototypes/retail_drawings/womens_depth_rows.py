"""Womens clothing depth (gen#310, the Womens slice): data only.

The Womens tree held 117 dresses over eight leaves, 41 blouses and shirts, 56 coats and jackets,
43 skirts and no camisoles, vest tops, tunics, wool coats, trench coats or rain macs, so a query
for "midi dress" or "womens trench" had little to choose between. This module adds, as distinct
products (a product is a style; its colors times its sizes are its SKUs):

=============================  =====================================================  =====
group                          leaves added to                                        floor
=============================  =====================================================  =====
dresses                        Womens/Dresses: Midi, Mini, Slip, T-Shirt, Jumper,      200
                               Shift, Bodycon, Occasion
blouses and shirts             Womens/Shirts & Blouses; Womens/Tops/Shirts: Linen,      80
                               Oxford, Denim, Flannel
coats and jackets              Womens/Coats & Jackets: Wool Coats, Trench Coats,        80
                               Rain Macs, Blazers
skirts                         Womens/Skirts                                            80
tops                           Womens/Tops: Camisoles, Vest Tops, Tunics                80
=============================  =====================================================  =====

Nightwear and lingerie beyond bras (about 140) and school uniform (about 100) already meet their
floors; the Kids dresses and coats are a later slice. Every product carries its fit, material
and, where it applies, neckline and sleeve length, with a title a shop would use ("Womens Pure
Linen Relaxed Fit Midi Dress").

The text-match decoys (gen#294) of these types are the apparel plan's (:mod:`decoy_apparel`,
gen#311): Dress, Blouse, Shirt, Coat, Skirt and Top each carry three per class, cloned from a
real style of the type, so none is written here.

The rows are templates only: :func:`scale.derivable` leaves them out (``scale.WOMENS_DEPTH_IDS``),
so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import zlib
from dataclasses import dataclass
from itertools import product as _product

import kit_suits  # noqa: F401 -- registers suit_jacket
from breadth_rows import OWNERS
from class_model import BRAND_OWNER
from lowerbody_rows import ADULT, LRow
from main_color_hex import MAIN_COLORS
from variants import cw

_BRANDS = ("Harbour & Pine", "Larkmoor", "Wrenfield", "Calderby & Lune", "Bramblewood")
OWNERS.update({b: BRAND_OWNER[b] for b in _BRANDS})

_C = "Clothing"
HEX = {
    **MAIN_COLORS, "Navy": "#26365c", "Charcoal": "#4a4a50", "Stone": "#bdb5a6", "Grey": "#9a9a9a",
    "Camel": "#b5835a", "Burgundy": "#6d1f2f", "Cream": "#efe4cf", "Pink": "#e7a9b8",
    "Olive": "#6b6b2f", "Brown": "#6b4a32", "Lilac": "#b9a6d4", "Teal": "#1c7c7d",
}  # fmt: skip
_PALETTE = ("Navy", "Black", "Red", "Cream", "Green", "Pink", "Blue", "White", "Camel", "Burgundy",
            "Yellow", "Olive", "Lilac", "Teal", "Charcoal", "Stone")  # fmt: skip
_TAILORED = ("Navy", "Black", "Camel", "Charcoal", "Stone", "Burgundy", "Olive", "Cream", "Red",
             "Green", "Blue", "White", "Yellow")  # fmt: skip

#: neckline word -> (the neckline fact, the drawing's neckline) for the top shape.
NECKS = {
    "V Neck": ("v-neck", "v_neck"), "Square Neck": ("square", "square"),
    "Boat Neck": ("boat", "boat"), "Crew Neck": ("crew", "crew"),
    "Scoop Neck": ("scoop", "scoop"), "High Neck": ("high", "roll_neck"),
    "Collar": ("collared", "crew"),
}  # fmt: skip
#: sleeve word -> (the sleeve_length attribute, the drawing's sleeve).
SLEEVES = {
    "Long Sleeve": ("Long", "long"), "Short Sleeve": ("Short", "short"),
    "Three Quarter Sleeve": ("Three Quarter", "three_quarter"), "Sleeveless": ("Sleeveless", "sleeveless"),
}  # fmt: skip
_SKIRT_SHAPES = {"A-Line": "a_line", "Pleated": "pleated", "Pencil": "pencil", "Wrap": "wrap", "Tiered": "tiered"}


def _col(name: str):
    return cw(name, HEX[name])


def _colors(i: int, palette: tuple[str, ...]):
    n = len(palette)
    picks = [palette[(2 * i) % n], palette[(2 * i + 1) % n]]
    if i % 3 == 0:
        picks.append(palette[(5 * i + 3) % n])
    return tuple(_col(c) for c in dict.fromkeys(picks))


def _choose(combos: list[tuple], n: int) -> list[tuple]:
    """``n`` of the combinations, spread by a digest of each so no one kind takes the first n."""
    return sorted(combos, key=lambda c: zlib.crc32("|".join(map(str, c)).encode()))[:n]


def _an(phrase: str) -> str:
    word = phrase.lower()
    return f"{'an' if word[:1] in 'aeiou' else 'a'} {word}"


@dataclass(frozen=True)
class Kind:
    """What a product type is: how it is drawn and sold."""

    ptype: str
    noun: str
    shape: str
    base_price: float
    tail: str  # the description's last words


KINDS = {
    "Dress": Kind("Dress", "Dress", "dress", 28.0, "and a fitted waist"),
    "Blouse": Kind("Blouse", "Blouse", "blouse", 22.0, "and a button front"),
    "Shirt": Kind("Shirt", "Shirt", "blouse", 24.0, "and a button front with a chest pocket"),
    "Coat": Kind("Coat", "Coat", "coat", 70.0, "and a full lining"),
    "Suit Jacket": Kind("Suit Jacket", "Blazer", "suit_jacket", 55.0, "and a button fastening"),
    "Skirt": Kind("Skirt", "Skirt", "skirt", 22.0, "and a concealed zip"),
    "Top": Kind("Top", "Top", "top", 12.0, "in a soft, stretchy fabric"),
}


@dataclass(frozen=True)
class Leaf:
    abbr: str
    path: tuple[str, ...]
    kind: str
    n: int
    fabrics: tuple[str, ...]
    fits: tuple[str, ...]
    necks: tuple[str, ...]  # keys of NECKS ("" for none)
    sleeves: tuple[str, ...]  # keys of SLEEVES
    title: str  # "{f} {fit} {neck} {s} <noun>": the title's pattern
    palette: tuple[str, ...] = _PALETTE
    extra_price: float = 0.0
    styles: tuple[str, ...] = ("",)  # skirt shapes, or a title word each


_D = ("Womens", "Dresses")
_KNIT = ("Chunky Knit", "Ribbed Knit", "Cable Knit", "Merino Blend", "Soft Touch Knit", "Waffle Knit")
_LEAVES = (
    Leaf("MD", _D + ("Midi Dresses",), "Dress", 10,
         ("Pure Linen", "Crepe", "Satin", "Stretch Jersey", "Cotton Poplin", "Viscose", "Chiffon"),
         ("Regular", "Relaxed"), ("V Neck", "Square Neck", "Boat Neck", "Crew Neck"),
         ("Long Sleeve", "Short Sleeve", "Sleeveless"), "{f} {fit} Fit {neck} {s} Midi Dress"),
    Leaf("MX", _D + ("Maxi Dresses",), "Dress", 8,
         ("Pure Linen", "Cotton Poplin", "Viscose", "Chiffon", "Stretch Jersey", "Satin"),
         ("Regular", "Relaxed"), ("V Neck", "Square Neck", "Crew Neck", "Boat Neck"),
         ("Short Sleeve", "Sleeveless", "Long Sleeve"), "{f} {fit} Fit {neck} {s} Maxi Dress"),
    Leaf("MN", _D + ("Mini Dresses",), "Dress", 14,
         ("Cotton Poplin", "Stretch Jersey", "Denim", "Satin", "Crepe", "Corduroy", "Broderie"),
         ("Regular", "Fitted"), ("Square Neck", "V Neck", "Scoop Neck", "Crew Neck"),
         ("Short Sleeve", "Sleeveless", "Long Sleeve"), "{f} {fit} Fit {neck} {s} Mini Dress"),
    Leaf("SL", _D + ("Slip Dresses",), "Dress", 10,
         ("Satin", "Silk Blend", "Crepe", "Jersey", "Lace Trim Satin", "Viscose"),
         ("Regular", "Relaxed", "Fitted"), ("V Neck", "Scoop Neck", "Square Neck"),
         ("Sleeveless",), "{f} {fit} Fit {neck} Slip Dress"),
    Leaf("TS", _D + ("T-Shirt Dresses",), "Dress", 8,
         ("Organic Cotton", "Cotton Jersey", "Slub Cotton", "Stretch Jersey", "Modal"),
         ("Relaxed", "Regular", "Oversized"), ("Crew Neck",), ("Short Sleeve", "Long Sleeve"),
         "{f} {fit} Fit {s} T-Shirt Dress"),
    Leaf("JD", _D + ("Jumper Dresses",), "Dress", 12, _KNIT, ("Regular", "Relaxed", "Fitted"),
         ("Crew Neck", "High Neck", "V Neck", "Boat Neck"), ("Long Sleeve", "Three Quarter Sleeve"),
         "{f} {fit} Fit {neck} {s} Jumper Dress", extra_price=10.0),
    Leaf("SH", _D + ("Shift Dresses",), "Dress", 14,
         ("Crepe", "Ponte", "Textured Cotton", "Tweed Look", "Stretch Cotton", "Jacquard"),
         ("Regular", "Straight"), ("Boat Neck", "Scoop Neck", "Square Neck", "Crew Neck"),
         ("Short Sleeve", "Sleeveless", "Three Quarter Sleeve"),
         "{f} {fit} Fit {neck} {s} Shift Dress", palette=_TAILORED, extra_price=6.0),
    Leaf("BC", _D + ("Bodycon Dresses",), "Dress", 12,
         ("Ribbed Jersey", "Stretch Crepe", "Scuba", "Seamless Knit", "Ruched Jersey", "Satin"),
         ("Fitted",), ("Square Neck", "Scoop Neck", "V Neck", "High Neck"),
         ("Sleeveless", "Long Sleeve", "Short Sleeve"), "{f} {neck} {s} Bodycon Dress"),
    Leaf("OC", _D + ("Occasion Dresses",), "Dress", 20,
         ("Satin", "Velvet", "Sequin", "Lace", "Chiffon", "Taffeta", "Stretch Crepe", "Organza"),
         ("Regular", "Fitted", "Relaxed"), ("V Neck", "Square Neck", "High Neck", "Boat Neck"),
         ("Sleeveless", "Long Sleeve", "Three Quarter Sleeve"), "{f} {fit} Fit {neck} {s} Occasion Dress",
         palette=("Black", "Red", "Navy", "Green", "Burgundy", "White", "Blue", "Yellow", "Cream",
                  "Pink", "Lilac"), extra_price=22.0),
    Leaf("BL", ("Womens", "Shirts & Blouses", "Blouses"), "Blouse", 30,
         ("Crepe", "Satin", "Chiffon", "Cotton Poplin", "Viscose", "Georgette", "Linen Blend", "Silk Blend"),
         ("Regular", "Relaxed"), ("V Neck", "Collar", "Square Neck", "High Neck", "Boat Neck"),
         ("Long Sleeve", "Short Sleeve", "Three Quarter Sleeve"), "{f} {fit} Fit {neck} {s} Blouse"),
    Leaf("SLN", ("Womens", "Tops", "Shirts", "Linen Shirts"), "Shirt", 8,
         ("Pure Linen", "Linen Blend", "Washed Linen", "Linen Cotton"), ("Relaxed", "Regular", "Oversized"),
         ("Collar",), ("Long Sleeve", "Short Sleeve"), "{f} {fit} Fit {s} Shirt"),
    Leaf("SOX", ("Womens", "Tops", "Shirts", "Oxford Shirts"), "Shirt", 8,
         ("Washed Oxford", "Pinpoint Oxford", "Stretch Oxford", "Brushed Oxford", "Garment Dyed Oxford"),
         ("Relaxed", "Regular", "Fitted"), ("Collar",), ("Long Sleeve", "Short Sleeve"), "{f} {fit} Fit {s} Shirt"),
    Leaf("SDN", ("Womens", "Tops", "Shirts", "Denim Shirts"), "Shirt", 8,
         ("Light Wash Denim", "Stretch Denim", "Chambray", "Washed Denim", "Soft Denim"),
         ("Oversized", "Regular", "Relaxed"), ("Collar",), ("Long Sleeve", "Short Sleeve"), "{f} {fit} Fit {s} Shirt"),
    Leaf("SFL", ("Womens", "Tops", "Shirts", "Flannel Shirts"), "Shirt", 8,
         ("Brushed Cotton Flannel", "Soft Flannel", "Cotton Flannel", "Heavyweight Flannel"),
         ("Oversized", "Regular", "Relaxed"), ("Collar",), ("Long Sleeve",), "{f} {fit} Fit {s} Shirt"),
    Leaf("CW", ("Womens", "Coats & Jackets", "Wool Coats"), "Coat", 14,
         ("Wool Blend", "Pure Wool", "Wool Cashmere Blend", "Boucle", "Herringbone", "Felted Wool"),
         ("Regular", "Relaxed", "Oversized"), ("",), ("Long Sleeve",), "{f} {fit} Fit Wool Coat",
         palette=_TAILORED, extra_price=60.0),
    Leaf("CT", ("Womens", "Coats & Jackets", "Trench Coats"), "Coat", 14,
         ("Cotton Gabardine", "Water Repellent Cotton", "Cotton Twill", "Stretch Cotton", "Lightweight Cotton"),
         ("Regular", "Relaxed", "Belted"), ("",), ("Long Sleeve",), "{f} {fit} Fit Trench Coat",
         palette=("Camel", "Stone", "Navy", "Black", "Olive", "Cream", "Red", "Green", "Yellow", "Blue"),
         extra_price=40.0),
    Leaf("CR", ("Womens", "Coats & Jackets", "Rain Macs"), "Coat", 12,
         ("Waterproof Nylon", "Recycled Polyester", "Coated Cotton", "Taped Seam Nylon", "Ripstop", "Matte Nylon"),
         ("Regular", "Relaxed"), ("",), ("Long Sleeve",), "{f} {fit} Fit Hooded Rain Mac",
         palette=("Yellow", "Navy", "Red", "Green", "Black", "Blue", "White", "Pink", "Olive"), extra_price=20.0),
    Leaf("CB", ("Womens", "Coats & Jackets", "Blazers"), "Suit Jacket", 10,
         ("Crepe", "Stretch Suiting", "Linen Blend", "Textured Weave", "Wool Blend", "Tweed Look"),
         ("Regular", "Tailored", "Slim"), ("",), ("Long Sleeve",), "{f} {fit} Fit Blazer",
         palette=_TAILORED, extra_price=10.0),
    Leaf("SK", ("Womens", "Skirts"), "Skirt", 50,
         ("Cotton", "Satin", "Denim", "Faux Leather", "Linen", "Velvet", "Corduroy", "Jersey"),
         ("Regular", "Relaxed"), ("",), ("",), "{f} {st} {fit} Fit {hem} Skirt",
         styles=tuple(_SKIRT_SHAPES)),
    Leaf("CM", ("Womens", "Tops", "Camisoles"), "Top", 12,
         ("Satin", "Silk Blend", "Cotton Jersey", "Lace Trim Jersey", "Ribbed Jersey", "Modal"),
         ("Regular", "Fitted", "Relaxed"), ("V Neck", "Scoop Neck", "Square Neck"),
         ("Sleeveless",), "{f} {fit} Fit {neck} Camisole"),
    Leaf("VT", ("Womens", "Tops", "Vest Tops"), "Top", 12,
         ("Cotton Jersey", "Ribbed Cotton", "Organic Cotton", "Slub Cotton", "Modal", "Linen Blend"),
         ("Regular", "Fitted", "Relaxed"), ("Crew Neck", "Scoop Neck", "V Neck", "Square Neck"),
         ("Sleeveless",), "{f} {fit} Fit {neck} Vest Top"),
    Leaf("TN", ("Womens", "Tops", "Tunics"), "Top", 12,
         ("Cotton Voile", "Viscose", "Linen Blend", "Crinkle Cotton", "Embroidered Cotton", "Georgette"),
         ("Relaxed", "Regular"), ("V Neck", "Boat Neck", "Collar", "High Neck"),
         ("Long Sleeve", "Three Quarter Sleeve", "Short Sleeve"), "{f} {fit} Fit {neck} {s} Tunic"),
)  # fmt: skip


def _row(code, title, brand, kind: Kind, leaf: Leaf, desc, colors, attrs, *, price, params, facts) -> LRow:
    return LRow(code, title, brand, _C, leaf.path, kind.ptype, price, kind.shape, desc, colors,
                attrs=attrs, sizes=tuple((n, price) for n in ADULT), params=params, size_key="size",
                facts=facts)  # fmt: skip


def _rows() -> list[LRow]:
    out: list[LRow] = []
    for leaf in _LEAVES:
        kind = KINDS[leaf.kind]
        combos: dict[str, tuple] = {}
        for f, fit, st, neck, s in _product(leaf.fabrics, leaf.fits, leaf.styles, leaf.necks, leaf.sleeves):
            hem = ("Mini", "Midi", "Maxi")[zlib.crc32(f"{f}{fit}{st}".encode()) % 3] if st else ""
            t = "Womens " + " ".join(leaf.title.format(f=f, fit=fit, st=st, neck=neck, s=s, hem=hem).split())
            combos.setdefault(t, (f, fit, st, neck, s, hem))
        pairs = _choose([(t, *c) for t, c in combos.items()], leaf.n)
        assert len(pairs) == leaf.n, (leaf.abbr, len(combos))
        for i, (title, f, fit, st, neck, s, hem) in enumerate(pairs):
            brand = _BRANDS[(i + len(leaf.abbr)) % len(_BRANDS)]
            price = round(kind.base_price + leaf.extra_price + 2.0 * (i % 7), 2)
            attrs = [("fit", "Fit", fit)]
            attrs.append(("fabric", "Fabric", f) if kind.ptype == "Skirt"
                         else ("material", "Material", f.replace(" Blend", " blend")))
            facts: list = []
            params: tuple = ()
            wear = f"{_an(f)} {kind.noun.lower()} cut to {_an(fit)} fit"
            detail = []
            if neck:
                attrs_neck = NECKS[neck][0]
                facts.append(("neckline", attrs_neck))
                detail.append(f"a {neck.lower()}")
            if s:
                attrs.append(("sleeve_length", "Sleeve length", SLEEVES[s][0]))
                detail.append("no sleeves" if s == "Sleeveless" else f"{SLEEVES[s][0].lower()} sleeves")
            if kind.ptype == "Top":
                params = (("neckline", NECKS[neck][1]), ("sleeve", SLEEVES[s][1]), ("kind", "tee"))
            elif kind.ptype == "Skirt":
                attrs += [("skirt_shape", "Shape", st), ("garment_length", "Length", hem)]
                params = (("shape", _SKIRT_SHAPES[st]), ("hem", hem.lower()))
                detail.append(f"{st.lower()} shape and a {hem.lower()} length")
            elif kind.ptype == "Suit Jacket":
                params = (("fit", {"Slim": "slim", "Tailored": "tailored"}.get(fit, "regular")),
                          ("lapel", "notch"), ("buttons", "2"))  # fmt: skip
            desc = f"{wear.capitalize()}, with {' and '.join(detail) + ' ' if detail else ''}{kind.tail}."
            desc = desc.replace(", with  ", ", with ").replace("  ", " ")
            facts.append(("size_range", ["regular"]))
            colors = _colors(i, leaf.palette)
            out.append(_row(f"WD{leaf.abbr}{i:03d}", title, brand, kind, leaf, desc, colors, tuple(attrs),
                            price=price, params=params, facts=tuple(facts)))
    return out


ROWS: tuple[LRow, ...] = tuple(_rows())


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
