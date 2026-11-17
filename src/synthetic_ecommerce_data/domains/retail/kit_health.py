"""The Health department's own shapes (gen#1028): red-commit stub, drawn as the old tub."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import Fill, register, tub


def band_colour(nutrient: str) -> str:
    return "#000000"


def supplement_bottle(paint: str, fill: Fill, label: str | None, **_params: str) -> list[str]:
    return tub(paint, fill, label)


register({"supplement_bottle": supplement_bottle})
