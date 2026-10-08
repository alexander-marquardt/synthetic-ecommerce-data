"""Every dimensioned renderer refuses rather than defaulting a value.

The rule is one sentence -- the drawing may only contain numbers the record
contains -- and it is worth asserting per renderer rather than once, because
the way it is broken is always local: one ``record.get(name, something)`` in
one module, which nothing else in the suite would notice. A defaulted dimension
produces a drawing that disagrees with its own record, and nothing downstream
can tell.

The self-contradictory records here are not hypothetical. The generator
reproduces a measured defect rate: about 8% of tools publish a cut longer than
the tool. Those records stay defective on purpose, and the renderer's job is to
decline to draw them rather than to quietly repair them.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.dimensions import DimensionParseError
from synthetic_ecommerce_data.records import BUNDLED
from synthetic_ecommerce_data.render import CARD, drill, endmill, flapdisc, hammer, tap, washer
from synthetic_ecommerce_data.render.attrs import (
    ImpossibleGeometryError,
    MissingAttributeError,
    UnsupportedFeatureError,
)

#: Which record each renderer is exercised against, and the attributes it
#: cannot draw without. Derived from nothing -- stated -- because the point is
#: to pin the list the renderer requires, and a list read back out of the
#: renderer would agree with it by construction.
REQUIRED = [
    (
        drill,
        "42SR26",
        ["Size", "Shank Dia.", "Flute Length", "Overall Length", "Point Angle"],
    ),
    (tap, "65NL78", ["Thread Size", "Shank Dia.", "Thread Length", "Overall Length"]),
    (washer, "57KY59", ["Inside Dia.", "Outside Dia.", "Thickness"]),
    (flapdisc, "96HD84", ["Diameter", "Arbor Hole"]),
    (
        endmill,
        "26VW40",
        [
            "Milling Dia.",
            "Shank Dia.",
            "Length of Cut",
            "Overall Length",
            "Number of Flutes",
            "Helix Angle",
            "End Mill Style",
        ],
    ),
]

CASES = [(module, sku, name) for module, sku, names in REQUIRED for name in names]


@pytest.mark.parametrize(
    ("module", "sku", "attribute"),
    CASES,
    ids=[f"{m.__name__.split('.')[-1]}-{n}" for m, _, n in CASES],
)
def test_a_missing_attribute_refuses_instead_of_being_assumed(module, sku, attribute):
    record = {k: v for k, v in BUNDLED[sku].items() if k != attribute}
    with pytest.raises(MissingAttributeError):
        module.geometry_from_record(record)


@pytest.mark.parametrize(
    ("module", "sku", "attribute"),
    [(m, s, n) for m, s, n in CASES if n != "End Mill Style"],
    ids=[f"{m.__name__.split('.')[-1]}-{n}" for m, _, n in CASES if n != "End Mill Style"],
)
@pytest.mark.parametrize("bad", ["banana", "", '1/0"'])
def test_an_unreadable_value_refuses_instead_of_being_guessed(module, sku, attribute, bad):
    with pytest.raises(DimensionParseError):
        module.geometry_from_record({**BUNDLED[sku], attribute: bad})


@pytest.mark.parametrize(
    ("module", "sku", "changes"),
    [
        (drill, "42SR26", {"Flute Length": '9"'}),
        (drill, "42SR26", {"Flute Length": '5-7/8"'}),
        (tap, "65NL78", {"Thread Length": '3"'}),
        (washer, "57KY59", {"Inside Dia.": "20.00 mm"}),
        (washer, "57KY59", {"Inside Dia.": "16.00 mm"}),
        (flapdisc, "96HD84", {"Arbor Hole": '6"'}),
        (endmill, "26VW40", {"Length of Cut": '2"'}),
    ],
    ids=[
        "drill-flute-longer-than-tool",
        "drill-flute-equal-to-tool",
        "tap-thread-longer-than-tap",
        "washer-bore-bigger-than-washer",
        "washer-bore-equal-to-washer",
        "flapdisc-arbor-bigger-than-disc",
        "endmill-cut-longer-than-tool",
    ],
)
def test_a_record_that_contradicts_itself_is_refused_not_repaired(module, sku, changes):
    """The defect stays in the data; the drawing declines to depict it.

    Silently clamping the value would draw a tool that exists and publish a
    record that says otherwise, which is worse than no drawing: the picture
    would look like corroboration.
    """
    with pytest.raises(ImpossibleGeometryError):
        module.geometry_from_record({**BUNDLED[sku], **changes})


def test_an_angle_attribute_carrying_a_length_unit_is_refused():
    """A measured defect class: Point Angle published as 42 inches.

    The drill renderer must not read it as 42 degrees, which is what a lenient
    number parser would do.
    """
    with pytest.raises(DimensionParseError):
        drill.geometry_from_record({**BUNDLED["42SR26"], "Point Angle": '42"'})


def test_a_helix_angle_and_an_included_angle_have_different_admissible_ranges():
    """One parser for both would stop rejecting a helix angle published as a point.

    118 is a normal point angle and an impossible helix angle; the catalog
    publishes angle attributes carrying the wrong thing at a measured rate, so
    that rejection is load-bearing.
    """
    with pytest.raises(DimensionParseError):
        endmill.geometry_from_record({**BUNDLED["26VW40"], "Helix Angle": "118 Degrees"})
    assert (
        drill.geometry_from_record({**BUNDLED["42SR26"], "Point Angle": "118 Degrees"}).point_deg
        == 118.0
    )


def test_a_hammer_always_refuses_and_says_what_is_missing():
    """Not a gap in the renderer: see render/hammer.py."""
    with pytest.raises(UnsupportedFeatureError) as exc:
        hammer.geometry_from_record(BUNDLED["2DY27"])
    assert "head length" in str(exc.value)
    with pytest.raises(UnsupportedFeatureError):
        hammer.render(BUNDLED["2DY27"], "unused.png", CARD)


def test_the_refused_records_still_get_an_image():
    """Which is the whole point of the generic drawings.

    A refusal is a statement about what cannot be drawn TO SCALE, not about
    what the product is, and what the product is, is still known.
    """
    import tempfile

    from synthetic_ecommerce_data.render import draw_record

    with tempfile.TemporaryDirectory() as directory:
        for sku in ("2DY27", "56FL37", "77HW11", "44LU90"):
            drawn = draw_record(BUNDLED[sku], f"{directory}/{sku}.png", CARD)
            assert not drawn.dimensioned
            assert drawn.refusal
            assert drawn.path.exists()
