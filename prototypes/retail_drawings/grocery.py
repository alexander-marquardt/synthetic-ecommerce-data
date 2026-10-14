"""The grocery catalog: Food & Drink styles whose SKUs are flavor x pack size (gen#154).

Usage::

    python3 prototypes/retail_drawings/grocery.py --skus 10000 [--seed 0] [--out DIR]

prints the build's counts as JSON, checks every document against the output standard
(:func:`synthetic_ecommerce_data.core.standard.check_catalog`) and, with ``--out``,
writes ``nested.jsonl`` and ``flat.jsonl`` into DIR.

:func:`build` plants :data:`grocery_rows.ANCHORS` first, so every demo case exists at
any size. It then draws styles per family until the family holds its share of the
target SKUs. A style is a range name, a brand, an organic flag, its flavors, its packs
and its may-contain codes. A style whose family title names the flavor carries one
flavor; any other style carries several, as a selector. Each SKU states, from its own
flavor and pack:

- ``contains`` (the allergens its ingredients name) and ``may_contain`` (factory
  traces) over the seven allergens of :data:`grocery_rows.ALLERGENS`. "Free from X" is a
  query over these two, not a fact, so there is no ``free_from``;
- ``dietary``: Vegan (no milk, no egg, no animal ingredient), Vegetarian (no meat or
  fish), Gluten Free and Nut Free (the allergen neither contained nor traced), and
  Organic (the style's flag, which its title also states);
- ``pack_size``, ``units_per_pack`` and the net weight or volume.

At product level, ``contains`` and ``may_contain`` are the union over the variants
and ``dietary`` the intersection. ``ingredients`` is the base
recipe every variant shares (the intersection, so at most 20 and possibly under 5); a
SKU carries its flavor's full 5 to 20 list. Fresh fruit and vegetables carry none. A
non-food overlap style (a cleaner, a body milk) carries a ``scent`` and none of the
food facts.

One drawing per style (``export.image_id``): a pack shape from the kit, or
:mod:`kit_grocery`'s ``bar`` and ``bag``.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import zlib
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import kit_grocery  # noqa: E402,F401 -- registers bar and bag
from departments import check as check_departments  # noqa: E402
from export import NUMERIC_FACTS, standard_document  # noqa: E402
from grocery_ingredients import (  # noqa: E402
    allergen_value,
    base_value,
    facet_value,
    ingredients,
    shared,
    unmapped,
)
from grocery_rows import (  # noqa: E402
    ALLERGENS,
    ANCHORS,
    CUT_NOTES,
    DECOY_ANCHORS,
    FAMILIES,
    LINES,
    OWNERS,
    F,
    Family,
)
from kit_produce import pile_params  # noqa: E402
from variants import attr, drawing, product  # noqa: E402

from synthetic_ecommerce_data.core import standard  # noqa: E402
from synthetic_ecommerce_data.core.emit import write_jsonl  # noqa: E402

TARGET = 10_000
ORGANIC_SHARE = 0.12
ATTEMPTS = 40
STORAGE_TEXT = {
    "ambient": "Store in a cool, dry place.",
    "chilled": "Keep refrigerated.",
    "frozen": "Keep frozen.",
}
#: A fresh fruit variety -> the kit fruit that draws it (``kit_produce.FRUIT``).
FRUIT = {"Unwaxed Lemons": "lemon", "Lemons": "lemon", "Meyer Lemons": "lemon",
         "Oranges": "orange", "Blood Oranges": "orange", "Orange Segments": "orange",
         "Easy Peelers": "clementine", "Gala Apples": "apple", "Bramley Apples": "apple",
         "Braeburn Apples": "apple", "Fuji Apples": "apple",
         "Limes": "lime", "Unwaxed Limes": "lime", "Key Limes": "lime",
         "Ripe Strawberries": "strawberry", "Large Strawberries": "strawberry",
         "Spanish Strawberries": "strawberry", "Sweet Strawberries": "strawberry",
         "Ruby Red Grapefruit": "grapefruit", "Pink Grapefruit": "grapefruit",
         "White Grapefruit": "grapefruit", "Mandarins": "mandarin",
         "Easy Peel Mandarins": "mandarin", "Baby Mandarins": "mandarin",
         "Clementines": "clementine", "Seedless Clementines": "clementine",
         "Spanish Clementines": "clementine", "Satsumas": "satsuma",
         "Seedless Satsumas": "satsuma", "Easy Peel Satsumas": "satsuma",
         "Ripe Raspberries": "raspberry", "Sweet Raspberries": "raspberry",
         "Large Raspberries": "raspberry", "Plump Blueberries": "blueberry",
         "Sweet Blueberries": "blueberry", "Large Blueberries": "blueberry",
         "Juicy Blackberries": "blackberry", "Sweet Blackberries": "blackberry",
         "Large Blackberries": "blackberry"}  # fmt: skip
#: A pack word -> how a fruit pile shows it.
PILE_PACK = {"Single": "loose", "4 pack": "net", "1kg": "bag",
             "150g": "bag", "250g": "bag", "300g": "bag", "400g": "bag", "800g": "bag"}  # fmt: skip

#: Product entries that are a union over the flavors, so a flat SKU must not inherit them.
UNIONED = frozenset({"contains", "may_contain"})
#: Entries that are an allergen warning or a pack claim: facets, but never search text.
WARNINGS = frozenset({"contains", "may_contain", "dietary"})
#: A flavor whose pack label differs from its family's: the honey jar reads Honey, not Jam.
LABELS = {("JAM", "Clear Honey"): "Honey", ("JAM", "Set Honey"): "Honey"}
#: A flavor whose pack is not its family's: butter is a foil-wrapped block, a spread a tub.
SHAPES = {
    ("BUT", "Salted Butter"): "butter_block",
    ("BUT", "Unsalted Butter"): "butter_block",
    ("BUT", "Spreadable Butter"): "lidded_tub",
    ("BUT", "Plant Spread"): "lidded_tub",
}
#: Where a title's noun phrase ends (the honesty test's rule: "Tuna in Spring Water" is tuna).
_CUT = re.compile(r",|\d| for | with | of | in | to ")
LABEL_CHARS = 14
#: Words that modify the noun after them: a label never starts on one ("Free Penne").
DANGLING = frozenset({"Free", "Low", "No", "Reduced", "Light"})
#: Phrases kept whole past :data:`LABEL_CHARS`: "Selection" alone names no product.
WHOLE = frozenset({"Chocolate Selection", "Chocolate Orange"})

_PACK = re.compile(r"^(?:(\d+) x )?([\d.]+) ?(g|kg|ml|L|pint)$")
_COUNT = re.compile(r"^(\d+) (pack|bags)$")
_UNIT = {"g": ("g", 1), "kg": ("g", 1000), "ml": ("ml", 1), "L": ("ml", 1000), "pint": ("ml", 568)}


def parse_pack(label: str) -> dict[str, Any]:
    """``"4 x 35g"`` -> units 4, 140 g net; ``"6 pack"`` -> units 6; ``"Single"`` -> 1."""
    if m := _PACK.match(label):
        units = int(m[1] or 1)
        kind, factor = _UNIT[m[3]]
        net = round(units * float(m[2]) * factor, 1)
        net = int(net) if net == int(net) else net
        key = "net_weight_g" if kind == "g" else "net_volume_ml"
        return {"pack_size": label, "units_per_pack": units, key: net}
    if m := _COUNT.match(label):
        return {"pack_size": label, "units_per_pack": int(m[1])}
    if label in ("Single", "10 inch", "12 inch"):
        return {"pack_size": label, "units_per_pack": 1}
    raise ValueError(f"unknown pack {label!r}")


def _size(pack: dict[str, Any], item_g: float = 0.0) -> float:
    """A pack's size for pricing. A count pack of a family that declares ``item_g`` counts in
    grams (items x item weight), so a "1kg" pack sits beside "Single" as about 14 limes."""
    if item_g and "net_weight_g" not in pack:
        return pack["units_per_pack"] * item_g
    return float(pack.get("net_weight_g") or pack.get("net_volume_ml") or pack["units_per_pack"])


def _price(fam: Family, pack: dict, first: dict, flavor_i: int, brand: str) -> float:
    """The family's first-pack price, scaled by pack size (economies of scale), the
    flavor's step and the brand's tier, on a 5p point ending in 9 above a pound."""
    ratio = _size(pack, fam.item_g) / _size(first, fam.item_g)
    p = fam.price * ratio**0.8 * (1 + 0.05 * (flavor_i % 3))
    p *= 0.92 if OWNERS[brand] == "own" else 1.1
    p = max(0.35, round(p * 20) / 20)
    return round(p - 0.01, 2) if p >= 1 and round(p * 100) % 10 == 0 else p


def allergens(fam: Family, flavor: F, may_codes: str) -> dict[str, list[str]]:
    """One variant's ``contains`` and ``may_contain``, in ALLERGENS order."""
    have = set(fam.base) | {c for c in flavor.codes if c.isupper()}
    may = set(may_codes) - have
    pick = lambda codes: [ALLERGENS[c] for c in ALLERGENS if c in codes]  # noqa: E731
    return {
        "contains": pick(have),
        "may_contain": pick(may),
    }


