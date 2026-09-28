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
import re
import string
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog.naming import DELIMITER, TIGHT_DELIMITER

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden-catalog"
REBUILD = "uv run sip-generate build --out golden-catalog"

#: A character that could be part of the same value as the one either side of
#: it -- digits, fraction and decimal marks, unit marks, letters.
_CONTINUES = re.compile(r"""[0-9A-Za-z./\-"']""")


def _states(text: str, value: str) -> bool:
    """Whether ``text`` STATES ``value``, rather than merely containing it.

    Deliberately a SECOND implementation of the generator's
    ``naming.states_value`` rather than an import of it. The question "does
    this title name this value" is the one the generator uses to decide
    whether a title needs repairing and the one this file uses to decide
    whether the repair worked; sharing the code would make the two agree by
    construction, and a wrong answer would then be invisible from both sides.
    That is not hypothetical -- both asked it with a bare ``in`` and both were
    wrong about the same 10 SKUs, ``94PL94`` among them, whose title
    ``Button Head Socket Cap Screw, 1/4-20, Alloy Steel`` was credited with
    naming a ``Length Under Head`` of ``1/4``.
    """
    if not value:
        return False
    for match in re.finditer(re.escape(value), text):
        before = text[match.start() - 1 : match.start()]
        after = text[match.end() : match.end() + 1]
        if not _CONTINUES.match(before) and not _CONTINUES.match(after):
            return True
    return False


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
        out.extend((product_id, value, count) for value, count in counts.items() if count > 1)
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
        doc["sku"] for doc in flat_docs if not doc["description"].startswith(doc["title"] + " - ")
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
            if entry["value"] and not _states(doc["title"], entry["value"])
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
    and its siblings do not, and that it carries it as a VALUE: a substring
    test credits ``…, 1/4-20, …`` with naming a length of ``1/4``, which is
    how 10 SKUs passed this while naming nothing of their own.
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
            if not any(_states(doc["title"], own[name]) for name in identifying):
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


def test_no_title_is_cut_mid_word(flat_docs: list[dict]) -> None:
    """Every title ends on a whole segment, not half a label.

    Two mechanisms used to cut a title and BOTH had to go, which is the point
    of asserting on the finished string rather than on either of them:

    * the generator deliberately truncated a label at a measured 3.23% --
      removed by the ruling on elastic/prism#9284;
    * ``build_title`` cut the assembled string at the 100-character cap,
      which lands mid-word. Reconstructed on this catalog by
      ``test_the_cap_cut_this_replaced_really_did_land_inside_words``: **70
      of 10,080** titles (67 of 4,689 before the catalog grew), ending
      ``...Solid Carbide, U`` or ``...SGL Sq En``.
      Removing only the first would have left those in place while the
      change reported that truncation was gone. (That figure read "97 of
      4,688" and reproduced under no reading, which is why it is now
      measured rather than quoted.)

    The assertion is therefore on the published text: a title may not end
    part-way through the final segment it publishes. The denominator is
    asserted first, because "no truncated titles" and "no titles" produce the
    same count.

    THE DETECTOR USED TO COMPARE THE WHOLE TAIL, AND COULD NOT FIRE. It read
    ``title.rsplit(",", 1)[-1]`` and asked whether THAT was a strict prefix of
    a published attribute name -- which is the signature in the REFERENCE
    corpus, where the tail is a bare label ("Dia./Thread Siz"). This
    generator's segments are ``"<value> <label>"``, so the tail always carries
    the value too and no attribute name ever starts with it. Measured: a
    mutation truncating a label by one character left this test GREEN, and a
    hand-built ``"... , 1/2\" Cutting Directio"`` went undetected while the
    bare-label form was caught.

    So the signature is now a SUFFIX of the tail: the label sits after the
    value, and a truncated one is a trailing run of words that is a strict
    prefix of a name the document publishes and is not itself a name it
    publishes. That last clause is what keeps a correctly-published ``Length``
    from reading as a truncation of ``Length of Cut``.
    """
    assert len(flat_docs) > 100, "too few documents for a zero to mean anything"

    cut: list[str] = []
    for doc in flat_docs:
        title = doc["title"]
        assert title == title.rstrip(), f"trailing whitespace from a cut: {title!r}"
        tail = title.rsplit(",", 1)[-1].strip()
        published = set(doc["attribute_names"])
        words = tail.split()
        for start in range(len(words)):
            candidate = " ".join(words[start:])
            if len(candidate) <= 4 or candidate in published:
                continue
            if any(name.startswith(candidate) and name != candidate for name in published):
                cut.append(title)
                break

    assert cut == [], (
        f"{len(cut)} of {len(flat_docs)} titles end part-way through a label, "
        f"e.g. {cut[:3]}. A title that does not fit its cap must shed a whole "
        f"segment, never half of one."
    )


