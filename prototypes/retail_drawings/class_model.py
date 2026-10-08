"""The record model of :mod:`real_classes`: closed vocabularies, :class:`Style`
(one product page; :meth:`Style.docs` emits one doc per colourway), :class:`Policy`
and :class:`ClassRow`. The rows themselves are data, in :mod:`class_rows`.
Standard library only.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from departments import check as check_departments
from variants import Colourway, attr, drawing

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
                   "red", "pink", "orange", "gold", "silver", "multi")  # fmt: skip
#: Joins a category path into one keyword per ancestor (as industrial does);
#: a routed policy names its node in this form.
PATH_SEPARATOR = "/"
#: The metal finishes a ``metal`` style's colourway is made in.
FINISHES = ("Rose Gold", "Yellow Gold", "White Gold", "Silver")
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
    "Rust": "orange", "Terracotta": "orange", "Burnt Orange": "orange", "Orange": "orange",
    "Cream": "cream",
    "Red": "red",
    "Rose Gold": "gold", "Yellow Gold": "gold", "White Gold": "silver", "Silver": "silver",
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
#: The bed size vocabulary bedding and beds share: a label carries its size in
#: feet; the value is the mattress (width, length) in cm.
BED_SIZE_DIMS = {
    "Single (3 ft)": (90, 190),
    "Small Double (4 ft)": (120, 190),
    "Double (4 ft 6)": (135, 190),
    "King Size (5 ft)": (150, 200),
    "Super King Size (6 ft)": (180, 200),
}
#: The sizes bedding is made in; the price steps up per size.
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
    #: Beauty and food: (unit size, "g" or "ml") of every shade or product.
    unit: tuple[float, str] | None = None
    #: Furniture: the :data:`BED_SIZE_DIMS` sizes it is made in, one SKU each
    #: with its price and dimensions; a bed need not come in every size.
    bed_frame: tuple[str, ...] = ()
    #: Signals a tile shows as badges (see :func:`badges`).
    new_in: bool = False
    trending: bool = False
    online_only: bool = False
    #: An offer with no was-price (a multi-buy); a was-price is always an offer.
    multibuy: bool = False
    #: A merchandising label on the tile ("The Active Edit"), never a category.
    sub_collection: str | None = None
    #: A named product line; its name may carry another type's word.
    product_line: str | None = None
    #: Alcohol by volume, in percent: an attribute, whatever the title says.
    abv: float | None = None
    #: Food and furniture: no colour facet and no swatches.
    colourless: bool = False
    #: Metal goods (jewellery, watches, lighting, tech): the colour IS the
    #: metal finish, so each colourway also carries a ``finish`` attribute.
    metal: bool = False
    #: Further (key, name, value) attributes, unitless.
    extra: tuple[tuple[str, str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.lengths and self.size_range is not None:
            raise ValueError(f"{self.code}: a legwear size_range is derived from its SKUs")
        if self.bed_frame and not set(self.bed_frame) <= set(BED_SIZE_DIMS):
            raise ValueError(f"{self.code}: a bed size outside the shared vocabulary")
        if self.metal and not {c[0] for c, _ in self.colourways} <= set(FINISHES):
            raise ValueError(f"{self.code}: a metal colourway outside the finishes")

    def skus(self, colour: Colourway) -> list[dict]:
        """The colourway's SKUs: waist x inside leg, or bed sizes, or none."""
        if self.bed_frame:
            step = round(self.price / 5)
            return [
                {"bed_size": b, "width_cm": BED_SIZE_DIMS[b][0], "length_cm": BED_SIZE_DIMS[b][1],
                 "price": float(self.price + n * step), "in_stock": True}
                for n, b in enumerate(self.bed_frame)
            ]  # fmt: skip
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
            {"shade": c[0], "family": SHADE_FAMILY[c[0]], "hex": c[2]}
            for c, _ in self.colourways
            if not self.colourless
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
                "brand_owner": BRAND_OWNER[self.brand],
                "department": check_departments([self.department], self.title),
                "category_path": list(self.path),
                "category_leaf": self.path[-1],
                # The tile's "from" price: the cheapest SKU.
                "price": min(prices),
                "description": self.description,
                "attributes": [] if self.colourless else [attr("colour", "Colour", colour[0])],
                "drawing": drawing(self.shape, colour, **dict(self.params)),
                "collections": [],
                "currency": "GBP",
                "style_id": group,
                "product_type": self.product_type,
                "audience": self.audience,
                "sold_last_5_days": sold,
            }
            if not self.colourless:
                rec |= {
                    "colour_shade": colour[0],
                    "colour_family": SHADE_FAMILY[colour[0]],
                    "colour_hex": colour[2],
                    # The style's full swatch list, rotated so this colourway leads.
                    "swatches": swatches[n - 1 :] + swatches[: n - 1],
                }
            rec |= {
                "rating": rating,
                "review_count": reviews,
                "skus": skus,
                "price_min": min(prices),
                "price_max": max(prices),
                "offer": self.was_price is not None or self.multibuy,
                "online_only": self.online_only,
                "new_in": self.new_in,
                "trending": self.trending,
            }
            if size_range is not None:
                rec["size_range"] = size_range
            if self.lengths and "rise" in dict(self.params):
                rec["rise"] = dict(self.params)["rise"]
            if self.unit is not None:
                rec["unit_size"], rec["unit_measure"] = self.unit
            for key in ("was_price", "neckline", "pattern", "leg_style", "units_per_pack",
                        "sub_collection", "product_line", "abv"):  # fmt: skip
                if getattr(self, key) is not None:
                    rec[key] = getattr(self, key)
            if self.was_price is not None:
                rec["discount_pct"] = round(100 * (self.was_price - rec["price"]) / self.was_price)
            if self.units_per_pack is not None:
                # The count kind industrial uses for a package quantity (C62, one).
                rec["attributes"].append(
                    attr("units_per_pack", "Units per pack", self.units_per_pack, "C62")
                )
            if self.abv is not None:
                # P1 is UN/CEFACT's percent.
                rec["attributes"].append(attr("abv", "ABV", self.abv, "P1"))
            if self.metal:
                rec["attributes"].append(attr("finish", "Finish", colour[0].lower()))
            rec["attributes"] += [attr(k, name, v) for k, name, v in self.extra]
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
    ``route``: a category node (joined with "/"); its docs are recalled even
    when the text misses them, and boosted. ``sku_filters``: (SKU field,
    values) that one in-stock nested SKU must carry.
    """

    filters: tuple[tuple[str, tuple[str, ...]], ...] = ()
    on_sale: bool = False
    boosts: tuple[tuple[str, tuple[str, ...], float], ...] = ()
    collapse: bool = False
    route: str | None = None
    sku_filters: tuple[tuple[str, tuple[str, ...]], ...] = ()

    def describe(self) -> str:
        out = [f"filter {f} = {' or '.join(v)}" for f, v in self.filters]
        out += ["filter on sale (price < was_price)"] if self.on_sale else []
        out += [f"filter an in-stock SKU with {f} = {' or '.join(v)}" for f, v in self.sku_filters]
        out += [f"{f} = {' or '.join(v)} x{w:g}" for f, v, w in self.boosts]
        out += [f"route to {self.route} (recalled, boosted)"] if self.route else []
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


#: Who makes a brand: the retailer ("own") or another house ("third_party").
BRAND_OWNERS = ("own", "third_party")
_THIRD_PARTY = ("Kestlewood Cosmetics", "Stridewell", "Calderby & Lune", "Bramblewood",
                "Hollinwray Knits", "Lanternby", "Vine & Valley", "Thistle & Wren",
                "Crunchworth", "Olivar Grove", "Pewley Table")  # fmt: skip
_OWN = ("Harbour & Pine", "Larkmoor", "Wrenfield", "Little Fernby", "Quillon Sleep",
        "Ottery Denim", "Ferrowick Denim", "Goldfield Farms", "Crofter's Bakehouse",
        "Pantry Mill", "Hearth & Table", "Brackenmere Home", "Meadowgate Dairy",
        "Copper Hill Preserves", "Saltmarsh", "Velling Apothecary")  # fmt: skip
BRAND_OWNER = {**dict.fromkeys(_OWN, "own"), **dict.fromkeys(_THIRD_PARTY, "third_party")}
