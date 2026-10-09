"""The retail catalog at any size: a target SKU count, reached from the 328 templates (gen#125).

Usage::

    python3 prototypes/retail_drawings/scale.py --skus 20000 [--seed 0] [--out PATH] [--report PATH]

prints the coverage and distinctness report as JSON, checks every document
against the output standard (:func:`synthetic_ecommerce_data.core.standard.check_catalog`)
and, with ``--out``, writes the standard nested documents as JSONL.

:func:`build` keeps the 328 hand-authored styles (:func:`build_preview4.samples`)
first, as templates, and derives further styles until the SKUs reach the target.
A derived style copies one template and changes, deterministically from the seed:

- its **range name** (:data:`RANGE_NAMES`): the ``product_line``, the template's
  ``line`` attribute and the title head ("The Harrow ..." -> "The Ashcombe ...");
- its **brand**, from the brands of the same type's templates plus the department's
  :data:`EXTRA_BRANDS` (:func:`brand_pools`);
- its **attribute values**, each drawn from the values the same leaf's templates
  carry (:func:`value_pools`). A value never changes when it names the leaf, the
  path or the type ("Skinny" in "Skinny Jeans"), when its key is
  :data:`FROZEN_KEYS`, when it has a unit, or when the title or description holds
  it inside a longer word ("5" in "5pk"). A changed value is rewritten in the
  title, the description, the drawing params and the same-named top-level field;
- its **colorways**, a subset of the template's colors. Its SKUs are the
  template's own size run times those colors (:func:`variants.product`): no
  SKU is invented;
- its rating, review count and sales, redrawn; a bestseller rank stays with the
  authored styles.

Two styles are clones when they share the leaf, the brand, the attributes (the
range name aside) and the title without the range name (:func:`clone_key`).
The build makes no clone, nor any twin: a second style with the same leaf, brand
and title without the range name (:func:`twin_key`), which reads as the same
listing. A derived title never repeats one already made.
Departments get styles by :data:`DEPARTMENT_SHARE`, and leaves within a
department by a Zipf weight, so leaf sizes keep a long tail. A template whose
draws keep colliding is exhausted and leaves the pool.

**Capacity.** Twins bound the build: per template, its type's brands times the
title-visible values its leaf offers. With today's templates every template is
exhausted at about 30K SKUs. Past that, the CLI reports ``reached_target: false``
and exits 2. To grow it, add data, not code: more brands per type
(:data:`EXTRA_BRANDS`, or templates with new brands), more values per leaf that
the title shows, and more templates, deep-SKU ones above all.

Images: a derived style keeps its template's drawing (params aside), so the
distinct drawings (:func:`coverage` ``images.distinct_drawings``) stay near the
template count. ``export.image_id`` still embeds the product id, so
``images.image_ids`` is one per product and colorway.
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import random
import re
import resource
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from build_preview4 import samples  # noqa: E402
from export import drawing_spec, image_id, standard_document  # noqa: E402
from variants import product  # noqa: E402

#: Invented range names; a derived style's ``product_line`` and title head.
RANGE_NAMES = (
    "Abberley", "Alnmoor", "Ardley", "Ashcombe", "Barrowden", "Belstone", "Brisley",
    "Caddon", "Calver", "Corrow", "Dalesby", "Dellow", "Dunsop", "Elmsett", "Elvet",
    "Eskerby", "Fenmoss", "Fothery", "Gorran", "Greyholt", "Haskett", "Hurlow",
    "Ilsley", "Kelderby", "Kittow", "Lathom", "Lowick", "Marden", "Morwick",
    "Nettlebed", "Norley", "Ockley", "Orrell", "Pellow", "Penwith", "Quarley",
    "Rathby", "Redesdale", "Rillaton", "Selwood", "Sorrel", "Stennis", "Tarrow",
    "Thurlby", "Torrin", "Ulverby", "Vellan", "Wenlow", "Whitsby", "Yarrowby",
    "Yelden", "Zennor", "Brantham", "Copley", "Cawdell", "Feltwick", "Holmbury",
    "Kimble", "Langrick", "Merrow",
)  # fmt: skip

#: Invented brands a department's derived styles may carry, beside its template brands.
EXTRA_BRANDS: dict[str, tuple[str, ...]] = {
    "Clothing": ("Marrowgate", "Pellbrook", "Osier & Vane", "Tallow Street"),
    "Lingerie & Nightwear": ("Dovecote Lane", "Hushwell"),
    "Home": ("Larchwood Living", "Emberly Home", "Cobble & Kiln"),
    "Beauty": ("Brightwater Botanics", "Orrin Skin"),
    "Food & Drink": ("Mossgill Dairy", "Wheatsheaf Lane", "Barrowby Kitchen"),
    "Footwear": ("Cobbleway", "Treadmoor"),
    "Garden": ("Rookery Garden Co.",),
    "Gifts": ("Ribbonvale",),
    "Toys": ("Pipwick Toys",),
    "Cleaning & Janitorial": ("Clearbrook Household",),
}

#: The share of derived styles per department; the rest split by template count.
DEPARTMENT_SHARE = {
    "Clothing": 0.44, "Lingerie & Nightwear": 0.04, "Footwear": 0.10,
    "Home": 0.20, "Beauty": 0.08,
}  # fmt: skip

#: Keys whose value never changes: who it is for, its name, its size range, and
#: the pattern the drawing shows.
FROZEN_KEYS = frozenset({"audience", "line", "size_range", "pattern"})

#: Leaf weight within a department: 1 / rank ** ZIPF_S.
ZIPF_S = 1.0

#: Draws per template before it counts as exhausted.
ATTEMPTS = 40

#: Fields :func:`variants.product` derives from the SKUs; never copied.
DERIVED_FIELDS = ("product_id", "price", "sku_count", "skus", "color_options", "size_options")


@dataclass
class Scaled:
    """A build: its records in order, and each derived record's template product id."""

    records: list[dict]
    template_of: dict[str, str]

    @property
    def skus(self) -> int:
        return sum(r["sku_count"] for r in self.records)


