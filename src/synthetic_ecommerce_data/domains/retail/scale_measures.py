"""The prices of a derived style and the measures of a build (:mod:`scale`)."""

from __future__ import annotations

import collections
import json
import random
from typing import Any

from synthetic_ecommerce_data.core.standard import words
from synthetic_ecommerce_data.domains.retail import grocery
from synthetic_ecommerce_data.domains.retail.export import drawing_spec, image_id
from synthetic_ecommerce_data.domains.retail.scale_text import (
    _department,
    _words,
    clone_key,
)


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


#: A derived style's seeded spread around its template's price, before the band.
JITTER = (0.85, 1.2)

#: The price weight of a word in a value: a premium material costs more, a cheap one less.
#: A value's weight is the product of its words' (1.0 when none is listed).
PREMIUM = {
    "cashmere": 1.6, "silk": 1.4, "goose": 1.3, "merino": 1.3, "leather": 1.3,
    "down": 1.25, "suede": 1.25, "wool": 1.2, "egyptian": 1.2, "velvet": 1.15,
    "linen": 1.15, "organic": 1.1, "canvas": 0.9, "faux": 0.85, "rubber": 0.85,
    "nylon": 0.85, "microfibre": 0.85, "synthetic": 0.8, "polyester": 0.8,
    "acrylic": 0.8, "hollowfibre": 0.8, "plastic": 0.8,
    "bone": 2.0, "porcelain": 1.4, "enamel": 0.75, "melamine": 0.5,
}  # fmt: skip


def _weight(value: str) -> float:
    out = 1.0
    for w in words(value).split():
        out *= PREMIUM.get(w, 1.0)
    return out


def price_factor(changes: dict[str, tuple[str, str]]) -> float:
    """The price multiplier of attribute changes ``key -> (old, new)``: each new value's
    :data:`PREMIUM` weight over the old one's."""
    out = 1.0
    for old, new in changes.values():
        out *= _weight(new) / _weight(old)
    return out


def _step(price: float) -> float:
    return 0.05 if price < 5 else 0.5 if price < 20 else 1.0 if price < 100 else 5.0


def price_point(price: float, lo: float | None = None, hi: float | None = None) -> float:
    """``price`` on the nearest retail price point (5p under £5, 50p under £20, £1 under
    £100, then £5), moved one point inward when that leaves ``[lo, hi]``."""
    step = _step(price)
    n = round(price / step)
    if lo is not None and n * step < lo - 1e-9:
        n += 1
    if hi is not None and n * step > hi + 1e-9:
        n -= 1
    return round(max(n, 1) * step, 2)


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


#: The word overlap (Jaccard, over brand and title) at which two same-leaf listings read as one.
NEAR_DUPLICATE_JACCARD = grocery.NEAR_DUPLICATE_JACCARD


def listing_tokens(rec: dict) -> frozenset[str]:
    """The words a shopper and the index read on a listing: the brand and the title."""
    return frozenset(_words(f"{rec['brand']} {rec['title']}").split())


def distinctness(
    recs: list[dict], sample: int = 500, seed: int = 0, jaccard: float = NEAR_DUPLICATE_JACCARD
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
