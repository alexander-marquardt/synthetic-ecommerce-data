"""Model numbers of the large appliances (gen#622). Stub: the schemes land in the fix."""

from __future__ import annotations

from typing import NamedTuple


class Scheme(NamedTuple):
    lead: str


_BRANDS = ("Frostholm", "Brimwell", "Tavorne", "Hollinmere", "Cleavewick", "Lunden & Voss")
SCHEMES = {b: Scheme("") for b in _BRANDS}


def encode(brand: str, kind: str, capacity: int, spin: int, generation: str, color: str) -> str:
    return ""


def decode(code: str) -> dict | None:
    return None
