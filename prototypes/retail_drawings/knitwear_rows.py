"""Knitwear depth (gen#309): data only.

Women's knitwear held 16 products (jumpers and cardigans, mostly extra colors on a few styles)
and Mens none, so "ladies white jumper", "mens navy v neck jumper" or "cashmere cardigan" had a
handful of products to choose between. This module adds, as distinct products (a product is a
style; its colors times its sizes are its SKUs), a grid of knit style by material for each
audience:

=========  ==================================================================  ===========
audience   styles                                                              floor rows
=========  ==================================================================  ===========
Women      jumpers: crew, V, roll, turtle, cable, half zip, boat neck;                 130
           cardigans: button front, longline, cropped; knitted tops: tank, slipover
Men        jumpers: crew, V, roll, cable, half zip, quarter zip;                        95
           cardigans: button front, zip through, shawl collar; knitted top: slipover
=========  ==================================================================  ===========

Every style is made in seven materials (cashmere, merino wool, lambswool, cotton, wool blend,
recycled wool, acrylic blend); a second pass adds more fits so a page does not repeat one title.
Colors: two to four per product, four of five with one of the white group (White, Cream,
Ivory, Off White, Ecru) so "white jumper" shows the color-group story; ``main_colors.complete``
adds the missing main colors. Each product carries its neckline (the existing facet's words,
plus ``v-neck``) and a ``knit_style`` attribute.

**Text-match decoys (gen#294, maintainer ruling 2026-10-14).** Every product type and audience
carries at least three decoys of each of seven classes: a title whose words mislead a text
search while the structured fields stay true. :data:`TABLE` lists each one with its class, the
query it targets and the policy that repairs it; ``tests/test_retail_knitwear_309.py`` pins the
three per class per type and their truth.

1. **color**: "Womens Navy Jumper with Red Stripes" is navy.
2. **category word**: "Womens Dress Length Cardigan".
3. **audience word**: "Mens Women's-Style Cut Jumper".
4. **feature absent**: "Womens Alpaca-Feel Jumper" has no alpaca.
5. **shade in the description only**: "Womens Moonbeam Jumper" is Ivory.
6. **incidental word in a short title** (a range name): "Womens Kettle Hill Jumper" is not a kettle.
7. **invented brand** holding a color or category word: "White Heron", "Red Kite", "Cardigan
   Finch", each with its own house style (``house_styles.py``) and a lockup whose text is the
   brand; the garment is drawn in its true color.

The rows are templates only: :func:`scale.derivable` leaves them out, so the seeded derivation
is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import zlib
from dataclasses import dataclass

from breadth_rows import OWNERS
from class_model import BRAND_OWNER
from lowerbody_rows import LRow
from main_colors import MAIN_COLORS
from place_ranges import place_range
from variants import cw

#: The shop's own brands these rows sell, owned as the rest of the clothing tree states.
_BRANDS = ("Harbour & Pine", "Larkmoor", "Hollinwray Knits", "Wrenfield", "Calderby & Lune")
OWNERS.update({b: BRAND_OWNER[b] for b in _BRANDS})
#: The invented class-7 brands: a color or a category word in the name (not real shops).
NEW_BRANDS = ("White Heron", "Red Kite", "Cardigan Finch")
OWNERS.update(dict.fromkeys(NEW_BRANDS, "third_party"))

_C = "Clothing"
#: Each style's own hex: the drawing keeps these, so Ecru here (#e4d9bd) is not ``variants.py``'s
#: jeans-wash Ecru (#efe7d4) on purpose; a knit's Ecru is a warmer yarn shade.
HEX = {
    **MAIN_COLORS, "White": "#ffffff", "Cream": "#efe4cf", "Ivory": "#f3ecd9",
    "Off White": "#f4f1ea", "Ecru": "#e4d9bd", "Oatmeal": "#d9ccb4", "Camel": "#b5835a",
    "Grey Marl": "#a9a9ac", "Navy": "#26365c", "Stone": "#bdb5a6", "Rose": "#d98a96",
    "Charcoal": "#4a4a50", "Burgundy": "#6d1f2f", "Grey": "#9a9a9a", "Black": "#2a2a2e",
}  # fmt: skip

#: The white group, ordered so White itself leads the rotation.
_WHITES_W = ("White", "Cream", "White", "Ivory", "Off White", "White", "Ecru", "Cream")
_WHITES_M = ("White", "Cream", "White", "Ivory", "White", "Off White", "Cream", "Ecru")
_OTHER = {
    "Womens": ("Navy", "Black", "Red", "Blue", "Green", "Rose", "Camel", "Oatmeal", "Grey Marl",
              "Stone", "Yellow"),
    "Mens": ("Navy", "Black", "Grey Marl", "Blue", "Green", "Red", "Camel", "Oatmeal", "Charcoal",
            "Burgundy", "Yellow"),
}  # fmt: skip


def _article(word: str) -> str:
    return "an" if word[0] in "AEIOU" else "a"


def _col(name: str):
    return cw(name, HEX[name])


@dataclass(frozen=True)
class Style:
    """A knit style: what it is called, where it lives and how it is drawn."""

    name: str  # the knit_style attribute and the grid's row
    noun: str  # the title's last words
    ptype: str
    neck: str  # the neckline fact
    draw_neck: str  # the drawing's neckline
    sleeve: str
    desc: str  # what the description says it has


_JUMP, _CARDI, _TOP = "Jumper", "Cardigan", "Knitted Top"
STYLES = {
    "Crew Neck": Style("Crew Neck", "Crew Neck Jumper", _JUMP, "crew", "crew", "Long", "a ribbed crew neck, cuffs and hem"),
    "V Neck": Style("V Neck", "V Neck Jumper", _JUMP, "v-neck", "v_neck", "Long", "a V neck, ribbed cuffs and a straight hem"),
    "Roll Neck": Style("Roll Neck", "Roll Neck Jumper", _JUMP, "high", "roll_neck", "Long", "a folded roll neck that sits close under a coat"),
    "Turtle Neck": Style("Turtle Neck", "Turtle Neck Jumper", _JUMP, "high", "roll_neck", "Long", "a close turtle neck and a ribbed hem"),
    "Cable Knit": Style("Cable Knit", "Cable Knit Jumper", _JUMP, "crew", "crew", "Long", "a chunky cable knit front and a crew neck"),
    "Half Zip": Style("Half Zip", "Half Zip Jumper", _JUMP, "high", "roll_neck", "Long", "a half zip at a funnel neck"),
    "Quarter Zip": Style("Quarter Zip", "Quarter Zip Jumper", _JUMP, "high", "roll_neck", "Long", "a quarter zip at a stand collar"),
    "Boat Neck": Style("Boat Neck", "Boat Neck Jumper", _JUMP, "boat", "boat", "Long", "a wide boat neck from shoulder to shoulder"),
    "Button Front": Style("Button Front", "Button Front Cardigan", _CARDI, "v-neck", "v_neck", "Long", "a button front and two patch pockets"),
    "Longline": Style("Longline", "Longline Cardigan", _CARDI, "v-neck", "v_neck", "Long", "an open front and a hem that falls below the hip"),
    "Cropped": Style("Cropped", "Cropped Cardigan", _CARDI, "crew", "crew", "Long", "a short body and a crew neck"),
    "Zip Through": Style("Zip Through", "Zip Through Cardigan", _CARDI, "high", "roll_neck", "Long", "a full length zip and a stand collar"),
    "Shawl Collar": Style("Shawl Collar", "Shawl Collar Cardigan", _CARDI, "collared", "crew", "Long", "a shawl collar, a button front and deep pockets"),
    "Tank Top": Style("Tank Top", "Knit Tank Top", _TOP, "round", "crew", "Sleeveless", "a round neck and wide straps"),
    "Slipover": Style("Slipover", "Knitted Slipover", _TOP, "v-neck", "v_neck", "Sleeveless", "a V neck and no sleeves, to wear over a shirt"),
}  # fmt: skip
GRID = {
    "Womens": ("Crew Neck", "V Neck", "Roll Neck", "Turtle Neck", "Cable Knit", "Half Zip",
              "Boat Neck", "Button Front", "Longline", "Cropped", "Tank Top", "Slipover"),
    "Mens": ("Crew Neck", "V Neck", "Roll Neck", "Cable Knit", "Half Zip", "Quarter Zip",
            "Button Front", "Zip Through", "Shawl Collar", "Slipover"),
}  # fmt: skip
#: Extra products beyond the full grid (a second fit on a digest-chosen cell).
EXTRA = {"Womens": 46, "Mens": 25}

#: material -> (title words, the attribute value, base price).
MATERIALS = {
    "cashmere": ("Pure Cashmere", "Cashmere", 120.0),
    "merino": ("Merino Wool", "Merino wool", 60.0),
    "lambswool": ("Lambswool", "Lambswool", 55.0),
    "cotton": ("Cotton", "Cotton", 32.0),
    "wool blend": ("Wool Blend", "Wool blend", 42.0),
    "recycled": ("Recycled Wool", "Recycled wool", 40.0),
    "acrylic": ("Soft Acrylic Blend", "Acrylic blend", 24.0),
}  # fmt: skip
#: The fits a title names (a style's own word, such as Cropped, is not repeated as a fit).
FITS = {
    "Womens": ("Classic", "Relaxed", "Slim", "Oversized", "Fitted", "Boxy"),
    "Mens": ("Classic", "Regular", "Slim", "Relaxed", "Tailored"),
}  # fmt: skip
SIZES = {
    "Womens": ("XS", "S", "M", "L", "XL", "XXL"),
    "Mens": ("S", "M", "L", "XL", "XXL"),
}  # fmt: skip
_STYLE_PRICE = {_JUMP: 0.0, _CARDI: 6.0, _TOP: -8.0}
_TYPE_NOUN = {_JUMP: "jumper", _CARDI: "cardigan", _TOP: "knit top"}
_LEAF = {_JUMP: "Jumpers", _CARDI: "Cardigans", _TOP: "Knitted Tops"}
_SHAPE_KIND = {_JUMP: "jumper", _CARDI: "cardigan", _TOP: "jumper"}


def _digest(*parts) -> int:
    return zlib.crc32("|".join(map(str, parts)).encode())


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _an(phrase: str) -> str:
    word = phrase.lower()
    return f"{'an' if word[:1] in 'aeiou' else 'a'} {word}"


def _row(code, title, brand, root, st: Style, desc, colors, material, fit, *, price,
         style_name=None, extra=()) -> LRow:
    attrs = (_a("material", "Material", material), _a("knit_style", "Knit style", style_name or st.name),
             _a("fit", "Fit", fit), _a("sleeve_length", "Sleeve length", st.sleeve), *extra)  # fmt: skip
    return LRow(
        code, title, brand, _C, (root, "Knitwear", _LEAF[st.ptype]), st.ptype, price, "top", desc,
        colors, attrs=attrs, sizes=tuple((s, price) for s in SIZES[root]),
        params=(("neckline", st.draw_neck), ("sleeve", "sleeveless" if st.sleeve == "Sleeveless" else "long"),
                ("kind", _SHAPE_KIND[st.ptype])),
        size_key="size", facts=(("neckline", st.neck), ("size_range", ["regular"])),
    )  # fmt: skip


def _colors(root: str, n: int):
    """Two to four colors: a white-group shade on four products of five, then others.

    An index that lands on a color already picked moves on to the next unused one, so the
    count is the one planned (a white-group product has three or four, the rest two or three).
    """
    whites = _WHITES_W if root == "Womens" else _WHITES_M
    other = _OTHER[root]
    picks: list[str] = []
    if n % 5 != 4:
        picks.append(whites[(3 * n) % len(whites)])
    plan = [2 * n, 3 * n + 5] + ([5 * n + 1] if n % 3 == 0 else [])
    for start in plan:
        i = start
        while other[i % len(other)] in picks:
            i += 1
        picks.append(other[i % len(other)])
    return tuple(_col(c) for c in picks)


def _floor_rows() -> list[LRow]:
    out: list[LRow] = []
    for root, names in GRID.items():
        tag = root[0]
        cells = [(s, m) for s in names for m in MATERIALS]
        fits = FITS[root]
        picks = [(s, m, fits[_digest(root, s, m) % len(fits)], 0) for s, m in cells]
        ranked = sorted(cells, key=lambda c: _digest("extra", root, *c))
        for s, m in ranked[: EXTRA[root]]:
            first = fits[_digest(root, s, m) % len(fits)]
            second = fits[(_digest("second", root, s, m) % (len(fits) - 1) + 1
                           + fits.index(first)) % len(fits)]
            picks.append((s, m, second, 1))
        seen: set[str] = set()
        for n, (s, m, fit, p) in enumerate(picks):
            st = STYLES[s]
            words, value, base = MATERIALS[m]
            title = f"{root} {words} {fit} {st.noun}"
            assert title not in seen, title
            seen.add(title)
            brand = _BRANDS[(n + len(s)) % len(_BRANDS)]
            price = round(base + _STYLE_PRICE[st.ptype] + (4.0 if root == "Mens" else 0.0)
                          + 2.0 * (n % 5), 2)
            desc = (f"{_an(value).capitalize()} {_TYPE_NOUN[st.ptype]} cut for {_an(fit)} fit, with "
                    f"{st.desc}.")  # fmt: skip
            code = f"K{tag}{names.index(s):02d}{list(MATERIALS).index(m)}{p}"
            out.append(_row(code, title, brand, root, st, desc, _colors(root, n), value, fit,
                            price=price))
    return out


# --------------------------------------------------------------------------
# The decoys: seven classes, three per type and audience each, every field true.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Decoy:
    """One decoy's table row: the doc is :data:`ROWS`'s, found by ``code``."""

    code: str
    root: str
    ptype: str
    klass: int
    word: str  # the misleading word: a color, a noun, an audience word, a feature, a brand
    color: str  # the product's true main color
    query: str  # the shopper query its words match
    policy: str  # which kind of policy repairs it


_TRIMS = ("Stripes", "Piping", "Contrast Stitching")
_MAIN_WORDS = ("Red", "Blue", "Green", "Yellow", "Black", "White")
_TRUE = ("White", "Black", "Navy", "Grey", "Stone", "Oatmeal")
_FANCY = ("Moonbeam", "Candlelight", "Moss Lantern", "Morning Mist", "Sandcastle", "Soft Dune")
_SHADES = ("Ivory", "Cream", "Ecru", "Off White")
_AUDIENCE = {
    "Womens": ("Boyfriend Fit", "Menswear-Style Cut", "Mini-Me Kids' Style"),
    "Mens": ("Women's-Style Cut", "Boyfriend Fit", "Mini-Me Kids' Style"),
}  # fmt: skip
_BORROW = {  # (the noun a title borrows, the modifier phrase), three per type
    _JUMP: (("shirt", "Shirt Collar"), ("coat", "Coat Length"), ("blazer", "Blazer Style")),
    _CARDI: (("coat", "Coat Style"), ("dress", "Dress Length"), ("skirt", "Skirt Hem")),
    _TOP: (("shirt", "Shirt Hem"), ("dress", "Dress Length"), ("trouser", "Trouser Fit")),
}  # fmt: skip
_ABSENT = {
    _JUMP: ("Alpaca-Feel", "Wool-Free", "Silk-Feel"),
    _CARDI: ("Mohair-Look", "Wool-Free", "Angora-Feel"),
    _TOP: ("Linen-Look", "Wool-Free", "Alpaca-Feel"),
}  # fmt: skip
_BRAND_TRUE = {"White Heron": "Navy", "Red Kite": "Oatmeal", "Cardigan Finch": "Grey"}
_BRAND_QUERY = {"White Heron": "white", "Red Kite": "red", "Cardigan Finch": "cardigan"}
#: The style a decoy truly is (its knit_style): a plain one of its type.
_DECOY_STYLE = {_JUMP: "Crew Neck", _CARDI: "Button Front", _TOP: "Slipover"}
_TAIL = {_JUMP: "with ribbed cuffs and hem", _CARDI: "with a button front and ribbed cuffs",
         _TOP: "with a close fit and a ribbed hem"}  # fmt: skip
_NOUN = {_JUMP: "Jumper", _CARDI: "Cardigan", _TOP: "Knit Top"}


def _decoys() -> tuple[list[LRow], list[Decoy]]:
    rows: list[LRow] = []
    table: list[Decoy] = []
    for r_i, root in enumerate(("Womens", "Mens")):
        for k, ptype in enumerate((_JUMP, _CARDI, _TOP)):
            noun = _NOUN[ptype]
            low = noun.lower()
            st = STYLES[_DECOY_STYLE[ptype]]
            tag = f"{root[0]}{k}"
            kk = k + 3 * r_i

            def add(klass, i, title, desc, true, word, query, policy="generic", tag=tag,
                    st=st, ptype=ptype, root=root, extra=()):  # noqa: PLR0913
                code = f"KD{tag}{klass}{i}"
                brand = word if klass == 7 else _BRANDS[(i + klass) % len(_BRANDS)]
                rows.append(_row(code, title, brand, root, st, desc, (_col(true),),
                                 "Acrylic blend", "Regular", price=round(22.0 + 1.5 * i + klass, 2),
                                 extra=extra))
                table.append(Decoy(code, root, ptype, klass, word, true, query, policy))

            for i in range(3):
                w = _MAIN_WORDS[(2 * kk + i) % 6]
                true = _TRUE[(kk + i) % 6]
                if true == w:
                    true = "Navy"
                # 1: a trim, a stripe or a print names the other color.
                add(1, i, f"{root} {true} {noun} with {w} {_TRIMS[i]}",
                    f"{_an(true).capitalize()} {low} {_TAIL[ptype]}, finished with {w.lower()} "
                    f"{_TRIMS[i].lower()}.", true, w, f"{w.lower()} {low}")  # fmt: skip
                # 2: another category's noun used as a modifier.
                b, mod = _BORROW[ptype][i]
                add(2, i, f"{root} {mod} {noun}",
                    f"A {low} named for its {b} detail; it is not a {b}.",
                    _TRUE[(kk + i + 1) % 6], b, f"{b} {low}")  # fmt: skip
                # 3: an audience word that names a sibling cut.
                a = _AUDIENCE[root][i]
                who = root.lower().rstrip("s")
                if a == "Mini-Me Kids' Style":  # a real listing says what it matches, not "Kids' Style"
                    add(3, i, f"{root} Mini-Me {noun}, Kids' Version Sold Separately",
                        f"A {who}'s {low} with a matching kids' version, sold in {who}'s sizes.",
                        _TRUE[(kk + i + 2) % 6], "Mini-Me", f"mini-me {low}")  # fmt: skip
                else:
                    add(3, i, f"{root} {a} {noun}",
                        f"A {who}'s {low} in the {a.lower()}, sold in {who}'s sizes.",
                        _TRUE[(kk + i + 2) % 6], a, f"{a.split()[0].lower()} {low}")  # fmt: skip
                # 4: a material or feature named, and absent.
                f = _ABSENT[ptype][i]
                add(4, i, f"{root} {f} {noun}",
                    f"A {low} with {_article(f)} {f.lower()} finish, made in acrylic blend.",
                    _TRUE[(kk + i + 3) % 6], f, f"{f.split('-')[0].lower()} {low}")  # fmt: skip
                # 5: the title gives a fancy name, the description the shade.
                s = _SHADES[(kk + i) % 4]
                add(5, i, f"{root} {_FANCY[(kk + i) % 6]} {noun}",
                    f"A {low} in soft {s.lower()}, {_TAIL[ptype]}.", s,
                    _FANCY[(kk + i) % 6], f"{s.lower()} {low}")  # fmt: skip
                # 6: an incidental word in a short title: a range name.
                rg, gloss, word = place_range(kk + i * 2)
                add(6, i, f"{root} {rg} {noun}",
                    f"From the {rg} range, named for {gloss}; the {low} itself is "
                    f"{_TRUE[(kk + i + 4) % 6].lower()}.", _TRUE[(kk + i + 4) % 6], word, word,
                    extra=(_a("range", "Range", rg),))  # fmt: skip
                # 7: an invented brand holding a color or category word.
                brand = NEW_BRANDS[i]
                add(7, i, f"{root} {brand} {noun}",
                    f"{_an(_BRAND_TRUE[brand]).capitalize()} {low} from {brand}; the name is the "
                    f"brand's, not the color.", _BRAND_TRUE[brand], brand,
                    f"{_BRAND_QUERY[brand]} {low}")  # fmt: skip
    return rows, table


_DECOY_ROWS, _TABLE = _decoys()
_FLOOR_ROWS = _floor_rows()
_ALL_ROWS: tuple[LRow, ...] = (*_FLOOR_ROWS, *_DECOY_ROWS)
#: Knitted Top is a type of its own with a spec file (``type_specs/knitted_top.py``, gen#351): the
#: registry builds its rows, so :data:`ROWS` holds the jumpers and cardigans only.
TOP_ROWS: tuple[LRow, ...] = tuple(r for r in _ALL_ROWS if r.product_type == _TOP)
ROWS: tuple[LRow, ...] = tuple(r for r in _ALL_ROWS if r.product_type != _TOP)
#: Every decoy, with its class, word, query and policy: the docs table is generated from it.
TABLE: tuple[Decoy, ...] = tuple(_TABLE)


def docs() -> list[dict]:
    """Every row's catalog document, floor rows then decoys."""
    return [r.doc() for r in ROWS]


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: ``main_colors.complete`` leaves them as authored."""
    return frozenset(f"BRD-{d.code}" for d in TABLE)


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
