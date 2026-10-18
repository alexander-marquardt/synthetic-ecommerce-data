"""The shopper-facing color word (gen#150): a plain color, never an object or a food.

A shade is authored under a fashion name ("Lemon", "Mustard", "Chocolate", "Velvet
Cherry"). The ``color`` facet and the SKU ``color`` field are what a shopper filters
and reads, so they carry a plain color word ("Yellow", "Dark Yellow", "Dark Brown",
"Red"). :func:`plain` maps an authored shade name to it; :func:`variants.cw` calls it,
so every swatch, SKU and facet downstream holds the plain word and the drawing keeps
the shade's hex. A fashion name may still sit in a title or a description when it reads
naturally ("a sunny lemon yellow"); it is never the facet value.

Two shades of one color on one style stay apart by a light or dark qualifier ("Lemon" is
``Yellow``, "Mustard" ``Dark Yellow``); a style that still collapsed two shades would
fail ``tests/test_retail_color_words.py``. Standard library only.
"""

from __future__ import annotations

import re

#: The words a color value is made of. A value is valid when every word is one of these
#: (or it is a foundation shade code such as ``2N``).
COLOR_WORDS = frozenset({
    "Aqua", "Beige", "Black", "Blue", "Brown", "Burgundy", "Camel", "Charcoal", "Clear",
    "Cobalt", "Copper", "Coral", "Cream", "Ecru", "Emerald", "Fuchsia", "Gold", "Green",
    "Grey", "Indigo", "Ivory", "Khaki", "Lavender", "Lilac", "Maroon", "Multi", "Natural", "Navy",
    "Nude", "Orange", "Pink", "Purple", "Red", "Rose", "Scarlet", "Silver", "Taupe",
    "Teal", "Tan", "White", "Yellow",
    # The shopper color words typed before a category (gen#195): each is a color value of
    # its own, never folded into a plainer one. A two-word color is one value.
    "Amber", "Aubergine", "Berry", "Caramel", "Champagne", "Duck", "Egg", "Mint", "Oatmeal",
    "Olive", "Quartz", "Raspberry", "Rust", "Stone", "Tortoiseshell",
    # The near-white shade typed before a garment (gen#302): "Off White" is one value.
    "Off",
})  # fmt: skip
#: Words that qualify a color: a tone, a finish, a material, a pattern or a denim wash.
MODIFIERS = frozenset({
    "Bright", "Brushed", "Burnt", "Dark", "Dusky", "Dusty", "Hot", "Light", "Pale", "Sheer",
    "Soft", "Heather", "Vintage", "Warm", "Velvet", "Washed", "Marl",
    "Leather", "Suede", "Patent", "Lace", "Check", "Gingham", "Polka", "Dot", "Spot",
    "Print", "Stripe", "Leopard", "Tartan", "Floral", "Patchwork", "Breton", "and",
})  # fmt: skip
#: The denim washes of a jeans style: a wash is a color word of its own there.
DENIM_WASHES = frozenset({"Rinse", "Light Wash", "Mid Wash", "Bleach Wash", "Grey Wash",
                          "Mid Wash and Yellow"})
#: A foundation or tint shade code: depth and undertone ("2N").
SHADE_CODE = re.compile(r"^\d+[CNW]$")