def test_an_over_long_title_sheds_a_whole_segment_rather_than_being_cut() -> None:
    """The structural form of the property above, asserted where it is decided.

    The string test cannot see every cut: a title sliced at the cap often
    lands mid-VALUE (``...Solid Carbide, U``) rather than mid-LABEL, and no
    amount of prefix matching against attribute names finds that. Measured --
    the string test alone left the "cut at the cap" mutation GREEN, which is
    why both exist rather than one.

    So this asserts the invariant itself, on the function that decides it: the
    result is EXACTLY the item plus some whole-segment prefix, joined the way
    the title joins them. A string cut at the cap is a slice of that and
    matches no prefix.

    Both directions are covered here: a title that fits keeps every segment,
    and one that does not sheds from the end until it does. Without the first
    assertion a ``build_title`` that dropped everything would also pass.
    """
    from synthetic_industrial_products.catalog.naming import (
        DELIMITER,
        Segment,
        build_title,
    )

    item = "Solid Carbide Square End Mill"
    segments = tuple(
        Segment(value=f'{n}/16"', label="Milling Dia.", attribute="Milling Dia.")
        for n in range(1, 12)
    )

    def prefixes() -> list[str]:
        out = []
        for keep in range(len(segments) + 1):
            pieces = [item] + [DELIMITER + seg.text() for seg in segments[:keep]]
            out.append("".join(pieces))
        return out

    whole = prefixes()

    roomy = build_title(item, segments, cap=10_000)
    assert roomy.text == whole[-1], "a title that fits must keep every segment"
    assert not roomy.truncated

    for cap in (40, 60, 80, 100, 140):
        title = build_title(item, segments, cap=cap)
        assert title.text in whole, (
            f"at cap {cap} the title {title.text!r} is not a whole-segment "
            f"prefix of what it was assembled from -- it was cut"
        )
        assert len(title.text) <= cap or title.text == item, (
            f"at cap {cap} the title is {len(title.text)} characters"
        )

    tight = build_title(item, segments, cap=len(item) + 1)
    assert tight.text == item, "shedding stops at the item, which names the product"


def test_the_cap_cut_this_replaced_really_did_land_inside_words() -> None:
    """The counterfactual the segment rule exists to remove, MEASURED.

    ``test_no_title_is_cut_mid_word`` asserts a zero, and a zero is only worth
    something if the thing it counts was ever non-zero. This reconstructs the
    PRE-#9284 behaviour on the catalog this package generates today -- assemble
    every segment, slice at the cap -- and counts the titles that land inside a
    word.

    THE FIGURE THIS REPLACES DID NOT REPRODUCE. The docstrings carried "97 of
    4,688"; 4,688 is the PREVIOUS generation's document count and 97 is not the
    mid-word count of either generation. Reconstructed here it was 67 of 4,689,
    was 74 of 10,029 on the grown catalog
    (elastic/prism-industrial-products#103), and is 70 of 10,080 (93 over the
    cap) after the 100K brand book,
    and stating it as a test rather than as prose is what stops the next
    regeneration inheriting a number nobody can re-derive.

    The reconstruction spies on ``build_title`` rather than reimplementing the
    grammar: the segments and the delimiters are the production ones, and only
    the trimming rule is the old one.
    """
    from synthetic_industrial_products.catalog import generate as generate_module

    real = generate_module.build_title
    assembled: dict[str, tuple[str, int]] = {}

    def spy(item, segments, *, cap=100, tight_delimiter_at=None):
        pieces = [item]
        for index, segment in enumerate(segments):
            delimiter = TIGHT_DELIMITER if index == tight_delimiter_at else DELIMITER
            pieces.append(delimiter + segment.text())
        title = real(item, segments, cap=cap, tight_delimiter_at=tight_delimiter_at)
        assembled.setdefault(title.text, ("".join(pieces), cap))
        return title

    generate_module.build_title = spy
    try:
        catalog = generate_module.generate()
    finally:
        generate_module.build_title = real

    documents = [child for line in catalog.lines for child in line.children]
    assert len(documents) == 10080
    assert len(assembled) > 100, "the spy recorded nothing; the reconstruction is broken"

    word = set(string.ascii_letters + string.digits + './"-')
    over_cap = mid_word = 0
    for document in documents:
        full, cap = assembled[document.title]
        if len(full) <= cap:
            continue
        over_cap += 1
        if full[cap - 1] in word and full[cap] in word:
            mid_word += 1

    assert over_cap == 93, f"{over_cap} titles exceed the cap, not 93"
    assert mid_word == 70, (
        f"the cap cut would land inside a word on {mid_word} titles, not 70. "
        "If the catalog moved, restate the figure in build_title's docstring "
        "and in test_no_title_is_cut_mid_word with it."
    )
