"""The shirts: Oxford, Flannel, Linen and Denim, for Mens and Womens (data only).

Until now a search for "shirt" found only T-shirt bras and shirt dresses, because the tree
held blouses and T-shirts but no shirt. The Womens and Mens trees each get ``Tops/Shirts`` with
four leaves, and every style is typed ``Shirt``::

    Mens/Tops/Shirts/Oxford Shirts      Womens/Tops/Shirts/Oxford Shirts
    Mens/Tops/Shirts/Flannel Shirts     Womens/Tops/Shirts/Flannel Shirts
    Mens/Tops/Shirts/Linen Shirts       Womens/Tops/Shirts/Linen Shirts
    Mens/Tops/Shirts/Denim Shirts       Womens/Tops/Shirts/Denim Shirts

Three styles per leaf and audience, so 24 in all, each in :data:`SIZES` and one or two colors.
:func:`scale.templates` builds them just before the grocery styles and :func:`scale.derivable`
leaves them out, so the seeded derivation (and every product id and image id it makes) is
what it was; a build to the old ceiling is cut a few derived styles short of it instead.
Every row is a :class:`class_model.Style`; a title says "Shirt", never "Tee".
"""

from __future__ import annotations

from class_model import Style
from variants import cw

SIZES = ("XS", "S", "M", "L", "XL")
NAVY, WHITE, BLUE, RED, GREEN, SAND, BLACK = (
    "#26365c", "#ffffff", "#8fb8de", "#a83a32", "#5f7a4d", "#d9c9a8", "#2a2a2e",
)  # fmt: skip

#: leaf -> ((fabric, ((title head, description, pattern, ((color, sold), ...)) x 3)),): the
#: same three rows are sold to Mens and Womens.
_ROWS = {
    "Oxford Shirts": (
        ("100% Cotton Oxford", (
            ("Button Down Oxford Shirt", "A button down collar oxford shirt with a chest pocket.",
             "plain", ((cw("White", WHITE), 640), (cw("Ice", BLUE), 410))),
            ("Pinpoint Oxford Shirt", "A smart pinpoint oxford shirt with a curved hem.",
             "plain", ((cw("Pink", "#f3c6cf"), 220),)),
            ("Striped Oxford Shirt", "A crisp striped oxford shirt, easy to wear open or buttoned.",
             "stripe", ((cw("Blue Stripe", WHITE, "stripe", BLUE), 330),)),
        )),
    ),
    "Flannel Shirts": (
        ("Brushed Cotton Flannel", (
            ("Checked Flannel Shirt", "A warm brushed flannel shirt in a bold check.",
             "check", ((cw("Brown Check", "#8a5a3c", "gingham", "#2a2a2e"), 520),)),
            ("Navy Check Flannel Shirt", "A soft flannel shirt with two chest pockets.",
             "check", ((cw("Navy Check", NAVY, "gingham", RED), 380),
                       (cw("Grey Check", "#9a9a9a", "gingham", BLACK), 260))),
            ("Plain Flannel Shirt", "A plain brushed flannel shirt with a relaxed fit.",
             "plain", ((cw("Olive", GREEN), 290),)),
        )),
    ),
    "Linen Shirts": (
        ("Washed Linen", (
            ("Linen Blend Shirt", "A lightweight linen blend shirt for warm days.",
             "plain", ((cw("White", WHITE), 450), (cw("Sage", "#9bb08f"), 300))),
            ("Short Sleeve Linen Shirt", "A short sleeve linen shirt with a camp collar.",
             "plain", ((cw("Stone", SAND), 260), (cw("Navy", NAVY), 210))),
            ("Striped Linen Shirt", "A relaxed linen shirt woven with a fine stripe.",
             "stripe", ((cw("Navy Stripe", WHITE, "stripe", NAVY), 240),)),
        )),
    ),
    "Denim Shirts": (
        ("Mid Weight Denim", (
            ("Classic Denim Shirt", "A classic denim shirt with two flap pockets.",
             "plain", ((cw("Mid Wash", "#5b7aa6"), 560),)),
            ("Light Wash Denim Shirt", "A faded light wash denim shirt with a western yoke.",
             "plain", ((cw("Light Wash", "#9fb4cf"), 340),)),
            ("Black Denim Shirt", "A black denim shirt with press stud fastenings.",
             "plain", ((cw("Black", BLACK), 280),)),
        )),
    ),
}  # fmt: skip

_BRANDS = {
    "Mens": ("Harbour & Pine", "Larkmoor", "Wrenfield"),
    "Womens": ("Wrenfield", "Larkmoor", "Calderby & Lune"),
}
_PRICE = {"Oxford Shirts": 28.0, "Flannel Shirts": 24.0, "Linen Shirts": 30.0, "Denim Shirts": 32.0}


def _style(root: str, who: str, leaf: str, fabric: str, n: int, row: tuple) -> Style:
    head, text, pattern, colors = row
    code = f"SH{root[0]}{leaf[0]}{n}"
    return Style(
        code, f"{who} {head}", _BRANDS[who][n], "Clothing", (root, "Tops", "Shirts", leaf),
        _PRICE[leaf] + 2.0 * n, text, "Shirt", "blouse",
        colors, neckline="collared", pattern=pattern, size_range="regular", sizes=SIZES,
        extra=(("fabric", "Fabric", fabric),),
    )  # fmt: skip


STYLES = tuple(
    _style(root, who, leaf, fabric, n, row)
    for root, who in (("Mens", "Mens"), ("Womens", "Womens"))
    for leaf, ((fabric, rows),) in _ROWS.items()
    for n, row in enumerate(rows)
)


def docs() -> list[dict]:
    """Every shirt's catalog document, in the order of :data:`STYLES`."""
    return [s.doc() for s in STYLES]
