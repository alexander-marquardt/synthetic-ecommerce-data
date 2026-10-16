"""Footwear of gen#125 (prototype): thirty-one styles across women's, men's and kids'.

One :class:`FootwearStyle` is one product page and one document (the gen#125
ruling): its SKUs are color x width x size, nested. A size is held in one
field per size system, ``size_uk``, ``size_eu`` and ``size_us``, all three
read from ONE chart row of the style's audience (:data:`CHARTS`), so they can
never disagree. Slippers add a letter ``size`` (S, M, L) whose row gives each
system's range ("5-6"). ``width`` is a selector too: Standard, Wide and
Extra Wide for adults, the F, G and H fittings for kids' school shoes; a
non-standard width is cut only in the sizes ``wide`` names.

Half sizes are cut only where a shoe really comes in them (trainers, running
shoes, brogues, loafers), never in wellies, slippers or kids' sizes. Each
color names its upper material, so the drawing (:mod:`kit_footwear`, shape
``shoe``) and the ``upper_material`` facet agree. The safety boot is the
workwear bridge: department Footwear and Workwear & PPE, rated S3.

:data:`BOOTS` is a distractor row of the "Complements and accessories" class
(:mod:`distractors`): a car boot organiser, boot polish and welly boot socks
say *boot* more often than a boot does. :func:`catalog` is the text corpus it
is checked over. Every brand, line and style name is invented.
"""

# ruff: noqa: E501 -- one style per block reads better than wrapped data (prototype only).

from __future__ import annotations

from dataclasses import dataclass

import distractors as dz
from class_model import BRAND_OWNER, COLOR_FAMILIES, _digest
from colorwords import plain
from departments import check as check_departments
from promotion import values as promotion_values
from real_classes import badges
from variants import Color, attr, cw, drawing, product, swatch

# ==========================================================================
# Size charts: one row per size, (UK, EU, US)
# ==========================================================================

Row3 = tuple[str, str, str]


def _n(x: float) -> str:
    return f"{x:g}"


def _chart(lo: int, hi: int, eu: int, us: int) -> dict[str, Row3]:
    """Whole and half UK sizes ``lo`` to ``hi``; EU and US are UK plus a fixed step."""
    sizes = [lo + n / 2 for n in range(2 * (hi - lo) + 1)]
    return {_n(uk): (_n(uk), _n(uk + eu), _n(uk + us)) for uk in sizes}


#: Women's: UK 5 = EU 38 = US 7.
WOMEN = _chart(2, 9, 33, 2)
#: Men's: UK 9 = EU 43 = US 10.
MEN = _chart(5, 14, 34, 1)
#: Kids': infant sizes run to 13, then junior sizes start again at 1; US
#: child (C) sizes, then youth (Y). Whole sizes only.
KIDS: dict[str, Row3] = {
    uk: (uk, eu, us)
    for uk, eu, us in (
        ("4 Infant", "20", "4.5C"), ("5 Infant", "21", "5.5C"), ("6 Infant", "23", "6.5C"),
        ("7 Infant", "24", "7.5C"), ("8 Infant", "25", "8.5C"), ("9 Infant", "27", "9.5C"),
        ("10 Infant", "28", "10.5C"), ("11 Infant", "29", "11.5C"),
        ("12 Infant", "30", "12.5C"), ("13 Infant", "32", "13.5C"),
        ("1 Junior", "33", "1.5Y"), ("2 Junior", "34", "2.5Y"), ("3 Junior", "35", "3.5Y"),
        ("4 Junior", "37", "4.5Y"), ("5 Junior", "38", "5.5Y"), ("6 Junior", "39", "6.5Y"),
    )
}  # fmt: skip
#: Slippers come in letter sizes, each spanning two shoe sizes per system.
SLIPPERS_WOMEN = {"S": ("3-4", "36-37", "5-6"), "M": ("5-6", "38-39", "7-8"),
                  "L": ("7-8", "40-41", "9-10")}  # fmt: skip
SLIPPERS_MEN = {"M": ("7-8", "41-42", "8-9"), "L": ("9-10", "43-44", "10-11"),
                "XL": ("11-12", "45-46", "12-13")}  # fmt: skip
CHARTS: dict[str, dict[str, Row3]] = {
    "women": WOMEN, "men": MEN, "kids": KIDS,
    "slippers_women": SLIPPERS_WOMEN, "slippers_men": SLIPPERS_MEN,
}  # fmt: skip


def run(lo: str, hi: str, halves_to: float | None = None, chart: str = "women") -> tuple:
    """The chart's sizes ``lo`` to ``hi`` in order, half sizes only up to ``halves_to``."""
    keys = list(CHARTS[chart])
    out = keys[keys.index(lo) : keys.index(hi) + 1]
    return tuple(
        s for s in out
        if not s.endswith(".5") or (halves_to is not None and float(s) <= halves_to)
    )  # fmt: skip


def chart_of(doc: dict) -> str:
    """The :data:`CHARTS` key a footwear doc's sizes are read from."""
    root = {v: k for k, v in ROOTS.items()}[doc["category_path"][0]]
    return f"slippers_{root}" if "size" in doc["size_options"] else root


# ==========================================================================
# Vocabularies and kinds
# ==========================================================================

MATERIALS = ("leather", "suede", "nubuck", "patent", "canvas", "synthetic", "mesh",
             "rubber", "jute")  # fmt: skip
CLOSURES = ("Lace-Up", "Slip-On", "Zip", "Buckle", "Elastic Gusset", "Hook & Loop",
            "Pull-On", "Ankle Strap", "Slingback")  # fmt: skip
