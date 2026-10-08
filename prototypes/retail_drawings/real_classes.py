"""Failure classes 2 to 7 of gen#125, rebuilt from hand-searched live results.

Each :class:`ClassRow` is one query shape observed on a live retail site
(every name here is invented): the *targets* a shopper meant, the products
that win WITHOUT a policy, and the policy that fixes it. The records carry the
fields a policy reads and a title never states:

- ``product_type``, separate from the title;
- ``audience`` (:data:`AUDIENCES`) and ``size_range`` (:data:`SIZE_RANGES`);
- ``neckline``, ``pattern`` and ``leg_style`` (closed lists below);
- ``was_price``, present only on a sale item (``price < was_price``);
- popularity: ``sold_last_5_days`` and ``bestseller_rank`` (1 = best);
- ``style_id``: the colourway docs of one style share it, so a search that
  does not collapse on it shows the same product as several tiles;
- the variant structure (:meth:`Style.docs`): swatches, colour family and
  shade, pooled rating, nested ``skus``, ``price_min``/``price_max``, and a
  legwear ``size_range`` derived by :func:`derive_size_range`.

The pre-existing records (:func:`distractors.corpus`) are unchanged and carry
none of these fields. The proof is Elasticsearch (:mod:`es_proof`): the
baseline is BM25 times a popularity boost (it mimics the live site); the
policy adds filters, boosts and a collapse. Its result is committed in
``real_classes_proof.json`` and rendered into the README by :func:`markdown`.
Standard library only.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass

from departments import check as check_departments
from distractors import corpus as base_corpus
from variants import Colourway, attr, cw, drawing

AUDIENCES = ("adult", "kids", "baby")
SIZE_RANGES = ("regular", "petite", "tall", "plus")
NECKLINES = ("boat", "slash", "high", "crew", "round", "collared", "square")
PATTERNS = ("plain", "check", "stripe", "print")
LEG_STYLES = ("balloon", "barrel", "straight", "wide", "slim", "tapered")
#: A record ranked this high gets the baseline's bestseller boost.
BESTSELLER_TOP = 15
RISES = ("low", "mid", "high")

# --------------------------------------------------------------------------
# Variant structure, as observed: style (one product page, shared rating) >
# colourway (one doc, one tile) > SKU (nested; what stock and price are per)
# --------------------------------------------------------------------------

#: The colour facet: a marketing shade ("Washed Black") rolls up to a family.
COLOUR_FAMILIES = ("black", "white", "grey", "blue", "navy", "brown", "cream", "green",
                   "red", "pink", "orange", "multi")  # fmt: skip
SHADE_FAMILY = {
    "Black": "black", "Washed Black": "black",
    "White": "white",
    "Charcoal": "grey", "Grey": "grey", "Grey Check": "grey",
    "Mid Wash": "blue", "Light Wash": "blue", "Vintage Blue": "blue", "Indigo": "blue",
    "Blue Stripe": "blue", "Ice": "blue",
    "Navy": "navy", "Rinse": "navy", "Navy Check": "navy", "Navy Print": "navy",
    "Navy Stripe": "navy",
    "Brown Check": "brown", "Camel Check": "brown", "Tobacco": "brown",
    "Wild Honey": "brown", "Mocha Kiss": "brown", "Caramel": "brown", "Toffee": "brown",
    "Espresso": "brown",
    "Ecru": "cream", "Oat": "cream", "Natural": "cream", "Stone": "cream",
    "Champagne": "cream", "Porcelain": "cream",
    "Khaki": "green", "Olive": "green", "Sage": "green", "Green Print": "green",
    "Gingham": "red", "Cherry Pop": "red",
    "Pink": "pink",
    "Rust": "orange", "Terracotta": "orange",
    "Stripe": "multi",
}  # fmt: skip
#: The inside-leg axis of a legwear product page, and the size range each serves.
INSIDE_LEGS = ("Extra Short", "Short/Petite", "Regular", "Long", "Extra Long")
LENGTH_RANGE = {"Extra Short": "petite", "Short/Petite": "petite", "Regular": "regular",
                "Long": "tall", "Extra Long": "tall"}  # fmt: skip
#: The usual cut: petite, regular and long.
LEGS3 = ("Short/Petite", "Regular", "Long")
WAISTS = tuple(str(n) for n in range(6, 25, 2))
#: A kids style is sized by age, in the same SKU field.
KIDS_WAISTS = tuple(f"{n} Yrs" for n in range(6, 17, 2))
#: A bed size label carries its dimension; the price steps up per size.
BED_SIZES = ("Single (3 ft)", "Double (4 ft 6)", "King Size (5 ft)", "Super King Size (6 ft)")


def derive_size_range(skus: list[dict]) -> list[str]:
    """The size ranges ``skus`` serve with stock, in :data:`SIZE_RANGES` order.

    Petite is an inside-leg option of a regular style, not a separate
    product, so a style is petite when a Short/Petite (or Extra Short) SKU is
    in stock. The flat ``size_range`` filter of class 6 reads this.
    """
    served = {LENGTH_RANGE[s["inside_leg"]] for s in skus if s["in_stock"]}
    return [r for r in SIZE_RANGES if r in served]


def _digest(*parts: str) -> int:
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:12], 16)

# ==========================================================================
# Styles: one doc per colourway, all sharing the style's ``style_id``
# ==========================================================================


@dataclass(frozen=True)
class Style:
    code: str
    title: str
    brand: str
    department: str
    path: tuple[str, ...]
    price: float
    description: str
    product_type: str
    shape: str
    #: (colourway, sold_last_5_days): one doc each.
    colourways: tuple[tuple[Colourway, int], ...]
    audience: str = "adult"
    was_price: float | None = None
    size_range: str | None = None
    neckline: str | None = None
    pattern: str | None = None
    leg_style: str | None = None
    params: tuple[tuple[str, str], ...] = ()
    #: A style attribute: another pack count is another style, never a variant.
    units_per_pack: int | None = None
    #: Legwear: the inside legs it is cut in (SKUs = waist x inside leg); its
    #: ``size_range`` is then derived, never declared.
    lengths: tuple[str, ...] = ()
    #: Lengths whose every SKU is out of stock.
    sold_out: tuple[str, ...] = ()
    #: Bedding: one SKU per :data:`BED_SIZES` entry, each with its own price.
    bed_sized: bool = False
    #: Beauty: (unit size, "g" or "ml") of every shade.
    unit: tuple[float, str] | None = None

    def __post_init__(self) -> None:
        if self.lengths and self.size_range is not None:
            raise ValueError(f"{self.code}: a legwear size_range is derived from its SKUs")

    def skus(self, colour: Colourway) -> list[dict]:
        """The colourway's SKUs: waist x inside leg, or bed sizes, or none."""
        if self.lengths:
            waists = KIDS_WAISTS if self.audience == "kids" else WAISTS
            return [
                {"waist": w, "inside_leg": leg, "price": self.price,
                 # About one SKU in seven is greyed out, differently per colour.
                 "in_stock": leg not in self.sold_out
                 and _digest(self.code, colour[0], w, leg) % 7 != 0}
                for leg in self.lengths for w in waists
            ]  # fmt: skip
        if self.bed_sized:
            step = round(self.price / 4)
            return [{"bed_size": b, "price": float(self.price + n * step)}
                    for n, b in enumerate(BED_SIZES)]  # fmt: skip
        return []

    def size_ranges(self) -> list[str] | None:
        if self.lengths:
            return derive_size_range([s for c, _ in self.colourways for s in self.skus(c)])
        return None if self.size_range is None else [self.size_range]

    def docs(self) -> list[dict]:
        group = f"PLT-{self.code}"
        swatches = [
            {"shade": c[0], "family": SHADE_FAMILY[c[0]], "hex": c[2]} for c, _ in self.colourways
        ]
        # Pooled per style: every colourway shows the same rating and count.
        h = _digest(self.code)
        rating, reviews = round(3.6 + (h % 14) / 10, 1), 5 + (h >> 8) % 1700
        size_range = self.size_ranges()
        out = []
        for n, (colour, sold) in enumerate(self.colourways, 1):
            skus = self.skus(colour)
            prices = [s["price"] for s in skus] or [self.price]
            rec = {
                "product_id": f"{group}-{n:02d}",
                "sku": f"PLT{self.code}{n:02d}",
                "variant_group": group,
                "sku_count": max(1, len(skus)),
                "title": self.title,
                "brand": self.brand,
                "department": check_departments([self.department], self.title),
                "category_path": list(self.path),
                # The tile's "from" price: the cheapest SKU.
                "price": min(prices),
                "description": self.description,
                "attributes": [attr("colour", "Colour", colour[0])],
                "drawing": drawing(self.shape, colour, **dict(self.params)),
                "collections": [],
                "currency": "GBP",
                "style_id": group,
                "product_type": self.product_type,
                "audience": self.audience,
                "sold_last_5_days": sold,
                "colour_shade": colour[0],
                "colour_family": SHADE_FAMILY[colour[0]],
                "colour_hex": colour[2],
                # The style's full swatch list, rotated so this colourway leads.
                "swatches": swatches[n - 1 :] + swatches[: n - 1],
                "rating": rating,
                "review_count": reviews,
                "skus": skus,
                "price_min": min(prices),
                "price_max": max(prices),
            }
            if size_range is not None:
                rec["size_range"] = size_range
            if self.lengths and "rise" in dict(self.params):
                rec["rise"] = dict(self.params)["rise"]
            if self.unit is not None:
                rec["unit_size"], rec["unit_measure"] = self.unit
            for key in ("was_price", "neckline", "pattern", "leg_style", "units_per_pack"):
                if getattr(self, key) is not None:
                    rec[key] = getattr(self, key)
            if self.units_per_pack is not None:
                # The count kind industrial uses for a package quantity (C62, one).
                rec["attributes"].append(
                    attr("units_per_pack", "Units per pack", self.units_per_pack, "C62")
                )
            out.append(rec)
        return out


