"""Face Cream (gen#542): five existing beauty brands beside the one of the class rows, each with a day, a
night and an SPF line (and a fourth: barrier, sensitive, anti-ageing or rich) in 30, 50 and 100 ml.

Three tiers, as a shopper sees them on a shelf: pharmacy (Sorrel & Salt, Aldermist), mid (Thornlea
Skin, Pearlbrook) and premium (Fenmere). The price rises with the volume and falls per
ml: a 100 ml pot costs less than twice the 50 ml one and well under three times the 30 ml one.
The skin type and the skin concern are attributes, the volume in ml is a SKU option, and an SPF
line is also sold by its SPF (the option ``sun_cream`` declares the same way).

The three Velling Apothecary face creams (``PLT-FCDAYC``, ``PLT-FCNGHT``, ``PLT-FCCALM``) and the
"Daylight" decoy (``PLT-DXL10``) stay in ``class_rows`` and ``decoy_rows``: the committed
Elasticsearch proof of the "face cream" demo (class 12) names their ids
(``tests/test_retail_type_specs_351.py``, ``PROOF_PINNED_CLASS_ROWS``). Their brand still sells here.
The five brands keep the marks and house styles they already have. The type is drawn as the class rows draw it
(``moisturiser_jar``); the SPF line is a day cream with sun protection, not a sun cream, so it
stays in the Face Creams leaf.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK, PACK_INK, PACK_ROSE, PACK_SAGE, PACK_SAND, PACK_SKY, row
from type_registry import Option, TypeSpec, a

_PATH = ("Beauty", "Skincare", "Creams", "Face Creams")
_FACE = partial(row, path=_PATH, ptype="Face Cream")


def _line(code, title, brand, desc, skin, concern, prices, color, spf=()):
    """One line in 30, 50 and 100 ml: ``prices`` is the price of each size, in that order."""
    sizes = tuple(zip(("30", "50", "100"), prices, strict=True))
    return _FACE(
        code, title, brand, prices[0], "moisturiser_jar", desc,
        (a("skin_type", "Skin type", skin), a("skin_concern", "Skin concern", concern)),
        sizes, "net_volume_ml", (), (color,), option=("spf", spf) if spf else (),
    )  # fmt: skip


ROWS = (
    # -- pharmacy: about 8 to 22 --
    _line("FCCDDY", "Hydrating Day Face Cream", "Sorrel & Salt",
        "A light daily face cream that keeps normal skin comfortable from morning to evening.",
        "Normal", "Dryness", (8.0, 11.0, 17.0), PACK_SKY),
    _line("FCCDNT", "Repair Night Face Cream", "Sorrel & Salt",
        "A soothing night face cream that helps dry skin recover while you sleep.",
        "Dry", "Dryness", (9.0, 13.0, 20.0), PACK),
    _line("FCCDSP", "Day Face Cream SPF 30", "Sorrel & Salt",
        "A non-greasy daily face cream with broad spectrum SPF 30 for every day wear.",
        "Normal", "Sun Protection", (9.5, 13.5, 21.0), PACK_SAND, spf=("30",)),
    _line("FCCDBR", "Barrier Repair Face Cream", "Sorrel & Salt",
        "A thick face cream with ceramides that restores the skin barrier of dry, tight skin.",
        "Dry", "Dryness", (8.5, 12.0, 18.5), PACK_SAGE),
    _line("FCPLDY", "Oil Free Day Face Cream", "Aldermist",
        "A fast absorbing, oil free day face cream that leaves oily skin matte and fresh.",
        "Oily", "Blemishes", (9.0, 12.5, 19.0), PACK_SAGE),
    _line("FCPLNT", "Clarifying Night Face Cream", "Aldermist",
        "A night face cream with salicylic acid that clears pores without drying combination skin.",
        "Combination", "Blemishes", (10.0, 14.0, 22.0), PACK_SKY),
    _line("FCPLSP", "Mattifying Day Face Cream SPF 30", "Aldermist",
        "A shine control day face cream with SPF 30 that sits well under make-up.",
        "Oily", "Sun Protection", (11.0, 15.0, 24.0), PACK, spf=("30", "50")),
    _line("FCPLSN", "Sensitive Skin Face Cream", "Aldermist",
        "A fragrance free face cream, tested on sensitive skin, that calms redness and tightness.",
        "Sensitive", "Sensitivity", (10.0, 14.0, 22.0), PACK_ROSE),
    # -- mid: about 20 to 66 --
    _line("FCWYDY", "Radiance Day Face Cream", "Thornlea Skin",
        "A silky day face cream with vitamin C that brightens skin that looks tired.",
        "Normal", "Dullness", (22.0, 32.0, 52.0), PACK_SAND),
    _line("FCWYNT", "Restorative Night Face Cream", "Thornlea Skin",
        "A rich night face cream with shea butter that replenishes dry skin overnight.",
        "Dry", "Dryness", (24.0, 35.0, 57.0), PACK_INK),
    _line("FCWYSP", "Protect Day Face Cream SPF 30", "Thornlea Skin",
        "A lightweight day face cream with SPF 30 and antioxidants for daily city wear.",
        "Combination", "Sun Protection", (24.0, 34.0, 55.0), PACK_SKY, spf=("30", "50")),
    _line("FCWYAG", "Firming Anti-Ageing Face Cream", "Thornlea Skin",
        "A firming face cream with peptides and retinol that softens the look of fine lines.",
        "Normal", "Fine Lines", (28.0, 40.0, 66.0), PACK_ROSE),
    _line("FCLVDY", "Light Hydra Day Face Cream", "Pearlbrook",
        "A gel texture day face cream that gives combination skin water without weight.",
        "Combination", "Dryness", (20.0, 29.0, 46.0), PACK_SAGE),
    _line("FCLVNT", "Replenishing Night Face Cream", "Pearlbrook",
        "A cushiony night face cream with hyaluronic acid that plumps and comforts dry skin.",
        "Dry", "Dryness", (22.0, 32.0, 52.0), PACK_INK),
    _line("FCLVSP", "Everyday Day Face Cream SPF 50", "Pearlbrook",
        "A high protection day face cream with SPF 50 and no white cast.",
        "Normal", "Sun Protection", (23.0, 33.0, 53.0), PACK, spf=("50",)),
    _line("FCLVRC", "Rich Barrier Face Cream", "Pearlbrook",
        "A rich, balm-like face cream that wraps very dry skin in comfort through the cold months.",
        "Dry", "Dryness", (24.0, 34.0, 55.0), PACK_SAND),
    # -- premium: about 58 to 145 --
    _line("FCSADY", "Luminous Day Face Cream", "Fenmere",
        "A weightless day face cream with botanical extracts that gives skin a lit-from-within glow.",
        "Normal", "Dullness", (58.0, 82.0, 125.0), PACK_SAND),
    _line("FCSANT", "Renewal Night Face Cream", "Fenmere",
        "A luxurious night face cream with encapsulated retinol that renews skin while you rest.",
        "Dry", "Fine Lines", (64.0, 92.0, 138.0), PACK_INK),
    _line("FCSASP", "Veil Day Face Cream SPF 30", "Fenmere",
        "An elegant day face cream with SPF 30 and peptides that protects and smooths in one step.",
        "Combination", "Sun Protection", (62.0, 88.0, 132.0), PACK_SKY, spf=("30", "50")),
    _line("FCSAAG", "Lift Anti-Ageing Face Cream", "Fenmere",
        "A firming, anti-ageing face cream with a velvet texture, for skin that has lost its spring.",
        "Normal", "Fine Lines", (68.0, 98.0, 145.0), PACK_ROSE),
)  # fmt: skip

SPEC = TypeSpec(
    key="face_cream",
    department="Beauty",
    product_type="Face Cream",
    options=(Option("spf", "spf", "SPF"),),
    rows=ROWS,
    owners=(
        ("Sorrel & Salt", "third_party"),
        ("Aldermist", "third_party"),
        ("Thornlea Skin", "third_party"),
        ("Pearlbrook", "third_party"),
        ("Fenmere", "third_party"),
    ),
)  # fmt: skip
