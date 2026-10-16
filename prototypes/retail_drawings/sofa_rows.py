"""Living-room seating (gen#196): sofas by seat count and shape, sofa beds, armchairs and
footstools (data only).

The catalog had one sofa (a fixed three-seater drawing) and one sofa bed, so a sofa search
showed no seat count, shape or material to narrow on. Each type here is a leaf of its own
under ``Home/Furniture``, typed by its name, with at least three styles from at least three
of the furniture brands, and draws with its own shape in :mod:`kit_seating`.

What changes a sofa's picture is a style, not a SKU (one image per style and colorway,
``tests/test_retail_image_release.py``): a model (its ``line``) is sold as a 2, 2.5, 3 or 4
seater, and a corner or chaise sofa as a left-hand or right-hand one, each its own style
with its colors as SKUs. What does not change the picture is a SKU axis: a recliner's
``recline`` (manual or power) and a sofa bed's ``bed_size``.

:func:`scale.templates` builds these just before the grocery styles and :func:`scale.derivable`
leaves them out, as it does the shirts, so the seeded derivation (and every product id and
image id it makes) is what it was.
"""

from __future__ import annotations

import kit_seating  # noqa: F401 -- registers the seating shapes
from breadth_rows import Row
from variants import Color, cw

_FURN = ("Home", "Furniture")
SOFAS = (*_FURN, "Sofas")
CORNER = (*SOFAS, "Corner Sofas")
CHAISE = (*SOFAS, "Chaise Sofas")
MODULAR = (*SOFAS, "Modular Sofas")
RECLINER = (*SOFAS, "Recliner Sofas")
SOFA_BEDS = (*SOFAS, "Sofa Beds")
ARMCHAIRS = (*_FURN, "Armchairs")
FOOTSTOOLS = (*_FURN, "Footstools")

GREEN, NAVY, BLUSH, MUSTARD = (cw("Bottle Green", "#2f5b46"), cw("Navy", "#26365c"),
                               cw("Blush", "#e8b9b3"), cw("Mustard", "#d4a32a"))
CREAM, OAT, TAUPE = cw("Cream", "#efe8d8"), cw("Oat", "#d8c9a8"), cw("Taupe", "#8b7d6b")
GREY, RUST, SAGE, CHARCOAL = (cw("Grey", "#9a9ca0"), cw("Rust", "#a4502a"),
                              cw("Sage", "#9bb08f"), cw("Charcoal", "#3b3b3e"))
TAN, BLACK, BROWN = cw("Tan", "#b07a43"), cw("Black", "#2a2a2e"), cw("Brown", "#6b4a2e")
NATURAL, TEAL, OCHRE = cw("Natural", "#d8cdb8"), cw("Teal", "#1c7c7d"), cw("Ochre", "#c9873a")

#: leg finish param -> its shopper-facing name
LEGS = {"oak": "Oak", "walnut": "Walnut", "black_metal": "Black Metal", "chrome": "Chrome"}
#: arm style param -> (shopper-facing name, how a description says it)
ARMS = {"track": ("Track", "square track arms"), "rolled": ("Rolled", "rolled arms"),
        "slim": ("Slim", "slim arms")}  # fmt: skip
WORDS = {2: "two", 2.5: "two and a half", 3: "three", 4: "four", 5: "five", 6: "six"}


def _yes(v: bool) -> str:
    return "yes" if v else "no"


def _cm(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "CMT", float(v * 10))  # canonical length is millimeters


def _dims(w: int, d: int, h: int) -> tuple[tuple, ...]:
    return (_cm("item_width", "Item width", w), _cm("item_depth", "Item depth", d),
            _cm("item_height", "Item height", h))  # fmt: skip


def _seats(n: float) -> tuple[str, str, str, str]:
    return ("seat_count", "Seat count", f"{n:g}", "C62")


def _seat_word(n: float) -> str:
    return f"{n:g} Seater"


# --------------------------------------------------------------------------
# Sofas: one model per line, sold as a 2, 2.5, 3 or 4 seater
# --------------------------------------------------------------------------

