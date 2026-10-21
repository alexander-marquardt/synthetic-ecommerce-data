"""Class-8 decoys of the Electronics department (gen#332): a device word in another product's title.

Six words of the department's shoppers meet products that are not the device. "mouse" meets
two soft furnishings with a field mouse on them. "tablet" meets dishwasher tablets and Scottish
tablet, the sweet. "monitor" meets a monitor lizard cushion. "mobile" meets a mobile coat stand.
"charger" meets the charger plate that sits under a dinner plate. "apple" meets the fruit, its
juice, a candle and the tree: the brand is a real name the catalog keeps (README: Real names), so the fruit is the
clash. Each decoy is a real product of a type the catalog already has, or of a plain kit
shape, drawn as that product; the department policy drops it from an Electronics query. No
title or description names a color.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from decoy_kind import Kind

#: Each decoy's true type: dishwasher tablets are a cleaning product, the plate is tableware.
KINDS = {
    "el_tablets": Kind("Cleaning & Janitorial", ("Cleaning", "Kitchen & Surfaces", "Dish Soap"), "Dish Soap", "dishwasher_tablets", "Pantry Mill", 7.0, colorless=True),
    "el_plate": Kind("Home", ("Home", "Kitchen & Dining", "Plates"), "Plate", "plate", "Calderby & Lune", 9.0, params=(("kind", "dinner"), ("diameter", "33"), ("finish", ""))),
}  # fmt: skip

#: Rows of (number, kind, title, description, color, query, noun, device type).
_ROWS = (
    (701, "cushion", "Harvest Mouse Cushion", "A soft cushion shaped like a harvest mouse with a long curled tail.", "Brown", "mouse", "mouse", "Computer Mouse"),
    (702, "throw", "Field Mouse Throw", "A woven throw with a pattern of field mice among the grasses.", "Grey", "mouse", "mouse", "Computer Mouse"),
    (703, "el_tablets", "All-in-One Dishwasher Tablets", "A box of tablets that clean and add shine to a full load.", "Blue", "tablet", "tablet", "Tablet"),
    (704, "sweets", "Scottish Tablet Sweets", "Crumbly vanilla tablet, the sugar sweet from Scotland, in a bag.", "Cream", "tablet", "tablet", "Tablet"),
    (705, "chocolate_box", "Scottish Tablet Gift Box", "A gift box of vanilla and whisky tablet, cut into squares.", "Navy", "tablet", "tablet", "Tablet"),
    (708, "cushion", "Monitor Lizard Cushion", "A soft cushion shaped like a monitor lizard with a striped tail.", "Green", "monitor", "monitor", "Monitor"),
    (711, "stand", "Mobile Coat Stand", "A coat stand on wheels, easy to move from the hall to the bedroom.", "Black", "mobile", "mobile", "Smartphone"),
    (714, "el_plate", "Charger Plate, 33 cm", "A wide plate that sits under the dinner plate and sets the table.", "Gold", "charger", "charger", "Charger"),
    (715, "apples", "Bramley Apples, 1 kg", "Large cooking apples, sold loose by the kilo.", "Green", "apple", "apple", "Smartphone"),
    (716, "juice", "Pressed Apple Juice, 1 L", "Cloudy juice from pressed apples, in a carton.", "Yellow", "apple", "apple", "Smartphone"),
    (717, "candle", "Apple Blossom Candle", "A scented candle in a jar, with the smell of apple blossom in spring.", "Pink", "apple", "apple", "Smartphone"),
    (718, "house_plant", "Crab Apple Tree, Potted", "A small crab apple tree in a pot, with blossom in spring and fruit in autumn.", "Green", "apple", "apple", "Tablet"),
    (719, "basket", "Field Mouse Storage Basket", "A fabric basket with a field mouse stitched on the front, for toys and blankets.", "Brown", "mouse", "mouse", "Computer Mouse"),
    (720, "throw", "Monitor Lizard Throw", "A woven throw with a pattern of monitor lizards basking on rocks.", "Green", "monitor", "monitor", "Monitor"),
    (721, "basket", "Monitor Lizard Toy Basket", "A canvas basket with a monitor lizard on the front, for a child's soft toys.", "Green", "monitor", "monitor", "Monitor"),
    (722, "rack", "Mobile Clothes Rack", "A clothes airer on wheels that folds flat and rolls from room to room.", "White", "mobile", "mobile", "Smartphone"),
    (723, "basket", "Mobile Storage Basket on Wheels", "A deep basket on four castors, easy to push around the house.", "Brown", "mobile", "mobile", "Smartphone"),
    (724, "el_plate", "Beaded Charger Plate", "A plate with a beaded rim that sits under the dinner plate for a formal table.", "Grey", "charger", "charger", "Charger"),
    (725, "el_plate", "Woven Rattan Charger Plate", "A round plate of woven rattan that sets off the table and takes the heat of a dish.", "Brown", "charger", "charger", "Charger"),
)  # fmt: skip


def word_rows(d):
    return tuple(
        d(n, kind, title, desc, color, query, noun, "department", cross=True, device_type=device)
        for n, kind, title, desc, color, query, noun, device in _ROWS
    )