def dietary(flavor: F, facts: dict[str, list[str]], organic: bool) -> list[str]:
    """One variant's dietary labels, from its allergens and its animal flags."""
    have, traced = set(facts["contains"]), set(facts["contains"]) | set(facts["may_contain"])
    out = []
    if not {"Milk", "Egg"} & have and not {"h", "x"} & set(flavor.codes):
        out.append("Vegan")
    if "x" not in flavor.codes:
        out.append("Vegetarian")
    if "Gluten" not in traced:
        out.append("Gluten Free")
    if not {"Peanuts", "Tree Nuts"} & traced:
        out.append("Nut Free")
    if organic:
        out.append("Organic")
    return out


def _union(lists) -> list[str]:
    return list(dict.fromkeys(v for lst in lists for v in lst))


def _common(lists) -> list[str]:
    lists = list(lists)
    return [v for v in lists[0] if all(v in lst for lst in lists[1:])]


def _description(fam: Family, flavors: list[F], packs: list[dict], skus: list[dict]) -> str:
    names = [f.name for f in flavors]
    sizes = ", ".join(p["pack_size"] for p in packs)
    if not fam.food:
        noun = fam.noun or (
            "multi-surface spray that cuts through grease"
            if fam.axis == "scent" and fam.department.startswith("Cleaning")
            else "light body milk that absorbs quickly"
        )
        if fam.fits:
            return f"A {noun}, in {sizes}. {fam.fits.format(x=names[0].lower())}"
        return f"A {noun}, in {sizes}. Scented with {names[0].lower()}."
    if len(names) > 1:
        head = f"{fam.product_type} in {len(names)} flavors: {', '.join(names)}. In {sizes}."
    else:
        head = f"{names[0]}, in {sizes}."
    out = [head]
    if len(names) == 1 and (fam.code, names[0]) in CUT_NOTES:
        out.append(CUT_NOTES[fam.code, names[0]])
    out.append(STORAGE_TEXT[fam.storage])
    contains = _union(s.get("contains", []) for s in skus)
    may = [a for a in _union(s.get("may_contain", []) for s in skus) if a not in contains]
    if contains:
        out.append(f"Contains: {', '.join(contains)}.")
    if may:
        out.append(f"May contain: {', '.join(may)}.")
    if "Vegan" in _common(s.get("dietary", []) for s in skus):
        out.append("Suitable for vegans.")
    return " ".join(out)


