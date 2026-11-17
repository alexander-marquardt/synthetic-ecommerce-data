"""The Automotive department's fluids and electrics rows (gen#970, slice 2).

Data only. Each spec file of ``type_specs/`` (``motor_oil.py``, ``coolant.py``, ``jump_starter.py``,
``tire_inflator.py``, ``phone_mount.py``, ``car_charger.py``) takes one list from here, so a spec
stays a few lines and the slice reads in one place. The department's page is
``docs/retail-automotive.md``.

Every brand is invented: Corvane, Ampwick and Holtvane (:mod:`automotive_fluids_brand_styles`), and
slice 1's Kestrova and Drayfield (:mod:`automotive_brand_styles`). A style is one product: an oil's
grade and base, a coolant's chemistry and form, a jump starter's build and peak current, an
inflator's build, a mount's position and hold, a charger's ports. Its SKUs are what a shopper picks
on the product page: a bottle size or a pack size. None of the six carries a color: the jug's or
the case's color is not what is sold, so each row is colorless and its drawing takes the brand's.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    automotive_fluids_brand_styles,  # noqa: F401 -- registers the three house styles
    kit_automotive_electrics,  # noqa: F401 -- registers jump_starter, tire_inflator, phone_mount
)
from synthetic_ecommerce_data.domains.retail.automotive_rows import DRAYFIELD, KESTROVA
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

DEPARTMENT = "Automotive"
CORVANE, AMPWICK, HOLTVANE = "Corvane", "Ampwick", "Holtvane"

#: The brands of the fluids, and of the electrics; all of them invented.
FLUIDS_OWNERS = tuple((b, "third_party") for b in (CORVANE, KESTROVA, DRAYFIELD))
ELECTRICS_OWNERS = tuple((b, "third_party") for b in (AMPWICK, HOLTVANE, DRAYFIELD))

#: The drawing color of each brand's jugs and cases (a colorless row's drawing takes it).
_PACK = {
    CORVANE: cw("Burgundy", "#7a1f2b"),
    KESTROVA: cw("Grey", "#5b6670"),
    DRAYFIELD: cw("Orange", "#e07a1f"),
    AMPWICK: cw("Yellow", "#e8b31c"),
    HOLTVANE: cw("Black", "#2a2a2e"),
}


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _row(code, title, brand, family, leaf, ptype, shape, description, attrs, sizes, size_key,
         price=0.0, params=()) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, (DEPARTMENT, family, leaf), ptype, sizes[0][1] if sizes else price,
               shape, description, (_PACK[brand],), attrs, sizes, colorless=True, params=params,
               size_key=size_key)  # fmt: skip


def _decoy(code: str, title: str, description: str, base: Row, brand: str = "") -> Row:
    """A copy of ``base`` whose title and text mislead while its fields tell the truth."""
    return replace(base, code=code, title=title, description=description, brand=brand or base.brand)


def _sentence(note: str) -> str:
    return f"{note[0].upper()}{note[1:]}."


# --- Motor oil: brand x base x viscosity grade, sold by the jug size in ml ------------------------
_GRADES = {
    "0W-16": "the thinnest common grade, for the newest small engines whose maker calls for it",
    "0W-20": "a thin grade that flows at once on a cold start, called for by many recent small engines",
    "5W-20": "a light grade for many family cars and pickups of the last twenty years",
    "5W-30": "the most common grade for gasoline cars, light at a cold start and steady when hot",
    "10W-30": "a slightly heavier grade for older engines and warm climates",
    "10W-40": "a heavier grade for older and high-revving engines that run hot",
    "5W-40": "a grade many European cars call for, light at a cold start and thick when hot",
    "15W-40": "a heavy grade for work trucks, tractors and generators",
    "20W-50": "a thick grade for classic cars, air-cooled engines and very hot climates",
}
#: (code, oil type, grades, brands with their price factor, 20 L drum too, the base's note).
_BASES = (
    ("F", "Full Synthetic", ("0W-16", "0W-20", "5W-20", "5W-30", "10W-30", "10W-40", "5W-40", "15W-40"),
     ((CORVANE, 1.25), (KESTROVA, 1.1), (DRAYFIELD, 0.9)), True,
     "Its man-made base oil keeps its strength longest between changes, in summer heat and winter cold"),
    ("B", "Synthetic Blend", ("5W-20", "5W-30", "10W-30", "10W-40", "15W-40"),
     ((CORVANE, 1.15), (KESTROVA, 1.0), (DRAYFIELD, 0.85)), False,
     "Its mix of man-made and refined mineral base oils protects better than a plain mineral oil at a lower price than a fully man-made one"),
    ("H", "High Mileage", ("5W-20", "5W-30", "10W-30", "10W-40", "20W-50"),
     ((CORVANE, 1.2), (KESTROVA, 1.05), (DRAYFIELD, 0.9)), False,
     "Seal conditioners swell tired gaskets back into shape, for an engine past 75,000 miles that seeps or burns a little oil"),
    ("C", "Conventional", ("5W-20", "5W-30", "10W-30", "10W-40", "15W-40", "20W-50"),
     ((CORVANE, 1.0), (DRAYFIELD, 0.8)), True,
     "A refined mineral oil for an engine on a short change interval, the plain choice at the lowest price"),
)
_OIL_PRICES = {"F": (9.0, 29.0, 35.0, 119.0), "B": (7.0, 22.0, 26.0), "H": (8.0, 25.0, 30.0), "C": (5.5, 17.0, 20.0, 69.0)}
MOTOR_OILS = tuple(
    _row(f"AUMO{code}{grade.replace('-', '')}{b + 1}", f"{brand} {grade} {oil_type} Motor Oil", brand, "Fluids", "Motor Oil",
         "Motor Oil", "fluid_jug", f"{_sentence(_GRADES[grade])} {note}.",
         (_a("viscosity_grade", "Viscosity grade", grade), _a("oil_type", "Oil type", oil_type)),
         tuple((s, round(p * k, 2)) for s, p in zip(("1000", "4000", "5000", "20000") if drum else ("1000", "4000", "5000"),
                                                    _OIL_PRICES[code], strict=True)), "net_volume_ml")
    for code, oil_type, grades, brands, drum, note in _BASES
    for grade in grades
    for b, (brand, k) in enumerate(brands)
)  # fmt: skip

# --- Coolant: brand x chemistry x form, sold by the jug size in ml --------------------------------
_CHEMISTRIES = (
    ("UN", "Universal", "a formula that mixes safely with whatever coolant is already in the system and suits most makes and models"),
    ("EL", "Extended Life", "an organic acid formula that lasts up to 150,000 miles or five years between flushes"),
    ("HY", "Hybrid", "a formula of silicates and organic acids that guards aluminum quickly and lasts for years"),
    ("AS", "Asian Vehicle", "a phosphate formula made for the cooling systems of Japanese and Korean makes"),
    ("EU", "European Vehicle", "a low-phosphate formula made for the cooling systems of German and other European makes"),
    ("HD", "Heavy Duty", "a formula for work trucks, tractors and generators that protects cylinder liners from pitting"),
    ("SE", "Small Engine", "a formula for motorcycles, ATVs, snowmobiles and outboard motors"),
)
_FORMS = (
    ("C", "Antifreeze Coolant Concentrate", "Concentrate", (9.0, 15.0, 24.0),
     "Mix it half and half with distilled water before it goes in the reservoir"),
    ("R", "50/50 Prediluted Antifreeze Coolant", "Ready to Use", (6.0, 10.0, 16.0),
     "It is already mixed half and half with water, so it pours straight into the reservoir"),
)
_COOLANT_BRANDS = ((CORVANE, 1.2), (KESTROVA, 1.0), (DRAYFIELD, 0.85))
COOLANTS = tuple(
    _row(f"AUCO{c}{f}{b + 1}", f"{brand} {chem} {title}", brand, "Fluids", "Coolant", "Coolant", "fluid_jug",
         f"{_sentence(note)} {form_note}.", (_a("coolant_chemistry", "Coolant chemistry", chem), _a("fluid_form", "Fluid form", form)),
         tuple((s, round(p * k, 2)) for s, p in zip(("1000", "2000", "4000"), prices, strict=True)), "net_volume_ml")
    for c, chem, note in _CHEMISTRIES
    for f, title, form, prices, form_note in _FORMS
    for b, (brand, k) in enumerate(_COOLANT_BRANDS)
)  # fmt: skip

# --- Jump starters: brand x build x peak current, one SKU each ------------------------------------
_STARTERS = (
    ("LC", "Lithium Jump Starter", "Lithium-Ion", "compact", (("1000", 59.0), ("1500", 79.0), ("2000", 99.0)),
     "a pocket-sized pack whose smart clamps stay dead until they sit on the right terminals"),
    ("LU", "Lithium Jump Starter with USB Output", "Lithium-Ion", "compact", (("1500", 89.0), ("2000", 109.0), ("3000", 139.0)),
     "a pack that also charges a phone over USB-C and has a flashlight for a stop at the roadside"),
    ("LW", "Waterproof Lithium Jump Starter", "Lithium-Ion", "compact", (("1500", 99.0), ("2000", 119.0), ("3000", 149.0)),
     "a sealed pack in a rubber shell for a boat, a jet ski or a truck that lives outdoors"),
    ("JB", "Jump Starter Box", "Lead-Acid", "jump_box", (("900", 79.0), ("1200", 99.0), ("1700", 129.0)),
     "a sealed jump box with a carry handle and long cables, the kind a garage keeps by the door"),
    ("HD", "Heavy-Duty Jump Starter", "Lithium-Ion", "jump_box", (("3000", 189.0), ("4000", 229.0), ("5000", 269.0)),
     "a switch between 12 V and 24 V starts trucks, tractors and boats as well as cars"),
)
_STARTER_BRANDS = ((AMPWICK, 1.15), (HOLTVANE, 1.0), (DRAYFIELD, 0.85))
JUMP_STARTERS = tuple(
    _row(f"AUJS{c}{amps}{b + 1}", f"{brand} {amps}A {title}", brand, "Electrics", "Jump Starters", "Jump Starter",
         "jump_starter", f"{_sentence(note)} It starts a flat battery with {amps} amps of peak current.",
         (_a("battery_type", "Battery type", battery), _a("peak_current", "Peak current", f"{amps} A")),
         (), "size", round(price * k, 2), (("style", style),))
    for c, title, battery, style, ratings, note in _STARTERS
    for amps, price in ratings
    for b, (brand, k) in enumerate(_STARTER_BRANDS)
)  # fmt: skip

# --- Tire inflators: brand x build, one SKU each ------------------------------------------------------
_INFLATORS = (
    ("PL", "12V Plug-In Tire Inflator", "12V Socket", "150", "box", 29.0,
     "it plugs into the car's 12 V socket and fills a flat car tire in about eight minutes"),
    ("DA", "Digital Auto-Stop Tire Inflator", "12V Socket", "150", "box", 39.0,
     "set the pressure on its screen and it stops by itself when the tire reaches it"),
    ("CL", "Cordless Tire Inflator", "Rechargeable Battery", "160", "handheld", 59.0,
     "a handheld inflator for car, bike and ball tires with no cord to the dashboard"),
    ("DP", "Dual Power Tire Inflator", "12V Socket or Wall Outlet", "150", "box", 69.0,
     "it runs from the car's 12 V socket on the road or a wall outlet in the garage"),
    ("BC", "Battery Clamp Tire Inflator", "Car Battery Clamps", "150", "box", 79.0,
     "it clamps straight onto the car battery to fill the larger tires of an SUV or a pickup quickly"),
    ("MN", "Mini Tire Inflator", "Rechargeable Battery", "120", "handheld", 35.0,
     "a palm-sized inflator for the glovebox that tops up one tire on a charge"),
)
_INFLATOR_BRANDS = ((AMPWICK, 1.1), (HOLTVANE, 1.0), (DRAYFIELD, 0.85))
TIRE_INFLATORS = tuple(
    _row(f"AUTI{c}{b + 1}", f"{brand} {title}", brand, "Electrics", "Tire Inflators", "Tire Inflator", "tire_inflator",
         f"{_sentence(note)} It reads the pressure in psi and holds up to {psi} psi.",
         (_a("power_source", "Power source", power), _a("max_pressure", "Max pressure", f"{psi} psi")),
         (), "size", round(price * k, 2), (("style", style),))
    for c, title, power, psi, style, price, note in _INFLATORS
    for b, (brand, k) in enumerate(_INFLATOR_BRANDS)
)  # fmt: skip

# --- Phone mounts: brand x position x hold, sold singly or as a 2 pack ----------------------------
_MOUNTS = (
    ("VC", "Air Vent Phone Mount", "Air Vent", "Spring Clamp", "vent", 12.0,
     "it clips onto a vent slat and its spring arms open wide for a phone in a thick case"),
    ("VM", "Magnetic Air Vent Phone Mount", "Air Vent", "Magnetic", "magnetic", 15.0,
     "a strong magnet holds the phone by the thin metal plate that goes inside its case"),
    ("DS", "Dashboard Phone Mount", "Dashboard", "Spring Clamp", "suction", 18.0,
     "a sticky gel suction cup holds to a textured dashboard, on an arm that turns the phone toward the driver"),
    ("WS", "Windshield Phone Mount", "Windshield", "Spring Clamp", "suction", 17.0,
     "a suction cup on the glass and a long arm put the phone at eye level"),
    ("CH", "Cup Holder Phone Mount", "Cup Holder", "Spring Clamp", "cup_holder", 22.0,
     "an expanding base locks into a cup holder and a bendable neck lifts the phone into view"),
    ("CD", "CD Slot Phone Mount", "CD Slot", "Spring Clamp", "vent", 14.0,
     "a blade slides into the CD slot, for a car whose vents are round or awkward"),
    ("WC", "Wireless Charging Phone Mount", "Air Vent", "Motorized Clamp", "vent", 39.0,
     "its arms close by themselves around the phone and charge it without a cable when the phone supports it"),
    ("MD", "Magnetic Dashboard Phone Mount", "Dashboard", "Magnetic", "magnetic", 14.0,
     "a low round pad sticks to the dashboard with adhesive and holds the phone by its metal plate"),
)
_MOUNT_BRANDS = ((HOLTVANE, 1.1), (AMPWICK, 1.0), (DRAYFIELD, 0.85))
PHONE_MOUNTS = tuple(
    _row(f"AUPM{c}{b + 1}", f"{brand} {title}", brand, "Electrics", "Phone Mounts", "Phone Mount", "phone_mount",
         f"{_sentence(note)} It fits phones up to 3.5 inches wide.",
         (_a("mount_position", "Mount position", position), _a("hold_type", "Hold type", hold)),
         (("Single", round(price * k, 2)), ("2 pack", round(price * k * 1.8, 2))), "pack_size", params=(("style", style),))
    for c, title, position, hold, style, price, note in _MOUNTS
    for b, (brand, k) in enumerate(_MOUNT_BRANDS)
)  # fmt: skip

# --- Car chargers: brand x ports and output, sold singly or as a 2 pack ---------------------------
_CHARGERS = (
    ("A2", "Dual USB-A Car Charger", "Two USB-A", "24 W", 9.0, "two older-style ports for two phones on a long drive"),
    ("C1", "USB-C Car Charger", "One USB-C", "20 W", 11.0, "one port that fast-charges a recent phone"),
    ("C3", "30W USB-C Fast Car Charger", "One USB-C", "30 W", 15.0, "one port with enough power to charge a tablet at full speed"),
    ("CA", "USB-C and USB-A Car Charger", "One USB-C and One USB-A", "48 W", 18.0, "one port of each kind, so a new phone and an old cable both charge"),
    ("C2", "Dual USB-C Car Charger", "Two USB-C", "65 W", 25.0, "two ports that share enough power for a laptop and a phone"),
    ("T3", "Three-Port Car Charger", "Two USB-C and One USB-A", "100 W", 32.0, "three ports for a family car, with a laptop on one of them"),
    ("CC", "Car Charger with Coiled USB-C Cable", "One USB-C and One Coiled Cable", "36 W", 19.0, "a coiled cable built in for the driver, and a spare port for a passenger"),
    ("FF", "Flush-Fit Mini Car Charger", "One USB-C and One USB-A", "30 W", 14.0, "a stubby body that sits flush in the socket and stays out of the way"),
)
_CHARGER_BRANDS = ((AMPWICK, 1.1), (HOLTVANE, 1.0), (DRAYFIELD, 0.85))
CAR_CHARGERS = tuple(
    _row(f"AUCC{c}{b + 1}", f"{brand} {title}", brand, "Electrics", "Car Chargers", "Car Charger", "charger",
         f"{_sentence(note)} It plugs into the 12 V socket and gives up to {watts} in all.",
         (_a("ports", "Ports", ports), _a("power_output", "Power output", watts)),
         (("Single", round(price * k, 2)), ("2 pack", round(price * k * 1.8, 2))), "pack_size", params=(("kind", "car"),))
    for c, title, ports, watts, price, note in _CHARGERS
    for b, (brand, k) in enumerate(_CHARGER_BRANDS)
)  # fmt: skip

# --- In-slice text-match decoys (gen#294 classes 1-7): the fields tell the truth -------------------
#: type key -> (class, query, policy, row).
DECOY_ROWS = {
    "motor_oil": (
        (6, "high mileage motor oil", "generic", _decoy("AUDMO1", "Corvane High Mileage Club 5W-30 Full Synthetic Motor Oil",
         "From the High Mileage Club range: a fully man-made base oil in a 5W-30 grade.", MOTOR_OILS[9])),
        (4, "5w-20 motor oil", "vocabulary", _decoy("AUDMO2", "5W-30 Motor Oil, Replaces 5W-20 in Some Older Engines",
         "A 5W-30 oil for an engine whose maker allows it in place of a lighter grade.", MOTOR_OILS[10])),
    ),
    "coolant": (
        (6, "heavy duty coolant", "generic", _decoy("AUDCO1", "Heavy Duty Garage Universal Antifreeze Coolant Concentrate",
         "From the Heavy Duty Garage range: a coolant that suits most makes and models.", COOLANTS[0])),
        (7, "kestrova coolant", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDCO2", "Coolant Concentrate for Kestrova Washer Pumps", "A coolant concentrate sold beside Kestrova washer pumps.", COOLANTS[2])),
    ),
    "jump_starter": (
        (6, "lithium jump starter", "generic", _decoy("AUDJS1", "Ampwick 900A Lithium Run Jump Starter Box",
         "From the Lithium Run range: a sealed lead-acid jump box with a carry handle.", JUMP_STARTERS[27])),
        (7, "holtvane jump starter", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDJS2", "Jump Starter that Charges Holtvane Phone Mounts", "A jump starter whose USB-C port can power a Holtvane wireless mount.", JUMP_STARTERS[3], brand=AMPWICK)),
    ),
    "tire_inflator": (
        (6, "cordless tire inflator", "generic", _decoy("AUDTI1", "Cordless Garage 12V Plug-In Tire Inflator",
         "From the Cordless Garage range: an inflator for the car's 12 V socket.", TIRE_INFLATORS[0])),
        (4, "digital tire inflator", "vocabulary", _decoy("AUDTI2", "Mini Tire Inflator with Digital-Look Dial",
         "A palm-sized inflator with an analog dial printed in a digital style.", TIRE_INFLATORS[15])),
    ),
    "phone_mount": (
        (6, "magnetic phone mount", "generic", _decoy("AUDPM1", "Magnetic North Air Vent Phone Mount",
         "From the Magnetic North range: a vent clip with spring arms.", PHONE_MOUNTS[0])),
        (4, "windshield phone mount", "vocabulary", _decoy("AUDPM2", "Dashboard Phone Mount, Clear of the Windshield",
         "A dashboard mount that keeps the phone low, clear of the driver's view.", PHONE_MOUNTS[6])),
    ),
    "car_charger": (
        (6, "dual usb-c car charger", "generic", _decoy("AUDCC1", "Dual Road USB-C Car Charger",
         "From the Dual Road range: a single-port fast charger for the 12 V socket.", CAR_CHARGERS[3])),
        (7, "ampwick car charger", "brand facet: a brand named in the text is not the product's brand",
         _decoy("AUDCC2", "Car Charger for Ampwick Jump Starters", "A car charger that tops up an Ampwick jump starter on the move.", CAR_CHARGERS[4], brand=HOLTVANE)),
    ),
}
