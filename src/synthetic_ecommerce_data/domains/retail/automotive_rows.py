"""The Automotive department's car care rows (gen#970, slice 1): wash, wax, wipers, fluids, fresheners.

Data only. Each spec file of ``type_specs/`` (``car_shampoo.py`` ... ``microfiber_towel.py``) takes
one list from here, so a spec stays a few lines and the department reads in one place. The
department's page is ``docs/retail-automotive.md``.

Every brand is invented (:mod:`automotive_brand_styles`). A style is one product: a brand's formula,
blade design, format or scent. Its SKUs are what a shopper picks on the product page: a bottle size,
a blade length, a pack size or a color. A liquid, a blade and an air freshener carry no color (the
bottle's color is not what is sold); a wash mitt and a microfiber towel come in the six main colors.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    automotive_brand_styles,  # noqa: F401 -- registers the four house styles
    kit_automotive,  # noqa: F401 -- registers wiper_blade, fluid_jug, air_freshener, ...
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

DEPARTMENT = "Automotive"
GLOSSMERE, KESTROVA, DRAYFIELD, OSTREL = "Glossmere", "Kestrova", "Drayfield", "Ostrel"

#: Every brand of the department, all of them invented.
AUTOMOTIVE_OWNERS = tuple((b, "third_party") for b in (GLOSSMERE, KESTROVA, DRAYFIELD, OSTREL))

RED = cw("Red", "#c8322b")
BLUE = cw("Blue", "#2f6db5")
GREEN = cw("Green", "#3c8d4f")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2a2a2e")
WHITE = cw("White", "#ffffff", "solid", "#9a9ca0")
MAIN = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)
#: Lambswool is sold in its natural cream: the color is the fleece's own.
CREAM = cw("Cream", "#efe6cf")

#: The drawing color of each brand's bottles and packs (a colorless row's drawing takes it).
_PACK = {
    GLOSSMERE: cw("Navy", "#1d3f6e"),
    KESTROVA: cw("Grey", "#5b6670"),
    DRAYFIELD: cw("Orange", "#e07a1f"),
    OSTREL: cw("Green", "#4d7f2f"),
}

_CARE = (DEPARTMENT, "Car Care")


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _row(code, title, brand, leaf, ptype, shape, description, colors, attrs, sizes, size_key,
         params=(), colorless=True) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, (*_CARE, leaf), ptype, sizes[0][1] if sizes else 0.0, shape,
               description, colors, attrs, sizes, colorless=colorless, params=params,
               size_key=size_key)  # fmt: skip


def _decoy(code: str, title: str, description: str, base: Row, brand: str = "") -> Row:
    """A copy of ``base`` whose title and text mislead while its fields tell the truth."""
    return replace(base, code=code, title=title, description=description, brand=brand or base.brand)


# --- Car shampoo: brand x formula, sold by the bottle size in ml ---------------------------------
_SHAMPOO_FORMULAS = (
    ("SHN", "pH Neutral Car Shampoo", "pH Neutral", "a gentle pH-neutral shampoo that lifts road grime without stripping wax or sealant"),
    ("SHW", "Wash and Wax Car Shampoo", "Wash and Wax", "a shampoo that leaves a thin layer of carnauba wax as it rinses, for a quick shine"),
    ("SHF", "Snow Foam Car Shampoo", "Snow Foam", "a thick pre-wash foam for a foam lance that clings to the paint and softens dirt before a contact wash"),
    ("SHL", "Waterless Car Wash Spray", "Waterless", "a spray-on wash for light dust between washes: wipe it off with a microfiber towel, no hose needed"),
    ("SHC", "Ceramic Car Shampoo", "Ceramic", "a shampoo with a ceramic additive that tops up a coated car and makes water bead"),
)
_SHAMPOO_BRANDS = ((GLOSSMERE, 1.3), (KESTROVA, 1.0), (DRAYFIELD, 0.8), (OSTREL, 1.1))
CAR_SHAMPOOS = tuple(
    _row(f"AU{code}{b + 1}", f"{brand} {title}", brand, "Car Shampoo", "Car Shampoo",
         "trigger_spray" if form == "Waterless" else "bottle",
         f"{note[0].upper()}{note[1:]}. Each bottle washes a family car many times over.",
         (_PACK[brand],), (_a("formula", "Formula", form),),
         (("500", round(7.0 * k, 2)), ("1000", round(11.0 * k, 2)), ("2000", round(18.0 * k, 2))), "net_volume_ml")
    for code, title, form, note in _SHAMPOO_FORMULAS
    for b, (brand, k) in enumerate(_SHAMPOO_BRANDS)
)  # fmt: skip

# --- Car wax: brand x wax, a paste by weight, a liquid or spray by volume -------------------------
_WAX_PRICES = {2: (12.0, 20.0), 3: (7.0, 12.0, 20.0)}  # base price per size, by how many sizes a wax has
_WAXES = (
    ("WXP", "Carnauba Paste Car Wax Pot", "Paste", "Carnauba", "tub", ("200", "400"), "net_weight_g", "a hard carnauba paste worked on with a foam pad for a deep, warm shine that lasts about two months"),
    ("WXL", "Liquid Car Wax", "Liquid", "Synthetic", "bottle", ("250", "500", "1000"), "net_volume_ml", "a synthetic liquid wax that spreads thin by hand or by machine and buffs off without dust"),
    ("WXS", "Spray Car Wax", "Spray", "Carnauba", "trigger_spray", ("250", "500", "1000"), "net_volume_ml", "a quick spray wax for a wet or dry car: mist one panel at a time and buff to a gloss"),
    ("WXC", "Ceramic Spray Sealant", "Spray", "Ceramic", "trigger_spray", ("250", "500", "1000"), "net_volume_ml", "a ceramic sealant spray that bonds to clean paint and keeps water beading for months"),
)
CAR_WAXES = tuple(
    _row(f"AU{code}{b + 1}", f"{brand} {title}", brand, "Car Wax", "Car Wax", shape,
         f"{note[0].upper()}{note[1:]}.", (_PACK[brand],),
         (_a("wax_form", "Wax form", form), _a("wax_type", "Wax type", wax)),
         tuple((s, round(price * k, 2)) for s, price in zip(sizes, _WAX_PRICES[len(sizes)], strict=True)), key)
    for code, title, form, wax, shape, sizes, key, note in _WAXES
    for b, (brand, k) in enumerate(_SHAMPOO_BRANDS)
)  # fmt: skip

# --- Car polish: brand x job, sold by the bottle size in ml ---------------------------------------
_POLISHES = (
    ("PLC", "Polishing Compound", "Polishing Compound", "a cutting compound that levels swirl marks and light oxidation by hand or with a dual-action polisher"),
    ("PLS", "Scratch Remover", "Scratch Remover", "a fine abrasive cream for a single light scratch: rub it in with the pad in the box until the mark fades"),
    ("PLH", "Headlight Restorer", "Headlight Restorer", "a polish and sealant for yellowed plastic headlight lenses that clears the haze and slows its return"),
)
CAR_POLISHES = tuple(
    _row(f"AU{code}{b + 1}", f"{brand} {title}", brand, "Car Polish", "Car Polish", "bottle",
         f"{note[0].upper()}{note[1:]}.", (_PACK[brand],), (_a("polish_type", "Polish type", job),),
         (("100", round(5.0 * k, 2)), ("250", round(9.0 * k, 2)), ("500", round(15.0 * k, 2))), "net_volume_ml")
    for code, title, job, note in _POLISHES
    for b, (brand, k) in enumerate(_SHAMPOO_BRANDS)
)  # fmt: skip

# --- Windshield washer fluid: brand x blend, sold by the jug size in ml ---------------------------
_FLUIDS = (
    ("WFA", "All-Season Windshield Washer Fluid", "All-Season", "Ready to Use", "a ready-to-pour washer fluid that cleans road film in summer and resists freezing in a mild winter"),
    ("WFD", "De-Icer Windshield Washer Fluid", "De-Icer", "Ready to Use", "a winter washer fluid that melts thin frost on the glass and keeps the jets clear in a hard freeze"),
    ("WFB", "Bug Remover Windshield Washer Fluid", "Bug Remover", "Ready to Use", "a summer washer fluid that softens dried insects and tree sap so the wipers clear them"),
    ("WFC", "Concentrated Windshield Washer Fluid", "All-Season", "Concentrate", "a concentrate to mix with water in the reservoir: one jug makes several fills"),
)
WASHER_FLUIDS = tuple(
    _row(f"AU{code}{b + 1}", f"{brand} {title}", brand, "Windshield Washer Fluid", "Windshield Washer Fluid",
         "fluid_jug", f"{note[0].upper()}{note[1:]}.", (_PACK[brand],),
         (_a("blend", "Blend", blend), _a("fluid_form", "Fluid form", form)),
         (("1000", round(3.0 * k, 2)), ("2000", round(5.0 * k, 2)), ("5000", round(9.0 * k, 2))), "net_volume_ml")
    for code, title, blend, form, note in _FLUIDS
    for b, (brand, k) in enumerate(_SHAMPOO_BRANDS)
)  # fmt: skip

# --- Car interior cleaner: brand x surface, a trigger spray sold by size in ml ---------------------
_INTERIOR = (
    ("ICD", "Dashboard Cleaner", "Dashboard", "a matte-finish spray for plastic and vinyl trim that lifts dust and leaves no greasy shine"),
    ("ICU", "Upholstery Cleaner", "Upholstery", "a foaming spray for cloth seats and carpets that lifts coffee, mud and pet marks"),
    ("ICL", "Leather Cleaner", "Leather", "a gentle spray for leather seats and steering wheels that cleans without drying the hide"),
    ("ICG", "Car Glass Cleaner", "Glass", "a streak-free spray for the inside of the windshield and windows, safe on tinted film"),
)
INTERIOR_CLEANERS = tuple(
    _row(f"AU{code}{b + 1}", f"{brand} {title}", brand, "Car Interior Cleaners", "Car Interior Cleaner",
         "trigger_spray", f"{note[0].upper()}{note[1:]}.", (_PACK[brand],), (_a("surface", "Surface", surface),),
         (("250", round(4.0 * k, 2)), ("500", round(6.0 * k, 2)), ("750", round(8.0 * k, 2))), "net_volume_ml")
    for code, title, surface, note in _INTERIOR
    for b, (brand, k) in enumerate(_SHAMPOO_BRANDS)
)  # fmt: skip

# --- Wiper blades: brand x design, sold by the blade length in inches -----------------------------
_FRONT_LENGTHS = ("13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "24", "26", "28")
_REAR_LENGTHS = ("10", "11", "12", "13", "14", "16")
_BLADES = (
    ("WBC", "Conventional Wiper Blade", "Conventional", "Front", "All-Season", "conventional", _FRONT_LENGTHS, 8.0,
     "a steel-frame blade whose bridges press the rubber evenly along a flat or gently curved windshield"),
    ("WBB", "Beam Wiper Blade", "Beam", "Front", "All-Season", "beam", _FRONT_LENGTHS, 14.0,
     "a frameless beam blade that follows the curve of the glass, with no frame for snow to pack into"),
    ("WBH", "Hybrid Wiper Blade", "Hybrid", "Front", "All-Season", "hybrid", _FRONT_LENGTHS, 17.0,
     "a hybrid blade: a beam's even pressure under a spoiler cover that holds it down at highway speed"),
    ("WBR", "Rear Wiper Blade", "Conventional", "Rear", "All-Season", "rear", _REAR_LENGTHS, 7.0,
     "a short rear blade for a hatchback or SUV tailgate"),
)
_WINTER = (
    ("WBW", "Winter Beam Wiper Blade", "Beam", "Front", "Winter", "beam", _FRONT_LENGTHS, 18.0,
     "a winter beam blade in a sealed rubber boot, so ice cannot lock the joints and the edge stays soft in the cold"),
)
_BLADE_BRANDS = ((GLOSSMERE, 1.15), (KESTROVA, 1.0), (DRAYFIELD, 0.85), (OSTREL, 0.95))
_WINTER_BRANDS = ((KESTROVA, 1.0), (DRAYFIELD, 0.85))
_BLADE_INK = cw("Black", "#2a2a2e")


def _blades(designs, brands) -> tuple[Row, ...]:
    return tuple(
        _row(f"AU{code}{b + 1}", f"{brand} {title}", brand, "Wiper Blades", "Wiper Blade", "wiper_blade",
             f"{note[0].upper()}{note[1:]}. It clips onto the common J-hook arm with the adapter in the box.",
             (_BLADE_INK,),
             (_a("blade_type", "Blade type", design), _a("wiper_position", "Wiper position", position),
              _a("season", "Season", season), _a("connector", "Connector", "J-Hook")),
             tuple((n, round((price + 0.25 * i) * k, 2)) for i, n in enumerate(lengths)), "blade_length_in",
             (("style", style),))
        for code, title, design, position, season, style, lengths, price, note in designs
        for b, (brand, k) in enumerate(brands)
    )  # fmt: skip


WIPER_BLADES = _blades(_BLADES, _BLADE_BRANDS) + _blades(_WINTER, _WINTER_BRANDS)

# --- Car air fresheners: brand x format x scent, sold by the pack ---------------------------------
_SCENTS = (
    ("NC", "New Car", cw("Blue", "#4a7fc0")),
    ("VA", "Vanilla", cw("Cream", "#efe0b8")),
    ("PI", "Pine", cw("Green", "#3c7a3f")),
    ("CI", "Citrus", cw("Yellow", "#f2c230")),
    ("CH", "Black Cherry", cw("Red", "#8c1f2e")),
    ("OC", "Ocean Breeze", cw("Teal", "#2f8f8a")),
    ("LA", "Lavender", cw("Purple", "#7b5aa6")),
)
_FORMATS = (
    ("C", "Hanging Car Air Freshener", "Hanging Card", "card", (("Single", 2.0), ("3 pack", 5.0)), "a scented card on an elastic string for the mirror or a headrest; it lasts about four weeks"),
    ("V", "Vent Clip Car Air Freshener", "Vent Clip", "vent_clip", (("Single", 4.0), ("2 pack", 7.0)), "a clip for an air vent that releases its scent faster when the fan is on; it lasts about six weeks"),
    ("G", "Gel Can Car Air Freshener", "Gel Can", "gel_can", (("Single", 3.5),), "a gel can for a cup holder or under a seat with a twist lid that sets how strong it smells"),
)
_FRESH_BRANDS = ((OSTREL, 1.0), (DRAYFIELD, 0.85), (GLOSSMERE, 1.2))
AIR_FRESHENERS = tuple(
    _row(f"AUF{f}{s}{b + 1}", f"{brand} {scent} {title}", brand, "Car Air Fresheners", "Car Air Freshener",
         "air_freshener", f"{note[0].upper()}{note[1:]}. Its scent is {scent.lower()}.",
         (color,), (_a("freshener_format", "Freshener format", fmt), _a("scent", "Scent", scent)),
         tuple((n, round(p * k, 2)) for n, p in packs), "pack_size", (("style", style),))
    for f, title, fmt, style, packs, note in _FORMATS
    for s, scent, color in _SCENTS
    for b, (brand, k) in enumerate(_FRESH_BRANDS)
)  # fmt: skip

# --- Wash mitts and microfiber towels: brand x product, sold by color ------------------------------
_CLOTH_BRANDS = ((GLOSSMERE, 1.2), (OSTREL, 1.0), (DRAYFIELD, 0.8))
WASH_MITTS = tuple(
    _row(f"AUMT{c}{b + 1}", f"{brand} {title}", brand, "Wash Mitts", "Wash Mitt", "wash_mitt",
         f"{note[0].upper()}{note[1:]}. It has an elastic cuff and goes in the washing machine.",
         colors, (_a("material", "Material", material),), (), "size", (("style", style),), colorless=False)
    for c, title, material, style, colors, note in (
        ("C", "Chenille Microfiber Wash Mitt", "Chenille Microfiber", "chenille", MAIN,
         "a mitt of soft microfiber noodles that hold suds and pull grit away from the paint"),
        ("L", "Lambswool Wash Mitt", "Lambswool", "lambswool", (CREAM,),
         "a deep-pile natural lambswool mitt, the gentlest wash for soft or dark paint"),
    )
    for b, (brand, _k) in enumerate(_CLOTH_BRANDS)
)  # fmt: skip
WASH_MITTS = tuple(replace(r, price=round((9.0 if "Chenille" in r.title else 16.0) * dict(_CLOTH_BRANDS)[r.brand], 2),
                           sizes=()) for r in WASH_MITTS)  # fmt: skip

_TOWELS = (
    ("D", "Microfiber Drying Towel", "Drying Towel", "folded", "dimensions", (("40 x 60 cm", 8.0), ("60 x 90 cm", 14.0)),
     "a thick twisted-loop towel that soaks up the water on a whole panel in one pass"),
    ("A", "All-Purpose Microfiber Cloths", "All-Purpose Cloth", "stack", "pack_size", (("6 pack", 7.0), ("12 pack", 12.0)),
     "soft edgeless cloths for wax removal, wheels and the interior"),
    ("G", "Microfiber Glass Cloths", "Glass Cloth", "stack", "pack_size", (("3 pack", 6.0), ("6 pack", 10.0)),
     "flat low-pile cloths that buff glass and mirrors without lint or streaks"),
)
MICROFIBER_TOWELS = tuple(
    _row(f"AUTW{t}{b + 1}", f"{brand} {title}", brand, "Microfiber Towels", "Microfiber Towel", "microfiber_towel",
         f"{note[0].upper()}{note[1:]}.", MAIN, (_a("towel_type", "Towel type", kind), _a("material", "Material", "Microfiber")),
         tuple((n, round(p * k, 2)) for n, p in sizes), key, (("style", style),), colorless=False)
    for t, title, kind, style, key, sizes, note in _TOWELS
    for b, (brand, k) in enumerate(_CLOTH_BRANDS)
)  # fmt: skip

# --- In-department text-match decoys (gen#294 classes 1-7): the fields tell the truth --------------
#: type key -> (class, query, policy, row).
DECOY_ROWS = {
    "car_shampoo": (
        (6, "ceramic car shampoo", "generic", _decoy("AUDSH1", "Ceramic Coast pH Neutral Car Shampoo",
         "From the Ceramic Coast range: a pH-neutral shampoo with no ceramic additive.", CAR_SHAMPOOS[0])),
        (7, "kestrova car shampoo", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDSH2", "Snow Foam Car Shampoo for Kestrova Foam Lances", "A snow foam made to run through a Kestrova foam lance.", CAR_SHAMPOOS[8], brand=DRAYFIELD)),
    ),
    "car_wax": (
        (4, "paste wax", "vocabulary", _decoy("AUDWX1", "Liquid Car Wax with Paste-Hard Finish",
         "A synthetic liquid wax that dries to a hard finish.", CAR_WAXES[4])),
        (6, "carnauba wax", "generic", _decoy("AUDWX2", "Carnauba Gold Ceramic Spray Sealant",
         "From the Carnauba Gold range: a ceramic sealant spray.", CAR_WAXES[12])),
    ),
    "car_polish": (
        (6, "headlight restorer", "generic", _decoy("AUDPL1", "Headlight Line Scratch Remover",
         "From the Headlight Line range: a cream for a light scratch in the paint.", CAR_POLISHES[4])),
        (7, "glossmere polish", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDPL2", "Polishing Compound for Glossmere Pads", "A cutting compound sized for Glossmere polishing pads.", CAR_POLISHES[2])),
    ),
    "washer_fluid": (
        (6, "de-icer washer fluid", "generic", _decoy("AUDWF1", "De-Icer Pro Bug Remover Windshield Washer Fluid",
         "From the De-Icer Pro range: a summer washer fluid for insects and sap.", WASHER_FLUIDS[8])),
        (4, "concentrated washer fluid", "vocabulary", _decoy("AUDWF2", "Concentrated-Clean All-Season Windshield Washer Fluid",
         "A ready-to-pour washer fluid with a concentrated cleaning blend.", WASHER_FLUIDS[0])),
    ),
    "car_interior_cleaner": (
        (6, "leather cleaner", "generic", _decoy("AUDIC1", "Leather Look Dashboard Cleaner",
         "From the Leather Look range: a matte spray for plastic and vinyl trim.", INTERIOR_CLEANERS[0])),
        (7, "ostrel interior cleaner", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDIC2", "Upholstery Cleaner for Ostrel Seat Brushes", "A foaming seat cleaner to work in with an Ostrel seat brush.", INTERIOR_CLEANERS[5])),
    ),
    "wiper_blade": (
        (6, "snow wiper blade", "generic", _decoy("AUDWB1", "Snow Ridge Beam Wiper Blade",
         "From the Snow Ridge range: an all-season beam blade.", WIPER_BLADES[5])),
        (4, "rear wiper blade", "vocabulary", _decoy("AUDWB2", "Hybrid Wiper Blade with Rear-Mounted Spoiler",
         "A front hybrid blade whose spoiler sits at the rear edge of the cover.", WIPER_BLADES[9])),
    ),
    "car_air_freshener": (
        (6, "vanilla air freshener", "generic", _decoy("AUDAF1", "Vanilla Sky Pine Hanging Car Air Freshener",
         "From the Vanilla Sky range: a hanging card with a pine scent.", AIR_FRESHENERS[6])),
        (4, "vent clip air freshener", "vocabulary", _decoy("AUDAF2", "Gel Can Car Air Freshener, Fits Beside a Vent Clip",
         "A gel can for a cup holder that sits beside a phone vent clip.", AIR_FRESHENERS[42])),
    ),
    "wash_mitt": (
        (6, "lambswool wash mitt", "generic", _decoy("AUDMT1", "Lambswool Soft Chenille Microfiber Wash Mitt",
         "From the Lambswool Soft range: a chenille microfiber mitt.", WASH_MITTS[0])),
        (5, "red wash mitt", "color", _decoy("AUDMT2", "Red Line Chenille Microfiber Wash Mitt",
         "From the Red Line range: a blue chenille microfiber mitt.", replace(WASH_MITTS[1], colors=(BLUE,)))),
    ),
    "microfiber_towel": (
        (6, "glass cloth", "generic", _decoy("AUDTW1", "Glass Finish Microfiber Drying Towel",
         "From the Glass Finish range: a twisted-loop drying towel.", MICROFIBER_TOWELS[0])),
        (5, "yellow microfiber towel", "color", _decoy("AUDTW2", "Yellow Label All-Purpose Microfiber Cloths",
         "From the Yellow Label range: green all-purpose cloths.", replace(MICROFIBER_TOWELS[3], colors=(GREEN,)))),
    ),
}
