"""Bouquet (Garden): hand-tied bouquets and letterbox flowers (gen#537, gen#1115).

The legacy rows stay in the shared row modules named by ``homes``. gen#1115 adds the live cut
flowers as this spec's own ``rows``: hand-tied bouquets under Garden > Flowers > Bouquets and
letterbox flowers (a slim box that fits through the door) under Garden > Flowers > Letterbox
Flowers. ``derivable`` is True, so the scaled build draws more styles from them by the flower the
title shows; each SKU is a bloom color times a stem count. The color is the bloom's own
(``main_colors.EXCEPTIONS``), so a style offers the colors its flower is grown in, not the six
main colors. ``occasion`` is a filter, never in the title, so a derived style may take another.
A text never names the flower in the plural: ``scale`` swaps a whole word, so "each rose stem"
becomes "each tulip stem" on a derived tulip bouquet.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_flowers,  # noqa: F401 -- registers cut_flowers
)
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.outdoor_helpers import DEPARTMENT, H, L, M, V, W, a
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Option, TypeSpec
from synthetic_ecommerce_data.domains.retail.variants import cw

BOUQUETS = (DEPARTMENT, "Flowers", "Bouquets")
LETTERBOX = (DEPARTMENT, "Flowers", "Letterbox Flowers")
_PT = "Bouquet"
G = "Goldfield Farms"

RED = cw("Red", "#b0182f")
PINK = cw("Pink", "#f3a6bf")
WHITE = cw("White", "#f7f5ef", "solid", "#9a9ca0")
YELLOW = cw("Yellow", "#f2c62e")
ORANGE = cw("Orange", "#f08a24")
PURPLE = cw("Purple", "#7d4a9e")


def _stems(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A style's stem counts as its SKU sizes, each at its price."""
    return tuple((str(n), p) for n, p in pairs)


def _row(code: str, title: str, brand: str, path: tuple[str, ...], flower: str, occasion: str,
         colors: tuple, stems: tuple, desc: str) -> Row:  # fmt: skip
    pack = "letterbox" if path == LETTERBOX else "bouquet"
    attrs = (a("flower", "Flower", flower), a("occasion", "Occasion", occasion), a("delivery", "Delivery", "Letterbox" if pack == "letterbox" else "Hand delivered"))
    return Row(code, title, brand, DEPARTMENT, path, _PT, stems[0][1], "cut_flowers", desc, colors, attrs, stems,
               params=(("flower", flower.lower()), ("pack", pack)), size_key="stem_count")  # fmt: skip


ROWS = (
    _row("CFRSHT", "Hand-Tied Rose Bouquet", G, BOUQUETS, "Rose", "Anniversary", (RED, PINK, WHITE, YELLOW),
         _stems((6, 25.0), (12, 40.0), (24, 65.0)),
         "A hand-tied bouquet: each rose stem is cut in bud and tied with eucalyptus, sent in water with flower food and a gift card."),
    _row("CFRSLS", "Long-Stem Rose Bouquet", V, BOUQUETS, "Rose", "Valentine's Day", (RED, PINK, WHITE),
         _stems((12, 55.0), (24, 90.0)),
         "A bouquet of long stems, each rose stem 60 cm tall, wrapped in kraft paper and sent with flower food."),
    _row("CFTLSP", "Spring Tulip Bouquet", M, BOUQUETS, "Tulip", "Birthday", (RED, PINK, YELLOW, WHITE, PURPLE, ORANGE),
         _stems((10, 22.0), (20, 32.0), (30, 42.0)),
         "A fresh bouquet: each tulip stem is picked closed so it opens in the vase, tied with a raffia bow."),
    _row("CFLYSC", "Scented Lily Bouquet", W, BOUQUETS, "Lily", "Sympathy", (WHITE, PINK, ORANGE, YELLOW),
         _stems((5, 30.0), (10, 48.0), (15, 62.0)),
         "A bouquet with each lily stem sent in bud, so the blooms open over a week."),
    _row("CFCNTY", "Carnation Bouquet", H, BOUQUETS, "Carnation", "Thank You", (RED, PINK, WHITE, PURPLE),
         _stems((10, 20.0), (20, 30.0)),
         "A long-lasting bouquet: each carnation stem keeps two weeks in fresh water."),
    _row("CFGRBR", "Gerbera Bouquet", L, BOUQUETS, "Gerbera", "Congratulations", (ORANGE, YELLOW, PINK, RED),
         _stems((7, 24.0), (14, 36.0)),
         "A bright bouquet: each gerbera stem is supported by a fine wire so the head stays up."),
    _row("CFMXSN", "Seasonal Mixed Flower Bouquet", G, BOUQUETS, "Mixed Flower", "Birthday", (PINK, YELLOW, WHITE, ORANGE),
         _stems((10, 30.0), (15, 40.0), (20, 50.0)),
         "The florist's choice of the season's blooms in one tone, each mixed flower stem tied by hand with seasonal foliage."),
    _row("LBRSCL", "Rose Letterbox Flowers", G, LETTERBOX, "Rose", "Anniversary", (RED, PINK, WHITE, YELLOW),
         _stems((8, 22.0), (12, 30.0)),
         "Letterbox flowers: each rose stem is packed in bud in a slim box that fits through the letterbox, with a vase guide and flower food."),
    _row("LBTLFL", "Tulip Letterbox Flowers", M, LETTERBOX, "Tulip", "Thank You", (RED, PINK, YELLOW, WHITE, PURPLE, ORANGE),
         _stems((10, 18.0), (15, 24.0), (20, 30.0)),
         "Letterbox flowers: each tulip stem is packed closed in a slim box that fits through the letterbox, to open in the vase."),
    _row("LBLYBX", "Lily Letterbox Flowers", W, LETTERBOX, "Lily", "Birthday", (WHITE, PINK, ORANGE),
         _stems((5, 24.0), (8, 32.0)),
         "Letterbox flowers: each lily stem is sent in bud in a slim box that fits through the letterbox."),
    _row("LBMXPS", "Mixed Flower Letterbox Flowers", V, LETTERBOX, "Mixed Flower", "Get Well", (PINK, YELLOW, WHITE),
         _stems((10, 25.0), (15, 32.0)),
         "Letterbox flowers: the season's blooms in one tone, each mixed flower stem packed in a slim box that fits through the letterbox."),
)

SPEC = TypeSpec(
    key="bouquet",
    department=DEPARTMENT,
    product_type=_PT,
    rows=ROWS,
    derivable=True,
    options=(Option("stem_count", "stem_count", "Stem count", "C62"),),
    homes=(
        Home("samples", True),
        Home("decor_rows", False),
    ),
)
