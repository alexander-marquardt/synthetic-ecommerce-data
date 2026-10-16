"""Furniture for the rest of the house (gen#199): dining tables and chairs, coffee and side
tables, bookcases, wardrobes, chests of drawers and mirrors (data only).

Beyond a sofa and its beds, the retail catalog had no furniture, so a search by room, material,
size or finish had no range to land on. Each type here is a leaf of its own (under
``Home/Furniture``, a mirror under ``Home/Home Accessories``), typed by its name, with at least
three styles from at least three brands, and draws with its own shape in :mod:`kit_furniture`.

What changes a piece's picture is a style, not a SKU (one image per style and colorway): a
table's top outline and seat count, a chair's style, a bookcase's shelves, a wardrobe's doors and
mirror, a chest's drawers and a mirror's outline and kind are each a drawing param of the
style, and a structured attribute beside it. What does not change the picture is a SKU axis:
a table's or a mirror's size (with its ``width_cm``, ``length_cm`` or ``height_cm``), a
bookcase's height (its ``size``, with its ``height_cm``: ``height`` holds the trees' feet, a
measured value) and a chair's pack (with its ``units_per_pack``).

:func:`breadth_rows.docs` takes these rows after its own, so every scaled build carries them;
:func:`scale.derivable` leaves them out, as it does the shirts, so the seeded derivation (and
every product id and image id it makes) is what it was. At the ceiling, Food & Drink sits within
two styles of the fairness floor (``tests/test_retail_scale.py``), and the furniture templates
alone would lift that floor past it.
"""

from __future__ import annotations

from dataclasses import dataclass

import kit_furniture  # noqa: F401 -- registers the furniture shapes
from breadth_rows import Row
from variants import cw

_HOME = "Home"
_FURN = ("Home", "Furniture")
TABLES = (*_FURN, "Tables")
DINING_TABLES = (*TABLES, "Dining Tables")
DINING_CHAIRS = (*_FURN, "Dining Chairs")
COFFEE_TABLES = (*TABLES, "Coffee Tables")
SIDE_TABLES = (*TABLES, "Side Tables")
BOOKCASES = (*_FURN, "Bookcases")
WARDROBES = (*_FURN, "Wardrobes")
CHESTS = (*_FURN, "Chests of Drawers")
MIRRORS = ("Home", "Home Accessories", "Mirrors")

# Wood tones and paints are plain color words (``tests/test_retail_color_words.py``): the
# timber is the ``material``, the color is the finish the drawing is painted in.
NATURAL, DARK_BROWN = cw("Natural", "#c9a06a", accent="#7a5a3a"), cw("Dark Brown", "#5e3b25")
WHITE, GREY, BLACK = cw("White", "#f2efe8"), cw("Grey", "#9a9ca0"), cw("Black", "#2b2b2e")
GREEN, NAVY, PINK = cw("Green", "#3f6b4f"), cw("Navy", "#2c3e5c"), cw("Pink", "#e3b2ad")
TAN, GOLD, SILVER = cw("Tan", "#b07a43"), cw("Gold", "#c9a24a"), cw("Silver", "#b9bcc0")
BRUSHED_GOLD = cw("Brushed Gold", "#b8995a")

Size = tuple  # (name, price, ((sku field, value), ...)), see FurnitureRow


@dataclass(frozen=True)
class FurnitureRow(Row):
    """A breadth row whose sizes carry per-SKU fields: ``(name, price, ((field, value), ...))``.

    A table's ``160 x 90 cm`` carries ``width_cm`` 90 and ``length_cm`` 160, a chair set's
    ``4 pack`` its ``units_per_pack`` 4: :mod:`export` writes each as its own variant entry
    (``item_width``, ``units_per_pack``), so a size is a range filter, not only a label.
    """

    def skus(self) -> list[dict]:
        sizes = [{self.size_key: s[0], "price": s[1], **dict(s[2])} for s in self.sizes]
        sizes = sizes or [{"price": self.price}]
        return [{"color": c[0], **s, "in_stock": True} for c in self.colors for s in sizes]


def _yes(v: bool) -> str:
    return "yes" if v else "no"


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    """A count (unit code C62): a facet ranges over it, and a derived style never changes it."""
    return (key, name, str(n), "C62")


