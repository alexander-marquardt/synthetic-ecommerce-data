"""Apparel, accessories and luggage: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

from ._shared import WEIGHT

MOVED: dict[str, list[Option]] = {
    "tracksuit": [Option("sold_as", "sold_as", "Sold as")],
    "school_socks": [Option("shoe_size_band", "shoe_size_band", "Shoe size band")],
    # The options the shared table still held that no shared source's row carries (#413).
    "belt": [Option("waist_in", "waist_size", "Waist size", "INH")],
    "hat_cap": [Option("hat_size", "hat_size", "Hat size")],
    "gloves": [Option("glove_size_letter", "glove_size_letter", "Glove size (S to XL)")],
    "suitcase": [WEIGHT, Option("luggage_size", "luggage_size", "Luggage size")],
}