def one(colour: Colourway, sold: int) -> tuple[tuple[Colourway, int], ...]:
    return ((colour, sold),)


def on_sale(doc: dict) -> bool:
    return "was_price" in doc and doc["price"] < doc["was_price"]


@dataclass(frozen=True)
class Policy:
    """What the fix reads, in a shape both Python and Elasticsearch apply.

    ``filters``: (field, allowed values), every one required. ``boosts``:
    (field, values, weight) multiplied into the score; a weight below 1 buries.
    """

    filters: tuple[tuple[str, tuple[str, ...]], ...] = ()
    on_sale: bool = False
    boosts: tuple[tuple[str, tuple[str, ...], float], ...] = ()
    collapse: bool = False

    def describe(self) -> str:
        out = [f"filter {f} = {' or '.join(v)}" for f, v in self.filters]
        out += ["filter on sale (price < was_price)"] if self.on_sale else []
        out += [f"{f} = {' or '.join(v)} x{w:g}" for f, v, w in self.boosts]
        out += ["collapse on style_id"] if self.collapse else []
        return "; ".join(out)


@dataclass(frozen=True)
class ClassRow:
    n: int
    cls: str
    query: str
    intended: str
    is_intended: Callable[[dict], bool]
    policy_text: str
    policy: Policy
    targets: tuple[Style, ...]
    #: (style, the policy part that buries it).
    distractors: tuple[tuple[Style, str], ...]


DENIM, MID, LIGHT, ECRU, BLACK = "#4a6a94", "#5b7aa6", "#9fb4cf", "#e8dfcc", "#2a2a2e"
WHITE, NAVY, CAMEL, OLIVE, RUST = "#ffffff", "#26365c", "#c19a6b", "#6b6b3a", "#a8502e"

# --------------------------------------------------------------------------
# 2. "mattress topper": protectors share the head word and sell more
# --------------------------------------------------------------------------