def _cm(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "CMT", float(v * 10))  # canonical length is millimeters


def _dims(w: int, h: int) -> tuple[tuple, ...]:
    return (_cm("item_width", "Item width", w), _cm("item_height", "Item height", h))


def _room(v: str) -> tuple[str, str, str]:
    return ("room", "Room", v)


def _mat(v: str) -> tuple[str, str, str]:
    return ("material", "Material", v)


def _table_size(w: int, length: int, price: float) -> Size:
    """A rectangular top ``length x w``; a round or square one is ``w`` across both ways."""
    name = f"{length} x {w} cm" if length != w else f"{w} cm"
    return (name, price, (("width_cm", w), ("length_cm", length)))


def _pack(n: int, price: float) -> Size:
    return ("Single" if n == 1 else f"{n} pack", price, (("units_per_pack", n),))


def _height(h: int, price: float) -> Size:
    return (f"{h} cm", price, (("height_cm", h),))


def _glass(w: int, h: int, price: float) -> Size:
    """A mirror glass ``w`` wide and ``h`` high; a round one is ``w`` across."""
    name = f"{w} x {h} cm" if w != h else f"{w} cm"
    return (name, price, (("width_cm", w), ("height_cm", h)))


# --------------------------------------------------------------------------
# Dining tables: the top's outline and its seat count are drawn
# --------------------------------------------------------------------------


def _table(code, title, brand, shape, seats, extending, top, colors, sizes, text) -> FurnitureRow:
    return FurnitureRow(
        code, title, brand, _HOME, DINING_TABLES, "Dining Table", sizes[0][1], "dining_table",
        text, colors,
        (_count("seat_count", "Seat count", seats), ("shape", "Shape", shape.title()),
         ("extending", "Extending", _yes(extending)), ("top_material", "Top material", top),
         _room("Dining Room")),
        sizes, size_key="size",
        params=(("outline", shape), ("seats", str(seats)), ("extending", _yes(extending)),
                ("top", top.lower().replace("-", "_"))),
    )  # fmt: skip


DINING = (
    _table("DTSQ2", "Square 2 Seater Walnut Dining Table", "Brackenmere Home", "square", 2, False,
           "Walnut", (DARK_BROWN, BLACK), (_table_size(70, 70, 149.0), _table_size(80, 80, 179.0)),
           "A small square table for two in solid walnut, sized for a kitchen corner or a "
           "dining room nook."),
    _table("DTRD4", "Round 4 Seater Oak Dining Table", "Hearth & Table", "round", 4, False,
           "Oak", (NATURAL, DARK_BROWN, WHITE),
           (_table_size(100, 100, 299.0), _table_size(110, 110, 349.0)),
           "A round oak top on a single pedestal, so four chairs tuck in with no leg in the way. "
           "A warm centerpiece for a dining room."),
    _table("DTEX6", "6 Seater Extending Oak Dining Table", "Calderby & Lune", "rectangular", 6,
           True, "Oak", (NATURAL, DARK_BROWN),
           (_table_size(90, 160, 599.0), _table_size(90, 180, 699.0)),
           "A rectangular oak top with a leaf that slides out from the center, for six at "
           "dinner and more when guests come. Made for the dining room."),
    _table("DTOV6", "Oval 6 Seater Glass Top Dining Table", "Lanternby", "oval", 6, False,
           "Glass", (BLACK, NATURAL), (_table_size(100, 180, 449.0),),
           "An oval tempered glass top on two solid legs, light enough to keep a small dining "
           "room open."),
    _table("DTMB8", "Rectangular 8 Seater Marble-Effect Dining Table", "Brackenmere Home",
           "rectangular", 8, True, "Marble-Effect", (WHITE, BLACK),
           (_table_size(100, 200, 799.0), _table_size(100, 240, 949.0)),
           "A long rectangular marble-effect top that extends from 200 cm, seating eight round "
           "a family dining room."),
)  # fmt: skip


# --------------------------------------------------------------------------
# Dining chairs: the style is drawn; a pack of 1, 2 or 4 is a SKU
# --------------------------------------------------------------------------


