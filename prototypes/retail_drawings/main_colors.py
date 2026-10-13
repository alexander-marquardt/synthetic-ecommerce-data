"""The main colors every color-bearing type offers (gen#275).

Each retail product type that varies by color offers red, blue, green, yellow, black and
white as plain color values (gen#195: no shade name). The six are a baseline, not the full
set: a type keeps every color it had and may add more. :func:`complete` runs at the end of
:func:`scale.templates`: for each missing main color of a type it adds that color, as
SKUs copied from a solid color of one of the type's styles, to one style of the type (a
style whose text names no color of its own is preferred, and the choice rotates over the
type's styles, so one style does not take them all).

A type whose color IS its material or natural finish declares it in :data:`EXCEPTIONS`,
one line of reason each. A dyed, painted, printed or coated product carries the baseline.
``tests/test_retail_main_colors_275.py`` lists every color-bearing type and reds when one
lacks a main color without an entry here.
"""

from __future__ import annotations

import copy
import re

#: The baseline: plain color -> swatch hex (the color word is also the swatch family).
MAIN_COLORS = {
    "Red": "#c8322b", "Blue": "#2f6db5", "Green": "#3c8d4f", "Yellow": "#f2c230",
    "Black": "#2a2a2e", "White": "#ffffff",
}  # fmt: skip

#: product_type -> why its color is its material or natural finish (the only way out).
EXCEPTIONS = {
    "Bouquet": "cut flowers: the color is the bloom's own",
    "Lemons": "fresh fruit: the color is the fruit's own",
    "Oranges": "fresh fruit: the color is the fruit's own",
    "Foundation": "cosmetic: shade codes matched to skin tone",
    "Moisturiser": "cosmetic: tinted shade codes matched to skin tone",
    "Lipstick": "cosmetic: shades, not paint colors",
    "Lip Balm": "cosmetic: sheer tints of the balm",
    "Eyeliner": "cosmetic: a small range of liner shades",
    "Highlighter": "cosmetic: a glow shade of the pigment",
    "Perfume": "cosmetic: the color is the fragrance liquid's tint",
    "Watch": "metal case and strap finish: gold, silver, rose gold",
    "Earrings": "precious metal: the color is the metal",
    "Cutlery": "stainless steel and plated metal: the color is the metal",
    "Cutlery Set": "stainless steel: the color is the metal",
    "Claw Hammer": "forged steel tool: the color is the raw metal",
    "Socket Set": "chrome vanadium steel: the color is the raw metal",
    "Bit Set": "hardened steel bits: the color is the metal finish",
    "Trophy": "cast metal: the color is the plating",
    "Storage Jar": "glass: sold clear",
    "Mattress": "inner bedding: sold in its natural ticking",
    "Mattress Topper": "inner bedding: sold in its natural fill and cover",
    "Mattress Protector": "inner bedding: sold in its natural white cover",
    "Duvet": "inner bedding: sold in its natural white cover",
    "Pillow": "inner bedding: sold in its natural white cover",
    "Pillow Protector": "inner bedding: sold in its natural white cover",
}


def colored_types(tpls: list[dict]) -> dict[str, list[dict]]:
    """product_type -> its styles, for every type with a color selector."""
    out: dict[str, list[dict]] = {}
    for r in tpls:
        if r.get("color_options"):
            out.setdefault(r["product_type"], []).append(r)
    return out


def offered(styles: list[dict]) -> set[str]:
    return {c["color"] for r in styles for c in r["color_options"]}


def missing(tpls: list[dict]) -> dict[str, list[str]]:
    """product_type -> the main colors it lacks (an excepted type is left out)."""
    out = {}
    for ptype, styles in colored_types(tpls).items():
        lacks = [c for c in MAIN_COLORS if c not in offered(styles)]
        if lacks and ptype not in EXCEPTIONS:
            out[ptype] = lacks
    return out


def _material_skus(rec: dict) -> bool:
    """Whether a SKU carries its own upper material, which a copied color would repeat."""
    return any("upper_material" in s for s in rec["skus"])


