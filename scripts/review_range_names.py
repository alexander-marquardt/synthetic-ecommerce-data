#!/usr/bin/env python3
"""Review the retail export for range names that read as brands (gen#623).

    uv run python scripts/review_range_names.py FILE.jsonl     # an export: flat rows or products
    uv run python scripts/review_range_names.py                # the ceiling build, from scale.py

A *range name* (a line, a collection: "Larkrise", "Harrow") is a model word. A shopper reads it as
one only when it belongs to one brand and the row says so in a ``Line`` attribute; the same word
under many brands, or a brand's name inside another brand's title, reads as the wrong brand. The
review counts four classes and exits 1 when any is not 0:

* ``shared``: a range word that leads the titles of two or more brands (class A).
* ``foreign``: a title that names a brand other than the row's own (class B).
* ``phrase``: a brand made of a product phrase of two or more words, "Card Game Row" (class C).
* ``unlabeled``: a title led by a range word whose row carries no ``Line`` (or ``Range``)
  attribute naming it (class D).

A single-word brand that is also a product word ("Cardigan Finch", "Red Kite") is a deliberate decoy
of the failure classes and is not a phrase brand.

The review takes plain dicts with ``title``, ``brand`` and ``attributes`` (a list of ``{key,
value}``), so it reads an export row, a nested product or a ``scale`` record alike.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"

#: The attribute keys that name a range on a row.
LINE_KEYS = ("line", "range")
_WORD = re.compile(r"[a-z0-9&]+")


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower().replace("'", "").replace("\u2019", ""))


def _singular(word: str) -> str:
    """A rough singular, enough to match "Card Games" with "card game"."""
    for tail, repl in (
        ("ies", "y"),
        ("ves", "f"),
        ("sses", "ss"),
        ("ches", "ch"),
        ("shes", "sh"),
        ("xes", "x"),
        ("s", ""),
    ):
        if len(word) > 3 and word.endswith(tail):
            return word[: -len(tail)] + repl
    return word


def _prototype() -> None:
    if str(RETAIL) not in sys.path:
        sys.path.insert(0, str(RETAIL))


def known_ranges() -> set[str]:
    """Every range name the generator draws from (its pools), read from the prototype."""
    _prototype()
    import grocery_rows  # noqa: PLC0415 -- the prototype's own directory is its import root
    import range_ownership  # noqa: PLC0415

    names = set(grocery_rows.LINES) | set(grocery_rows.TIER_LINES)
    names |= set(range_ownership.candidates())
    names |= set(range_ownership.AUTHORED)
    return names


def line_of(row: dict[str, Any]) -> str | None:
    """The row's ``Line`` or ``Range`` attribute value, if it has one."""
    for attr in row.get("attributes") or ():
        if str(attr.get("key", "")).lower() in LINE_KEYS and attr.get("value"):
            return str(attr["value"])
    return None


def lead_range(title: str, ranges: Iterable[str]) -> str | None:
    """The range name a title starts with ("The Harrow ..." or "Harrow ..."), longest first."""
    body = title[4:] if title.startswith("The ") else title
    best = None
    for name in ranges:
        if (body == name or body.startswith(name + " ")) and (
            best is None or len(name) > len(best)
        ):
            best = name
    return best


def _styles(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per style: an export row repeats its style once per SKU."""
    seen: dict[Any, dict[str, Any]] = {}
    for i, row in enumerate(rows):
        seen.setdefault(row.get("product_id", i), row)
    return list(seen.values())


def product_phrases(rows: Iterable[dict[str, Any]]) -> set[str]:
    """The product phrases of two or more words the rows sell: leaves, types and their labels."""
    phrases: set[str] = set()
    for row in rows:
        labels = [row.get("category_leaf"), row.get("product_type"), row.get("product_type_label")]
        labels += list(row.get("category_path") or ())
        for label in labels:
            if not isinstance(label, str):
                continue
            words = _words(label)
            for form in (words, [_singular(w) for w in words]):
                if len(form) >= 2:
                    phrases.add(" ".join(form))
    return phrases


def phrase_brands(brands: Iterable[str], phrases: set[str]) -> dict[str, str]:
    """Each brand that holds a product phrase of two or more words, with the phrase."""
    found: dict[str, str] = {}
    for brand in sorted(set(brands)):
        words = [_singular(w) for w in _words(brand)]
        for i in range(len(words)):
            for j in range(i + 2, len(words) + 1):
                if " ".join(words[i:j]) in phrases:
                    found.setdefault(brand, " ".join(words[i:j]))
    return found


def review(rows: Iterable[dict[str, Any]], ranges: Iterable[str] | None = None) -> dict[str, Any]:
    """The four classes over the rows: each a collection of what was found, empty when clean."""
    rows = list(rows)
    styles = _styles(rows)
    names = set(known_ranges() if ranges is None else ranges)
    # A line the data itself names also counts: an authored one is in no pool.
    names |= {v for s in styles if (v := line_of(s) or s.get("product_line") or s.get("series"))}
    names = sorted(names)
    brands = {s["brand"] for s in styles if s.get("brand")}

    by_range: dict[str, set[str]] = collections.defaultdict(set)
    unlabeled: list[tuple[str, str, str]] = []
    for s in styles:
        name = lead_range(s["title"], names)
        if name is None:
            continue
        by_range[name].add(s["brand"])
        if (line_of(s) or "").lower() != name.lower():
            unlabeled.append((s["title"], s["brand"], name))
    shared = {n: sorted(b) for n, b in sorted(by_range.items()) if len(b) >= 2}

    pattern = {b: re.compile(r"(?<![\w&])" + re.escape(b.lower()) + r"(?![\w&])") for b in brands}
    foreign: list[tuple[str, str, str]] = []
    for s in styles:
        title, own = s["title"].lower(), s["brand"]
        for other, rx in pattern.items():
            if other != own and other.lower() not in own.lower() and rx.search(title):
                foreign.append((s["title"], own, other))

    return {
        "styles": len(styles),
        "brands": len(brands),
        "shared": shared,
        "foreign": foreign,
        "phrase": phrase_brands(brands, product_phrases(rows)),
        "unlabeled": unlabeled,
    }


def counts(result: dict[str, Any]) -> dict[str, int]:
    """The number each class found: the ranges, the titles, the brands, the titles."""
    return {k: len(result[k]) for k in ("shared", "foreign", "phrase", "unlabeled")}


def read_rows(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def ceiling_rows(skus: int = 10**9) -> list[dict[str, Any]]:
    """The ceiling build's styles (every template exhausted), read from ``scale``."""
    _prototype()
    import scale  # noqa: PLC0415

    return list(scale.build(skus).records)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument(
        "export", nargs="?", type=Path, help="a .jsonl export; default: the ceiling build"
    )
    ap.add_argument("--show", type=int, default=8, help="examples to print per class")
    args = ap.parse_args(argv)
    rows = read_rows(args.export) if args.export else ceiling_rows()
    result = review(rows)
    print(f"{result['styles']} styles, {result['brands']} brands")
    for key in ("shared", "foreign", "phrase", "unlabeled"):
        found = result[key]
        print(f"{key}: {len(found)}")
        items = list(found.items()) if isinstance(found, dict) else found
        for item in items[: args.show]:
            print("   ", item)
    return 1 if any(counts(result).values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