def templates() -> list[dict]:
    """The 328 hand-authored styles, in build order."""
    return [r for recs in samples().values() for r in recs]


def _words(text: str) -> str:
    return " " + re.sub(r"[^a-z0-9]+", " ", text.lower()) + " "


def _has_word(text: str, value: str) -> bool:
    return f" {_words(value).strip()} " in _words(text)


def value_pools(recs: list[dict]) -> dict[tuple[str, str], tuple[str, ...]]:
    """(leaf, key) -> the unit-free values the leaf's templates carry, in first-seen order."""
    pools: dict[tuple[str, str], dict[str, None]] = collections.defaultdict(dict)
    for r in recs:
        for a in r["attributes"]:
            if "unit_code" not in a:
                pools[(r["category_leaf"], a["key"])][str(a["value"])] = None
    return {k: tuple(v) for k, v in pools.items()}


def variable_keys(rec: dict, pools: dict[tuple[str, str], tuple[str, ...]]) -> list[str]:
    """The attribute keys a style derived from ``rec`` may change (see the module doc)."""
    names = " ".join([*rec["category_path"], rec["category_leaf"], rec["product_type"]])
    counts = collections.Counter(a["key"] for a in rec["attributes"])
    out = []
    for a in rec["attributes"]:
        key, value = a["key"], str(a["value"])
        if key in FROZEN_KEYS or "unit_code" in a or counts[key] > 1:
            continue
        if len(pools.get((rec["category_leaf"], key), ())) < 2 or _has_word(names, value):
            continue
        if any(value.lower() in t.lower() and not _has_word(t, value)
               for t in (rec["title"], rec["description"])):  # fmt: skip
            continue
        out.append(key)
    return out


def _line(rec: dict) -> str | None:
    if rec.get("product_line"):
        return str(rec["product_line"])
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == "line"), None)


def clone_key(rec: dict) -> tuple:
    """Leaf, brand, attributes and title, the range name taken out of both."""
    title, name = rec["title"], _line(rec)
    if name:
        title = re.sub(rf"\b{re.escape(name)}\b ?", "", title)
    attrs = tuple(
        sorted((a["key"], str(a["value"])) for a in rec["attributes"] if a["key"] != "line")
    )
    return (rec["category_leaf"], rec["brand"], attrs, title.strip())


def twin_key(rec: dict) -> tuple:
    """Leaf, brand and title without the range name: two styles that share it read as one
    listing whatever their unseen attributes, so the build makes no second (clones included)."""
    leaf, brand, _, title = clone_key(rec)
    return (leaf, brand, title)


def _swap(text: str, old: str, new: str) -> str:
    """``old`` -> ``new`` as a whole word in any case, each occurrence keeping its case:
    lower stays lower, a capital first letter stays capital, otherwise ``new`` as given."""

    def cased(m: re.Match[str]) -> str:
        hit = m.group(0)
        if hit.islower():
            return new.lower()
        if hit[0].isupper() and (len(hit) == 1 or hit[1:].islower()):
            return new[0].upper() + new[1:]
        return new

    return re.sub(rf"\b{re.escape(old)}\b", cased, text, flags=re.IGNORECASE)


def _title(tpl: dict, name: str) -> str:
    old = _line(tpl)
    if old and re.search(rf"\b{re.escape(old)}\b", tpl["title"]):
        return re.sub(rf"\b{re.escape(old)}\b", name, tpl["title"], count=1)
    if tpl["title"].startswith("The "):
        return f"The {name} {tpl['title'][4:]}"
    return f"{name} {tpl['title']}"


def derive(tpl: dict, pid: str, name: str, brand: str, values: dict[str, str],
           colors: list[str], owners: dict[str, str], rng: random.Random) -> dict:  # fmt: skip
    """One style from ``tpl``: the given range name, brand, attribute values and colors."""
    rec = {k: copy.deepcopy(v) for k, v in tpl.items() if k not in DERIVED_FIELDS}
    rec.pop("price_min", None)
    rec.pop("price_max", None)
    rec.pop("bestseller_rank", None)
    old_line = _line(tpl)
    rec["title"] = _title(tpl, name)
    if old_line:
        rec["description"] = _swap(rec["description"], old_line, name)
    rec["product_line"] = name
    for a in rec["attributes"]:
        if a["key"] == "line":
            a["value"] = name
        if a["key"] in values and values[a["key"]] != str(a["value"]):
            old, new = str(a["value"]), values[a["key"]]
            a["value"] = new
            rec["title"] = _swap(rec["title"], old, new)
            rec["description"] = _swap(rec["description"], old, new)
            if rec.get(a["key"]) == old:
                rec[a["key"]] = new
            params = rec["drawing"].get("params") or {}
            for p, v in params.items():
                if isinstance(v, str) and v.lower() == old.lower():
                    params[p] = new.lower() if v == old.lower() else new
    if brand != tpl["brand"]:
        rec["title"] = rec["title"].replace(tpl["brand"], brand)
        rec["description"] = rec["description"].replace(tpl["brand"], brand)
        rec["brand"] = brand
        if "brand_owner" in rec:
            rec["brand_owner"] = owners.get(brand, "third_party")
    if "rating" in rec:
        rec["rating"] = round(rng.uniform(3.4, 4.9), 1)
    if "review_count" in rec:
        rec["review_count"] = int(rng.lognormvariate(3.2, 1.1))
    if "sold_last_5_days" in rec:
        rec["sold_last_5_days"] = int(rng.lognormvariate(3.5, 1.2))
    swatches = {c["color"]: c for c in tpl.get("color_options", ())}
    keep = set(colors)
    skus = [{k: v for k, v in s.items() if k != "sku"} for s in tpl["skus"]
            if "color" not in s or s["color"] in keep]  # fmt: skip
    out = product(pid, skus, swatches, **rec)
    if "price_min" in tpl:
        out["price_min"] = min(s["price"] for s in out["skus"])
        out["price_max"] = max(s["price"] for s in out["skus"])
    return out


def _department(rec: dict) -> str:
    return str(rec["department"][0])


def _plan(tpls: list[dict], rng: random.Random) -> dict[str, dict[str, list[dict]]]:
    """department -> leaf -> its templates, leaves in a seeded Zipf rank order."""
    plan: dict[str, dict[str, list[dict]]] = collections.defaultdict(dict)
    for r in tpls:
        plan[_department(r)].setdefault(r["category_leaf"], []).append(r)
    for dept, leaves in plan.items():
        order = sorted(leaves)
        rng.shuffle(order)
        plan[dept] = {leaf: leaves[leaf] for leaf in order}
    return plan


def brand_pools(tpls: list[dict]) -> dict[tuple[str, str], list[str]]:
    """(department, product type) -> the brands its templates carry, then the department's
    :data:`EXTRA_BRANDS`: a denim label never sells a car coat."""
    out: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for r in tpls:
        pool = out[(_department(r), r["product_type"])]
        if r["brand"] not in pool:
            pool.append(r["brand"])
    for (dept, _), pool in out.items():
        pool += [b for b in EXTRA_BRANDS.get(dept, ()) if b not in pool]
    return dict(out)


def _department_weights(plan: dict[str, dict[str, list[dict]]]) -> dict[str, float]:
    rest = [d for d in plan if d not in DEPARTMENT_SHARE]
    left = 1.0 - sum(DEPARTMENT_SHARE[d] for d in plan if d in DEPARTMENT_SHARE)
    sizes = {d: sum(len(t) for t in plan[d].values()) for d in rest}
    total = sum(sizes.values()) or 1
    return {d: DEPARTMENT_SHARE.get(d, left * sizes.get(d, 0) / total) for d in plan}


def build(skus: int, seed: int = 0) -> Scaled:
    """Styles until their SKUs reach ``skus``: the templates first, then derived ones."""
    tpls = templates()
    records: list[dict] = []
    for r in tpls:
        if sum(x["sku_count"] for x in records) >= skus:
            return Scaled(records, {})
        records.append(r)
    rng = random.Random(seed)
    pools = value_pools(tpls)
    owners = {r["brand"]: r["brand_owner"] for r in tpls if "brand_owner" in r}
    brands = brand_pools(tpls)
    plan = _plan(tpls, rng)
    weights = _department_weights(plan)
    used = {twin_key(r) for r in tpls}
    titles = {r["title"] for r in tpls}
    template_of: dict[str, str] = {}
    total = sum(r["sku_count"] for r in records)
    serial = 0
    while total < skus and plan:
        depts = list(plan)
        dept = rng.choices(depts, [weights[d] for d in depts])[0]
        leaves = list(plan[dept])
        leaf = rng.choices(leaves, [1 / (i + 1) ** ZIPF_S for i in range(len(leaves))])[0]
        tpl = rng.choice(plan[dept][leaf])
        pool = brands[(dept, tpl["product_type"])]
        made = _draw(tpl, serial, pools, pool, owners, used, titles, rng)
        if made is None:
            plan[dept][leaf].remove(tpl)
            if not plan[dept][leaf]:
                del plan[dept][leaf]
            if not plan[dept]:
                del plan[dept]
            continue
        serial += 1
        records.append(made)
        template_of[made["product_id"]] = tpl["product_id"]
        total += made["sku_count"]
    return Scaled(records, template_of)


