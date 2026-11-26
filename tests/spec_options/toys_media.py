"""Toys, books and games: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

MOVED: dict[str, list[Option]] = {
    "dolls_house": [Option("house_style", "style", "Style")],
    "book": [Option("format", "format", "Format")],
    # the platform a video game SKU is sold on: PC or an invented console family (gen#1120)
    "video_game": [Option("platform", "platform", "Platform")],
}
