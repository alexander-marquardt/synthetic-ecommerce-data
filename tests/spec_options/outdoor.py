"""Camping, cycling and skating: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

from ._shared import THICKNESS

MOVED: dict[str, list[Option]] = {
    "camping_lantern": [Option("brightness_lm", "brightness", "Brightness (lm)")],
    "skateboard": [Option("deck_width_in", "deck_width", "Deck width", "INH")],
    "bicycle": [Option("frame_cm", "frame_size", "Frame size", "CMT")],
    # The options the shared table still held that no shared source's row carries (#413).
    "tent": [Option("berth", "berth", "Berth", "C62")],
    "roll_mat": [THICKNESS],
    # a bike light's output in lumens (gen#959 slice 3), declared by its spec from the start
    "bike_light": [Option("light_output", "light_output", "Light output")],
}
