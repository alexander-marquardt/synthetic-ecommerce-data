"""A pack is drawn smaller when its line sells a smaller size of it (gen#543).

Within one line a 30 ml jar and a 100 ml jar were one drawing, so a shopper could not see the
size at a glance. The pack now scales by about the cube root of its content against the line's
largest size (how real packs grow), floored so a small size stays legible, on the same 400 x 400
canvas and the same baseline. The bounding box of the rendered pack is the measure.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from functools import cache
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import image_release  # noqa: E402
import pack_scale  # noqa: E402
import pack_scale_strip  # noqa: E402
import scale  # noqa: E402
import sheet_extent  # noqa: E402
from build_preview import drawing_svg  # noqa: E402

STRIP = Path(__file__).resolve().parent.parent / "docs" / "images" / "pack-scale.svg"

SVG = "{http://www.w3.org/2000/svg}"
#: A measured height may differ from the rule by this share: the shapes' own curves and strokes.
TOLERANCE = 0.03


@cache
def line_30_50_100() -> dict:
    """An authored line that sells 30, 50 and 100 ml of one pack."""
    return next(
        r
        for r in scale.templates()
        if r["drawing"]["shape"] == "aftershave"
        and {float(s["net_volume_ml"]) for s in r["skus"]} == {30.0, 50.0, 100.0}
    )


def _sku(rec: dict, ml: float) -> dict:
    return next(s for s in rec["skus"] if float(s["net_volume_ml"]) == ml)


def _pack_box(rec: dict, sku: dict) -> tuple[float, float, float, float]:
    """The bounding box of the rendered pack alone: the plain sheet's paper, frame and brand
    tag are taken off the SVG that ``image_release.render`` writes."""
    root = ET.fromstring(image_release.render(rec | {"brand": ""}, sku, styled=False))
    for el in list(root):
        if el.tag == f"{SVG}rect" and (el.get("width") == "400" or el.get("x") == "6"):
            root.remove(el)
    box = sheet_extent.reach(ET.tostring(root))
    assert box is not None
    return box


def _height(rec: dict, sku: dict) -> float:
    _, y0, _, y1 = _pack_box(rec, sku)
    return y1 - y0


@pytest.mark.parametrize("ml", [30.0, 50.0])
def test_a_smaller_size_is_drawn_at_the_cube_root_of_its_volume_ratio(ml: float) -> None:
    rec = line_30_50_100()
    ratio = _height(rec, _sku(rec, ml)) / _height(rec, _sku(rec, 100.0))
    assert ratio == pytest.approx((ml / 100.0) ** (1 / 3), rel=TOLERANCE)


def test_the_30_ml_pack_is_visibly_smaller_than_the_100_ml_pack() -> None:
    rec = line_30_50_100()
    assert _height(rec, _sku(rec, 30.0)) < 0.75 * _height(rec, _sku(rec, 100.0))


def test_the_largest_size_is_the_drawing_unchanged() -> None:
    rec = line_30_50_100()
    for styled in (True, False):
        assert (
            image_release.render(rec, _sku(rec, 100.0), styled) == drawing_svg(rec, styled).encode()
        )


def test_the_packs_stand_on_one_baseline_and_one_center_line() -> None:
    rec = line_30_50_100()
    boxes = [_pack_box(rec, _sku(rec, ml)) for ml in (30.0, 50.0, 100.0)]
    bottoms = {round(b[3], 1) for b in boxes}
    centers = {round((b[0] + b[2]) / 2, 1) for b in boxes}
    assert len(bottoms) == len(centers) == 1


@pytest.mark.parametrize("styled", [True, False])
def test_the_canvas_is_unchanged(styled: bool) -> None:
    rec = line_30_50_100()
    for ml in (30.0, 50.0, 100.0):
        root = ET.fromstring(image_release.render(rec, _sku(rec, ml), styled=styled))
        assert (root.get("width"), root.get("height"), root.get("viewBox")) == (
            "400",
            "400",
            "0 0 400 400",
        )


def test_each_size_of_a_line_is_its_own_image() -> None:
    rec = line_30_50_100()
    ids = {export.image_id(rec, _sku(rec, ml)) for ml in (30.0, 50.0, 100.0)}
    assert len(ids) == 3


@pytest.mark.parametrize(
    ("ml", "want"), [(30.0, 0.669), (50.0, 0.794), (100.0, None)], ids=["30ml", "50ml", "100ml"]
)
def test_the_factor_is_the_cube_root_against_the_largest_size(
    ml: float, want: float | None
) -> None:
    rec = line_30_50_100()
    got = pack_scale.factor(rec, _sku(rec, ml))
    assert got == (pytest.approx(want, abs=0.001) if want else None)


def _line(*skus: dict, department: str = "Beauty") -> dict:
    return {"category_path": [department, "Any"], "skus": list(skus)}


def test_a_tiny_size_stops_at_the_floor() -> None:
    rec = _line({"net_volume_ml": 10}, {"net_volume_ml": 1000})
    assert pack_scale.factor(rec, rec["skus"][0]) == pack_scale.FLOOR


def test_a_line_of_one_size_is_not_scaled() -> None:
    rec = _line({"net_volume_ml": 50}, {"net_volume_ml": 50})
    assert pack_scale.factor(rec, rec["skus"][0]) is None


def test_a_weight_scales_like_a_volume() -> None:
    rec = _line({"net_weight_g": 100}, {"net_weight_g": 200}, department="Food & Drink")
    assert pack_scale.factor(rec, rec["skus"][0]) == pytest.approx(0.794, abs=0.001)


def test_a_count_scales_a_food_or_beauty_pack_and_never_a_garment() -> None:
    skus = [{"units_per_pack": 1}, {"units_per_pack": 8}]
    assert pack_scale.factor(_line(*skus, department="Food & Drink"), skus[0]) == pack_scale.FLOOR
    assert pack_scale.factor(_line(*skus, department="Womens"), skus[0]) is None


def test_a_total_content_wins_over_the_count() -> None:
    rec = _line(
        {"net_weight_g": 100, "units_per_pack": 1}, {"net_weight_g": 800, "units_per_pack": 8}
    )
    assert pack_scale.factor(rec, rec["skus"][0]) == pack_scale.FLOOR


def test_every_smaller_size_of_every_authored_line_renders_inside_its_sheet() -> None:
    """The sweep: each image a scaled SKU names is drawn once, carries the pack group, and stays
    on the sheet (a shrink about the bottom center can only pull a pack in)."""
    seen: set[str] = set()
    for rec in scale.templates():
        for sku in rec["skus"]:
            if pack_scale.factor(rec, sku) is None or (image := export.image_id(rec, sku)) in seen:
                continue
            seen.add(image)
            svg = image_release.render(rec, sku, styled=False)
            assert b'class="pack"' in svg, image
            assert sheet_extent.overrun(svg) == 0, image
    assert len(seen) > 1000


def _styled_pack_box(rec: dict, sku: dict) -> tuple[float, float, float, float]:
    """The bounding box of the pack in the STYLED render (the one the image release ships): the
    sheet's paper and the brand overlay are left out, only the ``product`` group is measured."""
    root = ET.fromstring(image_release.render(rec, sku, styled=True))
    only = ET.Element(root.tag, root.attrib)
    only.extend(el for el in root if el.tag == f"{SVG}defs" or el.get("class") == "product")
    box = sheet_extent.reach(ET.tostring(only))
    assert box is not None
    return box


