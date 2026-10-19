"""screw_flat_head: a modelled type declared in its own module (#61).

The builder is ``Generator`` 's own, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial import conformance, standards
from synthetic_ecommerce_data.domains.industrial.drawing.figures import _broken
from synthetic_ecommerce_data.domains.industrial.vocab import _SOCKET_SCREW


#: This type's row of the socket-screw family.
LINE = standards.SocketScrewLine(
    "ISO 10642",
    "ASME B18.3.2",
    "Flat",
    "Socket Flat Head Cap Screw",
    standards.flat_head,
    length_over_head=True,
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_socket_screw(type_key, category, LINE)


SPEC = TypeSpec(
    "screw_flat_head",
    category=("Fasteners", "Bolts, Screws & Cap Screws", "Flat Socket Cap Screws"),
    standards_family="fastener",
    vocab=_SOCKET_SCREW,
    figure=_broken(3.7, 3.25),
    extent=(3.7, 3.25),
    make=_make,
    share=0.07,
    borrows="screw_socket_head",
    claims=lambda facts, *, metric, provenance, standard: conformance.socket_screw(
        facts, metric=metric, provenance=provenance
    ),
    may_claim=frozenset({"ASME B18.3.2", "ISO 898-1", "ASME B18.3", "ISO 10642", "ISO 3506-1"}),
    key_attributes=("Dia./Thread Size",),
    threaded="Dia./Thread Size",
    fastener=True,
    use_lines=(
        "Sits flush in a countersunk hole.",
        "For fastening where the head must not stand proud.",
    ),
)
