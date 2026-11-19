"""``tub`` is drawn as a real lidded tub, and Hot Chocolate leaves it for a tin (gen#1028, slice 3).

The maintainer: "that 'tub' drawing label feels a bit misleading if it looks like a cup". The old
``tub`` was a tall tapered open pot, which reads as a paper cup. It is now short and wide, with a
slightly flared wall under a lid with a rim. Only real tubs draw it (``TUB_TYPES`` in
``tests/test_retail_supplement_bottle_1028.py``): yogurt, laundry pods and capsules, the gel air
freshener pot and the car wax pot. The one Hot Chocolate that drew it (PLT-HCORNG) is a tin.
"""

from __future__ import annotations

import collections
import json
import re

import pytest

from synthetic_ecommerce_data.domains.retail import kit, scale

#: The old ``tub``'s tapered open pot, as ``kit.tub`` drew it before slice 3.
OLD_CUP = "M112,118 L288,118 L262,356"
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    return scale.templates()


def _svg(row: dict) -> str:
    d = row["drawing"]
    fill = kit.Fill("solid", d["base"], d["accent"], d["third"])
    return kit.render(d["shape"], fill, d.get("label"), params=d.get("params"))


@pytest.fixture(scope="module")
def yogurt(rows) -> str:
    tubs = (r for r in rows if r["product_type"] == "Yogurt" and r["drawing"]["shape"] == "tub")
    return _svg(next(tubs))


def _path_points(svg: str, part: str) -> list[tuple[float, float]]:
    """The move, line and arc end points of the ``class=part`` path."""
    d = re.search(rf'<path d="([^"]+)"[^>]*class="{part}"', svg)
    assert d, f"no {part} path"
    points = []
    for cmd in re.findall(r"[MLA][^MLAZ]*", d.group(1)):
        nums = [float(n) for n in NUMBER.findall(cmd)]
        points.append((nums[-2], nums[-1]))
    return points


def test_hot_chocolate_is_drawn_as_a_tin_or_a_jar(rows) -> None:
    wrong = [
        (r["product_id"], r["drawing"]["shape"])
        for r in rows
        if r["product_type"] == "Hot Chocolate" and r["drawing"]["shape"] not in {"tin", "jar"}
    ]
    assert wrong == []


def test_no_two_products_of_one_brand_share_a_picture_in_the_hot_chocolate_leaf(rows) -> None:
    pictures = collections.defaultdict(list)
    for r in rows:
        if r["product_type"] == "Hot Chocolate":
            key = (r["category_leaf"], r["brand"], json.dumps(r["drawing"], sort_keys=True))
            pictures[key].append(r["product_id"])
    assert [ids for ids in pictures.values() if len(ids) > 1] == []


def test_the_yogurt_tub_has_a_lid_with_a_rim(yogurt: str) -> None:
    assert 'class="lid"' in yogurt
    assert 'class="lid-rim"' in yogurt
    assert yogurt.count('class="pot"') == 1


def test_the_yogurt_tub_is_wider_than_it_is_tall_with_a_slightly_flared_wall(yogurt: str) -> None:
    (x0, top), (x1, _), (x2, foot), (x3, _) = _path_points(yogurt, "pot")
    assert x1 - x0 > foot - top, "a tub is short and wide, not a tall cup"
    assert x0 < x3 and x1 > x2, "the wall flares out toward the lid"
    assert (x2 - x3) / (x1 - x0) >= 0.85, "only slightly: a cup tapers far more"


def test_the_yogurt_tub_is_not_the_old_cup(yogurt: str) -> None:
    assert OLD_CUP not in yogurt


def test_the_tub_is_not_the_grocery_lidded_tub() -> None:
    fill = kit.Fill("solid", "#e9eef4", "#2a2a2e")
    assert kit.render("tub", fill, "Yogurt") != kit.render("lidded_tub", fill, "Yogurt")
