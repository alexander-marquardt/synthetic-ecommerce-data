"""The encoding itself: what each channel is a function of, and what it refuses.

Everything here is about the TABLES, not about the pictures. It is deliberately
only half the story -- a channel can be defined here, round-trip perfectly, and
never reach a drawing at all, which is precisely the ``End Mill Style`` defect
that prompted this work. ``tests/test_line_drawings.py`` is where each channel
is measured on the rendered pixels; this file is where the mapping is measured
on its own terms, so that a failure says which of the two is wrong.

The sweeps are taken from a GENERATED CATALOG rather than from a list written
out here. A value vocabulary that gained a coating would otherwise be covered
only when somebody remembered to add it, and "somebody remembered" is not a
property a test can assert.
"""

from __future__ import annotations

import dataclasses

import pytest

from published import authored_name
from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.brands import BRAND_BOOK, FRAMES, INKS
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, generate
from synthetic_ecommerce_data.domains.industrial.render.attrs import UnsupportedFeatureError
from synthetic_ecommerce_data.domains.industrial.render.marking import (
    BRAND_INK,
    DIRECTION_ATTRIBUTES,
    FINISH_ATTRIBUTES,
    FINISH_TINT,
    MATERIAL_ATTRIBUTES,
    MATERIAL_HATCH,
    MIN_INK_SEPARATION,
    marking_for_line,
)

CATALOG = generate(SMALL)
LINES = list(emit.iter_nested(CATALOG))


def _published(names) -> set[str]:
    """Every value the ORIGINAL twelve types publish under any of ``names``.

    The line marking belongs to those types' line drawings. The newer types
    (elastic/prism-industrial-products#103) are drawn only by the catalog's
    per-SKU renderer, whose palette ``tests/test_sku_drawings.py`` sweeps.
    """
    from synthetic_ecommerce_data.domains.industrial.render.kinds import TYPE_KIND

    wanted = set(names)
    return {
        entry["value"]
        for line in LINES
        if line["product_type"] in TYPE_KIND
        for entry in line["attributes"]
        if authored_name(line["product_type"], entry["name"]) in wanted
    }


# --- the outline color, and reading it backwards -------------------------


def test_every_brand_the_generator_uses_has_an_outline_color():
    """A brand with no color makes a drawing that refuses rather than renders.

    Taken from the generator's own brand list, so a brand added there fails
    here the day it is added rather than the day someone renders it.
    """
    assert set(BRANDS) <= set(BRAND_INK)
    assert set(BRAND_INK) == set(BRANDS), "a color for a brand nothing sells is dead text"


def test_no_ink_lies_on_another_inks_blend_to_the_paper():
    """Distinct hex values are not enough; antialiasing is what breaks this.

    Every stroke is antialiased, so a line drawn in one ink puts pixels at
    every blend between that ink and the paper. Two inks can therefore be
    different colors and still be indistinguishable in the pixels --
    measured, the first palette here put sixteen of one brand's pixels inside
    another brand's color on one card. Checked over the PALETTE: brands now
    share inks (the (ink, frame) pair is what names a brand), so the
    separation that matters is between the inks two brands can be told
    apart by.
    """
    import itertools

    import numpy as np
    from matplotlib.colors import to_rgb

    def separation(color: str, other: str) -> float:
        start = np.array(to_rgb(color))
        target = np.array(to_rgb(other))
        blend = start + (np.ones(3) - start) * np.linspace(0, 1, 201)[:, None]
        return float(np.min(np.max(np.abs(blend - target), axis=1)))

    worst = min((separation(a, b), a, b) for a, b in itertools.permutations(INKS, 2))
    assert worst[0] >= MIN_INK_SEPARATION, f"{worst[1]} fades through {worst[2]} ({worst[0]:.3f})"


def test_the_palette_has_no_repeated_ink():
    assert len(set(INKS)) == len(INKS)


def test_every_brands_ink_is_its_brand_book_ink():
    for book in BRAND_BOOK:
        assert BRAND_INK[book.name] == INKS[book.ink]


