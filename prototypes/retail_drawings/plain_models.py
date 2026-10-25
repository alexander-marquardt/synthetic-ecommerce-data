"""The plain model words of the home, gifts, garden and toys families (gen#664).

A range name such as "Eskshaw" or "Elmfield" leads a title the way a brand does, so a shopper
reads it as a second brand (gen#662). Public retail listings of lamps, sofas, towels, mugs, toys
and the rest name a model from a plain word, then a number, a sub-model or a code, then the kind:
"Beam 300 Fabric Shade Floor Lamp", "Cloud Plus 3 Cotton Bath Towel", "Wonder 4 Wooden Tow Truck".
The brand leads the title and the model follows it (:func:`line_grammar.retitle`).

Each family below has its own lead words, so one word is never a model of two families. A lead
word is a plain English word, not a coined brand-sounding one and not a name or a place:
``tests/test_retail_scale.py`` holds the vocabularies off the brand names, the first names of
:data:`line_grammar.NAME_WORDS` and the invented place words of :mod:`range_ownership`. A family's
lead words are dealt over the brands that sell it (:class:`line_grammar.Deal`), so a lead word
belongs to one brand (gen#642).

A model is a lead word, an optional sub-model word and a number: "Beam 300", "Cloud Plus 3".
"""

from __future__ import annotations

#: family -> the product types it names.
KINDS = {
    "lighting": (
        "Lampshade", "Ceiling Light", "Floor Lamp", "Table Lamp", "Wall Light", "Desk Lamp",
        "Night Light", "Light Bulb",
    ),
    "furniture": (
        "Sofa", "Corner Sofa", "Chaise Sofa", "Modular Sofa", "Recliner Sofa", "Sofa Bed",
        "Armchair", "Footstool", "Bed", "Dining Table", "Side Table", "Coffee Table",
        "Dining Chair", "Bookcase", "Wardrobe", "Chest of Drawers", "Hallway Stands", "Chairbed",
        "Mirror",
    ),
    "soft": (
        "Cushion", "Throws", "Baby Blanket", "Towel", "Beach Towel", "Tea Towels", "Duvet",
        "Duvet Cover", "Duvet Set", "Pillow", "Pillowcase", "Mattress Protector",
        "Mattress Topper", "Mattress", "Pillow Protector", "Valances", "Sofa Covers", "Apron",
        "Changing Mat",
    ),
    "tableware": (
        "Plate", "Bowl", "Mug", "Cup", "Cup Set", "Cutlery", "Cutlery Set", "Dinner Set",
        "Glassware", "Tumbler", "Travel Cup", "Measuring Cup", "Paper Cup", "Party Cup",
        "Sippy Cup", "Baby Beakers", "Casserole Dish", "Storage Jar", "Lunch Box",
    ),
    "kitchen": (
        "Kitchen Utensil", "Kitchen Knife", "Chopping Board", "Colander", "Saucepan",
        "Frying Pan", "Kettle", "Toaster", "Kitchen Scales", "Kitchen Bin", "Kitchen Roll",
        "Cupcake Cases",
    ),
    "storage": (
        "Storage Basket", "Storage Boxes", "Storage Box", "Garment Bags", "Hanger",
        "Clothes Hangers", "Wash Bags", "Nursery Storage", "Laundry Basket", "Drying Racks",
        "Clothes Airer", "Wall Hooks", "Door Stop", "Car Boot Organiser", "Cup Holder",
        "Nappy Caddy", "Money Box",
    ),
    "decor": (
        "Photo Frame", "Decorative Tray", "Clock", "Christmas Decoration", "Ornament",
        "Artificial Flowers", "Scented Candle", "Wallpaper", "Paint", "Trophy", "Fridge Magnets",
    ),
    "gifts": (
        "Keyring", "Gift Bag", "Gift Set", "Gift Hamper", "Gift Card", "Greeting Card",
        "Wrapping Paper", "Notebook", "Diary", "Bouquet",
    ),
    "garden": (
        "Plant", "Bedding Plant", "Bulbs", "Seeds", "Growing Kit", "Christmas Tree", "BBQ",
        "Garden Furniture Set", "Lawn Mower", "Robot Mower", "Grass Trimmer", "Hedge Trimmer",
        "Parasol", "Garden Hose",
    ),
    "tools": (
        "Cordless Drill", "Bit Set", "Screwdriver Set", "Socket Set", "Caulking Gun", "Glue Gun",
        "Jump Leads", "Cable Ties", "Foot Pumps", "Wireless Charger", "Fridge Thermometer",
        "Heater", "Desk Fan", "Pedestal Fan", "Tower Fan", "Ceiling Fan", "Handheld Fan",
    ),
    "toys": (
        "Doll", "Soft Toy", "Toy Figure", "Toy Vehicle", "Bath Toy", "Building Set",
        "Jigsaw Puzzle", "Wooden Toy", "Role Play Toy", "Arts and Crafts Kit", "Ride-On Toy",
        "Card Game", "Board Game", "Kite", "Marble Run", "Dolls' House", "Play Kitchen",
        "Water Gun",
    ),
}  # fmt: skip