#: kind -> (product type, category nodes under the audience root, heel height
#: in mm, the :mod:`kit_footwear` kind that draws it).
TYPES: dict[str, tuple[str, tuple[str, ...], int, str]] = {
    "trainer": ("Trainers", ("Shoes", "Trainers"), 30, "trainer"),
    "running": ("Running Shoes", ("Shoes", "Sports Shoes", "Running Shoes"), 32, "running"),
    "ankle_boot": ("Ankle Boots", ("Shoes", "Boots", "Ankle Boots"), 60, "ankle_boot"),
    "chelsea": ("Chelsea Boots", ("Shoes", "Boots", "Chelsea Boots"), 30, "chelsea"),
    "chukka": ("Chukka Boots", ("Shoes", "Boots", "Chukka Boots"), 25, "chukka"),
    "knee_boot": ("Knee High Boots", ("Shoes", "Boots", "Knee High Boots"), 45, "knee_boot"),
    "walking_boot": ("Walking Boots", ("Shoes", "Boots", "Walking Boots"), 35, "walking_boot"),
    "safety_boot": ("Safety Boots", ("Shoes", "Boots", "Safety Boots"), 35, "safety_boot"),
    "welly": ("Wellies", ("Shoes", "Wellies"), 25, "welly"),
    "sandal": ("Sandals", ("Shoes", "Sandals"), 15, "sandal"),
    "court": ("Court Shoes", ("Shoes", "Heels", "Court Shoes"), 95, "court"),
    "block_heel": ("Block Heels", ("Shoes", "Heels", "Block Heels"), 60, "block_heel"),
    "kitten": ("Kitten Heels", ("Shoes", "Heels", "Kitten Heels"), 35, "kitten"),
    "ballet": ("Ballet Pumps", ("Shoes", "Flats", "Ballet Pumps"), 5, "ballet"),
    "loafer": ("Loafers", ("Shoes", "Loafers"), 20, "loafer"),
    "brogue": ("Brogues", ("Shoes", "Brogues"), 25, "brogue"),
    "school": ("School Shoes", ("Shoes", "School Shoes"), 15, "brogue"),
    "slipper": ("Slippers", ("Shoes", "Slippers"), 15, "slipper"),
    # gen#216: each draws as its own kind (kit_footwear), its variant axes as drawing params
    "plimsoll": ("Plimsolls", ("Shoes", "Plimsolls"), 10, "plimsoll"),
    "clog": ("Clogs", ("Shoes", "Clogs"), 30, "clog"),
    "wedge": ("Wedges", ("Shoes", "Wedges"), 60, "wedge"),
    "espadrille": ("Espadrilles", ("Shoes", "Espadrilles"), 10, "espadrille"),
    "platform_trainer": ("Platform Trainers", ("Shoes", "Platform Trainers"), 45, "platform_trainer"),
    "mule": ("Mules", ("Shoes", "Mules"), 5, "mule"),
    "jelly": ("Jelly Shoes", ("Shoes", "Jelly Shoes"), 10, "jelly"),
    "barefoot": ("Barefoot Shoes", ("Shoes", "Barefoot Shoes"), 0, "barefoot"),
}

#: (color, color family, upper material).
Shade = tuple[Color, str, str]


def sh(name: str, hex_: str, family: str, material: str, pattern: str = "solid",
       accent: str = "#333333") -> Shade:  # fmt: skip
    return (cw(name, hex_, pattern, accent), family, material)


# ==========================================================================
# The style
# ==========================================================================


