"""Snowsuits and pramsuits (gen#213): padded all-in-one suits with a hood, fold-over mitts and
fold-over feet where the record says so. :mod:`kit_baby` draws each as its own shape."""

from __future__ import annotations

from babywear_rows import (
    BLACK,
    BLUE,
    CREAM,
    DOVECOTE,
    FENWOLD,
    GREEN,
    GREY,
    HUSHWELL,
    LITTLE_FERNBY,
    NAVY,
    NEWBORN,
    PINK,
    RED,
    SAGE,
    WHITE,
    YELLOW,
    a,
    garment,
    priced,
    yes,
)
from type_registry import ApparelPlan, TypeSpec

_P = ("Kids", "Baby", "Snowsuits & Pramsuits")


def _snow(code, title, brand, price, desc, colors, fill, hood, mitts, feet,
          sizes=NEWBORN):  # fmt: skip
    return garment(
        code, title, brand, _P, "Snowsuit", "snowsuit", price, desc, colors,
        (a("fill", "Fill", fill), a("hood", "Hood", yes(hood)),
         a("fold_over_mitts", "Fold-over mitts", yes(mitts)),
         a("fold_over_feet", "Fold-over feet", yes(feet)),
         a("season", "Season", "Winter")),
        (("hood", "yes" if hood else "no"), ("mitts", "yes" if mitts else "no"),
         ("feet", "yes" if feet else "no")),
        priced(sizes, price),
    )  # fmt: skip


SPEC = TypeSpec(
    key="snowsuit",
    department="Clothing",
    product_type="Snowsuit",
    rows=(
        _snow("SNWHMF", "Hooded Pramsuit with Mitts and Feet", LITTLE_FERNBY, 28.0,
              "A quilted pramsuit with a hood, fold-over mitts and fold-over feet, fleece lined "
              "and zipped from neck to ankle.",
              (BLUE, RED, GREEN, WHITE), "Polyester Wadding", True, True, True),
        _snow("SNWHND", "Padded Snowsuit with Hood", HUSHWELL, 24.0,
              "A padded snowsuit with a hood and a front zip. No mitts or feet, so it layers "
              "over a sleepsuit.",
              (YELLOW, NAVY, GREY), "Polyester Wadding", True, False, False),
        _snow("SNWNHD", "Hoodless Quilted Pramsuit", FENWOLD, 22.0,
              "A quilted pramsuit with fold-over mitts and feet and a high collar instead of a "
              "hood.",
              (BLACK, PINK, CREAM), "Recycled Fill", False, True, True),
        _snow("SNWDNF", "Down-Feel Pramsuit with Fold-Over Feet", DOVECOTE, 32.0,
              "A soft padded pramsuit with a hood and fold-over feet, for the winter pram.",
              (WHITE, SAGE, RED), "Down-Feel Fill", True, False, True),
    ),
    apparel=ApparelPlan(
        compounds=(("trousers", "Snowsuit Trousers"), ("jacket", "Snowsuit Jacket"),
            ("fleece", "Fleece Snowsuit"))
    ),
)  # fmt: skip
