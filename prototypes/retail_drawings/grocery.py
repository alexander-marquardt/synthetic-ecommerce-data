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

- ``contains``, ``may_contain`` and ``free_from`` over the six allergens of
  :data:`grocery_rows.ALLERGENS`. ``free_from`` holds an allergen only when it is in
  neither of the other two;
- ``dietary``: Vegan (no milk, no egg, no animal ingredient), Vegetarian (no meat or
  fish), Gluten Free and Nut Free (the allergen neither contained nor traced), and
  Organic (the style's flag, which its title also states);
- ``pack_size``, ``units_per_pack`` and the net weight or volume.

At product level, ``contains`` and ``may_contain`` are the union over the variants,
and ``free_from`` and ``dietary`` the intersection. A product that is "free from
peanuts" is therefore free from them in every variant. A non-food overlap style (a
cleaner, a body milk) carries a ``scent`` and none of the food facts.

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
from grocery_ingredients import ingredients, union  # noqa: E402
from grocery_rows import ALLERGENS, ANCHORS, FAMILIES, LINES, OWNERS, F, Family  # noqa: E402
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
FRUIT = {"Unwaxed Lemons": "lemon", "Oranges": "orange", "Easy Peelers": "clementine",
         "Gala Apples": "apple", "Bramley Apples": "apple"}  # fmt: skip
#: A pack word -> how a fruit pile shows it.
PILE_PACK = {"Single": "loose", "4 pack": "net", "1kg": "bag"}

#: Product entries that are a union over the flavors, so a flat SKU must not inherit them.
UNIONED = frozenset({"contains", "may_contain"})
#: A flavor whose pack label differs from its family's: the honey jar reads Honey, not Jam.
LABELS = {("JAM", "Clear Honey"): "Honey", ("JAM", "Set Honey"): "Honey"}

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


def _size(pack: dict[str, Any]) -> float:
    return float(pack.get("net_weight_g") or pack.get("net_volume_ml") or pack["units_per_pack"])


def _price(fam: Family, pack: dict, first: dict, flavor_i: int, brand: str) -> float:
    """The family's first-pack price, scaled by pack size (economies of scale), the
    flavor's step and the brand's tier, on a 5p point ending in 9 above a pound."""
    p = fam.price * (_size(pack) / _size(first)) ** 0.8 * (1 + 0.05 * (flavor_i % 3))
    p *= 0.92 if OWNERS[brand] == "own" else 1.1
    p = max(0.35, round(p * 20) / 20)
    return round(p - 0.01, 2) if p >= 1 and round(p * 100) % 10 == 0 else p


