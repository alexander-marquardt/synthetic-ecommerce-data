"""Class-8 decoys of the worn accessories (gen#422): an accessory's word on a product of another root.

The issue names them: "belt" meets a belt sander, "cap" a screw cap on a bottle and a pen cap on a
notebook's loop. "scarf" had no such product yet, so it meets a hanger and a storage box made for
scarves. Each decoy is a real product of a type the catalog already has, drawn as that product; the
department policy drops it from an accessory query.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.decoy_kind import Kind

#: Each decoy's true type, one the catalog already sells.
KINDS = {
    "ac_tool_kit": Kind("Home", ("Home", "DIY & Tools", "Tool Sets", "Tool Kits"), "Tool Kit", "tool_kit", "Calderby & Lune", 79.0, colorless=True),
    "ac_bike_bottle": Kind("Sports & Outdoors", ("Sports & Outdoors", "Cycling", "Bike Bottles"), "Bike Bottle", "bike_bottle", "Wrenfield", 9.0),
    "ac_notebook": Kind("Gifts", ("Gifts", "Stationery", "Notebooks"), "Notebook", "notebook", "Lanternby", 8.0),
    "ac_hanger": Kind("Home", ("Home", "Storage", "Hangers"), "Hanger", "hanger", "Brackenmere Home", 7.0),
    "ac_storage_box": Kind("Home", ("Home", "Storage", "Storage Boxes"), "Storage Box", "storage_box", "Harbour & Pine", 11.0),
}  # fmt: skip

#: Rows of (number, kind, title, description, color, query, noun, accessory type).
_ROWS = (
    (4220, "ac_tool_kit", "Belt Sander Tool Kit", "A belt sander in a carry case with three spare sanding belts for floors and doors.", "Grey", "belt", "belt", "Belt"),
    (4221, "ac_bike_bottle", "Screw Cap Bike Bottle", "A leakproof bottle with a screw cap and a wide mouth, for a long ride.", "Grey", "cap", "cap", "Hat"),
    (4222, "ac_notebook", "Pen Cap Loop Notebook", "A lined notebook with a loop on the spine that holds a pen by its cap.", "Grey", "cap", "cap", "Hat"),
    (4223, "ac_hanger", "Scarf Hanger with Loops", "A hanger with twelve round loops that keeps every scarf in view in the wardrobe.", "Grey", "scarf", "scarf", "Scarf"),
    (4224, "ac_storage_box", "Scarf Storage Box", "A lidded fabric box with sixteen small sections for folded scarves.", "Grey", "scarf", "scarf", "Scarf"),
)  # fmt: skip


def word_rows(d):
    return tuple(
        d(n, kind, title, desc, color, query, noun, "department", cross=True, target=target)
        for n, kind, title, desc, color, query, noun, target in _ROWS
    )
