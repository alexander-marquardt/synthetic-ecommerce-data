"""A pack of N is drawn as N items, and a pack above 24 as its outer box (gen#728).

Most packs drew one item, so a six-pack looked like a single can. Every family now shares one
layout, and the guard is the whole generated catalogue, so a new family cannot miss it.
"""

from __future__ import annotations

import re
from collections import Counter
from functools import cache
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    kit,
    pack_copies,
    pack_copies_strip,
    pack_scale,
    scale,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.kit import Fill

STRIP = Path(__file__).resolve().parent.parent / "docs" / "images" / "pack-copies.svg"
USE = re.compile(
    r'<use class="pack-copy" href="#([^"]+)" '
    r'transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([\d.]+)\)"/>'
)
NAVY = Fill("solid", "#1f2d4d", "#ffffff", "#ffffff")


@cache
def templates() -> tuple[dict, ...]:
    return tuple(scale.templates())


def _sku(rec: dict, **fields) -> dict:
    return rec["skus"][0] | fields


def _pack_of(shape: str, n: int) -> tuple[dict, dict]:
    """A real product of ``shape`` and its SKU that holds ``n``."""
    return next(
        (rec, sku)
        for rec in templates()
        if rec["drawing"]["shape"] == shape
        for sku in rec["skus"]
        if pack_copies.count(rec, sku) == n
    )


def _svg(rec: dict, sku: dict) -> str:
    return image_release.render(rec, sku).decode()


def _rec(title: str = "Plain Thing", **drawing) -> dict:
    return {"title": title, "drawing": {"shape": "tub"} | drawing, "attributes": []}


# --------------------------------------------------------------------------
# The count
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("sku", "expected"),
    [
        ({"units_per_pack": 6}, 6),
        ({"units_per_pack": "6"}, 6),
        ({"pack_size": "4 x 125g"}, 4),
        ({"pack_size": "3 pack"}, 3),
        ({"pack_size": "40 bags"}, 40),
        ({"pack_size": "Single"}, 1),
        ({"pack_size": "500g"}, 1),
        ({"pack_size": "2 pint"}, 1),
        ({"pack_size": "10 inch"}, 1),
        ({}, 1),
    ],
)
def test_a_skus_own_pack_is_its_count(sku: dict, expected: int) -> None:
    assert pack_copies.count(_rec(), sku) == expected


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Fruit Yogurt, 4 Pack", 4),
        ("Sports Trainer Socks 5 Pack", 5),
        ("Cotton Rich Ankle Socks 5pk", 5),
        ("Jeans Hanger, Pack of 5", 5),
        ("Linen Tea Towels, Set of 2", 2),
        ("Lemon Rim Block, Twin Pack", 2),
        ("Percale Pillowcase Pair", 2),
        ("Cool Pillow Protectors, Pair", 2),
        ("Running Waist Pack", 1),
        ("Birthday Foil Wrapping Paper Pack", 1),
        ("Pair of Scissors", 1),
        ("Set of Three Stacking Rings", 1),
        ("Pantry Mill Batch 3 Set", 1),
    ],
)
def test_a_title_names_a_count(title: str, expected: int) -> None:
    assert pack_copies.count(_rec(title), {}) == expected


def test_the_skus_own_pack_beats_its_product_and_title() -> None:
    rec = _rec("Socks, 5 Pack", params={"pairs": "7"})
    rec["attributes"] = [{"key": "units_per_pack", "value": "3"}]
    assert pack_copies.count(rec, {"units_per_pack": 2}) == 2
    assert pack_copies.count(rec, {"pack_size": "2 pack"}) == 2
    assert pack_copies.count(rec, {}) == 3
    rec["attributes"] = []
    assert pack_copies.count(rec, {}) == 7


def test_a_product_attribute_gives_the_count_only_when_it_has_one_value() -> None:
    rec = _rec("Thing", attributes=[])
    rec["attributes"] = [{"key": "pack_size", "value": "8 pack"}]
    assert pack_copies.count(rec, {}) == 8
    rec["attributes"] += [{"key": "pack_size", "value": "4 pack"}]
    assert pack_copies.count(rec, {}) == 1
    rec["attributes"] = [{"key": "units_per_pack", "value": v} for v in ("2", "4")]
    assert pack_copies.count(rec, {}) == 1
    rec["attributes"] = [{"key": "pack_size", "value": "500g"}]
    assert pack_copies.count(rec, {}) == 1