def _chair(code, title, brand, style, seat, legs, colors, packs, text, count=1) -> FurnitureRow:
    return FurnitureRow(
        code, title, brand, _HOME, DINING_CHAIRS, "Dining Chair", packs[0][1], "dining_chair",
        text, colors,
        (("chair_style", "Chair style", style.title()), ("seat_material", "Seat material", seat),
         ("leg_finish", "Leg finish", legs), _room("Dining Room")),
        packs, size_key="pack_size", params=(("style", style), ("count", str(count))),
    )  # fmt: skip


CHAIRS = (
    _chair("DCUPV", "Velvet Upholstered Dining Chair", "Calderby & Lune", "upholstered",
           "Velvet", "Walnut", (GREEN, NAVY, PINK, GREY),
           (_pack(1, 89.0), _pack(2, 169.0), _pack(4, 319.0)),
           "A fully upholstered velvet seat and back with piped seams, on walnut legs. Sold "
           "single, or as a set of 2 or 4 for the dining room."),
    _chair("DCSPN", "Spindle Back Oak Dining Chair", "Hearth & Table", "spindle", "Oak", "Oak",
           (NATURAL, BLACK, WHITE), (_pack(1, 69.0), _pack(2, 129.0), _pack(4, 249.0)),
           "A farmhouse spindle back in solid oak, with a shaped seat and stretchers between "
           "the legs. Sold single, or as a set of 2 or 4 for the dining room."),
    _chair("DCCNT", "Cantilever Faux Leather Dining Chairs, Set of 2", "Lanternby",
           "cantilever", "Faux Leather", "Chrome", (BLACK, TAN, GREY), (_pack(2, 139.0),),
           "Two cantilever chairs on a single bent chrome frame that gives a little as you sit. "
           "The faux leather wipes clean after dinner in the dining room.", count=2),
    _chair("DCBEN", "Upholstered Dining Bench", "Brackenmere Home", "bench", "Fabric", "Oak",
           (GREY, NATURAL), (_pack(1, 149.0),),
           "A padded fabric bench on oak legs that seats two or three along one side of the "
           "table, and tucks under it after dinner in the dining room."),
)  # fmt: skip


# --------------------------------------------------------------------------
# Coffee tables: the top's outline and its storage are drawn
# --------------------------------------------------------------------------


def _coffee(code, title, brand, shape, storage, mat, colors, price, text, pieces=1) -> FurnitureRow:
    feature = (("storage_feature", "Storage feature", storage.replace("_", "-").title()),) \
        if storage != "none" else ()  # fmt: skip
    count = (_count("piece_count", "Piece count", pieces),) if pieces > 1 else ()
    return FurnitureRow(
        code, title, brand, _HOME, COFFEE_TABLES, "Coffee Table", price, "coffee_table", text,
        colors, (("shape", "Shape", shape.title()), *feature, _mat(mat), *count,
                 _room("Living Room")),
        params=(("outline", shape), ("storage", storage), ("pieces", str(pieces))),
    )  # fmt: skip


COFFEE = (
    _coffee("CTLFT", "Lift-Top Oak Coffee Table with Storage", "Brackenmere Home", "rectangular",
            "lift_top", "Oak", (NATURAL, WHITE), 249.0,
            "A rectangular oak coffee table whose top lifts up and forward to laptop height, "
            "with a storage well beneath it for the living room's remotes and throws."),
    _coffee("CTRSH", "Round Walnut Coffee Table with Shelf", "Calderby & Lune", "round", "shelf",
            "Walnut", (DARK_BROWN, BLACK), 199.0,
            "A round walnut top on four tapered legs, with a shelf below for books and "
            "magazines. A soft edge for a busy living room."),
    _coffee("CTDRW", "Rectangular Pine Coffee Table with Drawer", "Hearth & Table",
            "rectangular", "drawer", "Pine", (WHITE, GREY, GREEN), 159.0,
            "A painted pine coffee table with a full-width drawer for coasters and remotes, "
            "made for the living room."),
    _coffee("CTNST", "Round Oak Nesting Coffee Tables, Set of 2", "Lanternby", "round", "none",
            "Oak", (NATURAL, BLACK), 179.0,
            "Two round oak coffee tables, the smaller tucked under the larger, to pull out when "
            "the living room fills up.", pieces=2),
)  # fmt: skip


# --------------------------------------------------------------------------
# Side tables: the kind (side, bedside, console, nest) and its drawers are drawn
# --------------------------------------------------------------------------

