"""Women's pants (gen#329, everyday pants since gen#780): plain underwear in their own leaf
under Womens Lingerie.

In British English underwear is called pants, and a demo search for ``pants`` should find
ordinary underwear, so these styles are everyday pants sold by cut and fabric (gen#780: they
were period pants with an absorbency attribute, which a demo should not show). Each cut is drawn
as the knicker cut it states (:mod:`kit_underwear`), so the picture, the title and the attribute
agree, and the drawings are the ones the styles had. The men's pants are :mod:`.mens_pants`. The
styles are templates only (``derivable`` False). The text-match decoys come from the apparel plan
(gen#311): three of each class, cloned from these rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import (
    ApparelPlan,
    Row,
    TypeSpec,
    a,
    cw,
    sizes,
)

_LING = "Lingerie & Nightwear"
PATH = ("Womens", "Lingerie", "Pants")
UK = ("8", "10", "12", "14", "16", "18", "20", "22")
BLACK, WHITE = cw("Black", "#2f2f35", "solid", "#8f989f"), cw("White", "#f4f1ea", "solid", "#b9b4a6")
NUDE, NAVY = cw("Nude", "#e5c1a8", "solid", "#a9805f"), cw("Navy", "#2c3a5e", "solid", "#d8dce8")
GREY, PLUM = cw("Grey", "#9a9ca0", "solid", "#55575c"), cw("Plum", "#5e2a4a", "solid", "#e8d0de")
CUTS = {"Bikini": "bikini", "Briefs": "brief", "High-Waisted": "high_waisted", "High-Leg": "high_leg"}


def _row(code, title, brand, cut, fabric, price, desc, colors):
    """One style: its cut and fabric are attributes, and the cut is what the drawing shows."""
    return Row(
        code, title, brand, _LING, PATH, "Pants", price, "knickers", f"{desc} Machine washable.",
        colors, (a("cut", "Cut", cut), a("fabric", "Fabric", fabric)),
        sizes(price, UK), params=(("cut", CUTS[cut]), ("trim", "plain")),
    )  # fmt: skip


ROWS = (
    _row("PPBKLT", "Cotton Bikini Pants", "Dovecote Lane", "Bikini", "Cotton", 8.0,
         "Low-rise bikini pants in soft breathable cotton for every day.", (BLACK, WHITE, NUDE)),
    _row("PPBRMD", "Full Brief Pants", "Hushwell", "Briefs", "Cotton", 9.0,
         "Full-coverage brief pants in soft stretch cotton with a covered waistband.",
         (BLACK, NAVY, GREY)),
    _row("PPHWHV", "High-Waisted Modal Pants", "Wrenfield", "High-Waisted", "Modal", 12.0,
         "High-waisted pants in smooth modal that sit above the navel.", (BLACK, NUDE, PLUM)),
    _row("PPHWON", "Comfort High-Waisted Pants", "Quillon Sleep", "High-Waisted", "Cotton", 11.0,
         "Roomy high-waisted cotton pants with a soft wide waistband, as easy for lounging as for sleep.",
         (BLACK, NAVY)),
    _row("PPHLMD", "High-Leg Pants", "Dovecote Lane", "High-Leg", "Microfiber", 9.0,
         "Pants cut high on the hip, in smooth fast-drying microfiber.", (BLACK, NUDE, WHITE)),
    _row("PPBKMD", "Seamless Bikini Pants", "Hushwell", "Bikini", "Seamless", 10.0,
         "Seamless bikini pants with a bonded edge that disappears under fitted clothes.",
         (BLACK, NUDE, GREY)),
    _row("PPBRHV", "Full Coverage Pants", "Wrenfield", "Briefs", "Cotton", 10.0,
         "Full-coverage cotton pants with a deep waist and a smooth leg line.", (BLACK, WHITE, PLUM)),
    _row("PPHWLT", "Everyday High-Waisted Pants", "Quillon Sleep", "High-Waisted", "Cotton", 9.0,
         "Soft high-waisted cotton pants for every day, with a comfortable flat waistband.",
         (WHITE, NUDE, NAVY)),
    _row("PPBROV", "Modal Brief Pants", "Hushwell", "Briefs", "Modal", 11.0,
         "Brief pants in silky modal with a gentle stretch and a covered waistband.", (BLACK, GREY)),
    _row("PPHLHV", "Microfiber High-Leg Pants", "Dovecote Lane", "High-Leg", "Microfiber", 10.0,
         "High-leg pants in light microfiber with a stay-put leg that lies flat under clothes.",
         (BLACK, NAVY, NUDE)),
)  # fmt: skip

SPEC = TypeSpec(
    key="pants",
    department=_LING,
    product_type="Pants",
    rows=ROWS,
    derivable=False,
    apparel=ApparelPlan(
        family="u",
        compounds=(
            ("bikini", "Bikini Pants"),
            ("boyshort", "Boyshort Pants"),
            ("thong", "Thong Pants"),
        ),
    ),
)
