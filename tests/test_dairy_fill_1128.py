"""Milk is drawn as a jug and plant milk as a gable-top carton, filling their picture (gen#1128).

Before gen#1128 every milk (GRC-MLK) and plant milk (GRC-PLM) SKU drew the kit's generic
``carton``, painted in its line's first flavor, and ``pack_scale`` shrank a 1 pint to 0.63 and a
2 pint to 0.79: they covered 0.19 and 0.30 of the product area. A Semi Skimmed SKU of a line whose
first flavor is Whole drew blue. Milk is now a translucent jug of white milk with a cap in its
fat level's color, the SKU's own (whole blue, semi skimmed green, skimmed red, as UK shelves
code it). The 1, 2 and 4 pint jugs are drawn in their own proportions, the larger jug wider. A
plant milk is a gable-top carton. Both carry a gloss and stand on a ground shadow, and neither
takes a ``pack_scale`` factor.

Fill is measured as gen#1111 measures it: the share of the plain sheet's product area
(``TURN_AREA``) that the pack (``<g class="dairy">``) paints in ``image_release.render``'s own
SVG. The ground shadow does not count.
"""

from __future__ import annotations

import functools
import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    grocery,
    image_release,
    pack_scale,
    sheet_cover,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA

FLOOR = 0.5
#: Over this, the pack no longer sits framed with paper round it (the issue asks 60-70%).
CEILING = 0.8
FAMILIES = ("MLK", "PLM")
DRAWN = ("path", "rect", "circle", "ellipse")
#: The channel that leads in each fat level's cap: blue, green, red (and Lactose Free purple).
CAP_LEAD = {"Whole": "b", "Semi Skimmed": "g", "Skimmed": "r", "Lactose Free": "rb"}


@functools.cache
def _records() -> dict[str, list[dict]]:
    """Every milk and plant milk product of the 10K grocery build, by family."""
    out: dict[str, list[dict]] = {code: [] for code in FAMILIES}
    for rec in grocery.build():
        code = rec["product_id"].split("-")[1]
        if code in out:
            out[code].append(rec)
    assert all(out.values()), {k: len(v) for k, v in out.items()}
    return out


@functools.cache
def _served(pid: str, sku_id: str) -> str:
    rec = next(r for recs in _records().values() for r in recs if r["product_id"] == pid)
    sku = next(s for s in rec["skus"] if s["sku"] == sku_id)
    return image_release.render(rec, sku, styled=False).decode()


def _skus(code: str) -> list[tuple[dict, dict]]:
    return [(rec, sku) for rec in _records()[code] for sku in rec["skus"]]


def _pack_only(svg: str) -> str:
    """``svg`` with every painted shape outside the ``dairy`` group made invisible."""
    root = ET.fromstring(svg)

    def hide(el: ET.Element, inside: bool) -> None:
        inside = inside or el.get("class") == "dairy"
        if not inside and el.tag.rsplit("}", 1)[-1] in DRAWN:
            el.set("opacity", "0")
        for child in el:
            hide(child, inside)

    hide(root, False)
    return ET.tostring(root, encoding="unicode")


def _fill(svg: str) -> float:
    return sheet_cover.cover(_pack_only(svg), TURN_AREA, step=4.0, skip=("ground",))


def _width(svg: str) -> float:
    group = re.search(r'<g class="dairy">.*?</g>', svg)
    assert group, "no dairy group"
    box = sheet_extent.reach(f'<svg xmlns="http://www.w3.org/2000/svg">{group.group(0)}</svg>')
    assert box is not None
    return box[2] - box[0]


@pytest.mark.parametrize("code", FAMILIES)
def test_every_milk_and_plant_milk_sku_fills_half_its_product_area(code: str) -> None:
    fills = {sku["sku"]: _fill(_served(rec["product_id"], sku["sku"])) for rec, sku in _skus(code)}
    low = {k: round(v, 3) for k, v in fills.items() if v < FLOOR}
    high = {k: round(v, 3) for k, v in fills.items() if v > CEILING}
    assert not low, f"{len(low)} {code} SKUs under {FLOOR}: {dict(list(low.items())[:5])}"
    assert not high, f"{len(high)} {code} SKUs over {CEILING}: {dict(list(high.items())[:5])}"


