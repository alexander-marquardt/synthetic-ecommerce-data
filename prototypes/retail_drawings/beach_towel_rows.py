"""The real beach towels (gen#624): material, weave and feature vary, and the titles are long.

The catalog had one beach towel, "Cotton Velour Beach Towel", and the derivation copied it
(``<Name> Cotton Velour Beach Towel, <Colour>``): thirteen rows with one material, one weave and
four to seven words. A short decoy title ("Beach Towel Print Tote") outranked every one of them on
a text score. These twelve are authored rows of Home > Bathroom > Beach Towels instead:

* a **material** (cotton, organic cotton, polyester, microfibre, a cotton-polyester blend),
* a **weave** (velour, terry, waffle, Turkish peshtemal, sand-free),
* a **feature** (quick dry, extra absorbent, oversized, double sided, hooded, ...) and
* a **size** in centimetres,

each a structured attribute and each named in the title, so a filter on "microfibre" or "quick dry"
finds the rows whose titles say so. A title is 7 to 12 words. Some name the one colour or print the
style comes in ("..., Navy Stripe"); the others leave the color to the SKUs, as real listings do.
One reads "Sun Lounger Towel": a shopper's word for it that holds no "beach". The brands are the
catalog's invented ones; the colour and pattern split is :mod:`colorwords` (a "Navy Stripe"
colourway is the color Navy and the pattern stripe).

The rows are templates only: the derivation leaves them out (``scale.derivable``) so each title
stays the one authored here.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_home  # noqa: F401 -- registers the beach_towel drawing
from breadth_rows import Row
from variants import cw

PATH = ("Home", "Bathroom", "Beach Towels")
CALDERBY, HARBOUR, THISTLE = "Calderby & Lune", "Harbour & Pine", "Thistle & Wren"
LARCHWOOD, BRACKENMERE, EMBERLY = "Larchwood Living", "Brackenmere Home", "Emberly Home"
COBBLE, LANTERNBY = "Cobble & Kiln", "Lanternby"

WHITE = "#ffffff"


def _towel(code, title, brand, price, desc, colors, material, weave, feature, size):
    attrs = (
        ("material", "Material", material),
        ("weave", "Weave", weave),
        ("feature", "Feature", feature),
        ("dimensions", "Size", size),
    )
    return Row(code, title, brand, "Home", PATH, "Beach Towel", price, "beach_towel", desc, colors, attrs)


ROWS = (
    _towel("BCHAOT", "Extra Absorbent Organic Cotton Terry Beach Towel, Navy Stripe", HARBOUR, 24.0,
           "A thick organic cotton terry towel with a looped pile that soaks up water fast, woven in navy and white stripes.",
           (cw("Navy Stripe", "#ffffff", "stripe", "#26365c"),),
           "Organic Cotton", "Terry", "Extra Absorbent", "90 x 170 cm"),
    _towel("BCHQDM", "Quick Dry Microfibre Sand Free Beach Towel, 80 x 160 cm", CALDERBY, 16.0,
           "A thin microfibre towel with a smooth weave that shakes the sand off, dries in minutes and folds into its pouch.",
           (cw("Aqua", "#4fb3bf", "solid", WHITE), cw("Coral", "#ef7b62", "solid", WHITE), cw("Grey", "#9a9ca0", "solid", WHITE)),
           "Microfibre", "Sand Free", "Quick Dry", "80 x 160 cm"),
    _towel("BCHTUR", "Oversized Turkish Peshtemal Cotton Beach Towel with Tassels", THISTLE, 28.0,
           "A flat woven Turkish peshtemal in light cotton, big enough to lie on, with knotted tassels at both ends.",
           (cw("Sand", "#d8c9a8", "solid", WHITE), cw("Navy", "#26365c", "solid", WHITE), cw("Sage", "#9bb08f", "solid", WHITE)),
           "Cotton", "Turkish Peshtemal", "Oversized", "100 x 180 cm"),
    _towel("BCHDWF", "Double Sided Cotton Polyester Blend Waffle Beach Towel", LARCHWOOD, 19.0,
           "A honeycomb waffle towel in a cotton polyester blend, a different color on each side so it can be turned over on the sand.",
           (cw("Blue", "#3f6fb5", "solid", WHITE), cw("Green", "#4f7a3a", "solid", WHITE), cw("Pink", "#e8a0b4", "solid", WHITE)),
           "Cotton Polyester Blend", "Waffle", "Double Sided", "90 x 160 cm"),
    _towel("BCHXSV", "Extra Soft Cotton Velour Beach Towel, Coral", CALDERBY, 18.0,
           "A large cotton towel with a soft sheared velour face and a looped terry back.",
           (cw("Coral", "#ef7b62", "solid", WHITE),),
           "Cotton", "Velour", "Extra Soft", "85 x 160 cm"),
    _towel("BCHHOD", "Hooded Cotton Terry Beach Towel Poncho with Front Pocket", BRACKENMERE, 26.0,
           "A cotton terry poncho towel with a hood to pull up after a swim and a warm front pocket for the hands.",
           (cw("Navy", "#26365c", "solid", WHITE), cw("Grey", "#9a9ca0", "solid", WHITE)),
           "Cotton", "Terry", "Hooded", "75 x 110 cm"),
    _towel("BCHFDR", "Fade Resistant Cotton Polyester Blend Terry Beach Towel, Red Stripe", EMBERLY, 17.0,
           "A cotton polyester blend terry towel in wide red and white stripes that hold their color wash after wash.",
           (cw("Red Stripe", "#ffffff", "stripe", "#c8312e"),),
           "Cotton Polyester Blend", "Terry", "Fade Resistant", "90 x 180 cm"),
    _towel("BCHQOW", "Quick Dry Organic Cotton Waffle Beach Towel with Contrast Edge", COBBLE, 21.0,
           "A light organic cotton waffle towel that dries quickly in the sun, with a contrast band along each long edge.",
           (cw("Sage", "#9bb08f", "solid", WHITE), cw("Cream", "#efe6cf", "solid", "#9a9ca0"), cw("Grey", "#9a9ca0", "solid", WHITE)),
           "Organic Cotton", "Waffle", "Quick Dry", "90 x 170 cm"),
    _towel("BCHOPV", "Oversized Quick Dry Polyester Velour Beach Towel, Pink Floral", LANTERNBY, 15.0,
           "A big polyester velour towel with a printed floral face that dries fast and packs small.",
           (cw("Pink Floral", "#e8a0b4", "floral", "#4f7a3a"),),
           "Polyester", "Velour", "Oversized", "100 x 190 cm"),
    _towel("BCHOGC", "Oversized Cotton Terry Beach Towel with Hanging Loop, Green Check", THISTLE, 20.0,
           "A roomy cotton terry towel in green and white checks, with a sewn loop to hang it on a hook.",
           (cw("Green Check", "#ffffff", "check", "#4f7a3a"),),
           "Cotton", "Terry", "Oversized", "100 x 180 cm"),
    _towel("BCHSLV", "Oversized Cotton Velour Sun Lounger Towel with Pocket, Green Stripe", LARCHWOOD, 23.0,
           "A cotton velour towel cut to fit a sun lounger, with a pocket sewn into the top for a phone or sun cream.",
           (cw("Green Stripe", "#ffffff", "stripe", "#4f7a3a"),),
           "Cotton", "Velour", "Oversized", "75 x 200 cm"),
    _towel("BCHSAM", "Super Absorbent Microfibre Terry Beach Towel with Zip Pocket", BRACKENMERE, 14.0,
           "A microfibre terry towel that holds several times its weight in water, with a zip pocket for a key.",
           (cw("Teal", "#1c7c7d", "solid", WHITE), cw("Black", "#2d2d33", "solid", WHITE), cw("Yellow", "#f2c230", "solid", "#2f2f35")),
           "Microfibre", "Terry", "Super Absorbent", "80 x 150 cm"),
)  # fmt: skip


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]


def product_ids() -> frozenset[str]:
    """The towels' product ids: the derivation leaves them as authored."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
