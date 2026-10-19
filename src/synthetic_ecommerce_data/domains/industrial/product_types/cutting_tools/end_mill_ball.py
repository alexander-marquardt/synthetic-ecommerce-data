"""end_mill_ball: a modelled type declared in its own module (#61).

The builder is ``Generator`` 's own, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import end_mill
from synthetic_ecommerce_data.domains.industrial.vocab import _END_MILL


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_end_mill(type_key, category)


def _claims(facts, *, metric, provenance, standard):
    if metric:
        return ["DIN 6527" if facts.get("Material", "") == "Solid Carbide" else "ISO 1641"]
    return ["ANSI B94.19"]


SPEC = TypeSpec(
    "end_mill_ball",
    category=("Milling", "End Mills", "Ball End Mills"),
    standards_family="cutting_tool",
    vocab=_END_MILL,
    figure=lambda record: end_mill(record, "Ball Nose"),
    extent=(3.3, 9.8),
    make=_make,
    share=0.11,
    price=FITTED["end_mill_ball"],
    claims=_claims,
    may_claim=frozenset({"ISO 1641", "DIN 6527", "ANSI B94.19"}),
    key_attributes=("Milling Dia.",),
    unit_primary="Milling Dia.",
    cutting=True,
    use_lines=(
        "For contouring and profiling curved surfaces.",
        "Cuts radiused slots and contoured surfaces.",
    ),
)
