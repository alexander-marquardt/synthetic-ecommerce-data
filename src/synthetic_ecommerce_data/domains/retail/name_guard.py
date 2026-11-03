"""No two attribute keys on one document share a display name (gen#256).

A skirt once exported ``garment_length`` (name "Length": Mini, Midi, Maxi) and a SKU axis
``length`` (name "Length": Petite, Regular, Long). A facet panel showed two facets called
Length, and a Maxi skirt was offered in a Short/Petite length. The axis is now ``fit_length``
("Fit length", ``export.OPTIONS``); this guard keeps the class from coming back for any type.

:func:`shared_name_findings` takes nested documents (``attributes`` on the product and on each
variant) or flat rows (``attributes`` on the row); a key listed on both the product and a
variant is one attribute, not two. :func:`catalogue_name_findings` is the same rule across
documents: one key, one display name, and one display name, one key, catalogue-wide.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def shared_name_findings(docs: Iterable[dict[str, Any]]) -> list[str]:
    """One line per document that gives one display name to two different keys."""
    found = []
    for doc in docs:
        entries = [*doc.get("attributes", ())]
        for variant in doc.get("variants", ()):
            entries.extend(variant.get("attributes", ()))
        keys: dict[str, set[str]] = {}
        for entry in entries:
            keys.setdefault(entry["name"], set()).add(entry["key"])
        for name, held in sorted(keys.items()):
            if len(held) > 1:
                found.append(f"{doc.get('product_id')}: {name!r} names {sorted(held)}")
    return found


def catalogue_name_findings(docs: Iterable[dict[str, Any]]) -> list[str]:
    """One line per key shown under two display names and per display name given to two keys,
    across every document (gen#497's guard): a Rug's ``rug_shape`` "Shape" beside every other
    type's ``shape`` "Shape" is one facet name over two keys, which no one document shows."""
    names: dict[str, set[str]] = {}
    keys: dict[str, set[str]] = {}
    for doc in docs:
        entries = [*doc.get("attributes", ())]
        for variant in doc.get("variants", ()):
            entries.extend(variant.get("attributes", ()))
        for entry in entries:
            names.setdefault(entry["key"], set()).add(entry["name"])
            keys.setdefault(entry["name"], set()).add(entry["key"])
    return [
        *(f"key {k!r} is shown as {sorted(n)}" for k, n in sorted(names.items()) if len(n) > 1),
        *(f"name {n!r} names {sorted(k)}" for n, k in sorted(keys.items()) if len(k) > 1),
    ]
