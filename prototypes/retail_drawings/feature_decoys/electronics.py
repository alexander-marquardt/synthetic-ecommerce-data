"""Class-8 decoys of the Electronics department (gen#332): a device word in another product's title.

Five words of the department's shoppers meet products that are not the device. "mouse" meets
the trap and two soft furnishings with a field mouse on them. "tablet" meets dishwasher tablets
and Scottish tablet, the sweet. "monitor" meets baby monitors and a monitor lizard cushion.
"mobile" meets the cot mobile and a mobile coat stand. "charger" meets battery chargers and the
charger plate that sits under a dinner plate. "apple" meets the fruit, its juice, a candle and
the tree: the brand is a real name the catalog keeps (README: Real names), so the fruit is the
clash. Each decoy is a real product of a type the catalog already has, or of a plain kit
shape, drawn as that product; the department policy drops it from an Electronics query. No
title or description names a color.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from decoy_kind import Kind

_H = "Brackenmere Home"
_DIY = ("Home", "DIY & Car")
_NURSERY = ("Toys", "Nursery")

#: Each decoy's true type: a trap, dishwasher tablets, a baby monitor, a cot mobile and a
#: battery charger are household and nursery products; the plate is tableware.
KINDS = {
    "el_trap": Kind("Home", (*_DIY, "Mouse Traps"), "Mouse Trap", "mouse_trap", _H, 4.0),
    "el_tablets": Kind("Cleaning & Janitorial", ("Cleaning", "Kitchen & Surfaces", "Dish Soap"), "Dish Soap", "dishwasher_tablets", "Pantry Mill", 7.0, colorless=True),
    "el_baby_monitor": Kind("Toys", (*_NURSERY, "Baby Monitors"), "Baby Monitor", "baby_monitor", "Little Fernby", 39.0),
    "el_cot_mobile": Kind("Toys", (*_NURSERY, "Cot Mobiles"), "Cot Mobile", "cot_mobile", "Little Fernby", 24.0),
    "el_battery_charger": Kind("Home", (*_DIY, "Battery Chargers"), "Battery Charger", "battery_charger", _H, 29.0),
    "el_plate": Kind("Home", ("Home", "Kitchen & Dining", "Plates"), "Plate", "plate", "Calderby & Lune", 9.0, params=(("kind", "dinner"), ("diameter", "33"), ("finish", ""))),
}  # fmt: skip

#: Rows of (number, kind, title, description, color, query, noun, device type).
_ROWS = (
    (700, "el_trap", "Mouse Trap, Twin Pack", "A wooden snap trap with a sensitive spring, sold as a pair.", "Brown", "mouse", "mouse", "Computer Mouse"),
    (701, "cushion", "Harvest Mouse Cushion", "A soft cushion shaped like a harvest mouse with a long curled tail.", "Brown", "mouse", "mouse", "Computer Mouse"),
    (702, "throw", "Field Mouse Throw", "A woven throw with a pattern of field mice among the grasses.", "Grey", "mouse", "mouse", "Computer Mouse"),
    (703, "el_tablets", "All-in-One Dishwasher Tablets", "A box of tablets that clean and add shine to a full load.", "Blue", "tablet", "tablet", "Tablet"),
    (704, "sweets", "Scottish Tablet Sweets", "Crumbly vanilla tablet, the sugar sweet from Scotland, in a bag.", "Cream", "tablet", "tablet", "Tablet"),
    (705, "chocolate_box", "Scottish Tablet Gift Box", "A gift box of vanilla and whisky tablet, cut into squares.", "Navy", "tablet", "tablet", "Tablet"),
    (706, "el_baby_monitor", "Baby Monitor, Audio Only", "A monitor with a parent unit that carries a baby's sounds across the house.", "White", "monitor", "monitor", "Monitor"),
    (707, "el_baby_monitor", "Video Baby Monitor", "A monitor with a camera for the cot and a small screen for the parent.", "Grey", "monitor", "monitor", "Monitor"),
    (708, "cushion", "Monitor Lizard Cushion", "A soft cushion shaped like a monitor lizard with a striped tail.", "Green", "monitor", "monitor", "Monitor"),
    (709, "el_cot_mobile", "Musical Cot Mobile", "A cot mobile with hanging stars that turn to a lullaby.", "Cream", "mobile", "mobile", "Smartphone"),
    (710, "el_cot_mobile", "Woodland Animals Cot Mobile", "A cot mobile with felt foxes, owls and hedgehogs on a wooden arm.", "Green", "mobile", "mobile", "Smartphone"),
    (711, "stand", "Mobile Coat Stand", "A coat stand on wheels, easy to move from the hall to the bedroom.", "Black", "mobile", "mobile", "Smartphone"),
    (712, "el_battery_charger", "Car Battery Charger", "A charger with clips that tops up a flat car battery overnight.", "Red", "charger", "charger", "Charger"),
    (713, "el_battery_charger", "Motorbike Battery Charger", "A compact charger with clips that keeps a motorbike battery full over winter.", "Yellow", "charger", "charger", "Charger"),
    (714, "el_plate", "Charger Plate, 33 cm", "A wide plate that sits under the dinner plate and sets the table.", "Gold", "charger", "charger", "Charger"),
    (715, "apples", "Bramley Apples, 1 kg", "Large cooking apples, sold loose by the kilo.", "Green", "apple", "apple", "Smartphone"),
    (716, "juice", "Pressed Apple Juice, 1 L", "Cloudy juice from pressed apples, in a carton.", "Yellow", "apple", "apple", "Smartphone"),
    (717, "candle", "Apple Blossom Candle", "A scented candle in a jar, with the smell of apple blossom in spring.", "Pink", "apple", "apple", "Smartphone"),
    (718, "house_plant", "Crab Apple Tree, Potted", "A small crab apple tree in a pot, with blossom in spring and fruit in autumn.", "Green", "apple", "apple", "Tablet"),
)  # fmt: skip


def word_rows(d):
    return tuple(
        d(n, kind, title, desc, color, query, noun, "department", cross=True, device_type=device)
        for n, kind, title, desc, color, query, noun, device in _ROWS
    )
