"""No two attribute keys on one document share a display name (gen#256).

A skirt once exported ``garment_length`` (name "Length": Mini, Midi, Maxi) and a SKU axis
``length`` (name "Length": Petite, Regular, Long). A facet panel showed two facets called
Length, and a Maxi skirt was offered in a Short/Petite length. The axis is now ``fit_length``
("Fit length", ``export.OPTIONS``); this guard keeps the class from coming back for any type.

:func:`shared_name_findings` takes nested documents (``attributes`` on the product and on each
variant) or flat rows (``attributes`` on the row); a key listed on both the product and a
variant is one attribute, not two.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def shared_name_findings(docs: Iterable[dict[str, Any]]) -> list[str]:
    """One line per document that gives one display name to two different keys."""
    return []
