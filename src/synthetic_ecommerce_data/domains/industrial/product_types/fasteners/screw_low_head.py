"""screw_low_head: a modelled type declared in its own module (#61).

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
    "DIN 7984",
    "ASME B18.3.1G",
    "Low Socket",
    "Low Head Socket Cap Screw",
    standards.low_head,
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_socket_screw(type_key, category, LINE)


SPEC = TypeSpec(
    "screw_low_head",
    category=("Fasteners", "Bolts, Screws & Cap Screws", "Low Socket Cap Screws"),
    standards_family="fastener",
    vocab=_SOCKET_SCREW,
    figure=_broken(2.75, 3.3),
    extent=(2.75, 3.3),
    make=_make,
    share=0.04,
    borrows="screw_socket_head",
    claims=lambda facts, *, metric, provenance, standard: conformance.socket_screw(
        facts, metric=metric, provenance=provenance
    ),
    may_claim=frozenset({"ASME B18.3.1G", "ISO 898-1", "ASME B18.3", "DIN 7984", "ISO 3506-1"}),
    key_attributes=("Dia./Thread Size",),
    threaded="Dia./Thread Size",
    fastener=True,
    use_lines=(
        "A reduced-height head for tight clearances.",
        "Driven with a hex key where a standard head would not fit.",
    ),
)