#: line -> (brand, material, arms, legs, filling, firmness, removable covers, pet friendly,
#:          colors, ((seats, width cm, price, title or None), ...))
_SOFA_MODELS = {
    "Harwell": ("Brackenmere Home", "Velvet", "track", "black_metal", "Foam", "Firm", False, False,
                (GREEN, NAVY, BLUSH, MUSTARD),
                ((2, 168, 649.0, "Harwell Velvet Loveseat, 2 Seater"), (3, 214, 799.0, None),
                 (4, 248, 999.0, None))),
    "Ashby": ("Larchwood Living", "Boucle", "slim", "oak", "Fiber", "Medium", True, False,
              (CREAM, OAT, TAUPE),
              ((2, 150, 549.0, "Ashby Boucle Snuggler Sofa, 2 Seater"), (2.5, 192, 699.0, None),
               (3, 212, 849.0, None))),
    "Corrin": ("Emberly Home", "Chenille", "rolled", "walnut", "Feather Blend", "Soft", True, True,
               (GREY, RUST, SAGE, CHARCOAL),
               ((2, 172, 599.0, None), (3, 218, 749.0, None), (4, 252, 949.0, None))),
    "Delby": ("Cobble & Kiln", "Leather", "track", "chrome", "Foam", "Firm", False, False,
              (TAN, BLACK, BROWN),
              ((2, 164, 1099.0, None), (3, 206, 1399.0, None))),
    "Fenby": ("Brackenmere Home", "Linen Look", "slim", "oak", "Fiber", "Medium", True, True,
              (NATURAL, SAGE, NAVY),
              ((2, 160, 499.0, "Fenby Linen Look Loveseat, 2 Seater"), (3, 204, 649.0, None))),
}  # fmt: skip

_FILL_TEXT = {
    "Foam": "Foam seat cushions keep a firm, tailored seat.",
    "Fiber": "Fiber-wrapped cushions give a relaxed, medium seat.",
    "Feather Blend": "Feather blend cushions sink in softly and plump back up.",
}


def _care(removable: bool, pet: bool) -> str:
    parts = []
    if removable:
        parts.append("The covers zip off to wash.")
    if pet:
        parts.append("The easy-clean, pet-friendly fabric wipes clean.")
    return " ".join(parts)


def _sofa(line: str, seats: float, width: int, price: float, title: str | None) -> Row:
    brand, mat, arms, legs, filling, firm, removable, pet, colors, _ = _SOFA_MODELS[line]
    small = "A small sofa for two" if seats == 2 else f"A {WORDS[seats]} seater sofa"
    text = (
        f"{small} in {mat.lower()}, with {ARMS[arms][1]} on {LEGS[legs].lower()} legs. "
        f"{_FILL_TEXT[filling]} {_care(removable, pet)} Width {width} cm."
    ).replace("  ", " ").strip()
    return Row(
        f"SF{line[:3].upper()}{f'{seats:g}'.replace('.', '')}",
        title or f"{line} {_seat_word(seats)} {mat} Sofa", brand, "Home", SOFAS, "Sofa", price,
        "sofa_seats", text, colors,
        (("line", "Line", line), _seats(seats), *_dims(width, 92, 84),
         ("material", "Material", mat),
         ("arm_style", "Arm style", ARMS[arms][0]), ("leg_finish", "Leg finish", LEGS[legs]),
         ("filling", "Filling", filling), ("firmness", "Firmness", firm),
         ("removable_covers", "Removable covers", _yes(removable)),
         ("pet_friendly", "Pet friendly", _yes(pet))),
        params=(("seats", f"{seats:g}"), ("arms", arms), ("legs", legs)),
    )  # fmt: skip


SOFA_ROWS = tuple(
    _sofa(line, seats, width, price, title)
    for line, model in _SOFA_MODELS.items()
    for seats, width, price, title in model[-1]
)

# --------------------------------------------------------------------------
# Corner and chaise sofas: a left-hand and a right-hand style of each model
# --------------------------------------------------------------------------

_HANDS = (("left", "Left Hand"), ("right", "Right Hand"))


