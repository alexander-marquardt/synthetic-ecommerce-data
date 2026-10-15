"""Text-match decoys on every clothing, footwear and lingerie type (gen#311).

gen#294's rule (:mod:`decoy_rows`): a decoy's words mislead a plain text search and its structured
fields tell the truth, so the color, category and audience policies, which read the fields, are
right. :mod:`decoy_rows` plants them for the demo queries; this module plants them on EVERY type
of the Womens, Mens and Kids clothing, footwear and lingerie, generated from the plan below
(:data:`TYPES`), never written row by row.

A decoy is a clone of one real style of its type (the exemplar: its category leaf, sizes,
attributes and drawing), in one main color, with a new title, description and, for class 7, brand.
The classes (the numbers follow the issue):

1. **part**: the color word names a strap, a sole, a stripe ("White Bra, Red Straps").
2. **type**: another category's noun as a modifier ("Navy Jumper Dress", "Cream Trouser Socks").
3. **audience**: an audience word of a sibling version ("Black Mens-Style Jeans", a women's style).
4. **absent**: a material or feature named but absent ("Black Leather-Look Jacket").
5. **shade**: the shade is spelled in the description only ("Moonbeam Dress", "in soft ivory").
6. **incidental**: a range name holds a color or a category word ("Red Harbour Jumper", ivory).
7. **brand**: an invented brand holds a color or a category word ("Red Plover Bra", blue).

Every type gets :attr:`Spec.per_class` decoys per class (three, more for Bra and Jeans, which
are large, so a type holds at least a tenth of its size), one more of class 6 on a category word,
and at most eight of class 7 (one per brand). Titles of classes 6 and 7 are five words or fewer, so
the word sits where the text score weights it most. A type missing from the catalog, or one the
catalog gains, reds ``tests/test_retail_apparel_decoys_311.py`` until it is planned or exempt.
Names are invented. :data:`IDS` is what :mod:`scale` leaves out of its derivation and
:mod:`main_colors` out of its color completion.
"""

from __future__ import annotations

import copy
import random
import re
import zlib
from dataclasses import dataclass

from audience import audience_of_path
from class_model import SHADE_FAMILY
from decoy_rows import COLORS
from variants import cw, product, swatch

ROOTS = ("Womens", "Mens", "Kids")
DEPARTMENTS = ("Clothing", "Footwear", "Lingerie & Nightwear")
BRANDS = (("Red Plover", "red"), ("Blue Otter", "blue"), ("Green Stoat", "green"),
          ("Yellow Wagtail", "yellow"), ("Black Lapwing", "black"), ("White Dormouse", "white"),
          ("Jumper Jay", "jumper"), ("Coat Crake", "coat"))  # fmt: skip
#: The main colors a decoy is sold in, with the swatch hex of :mod:`decoy_rows`.
PRODUCT_COLORS = ("Black", "White", "Navy", "Cream", "Grey", "Brown", "Pink", "Red", "Blue",
                  "Green")  # fmt: skip
MAIN_WORDS = ("red", "blue", "green", "yellow", "black", "white")
CLASSES = {
    1: "color names a part", 2: "another category's noun as a modifier",
    3: "audience word of a sibling version", 4: "material or feature named but absent",
    5: "shade spelled in the description only", 6: "incidental word in a range name",
    7: "invented brand holding a color or category word",
}
POLICY = {4: "special: material claim"}


@dataclass(frozen=True)
class Spec:
    """A planned type: its ``product_type``, its word family (a: garment, b: bra, u: underwear,
    s: shoe, k: sock) and its decoys per class."""

    product_type: str
    family: str = "a"
    per_class: int = 3

    @property
    def classes(self) -> dict[int, int]:
        n = self.per_class
        return {1: n, 2: n, 3: n, 4: n, 5: n, 6: n + 1, 7: min(n, len(BRANDS))}


def _plan(family: str, *names: str) -> tuple[Spec, ...]:
    return tuple(Spec(n, family) for n in names)


