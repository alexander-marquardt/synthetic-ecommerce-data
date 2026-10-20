"""The colors a product type really comes in, and the words that are not a cloth (gen#448).

gen#275 gives every color-bearing type the six main colors. A type that is not sold in some of
them declares it here, with the colors it does come in and why: the color completion
(``main_colors.complete``), the row palettes (``mens_depth_rows``) and the decoy clone picker
(``decoy_apparel``) all read this one table, and ``tests/test_retail_real_attributes_448.py``
reds when a style of a restricted type carries a color outside it. A restricted type is asked
for only the main colors it does come in ("black suit trousers", never "yellow").

Other types are not restricted: "red shirt" must still find a shirt.
"""

from __future__ import annotations

import re

#: Shades a "shade in the description only" decoy (class 5) is spelled in: allowed on every
#: restricted type, because a near-neutral is a real finish of cloth (an ivory blazer).
NEUTRAL_SHADES = ("Ivory", "Cream", "Off White", "Taupe", "Beige", "Ecru", "Champagne", "Khaki",
                  "Camel", "Stone", "Oatmeal")  # fmt: skip

_TAILORED = ("Black", "Navy", "Grey", "Charcoal", "White")
_WHY_TAILORED = "tailoring comes in dark suiting colors and white, not in bright dyes"
_SCHOOL = ("Black", "Navy", "Grey", "Charcoal")
_WHY_SCHOOL = "school uniform follows the dull dress code colors of a school"

#: path prefix -> (the colors the type comes in, why): the longest prefix of a style's
#: ``category_path`` wins.
RESTRICTED: dict[tuple[str, ...], tuple[tuple[str, ...], str]] = {
    ("Mens", "Suits & Tailoring", "Blazers"): (_TAILORED, _WHY_TAILORED),
    ("Mens", "Suits & Tailoring", "Suit Jackets"): (_TAILORED, _WHY_TAILORED),
    ("Mens", "Suits & Tailoring", "Suit Trousers"): (_TAILORED, _WHY_TAILORED),
    ("Mens", "Suits & Tailoring", "Waistcoats"): (_TAILORED, _WHY_TAILORED),
    ("Mens", "Suits & Tailoring", "Dinner Suits"): (_TAILORED, _WHY_TAILORED),
    ("Mens", "Trousers", "Formal Trousers"): (_TAILORED, _WHY_TAILORED),
    ("Kids", "School Uniform", "School Trousers"): (_SCHOOL, _WHY_SCHOOL),
    ("Kids", "School Uniform", "School Shirts"): (
        ("White", "Blue"), "a school shirt is white or pale blue by the dress code"),
    ("Kids", "School Uniform", "School Skirts"): (
        (*_SCHOOL, "Brown", "Green", "Burgundy"), _WHY_SCHOOL),
    ("Kids", "School Uniform", "School Pinafores"): (
        (*_SCHOOL, "Brown", "Green", "Burgundy"), _WHY_SCHOOL),
    ("Womens", "Hosiery", "Tights"): (
        ("Nude", "Natural", "Black", "White", "Navy", "Grey", "Charcoal", "Brown", "Burgundy",
         "Teal", "Beige", "Cream"), "tights are skin tones and dark opaque colors"),
    ("Home", "Heating & Cooling", "Fans", "Ceiling Fans"): (
        ("White", "Black", "Silver", "Brown", "Gold", "Copper", "Bronze", "Nickel"),
        "a ceiling fan's color is its metal or wood finish"),
    ("Home", "Large Appliances", "Dishwashers"): (
        ("White", "Black", "Silver"), "enamel white, black or stainless steel (gen#334)"),
    ("Home", "Large Appliances", "Laundry"): (
        ("White", "Black", "Silver"), "enamel white, black or silver (gen#334)"),
}  # fmt: skip

_MATERIAL_WORDS = ("leather", "suede", "patent")
_MODIFIERS = frozenset({"dark", "light", "bright", "pale", "brushed", "polished", "deep"})
_PATTERN_WORDS = frozenset({"check", "polka", "dot", "stripe", "striped", "spot", "gingham"})


def _path(path) -> tuple[str, ...]:
    return (path,) if isinstance(path, str) else tuple(path)


def allowed_for(path) -> tuple[str, ...] | None:
    """The colors a style at ``path`` comes in, or None when it is not restricted."""
    p = _path(path)
    best = max((k for k in RESTRICTED if p[: len(k)] == k), key=len, default=None)
    return None if best is None else RESTRICTED[best][0]


def base_color(name: str) -> str:
    """The color of a "<Color> <Material>" swatch: "Black Leather" is Black."""
    words = name.split()
    if len(words) > 1 and words[-1].lower() in _MATERIAL_WORDS:
        return " ".join(words[:-1])
    return name


def _family(name: str) -> str:
    """The color word a swatch is filed under: the pattern, material and shade modifier off."""
    words = [w for w in base_color(name).split() if w.lower() not in _PATTERN_WORDS]
    words = [w for w in words if w.lower() not in _MODIFIERS] or words
    return " ".join(words)


def permits(path, color: str) -> bool:
    """Whether a style at ``path`` may carry ``color``."""
    allowed = allowed_for(path)
    if allowed is None:
        return True
    fam = _family(color)
    return fam in allowed or fam in NEUTRAL_SHADES or base_color(color) in allowed


def palette(path, colors: tuple[str, ...]) -> tuple[str, ...]:
    """``colors`` less those a style at ``path`` never comes in."""
    return tuple(c for c in colors if permits(path, c))


#: a non-cloth word -> (attribute key, attribute name, value) it is carried as
CARRIED_AS = {
    "crease resistant": ("finish", "Finish", "Crease Resistant"),
    "easy iron": ("finish", "Finish", "Easy Iron"),
    "non-iron": ("finish", "Finish", "Non-Iron"),
    "easy care": ("finish", "Finish", "Easy Care"),
    "garment dyed": ("finish", "Finish", "Garment Dyed"),
    "textured": ("finish", "Finish", "Textured"),
    "unstructured": ("finish", "Finish", "Unstructured"),
    "checked": ("pattern", "Pattern", "Check"),
    "check": ("pattern", "Pattern", "Check"),
    "arch support": ("feature", "Feature", "Arch Support"),
    "padded sole": ("feature", "Feature", "Padded Sole"),
    "moisture wicking": ("feature", "Feature", "Moisture Wicking"),
    "running": ("feature", "Feature", "Running"),
    "sports cushioned": ("feature", "Feature", "Cushioned"),
    "soft top": ("feature", "Feature", "Soft Top"),
}
#: Words a ``Material`` value must never be: a finish, a pattern or a sourcing claim, which
#: the row carries as ``Finish``, ``Pattern`` or inside a true material ("Recycled Polyester").
NOT_A_CLOTH = frozenset({*CARRIED_AS, "recycled"})
#: a sourcing claim -> the material it names
MATERIAL_OF = {"recycled": "Recycled Polyester"}


def not_a_cloth(value: str) -> bool:
    return re.sub(r"\s+", " ", value.strip().lower()) in NOT_A_CLOTH