_KIND = {"side": "Side Table", "bedside": "Bedside Table", "console": "Console Table",
         "nest": "Nest of Tables"}  # fmt: skip


def _side(
    code, title, brand, kind, drawers, mat, room, colors, price, text, pieces=1
) -> FurnitureRow:
    extra = (_count("drawer_count", "Drawer count", drawers),) if drawers else ()
    extra += (_count("piece_count", "Piece count", pieces),) if pieces > 1 else ()
    return FurnitureRow(
        code, title, brand, _HOME, SIDE_TABLES, "Side Table", price, "side_table", text, colors,
        (("table_type", "Table type", _KIND[kind]), *extra, _mat(mat), _room(room)),
        params=(("kind", kind), ("drawers", str(drawers))),
    )  # fmt: skip


SIDE = (
    _side("STRND", "Round Oak Side Table", "Lanternby", "side", 0, "Oak", "Living Room",
          (NATURAL, BLACK), 79.0,
          "A small round oak side table on three splayed legs, the right height beside a sofa "
          "in the living room."),
    _side("STBD2", "Pine Bedside Table with 2 Drawers", "Hearth & Table", "bedside", 2, "Pine",
          "Bedroom", (WHITE, GREY, NATURAL), 99.0,
          "A painted pine bedside table with two drawers and an open shelf beneath, room for a "
          "lamp and a book by the bed in the bedroom."),
    _side("STBD3", "Oak Bedside Table with 3 Drawers", "Brackenmere Home", "bedside", 3, "Oak",
          "Bedroom", (NATURAL, DARK_BROWN), 149.0,
          "A tall oak bedside table with three deep drawers on soft-close runners, for the "
          "bedroom."),
    _side("STCN2", "Narrow Walnut Console Table with 2 Drawers", "Calderby & Lune", "console", 2,
          "Walnut", "Hallway", (DARK_BROWN, BLACK), 229.0,
          "A narrow walnut console table, only 30 cm deep, with two drawers for keys and post "
          "and a low shelf for shoes in a hallway."),
    _side("STNS3", "Oak Nest of Tables, Set of 3", "Lanternby", "nest", 0, "Oak", "Living Room",
          (NATURAL, WHITE), 129.0,
          "A nest of three oak tables that slide inside one another, out of the way until the "
          "living room needs them.", pieces=3),
)  # fmt: skip


# --------------------------------------------------------------------------
# Bookcases: the shelves and the style are drawn; the height is a SKU
# --------------------------------------------------------------------------


def _bookcase(code, title, brand, style, shelves, mat, colors, heights, text) -> FurnitureRow:
    shown = {"standard": "Open", "glass_door": "Glass-Door"}.get(style, style.title())
    count = (_count("cube_count", "Cube count", shelves) if style == "cube"
             else _count("shelf_count", "Shelf count", shelves))  # fmt: skip
    return FurnitureRow(
        code, title, brand, _HOME, BOOKCASES, "Bookcase", heights[0][1], "bookcase", text, colors,
        (("bookcase_style", "Bookcase style", shown), count, _mat(mat), _room("Living Room")),
        heights, size_key="size", params=(("shelves", str(shelves)), ("style", style)),
    )  # fmt: skip


BOOKS = (
    _bookcase("BKST5", "5 Shelf Oak Bookcase", "Hearth & Table", "standard", 5, "Oak",
              (NATURAL, WHITE, BLACK), (_height(180, 199.0), _height(200, 229.0)),
              "A tall open oak bookcase with five shelves, deep enough for hardbacks, that "
              "fixes to the living room wall."),
    _bookcase("BKLD4", "4 Shelf Ladder Bookcase", "Lanternby", "ladder", 4, "Pine",
              (NATURAL, BLACK), (_height(150, 99.0), _height(180, 119.0)),
              "A leaning ladder bookcase in pine, its four shelves deepening toward the floor, "
              "for plants and paperbacks in the living room."),
    _bookcase("BKCB4", "4 Cube Storage Unit", "Brackenmere Home", "cube", 4, "Oak",
              (WHITE, NATURAL, GREY), (_height(77, 59.0),),
              "A square cube storage unit with four open cubes, two of them holding fabric boxes, "
              "for books and toys in a living room or a playroom corner."),
    _bookcase("BKGD4", "4 Shelf Glass-Door Bookcase", "Calderby & Lune", "glass_door", 4,
              "Walnut", (DARK_BROWN, WHITE), (_height(180, 349.0), _height(200, 399.0)),
              "A walnut bookcase behind two glass doors that keep the dust off four shelves of "
              "books in the living room."),
)  # fmt: skip


