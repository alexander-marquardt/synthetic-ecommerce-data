"""Breadth shapes drawn from found SVG files (#102)."""

from __future__ import annotations

from synthetic_ecommerce_data.core.drawing.model import Figure


def load(name: str, extent_in: float) -> Figure:
    del name, extent_in
    return Figure()