TYPES: tuple[Spec, ...] = (
    *_plan("a", "Blouse", "Bodysuit", "Bomber Jacket", "Cardigan", "Coat", "Co-ord Set",
           "Cycling Shorts", "Denim Jacket", "Dress", "Joggers", "Jumper", "Leggings",
           "Outfit Set", "Puffer Jacket", "Shirt", "Shorts", "Skirt", "Suit Jacket", "Sweatshirt",
           "T-Shirt", "Tea Dress", "Tee", "Top", "Tracksuit", "Trousers"),
    Spec("Jeans", "a", 12),
    *_plan("k", "Socks", "Boot Socks"),
    *_plan("s", "Ankle Boots", "Ballet Pumps", "Block Heels", "Brogues", "Chelsea Boots",
           "Chukka Boots", "Court Shoes", "Kitten Heels", "Knee High Boots", "Loafers",
           "Running Shoes", "Safety Boots", "Sandals", "School Shoes", "Slippers", "Trainers",
           "Walking Boots", "Wellies"),
    Spec("Bra", "b", 9),
    *_plan("u", "Boxers", "Dressing Gown", "Knickers", "Pyjama Shorts", "Pyjamas", "Shapewear",
           "Slip", "Tights", "Vest"),
)  # fmt: skip
#: Types of the three departments that carry no decoys, each with its reason.
EXEMPT = {
    "Belt": "an accessory, not a garment: its text words are those of the accessories batch",
    "Bracelet": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Earrings": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Necklace": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Ring": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Watch": "a watch: the color is the metal finish, not a printed or dyed color",
    "Shoe Care Kit": "a care product sold in the footwear department, not footwear",
}


def _code(ti: int, cls: int, i: int) -> str:
    return f"A{ti:02d}{cls}{i:02d}"


IDS = frozenset(
    f"PLT-D{_code(ti, cls, i)}"
    for ti, s in enumerate(TYPES) for cls, n in s.classes.items() for i in range(n)
)  # fmt: skip

# -- the words ------------------------------------------------------------------------------------
PARTS = {"a": ("Stripes", "Piping", "Buttons", "Collar", "Cuffs", "Lining", "Pocket", "Stitching",
               "Trim", "Zip"),
         "b": ("Straps", "Bow", "Stitching", "Trim", "Hooks", "Lining"),
         "u": ("Waistband", "Bow", "Stitching", "Trim", "Piping", "Cuffs"),
         "s": ("Sole", "Eyelets", "Heel", "Lining", "Stitching", "Trim"),
         "k": ("Stripes", "Heel", "Toe", "Cuff", "Trim", "Stitching")}  # fmt: skip
MODS = {"a": ("Shirt", "Jumper", "Jacket", "Coat", "Dress", "Skirt", "Blazer", "Cardigan",
              "Trouser", "Vest", "Hoodie", "Gilet", "Tunic", "Poncho"),
        "b": ("Dress", "Vest", "Shirt", "Top", "Jumper", "Slip", "Bodysuit", "Cami", "Skirt"),
        "u": ("Dress", "Shirt", "Skirt", "Short", "Vest", "Top", "Trouser", "Bra", "Cami"),
        "s": ("Boot", "Sock", "Slipper", "Sandal", "Trainer", "Loafer", "Sneaker", "Pump",
              "Shoe", "Heel", "Mule"),
        "k": ("Boot", "Trouser", "Shoe", "Trainer", "Slipper", "Loafer", "Sandal", "Sneaker")}  # noqa: E501
AUDIENCE = {"Womens": (("Mens-Style", "mens"), ("Mens Fit", "mens"), ("Boys Fit", "boys")),
            "Mens": (("Womens-Style", "womens"), ("Womens Fit", "womens"), ("Girls Fit", "girls")),
            "Kids": (("Mini-Me Mens", "mens"), ("Mini-Me Womens", "womens"),
                     ("Mens-Style", "mens"))}  # fmt: skip
ABSENT = (("Leather-Look", "leather", "A finish made to look like leather; it holds no leather."),
          ("Suede-Look", "suede", "A soft finish that resembles suede; no suede is used."),
          ("Cashmere-Feel", "cashmere", "Soft to the touch like cashmere; it holds no cashmere."),
          ("Wool-Free", "wool", "Made without wool."),
          ("Silk-Feel", "silk", "A smooth finish that feels like silk; no silk is used."),
          ("Linen-Look", "linen", "Woven to look like linen; it holds no linen."),
          ("Lace-Free", "lace", "Made without lace."),
          ("Velvet-Feel", "velvet", "A plush finish that feels like velvet; no velvet is used."),
          ("Denim-Look", "denim", "Printed to look like denim; it holds no denim."),
          ("Satin-Look", "satin", "A sheen that resembles satin; no satin is used."),
          ("Mohair-Free", "mohair", "Made without mohair."),
          ("Tweed-Look", "tweed", "A weave that resembles tweed; it holds no tweed."),
          ("Fleece-Free", "fleece", "Made without fleece."),
          ("Corduroy-Look", "corduroy", "Ribbed to look like corduroy; it holds no corduroy."),
          ("Mesh-Free", "mesh", "Made without mesh."), ("Silk-Free", "silk", "Made without silk."),
          ("Canvas-Look", "canvas", "A weave that resembles canvas; it holds no canvas."),
          ("Rubber-Free", "rubber", "Made without rubber."))  # fmt: skip
SHADES = (("Moonbeam", "Ivory", "#f6f1e1", "cream"), ("Driftwood", "Taupe", "#8b7d6b", "brown"),
          ("Dune", "Beige", "#d9c6a5", "cream"), ("Ember", "Burgundy", "#6d1a2e", "red"),
          ("Lagoon", "Teal", "#2a7f80", "blue"), ("Willow", "Olive", "#7a7a3c", "green"),
          ("Pebble", "Ecru", "#e6dcc4", "cream"), ("Meadow", "Mint", "#a9d6b5", "green"),
          ("Harvest", "Rust", "#b5522b", "orange"), ("Seashell", "Coral", "#f26b5a", "orange"),
          ("Biscuit", "Champagne", "#f1e0c0", "cream"), ("Hearth", "Khaki", "#b5a57a", "green"),
          ("Cobble", "Camel", "#c19a6b", "brown"), ("Silt", "Stone", "#cfc6b8", "cream"),
          ("Tallow", "Oatmeal", "#d8cdb4", "cream"), ("Quill", "Aubergine", "#4b2a45", "brown"))  # fmt: skip  # noqa: E501
RANGES = {  # color word -> (range name, what it is named for)
    "red": (("Red Harbour", "a small fishing harbour"), ("Red Fern", "a fern of the hills")),
    "blue": (("Blue Meadow", "a meadow of cornflowers"), ("Blue Cove", "a sheltered cove")),
    "green": (("Green Park", "a city park"), ("Green Hollow", "a wooded hollow")),
    "yellow": (("Yellow Brook", "a brook lined with buttercups"),
               ("Yellow Marsh", "a salt marsh")),
    "black": (("Black Mill", "a disused mill"), ("Black Tor", "a granite tor")),
    "white": (("White Cliff", "a chalk cliff"), ("White Moor", "an upland moor")),
}  # fmt: skip
CATEGORY_RANGES = (("Jumper Lane", "a village lane"), ("Coat Hook", "a headland"),
                   ("Shirt Row", "a terrace of cottages"), ("Dress Circle", "a theatre tier"),
                   ("Boot Hill", "a wooded hill"), ("Skirt Point", "a rocky point"),
                   ("Jacket Quay", "a harbour quay"), ("Sock Hop", "a village dance"))  # fmt: skip