def pack_label(title: str, head: str) -> str:
    """The word a pack carries: the title's product noun phrase after the range name, cut where
    the phrase ends, its last two words when they fit :data:`LABEL_CHARS` ("Cereal Bars", "Tikka
    Masala"). It ends in the title's product noun, never a category fragment, and never starts
    on a modifier: "Gluten Free Penne" is "Penne", "Chocolate Selection" stays whole."""
    words = _CUT.split(title.removeprefix(head).strip())[0].split()
    label = words[-1]
    if len(words) > 1 and words[-2] not in {"&", "and"} | DANGLING:
        two = f"{words[-2]} {label}"
        label = two if len(two) <= LABEL_CHARS or two in WHOLE else label
    return label


def _drawing(fam: Family, flavors: list[F], pid: str, pack: dict, title: str, head: str) -> dict:
    """One style's drawing: the first flavor's color, the title's noun, and the marks that make
    a sibling's picture differ: the range name and a band of the style's flavor colors."""
    flavor = flavors[0]
    color = (flavor.name, "solid", flavor.hex, "#ffffff")
    marks = {"line": head, "chips": ",".join(f.hex for f in flavors)}
    shape = SHAPES.get((fam.code, flavor.name), fam.shape)
    if fam.shape == "produce_pile":
        grams = pack.get("net_weight_g")
        count = None if grams else pack["units_per_pack"]
        params = pile_params(FRUIT[flavor.name], pid, PILE_PACK[pack["pack_size"]], grams, count)
        return drawing(shape, color, pack_label(title, head), **params)
    label = LABELS.get((fam.code, flavor.name)) or pack_label(title, head)
    return drawing(shape, color, label, **marks)