@pytest.mark.parametrize("ml", [30.0, 50.0])
def test_the_styled_render_draws_a_smaller_size_smaller_on_the_same_canvas(ml: float) -> None:
    """The shipped drawings are the styled ones: a 30 ml and a 50 ml pack measure smaller than the
    100 ml pack at the cube-root rule, and the canvas is the same 400 x 400."""
    rec = line_30_50_100()
    small = _styled_pack_box(rec, _sku(rec, ml))
    big = _styled_pack_box(rec, _sku(rec, 100.0))
    want = pack_scale.factor(rec, _sku(rec, ml))
    assert want is not None and want < 1
    for lo, hi in ((0, 2), (1, 3)):  # width, then height
        got = (small[hi] - small[lo]) / (big[hi] - big[lo])
        assert got == pytest.approx(want, rel=TOLERANCE)
    assert small[3] == pytest.approx(big[3], abs=1.0)  # same baseline
    root = ET.fromstring(image_release.render(rec, _sku(rec, ml), styled=True))
    assert (root.get("width"), root.get("height"), root.get("viewBox")) == (
        "400",
        "400",
        "0 0 400 400",
    )


def _strip_facts(text: str) -> tuple[list[str], list[str]]:
    """What the strip states and applies, not the bytes of the whole sheets it embeds (those move
    with any sibling PR that touches the line's drawing): its captions and its pack scales."""
    captions = re.findall(r"<text [^>]*>([^<]*)</text>", text)
    scales = re.findall(r'class="pack" transform="translate\([^)]*\) scale\(([0-9.]+)\)"', text)
    return captions, scales


def test_the_docs_before_and_after_strip_states_the_scales_the_drawings_apply_now() -> None:
    """Compares the strip's captions and the scale factors it applies with a fresh strip's; a
    byte-exact comparison would red in the merge queue whenever a sibling PR moves the tree."""
    shipped = _strip_facts(STRIP.read_text(encoding="utf-8"))
    assert shipped == _strip_facts(pack_scale_strip.strip()), (
        "docs/images/pack-scale.svg is stale: uv run python prototypes/retail_drawings/"
        "pack_scale_strip.py --out docs/images/pack-scale.svg"
    )
