"""What a product type needs to be a decoy's true type: :class:`Kind` (gen#513).

It lived in :mod:`decoy_rows`, which imports :mod:`feature_decoys` while its table is built, so a
module of that package could not import it without a cycle. :mod:`decoy_rows` re-exports it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Kind:
    """What a product type needs to be a :class:`Style`: its place, shape and defaults."""

    department: str
    path: tuple[str, ...]
    product_type: str
    shape: str
    brand: str
    price: float
    audience: str = "adult"
    params: tuple[tuple[str, str], ...] = ()
    extra: tuple[tuple[str, str, str], ...] = ()
    sizes: tuple[str, ...] = ()
    size_range: str | None = None
    colorless: bool = False
    units_per_pack: int | None = None
    pattern: str | None = None
