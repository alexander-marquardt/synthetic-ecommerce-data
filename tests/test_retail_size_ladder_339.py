"""Clothing and footwear are drawn once per size, scaled by its place in the ladder (gen#339).

A product's sizes used to share one drawing per colour. Now a clothing or footwear product with
more than one size draws each rung at its own scale, from ``size_ladder.BOTTOM`` (the smallest) to
``size_ladder.TOP`` (the largest), symbolic and not true to dimension. The ladder is the product's
own; a two-dimensional size ranks by its first dimension and a fit that is not bigger or smaller
changes nothing; bedding and pack sizes keep one image per colour.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402 -- the prototype's own directory is its import root
import footwear_rows  # noqa: E402
import image_release  # noqa: E402
import sheet_extent  # noqa: E402
import size_ladder  # noqa: E402

BY_ID = {r["product_id"]: r for r in image_release.records()}


def _scale(rec: dict, sku: dict) -> float | None:
    return image_release.colorway_drawing(rec, sku).get("size_scale")


def _rung(sku: dict, key: str) -> str:
    """The rung a SKU stands on: its size, or for a bra its band whichever the cup."""
    size = sku[key]
    band = re.fullmatch(r"(\d+)[A-Z]+", size)
    return band.group(1) if band else size


def _by_rung(rec: dict, key: str) -> dict[str, set]:
    """``rung -> the set of scales its SKUs are drawn at`` (one value each when the rung is one)."""
    out: dict[str, set] = {}
    for sku in rec["skus"]:
        out.setdefault(_rung(sku, key), set()).add(_scale(rec, sku))
    return out


def _ids(rec: dict, key: str) -> dict[tuple, set]:
    """``(rung, colour) -> the image ids of its SKUs``."""
    out: dict[tuple, set] = {}
    for sku in rec["skus"]:
        out.setdefault((_rung(sku, key), sku.get("color")), set()).add(export.image_id(rec, sku))
    return out


#: ``(product, the key that names the size, its ladder smallest first)``: one product per kind of
#: ladder, the ladder written out here and not read back from the code under test.
LADDERS = [
    pytest.param("PLT-TEEW5", "size", ["XS", "S", "M", "L", "XL"], id="letter-top"),
    pytest.param("PLT-WIDTRS", "waist", ["6", "8", "10", "12", "14", "16", "18", "20", "22", "24"],
                 id="numeric-garment"),
    pytest.param("PLT-TEEK3", "size", ["3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs"], id="kids-age"),
    pytest.param("PLT-CUPBAL", "size", ["32", "34", "36", "38"], id="bra-band"),
    pytest.param("FTW-KSCHLL", "size_uk", None, id="footwear-kids-chart"),
    pytest.param("FTW-WTRCNV", "size_uk", None, id="footwear-womens-chart"),
]  # fmt: skip


def _ladder(rec: dict, ladder: list[str] | None) -> list[str]:
    """The ladder as the test knows it: written out, or a footwear chart's own row order."""
    if ladder is not None:
        return ladder
    chart = footwear_rows.KIDS if rec["product_id"] == "FTW-KSCHLL" else footwear_rows.WOMEN
    return [uk for uk in chart if uk in {s["size_uk"] for s in rec["skus"]}]


@pytest.mark.parametrize(("pid", "key", "ladder"), LADDERS)
def test_the_drawing_scale_strictly_increases_with_size_rank(pid, key, ladder):
    rec = BY_ID[pid]
    by_rung = _by_rung(rec, key)
    sizes = _ladder(rec, ladder)
    assert set(sizes) == set(by_rung), "the ladder written here is the product's"
    scales = []
    for rung in sizes:
        assert len(by_rung[rung]) == 1, f"{pid} {rung} is drawn at {by_rung[rung]}"
        scales.append(next(iter(by_rung[rung])))
    assert None not in scales, f"{pid} has an unscaled size"
    assert scales == sorted(set(scales)), f"{pid} scales do not strictly increase: {scales}"
    assert scales[0] == size_ladder.BOTTOM
    assert scales[-1] == size_ladder.TOP


def test_a_two_dimensional_size_scales_by_its_primary_dimension_only():
    bra = BY_ID["PLT-CUPBAL"]
    assert {len(v) for v in _by_rung(bra, "size").values()} == {1}  # a band: one scale, any cup
    ids = _ids(bra, "size")
    assert {len(v) for v in ids.values()} == {1}, "the cups of one band should share one image"
    colour = bra["skus"][0].get("color")
    bands = {band for (band, c) in ids if c == colour}
    assert len(bands) == 4
    assert len({next(iter(v)) for (_, c), v in ids.items() if c == colour}) == 4
    trousers = BY_ID["PLT-WIDTRS"]
    legs = _ids(trousers, "waist")
    assert {len(v) for v in legs.values()} == {1}, "a waist's legs should share one image"
    assert len({next(iter(v)) for v in legs.values()}) == len(legs)