def test_a_drawing_that_shows_its_own_count_is_not_copied() -> None:
    assert pack_copies.copies(_rec(params={"count": "4"}), {"units_per_pack": 4}) == 1
    assert pack_copies.copies(_rec(params={"pieces": "2"}), {"units_per_pack": 2}) == 1
    assert pack_copies.copies(_rec(params={"units": "2"}), {"units_per_pack": 2}) == 1
    assert pack_copies.copies(_rec(shape="produce_pile"), {"units_per_pack": 4}) == 1
    assert pack_copies.copies(_rec(params={"count": "1"}), {"units_per_pack": 4}) == 4
    assert pack_copies.spec(_rec(params={"count": "4"}), {"units_per_pack": 4}) == {}
    assert pack_copies.spec(_rec(), {"units_per_pack": 4}) == {"pack_count": 4}
    assert pack_copies.spec(_rec(), {}) == {}


# --------------------------------------------------------------------------
# The catalogue: the guard a new family cannot miss
# --------------------------------------------------------------------------


def _packs() -> dict[int, dict[str, tuple[dict, dict]]]:
    """One SKU per count and shape, over the whole generated catalogue."""
    found: dict[int, dict[str, tuple[dict, dict]]] = {}
    for rec in templates():
        for sku in rec["skus"]:
            found.setdefault(pack_copies.count(rec, sku), {}).setdefault(
                rec["drawing"]["shape"], (rec, sku)
            )
    return found


def test_every_pack_of_2_to_24_draws_its_count() -> None:
    drawn = Counter()
    for n, shapes in _packs().items():
        if not 2 <= n <= pack_copies.MOST_DRAWN:
            continue
        for shape, (rec, sku) in shapes.items():
            svg = _svg(rec, sku)
            copied = svg.count('class="pack-copy"')
            if pack_copies.self_drawn(rec, n):
                assert copied == 0, (shape, n)
                params = rec["drawing"].get("params") or {}
                assert shape in pack_copies.SELF_DRAWN_SHAPES or str(n) in map(str, params.values())
            else:
                assert copied == n, (rec["title"], sku.get("pack_size"), n)
                assert f'data-count="{n}"' in svg
                drawn[shape] += 1
    assert {"knickers", "bar", "tin", "tub", "socks", "baby_bodysuit", "plate"} <= set(drawn)


def test_every_pack_of_fruit_draws_its_count_in_its_pile() -> None:
    piles = [
        (rec, sku)
        for rec in templates()
        if rec["drawing"]["shape"] == "produce_pile"
        for sku in rec["skus"]
        if pack_copies.count(rec, sku) > 1
    ]
    assert len(piles) > 100
    for rec, sku in piles:
        assert _svg(rec, sku).count('class="fruit"') == pack_copies.count(rec, sku), sku["sku"]


def test_a_pack_of_fruit_its_drawing_already_counts_keeps_its_image_id() -> None:
    rec, sku = next(
        (r, s)
        for r in templates()
        if r["drawing"]["shape"] == "produce_pile"
        for s in r["skus"]
        if str(r["drawing"]["params"]["count"]) == str(pack_copies.count(r, s))
    )
    assert pack_copies.pile_count(rec, sku) == {}
    assert "params" not in export.drawing_spec(rec, sku)


def test_a_single_of_fruit_keeps_its_lines_pile() -> None:
    rec = {"title": "Pears", "drawing": {"shape": "produce_pile", "params": {"count": 3}}}
    assert pack_copies.pile_count(rec, {"units_per_pack": 1}) == {}
    assert pack_copies.pile_count(rec, {"units_per_pack": 4}) == {"count": 4}


def test_every_pack_above_24_is_its_outer_box_and_loose_items() -> None:
    shapes = 0
    for n, found in _packs().items():
        if n <= pack_copies.MOST_DRAWN:
            continue
        for shape, (rec, sku) in found.items():
            svg = _svg(rec, sku)
            assert f'<g class="pack-box" data-count="{n}">' in svg, (shape, n)
            assert svg.count('class="pack-copy"') == pack_copies.LOOSE, (shape, n)
            assert f">{n}</text>" in svg, (shape, n)
            shapes += 1
    assert shapes >= 6


