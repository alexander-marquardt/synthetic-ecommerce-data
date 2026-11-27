"""What the writer names, sizes and prices a picture's product by: the generator's own words (gen#1022).

Every word of a title or a description comes from here, the brand book (``house_styles``) or a
number the writer measured, so no text reaches a product from anywhere else. The brands are the
furniture brands that already have a house style; each has its own ranges, and a range belongs to
one brand. The measured ranges are realistic sizes for the type, in centimeters.

Every type the manifest names (``picture_manifest.TYPES``, all that ``drawings`` draws) has an
entry, so a picture of any drawn type makes a product (gen#1093). A type's department is the top
of its path, as the issue's 2026-11-21 table files it: Home, Hardware (faucet, pull, tile), Garden
(statue, fountain) or Office & School (office chair).
"""

from __future__ import annotations

from dataclasses import dataclass

# ruff: noqa: E501 -- the tables read better whole than wrapped.


@dataclass(frozen=True)
class TypeBook:
    """How one type's products are named, filed, sized and priced."""

    #: The product type, and the title's last words (a dict picks them by a part's value).
    noun: str | tuple[str, dict[str, str]]
    product_type: str
    path: tuple[str, ...]
    #: Realistic (least, most) width, height and depth in centimeters.
    width: tuple[int, int]
    height: tuple[int, int]
    depth: tuple[int, int]
    #: The price of a mid-sized piece, in GBP.
    price: float


_FURN = ("Home", "Furniture")
_OFFICE = (*_FURN, "Office Furniture")
_STORE = ("Home", "Storage")
_SOFT = ("Home", "Soft Furnishings")
_DECOR = ("Home", "Decor")
_BATH = ("Home", "Bathroom")
_LIGHT = ("Home", "Lighting")
_KITCHEN = ("Home", "Kitchen")
_HARDWARE = ("Home", "DIY & Tools")
_GARDEN = ("Garden", "Garden Decor")

