"""The options more than one spec declares alike: a family imports them (gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

STORAGE = Option("storage_gb", "storage_capacity", "Storage (GB)")
RAM = Option("ram_gb", "ram", "Memory (GB)")
SCREEN = Option("screen_size_in", "screen_size", "Screen size", "INH")
LENGTH = Option("length_m", "item_length", "Item length", "MTR")
DROP = Option("drop_cm", "drop_length", "Drop length", "CMT")
THICKNESS = Option("thickness_mm", "thickness", "Thickness", "MMT")
WEIGHT = Option("weight_kg", "weight", "Weight", "KGM")
VEHICLE = Option("vehicle_fit", "vehicle_fit", "Vehicle fit", None)
COVERAGE = Option("coverage", "coverage", "Coverage", None)