def test_a_single_item_is_drawn_as_before() -> None:
    rec = next(r for r in templates() if r["drawing"]["shape"] == "tub"
               and any(pack_copies.count(r, s) == 1 for s in r["skus"]))  # fmt: skip
    sku = next(s for s in rec["skus"] if pack_copies.count(rec, s) == 1)
    assert "pack_count" not in export.drawing_spec(rec, sku)
    svg = _svg(rec, sku)
    assert "<use" not in svg and svg.count('class="pot"') == 1


def test_every_pack_has_its_own_drawing_and_its_own_file() -> None:
    rec = next(r for r in templates() if r["drawing"]["shape"] == "tin"
               and len({pack_copies.count(r, s) for s in r["skus"]}) > 1)  # fmt: skip
    counts = {pack_copies.count(rec, s): s for s in rec["skus"]}
    assert len({export.drawing_id(rec, s) for s in counts.values()}) == len(counts)
    assert len({export.image_id(rec, s) for s in counts.values()}) == len(counts)
    files = dict(image_release.image_files([rec]))
    drawn = {files[image_release.member_path(export.image_id(rec, s))] for s in counts.values()}
    assert len(drawn) == len(counts)


def test_a_matching_pack_variant_carries_the_pack_image() -> None:
    """A tile shows the matching variant's image, so the variant must name the pack's file."""
    rec, sku = _pack_of("tub", 4)
    doc = export.standard_document(rec)
    variant = next(v for v in doc["variants"] if v["sku"] == sku["sku"])
    assert variant["image_url"].endswith(f"/{sku['sku']}.svg")
    files = dict(image_release.image_files([rec]))
    drawn = files[variant["image_url"].removeprefix("/images/")].decode()
    assert drawn.count('class="pack-copy"') == 4


def test_a_yogurt_of_four_pots_shows_four_pots() -> None:
    rec, sku = next(
        (r, s)
        for r in templates()
        if r["drawing"]["shape"] == "tub"
        for s in r["skus"]
        if s.get("pack_size") == "4 x 125g"
    )
    svg = _svg(rec, sku)
    assert len(USE.findall(svg)) == 4
    assert svg.count('class="pot"') == 1, "one pot in the <defs>, four uses of it"


def test_a_pack_is_not_scaled_by_its_pack_factor_too() -> None:
    rec, sku = _pack_of("tin", 4)
    assert pack_scale.factor(rec, sku) is None
    assert "pack_scale" not in export.drawing_spec(rec, sku)


def test_a_single_of_a_multipack_line_keeps_its_factor() -> None:
    rec = _rec()
    skus = [{"units_per_pack": 1}, {"units_per_pack": 8}]
    rec |= {"category_path": ["Food & Drink"], "skus": skus}
    assert pack_scale.factor(rec, rec["skus"][0]) == 0.6
    assert pack_scale.factor(rec, rec["skus"][1]) is None


# --------------------------------------------------------------------------
# The layout
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("n", "width", "height", "expected"),
    [
        (4, 200, 300, [2, 2]),
        (5, 200, 300, [2, 2, 1]),
        (6, 180, 300, [2, 2, 2]),  # a six-pack: two in front, two more rows behind
        (6, 120, 340, [2, 2, 2]),  # a tall bottle keeps the two columns
        (7, 200, 300, [2, 2, 2, 1]),
        (8, 300, 100, [2, 2, 2, 2]),
        (12, 200, 300, [3, 3, 3, 3]),
        (24, 120, 340, [5, 5, 5, 5, 4]),
        (24, 340, 120, [4, 4, 4, 4, 4, 4]),  # wide, but never a tower of two columns
    ],
)
def test_rows(n: int, width: float, height: float, expected: list[int]) -> None:
    assert pack_copies.rows(n, width, height) == expected


@pytest.mark.parametrize("n", range(4, 25))
@pytest.mark.parametrize(("width", "height"), [(100, 300), (250, 300), (300, 300), (340, 120)])
def test_rows_hold_every_copy_with_the_front_row_widest(n: int, width: int, height: int) -> None:
    counts = pack_copies.rows(n, width, height)
    assert sum(counts) == n and counts == sorted(counts, reverse=True)
    assert counts[0] - counts[-1] <= 1