@pytest.mark.parametrize("code", FAMILIES)
def test_no_milk_pack_is_shrunk_by_pack_scale(code: str) -> None:
    shrunk = [sku["sku"] for rec, sku in _skus(code) if pack_scale.factor(rec, sku) is not None]
    assert not shrunk, shrunk[:5]


def _rgb(hex_: str) -> dict[str, int]:
    return dict(zip("rgb", (int(hex_[i : i + 2], 16) for i in (1, 3, 5)), strict=True))


def _caps(svg: str) -> list[str]:
    return re.findall(r'class="cap"[^>]*fill="(#[0-9a-f]{6})"', svg)


def test_a_milk_jug_cap_is_the_color_of_its_skus_fat_level() -> None:
    seen: set[str] = set()
    for rec, sku in _skus("MLK"):
        svg = _served(rec["product_id"], sku["sku"])
        caps = _caps(svg)
        assert len(caps) == 1, (sku["sku"], caps)
        c, lead = _rgb(caps[0]), CAP_LEAD[sku["flavor"]]
        others = [c[k] for k in "rgb" if k not in lead]
        assert min(c[k] for k in lead) > max(others) + 40, (sku["sku"], sku["flavor"], caps[0])
        seen.add(sku["flavor"])
    assert {"Whole", "Semi Skimmed", "Skimmed"} <= seen


def test_each_sku_of_a_mixed_line_draws_its_own_fat_level() -> None:
    """A line of Whole and Semi Skimmed draws a blue cap on its Whole SKUs and a green one on its
    Semi Skimmed, not its first flavor's on all of them."""
    mixed = [rec for rec in _records()["MLK"] if len({s["flavor"] for s in rec["skus"]}) > 1]
    assert mixed
    for rec in mixed:
        pid = rec["product_id"]
        caps = {sku["flavor"]: _caps(_served(pid, sku["sku"])) for sku in rec["skus"]}
        assert all(len(c) == 1 for c in caps.values()), (pid, caps)
        assert len({c[0] for c in caps.values()}) == len(caps), (pid, caps)


@pytest.mark.parametrize("code", FAMILIES)
def test_a_larger_pack_of_a_line_draws_a_wider_pack(code: str) -> None:
    lines = 0
    for rec in _records()[code]:
        flavor = rec["skus"][0]["flavor"]
        by_ml = sorted((s["net_volume_ml"], s["sku"]) for s in rec["skus"] if s["flavor"] == flavor)
        if len(by_ml) < 2:
            continue
        widths = [_width(_served(rec["product_id"], sku)) for _, sku in by_ml]
        assert widths == sorted(widths) and len(set(widths)) == len(widths), (by_ml, widths)
        lines += 1
    assert lines, f"no {code} line sells two sizes of one flavor"


@pytest.mark.parametrize("code", FAMILIES)
def test_every_milk_pack_has_a_gloss_and_stands_on_a_ground_shadow(code: str) -> None:
    for rec in _records()[code][:5]:
        sku = rec["skus"][0]
        svg = _served(rec["product_id"], sku["sku"])
        assert 'class="ground"' in svg, sku["sku"]
        assert 'class="gloss"' in svg, sku["sku"]


def test_a_milk_jug_shows_white_milk_through_its_plastic() -> None:
    rec, sku = _skus("MLK")[0]
    svg = _served(rec["product_id"], sku["sku"])
    milk = re.findall(r'class="milk"[^>]*fill="(#[0-9a-f]{6})"', svg)
    assert milk and min(_rgb(milk[0]).values()) >= 0xF0, milk
    plastic = re.findall(r'class="jug"[^>]*fill-opacity="([.0-9]+)"', svg)
    assert plastic and float(plastic[0]) < 1, "the jug's plastic is translucent over the milk"