@dataclass(frozen=True)
class Row:
    """One planted decoy: its class, the misleading ``word``, the ``query`` it targets and its
    ``policy`` (``generic`` or ``special: <name>``); ``doc`` is the catalog document."""

    pid: str
    product_type: str
    cls: int
    word: str
    query: str
    policy: str
    doc: dict

    @property
    def title(self) -> str:
        return self.doc["title"]


def field_text(doc: dict) -> str:
    """Every attribute value, SKU text field and the category leaf, lowercased: what the
    structured fields say, so a misleading word is one this does not hold."""
    vals = [str(a["value"]) for a in doc["attributes"]] + [doc["product_type"]]
    vals += [str(v) for s in doc["skus"] for k, v in s.items()
             if isinstance(v, str) and not k.startswith("size") and k not in ("sku", "color")]
    return " ".join(vals).lower()


def _in_path(word: str, doc: dict) -> bool:
    path = " ".join(doc["category_path"]) + " " + doc["product_type"]
    return re.search(rf"\b{re.escape(word)}s?\b", path.lower()) is not None


def _clone(ex: dict, code: str, title: str, desc: str, color: str, hexv: str, family: str,
           brand: str | None = None) -> dict:
    """``ex`` re-run through :func:`variants.product` in one color with a new title, description
    and (class 7) brand; its popularity is above the typical so the text score competes."""
    from class_model import BRAND_OWNER

    keep = {k: v for k, v in copy.deepcopy(ex).items()
            if k not in ("product_id", "price", "sku_count", "skus", "color_options",
                         "size_options", "was_price", "discount_pct", "pattern",
                         "sub_collection", "product_line")}  # fmt: skip
    first = ex["skus"][0]["color"]
    color_tuple = cw(color, hexv)
    skus = [{**{k: v for k, v in s.items() if k != "sku"}, "color": color_tuple[0]}
            for s in ex["skus"] if s["color"] == first]  # fmt: skip
    if not any(s["in_stock"] for s in skus):
        skus[0]["in_stock"] = True
    sold = 500 + zlib.crc32(code.encode()) % 400
    prices = [s["price"] for s in skus]
    keep["attributes"] = [a for a in keep["attributes"]
                          if a["key"] not in ("line", "pattern", "print", "color", "motif",
                                               "motif_count", "print_placement")]  # fmt: skip
    keep |= {"title": title, "description": desc, "sold_last_5_days": sold,
             "review_count": 900 + sold, "offer": False, "trending": False,
             "price_min": min(prices), "price_max": max(prices)}  # fmt: skip
    if brand is not None:
        keep |= {"brand": brand, "brand_owner": BRAND_OWNER[brand]}
    keep["drawing"] = {k: v for k, v in keep["drawing"].items() if k != "accents"} | {
        "pattern": "solid", "base": hexv, "accent": "#333333",
        "motif": None, "placement": None}  # fmt: skip
    return product(f"PLT-D{code}", skus, {color_tuple[0]: swatch(color_tuple, family)}, **keep)


