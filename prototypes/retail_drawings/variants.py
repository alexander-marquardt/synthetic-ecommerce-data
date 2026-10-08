"""The retail variant model of gen#125 (prototype, round 4).

A variant is a SKU, size included. One document is one style x colourway
(x leg length for jeans, where shoppers filter on it); its sizes are held as
parallel ``size_uk`` / ``size_eu`` / ``size_us`` arrays, so a doc's
``sku_count`` is the length of those arrays (1 for a sizeless doc). Every doc
of one style shares a ``variant_group``.

Two kinds of family:

* **Deep** families cross rule-bound axes. :data:`JEANS` crosses named fit x
  rise x leg length x wash x waist size, with :func:`jeans_size_valid` saying
  which leg lengths a size comes in. :data:`BRAS` cross band x cup, keeping
  only the combinations :func:`bra_size_valid` allows.
* **Shallow** families are one hand list per row: :data:`BEDDING` lists bed
  sizes and colours, :data:`BEAUTY` lists shades.

Self-contained: standard library plus :mod:`departments` only, so it can move
with the retail domain. Every brand, line and shade name is invented.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from departments import check as check_departments

Colourway = tuple[str, str, str, str]  # (name, pattern, base hex, accent hex)


def cw(name: str, base: str, pattern: str = "solid", accent: str = "#333333") -> Colourway:
    return (name, pattern, base, accent)


def attr(key: str, name: str, value, unit_code: str | None = None, canonical=None) -> dict:
    """One ``{key, name, value[, unit_code, value_canonical]}`` attribute, as round 3."""
    a = {"key": key, "name": name, "value": str(value)}
    if unit_code is not None:
        a["unit_code"] = unit_code
        a["value_canonical"] = float(value if canonical is None else canonical)
    return a


def drawing(shape: str, colour: Colourway, label: str | None = None, **params) -> dict:
    _, pattern, base, accent = colour
    out = {
        "shape": shape,
        "pattern": pattern,
        "base": base,
        "accent": accent,
        "third": "#f2d14b",
        "label": label,
    }
    if params:
        out["params"] = params
    return out


# ==========================================================================
# Jeans: named fit x rise x leg length x wash x waist size
# ==========================================================================

WASHES = {
    "Rinse": "#1f2a44",
    "Dark Indigo": "#25345a",
    "Indigo": "#34466e",
    "Mid Wash": "#4a6a94",
    "Vintage Blue": "#6283ad",
    "Light Wash": "#8fb0cf",
    "Bleach Wash": "#c4d6e6",
    "Black": "#2a2a2e",
    "Washed Black": "#4a4a50",
    "Grey": "#8a8c90",
    "Ecru": "#efe7d4",
    "White": "#ffffff",
}

#: UK dress size -> (UK, EU, US); UK 4-26.
WOMENS_WAIST = {uk: (str(uk), str(uk + 28), str(uk - 4)) for uk in range(4, 27, 2)}
#: Waist in inches -> (UK, EU, US); W28-42, odd waists to 33.
MENS_WAIST = {
    w: (str(w), str(w + 16), str(w)) for w in (28, 29, 30, 31, 32, 33, 34, 36, 38, 40, 42)
}

#: Leg length -> inside leg in inches.
WOMENS_LEGS = {"Petite": 28, "Regular": 30, "Long": 32, "Extra Long": 34}
MENS_LEGS = {"Short": 30, "Regular": 32, "Long": 34, "Extra Long": 36}

#: (audience, leg length) -> the sizes it is cut in. A pair missing here is
#: refused, and a leg length comes only in these sizes.
JEANS_LENGTH_RULES: dict[tuple[str, str], Callable[[int], bool]] = {
    ("Womens", "Petite"): lambda uk: uk <= 18,
    ("Womens", "Regular"): lambda uk: True,
    ("Womens", "Long"): lambda uk: uk >= 8,
    ("Womens", "Extra Long"): lambda uk: 10 <= uk <= 22,
    ("Mens", "Short"): lambda w: w <= 40,
    ("Mens", "Regular"): lambda w: True,
    ("Mens", "Long"): lambda w: w >= 29,
    ("Mens", "Extra Long"): lambda w: 32 <= w <= 40,
}


def jeans_size_valid(audience: str, length: str, size: int) -> bool:
    """Whether a jean of ``audience`` in leg ``length`` is cut in ``size``."""
    return JEANS_LENGTH_RULES[(audience, length)](size)


@dataclass(frozen=True)
class JeanStyle:
    code: str
    line: str  # the named fit, "the Harrow"
    brand: str
    audience: str  # Womens | Mens
    leg_fit: str  # a kit_garments.FITS key, title-cased
    rise: str  # Low | Mid | High
    washes: tuple[str, ...]
    lengths: tuple[str, ...]
    first: int  # smallest size (UK dress size or waist)
    last: int
    price: float
    fabric: str = "98% Cotton, 2% Elastane"

    family = "Jeans"
    department = ("Clothing",)

    @property
    def title(self) -> str:
        return f"The {self.line} {self.rise} Rise {self.leg_fit} Jeans"

    def chart(self) -> dict[int, tuple[str, str, str]]:
        return WOMENS_WAIST if self.audience == "Womens" else MENS_WAIST

    def sizes(self, length: str) -> list[tuple[str, str, str]]:
        return [
            row
            for size, row in self.chart().items()
            if self.first <= size <= self.last and jeans_size_valid(self.audience, length, size)
        ]

    def axes(self):
        for wash in self.washes:
            for length in self.lengths:
                yield wash, length

    def doc(self, wash: str, length: str) -> dict:
        legs = WOMENS_LEGS if self.audience == "Womens" else MENS_LEGS
        who = "Women" if self.audience == "Womens" else "Men"
        suffix = "" if length == "Regular" else f", {length}"
        colour = cw(wash, WASHES[wash])
        return {
            "title": f"{self.title}, {wash}{suffix}",
            "brand": self.brand,
            "department": list(self.department),
            "category_path": [who, "Jeans", f"{self.leg_fit} Jeans"],
            "price": self.price,
            "description": (
                f"The {self.line} is our {self.rise.lower()} rise {self.leg_fit.lower()} fit, "
                f"cut from {self.fabric.lower()} denim in a {wash.lower()} finish with a "
                f"{legs[length]} inch inside leg, five pockets and a zip fly."
            ),
            **_size_arrays(self.sizes(length)),
            "attributes": [
                attr("colour", "Colour", wash),
                attr("wash", "Wash", wash),
                attr("pattern", "Pattern", "Plain"),
                attr("fabric", "Fabric", self.fabric),
                attr("line", "Named fit", self.line),
                attr("leg_fit", "Leg fit", self.leg_fit),
                attr("rise", "Rise", self.rise),
                attr("length", "Length", length),
                attr("inside_leg", "Inside leg", legs[length], "INH"),
                attr("audience", "Audience", self.audience),
            ],
            "drawing": drawing(
                "trousers",
                colour,
                fit=self.leg_fit.lower().replace(" ", "_"),
                rise=self.rise.lower(),
            ),
        }


_W12 = tuple(WASHES)
JEANS = (
    JeanStyle("HARROW", "Harrow", "Ottery Denim", "Womens", "Skinny", "High", _W12,
              ("Petite", "Regular", "Long", "Extra Long"), 4, 26, 32.0),
    JeanStyle("BRINDLE", "Brindle", "Ottery Denim", "Womens", "Straight", "High", _W12[:8],
              ("Petite", "Regular", "Long"), 6, 24, 35.0),
    JeanStyle("CORVEY", "Corvey", "Ferrowick Denim", "Womens", "Wide Leg", "High",
              ("Rinse", "Mid Wash", "Light Wash", "Ecru", "Black", "White"),
              ("Petite", "Regular", "Long"), 6, 22, 39.0),
    JeanStyle("MARDALE", "Mardale", "Ottery Denim", "Womens", "Bootcut", "Mid",
              ("Indigo", "Mid Wash", "Vintage Blue", "Black", "Grey"),
              ("Petite", "Regular", "Long"), 6, 20, 30.0),
    JeanStyle("PENHALLOW", "Penhallow", "Ferrowick Denim", "Womens", "Barrel", "High",
              ("Rinse", "Light Wash", "Ecru", "Washed Black", "Vintage Blue"),
              ("Regular", "Long"), 6, 18, 45.0, "100% Cotton"),
    JeanStyle("QUENBY", "Quenby", "Ottery Denim", "Womens", "Slim", "Mid",
              ("Dark Indigo", "Mid Wash", "Light Wash", "Black", "Grey", "White"),
              ("Petite", "Regular", "Long"), 6, 20, 28.0),
    JeanStyle("ROOKLEY", "Rookley", "Ferrowick Denim", "Womens", "Flared", "High",
              ("Indigo", "Vintage Blue", "Black", "Ecru"),
              ("Regular", "Long", "Extra Long"), 8, 22, 42.0),
    JeanStyle("TOLLAND", "Tolland", "Ferrowick Denim", "Mens", "Slim", "Mid", _W12[:10],
              ("Short", "Regular", "Long", "Extra Long"), 28, 42, 38.0),
    JeanStyle("WEXCOMBE", "Wexcombe", "Ottery Denim", "Mens", "Straight", "Mid", _W12[:8],
              ("Short", "Regular", "Long"), 28, 42, 34.0),
    JeanStyle("ASHLOW", "Ashlow", "Ferrowick Denim", "Mens", "Skinny", "Low",
              ("Rinse", "Mid Wash", "Light Wash", "Black", "Washed Black", "Grey"),
              ("Regular", "Long"), 28, 42, 36.0),
    JeanStyle("KELDEN", "Kelden", "Ottery Denim", "Mens", "Carrot", "Mid",
              ("Dark Indigo", "Mid Wash", "Vintage Blue", "Black", "Ecru"),
              ("Short", "Regular", "Long"), 28, 42, 40.0, "100% Cotton"),
    JeanStyle("FENNICK", "Fennick", "Ferrowick Denim", "Mens", "Bootcut", "Mid",
              ("Indigo", "Mid Wash", "Black"),
              ("Regular", "Long"), 28, 42, 32.0),
)  # fmt: skip


# ==========================================================================
# Bras: band x cup, valid combinations only
# ==========================================================================

BANDS = (28, 30, 32, 34, 36, 38, 40, 42, 44, 46)
#: UK cup, then its EU and US names (one row per cup, so the systems never disagree).
CUPS = (
    ("AA", "AA", "AA"),
    ("A", "A", "A"),
    ("B", "B", "B"),
    ("C", "C", "C"),
    ("D", "D", "D"),
    ("DD", "E", "DD"),
    ("E", "F", "DDD"),
    ("F", "G", "G"),
    ("FF", "H", "H"),
    ("G", "I", "I"),
    ("GG", "J", "J"),
    ("H", "K", "K"),
    ("HH", "L", "L"),
    ("J", "M", "M"),
)
UK_CUPS = tuple(c[0] for c in CUPS)


def eu_band(band: int) -> int:
    return 60 + (band - 28) // 2 * 5


def _cup(c: str) -> int:
    return UK_CUPS.index(c)


#: (rule, test): a band x cup pair is cut only if every test passes.
BRA_RULES: tuple[tuple[str, Callable[[int, str], bool]], ...] = (
    ("AA cups only on bands 28-34", lambda b, c: c != "AA" or b <= 34),
    ("bands 40 and up start at a B cup", lambda b, c: b < 40 or _cup(c) >= _cup("B")),
    ("FF cups and up only on bands 30 and up", lambda b, c: _cup(c) < _cup("FF") or b >= 30),
    ("HH and J cups only on bands 30-40", lambda b, c: _cup(c) < _cup("HH") or 30 <= b <= 40),
)


def bra_size_valid(band: int, cup: str) -> bool:
    return band in BANDS and cup in UK_CUPS and all(ok(band, cup) for _, ok in BRA_RULES)


@dataclass(frozen=True)
class BraStyle:
    code: str
    line: str
    brand: str
    kind: str  # Balcony, Plunge, ...
    bands: tuple[int, int]
    cups: tuple[str, str]
    colourways: tuple[Colourway, ...]
    price: float
    wired: bool = True
    fabric: str = "Recycled Polyamide, Elastane"

    family = "Bras"
    department = ("Lingerie & Nightwear",)

    @property
    def title(self) -> str:
        wire = "Underwired" if self.wired else "Non-Wired"
        return f"{self.line} {wire} {self.kind} Bra"

    def size_rows(self) -> list[tuple[str, str, str]]:
        lo, hi = _cup(self.cups[0]), _cup(self.cups[1])
        return [
            (f"{b}{uk}", f"{eu_band(b)}{eu}", f"{b}{us}")
            for b in BANDS
            if self.bands[0] <= b <= self.bands[1]
            for uk, eu, us in CUPS[lo : hi + 1]
            if bra_size_valid(b, uk)
        ]

    def axes(self):
        yield from ((c,) for c in self.colourways)

    def doc(self, colour: Colourway) -> dict:
        wire = "underwired" if self.wired else "non-wired"
        return {
            "title": f"{self.title}, {colour[0]}",
            "brand": self.brand,
            "department": list(self.department),
            "category_path": ["Women", "Lingerie", "Bras", f"{self.kind} Bras"],
            "price": self.price,
            "description": (
                f"The {self.line} {self.kind.lower()} bra: {wire}, with adjustable straps and a "
                f"three-row hook and eye back, in {self.fabric.lower()}."
            ),
            **_size_arrays(self.size_rows()),
            "attributes": [
                attr("colour", "Colour", colour[0]),
                attr("pattern", "Pattern", "Plain" if colour[1] == "solid" else colour[1].title()),
                attr("fabric", "Fabric", self.fabric),
                attr("line", "Line", self.line),
                attr("bra_style", "Bra style", self.kind),
                attr("wiring", "Wiring", "Underwired" if self.wired else "Non-Wired"),
                attr("audience", "Audience", "Womens"),
            ],
            "drawing": drawing("bra", colour),
        }


BLACK, WHITE, NUDE = cw("Black", "#2a2a2e"), cw("White", "#ffffff"), cw("Almond", "#d9b79a")
BRAS = (
    BraStyle("SORREL", "Sorrel", "Bramblewood", "Balcony", (30, 40), ("A", "G"),
             (BLACK, WHITE, NUDE, cw("Claret", "#7a1f35"), cw("Sage", "#9bb08f"),
              cw("Blush Spot", "#e8b4b0", "polka", "#2a2a2e")), 24.0),
    BraStyle("LINNET", "Linnet", "Bramblewood", "Plunge", (28, 38), ("AA", "F"),
             (BLACK, NUDE, cw("Cobalt", "#2b4fa8"), cw("Rose", "#d98a96")), 22.0),
    BraStyle("FARNLEY", "Farnley", "Saltmarsh", "Full Cup", (32, 46), ("B", "J"),
             (BLACK, WHITE, NUDE), 28.0),
    BraStyle("HALDEN", "Halden", "Saltmarsh", "T-Shirt", (30, 40), ("A", "GG"),
             (BLACK, WHITE, NUDE, cw("Mocha", "#7b5a45"), cw("Navy", "#26365c"),
              cw("Grey Marl", "#9a9ca0"), cw("Ivory", "#f3ecd9"),
              cw("Breton", "#ffffff", "stripe", "#26365c")), 20.0),
    BraStyle("THORNBY", "Thornby", "Bramblewood", "Soft Cup", (30, 42), ("A", "E"),
             (BLACK, NUDE), 16.0, wired=False),
    BraStyle("KINVER", "Kinver", "Saltmarsh", "Sports", (30, 44), ("A", "G"),
             (BLACK, cw("Teal", "#2e7d7a"), cw("Coral", "#ef7b62")), 30.0, wired=False,
             fabric="Recycled Polyester, Elastane"),
    BraStyle("ELSDON", "Elsdon", "Saltmarsh", "Minimiser", (34, 46), ("C", "H"),
             (BLACK, NUDE), 26.0),
    BraStyle("BRAYFORD", "Brayford", "Bramblewood", "Strapless", (28, 38), ("A", "F"),
             (NUDE,), 25.0),
    BraStyle("PELLOW", "Pellow", "Saltmarsh", "Nursing", (32, 42), ("B", "G"),
             (BLACK, WHITE), 21.0, wired=False, fabric="Cotton, Elastane"),
    BraStyle("ROSEDENE", "Rosedene", "Bramblewood", "Lace Balcony", (28, 36), ("AA", "GG"),
             (BLACK, WHITE, cw("Wine", "#5e1a2c"), cw("Lilac", "#b9a3d0"),
              cw("Leopard", "#d9a95b", "leopard", "#2a2a2e")), 27.0),
)  # fmt: skip


# ==========================================================================
# Shallow rows: one hand list per row
# ==========================================================================

#: Bed and pillow sizes -> (UK, EU, US).
BED = {
    "Single": ("Single", "90 x 200 cm", "Twin"),
    "Small Double": ("Small Double", "120 x 190 cm", "Three Quarter"),
    "Double": ("Double", "140 x 200 cm", "Full"),
    "King": ("King", "150 x 200 cm", "Queen"),
    "Super King": ("Super King", "180 x 200 cm", "King"),
    "Standard Pillow": ("Standard", "50 x 75 cm", "Standard"),
    "King Pillow": ("King", "50 x 90 cm", "King"),
    "Square Pillow": ("Square", "65 x 65 cm", "Euro"),
}
BEDS = ("Single", "Double", "King", "Super King")
PILLOWS = ("Standard Pillow", "King Pillow", "Square Pillow")


@dataclass(frozen=True)
class ShallowRow:
    code: str
    family: str  # Bedding | Beauty
    title: str
    brand: str
    path: tuple[str, ...]
    price: float
    shape: str
    description: str
    colourways: tuple[Colourway, ...]
    sizes: tuple[str, ...] = ()  # keys of BED; () for a sizeless product
    extra: tuple[tuple[str, str, str], ...] = ()  # (key, name, value)
    label: str | None = None
    axis: str = "Colour"  # what the colourway is called: Colour | Shade

    @property
    def department(self) -> tuple[str, ...]:
        return ("Home",) if self.family == "Bedding" else ("Beauty",)

    def axes(self):
        yield from ((c,) for c in self.colourways)

    def doc(self, colour: Colourway) -> dict:
        out = {
            "title": f"{self.title}, {colour[0]}",
            "brand": self.brand,
            "department": list(self.department),
            "category_path": list(self.path),
            "price": self.price,
            "description": self.description,
        }
        if self.sizes:
            out.update(_size_arrays([BED[s] for s in self.sizes]))
        out["attributes"] = [
            attr(self.axis.lower(), self.axis, colour[0]),
            *(attr(k, n, v) for k, n, v in self.extra),
        ]
        out["drawing"] = drawing(self.shape, colour, self.label)
        return out


_WHITE = (cw("White", "#ffffff"),)
_PLAIN = (
    cw("White", "#ffffff"),
    cw("Oyster", "#e4ddd0"),
    cw("Slate", "#6f7c86"),
    cw("Sage", "#9bb08f"),
    cw("Ochre", "#d1a03c"),
    cw("Navy", "#26365c"),
)
BEDDING = (
    ShallowRow("DUVHOL", "Bedding", "Hollowfibre 10.5 Tog Duvet", "Quillon Sleep",
               ("Home", "Bedding", "Duvets"), 35.0, "duvet",
               "An all-season duvet with a soft hollowfibre fill and a cotton-rich cover. "
               "Machine washable at 40 degrees.",
               _WHITE, BEDS, (("tog", "Tog", "10.5"), ("filling", "Filling", "Hollowfibre")),
               "10.5 Tog"),
    ShallowRow("DUVDWN", "Bedding", "Duck Feather and Down 13.5 Tog Duvet", "Quillon Sleep",
               ("Home", "Bedding", "Duvets"), 79.0, "duvet",
               "A warm winter duvet filled with duck feather and down, box stitched so the "
               "filling stays put.",
               _WHITE, ("Double", "King", "Super King"),
               (("tog", "Tog", "13.5"), ("filling", "Filling", "Duck Feather & Down")), "13.5 Tog"),
    ShallowRow("COVPER", "Bedding", "Percale 200 Thread Count Duvet Cover", "Brackenmere Home",
               ("Home", "Bedding", "Duvet Covers"), 30.0, "duvet",
               "Crisp cotton percale with a hidden button closure and corner ties.",
               _PLAIN, BEDS, (("thread_count", "Thread count", "200"),)),
    ShallowRow("COVPRT", "Bedding", "Printed Cotton Duvet Cover", "Brackenmere Home",
               ("Home", "Bedding", "Duvet Covers"), 34.0, "duvet",
               "Soft washed cotton in a woven print, with a button closure.",
               (cw("Ticking Stripe", "#ffffff", "stripe", "#26365c"),
                cw("Red Gingham", "#ffffff", "gingham", "#c8312e"),
                cw("Navy Spot", "#26365c", "polka", "#ffffff")),
               ("Double", "King", "Super King")),
    ShallowRow("PILMIC", "Bedding", "Microfibre Pillow Pair", "Quillon Sleep",
               ("Home", "Bedding", "Pillows"), 18.0, "pillow",
               "A pair of medium-support pillows with a hypoallergenic microfibre fill.",
               _WHITE, ("Standard Pillow", "King Pillow")),
    ShallowRow("PCSPER", "Bedding", "Percale Pillowcase Pair", "Brackenmere Home",
               ("Home", "Bedding", "Pillowcases"), 12.0, "pillow",
               "Housewife-style pillowcases in crisp cotton percale.",
               _PLAIN, PILLOWS),
    ShallowRow("TOPMEM", "Bedding", "Memory Foam 5cm Mattress Topper", "Quillon Sleep",
               ("Home", "Bedding", "Mattress Toppers"), 65.0, "mattress_topper",
               "A 5 cm memory foam topper with elasticated corner straps.",
               _WHITE, BEDS, (("depth", "Depth", "5 cm"),)),
    ShallowRow("PROQLT", "Bedding", "Quilted Waterproof Mattress Protector", "Quillon Sleep",
               ("Home", "Bedding", "Mattress Protectors"), 22.0, "mattress_protector",
               "A quilted protector with a waterproof backing and deep elasticated skirt.",
               _WHITE, ("Single", "Small Double", "Double", "King", "Super King")),
)  # fmt: skip


def _shades(names: str, hexes: str) -> tuple[Colourway, ...]:
    """A hand list of shade names (``;``-separated) and their hex colours."""
    ns, hs = [n.strip() for n in names.split(";")], hexes.split()
    if len(ns) != len(hs):
        raise ValueError(f"{len(ns)} shade names but {len(hs)} colours")
    return tuple(cw(n, f"#{h}", "solid", "#2b2b30") for n, h in zip(ns, hs, strict=True))


#: Foundation tones: depth 1-13, cool / neutral / warm, plus one deepest tone.
_TONES = "1C 1N 1W 2C 2N 2W 3C 3N 3W 4C 4N 4W 5C 5N 5W 6C 6N 6W 7C 7N 7W 8C 8N 8W " \
         "9C 9N 9W 10C 10N 10W 11C 11N 11W 12C 12N 12W 13C 13N 13W 14N"  # fmt: skip


def _tone_hex(tone: str) -> str:
    depth, under = int(tone[:-1]), tone[-1]
    t = (depth - 1) / 13
    fair, deep = (243, 217, 196), (74, 47, 33)
    rgb = [round(a + (b - a) * t) for a, b in zip(fair, deep, strict=True)]
    shift = {"C": (4, -2, 4), "N": (0, 0, 0), "W": (6, 2, -8)}[under]
    return "".join(f"{max(0, min(255, c + s)):02x}" for c, s in zip(rgb, shift, strict=True))


def _tones(tones: str) -> tuple[Colourway, ...]:
    return tuple(cw(t, f"#{_tone_hex(t)}", "solid", "#e9e4dc") for t in tones.split())


BEAUTY = (
    ShallowRow("LIPSAT", "Beauty", "Kestlewood Satin Lipstick", "Kestlewood Cosmetics",
               ("Beauty", "Make-Up", "Lips", "Lipstick"), 14.0, "lipstick",
               "A creamy satin lipstick with a comfortable, buildable finish.",
               _shades(
                   "Pale Petal; Bare Linen; Dusk Rose; Tea Rose; Fig Jam; Mulberry; Brick Kiln; "
                   "Toffee Apple; Cinder Red; Post Box; Poppy Field; Coral Reef; Watermelon; "
                   "Hot Fuchsia; Orchid Bloom; Plum Wine; Bramble; Cocoa Bean; Hazelnut; "
                   "Nude Shell; Peach Melba; Terracotta; Rust Leaf; Damson",
                   "e8b8b0 d9a99a c97f84 c98f8f 7d2d3d 6b2340 9c3b2a b8322f 8f1f1f c8102e "
                   "d8392b ef7b62 f06a73 d6267a b25ab0 5e1a2c 4b2238 5a3426 8a5a44 c99a86 "
                   "f3a683 b65c3a 8f3f22 5b2347"),
               axis="Shade", extra=(("finish", "Finish", "Satin"),)),
    ShallowRow("LIPMAT", "Beauty", "Velvet Matte Lipstick", "Kestlewood Cosmetics",
               ("Beauty", "Make-Up", "Lips", "Lipstick"), 16.0, "lipstick",
               "A long-wearing matte lipstick that will not dry the lips.",
               _shades(
                   "Velvet Brick; Velvet Rosewood; Velvet Scarlet; Velvet Mauve; Velvet Cocoa; "
                   "Velvet Berry; Velvet Nude; Velvet Coral; Velvet Plum; Velvet Cherry; "
                   "Velvet Taupe; Velvet Ruby",
                   "93402e 9c5b5b c41e3a a7738a 6b4130 7a1f4a b88a7a e3704f 5c2340 9e1b32 "
                   "8c7268 9b111e"),
               axis="Shade", extra=(("finish", "Finish", "Matte"),)),
    ShallowRow("BALTNT", "Beauty", "Tinted Lip Balm", "Velling Apothecary",
               ("Beauty", "Make-Up", "Lips", "Lip Balm"), 8.0, "lipstick",
               "A nourishing balm with a sheer wash of colour and shea butter.",
               _shades("Sheer Rose; Sheer Berry; Sheer Peach; Sheer Red; Clear",
                       "e2a3a6 a3485f f2b38f c8423f f4ece4"),
               axis="Shade", extra=(("finish", "Finish", "Sheer"),)),
    ShallowRow("FNDFTH", "Beauty", "Featherwear Liquid Foundation 30ml", "Kestlewood Cosmetics",
               ("Beauty", "Make-Up", "Face", "Foundation"), 28.0, "bottle",
               "A lightweight medium-coverage foundation with a natural satin finish.",
               _tones(_TONES), label="Foundation", axis="Shade",
               extra=(("coverage", "Coverage", "Medium"),)),
    ShallowRow("FNDSRM", "Beauty", "Skin Serum Foundation 30ml", "Velling Apothecary",
               ("Beauty", "Make-Up", "Face", "Foundation"), 32.0, "bottle",
               "A serum-light foundation with hyaluronic acid for a dewy, sheer finish.",
               _tones("1N 1W 2C 2N 3N 3W 4C 4N 5N 5W 6C 6N 7N 7W 8N 9N 10N 11W 12N 13N"),
               label="Serum", axis="Shade", extra=(("coverage", "Coverage", "Sheer"),)),
    ShallowRow("TNTMST", "Beauty", "Tinted Moisturiser SPF 20", "Velling Apothecary",
               ("Beauty", "Skincare", "Moisturisers"), 22.0, "moisturiser_jar",
               "A tinted daily moisturiser with SPF 20 and a light, even glow.",
               _tones("1N 2N 3N 5N 7N 9N 11N 13N"), label="SPF 20", axis="Shade",
               extra=(("spf", "SPF", "20"),)),
)  # fmt: skip


# ==========================================================================
# Docs and the SKU report
# ==========================================================================

FAMILIES: dict[str, tuple] = {"Jeans": JEANS, "Bras": BRAS, "Bedding": BEDDING, "Beauty": BEAUTY}
DEEP = ("Jeans", "Bras")


def _size_arrays(rows: list[tuple[str, str, str]]) -> dict:
    if not rows:
        raise ValueError("a sized style with no valid size")
    return {
        "size_uk": [r[0] for r in rows],
        "size_eu": [r[1] for r in rows],
        "size_us": [r[2] for r in rows],
    }


def style_docs(family: str, style) -> list[dict]:
    """Every doc of one style, with its ``variant_group`` and ``sku_count``."""
    group = f"{family[:3].upper()}-{style.code}"
    out = []
    for n, axis in enumerate(style.axes(), 1):
        rec = style.doc(*axis)
        check_departments(rec["department"], rec["title"])
        out.append(
            {
                "product_id": f"{group}-{n:02d}",
                "sku": f"{group.replace('-', '')}{n:02d}",
                "variant_group": group,
                "sku_count": len(rec.get("size_uk", ())) or 1,
                **rec,
                "collections": [],
                "currency": "GBP",
            }
        )
    return out


def docs() -> list[dict]:
    """Every variant doc of every family."""
    return [d for fam, styles in FAMILIES.items() for s in styles for d in style_docs(fam, s)]


def sku_counts() -> dict[str, dict[str, int]]:
    """family -> style code -> SKU count (the sum of its docs' ``sku_count``)."""
    return {
        fam: {s.code: sum(d["sku_count"] for d in style_docs(fam, s)) for s in styles}
        for fam, styles in FAMILIES.items()
    }


def sku_report() -> str:
    lines = [f"{'family':<8} {'kind':<7} styles  docs   SKUs  min  max"]
    for fam, counts in sku_counts().items():
        n_docs = sum(len(style_docs(fam, s)) for s in FAMILIES[fam])
        v = list(counts.values())
        kind = "deep" if fam in DEEP else "shallow"
        lines.append(
            f"{fam:<8} {kind:<7} {len(v):>6} {n_docs:>5} {sum(v):>6} {min(v):>4} {max(v):>4}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(sku_report())
    for fam, counts in sku_counts().items():
        print(fam, counts)