def _handed(code: str, line: str, kind: str, brand: str, path: tuple[str, ...], ptype: str,
            shape: str, mat: str, seats: int, dims: tuple[int, int, int], price: float,
            colors: tuple[Color, ...], text: str, extra: tuple = (), arms: str = "track",
            legs: str = "black_metal") -> tuple[Row, ...]:
    """One model sold left-hand and right-hand: two styles, each drawn on its own side."""
    return tuple(
        Row(f"{code}{side[0].upper()}", f"{line} {hand} {mat} {kind}", brand, "Home", path,
            ptype, price, shape,
            f"{text} The {kind.lower().split()[0]} is on the {side} as you face it"
            f" ({hand.lower()}).",
            colors,
            (("line", "Line", line), _seats(seats), *_dims(*dims), ("material", "Material", mat),
             ("orientation", "Orientation", hand), ("arm_style", "Arm style", ARMS[arms][0]),
             ("leg_finish", "Leg finish", LEGS[legs]), *extra),
            params=(("seats", "3"), ("side", side), ("arms", arms), ("legs", legs)))
        for side, hand in _HANDS
    )  # fmt: skip


CORNER_ROWS = (
    *_handed("CNHAR", "Harwell", "Corner Sofa", "Brackenmere Home", CORNER, "Corner Sofa",
             "corner_sofa", "Velvet", 4, (262, 212, 84), 1499.0, (GREEN, NAVY, MUSTARD),
             "A four seater L-shaped corner sofa in velvet, deep enough to stretch out on.",
             (("shape", "Shape", "L-Shape"),)),
    *_handed("CNCOR", "Corrin", "Corner Sofa", "Emberly Home", CORNER, "Corner Sofa",
             "corner_sofa", "Chenille", 5, (286, 218, 86), 1699.0, (GREY, RUST, SAGE),
             "A five seater L-shaped corner sofa in an easy-clean, pet-friendly chenille.",
             (("shape", "Shape", "L-Shape"), ("pet_friendly", "Pet friendly", "yes")),
             arms="rolled", legs="walnut"),
    *_handed("CNDEL", "Delby", "Corner Sofa", "Cobble & Kiln", CORNER, "Corner Sofa",
             "corner_sofa", "Faux Leather", 5, (280, 210, 82), 1299.0, (BLACK, TAN),
             "A five seater L-shaped corner sofa in a soft faux leather that wipes clean.",
             (("shape", "Shape", "L-Shape"),), legs="chrome"),
    Row("CNASHU", "Ashby Boucle U-Shaped Corner Sofa", "Larchwood Living", "Home", CORNER,
        "Corner Sofa", 2299.0, "corner_sofa",
        "A six seater U-shaped corner sofa in boucle, with a return at both ends for a big"
        " family room.",
        (CREAM, OAT, TAUPE),
        (("line", "Line", "Ashby"), _seats(6), *_dims(330, 212, 82),
         ("material", "Material", "Boucle"),
         ("shape", "Shape", "U-Shape"), ("arm_style", "Arm style", "Track"),
         ("leg_finish", "Leg finish", "Oak")),
        params=(("seats", "3"), ("side", "u"), ("arms", "track"), ("legs", "oak"))),
)  # fmt: skip


def _chaise(code: str, line: str, brand: str, mat: str, seats: int, width: int, price: float,
            colors: tuple[Color, ...], text: str, arms: str, legs: str) -> tuple[Row, ...]:
    rows = _handed(code, line, "Chaise Sofa", brand, CHAISE, "Chaise Sofa", "chaise_sofa", mat,
                   seats, (width, 160, 84), price, colors, text, arms=arms, legs=legs)
    return tuple(
        Row(r.code, f"{line} {_seat_word(seats)} {r.title.split(line + ' ')[1]}", *_fields(r),
            params=(("seats", str(seats)), *r.params[1:]))
        for r in rows
    )


def _fields(r: Row) -> tuple:
    return (r.brand, r.department, r.path, r.product_type, r.price, r.shape, r.description,
            r.colors, r.attrs)  # fmt: skip


