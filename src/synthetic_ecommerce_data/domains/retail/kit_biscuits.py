"""The biscuit pack (gen#608): a wrapped sleeve, not the kit's upright cereal-style carton.

==============  ===================================================  ======
shape           draws                                                params
==============  ===================================================  ======
sleeve          a flow-wrapped sleeve lying on its side: crimped      --
                ends, a lighter band along the top edge, a label panel
==============  ===================================================  ======

It paints the record's fill on the wrapper and carries the product word on a white label
panel, as the kit's other packs do (``kit.box``); the panel also carries the range name and
the band of flavor colors (``kit._panel`` reads them from the drawing's marks).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import Fill, _mix, _panel, _path, register


def sleeve(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A flow-wrapped sleeve lying on its side: crimped ends, a top band, a label panel."""
    crimp_l = " ".join(f"L{58 if i % 2 else 70},{140 + i * 10}" for i in range(15))
    crimp_r = " ".join(f"L{342 if i % 2 else 330},{290 - i * 10}" for i in range(15))
    body = "M72,148 Q200,130 328,148 L328,282 Q200,300 72,282 Z"
    return [
        _path(f"M72,140 {crimp_l} L72,290 Z", paint, 1.6, ' class="crimp"'),
        _path(f"M328,290 {crimp_r} L328,140 Z", paint, 1.6, ' class="crimp"'),
        _path(body, paint),
        _path("M72,148 Q200,130 328,148 L328,160 Q200,142 72,160 Z", _mix(fill.base, "#ffffff", 0.35), 1.6),
        *_panel(104, 176, 192, 80, label, 44),
    ]


register({"sleeve": sleeve})
