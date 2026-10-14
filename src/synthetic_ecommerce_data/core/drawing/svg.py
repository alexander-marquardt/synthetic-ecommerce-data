"""A minimal SVG writer: shapes in, a small deterministic file out.

Why not matplotlib. The catalog's drawings carry NO text but the brand's
wordmark (maintainer ruling on elastic/prism-industrial-products#103,
2026-09-28, revised for the brand mark on 2026-10-08, synthetic-ecommerce-data#132):
no dimensions, no callouts, no labels, no SKU. Everything a shopper reads is on the
record -- title, description and attributes -- so text in the picture is
redundant, and it would pin a drawing to wording that can change. What is left
is line work and fills, and for that a figure library costs more than it gives:
its SVG carries metadata, clip-path ids and glyph definitions, and a card came
out at ~6 KB with live text or ~26 KB with glyph paths. Writing the few
primitives directly gives a file of a few hundred bytes to a couple of KB, byte
for byte the same on every machine, with nothing in it that could be text.

Coordinates are written with at most one decimal. The viewBox is 200 x 300, so
a tenth of a unit is well under a display pixel at any size a card is shown at.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from html import escape

#: The drawing's coordinate box. Portrait, the card's 150 x 220 box at the same
#: aspect near enough; the page scales it.
WIDTH = 200
HEIGHT = 300

Point = tuple[float, float]


def num(value: float) -> str:
    """A coordinate at one decimal, with no trailing zero and no ``-0``."""
    text = f"{value:.1f}"
    if text.endswith(".0"):
        text = text[:-2]
    return "0" if text in ("-0", "") else text


def path_d(points: Sequence[Point], closed: bool = True) -> str:
    """A polyline path from absolute points."""
    if not points:
        raise ValueError("a path needs at least one point")
    head, *rest = points
    parts = [f"M{num(head[0])} {num(head[1])}"]
    parts.extend(f"L{num(x)} {num(y)}" for x, y in rest)
    if closed:
        parts.append("Z")
    return "".join(parts)


def bars_d(rects: Sequence[tuple[float, float, float, float]]) -> str:
    """Many rectangles as one path's data. Each side is the difference of its
    ROUNDED corners, so an edge lands where an absolute path would put it and
    the closing ``z`` returns exactly to the start."""
    parts = []
    for x0, y0, x1, y1 in rects:
        left, top = round(min(x0, x1), 1), round(min(y0, y1), 1)
        wide, high = round(max(x0, x1), 1) - left, round(max(y0, y1), 1) - top
        parts.append(f"M{num(left)} {num(top)}h{num(wide)}v{num(high)}h{num(-wide)}z")
    return "".join(parts)


class Svg:
    """An ordered list of SVG elements, and the pattern definitions they use."""

    def __init__(self, background: str) -> None:
        self._defs: dict[str, str] = {}
        self._body: list[str] = []
        self._background = background

    def define(self, key: str, element: str) -> str:
        """Register a ``<defs>`` element once; return its id."""
        self._defs.setdefault(key, element)
        return key

    def add(self, element: str) -> None:
        self._body.append(element)

    def polygon(self, points: Sequence[Point], **attrs: str) -> None:
        self.add(f'<path d="{path_d(points)}"{_attrs(attrs)}/>')

    def polyline(self, points: Sequence[Point], **attrs: str) -> None:
        self.add(f'<path d="{path_d(points, closed=False)}" fill="none"{_attrs(attrs)}/>')

    def path(self, d: str, **attrs: str) -> None:
        self.add(f'<path d="{d}"{_attrs(attrs)}/>')

    def rect(self, x: float, y: float, w: float, h: float, **attrs: str) -> None:
        self.add(
            f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}"{_attrs(attrs)}/>'
        )

    def circle(self, cx: float, cy: float, r: float, **attrs: str) -> None:
        self.add(f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r)}"{_attrs(attrs)}/>')

    def text(self, x: float, y: float, content: str, **attrs: str) -> None:
        """A ``<text>`` element: the brand wordmark is the only text a drawing carries (#132)."""
        body = escape(content, quote=False)
        self.add(f'<text x="{num(x)}" y="{num(y)}"{_attrs(attrs)}>{body}</text>')

    def lines(self, segments: Iterable[tuple[Point, Point]], **attrs: str) -> None:
        """Many unconnected segments as ONE path element -- the cheap way to hatch."""
        d = "".join(f"M{num(a[0])} {num(a[1])}L{num(b[0])} {num(b[1])}" for a, b in segments)
        if d:
            self.add(f'<path d="{d}" fill="none"{_attrs(attrs)}/>')

    def to_bytes(self) -> bytes:
        defs = "".join(self._defs[key] for key in sorted(self._defs))
        head = (
            # The intrinsic size beside the viewBox: an <img> styled only
            # with max-width/max-height inside a flex item that does not
            # grow sizes a viewBox-only SVG to 0 x 0 -- served, and invisible
            # (seen on the live product page, 2026-09-28).
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}">'
            f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{self._background}"/>'
        )
        body = "".join(self._body)
        tail = "</svg>"
        return (head + (f"<defs>{defs}</defs>" if defs else "") + body + tail).encode("utf-8")


def _attrs(attrs: dict[str, str]) -> str:
    # ``stroke_width`` -> ``stroke-width``; sorted so the bytes never depend on
    # keyword order at a call site.
    return "".join(f' {key.replace("_", "-")}="{value}"' for key, value in sorted(attrs.items()))