def _options(cls: int, spec: Spec, ex: dict) -> list[dict]:
    """Every decoy of class ``cls`` this exemplar can carry: title, description, word, query,
    color. Any option whose word the exemplar's own fields hold is left out."""
    fam, noun = spec.family, spec.product_type
    n = noun.lower()
    path_has = lambda w: _in_path(w, ex)  # noqa: E731
    out = []
    if cls == 1:
        for part in PARTS[fam]:
            for sec in MAIN_WORDS:
                for c in PRODUCT_COLORS:
                    if c.lower() != sec:
                        out.append(dict(title=f"{c} {noun}, {sec.title()} {part}", word=sec,
                                        desc=f"{c} {n} with {sec} {part.lower()}.", color=c,
                                        query=f"{sec} {n}"))
    elif cls == 2:
        for mod in (m for m in MODS[fam] if not path_has(m.lower())):
            for c in PRODUCT_COLORS:
                out.append(dict(title=f"{c} {mod} {noun}", word=mod.lower(), color=c,
                                desc=f"{c} {n} with {mod.lower()}-style detailing. Not a "
                                     f"{mod.lower()}.", query=mod.lower()))
    elif cls == 3:
        # The text names the real audience too, as every #294 decoy does: the output standard
        # refuses a text naming only another audience.
        # A style with no audience attribute gets the one export derives from its path.
        aud = next((a["value"] for a in ex["attributes"] if a["key"] == "audience"),
                   None) or audience_of_path(ex["category_path"])
        for phrase, word in AUDIENCE[ex["category_path"][0]]:
            for c in PRODUCT_COLORS:
                out.append(dict(title=f"{c} {aud} {noun}, {phrase}", word=word, color=c,
                                desc=f"{c} {aud.lower()} {n}, cut in a {phrase.lower()} fit.",
                                query=f"{word} {n}"))
    elif cls == 4:
        held = field_text(ex)
        for phrase, word, sentence in ABSENT:
            if word not in held:
                real = [str(a["value"]) for a in ex["attributes"]
                        if a["key"].endswith("material") and re.search(r"[A-Za-z]", str(a["value"]))]
                tail = f", {real[0].title()}" if real else ""  # the text names its real material too
                more = f" Material: {', '.join(real)}." if real else ""
                for c in PRODUCT_COLORS:
                    out.append(dict(title=f"{c} {phrase} {noun}{tail}", word=word, color=c,
                                    desc=f"{c} {n}. {sentence}{more}", query=f"{word} {n}"))
    elif cls == 5:
        for fancy, shade, hexv, family in SHADES:
            out.append(dict(title=f"{fancy} {noun}", word=shade.lower(), color=shade, hex=hexv,
                            family=family, desc=f"{fancy} {n} in soft {shade.lower()}.",
                            query=f"{shade.lower()} {n}"))
    elif cls == 6:
        for word, ranges in RANGES.items():
            for name, gloss in ranges:
                for c in PRODUCT_COLORS:
                    if c.lower() != word:
                        out.append(dict(title=f"{name} {noun}", word=word, color=c,
                                        desc=f"{c} {n} from the {name} range, named for {gloss}.",
                                        query=f"{word} {n}", kind="color"))
        for name, gloss in CATEGORY_RANGES:
            if not path_has(name.split()[0].lower()):
                for c in PRODUCT_COLORS:
                    out.append(dict(title=f"{name} {noun}", word=name.split()[0].lower(),
                                    color=c, query=name.split()[0].lower(), kind="category",
                                    desc=f"{c} {n} from the {name} range, named for {gloss}."))
    else:
        for brand, word in BRANDS:
            if word in MAIN_WORDS or not path_has(word):
                for c in PRODUCT_COLORS:
                    if c.lower() != word:
                        out.append(dict(title=f"{brand} {noun}", word=word, color=c, brand=brand,
                                        desc=f"{c} {n} by {brand}.", query=f"{word} {n}"))
    return out


def _wanted(cls: int, i: int, n: int, kind: str | None) -> bool:
    """Class 6: the last row of a type is the category-word one, the others a color word."""
    return cls != 6 or (kind == "category") == (i == n - 1)