BED = ("Home", "Bedding")
TOPPERS = (
    Style("MTTMEM", "Memory Foam Mattress Topper", "Quillon Sleep", "Home",
          (*BED, "Mattress Toppers"), 60.0,
          "A 5cm layer of memory foam that softens a firm bed, with corner straps.",
          "Mattress Topper", "mattress_topper", one(cw("White", WHITE), 6),
          bed_sized=True, params=(("depth", "5cm"),)),
    Style("MTTFIB", "Hollowfibre Mattress Topper", "Quillon Sleep", "Home",
          (*BED, "Mattress Toppers"), 35.0,
          "A deep hollowfibre topper that adds a soft, springy layer. Machine washable.",
          "Mattress Topper", "mattress_topper", one(cw("White", WHITE), 4),
          bed_sized=True, params=(("depth", "7cm"),)),
    Style("MTTWOL", "Wool Mattress Topper", "Brackenmere Home", "Home",
          (*BED, "Mattress Toppers"), 85.0,
          "A breathable wool-filled topper, quilted in cotton, for a cooler night.",
          "Mattress Topper", "mattress_topper", one(cw("Natural", "#efe8d8"), 3),
          bed_sized=True, params=(("depth", "4cm"),)),
)  # fmt: skip

_BURY_BED = "type boost: Mattress Topper; Mattress Protector buried"
MATTRESS = (
    (Style("MTPQLT", "Quilted Mattress Protector", "Quillon Sleep", "Home",
           (*BED, "Mattress Protectors"), 20.0,
           "A quilted mattress protector with deep skirts. Keeps the mattress and any "
           "mattress topper fresh.",
           "Mattress Protector", "mattress_protector", one(cw("White", WHITE), 880),
           bed_sized=True), _BURY_BED),
    (Style("MTPWTP", "Waterproof Mattress Protector", "Quillon Sleep", "Home",
           (*BED, "Mattress Protectors"), 18.0,
           "A waterproof mattress protector that guards the mattress against spills. Fits "
           "over a mattress topper.",
           "Mattress Protector", "mattress_protector", one(cw("White", WHITE), 760),
           bed_sized=True), _BURY_BED),
    (Style("MTPTOP", "Deep Fill Mattress Topper Protector", "Brackenmere Home", "Home",
           (*BED, "Mattress Protectors"), 28.0,
           "A protector with a padded top: protects the mattress with a topper-soft feel.",
           "Mattress Protector", "mattress_protector", one(cw("White", WHITE), 540),
           bed_sized=True), _BURY_BED),
    (Style("MTPCOL", "Cool Touch Mattress Protector", "Quillon Sleep", "Home",
           (*BED, "Mattress Protectors"), 24.0,
           "A cooling mattress protector for the mattress you have. Goes under a topper too.",
           "Mattress Protector", "mattress_protector", one(cw("Ice", "#e6eef2"), 610),
           bed_sized=True), _BURY_BED),
    (Style("MTRPKT", "Pocket Sprung Mattress", "Quillon Sleep", "Home",
           (*BED, "Mattresses"), 320.0,
           "A medium firm pocket sprung mattress with a built-in comfort topper layer.",
           "Mattress", "mattress_topper", one(cw("Stone", "#d9d3c7"), 190),
           bed_sized=True, params=(("depth", "25cm"),)), "type boost: Mattress buried"),
    (Style("PILPRT", "Pillow Protectors, Pair", "Quillon Sleep", "Home",
           (*BED, "Pillow Protectors"), 9.0,
           "Zipped pillow protectors to match your mattress protector.",
           "Pillow Protector", "pillow", one(cw("White", WHITE), 650)),
     "type boost: Pillow Protector buried"),
)  # fmt: skip

# --------------------------------------------------------------------------
# 3. "balloon jeans": an over-broad synonym (balloon -> barrel) and a
# bestseller boost; the barrel bestseller shows once per colourway
# --------------------------------------------------------------------------

WJEANS = ("Women", "Jeans")
BALLOON = (
    Style("BLNLEG", "Balloon Leg Jeans", "Ferrowick Denim", "Clothing",
          (*WJEANS, "Balloon Jeans"), 45.0,
          "Full through the thigh and knee, curving back in at a cropped ankle.",
          "Jeans", "trousers", ((cw("Mid Wash", MID), 30), (cw("Ecru", ECRU), 21)),
          leg_style="balloon", pattern="plain", lengths=LEGS3,
          params=(("fit", "balloon"), ("rise", "high"))),
    Style("BLNHIW", "High Waisted Balloon Jeans", "Ottery Denim", "Clothing",
          (*WJEANS, "Balloon Jeans"), 42.0,
          "A high waist and a rounded leg that tapers to the hem, in rigid denim.",
          "Jeans", "trousers", one(cw("Light Wash", LIGHT), 25),
          leg_style="balloon", pattern="plain", lengths=LEGS3,
          params=(("fit", "balloon"), ("rise", "high"))),
    Style("BLNCRP", "Cropped Balloon Jeans", "Harbour & Pine", "Clothing",
          (*WJEANS, "Balloon Jeans"), 39.0,
          "A volume leg cut to just above the ankle, with a curved side seam.",
          "Jeans", "trousers", one(cw("Black", BLACK), 18),
          leg_style="balloon", pattern="plain", lengths=LEGS3,
          params=(("fit", "balloon"), ("rise", "mid"))),
)  # fmt: skip

