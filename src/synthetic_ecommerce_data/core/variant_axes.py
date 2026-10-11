"""The attributes a shopper selects on a product page (gen#47): ``variant_axes``.

Every SKU of a product states the same ordered list of attribute keys, coarsest first
(``["thread_size", "length"]``). A key is the one the flat document stores the attribute
under (``facets``), so a consumer looks up each hit's values by key.

An axis is an attribute the generator actually varied across the product's SKUs and that
a shopper has to pick. Several attributes often move together without being separate
choices: a hex nut's width across flats and height follow its thread size, a color
family follows the color, a UK size follows the US size. Those are *derived*: the
axes determine them. The axes are the attributes left when every derived one is dropped,
so the axis tuple still names exactly one SKU. Of two attributes that determine each
other the one the generator states first stays. An attribute that follows no single axis, but
only the tuple, is not derived: it stays an axis. The axes keep the order the generator states
them in, which is its own coarse-to-fine order (the thread size before the length, the color
before the size).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

#: One SKU's attributes: key -> its values (a multi-valued attribute has several).
Profile = Mapping[str, tuple[str, ...]]


def profile(entries: Iterable[Mapping[str, Any]]) -> dict[str, tuple[str, ...]]:
    """A SKU's :data:`Profile` from nested attribute entries (``key``, ``value``)."""
    out: dict[str, list[str]] = {}
    for entry in entries:
        out.setdefault(entry["key"], []).append(str(entry["value"]))
    return {key: tuple(sorted(set(values))) for key, values in out.items()}


def _determined(key: str, by: Sequence[str], profiles: Sequence[Profile]) -> bool:
    """Whether ``key``'s value is a function of ``by``'s values across the SKUs."""
    seen: dict[tuple[Any, ...], Any] = {}
    for p in profiles:
        given = tuple(p.get(k) for k in by)
        value = p.get(key)
        if seen.setdefault(given, value) != value:
            return False
    return True


def derived_from_one(key: str, axes: Sequence[str], profiles: Sequence[Profile]) -> bool:
    """Whether ``key`` follows a single one of ``axes`` (a width follows its thread size).

    One axis, not the tuple: every attribute is a function of a tuple that names the SKU, so
    only a single axis tells a derived attribute from a hidden second selector."""
    return any(_determined(key, [axis], profiles) for axis in axes)


def variant_axes(profiles: Sequence[Profile]) -> list[str]:
    """The ordered axes of one product from its SKUs' profiles; ``[]`` for a single SKU."""
    if len(profiles) < 2:
        return []
    keys = list(dict.fromkeys(k for p in profiles for k in p))
    varying = [k for k in keys if len({p.get(k) for p in profiles}) >= 2]
    kept = list(varying)
    for key in reversed(varying):
        rest = [k for k in kept if k != key]
        if derived_from_one(key, rest, profiles):
            kept = rest
    return kept
