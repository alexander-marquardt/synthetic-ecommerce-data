"""What the writer names, sizes and prices a picture's product by: the generator's own words (gen#1022).

Every word of a title or a description comes from here, the brand book (``house_styles``) or a
number the writer measured, so no text reaches a product from anywhere else. The brands are the
furniture brands that already have a house style; each has its own ranges, and a range belongs to
one brand. The measured ranges are realistic sizes for the type, in centimeters.
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

TYPES: dict[str, TypeBook] = {
    "sideboard": TypeBook("Sideboard", "Sideboard", (*_FURN, "Sideboards"), (90, 200), (65, 95), (35, 50), 349.0),
    "bar_cabinet": TypeBook("Drinks Cabinet", "Drinks Cabinet", (*_FURN, "Drinks Cabinets"), (60, 120), (90, 180), (35, 55), 299.0),
    "storage_cabinet": TypeBook("Storage Cabinet", "Storage Cabinet", (*_OFFICE, "Storage Cabinets"), (60, 100), (100, 200), (35, 50), 249.0),
    "shoe_storage": TypeBook(("form", {"rack": "Shoe Rack", "bench": "Shoe Storage Bench"}), "Shoe Storage", (*_STORE, "Shoe Storage"), (50, 120), (40, 110), (25, 40), 89.0),
    "wall_shelf": TypeBook("Wall Shelf", "Wall Shelf", (*_STORE, "Wall Shelves"), (40, 120), (15, 80), (15, 30), 39.0),
    "bar_stool": TypeBook("Bar Stool", "Bar Stool", (*_FURN, "Bar Stools"), (35, 50), (75, 115), (35, 50), 79.0),
    "desk": TypeBook("Desk", "Desk", (*_OFFICE, "Desks"), (90, 180), (72, 78), (50, 80), 199.0),
    "office_chair": TypeBook("Office Chair", "Office Chair", (*_OFFICE, "Office Chairs"), (55, 70), (90, 130), (55, 70), 149.0),
    "tv_stand": TypeBook("TV Unit", "TV Unit", (*_FURN, "TV Units"), (100, 200), (40, 65), (35, 50), 179.0),
    "kitchen_island": TypeBook("Kitchen Island", "Kitchen Island", (*_FURN, "Kitchen Islands"), (90, 180), (85, 95), (60, 100), 449.0),
}  # fmt: skip

#: Each furniture brand with a house style, and its own ranges (invented place-like names).
RANGES: dict[str, tuple[str, ...]] = {
    "Brackenmere Home": ("Ashcombe", "Fernleigh", "Brindlewick"),
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
}
COUNTS_OF: dict[tuple[str, str], tuple[str, str]] = {("wall_shelf", "shelves"): ("Tier", "shelves")}
#: The counts a title leaves to the description (a drinks cabinet's stools are a set's, not its own).
UNTITLED_COUNTS = {("bar_cabinet", "stools")}

#: The title words of a word part's value; a value not listed adds no title word.
TITLE_WORDS: dict[tuple[str, str], dict[str, str]] = {
    ("bar_stool", "seat_height"): {"counter": "Counter Height", "bar": "Bar Height"},
    ("bar_stool", "back"): {"none": "Backless", "low": "Low Back"},
    ("desk", "outline"): {"l_shaped": "L-Shaped"},
    ("office_chair", "back"): {"mid": "Mid Back", "high": "High Back"},
    ("office_chair", "cover"): {"mesh": "Mesh", "fabric": "Fabric"},
    ("storage_cabinet", "front"): {"glass": "Glass Door"},
    ("wall_shelf", "mount"): {"floating": "Floating", "bracket": "Bracket", "rail": "Rail"},
    ("kitchen_island", "wheels"): {"yes": "Rolling"},
}

#: A part's attribute name and description words, where the param name does not read well alone.
NAMES: dict[str, str] = {"glass_rack": "Glass rack", "seat": "Seat shape", "top": "Worktop"}
