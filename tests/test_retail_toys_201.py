"""Toy types (gen#201): building sets, jigsaws, board games, dolls, wooden toys, role play,
arts and crafts kits and ride-ons, each with an age range.

:mod:`toys_rows` holds the styles and :mod:`kit_toys` draws them. These checks hold what
the issue asked for: every type has its range (three styles, three brands), each style
draws as its own toy shape, each key attribute the issue lists is a structured entry in
the export, each invented character range is one brand's and spans several kinds, a count
the record states is the count the drawing shows, and the styles reach the scaled build.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import kit  # noqa: E402
import kit_toys  # noqa: E402
import scale  # noqa: E402
import toys_rows  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = toys_rows.ROWS

#: Each type and every key attribute the issue's table lists for it, with the variant
#: axis (the SKU key) and ``age_group`` (the row's audience, which every type carries).
#: Players are a range, so a board game states ``min_players`` and ``max_players``; a
#: kind is ``toy_type``; a craft kit's contents count is its ``piece_count``; a wooden
#: toy's painted or natural is its SKU ``finish``.
KEYS = {
    "Building Set": {"piece_count", "age_range", "age_group", "theme", "compatible_system"},
    "Jigsaw Puzzle": {"piece_count", "age_range", "age_group", "theme", "finished_size"},
    "Board Game": {"min_players", "max_players", "age_range", "age_group", "play_time",
                   "toy_type", "edition"},
    "Doll": {"toy_type", "height_cm", "accessory_count", "age_range", "age_group", "color"},
    "Wooden Toy": {"toy_type", "age_range", "age_group", "fsc_certified", "finish", "material",
                   "color"},
    "Role Play Toy": {"toy_type", "age_range", "age_group", "material", "color"},
    "Arts and Crafts Kit": {"toy_type", "age_range", "age_group", "piece_count", "theme"},
    "Ride-On Toy": {"toy_type", "age_range", "age_group", "max_weight_kg", "wheel_size_in",
                    "wheel_count", "color"},
}  # fmt: skip

#: The marked group each counted mark draws once per counted item, and the attribute that
#: states the count. A jigsaw draws its pieces as a grid of cuts, counted apart.
COUNTED = {
    "piece": "piece_count",
    "accessory": "accessory_count",
    "wheel": "wheel_count",
}


def _attr(row: toys_rows.Row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _svg(row: toys_rows.Row) -> str:
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))


def _marks(svg: str, cls: str) -> int:
    return len(re.findall(rf'<(?:g|path) class="{cls}"', svg))


def _drawn(row: toys_rows.Row) -> dict[str, int]:
    """Each counted attribute and the count the drawing shows for it. A jigsaw's pieces
    are the tiles its cuts make: (horizontal cuts + 1) x (vertical cuts + 1)."""
    svg = _svg(row)
    got = {key: _marks(svg, cls) for cls, key in COUNTED.items()}
    if row.shape == "jigsaw":
        got["piece_count"] = (_marks(svg, "cut-h") + 1) * (_marks(svg, "cut-v") + 1)
    return got


def _stated(row: toys_rows.Row) -> dict[str, int]:
    """Each counted attribute and the count the record states (none stated is none drawn).
    A building set states its piece count per SKU, on one shared box that draws none."""
    return {key: int((_attr(row, key) or ["0"])[0]) for key in COUNTED.values()}


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list[toys_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}


def test_every_style_draws_as_its_own_toy_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_toys.SHAPES} == {}


def test_every_type_draws_with_one_shape_of_its_own() -> None:
    shapes = collections.defaultdict(set)
    for row in ROWS:
        shapes[row.product_type].add(row.shape)
    assert {t: s for t, s in shapes.items() if len(s) != 1} == {}
    assert len({s for ss in shapes.values() for s in ss}) == len(KEYS)


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if KEYS[ptype] - keys:
            missing[row.code] = sorted(KEYS[ptype] - keys)
    assert missing == {}


def test_every_style_is_for_a_child_audience_or_an_adult_jigsaw() -> None:
    ok = {"baby", "toddler", "kids"}
    wrong = {r.code: r.audience for r in ROWS if r.audience not in ok}
    assert {c: a for c, a in wrong.items() if not (a == "adult" and c.startswith("JIG"))} == {}


def test_each_character_range_is_one_brands_and_spans_several_kinds() -> None:
    """A range name alone finds a jigsaw, a building set and a scooter: each of the 3-5
    invented ranges is sold by one brand across two or more types, and its styles carry
    the range's mark."""
    assert 3 <= len(toys_rows.RANGES) <= 5
    kinds: dict[str, set[str]] = collections.defaultdict(set)
    wrong = {}
    for row in ROWS:
        for line in _attr(row, "line"):
            kinds[line].add(row.product_type)
            brand, motif = toys_rows.RANGES[line]
            if row.brand != brand or dict(row.params).get("character") != motif:
                wrong[row.code] = (row.brand, dict(row.params).get("character"))
            elif _marks(_svg(row), "character") != 1:
                wrong[row.code] = "no character mark"
    assert wrong == {}
    assert {n: len(k) for n, k in kinds.items() if len(k) < 2} == {}
    assert set(kinds) == set(toys_rows.RANGES)


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_the_drawing_shows_the_count_its_record_states(row: toys_rows.Row) -> None:
    """A set's pieces, a jigsaw's tiles, a doll's accessories and a ride-on's wheels: the
    drawing has one marked group per item the record states, and none it does not."""
    assert _drawn(row) == _stated(row)


def test_the_counted_marks_cover_a_count_above_one_for_every_mark() -> None:
    """The drawn-count test reads a real count for each mark, jigsaws included."""
    big = {key for r in ROWS for key, n in _stated(r).items() if n > 1}
    assert big == set(COUNTED.values())
    assert {r.code for r in ROWS if r.shape == "jigsaw" and _stated(r)["piece_count"] > 1}


def test_no_toy_drawing_prints_a_number() -> None:
    """A building set's sizes share one box, so a printed piece count would be wrong for
    all but one; no toy drawing prints a number."""
    printed = {}
    for row in ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        if any(re.search(r"\d", w) for w in words):
            printed[row.code] = words
    assert printed == {}


@pytest.mark.timeout(300)
def test_every_toy_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.TOY_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []
