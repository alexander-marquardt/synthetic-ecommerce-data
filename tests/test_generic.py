"""The ten catalog images: what they are, and what they must not contain.

A generic drawing asserts one thing -- *this product is a ball nose end mill* --
and nothing numeric. That is what makes it safe to put the same image behind
seven hundred products whose dimensions all differ, and it is a property worth
measuring rather than trusting, because "no dimension callout" is exactly the
kind of thing that stays true right up until somebody adds a helpful label.

Two independent proofs are asserted here, each with its own control:

* **Nothing on the image is drawn in the dimension colour.** Every callout
  primitive in :mod:`~synthetic_industrial_products.render.canvas` draws in
  ``DIM`` and nothing else does, so a callout cannot appear without ``DIM``
  pixels appearing. The control is
  :func:`test_the_same_check_finds_the_callouts_on_a_dimensioned_drawing`: the
  identical measurement, applied to a drawing that DOES carry callouts, must
  find them. Without that control, a green here would be consistent with the
  measurement being broken.
* **The image is the same file whatever the record says.** Two records of one
  product type whose every dimension differs render byte for byte identically,
  which is a proof no reviewer has to re-read the drawing code for: there is no
  number from the record on the page because there is no path by which one
  could get there.
"""

from __future__ import annotations

import re

import numpy as np
import pytest
from matplotlib.text import Text

from helpers import colour_mask, figure_pixels
from synthetic_industrial_products.catalog import taxonomy
from synthetic_industrial_products.records import DRAWABLE
from synthetic_industrial_products.render import CARD, DETAIL, endmill, generic
from synthetic_industrial_products.render.canvas import DIM
from synthetic_industrial_products.render.profiles import CARD_CSS, DETAIL_CSS, SCALE

#: Anything that looks like a measurement: a diameter sign, a number with a
#: unit, a fraction, a thread designation, a degree.
DIMENSION_TEXT = re.compile(
    r"Ø|\d\s*(?:\"|in\b|mm\b|°|deg)|\b\d+\s*/\s*\d+\b|#\d+-\d+", re.IGNORECASE
)


def _texts(fig) -> list[str]:
    return [t.get_text() for t in fig.findobj(Text) if t.get_text().strip()]


def _dim_pixels(fig) -> int:
    return int(colour_mask(figure_pixels(fig), DIM, tol=0.10).sum())


@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
@pytest.mark.parametrize("image_id", generic.IMAGE_IDS)
def test_a_generic_image_carries_no_dimension_callout(image_id, profile):
    """Not an estimated one, not a typical one, none."""
    fig, _ = generic.build(image_id, profile)
    assert _dim_pixels(fig) == 0, f"{image_id} {profile.name} draws in the dimension colour"


def test_the_same_check_finds_the_callouts_on_a_dimensioned_drawing():
    """The control. Without it the test above could be measuring nothing.

    A dimensioned end-mill card carries two diameter callouts, so the identical
    measurement must come back non-zero on it.
    """
    fig, _, _ = endmill.build(DRAWABLE["26VW40"], CARD)
    assert _dim_pixels(fig) > 100


@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
@pytest.mark.parametrize("image_id", generic.IMAGE_IDS)
def test_no_text_on_a_generic_image_looks_like_a_measurement(image_id, profile):
    """The second, independent reading of the same property.

    A callout that somehow avoided the dimension colour would still have to put
    a value on the page, and this is what looks for one.
    """
    fig, _ = generic.build(image_id, profile)
    for text in _texts(fig):
        assert not DIMENSION_TEXT.search(text), f"{image_id} {profile.name} prints {text!r}"


def test_the_measurement_check_would_catch_a_value_that_was_printed():
    """The control for the text reading: the pattern really does match values."""
    for value in ('Ø1/4"', "3.5 mm", "#10-32", "118 Degrees", "0.411 in"):
        assert DIMENSION_TEXT.search(value), value


def test_the_card_carries_no_text_at_all():
    """Including no SKU.

    One image stands behind hundreds of products. A SKU printed on it would be
    wrong for all but one of them, which is a worse failure than a missing
    label -- it is a true-looking claim about the wrong product.
    """
    for image_id in generic.IMAGE_IDS:
        fig, _ = generic.build(image_id, CARD)
        assert _texts(fig) == [], f"{image_id} card prints {_texts(fig)}"


