"""Own-kind shapes for the home furniture the kit could not draw (gen#1022): stub."""

# ruff: noqa: E501 -- param tables and SVG path literals read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import Fill, register
from synthetic_ecommerce_data.domains.retail.kit_furniture import _rect

PARAMS: dict[str, dict[str, tuple[str, ...]]] = {
    "bar_stool": {"height": ("counter", "bar"), "back": ("none", "low", "full"), "seat": ("round", "square"), "base": ("four_leg", "pedestal", "sled")},
    "desk": {"outline": ("rectangular", "l_shaped"), "drawers": ("0", "1", "2", "3", "4"), "legs": ("straight", "panel", "hairpin")},
    "office_chair": {"back": ("mid", "high"), "cover": ("mesh", "fabric"), "arms": ("yes", "no"), "base": ("castor", "sled")},
    "tv_stand": {"doors": ("0", "1", "2", "3", "4"), "shelves": ("0", "1", "2", "3"), "legs": ("short", "plinth", "hairpin")},
    "kitchen_island": {"doors": ("0", "1", "2", "3", "4"), "drawers": ("0", "1", "2", "3"), "top": ("wood", "marble_effect", "steel"), "wheels": ("no", "yes")},
}  # fmt: skip


def _stub(paint: str, fill: Fill, label: str | None, **params: str) -> list[str]:
    return [_rect(100, 100, 200, 200, paint)]


register({shape: _stub for shape in PARAMS})
