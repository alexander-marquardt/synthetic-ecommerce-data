"""Deodorants (gen#957): Beauty > Body Care > Deodorants.

A breadth type: ``derivable`` True, so the scaled build draws more deodorants from these six by
the scent and the applicator their titles show. A deodorant is colorless (its stick, can or
bottle is its pack, as a toothpaste's tube is); each is drawn as a ``deodorant``
(:mod:`kit_skin`) whose applicator draws the pack and whose band takes the scent's tone. Each SKU
is a pack's count of deodorants, which ``pack_copies`` draws as that many.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.hair_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.skin_rows import DEODORANTS, OWNED
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw


def _attrs(scent: str, applicator: str, protection: str = "") -> tuple[tuple, ...]:
    out = (a("scent", "Scent", scent), a("applicator", "Applicator", applicator))
    return (*out, a("protection", "Protection", protection)) if protection else out


def _packs(price: float) -> tuple[tuple[str, float], ...]:
    return (("1", price), ("2", round(price * 1.8, 2)), ("3", round(price * 2.5, 2)))


def _params(scent: str, applicator: str, protection: str = "") -> tuple[tuple[str, str], ...]:
    out = (("scent", scent.lower()), ("applicator", applicator.lower()))
    return (*out, ("protection", protection.lower())) if protection else out


def _row(code: str, title: str, brand: str, desc: str, scent: str, applicator: str, price: float,
         pack: tuple, protection: str = "") -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, DEODORANTS, "Deodorant", price, "deodorant",
               desc, (pack,), _attrs(scent, applicator, protection), _packs(price), "Deodorant",
               colorless=True, size_key="units_per_pack",
               params=_params(scent, applicator, protection))  # fmt: skip


ROWS = (
    _row("DEOROL", "Unscented Roll-On Deodorant", "Thornlea Skin",
         "A 48-hour antiperspirant that keeps underarms dry and leaves no residue on clothes.",
         "Unscented", "Roll-On", 3.0, cw("White", "#ffffff", "solid", "#2f6b8a")),
    _row("DEOSTK", "Citrus Stick Deodorant", "Aldermist",
         "An aluminium-free deodorant that keeps underarms fresh through a long day.",
         "Citrus", "Stick", 5.5, cw("Pale Yellow", "#f4ecc4", "solid", "#5a4a1a")),
    _row("DEOSPR", "Sandalwood Spray Deodorant", "Pearlbrook",
         "A 72-hour antiperspirant with protection against sweat and odour.",
         "Sandalwood", "Spray", 4.0, cw("Dark Grey", "#4a4d52", "solid", "#ffffff")),
    _row("DEOGEL", "Aloe Vera Gel Deodorant", "Sorrel & Salt",
         "A deodorant that leaves no marks on dark clothes, tested by dermatologists.",
         "Aloe Vera", "Gel", 4.5, cw("Pale Green", "#d7e4d3", "solid", "#2f6b4a")),
    _row("DEOSEA", "Sea Breeze Spray Deodorant", "Veilmoor",
         "A sporty deodorant for after the gym, with 48-hour odour control.",
         "Sea Breeze", "Spray", 3.5, cw("Pale Blue", "#d6e3ee", "solid", "#2f3a4a")),
    _row("DEOCED", "Cedarwood Stick Deodorant", "Fenmere",
         "A deodorant with odour control free from baking soda, in recyclable packaging.",
         "Cedarwood", "Stick", 7.0, cw("Kraft", "#c9a77c", "solid", "#3a2a1a")),
    # gen#1112 slice 3: rows whose title also shows the protection, Antiperspirant or
    # Aluminum-Free, so the scaled build draws the range in both and 'antiperspirant' finds it.
    _row("DEOAPR", "Unscented Antiperspirant Roll-On Deodorant", "Pearlbrook",
         "A daily deodorant for the underarms, in a pack small enough for a gym bag.",
         "Unscented", "Roll-On", 3.25, cw("Pale Grey", "#e4e6e8", "solid", "#2f3a4a"), "Antiperspirant"),
    _row("DEOAFS", "Citrus Aluminum-Free Stick Deodorant", "Veilmoor",
         "A deodorant made without parabens, sold in a recyclable pack.",
         "Citrus", "Stick", 5.0, cw("Cream", "#efe8d8", "solid", "#5a4a1a"), "Aluminum-Free"),
    _row("DEOAPS", "Sea Breeze Antiperspirant Spray Deodorant", "Thornlea Skin",
         "A deodorant for a long working day, tested by dermatologists.",
         "Sea Breeze", "Spray", 3.75, cw("Navy", "#2f3a4a", "solid", "#ffffff"), "Antiperspirant"),
)  # fmt: skip

SPEC = TypeSpec(
    key="deodorant",
    department=DEPARTMENT,
    product_type="Deodorant",
    derivable=True,
    rows=ROWS,
    owners=OWNED,
    decoys=(
        Decoy(4, "white deodorant", "vocabulary", Row(
            "DEONWM", "No White Marks Gel Deodorant", "Sorrel & Salt", DEPARTMENT, DEODORANTS, "Deodorant", 4.5,
            "deodorant", "A deodorant that leaves no marks on dark clothes, in a black pack.", (cw("Black", "#1f1f22", "solid", "#ffffff"),),
            _attrs("Aloe Vera", "Gel"), _packs(4.5), "Deodorant", colorless=True, size_key="units_per_pack",
            params=_params("Aloe Vera", "Gel"))),
        Decoy(6, "blue deodorant", "generic", Row(
            "DEOBLR", "Blue Ridge Sandalwood Spray Deodorant", "Pearlbrook", DEPARTMENT, DEODORANTS, "Deodorant", 4.0,
            "deodorant", "From the Blue Ridge range: a 72-hour antiperspirant in a dark grey pack.", (cw("Dark Grey", "#4a4d52", "solid", "#ffffff"),),
            _attrs("Sandalwood", "Spray"), _packs(4.0), "Deodorant", colorless=True, size_key="units_per_pack",
            params=_params("Sandalwood", "Spray"))),
    ),
)  # fmt: skip
