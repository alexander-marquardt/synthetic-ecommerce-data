"""Every shoe is one product sold in UK sizes and colors (gen#935).

A footwear style (a ``Mens``, ``Womens`` or ``Kids`` path whose second node is ``Shoes``) is one
product whose SKUs are UK size x color, grouped by ``product_id``, as most footwear rows already
are (:mod:`footwear_rows`). Three kinds of row were not:

- the planted shoe rows (:mod:`decoy_rows`, :mod:`decoy_product_words`) and the decoys cloned
  from them (:mod:`decoy_apparel`): one SKU, no size and one color;
- the decoys cloned from a sized style: its sizes, in one color;
- the slippers, sized S, M, L and XL, whose ``size_uk`` was a range ("7-8"), so "slippers size 7"
  reached none of them.

:func:`apply` runs last over the templates (:func:`scale.templates`), so a derived style copies a
template's sizes and nothing upstream moves. A row with no UK size, or a letter one, takes the
:data:`LADDERS` run of its audience's chart (:mod:`..core.size_charts`): whole sizes, one of them
sometimes not cut, as real ranges have gaps. A row sold in one color takes 2 to 5 from its type's
:data:`PALETTES`, every SKU of its hero color repeated in each.

A decoy keeps its decoy property (gen#294, gen#444): an added color is never a color word its title,
brand, line or description names, so "Brogues with Blue Sole" is never sold in blue and a
"Blue Bull" brand never in blue. A title that names the hero color ("Red Cashmere-Feel Chelsea
Boots") names each SKU's own color on that SKU (:data:`COLOR_COPY`, read by
:func:`export._variant`): the black SKU is "Black Cashmere-Feel Chelsea Boots".
"""

from __future__ import annotations

import random
import re

from synthetic_ecommerce_data.core import size_charts
from synthetic_ecommerce_data.domains.retail.class_model import SHADE_FAMILY
from synthetic_ecommerce_data.domains.retail.decoy_rows import COLORS
from synthetic_ecommerce_data.domains.retail.variants import cw, product, swatch

ROOTS = ("Mens", "Womens", "Kids")
#: The record field holding, per added color, the title and description its SKUs carry.
COLOR_COPY = "color_copy"
#: The SKU keys that state a size, replaced when a row takes a ladder.
SIZE_KEYS = ("size", "size_uk", "size_eu", "size_us")
#: Audience root -> (chart, first and last UK size of the run a row without sizes is cut in).
LADDERS = {
    "Womens": (size_charts.WOMENS_SHOES, "3", "8"),
    "Mens": (size_charts.MENS_SHOES, "6", "12"),
    "Kids": (size_charts.KIDS_SHOES, "8 Infant", "2 Junior"),
}
#: The colors a shoe of a type is sold in, most usual first; :data:`DEFAULT_PALETTE` otherwise.
DEFAULT_PALETTE = ("Black", "Brown", "Navy", "Grey", "Cream", "White", "Red", "Pink", "Blue",
                   "Green")  # fmt: skip
_FORMAL = ("Black", "Brown", "Navy", "Grey", "Cream", "Red")
_SPORT = ("White", "Black", "Grey", "Navy", "Red", "Blue", "Green", "Pink")
_SUMMER = ("Black", "Brown", "Cream", "White", "Pink", "Navy", "Red")
PALETTES: dict[str, tuple[str, ...]] = {
    **dict.fromkeys(("Brogues", "Loafers", "Chelsea Boots", "Court Shoes", "Block Heels",
                     "Kitten Heels", "Ankle Boots", "Chukka Boots", "Knee High Boots"), _FORMAL),
    **dict.fromkeys(("Trainers", "Running Shoes", "Plimsolls", "Platform Trainers"), _SPORT),
    **dict.fromkeys(("Sandals", "Ballet Pumps", "Espadrilles", "Mules", "Wedges"), _SUMMER),
    "Slippers": ("Grey", "Navy", "Pink", "Brown", "Cream", "Black", "Red"),
}  # fmt: skip
#: Colors a row is sold in after :func:`apply`: at least, and at most.
MIN_COLORS, MAX_COLORS = 2, 5


def is_footwear(rec: dict) -> bool:
    path = rec["category_path"]
    return len(path) > 1 and path[0] in ROOTS and path[1] == "Shoes"


def _whole(size: str) -> bool:
    return not size.split()[0].endswith(".5")


def ladder(rec: dict) -> list[str]:
    """The UK sizes a row without its own is cut in: its root's run, whole sizes, and one inner
    size left out of about a third of the rows."""
    chart, lo, hi = LADDERS[rec["category_path"][0]]
    keys = list(chart)
    run = [s for s in keys[keys.index(lo) : keys.index(hi) + 1] if _whole(s)]
    rng = random.Random(f"935-sizes-{rec['product_id']}")
    if rng.random() < 1 / 3:
        run.pop(rng.randrange(1, len(run) - 1))
    return run


