"""The breadth rows of the Beauty department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_gifts import _scent
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import _shades, _tones, cw

# --------------------------------------------------------------------------
# Beauty: the hair type and the ingredient vary; the hand wash's fragrance varies; a lipstick
# takes another finish and a foundation another formula.
# --------------------------------------------------------------------------

_CONDIT = ("Beauty", "Hair Care", "Conditioner")
_HANDWASH = ("Beauty", "Bath & Body", "Hand Wash")
_BATH_SALTS = ("Beauty", "Bath & Body", "Bath Salts")
_SHOWER_GEL = ("Beauty", "Bath & Body", "Shower Gel")


_LIPS = ("Beauty", "Make-Up", "Lips", "Lipstick")
_FOUNDATION = ("Beauty", "Make-Up", "Face", "Foundation")


def _hair(hair: str, ingredient: str) -> tuple[tuple[str, str, str], ...]:
    return (("hair_type", "Hair type", hair), ("ingredient", "Ingredient", ingredient))


def _finish(finish: str) -> tuple[tuple[str, str, str], ...]:
    return (("finish", "Finish", finish),)


def _formula(formula: str) -> tuple[tuple[str, str, str], ...]:
    return (("formula", "Formula", formula),)


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
    # #851: a shade is a SKU of one lipstick or foundation, and a line is split by its finish or
    # its formula, as a beauty retailer lists them. Each finish and formula here is a value the
    # leaf's derived styles may take (the satin and matte lipsticks are in ``variants.BEAUTY``).
    Row("LIPCRM", "Kestlewood Cream Lipstick", "Kestlewood Cosmetics", "Beauty", _LIPS,
        "Lipstick", 13.0, "lipstick", "A cushiony cream lipstick with full color in one sweep.",
        _shades("Light Rose; Dark Purple; Red; Soft Lilac; Tan; Warm Nude; "
                "Raspberry; Dark Burgundy",
                "d98c95 7a3b4f b3132b b48a96 a0522d c49a83 c72c58 5b1a2a"),
        _finish("Cream")),
    Row("LIPSHR", "Kestlewood Sheer Lipstick", "Kestlewood Cosmetics", "Beauty", _LIPS,
        "Lipstick", 12.0, "lipstick",
        "A light, glossy lipstick that gives a wash of color you can layer.",
        _shades("Sheer Pink; Sheer Rose; Sheer Red; Sheer Nude; Sheer Purple; Sheer Coral",
                "e8a3a8 e58fa8 c0392b d8b4a0 8e4a6b f08070"),
        _finish("Sheer")),
    Row("LIPMET", "Kestlewood Metallic Lipstick", "Kestlewood Cosmetics", "Beauty", _LIPS,
        "Lipstick", 15.0, "lipstick", "A foiled lipstick with a high-shine metallic finish.",
        _shades("Dark Copper; Rose Gold; Copper; Maroon; Purple; Champagne Pink",
                "a0663a c98b7c b0643c 7b1e2a 7d4e8a e3b7a8"),
        _finish("Metallic")),
    Row("FNDCRM", "Kestlewood Cream Foundation 30ml", "Kestlewood Cosmetics", "Beauty",
        _FOUNDATION, "Foundation", 30.0, "bottle",
        "A rich foundation with full coverage and a soft matte finish.",
        _tones("1N 2N 3N 3W 4N 5N 5W 6N 7N 8N 9N 10N 11N 12N"), _formula("Cream"),
        label="Foundation"),
    Row("FNDMSE", "Airy Mousse Foundation 30ml", "Kestlewood Cosmetics", "Beauty", _FOUNDATION,
        "Foundation", 34.0, "bottle", "A light foundation that blends out to a soft, airy finish.",
        _tones("1C 2N 3C 4N 5W 6N 7C 8N 9W 10N"), _formula("Mousse"), label="Foundation"),
    Row("FNDLIQ", "Weightless Liquid Foundation 30ml", "Kestlewood Cosmetics", "Beauty",
        _FOUNDATION, "Foundation", 26.0, "bottle",
        "A thin, buildable foundation that wears light all day.",
        _tones("1N 1W 2N 3N 4C 4N 5N 6W 7N 8N 9N 10W 11N 12N 13N"), _formula("Liquid"),
        label="Foundation"),
    Row("FNDSER", "Dewy Serum Foundation 30ml", "Kestlewood Cosmetics", "Beauty", _FOUNDATION,
        "Foundation", 36.0, "bottle",
        "A sheer foundation with a serum base for a fresh, dewy finish.",
        _tones("1N 2C 3N 4W 5N 6C 7N 8W 9N 10N 11W 12N"), _formula("Serum"), label="Foundation"),
)  # fmt: skip
