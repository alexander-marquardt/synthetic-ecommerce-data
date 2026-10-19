"""Class-8 decoys of the large appliances (gen#334): the appliance word in another product's title.

Three queries meet products that are not the appliance. "dishwasher" meets the tablets, salt and
rinse aid that go in one (and, through their text, the mugs, lunch boxes and cutlery whose
descriptions say "Dishwasher safe", which are already in the catalog). "washing machine" meets its
cleaner, a descaler, pods for it and an anti-vibration mat. "fridge" meets storage boxes, a lunch
cooler, cheese crisps, a magnet set and a thermometer. Each
is a real product of its own type, drawn as that product by :mod:`kit_large_appliances` or the
kits; the category policy (Home > Large Appliances) or the department policy drops it. No title
or description names a color. The "mini fridge" cooler is the lunch cooler below.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from decoy_kind import Kind

_H = "Brackenmere Home"
_DISH = ("Cleaning", "Kitchen & Surfaces", "Dish Soap")
_LAUNDRY = ("Cleaning", "Laundry", "Laundry Detergent")
_CF = "Pantry Mill"

#: Each decoy's true type is one the catalog already has (the cleaning types, storage boxes,
#: crisps): the tablets, salt and rinse aid are dishwashing products, the machine cleaner,
#: descaler and pods are laundry products.
KINDS = {
    "la_tablets": Kind("Cleaning & Janitorial", _DISH, "Dish Soap", "tub", _CF, 9.0, colorless=True),
    "la_salt": Kind("Cleaning & Janitorial", _DISH, "Dish Soap", "pouch", _CF, 4.0, colorless=True),
    "la_rinse": Kind("Cleaning & Janitorial", _DISH, "Dish Soap", "bottle", _CF, 3.5, colorless=True),
    "la_cleaner": Kind("Cleaning & Janitorial", _LAUNDRY, "Laundry Detergent", "angled_bottle", _CF, 5.0, colorless=True),
    "la_descaler": Kind("Cleaning & Janitorial", _LAUNDRY, "Laundry Detergent", "box", _CF, 4.5, colorless=True),
    "la_pods": Kind("Cleaning & Janitorial", _LAUNDRY, "Laundry Detergent", "lidded_tub", _CF, 8.0, colorless=True),
    "la_magnets": Kind("Home", ("Home", "Kitchen & Dining", "Fridge Magnets"), "Fridge Magnets", "fridge_magnet", "Hearth & Table", 6.0, colorless=True),
    "la_thermo": Kind("Home", ("Home", "Kitchen & Dining", "Fridge Thermometers"), "Fridge Thermometer", "fridge_thermometer", "Hearth & Table", 7.0, colorless=True),
    "la_mat": Kind("Cleaning & Janitorial", ("Cleaning", "Laundry", "Anti-Vibration Mats"), "Anti-Vibration Mat", "anti_vibration_mat", _CF, 16.0, colorless=True),
    "la_lunch": Kind("Home", ("Home", "Kitchen & Dining", "Lunch Boxes"), "Lunch Box", "box", "Hearth & Table", 14.0),
    "la_boxes": Kind("Home", ("Home", "Storage", "Storage Boxes"), "Storage Boxes", "storage_box", _H, 12.0),
}  # fmt: skip

#: Rows of (number, kind, title, description, color, query, noun, policy, cross).
_ROWS = (
    (309, "la_lunch", "Mini Fridge Lunch Cooler", "An insulated lunch box with an ice pack that keeps food cool for hours.", "Grey", "fridge", "fridge", "category", False),
    (301, "la_tablets", "Dishwasher Tablets, 60 Pack", "All-in-one tablets that clean and add shine to a full load.", "Blue", "dishwasher", "dishwasher", "category", False),
    (302, "la_salt", "Dishwasher Salt, 2 kg", "Coarse salt that softens the water for every cycle.", "White", "dishwasher", "dishwasher", "category", False),
    (303, "la_rinse", "Dishwasher Rinse Aid", "A rinse aid that leaves glasses clear and dry.", "Blue", "dishwasher", "dishwasher", "category", False),
    (304, "la_cleaner", "Washing Machine Cleaner", "A cleaner that clears limescale and odors from the drum.", "Green", "washing machine", "washing", "category", False),
    (305, "la_descaler", "Washing Machine Descaler", "Sachets that remove limescale from the heater and the pipes.", "White", "washing machine", "washing", "category", False),
    (306, "la_pods", "Laundry Pods for Washing Machines", "Single dose pods, made for a load in the drum.", "Blue", "washing machine", "washing", "category", False),
    (310, "crisps", "Fridge Forager Cheese Crisps", "Baked cheese crisps, sold chilled in a resealable pack.", "Red", "fridge", "fridge", "department", True),
    (312, "la_magnets", "Fridge Magnets, Set of 6", "Six small magnets that hold notes and photos on a door.", "Red", "fridge", "fridge", "category", False),
    (313, "la_thermo", "Fridge Thermometer", "A dial thermometer that hangs on a shelf and shows the temperature inside.", "Grey", "fridge", "fridge", "category", False),
    (307, "la_mat", "Washing Machine Anti-Vibration Mat", "Four rubber pads that stop a machine from walking across the floor.", "Black", "washing machine", "washing", "category", False),
    (311, "la_boxes", "Fridge Storage Boxes", "Stackable boxes with lids that keep food fresh on a shelf.", "White", "fridge", "fridge", "category", False),
)  # fmt: skip


def word_rows(d):
    return tuple(
        d(n, kind, title, desc, color, query, noun, policy, cross=cross)
        for n, kind, title, desc, color, query, noun, policy, cross in _ROWS
    )
