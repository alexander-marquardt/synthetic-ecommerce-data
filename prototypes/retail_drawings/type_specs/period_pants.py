"""Period pants (gen#329): absorbent knickers, in their own leaf under Womens Lingerie.

The probe of 2026-10-15 found no period-wear lingerie: a query for it met ordinary knickers. The
type is sold by absorbency (light, medium, heavy, overnight), and each cut is drawn as the knicker
cut it states (:mod:`kit_underwear`), so the picture, the title and the attribute agree. The
styles are templates only (``derivable`` False). The text-match decoys come from the apparel plan
(gen#311): three of each class, cloned from these rows.
"""

from __future__ import annotations

from type_registry import ApparelPlan, Row, TypeSpec, a, cw, sizes

_LING = "Lingerie & Nightwear"
PATH = ("Womens", "Lingerie", "Period Pants")
UK = ("8", "10", "12", "14", "16", "18", "20", "22")
BLACK, WHITE = cw("Black", "#2f2f35", "solid", "#8f989f"), cw("White", "#f4f1ea", "solid", "#b9b4a6")
NUDE, NAVY = cw("Nude", "#e5c1a8", "solid", "#a9805f"), cw("Navy", "#2c3a5e", "solid", "#d8dce8")
GREY, PLUM = cw("Grey", "#9a9ca0", "solid", "#55575c"), cw("Plum", "#5e2a4a", "solid", "#e8d0de")

#: What each absorbency holds, as the descriptions word it.
HOLDS = {
    "Light": "about one tampon's worth",
    "Medium": "about two tampons' worth",
    "Heavy": "about three tampons' worth",
    "Overnight": "about four tampons' worth",
}
CUTS = {"Bikini": "bikini", "Briefs": "brief", "High-Waisted": "high_waisted", "High-Leg": "high_leg"}


def _row(code, title, brand, cut, level, fabric, price, desc, colors):
    """One style: its cut and absorbency are attributes, and the cut is what the drawing shows."""
    return Row(
        code, title, brand, _LING, PATH, "Period Pants", price, "knickers",
        f"{desc} Holds {HOLDS[level]}, with a leakproof gusset. Machine washable.", colors,
        (a("absorbency", "Absorbency", level), a("cut", "Cut", cut), a("fabric", "Fabric", fabric)),
        sizes(price, UK), params=(("cut", CUTS[cut]), ("trim", "plain")),
    )  # fmt: skip


ROWS = (
    _row("PPBKLT", "Light Bikini Period Pants", "Dovecote Lane", "Bikini", "Light", "Cotton", 12.0,
         "Low-rise cotton bikini period pants for the light days at either end of a period.",
         (BLACK, WHITE, NUDE)),
    _row("PPBRMD", "Medium Briefs Period Pants", "Hushwell", "Briefs", "Medium", "Cotton", 14.0,
         "Full-coverage period briefs in soft stretch cotton with a covered waistband.",
         (BLACK, NAVY, GREY)),
    _row("PPHWHV", "Heavy Flow High-Waisted Period Pants", "Wrenfield", "High-Waisted", "Heavy",
         "Modal", 18.0, "High-waisted period pants in smooth modal that sit above the navel.",
         (BLACK, NUDE, PLUM)),
    _row("PPHWON", "Overnight High-Waisted Period Pants", "Quillon Sleep", "High-Waisted",
         "Overnight", "Cotton", 20.0,
         "Extra-long high-waisted period pants cut to cover the back for sleep.",
         (BLACK, NAVY)),
    _row("PPHLMD", "High-Leg Period Pants", "Dovecote Lane", "High-Leg", "Medium", "Microfiber",
         15.0, "Period pants cut high on the hip, in fast-drying microfiber.", (BLACK, NUDE, WHITE)),
    _row("PPBKMD", "Seamless Bikini Period Pants", "Hushwell", "Bikini", "Medium", "Seamless",
         16.0, "Seamless bikini period pants with a bonded edge that disappears under fitted clothes.",
         (BLACK, NUDE, GREY)),
    _row("PPBRHV", "Full Coverage Period Pants", "Wrenfield", "Briefs", "Heavy", "Cotton", 17.0,
         "Full-coverage period briefs with an extra-wide gusset for the heaviest days.",
         (BLACK, WHITE, PLUM)),
    _row("PPHWLT", "Everyday High-Waisted Period Pants", "Quillon Sleep", "High-Waisted", "Light",
         "Cotton", 13.0, "Soft high-waisted period pants for light flow or as a back-up.",
         (WHITE, NUDE, NAVY)),
    _row("PPBROV", "Overnight Briefs Period Pants", "Hushwell", "Briefs", "Overnight", "Modal",
         21.0, "Longer-cut period briefs in modal, built for a full night.", (BLACK, GREY)),
    _row("PPHLHV", "Heavy Flow High-Leg Period Pants", "Dovecote Lane", "High-Leg", "Heavy",
         "Microfiber", 19.0, "High-leg period pants with a wide absorbent panel and a stay-put leg.",
         (BLACK, NAVY, NUDE)),
)  # fmt: skip

SPEC = TypeSpec(
    key="period_pants",
    department=_LING,
    product_type="Period Pants",
    rows=ROWS,
    derivable=False,
    apparel=ApparelPlan(
        family="u",
        compounds=(
            ("bikini", "Bikini Period Pants"),
            ("boyshort", "Boyshort Period Pants"),
            ("thong", "Thong Period Pants"),
        ),
    ),
)
