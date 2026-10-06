"""Socket head cap screws: the first type declared in a module of its own (#48).

The builder and the vocabulary are the socket-screw family's, shared with the
flat, button and low head screws; what is this type's own is its category,
its family row (``LINE``: standards, head style, head accessor), its drawing
extent, its use lines and its share of the build.
"""

from __future__ import annotations

from typing import Any

from ...catalog.price import CENSUS, ENDINGS, PriceModel
from ...catalog.standards import SocketScrewLine, socket_head
from ...catalog.typespec import TypeSpec
from ...catalog.vocab import _SOCKET_SCREW
from ...drawing.figures import _broken

#: This type's row of the socket-screw family: its standards, its head style
#: and name, and which columns of the standard are its head.
LINE = SocketScrewLine("ISO 4762", "ASME B18.3", "Socket", "Socket Head Cap Screw", socket_head)


#: The census slope and endings; the anchor and both sigmas fitted by
#: ``scripts/fit_price_model.py``. The button, low and flat head screws borrow
#: this model (``price.BORROWS``): the census has no prices of their own.
PRICE = PriceModel(
    # @fit-begin screw_socket_head
    anchor=21.5,
    anchor_key=0.25,
    line_sigma=0.3,
    sku_sigma=0.1,
    # @fit-end
    slope=CENSUS["screw_socket_head"].slope,
    endings=ENDINGS["screw_socket_head"],
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Called through the generator rather than imported from generate.py:
    # generate imports the type tables, which discover this module, so
    # importing generate from here would be an import cycle.
    return gen._build_socket_screw(type_key, category, LINE)


SPEC = TypeSpec(
    "screw_socket_head",
    category=("Fasteners", "Bolts, Screws & Cap Screws", "Socket Cap Screws"),
    standards_family="fastener",
    vocab=_SOCKET_SCREW,
    figure=_broken(2.75, 5.95),
    extent=(2.75, 5.95),
    make=_make,
    share=0.12,
    price=PRICE,
    use_lines=(
        "Driven with a hex key.",
        "Fastens parts into a tapped hole or with a nut.",
    ),
)
