"""A class 6 range name is a place, never a color (gen#446, the rule of #444).

"Womens Red Tarn Jumper", "Mens Red Tarn Chinos", "Red Tarn Kite" read as red products although
the product is not red, and a title may not claim a color the product lacks. The decoy tables of
knitwear, mens depth, the elasticated-waist needs slice and the six toy types held a range name
that starts with a main color. A class 6 title now holds no color word at all: the range is a
place that starts with a product word (the word the decoy targets), and a color word in a decoy
name is only ever the invented brand (class 7), which is the product's brand field.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import knitwear_rows  # noqa: E402
import mens_depth_rows  # noqa: E402
import needs_rows  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402

#: Written out here, not read from the generator: the colors a title can claim.
COLOR_WORDS = frozenset({
    "red", "blue", "green", "yellow", "black", "white", "orange", "pink", "purple", "brown",
    "grey", "gray", "navy", "beige", "cream", "ivory", "gold", "silver", "teal", "olive",
})
TOY_KEYS = ("kite", "play_kitchen", "dolls_house", "card_game", "marble_run", "water_gun")
#: Each family's range-name decoys: three types times two roots for knitwear, the mens kinds
#: times three, the needs kind times three, two per toy type.
FAMILIES = {"knitwear": knitwear_rows, "mens depth": mens_depth_rows, "needs": needs_rows}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


@pytest.fixture(scope="module")
def shipped() -> dict[str, dict]:
    return {r["product_id"]: r for r in scale.templates()}


@pytest.mark.parametrize("family", FAMILIES)
def test_a_class_6_apparel_range_name_holds_no_color_and_names_a_product_word(
    family: str, shipped: dict[str, dict]
) -> None:
    """The title of a class 6 decoy holds no color word, and the decoy's targeted word (its
    ``word``) is a product word the range starts with, so a plain text match on that word still
    finds it. The old table started every range with a main color."""
    sixes = [d for d in FAMILIES[family].TABLE if d.klass == 6]
    assert len(sixes) >= 3, (family, len(sixes))
    for d in sixes:
        rec = shipped[f"BRD-{d.code}"]
        title = rec["title"]
        assert not _words(title) & COLOR_WORDS, (d.code, title)
        assert d.word.lower() not in COLOR_WORDS, (d.code, d.word)
        assert d.word.lower() in _words(title), (d.code, d.word, title)
        assert d.query.lower() == d.word.lower(), (d.code, d.query)
        assert d.word.lower() not in _words(rec["category_path"][-1]), (d.code, d.word)
        assert "range" in rec["description"].lower(), d.code


@pytest.mark.parametrize("family", FAMILIES)
def test_a_class_6_apparel_decoy_gives_its_range_as_a_place_in_the_description(
    family: str, shipped: dict[str, dict]
) -> None:
    """The description names the range and says what it is named for, in words with no color
    that the product lacks (the product's own true color is the only one it may state)."""
    for d in (d for d in FAMILIES[family].TABLE if d.klass == 6):
        desc = shipped[f"BRD-{d.code}"]["description"]
        claimed = _words(desc) & COLOR_WORDS - {d.color.lower()}
        assert not claimed, (d.code, desc)
        assert "named for" in desc, (d.code, desc)


@pytest.mark.parametrize("key", TOY_KEYS)
def test_a_toy_class_6_range_name_holds_no_color_and_a_toy_word_of_its_query(key: str) -> None:
    """Every class 6 toy decoy is a place named with another toy's words; its query is those
    words and its title holds no color word."""
    decoys = [d for d in type_registry.specs()[key].decoys if d.cls == 6]
    assert len(decoys) >= 2, (key, [d.row.code for d in decoys])
    for d in decoys:
        title = d.row.title
        assert not _words(title) & COLOR_WORDS, (d.row.code, title)
        assert not _words(d.query) & COLOR_WORDS, (d.row.code, d.query)
        assert _words(d.query) <= _words(title), (d.row.code, d.query, title)
        assert _words(d.query).isdisjoint(_words(d.row.path[-1])), (d.row.code, d.query)
        claimed = _words(d.row.description) & COLOR_WORDS - {d.row.colors[0][0].lower()}
        assert not claimed, (d.row.code, d.row.description)
    assert len({d.query for d in decoys}) == len(decoys), (key, [d.query for d in decoys])
