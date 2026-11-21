"""The orientation of each shape ``kit_lighting.py`` registers (#1045)."""

#: A bulb has no floor to stand on and keeps its tilt.
UPRIGHT: tuple[str, ...] = ("light_bulb",)
#: Every lamp and light fitting, and the lampshade, is level (#1095).
LEVEL: tuple[str, ...] = (
    "ceiling_light",
    "desk_lamp",
    "floor_lamp",
    "lampshade",
    "wall_light",
)
