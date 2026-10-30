"""A pack of socks or knickers lies in one fan, as a shop's listing shows it (gen#734).

Rows of them read as a heap: most of each item was hidden and black ones merged. The guard reads
the rendered drawing, so what it holds is what the image release draws.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from functools import cache

import pytest

from synthetic_ecommerce_data.domains.retail import (
    image_release,
    kit,
    pack_copies,
    scale,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.kit import Fill

NAVY = Fill("solid", "#1f2d4d", "#ffffff", "#ffffff")
BLACK = Fill("solid", "#1a1a1a", "#ffffff", "#ffffff")
LAID = re.compile(
    r'<use class="pack-copy" href="#[^"]+" transform="rotate\(([-\d.]+) ([\d.]+) ([\d.]+)\)"/>'
)
#: Every way the catalogue draws these two shapes, up to the largest pack it sells.
DRAWN = [
    ("socks", None),
    *(
        ("knickers", {"cut": cut})
        for cut in ("brief", "high_waisted", "high_leg", "bikini", "thong", "shorts")
    ),
]
LARGEST = 7


@cache
def templates() -> tuple[dict, ...]:
    return tuple(scale.templates())


def _fans() -> Iterator[tuple[dict, dict, int]]:
    """Every pack of socks or knickers the catalogue sells that is drawn item by item."""
    for rec in templates():
        if rec["drawing"]["shape"] in ("socks", "knickers"):
            for sku in rec["skus"]:
                n = pack_copies.count(rec, sku)
                if 2 <= n <= pack_copies.MOST_DRAWN:
                    yield rec, sku, n


def test_every_pack_of_socks_or_knickers_fans_its_count() -> None:
    packs = list(_fans())
    assert len(packs) > 500
    assert {n for _, _, n in packs} == {3, 5, 7}
    assert max(n for _, _, n in packs) == LARGEST, "a larger pack needs a look, and this list"
    seen: set[tuple] = set()
    for rec, sku, n in packs:
        key = (rec["drawing"]["shape"], n, (rec["drawing"].get("params") or {}).get("cut"))
        if key in seen:
            continue
        seen.add(key)
        svg = image_release.render(rec, sku).decode()
        assert svg.count('class="pack-copy"') == n, key
        assert len({a for a, _, _ in LAID.findall(svg)}) == n, key


def test_a_pack_of_socks_shows_one_sock_for_each_pair() -> None:
    assert kit.render("socks", NAVY).count('class="sock"') == 2
    assert kit.render("socks", NAVY, copies=3).count('class="sock"') == 1


def test_a_lone_sock_still_takes_the_family_detail() -> None:
    fill = Fill("solid", "#1f2d4d", "#ffffff", "#ffffff", detail=("heel", "#cc0000"))
    svg = kit.render("socks", fill, copies=3)
    assert svg.count('fill="#cc0000"') == 1


def test_knickers_in_a_pack_lie_flat_with_no_shadow() -> None:
    assert kit.render("knickers", NAVY).count("<ellipse") == 1
    assert kit.render("knickers", NAVY, copies=3).count("<ellipse") == 0


def test_a_shape_that_does_not_fan_keeps_the_rows_of_728() -> None:
    svg = kit.render("boxers", NAVY, copies=5)
    assert svg.count('class="pack-copy"') == 5
    assert "pack-edge" not in svg and "rotate(" not in svg


def test_every_family_that_fans_is_named() -> None:
    assert set(pack_copies.FANS) == {"knickers", "socks"}


@pytest.mark.parametrize(
    ("n", "expected"),
    [(2, [-8.0, 8.0]), (3, [-16.0, 0.0, 16.0]), (5, [-32.0, -16.0, 0.0, 16.0, 32.0])],
)
def test_socks_lie_left_to_right(n: int, expected: list[float]) -> None:
    assert pack_copies.turns(n, pack_copies.FANS["socks"]) == expected


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (2, [-4.5, 4.5]),
        (3, [-9.0, 9.0, 0.0]),
        (5, [-18.0, 18.0, -9.0, 9.0, 0.0]),
        (6, [-22.5, 22.5, -13.5, 13.5, -4.5, 4.5]),
    ],
)
def test_knickers_lay_the_middle_one_last(n: int, expected: list[float]) -> None:
    assert pack_copies.turns(n, pack_copies.FANS["knickers"]) == expected


@pytest.mark.parametrize("family", ["knickers", "socks"])
def test_a_large_pack_keeps_to_the_widest_sweep(family: str) -> None:
    fan = pack_copies.FANS[family]
    laid = pack_copies.turns(24, fan)
    assert max(laid) - min(laid) == pytest.approx(fan.sweep)
    assert len(set(laid)) == 24


def test_each_item_turns_about_the_point_its_fan_names() -> None:
    box = (100.0, 50.0, 300.0, 250.0)
    fan = pack_copies.Fan(step=10.0, sweep=90.0, across=0.25, below=0.5)
    svg = pack_copies._fanned('<path d="M100,50 L300,250" fill="#123"/>', box, 2, "#123", "p", fan)
    assert 'rotate(-5.00 150.00 350.00)' in svg and 'rotate(5.00 150.00 350.00)' in svg


def test_every_item_lies_on_its_own_edge_in_the_order_it_is_laid() -> None:
    svg = kit.render("socks", NAVY, copies=3, uid="u")
    assert re.findall(r'<use class="(pack-\w+)"', svg) == ["pack-edge", "pack-copy"] * 3
    turned = re.findall(r'<use class="pack-\w+" href="#(pack-\w+)-u" transform="([^"]+)"', svg)
    assert turned[0][1] == turned[1][1] and turned[2][1] == turned[3][1]
    assert [name for name, _ in turned[:2]] == ["pack-edge", "pack-item"]


def test_the_edge_is_each_painted_path_in_light_keeping_its_groups_turn() -> None:
    body = (
        '<ellipse cx="1"/><g class="sock" transform="translate(1 2)">'
        '<path d="M0,0 L1,1" fill="#abc" stroke="#111" stroke-width="2"/>'
        '<path d="M2,2 L3,3" fill="none" stroke="#111"/></g>'
        '<g class="x"><rect fill="#abc"/></g>'
    )
    assert pack_copies._edge(body, "#abc") == (
        '<g transform="translate(1 2)">'
        '<path d="M0,0 L1,1" fill="#ffffff" stroke="#ffffff" stroke-width="7" '
        'stroke-linejoin="round"/></g><g></g>'
    )


def test_a_black_pack_shows_a_light_edge_and_no_id_twice() -> None:
    svg = kit.render("knickers", BLACK, copies=5, uid="u")
    ids = re.findall(r'\bid="([^"]+)"', svg)
    assert len(ids) == len(set(ids))
    assert 'id="pack-edge-u"' in svg and svg.count('class="pack-edge"') == 5
    edge = svg[svg.index('id="pack-edge-u"') :]
    assert 'stroke="#ffffff" stroke-width="7"' in edge
    assert 'class="waistband"' not in edge


def test_a_print_keeps_its_paint_in_the_edge_only_as_a_silhouette() -> None:
    stripe = Fill("stripe", "#ffffff", "#aa3311", "#ffffff")
    svg = kit.render("socks", stripe, copies=3, uid="u")
    edge = svg[svg.index('id="pack-edge-u"') :]
    assert "url(#fill-u)" not in edge
    assert 'stroke-width="7"' in edge


@pytest.mark.parametrize("n", range(2, pack_copies.MOST_DRAWN + 1))
@pytest.mark.parametrize(("shape", "params"), DRAWN)
def test_a_fan_stays_in_the_area_and_centered(shape: str, params: dict | None, n: int) -> None:
    svg = kit.render(shape, NAVY, params=params, copies=n)
    plain = re.sub(r'<rect width="400".*?/>|<rect x="6".*?/>', "", svg)
    x0, y0, x1, y1 = sheet_extent.reach(plain)
    ax0, ay0, ax1, ay1 = pack_copies.AREA
    assert x0 >= ax0 - 0.1 and y0 >= ay0 - 0.1 and x1 <= ax1 + 0.1 and y1 <= ay1 + 0.1
    assert (x0 + x1) / 2 == pytest.approx((ax0 + ax1) / 2, abs=0.1)
    assert (y0 + y1) / 2 == pytest.approx((ay0 + ay1) / 2, abs=0.1)


def test_a_fan_that_fits_keeps_its_items_full_size() -> None:
    small = pack_copies._fanned(
        '<path d="M190,190 L210,190 L210,210 Z" fill="#123"/>',
        (190.0, 190.0, 210.0, 210.0),
        2,
        "#123",
        "p",
        pack_copies.FANS["socks"],
    )
    assert "scale(1.0000)" in small


def test_a_fan_that_overflows_is_scaled_on_its_tighter_side() -> None:
    tall = pack_copies._fanned(
        '<path d="M190,0 L210,0 L210,800 L190,800 Z" fill="#123"/>',
        (190.0, 0.0, 210.0, 800.0),
        2,
        "#123",
        "p",
        pack_copies.Fan(step=0.0, sweep=0.0, across=0.5, below=0.0),
    )
    assert f"scale({334 / 800:.4f})" in tall
    wide = pack_copies._fanned(
        '<path d="M0,190 L800,190 L800,210 L0,210 Z" fill="#123"/>',
        (0.0, 190.0, 800.0, 210.0),
        2,
        "#123",
        "p",
        pack_copies.Fan(step=0.0, sweep=0.0, across=0.5, below=0.0),
    )
    assert f"scale({352 / 800:.4f})" in wide


@pytest.mark.parametrize("shape", ["socks", "knickers"])
def test_a_pack_above_24_is_still_its_outer_box(shape: str) -> None:
    svg = kit.render(shape, NAVY, copies=30)
    assert 'class="pack-box"' in svg and svg.count('class="pack-copy"') == pack_copies.LOOSE
    assert "rotate(" not in svg and "pack-edge" not in svg


def _outlines(svg: str, uid: str) -> list[list[tuple[float, float]]]:
    """The item's painted paths as polygons on the sheet, read from its edge."""
    root = ET.fromstring(svg)
    named = next(el for el in root.iter() if el.get("id") == f"pack-edge-{uid}")

    def walk(el: ET.Element, m: sheet_extent.Matrix) -> Iterator[list[tuple[float, float]]]:
        here = sheet_extent._mul(m, sheet_extent._transform(el.get("transform")))
        if el.tag.endswith("path"):
            yield [sheet_extent._apply(here, p) for p in sheet_extent._path_points(el.get("d"))]
        for child in el:
            yield from walk(child, here)

    return list(walk(named, sheet_extent.IDENTITY))


