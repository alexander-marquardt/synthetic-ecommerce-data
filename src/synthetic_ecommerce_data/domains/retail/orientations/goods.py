"""The orientation of each shape ``kit_goods.py`` registers (#1045)."""

ANY: tuple[str, ...] = ("cable_ties", "jumper_cables", "shoe_laces")
UPRIGHT: tuple[str, ...] = (
    "garment_bag",
    "hangers",
    "hook_rail",
    "mesh_bag",
    "pump",
)
#: A coat stand is furniture: level (#1095).
#: Not held or worn, so drawn level (#1101): sofa_cover, throw.
LEVEL: tuple[str, ...] = (
    "coat_stand",
    "sofa_cover",
    "throw",
)
