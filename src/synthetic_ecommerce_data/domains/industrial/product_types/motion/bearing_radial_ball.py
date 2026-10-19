"""bearing_radial_ball: a modelled type declared in its own module (#61).

The builder is the newer-type builder in ``newtypes``.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import bearing
from synthetic_ecommerce_data.domains.industrial.newtypes import build_bearing
from synthetic_ecommerce_data.domains.industrial.vocab import _BEARING


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return build_bearing(gen, type_key, category)


def _claims(facts, *, metric, provenance, standard):
    # ABMA 20 is "Radial Bearings of Ball, Cylindrical Roller and Spherical
    # Roller Types -- METRIC Design": it is the metric bearing's ABMA
    # standard, like ISO 15 and ISO 492. The inch R series is not in it, and
    # no inch-series standard could be confirmed from a readable source, so
    # an inch bearing claims none.
    if metric:
        return ["ISO 15", "ISO 492", "ABMA 20"]
    return []


SPEC = TypeSpec(
    "bearing_radial_ball",
    category=("Motion Control & Fluid Power", "Bearings", "Radial Ball Bearings"),
    standards_family="motion",
    vocab=_BEARING,
    figure=bearing,
    extent=(8.75, 13.25),
    make=_make,
    share=700 / 2600,
    price=FITTED["bearing_radial_ball"],
    claims=_claims,
    may_claim=frozenset({"ISO 15", "ABMA 20", "ISO 492"}),
    key_attributes=("Bore Dia.",),
    title_attributes=("Bearing Number", "Bore Dia."),
    unit_primary="Bore Dia.",
    newer=True,
    use_lines=(
        "Supports a rotating shaft.",
        "Carries a rotating shaft in its housing.",
    ),
)
