"""Socket head cap screws: the first type declared in a module of its own (#48).

The builder and the vocabulary are the socket-screw family's, shared with the
flat, button and low head screws; what is this type's own is its category,
its family row (``LINE``: standards, head style, head accessor), its drawing
extent, its use lines and its share of the build.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.price import (
    CENSUS,
    ENDINGS,
    LENGTH_CENSUS,
    PACK_SLOPES,
    TYPE_TIERS,
    PriceModel,
)
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial import conformance
from synthetic_ecommerce_data.domains.industrial.drawing.figures import _broken
from synthetic_ecommerce_data.domains.industrial.standards import SocketScrewLine, socket_head
from synthetic_ecommerce_data.domains.industrial.vocab import _SOCKET_SCREW

#: This type's row of the socket-screw family: its standards, its head style
#: and name, and which columns of the standard are its head.
LINE = SocketScrewLine("ISO 4762", "ASME B18.3", "Socket", "Socket Head Cap Screw", socket_head)


#: The census slopes (size, length and pack), tiers and endings; the anchor
#: and both sigmas fitted by ``scripts/fit_price_model.py``. The button, low
#: and flat head screws borrow this model (``price.BORROWS``): the census has
#: no prices of their own.
PRICE = PriceModel(
    # @fit-begin screw_socket_head
    anchor=15.16,
    anchor_key=0.25,
    slope=CENSUS["screw_socket_head"].slope,
    group_sigma=0.000,
    sku_sigma=0.234,
    size_sigma=0.562,
    # @fit-end
    endings=ENDINGS["screw_socket_head"],
    pack_attribute="Units per Pack",
    pack_slope=PACK_SLOPES["screw_socket_head"],
    pack_ref=100.0,
    length_slope=LENGTH_CENSUS["screw_socket_head"].slope,
    tiers=TYPE_TIERS["screw_socket_head"],
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
    claims=lambda facts, *, metric, provenance, standard: conformance.socket_screw(
        facts, metric=metric, provenance=provenance, cap_screw=True
    ),
    may_claim=frozenset(
        {"ISO 4762", "DIN 912", "ASME B18.3", "ASTM A574", "ASTM F837", "ISO 898-1", "ISO 3506-1"}
    ),
    key_attributes=("Dia./Thread Size",),
    threaded="Dia./Thread Size",
    fastener=True,
    use_lines=(
        "Driven with a hex key.",
        "Fastens parts into a tapped hole or with a nut.",
    ),
)
