"""washer_flat: a modelled type declared in its own module (#61).

The builder is ``Generator`` 's own, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import washer
from synthetic_ecommerce_data.domains.industrial.vocab import _WASHER


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_washer(type_key, category)


def _claims(facts, *, metric, provenance, standard):
    return ["ISO 7089", "DIN 125-A"]


SPEC = TypeSpec(
    "washer_flat",
    category=("Fasteners", "Washers & Shims", "Flat & Square Flat Washers", "Flat Washers"),
    standards_family="fastener",
    vocab=_WASHER,
    figure=washer,
    extent=(1.5, 2.15),
    make=_make,
    share=0.06,
    price=FITTED["washer_flat"],
    claims=_claims,
    may_claim=frozenset({"ISO 7089", "DIN 125-A"}),
    key_attributes=("Inside Dia.",),
    title_attributes=("Size",),
    fastener=True,
    use_lines=(
        "Spreads the load under a bolt head or nut.",
        "Protects the surface under a fastener and spreads its load.",
    ),
)
