"""Tableware and kitchen utensil templates for the scaled retail catalog (gen#198): data only.

The catalog had cutlery sets and dinner sets but no single plate, bowl, glass, piece of
cutlery, kitchen knife or utensil, so a search for one piece found a boxed set or nothing.
Each type here is a leaf under ``Home > Kitchen & Dining`` with its own drawing
(:mod:`kit_tableware`), its shopper attributes as structured entries, and SKUs over the
color (a glaze, a finish, a tint, a handle) and the type's own axis: a pack size, a blade
length or a board's dimensions. The style also lists every SKU axis value at product level
(:func:`_each`), so a facet sees every value the style sells; a knife's blade length, a
measured axis, is on its SKUs alone.

:func:`breadth_rows.docs` appends these rows, so they derive through :mod:`scale` as breadth
rows do. The kind of each type (``plate_type``, ``knife_type``, ...) fixes its drawn profile
and its measured size, so it is a :data:`scale.FROZEN_KEYS` key: a derived style never turns
a 27 cm dinner plate into a side plate.
"""

from __future__ import annotations

import kit_tableware  # noqa: F401 -- registers plate, bowl, cutlery_piece, ...
from breadth_rows import Contents, Row
from variants import cw

_KD = ("Home", "Kitchen & Dining")
_HW = "Home"


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _cm(key: str, name: str, v: float) -> tuple[str, str, str, str, float]:
    """A length in cm: the canonical value is in mm, as the core's ``CMT`` unit states it."""
    return (key, name, f"{v:g}", "CMT", v * 10)


def _ml(v: int) -> tuple[str, str, str, str, float]:
    return ("capacity", "Capacity", str(v), "MLT", float(v))


def _each(key: str, name: str, sizes: tuple[tuple[str, float], ...], unit: str | None = None):
    """The product-level entry for a SKU axis, so a facet lists every value sold: ONE entry
    under the SKUs' key, their values comma-joined, as a shoe's ``upper_material`` is
    (``tests/test_retail_scale.py``). A measured axis (``unit``, a knife's blade length) has
    none: a classed value is one number, so it stays on the SKUs alone, which the export
    states with its unit (``export.OPTIONS``), as a Christmas tree's height does."""
    if unit is not None:
        return ()
    return (_a(key, name, ", ".join(s for s, _ in sizes)),)


DISHWASHER = _a("dishwasher_safe", "Dishwasher safe", "Yes")
MICROWAVE = _a("microwave_safe", "Microwave safe", "Yes")


