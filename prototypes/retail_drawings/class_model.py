"""The record model of :mod:`real_classes`: closed vocabularies, :class:`Style`
(one product page; :meth:`Style.doc` emits its one document, color x size SKUs
nested, gen#125 ruling), :class:`Policy`
and :class:`ClassRow`. The rows themselves are data, in :mod:`class_rows`.
Standard library only.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass

from colorwords import plain
from departments import check as check_departments
from variants import Color, attr, drawing, product, swatch

AUDIENCES = ("adult", "kids", "baby")
SIZE_RANGES = ("regular", "petite", "tall", "plus")
NECKLINES = ("boat", "slash", "high", "crew", "round", "collared", "square")
PATTERNS = ("plain", "check", "stripe", "print")
LEG_STYLES = ("balloon", "barrel", "straight", "wide", "slim", "tapered")
#: A record ranked this high gets the baseline's bestseller boost.
BESTSELLER_TOP = 15
RISES = ("low", "mid", "high")

# --------------------------------------------------------------------------
# Variant structure (gen#125 ruling): a style is one product and one document;
# every color x size it is sold in is a SKU nested in it (stock and price are per SKU)
# --------------------------------------------------------------------------

#: The family a marketing shade ("Washed Black") rolls up to. It stays on the swatch, where
#: the scaled build's style signature reads it (``scale.py``), and is no facet: PRISM's
#: vocabulary groups do that grouping, where a merchandiser can see it (gen#186).
COLOR_FAMILIES = ("black", "white", "grey", "blue", "navy", "brown", "cream", "green",
                   "red", "pink", "orange", "yellow", "gold", "silver", "multi")  # fmt: skip
#: Joins a category path into one keyword per ancestor (as industrial does);
#: a routed policy names its node in this form.
PATH_SEPARATOR = "/"
#: The metal finishes a ``metal`` style's colors are.
FINISHES = ("Rose Gold", "Yellow Gold", "White Gold", "Silver")
_AUTHORED_SHADE_FAMILY = {
    "Black": "black", "Washed Black": "black",
    "White": "white",
    "Charcoal": "grey", "Grey": "grey", "Heather Grey": "grey", "Grey Check": "grey",
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
    "Bright Orange": "orange", "Lemon": "yellow",
    "Rose Gold": "gold", "Yellow Gold": "gold", "White Gold": "silver", "Silver": "silver",
    "Stripe": "multi",
    "Blue": "blue", "Green": "green", "Brown": "brown", "Gold": "gold",
}  # fmt: skip
#: Keyed by the plain word ``cw`` gives a shade ("Lemon" is "Yellow"), as ``color[0]`` reads.
SHADE_FAMILY = {plain(shade): family for shade, family in _AUTHORED_SHADE_FAMILY.items()}
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
# Styles: one document per style
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
    #: (color, sold_last_5_days): the colors it is sold in; the product's
    #: popularity is their sum.
    colors: tuple[tuple[Color, int], ...]
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
    #: Food and furniture: no color facet and no swatches.
    colorless: bool = False
    #: Metal goods (jewellery, watches, lighting, tech): the color IS the
    #: metal finish, so each SKU also carries a ``finish``.
    metal: bool = False
    #: Further (key, name, value) attributes, unitless.
    extra: tuple[tuple[str, str, str], ...] = ()
    #: Letter sizes (S, M, L, XL), one SKU per color x size ...
    sizes: tuple[str, ...] = ()
    #: ... except these (color, size) pairs, which are not made.
    not_made: tuple[tuple[str, str], ...] = ()
    #: A motif print's drawing fields (motif, placement, scale, spacing), see :mod:`prints`.
    motif_print: tuple[tuple[str, object], ...] = ()
    #: The pooled review count; set only where a row must out-sell another (otherwise
    #: a digest of the code).
    reviews: int | None = None

    def __post_init__(self) -> None:
        if self.lengths and self.size_range is not None:
            raise ValueError(f"{self.code}: a legwear size_range is derived from its SKUs")
        if self.bed_frame and not set(self.bed_frame) <= set(BED_SIZE_DIMS):
            raise ValueError(f"{self.code}: a bed size outside the shared vocabulary")
        if self.metal and not {c[0] for c, _ in self.colors} <= set(FINISHES):
            raise ValueError(f"{self.code}: a metal color outside the finishes")

    def _sizes(self, color: Color) -> list[dict]:
        """The sizes ``color`` is sold in: waist x inside leg, bed sizes, letter
        sizes, or one sizeless row."""
        if self.sizes:
            return [{"size": s, "price": self.price, "in_stock": True}
                    for s in self.sizes if (color[0], s) not in self.not_made]  # fmt: skip
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
                 # About one SKU in seven is greyed out, differently per color.
                 "in_stock": leg not in self.sold_out
                 and _digest(self.code, color[0], w, leg) % 7 != 0}
                for leg in self.lengths for w in waists
            ]  # fmt: skip
        if self.bed_sized:
            step = round(self.price / 4)
            return [{"bed_size": b, "price": float(self.price + n * step), "in_stock": True}
                    for n, b in enumerate(BED_SIZES)]  # fmt: skip
        return [{"price": self.price, "in_stock": True}]

    def skus(self) -> list[dict]:
        """Every color x size the style is sold in; a colorless style's SKUs carry no color.

        A metal good's color IS its finish, so its SKUs also carry ``finish``.
        """
        out = []
        for color, _ in self.colors:
            tag = {} if self.colorless else {"color": color[0]}
            if self.metal:
                tag["finish"] = color[0].lower()
            out += [{**tag, **row} for row in self._sizes(color)]
        return out

    def size_ranges(self) -> list[str] | None:
        if self.lengths:
            return derive_size_range(self.skus())
        return None if self.size_range is None else [self.size_range]

    def drawing_params(self) -> dict:
        """The drawing's params; a produce pile's fruit count comes from the record's
        weight (:attr:`unit`) or pack count, here and nowhere else."""
        params = dict(self.params)
        if self.shape != "produce_pile":
            return params
        from kit_produce import pile_params  # deferred: the record model draws nothing else

        grams = self.unit[0] if self.unit is not None and self.unit[1] == "g" else None
        return pile_params(params["fruit"], f"PLT-{self.code}", params.get("pack", "loose"),
                           grams=grams, count=self.units_per_pack)  # fmt: skip

    def doc(self) -> dict:
        """The style's one catalog document, its SKUs nested (see :func:`variants.product`)."""
        # Pooled per style: one rating and count, one popularity over every color.
        h = _digest(self.code)
        rating, reviews = round(3.6 + (h % 14) / 10, 1), 5 + (h >> 8) % 1700
        if self.reviews is not None:
            reviews = self.reviews
        skus = self.skus()
        prices = [s["price"] for s in skus]
        lead = self.colors[0][0]
        rec = {
            "title": self.title,
            "brand": self.brand,
            "brand_owner": BRAND_OWNER[self.brand],
            "department": check_departments([self.department], self.title),
            "category_path": list(self.path),
            "category_leaf": self.path[-1],
            "description": self.description,
            "attributes": [],
            # The tile shows the lead color.
            "drawing": {
                **drawing(self.shape, lead, **self.drawing_params()),
                **dict(self.motif_print),
            },
            "collections": [],
            "currency": "GBP",
            "product_type": self.product_type,
            "audience": self.audience,
            "sold_last_5_days": sum(sold for _, sold in self.colors),
            "rating": rating,
            "review_count": reviews,
            "price_min": min(prices),
            "price_max": max(prices),
            "offer": self.was_price is not None or self.multibuy,
            "online_only": self.online_only,
            "trending": self.trending,
        }
        size_range = self.size_ranges()
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
            rec["discount_pct"] = round(100 * (self.was_price - min(prices)) / self.was_price)
        if self.units_per_pack is not None:
            # The count kind industrial uses for a package quantity (C62, one).
            rec["attributes"].append(
                attr("units_per_pack", "Units per pack", self.units_per_pack, "C62")
            )
        if self.abv is not None:
            # A plain number, the percent in its name: prism spells no percent unit.
            rec["attributes"].append(attr("abv", "ABV (%)", self.abv))
        rec["attributes"] += [attr(k, name, v) for k, name, v in self.extra]
        swatches = {} if self.colorless else {
            c[0]: swatch(c, SHADE_FAMILY[c[0]]) for c, _ in self.colors
        }
        return product(f"PLT-{self.code}", skus, swatches, **rec)