def test_the_detail_names_the_product_type_and_says_it_is_not_to_scale():
    for image_id in generic.IMAGE_IDS:
        fig, _ = generic.build(image_id, DETAIL)
        printed = " ".join(_texts(fig))
        assert generic.IMAGES[image_id].label in printed
        assert "not to scale" in printed


#: Two different, valid values for every dimension attribute the catalog
#: publishes. Anything not listed gets two different keyword values.
TWO_VALUES: dict[str, tuple[str, str]] = {
    "Milling Dia.": ('1/4"', "9 mm"),
    "Shank Dia.": ('3/8"', "12 mm"),
    "Length of Cut": ('5/8"', "40 mm"),
    "Overall Length": ('3-3/8"', "120 mm"),
    "Neck Length": ('3/4"', "50 mm"),
    "Corner Radius": ('1/32"', "1 mm"),
    "Number of Flutes": ("2", "6"),
    "Helix Angle": ("30 Degrees", "45 Degrees"),
    "Point Angle": ("118 Degrees", "135 Degrees"),
    "Drill Size": ('1/8"', "11 mm"),
    "Decimal Equivalent": ("0.1250", "0.4331"),
    "Flute Length": ('1"', "70 mm"),
    "Thread Size": ("#10-32", "M12x1.75"),
    "Pitch": ("32", "1.75"),
    "Thread Length": ('1/2"', "30 mm"),
    "Square Size": ('1/8"', "9 mm"),
    "Inside Dia.": ("3 mm", "17 mm"),
    "Outside Dia.": ("7 mm", "30 mm"),
    "Thickness": ("0.5 mm", "3 mm"),
    "Disc Dia.": ('4-1/2"', "180 mm"),
    "Arbor Hole Size": ('7/8"', "22 mm"),
    "Grit": ("40", "120"),
    "Max. RPM": ("13,300", "8,600"),
    "Head Weight": ("4 oz", "32 oz"),
    "Face Dia.": ('0.68"', "40 mm"),
    "Handle Length": ('9"', "400 mm"),
    "Length": ('1/2"', "80 mm"),
    "Head Dia.": ('0.411"', "18 mm"),
    "Head Height": ('0.127"', "12 mm"),
    "Drive Size": ('1/8"', "6 mm"),
    "Width Across Flats": ('7/16"', "19 mm"),
    "Dia./Thread Size": ("#10-32", "M12x1.75"),
}

#: The style attribute that decides which of the ten a product type shows.
STYLE_OF_TYPE: dict[str, dict[str, str]] = {
    "end_mill_square": {"End Mill Style": "Square"},
    "end_mill_ball": {"End Mill Style": "Ball Nose"},
    "screw_socket_head": {"Screw Head Type": "Socket"},
    "screw_flat_head": {"Screw Head Type": "Flat"},
    "bolt_hex": {"Screw Head Type": "Hex"},
}


def _two_records(type_key: str) -> tuple[dict, dict]:
    """Two records of one product type agreeing on nothing but their type.

    Built from the type's whole VOCABULARY rather than from a fixture, so an
    attribute added to the catalog is covered here without anyone remembering.
    """
    from synthetic_industrial_products.catalog.vocab import names_for

    first: dict[str, str] = {"sku": "AAA11"}
    second: dict[str, str] = {"sku": "ZZZ99"}
    for name in sorted(names_for(type_key)):
        low, high = TWO_VALUES.get(name, (f"{name} one", f"{name} two"))
        first[name] = low
        second[name] = high
    for name, value in STYLE_OF_TYPE.get(type_key, {}).items():
        first[name] = second[name] = value
    return first, second


@pytest.mark.parametrize("type_key", sorted(taxonomy.DRAWING))
def test_the_image_does_not_depend_on_any_record(type_key, tmp_path):
    """The structural proof that no number from a record can be on the page.

    Every attribute the product type publishes is given a different value in
    the second record -- a different diameter, a different length, a different
    material -- and the two image files are compared byte for byte.
    """
    first, second = _two_records(type_key)
    expected = taxonomy.DRAWING[type_key]
    assert generic.drawing_for_record(first) == expected
    assert generic.drawing_for_record(second) == expected
    a = generic.render_record(first, tmp_path / "a.png", CARD).read_bytes()
    b = generic.render_record(second, tmp_path / "b.png", CARD).read_bytes()
    assert a == b