_EXACT = "exact style first: leg_style balloon; collapse on style_id"
BARREL = (
    (Style("BRLMID", "Mid Rise Barrel Jeans", "Ottery Denim", "Clothing",
           (*WJEANS, "Barrel Jeans"), 36.0,
           "Our bestselling barrel jeans: a curved leg that narrows at the ankle.",
           "Jeans", "trousers",
           ((cw("Mid Wash", MID), 940), (cw("Light Wash", LIGHT), 820), (cw("Black", BLACK), 700),
            (cw("Ecru", ECRU), 610), (cw("Vintage Blue", DENIM), 540)),
           leg_style="barrel", pattern="plain", lengths=INSIDE_LEGS,
           params=(("fit", "barrel"), ("rise", "mid"))), _EXACT),
    (Style("BRLHIG", "High Rise Barrel Jeans", "Ferrowick Denim", "Clothing",
           (*WJEANS, "Barrel Jeans"), 40.0,
           "Barrel jeans with a high rise and a soft curve through the knee.",
           "Jeans", "trousers", ((cw("Rinse", NAVY), 640), (cw("Washed Black", BLACK), 460)),
           leg_style="barrel", pattern="plain", lengths=LEGS3,
           params=(("fit", "barrel"), ("rise", "high"))), _EXACT),
    (Style("BRLKID", "Girls' Barrel Jeans (6-16 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "Girls", "Jeans"), 18.0,
           "Barrel jeans for girls with an adjustable waist.",
           "Jeans", "trousers", one(cw("Mid Wash", MID), 520), audience="kids",
           leg_style="barrel", pattern="plain", lengths=("Regular",),
           params=(("fit", "barrel"), ("rise", "mid"))), _EXACT),
    (Style("BRLTRS", "Barrel Leg Trousers", "Larkmoor", "Clothing",
           ("Women", "Trousers", "Barrel Trousers"), 32.0,
           "Twill barrel trousers that wear like jeans, with a pressed crease.",
           "Trousers", "trousers", one(cw("Khaki", OLIVE), 480),
           leg_style="barrel", pattern="plain", lengths=LEGS3,
           params=(("fit", "barrel"), ("rise", "high"))), _EXACT),
)  # fmt: skip

# --------------------------------------------------------------------------
# 4. "womens boat neck top": the word "neck" matched as a keyword
# --------------------------------------------------------------------------

TOPS = ("Women", "Tops")
BOAT = (
    Style("BNTSTR", "Striped Boat Neck Top", "Harbour & Pine", "Clothing",
          (*TOPS, "Long Sleeve Tops"), 24.0,
          "A wide, shallow neckline that runs shoulder to shoulder, in striped cotton.",
          "Top", "top", one(cw("Navy Stripe", WHITE, "stripe", NAVY), 40),
          neckline="boat", pattern="stripe", size_range="regular",
          params=(("neckline", "boat"), ("sleeve", "long"))),
    Style("BNTJER", "Boat Neck Jersey Top", "Larkmoor", "Clothing",
          (*TOPS, "Jersey Tops"), 20.0,
          "Soft jersey with a wide boat neckline and three quarter sleeves.",
          "Top", "top", one(cw("Ecru", ECRU), 22),
          neckline="boat", pattern="plain", size_range="regular",
          params=(("neckline", "boat"), ("sleeve", "three_quarter"))),
    Style("SNTLNG", "Slash Neck Long Sleeve Top", "Wrenfield", "Clothing",
          (*TOPS, "Long Sleeve Tops"), 26.0,
          "A straight slash neckline across the collarbone, in a fine rib.",
          "Top", "top", one(cw("Black", BLACK), 35),
          neckline="slash", pattern="plain", size_range="regular",
          params=(("neckline", "boat"), ("sleeve", "long"))),
)  # fmt: skip

_NECK = "type = Top; neckline boat or slash boosted"
NECK = (
    (Style("HNRIBT", "Womens High Neck Ribbed Top", "Larkmoor", "Clothing",
           (*TOPS, "Jersey Tops"), 22.0,
           "A ribbed high neck top for women. The neck sits close; a neat neck finish.",
           "Top", "top", one(cw("Oat", "#d8cbb2"), 950),
           neckline="high", pattern="plain", size_range="regular",
           params=(("neckline", "roll_neck"), ("sleeve", "long"))), _NECK),
    (Style("CNCOTT", "Womens Crew Neck Cotton Top", "Harbour & Pine", "Clothing",
           (*TOPS, "T-Shirts"), 14.0,
           "A crew neck cotton top for women with a ribbed neck trim.",
           "Top", "top", one(cw("White", WHITE), 820),
           neckline="crew", pattern="plain", size_range="regular",
           params=(("neckline", "crew"), ("sleeve", "short"))), _NECK),
    (Style("RNJERS", "Womens Round Neck Jersey Top", "Wrenfield", "Clothing",
           (*TOPS, "Jersey Tops"), 16.0,
           "A round neck jersey top for women, the neck bound in self fabric.",
           "Top", "top", one(cw("Rust", RUST), 700),
           neckline="round", pattern="plain", size_range="regular",
           params=(("neckline", "crew"), ("sleeve", "long"))), _NECK),
    (Style("COLTOP", "Womens Collared Jersey Top", "Hollinwray Knits", "Clothing",
           (*TOPS, "Jersey Tops"), 26.0,
           "A womens jersey top with a neat collar at the neck and a button placket.",
           "Top", "top", one(cw("Navy", NAVY), 610),
           neckline="collared", pattern="plain", size_range="regular",
           params=(("neckline", "crew"), ("sleeve", "long"))), _NECK),
    (Style("SQBODY", "Womens Square Neck Bodysuit", "Larkmoor", "Clothing",
           (*TOPS, "Bodysuits"), 18.0,
           "A womens bodysuit with a square neck, worn as a top. Popper fastening.",
           "Bodysuit", "top", one(cw("Black", BLACK), 650),
           neckline="square", pattern="plain", size_range="regular",
           params=(("neckline", "square"), ("sleeve", "sleeveless"))), "type = Top"),
    (Style("NTSETS", "Womens Tie Neck Top and Trousers Set", "Wrenfield", "Clothing",
           ("Women", "Co-ords", "Sets"), 48.0,
           "A womens co-ord: a tie neck top and matching wide trousers.",
           "Co-ord Set", "outfit_set", one(cw("Sage", "#9bb08f"), 430),
           pattern="plain", size_range="regular", params=(("tee", "#9bb08f"),)), "type = Top"),
)  # fmt: skip

# --------------------------------------------------------------------------
# 5. "check contrast bomber jacket": type not enforced, "contrast" ignored,
# audience not defaulted
# --------------------------------------------------------------------------

