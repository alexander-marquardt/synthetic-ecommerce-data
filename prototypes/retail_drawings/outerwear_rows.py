"""Outerwear templates for the scaled retail catalog (gen#211): data only.

The catalog held one check coat, a bomber, a denim jacket and a suit jacket, so a search for a
trench coat, a raincoat, a parka, a gilet or a peacoat found the one coat or a bomber, and a
length, waterproof or fill filter had nothing to narrow. Each type here is a leaf under
Coats & Jackets with its own drawing (:mod:`kit_coats`), its shopper attributes (length, belt,
breasting, waterproof rating, hood, fill, warmth, pockets, collar, ...) as structured entries and
SKUs over color and size. Boleros, shrugs and capes are one type with three drawn styles; each type is a spec under
``type_specs/`` that reads its rows from :func:`rows_of`.

A style's attribute and its drawing param are made from one value (:func:`_p`), so the image never
states what the row does not: a belted trench coat draws one ``belt`` group, a hooded puffer one
``hood`` group, a double-breasted peacoat six ``button`` circles. A drawing prints no size, so
every size of a colorway shares one image. These styles are templates only: :func:`scale.derivable`
leaves them out, so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- descriptions and row data read better whole than wrapped.

from __future__ import annotations

import kit_coats  # noqa: F401 -- registers trench_coat, raincoat, parka, puffer, ...
from breadth_rows import Row
from variants import cw

#: The nine brands the outerwear is sold under, all with a house style (:mod:`house_styles`) and an
#: owner stated elsewhere in the clothing tree: ``brand -> owner``.
_BRANDS = {"Harbour & Pine": "own", "Calderby & Lune": "third_party", "Saltmarsh": "own",
           "Wrenfield": "own", "Stridewell": "third_party", "Larkmoor": "own",
           "Hollinwray Knits": "third_party", "Ottery Denim": "own", "Ferrowick Denim": "own"}  # fmt: skip
BRAND_OWNERS = tuple(_BRANDS.items())
FB, TR, AO, NM, BW, CM, OP, KR, LD = _BRANDS

CL = "Clothing"
CJ_W = ("Womens", "Coats & Jackets")
CJ_M = ("Mens", "Coats & Jackets")
ADULT = ("XS", "S", "M", "L", "XL")
ADULT_M = ("S", "M", "L", "XL", "XXL")

#: product type -> the leaf's name under Coats & Jackets (a Womens or a Mens one), and the nesting
#: parents: a trench coat and a peacoat sit under Coats, the generic node (gen#283).
LEAVES = {
    "Trench Coat": ("Coats", "Trench Coats"), "Peacoat": ("Coats", "Peacoats"),
    "Raincoat": ("Raincoats",), "Parka": ("Parkas",), "Puffer Jacket": ("Puffer Jackets",),
    "Gilet": ("Gilets",), "Utility Jacket": ("Utility Jackets",), "Shacket": ("Shackets",),
    "Bolero": ("Boleros & Capes",), "Windbreaker": ("Windbreakers",), "Hoodie": ("Hoodies",),
}  # fmt: skip
#: The drawing shape of each product type: one shape per type, never shared.
SHAPE_OF = {"Trench Coat": "trench_coat", "Raincoat": "raincoat", "Parka": "parka",
            "Puffer Jacket": "puffer", "Gilet": "gilet", "Peacoat": "peacoat",
            "Utility Jacket": "utility_jacket", "Shacket": "shacket", "Bolero": "bolero", "Windbreaker": "windbreaker",
            "Hoodie": "hoodie"}  # fmt: skip
TYPES = tuple(LEAVES)

PAL = {
    "Black": cw("Black", "#2f2f35"), "White": cw("White", "#f4f1ea", "solid", "#b9b4a6"),
    "Red": cw("Red", "#b8322b"), "Blue": cw("Blue", "#3f6fb5"), "Green": cw("Green", "#3f7a4a"),
    "Yellow": cw("Yellow", "#e8c547"), "Navy": cw("Navy", "#26365c"), "Camel": cw("Camel", "#c19a6b"),
    "Stone": cw("Stone", "#cfc6b8"), "Olive": cw("Olive", "#6b6b3a"), "Khaki": cw("Khaki", "#8a8456"),
    "Grey": cw("Grey", "#9a9ca0"), "Charcoal": cw("Charcoal", "#4b4e55"), "Cream": cw("Cream", "#efe8d8", "solid", "#b9b4a6"),
    "Burgundy": cw("Burgundy", "#6e2433"), "Pink": cw("Pink", "#e7a9b8"), "Brown": cw("Brown", "#6b4a35"),
    "Teal": cw("Teal", "#1c7c7d"), "Beige": cw("Beige", "#d8c9a8", "solid", "#b9b4a6"), "Tan": cw("Tan", "#b58a5a"), "Orange": cw("Orange", "#d9762b"),
    "Black Check": cw("Black Check", "#efe8d8", "gingham", "#2f2f35"), "Red Check": cw("Red Check", "#b8322b", "gingham", "#2f2f35"), "Green Check": cw("Green Check", "#3f7a4a", "gingham", "#2f2f35"),
}  # fmt: skip


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _p(key: str, name: str, value: str, param: str | None = None, shown: str | None = None):
    """The attribute and the drawing param made from one value: ``(attr, param)``."""
    return _a(key, name, value), (param or key, (shown or value).lower().replace("-", "_").replace(" ", "_"))


LEN = {"Short": "short", "Mid Length": "mid", "Long": "long", "Cropped": "cropped",
       "Regular": "regular", "Longline": "longline"}  # fmt: skip


def _row(code, title, brand, ptype, price, desc, colors, attrs, params, mens=False):
    root = CJ_M if mens else CJ_W
    title = f"Mens {title}" if mens else title
    leaf = (*root, *LEAVES[ptype])
    return Row(
        code, title, brand, CL, leaf, ptype, price, SHAPE_OF[ptype], desc,
        tuple(PAL[c] for c in colors), tuple(attrs), tuple((s, price) for s in (ADULT_M if mens else ADULT)),
        params=tuple(params),
    )  # fmt: skip


def _t(*words: str) -> str:
    return " ".join(w for w in words if w)


def _and(*parts: str) -> str:
    """``a, b and c``: the non-empty parts of a clause list, joined the way a shop writes them."""
    got = [p for p in parts if p]
    return got[0] if len(got) < 2 else ", ".join(got[:-1]) + " and " + got[-1]


def _lw(length: str) -> str:
    """A length as it reads in copy: ``Mid Length`` is ``mid-length``."""
    return length.lower().replace("mid length", "mid-length")


def _a_an(word: str) -> str:
    """The indefinite article that opens a description, capitalised: ``A`` or ``An``."""
    return "An" if word[:1].lower() in "aeiou" else "A"


# --------------------------------------------------------------------------
# Trench coats: length, belt and breasting are drawn; fabric and water repellency are stated.
# --------------------------------------------------------------------------


def _trench(code, brand, price, length, belt, breast, fabric, water, colors, note):
    a_len, p_len = _p("garment_length", "Length", length, "length", LEN[length])
    a_belt, p_belt = _p("belted", "Belted", belt, "belt", belt)
    a_br, p_br = _p("breasting", "Breasting", breast, "breasted", {"Double-Breasted": "double", "Single-Breasted": "single"}[breast])
    title = _t(length if length != "Mid Length" else "Mid Length", "Belted" if belt == "Yes" else "", breast, fabric, "Trench Coat")
    clauses = _and("epaulettes", "a storm flap", "a tie belt at the waist" if belt == "Yes" else "")
    desc = f"A {_lw(length)} {breast.lower()} {fabric.lower()} trench coat with {clauses}. {note}"
    return _row(code, title, brand, "Trench Coat", price, desc, colors,
                (a_len, a_belt, a_br, _a("fabric", "Fabric", fabric), _a("water_repellent", "Water repellent", water)),
                (p_len, p_belt, p_br))  # fmt: skip


TRENCH_ROWS = (
    _trench("TRNLNG", FB, 120.0, "Long", "Yes", "Double-Breasted", "Cotton", "Yes", ("Camel", "Black", "White"), "The classic cut, in a closely woven gabardine finished to shed a shower."),
    _trench("TRNMID", TR, 95.0, "Mid Length", "Yes", "Single-Breasted", "Cotton", "Yes", ("Stone", "Red", "Navy"), "Light enough for spring and autumn, and finished to shed a shower."),
    _trench("TRNSHT", AO, 85.0, "Short", "No", "Single-Breasted", "Polyester", "Yes", ("Black", "Yellow", "Green"), "Cut to the hip, in a recycled shell that sheds light rain."),
    _trench("TRNDBL", NM, 140.0, "Long", "No", "Double-Breasted", "Twill", "No", ("Khaki", "Blue", "Cream"), "Heavy enough for winter, with a wide collar that turns up against the wind."),
)  # fmt: skip

# --------------------------------------------------------------------------
# Raincoats: hood and length are drawn; the waterproof rating, breathability and lining stated.
# --------------------------------------------------------------------------


def _rain(code, brand, price, length, hood, rating, breathable, lining, fabric, colors, note, mens=False):
    a_len, p_len = _p("garment_length", "Length", length, "length", LEN[length])
    hood_attrs, p_hood = (_a("hood", "Hood", "No"),), ("hood", "none")
    if hood != "None":
        hood_attrs = (_a("hood", "Hood", "Yes"), _a("hood_type", "Hood type", hood))
        p_hood = ("hood", hood.lower())
    title = _t(length, "Hooded" if hood == "Fixed" else "Packaway Hooded" if hood == "Packaway" else "", "Lined" if lining == "Lined" else "", "Raincoat")
    hood_clause = {"Fixed": "a fixed hood", "Packaway": "a packaway hood"}.get(hood, "")
    clauses = _and(hood_clause, "a zip front under a storm placket", "taped seams", "a soft mesh lining" if lining == "Lined" else "")
    desc = f"A {_lw(length)} waterproof {fabric.lower()} raincoat rated to {rating}, with {clauses}. {note}"
    return _row(code, title, brand, "Raincoat", price, desc, colors,
                (a_len, *hood_attrs, _a("waterproof_rating", "Waterproof rating", rating), _a("breathable", "Breathable", breathable),
                 _a("lining", "Lining", lining), _a("fabric", "Fabric", fabric)),
                (p_len, p_hood), mens)  # fmt: skip


RAIN_ROWS = (
    _rain("RNCHDM", BW, 70.0, "Mid Length", "Fixed", "10,000 mm", "Yes", "Unlined", "Polyester", ("Yellow", "Navy", "Black"), "The hood rolls down into the collar when it is not needed."),
    _rain("RNCPKS", CM, 55.0, "Short", "Packaway", "5,000 mm", "No", "Unlined", "Nylon", ("Red", "Green", "White"), "The coat folds into a stuff pocket for the bag."),
    _rain("RNCLNL", FB, 110.0, "Long", "None", "20,000 mm", "Yes", "Lined", "Polyester", ("Black", "Blue", "Stone"), "Comfortable all day, with room for a jumper underneath."),
    _rain("RNCMAC", OP, 90.0, "Mid Length", "Fixed", "20,000 mm", "Yes", "Lined", "Nylon", ("Green", "Navy", "Cream"), "A mac cut with adjustable cuffs."),
    _rain("RNCMNH", KR, 85.0, "Long", "Fixed", "10,000 mm", "Yes", "Unlined", "Polyester", ("Navy", "Olive", "Black"), "Made for the commute.", True),
    _rain("RNCMNP", LD, 60.0, "Mid Length", "Packaway", "5,000 mm", "No", "Unlined", "Nylon", ("Yellow", "Blue", "Red"), "Folds into its own stuff pocket for the bag.", True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Parkas: the hood's trim and the length are drawn; warmth and waterproofing stated.
# --------------------------------------------------------------------------


def _parka(code, brand, price, length, hood, warmth, waterproof, fabric, colors, note, mens=False):
    a_len, p_len = _p("garment_length", "Length", length, "length", LEN[length])
    p_hood = ("hood", "faux_fur" if hood == "Faux-Fur Trim" else "fixed")
    title = _t(length, "Faux-Fur Hooded" if hood == "Faux-Fur Trim" else "Hooded", "Waterproof" if waterproof == "Yes" else "", "Padded Parka")
    hood_clause = "a faux-fur trimmed hood" if hood == "Faux-Fur Trim" else "a hood"
    rated = {"Warm": "cold weather", "Very Warm": "very cold weather", "Extreme": "extreme cold"}[warmth]
    clauses = _and(hood_clause, "a drawcord waist", "two flap pockets")
    desc = (f"A {_lw(length)} {'waterproof ' if waterproof == 'Yes' else ''}padded {fabric.lower()} parka with {clauses}, "
            f"rated for {rated}. {note}")
    return _row(code, title, brand, "Parka", price, desc, colors,
                (a_len, _a("hood", "Hood", "Yes"), _a("hood_type", "Hood type", hood), _a("fill", "Fill", "Padded"),
                 _a("warmth_rating", "Warmth rating", warmth), _a("waterproof", "Waterproof", waterproof), _a("fabric", "Fabric", fabric)),
                (p_len, p_hood), mens)  # fmt: skip


PARKA_ROWS = (
    _parka("PRKFUR", FB, 130.0, "Long", "Faux-Fur Trim", "Very Warm", "No", "Polyester", ("Khaki", "Black", "White"), "Cut generously to wear over a jumper."),
    _parka("PRKWPR", NM, 160.0, "Mid Length", "Fixed", "Warm", "Yes", "Nylon", ("Navy", "Red", "Green"), "Taped seams keep the weather out."),
    _parka("PRKLNG", AO, 150.0, "Long", "Fixed", "Extreme", "Yes", "Nylon", ("Black", "Blue", "Yellow"), "Cut to cover the knee."),
    _parka("PRKSHT", TR, 110.0, "Short", "Faux-Fur Trim", "Warm", "No", "Cotton", ("Olive", "Burgundy", "Cream"), "Cut to the hip for the commute."),
    _parka("PRKMNW", LD, 140.0, "Mid Length", "Fixed", "Warm", "Yes", "Nylon", ("Navy", "Olive", "Black"), "Made for the walk to work.", True),
    _parka("PRKMNF", KR, 170.0, "Long", "Faux-Fur Trim", "Very Warm", "No", "Polyester", ("Green", "Black", "Grey"), "Cut long, with room for a jumper underneath.", True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Puffer jackets: length, hood and the quilting are drawn; fill and packability stated.
# --------------------------------------------------------------------------


def _puffer(code, brand, price, length, hood, fill, quilt, packable, fabric, colors, note):
    a_len, p_len = _p("garment_length", "Length", length, "length", LEN[length])
    a_hood, p_hood = _p("hood", "Hood", hood)
    a_q, p_q = _p("quilting", "Quilting", quilt, "quilt")
    title = _t(length if length != "Regular" else "", "Hooded" if hood == "Yes" else "", "Diamond Quilted" if quilt == "Diamond" else "Channel Quilted", fill, "Puffer Jacket")
    filling = {"Down": "down", "Feather": "feathers", "Synthetic": "synthetic insulation"}[fill]
    lead = _t(length.lower() if length != "Regular" else "", "hooded" if hood == "Yes" else "", fabric.lower())
    desc = (f"{_a_an(lead)} {lead} puffer jacket filled with {filling}, with {quilt.lower()}-stitched baffles. "
            f"{'It packs into a stuff pocket. ' if packable == 'Yes' else ''}{note}")
    return _row(code, title, brand, "Puffer Jacket", price, desc, colors,
                (a_len, a_hood, a_q, _a("fill", "Fill", fill), _a("packable", "Packable", packable), _a("fabric", "Fabric", fabric)),
                (p_len, p_hood, p_q))  # fmt: skip


PUFFER_ROWS = (
    _puffer("PFFDWN", NM, 140.0, "Regular", "Yes", "Down", "Channel", "Yes", "Nylon", ("Black", "Red", "White"), "Light enough to wear under a shell."),
    _puffer("PFFZRP", BW, 80.0, "Cropped", "No", "Synthetic", "Diamond", "No", "Polyester", ("Yellow", "Pink", "Black"), "Sits at the waist, so it layers over high-rise trousers."),
    _puffer("PFFLNG", AO, 180.0, "Longline", "Yes", "Feather", "Channel", "No", "Nylon", ("Navy", "Green", "Charcoal"), "Falls to the thigh for extra cover."),
    _puffer("PFFQLT", CM, 100.0, "Regular", "No", "Synthetic", "Diamond", "Yes", "Polyester", ("Blue", "Olive", "Cream"), "A smooth stand collar and a flat finish."),
)  # fmt: skip

# --------------------------------------------------------------------------
# Gilets: the fill is drawn (channels, diamonds or a pile edge); use is stated.
# --------------------------------------------------------------------------


def _gilet(code, brand, price, fill, use, fabric, colors, note, mens=False):
    a_f, p_f = _p("fill", "Fill", fill, "padding")
    title = _t(fill, use if use == "Performance" else "", "Gilet")
    cloth = _t(fill.lower(), fabric.lower() if fabric != fill else "")
    desc = f"{_a_an(cloth)} {cloth} gilet with a high collar and a zip front, made for {'running and the hills' if use == 'Performance' else 'everyday wear'}. {note}"
    return _row(code, title, brand, "Gilet", price, desc, colors,
                (a_f, _a("use", "Use", use), _a("fabric", "Fabric", fabric)), (p_f,), mens)  # fmt: skip


GILET_ROWS = (
    _gilet("GLTPAD", TR, 55.0, "Padded", "Casual", "Nylon", ("Black", "Navy", "Red"), "Keeps the core warm without bulk."),
    _gilet("GLTFLC", LD, 35.0, "Fleece", "Casual", "Fleece", ("Grey", "Green", "Cream"), "Soft to the touch, with a pocket for the hands."),
    _gilet("GLTQLT", FB, 70.0, "Quilted", "Casual", "Cotton", ("Olive", "Yellow", "White"), "A country look for the lane and the pub."),
    _gilet("GLTPRF", KR, 65.0, "Padded", "Performance", "Polyester", ("Blue", "Black", "Orange"), "Wind-resistant, light and easy to stow."),
    _gilet("GLTMNP", CM, 60.0, "Padded", "Casual", "Nylon", ("Navy", "Black", "Green"), "A warm layer for under a coat.", True),
    _gilet("GLTMNF", OP, 40.0, "Fleece", "Performance", "Fleece", ("Charcoal", "Red", "Blue"), "A midlayer for the trail.", True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Peacoats: length and breasting are drawn; the wool is stated.
# --------------------------------------------------------------------------


def _pea(code, brand, price, length, breast, colors, note):
    a_len, p_len = _p("garment_length", "Length", length, "length", LEN[length])
    a_br, p_br = _p("breasting", "Breasting", breast, "breasted", {"Double-Breasted": "double", "Single-Breasted": "single"}[breast])
    title = _t(length, breast, "Wool Peacoat")
    desc = f"A {_lw(length)} {breast.lower()} wool peacoat with broad lapels and slanted pockets. {note}"
    return _row(code, title, brand, "Peacoat", price, desc, colors, (a_len, a_br, _a("fabric", "Fabric", "Wool")), (p_len, p_br))


PEA_ROWS = (
    _pea("PEAZDB", NM, 150.0, "Short", "Double-Breasted", ("Navy", "Black", "Red"), "The classic sailor's coat."),
    _pea("PEASGL", OP, 130.0, "Mid Length", "Single-Breasted", ("Camel", "Charcoal", "Green"), "Smart enough to wear over a suit."),
    _pea("PEALNG", FB, 170.0, "Long", "Double-Breasted", ("Black", "Burgundy", "Cream"), "Cut to the knee for extra cover."),
    _pea("PEABLU", AO, 140.0, "Mid Length", "Double-Breasted", ("Blue", "Yellow", "White"), "Weighty enough for winter and smart enough for the office."),
)  # fmt: skip

# --------------------------------------------------------------------------
# Utility, chore and field jackets: the pockets and the collar are drawn; the cloth is stated.
# --------------------------------------------------------------------------


def _util(code, brand, price, kind, fabric, pockets, collar, colors, note, mens=False):
    cloth = fabric if fabric != "Cotton" else "Cotton Twill" if kind == "Utility" else "Cotton"
    title = _t(cloth, kind, "Jacket")
    count = {"2": "two", "4": "four"}[pockets]
    desc = f"A boxy {cloth.lower()} {kind.lower()} jacket with {count} patch pockets and a {collar.lower()} collar. {note}"
    return _row(code, title, brand, "Utility Jacket", price, desc, colors,
                (_a("jacket_style", "Jacket style", kind), _a("fabric", "Fabric", fabric), ("pocket_count", "Pocket count", pockets, "C62"), _a("collar", "Collar", collar)),
                (("pockets", pockets), ("collar", collar.lower())), mens)  # fmt: skip


UTIL_ROWS = (
    _util("UTLTWL", LD, 65.0, "Utility", "Cotton", "4", "Point", ("Khaki", "Black", "White"), "Washed for a worn-in feel."),
    _util("UTLCHR", KR, 75.0, "Chore", "Corduroy", "2", "Stand", ("Brown", "Green", "Blue"), "Plain-fronted and easy to layer."),
    _util("UTLFLD", BW, 95.0, "Field", "Cotton", "4", "Stand", ("Olive", "Red", "Navy"), "Cut with room for a jumper underneath."),
    _util("UTLDNM", CM, 70.0, "Chore", "Denim", "2", "Point", ("Blue", "Black", "Yellow"), "Hard-wearing, and softer with every wash."),
    _util("UTLMNC", FB, 80.0, "Utility", "Cotton", "4", "Point", ("Khaki", "Navy", "Red"), "A weekend jacket that goes with everything.", True),
    _util("UTLMNF", NM, 90.0, "Chore", "Corduroy", "2", "Stand", ("Brown", "Black", "Green"), "A soft wale that wears in well.", True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Shackets: a shirt cut as a jacket; a teddy one draws a pile edge; weight is stated.
# --------------------------------------------------------------------------


def _shacket(code, brand, price, fabric, texture, weight, colors, note):
    cloth = "Teddy Fleece" if texture == "Teddy" else "Check Flannel" if fabric == "Flannel" else fabric
    title = _t(cloth, "Shacket")
    desc = f"An oversized {weight.lower()} {cloth.lower()} shacket, a shirt cut as a jacket, with two flap chest pockets. {note}"
    return _row(code, title, brand, "Shacket", price, desc, colors,
                (_a("fabric", "Fabric", fabric), _a("texture", "Texture", texture), _a("garment_weight", "Garment weight", weight)),
                (("teddy", "yes" if texture == "Teddy" else "no"),))  # fmt: skip


SHACKET_ROWS = (
    _shacket("SHKFLN", TR, 45.0, "Flannel", "Brushed", "Midweight", ("Red Check", "Black Check", "Green Check"), "Brushed on the inside for a soft feel."),
    _shacket("SHKCRD", LD, 55.0, "Corduroy", "Ribbed", "Midweight", ("Brown", "Olive", "Blue"), "A wide wale cord in a relaxed cut."),
    _shacket("SHKTDY", OP, 60.0, "Fleece", "Teddy", "Heavyweight", ("Cream", "Green", "Yellow"), "Deep pile on the outside."),
    _shacket("SHKCTN", CM, 40.0, "Cotton", "Plain", "Lightweight", ("White", "Black", "Navy"), "A layer for spring evenings."),
)  # fmt: skip

# --------------------------------------------------------------------------
# Boleros, shrugs and capes: the style and the sleeve are drawn; fabric and occasion stated.
# --------------------------------------------------------------------------


def _bolero(code, brand, price, style, sleeve, fabric, occasion, colors, note):
    sl = {"Long": "long", "Three-Quarter": "three_quarter", "Short": "short", "Sleeveless": "none"}[sleeve]
    title = _t(fabric, style)
    desc = f"A {fabric.lower()} {style.lower()} that leaves the front open, for {occasion.lower()} wear. {note}"
    return _row(code, title, brand, "Bolero", price, desc, colors,
                (_a("bolero_style", "Style", style), _a("fabric", "Fabric", fabric), _a("sleeve_length", "Sleeve length", sleeve), _a("occasion", "Occasion", occasion), _a("garment_length", "Length", "Cropped")),
                (("style", style.lower()), ("sleeve", sl)))  # fmt: skip


BOLERO_ROWS = (
    _bolero("BLRVLV", LD, 40.0, "Bolero", "Long", "Velvet", "Evening", ("Black", "Burgundy", "Green"), "A soft pile that holds its shape."),
    _bolero("BLRKNT", TR, 30.0, "Shrug", "Short", "Knitted", "Casual", ("White", "Pink", "Blue"), "Fine enough to go over a dress."),
    _bolero("BLRSTN", FB, 50.0, "Cape", "Sleeveless", "Satin", "Wedding", ("Cream", "Red", "Yellow"), "Fastened at the neck with a clasp."),
    _bolero("BLRLCE", NM, 45.0, "Bolero", "Short", "Lace", "Wedding", ("White", "Black", "Navy"), "Short sleeves and a scalloped edge."),
)  # fmt: skip

# --------------------------------------------------------------------------
# Windbreakers and anoraks: the zip and the hood are drawn; packability and cloth stated.
# --------------------------------------------------------------------------


def _wind(code, brand, price, zipped, hood, packable, fabric, colors, note, mens=False):
    a_z, p_z = _p("zip_style", "Zip style", zipped, "zip", "full" if zipped == "Full-Zip" else "half")
    style = "Windbreaker" if zipped == "Full-Zip" else "Anorak"
    title = _t("Packable" if packable == "Yes" else "", "Hooded" if hood == "Yes" else "", zipped if zipped == "Half-Zip" else "", style)
    clauses = _and("a full zip" if zipped == "Full-Zip" else "a half zip", "a hood" if hood == "Yes" else "", "an elastic hem",
                   "a pouch pocket" if style == "Anorak" else "")  # fmt: skip
    desc = f"A light {fabric.lower()} {style.lower()} with {clauses}. {'It packs into a stuff pocket. ' if packable == 'Yes' else ''}{note}"
    return _row(code, title, brand, "Windbreaker", price, desc, colors,
                (_a("jacket_style", "Jacket style", style), a_z, _a("hood", "Hood", hood), _a("packable", "Packable", packable), _a("fabric", "Fabric", fabric)),
                (p_z, ("hood", hood.lower())), mens)  # fmt: skip


WIND_ROWS = (
    _wind("WNDFUL", KR, 50.0, "Full-Zip", "No", "Yes", "Nylon", ("Red", "Black", "White"), "Wind-resistant and quick to dry."),
    _wind("WNDHOD", BW, 55.0, "Full-Zip", "Yes", "No", "Polyester", ("Yellow", "Navy", "Green"), "A storm flap sits behind the zip."),
    _wind("WNDANK", CM, 60.0, "Half-Zip", "Yes", "Yes", "Nylon", ("Blue", "Olive", "Pink"), "Pulls on over the head."),
    _wind("WNDHLF", LD, 45.0, "Half-Zip", "No", "No", "Polyester", ("Green", "Black", "Cream"), "A short placket keeps the neck snug."),
    _wind("WNDMNF", FB, 65.0, "Full-Zip", "No", "Yes", "Nylon", ("Navy", "Black", "Olive"), "Made for the commute.", True),
    _wind("WNDMNA", OP, 70.0, "Half-Zip", "Yes", "No", "Polyester", ("Blue", "Red", "Grey"), "Cut roomy enough for a jumper.", True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Hoodies: zip-through or pullover is drawn; the cloth and the fit are stated.
# --------------------------------------------------------------------------


def _hoodie(code, brand, price, zipped, fabric, fit, colors, note, mens=False):
    a_z, p_z = _p("zip_style", "Zip style", zipped, "zip", "through" if zipped == "Zip-Through" else "pullover")
    title = _t(fabric, "Zip Hoodie" if zipped == "Zip-Through" else "Pullover Hoodie")
    cut = f"in {_a_an(fit).lower()} {fit.lower()} cut"
    tail = ", zipped through the front, with a drawcord hood and ribbed cuffs" if zipped == "Zip-Through" else ", with a drawcord hood, ribbed cuffs and a pouch pocket"
    desc = f"A {fabric.lower()} hoodie {cut}{tail}. {note}"
    return _row(code, title, brand, "Hoodie", price, desc, colors,
                (a_z, _a("fabric", "Fabric", fabric), _a("fit", "Fit", fit)), (p_z,), mens)  # fmt: skip


HOODIE_ROWS = (
    _hoodie("HODFLZ", TR, 38.0, "Zip-Through", "Fleece", "Regular", ("Black", "Red", "White"), "Brushed on the inside, so it keeps you warm."),
    _hoodie("HODJPL", CM, 32.0, "Pullover", "Jersey", "Oversized", ("Green", "Yellow", "Grey"), "A soft cotton jersey that drapes well."),
    _hoodie("HODCSH", FB, 85.0, "Pullover", "Cashmere", "Slim", ("Blue", "Cream", "Navy"), "A fine blend that feels light and soft."),
    _hoodie("HODCZP", KR, 42.0, "Zip-Through", "Jersey", "Slim", ("Pink", "Black", "Olive"), "Easy to layer under a jacket."),
    _hoodie("HODMNP", LD, 40.0, "Pullover", "Fleece", "Regular", ("Navy", "Grey", "Green"), "A classic for every day.", True),
    _hoodie("HODMNZ", NM, 45.0, "Zip-Through", "Jersey", "Oversized", ("Black", "Blue", "Red"), "Easy to throw on over a tee.", True),
)  # fmt: skip

ROWS = (*TRENCH_ROWS, *RAIN_ROWS, *PARKA_ROWS, *PUFFER_ROWS, *GILET_ROWS, *PEA_ROWS, *UTIL_ROWS,
        *SHACKET_ROWS, *BOLERO_ROWS, *WIND_ROWS, *HOODIE_ROWS)  # fmt: skip


def rows_of(product_type: str) -> tuple[Row, ...]:
    """The rows of one outerwear type."""
    return tuple(r for r in ROWS if r.product_type == product_type)


def owners_of(product_type: str) -> tuple[tuple[str, str], ...]:
    """The brand owners a type's rows need stated."""
    brands = {r.brand for r in rows_of(product_type)}
    return tuple((b, o) for b, o in BRAND_OWNERS if b in brands)
