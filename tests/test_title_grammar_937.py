"""An industrial title reads ``<Type>: <attrs>``, and its description reads
``<title> - <remaining attrs>, <brand> <line> <mfr part number>`` (#937).

This is the reference catalogue's grammar, as the maintainer asked for it on
elastic/prism#9284. A title names its product type, then a colon, then the type's
most identifying attributes. Each attribute is written as its value and an
abbreviated name, such as ``Square End Mill: 3/4" Dia, 1-1/2" LOC``. The
description restates the title verbatim. It then gives the attributes the title
left out, and ends with the brand, the product line and the manufacturer part
number.

Every assertion runs over a FRESH build rather than the committed
``golden-catalog/``. A defect planted in the composer leaves the committed bytes
unchanged, so only a fresh build can show it. Removing the colon from
``naming.build_title`` turns the first test red.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.core.naming import Segment, build_title
from synthetic_ecommerce_data.domains.industrial.title_attributes import TITLE_ATTRIBUTES

#: The grammar's opening: a type with no comma and no colon, then ``": "``.
TYPE_COLON = re.compile(r"^[^:,]+: ")


@pytest.fixture(scope="module")
def docs() -> list[dict]:
    from synthetic_ecommerce_data.core import emit
    from synthetic_ecommerce_data.core.config import GeneratorConfig
    from synthetic_ecommerce_data.domains.industrial.generate import generate

    return list(emit.iter_flat(generate(GeneratorConfig())))


def _published(doc: dict) -> dict[str, set[str]]:
    """The record's published values by attribute name, case folded: the flat document
    writes a name in sentence case (``Abrasive material``)."""
    values: dict[str, set[str]] = {}
    for attribute in doc["attributes"]:
        values.setdefault(attribute["name"].casefold(), set()).add(attribute["value"])
    return values


def _undeclared(doc: dict) -> list[str]:
    """The title's attribute pieces that its type does not declare.

    A piece names a declared attribute when it ends with that attribute's abbreviation, or,
    for an attribute declared with none, when it is a value the record publishes for it."""
    declared = TITLE_ATTRIBUTES.get(doc["product_type"], ())
    published = _published(doc)
    rest = doc["title"].split(": ", 1)[1] if ": " in doc["title"] else ""
    bad = []
    for piece in rest.split(", "):
        if not any(
            piece.endswith(f" {abbrev}")
            if abbrev is not None
            else piece in published.get(name.casefold(), set())
            for name, abbrev in declared
        ):
            bad.append(piece)
    return bad


def test_every_industrial_title_opens_with_its_type_and_a_colon(docs: list[dict]) -> None:
    off = [d["title"] for d in docs if not TYPE_COLON.match(d["title"])]
    assert not off, f"{len(off)} of {len(docs)} titles are not '<Type>: <attrs>': {off[:5]}"


def test_every_title_attribute_is_one_its_type_declares(docs: list[dict]) -> None:
    off = [(d["product_type"], d["title"], bad) for d in docs if (bad := _undeclared(d))]
    assert not off, f"{len(off)} titles name an attribute their type does not declare: {off[:5]}"


def test_every_description_restates_the_title_and_ends_with_the_part_number(
    docs: list[dict],
) -> None:
    off = []
    for d in docs:
        part = d.get("mfr_part_number")
        tail = f"{d['brand']} {d['series']} {part}"
        description = d["description"]
        if (
            not part
            or not description.startswith(d["title"] + " - ")
            or not description.endswith(part)
            or not (description.endswith(f", {tail}") or description == f"{d['title']} - {tail}")
        ):
            off.append((d["sku"], description))
    assert not off, (
        f"{len(off)} descriptions are not '<title> - <attrs>, <brand> <line> <part number>': "
        f"{off[:3]}"
    )


def test_every_record_carries_a_part_number_that_is_not_its_sku(docs: list[dict]) -> None:
    off = [
        (d["sku"], d.get("mfr_part_number"))
        for d in docs
        if not d.get("mfr_part_number") or d.get("mfr_part_number") == d["sku"]
    ]
    assert not off, f"{len(off)} records have no part number of their own: {off[:5]}"


def test_the_end_mills_name_the_measured_pair() -> None:
    """elastic/prism-retail-and-industrial#1694 measured the reference's one family: 24 of
    24 square end mill titles name the mill diameter (``Dia``), then the length of cut
    (``LOC``)."""
    measured = (("Milling Dia.", "Dia"), ("Length of Cut", "LOC"))
    assert TITLE_ATTRIBUTES.get("end_mill_square") == measured
    assert TITLE_ATTRIBUTES.get("end_mill_ball") == measured


def test_the_composer_writes_type_colon_then_value_and_abbreviation() -> None:
    title = build_title(
        "Square End Mill",
        (
            Segment(value='3/4"', label="Dia", attribute="Milling Dia."),
            Segment(value='1-1/2"', label="LOC", attribute="Length of Cut"),
        ),
    )
    assert title.text == 'Square End Mill: 3/4" Dia, 1-1/2" LOC'