COATS = ("Women", "Coats & Jackets")
CHECK = (
    Style("CKBCON", "Check Bomber Jacket with Contrast Collar", "Calderby & Lune", "Clothing",
          (*COATS, "Bomber Jackets"), 69.0,
          "A wool-blend check bomber with a contrast rib collar and cuffs.",
          "Bomber Jacket", "coat", one(cw("Brown Check", CAMEL, "gingham", "#5a3426"), 14),
          pattern="check", size_range="regular"),
    Style("CKBWOL", "Wool Check Bomber Jacket", "Bramblewood", "Clothing",
          (*COATS, "Bomber Jackets"), 75.0,
          "A bomber in a soft check wool with contrast black ribbing.",
          "Bomber Jacket", "coat", one(cw("Grey Check", "#9a9a9a", "gingham", BLACK), 11),
          pattern="check", size_range="regular"),
    Style("CKBPAD", "Padded Check Bomber", "Harbour & Pine", "Clothing",
          (*COATS, "Bomber Jackets"), 59.0,
          "A lightly padded bomber in a checked twill, zip front, contrast lining.",
          "Bomber Jacket", "coat", one(cw("Navy Check", NAVY, "gingham", "#c8312e"), 9),
          pattern="check", size_range="regular"),
)  # fmt: skip

_TYPE = "type = Bomber Jacket (hard); pattern check boosted"
BOMBER = (
    (Style("BMBCRD", "Cord Bomber Jacket", "Wrenfield", "Clothing",
           (*COATS, "Bomber Jackets"), 55.0,
           "A plain cord bomber jacket with a zip front. The bomber jacket of the season.",
           "Bomber Jacket", "coat", one(cw("Tobacco", "#7a4a2a"), 900),
           pattern="plain", size_range="regular"), "pattern check boosted"),
    (Style("BMBWOL", "Wool Blend Bomber Jacket", "Larkmoor", "Clothing",
           (*COATS, "Bomber Jackets"), 65.0,
           "A plain wool blend bomber jacket with ribbed trims. A bomber jacket for every day.",
           "Bomber Jacket", "coat", one(cw("Charcoal", "#4a4a50"), 720),
           pattern="plain", size_range="regular"), "pattern check boosted"),
    (Style("SUITCK", "Check Suit Jacket", "Calderby & Lune", "Clothing",
           (*COATS, "Blazers"), 80.0,
           "A single breasted check suit jacket, the check jacket that matches our trousers.",
           "Suit Jacket", "coat", one(cw("Grey Check", "#9a9a9a", "gingham", BLACK), 650),
           pattern="check", size_range="regular"), _TYPE),
    (Style("CARCHK", "Checked Car Coat", "Bramblewood", "Clothing",
           (*COATS, "Coats"), 99.0,
           "A checked car coat, jacket length, with a contrast collar.",
           "Coat", "coat", one(cw("Camel Check", CAMEL, "gingham", NAVY), 500),
           pattern="check", size_range="regular"), _TYPE),
    (Style("KIDBMB", "Boys' Bomber Jacket (2-8 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "Boys", "Coats & Jackets"), 24.0,
           "A bomber jacket for boys with contrast stripe cuffs.",
           "Bomber Jacket", "coat", one(cw("Navy", NAVY), 600), audience="kids",
           pattern="plain", size_range="regular"), "audience adult by default"),
    (Style("BABBMB", "Baby Bomber Jacket (3-36 Mths)", "Little Fernby", "Clothing",
           ("Baby", "Coats & Jackets"), 20.0,
           "A soft padded bomber jacket for babies, with contrast ribbing.",
           "Bomber Jacket", "coat", one(cw("Olive", OLIVE), 420), audience="baby",
           pattern="plain"), "audience adult by default"),
)  # fmt: skip

# --------------------------------------------------------------------------
# 6. "petite sale": the size range and the sale state are not extracted
# --------------------------------------------------------------------------

PETITE = (
    Style("PETDRS", "Petite Wrap Midi Dress", "Larkmoor", "Clothing",
          ("Women", "Petite", "Dresses"), 28.0,
          "A wrap midi dress cut shorter in the body and hem for petite frames.",
          "Dress", "dress", one(cw("Navy Print", NAVY, "polka", WHITE), 4), was_price=40.0,
          size_range="petite", pattern="print"),
    Style("PETTRS", "Petite Wide Leg Trousers", "Wrenfield", "Clothing",
          ("Women", "Petite", "Trousers"), 22.0,
          "Wide leg trousers with a shorter inside leg for petite heights.",
          "Trousers", "trousers", one(cw("Black", BLACK), 3), was_price=32.0,
          lengths=("Extra Short", "Short/Petite"), pattern="plain", leg_style="wide",
          params=(("fit", "wide_leg"), ("rise", "high"))),
    Style("PETJNS", "Petite Straight Jeans", "Ottery Denim", "Clothing",
          ("Women", "Petite", "Jeans"), 25.0,
          "Straight jeans with a 28 inch inside leg, made for petite heights.",
          "Jeans", "trousers", one(cw("Mid Wash", MID), 5), was_price=35.0,
          lengths=("Extra Short", "Short/Petite"), pattern="plain", leg_style="straight",
          params=(("fit", "straight"), ("rise", "mid"))),
)  # fmt: skip

_SALE = "size range petite and on sale, as filters"
BESTSELLERS = (
    (Style("TAPTRS", "Tapered Trousers", "Wrenfield", "Clothing",
           ("Women", "Trousers", "Tapered Trousers"), 30.0,
           "Our bestselling tapered trousers. Also cut in petite and tall.",
           "Trousers", "trousers", one(cw("Navy", NAVY), 960),
           lengths=LEGS3, pattern="plain", leg_style="tapered",
           params=(("fit", "slim"), ("rise", "high"))), _SALE),
    (Style("STRJNS", "Straight Leg Jeans", "Ottery Denim", "Clothing",
           (*WJEANS, "Straight Jeans"), 32.0,
           "Straight leg jeans in a regular length. Also cut in petite and long.",
           "Jeans", "trousers", one(cw("Indigo", DENIM), 910),
           lengths=LEGS3, pattern="plain", leg_style="straight",
           params=(("fit", "straight"), ("rise", "high"))), _SALE),
    (Style("WIDTRS", "Wide Leg Trousers", "Larkmoor", "Clothing",
           ("Women", "Trousers", "Wide Leg Trousers"), 34.0,
           "Fluid wide leg trousers with a pressed crease. Also cut in petite.",
           "Trousers", "trousers", one(cw("Black", BLACK), 800),
           lengths=("Short/Petite", "Regular"), pattern="plain", leg_style="wide",
           params=(("fit", "wide_leg"), ("rise", "high"))), _SALE),
    (Style("SLMJNS", "Slim Jeans", "Ferrowick Denim", "Clothing",
           (*WJEANS, "Slim Jeans"), 30.0,
           "Slim jeans with stretch. Also cut in petite and tall lengths.",
           "Jeans", "trousers", one(cw("Black", BLACK), 690),
           # Cut in petite, but the petite lengths are sold out.
           lengths=LEGS3, sold_out=("Short/Petite",), pattern="plain", leg_style="slim",
           params=(("fit", "slim"), ("rise", "mid"))), _SALE),
)  # fmt: skip

