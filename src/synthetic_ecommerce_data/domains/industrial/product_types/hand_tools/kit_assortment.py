"""kit_assortment: a modelled type declared in its own module (#61).

The builder is the newer-type builder in ``newtypes``.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.core.price import FITTED
from synthetic_ecommerce_data.domains.industrial.drawing.figures import kit
from synthetic_ecommerce_data.domains.industrial.newtypes import build_kit
from synthetic_ecommerce_data.domains.industrial.vocab import _KIT


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    return build_kit(gen, type_key, category)


SPEC = TypeSpec(
    "kit_assortment",
    category=("Hand Tools", "Tool Sets & Kits", "Assortment Kits"),
    standards_family="hand_tool",
    vocab=_KIT,
    figure=kit,
    extent=(5.65, 2.95),
    make=_make,
    share=60 / 2600,
    price=FITTED["kit_assortment"],
    may_claim=frozenset(),
    key_attributes=("Piece Count",),
    newer=True,
    use_lines=(
        "Every size in one case.",
        "A set of the common sizes, kept together.",
    ),
)
