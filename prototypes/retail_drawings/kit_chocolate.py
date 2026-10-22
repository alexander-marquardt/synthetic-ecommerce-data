"""The chocolate selection box (gen#609).

==============  ===================================================  ======
shape           draws                                                params
==============  ===================================================  ======
chocolate_box   a flat, wide, shallow lidded box seen at a slight     --
                angle, a ribbon across the lid
==============  ===================================================  ======

The record's fill paints the lid and the front of the box; the label panel on the lid carries
the product word, the range name and the band of the style's flavour colors (``kit._panel``).
The pack scale (gen#543) draws a smaller box smaller on the same sheet, so a 150g selection is
visibly smaller than a 400g one.
"""

from __future__ import annotations

from kit import LW_DETAIL, Fill, _line, _mix, _panel, _path, _shade, register

RIBBON = "#d9b45a"


def _tag(cls: str, element: str) -> str:
    """``element`` (a ``<path .../>``) with a ``class`` so a test and a reader can find the part."""
    return element.replace("<path ", f'<path class="{cls}" ', 1)


def chocolate_box(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A flat box, wide and shallow: the lid's top face towards the viewer, the front and one
    side below it, a ribbon across the lid and down the front, the label panel on the lid."""
    side = _shade(fill.base, 0.25)
    ribbon = _shade(RIBBON, 0.1)
    return [
        _path("M304,290 L360,200 L360,250 L304,340 Z", side),
        _path("M40,290 L304,290 L304,340 L40,340 Z", paint),
        _line("M40,308 L304,308 M304,308 L360,218", LW_DETAIL, ' stroke-opacity=".7"'),
        _tag("lid", _path("M40,290 L96,200 L360,200 L304,290 Z", _mix(fill.base, "#ffffff", 0.18))),
        _tag("ribbon", _path("M268,290 L324,200 L346,200 L290,290 Z", RIBBON, LW_DETAIL)),
        _tag("ribbon", _path("M268,290 L290,290 L290,340 L268,340 Z", ribbon, LW_DETAIL)),
        *_panel(100, 214, 150, 62, label, 40),
    ]


register({"chocolate_box": chocolate_box})
