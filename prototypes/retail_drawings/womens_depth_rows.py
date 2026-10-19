"""Womens clothing depth (gen#310, the Womens slice): data only.

The Womens tree held 117 dresses over eight leaves, 41 blouses and shirts, 56 coats and jackets,
43 skirts and no camisoles, vest tops, tunics, wool coats, trench coats or rain macs, so a query
for "midi dress" or "womens trench" had little to choose between. This module adds, as distinct
products (a product is a style; its colors times its sizes are its SKUs):

=============================  =====================================================  =====
group                          leaves added to                                        floor
=============================  =====================================================  =====
dresses                        Womens/Dresses: Midi, Maxi, Mini, Tea, Slip,            200
                               T-Shirt, Jumper, Shift, Bodycon, Occasion
blouses and shirts             Womens/Shirts & Blouses; Womens/Tops/Shirts: Linen,      80
                               Oxford, Denim, Flannel
coats and jackets              Womens/Coats & Jackets: Wool Coats, Trench Coats,        80
                               Rain Macs, Puffer Jackets, Blazers
skirts                         Womens/Skirts                                            80
tops                           Womens/Tops: Camisoles, Vest Tops, Tunics                80
=============================  =====================================================  =====

Nightwear and lingerie beyond bras (about 140) and school uniform (about 100) already meet their
floors; the Kids dresses and coats are a later slice. Every product carries its fit, material
and, where it applies, neckline and sleeve length, with a title a shop would use ("Womens Pure
Linen Relaxed Fit Midi Dress"): the fit word, the waist phrase, the stretch phrase and the skirt
closure are derived per kind and leaf below, so none contradicts its title.

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
    "Scoop Neck": ("round", "scoop"), "High Neck": ("high", "roll_neck"),
    "Collar": ("collared", "crew"),
}  # fmt: skip
#: sleeve word -> (the sleeve_length attribute, the drawing's sleeve).
SLEEVES = {
    "Long Sleeve": ("Long", "long"), "Short Sleeve": ("Short", "short"),
    "Three Quarter Sleeve": ("Three quarter", "three_quarter"), "Sleeveless": ("Sleeveless", "sleeveless"),
}  # fmt: skip
_SKIRT_SHAPES = {"A-Line": "a_line", "Pleated": "pleated", "Pencil": "pencil", "Wrap": "wrap", "Tiered": "tiered"}
#: skirt shape -> (how a shop describes the shape, the waist_type fact, how it fastens). A wrap
#: ties and has no zip; a pleated or tiered skirt pulls on over an elastic waist.
_SKIRT_MAKE = {
    "A-Line": ("an A-line flare", "Zip", "a side zip"),
    "Pleated": ("knife pleats", "Elastic", "an elastic waist"),
    "Pencil": ("a slim pencil cut", "Zip", "a back zip"),
    "Wrap": ("a wrap front", "Tie", "a tie waist"),
    "Tiered": ("tiered layers", "Elastic", "an elastic waist"),
}
#: skirt fabric -> its lining fact, as the Skirts already on the tree state it.
_SKIRT_LINING = {"Cotton": "Unlined", "Satin": "Polyester", "Denim": "Unlined", "Faux Leather": "Polyester",
                 "Linen": "Unlined", "Velvet": "Polyester", "Corduroy": "Unlined", "Jersey": "Unlined"}  # fmt: skip
#: top fabric -> how it feels, so only a fabric that stretches is called stretchy.
_FEEL = {
    "Satin": "a smooth, fluid drape", "Silk Blend": "a smooth, soft drape", "Cotton Jersey": "a soft, stretchy feel",
    "Lace Trim Jersey": "a soft, stretchy feel", "Ribbed Jersey": "a soft, stretchy rib",
    "Modal": "a soft, stretchy feel", "Ribbed Cotton": "a stretchy rib", "Organic Cotton": "a soft organic cotton hand",
    "Slub Cotton": "a soft, textured slub", "Linen Blend": "a light, breathable weave",
    "Cotton Voile": "a light, airy weave", "Viscose": "a fluid drape", "Crinkle Cotton": "a crinkled texture",
    "Embroidered Cotton": "embroidered detail", "Georgette": "a light, floaty drape",
}  # fmt: skip
#: a feature word in the title -> the same feature in the description.
_FEATURE = {
    "Hooded": "an attached hood", "Cropped": "a cropped length", "Funnel Neck": "a funnel neck",
    "Longline": "a longline length", "Belted": "a self-tie belt", "Double Breasted": "a double-breasted front",
    "Single Breasted": "a single-breasted front",
}  # fmt: skip
#: fit -> how the description says the body is cut; a fit is a facet value, so the titles say
#: "Regular Fit" or "Oversized Fit" and the one word "Fitted".
_WAIST = {"Fitted": "a fitted waist", "Regular": "a defined waist", "Relaxed": "a relaxed, easy shape",
          "Oversized": "a loose, easy shape", "Slim": "a slim cut"}  # fmt: skip


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


def _fit_title(fit: str) -> str:
    """How a title says a fit: "Regular Fit", "Oversized Fit", but the one word "Fitted"."""
    return fit if fit == "Fitted" else f"{fit} Fit"


def _neck_title(neck: str) -> str:
    return "Collared" if neck == "Collar" else neck


def _tail(kind: Kind, leaf: Leaf, fit: str, fabric: str, neck: str, shape: str) -> str:
    """The description's last words: they follow the leaf's shape, the fit, the fabric or the neckline."""
    if leaf.tail or kind.tail:
        return leaf.tail or kind.tail
    if kind.ptype == "Skirt":
        return _SKIRT_MAKE[shape][2]
    if kind.ptype == "Top":
        return _FEEL[fabric]
    if kind.ptype == "Blouse":
        return "a button front" if neck == "Collar" else "a concealed button placket"
    if leaf.abbr == "SH":
        return "a straight shape that skims the body"
    return "a close, figure-hugging shape" if leaf.abbr == "BC" else _WAIST[fit]


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
    tail: str  # the description's last words; "" where they follow the leaf's fit, fabric or shape


KINDS = {
    "Dress": Kind("Dress", "Dress", "dress", 28.0, ""),
    "Blouse": Kind("Blouse", "Blouse", "blouse", 22.0, ""),
    "Shirt": Kind("Shirt", "Shirt", "blouse", 24.0, "a button front with a chest pocket"),
    "Coat": Kind("Coat", "Coat", "coat", 70.0, "a full lining"),
    "Suit Jacket": Kind("Suit Jacket", "Blazer", "suit_jacket", 55.0, "a button fastening"),
    "Skirt": Kind("Skirt", "Skirt", "skirt", 22.0, ""),
    "Top": Kind("Top", "Top", "top", 12.0, ""),
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
    styles: tuple[str, ...] = ("",)  # skirt shapes, or a feature word each ("Belted", "Hooded")
    noun: str = ""  # what the description calls it, where the kind's noun is not it
    tail: str = ""  # the description's last words, where the kind's are not the leaf's


_D = ("Womens", "Dresses")
_KNIT = ("Chunky Knit", "Ribbed Knit", "Cable Knit", "Merino Blend", "Soft Touch Knit", "Waffle Knit")
_LEAVES = (
    Leaf("MD", _D + ("Midi Dresses",), "Dress", 14,
         ("Pure Linen", "Crepe", "Satin", "Stretch Jersey", "Cotton Poplin", "Viscose", "Chiffon"),
         ("Regular", "Relaxed"), ("V Neck", "Square Neck", "Boat Neck", "Crew Neck"),
         ("Long Sleeve", "Short Sleeve", "Sleeveless"), "{f} {fit} {neck} {s} Midi Dress"),
    Leaf("MX", _D + ("Maxi Dresses",), "Dress", 8,
         ("Pure Linen", "Cotton Poplin", "Viscose", "Chiffon", "Stretch Jersey", "Satin"),
         ("Regular", "Relaxed"), ("V Neck", "Square Neck", "Crew Neck", "Boat Neck"),
         ("Short Sleeve", "Sleeveless", "Long Sleeve"), "{f} {fit} {neck} {s} Maxi Dress"),
    Leaf("MN", _D + ("Mini Dresses",), "Dress", 14,
         ("Cotton Poplin", "Stretch Jersey", "Denim", "Satin", "Crepe", "Corduroy", "Broderie"),
         ("Regular", "Fitted"), ("Square Neck", "V Neck", "Scoop Neck", "Crew Neck"),
         ("Short Sleeve", "Sleeveless", "Long Sleeve"), "{f} {fit} {neck} {s} Mini Dress"),
    Leaf("SL", _D + ("Slip Dresses",), "Dress", 10,
         ("Satin", "Silk Blend", "Crepe", "Jersey", "Lace Trim Satin", "Viscose"),
         ("Regular", "Relaxed", "Fitted"), ("V Neck", "Scoop Neck", "Square Neck"),
         ("Sleeveless",), "{f} {fit} {neck} Slip Dress"),
    Leaf("TS", _D + ("T-Shirt Dresses",), "Dress", 8,
         ("Organic Cotton", "Cotton Jersey", "Slub Cotton", "Stretch Jersey", "Modal"),
         ("Relaxed", "Regular", "Oversized"), ("Crew Neck",), ("Short Sleeve", "Long Sleeve"),
         "{f} {fit} {s} T-Shirt Dress"),
    Leaf("JD", _D + ("Jumper Dresses",), "Dress", 12, _KNIT, ("Regular", "Relaxed", "Fitted"),
         ("Crew Neck", "High Neck", "V Neck", "Boat Neck"), ("Long Sleeve", "Three Quarter Sleeve"),
         "{f} {fit} {neck} {s} Jumper Dress", extra_price=10.0),
    Leaf("SH", _D + ("Shift Dresses",), "Dress", 14,
         ("Crepe", "Ponte", "Textured Cotton", "Tweed Look", "Stretch Cotton", "Jacquard"),
         ("Regular", "Relaxed"), ("Boat Neck", "Scoop Neck", "Square Neck", "Crew Neck"),
         ("Short Sleeve", "Sleeveless", "Three Quarter Sleeve"),
         "{f} {fit} {neck} {s} Shift Dress", palette=_TAILORED, extra_price=6.0),
    Leaf("BC", _D + ("Bodycon Dresses",), "Dress", 12,
         ("Ribbed Jersey", "Stretch Crepe", "Scuba", "Seamless Knit", "Ruched Jersey", "Satin"),
         ("Fitted",), ("Square Neck", "Scoop Neck", "V Neck", "High Neck"),
         ("Sleeveless", "Long Sleeve", "Short Sleeve"), "{f} {neck} {s} Bodycon Dress"),
    Leaf("OC", _D + ("Occasion Dresses",), "Dress", 20,
         ("Satin", "Velvet", "Sequin", "Lace", "Chiffon", "Taffeta", "Stretch Crepe", "Organza"),
         ("Regular", "Fitted", "Relaxed"), ("V Neck", "Square Neck", "High Neck", "Boat Neck"),
         ("Sleeveless", "Long Sleeve", "Three Quarter Sleeve"), "{f} {fit} {neck} {s} Occasion Dress",
         palette=("Black", "Red", "Navy", "Green", "Burgundy", "White", "Blue", "Yellow", "Cream",
                  "Pink", "Lilac"), extra_price=22.0),
    Leaf("TE", _D + ("Tea Dresses",), "Dress", 10,
         ("Cotton Lawn", "Viscose", "Crepe", "Broderie Anglaise", "Cotton Poplin", "Chiffon"),
         ("Regular", "Fitted", "Relaxed"), ("V Neck", "Square Neck", "Scoop Neck", "Crew Neck"),
         ("Short Sleeve", "Three Quarter Sleeve", "Long Sleeve"), "{f} {fit} {neck} {s} Tea Dress"),
    Leaf("BL", ("Womens", "Shirts & Blouses", "Blouses"), "Blouse", 30,
         ("Crepe", "Satin", "Chiffon", "Cotton Poplin", "Viscose", "Georgette", "Linen Blend", "Silk Blend"),
         ("Regular", "Relaxed"), ("Collar",),  # the blouse shape draws a collar, so no other neckline
         ("Long Sleeve", "Short Sleeve", "Three Quarter Sleeve"), "{f} {fit} {neck} {s} Blouse"),
    Leaf("SLN", ("Womens", "Tops", "Shirts", "Linen Shirts"), "Shirt", 8,
         ("Pure Linen", "Linen Blend", "Washed Linen", "Linen Cotton"), ("Relaxed", "Regular", "Oversized"),
         ("Collar",), ("Long Sleeve", "Short Sleeve"), "{f} {fit} {s} Shirt"),
    Leaf("SOX", ("Womens", "Tops", "Shirts", "Oxford Shirts"), "Shirt", 8,
         ("Washed Oxford", "Pinpoint Oxford", "Stretch Oxford", "Brushed Oxford", "Garment Dyed Oxford"),
         ("Relaxed", "Regular", "Fitted"), ("Collar",), ("Long Sleeve", "Short Sleeve"), "{f} {fit} {s} Shirt"),
    Leaf("SDN", ("Womens", "Tops", "Shirts", "Denim Shirts"), "Shirt", 8,
         ("Light Wash Denim", "Stretch Denim", "Chambray", "Washed Denim", "Soft Denim"),
         ("Oversized", "Regular", "Relaxed"), ("Collar",), ("Long Sleeve", "Short Sleeve"), "{f} {fit} {s} Shirt"),
    Leaf("SFL", ("Womens", "Tops", "Shirts", "Flannel Shirts"), "Shirt", 8,
         ("Brushed Cotton Flannel", "Soft Flannel", "Cotton Flannel", "Heavyweight Flannel"),
         ("Oversized", "Regular", "Relaxed"), ("Collar",), ("Long Sleeve",), "{f} {fit} {s} Shirt"),
    Leaf("CW", ("Womens", "Coats & Jackets", "Coats", "Wool Coats"), "Coat", 14,
         ("Wool Blend", "Pure Wool", "Wool Cashmere Blend", "Boucle", "Herringbone", "Felted Wool"),
         ("Regular", "Relaxed", "Oversized"), ("",), ("Long Sleeve",), "{f} {fit} {wool}Coat",
         palette=_TAILORED, extra_price=60.0),
    Leaf("CT", ("Womens", "Coats & Jackets", "Coats", "Trench Coats"), "Coat", 14,
         ("Cotton Gabardine", "Water Repellent Cotton", "Cotton Twill", "Stretch Cotton", "Lightweight Cotton"),
         ("Regular", "Relaxed"), ("",), ("Long Sleeve",), "{f} {fit} {st} Trench Coat",
         palette=("Camel", "Stone", "Navy", "Black", "Olive", "Cream", "Red", "Green", "Yellow", "Blue"),
         extra_price=40.0, styles=("Belted", "Double Breasted", "Single Breasted")),
    Leaf("CR", ("Womens", "Coats & Jackets", "Rain Macs"), "Coat", 12,
         ("Waterproof Nylon", "Recycled Polyester", "Coated Cotton", "Taped Seam Nylon", "Ripstop", "Matte Nylon"),
         ("Regular", "Relaxed"), ("",), ("Long Sleeve",), "{f} {fit} Hooded Rain Mac", tail="a mesh lining", styles=("Hooded",),
         palette=("Yellow", "Navy", "Red", "Green", "Black", "Blue", "White", "Pink", "Olive"), extra_price=20.0),
    Leaf("CB", ("Womens", "Coats & Jackets", "Blazers"), "Suit Jacket", 10,
         ("Crepe", "Stretch Suiting", "Linen Blend", "Textured Weave", "Wool Blend", "Tweed Look"),
         ("Regular", "Slim", "Relaxed"), ("",), ("Long Sleeve",), "{f} {fit} Blazer",
         palette=_TAILORED, extra_price=10.0),
    Leaf("PF", ("Womens", "Coats & Jackets", "Puffer Jackets"), "Coat", 12,
         ("Recycled Nylon", "Quilted Nylon", "Matte Nylon", "Ripstop Nylon", "Glossy Nylon", "Recycled Polyester"),
         ("Regular", "Relaxed", "Oversized"), ("",), ("Long Sleeve",), "{f} {fit} {st} Puffer Jacket",
         noun="puffer jacket", tail="a quilted, padded body", styles=("Hooded", "Cropped", "Funnel Neck", "Longline"),
         palette=("Black", "Navy", "Red", "Green", "Blue", "White", "Yellow", "Olive", "Pink", "Cream"),
         extra_price=25.0),
    Leaf("SK", ("Womens", "Skirts"), "Skirt", 50,
         ("Cotton", "Satin", "Denim", "Faux Leather", "Linen", "Velvet", "Corduroy", "Jersey"),
         ("Regular", "Relaxed"), ("",), ("",), "{f} {st} {fit} {hem} Skirt",
         styles=tuple(_SKIRT_SHAPES)),
    Leaf("CM", ("Womens", "Tops", "Camisoles"), "Top", 12,
         ("Satin", "Silk Blend", "Cotton Jersey", "Lace Trim Jersey", "Ribbed Jersey", "Modal"),
         ("Regular", "Fitted", "Relaxed"), ("V Neck", "Scoop Neck", "Square Neck"),
         ("Sleeveless",), "{f} {fit} {neck} Camisole"),
    Leaf("VT", ("Womens", "Tops", "Vest Tops"), "Top", 12,
         ("Cotton Jersey", "Ribbed Cotton", "Organic Cotton", "Slub Cotton", "Modal", "Linen Blend"),
         ("Regular", "Fitted", "Relaxed"), ("Crew Neck", "Scoop Neck", "V Neck", "Square Neck"),
         ("Sleeveless",), "{f} {fit} {neck} Vest Top"),
    Leaf("TN", ("Womens", "Tops", "Tunics"), "Top", 12,
         ("Cotton Voile", "Viscose", "Linen Blend", "Crinkle Cotton", "Embroidered Cotton", "Georgette"),
         ("Relaxed", "Regular"), ("V Neck", "Boat Neck", "Collar", "High Neck"),
         ("Long Sleeve", "Three Quarter Sleeve", "Short Sleeve"), "{f} {fit} {neck} {s} Tunic"),
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
            hem = ("Mini", "Midi", "Maxi")[zlib.crc32(f"{f}{fit}{st}".encode()) % 3] if kind.ptype == "Skirt" else ""
            t = "Womens " + " ".join(leaf.title.format(f=f, fit=_fit_title(fit), st=st, s=s, hem=hem,
                                                      wool="" if "Wool" in f else "Wool ", neck=_neck_title(neck)).split())
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
            wear = f"{_an(f)} {(leaf.noun or kind.noun.lower())} cut " + ("close to the body" if fit == "Fitted" else f"to {_an(fit)} fit")
            detail = []
            if neck:
                attrs_neck = NECKS[neck][0]
                facts.append(("neckline", attrs_neck))
                detail.append("a collar" if neck == "Collar" else f"a {neck.lower()}")
            if s:
                attrs.append(("sleeve_length", "Sleeve length", SLEEVES[s][0]))
                detail.append("no sleeves" if s == "Sleeveless" else f"{SLEEVES[s][0].lower()} sleeves")
            if kind.ptype == "Top":
                params = (("neckline", NECKS[neck][1]), ("sleeve", SLEEVES[s][1]), ("kind", "tee"))
            elif kind.ptype == "Skirt":
                attrs += [("skirt_shape", "Shape", st), ("garment_length", "Length", hem),
                          ("waist_type", "Waist type", _SKIRT_MAKE[st][1]), ("lining", "Lining", _SKIRT_LINING[f])]
                params = (("shape", _SKIRT_SHAPES[st]), ("hem", hem.lower()))
                detail += [_SKIRT_MAKE[st][0], f"a {hem.lower()} length"]
            elif kind.ptype == "Suit Jacket":
                params = (("fit", "slim" if fit == "Slim" else "regular"),
                          ("lapel", "notch"), ("buttons", "2"))  # fmt: skip
            if st and kind.ptype != "Skirt":
                detail.append(_FEATURE[st])
            detail.append(_tail(kind, leaf, fit, f, neck, st))
            desc = f"{wear.capitalize()}, with {', '.join(detail[:-1])} and {detail[-1]}." if len(detail) > 1 \
                else f"{wear.capitalize()}, with {detail[0]}."
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
