"""nut_hex: a modelled type declared in its own module (#61).

The builder is the newer-type builder in ``newtypes``.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import hex_nut
from synthetic_ecommerce_data.domains.industrial.newtypes import build_nut
from synthetic_ecommerce_data.domains.industrial.vocab import _NUT


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return build_nut(gen, type_key, category)


def _claims(facts, *, metric, provenance, standard):
    # The dimensional standard is the one the rows were READ from, never
    # one chosen by style name: a heavy hex nut is not an ISO 4032 nut,
    # and a fine-pitch nut is not a coarse-thread standard's.
    grade = facts.get("Grade", "")
    out = [standard]
    if metric and grade.startswith("Class"):
        out.append("ISO 898-2")
    if not metric and grade.startswith("Grade"):
        out.append("SAE J995")
    return out


SPEC = TypeSpec(
    "nut_hex",
    category=("Fasteners", "Nuts", "Hex Nuts"),
    standards_family="fastener",
    vocab=_NUT,
    figure=hex_nut,
    extent=(1.95, 3.5),
    make=_make,
    share=700 / 2600,
    price=FITTED["nut_hex"],
    claims=_claims,
    may_claim=frozenset(
        {"ASME B18.2.2", "SAE J995", "ISO 898-2", "ISO 4032", "ISO 8673", "ISO 4035", "ISO 8675"}
    ),
    key_attributes=("Thread Size",),
    threaded="Thread Size",
    fastener=True,
    newer=True,
    use_lines=(
        "Mates with a bolt or threaded rod of the same thread.",
        "Tightened with a wrench onto a bolt or threaded rod.",
    ),
)
