"""Each title attribute is written one way within its product type (#938).

Two makers of one type used to write the same attribute two ways: ``40mm L`` beside ``60mm
Length``, and ``M12x1.75 Dia./Thread Size`` beside a bare ``M10x1.5``. The spelling was the
brand's and the labelled or unlabelled style the (brand, type)'s. The catalog is clean by ruling
(elastic/prism#9284), and a reader of a result list took the mix for a rendering bug.

The test reads the titles as published, not the generator's segments. Each comma-delimited
segment that is a SKU's published value, alone or followed by one of that attribute's declared
label forms, is that attribute written in that form (``<bare>`` for no label). Per product type,
every attribute has to come out in exactly one form.
"""

from __future__ import annotations

from collections import defaultdict

import pytest

from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.naming import LABEL_FORMS
from synthetic_ecommerce_data.core.voice import PACK_LABELS
from synthetic_ecommerce_data.domains.industrial.generate import generate

BARE = "<bare>"


def _forms(name: str) -> set[str]:
    """Every label an attribute is declared to be written with: its census spellings, its own
    name, and for a pack count the pack labels."""
    forms = {form for form, _ in LABEL_FORMS.get(name, ())} | {name}
    if name == "Units per Pack":
        forms |= set(PACK_LABELS)
    return forms


def forms_by_type(lines) -> dict[tuple[str, str], dict[str, list[str]]]:
    """``(type, attribute) -> form -> the titles that write it so``, over every SKU title."""
    found: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for line in lines:
        for sku in line.children:
            values = {a.name: a.value for a in (*line.attributes, *sku.attributes)}
            for segment in sku.title.split(", ")[1:]:
                for name, value in values.items():
                    if segment == value:
                        found[(line.type_key, name)][BARE].append(sku.title)
                    if name == "Units per Pack" and segment == f"Box of {value}":
                        found[(line.type_key, name)]["Box of"].append(sku.title)
                    for form in _forms(name):
                        if segment == f"{value} {form}":
                            found[(line.type_key, name)][form].append(sku.title)
    return found


@pytest.fixture(scope="module")
def catalog():
    return generate(SMALL)


def test_the_reader_tells_two_spellings_of_one_attribute_apart():
    """The reader is what the catalog test trusts: on two hand-made titles of one type that
    write length as ``L`` and as ``Length``, and thread size labelled and bare, it finds both."""

    class _A:
        def __init__(self, name, value):
            self.name, self.value = name, value

    class _Sku:
        def __init__(self, title, attrs):
            self.title, self.attributes = title, attrs

    class _Line:
        type_key = "bolt_hex"
        attributes = ()

        def __init__(self, children):
            self.children = children

    one = _Sku(
        "Hex Head Bolt, M12x1.75 Dia./Thread Size, 40mm L",
        (_A("Dia./Thread Size", "M12x1.75"), _A("Length", "40mm")),
    )
    two = _Sku(
        "Hex Head Bolt, M10x1.5, 60mm Length",
        (_A("Dia./Thread Size", "M10x1.5"), _A("Length", "60mm")),
    )
    found = forms_by_type([_Line([one, two])])
    assert set(found[("bolt_hex", "Length")]) == {"L", "Length"}
    assert set(found[("bolt_hex", "Dia./Thread Size")]) == {"Dia./Thread Size", BARE}


def test_each_title_attribute_has_one_name_form_within_its_product_type(catalog):
    found = forms_by_type(catalog.lines)
    assert found, "no title attribute was read off the catalog"
    mixed = {
        key: {form: (len(titles), titles[0]) for form, titles in forms.items()}
        for key, forms in sorted(found.items())
        if len(forms) > 1
    }
    assert not mixed, (
        f"{len(mixed)} (type, attribute) pairs are written more than one way; "
        f"form -> (titles, an example): {mixed}"
    )
