"""The Automotive department's interior rows (gen#970, slice 3).

Data only. Each spec file of ``type_specs/`` (``seat_cover.py``, ``floor_mat.py``,
``trunk_liner.py``, ``steering_wheel_cover.py``, ``sun_shade.py``) takes one list from here, so a
spec stays a few lines and the slice reads in one place. The department's page is
``docs/retail-automotive.md``.

Every brand is invented and comes from an earlier slice: Holtvane (:mod:`automotive_fluids_brand_styles`),
and Drayfield, Ostrel and Kestrova (:mod:`automotive_brand_styles`). A style is one product: a
brand's cover, mat, liner or shade in one build and material. Its SKUs are what a shopper picks on
the product page: a color times a set, a vehicle size or a rim size. Seat covers, floor mats,
trunk liners and steering wheel covers are sold by color, and each type offers the six main colors
(gen#275) across its styles; a rubber mat or tray comes in the black, grey and beige a rubber is
made in. A sun shade is colorless: its reflective face is what it is, so its drawing takes the
brand's pack color for the trim.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    automotive_fluids_brand_styles,  # noqa: F401 -- registers Holtvane's house style
    kit_automotive_interior,  # noqa: F401 -- registers seat_cover, floor_mat, trunk_liner, ...
)
from synthetic_ecommerce_data.domains.retail.automotive_fluids_rows import HOLTVANE
from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    BLACK,
    BLUE,
    CREAM,
    DRAYFIELD,
    GREEN,
    KESTROVA,
    MAIN,
    OSTREL,
    RED,
    WHITE,
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

DEPARTMENT = "Automotive"
GREY = cw("Grey", "#7d8187")
BEIGE = cw("Beige", "#cdb991")

#: The brands of the interior types; all of them invented.
INTERIOR_OWNERS = tuple((b, "third_party") for b in (HOLTVANE, OSTREL, DRAYFIELD, KESTROVA))

#: The trim color of each brand's sun shades (a colorless row's drawing takes it).
_PACK = {
    HOLTVANE: cw("Black", "#2a2a2e"),
    OSTREL: cw("Green", "#4d7f2f"),
    DRAYFIELD: cw("Orange", "#e07a1f"),
    KESTROVA: cw("Grey", "#5b6670"),
}
#: Three brands sell seat covers, steering wheel covers and sun shades; all four sell mats and liners.
_THREE = ((DRAYFIELD, 0.85), (HOLTVANE, 1.0), (OSTREL, 1.15))
_FOUR = (*_THREE, (KESTROVA, 1.3))


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _sentence(note: str) -> str:
    return f"{note[0].upper()}{note[1:]}."


def _row(code, title, brand, leaf, ptype, shape, description, colors, attrs, sizes, k, style,
         size_key="size") -> Row:  # fmt: skip
    priced = tuple((s, round(p * k, 2)) for s, p in sizes)
    return Row(code, title, brand, DEPARTMENT, (DEPARTMENT, "Interior", leaf), ptype, priced[0][1], shape,
               description, colors or (_PACK[brand],), attrs, priced, colorless=not colors,
               params=(("style", style),), size_key=size_key)  # fmt: skip


def _decoy(code: str, title: str, description: str, base: Row, brand: str = "") -> Row:
    """A copy of ``base`` whose title and text mislead while its fields tell the truth."""
    return replace(base, code=code, title=title, description=description, brand=brand or base.brand)


# --- Seat covers: brand x material, sold by color and by set ---------------------------------------
_PAIR = (("Front Pair", 1.0), ("Full Set", 1.75))
_SEATS = (
    ("NE", "Neoprene Seat Covers", "Neoprene", "Front Bucket", "bucket", MAIN, 79.0, _PAIR,
     "a wetsuit-style cover that shrugs off spills, sand and a wet dog"),
    ("LE", "Leatherette Seat Covers", "Faux Leather", "Front Bucket", "bucket", (BLACK, RED, BLUE, WHITE, BEIGE, GREY), 89.0, _PAIR,
     "a stitched faux leather cover that wipes clean and gives an older car a smarter cabin"),
    ("MS", "Breathable Mesh Seat Covers", "Polyester Mesh", "Front Bucket", "bucket", MAIN, 39.0, _PAIR,
     "an airy mesh cover that keeps a back cool on a long summer drive"),
    ("CA", "Heavy-Duty Canvas Seat Covers", "Canvas", "Front Bucket", "bucket", (BLACK, GREY, GREEN, BEIGE), 69.0, _PAIR,
     "a tough canvas cover for a work truck that takes boots, tools and mud every day"),
    ("SH", "Faux Sheepskin Seat Covers", "Faux Sheepskin", "Front Bucket", "bucket", (CREAM, GREY, BLACK), 99.0, (("Front Pair", 1.0),),
     "a deep-pile faux sheepskin cover, warm in winter and soft on a long drive"),
    ("BE", "Rear Bench Seat Cover", "Polyester", "Rear Bench", "bench", MAIN, 34.0, (("Solid Bench", 1.0), ("60/40 Split Bench", 1.15)),
     "a cover for the back seat with zips that open for a split bench and its seat belts"),
    ("PE", "Waterproof Pet Seat Cover", "Quilted Polyester", "Rear Bench", "bench", (BLACK, GREY, BEIGE, BLUE), 39.0, (("Standard", 1.0), ("XL", 1.25)),
     "a quilted hammock that hooks to both headrests and keeps a dog's hair and paws off the back seat"),
)
SEAT_COVERS = tuple(
    _row(f"AUSC{c}{b + 1}", f"{brand} {title}", brand, "Seat Covers", "Seat Cover", "seat_cover",
         f"{_sentence(note)} It fits most cars, trucks and SUVs and leaves room for the side airbags.", colors,
         (_a("material", "Material", material), _a("seat_cover_type", "Seat cover type", kind)),
         tuple((s, price * f) for s, f in sets), k, style)
    for c, title, material, kind, style, colors, price, sets, note in _SEATS
    for b, (brand, k) in enumerate(_THREE)
)  # fmt: skip

# --- Floor mats: brand x build, sold by color and by set ------------------------------------------
_MAT_SETS = (("Front Pair", 1.0), ("4-Piece Set", 1.6))
_MATS = (
    ("RU", "All-Weather Rubber Floor Mats", "Rubber", "All-Weather", "rubber", (BLACK, GREY, BEIGE), 29.0,
     "deep channels hold rain, snow and road salt off the car's floor until the mat is shaken out"),
    ("TR", "Trim-to-Fit Rubber Floor Mats", "Rubber", "Trim-to-Fit", "rubber", (BLACK, GREY, BEIGE), 24.0,
     "guide lines on the back show where to cut, so one mat fits a compact car or a pickup"),
    ("DD", "Deep Dish Floor Liners", "Thermoplastic", "All-Weather", "rubber", (BLACK, GREY), 59.0,
     "a stiff liner with a raised lip all round that holds a spilled drink and a winter's slush"),
    ("CP", "Carpet Floor Mats", "Nylon Carpet", "Carpet", "carpet", (*MAIN, GREY, BEIGE), 25.0,
     "a tufted carpet mat with a bound edge and a nibbed back that keeps it from sliding"),
    ("PC", "Premium Carpet Floor Mats with Heel Pad", "Plush Carpet", "Carpet", "carpet", (BLACK, GREY, BEIGE, RED, BLUE), 39.0,
     "a thick plush mat with a hard-wearing heel pad where the driver's shoe wears it"),
)
FLOOR_MATS = tuple(
    _row(f"AUFM{c}{b + 1}", f"{brand} {title}", brand, "Floor Mats", "Floor Mat", "floor_mat",
         f"{_sentence(note)} Each mat has holes for the car's floor hooks.", colors,
         (_a("material", "Material", material), _a("floor_mat_type", "Floor mat type", kind)),
         tuple((s, price * f) for s, f in _MAT_SETS), k, style)
    for c, title, material, kind, style, colors, price, note in _MATS
    for b, (brand, k) in enumerate(_FOUR)
)  # fmt: skip

# --- Trunk liners: brand x build, sold by color and by vehicle size -------------------------------
_VEHICLES = (("Sedan Trunk", 1.0), ("Midsize SUV", 1.25), ("Full-Size SUV", 1.5))
_LINERS = (
    ("TY", "Rubber Cargo Tray Liner", "Rubber", "Tray", "tray", (BLACK, GREY), 39.0,
     "a tray with raised walls that holds a leaking grocery bag or a muddy boot off the trunk floor"),
    ("FB", "Waterproof Fabric Cargo Liner", "Oxford Fabric", "Fabric", "fabric", MAIN, 29.0,
     "a waterproof fabric liner that folds away when the trunk is needed clean"),
    ("BP", "Cargo Liner with Bumper Protector", "Quilted Fabric", "Fabric with Bumper Flap", "fabric", (BLACK, GREY, BEIGE, BLUE, RED), 36.0,
     "a quilted liner whose flap folds over the bumper, so a dog jumping in never scratches the paint"),
)
TRUNK_LINERS = tuple(
    _row(f"AUTL{c}{b + 1}", f"{brand} {title}", brand, "Trunk Liners", "Trunk Liner", "trunk_liner",
         f"{_sentence(note)} Pick the size of the car's cargo floor.", colors,
         (_a("material", "Material", material), _a("liner_type", "Liner type", kind)),
         tuple((s, price * f) for s, f in _VEHICLES), k, style)
    for c, title, material, kind, style, colors, price, note in _LINERS
    for b, (brand, k) in enumerate(_FOUR)
)  # fmt: skip

# --- Steering wheel covers: brand x material, sold by color and by rim size -----------------------
_RIMS = (("Standard", 1.0), ("Large", 1.15))
_WHEELS = (
    ("LT", "Leatherette Steering Wheel Cover", "Faux Leather", "stitched", (*MAIN, GREY, BEIGE), 19.0, _RIMS,
     "a stitched faux leather cover that stays cool in summer and warm to the touch in winter"),
    ("SU", "Microfiber Suede Steering Wheel Cover", "Microfiber Suede", "stitched", MAIN, 17.0, _RIMS,
     "a soft suede-feel cover that keeps a firm hold when the hands are damp"),
    ("SI", "Silicone Steering Wheel Cover", "Silicone", "grip", MAIN, 12.0, (("Standard", 1.0),),
     "a stretchy silicone cover that pulls on without tools and washes under the tap"),
    ("SP", "Sport Grip Steering Wheel Cover", "Rubber", "grip", (BLACK, RED, BLUE, GREY), 15.0, _RIMS,
     "molded finger grips at ten and two give a sporty feel and a sure hold"),
)
STEERING_WHEEL_COVERS = tuple(
    _row(f"AUSW{c}{b + 1}", f"{brand} {title}", brand, "Steering Wheel Covers", "Steering Wheel Cover",
         "steering_wheel_cover",
         f"{_sentence(note)} Standard fits a 14.5 to 15 inch wheel; Large fits a 15.5 to 16 inch truck wheel.", colors,
         (_a("material", "Material", material),), tuple((s, price * f) for s, f in rims), k, style)
    for c, title, material, style, colors, price, rims, note in _WHEELS
    for b, (brand, k) in enumerate(_THREE)
)  # fmt: skip

# --- Sun shades: brand x build, one per size, colorless -------------------------------------------
_SHADE_SIZES = (("Standard", 1.0), ("Large", 1.2), ("Jumbo", 1.45))
_SHADES = (
    ("AC", "Accordion Windshield Sun Shade", "Accordion", "accordion", 15.0, _SHADE_SIZES, "size",
     "a reflective shade that folds like an accordion and is held up by the sun visors"),
    ("RB", "Reflective Bubble Windshield Sun Shade", "Accordion", "accordion", 18.0, _SHADE_SIZES, "size",
     "a two-layer shade with an air bubble core that keeps the dashboard and the seats cooler"),
    ("TW", "Twist-Fold Windshield Sun Shade", "Twist-Fold", "twist", 17.0, _SHADE_SIZES, "size",
     "two spring-wire rounds that pop open across the glass and twist down into a small pouch"),
    ("UM", "Umbrella Windshield Sun Shade", "Umbrella", "umbrella", 19.0, (("Standard", 1.0), ("Large", 1.2)), "size",
     "it opens like an umbrella behind the windshield and its handle rests on the dashboard"),
    ("SW", "Side Window Sun Shade", "Side Window Mesh", "side", 12.0, (("2 pack", 1.0), ("4 pack", 1.6)), "pack_size",
     "a static-cling mesh that shades a child in the back seat and still lets the driver see out"),
)
SUN_SHADES = tuple(
    _row(f"AUSS{c}{b + 1}", f"{brand} {title}", brand, "Sun Shades", "Sun Shade", "sun_shade",
         f"{_sentence(note)} It blocks the sun's ultraviolet light.", (),
         (_a("shade_type", "Shade type", kind),), tuple((s, price * f) for s, f in sizes), k, style, size_key)
    for c, title, kind, style, price, sizes, size_key, note in _SHADES
    for b, (brand, k) in enumerate(_THREE)
)  # fmt: skip


def _first(rows: tuple[Row, ...], code: str) -> Row:
    """The row whose code is ``code``: a decoy names its base by code, never by place."""
    return next(r for r in rows if r.code == code)


# --- In-department text-match decoys (gen#294 classes 1-7): the fields tell the truth --------------
#: type key -> (class, query, policy, row).
DECOY_ROWS = {
    "seat_cover": (
        (6, "leather seat covers", "generic", _decoy("AUDSC1", "Leather Lane Breathable Mesh Seat Covers",
         "From the Leather Lane range: an airy polyester mesh cover with no leather in it.", _first(SEAT_COVERS, "AUSCMS2"))),
        (4, "sheepskin seat covers", "vocabulary", _decoy("AUDSC2", "Neoprene Seat Covers, Warmer than Sheepskin",
         "A neoprene cover said to be warmer than a sheepskin one.", _first(SEAT_COVERS, "AUSCNE1"))),
    ),
    "floor_mat": (
        (6, "carpet floor mats", "generic", _decoy("AUDFM1", "Carpet Saver All-Weather Rubber Floor Mats",
         "From the Carpet Saver range: rubber mats that keep the car's own carpet clean.", _first(FLOOR_MATS, "AUFMRU2"))),
        (7, "ostrel floor mats", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDFM2", "Floor Mats to Match Ostrel Seat Covers", "Carpet mats in the shades of Ostrel seat covers.",
                _first(FLOOR_MATS, "AUFMCP2"), brand=HOLTVANE)),
    ),
    "trunk_liner": (
        (6, "rubber trunk liner", "generic", _decoy("AUDTL1", "Rubber Road Waterproof Fabric Cargo Liner",
         "From the Rubber Road range: a waterproof fabric liner with no rubber tray.", _first(TRUNK_LINERS, "AUTLFB2"))),
        (4, "trunk liner with bumper protector", "vocabulary", _decoy("AUDTL2", "Rubber Cargo Tray Liner, No Bumper Flap Needed",
         "A rubber tray whose walls stand clear of the bumper.", _first(TRUNK_LINERS, "AUTLTY1"))),
    ),
    "steering_wheel_cover": (
        (6, "leather steering wheel cover", "generic", _decoy("AUDSW1", "Leather Grain Silicone Steering Wheel Cover",
         "From the Leather Grain range: a silicone cover pressed with a grain texture.", _first(STEERING_WHEEL_COVERS, "AUSWSI2"))),
        (7, "holtvane steering wheel cover", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDSW2", "Steering Wheel Cover to Match Holtvane Seat Covers", "A wheel cover in the shades of Holtvane seat covers.",
                _first(STEERING_WHEEL_COVERS, "AUSWLT1"), brand=DRAYFIELD)),
    ),
    "sun_shade": (
        (6, "umbrella sun shade", "generic", _decoy("AUDSS1", "Umbrella Fold Accordion Windshield Sun Shade",
         "From the Umbrella Fold range: an accordion shade held up by the visors, with no handle.", _first(SUN_SHADES, "AUSSAC2"))),
        (4, "side window sun shade", "vocabulary", _decoy("AUDSS2", "Twist-Fold Windshield Sun Shade, No Side Windows",
         "A shade for the windshield only; it does not fit a side window.", _first(SUN_SHADES, "AUSSTW1"))),
    ),
}
