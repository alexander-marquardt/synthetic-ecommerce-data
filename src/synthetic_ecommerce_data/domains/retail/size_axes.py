"""Which SKU key is a product type's size: the declaration :mod:`size_ladder` reads (gen#719).

A type's SKUs can differ by many keys, and only some of them make the item bigger or smaller.
:data:`AXES` names them per type, in the order they are read: :func:`size_ladder.primary` takes
the first one that varies within the product, so a saucepan sold by capacity ranks by capacity
and a curtain sold in widths and drops ranks by its width (its drops share that rung's image).

:data:`NOT_SIZES` is the other half: the keys that vary within a product and are not a size, each
with its reason. ``tests/test_retail_size_axes_719.py`` holds the two to be the whole catalog, so
a new SKU key is refused until it is declared one way or the other.

A bottle is not here: a pack sold by content (``net_volume_ml``, ``net_weight_g``) is drawn by
:mod:`pack_scale`, and a type's axis never overlaps it, or a size would shrink twice.
"""

from __future__ import annotations

#: The SKU keys that carry a garment's or a shoe's size, in the order they are tried.
GARMENT_KEYS = ("waist", "size_uk", "size")

#: The clothing and footwear types, every one sized by :data:`GARMENT_KEYS` (gen#339).
GARMENT_TYPES = (
    "All-in-One", "Ankle Boots", "Baby Bodysuit", "Ballet Pumps", "Barefoot Shoes",
    "Bikini Bottoms", "Bikini Top", "Block Heels", "Blouse", "Bodysuit", "Bolero", "Bomber Jacket",
    "Boxers", "Boys Suit", "Bra", "Brogues", "Cardigan", "Changing Robe", "Chelsea Boots",
    "Chukka Boots", "Clogs", "Co-ord Set", "Coat", "Court Shoes", "Cover-Up", "Cycling Shorts",
    "Denim Jacket", "Dinner Suit", "Dress", "Dressing Gown", "Espadrilles", "Gilet", "Hoodie",
    "Jacket", "Jeans", "Jelly Shoes", "Joggers", "Jumper", "Kids Swimsuit", "Kitten Heels",
    "Knee High Boots", "Knickers", "Knitted Top", "Leggings", "Loafers", "Mens Trousers", "Mules",
    "Parka", "Peacoat", "Period Pants", "Period Swimwear", "Platform Trainers", "Plimsolls",
    "Polo Shirt", "Puddlesuit", "Puffer Jacket", "Pyjamas", "Raincoat", "Running Shoes",
    "Safety Boots", "Sandals", "School Pinafore", "School Shirt", "School Shoes", "School Skirt",
    "School Trousers", "Shacket", "Shapewear", "Shirt", "Shorts", "Skirt", "Sleepsuit", "Slip",
    "Slippers", "Snowsuit", "Socks", "Suit Jacket", "Suit Trousers", "Sweatshirt", "Swim Shorts",
    "Swimsuit", "T-Shirt", "Tankini", "Tea Dress", "Tee", "Tights", "Top", "Tracksuit", "Trainers",
    "Trench Coat", "Trouser Suit", "Trousers", "Utility Jacket", "Vest", "Waistcoat",
    "Walking Boots", "Wedges", "Wellies", "Windbreaker",
)  # fmt: skip

