"""Socket head cap screws: the first type declared in a module of its own (#48).

The builder and the vocabulary are the socket-screw family's, shared with the
flat, button and low head screws; what is this type's own is its category,
its drawing extent, its use lines and its share of the build.
"""

from __future__ import annotations

from typing import Any

from ...catalog.typespec import TypeSpec
from ...catalog.vocab import _SOCKET_SCREW
from ...drawing.figures import _broken


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Called through the generator, so this module never imports generate.py,
    # which registers the type modules at the end of its own import.
    return gen._build_socket_screw(type_key, category)


SPEC = TypeSpec(
    "screw_socket_head",
    category=("Fasteners", "Bolts, Screws & Cap Screws", "Socket Cap Screws"),
    standards_family="fastener",
    vocab=_SOCKET_SCREW,
    figure=_broken(2.75, 5.95),
    extent=(2.75, 5.95),
    make=_make,
    share=0.12,
    use_lines=(
        "Driven with a hex key.",
        "Fastens parts into a tapped hole or with a nut.",
    ),
)