# --------------------------------------------------------------------------
# Wardrobes: the doors, how they open and the mirror are drawn
# --------------------------------------------------------------------------


def _wardrobe(
    code, title, brand, doors, mirrored, door, drawers, mat, colors, size, price, text
) -> FurnitureRow:
    inner = (_count("drawer_count", "Drawer count", drawers),) if drawers else ()
    return FurnitureRow(
        code, title, brand, _HOME, WARDROBES, "Wardrobe", price, "wardrobe", text, colors,
        (_count("door_count", "Door count", doors), ("mirrored", "Mirrored", _yes(mirrored)),
         ("door_type", "Door type", door.title()), *inner, _mat(mat), *_dims(*size),
         _room("Bedroom")),
        params=(("doors", str(doors)), ("mirrored", _yes(mirrored)), ("door", door)),
    )  # fmt: skip


WARDROBE = (
    _wardrobe("WD2HG", "2 Door Pine Wardrobe", "Hearth & Table", 2, False, "hinged", 0, "Pine",
              (WHITE, GREY, NATURAL), (90, 180), 249.0,
              "A double pine wardrobe with two hinged doors over a full-length hanging rail and "
              "a top shelf, for a small bedroom."),
    _wardrobe("WD3MR", "3 Door Mirrored Oak Wardrobe", "Brackenmere Home", 3, True, "hinged", 2,
              "Oak", (NATURAL, WHITE), (130, 200), 549.0,
              "A triple oak wardrobe with three hinged doors, a full-length mirror on the "
              "middle one and two drawers inside, for the bedroom."),
    _wardrobe("WD2SL", "2 Door Sliding Mirrored Wardrobe", "Calderby & Lune", 2, True, "sliding",
              0, "Oak", (WHITE, BLACK), (150, 220), 499.0,
              "A wardrobe with two sliding doors, one a full mirror, that slide past each other "
              "rather than swing open, for a narrow bedroom."),
    _wardrobe("WD4HG", "4 Door Wardrobe with Drawers", "Lanternby", 4, False, "hinged", 3,
              "Walnut", (DARK_BROWN, WHITE), (180, 200), 699.0,
              "A wide walnut wardrobe with four hinged doors, two hanging rails, shelves and "
              "three drawers inside, for a main bedroom."),
)  # fmt: skip


# --------------------------------------------------------------------------
# Chests of drawers: the drawer fronts, tall or wide, are drawn
# --------------------------------------------------------------------------


def _chest(
    code, title, brand, drawers, form, mat, handles, colors, size, price, text
) -> FurnitureRow:
    return FurnitureRow(
        code, title, brand, _HOME, CHESTS, "Chest of Drawers", price, "chest_of_drawers", text,
        colors,
        (_count("drawer_count", "Drawer count", drawers),
         ("chest_style", "Chest style", form.title()), _mat(mat), ("handles", "Handles", handles),
         *_dims(*size), _room("Bedroom")),
        params=(("drawers", str(drawers)), ("form", form)),
    )  # fmt: skip


CHEST = (
    _chest("CD3WD", "3 Drawer Wide Oak Chest of Drawers", "Brackenmere Home", 3, "wide", "Oak",
           "Bar", (NATURAL, WHITE), (100, 80), 299.0,
           "A low, wide oak chest with three deep drawers on metal bar handles, its top at "
           "the right height for a bedroom lamp."),
    _chest("CD4TL", "4 Drawer Tall Pine Chest of Drawers", "Hearth & Table", 4, "tall", "Pine",
           "Knob", (WHITE, GREY, NATURAL), (60, 100), 179.0,
           "A tall, narrow painted pine chest with four drawers and round wooden knob handles, "
           "for a small bedroom."),
    _chest("CD5TL", "5 Drawer Tall Walnut Chest of Drawers", "Calderby & Lune", 5, "tall",
           "Walnut", "Cut-Out", (DARK_BROWN, BLACK), (70, 120), 399.0,
           "A tall walnut chest with five drawers and cut-out handles, so the fronts stay "
           "clean, for the bedroom."),
    _chest("CD6WD", "6 Drawer Wide Oak Chest of Drawers", "Lanternby", 6, "wide", "Oak", "Knob",
           (NATURAL, WHITE, GREY), (120, 85), 349.0,
           "A wide oak chest with two small drawers over four full-width ones, all on round "
           "knob handles, for the bedroom."),
)  # fmt: skip


