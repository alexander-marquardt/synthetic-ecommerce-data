"""Toothpaste (gen#957, slice 2): Beauty > Dental > Toothpaste.

A breadth type: ``derivable`` True, so the scaled build draws more toothpastes from these six by
the benefit and the flavour their titles show. A toothpaste is colorless (its tube is its pack,
as a shampoo's bottle is); each is drawn as a ``toothpaste`` tube (:mod:`kit_grooming`) that
prints the benefit and is striped in the flavour's tone. Each SKU is a tube size in ml.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.grooming_rows import OWNED, TOOTHPASTE
from synthetic_ecommerce_data.domains.retail.hair_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw


def _paste(benefit: str, flavour: str) -> tuple[tuple, ...]:
    return (a("benefit", "Benefit", benefit), a("flavour", "Flavour", flavour))


def _tubes(price: float) -> tuple[tuple[float, float], ...]:
    return ((75.0, price), (100.0, round(price * 1.25, 2)), (125.0, round(price * 1.5, 2)))


def _row(code: str, title: str, brand: str, desc: str, benefit: str, flavour: str, price: float,
         tube: tuple) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, TOOTHPASTE, "Toothpaste", price, "toothpaste",
               desc, (tube,), _paste(benefit, flavour), _tubes(price), "Toothpaste",
               colorless=True, size_key="net_volume_ml",
               params=(("benefit", benefit.lower()), ("flavour", flavour.lower())))  # fmt: skip


ROWS = (
    _row("TPSWHT", "Whitening Mint Toothpaste", "Thornlea Skin",
         "A fluoride paste with fine polishing silica that lifts surface stains from tea and coffee.",
         "Whitening", "Mint", 3.0, cw("White", "#ffffff", "solid", "#2f6b8a")),
    _row("TPSSEN", "Sensitive Cool Mint Toothpaste", "Aldermist",
         "A low-abrasion fluoride paste that builds a shield over exposed dentine, for twice-daily use.",
         "Sensitive", "Cool Mint", 4.5, cw("Pale Blue", "#d6e3ee", "solid", "#2f3a4a")),
    _row("TPSCAV", "Cavity Protection Spearmint Toothpaste", "Pearlbrook",
         "A 1450 ppm fluoride paste for the whole family that strengthens enamel against decay.",
         "Cavity Protection", "Spearmint", 2.0, cw("Pale Green", "#d7e4d3", "solid", "#2f6b4a")),
    _row("TPSGUM", "Gum Care Peppermint Toothpaste", "Sorrel & Salt",
         "A fluoride paste with stannous fluoride that helps stop bleeding at the gum line.",
         "Gum Care", "Peppermint", 4.0, cw("White", "#ffffff", "solid", "#7a3a4a")),
    _row("TPSENA", "Enamel Repair Herbal Toothpaste", "Thornlea Skin",
         "A fluoride paste with calcium that rebuilds weakened enamel, with plant extracts and no artificial sweetener.",
         "Enamel Repair", "Herbal", 5.0, cw("Cream", "#f1e4d6", "solid", "#5a6a3a")),
    _row("TPSFRB", "Fresh Breath Eucalyptus Toothpaste", "Aldermist",
         "A fluoride paste with zinc and a cooling finish that keeps the mouth clean for hours.",
         "Fresh Breath", "Eucalyptus", 3.5, cw("Grey", "#d9d9dc", "solid", "#2e2e33")),
)  # fmt: skip

SPEC = TypeSpec(
    key="toothpaste",
    department=DEPARTMENT,
    product_type="Toothpaste",
    derivable=True,
    rows=ROWS,
    owners=OWNED,
    decoys=(
        Decoy(4, "white toothpaste", "vocabulary", Row(
            "TPSWHS", "Mint Toothpaste for White Smiles", "Pearlbrook", DEPARTMENT, TOOTHPASTE, "Toothpaste", 3.0,
            "toothpaste", "A fluoride mint paste for strong teeth.", (cw("Pale Green", "#d7e4d3", "solid", "#2f6b4a"),),
            _paste("Cavity Protection", "Mint"), _tubes(3.0), "Toothpaste", colorless=True, size_key="net_volume_ml",
            params=(("benefit", "cavity protection"), ("flavour", "mint")))),
        Decoy(6, "red toothpaste", "generic", Row(
            "TPSRDH", "Red Harbour Sensitive Toothpaste", "Aldermist", DEPARTMENT, TOOTHPASTE, "Toothpaste", 4.0,
            "toothpaste", "From the Red Harbour range: a cool mint fluoride paste for sensitive teeth.", (cw("Pale Blue", "#d6e3ee", "solid", "#2f3a4a"),),
            _paste("Sensitive", "Cool Mint"), _tubes(4.0), "Toothpaste", colorless=True, size_key="net_volume_ml",
            params=(("benefit", "sensitive"), ("flavour", "cool mint")))),
    ),
)  # fmt: skip
