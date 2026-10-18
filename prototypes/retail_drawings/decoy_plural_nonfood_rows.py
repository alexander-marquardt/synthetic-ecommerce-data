"""Class 9 decoys from a non-food department: the fresh plural is a brand or a scent (gen#445).

On the combined demo with interpretation off, "lemons" must not return food alone. Each row is a
believable retail product (gen#444) of a department other than Food & Drink whose title carries
the exact plural of a fresh fruit or vegetable for one of two real reasons:

- **brand**: the plural is the label shown on the product, as a color word can be (Red Plover,
  gen#312): "Lucky Lemons Kids' Pyjamas" is a plain pair of pyjamas with ``brand: Lucky Lemons``
  and no lemon on them. The brands are invented (:data:`BRANDS`).
- **scent**: the product is scented with the fruit, and its ``fragrance`` attribute says so: a
  lemons hand wash, an oranges and cloves candle, a limes and sea salt air freshener.

No title or description claims the product is the fresh fruit. The fixing policy is the
category-node reading of the fresh word (the Oranges node keeps the fresh leaf and drops the
rest). Data only: :mod:`decoy_rows` turns each tuple into a :class:`decoy_rows.Decoy`.

A row is (code, kind, title, description, color, plural, sold, brand, scent): the brand is
``None`` for a scent row, the scent ``None`` for a brand row.
"""

# ruff: noqa: E501 -- one decoy's row reads better whole than wrapped (data only).

from __future__ import annotations

#: The invented fruit-word brands the brand rows carry, each on a product with no such motif.
BRANDS = ("Lucky Lemons", "Going Bananas", "Couch Potatoes", "Little Carrots", "Happy Onions")

ROWS: tuple[tuple[str, str, str, str, str, str, int, str | None, str | None], ...] = (
    # -- oranges
    ("XR01", "fruit_candle", "Oranges and Cloves Scented Candle", "A soy wax candle scented with oranges and cloves, in a glass jar. Burns for about 30 hours.", "Orange", "oranges", 960, None, "Orange & Clove"),
    ("XR02", "dish_soap", "Sweet Oranges Washing-Up Liquid, 500ml", "A washing-up liquid scented with sweet oranges, in a 500ml bottle.", "Orange", "oranges", 940, None, "Sweet Orange"),
    # -- lemons
    ("XR03", "kids_pj", "Lucky Lemons Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids, from the Lucky Lemons children's label.", "Navy", "lemons", 960, "Lucky Lemons", None),
    ("XR04", "kids_tee", "Lucky Lemons Kids' T-Shirt", "A plain cotton crew neck t-shirt for kids, from the Lucky Lemons children's label.", "White", "lemons", 940, "Lucky Lemons", None),
    ("XR05", "hand_wash", "Sicilian Lemons Hand Wash, 250ml", "A gentle hand wash scented with Sicilian lemons, in a 250ml pump bottle.", "Yellow", "lemons", 920, None, "Sicilian Lemon"),
    # -- limes
    ("XR06", "shower_gel", "Persian Limes Shower Gel, 250ml", "A shower gel scented with Persian limes, in a 250ml bottle.", "Green", "limes", 960, None, "Persian Lime"),
    ("XR07", "air_freshener", "Limes and Sea Salt Air Freshener", "A room mist scented with limes and sea salt, in a 300ml trigger spray.", "Green", "limes", 940, None, "Lime & Sea Salt"),
    # -- apples
    ("XR08", "shower_gel", "Green Apples Shower Gel, 250ml", "A shower gel scented with green apples, in a 250ml bottle.", "Green", "apples", 940, None, "Green Apple"),
    # -- strawberries
    ("XR09", "lotion", "Wild Strawberries Body Lotion, 200ml", "A light body lotion scented with wild strawberries, in a 200ml bottle.", "Pink", "strawberries", 940, None, "Wild Strawberry"),
    # -- raspberries
    ("XR10", "fruit_candle", "Raspberries and Vanilla Scented Candle", "A soy wax candle scented with raspberries and vanilla, in a glass jar.", "Pink", "raspberries", 940, None, "Raspberry & Vanilla"),
    # -- tomatoes
    ("XR11", "fruit_candle", "Tomatoes on the Vine Scented Candle", "A soy wax candle with the green, peppery scent of tomatoes on the vine, in a glass jar.", "Green", "tomatoes", 920, None, "Tomato Vine"),
    # -- onions
    ("XR12", "kids_tee", "Happy Onions Kids' T-Shirt", "A plain cotton crew neck t-shirt for kids, from the Happy Onions children's label.", "Cream", "onions", 920, "Happy Onions", None),
    # -- potatoes
    ("XR13", "kids_sweat", "Couch Potatoes Kids' Sweatshirt", "A soft crew neck sweatshirt for kids, from the Couch Potatoes loungewear label.", "Grey", "potatoes", 920, "Couch Potatoes", None),
    # -- carrots
    ("XR14", "kids_tee", "Little Carrots Kids' T-Shirt", "A plain cotton crew neck t-shirt for kids, from the Little Carrots children's label.", "Blue", "carrots", 920, "Little Carrots", None),
    # -- bananas
    ("XR15", "kids_pj", "Going Bananas Kids' Pyjamas", "Short-sleeve cotton pyjamas for kids, from the Going Bananas children's label.", "Pink", "bananas", 920, "Going Bananas", None),
    # -- cherries
    ("XR16", "hand_wash", "Cherries and Almond Hand Wash, 250ml", "A gentle hand wash scented with cherries and almond, in a 250ml pump bottle.", "Red", "cherries", 920, None, "Cherry & Almond"),
)

#: The product ids of these rows. A decoy is never the exemplar another decoy is cloned from
#: (:func:`decoy_apparel.build` skips them): a clone would carry a fruit-word brand to a style that
#: has no house style for it, and the decoy table of the clothing types would move.
IDS = frozenset(f"PLT-D{row[0]}" for row in ROWS)
