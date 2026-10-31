"""Each bike kind reads at thumbnail size, and each size is drawn at its own scale (gen#718).

The maintainer could tell the kinds apart only by looking hard, and a kids' bike with a stabilizer
in front of its rear wheel looked like a stationary trainer. So a mountain bike has larger wheels
with fat, knobbly tires and a sloping top tube, an electric bike has a thick down tube carrying a
large battery in a color that stands out from the frame, and a kids' bike has one stabilizer behind
the rear axle, on the same ground. A bicycle's sizes are on the shared size ladder, whole drawing
scaled, tires included.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    kit,
    kit_sports,
    scale,
    sheet_extent,
    size_ladder,
)

NS = "{http://www.w3.org/2000/svg}"
RED = "#c8312e"
#: The Mountain wheel, tire and hub of main: what "larger" and "fatter" are measured from.
OLD_MOUNTAIN_RADIUS, OLD_MOUNTAIN_TIRE = 68, 9
#: The battery of main, about 40 by 18 units: the new one is about twice that.
OLD_BATTERY_AREA = 40 * 18


def _root(style: str, color: str = RED) -> ET.Element:
    parts = kit_sports.bicycle(color, kit.Fill(base=color), None, style=style)
    return ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>')


def _classed(style: str, name: str, color: str = RED) -> list[ET.Element]:
    return [el for el in _root(style, color).iter() if el.get("class") == name]


def _width(el: ET.Element) -> float:
    return float(el.get("stroke-width", "0"))


def _tube(style: str, name: str) -> float:
    found = _classed(style, name)
    assert len(found) == 1, f"{style}: expected one {name}, found {len(found)}"
    return _width(found[0])


def _tires(style: str) -> list[ET.Element]:
    """The two main wheels: the widest unfilled circles, the tread and the stabilizer aside."""
    found = _classed(style, "tire")
    assert len(found) == 2, f"{style}: expected two tires, found {len(found)}"
    return found


def _luminance(color: str) -> float:
    def channel(i: int) -> float:
        c = int(color[i : i + 2], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5)


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _box(el: ET.Element) -> tuple[float, float, float, float]:
    svg = ET.Element(f"{NS}svg")
    svg.append(el)
    box = sheet_extent.reach(ET.tostring(svg))
    assert box is not None
    return box


def _bikes() -> dict[str, list[dict]]:
    found: dict[str, list[dict]] = {}
    for rec in scale.templates():
        if rec["product_type"] == "Bicycle":
            kind = next(a["value"] for a in rec["attributes"] if a["key"] == "bike_type")
            found.setdefault(kind, []).append(rec)
    return found


BIKES = _bikes()


def _bare_width(rec: dict, sku: dict) -> float:
    """The rendered bike across, on the plain sheet with no brand tag and the sheet rects off."""
    svg = image_release.render(rec | {"brand": ""}, sku, styled=False)
    root = ET.fromstring(svg)
    for rect in root.findall(f"{NS}rect")[:2]:
        root.remove(rect)
    box = sheet_extent.reach(ET.tostring(root))
    assert box is not None
    return box[2] - box[0]


# -- the kinds ----------------------------------------------------------------------------------


def test_the_mountain_tire_and_the_electric_down_tube_exceed_the_road_bikes():
    assert _width(_tires("mountain")[0]) > _width(_tires("road")[0])
    assert _tube("electric", "down-tube") > _tube("road", "down-tube")


def test_the_electric_down_tube_is_about_two_and_a_half_times_the_top_tube():
    assert _tube("electric", "down-tube") == pytest.approx(2.5 * _tube("electric", "top-tube"))
    assert _tube("road", "down-tube") == _tube("road", "top-tube")


def test_the_mountain_wheels_are_larger_fatter_and_clear_of_each_other():
    rear, front = _tires("mountain")
    radius, tire = float(rear.get("rx", "0")), _width(rear)
    assert radius >= OLD_MOUNTAIN_RADIUS + 8
    assert tire >= 2 * OLD_MOUNTAIN_TIRE
    apart = float(front.get("cx", "0")) - float(rear.get("cx", "0"))
    assert apart > 2 * (radius + tire / 2), "the wheels overlap"


def test_only_a_mountain_bike_has_a_knobbly_tread():
    tread = _classed("mountain", "tread")
    assert len(tread) == 2
    assert all(el.get("stroke-dasharray") for el in tread)
    for style in ("road", "electric", "kids"):
        assert _classed(style, "tread") == []


def test_a_mountain_top_tube_slopes_and_the_others_stay_about_level():
    def fall(style: str) -> float:
        found = _classed(style, "top-tube")
        assert len(found) == 1
        x0, y0, x1, y1 = _box(found[0])
        return y1 - y0

    assert fall("mountain") > 3 * fall("road")


@pytest.mark.parametrize("color", [c["hex"] for c in BIKES["Electric"][0]["color_options"]])
def test_the_battery_stands_out_from_every_electric_frame_color(color):
    found = _classed("electric", "battery", color)
    assert len(found) == 1
    assert _contrast(found[0].get("fill", "#000000"), color) >= 3.0


def test_the_battery_is_about_twice_as_large_as_it_was_and_sits_on_the_down_tube():
    battery = _classed("electric", "battery")
    tube = _classed("electric", "down-tube")
    assert len(battery) == 1 and len(tube) == 1
    bx0, by0, bx1, by1 = _box(battery[0])
    tx0, ty0, tx1, ty1 = _box(tube[0])
    assert (bx1 - bx0) * (by1 - by0) >= 2 * OLD_BATTERY_AREA
    assert (bx0 + bx1) / 2 == pytest.approx((tx0 + tx1) / 2, abs=3)
    assert (by0 + by1) / 2 == pytest.approx((ty0 + ty1) / 2, abs=3)


def test_the_battery_carries_a_bolt_in_the_frame_color():
    bolt = _classed("electric", "bolt")
    assert len(bolt) == 1 and bolt[0].get("fill") == RED


def test_the_electric_hub_motor_is_larger_than_it_was():
    hub = _classed("electric", "hub-motor")
    assert len(hub) == 1 and float(hub[0].get("rx", "0")) > 15


def test_a_kids_bike_has_one_stabilizer_behind_the_rear_axle_on_the_same_ground():
    wheels = _classed("kids", "stabilizer")
    assert len(wheels) == 1, "a side view shows one stabilizer, never one each side of the wheel"
    rear, _front = _tires("kids")
    axle, bottom = float(rear.get("cx", "0")), _box(rear)[3]
    x, *_ = _box(wheels[0])
    assert x < axle and float(wheels[0].get("cx", "0")) < axle, "the stabilizer is behind the axle"
    assert _box(wheels[0])[3] == pytest.approx(bottom, abs=1.0)


def test_a_road_bike_has_no_stabilizer_battery_or_hub_motor():
    for name in ("stabilizer", "battery", "bolt", "hub-motor"):
        assert _classed("road", name) == []


# -- the sizes ----------------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["Road", "Mountain", "Electric", "Kids"])
def test_a_bikes_sizes_step_up_the_shared_ladder(kind):
    rec = BIKES[kind][0]
    key = "wheel_size_in" if kind == "Kids" else "frame_cm"
    rungs = {sku[key]: export.drawing_spec(rec, sku).get("size_scale") for sku in rec["skus"]}
    ordered = [rungs[size] for size in sorted(rungs, key=int)]
    assert ordered == [size_ladder.BOTTOM, size_ladder.scale_at(1, 3), size_ladder.TOP]


@pytest.mark.parametrize("kind", ["Road", "Mountain", "Electric", "Kids"])
def test_the_largest_size_is_wider_than_the_smallest_by_the_ladders_ratio(kind):
    rec = BIKES[kind][0]
    color = rec["skus"][0]["color"]
    key = "wheel_size_in" if kind == "Kids" else "frame_cm"
    skus = sorted((s for s in rec["skus"] if s["color"] == color), key=lambda s: int(s[key]))
    ratio = _bare_width(rec, skus[-1]) / _bare_width(rec, skus[0])
    assert ratio == pytest.approx(size_ladder.TOP / size_ladder.BOTTOM, rel=0.05)


def test_every_size_of_a_color_draws_its_own_picture_and_stays_on_the_sheet():
    for recs in BIKES.values():
        rec = recs[0]
        assert len({export.drawing_id(rec, s) for s in rec["skus"]}) == len(rec["skus"])
        for sku in rec["skus"]:
            svg = image_release.render(rec, sku, styled=False)
            assert sheet_extent.overrun(svg, 400.0) == 0.0, sku["sku"]
