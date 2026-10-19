"""wheel_depressed_center: a modelled type declared in its own module (#61).

The builder is the newer-type builder in ``newtypes``.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import depressed_wheel
from synthetic_ecommerce_data.domains.industrial.newtypes import build_wheel
from synthetic_ecommerce_data.domains.industrial.vocab import _WHEEL


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return build_wheel(gen, type_key, category)


def _claims(facts, *, metric, provenance, standard):
    return ["ANSI B7.1", "EN 12413", "oSa Certified"]


SPEC = TypeSpec(
    "wheel_depressed_center",
    category=(
        "Abrasives",
        "Grinding & Cut-Off",
        "Grinding & Cut-Off Wheels",
        "Depressed-Center Wheels",
    ),
    standards_family="abrasive",
    vocab=_WHEEL,
    figure=depressed_wheel,
    extent=(9.3, 13.2),
    make=_make,
    share=700 / 2600,
    price=FITTED["wheel_depressed_center"],
    claims=_claims,
    may_claim=frozenset({"oSa Certified", "EN 12413", "ANSI B7.1"}),
    key_attributes=("Diameter",),
    unit_primary="Diameter",
    newer=True,
    use_lines=(
        "For grinding and surface preparation.",
        "The depressed center keeps the hub clear of the work.",
    ),
)
