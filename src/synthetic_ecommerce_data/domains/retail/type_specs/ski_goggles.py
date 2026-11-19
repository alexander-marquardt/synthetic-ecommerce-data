"""Ski Goggles (gen#959, slice 3): Sports & Outdoors > Winter Sports > Ski Goggles.

A breadth type: ``derivable`` True, so the scaled build draws more ski goggles by the values the titles
show (the lens coating, the lens shape and the fit). The frame is the SKU's color; the lens shape draws a domed, a flat or a toric lens (:func:`kit_outdoor_winter.ski_goggles`). Each SKU is a color in a size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import SKI_GOGGLES
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    _a,
    _row,
    _words,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _attrs(lens_coating: str, lens_shape: str, goggle_fit: str) -> tuple[tuple, ...]:
    return (
        _a("lens_coating", "Lens coating", lens_coating),
        _a("lens_shape", "Lens shape", lens_shape),
        _a("goggle_fit", "Goggle fit", goggle_fit),
    )


def _sizes(price: float) -> tuple[tuple[str, float], ...]:
    return _words(("S", price), ("M", price), ("L", price))


SPEC = TypeSpec(
    key="ski_goggles",
    department="Sports & Outdoors",
    product_type="Ski Goggles",
    derivable=True,
    rows=(
        _row("SKGMSS", "Mirrored Spherical Ski Goggles with Standard Fit", _W, SKI_GOGGLES, "Ski Goggles", 59.0, "ski_goggles",
             "Ski goggles with a mirrored double lens that resists fog, a foam face and a wide silicone strap.",
             (BLACK, WHITE, RED, BLUE), _attrs("Mirrored", "Spherical", "Standard"),
             _sizes(59.0), "size", (("lens_shape", "spherical"),)),
        _row("SKGPCO", "Photochromic Cylindrical Ski Goggles with Over-the-Glasses Fit", _H, SKI_GOGGLES, "Ski Goggles", 79.0, "ski_goggles",
             "Ski goggles whose lens darkens in bright sun, with a deep frame that fits over glasses.",
             (GREEN, YELLOW, BLACK, WHITE), _attrs("Photochromic", "Cylindrical", "Over-the-Glasses"),
             _sizes(79.0), "size", (("lens_shape", "cylindrical"),)),
        _row("SKGPTL", "Polarized Toric Ski Goggles with Low-Bridge Fit", _L, SKI_GOGGLES, "Ski Goggles", 99.0, "ski_goggles",
             "Ski goggles with a polarized lens that cuts glare off the snow and a low-bridge foam for a narrower nose.",
             (BLUE, RED, YELLOW, GREEN), _attrs("Polarized", "Toric", "Low-Bridge"),
             _sizes(99.0), "size", (("lens_shape", "toric"),)),
        _row("SKGMCS", "Mirrored Cylindrical Ski Goggles with Standard Fit", _L, SKI_GOGGLES, "Ski Goggles", 45.0, "ski_goggles",
             "Ski goggles with a mirrored cylindrical lens, vents in the frame and an adjustable strap.",
             (WHITE, BLACK, GREEN, YELLOW), _attrs("Mirrored", "Cylindrical", "Standard"),
             _sizes(45.0), "size", (("lens_shape", "cylindrical"),)),
    ),
)  # fmt: skip
