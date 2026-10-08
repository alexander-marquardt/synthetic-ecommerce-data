"""The published spelling of a catalog document's attributes, for the tests that compare it.

A nested entry carries no spelling: ``value`` is the bare magnitude and
``unit_code`` is the only place the unit lives (#42). The spelling a title or a
description must agree with (``3/8 in.``, ``1,070 lbf``) lives unchanged in the
flat document's ``facets``, so a test that compares spelling reads it from there.
"""

from __future__ import annotations

from synthetic_ecommerce_data.catalog.entry import published


def published_attributes(doc: dict) -> list[dict[str, str]]:
    """A FLAT document's attributes as ``{name, value}``, ``value`` the published spelling."""
    return [
        {"name": name, "value": value}
        for name, value in published(doc["attributes"], doc["facets"])
    ]
