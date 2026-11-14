"""Hair straighteners (gen#957): Beauty > Hair Care > Hair Straighteners.

A breadth type: ``derivable`` True, so the scaled build draws more straighteners from these four
by the values their titles show (the plate material and the kind). The arms are the SKU's color;
the plate material draws the plates' tone and the kind the body (:func:`kit_hair.hair_straightener`).
Each SKU is a color in a plate width.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.hair_rows import (
    BLACK,
    DEPARTMENT,
    RED,
    STRAIGHTENERS,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a


def _tool(plate: str, kind: str) -> tuple[tuple, ...]:
    return (a("plate_material", "Plate material", plate), a("kind", "Kind", kind))


def _widths(price: float) -> tuple[tuple[str, float], ...]:
    return (("25 mm", price), ("38 mm", price + 5.0))


def _params(plate: str, kind: str) -> tuple[tuple[str, str], ...]:
    return (("plate", plate.lower()), ("kind", kind.lower()))


ROWS = (
    row(
        "HSTCER",
        "Ceramic Salon Hair Straightener",
        "Pearlbrook",
        STRAIGHTENERS,
        "Hair Straightener",
        "hair_straightener",
        "Floating ceramic plates that heat to 230 C in 30 seconds, with a swivel cord and an auto shut-off.",
        _tool("Ceramic", "Salon"),
        _widths(35.0),
        _params("Ceramic", "Salon"),
        "plate_width",
    ),
    row(
        "HSTTIT",
        "Titanium Mini Hair Straightener",
        "Thornlea Skin",
        STRAIGHTENERS,
        "Hair Straightener",
        "hair_straightener",
        "A short titanium straightener for fringes and short hair that fits a handbag.",
        _tool("Titanium", "Mini"),
        _widths(18.0),
        _params("Titanium", "Mini"),
        "plate_width",
    ),
    row(
        "HSTTOU",
        "Tourmaline Cordless Hair Straightener",
        "Sorrel & Salt",
        STRAIGHTENERS,
        "Hair Straightener",
        "hair_straightener",
        "A rechargeable tourmaline straightener with a USB-C charger and up to 40 minutes of styling a charge.",
        _tool("Tourmaline", "Cordless"),
        _widths(55.0),
        _params("Tourmaline", "Cordless"),
        "plate_width",
    ),
    row(
        "HSTTRV",
        "Ceramic Travel Hair Straightener",
        "Veilmoor",
        STRAIGHTENERS,
        "Hair Straightener",
        "hair_straightener",
        "A dual-voltage ceramic straightener with a heat-proof pouch for trips away.",
        _tool("Ceramic", "Travel"),
        _widths(22.0),
        _params("Ceramic", "Travel"),
        "plate_width",
    ),
)

SPEC = TypeSpec(
    key="hair_straightener",
    department=DEPARTMENT,
    product_type="Hair Straightener",
    derivable=True,
    rows=ROWS,
    owners=(("Pearlbrook", "third_party"), ("Thornlea Skin", "third_party"), ("Sorrel & Salt", "third_party"), ("Veilmoor", "third_party")),
    options=(Option("plate_width", "plate_width", "Plate width"),),
    decoys=(
        Decoy(4, "blue hair straightener", "vocabulary", decoy(ROWS[1], "HSTBLP", "Titanium Hair Straightener with Blue Pouch",
              "A short titanium straightener in black, sold with a blue heat-proof pouch.", BLACK)),
        Decoy(6, "white hair straightener", "generic", decoy(ROWS[0], "HSTWHB", "White Bay Ceramic Hair Straightener",
              "From the White Bay range: a ceramic straightener in red.", RED)),
    ),
)  # fmt: skip