#: ``product type -> its size axis``, the keys in the order they are read.
AXES: dict[str, tuple[str, ...]] = {
    **dict.fromkeys(GARMENT_TYPES, GARMENT_KEYS),
    # Worn, outside clothing and footwear.
    "Baseball Glove": ("glove_size_in",),
    "Batting Helmet": ("head_cm",),
    "Belt": ("waist_in",),
    "Bike Helmet": ("size",),
    "Bracelet": ("size",),
    "Gloves": ("glove_size_letter",),
    "Hat": ("hat_size",),
    "Necklace": ("length_cm",),
    "Ring": ("ring_size_us", "ring_size_uk"),
    "Analog Watch": ("case_mm",),
    "Digital Watch": ("case_mm",),
    "Fitness Band": ("case_mm",),
    # Bicycles and sports.
    "Bicycle": ("frame_cm", "wheel_size_in"),
    "Ride-On Toy": ("wheel_size_in",),
    "Baseball Bat": ("length_cm",),
    "Dumbbell": ("weight_kg",),
    "Foam Roller": ("length_cm",),
    "Football": ("ball_size",),
    "Kayak": ("length_cm",),
    "Kettlebell": ("weight_kg",),
    "Kickboard": ("length_cm",),
    "Roll Mat": ("thickness_mm",),
    "Skateboard": ("deck_width_in",),
    "Sleeping Bag": ("length_cm",),
    "Tent": ("berth",),
    "Yoga Block": ("height_cm",),
    "Yoga Mat": ("thickness_mm",),
    "Yoga Strap": ("length_cm",),
    # What holds: a volume or a capacity.
    "Backpack": ("capacity_l",),
    "Casserole Dish": ("capacity_l",),
    "Holdall": ("capacity_l",),
    "Kettle": ("capacity_l",),
    "Kitchen Bin": ("capacity_l",),
    "Saucepan": ("capacity_l", "diameter_cm"),
    "Storage Box": ("capacity_l",),
    "Storage Jar": ("size",),
    "Suitcase": ("capacity_l", "weight_kg"),
    # Bags and baskets sold by a word.
    "Gift Bag": ("size", "dimensions"),
    "Handbag": ("size",),
    "Scented Candle": ("size",),
    "Storage Basket": ("size",),
    # Bedding: by bed size, or the cover's own dimensions.
    "Bed": ("bed_size", "width_cm", "length_cm"),
    "Duvet": ("size_eu", "size_uk"),
    "Duvet Cover": ("bed_size", "size_eu", "size_uk"),
    "Mattress": ("bed_size",),
    "Mattress Protector": ("bed_size", "size_eu", "size_uk"),
    "Mattress Topper": ("bed_size", "size_eu", "size_uk"),
    "Pillow": ("size_eu", "size_uk"),
    "Pillowcase": ("size_eu", "size_uk"),
    "Sofa Bed": ("bed_size",),
    # Rugs, towels and what else is sold by its dimensions.
    "Bath Mat": ("width_cm", "length_cm"),
    "Blind": ("width_cm",),
    "Chopping Board": ("dimensions",),
    "Curtains": ("width_cm", "drop_cm"),
    "Cushion": ("size",),
    "Photo Frame": ("size",),
    "Picnic Blanket": ("dimensions",),
    "Rug": ("width_cm", "diameter_cm", "length_cm"),
    "Shower Curtain": ("drop_cm",),
    "Throws": ("width_cm", "length_cm"),
    "Towel": ("size",),
    "Wallpaper": ("roll_length_m",),
    # Furniture and what stands in a room.
    "Artificial Flowers": ("height_cm",),
    "Bookcase": ("height_cm", "size"),
    "Christmas Tree": ("height",),
    "Clock": ("diameter_cm",),
    "Decorative Tray": ("diameter_cm", "length_cm"),
    "Dining Table": ("width_cm", "length_cm", "size"),
    "Mirror": ("height_cm", "width_cm", "size"),
    "Plant": ("size",),
    # Tools, cables and machines by what they cut or reach.
    "BBQ": ("diameter_cm", "length_cm"),
    "Cable": ("length_m",),
    "Ceiling Fan": ("blade_span_cm",),
    "Desk Fan": ("blade_size_in",),
    "Frying Pan": ("diameter_cm",),
    "Garden Hose": ("length_m",),
    "Grass Trimmer": ("cutting_width_cm",),
    "Hedge Trimmer": ("blade_length_cm",),
    "Kitchen Knife": ("blade_length_cm",),
    "Lawn Mower": ("cutting_width_cm",),
    "Parasol": ("canopy_m",),
    "Umbrella": ("canopy_cm",),
    # Screens.
    "Laptop Sleeve": ("screen_size_in",),
    "Monitor": ("screen_size_in",),
    "TV": ("screen_size_in",),
}

#: The SKU keys that vary within a product and are not its size, and why.
NOT_SIZES: dict[str, str] = {
    "brightness_lm": "a rating",
    "cup_size": "a fit",
    "edition": "a kind of game",
    "fin_count": "the heater's drawing reads it",
    "finish": "a color",
    "fit_length": "a fit",
    "flavor": "a kind",
    "grip": "a fit: the racket is no bigger",
    "house_style": "a color",
    "inside_leg": "a fit",
    "inside_leg_in": "a fit",
    "lawn_area_m2": "a rating",
    "length": "a fit",
    "luggage_size": "the word for the capacity that ranks the suitcase",
    "max_load_kg": "a rating",
    "metal": "a material",
    "model_number": "an identifier",
    "net_volume_ml": "a pack's content: pack_scale",
    "net_weight_g": "a pack's content: pack_scale",
    "pack_size": "a pack: pack_scale and pack_copies",
    "piece_count": "a count",
    "ram_gb": "a rating",
    "recline": "a kind",
    "resistance": "a rating",
    "scent": "a kind",
    "seats": "the set's drawing reads it",
    "shade_color": "a color",
    "size_eu": "the same shoe's other chart",
    "size_us": "the same shoe's other chart",
    "slots": "the toaster's drawing reads it",
    "sold_as": "a kind",
    "spf": "a rating",
    "storage_gb": "a rating",
    "theme": "a kind",
    "units_per_pack": "a pack: pack_scale and pack_copies",
    "upper_material": "a material",
    "wattage": "a rating",
    "width": "a shoe's fit",
}

#: The types whose drawing reads the size itself, so its sizes already differ (gen#197).
DRAWN_TO_SIZE = {"Lampshade": "diameter_cm"}
#: The types whose ``size`` value is a pack's weight (``400 g``), so a pack and not an axis.
PACK_SIZED = ("Crisps", "Fresh Fruit", "Pasta", "Pickle")