def _named(word: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) is not None


def _text(rec: dict) -> str:
    return " ".join(str(rec.get(k) or "") for k in ("title", "brand", "description",
                                                    "product_line"))  # fmt: skip


def colors_for(rec: dict, held: list[str], titles: frozenset[str] = frozenset()) -> list[str]:
    """``held`` and the colors added to it: 2 to 5 in all, from the type's palette, never one
    whose word the row's text names, nor one whose own title (:func:`_swap`) is
    another row's title in ``titles``: "White Trainers with Black Sole" is never sold in red
    beside "Red Trainers with Black Sole"."""
    if len(held) >= MIN_COLORS:
        return held
    rng = random.Random(f"935-colors-{rec['product_id']}")
    want = rng.randint(MIN_COLORS, MAX_COLORS)
    text = _text(rec)
    pool = [c for c in PALETTES.get(rec["product_type"], DEFAULT_PALETTE)
            if c not in held and c in COLORS
            and not _named(c, text)
            and not (held and _named(held[0], rec["title"])
                     and _swap(rec["title"], held[0], c) in titles)]
    rng.shuffle(pool)
    return [*held, *pool[: want - len(held)]]


def _swap(text: str, old: str, new: str) -> str:
    """``text`` with the word ``old`` read as ``new``, in the case it was written in."""
    return re.sub(rf"\b{re.escape(old)}\b",
                  lambda m: new if m.group(0)[0].isupper() else new.lower(),
                  text, flags=re.IGNORECASE)  # fmt: skip


def _uk_range(value: str) -> tuple[float, float] | None:
    """A slipper's letter row's UK range ("7-8"), or ``None`` for a single size."""
    if "-" not in value:
        return None
    lo, hi = value.split("-")
    return float(lo), float(hi)


def _sized(rec: dict, color_skus: list[dict]) -> list[dict]:
    """One color's SKUs on the ladder: each takes the fields of the letter row it fell in, or
    the color's first SKU's."""
    chart = LADDERS[rec["category_path"][0]][0]
    out = []
    for uk in ladder(rec):
        base = color_skus[0]
        for s in color_skus:
            band = _uk_range(str(s.get("size_uk", "")))
            if band and band[0] <= float(uk.split()[0]) <= band[1]:
                base = s
                break
        row = {k: v for k, v in base.items() if k not in (*SIZE_KEYS, "sku")}
        _, eu, us = chart[uk]
        out.append(row | {"size_uk": uk, "size_eu": eu, "size_us": us})
    if not any(s["in_stock"] for s in out):
        out[0]["in_stock"] = True
    return out


def _needs_ladder(rec: dict) -> bool:
    return any("size_uk" not in s or "size" in s for s in rec["skus"])


def apply_one(rec: dict, titles: frozenset[str] = frozenset()) -> dict:
    """``rec`` sold in UK sizes and 2 to 5 colors: the same object when it already is.
    ``titles`` are the other rows' titles (:func:`colors_for`)."""
    if not is_footwear(rec):
        return rec
    held = list(dict.fromkeys(s["color"] for s in rec["skus"]))
    if not _needs_ladder(rec) and len(held) >= MIN_COLORS:
        return rec
    by_color = {c: [s for s in rec["skus"] if s["color"] == c] for c in held}
    if _needs_ladder(rec):
        by_color = {c: _sized(rec, skus) for c, skus in by_color.items()}
    else:
        by_color = {c: [{k: v for k, v in s.items() if k != "sku"} for s in skus]
                    for c, skus in by_color.items()}  # fmt: skip
    colors = colors_for(rec, held, titles)
    hero = held[0]
    swatches = {o["color"]: o for o in rec["color_options"]}
    copy_of: dict[str, dict[str, str]] = {}
    skus = [s for c in held for s in by_color[c]]
    for c in colors[len(held):]:
        swatches[c] = swatch(cw(c, COLORS[c]), SHADE_FAMILY.get(c, c.lower()))
        skus += [s | {"color": c} for s in by_color[hero]]
        if _named(hero, rec["title"]) or _named(hero, rec["description"]):
            copy_of[c] = {"title": _swap(rec["title"], hero, c),
                          "description": _swap(rec["description"], hero, c)}  # fmt: skip
    fields = {k: v for k, v in rec.items()
              if k not in ("product_id", "price", "sku_count", "skus", "color_options",
                           "size_options")}  # fmt: skip
    if copy_of:
        fields[COLOR_COPY] = copy_of
    return product(rec["product_id"], skus, swatches, **fields)


def apply(recs: list[dict]) -> list[dict]:
    """Every row of ``recs``, each footwear one sold in UK sizes and colors (:func:`apply_one`)."""
    titles = frozenset(r["title"] for r in recs)
    return [apply_one(r, titles) for r in recs]
