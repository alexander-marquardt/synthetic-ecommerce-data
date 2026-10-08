"""The domain-neutral part of a brand house style: shared by every prototype catalog.

A house style is one declared row per brand (never a hash of its name), and
the drawing a catalog already makes is dressed in it: a paper, a frame, a logo
mark and a name lockup over the product, whose outline is re-inked in the
brand's hand. What a row holds and how a lockup is laid out belong to each
catalog (``retail_drawings/house_styles.py``,
``industrial_drawings/industrial_styles.py``); this module holds what both
need and neither owns:

* number formatting and the primitive shapes marks are built from
  (:func:`dot`, :func:`ring`, :func:`stroke`, :func:`hexagon`, ...);
* :func:`register_marks`, which reads a module's ``m_*`` functions into its
  mark table, and :func:`mark_group`, which places a unit-space mark;
* wordmarks set without a font engine: :func:`text_width` from an average
  glyph advance, :func:`fit_size` and :func:`wordmark`;
* :func:`texture`, the faint paper patterns;
* :func:`restyle_strokes`, the outline re-inked in a brand's colour and weight;
* :func:`compose`, the sheet, product and overlay as one SVG;
* :func:`differing` and :func:`duplicates`, what the table tests are built on.

Every function returns SVG text; nothing here chooses a brand's look.
"""

# ruff: noqa: E501 -- SVG literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable, Hashable, Iterable
from dataclasses import astuple
from html import escape
from typing import Protocol

# --------------------------------------------------------------------------
# Numbers and primitive shapes
# --------------------------------------------------------------------------


def n(v: float) -> str:
    """``v`` with at most three decimals and no trailing zeros."""
    return f"{v:.3f}".rstrip("0").rstrip(".")


def star(x: float, y: float, r: float, c: str, points: int = 5, inner: float = 0.45) -> str:
    pts = []
    for k in range(2 * points):
        a = -math.pi / 2 + k * math.pi / points
        rr = r if k % 2 == 0 else r * inner
        pts.append(f"{n(x + rr * math.cos(a))},{n(y + rr * math.sin(a))}")
    return f'<polygon points="{" ".join(pts)}" fill="{c}"/>'


def ring(x: float, y: float, r: float, w: float, c: str) -> str:
    return f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="none" stroke="{c}" stroke-width="{n(w)}"/>'


def dot(x: float, y: float, r: float, c: str, extra: str = "") -> str:
    return f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{c}"{extra}/>'


def stroke(d: str, w: float, c: str, join: str = "round") -> str:
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="{join}"/>'


def diamond(x: float, y: float, h: float) -> str:
    return f"M{n(x)},{n(y - h)} L{n(x + h)},{n(y)} L{n(x)},{n(y + h)} L{n(x - h)},{n(y)} Z"


def polygon_d(x: float, y: float, r: float, sides: int, turn: float = 0.0) -> str:
    """A regular polygon's path data; ``turn`` rotates it (radians)."""
    pts = [
        (x + r * math.cos(turn + 2 * math.pi / sides * k), y + r * math.sin(turn + 2 * math.pi / sides * k))
        for k in range(sides)
    ]
    return "M" + " L".join(f"{n(a)},{n(b)}" for a, b in pts) + " Z"


def hexagon(x: float, y: float, r: float) -> str:
    return polygon_d(x, y, r, 6)


# --------------------------------------------------------------------------
# Marks
# --------------------------------------------------------------------------

MarkFn = Callable[[str], list[str]]


def register_marks(namespace: dict[str, object]) -> dict[str, MarkFn]:
    """``{name: fn}`` for every ``m_<name>`` function in ``namespace`` (a module's globals)."""
    return {
        name[2:]: fn  # type: ignore[misc]
        for name, fn in list(namespace.items())
        if name.startswith("m_") and callable(fn)
    }


def mark_group(body: str, cx: float, cy: float, size: float) -> str:
    """A unit-space (-1..1) mark ``body``, ``size`` px across, centred on (cx, cy)."""
    return f'<g class="mark" transform="translate({n(cx)} {n(cy)}) scale({n(size / 2)})">{body}</g>'


# --------------------------------------------------------------------------
# Wordmarks
# --------------------------------------------------------------------------


class Lettering(Protocol):
    """What a wordmark reads from a house style row."""

    weight: int
    case: str
    spacing: float
    italic: bool


def cased(case: str, text: str) -> str:
    return {"caps": text.upper(), "lower": text.lower()}.get(case, text)


def text_width(advance: float, style: Lettering, text: str, size: float) -> float:
    """An estimate of ``text``'s width, from the font's average ``advance`` per em."""
    f = advance * {"caps": 1.22, "smallcaps": 1.1}.get(style.case, 1.0)
    f *= 1.07 if style.weight == 700 else 1.0
    return len(text) * (size * f + style.spacing)


def fit_size(
    advance: float, style: Lettering, text: str, max_width: float, start: float, floor: float
) -> float:
    """The largest size from ``start`` down to ``floor``, in half points, that fits ``max_width``."""
    size = start
    while size > floor and text_width(advance, style, text, size) > max_width:
        size -= 0.5
    return size


