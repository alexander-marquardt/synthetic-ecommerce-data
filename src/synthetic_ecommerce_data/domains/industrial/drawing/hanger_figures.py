"""Picture hangers, each drawn as its real style, face on and lit (#1215).

The record gives the style, the color and, by its rating, the size and the number of nails or
screws: a heavier hanger is larger and is held by more of them. Figures are laid out in a 156 by
200 box, in hundredths, y down.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.drawing.model import Figure, arc
from synthetic_ecommerce_data.domains.industrial.drawing.lit import block, box, inches, lit

#: The box every hanger's drawing at full size stays in, in inches: the type's extent.
EXTENT = (1.56, 2.0)
#: The scale of the lightest hanger, of the heaviest one's: siblings draw apart.
SMALLEST = 0.95
STEEL, WIRE, CASE = "#c3cad0", "#a9845a", "#d3dae0"


def _fixings(pounds: float) -> int:
    """How many nails or screws hold a hanger of a rating."""
    return 1 if pounds <= 30 else 2 if pounds <= 75 else 3


def _across(count: int, wide: float, centre: float) -> list[float]:
    return [centre + wide * (k - (count - 1) / 2) / max(count - 1, 1) for k in range(count)]


def _nail_hook(fig: Figure, fill: str, pounds: float) -> None:
    """A folded strap: its back plate, the lip turned up at its foot, nails through its top."""
    lit(fig, block(6, 12, 150, 190, 18), fill)
    top = arc((78, 120), 78, 180, 360, 10)
    lit(fig, [*[(x, 120 + (y - 120) * 0.22) for x, y in top], (156, 182), (140, 200), (16, 200),
              (0, 182)], fill)  # fmt: skip
    for x in _across(_fixings(pounds), 76, 78):
        fig.poly([(x - 4, 22), (x + 4, 22), (x + 2, 78), (x, 84), (x - 2, 78)], "handle", STEEL)
        fig.poly(block(x - 12, 0, x + 12, 20, 5), "handle", STEEL)
        fig.poly(block(x - 10, 3, x - 2, 8, 2), "gloss")


def _sawtooth(fig: Figure, fill: str, pounds: float) -> None:
    """A strip: teeth cut in its lower edge, and a screw in each end."""
    teeth, x0, x1, root, tip = 7, 24.0, 132.0, 62.0, 76.0
    step = (x1 - x0) / teeth
    under = [(x1, tip)]
    for k in reversed(range(teeth)):
        under += [(x0 + step * (k + 0.5), root), (x0 + step * k, tip)]
    lit(fig, [(8, 0), (148, 0), (156, 8), (156, 68), (148, 76), *under, (8, 76), (0, 68), (0, 8)],
        fill, across=True)  # fmt: skip
    for x in (14, 142):
        fig.disc((x, 38), 6, "handle", STEEL)
        fig.lines([((x - 4, 38), (x + 4, 38))])
    del pounds


def _d_ring(fig: Figure, fill: str, pounds: float) -> None:
    """A strap plate with its screw holes, folded over the bar of a wire ring."""
    outer = [(156 - 78 + x, 112 + y) for x, y in arc((0, 0), 78, 0, 180, 14)]
    outer = [(x, 112 + (y - 112) * 88 / 78) for x, y in outer]
    ring = [(0, 88), (156, 88), *outer]
    lit(fig, ring, STEEL)
    inner = arc((78, 114), 52, 0, 180, 12)
    fig.poly([(26, 114), (130, 114), *[(x, 114 + (y - 114) * 58 / 52) for x, y in inner]], "hole")
    lit(fig, block(12, 0, 144, 122, 14), fill)
    fig.lines([((12, 94), (144, 94))])
    for x in _across(_fixings(pounds), 76, 78):
        fig.disc((x, 44), 11, "dark")
        fig.disc((x, 44), 6, "handle", STEEL)


def _hanging_kit(fig: Figure, fill: str, pounds: float) -> None:
    """A kit in its compartment box: hooks, a coil of wire and nails, under a clear lid."""
    fig.poly(block(0, 0, 156, 200, 10), "handle", CASE)
    for rect in ((8, 8, 148, 92), (8, 98, 88, 192), (94, 98, 148, 192)):
        fig.poly(box(*rect), "handle", "#eef2f4")
    hooks = 1 + _fixings(pounds)
    step = 136 / hooks
    wide = min(step - 6, 56)
    for k in range(hooks):
        x = 10 + step * (k + 0.5)
        lit(fig, block(x - wide / 2, 14, x + wide / 2, 84, 6), fill)
        lit(fig, block(x - wide / 2 - 2, 56, x + wide / 2 + 2, 88, 6), fill)
        fig.disc((x, 28), 5, "handle", STEEL)
    for radius in (36, 31, 26):
        fig.disc((48, 145), radius, "handle", WIRE)
    fig.disc((48, 145), 20, "handle", "#eef2f4")
    for x in (106, 121, 136):
        fig.poly([(x - 2.5, 112), (x + 2.5, 112), (x, 182)], "handle", STEEL)
        fig.poly(block(x - 6, 106, x + 6, 114, 2), "handle", STEEL)
    fig.poly([(0, 60), (60, 0), (84, 0), (0, 84)], "gloss")
    fig.poly(box(146, 10, 156, 190), "shade")


STYLES = {
    "Nail Hook": _nail_hook,
    "Sawtooth Hanger": _sawtooth,
    "D-Ring Hanger": _d_ring,
    "Hanging Kit": _hanging_kit,
}


def hanger(style: str, fill: str, pounds: float) -> Figure:
    """A hanger of ``style`` in ``fill`` rated for ``pounds``."""
    fig = Figure()
    STYLES.get(style, _nail_hook)(fig, fill, pounds)
    place = min(1.0, max(0.0, (pounds - 10) / 90)) ** 0.5
    return inches(fig, SMALLEST + (1 - SMALLEST) * place)
