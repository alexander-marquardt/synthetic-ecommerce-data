"""The published spelling of a catalog document's attributes, for the tests that compare it.

A nested entry carries no spelling: ``value`` is the bare magnitude and
``unit_code`` is the only place the unit lives (#42). The spelling a title or a
description must agree with (``3/8 in.``, ``1,070 lbf``) lives unchanged in the
flat document's ``facets``, so a test that compares spelling reads it from there.

A document's attribute NAMES are sentence case (gen#499: ``Bore dia.``), while a
product type looks an attribute up by the name it authored (``Bore Dia.``). A test
that hands a document's attributes to type code reads them through
:func:`authored_attributes`, which maps each name back through the map the build
writes beside the catalogue (``golden-catalog/authored_names.json``); a test that
checks the published case reads :func:`published_attributes`.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

from synthetic_ecommerce_data.core.entry import published
from synthetic_ecommerce_data.core.letter_case import AUTHORED_NAMES_FILE

_AUTHORED = Path(__file__).resolve().parents[1] / "golden-catalog" / AUTHORED_NAMES_FILE


@cache
def _authored_map() -> dict[str, dict[str, str]]:
    return json.loads(_AUTHORED.read_text("utf-8"))


def authored_name(type_key: str, name: str) -> str:
    """The name ``type_key`` authored for the published ``name``: ``Bore dia.`` -> ``Bore Dia.``."""
    return _authored_map().get(type_key, {}).get(name, name)


def published_attributes(doc: dict) -> list[dict[str, str]]:
    """A FLAT document's attributes as ``{name, value}``: the published (sentence case) name
    and ``value`` the published spelling."""
    return [
        {"name": name, "value": value}
        for name, value in published(doc["attributes"], doc["facets"])
    ]


def authored_entries(doc: dict) -> list[dict]:
    """A document's attribute entries as published (``key``, ``value``, ``value_canonical`` ...)
    with each ``name`` mapped back to the one its type authored: for a test that reads a
    value by the name the type's table or census states (``entry["Pin Dia."]``)."""
    return [
        entry | {"name": authored_name(doc["product_type"], entry["name"])}
        for entry in doc["attributes"]
    ]


def authored_attributes(doc: dict) -> list[dict[str, str]]:
    """:func:`published_attributes` with each name mapped back to the one its type authored,
    for a test that feeds the attributes to type code or compares them with a type's literals."""
    return [
        {"name": authored_name(doc["product_type"], a["name"]), "value": a["value"]}
        for a in published_attributes(doc)
    ]
