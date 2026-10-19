"""abrasive_flap_disc: a modelled type declared in its own module (#61).

The builder is ``Generator`` 's own, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import flap_disc
from synthetic_ecommerce_data.domains.industrial.vocab import _FLAP_DISC


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_flap_disc(type_key, category)


def _claims(facts, *, metric, provenance, standard):
    return ["EN 13743", "oSa Certified"]


SPEC = TypeSpec(
    "abrasive_flap_disc",
    category=("Abrasives", "Coated & Non-Woven Abrasives", "Discs", "Flap Discs"),
    standards_family="abrasive",
    vocab=_FLAP_DISC,
    figure=flap_disc,
    extent=(7.25, 7.25),
    make=_make,
    share=0.05,
    price=FITTED["abrasive_flap_disc"],
    claims=_claims,
    may_claim=frozenset({"EN 13743", "oSa Certified"}),
    key_attributes=("Diameter",),
    unit_primary="Diameter",
    use_lines=(
        "For blending, deburring and finishing.",
        "Grinds and finishes in one step.",
    ),
)
