"""The biscuit pack (gen#608): a wrapped sleeve, not the kit's upright cereal-style carton.

==============  ===================================================  ======
shape           draws                                                params
==============  ===================================================  ======
sleeve          a flow-wrapped sleeve lying on its side: crimped      --
                ends, a fin seal along the back, a label panel
==============  ===================================================  ======

It paints the record's fill on the wrapper and carries the product word on a white label
panel, as the kit's other packs do (``kit.box``); the panel also carries the range name and
the band of flavor colors (``kit._panel`` reads them from the drawing's marks).
"""

from __future__ import annotations

from kit import Fill, _panel, _path, register


def sleeve(paint: str, fill: Fill, label: str | None) -> list[str]:
    """STUB (red commit): the upright carton, until the sleeve is drawn."""
    return [
        _path("M110,74 L270,74 L270,362 L110,362 Z", paint),
        *_panel(118, 120, 144, 96, label, 50),
    ]


register({"sleeve": sleeve})