def _abv_text(pid: str, flavor: F) -> str:
    """A beer's strength as a title suffix (" 4.8%") for about half the styles, else "".
    It trails the noun: :func:`pack_label` cuts a label at the first digit. Real titles are
    inconsistent here (some state it, some leave it to the can), so the choice is the id's."""
    if flavor.abv is None or zlib.crc32(f"abv:{pid}".encode()) % 2:
        return ""
    return f" {flavor.abv:g}%"


def style(fam: Family, pid: str, line: str, brand: str, flavors: list[F], packs: list[str],
          may_codes: str, organic: bool, grade: str) -> dict:  # fmt: skip
    """One style's record (the retail build's shape, for :func:`export.standard_document`)."""
    check_departments([fam.department], pid)
    parsed = [parse_pack(p) for p in packs]
    first = parse_pack(fam.packs[0])
    skus = []
    for flavor in flavors:
        fi = fam.flavors.index(flavor)
        food: dict[str, list[str]] = {}
        if fam.food:
            facts = allergens(fam, flavor, may_codes)
            food = {**facts, "dietary": dietary(flavor, facts, organic)}
        for pack in parsed:
            sku = {fam.axis: flavor.name, **pack, **{k: v for k, v in food.items() if v}}
            if listed := ingredients(fam.code, flavor.name, pid) if fam.food else None:
                sku["ingredients"] = listed
            skus.append(sku | {"price": _price(fam, pack, first, fi, brand), "in_stock": True})
    head = f"{line} Organic" if organic else line
    title = fam.title.format(line=head, flavor=flavors[0].name, abv=_abv_text(pid, flavors[0]))
    attrs = [attr(fam.axis, fam.axis_name or fam.axis.capitalize(), f.name) for f in flavors]
    attrs += [attr("pack_size", "Pack size", p) for p in packs]
    if flavors[0].abv is not None:  # a beer's strength: always an attribute, in some titles
        attrs.append(attr("abv", "ABV (%)", flavors[0].abv))
    for key, name, value in dict.fromkeys(x for f in flavors for x in f.extras):
        attrs.append(attr(key, name, value))  # a wine's grape and country, a fruit's origin
    if fam.food:
        contains = _union(s.get("contains", []) for s in skus)
        may = [a for a in _union(s.get("may_contain", []) for s in skus) if a not in contains]
        attrs += [attr("contains", "Contains", a) for a in contains]
        attrs += [attr("may_contain", "May contain", a) for a in may]
        attrs += [
            attr("dietary", "Dietary", d) for d in _common(s.get("dietary", []) for s in skus)
        ]
        attrs += [
            attr("storage", "Storage", fam.storage),
            attr("nutrition_grade", "Nutrition grade", f"Grade {grade}"),
        ]
    base = shared([s["ingredients"] for s in skus]) if "ingredients" in skus[0] else None
    extra = {"ingredients": base} if base is not None else {}
    h = zlib.crc32(pid.encode())
    prices = [s["price"] for s in skus]
    return product(
        pid, skus, {},
        title=title, brand=brand, brand_owner=OWNERS[brand], department=[fam.department],
        product_type=fam.product_type, category_path=list(fam.path), category_leaf=fam.path[-1],
        description=_description(fam, flavors, parsed, skus), attributes=attrs,
        drawing=_drawing(fam, flavors, pid, parsed[0], title, head), collections=[], currency="GBP",
        audience="baby" if fam.code == "BAB" else "adult",
        sold_last_5_days=5 + h % 90, rating=round(3.8 + (h >> 8) % 11 / 10, 1),
        review_count=3 + (h >> 16) % 400, price_min=min(prices), price_max=max(prices), **extra,
    )  # fmt: skip