def _inside(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    for (x0, y0), (x1, y1) in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _shown(shape: str, params: dict | None, n: int) -> list[float]:
    """Each item's share that no item laid after it covers, in the order they are laid."""
    svg = kit.render(shape, NAVY, params=params, copies=n, uid="u")
    assert 'class="pack-edge"' in svg, "the pack is not a fan"
    outlines = _outlines(svg, "u")
    laid = [sheet_extent._transform(f"rotate({a} {x} {y})") for a, x, y in LAID.findall(svg)]
    assert len(laid) == n
    points = [p for outline in outlines for p in outline]
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    across, down = max(xs) - min(xs), max(ys) - min(ys)
    grid = [
        (min(xs) + across * (u + 0.5) / 18, min(ys) + down * (v + 0.5) / 18)
        for u in range(18)
        for v in range(18)
    ]
    own = [p for p in grid if any(_inside(p, outline) for outline in outlines)]
    shares = []
    for i, turn in enumerate(laid):
        later = [
            [[sheet_extent._apply(m, p) for p in outline] for outline in outlines]
            for m in laid[i + 1 :]
        ]
        turned = [sheet_extent._apply(turn, p) for p in own]
        seen = sum(not any(_inside(p, o) for item in later for o in item) for p in turned)
        shares.append(seen / len(own))
    return shares


@pytest.mark.parametrize("n", range(2, LARGEST + 1))
@pytest.mark.parametrize(("shape", "params"), DRAWN)
def test_every_item_of_the_pack_can_be_counted(shape: str, params: dict | None, n: int) -> None:
    """The issue's words: every item shows enough of itself to be counted."""
    shares = _shown(shape, params, n)
    assert shares[-1] == 1.0, "the last laid lies whole"
    assert min(shares) >= 0.2, shares
