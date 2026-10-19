"""bolt_hex: a modelled type declared in its own module (#61).

The builder is ``Generator`` 's own, called through the generator because
``generate`` imports the type tables, which discover this module.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial import conformance
from synthetic_ecommerce_data.domains.industrial.drawing.figures import _broken
from synthetic_ecommerce_data.domains.industrial.vocab import _HEX_BOLT


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return gen._build_hex_bolt(type_key, category)


def _claims(facts, *, metric, provenance, standard):
    grade = facts.get("Grade", "")
    out = [provenance]
    if provenance in conformance.EQUIVALENTS:
        out.append(conformance.EQUIVALENTS[provenance])
    if grade.startswith("Grade"):
        out.append("SAE J429")
    elif grade.startswith("Class"):
        out.append("ISO 898-1")
    return out


SPEC = TypeSpec(
    "bolt_hex",
    category=("Fasteners", "Bolts, Screws & Cap Screws", "Hex Head Bolts"),
    standards_family="fastener",
    vocab=_HEX_BOLT,
    figure=_broken(2.85, 5.35),
    extent=(2.85, 5.35),
    make=_make,
    share=0.09,
    price=FITTED["bolt_hex"],
    claims=_claims,
    may_claim=frozenset(
        {
            "DIN 961",
            "ISO 4017",
            "ISO 8765",
            "SAE J429",
            "ISO 898-1",
            "DIN 933",
            "ISO 8676",
            "ASME B18.2.1",
            "ISO 4014",
        }
    ),
    key_attributes=("Dia./Thread Size",),
    threaded="Dia./Thread Size",
    fastener=True,
    use_lines=(
        "Tightened with a wrench, for machinery and structural assembly.",
        "Fastens parts with a nut or into a tapped hole.",
    ),
)
