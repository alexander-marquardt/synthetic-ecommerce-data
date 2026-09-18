"""A SKU's title and its description say what makes it different from its siblings.

The defect this exists to catch is what the storefront showed on its first
screen: six cards, identical in every visible respect -- same title, same
brand, same series, same drawing, same breadcrumb -- at $2.10, $2.48, $4.85,
$8.00, $8.34 and $10.42. *"there seem to be duplicates?"* They were not
duplicates. They were 12, 16, 30 and 45 mm long, and neither the title nor the
description said so::

    3RX99   Length 12.00mm   "Socket Head Cap Screw, M6x1, Alloy Steel"
    99JZ63  Length 16.00mm   "Socket Head Cap Screw, M6x1, Alloy Steel"
    15NV56  Length 30.00mm   "Socket Head Cap Screw, M6x1,Alloy Steel"
    15HA54  Length 45.00mm   "Socket Head Cap Screw, M6x1, Alloy Steel"

Measured on the committed catalog before the fix: **176 of 500 product lines
published a title two of their SKUs shared, over 1,214 SKUs**, and **500 of
500 lines published one description for every SKU under them** -- the
description was the LINE's title, ``Marrow & Sons ISO4762-64 -- Socket Head
Cap Screw``, which restates the brand, the series and the product type and
says nothing about the SKU.

Three tiers, each read at a different moment, and this file is about the first
two:

======================  ==========================================  ==============================
tier                    job                                         content
======================  ==========================================  ==============================
title                   tell them apart AT A GLANCE                 the ONE main distinguishing
                                                                    attribute
description             tell them apart WHILE SCANNING              the distinguishing attributes,
                                                                    with context
attribute block         tell them apart PRECISELY                   every published attribute
======================  ==========================================  ==============================

Every assertion here is over the WHOLE catalog and derived from the data --
which SKUs share a title is a question about the catalog, and a spot-check of
one product type is how this got shipped in the first place. Each runs twice,
against the committed files and against a fresh build; ``SOURCES`` below says
why neither alone is enough.
"""

from __future__ import annotations

import collections
import json
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden-catalog"
REBUILD = "uv run sip-generate build --out golden-catalog"


#: Every property here is asserted against TWO sources, and both are needed.
#:
#: ``committed`` is ``golden-catalog/``, the artifact anyone can read without
#: running a build. Asserting against it is what stops a careless
#: ``sip-generate build && git commit -a`` from a broken generator sailing
#: through, and it is why ``test_catalog_golden`` states its headline numbers
#: that way too.
#:
#: ``generated`` is a fresh build in memory. Without it every property here
#: would be unprovable by mutation: a defect planted in the generator does not
#: move the committed bytes, so a test reading only those stays green while the
#: generator is broken -- which is exactly the shape of the failure this
#: repository keeps finding.
SOURCES = ("committed", "generated")


@pytest.fixture(scope="module", params=SOURCES)
def catalog(request) -> tuple[list[dict], list[dict]]:
    if request.param == "committed":
        def read(name: str) -> list[dict]:
            with (GOLDEN_DIR / name).open(encoding="utf-8") as handle:
                return [json.loads(line) for line in handle]

        return read("flat.jsonl"), read("nested.jsonl")

    from synthetic_industrial_products.catalog import emit
    from synthetic_industrial_products.catalog.config import GeneratorConfig
    from synthetic_industrial_products.catalog.generate import generate

    built = generate(GeneratorConfig())
    return list(emit.iter_flat(built)), list(emit.iter_nested(built))


@pytest.fixture(scope="module")
def flat_docs(catalog: tuple[list[dict], list[dict]]) -> list[dict]:
    return catalog[0]


@pytest.fixture(scope="module")
def variant_attributes(catalog: tuple[list[dict], list[dict]]) -> dict[str, list[dict]]:
    """Each SKU's OWN attributes, read off the nested shape.

    The flat document denormalises the line's attributes onto every SKU, so
    its ``attributes`` array is the merged set and cannot answer "what does
    this SKU publish that its line does not". The description composes from
    the SKU's own half -- the line's half is the third tier's job -- so the
    question has to be asked of the shape that still distinguishes them.
    """
    own: dict[str, list[dict]] = {}
    for line in catalog[1]:
        for variant in line["variants"]:
            own[variant["sku"]] = variant["attributes"]
    return own


