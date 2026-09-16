"""The drawing is a function of the record.

Everything else in the suite would pass just as well for a renderer that
ignored its input and drew the same picture every time, so this is where that
possibility is closed off: change one published value, and the bytes move.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.records import FIXTURES
from synthetic_industrial_products.render import CARD, DETAIL, render_record


def _bytes(record: dict, tmp_path, profile, name="x") -> bytes:
    return render_record(record, tmp_path / f"{name}.png", profile).read_bytes()


@pytest.mark.parametrize("sku", sorted(FIXTURES))
@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_the_same_record_renders_to_the_same_bytes(sku, profile, tmp_path):
    """The control: without this, every comparison below could be noise."""
    first = _bytes(FIXTURES[sku], tmp_path, profile, "a")
    second = _bytes(FIXTURES[sku], tmp_path, profile, "b")
    assert first == second


@pytest.mark.parametrize("sku", sorted(FIXTURES))
@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_an_attribute_the_drawing_does_not_read_does_not_move_it(sku, profile, tmp_path):
    """The other control: the comparison is sensitive to the drawing, not to dict order."""
    base = _bytes(FIXTURES[sku], tmp_path, profile, "a")
    with_extra = _bytes({**FIXTURES[sku], "Country of Origin": "Somewhere"}, tmp_path, profile, "b")
    assert base == with_extra


CARD_CASES = [
    ("4LU10", "Milling Dia.", '3/8"'),
    ("4LU10", "Shank Dia.", '1/2"'),
    ("4LU10", "Length of Cut", '1"'),
    ("4LU10", "Overall Length", '4"'),
    ("4LU10", "Number of Flutes", "2"),
    ("4LU10", "Helix Angle", "45 Degrees"),
    ("4LU10", "sku", "9ZZ99"),
    ("35AM34", "Milling Dia.", "4 mm"),
    ("35AM34", "Shank Dia.", "8 mm"),
    ("33TN24", "Shank Dia.", '5/8"'),
    ("26LD37", "Dia./Thread Size", "#8-32"),
    ("26LD37", "Length", "3/4 in"),
    ("26LD37", "Thread Length", "1/4 in"),
    ("26LD37", "Head Dia.", "0.500 in"),
    ("26LD37", "Head Height", "0.150 in"),
    ("26LD37", "Drive Size", "3/32 in"),
    ("26LD37", "Drive Type", "Square Socket"),
]

DETAIL_ONLY_CASES = [
    ("4LU10", "Finish", "TiCN"),
    ("4LU10", "Item", "Carbide End Mill"),
    ("26LD37", "Screw Style", "Socket Head Cap Screw"),
]


@pytest.mark.parametrize(("sku", "attribute", "value"), CARD_CASES)
@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_changing_a_drawn_value_changes_the_drawing(sku, attribute, value, profile, tmp_path):
    record = FIXTURES[sku]
    assert record[attribute] != value, "the mutation must actually change the record"
    base = _bytes(record, tmp_path, profile, "a")
    moved = _bytes({**record, attribute: value}, tmp_path, profile, "b")
    assert base != moved, f"{attribute} does not reach the {profile.name} drawing"


@pytest.mark.parametrize(("sku", "attribute", "value"), DETAIL_ONLY_CASES)
def test_changing_a_value_the_detail_lists_changes_the_detail(sku, attribute, value, tmp_path):
    record = FIXTURES[sku]
    base = _bytes(record, tmp_path, DETAIL, "a")
    moved = _bytes({**record, attribute: value}, tmp_path, DETAIL, "b")
    assert base != moved


@pytest.mark.parametrize("sku", sorted(FIXTURES))
def test_the_card_and_the_detail_are_different_drawings(sku, tmp_path):
    assert _bytes(FIXTURES[sku], tmp_path, CARD, "a") != _bytes(
        FIXTURES[sku], tmp_path, DETAIL, "b"
    )