def test_a_color_no_brand_claims_does_not_resolve_to_the_nearest_one():
    """The control for the round trip above.

    A ``brand_for_house_style`` that returned the first brand whatever it was
    given would pass most round trips and be useless. This is what says the
    inverse is a lookup and not a guess: an ink no brand uses, and a real ink
    with a frame no brand pairs it with, both refuse.
    """
    from synthetic_ecommerce_data.core.drawing.style import (
        UnknownStyleError,
        brand_for_house_style,
    )

    with pytest.raises(UnknownStyleError):
        brand_for_house_style("#123456", "rule")
    used = {(INKS[b.ink], FRAMES[b.frame]) for b in BRAND_BOOK}
    unused = next((i, f) for i in INKS for f in FRAMES if (i, f) not in used)
    with pytest.raises(UnknownStyleError):
        brand_for_house_style(*unused)


# --- the tint and the hatch ------------------------------------------------


def test_every_coating_the_catalog_publishes_has_a_tint():
    """Swept from the DATA, which is the only place the raggedness is visible.

    A coating with no tint is the ``End Mill Style`` shape: published on the
    record, consumed nowhere, and invisible to mutation testing because an
    unread input has no code to mutate. Here it refuses instead.
    """
    published = _published(FINISH_ATTRIBUTES)
    assert published, "the sweep found no coatings at all, so it is proving nothing"
    assert published <= set(FINISH_TINT), sorted(published - set(FINISH_TINT))


def test_every_material_the_catalog_publishes_has_a_hatch():
    published = _published(MATERIAL_ATTRIBUTES)
    assert published, "the sweep found no materials at all, so it is proving nothing"
    assert published <= set(MATERIAL_HATCH), sorted(published - set(MATERIAL_HATCH))


def test_every_direction_the_catalog_publishes_is_one_the_drawing_can_lean():
    published = _published(DIRECTION_ATTRIBUTES)
    assert published, "the sweep found no directions at all, so it is proving nothing"
    assert published <= {"Right Hand", "Left Hand"}, sorted(published)


def test_no_two_coatings_share_a_tint_and_no_two_materials_share_a_hatch():
    """A channel that maps two values to one appearance is a channel with a lie in it.

    TiAlN and AlTiN are the near miss worth naming: both are violet-greys in
    life, and giving them one color because they look alike would make the
    drawing say the two coatings are the same thing.
    """
    assert len(set(FINISH_TINT.values())) == len(FINISH_TINT)
    assert len(set(MATERIAL_HATCH.values())) == len(MATERIAL_HATCH)


# --- what is refused rather than defaulted --------------------------------


def _attrs(**pairs):
    return [{"name": name, "value": value} for name, value in pairs.items()]


def test_an_unknown_brand_is_refused_rather_than_drawn_in_a_neutral():
    with pytest.raises(UnsupportedFeatureError):
        marking_for_line("Not A Brand", [])


def test_an_unknown_coating_is_refused_rather_than_drawn_as_bare_steel():
    """The failure mode this prevents is a drawing that contradicts its record.

    A fallback would draw an unrecognised coating as uncoated, which is a
    positive claim about the product, made silently, that nothing downstream
    could tell from a real one.
    """
    with pytest.raises(UnsupportedFeatureError):
        marking_for_line("Dravenholt", _attrs(**{"Finish": "Unobtainium Nitride"}))


def test_an_unknown_material_is_refused_rather_than_left_unhatched():
    with pytest.raises(UnsupportedFeatureError):
        marking_for_line("Dravenholt", _attrs(**{"Material": "Wishful Thinking"}))


def test_a_flute_count_that_is_not_a_count_is_refused():
    """``Number of Flutes`` arrives from a real supplier feed and is not always a number."""
    with pytest.raises(UnsupportedFeatureError):
        marking_for_line("Dravenholt", _attrs(**{"Number of Flutes": "several"}))
    with pytest.raises(UnsupportedFeatureError):
        marking_for_line("Dravenholt", _attrs(**{"Number of Flutes": "97"}))


def test_a_record_that_publishes_no_finish_or_material_is_marked_without_one():
    """Silence is not a value. An absent coating leaves the part unfilled.

    Refusing here would be wrong in the other direction: the catalog publishes
    these attributes at measured presence rates well under 1.0, so a line that
    is simply silent about its coating is normal data, not bad data.
    """
    mark = marking_for_line("Dravenholt", [])
    assert mark.tint is None
    assert mark.hatch is None
    assert mark.flutes is None
    assert mark.hand is None