def wordmark(
    family: str,
    style: Lettering,
    text: str,
    x: float,
    y: float,
    size: float,
    colour: str,
    anchor: str = "start",
    extra: Iterable[str] = (),
) -> str:
    """``text`` in ``family`` and ``style``'s treatment; (x, y) is the baseline anchor."""
    attrs = [
        f'x="{x:.1f}" y="{y:.1f}"',
        f'font-family="{family}"',
        f'font-size="{size:g}"',
        f'font-weight="{style.weight}"',
        f'fill="{colour}"',
        f'text-anchor="{anchor}"',
    ]
    if style.spacing:
        attrs.append(f'letter-spacing="{style.spacing:g}"')
    if style.case == "smallcaps":
        attrs.append('font-variant="small-caps"')
    if style.italic:
        attrs.append('font-style="italic"')
    attrs.extend(extra)
    return f"<text {' '.join(attrs)}>{escape(cased(style.case, text))}</text>"


# --------------------------------------------------------------------------
# Paper textures
# --------------------------------------------------------------------------

#: Texture -> (tile px, the tile's body with ``{c}`` for the colour).
TEXTURE_TILES: dict[str, tuple[int, str]] = {
    "dots": (14, '<circle cx="7" cy="7" r="1.1" fill="{c}" fill-opacity=".22"/>'),
    "lines": (10, '<path d="M0,9.5 L10,9.5" stroke="{c}" stroke-opacity=".12" stroke-width="1"/>'),
    "grid": (
        16,
        '<path d="M0,15.5 L16,15.5 M15.5,0 L15.5,16" stroke="{c}" stroke-opacity=".1" stroke-width="1"/>',
    ),
    "diagonal": (
        10,
        '<path d="M-2,2 L2,-2 M0,10 L10,0 M8,12 L12,8" stroke="{c}" stroke-opacity=".1" stroke-width="1"/>',
    ),
    "hatch": (12, '<path d="M0,12 L12,0 M0,0 L12,12" stroke="{c}" stroke-opacity=".08" stroke-width="1"/>'),
}


def texture(
    kind: str, colour: str, uid: str, width: float, height: float, tiles: dict[str, tuple[int, str]] | None = None
) -> tuple[str, str]:
    """(pattern def, the rect that paints it) for a paper texture; ``("", "")`` for ``none``."""
    if kind == "none":
        return "", ""
    tile, body = (tiles or TEXTURE_TILES)[kind]
    pid = f"tex-{uid}"
    return (
        f'<pattern id="{pid}" width="{tile}" height="{tile}" patternUnits="userSpaceOnUse">{body.format(c=colour)}</pattern>',
        f'<rect width="{n(width)}" height="{n(height)}" fill="url(#{pid})"/>',
    )


# --------------------------------------------------------------------------
# The product's outline in the brand's hand
# --------------------------------------------------------------------------

_WIDTH = re.compile(r'stroke-width="([0-9]*\.?[0-9]+)"')
_ELEMENT = re.compile(r"<(?:path|rect|circle|ellipse|polygon|polyline|line)\b[^>]*/>")


def restyle_strokes(
    fragment: str,
    ink: str,
    *,
    to_ink: str,
    factor: float,
    sharp: bool,
    dashed: bool = False,
    dash_min: float = 2.5,
) -> str:
    """Strokes in ``ink`` re-inked ``to_ink``, ``factor`` times as wide, with sharp or kept joins.

    Only strokes in ``ink`` change; fills, patterns and other strokes are the
    product's and stay as drawn. ``dashed`` dashes the strokes at least
    ``dash_min`` wide.
    """

    def one(el: str) -> str:
        if f'stroke="{ink}"' not in el:
            return el
        m = _WIDTH.search(el)
        width = float(m.group(1)) if m else 1.0
        el = el.replace(f'stroke="{ink}"', f'stroke="{to_ink}"')
        if m:
            el = el[: m.start()] + f'stroke-width="{width * factor:.2f}"' + el[m.end() :]
        if sharp:
            el = el.replace('stroke-linejoin="round"', 'stroke-linejoin="miter"').replace(
                'stroke-linecap="round"', 'stroke-linecap="butt"'
            )
            if "stroke-linejoin" not in el:
                el = el.replace("/>", ' stroke-linejoin="miter"/>', 1)
        if dashed and width >= dash_min and "stroke-dasharray" not in el:
            el = el.replace("/>", ' stroke-dasharray="9 4"/>', 1)
        return el

    return _ELEMENT.sub(lambda m: one(m.group(0)), fragment)


# --------------------------------------------------------------------------
# The sheet
# --------------------------------------------------------------------------


def compose(
    width: float,
    height: float,
    defs: str,
    sheet: Iterable[str],
    transform: str,
    product: str,
    overlay: Iterable[str],
) -> str:
    """One SVG: the sheet under the transformed product, the brand overlay on top."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(width)}" height="{n(height)}" viewBox="0 0 {n(width)} {n(height)}">',
        f"<defs>{defs}</defs>" if defs else "",
        *sheet,
        f'<g class="product" transform="{transform}">{product}</g>',
        f'<g class="brand">{"".join(overlay)}</g>',
        "</svg>",
    ]
    return "".join(p for p in parts if p)


# --------------------------------------------------------------------------
# What the table tests are built on
# --------------------------------------------------------------------------


def differing(a: object, b: object) -> int:
    """How many fields two rows (dataclass instances of one type) differ in."""
    return sum(x != y for x, y in zip(astuple(a), astuple(b), strict=True))  # type: ignore[arg-type]


def duplicates(values: Iterable[Hashable]) -> dict[Hashable, int]:
    """Each value that occurs more than once, with its count."""
    return {v: c for v, c in Counter(values).items() if c > 1}