def test_those_two_records_really_do_differ():
    """The control: a comparison of two identical inputs proves nothing."""
    for type_key in taxonomy.DRAWING:
        first, second = _two_records(type_key)
        differing = [k for k in first if k != "sku" and first[k] != second[k]]
        assert len(differing) >= 6, (type_key, differing)


def test_the_control_for_that_is_a_dimensioned_drawing_which_does_move(tmp_path):
    """Same two records, drawn to scale: those files must differ.

    Otherwise the comparison above proves nothing about generic drawings and
    only proves the harness is comparing the wrong thing.
    """
    base = dict(DRAWABLE["26VW40"])
    a = endmill.render(base, tmp_path / "a.png", CARD).read_bytes()
    b = endmill.render({**base, "Milling Dia.": '1/2"'}, tmp_path / "b.png", CARD).read_bytes()
    assert a != b


def test_the_ten_are_ten_DIFFERENT_drawings(tmp_path):
    """Two product types sharing one picture is a wrong picture for one of them.

    Nothing else here would notice: every other property of a generic drawing
    -- no callouts, no dependence on the record -- stays true of a drawing that
    is simply the wrong shape, which is how a square end mill could come to be
    drawn with a ball nose and stay green.
    """
    seen: dict[bytes, str] = {}
    for image_id in generic.IMAGE_IDS:
        data = generic.render(image_id, tmp_path / f"{image_id}.png", CARD).read_bytes()
        assert data not in seen, f"{image_id} and {seen.get(data)} are the same drawing"
        seen[data] = image_id


def test_a_square_end_mill_and_a_ball_nose_are_not_the_same_picture(tmp_path):
    """Named separately because it is the defect that prompted all of this."""
    square = generic.render("end_mill_square", tmp_path / "s.png", CARD).read_bytes()
    ball = generic.render("end_mill_ball", tmp_path / "b.png", CARD).read_bytes()
    assert square != ball


def test_there_are_exactly_ten_and_the_catalog_uses_all_of_them():
    assert len(generic.IMAGE_IDS) == 10
    assert set(taxonomy.DRAWING.values()) == set(generic.IMAGE_IDS)
    assert set(taxonomy.DRAWING) == set(taxonomy.LEAVES)


@pytest.mark.parametrize("image_id", generic.IMAGE_IDS)
def test_each_image_is_the_size_its_profile_promises(image_id, tmp_path, png_size):
    card = generic.render(image_id, tmp_path / "c.png", CARD)
    detail = generic.render(image_id, tmp_path / "d.png", DETAIL)
    assert png_size(card) == (CARD_CSS[0] * SCALE, CARD_CSS[1] * SCALE)
    assert png_size(detail) == (DETAIL_CSS[0] * SCALE, DETAIL_CSS[1] * SCALE)


@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
@pytest.mark.parametrize("image_id", generic.IMAGE_IDS)
def test_the_image_is_not_blank_and_has_not_run_away(image_id, profile):
    fig, _ = generic.build(image_id, profile)
    image = figure_pixels(fig)
    inked = float(np.mean(np.any(image < 0.85, axis=-1)))
    assert 0.01 < inked < 0.5, f"{image_id} {profile.name}: {inked:.2%} inked"


def test_a_style_the_drawings_do_not_cover_is_refused_not_approximated():
    with pytest.raises(generic.UnsupportedFeatureError):
        generic.drawing_for_record({"sku": "A", "Milling Dia.": "x", "End Mill Style": "Corner"})


def test_an_end_mill_that_does_not_say_which_end_it_has_gets_no_generic_either():
    """There is no drawing that is true of "an end mill, end unknown".

    A square one and a ball nose one are different products; picking either
    because the record was silent would assert something the record does not
    say, and a generic drawing's whole value is that it asserts only what is
    certain.
    """
    with pytest.raises(generic.MissingAttributeError):
        generic.drawing_for_record({"sku": "A", "Milling Dia.": '1/4"'})