def test_a_file_shrinks_about_five_percent_per_copy_up_and_to_the_right() -> None:
    placed = pack_copies.places(3, 200, 300)
    assert placed[0] == (0.0, 0.0, 1.0)
    assert [round(s, 4) for _, _, s in placed] == [1.0, 0.95, 0.9025]
    assert placed[1][:2] == pytest.approx((200 * 0.2, -300 * 0.1))
    assert placed[2][:2] == pytest.approx((2 * 200 * 0.2, -2 * 300 * 0.1))


def test_each_row_is_smaller_and_higher_than_the_one_before() -> None:
    placed = pack_copies.places(6, 180, 300)
    rows = sorted({(y, s) for _, y, s in placed}, reverse=True)
    assert [s for _, s in rows] == pytest.approx([1.0, 0.9, 0.81])
    assert [y for y, _ in rows] == pytest.approx([0.0, -150.0, -150.0 - 135.0])
    front = sorted(x for x, y, _ in placed if y == 0)
    assert front == pytest.approx([-180 * 0.94 / 2, 180 * 0.94 / 2])


def test_a_deep_pack_keeps_its_rear_row_above_the_floor() -> None:
    placed = pack_copies.places(24, 340, 120)
    assert len({s for _, _, s in placed}) == 6
    assert min(s for _, _, s in placed) == pytest.approx(pack_copies.ROW_FLOOR)
    shallow = pack_copies.places(6, 120, 340)
    assert min(s for _, _, s in shallow) == pytest.approx(0.9**2)


def test_a_pack_that_fits_keeps_its_front_copy_full_size_and_centered() -> None:
    placed = pack_copies.fitted(pack_copies.places(2, 40, 40), 40, 40)
    assert placed[0][2] == 1.0
    left = min(x - s * 20 for x, _, s in placed)
    right = max(x + s * 20 for x, _, s in placed)
    top = min(y - s * 40 for _, y, s in placed)
    bottom = max(y for _, y, _ in placed)
    assert (left + right) / 2 == pytest.approx(200)
    assert (top + bottom) / 2 == pytest.approx(195)


@pytest.mark.parametrize("n", range(2, 25))
@pytest.mark.parametrize(("width", "height"), [(120, 340), (260, 330), (340, 120), (340, 340)])
def test_a_stack_that_overflows_is_scaled_as_a_whole_into_the_area(
    n: int, width: int, height: int
) -> None:
    unit = pack_copies.places(n, width, height)
    placed = pack_copies.fitted(unit, width, height)
    x0, y0, x1, y1 = pack_copies.AREA
    assert min(x - s * width / 2 for x, _, s in placed) >= x0 - 1e-6
    assert max(x + s * width / 2 for x, _, s in placed) <= x1 + 1e-6
    assert min(y - s * height for _, y, s in placed) >= y0 - 1e-6
    assert max(y for _, y, _ in placed) <= y1 + 1e-6
    ratios = {round(p[2] / u[2], 6) for p, u in zip(placed, unit, strict=True)}
    assert len(ratios) == 1, "every copy is scaled by the one fit"


def _visible(placed: list, width: float, height: float) -> list[float]:
    """Each copy's share of its box that no nearer copy's box covers, sampled on a grid."""
    out = []
    for i, (x, y, s) in enumerate(placed):
        nearer = placed[:i]
        grid = [(x + s * width * (u / 19 - 0.5), y - s * height * v / 19)
                for u in range(20) for v in range(20)]  # fmt: skip
        seen = sum(
            not any(
                abs(px - a) <= c * width / 2 and b - c * height <= py <= b for a, b, c in nearer
            )
            for px, py in grid
        )
        out.append(seen / len(grid))
    return out


@pytest.mark.parametrize("n", range(2, 25))
@pytest.mark.parametrize(("width", "height"), [(120, 340), (200, 300), (300, 300), (340, 120)])
def test_each_copy_can_still_be_told_apart(n: int, width: int, height: int) -> None:
    assert min(_visible(pack_copies.places(n, width, height), width, height)) >= 0.15


def test_the_rear_copy_is_drawn_first_so_the_front_one_is_on_top() -> None:
    rec, sku = _pack_of("bottle", 6)
    sizes = [float(m[3]) for m in USE.findall(_svg(rec, sku))]
    assert sizes == sorted(sizes)
    assert sizes[0] < sizes[-1]


