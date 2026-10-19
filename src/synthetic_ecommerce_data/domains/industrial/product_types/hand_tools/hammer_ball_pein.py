"""hammer_ball_pein: a modelled type declared in its own module (#61).

The builder is ``Generator`` 's own, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import hammer
from synthetic_ecommerce_data.domains.industrial.vocab import HAMMER_VOCAB


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_hammer(type_key, category)


def _claims(facts, *, metric, provenance, standard):
    return ["ASME B107.400"]


SPEC = TypeSpec(
    "hammer_ball_pein",
    category=("Hand Tools", "Hammers"),
    standards_family="hand_tool",
    vocab=HAMMER_VOCAB,
    figure=hammer,
    extent=(5.8, 18.25),
    make=_make,
    share=0.04,
    price=FITTED["hammer_ball_pein"],
    claims=_claims,
    may_claim=frozenset({"ASME B107.400"}),
    key_attributes=("Head Weight",),
    use_lines=(
        "For peening, riveting and general metalwork.",
        "Shapes metal and sets rivets.",
    ),
)
