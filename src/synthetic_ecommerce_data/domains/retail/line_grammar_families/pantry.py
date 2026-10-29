"""The pantry family of the line grammar: the food kinds that are neither a drink nor alcohol
(gen#665, gen#513).

A model is a plain own-label word (``Finest``, ``Basics``), an optional sub-model and a number,
then the product, e.g. "Hollin Finest Reserve 2 Strawberry Jam 340g". The words are plain
adjectives, kept disjoint from every other vocabulary on purpose, not a quoted list: only
"Finest", "Basics", "Value" and "Choice" are real own-label tiers of public grocery listings. A
word is no name, no place and no brand-like coinage, and none is in a food title, a description,
a flavor, a brand, another family's vocabulary or the first word of any other product's title.
"""

from __future__ import annotations

KINDS = (
    "Baby Food", "Battered Fish", "Biscuit", "Biscuits", "Bread", "Butter & Spreads", "Cake",
    "Cereal", "Cereal Bar", "Cheese", "Chips", "Chocolate Bar", "Chocolate Box",
    "Christmas Pudding", "Chutney", "Cookies", "Crisps", "Doughnut", "Easy Peelers",
    "Festive Bake", "Fish", "Free From Snack", "Fresh Fruit", "Fresh Vegetables",
    "Frozen Vegetables", "Fruit", "Hamper", "Honey", "Ice Cream", "Jam", "Lemons",
    "Letterbox Gift", "Meat", "Nuts & Popcorn", "Olive Oil", "Oranges", "Panettone", "Pasta",
    "Pickle", "Pizza", "Porridge", "Potatoes", "Ready Meal", "Rice & Grains", "Sauce",
    "Seasoning", "Snack Bar", "Spread", "Sugar", "Sweets", "Tinned Food", "Vinegar",
    "World Food", "Yogurt",
)  # fmt: skip
#: The lead words of the scale build.
LEADS = (
    "Sunday", "Weekday", "Basics", "Value", "Steady", "Plenty", "Bountiful", "Kindly",
    "Heartfelt", "Wholefood",
)  # fmt: skip
#: The lead words of the grocery build: disjoint from ``LEADS``, so one word belongs to one
#: brand across both builds (gen#642).
GROCERY_LEADS = (
    "Trusty", "Humble", "Generous", "Fair", "Honest", "Tasty", "Savoury", "Hearty",
    "Proper", "Plentiful", "Simply", "Gourmet", "Deli", "Artisan", "Rustic", "Supreme",
    "Wholesome", "Wholehearted", "Finest", "Pleasant", "Choice", "Homestyle", "Reliable",
    "Authentic", "Prime", "Dependable", "Cherished",
)  # fmt: skip
SUBS = ("Reserve", "Special", "Deluxe", "Edition", "Batch", "Series")
NUMBERS = tuple(range(2, 10))
#: The lead word alone is a model ("Finest Strawberry Jam"), the decoy-friendly short title.
BARE = True
#: The title leads with its brand in two of three draws (``line_grammar.brand_led``).
MIXED_BRAND = True