def test_a_fit_only_difference_keeps_the_shared_per_colour_image():
    trousers = BY_ID["PLT-WIDTRS"]
    legs = [s for s in trousers["skus"] if s["waist"] == "10"]
    one_size = trousers | {"skus": legs}
    assert len({s["inside_leg"] for s in legs}) > 1
    assert {_scale(one_size, s) for s in legs} == {None}
    per_colour: dict = {}
    for s in legs:
        per_colour.setdefault(s.get("color"), set()).add(export.image_id(one_size, s))
    assert {len(v) for v in per_colour.values()} == {1}


@pytest.mark.parametrize("pid", ["BED-DUVHOL", "PLT-MTTMEM", "GFT-KRAFT"])
def test_bedding_and_pack_sizes_keep_one_image_per_colour(pid):
    rec = BY_ID[pid]
    per_colour: dict = {}
    for sku in rec["skus"]:
        assert _scale(rec, sku) is None
        per_colour.setdefault(sku.get("color"), set()).add(export.image_id(rec, sku))
    assert len({s.get("size") or s.get("bed_size") or s.get("size_uk") for s in rec["skus"]}) > 1
    assert {len(v) for v in per_colour.values()} == {1}


def test_each_size_of_a_colour_has_its_own_image():
    rec = next(r for r in BY_ID.values() if r["product_type"] == "Tee"
               and {s.get("size") for s in r["skus"]} >= {"XS", "S", "M", "L", "XL"}
               and len({s.get("color") for s in r["skus"]}) > 1)  # fmt: skip
    by_colour: dict = {}
    for sku in rec["skus"]:
        by_colour.setdefault(sku["color"], []).append(export.image_id(rec, sku))
    assert len(by_colour) > 1
    for colour, ids in by_colour.items():
        assert len(ids) == len(set(ids)) == 5, f"{colour}: one image per size"
    every = [i for ids in by_colour.values() for i in ids]
    assert len(every) == len(set(every)), "no image is shared between colours"


def _anchor(svg: bytes) -> tuple[float, float, float] | None:
    found = re.search(
        rb'<g class="size" transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([\d.]+)\)', svg
    )
    return None if found is None else tuple(float(g) for g in found.groups())  # type: ignore[return-value]


def test_a_ladder_stands_on_one_floor_and_the_largest_is_the_drawing_as_it_was():
    rec = BY_ID["PLT-TEEW5"]
    colour = rec["skus"][0]["color"]
    skus = [s for s in rec["skus"] if s["color"] == colour]
    for styled in (False, True):
        svgs = [image_release.render(rec, s, styled=styled) for s in skus]
        anchors = [_anchor(svg) for svg in svgs]
        assert anchors[-1] is None, "the largest rung is not wrapped"
        assert None not in anchors[:-1]
        assert len({a[:2] for a in anchors[:-1]}) == 1, "the rungs share one bottom centre"
        ratios = [a[2] for a in anchors[:-1]]
        assert ratios == sorted(set(ratios))
        assert ratios[0] == pytest.approx(size_ladder.BOTTOM / size_ladder.TOP, abs=1e-3)
        bare = {k: v for k, v in image_release.colorway_drawing(rec, skus[-1]).items()
                if k != "size_scale"}  # fmt: skip
        from build_preview import drawing_svg  # noqa: PLC0415

        assert svgs[-1] == drawing_svg(rec | {"drawing": bare}, styled).encode()


def test_stand_scales_a_body_about_its_bottom_centre():
    body = '<rect x="100" y="50" width="200" height="300" fill="#000"/>'
    scaled = size_ladder.stand(body, "", 0.45)
    box = sheet_extent.reach(f'<svg xmlns="http://www.w3.org/2000/svg">{scaled}</svg>')
    assert box is not None
    x0, y0, x1, y1 = box
    ratio = 0.45 / size_ladder.TOP
    assert (x0 + x1) / 2 == pytest.approx(200)
    assert y1 == pytest.approx(350)
    assert x1 - x0 == pytest.approx(200 * ratio)
    assert y1 - y0 == pytest.approx(300 * ratio)
    assert size_ladder.stand(body, "", None) == body
    assert size_ladder.stand(body, "", size_ladder.TOP) == body


def test_every_scaled_rung_stays_on_the_sheet():
    """Scaling about the bottom centre only pulls a drawing in: no rung leaves the sheet."""
    for pid in ("PLT-TEEW5", "FTW-KSCHLL", "PLT-CUPBAL"):
        rec = BY_ID[pid]
        for sku in rec["skus"]:
            svg = image_release.render(rec, sku, styled=False)
            assert sheet_extent.overrun(svg, 400.0) == 0.0, f"{pid} {sku['sku']}"