def _single(fam: Family) -> bool:
    return "{flavor}" in fam.title


def _weighted(rng: random.Random, options: tuple[tuple[int, str], ...]) -> str:
    return rng.choices([o for _, o in options], [w for w, _ in options])[0]


def build(skus: int = TARGET, seed: int = 0) -> list[dict]:
    """The grocery records: the anchors, then each family's share of ``skus``."""
    rng = random.Random(f"grocery:{seed}")
    fams = {f.code: f for f in FAMILIES}
    # A depth family is sized against the core families' weight and drawn from its own stream,
    # so adding one never moves a core family's budget, ids or draws (gen#154).
    total = sum(f.weight for f in FAMILIES if not f.depth)
    budget = {f.code: max(1, round(skus * f.weight / total)) for f in FAMILIES}
    held: Counter[str] = Counter()
    titles: set[str] = set()
    recs: list[dict] = []

    def add(fam: Family, line: str, brand: str, flavors: list[F], packs: list[str], may: str,
            organic: bool) -> bool:  # fmt: skip
        grade = rng.choice(fam.grades) if fam.grades else ""
        rec = style(fam, f"GRC-{fam.code}-{held[fam.code + '#'] + 1:04d}", line, brand, flavors,
                    packs, may, organic, grade)  # fmt: skip
        # A depth family's twin is the same title bar the strength suffix: one drawing, two ids.
        key = re.sub(r" [\d.]+%$", "", rec["title"]) if fam.depth else rec["title"]
        if key in titles:
            return False
        titles.add(key)
        held[fam.code + "#"] += 1
        held[fam.code] += rec["sku_count"]
        recs.append(rec)
        return True

    for n, (code, names, may) in enumerate(ANCHORS):
        fam = fams[code]
        flavors = [next(f for f in fam.flavors if f.name == name) for name in names]
        packs = list(fam.packs)
        add(fam, LINES[n % len(LINES)], fam.brands[n % len(fam.brands)], flavors, packs, may, False)

    # The text-match decoys (gen#294) draw from a stream of their own, so no other draw moves.
    core_rng, rng = rng, random.Random(f"grocery-decoys:{seed}")
    for code, names, may, offset in DECOY_ANCHORS:
        if code not in fams:  # a build without this (depth) family plants no decoy for it
            continue
        fam = fams[code]
        flavors = [next(f for f in fam.flavors if f.name == name) for name in names]
        add(fam, LINES[offset % len(LINES)], fam.brands[offset % len(fam.brands)],
            flavors, list(fam.packs), may, False)
    rng = core_rng
    depth_rng = random.Random(f"grocery-depth:{seed}")
    for fam in sorted(FAMILIES, key=lambda f: f.depth):
        misses = 0
        if fam.depth:
            rng = depth_rng
        while held[fam.code] < budget[fam.code] and misses < ATTEMPTS:
            if _single(fam):
                flavors = [rng.choice(fam.flavors)]
                packs = list(fam.packs)
            else:
                lo, hi = fam.per_style
                flavors = rng.sample(fam.flavors, rng.randint(lo, hi))
                flavors.sort(key=fam.flavors.index)
                packs = list(fam.packs)
            organic = fam.food and rng.random() < ORGANIC_SHARE
            ok = add(fam, rng.choice(LINES), rng.choice(fam.brands), flavors, packs,
                     _weighted(rng, fam.may), organic)  # fmt: skip
            misses = 0 if ok else misses + 1
    return recs


def documents(recs: list[dict]) -> list[dict[str, Any]]:
    """The records as the standard's nested documents."""
    return [standard_document(r) for r in recs]


