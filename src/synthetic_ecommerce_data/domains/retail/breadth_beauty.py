"""The breadth rows of the Beauty department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_gifts import _scent
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

# --------------------------------------------------------------------------
# Beauty: the hair type and the ingredient vary; the hand wash's fragrance varies.
# --------------------------------------------------------------------------

_CONDIT = ("Beauty", "Hair Care", "Conditioner")
_HANDWASH = ("Beauty", "Bath & Body", "Hand Wash")
_BATH_SALTS = ("Beauty", "Bath & Body", "Bath Salts")
_SHOWER_GEL = ("Beauty", "Bath & Body", "Shower Gel")


def _hair(hair: str, ingredient: str) -> tuple[tuple[str, str, str], ...]:
    return (("hair_type", "Hair type", hair), ("ingredient", "Ingredient", ingredient))


BEAUTY = (
    Row("CNDARG", "Argan Oil Conditioner for Dry Hair", "Mirefield Naturals", "Beauty",
        _CONDIT, "Conditioner", 6.0, "bottle",
        "A rinse-out cream for the mid-lengths and ends. Leave on for one minute.",
        (cw("Cream", "#efe8d8", "solid", "#c98a2e"),), _hair("Dry", "Argan Oil"),
        ((250.0, 6.0), (400.0, 8.0), (500.0, 10.0)), "Conditioner", colorless=True,
        size_key="net_volume_ml"),
    Row("CNDCOC", "Coconut Conditioner for Curly Hair", "Hollin Hair", "Beauty", _CONDIT,
        "Conditioner", 8.0, "bottle",
        "A thick cream that defines the curl pattern and cuts frizz between washes.",
        (cw("White", "#ffffff", "solid", "#7a5a3a"),), _hair("Curly", "Coconut"),
        ((250.0, 8.0), (400.0, 10.5), (500.0, 12.5)), "Conditioner", colorless=True,
        size_key="net_volume_ml"),
    Row("HWSFIG", "Fig Leaf Hand Wash 300ml", "Mirefield Naturals", "Beauty", _HANDWASH,
        "Hand Wash", 5.0, "bottle",
        "A gentle pump wash with plant glycerin, for kitchen or bathroom. Scented with fig leaf.",
        (cw("Green", "#4f7a3a", "solid", "#ffffff"),), _scent("Fig Leaf"), label="Hand Wash",
        colorless=True),
    Row("HWSROS", "Rose & Geranium Hand Wash 500ml", "Hollin Hair", "Beauty", _HANDWASH,
        "Hand Wash", 7.0, "bottle",
        "A refillable glass pump bottle of hand wash. Scented with rose & geranium.",
        (cw("Pink", "#e27d9f", "solid", "#2a2a2e"),), _scent("Rose & Geranium"),
        label="Hand Wash", colorless=True),
    Row("HWSALM", "Sweet Almond Hand Wash Refill 1L", "Mirefield Naturals", "Beauty", _HANDWASH,
        "Hand Wash", 9.0, "bottle",
        "A recycled bottle with enough to refill a pump bottle four times. "
        "Scented with sweet almond.",
        (cw("Cream", "#efe8d8", "solid", "#7a5a3a"),), _scent("Sweet Almond"), label="Refill",
        colorless=True),
    # gen#509: the scent sense of a plant word in the bath. A lavender shower gel comes from
    # the depth family (grocery_families._BODY_SCENTS), which holds neither sage nor eucalyptus.
    Row("BSLLAV", "Lavender Bath Salts 500g", "Mirefield Naturals", "Beauty", _BATH_SALTS,
        "Bath Salts", 7.0, "jar",
        "Mineral salts to stir into a warm bath, a handful at a time. Scented with lavender.",
        (cw("Lilac", "#c8b6d8", "solid", "#ffffff"),), _scent("Lavender"), label="Bath Salts",
        colorless=True),
    Row("BSLSAG", "Sage Bath Salts 500g", "Mirefield Naturals", "Beauty", _BATH_SALTS,
        "Bath Salts", 7.0, "jar",
        "Mineral salts to stir into a warm bath, a handful at a time. Scented with sage.",
        (cw("Green", "#4f7a3a", "solid", "#ffffff"),), _scent("Sage"), label="Bath Salts",
        colorless=True),
    Row("BSLEUC", "Eucalyptus Bath Salts 500g", "Mirefield Naturals", "Beauty", _BATH_SALTS,
        "Bath Salts", 7.0, "jar",
        "Mineral salts to stir into a warm bath, a handful at a time. "
        "Scented with eucalyptus.",
        (cw("Teal", "#2a7f80", "solid", "#ffffff"),), _scent("Eucalyptus"), label="Bath Salts",
        colorless=True),
    Row("SGLSAG", "Sage Shower Gel 250ml", "Mirefield Naturals", "Beauty", _SHOWER_GEL,
        "Shower Gel", 4.0, "bottle", "A creamy shower gel in a recycled bottle. Scented with sage.",
        (cw("Green", "#4f7a3a", "solid", "#ffffff"),), _scent("Sage"), label="Shower Gel",
        colorless=True),
    Row("SGLEUC", "Eucalyptus Shower Gel 250ml", "Mirefield Naturals", "Beauty", _SHOWER_GEL,
        "Shower Gel", 4.0, "bottle",
        "A creamy shower gel in a recycled bottle. Scented with eucalyptus.",
        (cw("Teal", "#2a7f80", "solid", "#ffffff"),), _scent("Eucalyptus"), label="Shower Gel",
        colorless=True),
)  # fmt: skip
