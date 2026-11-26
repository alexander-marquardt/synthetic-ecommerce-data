"""Garden and plants: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

MOVED: dict[str, list[Option]] = {
    "parasol": [Option("canopy_m", "canopy_diameter", "Canopy diameter", "MTR")],
    "garden_furniture_set": [Option("seats", "seats", "Seats", "C62")],
    "garden_hose": [Option("length_m", "item_length", "Item length", "MTR")],
    # a bouquet's stems and a house plant's pot (gen#1115)
    "bouquet": [Option("stem_count", "stem_count", "Stem count", "C62")],
    "house_plant": [Option("pot_size_cm", "pot_size", "Pot size", "CMT")],
}