#: family -> its lead words: plain words, none shared with another family.
LEADS = {
    "lighting": (
        "Glow", "Beam", "Halo", "Lumen", "Spark", "Bright", "Gleam", "Flare", "Shimmer", "Shine",
        "Dusk", "Morning", "Kindle", "Aura", "Glint", "Lustre", "Sheen", "Flicker", "Twilight",
        "Radiant",
    ),
    "furniture": (
        "Settle", "Classic", "Modern", "Tradition", "Essential", "Signature", "Premier", "Relax",
        "Urban", "Heart", "Form", "Simple", "Easy", "Style", "Daily", "Retreat", "Habit", "Ease",
        "Basic", "Select",
    ),
    "soft": (
        "Cloud", "Restful", "Snug", "Cosy", "Dream", "Drift", "Feather", "Nap", "Rest", "Hush",
        "Lull", "Slumber", "Doze", "Cuddle", "Tender", "Gentle", "Fluff", "Haze", "Calm",
        "Lounge",
    ),
    "tableware": (
        "Supper", "Feast", "Brunch", "Banquet", "Serve", "Dine", "Savour", "Relish", "Gather",
        "Toast", "Buffet", "Picnic", "Dessert", "Starter", "Platter", "Sip", "Taste", "Entertain",
        "Everyday", "Spread",
    ),
    "kitchen": (
        "Chef", "Cook", "Bake", "Simmer", "Whisk", "Sizzle", "Stir", "Roast", "Larder", "Prep",
        "Galley", "Brew", "Steam", "Poach", "Braise", "Saute", "Knead", "Zest", "Spice", "Season",
    ),
    "storage": (
        "Tidy", "Stow", "Neat", "Order", "Stack", "Tuck", "Sort", "Keep", "Fold", "Hold", "Haul",
        "Carry", "Shelve", "Clear", "Space", "Nook", "Cache", "Locker", "Handy", "Utility",
    ),
    "decor": (
        "Accent", "Display", "Treasure", "Memory", "Moment", "Charm", "Trinket", "Keepsake",
        "Festive", "Sparkle", "Merry", "Jolly", "Cheer", "Glee", "Fable", "Delight", "Tidings",
        "Yule", "Decor", "Showcase",
    ),
    "gifts": (
        "Present", "Surprise", "Token", "Treat", "Wish", "Greeting", "Regards", "Thanks",
        "Blessing", "Occasion", "Celebrate", "Party", "Parcel", "Ribbon", "Jubilee", "Milestone",
        "Gesture", "Wrap", "Offering", "Hello",
    ),
    "garden": (
        "Border", "Patio", "Meadow", "Bloom", "Blossom", "Sprout", "Harvest", "Wildflower",
        "Trellis", "Terrace", "Hedgerow", "Verge", "Plot", "Pasture", "Grow", "Seedling", "Sunlit",
        "Cottage", "Allotment", "Potting",
    ),
    "tools": (
        "Torque", "Grip", "Drive", "Anvil", "Lever", "Gear", "Crank", "Pivot", "Ratchet", "Forge",
        "Workshop", "Bench", "Rivet", "Power", "Volt", "Amp", "Watt", "Dynamo", "Breeze", "Gust",
    ),
    "toys": (
        "Fun", "Giggle", "Wonder", "Romp", "Skip", "Leap", "Whizz", "Zoom", "Tumble", "Frolic",
        "Bounce", "Caper", "Wobble", "Squeak", "Splash", "Imagine", "Pretend", "Explore",
        "Discover", "Adventure",
    ),
}  # fmt: skip

#: The sub-model word that may follow a lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")

#: The numbers a model may carry: a series for hard goods, a generation for soft ones. A kitchen
#: code is lettered ("K16") so that no count noun after it reads as a count ("16 Color Coded").
SERIES = (200, 300, 400, 500, 600, 700, 800, 900)
GENERATIONS = tuple(range(2, 10))
NUMBERS = {
    "lighting": SERIES,
    "furniture": (210, 220, 230, 240, 310, 320, 330, 340),
    "tools": (10, 20, 30, 40, 50, 60, 70, 80),
    "kitchen": ("K11", "K12", "K13", "K14", "K15", "K16", "K17", "K18"),
}


def numbers(fam: str) -> tuple[int | str, ...]:
    """The numbers a model of ``fam`` may carry."""
    return NUMBERS.get(fam, GENERATIONS)