def build(body: list[dict]) -> list[Row]:
    """Every decoy row for ``body`` (the templates without the decoys), in plan order."""
    pool: dict[str, list[dict]] = {}
    for d in sorted(body, key=lambda r: r["product_id"]):
        if (d["category_path"][0] in ROOTS and d["department"][0] in DEPARTMENTS
                and d.get("color_options") and d["product_id"] not in IDS
                and not (d["product_type"] == "Jeans" and d.get("leg_style"))):
            pool.setdefault(d["product_type"], []).append(d)
    rows = []
    for ti, spec in enumerate(TYPES):
        exemplars = pool[spec.product_type]
        used: set[tuple[str, str]] = set()
        words: set[tuple[int, str]] = set()
        step = 0
        for cls, n in spec.classes.items():
            rnd = random.Random(f"311-{spec.product_type}-{cls}")
            for i in range(n):
                ex = exemplars[step % len(exemplars)]
                step += 1
                opts = [o for o in _options(cls, spec, ex) if _wanted(cls, i, n, o.get("kind"))
                        and (o["title"], ex["category_path"][0]) not in used
                        and (cls not in (4, 5) or (cls, o["word"]) not in words)]  # fmt: skip
                if not opts:
                    raise ValueError(f"{spec.product_type} class {cls}: no option left")
                if cls in (4, 5):  # the common words first: leather, suede, cashmere; ivory
                    first = opts[0]["word"]
                    opts = [o for o in opts if o["word"] == first]
                o = rnd.choice(opts)
                words.add((cls, o["word"]))
                used.add((o["title"], ex["category_path"][0]))
                code = _code(ti, cls, i)
                color = o["color"]
                hexv = o.get("hex") or COLORS[color]
                family = o.get("family") or SHADE_FAMILY.get(color, color.lower())
                title = o["title"]
                fit = next((a["value"] for a in ex["attributes"] if a["key"] == "leg_fit"), None)
                if fit and fit.lower() not in title.lower() and spec.product_type in title:
                    title = title.replace(spec.product_type, f"{fit} {spec.product_type}", 1)
                if cls in (6, 7) and color.lower() not in title.lower():
                    # The output standard refuses a title naming only another color's word;
                    # naming the real color too is how every #294 decoy passes it.
                    title = f"{title}, {color}"
                doc = _clone(ex, code, title, o["desc"], color, hexv, family, o.get("brand"))
                rows.append(Row(f"PLT-D{code}", spec.product_type, cls, o["word"], o["query"],
                                POLICY.get(cls, "generic"), doc))
    return rows


def docs(body: list[dict]) -> list[dict]:
    """Every row's catalog document, in plan order."""
    return [r.doc for r in build(body)]


def table_markdown(rows: list[Row]) -> str:
    """The docs table: one line per row, generated, never kept by hand."""
    lines = ["| Product id | Type | Class | Title | Word | Query | Policy |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r.pid} | {r.product_type} | {r.cls} {CLASSES[r.cls]} | {r.title} | "
                     f"{r.word} | {r.query} | {r.policy} |")
    return "\n".join(lines)


DOC = "docs/retail-apparel-decoys.md"
DOC_HEAD = """# Text-match decoys on every clothing, footwear and lingerie type (gen#311)

`prototypes/retail_drawings/decoy_apparel.py` plants, on every product type of the Womens, Mens and
Kids clothing, footwear and lingerie, products whose words mislead a plain text search while their
structured fields tell the truth (gen#294's rule; `decoy_rows.py` holds the demo-query rows). A
decoy is a clone of one real style of its type in one main color. The color, category and audience
policies read the fields and drop it. The classes: 1 a color word names a trim or strap; 2 another
category's noun is a modifier; 3 an audience word of a sibling version; 4 a material or feature
named but absent; 5 the shade is in the description only; 6 a short range name holds a color word
(or a category word); 7 an invented brand holds a color or category word.

Each type holds at least three decoys per class (nine and twelve for bras and jeans, so a type
holds a tenth of its size), one more of class 6 on a category word, and one class 7 decoy per brand.
Classes 6 and 7 have titles of five words or fewer. The Policy column is `generic` where the
color, category or audience policy separates the decoy, and `special: <name>` where it needs its own
(a material claim: no field says the product is not leather). The exempt types are in
`decoy_apparel.EXEMPT`. The table is generated
(`python3 prototypes/retail_drawings/decoy_apparel.py`) and
`tests/test_retail_apparel_decoys_311.py` holds it verbatim.

"""


def render_doc(rows: list[Row]) -> str:
    return DOC_HEAD + table_markdown(rows) + "\n"


if __name__ == "__main__":
    import pathlib

    import scale

    root = pathlib.Path(__file__).resolve().parents[2]
    base = [d for d in scale.templates(baseline=False) if d["product_id"] not in IDS]
    (root / DOC).write_text(render_doc(build(base)), "utf-8")