def _names_main_color(rec: dict) -> bool:
    """Whether the text names a main color: once the type offers it, the text-agrees gate
    reads that word as naming a value this style lacks."""
    text = f"{rec['title']} {rec['description']}".lower()
    return any(re.search(rf"\b{c.lower()}\b", text) for c in MAIN_COLORS)


def _names(rec: dict, color: str) -> bool:
    return bool(re.search(rf"\b{color.lower()}\b", f"{rec['title']} {rec['description']}".lower()))


def _printed(rec: dict) -> bool:
    d = rec.get("drawing") or {}
    return d.get("pattern") == "print" or "motif" in d or "placement" in d


def _names_own_color(rec: dict) -> bool:
    text = f"{rec['title']} {rec['description']}".lower()
    for c in rec["color_options"]:
        words = [w for w in re.findall(r"[a-z]+", c["color"].lower())
                 if w not in ("dark", "light", "bright", "pale", "natural", "clear", "multi")]
        if any(re.search(rf"\b{w}\b", text) for w in words):
            return True
    return False


def _add(rec: dict, colors: list[str]) -> dict:
    import scale  # lazy: scale imports this module

    rec = copy.deepcopy(rec)
    base = next((c for c in rec["color_options"] if c["pattern"] == "solid"
                 and not re.search(r"suede|leather|patent|lace", c["color"], re.I)),
                next((c for c in rec["color_options"] if c["pattern"] == "solid"),
                     rec["color_options"][0]))  # fmt: skip
    swatches = {c["color"]: c for c in rec["color_options"]}
    skus = [{k: v for k, v in s.items() if k != "sku"} for s in rec["skus"]]
    seed = [s for s in skus if s.get("color") == base["color"]]
    for color in colors:
        swatches[color] = {"color": color, "hex": MAIN_COLORS[color], "pattern": "solid",
                           "family": color.lower()}
        skus += [{**s, "color": color} for s in seed]
        # A style whose SKUs carry an upper material in more than one (a compound attribute
        # such as "leather, patent"): the new color keeps them all, one per size in turn, so
        # a derived style that keeps it does not drop a part of the attribute.
        mats = list(dict.fromkeys(s["upper_material"] for s in skus if "upper_material" in s))
        if len(mats) > 1:
            added = [s for s in skus if s["color"] == color]
            for n, s in enumerate(added):
                s["upper_material"] = mats[n % len(mats)]
    fields = {k: v for k, v in rec.items() if k not in scale.DERIVED_FIELDS}
    out = scale.product(rec["product_id"], skus, swatches, **fields)
    kept = len({s["color"] for s in out["skus"]})
    for f in ("title", "description"):
        out[f] = scale._restate_color_count(out[f], kept)
    if "price_min" in rec:
        out["price_min"] = min(s["price"] for s in out["skus"])
        out["price_max"] = max(s["price"] for s in out["skus"])
    return out


def complete(tpls: list[dict]) -> list[dict]:
    """``tpls`` with every missing main color added, in the same order."""
    by_id = {r["product_id"]: r for r in tpls}
    for ptype, lacks in missing(tpls).items():
        # A printed drawing takes no solid fill, so it never gets a color. Of the rest, the
        # best tier (no per-SKU material, text names no main color or color of its own)
        # takes the colors in rotation; a style whose text names a missing main color takes
        # that color itself, or the text-agrees gate reads the word as naming a value the
        # style lacks once the type offers it.
        styles = sorted(
            (r for r in colored_types(tpls)[ptype] if not _printed(r)),
            key=lambda r: r["product_id"],
        )
        if not styles:
            raise ValueError(f"{ptype}: every style is a printed drawing, none takes a solid color")
        tier = lambda r: (_material_skus(r), _names_main_color(r), _names_own_color(r))  # noqa: E731
        best = [r for r in styles if tier(r) == min(tier(x) for x in styles)]
        picks: dict[str, list[str]] = {}
        for i, color in enumerate(lacks):
            naming = [r for r in styles if _names(r, color)]
            pick = naming[0] if naming else best[i % len(best)]
            picks.setdefault(pick["product_id"], []).append(color)
        for pid, colors in picks.items():
            by_id[pid] = _add(by_id[pid], colors)
    return [by_id[r["product_id"]] for r in tpls]
