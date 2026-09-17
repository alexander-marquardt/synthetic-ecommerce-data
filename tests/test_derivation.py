"""The dimensioned drawing is a function of the record -- of ALL of it.

Everything else in the suite would pass just as well for a renderer that
ignored its input and drew the same picture every time, so this is where that
possibility is closed off: change one published value, and the bytes move.

The important test here is :func:`test_every_published_attribute_reaches_the_drawing`,
and it is important because of what it catches that nothing else does. The
suite had 39 mutations and no zeros while ``End Mill Style`` was published on
every end mill and read by nothing, so every ball nose in the catalog was drawn
with a square end. **Mutation testing can only mutate code that exists**, and
an attribute nobody consumes has no code path to plant a defect in. The check
that finds that class of defect has to start from the RECORD: take every
attribute the record actually publishes, change it, and require the output to
notice -- or require the attribute to be named, with a reason, in
:data:`~synthetic_industrial_products.render.attrs.NOT_DRAWN`. A newly
published attribute is then covered the day it appears, without anyone
remembering to add it here.

Both directions are asserted. An attribute that is neither consumed nor
declared fails; an attribute declared not-drawn that DOES move the output fails
too, because a declaration nobody checks is a comment.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.records import DRAWABLE
from synthetic_industrial_products.render import CARD, DETAIL, draw_record
from synthetic_industrial_products.render.attrs import NOT_DRAWN, REFUSALS

#: What an attribute is changed to. A value no renderer can read is
#: deliberate: for an attribute the drawing needs, the render then REFUSES,
#: and a refusal is as good a proof that the value reached the drawing as a
#: change in the pixels is.
MUTATED = "ZZZ-mutated"


def _bytes(record: dict, tmp_path, profile, name="x") -> bytes:
    return draw_record(record, tmp_path / f"{name}.png", profile).path.read_bytes()


def _reaches_the_drawing(record: dict, attribute: str, tmp_path, profile) -> bool:
    """True when changing ``attribute`` changes what comes out, or refuses it."""
    base = _bytes(record, tmp_path, profile, "a")
    try:
        moved = _bytes({**record, attribute: MUTATED}, tmp_path, profile, "b")
    except REFUSALS:
        return True
    return base != moved


@pytest.mark.parametrize("sku", sorted(DRAWABLE))
@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_the_same_record_renders_to_the_same_bytes(sku, profile, tmp_path):
    """The control: without this, every comparison below could be noise."""
    first = _bytes(DRAWABLE[sku], tmp_path, profile, "a")
    second = _bytes(DRAWABLE[sku], tmp_path, profile, "b")
    assert first == second


@pytest.mark.parametrize("sku", sorted(DRAWABLE))
@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_an_attribute_the_drawing_does_not_read_does_not_move_it(sku, profile, tmp_path):
    """The other control: the comparison is sensitive to the drawing, not to dict order."""
    base = _bytes(DRAWABLE[sku], tmp_path, profile, "a")
    with_extra = _bytes({**DRAWABLE[sku], "Country of Origin": "Somewhere"}, tmp_path, profile, "b")
    assert base == with_extra


def _is_dimensioned(record: dict) -> bool:
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        return draw_record(record, f"{directory}/x.png", CARD).dimensioned


#: The bundled records the dimensioned renderer actually draws. A record that
#: falls back to its generic drawing shows nothing from its own attributes at
#: all -- that is what a generic drawing is -- so the coverage question does
#: not apply to it, and ``test_generic.py`` asserts the opposite property.
TO_SCALE = {sku: record for sku, record in DRAWABLE.items() if _is_dimensioned(record)}

#: Every (sku, attribute) pair those records publish. Derived from the records,
#: so an attribute that starts being published is covered without anyone adding
#: it here.
PUBLISHED = sorted(
    (sku, name) for sku, record in TO_SCALE.items() for name in record if name != "sku"
)


@pytest.mark.parametrize(("sku", "attribute"), PUBLISHED, ids=lambda v: str(v))
def test_every_published_attribute_reaches_the_drawing(sku, attribute, tmp_path):
    """Read it, or say in NOT_DRAWN why the drawing cannot show it.

    Silence is the failure mode this exists for: an attribute that is neither
    read nor declared is one the drawing may be contradicting.
    """
    record = TO_SCALE[sku]
    reaches = any(
        _reaches_the_drawing(record, attribute, tmp_path, profile) for profile in (CARD, DETAIL)
    )
    if attribute in NOT_DRAWN:
        assert not reaches, (
            f"{attribute!r} is declared not drawn, but changing it moves the drawing of {sku}. "
            "Either the declaration is stale or the reason in it is wrong."
        )
        return
    assert reaches, (
        f"{sku} publishes {attribute!r} and no drawing of it changes when it does. "
        "Read it, or add it to render.attrs.NOT_DRAWN with the reason it cannot be shown."
    )


def test_the_not_drawn_declarations_all_carry_a_reason():
    """A name with an empty reason is a list entry, not a declaration."""
    assert NOT_DRAWN
    for name, reason in NOT_DRAWN.items():
        assert len(reason) > 20, f"{name} needs a reason, not {reason!r}"


def test_every_not_drawn_declaration_is_about_an_attribute_something_publishes():
    """A declaration for a name no product type carries is dead text.

    Checked against the vocabulary rather than the fixtures, because an
    attribute can be rare enough that no bundled record happens to carry it.
    """
    from synthetic_industrial_products.catalog.vocab import VOCAB, names_for

    published = {name for type_key in VOCAB for name in names_for(type_key)}
    published |= {name for record in DRAWABLE.values() for name in record}
    unknown = sorted(set(NOT_DRAWN) - published)
    assert unknown == [], f"NOT_DRAWN names nothing publishes: {unknown}"


@pytest.mark.parametrize("sku", sorted(DRAWABLE))
def test_the_card_and_the_detail_are_different_drawings(sku, tmp_path):
    assert _bytes(DRAWABLE[sku], tmp_path, CARD, "a") != _bytes(
        DRAWABLE[sku], tmp_path, DETAIL, "b"
    )


# --- the same check, over the vocabulary rather than over the fixtures -----
#
# The bundled records do not carry every attribute the catalog publishes: some
# names are rare, and a fixture is a snapshot. So the sweep is repeated against
# a generated catalog, taking the richest record of each product type that the
# dimensioned renderer draws. That is what makes the property a statement about
# the VOCABULARY rather than about eighteen hand-picked records.


def _richest_dimensioned_record_per_type():
    import tempfile

    from synthetic_industrial_products.catalog.config import SMALL
    from synthetic_industrial_products.catalog.emit import render_records
    from synthetic_industrial_products.catalog.generate import generate

    catalog = generate(SMALL)
    type_of = {child.sku: line.type_key for line, child in catalog.all_skus()}
    best: dict[str, dict] = {}
    with tempfile.TemporaryDirectory() as directory:
        for record in render_records(catalog):
            type_key = type_of[record["sku"]]
            if len(record) <= len(best.get(type_key, {})):
                continue
            if draw_record(record, f"{directory}/x.png", CARD).dimensioned:
                best[type_key] = record
    return best


RICHEST = _richest_dimensioned_record_per_type()

CATALOG_PUBLISHED = sorted(
    (type_key, name)
    for type_key, record in RICHEST.items()
    for name in record
    if name != "sku"
)


@pytest.mark.parametrize(("type_key", "attribute"), CATALOG_PUBLISHED, ids=lambda v: str(v))
def test_every_attribute_a_generated_record_publishes_reaches_the_drawing(
    type_key, attribute, tmp_path
):
    record = RICHEST[type_key]
    reaches = any(
        _reaches_the_drawing(record, attribute, tmp_path, profile) for profile in (CARD, DETAIL)
    )
    if attribute in NOT_DRAWN:
        assert not reaches, f"{attribute!r} is declared not drawn but moves a {type_key} drawing"
        return
    assert reaches, (
        f"a {type_key} publishes {attribute!r} and no drawing of it changes when it does. "
        "Read it, or add it to render.attrs.NOT_DRAWN with the reason it cannot be shown."
    )


def test_the_sweep_covers_every_product_type_the_renderer_draws():
    """Guards the sweep itself: a type dropping out would silence its whole row.

    The hammer is absent on purpose and is the one exception -- no view of a
    hammer can be drawn from what a hammer record publishes, so there is no
    dimensioned drawing of one to sweep. See render/hammer.py.
    """
    from synthetic_industrial_products.catalog.vocab import VOCAB

    assert set(RICHEST) == set(VOCAB) - {"hammer_ball_pein"}
    assert len(CATALOG_PUBLISHED) > 80
