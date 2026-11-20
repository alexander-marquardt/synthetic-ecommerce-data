"""Nail polish (gen#957): Beauty > Nails > Nail Polish.

A breadth type: ``derivable`` True, so the scaled build draws more polishes from these six by
the values their titles show (the wear and the finish). The polish in the bottle is the SKU's
color, sold in the six main colors (gen#275); the finish draws the glass's sheen and the wear
the cap (:func:`kit_skin.nail_polish`). Each SKU is a color times the bottle's size in ml.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.hair_rows import BLUE, DEPARTMENT, GREEN, decoy, row
from synthetic_ecommerce_data.domains.retail.skin_rows import NAIL_POLISH, OWNED
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _attrs(wear: str, finish: str) -> tuple[tuple, ...]:
    return (a("wear", "Wear", wear), a("finish", "Finish", finish))


def _bottles(price: float) -> tuple[tuple[str, float], ...]:
    return (("5", round(price * 0.6, 2)), ("10", price), ("15", round(price * 1.35, 2)))


def _params(wear: str, finish: str) -> tuple[tuple[str, str], ...]:
    return (("wear", wear.lower()), ("finish", finish.lower()))


def _row(code: str, title: str, brand: str, desc: str, wear: str, finish: str, price: float):
    return row(code, title, brand, NAIL_POLISH, "Nail Polish", "nail_polish", desc,
               _attrs(wear, finish), _bottles(price), _params(wear, finish), "net_volume_ml")  # fmt: skip


ROWS = (
    _row("NPLQDG", "Quick Dry Gloss Nail Polish", "Veilmoor",
         "A polish with a wide flat brush that covers a nail in one stroke.",
         "Quick Dry", "Gloss", 6.0),
    _row("NPLLWM", "Long Wear Matte Nail Polish", "Pearlbrook",
         "A vegan polish free from formaldehyde and toluene, with no top coat needed.",
         "Long Wear", "Matte", 7.5),
    _row("NPLCRS", "Chip Resistant Shimmer Nail Polish", "Aldermist",
         "A polish with a rounded brush that hugs the cuticle for a clean edge.",
         "Chip Resistant", "Shimmer", 8.0),
    _row("NPLSTG", "Strengthening Glitter Nail Polish", "Thornlea Skin",
         "A polish with keratin and calcium for nails that split and break.",
         "Strengthening", "Glitter", 9.0),
    _row("NPLLWG", "Long Wear Gel Effect Nail Polish", "Fenmere",
         "A polish in a weighted glass bottle, made for a manicure at home.",
         "Long Wear", "Gel Effect", 10.0),
    _row("NPLQDM", "Quick Dry Metallic Nail Polish", "Sorrel & Salt",
         "A polish that goes on smooth and even in two thin coats.",
         "Quick Dry", "Metallic", 7.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="nail_polish",
    department=DEPARTMENT,
    product_type="Nail Polish",
    derivable=True,
    rows=ROWS,
    owners=OWNED,
    decoys=(
        Decoy(4, "red nail polish", "vocabulary", decoy(ROWS[0], "NPLRCP", "Quick Dry Gloss Nail Polish with a Red Brush Tip",
              "A polish in blue whose brush is tipped red, so the bottle is easy to spot.", BLUE)),
        Decoy(6, "pink nail polish", "generic", decoy(ROWS[1], "NPLPKL", "Pink Lagoon Long Wear Matte Nail Polish",
              "From the Pink Lagoon range: a vegan polish in green.", GREEN)),
    ),
)  # fmt: skip