def allergens(fam: Family, flavor: F, may_codes: str) -> dict[str, list[str]]:
    """One variant's ``contains``, ``may_contain`` and ``free_from``, in ALLERGENS order."""
    have = set(fam.base) | {c for c in flavor.codes if c.isupper()}
    may = set(may_codes) - have
    pick = lambda codes: [ALLERGENS[c] for c in ALLERGENS if c in codes]  # noqa: E731
    return {
        "contains": pick(have),
        "may_contain": pick(may),
        "free_from": pick(set(ALLERGENS) - have - may),
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
        noun = (
            "multi-surface spray that cuts through grease"
            if fam.axis == "scent" and fam.department.startswith("Cleaning")
            else "light body milk that absorbs quickly"
        )
        return f"A {noun}, in {sizes}. Scented with {names[0].lower()}."
    if len(names) > 1:
        head = f"{fam.product_type} in {len(names)} flavors: {', '.join(names)}. In {sizes}."
    else:
        head = f"{names[0]}, in {sizes}."
    out = [head, STORAGE_TEXT[fam.storage]]
    contains = _union(s.get("contains", []) for s in skus)
    may = [a for a in _union(s.get("may_contain", []) for s in skus) if a not in contains]
    if contains:
        out.append(f"Contains: {', '.join(contains)}.")
    if may:
        out.append(f"May contain: {', '.join(may)}.")
    if "Vegan" in _common(s.get("dietary", []) for s in skus):
        out.append("Suitable for vegans.")
    return " ".join(out)


def _drawing(fam: Family, flavor: F, pid: str, pack: dict) -> dict:
    color = (flavor.name, "solid", flavor.hex, "#ffffff")
    if fam.shape == "produce_pile":
        grams = pack.get("net_weight_g")
        count = None if grams else pack["units_per_pack"]
        params = pile_params(FRUIT[flavor.name], pid, PILE_PACK[pack["pack_size"]], grams, count)
        return drawing(fam.shape, color, fam.label, **params)
    return drawing(fam.shape, color, LABELS.get((fam.code, flavor.name), fam.label))


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
    title = fam.title.format(line=head, flavor=flavors[0].name)
    attrs = [attr(fam.axis, fam.axis.capitalize(), f.name) for f in flavors]
    attrs += [attr("pack_size", "Pack size", p) for p in packs]
    if fam.food:
        contains = _union(s.get("contains", []) for s in skus)
        may = [a for a in _union(s.get("may_contain", []) for s in skus) if a not in contains]
        attrs += [attr("contains", "Contains", a) for a in contains]
        attrs += [attr("may_contain", "May contain", a) for a in may]
        attrs += [
            attr("free_from", "Free from", a) for a in _common(s.get("free_from", []) for s in skus)
        ]
        attrs += [
            attr("dietary", "Dietary", d) for d in _common(s.get("dietary", []) for s in skus)
        ]
        attrs += [
            attr("storage", "Storage", fam.storage),
            attr("nutrition_grade", "Nutrition grade", f"Grade {grade}"),
        ]
    extra = (
        {"ingredients": union([s["ingredients"] for s in skus])} if "ingredients" in skus[0] else {}
    )
    h = zlib.crc32(pid.encode())
    prices = [s["price"] for s in skus]
    return product(
        pid, skus, {},
        title=title, brand=brand, brand_owner=OWNERS[brand], department=[fam.department],
        product_type=fam.product_type, category_path=list(fam.path), category_leaf=fam.path[-1],
        description=_description(fam, flavors, parsed, skus), attributes=attrs,
        drawing=_drawing(fam, flavors[0], pid, parsed[0]), collections=[], currency="GBP",
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
    total = sum(f.weight for f in FAMILIES)
    budget = {f.code: max(1, round(skus * f.weight / total)) for f in FAMILIES}
    held: Counter[str] = Counter()
    titles: set[str] = set()
    recs: list[dict] = []

    def add(fam: Family, line: str, brand: str, flavors: list[F], packs: list[str], may: str,
            organic: bool) -> bool:  # fmt: skip
        grade = rng.choice(fam.grades) if fam.grades else ""
        rec = style(fam, f"GRC-{fam.code}-{held[fam.code + '#'] + 1:04d}", line, brand, flavors,
                    packs, may, organic, grade)  # fmt: skip
        if rec["title"] in titles:
            return False
        titles.add(rec["title"])
        held[fam.code + "#"] += 1
        held[fam.code] += rec["sku_count"]
        recs.append(rec)
        return True

    for n, (code, names, may) in enumerate(ANCHORS):
        fam = fams[code]
        flavors = [next(f for f in fam.flavors if f.name == name) for name in names]
        packs = list(fam.packs)
        add(fam, LINES[n % len(LINES)], fam.brands[n % len(fam.brands)], flavors, packs, may, False)

    for fam in FAMILIES:
        misses = 0
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
    beside "Free from: Milk", because the Toffee in the style has milk). Each SKU is
    flattened with the product's entries for those two keys left out when it states none.
    """
    out = []
    for doc in docs:
        for variant in doc["variants"]:
            own = {e["key"] for e in variant["attributes"]}
            kept = [e for e in doc["attributes"] if e["key"] not in UNIONED - own]
            one = doc | {"attributes": kept, "variants": [variant]}
            out += standard.flat_documents(one, NUMERIC_FACTS)
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skus", type=int, default=TARGET)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    recs = build(args.skus, args.seed)
    docs = documents(recs)
    problems = standard.check_catalog(docs)
    print(json.dumps({**report(recs), "standard_problems": len(problems)}, indent=1))
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        write_jsonl(iter(docs), args.out / "nested.jsonl")
        write_jsonl(iter(flat(docs)), args.out / "flat.jsonl")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