# --------------------------------------------------------------------------
# 7. "womens sale dresses": "sale" ignored, so the full-price bestsellers win
# --------------------------------------------------------------------------

DRESSES = ("Women", "Dresses")
SALE_DRESSES = (
    Style("SDWRAP", "Womens Wrap Dress", "Larkmoor", "Clothing",
          (*DRESSES, "Wrap Dresses"), 27.0,
          "A jersey wrap dress for women with a tie waist.",
          "Dress", "dress", one(cw("Green Print", "#2f6b3c", "polka", WHITE), 5), was_price=45.0,
          size_range="regular", pattern="print"),
    Style("SDSHRT", "Womens Shirt Dress", "Harbour & Pine", "Clothing",
          (*DRESSES, "Shirt Dresses"), 23.0,
          "A cotton shirt dress for women with a self belt.",
          "Dress", "dress", one(cw("Blue Stripe", WHITE, "stripe", "#5b84b8"), 4), was_price=38.0,
          size_range="regular", pattern="stripe"),
    Style("SDMAXI", "Womens Tiered Maxi Dress", "Wrenfield", "Clothing",
          (*DRESSES, "Maxi Dresses"), 33.0,
          "A tiered maxi dress for women in cotton voile.",
          "Dress", "dress", one(cw("Terracotta", RUST), 6), was_price=55.0,
          size_range="regular", pattern="plain"),
)  # fmt: skip

_ONSALE = "on sale (price < was_price), as a filter"
FULL_PRICE = (
    (Style("FPLINN", "Womens Linen Midi Dress", "Harbour & Pine", "Clothing",
           (*DRESSES, "Midi Dresses"), 45.0,
           "A linen midi dress for women. Our most loved dress of the season.",
           "Dress", "dress", one(cw("White", WHITE), 950),
           size_range="regular", pattern="plain"), _ONSALE),
    (Style("FPTEES", "Womens Jersey T-Shirt Dress", "Larkmoor", "Clothing",
           (*DRESSES, "T-Shirt Dresses"), 22.0,
           "An easy jersey t-shirt dress for women.",
           "Dress", "dress", one(cw("Navy", NAVY), 870),
           size_range="regular", pattern="plain"), _ONSALE),
    (Style("FPSMOK", "Womens Smocked Mini Dress", "Wrenfield", "Clothing",
           (*DRESSES, "Mini Dresses"), 35.0,
           "A smocked mini dress for women with puff sleeves.",
           "Dress", "dress", one(cw("Gingham", WHITE, "gingham", "#c8312e"), 720),
           size_range="regular", pattern="check"), _ONSALE),
    (Style("FPSLIP", "Womens Satin Slip Dress", "Larkmoor", "Clothing",
           (*DRESSES, "Slip Dresses"), 39.0,
           "A bias cut satin slip dress for women.",
           "Dress", "dress", one(cw("Champagne", "#e8d6b0"), 640),
           size_range="regular", pattern="plain"), _ONSALE),
    (Style("KIDDRS", "Girls' Party Dress (2-8 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "Girls", "Dresses"), 20.0,
           "A tulle party dress for girls. Dresses for every party.",
           "Dress", "dress", one(cw("Pink", "#f3c6cf"), 560), audience="kids",
           size_range="regular", pattern="plain"), "audience adult by default; on sale filter"),
)  # fmt: skip


# --------------------------------------------------------------------------
# 9. "5 pack socks" (an on-stage demo case): the count lives in title
# spellings ("5 Pack", "5pk", "Pack of 5"), so "5pk" misses and the
# bestselling 7 pack and a single pair win
# --------------------------------------------------------------------------

SOCKS = ("Men", "Socks")
FIVE_PACKS = (
    Style("SK5PKC", "Cotton Rich Ankle Socks 5pk", "Harbour & Pine", "Clothing",
          (*SOCKS, "Ankle Socks"), 10.0, "Cushioned ankle socks in soft cotton rich yarn.",
          "Socks", "box", one(cw("Black", BLACK), 28), pattern="plain", units_per_pack=5),
    Style("SK5BMB", "Bamboo Socks, Pack of 5", "Wrenfield", "Clothing",
          (*SOCKS, "Everyday Socks"), 12.0, "Breathable bamboo socks with a comfort top.",
          "Socks", "box", one(cw("Navy", NAVY), 24), pattern="plain", units_per_pack=5),
    Style("SK5SPT", "Sports Trainer Socks 5 Pack", "Stridewell", "Clothing",
          (*SOCKS, "Sports Socks"), 9.0, "Trainer liners with an arch grip.",
          "Socks", "box", one(cw("White", WHITE), 9), pattern="plain", units_per_pack=5),
)  # fmt: skip

_PACK = "units_per_pack = 5, as a filter"
PACKS = (
    (Style("SK7PKC", "Cotton Rich Socks 7 Pack", "Harbour & Pine", "Clothing",
           (*SOCKS, "Everyday Socks"), 14.0,
           "Our bestselling socks: a pack of socks for every day of the week.",
           "Socks", "box", one(cw("Black", BLACK), 960), pattern="plain", units_per_pack=7),
     _PACK),
    (Style("SK3PKS", "Striped Socks 3 Pack", "Wrenfield", "Clothing",
           (*SOCKS, "Everyday Socks"), 8.0, "A pack of striped cotton socks.",
           "Socks", "box", one(cw("Stripe", WHITE, "stripe", RUST), 720), pattern="stripe",
           units_per_pack=3), _PACK),
    (Style("SK1WAL", "Wool Walking Socks", "Stridewell", "Clothing",
           (*SOCKS, "Walking Socks"), 9.0,
           "Cushioned wool walking socks, sold as a single pair. Socks for long days.",
           "Socks", "box", one(cw("Grey", "#9a9a9a"), 690), pattern="plain", units_per_pack=1),
     _PACK),
    (Style("SK5KID", "Kids' School Socks 5 Pack (6-16 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "School", "Socks"), 7.0, "Five pairs of grey school socks.",
           "Socks", "box", one(cw("Grey", "#9a9a9a"), 610), audience="kids", pattern="plain",
           units_per_pack=5), "audience adult by default"),
)  # fmt: skip


