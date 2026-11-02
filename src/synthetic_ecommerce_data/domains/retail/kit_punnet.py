"""The punnet and the fruit or vegetable it holds (moved out of ``kit`` to keep it under the line cap, gen#455)."""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _word,
    register,
)

HALF = ' stroke-opacity=".5"'


def _strawberry(x: float, y: float) -> str:
    berry = (
        "M0,-24 C18,-24 24,-8 16,10 C10,22 4,30 0,32 C-4,30 -10,22 -16,10 C-24,-8 -18,-24 0,-24 Z"
    )
    return (
        f'<g transform="translate({x} {y})">{_path(berry, "#d23a3a", 2)}'
        f"{_path('M-12,-22 L0,-32 L12,-22 L0,-18 Z', '#4c9a3c', 1.4)}"
        f'<g fill="#f6e27a"><circle cx="-6" cy="-6" r="1.6"/><circle cx="6" cy="2" r="1.6"/><circle cx="-2" cy="12" r="1.6"/></g></g>'
    )


def _tomato(x: float, y: float) -> str:
    return (
        f'<g transform="translate({x} {y})">{_path("M0,-22 C22,-22 28,-2 22,12 C16,26 -16,26 -22,12 C-28,-2 -22,-22 0,-22 Z", "#c8312e", 2)}'
        f"{_path('M-10,-20 L0,-30 L10,-20 L4,-16 L0,-20 L-4,-16 Z', '#4c9a3c', 1.4)}"
        f"{_highlight('M-14,-8 Q-12,-16 -4,-17', 2, 0.6)}</g>"
    )


def _mushroom(x: float, y: float) -> str:
    return (
        f'<g transform="translate({x} {y})">{_path("M-9,2 L-7,26 Q0,30 7,26 L9,2 Z", "#efe9da", 2)}'
        f"{_path('M-26,4 C-26,-20 -10,-28 0,-28 C10,-28 26,-20 26,4 Q0,12 -26,4 Z', '#cdb797', 2)}"
        f"{_highlight('M-16,-8 Q-12,-18 -4,-20', 2, 0.5)}</g>"
    )


def _carrot(x: float, y: float) -> str:
    return (
        f'<g transform="translate({x} {y}) rotate(-14)">{_path("M-8,-20 L8,-20 L3,34 L-3,34 Z", "#e07a1f", 2)}'
        f"{_line('M-6,-8 L-1,-8 M2,6 L7,6 M-4,18 L0,18', 1.4)}"
        f"{_path('M-6,-20 L-10,-34 L-2,-26 L0,-38 L2,-26 L10,-34 L6,-20 Z', '#4c9a3c', 1.4)}</g>"
    )


def _bean(x: float, y: float) -> str:
    return (
        f'<g transform="translate({x} {y})">{_path("M-20,22 C-24,0 -10,-16 6,-26 C12,-22 14,-18 10,-14 C0,-6 -2,6 -2,22 Z", "#5a9a3a", 2)}'
        f"{_line('M-12,18 C-14,2 -4,-10 4,-20', 1.2, HALF)}</g>"
    )


def _herb(x: float, y: float) -> str:
    leaf = "M0,0 C-14,-8 -14,-26 0,-34 C14,-26 14,-8 0,0 Z"
    return (
        f'<g transform="translate({x} {y})">'
        f'<g transform="rotate(-38) translate(0 -2)">{_path(leaf, "#3a8f6a", 1.6)}</g>'
        f'<g transform="rotate(38) translate(0 -2)">{_path(leaf, "#2f7d5a", 1.6)}</g>'
        f'<g transform="translate(0 4)">{_path(leaf, "#47a57a", 1.6)}</g>'
        f"{_line('M0,0 L0,-22', 1.0, HALF)}</g>"
    )


def _pepper(x: float, y: float) -> str:
    return (
        f'<g transform="translate({x} {y})">{_path("M-16,-16 C-26,0 -20,24 -4,28 C0,30 6,30 10,28 C24,22 26,-2 16,-16 C8,-22 -8,-22 -16,-16 Z", "#c8312e", 2)}'
        f"{_path('M-3,-18 L-1,-30 L4,-30 L4,-18 Z', '#4c9a3c', 1.4)}"
        f"{_highlight('M-14,-6 Q-14,-14 -6,-16', 2, 0.6)}</g>"
    )


#: What a punnet holds, by the ``produce`` param (a punnet of strawberries when it is absent).
PRODUCE = {
    "strawberry": _strawberry,
    "tomato": _tomato,
    "mushroom": _mushroom,
    "carrot": _carrot,
    "bean": _bean,
    "herb": _herb,
    "pepper": _pepper,
}


def punnet(paint: str, fill: Fill, label: str | None, produce: str = "strawberry") -> list[str]:
    """A punnet of ``produce`` (one of :data:`PRODUCE`): the fruit or vegetable it is named for."""
    item = PRODUCE[produce]
    berries = [
        item(x, y)
        for x, y in (
            (126, 186),
            (166, 176),
            (206, 182),
            (246, 174),
            (282, 188),
            (146, 200),
            (226, 200),
            (266, 204),
        )
    ]
    slots = " ".join(f"M{x},236 L{x + (x - 200) * -0.08:.1f},344" for x in range(112, 300, 20))
    return [
        *berries,
        _path("M86,204 L314,204 L288,356 L112,356 Z", "#eef6f8"),
        _line(slots, 1.0, ' stroke-opacity=".5"'),
        _path("M96,224 L304,224 L296,276 L104,276 Z", paint, LW_DETAIL),
        _word(label or "", 200, 250, 186, 40, "#ffffff") if label else "",
    ]


register({"punnet": punnet})