def flat(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One flat document per SKU (:func:`synthetic_ecommerce_data.core.standard.flat_documents`).

    The standard fills a key a variant does not state from its product's entries. For
    ``contains`` and ``may_contain`` the product states the UNION over its flavors, so a
    SKU with none of its own would inherit another flavor's (Fruit Gums "Contains: Milk"
    though the Toffee in the style has milk). Each SKU is flattened with the product's
    entries for those two keys left out when it states none.

    The four food facts are facets, because only a facet can be a hard filter:
    ``facets.ingredients`` (the SKU's label list as ``facet_value`` forms; the
    top-level ``ingredients`` keeps the label text), ``facets.ingredient_base`` (the
    base ingredient of each of those, from the committed table
    ``grocery_ingredients.BASE``, gen#295), ``facets.contains``,
    ``facets.may_contain`` and ``facets.dietary``, each a keyword list.
    ``contains``, ``may_contain`` and ``dietary`` are warnings and claims, not description
    (:data:`WARNINGS`): they stay out of ``text``, so a "peanut"
    query cannot match a product through its allergen warning. ``contains`` and
    ``may_contain`` also leave the flat ``attributes`` and ``attribute_names`` (a
    searchable surface); they live in their facets only. ``dietary`` stays in both.
    """
    out = []
    for doc in docs:
        for variant in doc["variants"]:
            own = {e["key"] for e in variant["attributes"]}
            kept = [e for e in doc["attributes"] if e["key"] not in UNIONED - own]
            one = doc | {"attributes": kept, "variants": [variant]}
            for row in standard.flat_documents(one, NUMERIC_FACTS, text_skip=WARNINGS):
                # An allergen warning is a facet only: the attributes are a searchable
                # surface in the industrial field map, so it must not stay in them.
                row["attributes"] = [e for e in row["attributes"] if e["key"] not in UNIONED]
                row["attribute_names"] = sorted({e["name"] for e in row["attributes"]})
                if row.get("ingredients"):
                    row["facets"]["ingredients"] = list(
                        dict.fromkeys(facet_value(i) for i in row["ingredients"])
                    )
                    row["facets"]["ingredient_base"] = list(
                        dict.fromkeys(base_value(v) for v in row["facets"]["ingredients"])
                    )
                for key in UNIONED:
                    if key in row["facets"]:
                        row["facets"][key] = [allergen_value(v) for v in row["facets"][key]]
                out.append(row)
    return out


def report(recs: list[dict]) -> dict[str, Any]:
    """Styles, SKUs and images, overall and per group (the path's second level)."""
    groups: Counter[str] = Counter()
    styles: Counter[str] = Counter()
    for r in recs:
        groups[r["category_path"][1]] += r["sku_count"]
        styles[r["category_path"][1]] += 1
    images = {v["image_id"] for d in documents(recs) for v in d["variants"]}
    return {
        "styles": len(recs),
        "skus": sum(r["sku_count"] for r in recs),
        "images": len(images),
        "leaves": len({tuple(r["category_path"]) for r in recs}),
        "skus_per_group": dict(groups.most_common()),
        "styles_per_group": dict(styles.most_common()),
    }


def coverage_report(recs: list[dict]) -> dict[str, Any]:
    """The share of the food rows (one per SKU) with ``facets.contains`` filled (gen#296)."""
    return {}


def ingredient_report(recs: list[dict]) -> dict[str, Any]:
    """The distinct label values and base ingredients of ``recs`` (gen#295), and the label
    values the base table has no row for: the build prints them, it never guesses a base."""
    rows = flat(documents(recs))
    labels = {v for r in rows for v in r["facets"].get("ingredients", ())}
    bases = {v for r in rows for v in r["facets"].get("ingredient_base", ())}
    return {
        "ingredients_distinct": len(labels),
        "ingredient_base_distinct": len(bases),
        "ingredients_unmapped": unmapped(labels),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skus", type=int, default=TARGET)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    recs = build(args.skus, args.seed)
    docs = documents(recs)
    problems = standard.check_catalog(docs)
    print(json.dumps({**report(recs), **ingredient_report(recs),
                      "standard_problems": len(problems)}, indent=1))
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        write_jsonl(iter(docs), args.out / "nested.jsonl")
        write_jsonl(iter(flat(docs)), args.out / "flat.jsonl")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
