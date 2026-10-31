"""The breadth rows of the Home department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_row import Row, _fab, _mat
from synthetic_ecommerce_data.domains.retail.variants import cw

# --------------------------------------------------------------------------
# Home (growth round 3): the cushion's or towel's fabric and the basket's material
# vary; the shape is drawn in the hero color. A basket draws as a ``storage_box``
# (kit_household.py, gen#200) whose ``material`` param follows a derived material.
# --------------------------------------------------------------------------

_CUSH = ("Home", "Soft Furnishings", "Cushions")
_TOWEL = ("Home", "Bathroom", "Bath Towels")
_BASKET = ("Home", "Storage", "Storage Baskets")
_TWL = (("Hand Towel", 8.0), ("Bath Towel", 14.0), ("Bath Sheet", 22.0))

HOME = (
    Row("CSHVEL", "Velvet Piped Cushion", "Hearth & Table", "Home", _CUSH, "Cushion", 18.0,
        "cushion", "A square cushion with a piped edge and a feather pad. Zip opening.",
        (cw("Teal", "#1c7c7d"), cw("Mustard", "#d4a32a"), cw("Blush", "#e8b9b3"),
         cw("Navy", "#26365c")), _fab("Velvet"), (("45 x 45cm", 18.0), ("55 x 55cm", 24.0))),
    Row("CSHLIN", "Linen Fringed Cushion", "Lanternby", "Home", _CUSH, "Cushion", 22.0,
        "cushion", "A square cushion with a knotted fringe and a hollowfibre pad.",
        (cw("Multi Patchwork", "#c46a4a", "patchwork", "#26365c"), cw("Sage", "#9bb08f"),
         cw("Rust", "#a4502a")), _fab("Linen"),
        (("45 x 45cm", 22.0), ("55 x 55cm", 28.0))),
    Row("CSHBOU", "Boucle Bolster Cushion", "Calderby & Lune", "Home", _CUSH, "Cushion", 26.0,
        "cushion", "A long round bolster with gathered ends, for a sofa arm or a bed.",
        (cw("Cream", "#efe8d8"), cw("Taupe", "#8b7d6b"), cw("Charcoal", "#3b3b3e")),
        _fab("Boucle"), label="Bolster"),
    Row("CSHCHN", "Chenille Oblong Cushion", "Hearth & Table", "Home", _CUSH, "Cushion", 20.0,
        "cushion", "A 30 x 50 cm cushion with a feather pad, for a chair or a window seat.",
        (cw("Ochre", "#c9873a"), cw("Forest", "#2f5a3a"), cw("Dove Grey", "#b5b5b0")),
        _fab("Chenille")),
    Row("CSHCRD", "Corduroy Pleated Cushion", "Lanternby", "Home", _CUSH, "Cushion", 24.0,
        "cushion", "A round cushion pleated to a covered button at its center.",
        (cw("Terracotta", "#c46a4a"), cw("Olive", "#6b6b3a"), cw("Ivory", "#f3ecd9")),
        _fab("Corduroy")),
    Row("TWLORG", "Organic Cotton Bath Towel", "Hearth & Table", "Home", _TOWEL, "Towel", 8.0,
        "bath_towel", "A soft, absorbent towel with a hanging loop. Machine wash at 40.",
        (cw("White", "#ffffff"), cw("Sage", "#9bb08f"), cw("Slate", "#5a6470"),
         cw("Blush", "#e8b9b3")), _fab("Organic Cotton"), _TWL),
    Row("TWLBAM", "Bamboo Bath Towel", "Calderby & Lune", "Home", _TOWEL, "Towel", 10.0,
        "bath_towel", "A silky, quick-drying towel with a woven border and a hanging loop.",
        (cw("Ivory", "#f3ecd9"), cw("Charcoal", "#3b3b3e"), cw("Duck Egg", "#a9c9c4")),
        _fab("Bamboo"), (("Hand Towel", 10.0), ("Bath Towel", 18.0), ("Bath Sheet", 28.0))),
    Row("TWLTRK", "Turkish Cotton Bath Towel", "Lanternby", "Home", _TOWEL, "Towel", 9.0,
        "bath_towel", "A heavy towel woven with long loops, with a hanging loop. Machine wash.",
        (cw("Navy", "#26365c"), cw("White", "#ffffff"), cw("Mustard", "#d4a32a"),
         cw("Stone", "#c9bfae")), _fab("Turkish Cotton"),
        (("Hand Towel", 9.0), ("Bath Towel", 16.0), ("Bath Sheet", 25.0))),
    Row("TWLZRO", "Zero Twist Cotton Bath Towel", "Hearth & Table", "Home", _TOWEL, "Towel",
        11.0, "bath_towel", "A light, fluffy towel that dries fast. Tumble dry low.",
        (cw("Pale Pink", "#f2c9cf"), cw("Teal", "#1c7c7d"), cw("Cloud Grey", "#cfd1d3")),
        _fab("Zero Twist Cotton"),
        (("Hand Towel", 11.0), ("Bath Towel", 19.0), ("Bath Sheet", 30.0))),
    Row("BSKSEA", "Seagrass Lidded Storage Basket", "Lanternby", "Home", _BASKET,
        "Storage Basket", 22.0, "storage_box",
        "A woven basket with a fitted lid and two handles, for blankets or toys.",
        (cw("Natural", "#c9a96e"), cw("Black", "#2a2a2e")), _mat("Seagrass"),
        (("Medium", 22.0), ("Large", 30.0)),
        params=(("form", "box"), ("lid", "yes"), ("material", "seagrass"))),
    Row("BSKRAT", "Rattan Round Storage Basket", "Calderby & Lune", "Home", _BASKET,
        "Storage Basket", 26.0, "storage_box",
        "A round woven basket with cut-out handles, for a shelf or a bathroom floor.",
        (cw("Honey", "#c48a3a"), cw("Natural", "#c9a96e")), _mat("Rattan"),
        (("Small", 18.0), ("Medium", 26.0)),
        params=(("form", "round"), ("lid", "no"), ("material", "rattan"))),
    Row("BSKHYA", "Water Hyacinth Storage Basket", "Hearth & Table", "Home", _BASKET,
        "Storage Basket", 24.0, "storage_box",
        "A chunky woven basket on a metal frame that keeps its shape, with rope handles.",
        (cw("Natural", "#c9a96e"), cw("Grey Wash", "#9a9a94")), _mat("Water Hyacinth"),
        (("Medium", 24.0), ("Large", 32.0)),
        params=(("form", "box"), ("lid", "no"), ("material", "water hyacinth"))),
    Row("BSKFLT", "Felt Storage Basket", "Lanternby", "Home", _BASKET, "Storage Basket", 14.0,
        "storage_box", "A soft folding basket with stitched loop handles, for a cube shelf.",
        (cw("Grey Marl", "#9a9ca0"), cw("Charcoal", "#3b3b3e"), cw("Oat", "#d8c9a8")),
        _mat("Felt"),
        params=(("form", "box"), ("lid", "no"), ("material", "felt"))),
)  # fmt: skip
