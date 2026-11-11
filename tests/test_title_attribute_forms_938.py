"""Each title attribute is written one way within its product type (#938).

Two makers of one type used to write the same attribute two ways: ``40mm L`` beside ``60mm
Length``, and ``M12x1.75 Dia./Thread Size`` beside a bare ``M10x1.5``. The spelling was the
brand's and the labelled or unlabelled style the (brand, type)'s. The catalog is clean by ruling
(elastic/prism#9284), and a reader of a result list took the mix for a rendering bug.

The test reads the titles as published, not the generator's segments. Each comma-delimited
segment that is a SKU's published value, alone or followed by one of that attribute's declared
label forms, is that attribute written in that form (``<bare>`` for no label). Per product type,
every attribute has to come out in exactly one form.

No deliberate variation comes back either (Deliverable 2): no title writes an attribute's label cut
off (``40mm Lengt``, ``M12x1.75 Thread Siz``) and no comma runs into the next segment. A cut-off
label is one that follows the attribute's published value and is a strict prefix of one of that
attribute's declared forms without being a declared form itself, so ``L`` and ``Dia`` are not cut
off. The forms are compared within one attribute only: Key Stock's ``Width`` is a whole label,
though it starts ``Width Across Flats``.
"""

from __future__ import annotations

from collections import defaultdict

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig
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


def cut_off_labels(lines) -> list[tuple[str, str]]:
    """``(the cut-off label, its title)`` for every title segment that writes an attribute's
    published value followed by a strict prefix of one of that attribute's declared forms."""
    return []  # stub: the reader comes in the next commit


def tight_commas(lines) -> list[str]:
    """Every SKU title that holds a comma not followed by a space."""
    return []  # stub: the reader comes in the next commit


@pytest.fixture(scope="module")
def catalog():
    """The default build, the committed catalog's: SMALL has no unlabelled type whose titles
    name a second length or a disambiguating size, so it could not see those labelled."""
    return generate(GeneratorConfig())


def _hand_made(*titles_and_attrs):
    """A one-line catalog of hand-made SKU titles, each with its ``(name, value)`` attributes."""

    class _A:
        def __init__(self, name, value):
            self.name, self.value = name, value

    class _Sku:
        def __init__(self, title, attrs):
            self.title, self.attributes = title, tuple(_A(n, v) for n, v in attrs)

    class _Line:
        type_key = "bolt_hex"
        attributes = ()

        def __init__(self, children):
            self.children = children

    return [_Line([_Sku(title, attrs) for title, attrs in titles_and_attrs])]


def test_the_reader_tells_two_spellings_of_one_attribute_apart():
    """The reader is what the catalog test trusts: on two hand-made titles of one type that
    write length as ``L`` and as ``Length``, and thread size labelled and bare, it finds both."""
    found = forms_by_type(
        _hand_made(
            (
                "Hex Head Bolt, M12x1.75 Dia./Thread Size, 40mm L",
                (("Dia./Thread Size", "M12x1.75"), ("Length", "40mm")),
            ),
            (
                "Hex Head Bolt, M10x1.5, 60mm Length",
                (("Dia./Thread Size", "M10x1.5"), ("Length", "60mm")),
            ),
        )
    )
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


def test_the_reader_finds_a_cut_off_label_and_spares_a_declared_abbreviation():
    """``Lengt`` and ``Thread Siz`` are cut off; ``L``, ``Outside Dia`` and a whole attribute
    name that starts a longer form of another attribute are not."""
    lines = _hand_made(
        (
            "Hex Head Bolt, M12x1.75 Thread Siz, 40mm Lengt",
            (("Thread Size", "M12x1.75"), ("Length", "40mm")),
        ),
        (
            "Hex Head Bolt, M10x1.5 Thread Size, 60mm L",
            (("Thread Size", "M10x1.5"), ("Length", "60mm")),
        ),
        ('Washer, 20mm Outside Dia, 3/8" Width', (("Outside Dia.", "20mm"), ("Width", '3/8"'))),
    )
    assert sorted(label for label, _ in cut_off_labels(lines)) == ["Lengt", "Thread Siz"]


def test_the_reader_finds_a_comma_without_a_following_space():
    lines = _hand_made(
        ("Hex Head Bolt,M12x1.75, 40mm L", ()),
        ("Hex Head Bolt, M10x1.5, 60mm L", ()),
    )
    assert tight_commas(lines) == ["Hex Head Bolt,M12x1.75, 40mm L"]


def test_no_title_holds_a_cut_off_attribute_label(catalog):
    found = cut_off_labels(catalog.lines)
    assert not found, f"{len(found)} titles write a label cut off; the first: {found[:5]}"


def test_every_comma_in_a_title_is_followed_by_a_space(catalog):
    found = tight_commas(catalog.lines)
    assert not found, f"{len(found)} titles hold a comma with no space after it: {found[:5]}"