TYPES: dict[str, TypeBook] = {
    "sideboard": TypeBook("Sideboard", "Sideboard", (*_FURN, "Sideboards"), (90, 200), (65, 95), (35, 50), 349.0),
    "bar_cabinet": TypeBook("Drinks Cabinet", "Drinks Cabinet", (*_FURN, "Drinks Cabinets"), (60, 120), (90, 180), (35, 55), 299.0),
    "storage_cabinet": TypeBook("Storage Cabinet", "Storage Cabinet", (*_OFFICE, "Storage Cabinets"), (60, 100), (100, 200), (35, 50), 249.0),
    "shoe_storage": TypeBook(("form", {"rack": "Shoe Rack", "bench": "Shoe Storage Bench"}), "Shoe Storage", (*_STORE, "Shoe Storage"), (50, 120), (40, 110), (25, 40), 89.0),
    "wall_shelf": TypeBook("Wall Shelf", "Wall Shelf", (*_STORE, "Wall Shelves"), (40, 120), (15, 80), (15, 30), 39.0),
    "bar_stool": TypeBook("Bar Stool", "Bar Stool", (*_FURN, "Bar Stools"), (35, 50), (75, 115), (35, 50), 79.0),
    "desk": TypeBook("Desk", "Desk", (*_OFFICE, "Desks"), (90, 180), (72, 78), (50, 80), 199.0),
    "office_chair": TypeBook("Office Chair", "Office Chair", ("Office & School", "Office Furniture", "Office Chairs"), (55, 70), (90, 130), (55, 70), 149.0),
    "tv_stand": TypeBook("Media Unit", "TV Unit", (*_FURN, "Media Units"), (100, 200), (40, 65), (35, 50), 179.0),
    "kitchen_island": TypeBook("Kitchen Island", "Kitchen Island", (*_FURN, "Kitchen Islands"), (90, 180), (85, 95), (60, 100), 449.0),
    # gen#1093: the other drawn types, so every picture of the WANDS persona makes a product.
    "bookcase": TypeBook(("style", {"standard": "Bookcase", "ladder": "Ladder Bookcase", "cube": "Cube Bookcase", "glass_door": "Glass Door Bookcase"}), "Bookcase", (*_FURN, "Bookcases"), (40, 120), (80, 220), (25, 40), 149.0),
    "wardrobe": TypeBook("Wardrobe", "Wardrobe", (*_FURN, "Wardrobes"), (80, 250), (170, 240), (50, 65), 499.0),
    "chest_of_drawers": TypeBook("Chest of Drawers", "Chest of Drawers", (*_FURN, "Chests of Drawers"), (40, 160), (60, 140), (35, 55), 229.0),
    "sofa": TypeBook("Sofa", "Sofa", (*_FURN, "Sofas"), (150, 300), (75, 100), (80, 105), 699.0),
    "bench": TypeBook("Bench", "Bench", (*_FURN, "Benches"), (80, 160), (40, 90), (30, 50), 129.0),
    "rug": TypeBook(("form", {"rectangle": "Rug", "round": "Round Rug", "runner": "Runner Rug", "doormat": "Doormat", "kitchen_mat": "Kitchen Mat"}), "Rug", (*_SOFT, "Rugs"), (40, 300), (1, 4), (40, 240), 129.0),
    "wall_art": TypeBook("Wall Art", "Wall Art", (*_DECOR, "Wall Art"), (30, 150), (30, 120), (2, 5), 79.0),
    "decor_object": TypeBook(("form", {"sculpture": "Sculpture", "bowl": "Decorative Bowl", "lantern": "Lantern", "box": "Decorative Box"}), "Decorative Accessory", (*_DECOR, "Decorative Accessories"), (10, 50), (8, 60), (8, 40), 29.0),
    "faux_floral": TypeBook(("form", {"arrangement": "Faux Flower Arrangement", "wreath": "Faux Wreath", "topiary": "Faux Topiary", "tree": "Faux Tree"}), "Artificial Flowers", ("Home", "Home Accessories", "Artificial Flowers"), (20, 120), (25, 180), (15, 120), 39.0),
    "canister": TypeBook(("count", {"1": "Storage Canister", "2": "Canister Set", "3": "Canister Set", "4": "Canister Set"}), "Storage Canister", (*_KITCHEN, "Canisters"), (10, 60), (10, 30), (8, 15), 25.0),
    "vanity": TypeBook("Vanity Unit", "Vanity Unit", (*_BATH, "Vanity Units"), (50, 150), (45, 90), (35, 55), 349.0),
    "bath_storage": TypeBook(("form", {"tower": "Bathroom Storage Tower", "over_toilet": "Over Toilet Storage", "wall": "Bathroom Wall Cabinet"}), "Bathroom Storage", (*_BATH, "Bathroom Storage"), (25, 70), (50, 180), (15, 35), 89.0),
    "vanity_light": TypeBook("Vanity Light", "Vanity Light", (*_LIGHT, "Lights", "Vanity Lights"), (20, 120), (10, 30), (10, 25), 69.0),
    "sink_faucet": TypeBook("Sink Faucet", "Faucet", (*_HARDWARE, "Faucets"), (10, 30), (15, 45), (10, 30), 89.0),
    "cabinet_pull": TypeBook(("style", {"bar": "Bar Pull", "cup": "Cup Pull", "knob": "Cabinet Knob", "ring": "Ring Pull", "edge": "Edge Pull"}), "Cabinet Hardware", (*_HARDWARE, "Cabinet Pulls & Knobs"), (2, 35), (1, 6), (1, 4), 9.0),
    "tile": TypeBook(("form", {"square": "Square Tile", "subway": "Subway Tile", "hexagon": "Hexagon Tile"}), "Tile", (*_HARDWARE, "Wall & Floor Tiles"), (7, 60), (7, 60), (1, 2), 9.0),
    "garden_statue": TypeBook(("form", {"animal": "Animal Statue", "figure": "Figure Statue", "sphere": "Garden Sphere", "obelisk": "Garden Obelisk"}), "Garden Statue", (*_GARDEN, "Garden Statues"), (15, 80), (20, 150), (15, 60), 79.0),
    "fountain": TypeBook(("form", {"tiered": "Garden Fountain", "wall": "Wall Fountain", "tabletop": "Tabletop Fountain"}), "Water Feature", (*_GARDEN, "Fountains"), (25, 120), (25, 180), (15, 120), 199.0),
}  # fmt: skip

#: Each furniture brand with a house style, and its own ranges (invented place-like names).
RANGES: dict[str, tuple[str, ...]] = {
    "Brackenmere Home": ("Ashdene", "Fernleigh", "Brindlewick"),
    "Larchwood Living": ("Copperdene", "Marrowby", "Saltrigg"),
    "Emberly Home": ("Wendlecote", "Orrinvale", "Tamblehurst"),
    "Cobble & Kiln": ("Quarrendon", "Pellowmere", "Stagsby"),
}

#: A count part's word in a title and a description: (singular, plural). A type may name a
#: count its own way (a wall shelf's boards are its tiers).
COUNTS: dict[str, tuple[str, str]] = {
    "doors": ("Door", "doors"),
    "drawers": ("Drawer", "drawers"),
    "shelves": ("Shelf", "shelves"),
    "tiers": ("Tier", "tiers"),
    "stools": ("Stool", "stools"),
    "sinks": ("Sink", "sinks"),
    "handles": ("Handle", "handles"),
    "count": ("Piece", "pieces"),
    "panels": ("Panel", "panels"),
    "pieces": ("Piece", "pieces"),
    "basins": ("Basin", "basins"),
    "lights": ("Light", "lights"),
}
COUNTS_OF: dict[tuple[str, str], tuple[str, str]] = {
    ("wall_shelf", "shelves"): ("Tier", "shelves"),
    ("canister", "count"): ("Canister", "canisters"),
}
#: The counts a title leaves to the description (a drinks cabinet's stools are a set's, not its own).
UNTITLED_COUNTS = {
    ("bar_cabinet", "stools"),
    ("vanity", "doors"),
    ("vanity", "drawers"),
    ("decor_object", "pieces"),
}

