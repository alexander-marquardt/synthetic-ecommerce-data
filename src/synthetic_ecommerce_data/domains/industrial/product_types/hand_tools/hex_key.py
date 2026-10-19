"""hex_key: a modelled type declared in its own module (#61).

The builder is the newer-type builder in ``newtypes``.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import hex_key
from synthetic_ecommerce_data.domains.industrial.newtypes import build_hex_key
from synthetic_ecommerce_data.domains.industrial.vocab import _HEX_KEY


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return build_hex_key(gen, type_key, category)


def _claims(facts, *, metric, provenance, standard):
    return ["ISO 2936" if metric else "ASME B18.3"]


SPEC = TypeSpec(
    "hex_key",
    category=(
        "Hand Tools",
        "Screwdrivers & Hex Keys",
        "Hex & Torx Keys",
        "Hex Keys & Accessories",
        "Hex Keys",
    ),
    standards_family="hand_tool",
    vocab=_HEX_KEY,
    figure=hex_key,
    extent=(2.95, 9.85),
    make=_make,
    share=700 / 2600,
    price=FITTED["hex_key"],
    claims=_claims,
    may_claim=frozenset({"ASME B18.3", "ISO 2936"}),
    key_attributes=("Size",),
    unit_primary="Size",
    newer=True,
    use_lines=(
        "Drives hex socket fasteners.",
        "Turns hex socket screws.",
    ),
)