def test_a_copy_stands_its_bottom_center_on_its_place() -> None:
    use = pack_copies._use("i", (100.0, 50.0, 300.0, 350.0), (150.0, 340.0, 0.5))
    assert 'href="#i"' in use
    assert 'translate(50.00 165.00) scale(0.5000)' in use


def test_one_drawing_many_uses_keeps_ids_unique_and_the_swatch() -> None:
    rec, sku = _pack_of("knickers", 3)
    color = next(c for c in rec["color_options"] if c["color"] == sku["color"])
    svg = _svg(rec, sku)
    ids = re.findall(r'\bid="([^"]+)"', svg)
    assert len(ids) == len(set(ids))
    assert set(re.findall(r'class="pack-copy" href="#([^"]+)"', svg)) == {
        f"pack-item-{rec['product_id']}"
    }
    assert color["hex"] in svg
    assert svg.count(color["hex"]) == _svg(rec, {**sku, "units_per_pack": 1}).count(color["hex"])


@pytest.mark.parametrize("shape", ["bra", "trainer"])
def test_a_shape_drawn_off_center_stays_inside_the_area_as_a_pack(shape: str) -> None:
    svg = kit.render(shape, NAVY, copies=6)
    plain = re.sub(r'<rect width="400".*?/>|<rect x="6".*?/>', "", svg)
    x0, y0, x1, y1 = sheet_extent.reach(plain)
    assert x0 >= 23 and y0 >= 27 and x1 <= 377 and y1 <= 363


def test_a_stack_measures_through_its_uses_on_the_size_ladder() -> None:
    plain = kit.render("tub", NAVY, copies=4, size_scale=0.7)
    assert 'class="size"' in plain and plain.count('class="pack-copy"') == 4


# --------------------------------------------------------------------------
# Shapes that hold more than one item
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("shape", "params", "mark", "single", "several"),
    [
        ("hangers", None, 'stroke-width="7"', 1, 3),
        ("bath_towel", None, 'stroke-dasharray="1 5"', 1, 3),
        ("travel_organizer", {"kind": "packing cubes"}, 'class="cube"', 1, 3),
    ],
)
def test_a_copy_of_a_shape_that_draws_several_is_one_item(
    shape, params, mark, single, several
) -> None:
    assert kit.render(shape, NAVY, params=params, copies=2).count(mark) == single
    assert kit.render(shape, NAVY, params=params).count(mark) == several


def test_a_pack_tells_a_shape_only_what_it_reads() -> None:
    assert pack_copies.one_item("tub", {"a": "b"}) == {"a": "b"}
    assert pack_copies.one_item("tub", None) is None
    assert pack_copies.one_item("hangers", None) == {"nested": "1"}
    assert pack_copies.one_item("hangers", {"a": "b"}) == {"a": "b", "nested": "1"}
    assert pack_copies.one_item("socks", None) == {"lone": "1"}
    assert pack_copies.one_item("knickers", {"cut": "thong"}) == {"cut": "thong", "flat": "1"}


def test_a_sock_rows_pairs_are_its_count_not_a_shape_param() -> None:
    rec, sku = _pack_of("socks", 5)
    assert rec["drawing"]["params"]["pairs"] == "5"
    svg = _svg(rec, sku)
    assert svg.count('class="pack-copy"') == 5 and "pairs</text>" not in svg


# --------------------------------------------------------------------------
# Above 24: the outer box
# --------------------------------------------------------------------------


def _box_width(n: int) -> float:
    svg = pack_copies.outer_box(n, "#336699")
    root = f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>'
    box = sheet_extent.reach(root)
    assert box is not None
    return box[2] - box[0]


def test_the_box_grows_a_little_with_the_count_so_tea_packs_tell_apart() -> None:
    small, middle, large = (_box_width(n) for n in (40, 80, 240))
    assert small < middle < large
    assert middle - small >= 20 and large - middle >= 20
    assert large / small <= 1.4, "a little, not a jump"


def test_the_box_stops_growing_at_its_largest_size() -> None:
    assert pack_copies.growth(240) == pytest.approx(1.0)
    assert pack_copies.growth(1000) == 1.0
    assert pack_copies.growth(25) == pytest.approx(pack_copies.BOX_SMALLEST)