#: The title words of a part's value; a value not listed adds no title word. A count listed here
#: is worded by this table, not as its number and noun.
TITLE_WORDS: dict[tuple[str, str], dict[str, str]] = {
    ("bar_stool", "seat_height"): {"counter": "Counter Height", "bar": "Bar Height"},
    ("bar_stool", "back"): {"none": "Backless", "low": "Low Back"},
    ("desk", "outline"): {"l_shaped": "L-Shaped"},
    ("office_chair", "back"): {"mid": "Mid Back", "high": "High Back"},
    ("office_chair", "cover"): {"mesh": "Mesh", "fabric": "Fabric"},
    ("storage_cabinet", "front"): {"glass": "Glass Door"},
    ("wall_shelf", "mount"): {"floating": "Floating", "bracket": "Bracket", "rail": "Rail"},
    ("kitchen_island", "wheels"): {"yes": "Rolling"},
    ("wardrobe", "mirrored"): {"yes": "Mirrored"},
    ("wardrobe", "door"): {"sliding": "Sliding"},
    ("chest_of_drawers", "form"): {"tall": "Tall", "wide": "Wide"},
    ("bench", "seat"): {"upholstered": "Upholstered", "wood": "Wooden"},
    ("bench", "storage"): {"shelf": "Storage", "drawers": "Storage"},
    ("rug", "pile"): {"shag": "Shaggy", "flat": "Flatweave"},
    ("rug", "motif"): {"road": "Road Map", "hopscotch": "Hopscotch", "stars": "Star"},
    ("wall_art", "panels"): {"2": "2 Piece", "3": "3 Piece"},
    ("wall_art", "subject"): {
        "abstract": "Abstract",
        "landscape": "Landscape",
        "botanical": "Botanical",
        "geometric": "Geometric",
    },
    ("wall_art", "frame"): {"canvas": "Canvas", "thin": "Framed", "wide": "Framed"},
    ("decor_object", "material"): {
        "ceramic": "Ceramic",
        "metal": "Metal",
        "wood": "Wooden",
        "glass": "Glass",
    },
    ("faux_floral", "bloom"): {"berry": "Berry"},
    ("canister", "count"): {"2": "2 Piece", "3": "3 Piece", "4": "4 Piece"},
    ("canister", "body"): {"ceramic": "Ceramic", "glass": "Glass", "metal": "Metal"},
    ("vanity", "sinks"): {"1": "Single Sink", "2": "Double Sink"},
    ("vanity", "mount"): {"wall": "Wall Hung"},
    ("bath_storage", "cabinet"): {"mirror": "Mirrored"},
    ("vanity_light", "shade"): {"cone": "Cone", "drum": "Drum", "globe": "Globe"},
    ("vanity_light", "finish"): {
        "brass": "Brass",
        "antique brass": "Antique Brass",
        "chrome": "Chrome",
        "satin nickel": "Satin Nickel",
        "matte black": "Matte Black",
        "copper": "Copper",
        "oak": "Oak",
        "walnut": "Walnut",
        "matte white": "Matte White",
    },
    ("sink_faucet", "handles"): {"1": "Single Handle", "2": "Two Handle"},
    ("sink_faucet", "spout"): {"arc": "High Arc", "waterfall": "Waterfall"},
    ("sink_faucet", "mount"): {"wall": "Wall Mount"},
    ("cabinet_pull", "backplate"): {"yes": "Backplate"},
    ("tile", "pattern"): {"veined": "Veined", "motif": "Patterned"},
    ("tile", "surface"): {"matte": "Matte", "gloss": "Gloss"},
    ("garden_statue", "material"): {"stone": "Stone", "metal": "Metal", "resin": "Resin"},
    ("fountain", "basins"): {"2": "2 Tier", "3": "3 Tier"},
    ("fountain", "material"): {"stone": "Stone", "metal": "Metal", "resin": "Resin"},
}

#: A part's attribute name and description words, where the param name does not read well alone.
NAMES: dict[str, str] = {
    "glass_rack": "Glass rack",
    "seat": "Seat shape",
    "top": "Worktop",
    "size": "Pull size",
    "seat_height": "Stool height",
    "layout": "Shelf layout",
}
#: A count's display name where the catalog already names the concept (a light count is the
#: lighting rows' "Number of lights", under the same ``light_count`` key).
COUNT_NAMES: dict[str, str] = {"lights": "Number of lights"}

#: A part's attribute key, where the param name would collide with a key the catalog already
#: gives another meaning (``size`` is a SKU's size option, gen#1093).
#: A stool's counter or bar seat is a class, not a measure: ``item_height`` is the one height key.
KEYS: dict[str, str] = {"size": "pull_size", "seat_height": "stool_class"}
