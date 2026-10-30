"""Kids clothing depth (gen#310, the Kids slice): data only.

The Kids tree held one girls' dress, two real boys' coats and no girls' coat. The issue asks for
"school uniform ... plus dresses and coats" and names no number for them, so this slice raises the
three leaves below to thirty real products each (the issue calls a leaf of under thirty thin).
A product is a style; its colors times its school ages are its SKUs. A dress multipack (gen#727)
is its own product at each count, so "red dresses" has plural titles to prefer.

=========================  ===================================================  =====
leaf                       what is added                                        floor
=========================  ===================================================  =====
Kids/Girls/Dresses         party, summer, skater, smocked, tiered, pinafore,    30
                           jumper, wrap, T-shirt and shirt dresses
Kids/Girls/Coats & Jackets padded coats, parkas, rain macs, trench and pea      30
                           coats, quilted jackets
Kids/Boys/Coats & Jackets  the same six, for boys                               30
=========================  ===================================================  =====

School uniform already holds 103 products (:mod:`school_rows`, gen#205), above the issue's 80, so
it is not repeated here. Every product carries its fit, material and sleeve length and, on a
dress, its neckline, with a title a shop would use ("Girls Cotton Poplin Short Sleeve Summer
Dress"). The text-match decoys of the Dress and Coat types are the apparel plan's
(:mod:`decoy_apparel`, gen#311), so none is written here.

The rows are templates only: :func:`scale.derivable` leaves them out (``scale.source_ids("kids_depth_rows")``),
so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import zlib
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.lowerbody_rows import LRow
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.school_rows import AGES
from synthetic_ecommerce_data.domains.retail.underwear_rows import URow, _pack_attrs, _packs
from synthetic_ecommerce_data.domains.retail.variants import cw

_BRANDS = ("Little Fernby", "Calderby & Lune", "Bramblewood", "Larkmoor")
OWNERS.update({b: BRAND_OWNER[b] for b in _BRANDS})

_C = "Clothing"
HEX = {
    **MAIN_COLORS, "Navy": "#26365c", "Pink": "#e7a9b8", "Cream": "#efe4cf", "Grey": "#9a9a9a",
    "Lilac": "#b9a6d4", "Teal": "#1c7c7d", "Olive": "#6b6b2f", "Burgundy": "#6d1f2f",
    "Camel": "#b5835a", "Charcoal": "#4a4a50",
}  # fmt: skip
_GIRLS_DRESS = ("Pink", "Red", "Blue", "Yellow", "White", "Lilac", "Green", "Navy", "Teal", "Cream")
_GIRLS_COAT = ("Pink", "Navy", "Red", "Green", "Blue", "Yellow", "Cream", "Lilac", "Teal", "Black")
_BOYS_COAT = ("Navy", "Red", "Green", "Blue", "Black", "Grey", "Olive", "Yellow", "Charcoal", "White")

#: neckline word -> (the neckline fact, how the description says it).
NECKS = {"Crew Neck": ("crew", "a crew neck"), "V Neck": ("v-neck", "a v-neck"),
         "Scoop Neck": ("round", "a scoop neck"), "Square Neck": ("square", "a square neck"),
         "Collar": ("collared", "a collar")}  # fmt: skip
#: sleeve word -> (the sleeve_length attribute, how the description says it).
SLEEVES = {"Long Sleeve": ("Long", "long sleeves"), "Short Sleeve": ("Short", "short sleeves"),
           "Sleeveless": ("Sleeveless", "no sleeves")}  # fmt: skip
_SIZES = {"Dress": AGES[:6], "Coat": AGES}


@dataclass(frozen=True)
class DressStyle:
    name: str
    fabrics: tuple[str, ...]
    necks: tuple[str, ...]
    sleeves: tuple[str, ...]
    tail: str  # the description's last words: what the style is


@dataclass(frozen=True)
class CoatStyle:
    name: str
    fabrics: tuple[str, ...]
    tail: str


_ALL_SLEEVES = ("Short Sleeve", "Sleeveless", "Long Sleeve")
_DRESSES = (
    DressStyle("Party Dress", ("Tulle", "Satin", "Velvet", "Sequin"), ("Scoop Neck", "Square Neck"), _ALL_SLEEVES, "a full, floaty skirt"),
    DressStyle("Summer Dress", ("Cotton Poplin", "Cotton Lawn", "Viscose", "Broderie Anglaise"), ("Square Neck", "V Neck", "Scoop Neck"), _ALL_SLEEVES, "a light, easy skirt"),
    DressStyle("Skater Dress", ("Cotton Jersey", "Stretch Jersey", "Ponte", "Organic Cotton"), ("Crew Neck", "Scoop Neck"), _ALL_SLEEVES, "a flared skater skirt"),
    DressStyle("Smocked Dress", ("Cotton Poplin", "Seersucker", "Cotton Lawn", "Crinkle Cotton"), ("Square Neck", "Scoop Neck"), ("Short Sleeve", "Sleeveless"), "a smocked bodice"),
    DressStyle("Tiered Dress", ("Cotton Poplin", "Viscose", "Cotton Lawn", "Crinkle Cotton"), ("Square Neck", "V Neck", "Crew Neck"), ("Short Sleeve", "Sleeveless", "Long Sleeve"), "a tiered skirt"),
    DressStyle("Pinafore Dress", ("Corduroy", "Denim", "Cotton Twill", "Needlecord"), ("Square Neck", "Scoop Neck"), ("Sleeveless",), "a bib front and two straps"),
    DressStyle("Jumper Dress", ("Chunky Knit", "Ribbed Knit", "Cable Knit", "Waffle Knit"), ("Crew Neck", "V Neck"), ("Long Sleeve", "Short Sleeve"), "a soft knitted skirt"),
    DressStyle("Wrap Dress", ("Cotton Jersey", "Viscose", "Crepe", "Cotton Poplin"), ("V Neck",), ("Long Sleeve", "Short Sleeve", "Sleeveless"), "a wrap front with a tie waist"),
    DressStyle("T-Shirt Dress", ("Cotton Jersey", "Organic Cotton", "Slub Cotton", "Stretch Jersey"), ("Crew Neck",), ("Short Sleeve", "Long Sleeve"), "an easy jersey shape"),
    DressStyle("Shirt Dress", ("Light Wash Denim", "Chambray", "Cotton Poplin", "Linen Blend"), ("Collar",), ("Short Sleeve", "Sleeveless", "Long Sleeve"), "a button front"),
)  # fmt: skip
_COATS = (
    CoatStyle("Padded Coat", ("Quilted Nylon", "Recycled Polyester", "Lightweight Nylon"), "a padded fill and a zip front"),
    CoatStyle("Parka", ("Water Repellent Cotton", "Recycled Polyester", "Cotton Twill"), "a zip front and storm cuffs"),
    CoatStyle("Rain Mac", ("Waterproof PU", "Recycled Nylon", "Coated Cotton"), "taped seams and a press stud front"),
    CoatStyle("Trench Coat", ("Cotton Gabardine", "Cotton Twill", "Lightweight Cotton"), "a belt and a button front"),
    CoatStyle("Pea Coat", ("Wool Blend", "Felted Wool", "Herringbone"), "a double-breasted front"),
    CoatStyle("Quilted Jacket", ("Matte Nylon", "Cotton Twill", "Recycled Polyester"), "a quilted body and a zip front"),
)  # fmt: skip
_FEATURES = {"": "", "Hooded": "an attached hood", "Longline": "a longline length"}

#: The dress multipacks (gen#727): (style, fabric, neck, sleeve, colors). Each style sells a pack
#: of 2 and a pack of 3, in one color a pack, at the multibuy factor of a dress at the cheapest
#: single's price. There is no Womens multipack: packs of dresses are a children's-wear habit.
_PACKS = (
    ("T-Shirt Dress", "Cotton Jersey", "Crew Neck", "Short Sleeve", ("Red", "Navy", "Pink")),
    ("Summer Dress", "Cotton Poplin", "Square Neck", "Sleeveless", ("Red", "Blue", "Yellow")),
    ("Skater Dress", "Stretch Jersey", "Scoop Neck", "Long Sleeve", ("Red", "Green", "Lilac")),
)  # fmt: skip
_PACK_COUNTS = {2: "two", 3: "three"}
_PACK_PRICE = 12.0


@dataclass(frozen=True)
class PackRow(URow, LRow):
    """A style sold only as one multipack: ``LRow``'s facts, and ``URow``'s pack on every SKU."""


def _an(word: str) -> str:
    return f"{'an' if word.lower()[:1] in 'aeiou' else 'a'} {word.lower()}"


def _col(name: str):
    return cw(name, HEX[name])


def _colors(i: int, palette: tuple[str, ...]):
    n = len(palette)
    picks = [palette[(2 * i) % n], palette[(2 * i + 3) % n], palette[(3 * i + 1) % n]]
    return tuple(_col(c) for c in dict.fromkeys(picks))


def _price(base: float, i: int) -> float:
    return round(base + 1.5 * (i % 5), 2)


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, shape: str,
         price: float, desc: str, colors: tuple, attrs: tuple, facts: tuple,
         row: type[LRow] = LRow, **extra) -> LRow:  # fmt: skip
    sizes = tuple((a, round(price + 0.5 * k, 2)) for k, a in enumerate(_SIZES[ptype]))
    return row(code, title, brand, _C, path, ptype, price, shape, desc, colors, attrs=attrs,
               sizes=sizes, audience="kids", facts=facts, **extra)  # fmt: skip


def _pick(keyed: list[tuple], n: int) -> list[tuple]:
    """``n`` of the combinations, spread by a digest of each so no one style takes the first n."""
    return sorted(keyed, key=lambda c: zlib.crc32("|".join(map(str, c)).encode()))[:n]


def _dresses(n_each: int = 3) -> list[LRow]:
    out: list[LRow] = []
    path = ("Kids", "Girls", "Dresses")
    for si, st in enumerate(_DRESSES):
        combos = [(f, s) for f in st.fabrics for s in st.sleeves]
        for k, (f, s) in enumerate(_pick(combos, n_each)):
            i = si * n_each + k
            neck = st.necks[(i + k) % len(st.necks)]
            fit = ("Regular", "Relaxed")[i % 2]
            sleeve, sleeve_words = SLEEVES[s]
            title = f"Girls {f} {s} {st.name}"
            desc = (f"{_an(f).capitalize()} {st.name.lower()} cut to {_an(fit)} fit, with {NECKS[neck][1]}, "
                    f"{sleeve_words} and {st.tail}.")  # fmt: skip
            attrs = (("fit", "Fit", fit), ("material", "Material", f.replace(" Blend", " blend")), ("sleeve_length", "Sleeve length", sleeve))
            out.append(_row(f"KDD{i:03d}", title, _BRANDS[i % 4], path, "Dress", "dress",
                            _price(12.0, i), desc, _colors(i, _GIRLS_DRESS), attrs,
                            (("neckline", NECKS[neck][0]),)))
    return out


def _dress_packs() -> list[LRow]:
    """Each style of :data:`_PACKS` as a pack of 2 and a pack of 3, each its own product: the
    count is in the title, the ``pack_size`` and the SKU's ``units_per_pack``, which
    :mod:`pack_copies` draws."""
    out: list[LRow] = []
    for si, (name, f, neck, s, colors) in enumerate(_PACKS):
        st = next(d for d in _DRESSES if d.name == name)
        sleeve, sleeve_words = SLEEVES[s]
        for k, (n, word) in enumerate(_PACK_COUNTS.items()):
            i = len(_PACK_COUNTS) * si + k
            fit = ("Regular", "Relaxed")[i % 2]
            desc = (f"A pack of {word} {f.lower()} {name.lower()}es, all in the same color, cut to {_an(fit)} fit, "
                    f"with {NECKS[neck][1]}, {sleeve_words} and {st.tail}.")  # fmt: skip
            attrs = (("fit", "Fit", fit), ("material", "Material", f), ("sleeve_length", "Sleeve length", sleeve),
                     *_pack_attrs(_packs(n)))  # fmt: skip
            out.append(_row(f"KDP{i:03d}", f"Girls {f} {name}es, Pack of {n}", _BRANDS[i % 4], ("Kids", "Girls", "Dresses"),
                            "Dress", "dress", _PACK_PRICE, desc, tuple(_col(c) for c in colors), attrs,
                            (("neckline", NECKS[neck][0]),), row=PackRow, packs=_packs(n)))  # fmt: skip
    return out


def _coats(who: str, code: str, palette: tuple[str, ...], n: int, base: float) -> list[LRow]:
    path = ("Kids", who, "Coats & Jackets")
    combos = [(st.name, f, feat) for st in _COATS for f in st.fabrics for feat in _FEATURES]
    out: list[LRow] = []
    for i, (name, f, feat) in enumerate(_pick(combos, n)):
        st = next(s for s in _COATS if s.name == name)
        fit = ("Regular", "Relaxed")[i % 2]
        title = " ".join(w for w in (who, feat, f, name) if w)
        items = ["long sleeves", *([_FEATURES[feat]] if feat else [])]
        # a tail that holds its own "and" already closes the list; any other needs one before it
        rest = ", ".join([*items, st.tail]) if " and " in st.tail else f"{', '.join(items)} and {st.tail}"
        desc = f"{_an(f).capitalize()} {name.lower()} cut to {_an(fit)} fit, with {rest}."
        attrs = (("fit", "Fit", fit), ("material", "Material", f.replace(" Blend", " blend")), ("sleeve_length", "Sleeve length", "Long"))
        out.append(_row(f"{code}{i:03d}", title, _BRANDS[(i + 1) % 4], path, "Coat", "coat",
                        _price(base, i), desc, _colors(i, palette), attrs, ()))
    return out


ROWS: tuple[LRow, ...] = (
    *_dresses(),
    *_dress_packs(),
    *_coats("Girls", "KDG", _GIRLS_COAT, 30, 24.0),
    *_coats("Boys", "KDB", _BOYS_COAT, 30, 24.0),
)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
