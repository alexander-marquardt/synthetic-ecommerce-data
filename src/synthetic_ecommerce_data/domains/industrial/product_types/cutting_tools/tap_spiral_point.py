"""tap_spiral_point: a modelled type declared in its own module (#61).

The builder is ``Generator`` 's own, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import tap
from synthetic_ecommerce_data.domains.industrial.vocab import _TAP


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_tap(type_key, category)


def _claims(facts, *, metric, provenance, standard):
    return ["ISO 529" if metric else "ASME B94.9"]


SPEC = TypeSpec(
    "tap_spiral_point",
    category=("Threading", "Taps", "Spiral Point Taps"),
    standards_family="cutting_tool",
    vocab=_TAP,
    figure=tap,
    extent=(0.52, 4.15),
    make=_make,
    share=0.07,
    price=FITTED["tap_spiral_point"],
    claims=_claims,
    may_claim=frozenset({"ISO 529", "ASME B94.9"}),
    key_attributes=("Thread Size",),
    threaded="Thread Size",
    cutting=True,
    use_lines=(
        "Pushes chips ahead of the tap.",
        "Cuts internal threads in through holes.",
    ),
)