@pytest.mark.parametrize("n", [25, 40, 100, 240, 1000])
def test_the_box_stays_in_the_area_and_keeps_the_product_paint(n: int) -> None:
    svg = pack_copies.outer_box(n, "url(#fill-p)")
    assert 'fill="url(#fill-p)"' in svg and f">{n}</text>" in svg and ">pack</text>" in svg
    x0, y0, x1, y1 = sheet_extent.reach(f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>')
    assert x0 >= 24 and y0 >= 28 and x1 <= 376 and y1 <= 362


def test_the_loose_items_stand_before_the_box_in_the_area() -> None:
    placed = pack_copies._loose(300, 150)
    assert len(placed) == pack_copies.LOOSE
    assert {y for _, y, _ in placed} == {362.0}
    assert placed[0][0] == 200.0, "the front one is centered"
    size = placed[0][2]
    assert size == pytest.approx(116 / 300)
    assert min(x for x, _, _ in placed) - size * 150 == pytest.approx(24)
    assert max(x for x, _, _ in placed) + size * 150 == pytest.approx(376)
    assert pack_copies._loose(50, 50)[0][2] == 1.0
    assert pack_copies._loose(50, 200)[0][2] == pytest.approx(116 / 200)


def test_a_small_item_keeps_its_size_at_the_loose_box_but_never_grows() -> None:
    svg = kit.render("tub", NAVY, copies=40)
    assert 'class="pack-box"' in svg and svg.count('class="pack-copy"') == 3
    assert svg.index('class="pack-box"') < svg.index('class="pack-copy"'), "the box is behind"


def test_a_shape_that_draws_nothing_comes_back_as_it_is() -> None:
    assert pack_copies.layout("", [], 4, "#000000", "p", "tub") == ""


# --------------------------------------------------------------------------
# The measure, and the strip
# --------------------------------------------------------------------------

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg">'
    '<defs><g id="i"><rect width="10" height="20"/></g></defs>{}</svg>'
)


def test_a_use_is_measured_through_its_transform() -> None:
    use = '<use href="#i" transform="translate(100 50) scale(2)"/>'
    assert sheet_extent.reach(SVG.format(use)) == (100.0, 50.0, 120.0, 90.0)


def test_a_definition_alone_measures_nothing() -> None:
    assert sheet_extent.reach(SVG.format("")) is None


def test_a_use_that_names_nothing_is_refused() -> None:
    with pytest.raises(ValueError, match="names nothing"):
        sheet_extent.reach(SVG.format('<use href="#missing"/>'))


@pytest.mark.parametrize("attr", ["x", "y", "width", "height"])
def test_a_use_with_its_own_placement_is_refused(attr: str) -> None:
    with pytest.raises(ValueError, match="its own x, y"):
        sheet_extent.reach(SVG.format(f'<use href="#i" {attr}="5"/>'))


def test_a_clip_path_that_names_a_group_is_still_refused() -> None:
    drawn = '<rect width="5" height="5" clip-path="url(#i)"/>'
    with pytest.raises(ValueError, match="names no clipPath"):
        sheet_extent.reach(SVG.format(drawn))


def test_the_strip_shows_the_packs_the_issue_names() -> None:
    captions = [caption for caption, _ in pack_copies_strip.cells()]
    assert len(captions) == len(set(captions)) == 19
    drawn = dict(pack_copies_strip.cells())
    for caption, n in (("Socks, 3 pairs", 3), ("Socks, 5 pairs", 5), ("Lager, 6 cans", 6),
                       ("Knickers, 3 pack", 3), ("Knickers, 7 pack", 7),
                       ("Ginger beer, 6 bottles", 6),
                       ("Eye patches, 24", 24),
                       ("Kids dresses, 2 pack", 2), ("Kids dresses, 3 pack", 3)):  # fmt: skip
        assert drawn[caption].decode().count('class="pack-copy"') == n, caption
    for caption, n in (("Tea, 40 bags", 40), ("Tea, 80 bags", 80), ("Tea, 240 bags", 240),
                       ("Eye patches, 30", 30), ("Cable ties, 100", 100)):  # fmt: skip
        assert f">{n}</text>" in drawn[caption].decode(), caption


def test_the_docs_strip_is_the_one_the_code_draws() -> None:
    assert STRIP.read_text(encoding="utf-8") == pack_copies_strip.strip()