#: Authored shade -> plain color. A shade not here is already a plain word.
PLAIN = {
    # yellow, orange
    "Lemon": "Yellow", "Mustard": "Dark Yellow", "Ochre": "Dark Yellow",
    "Ginger": "Orange", "Peach": "Light Orange", "Peach Melba": "Light Orange",
    "Sheer Peach": "Sheer Orange", "Rust Leaf": "Dark Orange",
    "Terracotta": "Orange", "Coral Glow": "Coral", "Coral Reef": "Coral",
    "Velvet Coral": "Coral", "Honey": "Tan", "Wild Honey": "Tan",
    # red, pink, purple
    "Cherry Pop": "Red", "Velvet Cherry": "Red", "Poppy Field": "Red", "Post Box": "Bright Red",
    "Toffee Apple": "Light Red", "Watermelon": "Hot Pink", "Cinder Red": "Dark Red",
    "Brick Kiln": "Burnt Orange", "Velvet Brick": "Dark Orange", "Oxblood": "Dark Red",
    "Fig Jam": "Maroon", "Velvet Ruby": "Dark Red", "Ruby Spot": "Red Spot",
    "Velvet Scarlet": "Scarlet", "Claret": "Burgundy", "Wine": "Burgundy",
    "Plum Wine": "Burgundy", "Velvet Berry": "Dark Pink",
    "Sheer Berry": "Sheer Pink", "Blush": "Light Pink", "Blush Spot": "Pink Spot",
    "Pale Petal": "Pale Pink", "Tea Rose": "Pink", "Sheer Rose": "Sheer Rose",
    "Dusk Rose": "Dusty Rose", "Velvet Rosewood": "Dusty Rose",
    "Plum": "Dark Purple", "Velvet Plum": "Dark Purple", "Damson": "Dark Pink",
    "Bramble": "Dark Purple", "Mulberry": "Purple", "Orchid Bloom": "Light Purple",
    "Heather": "Light Purple", "Lilac Haze": "Lilac", "Velvet Mauve": "Purple",
    "Candy Stripe": "Red Stripe", "Confetti": "Multi Spot", "Gold Star": "Navy Spot",
    "Pastel Spot": "Blue Spot",
    # green
    "Lime": "Green", "Citrus Lime": "Bright Green",
    "Celadon": "Light Green", "Sage": "Green", "Sage Leaf": "Green Stripe",
    "Leaf": "Green", "Moss": "Dark Green", "Moss Green": "Green",
    "Olive Suede": "Dark Green Suede", "Sea Green": "Light Green",
    "Holly Sprig": "Cream Print",
    # blue, teal, navy
    "Ice": "Light Blue", "Glacier Blue": "Light Blue", "Sky": "Light Blue",
    "Sky Blue": "Light Blue", "Petrol": "Dark Teal",
    "Midnight": "Dark Navy", "Breton": "Navy Stripe", "Black Ice": "Black",
    "Cloud Grey": "Light Grey",
    # brown, beige, cream
    "Chocolate": "Dark Brown", "Chocolate Suede": "Dark Brown Suede",
    "Cocoa Bean": "Dark Brown", "Velvet Cocoa": "Dark Brown", "Espresso": "Dark Brown",
    "Walnut": "Dark Brown", "Mocha": "Brown", "Mocha Kiss": "Brown",
    "Chestnut": "Brown", "Cognac": "Brown", "Hazelnut": "Brown", "Oak": "Brown",
    "Tabby": "Brown", "Tobacco": "Brown", "Toffee": "Brown", "Mink": "Taupe",
    "Velvet Taupe": "Taupe", "Almond": "Beige", "Bare Linen": "Beige", "Calico": "Beige",
    "Fawn": "Beige", "Latte": "Light Brown", "Oat": "Light Beige",
    "Sand": "Beige",
    "Sand Suede": "Beige Suede",
    "Glaze": "Cream", "Oyster": "Cream", "Pearl": "Cream", "Porcelain": "Cream",
    "Kraft": "Tan Stripe", "Velvet Nude": "Nude", "Nude Shell": "Nude",
    # grey, metal
    "Slate": "Dark Grey", "Smoke": "Grey", "Pewter": "Dark Grey", "Storm Grey": "Dark Grey",
    "Dove Grey": "Light Grey", "Brass": "Gold",
    "Stripe": "Multi Stripe", "Gingham": "Red Gingham", "Ticking Stripe": "Blue Stripe",
    "Leopard": "Brown Leopard", "Forest": "Dark Green", "Bottle Green": "Dark Green",
}  # fmt: skip


def plain(name: str) -> str:
    """The plain color word for an authored shade name (the name itself when plain)."""
    return PLAIN.get(name, name)


#: Words that are a color only as the half of a two-word one (Duck Egg, Rose Quartz): alone they
#: are a bird, a food or a stone.
HALF_WORDS = frozenset({"Duck", "Egg", "Quartz", "Off"})


#: The pattern words an authored shade may carry after, or in place of, its color (gen#188).
#: They are a ``pattern`` value, never part of the ``color`` a shopper filters on.
PATTERN_WORDS = (
    "Polka Dot", "Gingham", "Breton Stripe", "Stripe", "Check", "Spot", "Print", "Leopard", "Marl",
    "Lace", "Tartan", "Floral", "Patchwork",
)  # fmt: skip
_PATTERN = re.compile(r"\b(" + "|".join(PATTERN_WORDS) + r")\b")
#: A denim wash: "Light Wash", "Mid Wash", "Bleach Wash", "Grey Wash", "Rinse" or a "Washed" tone.
_WASH = re.compile(r"\b((?:Light|Mid|Bleach|Grey) Wash|Rinse|Washed)\b")
#: The color of a wash with no color word of its own: denim is blue ("Grey Wash" is grey).
DENIM_BASE = "Blue"


def split(name: str) -> tuple[str, str | None]:
    """An authored shade -> (plain color, pattern or None).

    "Navy Stripe" is ``("Navy", "Stripe")``; "Light Wash" is ``("Blue", "Light Wash")`` (the
    base color of denim); "Washed Black" is ``("Black", "Washed")``; "Navy" is ``("Navy", None)``.
    The title and the swatch keep the authored words; only the color facet and the pattern facet
    read this.
    """
    wash = _WASH.search(name)
    hit = wash or _PATTERN.search(name)
    if hit is None:
        return name, None
    pattern = hit.group(1)
    rest = " ".join((name[: hit.start()] + " " + name[hit.end() :]).split())
    if pattern == "Grey Wash":
        return "Grey", pattern
    if not rest:
        return (DENIM_BASE if wash else "Multi"), pattern
    if rest.startswith("and "):
        return f"{DENIM_BASE} {rest}", pattern
    return rest, pattern


def is_plain(value: str) -> bool:
    """Whether ``value`` is a shade code, a denim wash or only color words and qualifiers."""
    if SHADE_CODE.match(value) or value in DENIM_WASHES:
        return True
    words = value.split()
    if len(words) == 1 and words[0] in HALF_WORDS:
        return False
    return bool(words) and all(w in COLOR_WORDS or w in MODIFIERS for w in words) and any(
        w in COLOR_WORDS for w in words
    )
