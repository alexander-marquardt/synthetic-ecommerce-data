"""Two generator defects a moved default seed exposed (#50, slice 3).

Seed 20260918 built a 1/2-13 nut claiming ASME B18.2.2 whose height read
``11.13mm``: the unit-mixing defect restated the published ``0.438`` (7/16"
rounded), not the 7/16" itself, which is 11.11 mm. The same seed built key
stock lines whose rectangular bar sat beside both the square of its width and
the square of its height, so a bar's title had no value of its own to name.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.model import keyword_attribute, length_attribute
from synthetic_ecommerce_data.domains.industrial.drafts import ChildDraft
from synthetic_ecommerce_data.domains.industrial.generate import Generator
from synthetic_ecommerce_data.domains.industrial.newtypes import build_nut
from synthetic_ecommerce_data.domains.industrial.product_types.raw_materials import key_stock

NUT_LENGTHS = {"Width Across Flats", "Height"}


class _EveryDefect:
    """A random stream that fires every defect and picks the last length."""

    def random(self) -> float:
        return 0.0

    def choice(self, options):
        return options[-1]


def test_a_unit_mixed_nut_height_restates_its_table_value_not_the_rounded_one():
    gen = Generator(GeneratorConfig(), "nut_hex")
    gen.rng = _EveryDefect()  # type: ignore[assignment]
    child = ChildDraft(system="in")
    child.attrs = [
        keyword_attribute("Thread Size", "1/2-13"),
        length_attribute("Width Across Flats", '0.750"'),
        length_attribute("Height", '0.438"'),
    ]
    child.exact = {"Width Across Flats": 0.75, "Height": 7 / 16}
    out = gen._inject_defects(child, list(child.attrs))
    assert out[2].value == "11.11mm", out[2]


def test_a_nut_records_the_magnitude_each_length_was_published_from():
    gen = Generator(GeneratorConfig(), "nut_hex")
    checked = 0
    for _ in range(40):
        draft = build_nut(gen, "nut_hex", ("Fasteners", "Nuts", "Hex Nuts"))
        for child in draft.children:
            lengths = {a.name: a.value_num for a in child.attrs if a.name in NUT_LENGTHS}
            assert set(child.exact) == NUT_LENGTHS, (child.primary, child.exact)
            for name, published in lengths.items():
                # The published figure is the recorded one, rounded at most to thousandths.
                assert published is not None
                assert abs(published - child.exact[name]) <= 0.0005 + 1e-9, (name, published)
                checked += 1
    assert checked > 100


def _bars_without_a_value_of_their_own(sections):
    return [
        (w, h)
        for w, h in sections
        if sum(other[0] == w for other in sections) > 1
        and sum(other[1] == h for other in sections) > 1
    ]


@pytest.mark.parametrize("count", range(1, len(key_stock.SECTIONS) + 2))
def test_every_key_stock_bar_has_a_width_or_height_no_other_bar_in_its_line_has(count):
    for start in range(len(key_stock.SECTIONS)):
        sections = key_stock.line_sections(start, count)
        assert len(set(sections)) == len(sections), (start, count, sections)
        assert _bars_without_a_value_of_their_own(sections) == [], (start, count, sections)


@pytest.mark.parametrize("count", range(1, len(key_stock.SECTIONS) + 2))
def test_a_key_stock_window_that_already_tells_its_bars_apart_is_kept(count):
    """A line moves only where its contiguous window would hold a bar with no value of its
    own; it then skips that bar for the next section, and keeps the count up to the eleven
    squares a line can always hold."""
    n = len(key_stock.SECTIONS)
    for start in range(n):
        window = [key_stock.SECTIONS[(start + k) % n] for k in range(min(count, n))]
        sections = key_stock.line_sections(start, count)
        if not _bars_without_a_value_of_their_own(window):
            assert sections == window, (start, count)
        assert len(sections) >= min(count, len(key_stock.SQUARE)), (start, count, sections)
        assert sections[0] == window[0]
        assert all(isinstance(w, Fraction) for w, _ in sections)
