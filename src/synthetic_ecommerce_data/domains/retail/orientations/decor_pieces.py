"""The orientation of each shape ``kit_decor_pieces.py`` registers (#1045)."""

UPRIGHT: tuple[str, ...] = ("faux_floral",)

#: Wall art hangs level, and a set of panels or of tabletop pieces is drawn as several items,
#: which overlap on a slant (#884).
#: Not held or worn, so drawn level (#1101): fountain, garden_statue.
LEVEL: tuple[str, ...] = (
    "decor_object",
    "fountain",
    "garden_statue",
    "wall_art",
)
