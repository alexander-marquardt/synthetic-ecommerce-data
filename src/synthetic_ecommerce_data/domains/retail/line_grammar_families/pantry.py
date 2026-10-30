"""The pantry family of the line grammar: the food kinds that are neither a drink nor alcohol
(gen#665, gen#513).

A model is a plain own-label word (``Finest``, ``Basics``) and an optional style word of the kind
(``STYLES``), then the product, e.g. "Hollin Finest Slow Cooked Strawberry Jam 340g". The lead
words are plain adjectives, kept disjoint from every other vocabulary on purpose, not a quoted
list: only "Finest", "Basics", "Value" and "Choice" are real own-label tiers of public grocery
listings. A word is no name, no place and no brand-like coinage, and none is in a food title, a
description, a flavor, a brand, another family's vocabulary or the first word of any other
product's title. A food model never carries a number and a style word never states a fact a
record has to back (a dietary claim, an ingredient), so a brand short of words sells fewer lines
(gen#729).
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
_BAKED = (
    "Bakery Style", "Hand Finished", "Light & Fluffy", "Extra Moist", "Home Baked Style",
    "Celebration", "Tray Baked", "Layered",
)  # fmt: skip
_BISCUIT = (
    "Hand Baked", "Bakery Style", "Extra Crunchy", "Thin & Crispy", "Melt Away",
    "Twice Baked", "Oven Baked", "Soft Baked", "Slow Baked", "Lightly Baked",
)  # fmt: skip
_BAR = (
    "Chewy", "Extra Chewy", "Extra Crunchy", "Oven Baked", "Soft Baked", "Lunchbox", "On the Go",
    "Lightly Toasted", "Slow Toasted", "Hand Baked",
)  # fmt: skip
_FESTIVE = (
    "Slow Risen", "Hand Wrapped", "Italian Style", "Traditional", "Bakery Style",
    "Hand Finished", "Naturally Leavened", "Celebration",
)  # fmt: skip
_GIFT = (
    "Luxury", "Indulgent", "Thoughtful", "Celebration", "Hand Packed", "Seasonal", "Treasured",
)  # fmt: skip
_FRUIT = (
    "Hand Picked", "Sun Ripened", "Naturally Ripened", "Hand Selected", "Seasonal",
    "Carefully Graded",
    "Farm Picked", "Just Picked", "Market Selected",
)  # fmt: skip
_VEGETABLE = (
    "Hand Picked", "Farm Picked", "Just Picked", "Seasonal", "Field Grown", "Hand Selected",
    "Market Selected", "Freshly Harvested",
)  # fmt: skip
#: Kind -> the style words a model of it may carry after its lead word ("Finest Greek Style"):
#: words a shelf label uses, one row per kind, so "Greek Style" never reaches the crisps.
STYLES = {
    "Baby Food": (
        "First Tastes", "Smooth Blend", "Gentle Blend", "Slow Cooked", "Little Bites",
        "Tiny Tastes", "Steam Cooked", "Soft Mash",
    ),
    "Battered Fish": (
        "Extra Crunchy", "Light & Crunchy", "Thick Cut", "Seaside Style", "Pub Style", "Chunky",
        "Flaky", "Crunchy Coated",
    ),
    "Biscuit": _BISCUIT,
    "Biscuits": _BISCUIT,
    "Bread": (
        "Farmhouse", "Thick Sliced", "Medium Sliced", "Stonebaked", "Bakery Style", "Crusty",
        "Slow Proved", "Hand Shaped", "Oven Bottom",
    ),
    "Butter & Spreads": (
        "Farmhouse", "Country Style", "Traditional", "Lightly Whipped", "Soft & Creamy",
        "Extra Creamy", "Easy Spreading", "Home Style",
    ),
    "Cake": _BAKED,
    "Cereal": (
        "Extra Crunchy", "Oven Baked", "Lightly Toasted", "Slow Toasted", "Breakfast Style",
        "Clustered",
        "Hand Baked", "Big Flake",
    ),
    "Cereal Bar": _BAR,
    "Cheese": (
        "Farmhouse", "Hand Crafted", "Traditional", "Hand Cut", "Slow Matured", "Small Batch",
        "Hand Made", "Cave Aged", "Vintage",
    ),
    "Chips": (
        "Skin On", "Extra Crispy", "Thin Cut", "Thick Cut", "Shoestring", "Seasoned", "Home Style",
        "Oven Ready",
    ),
    "Chocolate Bar": (
        "Silky Smooth", "Single Origin", "Luxury", "Stoneground", "Belgian Style", "Swiss Style",
        "Extra Smooth", "Indulgent", "Velvety", "Rich", "Slow Conched", "Thin",
    ),
    "Chocolate Box": (
        "Luxury", "Assorted", "Indulgent", "After Dinner", "Celebration", "Belgian Style",
        "Swiss Style", "Hand Finished",
    ),
    "Christmas Pudding": (
        "Matured", "Slow Steamed", "Traditional", "Family Recipe", "Vintage", "Rich",
        "Old Fashioned", "Hand Stirred",
    ),
    "Chutney": (
        "Chunky", "Slow Cooked", "Rich", "Hand Packed", "Small Batch", "Tangy", "Sticky",
        "Old Fashioned",
    ),
    "Cookies": _BISCUIT,
    "Crisps": (
        "Double Fried", "Slow Fried", "Lightly Fried", "Extra Crunchy", "Extra Thick",
        "Thick Sliced", "Wafer Thin", "Thin & Crispy", "Pub Style", "Sharing", "Double Crunch",
        "Moreish",
    ),
    "Doughnut": (
        "Bakery Style", "Hand Finished", "Light & Fluffy", "Soft & Fluffy", "Fairground Style",
        "Hand Rolled", "Pillowy", "Melt Away",
    ),
    "Easy Peelers": _FRUIT,
    "Festive Bake": _FESTIVE,
    "Fish": (
        "Line Caught", "Skin On", "Hand Filleted", "Fishmonger's Cut", "Day Boat", "Deep Sea",
        "Pin Boned", "Oven Ready",
    ),
    "Free From Snack": (
        "Bakery Style", "Soft Baked", "Oven Baked", "Lunchbox", "Light & Crispy", "Hand Baked",
        "Thin & Crispy", "Lightly Baked",
    ),
    "Fresh Fruit": _FRUIT,
    "Fresh Vegetables": _VEGETABLE,
    "Frozen Vegetables": (
        "Home Style", "Farm Picked", "Steam Ready", "Quick Cook", "Field Picked", "Just Picked",
        "Hand Selected", "Microwave Ready", "Extra Tender",
    ),
    "Fruit": _FRUIT,
    "Hamper": _GIFT,
    "Honey": (
        "Raw", "Single Origin", "Beekeeper's", "Unblended", "Pure", "Lightly Filtered",
        "Wild Meadow",
    ),
    "Ice Cream": (
        "Soft Scoop", "Luxury", "Gelato Style", "Slow Churned", "Rich & Creamy", "Smooth & Creamy",
        "Indulgent", "Parlor Style", "Extra Creamy", "Italian Style", "Double Churned",
    ),
    "Jam": (
        "Slow Cooked", "Small Batch", "Hand Stirred", "Old Fashioned", "Country Style",
        "Home Style", "Preserving Pan", "Open Pan",
    ),
    "Lemons": _FRUIT,
    "Letterbox Gift": _GIFT,
    "Meat": (
        "Butcher's Cut", "Hand Prepared", "Farm Assured", "Traditional", "Extra Tender",
        "Outdoor Reared", "Slow Reared", "Family Farmed", "Hand Selected",
    ),
    "Nuts & Popcorn": (
        "Oven Baked", "Snacking", "Sharing", "Moreish", "Extra Crunchy", "Bar Style", "Pub Style",
        "Lightly Dusted",
    ),
    "Olive Oil": (
        "Cold Pressed", "First Pressed", "Single Estate", "Hand Harvested", "Early Harvest",
        "Unfiltered", "Stone Pressed", "Single Grove", "Late Harvest",
    ),
    "Oranges": _FRUIT,
    "Panettone": _FESTIVE,
    "Pasta": (
        "Bronze Cut", "Slow Dried", "Italian Style", "Al Dente", "Traditional", "Trattoria Style",
        "Quick Cook", "Hand Rolled",
    ),
    "Pickle": (
        "Extra Crunchy", "Tangy", "Chunky", "Traditional", "Small Batch", "Slow Brined",
        "Old Fashioned",
        "Barrel Aged",
    ),
    "Pizza": (
        "Wood Fired", "Thin & Crispy", "Deep Pan", "Hand Stretched", "Stonebaked", "Thin Crust",
        "Pan Baked", "Italian Style", "Pizzeria Style", "Oven Baked", "Fire Baked",
    ),
    "Porridge": (
        "Creamy", "Steel Cut", "Rolled", "Jumbo", "Slow Cooked", "Quick Cook", "Stoneground",
        "Microwave Ready",
    ),
    "Potatoes": _VEGETABLE,
    "Ready Meal": (
        "Slow Cooked", "Restaurant Style", "Home Cooked Style", "Oven Baked", "Microwave Ready",
        "Family", "Home Style", "Hand Prepared", "Chef Prepared",
    ),
    "Rice & Grains": (
        "Fluffy", "Aged", "Quick Cook", "Steam Ready", "Microwave Ready", "Easy Cook", "Fragrant",
        "Stone Milled",
    ),
    "Sauce": (
        "Rich & Smooth", "Slow Cooked", "Tangy", "Squeezy", "Signature Recipe", "Home Style",
        "Restaurant Style", "Silky", "Bold", "Family Recipe",
    ),
    "Seasoning": (
        "Hand Blended", "Bold", "Stone Ground", "Freshly Ground", "Coarse Ground", "Home Style",
        "Butcher's Blend", "Small Batch",
    ),
    "Snack Bar": _BAR,
    "Spread": (
        "Stoneground", "Small Batch", "Slow Roasted", "Double Roasted", "Deep Roasted",
        "Extra Rich", "Home Style", "Velvety",
    ),
    "Sugar": (
        "Unrefined", "Fine", "Extra Fine", "Natural", "Free Flowing", "Slow Crystallized",
        "Baking", "Pure",
    ),
    "Sweets": (
        "Chewy", "Extra Chewy", "Old Fashioned", "Hand Pulled", "Vintage Style", "Pick & Mix",
        "Sharing",
        "Soft Centered", "Traditional", "Boiled", "Tangy", "Nostalgic",
    ),
    "Tinned Food": (
        "Store Cupboard", "Cupboard Staple", "Home Style", "Slow Cooked", "Signature Recipe",
        "Traditional",
        "Family", "Quick Cook",
    ),
    "Vinegar": (
        "Aged", "Barrel Aged", "Unfiltered", "Naturally Brewed", "Slow Fermented", "Traditional",
        "Small Batch", "Oak Aged",
    ),
    "World Food": (
        "Street Style", "Restaurant Style", "Slow Cooked", "Home Style", "Fragrant",
        "Family Recipe", "Traditional", "Small Batch",
    ),
    "Yogurt": (
        "Greek Style", "Thick & Creamy", "Smooth & Creamy", "Rich & Creamy", "Extra Creamy",
        "Bio Live", "Strained", "Farmhouse", "Icelandic Style", "French Set", "Pot Set", "Luxury",
        "Swiss Style", "Whipped", "Lightly Set", "Indulgent",
    ),
}  # fmt: skip
SUBS = tuple(dict.fromkeys(word for row in STYLES.values() for word in row))
NUMBERS = ()
#: The lead word alone is a model ("Finest Strawberry Jam"), the decoy-friendly short title.
BARE = True
#: The title leads with its brand in two of three draws (``line_grammar.brand_led``).
MIXED_BRAND = True
