"""The type key of an industrial document, flat or nested (gen#125).

A flat row's ``product_type`` is its category leaf (``Hammers``), and the key (``hammer_claw``)
is the first segment of its ``image_id`` (``emit.flat_type_key``); a nested document's
``product_type`` is the key. A test that picks or groups documents by type reads it here.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from synthetic_ecommerce_data.core.emit import flat_type_key


def type_key_of(doc: Mapping[str, Any]) -> str:
    """The type key of *doc*: off ``image_id`` for a flat row, else its ``product_type``."""
    return flat_type_key(doc) if "image_id" in doc else doc["product_type"]