CHAISE_ROWS = (
    *_chaise("CHFEN", "Fenby", "Brackenmere Home", "Linen Look", 3, 232, 999.0,
             (NATURAL, SAGE, NAVY),
             "A three seater sofa in a linen look weave whose end seat runs forward as a chaise "
             "for putting your feet up. The covers zip off to wash.", "slim", "oak"),
    *_chaise("CHCOR", "Corrin", "Emberly Home", "Chenille", 3, 238, 1099.0, (GREY, CHARCOAL, RUST),
             "A three seater chenille sofa with a long chaise end, soft feather blend cushions "
             "and walnut legs.", "rolled", "walnut"),
    *_chaise("CHHAL", "Halsey", "Larchwood Living", "Velvet", 2, 196, 849.0, (TEAL, BLUSH, OCHRE),
             "A compact two seater velvet chaise sofa that fits a small living room, on black "
             "metal legs.", "track", "black_metal"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Modular sofas: a configuration of modules is a style
# --------------------------------------------------------------------------


def _modular(code: str, line: str, brand: str, mat: str, pieces: int, layout: str,
             ottoman: bool, modules: tuple[str, ...], width: int, price: float,
             colors: tuple[Color, ...], legs: str) -> Row:
    seats = pieces - ottoman
    shape = "corner" if layout == "corner" else "straight"
    text = (
        f"A {mat.lower()} modular sofa in {WORDS.get(pieces, str(pieces))} pieces, set out as a "
        f"{shape} sofa{' with a loose ottoman' if ottoman else ''}. The modules clip together "
        "and can be rearranged or added to later."
    )
    return Row(
        code, f"{line} {mat} Modular Sofa, {pieces} Pieces", brand, "Home", MODULAR,
        "Modular Sofa", price, "modular_sofa", text, colors,
        (("line", "Line", line), ("piece_count", "Piece count", str(pieces), "C62"),
         _seats(seats), *_dims(width, 160 if layout == "corner" else 96, 80),
         ("material", "Material", mat), *(("module_type", "Module type", m) for m in modules),
         ("leg_finish", "Leg finish", LEGS[legs])),
        params=(("pieces", str(pieces)), ("layout", layout), ("ottoman", _yes(ottoman)),
                ("legs", legs)),
    )  # fmt: skip


MODULAR_ROWS = (
    _modular("MDKEN4", "Kenwick", "Cobble & Kiln", "Boucle", 4, "straight", False,
             ("Arm End", "Armless"), 256, 1599.0, (CREAM, TAUPE, CHARCOAL), "black_metal"),
    _modular("MDKEN5", "Kenwick", "Cobble & Kiln", "Boucle", 5, "corner", True,
             ("Corner", "Arm End", "Armless", "Ottoman"), 260, 2099.0, (CREAM, TAUPE),
             "black_metal"),
    _modular("MDMOR3", "Morland", "Emberly Home", "Chenille", 3, "straight", False,
             ("Arm End", "Armless"), 196, 1199.0, (GREY, SAGE, RUST), "walnut"),
    _modular("MDPEN4", "Penley", "Larchwood Living", "Velvet", 4, "corner", False,
             ("Corner", "Arm End", "Armless"), 230, 1799.0, (GREEN, NAVY, BLUSH), "oak"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Recliner sofas: color x recline (manual or power)
# --------------------------------------------------------------------------


def _recliner(code: str, line: str, brand: str, mat: str, seats: int, width: int,
              price: float, colors: tuple[Color, ...], usb: bool, headrest: str) -> Row:
    text = (
        f"A {WORDS[seats]} seater {mat.lower()} recliner sofa: every seat reclines and raises "
        "its own footrest. Choose a manual recline with a side handle or a power recline at "
        f"the touch of a button.{' Power recliners have USB charging in the arm.' if usb else ''}"
    )
    return Row(
        code, f"{line} {_seat_word(seats)} {mat} Recliner Sofa", brand, "Home", RECLINER,
        "Recliner Sofa", price, "recliner_sofa", text, colors,
        (("line", "Line", line), _seats(seats), *_dims(width, 96, 100),
         ("material", "Material", mat), ("recline", "Recline", "Manual"),
         ("recline", "Recline", "Power"), ("usb_port", "USB port", _yes(usb)),
         ("headrest", "Headrest", headrest)),
        (("Manual", price), ("Power", price + 300.0)), size_key="recline",
        params=(("seats", str(seats)), ("legs", "black_metal")),
    )  # fmt: skip


RECLINER_ROWS = (
    _recliner("RCRUS3", "Rusholme", "Larchwood Living", "Leather", 3, 210, 1499.0,
              (BROWN, BLACK, TAN), True, "Adjustable"),
    _recliner("RCRUS2", "Rusholme", "Larchwood Living", "Leather", 2, 158, 1199.0,
              (BROWN, BLACK), True, "Adjustable"),
    _recliner("RCMOR3", "Morland", "Emberly Home", "Faux Leather", 3, 204, 999.0,
              (BLACK, GREY), False, "Fixed"),
    _recliner("RCKEN2", "Kenwick", "Cobble & Kiln", "Chenille", 2, 162, 899.0,
              (CHARCOAL, OAT, SAGE), True, "Fixed"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Sofa beds: color x bed size
# --------------------------------------------------------------------------

_MECH = {"pull_out": "Pull-Out", "click_clack": "Click-Clack", "fold_out": "Fold-Out"}
_MECH_TEXT = {
    "pull_out": "the bed pulls out from under the seat",
    "click_clack": "the back clicks down flat beside the seat",
    "fold_out": "the mattress folds out on a metal frame",
}
_BEDS = ("Small Double (4 ft)", "Double (4 ft 6)")


def _sofa_bed(code: str, line: str, brand: str, mat: str, seats: int, mech: str,
              mattress: str, depth: int, width: int, price: float,
              colors: tuple[Color, ...]) -> Row:
    text = (
        f"A {WORDS[seats]} seater {mat.lower()} sofa that converts to a bed: "
        f"{_MECH_TEXT[mech]}, with a {depth} cm {mattress.lower()} mattress. Sold in a small "
        "double or a double bed size."
    )
    return Row(
        code, f"{line} {_seat_word(seats)} {mat} Sofa Bed", brand, "Home", SOFA_BEDS, "Sofa Bed",
        price, "sofa_bed", text, colors,
        (("line", "Line", line), _seats(seats), *_dims(width, 92, 84),
         ("material", "Material", mat), ("mechanism", "Mechanism", _MECH[mech]),
         ("mattress_type", "Mattress type", mattress), ("depth", "Depth", f"{depth} cm")),
        ((_BEDS[0], price), (_BEDS[1], price + 100.0)), size_key="bed_size",
        params=(("mechanism", mech), ("seats", str(seats))),
    )  # fmt: skip


SOFA_BED_ROWS = (
    _sofa_bed("SBASH3", "Ashby", "Larchwood Living", "Boucle", 3, "pull_out", "Memory Foam",
              14, 212, 999.0, (CREAM, OAT)),
    _sofa_bed("SBCOR2", "Corrin", "Emberly Home", "Chenille", 2, "fold_out", "Pocket Sprung",
              12, 176, 749.0, (GREY, RUST, SAGE)),
    _sofa_bed("SBDEL2", "Delby", "Cobble & Kiln", "Faux Leather", 2, "click_clack", "Foam", 10,
              190, 449.0, (BLACK, GREY)),
    _sofa_bed("SBFEN3", "Fenby", "Brackenmere Home", "Linen Look", 3, "pull_out",
              "Pocket Sprung", 16, 208, 899.0, (NATURAL, NAVY)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Armchairs and footstools: color only
# --------------------------------------------------------------------------


def _chair(code: str, title: str, brand: str, mat: str, style: str, legs: str, price: float,
           dims: tuple[int, int, int], colors: tuple[Color, ...], text: str) -> Row:
    return Row(
        code, title, brand, "Home", ARMCHAIRS, "Armchair", price, "armchair", text, colors,
        (("material", "Material", mat), ("style", "Style", style.title()),
         ("leg_finish", "Leg finish", LEGS[legs]), *_dims(*dims)),
        params=(("style", style), ("legs", legs)),
    )  # fmt: skip


ARMCHAIR_ROWS = (
    _chair("ACHALA", "Halsey Velvet Accent Chair", "Larchwood Living", "Velvet", "accent", "oak",
           229.0, (68, 74, 82), (TEAL, BLUSH, OCHRE, NAVY),
           "A small accent chair on tall oak legs, sized for a bedroom corner or a reading nook."),
    _chair("ACMORW", "Morland Boucle Wingback Armchair", "Emberly Home", "Boucle", "wingback",
           "walnut", 449.0, (80, 86, 108), (CREAM, OAT),
           "A tall wingback armchair with rolled arms and a high back that hugs your shoulders."),
    _chair("ACKENT", "Kenwick Chenille Tub Chair", "Cobble & Kiln", "Chenille", "tub",
           "black_metal", 279.0, (72, 70, 76), (GREY, RUST, SAGE),
           "A compact tub chair whose arms wrap round in one curve with the back."),
    _chair("ACPENS", "Penley Boucle Swivel Armchair", "Larchwood Living", "Boucle", "swivel",
           "chrome", 399.0, (78, 78, 78), (CREAM, TAUPE),
           "A swivel armchair on a round steel base that turns all the way round."),
    _chair("ACFENN", "Fenby Linen Look Nursing Chair", "Brackenmere Home", "Linen Look",
           "nursing", "oak", 249.0, (62, 76, 104), (NATURAL, SAGE, BLUSH),
           "A nursing chair with a high back and no arms, low enough to sit with a baby."),
    _chair("ACRUSR", "Rusholme Leather Recliner Armchair", "Larchwood Living", "Leather",
           "recliner", "black_metal", 699.0, (86, 94, 102), (BROWN, BLACK),
           "A recliner armchair whose footrest rises as the back leans back."),
)  # fmt: skip


def _stool(code: str, title: str, brand: str, mat: str, form: str, storage: bool, legs: str,
           price: float, dims: tuple[int, int, int], colors: tuple[Color, ...], text: str) -> Row:
    return Row(
        code, title, brand, "Home", FOOTSTOOLS, "Footstool", price, "footstool", text, colors,
        (("material", "Material", mat), ("shape", "Shape", form.title()),
         ("storage_feature", "Storage feature", "Lift-Top" if storage else "None"),
         ("leg_finish", "Leg finish", LEGS[legs]), *_dims(*dims)),
        params=(("form", form), ("storage", _yes(storage)), ("legs", legs)),
    )  # fmt: skip


FOOTSTOOL_ROWS = (
    _stool("FSHARR", "Harwell Velvet Round Footstool", "Brackenmere Home", "Velvet", "round",
           False, "oak", 129.0, (60, 60, 42), (GREEN, BLUSH, MUSTARD),
           "A deep buttoned round footstool on short oak legs."),
    _stool("FSKENS", "Kenwick Boucle Storage Footstool", "Cobble & Kiln", "Boucle",
           "rectangular", True, "black_metal", 149.0, (90, 50, 44), (CREAM, TAUPE),
           "A rectangular footstool with storage inside: the buttoned lid lifts off for blankets."),
    _stool("FSDELR", "Delby Leather Rectangular Footstool", "Cobble & Kiln", "Leather",
           "rectangular", False, "chrome", 229.0, (100, 60, 42), (TAN, BLACK),
           "A long leather footstool on chrome legs, buttoned on top."),
    _stool("FSCORS", "Corrin Chenille Round Storage Footstool", "Emberly Home", "Chenille", "round",
           True, "walnut", 139.0, (56, 56, 44), (GREY, RUST, SAGE),
           "A round footstool with storage under a lift-off buttoned lid."),
)  # fmt: skip

ROWS = (
    *SOFA_ROWS, *CORNER_ROWS, *CHAISE_ROWS, *MODULAR_ROWS, *RECLINER_ROWS, *SOFA_BED_ROWS,
    *ARMCHAIR_ROWS, *FOOTSTOOL_ROWS,
)  # fmt: skip


def docs() -> list[dict]:
    """Every seating style's catalog document, in the order of :data:`ROWS`."""
    return [r.doc() for r in ROWS]