def _draw(tpl: dict, serial: int, pools: dict, brands: list[str], owners: dict[str, str],
          used: set, titles: set, rng: random.Random) -> dict | None:  # fmt: skip
    """A new style from ``tpl``, or None when ATTEMPTS draws all repeat one."""
    keys = variable_keys(tpl, pools)
    colors = [c["color"] for c in tpl.get("color_options", ())]
    pid = f"{tpl['product_id'].split('-')[0]}-{serial + 1:06d}"
    for _ in range(ATTEMPTS):
        brand = rng.choice(brands)
        values = {k: rng.choice(pools[(tpl["category_leaf"], k)]) for k in keys}
        pick = sorted(rng.sample(range(len(colors)), rng.randint(1, len(colors)))) if colors else []
        name = rng.choice(RANGE_NAMES)
        rec = derive(tpl, pid, name, brand, values, [colors[i] for i in pick], owners, rng)
        if twin_key(rec) in used or rec["title"] in titles:
            continue
        used.add(twin_key(rec))
        titles.add(rec["title"])
        return rec
    return None


def coverage(recs: list[dict]) -> dict[str, Any]:
    """Styles, SKUs, products per leaf, attribute fill per type and the image counts."""
    per_leaf = collections.Counter(r["category_leaf"] for r in recs)
    sizes = sorted(per_leaf.values(), reverse=True)
    top = max(1, len(sizes) // 10)
    by_type: dict[str, list[dict]] = collections.defaultdict(list)
    for r in recs:
        by_type[r["product_type"]].append(r)
    fill = {}
    for ptype, rows in sorted(by_type.items()):
        keys = {a["key"] for r in rows for a in r["attributes"]}
        have = [{a["key"] for a in r["attributes"]} for r in rows]
        share = [sum(k in h for h in have) / len(rows) for k in keys]
        fill[ptype] = {"products": len(rows), "keys": len(keys),
                       "fill": round(sum(share) / len(share), 3) if share else 1.0}  # fmt: skip
    depts: dict[str, list[int]] = collections.defaultdict(list)
    for r in recs:
        depts[_department(r)].append(r["sku_count"])
    specs = {json.dumps(drawing_spec(r, s), sort_keys=True) for r in recs for s in r["skus"]}
    return {
        "styles": len(recs),
        "skus": sum(r["sku_count"] for r in recs),
        "skus_per_style_by_department": {
            d: {"styles": len(v), "skus": sum(v), "per_style": round(sum(v) / len(v), 1)}
            for d, v in sorted(depts.items())
        },
        "leaves": len(per_leaf),
        "products_per_leaf": dict(per_leaf.most_common()),
        "leaf_size": {
            "max": sizes[0],
            "median": sizes[len(sizes) // 2],
            "min": sizes[-1],
            "top_decile_share": round(sum(sizes[:top]) / len(recs), 3),
        },  # fmt: skip
        "attribute_fill": fill,
        "images": {
            "image_ids": len({image_id(r, s) for r in recs for s in r["skus"]}),
            "distinct_drawings": len(specs),
        },
    }


#: A derived style's price stays in [low * the leaf's cheapest template, high * its dearest].
PRICE_BAND = (0.75, 1.35)


def price_factor(changes: dict[str, tuple[str, str]]) -> float:
    """The price multiplier of attribute changes ``key -> (old, new)``."""
    return 1.0


def price_point(price: float) -> float:
    """``price`` on a retail price point."""
    return price


def grid_tile(rec: dict) -> tuple:
    """What a results grid shows of a style: its leaf, its hero picture and its price."""
    hero = rec["skus"][0]
    spec = json.dumps(drawing_spec(rec, hero), sort_keys=True)
    return (rec["category_leaf"], spec, hero["price"])


def grid_clones(recs: list[dict]) -> dict[str, Any]:
    """The styles that share their grid tile (:func:`grid_tile`) with another style."""
    tiles = collections.Counter(grid_tile(r) for r in recs)
    shared = sum(n for n in tiles.values() if n > 1)
    return {
        "styles": len(recs),
        "grid_clones": shared,
        "grid_clone_rate": round(shared / len(recs), 4),
        "largest_group": max(tiles.values()),
    }


def prices_per_leaf(recs: list[dict]) -> dict[str, Any]:
    """Distinct style prices per leaf: each leaf's count, then the min and the median."""
    prices: dict[str, set[float]] = collections.defaultdict(set)
    for r in recs:
        prices[r["category_leaf"]].add(r["price"])
    counts = sorted(len(v) for v in prices.values())
    return {
        "distinct": {leaf: len(v) for leaf, v in sorted(prices.items())},
        "min": counts[0],
        "median": counts[len(counts) // 2],
    }


def listing_tokens(rec: dict) -> frozenset[str]:
    """The words a shopper and the index read on a listing: the brand and the title."""
    return frozenset(_words(f"{rec['brand']} {rec['title']}").split())


def distinctness(
    recs: list[dict], sample: int = 500, seed: int = 0, jaccard: float = 0.8
) -> dict[str, Any]:
    """Duplicate titles and clones over all styles (excess copies: a pair is 1), and on a
    seeded sample the share of styles with a same-leaf listing at ``jaccard`` or above."""
    titles = collections.Counter(r["title"] for r in recs)
    clones = collections.Counter(clone_key(r) for r in recs)
    by_leaf: dict[str, list[tuple[int, frozenset[str]]]] = collections.defaultdict(list)
    for i, r in enumerate(recs):
        by_leaf[r["category_leaf"]].append((i, listing_tokens(r)))
    picked = random.Random(seed).sample(range(len(recs)), min(sample, len(recs)))
    near = 0
    for i in picked:
        mine = listing_tokens(recs[i])
        for j, other in by_leaf[recs[i]["category_leaf"]]:
            if j != i and len(mine & other) / len(mine | other) >= jaccard:
                near += 1
                break
    n = len(recs)
    dup = sum(c - 1 for c in titles.values())
    clone = sum(c - 1 for c in clones.values())
    return {
        "duplicate_titles": dup,
        "duplicate_title_rate": round(dup / n, 4),
        "clones": clone,
        "clone_rate": round(clone / n, 4),
        "near_duplicate_rate": round(near / len(picked), 4),
        "near_duplicate_sample": len(picked),
        "near_duplicate_jaccard": jaccard,
    }


def documents(scaled: Scaled) -> list[dict[str, Any]]:
    """The build as the output standard's nested documents."""
    return [standard_document(r) for r in scaled.records]


def main(argv: list[str] | None = None) -> int:
    from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: PLC0415

    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument(
        "--skus",
        type=int,
        required=True,
        help="target SKU count; the build stops at the first style past it",
    )
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--out", type=Path, help="write the standard nested documents here, one JSON per line"
    )
    ap.add_argument("--report", type=Path, help="write the report JSON here as well as to stdout")
    args = ap.parse_args(argv)
    start = time.perf_counter()
    scaled = build(args.skus, args.seed)
    docs = documents(scaled)
    built = time.perf_counter() - start
    problems = check_catalog(docs)
    if args.out:
        with args.out.open("w", encoding="utf-8") as handle:
            for d in docs:
                handle.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n")
    report = {
        "target_skus": args.skus,
        "reached_target": scaled.skus >= args.skus,
        "seed": args.seed,
        "coverage": coverage(scaled.records),
        "distinctness": distinctness(scaled.records, seed=args.seed),
        "templates_distinctness": distinctness(templates(), seed=args.seed),
        "standard_problems": len(problems),
        "build_seconds": round(built, 2),
    }
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report["peak_rss_mb"] = round(rss / (1 << 20 if sys.platform == "darwin" else 1 << 10))
    text = json.dumps(report, indent=1)
    if args.report:
        args.report.write_text(text + "\n", encoding="utf-8")
    print(text)
    for p in problems[:20]:
        print(p, file=sys.stderr)
    if problems:
        return 1
    if not report["reached_target"]:
        print(
            f"short: {scaled.skus} SKUs of {args.skus}; every template is exhausted",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
