"""The constants and helpers the cycling, wheeled and kayak specs share (gen#352): data only.

The five types (``bicycle``, ``bike_helmet``, ``kayak``, ``kick_scooter``, ``skateboard``) build
their rows from :mod:`sports_helpers`; this module adds the attribute makers those types need and
the places of their leaves in the Sports & Outdoors tree.
"""

from __future__ import annotations

from sports_helpers import _SO

from synthetic_ecommerce_data.core.entry import canonical

__all__ = ["BIKES", "CYCLING", "KAYAKS", "WHEELED", "_count", "_inch"]

CYCLING = (_SO, "Cycling")
#: The group holding the four kinds of bike; the helmets sit beside it, not under it.
BIKES = (*CYCLING, "Bikes")
KAYAKS = (_SO, "Water Sports", "Kayaks")
WHEELED = (_SO, "Wheeled Sports")


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str, float]:
    """A plain count (gears, seats): the unit is ``C62``, one."""
    return (key, name, str(n), "C62", float(n))


def _inch(key: str, name: str, inches: float) -> tuple[str, str, str, str, float]:
    """A length in inches (a wheel, a deck): the canonical value is in millimetres (``INH``)."""
    text = f"{inches:g}"
    return (key, name, text, "INH", float(canonical(text, "INH")))
