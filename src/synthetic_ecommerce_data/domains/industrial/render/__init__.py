"""Technical-drawing renderers, dispatched on what the record describes.

Two drawings, two different assertions
--------------------------------------
Every record in this catalog gets an image, and the images are not all the same
kind of statement.

A **dimensioned drawing** asserts *this tool is 1/4 inch across the cutting
edge*. It is drawn to scale from the record's own attribute values, every
callout restates a value the record publishes, and it is produced only when the
record carries every number the drawing needs and those numbers do not
contradict each other. When they do not, the renderer refuses -- it does not
default a value, because a drawing produced from a defaulted dimension is a
picture that disagrees with its own record and nothing downstream can tell.

A **generic drawing** asserts *this is a twist drill*. That is true from the
product type alone -- from the attribute names the record publishes, which is
what :mod:`.kinds` reads -- so it stays true of a record whose dimensions are
missing, unreadable, or impossible. It is not drawn to scale and it carries no
dimension callout of any kind. There are twelve of them, one per product type
and style, and they are what the catalog's cards actually show: see
:mod:`.generic`.

:func:`render_record` tries the first and falls back to the second. The refusal
is not swallowed: :func:`draw_record` returns which path was taken and, when a
record was refused, the class of the refusal, so a batch run can report the
mix rather than report a number that hides it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from synthetic_ecommerce_data.domains.industrial.render import (
    drill,
    endmill,
    fastener,
    flapdisc,
    generic,
    hammer,
    kinds,
    tap,
    washer,
)
from synthetic_ecommerce_data.domains.industrial.render.attrs import (
    REFUSALS,
    ImpossibleGeometryError,
    MissingAttributeError,
    UnsupportedFeatureError,
)
from synthetic_ecommerce_data.domains.industrial.render.kinds import (
    AmbiguousProductError,
    UnknownProductError,
    classify,
)
from synthetic_ecommerce_data.domains.industrial.render.profiles import (
    CARD,
    DETAIL,
    PROFILES,
    Profile,
)

__all__ = [
    "CARD",
    "DETAIL",
    "PROFILES",
    "REFUSALS",
    "AmbiguousProductError",
    "Drawn",
    "ImpossibleGeometryError",
    "MissingAttributeError",
    "Profile",
    "UnknownProductError",
    "UnsupportedFeatureError",
    "classify",
    "draw_record",
    "drill",
    "endmill",
    "fastener",
    "flapdisc",
    "generic",
    "hammer",
    "kinds",
    "render_record",
    "renderer_for",
    "tap",
    "washer",
]

#: The dimensioned renderer for each kind. Every entry either draws to scale or
#: refuses -- :mod:`.hammer` only ever refuses, and says why in its docstring.
DIMENSIONED: dict[str, ModuleType] = {
    kinds.END_MILL: endmill,
    kinds.FASTENER: fastener,
    kinds.DRILL: drill,
    kinds.TAP: tap,
    kinds.WASHER: washer,
    kinds.HAMMER: hammer,
    kinds.FLAP_DISC: flapdisc,
}


@dataclass(frozen=True)
class Drawn:
    """What came out of one render, and which way it got there."""

    path: Path
    kind: str
    dimensioned: bool
    #: The class name of the refusal that sent this to the type drawing, or
    #: ``None`` when the record was drawn to scale.
    refusal: str | None = None


def renderer_for(record: dict) -> ModuleType:
    """The dimensioned renderer for ``record``, picked from its attribute names.

    Catalogs in this vertical do not publish a machine-readable product class;
    what they publish is a set of attribute names. Those names are the signal,
    and :mod:`.kinds` is where the mapping lives.
    """
    return DIMENSIONED[classify(record)]


def draw_record(record: dict, path: str | Path, profile: Profile = CARD) -> Drawn:
    """Draw ``record``, to scale if it can be, as its type if it cannot.

    Raises :class:`.UnknownProductError` when nothing identifies the record:
    the type drawing is a statement about a product type, so a record with no
    identifiable type has no honest image either.
    """
    kind = classify(record)
    try:
        written = DIMENSIONED[kind].render(record, path, profile)
    except REFUSALS as refusal:
        written = generic.render_record(record, path, profile)
        return Drawn(written, kind, dimensioned=False, refusal=type(refusal).__name__)
    return Drawn(written, kind, dimensioned=True)


def render_record(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    return draw_record(record, path, profile).path
