"""Step 2: a product of our own around each picture of a manifest (gen#1022). Stub."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from synthetic_ecommerce_data.picture_products.manifest import Picture


@dataclass(frozen=True)
class Product:
    """One product of our own: its catalog document and its picture."""

    doc: dict
    image_name: str
    svg: str


def write(pictures: Iterable[Picture]) -> list[Product]:
    """Stub: writes nothing yet."""
    return []
