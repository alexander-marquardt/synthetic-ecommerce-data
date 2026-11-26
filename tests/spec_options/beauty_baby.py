"""Beauty, personal care and baby: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

MOVED: dict[str, list[Option]] = {
    "sun_cream": [Option("spf", "spf", "SPF")],
    "hair_dryer": [Option("attachments", "attachments", "Attachments")],
    "hair_straightener": [Option("plate_width", "plate_width", "Plate width")],
    "razor": [Option("cartridges", "cartridges", "Cartridges", "C62")],
    # a diaper's size, Size 1 to Size 6 (#965)
    "diapers": [Option("diaper_size", "diaper_size", "Diaper size")],
}