@pytest.fixture(scope="module")
def by_line(flat_docs: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for doc in flat_docs:
        grouped.setdefault(doc["product_id"], []).append(doc)
    return grouped


def _duplicates(by_line: dict[str, list[dict]], field: str) -> list[tuple[str, str, int]]:
    """Every (line, value, count) where one line published a value twice."""
    out: list[tuple[str, str, int]] = []
    for product_id, docs in sorted(by_line.items()):
        counts = collections.Counter(doc[field] for doc in docs)
        out.extend(
            (product_id, value, count) for value, count in counts.items() if count > 1
        )
    return out


@pytest.mark.parametrize("field", ["title", "description"])
def test_no_two_skus_in_one_product_line_share_a_title_or_a_description(
    by_line: dict[str, list[dict]], field: str
) -> None:
    """The headline acceptance, and the one that failed loudest before.

    Within a LINE rather than over the whole catalog: two unrelated lines of
    one brand may legitimately publish the same title, and they never sit
    beside each other on a card grid. Two SKUs of one line always do.
    """
    duplicates = _duplicates(by_line, field)
    lines = {product_id for product_id, _, _ in duplicates}
    skus = sum(count for _, _, count in duplicates)
    assert duplicates == [], (
        f"{len(lines)} product line(s) publish a {field} that {skus} of their SKUs "
        f"share, e.g. {duplicates[:3]}. A shopper reads those as duplicated data. "
        f"Regenerate with `{REBUILD}`."
    )


def test_the_description_is_not_the_line_title_over_again(flat_docs: list[dict]) -> None:
    """It used to be exactly that, on every SKU in the catalog.

    ``parent_title`` still ships -- it is what a grouped card will be headed
    with -- and is no longer what renders under a SKU's title.
    """
    same = [doc["sku"] for doc in flat_docs if doc["description"] == doc["parent_title"]]
    assert same == [], f"{len(same)} SKU(s) publish the line title as their description"


def test_the_description_opens_with_the_title_verbatim(flat_docs: list[dict]) -> None:
    """The overlap is the SOURCE's convention, not duplication to tidy away.

    The 24 real rows committed in the customization repo compose this way, 24
    of 24::

        TITLE        Square End Mill: 3/4" Dia, 1-1/2" LOC
        DESCRIPTION  Square End Mill: 3/4" Dia, 1-1/2" LOC - 4" OAL, ...

    Asserting it rather than merely permitting it, because "improve away the
    repetition" is the obvious-looking change that would break the grammar
    being reproduced -- and because it is what makes the description's
    uniqueness follow from the title's rather than being a second coincidence.
    """
    wrong = [
        doc["sku"]
        for doc in flat_docs
        if not doc["description"].startswith(doc["title"] + " - ")
    ]
    assert wrong == [], (
        f"{len(wrong)} description(s) do not open with their own title followed by "
        f"' - ': {wrong[:5]}"
    )


def test_the_description_says_something_the_title_did_not(
    flat_docs: list[dict], variant_attributes: dict[str, list[dict]]
) -> None:
    """A tier that only repeats the tier above it is not a tier.

    Conditional on there being anything left to say, and the condition is
    DERIVED rather than an allowance: the catalog is ragged on purpose, and a
    tap whose optional dimensions all fell to sparsity publishes a thread size
    and an overall length its title already carries. Demanding a new value
    from those would be demanding the description invent one.
    """
    thin: list[str] = []
    for doc in flat_docs:
        tail = doc["description"][len(doc["title"]) + 3 :]
        unnamed = [
            entry["value"]
            for entry in variant_attributes[doc["sku"]]
            if entry["value"] and entry["value"] not in doc["title"]
        ]
        if unnamed and not any(value in tail for value in unnamed):
            thin.append(doc["sku"])
    assert thin == [], (
        f"{len(thin)} description(s) publish an attribute of their own that the "
        f"title does not name and then do not name it either: {thin[:5]}"
    )


def test_every_title_names_a_value_that_is_this_skus_alone_in_its_line(
    by_line: dict[str, list[dict]],
) -> None:
    """Uniqueness stated as the PROPERTY rather than as an absence of collisions.

    A line's titles could be pairwise distinct for an accident -- a truncation
    that landed differently, a delimiter written tight on one of them -- and
    that would satisfy the duplicate check while telling the shopper nothing.
    What has to be true is that the title carries a VALUE this SKU publishes
    and its siblings do not.
    """
    failures: list[tuple[str, str]] = []
    for product_id, docs in sorted(by_line.items()):
        if len(docs) < 2:
            continue
        # Per ATTRIBUTE, not per value. The same string legitimately appears on
        # two SKUs of one line in two different roles -- a 3/8" that is one
        # tool's cutting diameter and another's shank -- and that collision is
        # the property this whole catalog exists to exhibit. What has to be
        # this SKU's alone is the (attribute, value) PAIR.
        elsewhere: dict[str, set[str]] = {}
        for doc in docs:
            for entry in doc["attributes"]:
                elsewhere.setdefault(entry["name"], set())
        for doc in docs:
            own = {entry["name"]: entry["value"] for entry in doc["attributes"]}
            identifying = {
                name
                for name, value in own.items()
                if not any(
                    other["sku"] != doc["sku"]
                    and any(
                        entry["name"] == name and entry["value"] == value
                        for entry in other["attributes"]
                    )
                    for other in docs
                )
            }
            if not any(own[name] in doc["title"] for name in identifying):
                failures.append((product_id, doc["sku"]))
    assert failures == [], (
        f"{len(failures)} SKU title(s) name no attribute value that is theirs "
        f"alone within their line: {failures[:5]}"
    )


def test_the_end_mill_titles_that_already_worked_are_not_regressed(
    flat_docs: list[dict],
) -> None:
    """They carried their cutting diameter before this and they still do.

    The end mill is the control for the whole rule. A mill's primary dimension
    IS its cutting diameter and it varies down the line, so its titles were
    already distinct and the repair never fires on them. If the fix had been
    "put the distinguishing attribute in every title" instead, the measured
    title hazards -- an unlabelled dimension token, a token that is not the
    primary dimension -- would have been erased from this type first.
    """
    mills = [doc for doc in flat_docs if doc["product_type"].startswith("end_mill")]
    assert mills, "no end mill documents"
    carrying = [
        doc
        for doc in mills
        if any(value in doc["title"] for value in doc["facets"].get("milling_dia", []))
    ]
    share = len(carrying) / len(mills)
    assert share > 0.6, (
        f"only {share:.0%} of end mill titles carry their own cutting diameter; "
        f"the measured grammar puts it in most of them"
    )


def test_the_description_is_derived_and_not_a_second_source_of_truth(
    flat_docs: list[dict],
) -> None:
    """Every value in a description is a value the record publishes.

    The failure this refuses is a description assembled from what the
    generator INTENDED rather than from what the record says -- which would
    put a value in front of a shopper that the attribute block contradicts.
    Checked on the numeric dimensions, whose spellings are the ones the
    defect classes move.
    """
    mismatched: list[tuple[str, str]] = []
    for doc in flat_docs:
        published = {entry["value"] for entry in doc["attributes"]}
        tail = doc["description"][len(doc["title"]) + 3 :]
        names = sorted({entry["name"] for entry in doc["attributes"]}, key=len, reverse=True)
        for chunk in tail.split(", "):
            # LONGEST name first: "1/8 in Thread Length" ends with " Length"
            # as well as with " Thread Length", and taking the short one
            # reads the value as "1/8 in Thread" and reports 1,894 false
            # mismatches.
            name = next((n for n in names if chunk.endswith(" " + n)), None)
            if name is None:
                continue
            value = chunk[: -len(name) - 1]
            if value not in published:
                mismatched.append((doc["sku"], chunk))
    assert mismatched == [], (
        f"{len(mismatched)} description fragment(s) state a value the record does "
        f"not publish: {mismatched[:5]}"
    )