# --------------------------------------------------------------------------
# Beauty: a third-party brand; the variant axis is the shade (one doc each,
# food-word shade names), every shade the same unit size. Not a query row.
# --------------------------------------------------------------------------

MAKEUP = ("Beauty", "Make-Up")
BEAUTY = (
    Style("BTYLIP", "Satin Lipstick", "Kestlewood Cosmetics", "Beauty", (*MAKEUP, "Lipstick"),
          25.0, "A creamy satin lipstick with a soft sheen, in a slim bullet.",
          "Lipstick", "lipstick",
          ((cw("Wild Honey", "#b9774a"), 2), (cw("Mocha Kiss", "#7b4a3a"), 1),
           (cw("Cherry Pop", "#b0182f"), 1)), unit=(1.9, "g")),
    Style("BTYFND", "Soft Veil Foundation", "Kestlewood Cosmetics", "Beauty",
          (*MAKEUP, "Foundation"), 32.0, "A light, buildable foundation with a natural finish.",
          "Foundation", "bottle",
          ((cw("Porcelain", "#f1dcc8"), 1), (cw("Caramel", "#c48a5c"), 2),
           (cw("Toffee", "#9a6440"), 1), (cw("Espresso", "#5a3a28"), 1)), unit=(30.0, "ml")),
)  # fmt: skip


def _type(*types: str) -> Callable[[dict], bool]:
    return lambda d: d.get("product_type") in types and d.get("audience") == "adult"


ROWS = (
    ClassRow(2, "Sibling types share a head word", "mattress topper", "a mattress topper",
             _type("Mattress Topper"), "product-type boost: topper; protector and mattress buried",
             Policy(boosts=(("product_type", ("Mattress Topper",), 10.0),
                            ("product_type", ("Mattress Protector", "Mattress",
                                              "Pillow Protector"), 0.2))),
             TOPPERS, MATTRESS),
    ClassRow(3, "Over-broad style synonym plus a bestseller boost", "balloon jeans",
             "balloon leg jeans",
             lambda d: _type("Jeans")(d) and d.get("leg_style") == "balloon",
             "exact style term first, synonym second; collapse colour variants",
             Policy(boosts=(("leg_style", ("balloon",), 10.0),), collapse=True),
             BALLOON, BARREL),
    ClassRow(4, "A neckline word matched as a keyword", "womens boat neck top",
             "a boat (or slash) neck top",
             lambda d: _type("Top")(d) and d.get("neckline") in ("boat", "slash"),
             "neckline attribute: boat = slash, others buried; type = top",
             Policy(filters=(("product_type", ("Top",)),),
                    boosts=(("neckline", ("boat", "slash"), 10.0),)),
             BOAT, NECK),
    ClassRow(5, "Product type, pattern and audience not enforced",
             "check contrast bomber jacket", "an adult check bomber jacket",
             lambda d: _type("Bomber Jacket")(d) and d.get("pattern") == "check",
             "type = bomber (hard), pattern = check (boost), audience adult by default",
             Policy(filters=(("product_type", ("Bomber Jacket",)), ("audience", ("adult",))),
                    boosts=(("pattern", ("check",), 5.0),)),
             CHECK, BOMBER),
    ClassRow(6, "Size range and sale state not extracted", "petite sale",
             "a petite item on sale",
             lambda d: "petite" in d.get("size_range", ()) and on_sale(d),
             "petite to a size-range filter; sale to an on-sale filter",
             Policy(filters=(("size_range", ("petite",)),), on_sale=True),
             PETITE, BESTSELLERS),
    ClassRow(7, "Sale word ignored", "womens sale dresses", "an adult dress on sale",
             lambda d: _type("Dress")(d) and on_sale(d),
             "sale to an on-sale filter (price below was-price)",
             Policy(filters=(("product_type", ("Dress",)), ("audience", ("adult",))),
                    on_sale=True),
             SALE_DRESSES, FULL_PRICE),
    ClassRow(9, "Pack count only in title spellings", "5 pack socks", "an adult 5 pack of socks",
             lambda d: _type("Socks")(d) and d.get("units_per_pack") == 5,
             "units_per_pack (a C62 count) as a filter; audience adult by default",
             Policy(filters=(("units_per_pack", ("5",)), ("audience", ("adult",)))),
             FIVE_PACKS, PACKS),
)  # fmt: skip


def class_docs() -> list[dict]:
    """Every record of :data:`ROWS` (targets first), then :data:`BEAUTY`, each ranked."""
    styles = [s for row in ROWS for s in (*row.targets, *(x for x, _ in row.distractors))]
    out = [d for s in (*styles, *BEAUTY) for d in s.docs()]
    ranked = sorted(out, key=lambda d: (-d["sold_last_5_days"], d["product_id"]))
    rank = {d["product_id"]: n for n, d in enumerate(ranked, 1)}
    return [{**d, "bestseller_rank": rank[d["product_id"]]} for d in out]


def corpus() -> list[dict]:
    """The catalog the proof indexes: the round 4 corpus, then every class record."""
    return [*base_corpus(), *class_docs()]


def fingerprint(catalog: list[dict]) -> str:
    """sha256 of the catalog as the proof indexed it: a record change makes the proof stale."""
    blob = "".join(json.dumps(d, sort_keys=True, ensure_ascii=False) + "\n" for d in catalog)
    return hashlib.sha256(blob.encode()).hexdigest()


# ==========================================================================
# The Elasticsearch bodies (the baseline mimics the live site)
# ==========================================================================