def test_an_unpublished_direction_is_not_recorded_as_a_published_one():
    """The drawing has to lean a flute somewhere; the marking must not pretend.

    ``lean`` is the direction drawn and ``hand`` is what the record said. A
    single field would make "the record says right hand" and "the record is
    silent" the same state, and the stamp would then be the only disclosure
    left -- for a property the picture is asserting.
    """
    silent = marking_for_line("Dravenholt", [])
    stated = marking_for_line("Dravenholt", _attrs(**{"Cutting Direction": "Right Hand"}))
    assert silent.hand is None and silent.lean == 1
    assert stated.hand == 1 and stated.lean == 1


# --- what the marking is NOT a function of --------------------------------


def test_the_marking_reads_nothing_but_the_brand_and_the_line_attributes():
    """Not the product id, not the series, not the title.

    A hash of the id would produce exactly as much variety as this encoding
    and would assert nothing -- and worse, a reader who sees two mills in
    different colors concludes the difference is real. The signature is
    frozen and built from two arguments, so this is asserted by showing that
    two lines with the same brand and attributes mark identically however much
    else about them differs.
    """
    attrs = _attrs(**{"Material": "Cobalt", "Number of Flutes": "3"})
    assert marking_for_line("Varnstrom", attrs) == marking_for_line("Varnstrom", list(attrs))


def test_the_marking_carries_every_published_value_including_repeats():
    """``Standards`` is multi-valued, and a line carries one to three of them.

    Folding them to one would quietly drop a published conformance claim and
    make two lines that differ only in their standards draw the same picture.
    """
    line = {
        "name": "Standards",
        "value": "ISO 1641",
        "values": ["ISO 1641", "REACH", "RoHS 2011/65/EU"],
    }
    mark = marking_for_line("Varnstrom", [line])
    assert [value for name, value in mark.rows if name == "Standards"] == [
        "ISO 1641",
        "REACH",
        "RoHS 2011/65/EU",
    ]


def test_the_stamp_never_breaks_a_published_value_at_its_hyphen():
    """A published value is a TOKEN, not prose.

    ``textwrap`` defaults to breaking at an internal hyphen, so
    ``Non-Coolant Through`` was set as ``Non-`` at the end of one stamp line
    and ``Coolant Through`` on the next. Read back, the card then says
    ``Non- Coolant Through`` -- a value no record publishes -- and the same
    shape threatens ``18-8 Stainless Steel``, ``7/16-14`` and
    ``Roughing/Finishing``.

    Asserted here, on the wrapper, rather than left to the rendered stamp.
    ``tests/test_line_drawings.py`` compares the card's text against the
    record's values for the RICHEST line of each type, and whether that line
    happens to carry a hyphenated value at a wrap boundary is an accident of
    which line is richest: measured, planting the defect back reds nothing
    there on the current catalog. A property that only holds by luck is not
    guarded.
    """
    # The line that found this, value for value: a ball nose end mill whose
    # stamp is long enough that the wrap point falls inside ``Non-Coolant``
    # at several of the widths the card uses. A shorter fixture proves
    # nothing -- textwrap only breaks a hyphenated word when the line is
    # full, so a two-value stamp never reaches the hyphen at any sane width.
    published = [
        "End Mill",
        "Ball Nose",
        "Cobalt",
        "TiAlN",
        "4",
        "35 deg",
        "Right Hand",
        "Single End",
        "Center Cutting",
        "Roughing/Finishing",
        "High Performance",
        "Non-Coolant Through",
        "R908",
        "DIN 338",
        "DIN 6527",
        "REACH",
        "18-8 Stainless Steel",
        "7/16-14",
    ]
    values = [
        {"name": f"attribute {index}", "value": value} for index, value in enumerate(published)
    ]
    mark = marking_for_line("Varnstrom", values)

    # Every width from "the longest value just fits" upwards, so the wrap
    # point sweeps across every hyphen in turn. Not narrower than that: a
    # word longer than the column cannot be set without breaking somewhere,
    # and the card sets this band at 58 columns.
    longest = max(len(value) for value in published)
    for columns in range(longest, 160):
        wrapped = mark.stamp_lines(columns=columns)
        assert wrapped, columns
        rejoined = " ".join(" ".join(wrapped).split())
        assert rejoined == " \u00b7 ".join(published), (
            f"at width {columns} the stamp reads {rejoined!r}, which is not what "
            f"the record publishes"
        )


def test_the_marking_is_frozen():
    """A drawing must not be able to acquire a property on the way through."""
    mark = marking_for_line("Varnstrom", [])
    with pytest.raises(dataclasses.FrozenInstanceError):
        mark.ink = "#000000"  # type: ignore[misc]
