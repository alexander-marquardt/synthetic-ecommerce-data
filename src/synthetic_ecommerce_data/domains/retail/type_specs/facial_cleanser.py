"""Facial cleansers (gen#957): Beauty > Skincare > Cleansers.

A breadth type: ``derivable`` True, so the scaled build draws more cleansers from these six by
the texture and the skin type their titles show. A cleanser is colorless (its bottle, tube or jar
is its pack, as a toothpaste's tube is); each is drawn as a ``facial_cleanser`` (:mod:`kit_skin`)
whose texture draws the pack and whose label prints the skin type. Each SKU is a size in ml.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.hair_rows import DEPARTMENT
from synthetic_ecommerce_data.domains.retail.skin_rows import CLEANSERS, OWNED
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw


def _attrs(texture: str, skin_type: str) -> tuple[tuple, ...]:
    return (a("texture", "Texture", texture), a("skin_type", "Skin type", skin_type))


def _sizes(price: float) -> tuple[tuple[float, float], ...]:
    return ((100.0, price), (150.0, round(price * 1.35, 2)), (200.0, round(price * 1.7, 2)))


def _params(texture: str, skin_type: str) -> tuple[tuple[str, str], ...]:
    return (("texture", texture.lower()), ("skin_type", skin_type.lower()))


def _row(code: str, title: str, brand: str, desc: str, texture: str, skin_type: str, price: float,
         pack: tuple) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, CLEANSERS, "Facial Cleanser", price, "facial_cleanser",
               desc, (pack,), _attrs(texture, skin_type), _sizes(price), "Facial Cleanser",
               colorless=True, size_key="net_volume_ml", params=_params(texture, skin_type))  # fmt: skip


ROWS = (
    _row("FCLFOA", "Foaming Facial Cleanser for Oily Skin", "Thornlea Skin",
         "A daily cleanser with zinc that clears away the day's grime and leaves skin comfortable.",
         "Foaming", "Oily", 8.0, cw("White", "#ffffff", "solid", "#2f6b8a")),
    _row("FCLGEL", "Gel Facial Cleanser for Combination Skin", "Aldermist",
         "A morning and evening cleanser with green tea extract and no soap or added colorants.",
         "Gel", "Combination", 7.0, cw("Pale Blue", "#d6e3ee", "solid", "#2f3a4a")),
    _row("FCLOIL", "Oil Facial Cleanser for Dry Skin", "Pearlbrook",
         "A gentle cleanser that lifts sunscreen and make-up in one step, tested by dermatologists.",
         "Oil", "Dry", 14.0, cw("Amber", "#e0a84a", "solid", "#3a2a1a")),
    _row("FCLMIC", "Micellar Facial Cleanser for Sensitive Skin", "Fenmere",
         "A cleanser with no added fragrance, kind enough to use around the eyes.",
         "Micellar", "Sensitive", 6.0, cw("Pale Pink", "#f2dde3", "solid", "#7a3a4a")),
    _row("FCLBLM", "Balm Facial Cleanser for Normal Skin", "Sorrel & Salt",
         "A cleanser with oat extract and vitamin E that leaves skin soft after every use.",
         "Balm", "Normal", 18.0, cw("Grey", "#d9d9dc", "solid", "#2e2e33")),
    _row("FCLCLY", "Clay Facial Cleanser for Blemish-Prone Skin", "Veilmoor",
         "A cleanser with salicylic acid that keeps pores clear, for use morning and night.",
         "Clay", "Blemish-Prone", 11.0, cw("Pale Green", "#d7e4d3", "solid", "#2f6b4a")),
)  # fmt: skip

SPEC = TypeSpec(
    key="facial_cleanser",
    department=DEPARTMENT,
    product_type="Facial Cleanser",
    derivable=True,
    rows=ROWS,
    owners=OWNED,
    decoys=(
        Decoy(4, "pink facial cleanser", "vocabulary", Row(
            "FCLPGF", "Gel Facial Cleanser with Pink Grapefruit", "Aldermist", DEPARTMENT, CLEANSERS, "Facial Cleanser", 7.0,
            "facial_cleanser", "A morning and evening cleanser scented with grapefruit, in a pale blue pack.", (cw("Pale Blue", "#d6e3ee", "solid", "#2f3a4a"),),
            _attrs("Gel", "Combination"), _sizes(7.0), "Facial Cleanser", colorless=True, size_key="net_volume_ml",
            params=_params("Gel", "Combination"))),
        Decoy(6, "green facial cleanser", "generic", Row(
            "FCLGRF", "Green Fern Balm Facial Cleanser for Normal Skin", "Sorrel & Salt", DEPARTMENT, CLEANSERS, "Facial Cleanser", 18.0,
            "facial_cleanser", "From the Green Fern range: a cleanser with oat extract, in a grey pack.", (cw("Grey", "#d9d9dc", "solid", "#2e2e33"),),
            _attrs("Balm", "Normal"), _sizes(18.0), "Facial Cleanser", colorless=True, size_key="net_volume_ml",
            params=_params("Balm", "Normal"))),
    ),
)  # fmt: skip