#: Search-time only: the over-broad style synonym class 3 observed.
SYNONYMS = ("balloon => balloon, barrel",)
KEYWORDS = ("product_id", "style_id", "product_type", "audience", "size_range",
            "neckline", "pattern", "leg_style", "rise", "colour_family",
            "colour_shade")  # fmt: skip
#: Price and stock are per SKU, so a SKU match must stay inside one SKU.
SKUS = {
    "type": "nested",
    "properties": {
        "waist": {"type": "keyword"},
        "inside_leg": {"type": "keyword"},
        "in_stock": {"type": "boolean"},
        "bed_size": {"type": "keyword"},
        "price": {"type": "float"},
    },
}


def index_body() -> dict:
    text = {"type": "text", "analyzer": "plain", "search_analyzer": "with_synonyms"}
    chain = ["possessive", "lowercase"]
    return {
        "settings": {
            "number_of_shards": 1,
            "analysis": {
                "filter": {
                    "possessive": {"type": "stemmer", "language": "possessive_english"},
                    "stem": {"type": "stemmer", "language": "english"},
                    "styles": {"type": "synonym_graph", "synonyms": list(SYNONYMS)},
                },
                "analyzer": {
                    "plain": {"tokenizer": "standard", "filter": [*chain, "stem"]},
                    "with_synonyms": {
                        "tokenizer": "standard",
                        "filter": [*chain, "styles", "stem"],
                    },
                },
            },
        },
        "mappings": {
            "dynamic": False,
            "properties": {
                "title": text,
                "description": text,
                **{k: {"type": "keyword"} for k in KEYWORDS},
                "price": {"type": "float"},
                "was_price": {"type": "float"},
                "sold_last_5_days": {"type": "integer"},
                "bestseller_rank": {"type": "integer"},
                "units_per_pack": {"type": "integer"},
                **{k: {"type": "float"} for k in ("price_min", "price_max", "rating")},
                "review_count": {"type": "integer"},
                "skus": SKUS,
            },
        },
    }


POPULARITY = (
    {"field_value_factor": {"field": "sold_last_5_days", "modifier": "log1p", "missing": 1}},
    {"filter": {"range": {"bestseller_rank": {"lte": BESTSELLER_TOP}}}, "weight": 1.5},
)
ON_SALE = "doc['was_price'].size() > 0 && doc['price'].value < doc['was_price'].value"


def _search(query: dict, functions: list[dict], collapse: bool, size: int) -> dict:
    body = {
        "size": size,
        "_source": ["product_id", "title"],
        "query": {
            "function_score": {
                "query": query,
                "functions": functions,
                "score_mode": "multiply",
                "boost_mode": "multiply",
            }
        },
        "sort": ["_score", {"product_id": "asc"}],
    }
    if collapse:
        body["collapse"] = {"field": "style_id"}
    return body


def text_query(q: str) -> dict:
    return {"multi_match": {"query": q, "fields": ["title^2", "description"], "tie_breaker": 0.3}}


def baseline_body(row: ClassRow, size: int = 5) -> dict:
    """BM25 over title and description, times the popularity boost: no policy."""
    return _search(text_query(row.query), list(POPULARITY), False, size)


def policy_body(row: ClassRow, size: int = 5) -> dict:
    """The baseline plus the row's :class:`Policy`, approximated in raw Elasticsearch."""
    p = row.policy
    filters: list[dict] = [{"terms": {f: list(v)}} for f, v in p.filters]
    if p.on_sale:
        filters.append({"script": {"script": ON_SALE}})
    query = {"bool": {"must": text_query(row.query), "filter": filters}}
    boosts = [{"filter": {"terms": {f: list(v)}}, "weight": w} for f, v, w in p.boosts]
    return _search(query, [*POPULARITY, *boosts], p.collapse, size)


# ==========================================================================
# The recorded proof, rendered for the README
# ==========================================================================


def verdicts(proof: dict, catalog: list[dict]) -> list[str]:
    """Every way ``proof`` fails the claim; empty when it holds over ``catalog``.

    The claim: the proof was taken over ``catalog``; per row, no target in the
    baseline top 3 and only targets in the policy top 3.
    """
    by_id = {d["product_id"]: d for d in catalog}
    out = []
    if proof.get("fingerprint") != fingerprint(catalog):
        out.append("the proof was taken over another catalog: re-run es_proof.py")
    got = {r["query"]: r for r in proof.get("rows", [])}
    for row in ROWS:
        rec = got.get(row.query)
        if rec is None:
            out.append(f"{row.query!r}: not in the proof")
            continue
        base = [by_id[h["product_id"]] for h in rec["baseline"][:3] if h["product_id"] in by_id]
        pol = [by_id[h["product_id"]] for h in rec["policy"][:3] if h["product_id"] in by_id]
        if any(row.is_intended(d) for d in base):
            out.append(f"{row.query!r}: a target is in the baseline top 3")
        if len(pol) != 3 or not all(row.is_intended(d) for d in pol):
            out.append(f"{row.query!r}: the policy top 3 is not all targets")
    return out


def markdown(proof: dict, catalog: list[dict]) -> str:
    """The README's before and after table; a target is in bold."""
    by_id = {d["product_id"]: d for d in catalog}
    got = {r["query"]: r for r in proof["rows"]}

    def cell(row: ClassRow, hits: list[dict]) -> str:
        out = []
        for n, h in enumerate(hits, 1):
            name = f"{h['title']} `{h['product_id']}`"
            target = row.is_intended(by_id[h["product_id"]])
            out.append(f"{n}. **{name}**" if target else f"{n}. {name}")
        return "<br>".join(out)

    lines = [
        "| # | Class | Query | Baseline top 5 (BM25 x popularity) | With the policy: top 5 "
        "| Policy (raw ES) |",
        "|---|---|---|---|---|---|",
    ]
    for row in ROWS:
        r = got[row.query]
        lines.append(
            f"| {row.n} | {row.cls} | *{row.query}* | {cell(row, r['baseline'])} | "
            f"{cell(row, r['policy'])} | {row.policy.describe()} |"
        )
    return "\n".join(lines)