def one(color: Color, sold: int) -> tuple[tuple[Color, int], ...]:
    return ((color, sold),)


def on_sale(doc: dict) -> bool:
    return "was_price" in doc and doc["price"] < doc["was_price"]


@dataclass(frozen=True)
class Policy:
    """What the fix reads, in a shape both Python and Elasticsearch apply.

    ``filters``: (field, allowed values), every one required. ``boosts``:
    (field, values, weight) multiplied into the score; a weight below 1 buries.
    ``route``: a category node (joined with "/"); its docs are recalled even
    when the text misses them, and boosted. ``sku_filters``: (SKU field,
    values) that one in-stock nested SKU must carry. ``unless``: regular
    expressions over the lowercased query; when one matches, the policy is
    off and the query runs as the baseline (``unless_text`` says so in words).
    """

    filters: tuple[tuple[str, tuple[str, ...]], ...] = ()
    on_sale: bool = False
    boosts: tuple[tuple[str, tuple[str, ...], float], ...] = ()
    route: str | None = None
    sku_filters: tuple[tuple[str, tuple[str, ...]], ...] = ()
    unless: tuple[str, ...] = ()
    unless_text: str = ""

    def applies(self, query: str) -> bool:
        """False when ``query`` holds an :attr:`unless` pattern: the policy is then off."""
        return not any(re.search(p, query.lower()) for p in self.unless)

    def describe(self) -> str:
        out = [f"filter {f} = {' or '.join(v)}" for f, v in self.filters]
        out += ["filter on sale (price < was_price)"] if self.on_sale else []
        out += [f"filter an in-stock SKU with {f} = {' or '.join(v)}" for f, v in self.sku_filters]
        out += [f"{f} = {' or '.join(v)} x{w:g}" for f, v, w in self.boosts]
        out += [f"route to {self.route} (recalled, boosted)"] if self.route else []
        out += [f"off when the query says {self.unless_text}"] if self.unless else []
        return "; ".join(out)


@dataclass(frozen=True)
class Control:
    """A query in the OTHER sense of a row's word, which its policy must leave alone.

    The proof runs it with the policy on; its top 3 must all be ``is_intended``.
    """

    query: str
    intended: str
    is_intended: Callable[[dict], bool]


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
    #: Queries in the word's other sense: the policy must still return that sense.
    controls: tuple[Control, ...] = ()
    #: Set when a target may share the baseline top 3 (a word whose other sense also leads):
    #: the claim for the row is then that this sense is in that top 3, not that no target is.
    baseline_holds: Control | None = None


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
