"""Suits sold as a set (gen#215): a women's trouser suit and a boys' suit, each its own shape.

``kit_suits`` draws the Mens tailoring pieces one at a time. A trouser suit and a boys' suit are
sold as the set, so each drawing shows the pieces together, a jacket over its trousers (and, for a
three piece boys' suit, a waistcoat beside them), every piece a ``class="piece"`` group so the
drawing counts what the record's ``piece_count`` states.

* ``trouser_suit(jacket, fit)``: the jacket is ``single`` (notch lapel), ``double`` (peak lapel
  and a second column of buttons) or ``collarless`` (a neck facing, no lapel); ``fit`` is the cut
  of the trouser leg, ``slim``, ``straight`` or ``wide``.
* ``boys_suit(pieces, fit)``: ``pieces`` 2 is a jacket and trousers, 3 adds the waistcoat; ``fit``
  is ``slim`` or ``regular``, which cuts the jacket and the trouser leg.

The jacket carries ``class="jacket-<style>"``, the trouser leg ``class="legfit-<fit>"`` (a trouser
suit) or ``class="fit-<fit>"`` (a boys' suit) and the set ``class="pieces-<n>"``, so
``tests/test_retail_suit_sets_215.py`` reads the record's choice back from the drawing. A shape is
painted in the record's fill and prints no size.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW_DETAIL, Fill, _line, _path, _shade, register
from kit_suits import _button, _g, _jacket_body, waistcoat

JACKETS = ("single", "double", "collarless")
LEG_FITS = ("slim", "straight", "wide")
BOY_FITS = ("slim", "regular")
BOY_PIECES = ("2", "3")
#: fit -> the half-width of one trouser leg at the hem.
_HALF = {"slim": 17, "straight": 24, "wide": 38, "regular": 28}
_TOP, _HEM = 70.0, 340.0


def _piece(parts: list[str], transform: str) -> str:
    return f'<g class="piece" transform="{transform}">' + "".join(parts) + "</g>"


def _legs(paint: str, fill: Fill, half: float, cls: str) -> list[str]:
    """Two trouser legs with a waistband, a button and a pressed crease down each."""
    top, hem, hip = _TOP, _HEM, 80
    left = f"M{200 - hip},{top} L200,{top} L200,{top + 96} L196,{hem} L{196 - 2 * half},{hem} L{200 - hip + 6},{top + 80} Z"
    right = f"M200,{top} L{200 + hip},{top} L{200 + hip - 6},{top + 80} L{204 + 2 * half},{hem} L204,{hem} L200,{top + 96} Z"
    band = f"M118,{top - 4} L282,{top - 4} L282,{top + 18} L118,{top + 18} Z"
    return [
        _g(cls, [_path(left, paint), _path(right, paint)]),
        _line(
            f"M160,{top + 24} L{196 - half},{hem} M240,{top + 24} L{204 + half},{hem}",
            1.2,
            ' stroke-opacity=".5"',
        ),
        _path(band, _shade(fill.base, 0.12), LW_DETAIL),
        f'<circle cx="206" cy="{top + 7}" r="4" fill="#d9d4c4" stroke="{INK}" stroke-width="1.2"/>',
        _line(f"M200,{top + 18} L200,{top + 96}", 1.4),
    ]


def trouser_suit(
    paint: str, fill: Fill, label: str | None, jacket: str = "single", fit: str = "straight"
) -> list[str]:
    jacket = jacket if jacket in JACKETS else "single"
    fit = fit if fit in LEG_FITS else "straight"
    lapel, buttons = {"single": ("notch", 2), "double": ("peak", 2), "collarless": ("none", 3)}[
        jacket
    ]
    body = _jacket_body(paint, fill, "tailored", lapel, buttons=buttons)
    if jacket == "double":  # the overlap panel of a double breasted front and its second column
        body.append(_path("M200,176 L166,176 L166,330 L200,330 Z", paint, LW_DETAIL))
        body += [_button(176, 202), _button(176, 250)]
    return [
        _piece([_g(f"jacket-{jacket}", body)], "translate(80 0) scale(.6)"),
        _piece(_legs(paint, fill, _HALF[fit], f"legfit-{fit}"), "translate(76 170) scale(.62)"),
    ]


def boys_suit(
    paint: str, fill: Fill, label: str | None, pieces: str = "2", fit: str = "regular"
) -> list[str]:
    n = 3 if pieces == "3" else 2
    fit = fit if fit in BOY_FITS else "regular"
    shift = -36 if n == 3 else 0
    out = [
        _piece(
            _jacket_body(paint, fill, fit, "notch", buttons=2),
            f"translate({80 + shift} 0) scale(.6)",
        ),
        _piece(
            _legs(paint, fill, _HALF[fit], f"fit-{fit}"), f"translate({76 + shift} 170) scale(.62)"
        ),
    ]
    if n == 3:
        out.append(_piece(waistcoat(paint, fill, None, fit, "5"), "translate(265 70) scale(.45)"))
    return [_g(f"pieces-{n}", out)]


SHAPES = {"trouser_suit": trouser_suit, "boys_suit": boys_suit}
register(SHAPES)