# --------------------------------------------------------------------------
# Mirrors: the outline and the kind are drawn; the size is a SKU
# --------------------------------------------------------------------------

_MIRROR = {"wall": "Wall", "full_length": "Full-Length", "floor": "Floor-Standing",
           "bathroom": "Bathroom", "vanity": "Vanity"}  # fmt: skip


def _mirror(code, title, brand, shape, kind, mat, room, colors, sizes, text) -> FurnitureRow:
    return FurnitureRow(
        code, title, brand, _HOME, MIRRORS, "Mirror", sizes[0][1], "mirror", text, colors,
        (("mirror_type", "Mirror type", _MIRROR[kind]), ("shape", "Shape", shape.title()),
         _mat(mat), _room(room)),
        sizes, size_key="size", params=(("outline", shape), ("kind", kind)),
    )  # fmt: skip


MIRROR = (
    _mirror("MRRWL", "Round Wall Mirror", "Hearth & Table", "round", "wall", "Metal", "Hallway",
            (GOLD, BLACK, SILVER),
            (_glass(50, 50, 49.0), _glass(60, 60, 69.0), _glass(80, 80, 99.0)),
            "A round wall mirror in a slim metal frame, to hang by the front door in a hallway."),
    _mirror("MRAFL", "Arched Full-Length Mirror", "Brackenmere Home", "arched", "full_length",
            "Metal", "Bedroom", (BLACK, GOLD), (_glass(40, 150, 89.0), _glass(50, 160, 109.0)),
            "A tall arched full-length mirror in a thin metal frame, to lean or hang in a "
            "bedroom and check an outfit head to toe."),
    _mirror("MRSUN", "Sunburst Wall Mirror", "Lanternby", "sunburst", "wall", "Metal",
            "Living Room", (GOLD, BRUSHED_GOLD), (_glass(70, 70, 79.0), _glass(90, 90, 119.0)),
            "A round glass in a sunburst of metal rays, a wall mirror that works as a piece of "
            "art over a living room fireplace."),
    _mirror("MRBTH", "Rectangular Bathroom Mirror with Shelf", "Calderby & Lune", "rectangular",
            "bathroom", "Aluminum", "Bathroom", (SILVER, BLACK),
            (_glass(50, 70, 59.0), _glass(60, 80, 79.0)),
            "A rectangular bathroom mirror in a damp-proof aluminum frame, with a glass shelf "
            "under it for a toothbrush and soap."),
    _mirror("MRFLR", "Rectangular Floor-Standing Mirror", "Hearth & Table", "rectangular",
            "floor", "Oak", "Bedroom", (NATURAL, WHITE), (_glass(45, 170, 149.0),),
            "A floor-standing mirror in an oak frame on a folding stand, tall enough to see a "
            "whole outfit in the bedroom."),
    _mirror("MRVAN", "Round Vanity Mirror", "Calderby & Lune", "round", "vanity", "Metal",
            "Bedroom", (GOLD, SILVER), (_glass(20, 20, 39.0),),
            "A round vanity mirror on a weighted metal foot, to stand on a bedroom dressing "
            "table for make-up."),
)  # fmt: skip

#: Every furniture row, by type.
TYPES: dict[str, tuple[FurnitureRow, ...]] = {
    "Dining Table": DINING, "Dining Chair": CHAIRS, "Coffee Table": COFFEE, "Side Table": SIDE,
    "Bookcase": BOOKS, "Wardrobe": WARDROBE, "Chest of Drawers": CHEST, "Mirror": MIRROR,
}  # fmt: skip
ROWS: tuple[FurnitureRow, ...] = tuple(r for rows in TYPES.values() for r in rows)


def docs() -> list[dict]:
    """Every furniture row's catalog document, type by type."""
    return [r.doc() for r in ROWS]
