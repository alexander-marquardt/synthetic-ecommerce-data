"""One attribute key per concept across the retail catalog (gen#227).

Two concepts were each exported under two keys, so one facet or range filter missed part of the
catalog: a height in centimetres was ``item_height`` on the furniture and ``height`` on a lamp and
an olive tree (a "height under 50 cm" filter on either key missed the other's products), and a
furniture piece's storage was ``storage_feature`` on a coffee table and ``storage_compartment`` on
a footstool.

:data:`CONCEPTS` names each concept, the one key that carries it (the winner) and every other key
whose name holds the concept's word by design, with the reason it is a different concept.
:func:`concept_findings` reports a key that is neither the winner nor a declared exception, and a
winner no document carries; :func:`keys_per_concept` is the metric (it is 1 for every concept).
:func:`stem_findings` is the same rule without a registry: two keys that differ only by an
``item_`` prefix or a unit suffix (``height`` / ``item_height``, ``weight`` / ``weight_kg``) are one
concept under two names, when both carry a ``unit_code``.

Winners, and why: ``item_height`` joins ``item_width``, ``item_depth`` and ``item_length``, the
keys the furniture, seating and appliance ranges already share (13 leaves carry it); one key for
the size of a thing keeps a range filter to one field. ``storage_feature`` is a kind (``Lift-Top``,
``Shelf``, ``Drawer``) where ``None`` means no storage, so "with storage" is "not None" and "with a
drawer" is the same key: a yes/no beside a kind would be two keys again.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Concept:
    """A concept: the word its keys hold, the key that carries it and the keys that do not."""

    word: str
    winner: str
    #: key -> why it is another concept, though its name holds the word
    exceptions: dict[str, str] = field(default_factory=dict)


CONCEPTS: dict[str, Concept] = {
    "item height": Concept(
        "height",
        "item_height",
        {
            "heel_height": "the heel of a shoe, a part of it and not the item",
            "min_height": "the low end of an adjustable range (a pedestal fan), not one height",
            "max_height": "the high end of an adjustable range (a pedestal fan), not one height",
        },
    ),
    "furniture storage": Concept(
        "storage",
        "storage_feature",
        {
            "storage": "how a food is kept (grocery: keep chilled), not a feature of a thing",
            "storage_type": "the kind of a storage box, a label of the product itself",
        },
    ),
}

#: A unit suffix a key may carry beside its stem (``weight_kg``); the export drops it from the key.
_UNIT_SUFFIX = re.compile(r"_(?:cm|mm|m|m2|in|ft|kg|g|ml|l|v|w)$")


def _keys(docs: Iterable[dict[str, Any]], measured: bool = False) -> set[str]:
    """Every attribute key on a nested document or on one of its variants; with ``measured``,
    only a key some entry of which carries a ``unit_code``."""
    found: set[str] = set()
    for doc in docs:
        for row in (doc, *doc.get("variants", ())):
            found.update(
                entry["key"]
                for entry in row.get("attributes", ())
                if not measured or entry.get("unit_code") is not None
            )
    return found


def _holds(key: str, word: str) -> bool:
    return word in key.split("_")


def keys_per_concept(docs: Iterable[dict[str, Any]]) -> dict[str, int]:
    """The metric: concept -> how many keys carry it (declared exceptions are other concepts)."""
    keys = _keys(docs)
    return {
        name: sum(1 for k in keys if _holds(k, c.word) and k not in c.exceptions)
        for name, c in CONCEPTS.items()
    }


def concept_findings(docs: Iterable[dict[str, Any]]) -> list[str]:
    """One line per concept carried under a key other than its winner, or under none."""
    keys = _keys(docs)
    found = []
    for name, c in CONCEPTS.items():
        held = sorted(k for k in keys if _holds(k, c.word) and k not in c.exceptions)
        if c.winner not in held:
            found.append(f"{name}: no document carries {c.winner!r}")
        extra = [k for k in held if k != c.winner]
        if extra:
            found.append(f"{name}: carried under {extra} as well as {c.winner!r}")
    return found


def stem(key: str) -> str:
    """The key without an ``item_`` prefix or a unit suffix."""
    return _UNIT_SUFFIX.sub("", key.removeprefix("item_"))


def stem_findings(docs: Iterable[dict[str, Any]]) -> list[str]:
    """One line per stem that two or more MEASURED keys share: one concept under two names.

    A key with no ``unit_code`` is text (a garment's ``width`` is Standard or Wide, its ``length``
    Short or Long), so it names no dimension and is left out."""
    groups: dict[str, set[str]] = {}
    for key in _keys(docs, measured=True):
        groups.setdefault(stem(key), set()).add(key)
    return [f"{s!r} is {sorted(ks)}" for s, ks in sorted(groups.items()) if len(ks) > 1]
