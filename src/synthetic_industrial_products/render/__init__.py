"""Technical-drawing renderers, dispatched on what the record describes."""

from __future__ import annotations

from pathlib import Path

from . import endmill, fastener
from .profiles import CARD, DETAIL, PROFILES, Profile

__all__ = [
    "CARD",
    "DETAIL",
    "PROFILES",
    "Profile",
    "UnknownProductError",
    "endmill",
    "fastener",
    "render_record",
    "renderer_for",
]


class UnknownProductError(ValueError):
    """No renderer knows how to draw this record."""


def renderer_for(record: dict):
    """Pick a renderer from the attributes the record carries, not from a type field.

    Catalogs in this vertical do not publish a machine-readable product class;
    what they publish is a set of attribute names. Those names are the signal.
    """
    if "Milling Dia." in record:
        return endmill
    if "Screw Head Type" in record or "Dia./Thread Size" in record:
        return fastener
    raise UnknownProductError(
        f"record {record.get('sku', '?')!r} carries no attribute that identifies it "
        "as a tool or a fastener"
    )


def render_record(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    return renderer_for(record).render(record, path, profile)
