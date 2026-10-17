"""A style's words and its attributes agree (gen#250).

A description that says "magnetic fastening" over a style whose ``closure`` is Zip, or a
"polka dot" umbrella that sells a gingham color, is a row a shopper's filter and the
text contradict. :func:`disagreements` reads every record and returns one line per row
that disagrees, so the count is the metric (``tests/test_retail_attribute_text_250.py``
holds it at zero, and holds the check itself against hand-made rows).

Closure. The closure words are the six of :data:`FAMILIES`. A record that has a
``closure`` attribute and names a closure word in its title or description:

- when the attribute is one of the six (Zip, Magnetic, Snap, Drawstring, Clasp, Buckle), the text
  must name that closure;
- when it is another closure (Lace-Up, Pull-On, Ankle Strap, ...), the text may name only the
  closures :data:`ALSO` lists for it, each with the reason.

A closure word describing a pocket or a lining ("a zipped inner pocket") is not a
closure: :data:`NOT_A_CLOSURE` strips it first.

Pattern. A record with a ``pattern`` attribute sells only that pattern: every color
option (and the drawing) carries the pattern :data:`PATTERN_KIND` maps it to, and the
title and description name no other pattern.

Material words are not read: 71 of the template rows hold a material word that is not
the style's material (a leather-look decoy, a wooden handle on a steel knife, a ceramic
coating on an aluminum pan), and none of those is a defect. The reason is in
``docs/retail-attribute-text.md``.
"""

from __future__ import annotations

import re
from typing import Any

#: closure family -> the words that name it in text.
FAMILIES: dict[str, str] = {
    "zip": r"zip|zips|zipped|zipper|zippers",
    "magnetic": r"magnet|magnets|magnetic",
    "snap": r"snap|snaps|snapped|press[- ]studs?|poppers?",
    "drawstring": r"drawstring|drawstrings",
    "clasp": r"clasp|clasps",
    "buckle": r"buckle|buckles|buckled",
}
#: closure attribute value (lower case) -> its family, for the six that are one.
VALUE_FAMILY: dict[str, str] = {
    "zip": "zip",
    "magnetic": "magnetic",
    "snap": "snap",
    "drawstring": "drawstring",
    "clasp": "clasp",
    "buckle": "buckle",
}
#: closure attribute value (lower case) -> {family: why the text may name it}.
ALSO: dict[str, dict[str, str]] = {
    "ankle strap": {"buckle": "the strap fastens with a buckle"},
    "pull-on": {"buckle": "a wellington is pulled on; its side strap and buckle (drawn) are trim"},
    "slingback": {"buckle": "the back strap fastens with a buckle"},
}
#: A closure word that names a pocket, a lining or a section is a feature, not the closure.
NOT_A_CLOSURE = re.compile(
    r"\b(?:zip|zips|zipped|zipper|zippers)\s+(?:\w+\s+){0,2}"
    r"(?:pockets?|compartments?|sections?|linings?|pouch(?:es)?)\b",
    re.I,
)
#: pattern attribute value (lower case) -> the ``pattern`` of a color option and the drawing.
PATTERN_KIND: dict[str, str] = {
    "plain": "solid",
    "gingham": "gingham",
    "striped": "stripe",
    "stripe": "stripe",
    "polka dot": "polka",
}
#: pattern kind -> the other pattern kinds whose words it may also carry (gingham is a check).
PATTERN_ALSO: dict[str, set[str]] = {"gingham": {"check"}}
#: pattern kind -> the words that name it in text.
PATTERN_WORDS: dict[str, str] = {
    "stripe": r"stripe|stripes|striped|pinstripe|pinstriped",
    "gingham": r"gingham",
    "polka": r"polka|polka dot|polka dots|spotted",
    "check": r"check|checks|checked|plaid|tartan",
    "leopard": r"leopard",
}


def _named(text: str, words: dict[str, str]) -> set[str]:
    return {k for k, p in words.items() if re.search(rf"\b(?:{p})\b", text, re.I)}


def _values(rec: dict[str, Any], key: str) -> list[str]:
    return [a["value"] for a in rec.get("attributes", ()) if a["key"] == key]


def closure_lines(rec: dict[str, Any]) -> list[str]:
    """The closure disagreements of one record (empty when it agrees)."""
    text = NOT_A_CLOSURE.sub(" ", f"{rec['title']} {rec['description']}")
    named = _named(text, FAMILIES)
    out = []
    for value in _values(rec, "closure"):
        if not named:
            continue
        family = VALUE_FAMILY.get(value.lower())
        if family is not None:
            if family not in named:
                out.append(f"closure {value} but the text names {sorted(named)}")
            continue
        extra = named - set(ALSO.get(value.lower(), {}))
        if extra:
            out.append(f"closure {value} but the text names {sorted(extra)}")
    return out


def pattern_lines(rec: dict[str, Any]) -> list[str]:
    """The pattern disagreements of one record (empty when it agrees)."""
    out = []
    for value in _values(rec, "pattern"):
        kind = PATTERN_KIND.get(value.lower())
        if kind is None:
            out.append(f"pattern {value} is not in PATTERN_KIND")
            continue
        sold = {c.get("pattern") for c in rec.get("color_options", ())}
        if sold - {kind}:
            out.append(f"pattern {value} but color options sell {sorted(sold - {kind}, key=str)}")
        drawn = rec.get("drawing", {}).get("pattern")
        if drawn is not None and drawn != kind:
            out.append(f"pattern {value} but the drawing is {drawn}")
        said = _named(f"{rec['title']} {rec['description']}", PATTERN_WORDS) - {kind}
        said -= PATTERN_ALSO.get(kind, set())
        if said:
            out.append(f"pattern {value} but the text names {sorted(said)}")
    return out


def disagreements(records: list[dict[str, Any]]) -> list[str]:
    """``product_id: reason`` for every row whose words contradict its attributes."""
    return [
        f"{rec['product_id']}: {line}"
        for rec in records
        for line in closure_lines(rec) + pattern_lines(rec)
    ]