def _packs(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    return tuple(("Single" if n == 1 else f"{n} pack", p) for n, p in pairs)


def _tw(code, title, brand, leaf, ptype, shape, desc, colors, attrs, sizes=(), params=(),
        size_key="pack_size", unit=None, price=None, axis_name="Pack size") -> Row:  # fmt: skip
    """A tableware row: its axis values are SKUs and product-level entries alike."""
    axis = _each(size_key.removesuffix("_cm"), axis_name, sizes, unit) if sizes else ()
    first = price or (sizes[0][1] if sizes else 0.0)
    return Row(code, title, brand, _HW, (*_KD, leaf), ptype, first,
               shape, desc, colors, (*attrs, *axis), sizes, params=params, size_key=size_key)


SILVER = cw("Silver", "#cfd5da", "solid", "#8f989f")
GOLD = cw("Gold", "#d6b56a", "solid", "#8f6f2a")
BLACK = cw("Black", "#2f2f35", "solid", "#8f989f")
NATURAL = cw("Natural", "#c9a46a", "solid", "#7d5634")
CLEAR = cw("Clear", "#e3eef0", "solid", "#7a7d82")

# --------------------------------------------------------------------------
# Plates: the kind and diameter are drawn; the glaze or pattern is the color.
# --------------------------------------------------------------------------


def _plate(kind: str, cm: float, material: str, finish: str) -> tuple:
    return (_a("plate_type", "Plate type", kind), _cm("diameter", "Diameter", cm),
            _a("material", "Material", material), _a("finish", "Finish", finish), DISHWASHER)


def _pp(kind: str, cm: float, finish: str) -> tuple[tuple[str, str], ...]:
    return (("kind", kind.lower()), ("diameter", f"{cm:g}"), ("finish", finish.lower()))


PLATES = (
    _tw("PLTSTO", "Reactive Glaze Stoneware Dinner Plate", "Calderby & Lune", "Plates", "Plate",
        "plate", "A 27 cm dinner plate with a pooling reactive glaze that runs darker at the rim, "
        "so no two plates match exactly. Dishwasher and microwave safe.",
        (cw("Sage", "#9bb08f"), cw("Teal", "#1c7c7d"), cw("Ochre", "#c9873a")),
        (*_plate("Dinner", 27, "Stoneware", "Reactive Glaze"), MICROWAVE),
        _packs((1, 9.0), (4, 32.0), (6, 45.0)), _pp("dinner", 27, "Reactive Glaze")),
    _tw("PLTPOR", "White Porcelain Side Plate", "Hearth & Table", "Plates", "Plate", "plate",
        "A 20 cm side plate with a gently rolled rim, for toast, cake or a starter. Dishwasher "
        "and microwave safe.",
        (cw("White", "#f4f1ea", "solid", "#b9b4a6"),),
        (*_plate("Side", 20, "Porcelain", "Gloss"), MICROWAVE),
        _packs((1, 4.0), (4, 14.0), (6, 19.0)), _pp("side", 20, "Gloss")),
    _tw("PLTMEL", "Striped Melamine Side Plate", "Lanternby", "Plates", "Plate", "plate",
        "A 20 cm side plate printed with a bold stripe, light and hard to break, for picnics "
        "and the garden. Dishwasher safe.",
        (cw("Blue Stripe", "#ffffff", "stripe", "#3f6fb5"),
         cw("Red Stripe", "#ffffff", "stripe", "#c8312e")),
        (*_plate("Side", 20, "Melamine", "Gloss"), _a("pattern", "Pattern", "Striped")),
        _packs((4, 12.0), (6, 16.0)), _pp("side", 20, "Gloss")),
    _tw("PLTPAS", "Speckled Stoneware Pasta Plate", "Hearth & Table", "Plates", "Plate", "plate",
        "A 23 cm pasta plate with a deep well and a wide rim, in a speckled matte glaze. "
        "Dishwasher and microwave safe.",
        (cw("Cream", "#d8cdb8", "solid", "#6b5b45"), cw("Grey", "#9a9a9a")),
        (*_plate("Pasta", 23, "Stoneware", "Matte"), MICROWAVE),
        _packs((1, 8.0), (4, 28.0)), _pp("pasta", 23, "Matte")),
    _tw("PLTBON", "Bone China Rim Band Dinner Plate", "Lanternby", "Plates", "Plate", "plate",
        "A fine 27 cm dinner plate with a hand-painted rim band, light enough to stack high. "
        "Dishwasher and microwave safe.",
        (cw("White", "#f7f5ef", "solid", "#26365c"),),
        (*_plate("Dinner", 27, "Bone China", "Rim Band"), MICROWAVE),
        _packs((1, 12.0), (4, 42.0), (6, 60.0)), _pp("dinner", 27, "Rim Band")),
    _tw("PLTPLA", "Enamel Serving Platter", "Calderby & Lune", "Plates", "Plate", "plate",
        "An oval 36 cm platter with a rolled rim band, for a roast, a salad or a sharing board. "
        "Dishwasher safe.",
        (cw("White", "#f7f5ef", "solid", "#26365c"), cw("Cream", "#efe8d8", "solid", "#2a2a2e")),
        _plate("Serving Platter", 36, "Enamel", "Rim Band"), price=24.0,
        params=_pp("serving platter", 36, "Rim Band")),
)  # fmt: skip

# --------------------------------------------------------------------------
# Bowls: the kind sets the drawn profile.
# --------------------------------------------------------------------------


def _bowl(kind: str, cm: float, ml: int, material: str) -> tuple:
    return (_a("bowl_type", "Bowl type", kind), _cm("diameter", "Diameter", cm), _ml(ml),
            _a("material", "Material", material), DISHWASHER)  # fmt: skip


BOWLS = (
    _tw("BWLCER", "Stoneware Cereal Bowl", "Hearth & Table", "Bowls", "Bowl", "bowl",
        "A 16 cm bowl that holds 600 ml, deep enough for cereal, porridge or a noodle soup. "
        "Dishwasher and microwave safe.",
        (cw("Sage", "#9bb08f"), cw("Navy", "#26365c"), cw("Cream", "#efe8d8")),
        (*_bowl("Cereal", 16, 600, "Stoneware"), MICROWAVE),
        _packs((1, 6.0), (4, 20.0)), (("kind", "cereal"),)),
    _tw("BWLPAS", "Porcelain Pasta Bowl", "Lanternby", "Bowls", "Bowl", "bowl",
        "A wide, shallow 22 cm bowl that holds 900 ml, for pasta, risotto or a salad. "
        "Dishwasher and microwave safe.",
        (cw("White", "#f4f1ea", "solid", "#b9b4a6"), cw("Grey", "#9a9a9a")),
        (*_bowl("Pasta", 22, 900, "Porcelain"), MICROWAVE),
        _packs((1, 7.0), (4, 24.0), (6, 34.0)), (("kind", "pasta"),)),
    _tw("BWLSOU", "Reactive Glaze Soup Bowl", "Calderby & Lune", "Bowls", "Bowl", "bowl",
        "A rounded 15 cm soup bowl that holds 500 ml, its glaze pooling darker inside. "
        "Dishwasher and microwave safe.",
        (cw("Teal", "#1c7c7d"), cw("Rust", "#a4502a")),
        (*_bowl("Soup", 15, 500, "Stoneware"), _a("finish", "Finish", "Reactive Glaze"), MICROWAVE),
        _packs((1, 8.0), (4, 28.0)), (("kind", "soup"),)),
    _tw("BWLSAL", "Large Bamboo Salad Bowl", "Lanternby", "Bowls", "Bowl", "bowl",
        "A large 30 cm salad bowl that holds 3000 ml, turned from bamboo and finished with a "
        "food-safe oil. Hand wash.",
        (NATURAL,), (_a("bowl_type", "Bowl type", "Salad"), _cm("diameter", "Diameter", 30),
                     _ml(3000), _a("material", "Material", "Bamboo")),
        price=18.0, params=(("kind", "salad"),)),
    _tw("BWLSER", "Large Porcelain Serving Bowl", "Hearth & Table", "Bowls", "Bowl", "bowl",
        "A large 28 cm serving bowl that holds 2500 ml, for a family salad, pasta or fruit. "
        "Dishwasher and microwave safe.",
        (cw("White", "#f4f1ea", "solid", "#b9b4a6"), cw("Sage", "#9bb08f")),
        (*_bowl("Serving", 28, 2500, "Porcelain"), MICROWAVE), price=16.0,
        params=(("kind", "serving"),)),
    _tw("BWLMIX", "Enamel Mixing Bowl with Pouring Lip", "Calderby & Lune", "Bowls", "Bowl",
        "bowl", "A deep 24 cm mixing bowl that holds 3000 ml, with a pouring lip for batter. "
        "Dishwasher safe.",
        (cw("Cream", "#efe8d8", "solid", "#2a2a2e"), cw("Red", "#c8312e")),
        _bowl("Mixing", 24, 3000, "Enamel"), price=19.0, params=(("kind", "mixing"),)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Cutlery by the piece: the piece and handle are drawn; the finish is the color.
# --------------------------------------------------------------------------


def _cut(piece: str, handle: str) -> tuple:
    return (_a("cutlery_type", "Cutlery type", piece),
            _a("material", "Material", "Stainless Steel"), _a("handle", "Handle", handle))


def _cp(piece: str, handle: str) -> tuple[tuple[str, str], ...]:
    """The drawn piece: one, with no ``count``. Image ids are one per product and color, so
    every pack size of a style shares one picture, and a fanned count would be wrong for all
    but one of them (gen#228)."""
    return (("piece", piece.lower()), ("handle", handle.lower()))


CUTLERY = (
    _tw("CUTKNF", "Polished Dinner Knives", "Hearth & Table", "Cutlery", "Cutlery",
        "cutlery_piece", "Dinner knives with a rounded tip and a weighted plain handle, sold "
        "loose to add to a canteen. Dishwasher safe.",
        (SILVER, GOLD, BLACK), (*_cut("Dinner Knife", "Plain"), DISHWASHER),
        _packs((4, 12.0), (6, 16.0), (8, 20.0)), _cp("Dinner Knife", "Plain")),
    _tw("CUTSTK", "Wooden Handle Steak Knives", "Lanternby", "Cutlery", "Cutlery",
        "cutlery_piece", "Steak knives with a pointed serrated blade and a riveted wooden "
        "handle. Hand wash.",
        (SILVER,), _cut("Steak Knife", "Wooden"), _packs((4, 18.0), (6, 25.0)),
        _cp("Steak Knife", "Wooden")),
    _tw("CUTFRK", "Hammered Dinner Forks", "Calderby & Lune", "Cutlery", "Cutlery",
        "cutlery_piece", "Four-tine dinner forks with a hand-hammered handle that catches the "
        "light. Dishwasher safe.",
        (SILVER, GOLD), (*_cut("Dinner Fork", "Hammered"), DISHWASHER),
        _packs((4, 14.0), (6, 19.0), (8, 24.0)), _cp("Dinner Fork", "Hammered")),
    _tw("CUTTSP", "Satin Teaspoons", "Hearth & Table", "Cutlery", "Cutlery", "cutlery_piece",
        "Teaspoons with a slim plain handle, for tea, coffee and sugar. Dishwasher safe.",
        (GOLD, SILVER, BLACK), (*_cut("Teaspoon", "Plain"), DISHWASHER),
        _packs((4, 8.0), (6, 11.0), (8, 14.0)), _cp("Teaspoon", "Plain")),
    _tw("CUTDSP", "Matte Dessert Spoons", "Lanternby", "Cutlery", "Cutlery", "cutlery_piece",
        "Dessert spoons with a deep bowl and a plain handle, for puddings and cereal. "
        "Dishwasher safe.",
        (BLACK, SILVER), (*_cut("Dessert Spoon", "Plain"), DISHWASHER),
        _packs((4, 10.0), (6, 14.0), (8, 18.0)), _cp("Dessert Spoon", "Plain")),
    _tw("CUTSRV", "Hammered Serving Spoon", "Calderby & Lune", "Cutlery", "Cutlery",
        "cutlery_piece", "A long serving spoon with a deep bowl and a hand-hammered handle. "
        "Dishwasher safe.",
        (SILVER, GOLD), (*_cut("Serving Spoon", "Hammered"), DISHWASHER),
        _packs((1, 9.0), (2, 16.0)), _cp("Serving Spoon", "Hammered")),
)  # fmt: skip

# --------------------------------------------------------------------------
# Kitchen knives: the kind and the blade length are drawn; the handle is the color.
# --------------------------------------------------------------------------


def _knife(kind: str, steel: str, handle: str) -> tuple:
    return (_a("knife_type", "Knife type", kind), _a("blade_steel", "Blade steel", steel),
            _a("handle_material", "Handle material", handle))  # fmt: skip


def _blades(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    return tuple((str(cm), p) for cm, p in pairs)


def _kn(code, title, brand, desc, colors, attrs, blades, kind) -> Row:  # fmt: skip
    # the image is shared by every blade length of a color, so a style sold in several
    # lengths states its range ("15-23 cm"), never one length the SKU may not sell
    lo, hi = blades[0][0], blades[-1][0]
    span = (("blade_max", hi),) if hi != lo else ()
    return _tw(code, title, brand, "Kitchen Knives", "Kitchen Knife", "kitchen_knife", desc,
               colors, attrs, blades, (("kind", kind), ("blade", lo), *span),
               size_key="blade_length_cm", unit="CMT", axis_name="Blade length")  # fmt: skip


_BLOCK6 = Contents((1, "chef's knife"), (1, "bread knife"), (1, "carving knife"),
                   (1, "utility knife"), (1, "paring knife"), (1, "knife block"))  # fmt: skip

KNIVES = (
    _kn("KNFCHF", "Forged Chef's Knife", "Calderby & Lune",
        "A forged chef's knife with a deep curved blade for rocking cuts, a full tang and a "
        "riveted handle. Hand wash.",
        (BLACK, cw("Walnut", "#5a3a26")), _knife("Chef's", "German Stainless Steel", "Pakkawood"),
        _blades((15, 25.0), (20, 32.0), (23, 38.0)), "chef's"),
    _kn("KNFSAN", "Santoku Knife with Dimpled Blade", "Lanternby",
        "A santoku with a flat sheepsfoot blade whose dimples stop slices sticking, on an "
        "olive wood handle. Hand wash.",
        (NATURAL,), _knife("Santoku", "Japanese VG10 Steel", "Olive Wood"),
        _blades((13, 34.0), (18, 42.0)), "santoku"),
    _kn("KNFBRD", "Serrated Bread Knife", "Hearth & Table",
        "A long bread knife with a scalloped edge that cuts a crusty loaf without crushing it. "
        "Dishwasher safe.",
        (BLACK, cw("Red", "#c8312e")), _knife("Bread", "Stainless Steel", "Polypropylene"),
        _blades((20, 12.0), (23, 15.0)), "bread"),
    _kn("KNFPAR", "Paring Knife", "Hearth & Table",
        "A short pointed paring knife for peeling, trimming and coring fruit. Dishwasher safe.",
        (BLACK, cw("Red", "#c8312e"), cw("Green", "#4f7a3a")),
        _knife("Paring", "Stainless Steel", "Polypropylene"), _blades((8, 5.0), (10, 6.0)),
        "paring"),
    _kn("KNFCRV", "Forged Carving Knife", "Calderby & Lune",
        "A long narrow carving knife for thin slices off a roast, with a riveted handle. "
        "Hand wash.",
        (BLACK,), _knife("Carving", "German Stainless Steel", "Pakkawood"),
        _blades((20, 30.0), (25, 36.0)), "carving"),
    _kn("KNFUTL", "Utility Knife", "Lanternby",
        "A mid-length utility knife for sandwiches, tomatoes and herbs, on an olive wood "
        "handle. Hand wash.",
        (NATURAL,), _knife("Utility", "Japanese VG10 Steel", "Olive Wood"),
        _blades((12, 22.0), (15, 26.0)), "utility"),
    _tw("KNFBLK", _BLOCK6.title("Knife Block Set"), "Calderby & Lune", "Kitchen Knives",
        "Kitchen Knife", "kitchen_knife",
        _BLOCK6.text("A block set of forged blades with riveted handles, stored in an angled "
                     "block."),
        (NATURAL, BLACK),
        (*_knife("Block Set", "German Stainless Steel", "Pakkawood"), *_BLOCK6.attrs),
        price=89.0, params=(("kind", "block"),)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Glassware: the kind's profile is drawn in the record's tint.
# --------------------------------------------------------------------------


#: A glassware row's leaf, product type and shape.
_GLASSWARE = ("Glassware", "Glassware", "drinking_glass")


def _glass(kind: str, ml: int, material: str) -> tuple:
    return (_a("glass_type", "Glass type", kind), _ml(ml), _a("material", "Material", material),
            DISHWASHER)  # fmt: skip


GLASSES = (
    _tw("GLSWIN", "Crystal Wine Glasses", "Lanternby", *_GLASSWARE,
        "Thin-rimmed wine glasses that hold 450 ml, with a tall stem and a tulip bowl. "
        "Dishwasher safe.",
        (CLEAR,), _glass("Wine", 450, "Crystal"), _packs((2, 24.0), (4, 40.0), (6, 55.0)),
        (("kind", "wine"),)),
    _tw("GLSFLT", "Champagne Flutes", "Hearth & Table", *_GLASSWARE,
        "Tall flutes that hold 200 ml and keep the bubbles longer. Dishwasher safe.",
        (CLEAR, cw("Gold", "#f2e29b")), _glass("Champagne Flute", 200, "Glass"),
        _packs((4, 16.0), (6, 22.0)), (("kind", "champagne flute"),)),
    _tw("GLSHIB", "Ribbed Highball Glasses", "Calderby & Lune", *_GLASSWARE,
        "Tall ribbed highball glasses that hold 400 ml, for long drinks and juice. "
        "Dishwasher safe.",
        (CLEAR, cw("Smoke", "#9a9a9a"), cw("Amber", "#d9a05b")), _glass("Highball", 400, "Glass"),
        _packs((4, 18.0), (6, 25.0)), (("kind", "highball"), ("ribbed", "1"))),
    _tw("GLSTUM", "Plastic Outdoor Tumblers", "Hearth & Table", *_GLASSWARE,
        "Shatterproof tumblers that hold 300 ml, for the garden, the pool and picnics. "
        "Dishwasher safe.",
        (cw("Blue", "#3f6fb5"), cw("Pink", "#f3c6cf"), cw("Green", "#6f8f4a")),
        _glass("Tumbler", 300, "Plastic"), _packs((4, 8.0), (6, 11.0)), (("kind", "tumbler"),)),
    _tw("GLSGIN", "Gin Balloon Glasses", "Lanternby", *_GLASSWARE,
        "Wide balloon glasses on a stem that hold 650 ml, room for ice and a garnish. "
        "Dishwasher safe.",
        (CLEAR, cw("Pink", "#f3c6cf")), _glass("Gin", 650, "Glass"),
        _packs((2, 14.0), (4, 24.0)), (("kind", "gin"),)),
    _tw("GLSBER", "Pint Beer Glasses", "Calderby & Lune", *_GLASSWARE,
        "Pint glasses that hold 568 ml, with a bulge near the rim for a sure grip. "
        "Dishwasher safe.",
        (CLEAR,), _glass("Beer", 568, "Glass"), _packs((2, 9.0), (4, 16.0)), (("kind", "beer"),)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Kitchen utensils: the kind is drawn; the head is the color.
# --------------------------------------------------------------------------


#: A utensil type whose drawn kind has another name: a set draws as ``set``, in its pot.
_UTENSIL_KIND = {"Utensil Set": "set"}


def _ut(code, title, brand, desc, colors, kind, material, price, extra=()) -> Row:  # fmt: skip
    return _tw(code, title, brand, "Kitchen Utensils", "Kitchen Utensil", "kitchen_utensil",
               desc, colors, (_a("utensil_type", "Utensil type", kind),
                              _a("material", "Material", material), *extra),
               price=price, params=(("kind", _UTENSIL_KIND.get(kind, kind.lower())),
                                    ("material", material.lower())))  # fmt: skip


_SET5 = Contents((1, "ladle"), (1, "turner"), (1, "whisk"), (1, "spoon"), (1, "holder"))

UTENSILS = (
    _ut("UTNSPA", "Silicone Spatula", "Hearth & Table",
        "A flexible spatula that scrapes a bowl clean and is heat resistant to 230 C.",
        (cw("Red", "#c8312e"), cw("Teal", "#1c7c7d"), cw("Grey", "#9a9a9a")), "Spatula",
        "Silicone", 4.0),
    _ut("UTNTRN", "Slotted Turner", "Lanternby",
        "A thin slotted turner that slides under eggs, fish and pancakes. Safe on non-stick.",
        (BLACK,), "Turner", "Nylon", 5.0),
    _ut("UTNLAD", "Stainless Steel Ladle", "Calderby & Lune",
        "A deep ladle with a hooked end that rests on the pan, for soups and stews.",
        (SILVER,), "Ladle", "Stainless Steel", 8.0),
    _ut("UTNSLS", "Wooden Slotted Spoon", "Lanternby",
        "A beech slotted spoon that drains peas and pasta and never scratches a pan.",
        (NATURAL,), "Slotted Spoon", "Wood", 4.5),
    _ut("UTNWHK", "Balloon Whisk", "Calderby & Lune",
        "A balloon whisk with springy wires for egg whites, batters and sauces.",
        (SILVER,), "Whisk", "Stainless Steel", 6.0),
    _ut("UTNTNG", "Silicone Tipped Tongs", "Hearth & Table",
        "Locking tongs with soft tips for turning, serving and tossing salad.",
        (cw("Green", "#4f7a3a"), BLACK), "Tongs", "Silicone", 7.0),
    _ut("UTNMSH", "Potato Masher", "Hearth & Table",
        "A sturdy masher with a perforated plate for smooth mash. Safe on non-stick.",
        (BLACK,), "Masher", "Nylon", 6.0),
    _ut("UTNPEL", "Y Peeler", "Lanternby",
        "A Y peeler with a swivel blade for potatoes, carrots and apples.",
        (cw("Orange", "#e07a1f"), cw("Green", "#6f8f4a")), "Peeler", "Stainless Steel", 3.5),
    _ut("UTNGRT", "Four Sided Box Grater", "Calderby & Lune",
        "A box grater with coarse, fine, slicing and zesting faces and a non-slip base.",
        (cw("Navy", "#26365c"), BLACK), "Grater", "Stainless Steel", 10.0),
    _ut("UTNSET", _SET5.title("Silicone Utensil Set with Holder"), "Hearth & Table",
        _SET5.text("Heat resistant heads on sturdy handles: the utensil set stands in a "
                   "matching pot."),
        (cw("Grey", "#9a9a9a"), cw("Cream", "#efe8d8")), "Utensil Set", "Silicone", 22.0,
        _SET5.attrs),
)  # fmt: skip

# --------------------------------------------------------------------------
# Chopping boards and colanders: the material is drawn.
# --------------------------------------------------------------------------


def _bd(code, title, brand, desc, colors, material, sizes, extra=(), drawn=()) -> Row:  # fmt: skip
    return _tw(code, title, brand, "Chopping Boards", "Chopping Board", "chopping_board", desc,
               colors, (_a("material", "Material", material), *extra), sizes,
               (("material", material.lower()), *drawn), size_key="dimensions",
               axis_name="Dimensions")


_BOARDS3 = Contents((1, "small board"), (1, "medium board"), (1, "large board"))

BOARDS = (
    _bd("BRDWOD", "Acacia Wood Chopping Board", "Lanternby",
        "A thick end-grain board with a hanging hole, oiled to bring out the grain. Hand wash.",
        (NATURAL,), "Wood", (("30 x 20 cm", 15.0), ("40 x 28 cm", 22.0), ("50 x 35 cm", 30.0))),
    _bd("BRDBAM", "Bamboo Chopping Board with Juice Groove", "Hearth & Table",
        "A light board with a groove round the edge that catches juice from a roast. Hand wash.",
        (cw("Natural", "#d9b77e", "solid", "#7d5634"),), "Bamboo",
        (("30 x 20 cm", 9.0), ("38 x 25 cm", 12.0), ("45 x 30 cm", 16.0)),
        drawn=(("groove", "juice"),)),
    _bd("BRDPLA", "Color Coded Plastic Chopping Board", "Calderby & Lune",
        "A non-slip board in a color for each food, to keep raw meat apart. Dishwasher safe.",
        (cw("Green", "#4f7a3a"), cw("Red", "#c8312e"), cw("Blue", "#3f6fb5")), "Plastic",
        (("30 x 20 cm", 6.0), ("40 x 28 cm", 9.0)), (DISHWASHER,)),
    _bd("BRDGLS", "Tempered Glass Chopping Board", "Lanternby",
        "A heat resistant board on rubber feet that doubles as a worktop saver. Dishwasher safe.",
        (CLEAR,), "Glass", (("30 x 20 cm", 10.0), ("40 x 30 cm", 14.0)), (DISHWASHER,)),
    _tw("BRDSET", _BOARDS3.title("Plastic Chopping Board Set"), "Hearth & Table",
        "Chopping Boards", "Chopping Board", "chopping_board",
        _BOARDS3.text("Non-slip edges, stored upright in a rack. Dishwasher safe."),
        (cw("Grey", "#9a9a9a"),), (_a("material", "Material", "Plastic"), DISHWASHER,
                                   *_BOARDS3.attrs),
        price=18.0, params=(("material", "plastic"),)),
)  # fmt: skip


def _col(code, title, brand, desc, colors, material, cm, ml, price) -> Row:  # fmt: skip
    return _tw(code, title, brand, "Colanders", "Colander", "colander", desc, colors,
               (_a("material", "Material", material), _cm("diameter", "Diameter", cm), _ml(ml)),
               price=price, params=(("material", material.lower()),))  # fmt: skip


COLANDERS = (
    _col("COLSTL", "Stainless Steel Colander", "Calderby & Lune",
         "A 24 cm colander that holds 4000 ml, on a sturdy foot ring with two side handles.",
         (SILVER,), "Stainless Steel", 24, 4000, 16.0),
    _col("COLENA", "Enamel Colander", "Hearth & Table",
         "A 22 cm colander that holds 3000 ml, with a dark rolled rim and loop handles.",
         (cw("Cream", "#efe8d8", "solid", "#2a2a2e"), cw("Red", "#c8312e")), "Enamel", 22,
         3000, 20.0),
    _col("COLCOL", "Collapsible Silicone Colander", "Lanternby",
         "A 24 cm colander that holds 3500 ml and folds flat to fit a drawer.",
         (cw("Teal", "#1c7c7d"), cw("Grey", "#9a9a9a")), "Silicone", 24, 3500, 12.0),
    _col("COLPLA", "Plastic Colander with Handles", "Calderby & Lune",
         "A light 26 cm colander that holds 4500 ml, with slotted drainage and a wide base.",
         (cw("Green", "#6f8f4a"), cw("Blue", "#3f6fb5")), "Plastic", 26, 4500, 6.0),
)  # fmt: skip

#: Every tableware row, by type.
TYPES = {
    "Plate": PLATES, "Bowl": BOWLS, "Cutlery": CUTLERY, "Kitchen Knife": KNIVES,
    "Glassware": GLASSES, "Kitchen Utensil": UTENSILS, "Chopping Board": BOARDS,
    "Colander": COLANDERS,
}  # fmt: skip
ROWS = tuple(r for rows in TYPES.values() for r in rows)


def docs() -> list[dict]:
    return [r.doc() for r in ROWS]