@dataclass(frozen=True)
class FootwearStyle:
    code: str
    title: str
    brand: str
    #: women | men | kids: the category root and the size chart.
    gender: str
    kind: str  # a key of TYPES
    price: float
    description: str
    colors: tuple[Shade, ...]
    sizes: tuple[str, ...]
    closure: str
    sole: str
    toe: str = "Round"
    widths: tuple[str, ...] = ("Standard",)
    #: The sizes every width after the first is cut in; () means every size.
    wide: tuple[str, ...] = ()
    #: Kids: the price of a junior size (infant sizes cost ``price``).
    junior_price: float | None = None
    heel_mm: int | None = None
    lining: str | None = None
    product_line: str | None = None
    was_price: float | None = None
    trending: bool = False
    online_only: bool = False
    #: Also sold as personal protective equipment (department Workwear & PPE).
    workwear: bool = False
    label: str | None = None
    #: More attributes: (key, name, value) or (key, name, value, unit code).
    extra: tuple[tuple, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in TYPES:
            raise ValueError(f"{self.code}: unknown kind {self.kind!r}")
        chart = self.chart
        bad = [s for s in self.sizes if s not in CHARTS[chart]]
        if bad:
            raise ValueError(f"{self.code}: size {bad} is not on the {chart} chart")
        if not set(self.wide) <= set(self.sizes):
            raise ValueError(f"{self.code}: a wide fit size the style is not cut in")
        if not 2 <= len(self.colors) <= 6:
            raise ValueError(f"{self.code}: {len(self.colors)} colors, not 2 to 6 colors")
        for c, family, material in self.colors:
            if material not in MATERIALS:
                raise ValueError(f"{self.code}: {c[0]} has material {material!r}")
            if family not in COLOR_FAMILIES:
                raise ValueError(f"{self.code}: {c[0]} has color family {family!r}")
        if self.closure not in CLOSURES:
            raise ValueError(f"{self.code}: unknown closure {self.closure!r}")
        if (self.junior_price is not None) != (self.gender == "kids"):
            raise ValueError(f"{self.code}: a junior price is for a kids style only")

    @property
    def chart(self) -> str:
        return f"slippers_{self.gender}" if self.kind == "slipper" else self.gender

    def _price(self, size: str) -> float:
        return self.junior_price if "Junior" in size and self.junior_price else self.price

    def axes(self, heel: int) -> dict[str, str]:
        """The drawing params of the kind's variant axes (:data:`kit_footwear.AXES`), read from
        the attributes the record states, so the picture and the attribute are one fact."""
        e = {k: v for k, _, v, *_ in self.extra}
        kind = self.kind
        if kind == "wedge":
            return {"heel": str(heel)}
        if kind == "espadrille":
            return {"heel": e["heel_type"].lower()}
        if kind == "mule":
            return {"heel": e["heel_type"].lower(), "toe": e["toe_style"].lower()}
        if kind == "platform_trainer":
            return {"platform": str(e["platform_height"])}
        if kind == "clog":
            return {"strap": "back" if e["strap"] == "Back strap" else "none", "body": e["material"].lower()}
        if kind == "jelly":
            return {"style": e["jelly_style"].lower(), "glitter": e["glitter"].lower()}
        if kind == "barefoot":
            return {"sole": str(e["sole_thickness"])}
        return {}

    def skus(self) -> list[dict]:
        """Color x width x size; a later width only in :attr:`wide` (when named)."""
        chart = CHARTS[self.chart]
        out = []
        for color, _, material in self.colors:
            for width in self.widths:
                for s in self.sizes:
                    if width != self.widths[0] and self.wide and s not in self.wide:
                        continue
                    uk, eu, us = chart[s]
                    row = {"color": color[0], "upper_material": material}
                    row |= {"size": s} if self.kind == "slipper" else {}
                    row |= {"size_uk": uk, "size_eu": eu, "size_us": us, "width": width,
                            "price": self._price(s),
                            # About one SKU in nine is sold out, differently per color.
                            "in_stock": _digest(self.code, color[0], width, s) % 9 != 0}  # fmt: skip
                    out.append(row)
        return out

    def doc(self) -> dict:
        """The style's one document, its SKUs nested (:func:`variants.product`)."""
        ptype, nodes, heel, draw = TYPES[self.kind]
        heel = heel if self.heel_mm is None else self.heel_mm
        h = _digest(self.code)
        skus = self.skus()
        prices = [s["price"] for s in skus]
        lead, _, lead_material = self.colors[0]
        materials = list(dict.fromkeys(m for _, _, m in self.colors))
        attrs = [
            attr("closure", "Closure", self.closure),
            attr("upper_material", "Upper material", ", ".join(materials)),
            attr("sole", "Sole", self.sole),
            attr("toe", "Toe", self.toe),
            # MMT is UN/CEFACT's millimetre.
            attr("heel_height", "Heel height", heel, "MMT"),
        ]
        if self.lining:
            attrs.append(attr("lining", "Lining", self.lining))
        attrs += [attr(k, n, v, *u) for k, n, v, *u in self.extra]
        dept = ["Footwear", *(["Workwear & PPE"] if self.workwear else [])]
        rec = {
            "title": self.title,
            "brand": self.brand,
            "brand_owner": BRAND_OWNER[self.brand],
            "department": check_departments(dept, self.title),
            "category_path": [ROOTS[self.gender], *nodes],
            "category_leaf": nodes[-1],
            "description": self.description,
            "attributes": attrs,
            "drawing": drawing("shoe", lead, self.label, kind=draw, material=lead_material,
                               closure=self.closure, **self.axes(heel)),  # fmt: skip
            "collections": [],
            "currency": "GBP",
            "product_type": ptype,
            "audience": "kids" if self.gender == "kids" else "adult",
            "sold_last_5_days": 3 + h % 240,
            "rating": round(3.6 + (h % 14) / 10, 1),
            "review_count": 5 + (h >> 8) % 1700,
            "price_min": min(prices),
            "price_max": max(prices),
            "online_only": self.online_only,
            "trending": self.trending,
        }
        if self.was_price is not None:
            rec["was_price"] = self.was_price
            rec["discount_pct"] = round(100 * (self.was_price - min(prices)) / self.was_price)
            rec["promotion"] = promotion_values(f"FTW-{self.code}")
        if self.product_line is not None:
            rec["product_line"] = self.product_line
        swatches = {c[0]: swatch(c, family) for c, family, _ in self.colors}
        return product(f"FTW-{self.code}", skus, swatches, **rec)


# ==========================================================================
# The styles
# ==========================================================================

STD_WIDE = ("Standard", "Wide")
W_RUN = run("3", "9", 8.5)
W_WHOLE = run("3", "8")
M_RUN = run("6", "13", 12, "men")
M_DRESS = run("6", "12", 11, "men")
INFANT_JUNIOR = run("4 Infant", "2 Junior", chart="kids")
#: The category root of each footwear gender (gen#304: Mens and Womens, as Kids).
ROOTS = {"women": "Womens", "men": "Mens", "kids": "Kids"}
_W, _M, _K = "women", "men", "kids"

WOMENS = (
    FootwearStyle("WTRCNV", "Canvas Lace-Up Trainers", "Larkmoor", _W, "trainer", 26.0,
                  "Low canvas trainers with a cushioned insole and a vulcanised rubber sole.",
                  (sh("White", "#f7f5ef", "white", "canvas"), sh("Navy", "#26365c", "navy", "canvas"),
                   sh("Black", "#2a2a2e", "black", "canvas"), sh("Sage", "#9bae8f", "green", "canvas")),
                  W_WHOLE, "Lace-Up", "Rubber"),
    FootwearStyle("WTRLTH", "Leather Chunky Trainers", "Larkmoor", _W, "trainer", 45.0,
                  "Smooth leather trainers on a deep, lightweight sole with a padded collar.",
                  (sh("White", "#fbfaf6", "white", "leather"), sh("Blush", "#e8b9b3", "pink", "leather"),
                   sh("Black", "#2a2a2e", "black", "leather")),
                  run("3", "8", 7.5), "Lace-Up", "Rubber", heel_mm=40, trending=True),
    FootwearStyle("WRUNCR", "Cloudrise Running Shoes", "Stridewell", _W, "running", 95.0,
                  "Neutral road running shoes with a soft foam midsole and a breathable mesh "
                  "upper. Reflective heel tab.",
                  (sh("Lilac Haze", "#b9a3d6", "pink", "mesh"), sh("Black Ice", "#24262b", "black", "mesh"),
                   sh("Coral Glow", "#f07d5e", "orange", "mesh"),
                   sh("Glacier Blue", "#8fc1e3", "blue", "mesh")),
                  W_RUN, "Lace-Up", "EVA foam", widths=STD_WIDE, wide=run("4", "8", 7.5),
                  product_line="Cloudrise", extra=(("drop", "Heel drop", "8mm"),)),
    FootwearStyle("WANKBL", "Suede Block Heel Ankle Boots", "Calderby & Lune", _W, "ankle_boot",
                  79.0, "Soft suede ankle boots on a stacked block heel, with an inside zip.",
                  (sh("Black Suede", "#26262a", "black", "suede"),
                   sh("Tan Suede", "#b5835a", "brown", "suede"),
                   sh("Taupe Suede", "#8f8174", "grey", "suede")),
                  W_WHOLE, "Zip", "Rubber", toe="Almond", widths=STD_WIDE, wide=run("4", "8")),
    FootwearStyle("WCHLSA", "Leather Chelsea Boots", "Larkmoor", _W, "chelsea", 65.0,
                  "Pull-on leather Chelsea boots with elastic side panels and a cleated sole.",
                  (sh("Black Leather", "#232326", "black", "leather"),
                   sh("Brown Leather", "#6b4430", "brown", "leather"),
                   sh("Burgundy", "#6e1f2f", "red", "leather")),
                  run("3", "9"), "Elastic Gusset", "Rubber", widths=STD_WIDE, wide=run("4", "8")),
    FootwearStyle("WKNEBT", "Leather Knee High Boots", "Calderby & Lune", _W, "knee_boot", 129.0,
                  "Tall leather riding boots with a full-length inside zip and a low block heel.",
                  (sh("Black Leather", "#232326", "black", "leather"),
                   sh("Chestnut", "#8a4b2a", "brown", "leather")),
                  W_WHOLE, "Zip", "Rubber", toe="Almond", was_price=159.0,
                  extra=(("calf", "Calf circumference", "36cm"),)),
    FootwearStyle("WWLKFS", "Fellside Waterproof Walking Boots", "Stridewell", _W, "walking_boot",
                  89.0, "Nubuck hiking boots with a waterproof membrane and a deep lug sole.",
                  (sh("Slate", "#5d646b", "grey", "nubuck"), sh("Plum", "#6b3a5a", "pink", "nubuck"),
                   sh("Moss", "#5f6b3f", "green", "nubuck")),
                  W_RUN, "Lace-Up", "Rubber lug", lining="Waterproof membrane",
                  product_line="Fellside", extra=(("waterproof", "Waterproof", "Yes"),)),
    FootwearStyle("WSNDTS", "Leather Two-Strap Sandals", "Wrenfield", _W, "sandal", 32.0,
                  "Flat leather sandals with two buckled straps and a cushioned footbed.",
                  (sh("Tan", "#b07a45", "brown", "leather"), sh("Black", "#2a2a2e", "black", "leather"),
                   sh("Gold", "#cfae63", "gold", "leather"), sh("White", "#f7f5ef", "white", "leather")),
                  W_WHOLE, "Buckle", "Rubber"),
    FootwearStyle("WSNDSL", "Padded Footbed Sliders", "Wrenfield", _W, "sandal", 22.0,
                  "Easy slip-on sliders with a wide padded strap and a contoured footbed.",
                  (sh("Black", "#2a2a2e", "black", "synthetic"), sh("Cream", "#efe6d2", "cream", "synthetic"),
                   sh("Khaki", "#8a8456", "green", "synthetic")),
                  W_WHOLE, "Slip-On", "EVA foam", heel_mm=20),
    FootwearStyle("WCRTST", "Pointed Stiletto Court Shoes", "Larkmoor", _W, "court", 45.0,
                  "Classic pointed courts on a slim stiletto heel, with a padded insole.",
                  (sh("Black Patent", "#141416", "black", "patent"),
                   sh("Nude Patent", "#d8b49a", "cream", "patent"),
                   sh("Red Suede", "#b3202e", "red", "suede")),
                  run("3", "8", 7.5), "Slip-On", "Leather", toe="Pointed", widths=STD_WIDE,
                  wide=run("4", "8")),
    FootwearStyle("WBLKAS", "Block Heel Ankle Strap Shoes", "Wrenfield", _W, "block_heel", 39.0,
                  "Almond-toe shoes on a steady block heel with a buckled ankle strap.",
                  (sh("Black Suede", "#26262a", "black", "suede"),
                   sh("Tan Leather", "#a8703f", "brown", "leather"),
                   sh("Leopard", "#c9a26b", "multi", "suede", "leopard", "#3a2a1c")),
                  W_WHOLE, "Ankle Strap", "Rubber", toe="Almond", trending=True),
    FootwearStyle("WKITSB", "Kitten Heel Slingback Shoes", "Larkmoor", _W, "kitten", 42.0,
                  "Pointed slingbacks on a low kitten heel, with an elasticated back strap.",
                  (sh("Black Leather", "#232326", "black", "leather"),
                   sh("Cream Leather", "#efe4cf", "cream", "leather"),
                   sh("Silver", "#c7c9cc", "silver", "leather")),
                  W_WHOLE, "Slingback", "Leather", toe="Pointed"),
    FootwearStyle("WBALLT", "Leather Ballet Pumps", "Wrenfield", _W, "ballet", 29.0,
                  "Soft leather ballet flats with a bow trim and a flexible sole. Folds flat.",
                  (sh("Black", "#2a2a2e", "black", "leather"), sh("Navy", "#26365c", "navy", "leather"),
                   sh("Nude", "#d9b8a0", "cream", "leather"),
                   sh("Leopard", "#c9a26b", "multi", "suede", "leopard", "#3a2a1c"),
                   sh("Red Patent", "#b3202e", "red", "patent")),
                  run("3", "9"), "Slip-On", "Leather", widths=("Standard", "Wide", "Extra Wide"),
                  wide=run("4", "8")),
    FootwearStyle("WLOAFP", "Leather Penny Loafers", "Larkmoor", _W, "loafer", 49.0,
                  "Polished leather loafers with a saddle strap and a low stacked heel.",
                  (sh("Black", "#2a2a2e", "black", "leather"), sh("Burgundy", "#6e1f2f", "red", "leather"),
                   sh("Tan", "#b07a45", "brown", "leather")),
                  run("3", "8", 7.5), "Slip-On", "Rubber"),
    FootwearStyle("WSLMOC", "Faux Fur Lined Moccasin Slippers", "Hollinwray Knits", _W, "slipper",
                  22.0, "Suede moccasin slippers lined in soft faux fur, on a grippy sole.",
                  (sh("Grey", "#9a9a9e", "grey", "suede"), sh("Dusky Pink", "#d7a1a6", "pink", "suede"),
                   sh("Navy", "#26365c", "navy", "suede")),
                  tuple(SLIPPERS_WOMEN), "Slip-On", "Rubber", lining="Faux fur"),
    FootwearStyle("WWELGL", "Gloss Tall Wellies", "Thistle & Wren", _W, "welly", 35.0,
                  "Glossy rubber wellingtons with a side buckle and a ribbed, grippy sole.",
                  (sh("Navy", "#26365c", "navy", "rubber"), sh("Olive", "#5f6b3a", "green", "rubber"),
                   sh("Red", "#b3202e", "red", "rubber")),
                  W_WHOLE, "Pull-On", "Rubber", extra=(("waterproof", "Waterproof", "Yes"),)),
)  # fmt: skip

MENS = (
    FootwearStyle("MTRLOW", "Leather Low Top Trainers", "Harbour & Pine", _M, "trainer", 45.0,
                  "Clean leather trainers with a padded collar and a stitched cupsole.",
                  (sh("White", "#fbfaf6", "white", "leather"), sh("Black", "#2a2a2e", "black", "leather"),
                   sh("White Navy", "#26365c", "navy", "leather")),
                  run("6", "13", 11, "men"), "Lace-Up", "Rubber"),
    FootwearStyle("MRUNCR", "Cloudrise Running Shoes", "Stridewell", _M, "running", 95.0,
                  "Neutral road running shoes with a soft foam midsole and a breathable mesh "
                  "upper. Reflective heel tab.",
                  (sh("Black Ice", "#24262b", "black", "mesh"), sh("Citrus Lime", "#b7cf3a", "green", "mesh"),
                   sh("Storm Grey", "#70757c", "grey", "mesh"), sh("Cobalt", "#2b56b5", "blue", "mesh")),
                  M_RUN, "Lace-Up", "EVA foam", widths=STD_WIDE, wide=run("7", "12", 11.5, "men"),
                  product_line="Cloudrise", extra=(("drop", "Heel drop", "8mm"),)),
    FootwearStyle("MCHLSD", "Suede Chelsea Boots", "Harbour & Pine", _M, "chelsea", 69.0,
                  "Suede Chelsea boots with elastic side panels, a pull tab and a crepe-look sole.",
                  (sh("Tan Suede", "#b5835a", "brown", "suede"), sh("Navy Suede", "#2c3a5e", "navy", "suede"),
                   sh("Black Suede", "#26262a", "black", "suede")),
                  M_DRESS, "Elastic Gusset", "Rubber"),
    FootwearStyle("MCHKSD", "Suede Chukka Boots", "Harbour & Pine", _M, "chukka", 59.0,
                  "Two-eyelet suede desert boots on a light rubber sole.",
                  (sh("Sand Suede", "#c9b28c", "cream", "suede"), sh("Olive Suede", "#6b6b3a", "green", "suede"),
                   sh("Navy Suede", "#2c3a5e", "navy", "suede")),
                  run("6", "12", chart="men"), "Lace-Up", "Rubber"),
    FootwearStyle("MWLKFS", "Fellside Waterproof Walking Boots", "Stridewell", _M, "walking_boot",
                  99.0, "Nubuck hiking boots with a waterproof membrane and a deep lug sole.",
                  (sh("Brown", "#6b4a33", "brown", "nubuck"), sh("Charcoal", "#3f4247", "grey", "nubuck"),
                   sh("Moss", "#5f6b3f", "green", "nubuck")),
                  M_RUN, "Lace-Up", "Rubber lug", widths=STD_WIDE, wide=run("7", "12", chart="men"),
                  lining="Waterproof membrane", product_line="Fellside",
                  extra=(("waterproof", "Waterproof", "Yes"),)),
    FootwearStyle("MBRODB", "Leather Derby Brogues", "Calderby & Lune", _M, "brogue", 85.0,
                  "Wingtip derby brogues in burnished leather, Goodyear welted on a leather sole.",
                  (sh("Tan", "#a8703f", "brown", "leather"), sh("Dark Brown", "#4a2f22", "brown", "leather"),
                   sh("Black", "#1f1f22", "black", "leather"), sh("Oxblood", "#5a1a22", "red", "leather")),
                  run("6", "12", 10.5, "men"), "Lace-Up", "Leather", widths=STD_WIDE,
                  wide=run("7", "11", chart="men"), extra=(("style", "Style", "Wingtip"),)),
    FootwearStyle("MLOAFP", "Leather Penny Loafers", "Harbour & Pine", _M, "loafer", 59.0,
                  "Hand-finished leather loafers with a saddle strap and a stacked heel.",
                  (sh("Black", "#1f1f22", "black", "leather"), sh("Brown", "#5c3a26", "brown", "leather"),
                   sh("Oxblood", "#5a1a22", "red", "leather")),
                  M_DRESS, "Slip-On", "Leather"),
    FootwearStyle("MSLMUL", "Sheepskin Lined Slippers", "Hollinwray Knits", _M, "slipper", 35.0,
                  "Suede slippers lined in warm sheepskin, with a hard-wearing sole.",
                  (sh("Chestnut", "#8a4b2a", "brown", "suede"), sh("Grey", "#7d7f84", "grey", "suede")),
                  tuple(SLIPPERS_MEN), "Slip-On", "Rubber", lining="Sheepskin"),
    FootwearStyle("MSAFS3", "Steel Toe Cap Safety Boots S3", "Ferrowick Denim", _M, "safety_boot",
                  59.0, "Leather work boots with a steel toe cap and steel midsole, rated S3: "
                  "water resistant, antistatic and slip resistant (SRC).",
                  (sh("Black", "#1f1f22", "black", "leather"), sh("Honey", "#b07a3a", "brown", "nubuck")),
                  run("6", "13", chart="men"), "Lace-Up", "Rubber, SRC slip resistant",
                  toe="Steel Toe Cap", workwear=True, label="S3",
                  extra=(("safety_rating", "Safety rating", "S3"),
                         ("safety_standard", "Safety standard", "EN ISO 20345"),
                         ("toe_cap", "Toe cap", "Steel"),
                         ("midsole", "Midsole", "Steel, penetration resistant"))),
    FootwearStyle("MWELNP", "Neoprene Lined Wellies", "Thistle & Wren", _M, "welly", 49.0,
                  "Rubber wellingtons lined in neoprene for warmth, with a padded heel kick.",
                  (sh("Green", "#3f5a3a", "green", "rubber"), sh("Black", "#1f1f22", "black", "rubber")),
                  run("6", "12", chart="men"), "Pull-On", "Rubber", lining="Neoprene",
                  extra=(("waterproof", "Waterproof", "Yes"),)),
)  # fmt: skip

KIDS_STYLES = (
    FootwearStyle("KTRHLT", "Kids' Hook & Loop Trainers", "Little Fernby", _K, "trainer", 18.0,
                  "Easy-on trainers with two hook and loop straps and a bendy rubber sole.",
                  (sh("Navy", "#26365c", "navy", "synthetic"), sh("Pink", "#e88aa8", "pink", "synthetic"),
                   sh("Black", "#2a2a2e", "black", "synthetic"), sh("White", "#fbfaf6", "white", "synthetic")),
                  INFANT_JUNIOR, "Hook & Loop", "Rubber", junior_price=22.0),
    FootwearStyle("KRUNCR", "Kids' Cloudrise Running Shoes", "Stridewell", _K, "running", 45.0,
                  "Lightweight running shoes for kids with a foam midsole and a mesh upper.",
                  (sh("Cobalt", "#2b56b5", "blue", "mesh"), sh("Black Ice", "#24262b", "black", "mesh"),
                   sh("Lilac Haze", "#b9a3d6", "pink", "mesh")),
                  run("10 Infant", "6 Junior", chart="kids"), "Lace-Up", "EVA foam",
                  junior_price=50.0, product_line="Cloudrise"),
    FootwearStyle("KSCHLL", "Kids' Leather School Shoes", "Little Fernby", _K, "school", 32.0,
                  "Scuff-resistant leather school shoes with a hook and loop strap, in three "
                  "fittings.",
                  (sh("Black Leather", "#1f1f22", "black", "leather"),
                   sh("Black Patent", "#141416", "black", "patent")),
                  run("7 Infant", "5 Junior", chart="kids"), "Hook & Loop", "Rubber",
                  widths=("F", "G", "H"), junior_price=36.0),
    FootwearStyle("KWELPD", "Kids' Polka Dot Wellies", "Little Fernby", _K, "welly", 14.0,
                  "Bright rubber wellies with easy pull-on handles and a grippy sole.",
                  (sh("Red Polka Dot", "#c8102e", "red", "rubber", "polka", "#ffffff"),
                   sh("Navy Polka Dot", "#26365c", "navy", "rubber", "polka", "#ffffff"),
                   sh("Pink Polka Dot", "#e88aa8", "pink", "rubber", "polka", "#ffffff")),
                  INFANT_JUNIOR, "Pull-On", "Rubber", junior_price=16.0,
                  extra=(("waterproof", "Waterproof", "Yes"),)),
    FootwearStyle("KSNDHL", "Kids' Hook & Loop Sandals", "Little Fernby", _K, "sandal", 16.0,
                  "Open sandals with a padded footbed and hook and loop straps.",
                  (sh("Navy", "#26365c", "navy", "synthetic"), sh("Pink", "#e88aa8", "pink", "synthetic"),
                   sh("Silver", "#c7c9cc", "silver", "synthetic")),
                  INFANT_JUNIOR, "Hook & Loop", "Rubber", junior_price=18.0),
)  # fmt: skip

# gen#216: plimsolls, clogs, wedges, espadrilles, platform trainers, mules, jelly and barefoot
# shoes. Each type is three styles from three brands; the attributes the issue lists are `extra`
# entries, and the drawing's variant-axis params are read from them (`FootwearStyle.axes`).
W_ALL = run("3", "8")
M_ALL = run("6", "12", chart="men")
KIDS_RUN = run("10 Infant", "6 Junior", chart="kids")
_BLK, _WHT = ("Black", "#2a2a2e", "black"), ("White", "#f7f5ef", "white")
_RED, _YEL = ("Red", "#b3202e", "red"), ("Yellow", "#e8c43a", "yellow")
_GRN, _BLU = ("Green", "#3f7a4a", "green"), ("Blue", "#2b56b5", "blue")
_NAV = ("Navy", "#26365c", "navy")


def _in(material: str, *colors: tuple[str, str, str]) -> tuple[Shade, ...]:
    """The colors ``colors`` (name, hex, family), each in one upper ``material``."""
    return tuple(sh(n, h, f, material) for n, h, f in colors)


NEW_STYLES: tuple[FootwearStyle, ...] = (
    # -- plimsolls: closure, canvas upper, school or adult
    FootwearStyle("KPLSCH", "Kids' School Plimsolls", "Little Fernby", _K, "plimsoll", 7.0,
                  "Plain canvas plimsolls for PE, with a hook and loop strap and a flat rubber sole.",
                  _in("canvas", _BLK, _WHT, _NAV, _BLU), KIDS_RUN, "Hook & Loop", "Rubber",
                  junior_price=9.0,
                  extra=(("use", "Use", "School"),)),
    FootwearStyle("WPLCNV", "Canvas Lace-Up Plimsolls", "Larkmoor", _W, "plimsoll", 12.0,
                  "Low canvas plimsolls with a reinforced toe cap and a flat vulcanised sole.",
                  _in("canvas", _WHT, _BLK, _RED, _YEL, _GRN, _BLU), W_ALL, "Lace-Up", "Rubber",
                  extra=(("use", "Use", "Adult"),)),
    FootwearStyle("MPLSLP", "Slip-On Canvas Plimsolls", "Harbour & Pine", _M, "plimsoll", 14.0,
                  "Easy canvas plimsolls with twin elastic gussets and a flat rubber sole.",
                  _in("canvas", _NAV, _BLK, _WHT, _RED), M_ALL, "Slip-On", "Rubber",
                  extra=(("use", "Use", "Adult"),)),
    # -- clogs: material, back strap or none, lined or not
    FootwearStyle("WCLEVA", "EVA Clogs with Back Strap", "Wrenfield", _W, "clog", 18.0,
                  "Light moulded clogs with ventilation holes and a pivoting back strap.",
                  _in("synthetic", _BLK, _WHT, _NAV, _GRN, _YEL, _RED), W_ALL, "Slip-On", "EVA foam",
                  extra=(("material", "Material", "EVA"), ("strap", "Strap", "Back strap"),
                         ("lined", "Lined", "No"))),
    FootwearStyle("MCLWOD", "Leather Topped Wooden Clogs", "Calderby & Lune", _M, "clog", 49.0,
                  "Traditional clogs with a smooth leather upper on a carved, hard-wearing wooden sole.",
                  _in("leather", ("Brown", "#6b4430", "brown"), _BLK, ("Tan", "#b07a45", "brown")),
                  M_ALL, "Slip-On", "Wood", heel_mm=35,
                  extra=(("material", "Material", "Wood"), ("strap", "Strap", "None"),
                         ("lined", "Lined", "No"))),
    FootwearStyle("WCLFLC", "Faux Fur Lined Clogs", "Hollinwray Knits", _W, "clog", 32.0,
                  "Suede clogs with a warm faux fur lining and a wooden sole.",
                  _in("suede", ("Chestnut", "#8a4b2a", "brown"), _BLK, ("Grey", "#9a9a9e", "grey")),
                  W_ALL, "Slip-On", "Wood", lining="Faux fur", heel_mm=40,
                  extra=(("material", "Material", "Wood"), ("strap", "Strap", "None"),
                         ("lined", "Lined", "Yes"))),
    # -- wedges: heel height, upper
    FootwearStyle("WWDESP", "Jute Espadrille Wedges", "Wrenfield", _W, "wedge", 28.0,
                  "Woven jute espadrille wedges with a rope-wrapped heel and an ankle tie.",
                  _in("jute", ("Natural", "#d8c08a", "cream"), _BLK, _NAV, _RED), W_ALL, "Ankle Strap",
                  "Rope", heel_mm=65),
    FootwearStyle("WWDSUE", "Suede Wedge Sandals", "Larkmoor", _W, "wedge", 39.0,
                  "Soft suede wedge sandals with a cork-look heel and an ankle strap.",
                  _in("suede", _BLK, ("Tan", "#b5835a", "brown"), _GRN, _BLU, _WHT), W_ALL, "Ankle Strap",
                  "Cork", heel_mm=80),
    FootwearStyle("WWDLTH", "Leather Cork Wedges", "Calderby & Lune", _W, "wedge", 45.0,
                  "Smooth leather wedges with a cork heel and an ankle strap that fastens at the back.",
                  _in("leather", ("Tan", "#a8703f", "brown"), _BLK, _WHT, _YEL), W_ALL, "Ankle Strap", "Cork",
                  heel_mm=55),
    # -- espadrilles: flat or wedge, canvas or jute
    FootwearStyle("WESFLT", "Canvas Flat Espadrilles", "Harbour & Pine", _W, "espadrille", 16.0,
                  "Flat canvas espadrilles with ankle ties and a braided rope sole.",
                  _in("canvas", _WHT, _NAV, _RED, _YEL, _GRN, _BLK), W_ALL, "Lace-Up", "Rope",
                  heel_mm=10, extra=(("heel_type", "Heel type", "Flat"),)),
    FootwearStyle("MESJUT", "Slip-On Jute Espadrilles", "Thistle & Wren", _M, "espadrille", 22.0,
                  "Slip-on espadrilles in woven jute on a braided rope sole.",
                  _in("jute", ("Natural", "#d8c08a", "cream"), _BLK, _NAV, _BLU), M_ALL, "Slip-On", "Rope",
                  heel_mm=10, extra=(("heel_type", "Heel type", "Flat"),)),
    FootwearStyle("WESWDG", "Canvas Wedge Espadrilles", "Larkmoor", _W, "espadrille", 30.0,
                  "Canvas espadrilles lifted on a rope-wrapped wedge, with ankle ties.",
                  _in("canvas", _WHT, _BLK, _RED, _BLU, _YEL), W_ALL, "Lace-Up", "Rope", heel_mm=45,
                  extra=(("heel_type", "Heel type", "Wedge"),)),
    # -- platform trainers: platform height, upper
    FootwearStyle("WPTLTH", "Chunky Leather Platform Trainers", "Larkmoor", _W, "platform_trainer", 55.0,
                  "Leather trainers on a chunky platform sole with a padded collar.",
                  _in("leather", _WHT, _BLK, ("Blush", "#e8b9b3", "pink"), _RED, _BLU), run("3", "8", 7.5),
                  "Lace-Up", "Rubber", heel_mm=50, trending=True,
                  extra=(("platform_height", "Platform height", 50, "MMT"),)),
    FootwearStyle("WPTCNV", "Canvas Platform Trainers", "Wrenfield", _W, "platform_trainer", 32.0,
                  "Low canvas trainers on a flatform sole, with a reinforced toe cap.",
                  _in("canvas", _WHT, _BLK, _RED, _YEL, _GRN, _BLU), W_ALL, "Lace-Up", "Rubber",
                  heel_mm=35, extra=(("platform_height", "Platform height", 35, "MMT"),)),
    FootwearStyle("WPTMSH", "Mesh Platform Trainers", "Stridewell", _W, "platform_trainer", 48.0,
                  "Breathable mesh trainers on a thick foam platform.",
                  _in("mesh", _WHT, _BLK, ("Lilac", "#b9a3d6", "pink"), _GRN), W_ALL, "Lace-Up", "EVA foam",
                  heel_mm=60, extra=(("platform_height", "Platform height", 60, "MMT"),)),
    # -- mules: heel, toe
    FootwearStyle("WMLFLT", "Flat Leather Mules", "Calderby & Lune", _W, "mule", 35.0,
                  "Backless flat mules in smooth leather with a closed toe and a padded footbed.",
                  _in("leather", _BLK, _WHT, ("Tan", "#b07a45", "brown"), _RED, _BLU), W_ALL, "Slip-On",
                  "Leather", heel_mm=5,
                  extra=(("heel_type", "Heel type", "Flat"), ("toe_style", "Toe style", "Closed"))),
    FootwearStyle("WMLBLK", "Suede Block Heel Mules", "Larkmoor", _W, "mule", 42.0,
                  "Open-toe suede mules on a steady block heel.",
                  _in("suede", _BLK, ("Camel", "#b5835a", "brown"), _GRN, _YEL), W_ALL, "Slip-On",
                  "Leather", heel_mm=60,
                  extra=(("heel_type", "Heel type", "Block"), ("toe_style", "Toe style", "Open"))),
    FootwearStyle("WMLKIT", "Kitten Heel Mules", "Wrenfield", _W, "mule", 38.0,
                  "Closed-toe mules on a slim kitten heel, with a stitched vamp.",
                  _in("leather", _BLK, _WHT, _RED, _NAV), W_ALL, "Slip-On", "Leather", heel_mm=35,
                  toe="Pointed",
                  extra=(("heel_type", "Heel type", "Kitten"), ("toe_style", "Toe style", "Closed"))),
    # -- jelly shoes: sandal or ballet, glitter
    FootwearStyle("KJLSND", "Kids' Glitter Jelly Sandals", "Little Fernby", _K, "jelly", 11.0,
                  "Glittery moulded jelly sandals with a hook and loop strap, for splashing about.",
                  _in("synthetic", ("Pink", "#e88aa8", "pink"), _RED, _BLU, _GRN, _YEL), KIDS_RUN,
                  "Hook & Loop", "Rubber", junior_price=13.0,
                  extra=(("jelly_style", "Style", "Sandal"), ("glitter", "Glitter", "Yes"))),
    FootwearStyle("WJLBAL", "Jelly Ballet Flats", "Thistle & Wren", _W, "jelly", 14.0,
                  "Soft moulded jelly ballet flats with a perforated vamp and a flexible sole.",
                  _in("synthetic", ("Pink", "#e88aa8", "pink"), _BLK, _WHT, _BLU, _YEL), W_ALL, "Slip-On",
                  "Rubber", extra=(("jelly_style", "Style", "Ballet"), ("glitter", "Glitter", "No"))),
    FootwearStyle("WJLGLT", "Glitter Buckle Jelly Sandals", "Wrenfield", _W, "jelly", 16.0,
                  "Moulded jelly sandals flecked with glitter, with a buckled strap.",
                  _in("synthetic", ("Silver", "#c7c9cc", "silver"), _BLK, _RED, _GRN, _YEL), W_ALL,
                  "Buckle", "Rubber",
                  extra=(("jelly_style", "Style", "Sandal"), ("glitter", "Glitter", "Yes"))),
    # -- barefoot shoes: sole thickness, zero drop
    FootwearStyle("MBFTRL", "Zero Drop Barefoot Trainers", "Stridewell", _M, "barefoot", 75.0,
                  "Flexible mesh trainers with a wide toe box and a thin, zero drop sole.",
                  _in("mesh", _BLK, _WHT, _BLU, _GRN), run("6", "12", 11, "men"), "Lace-Up", "Rubber",
                  extra=(("sole_thickness", "Sole thickness", 4, "MMT"), ("drop", "Heel drop", "0mm"))),
    FootwearStyle("WBFWID", "Wide Toe Barefoot Shoes", "Harbour & Pine", _W, "barefoot", 68.0,
                  "Leather barefoot shoes with a foot-shaped toe box, a hook and loop strap and a 3 mm sole.",
                  _in("leather", _BLK, _WHT, ("Tan", "#b07a45", "brown"), _RED), W_ALL, "Hook & Loop",
                  "Rubber",
                  extra=(("sole_thickness", "Sole thickness", 3, "MMT"), ("drop", "Heel drop", "0mm"))),
    FootwearStyle("KBFKID", "Kids' Barefoot Shoes", "Little Fernby", _K, "barefoot", 34.0,
                  "Bendy barefoot shoes for growing feet, with a wide toe box and a thin zero drop sole.",
                  _in("synthetic", _BLK, _WHT, _BLU, _GRN, _YEL), KIDS_RUN, "Hook & Loop", "Rubber",
                  junior_price=38.0,
                  extra=(("sole_thickness", "Sole thickness", 5, "MMT"), ("drop", "Heel drop", "0mm"))),
)  # fmt: skip

FOOTWEAR: tuple[FootwearStyle, ...] = (*WOMENS, *MENS, *KIDS_STYLES, *NEW_STYLES)


def docs() -> list[dict]:
    """Every footwear style's document, ranked by sales among footwear and badged."""
    out = [s.doc() for s in FOOTWEAR]
    ranked = sorted(out, key=lambda d: (-d["sold_last_5_days"], d["product_id"]))
    rank = {d["product_id"]: n for n, d in enumerate(ranked, 1)}
    out = [{**d, "bestseller_rank": rank[d["product_id"]]} for d in out]
    return [{**d, "badges": badges(d)} for d in out]


# ==========================================================================
# The boots row: products that say "boot" more than a boot does
# ==========================================================================

BOOTS = dz.Row(
    "Complements and accessories", "boots", "a pair of boots",
    lambda d: "Boots" in d["category_path"],
    "category intent: Boots",
    (
        dz.Distractor(dz.product(
            "BOOTORG", "Car Boot Organiser", "Brackenmere Home", "Home",
            ("Home", "Storage", "Car Boot Organisers"), 18.0,
            "A collapsible car boot organiser with three compartments. Keeps shopping upright "
            "in the boot and folds flat when the boot is full.",
            drawing("box_wide", cw("Charcoal", "#3f4247"), "Boot Tidy"),
            (("color", "Color", "Charcoal"),),
        ), "category intent: Boots (a Home item never answers a footwear word)"),
        dz.Distractor(dz.product(
            "BOOTPOL", "Boot Polish & Brush Kit", "Calderby & Lune", "Footwear",
            ("Mens", "Shoes", "Shoe Care"), 12.0,
            "Wax boot polish in black, brown and neutral with a horsehair brush. Feeds leather "
            "boots and keeps boots supple.",
            drawing("tin", cw("Black", "#2a2a2e", "solid", "#c9a24a"), "Polish"),
        ), "product-type demotion: shoe care below boots"),
        dz.Distractor(dz.product(
            "BOOTSOK", "Welly Boot Socks", "Hollinwray Knits", "Clothing",
            ("Womens", "Socks", "Boot Socks"), 9.0,
            "Thick knitted boot socks with a fold-over cuff that shows above welly boots. "
            "Warm in boots all winter.",
            drawing("boot_sock", cw("Oat", "#d9cdb4", "stripe", "#8a6b4a")),
            (("color", "Color", plain("Oat")),),
        ), "department boost: Footwear above Clothing"),
    ),
)  # fmt: skip


def catalog() -> list[dict]:
    """The text corpus the boots row is checked over: round 4, footwear, the planted three."""
    return [*dz.corpus(), *docs(), *(x.doc for x in BOOTS.distractors)]
