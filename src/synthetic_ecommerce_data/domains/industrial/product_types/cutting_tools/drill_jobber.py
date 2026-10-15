"""drill_jobber: a modelled type declared in its own module (#61).

The builder is ``Generator._build_drill``, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.price import _model
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import drill
from synthetic_ecommerce_data.domains.industrial.vocab import _DRILL


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_drill(type_key, category)


SPEC = TypeSpec(
    "drill_jobber",
    category=(
        "Holemaking",
        "Drilling & Drill Bits",
        "Metalworking & Multipurpose Drill Bits",
        "Jobber Length Drill Bits",
    ),
    standards_family="cutting_tool",
    vocab=_DRILL,
    figure=drill,
    extent=(0.52, 8.8),
    make=_make,
    share=0.11,
    price=_model("drill_jobber", 4.435, 0.25, 0.634, 0.182),
    claims=lambda facts, *, metric, provenance, standard: ["DIN 338" if metric else "ASME B94.11M"],
    may_claim=frozenset({"ASME B94.11M", "DIN 338"}),
    key_attributes=("Decimal Equivalent", "Size"),
    title_attributes=("Size",),
    unit_primary="Size",
    use_lines=(
        "For hole-making in the shop.",
        "Drills holes in general shop work.",
    ),
)
