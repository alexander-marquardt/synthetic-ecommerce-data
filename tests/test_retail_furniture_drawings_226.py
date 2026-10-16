"""Furniture drawings tell the truth about colour and material (gen#226).

A White bookcase read grey (its back panel and cells were shaded 30% toward black), and a
glass-top or marble-effect dining table drew an opaque wood-grained top in the record colour:
its ``top_material`` could not be seen in the picture. The colour a SKU carries drives the
fill, and the top material is a drawing param that follows the attribute.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import furniture_rows  # noqa: E402
import image_release  # noqa: E402
import kit  # noqa: E402
import kit_furniture  # noqa: E402

CELL = 4  # raster step in sheet units
BASE = "#f2efe8"  # the catalog's White


def _rgb(c: str) -> tuple[float, float, float]:
    return tuple(int(c[i : i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def _lum(c: tuple[float, float, float]) -> float:
    return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255


def _boxes(svg: str):
    """``(x0, y0, x1, y1, fill, opacity)`` of every filled rect and straight-edged path, in
    document order (the painter's order). Curves are skipped: furniture bodies are slabs."""
    for m in re.finditer(r"<(rect|path)\b([^>]*)>", svg):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m[2]))
        fill = attrs.get("fill", "")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", fill):
            continue
        opacity = float(attrs.get("fill-opacity", 1))
        if m[1] == "rect":
            x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
            yield x, y, x + float(attrs["width"]), y + float(attrs["height"]), fill, opacity
        elif re.fullmatch(r"[ML\d.,\s\-Z]+", attrs.get("d", "?")):
            nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", attrs["d"])]
            xs, ys = nums[0::2], nums[1::2]
            yield min(xs), min(ys), max(xs), max(ys), fill, opacity


def _structure_luminances(svg: str) -> list[float]:
    """The luminance of each raster cell the furniture body paints (books, fabric boxes and
    the sheet itself left out), the painter's order resolved."""
    skip = {c.lower() for c in (*kit_furniture.BOOKS, "#d8c9a8", "#8a7a5a", kit_furniture.METAL)}
    cells: dict[tuple[int, int], tuple[float, float, float] | None] = {}
    sheet = True
    for x0, y0, x1, y1, fill, opacity in _boxes(svg):
        if sheet:  # the first box is the sheet itself
            sheet = False
            if x1 - x0 >= 390:
                continue
        for cx in range(int(x0 // CELL), int(x1 // CELL)):
            for cy in range(int(y0 // CELL), int(y1 // CELL)):
                if fill.lower() in skip:
                    cells[cx, cy] = None
                    continue
                below = cells.get((cx, cy)) or (255.0, 255.0, 255.0)
                top = _rgb(fill)
                mixed = [b + (t - b) * opacity for b, t in zip(below, top, strict=True)]
                cells[cx, cy] = (mixed[0], mixed[1], mixed[2])
    return [_lum(c) for c in cells.values() if c is not None]


def _furniture_docs() -> list[dict]:
    return furniture_rows.docs()


def test_a_white_furniture_drawing_reads_white() -> None:
    """Every furniture SKU in White draws mostly light: at least 80% of the body's painted area
    keeps 80% of the record White's own lightness (a back panel at 70% read as grey)."""
    white = _lum(_rgb(BASE))
    checked = 0
    bad: list[str] = []
    for doc in _furniture_docs():
        for sku in doc["skus"]:
            if sku["color"] != "White":
                continue
            svg = image_release.render(doc, sku, styled=False).decode()
            lums = _structure_luminances(svg)
            light = sum(1 for v in lums if v >= 0.8 * white) / len(lums)
            checked += 1
            if light < 0.8:
                bad.append(f"{sku['sku']} ({doc['drawing']['shape']}) {light:.0%} light")
            break  # one SKU per colorway is one image
    assert checked >= 8
    assert not bad, bad


def test_a_white_bookcase_of_every_style_reads_white() -> None:
    white = _lum(_rgb(BASE))
    fill = kit.Fill("solid", BASE, "#333333", "#f2d14b")
    for style, shelves in (("standard", "5"), ("cube", "4"), ("glass_door", "4"), ("ladder", "5")):
        svg = kit.render("bookcase", fill, params={"shelves": shelves, "style": style})
        lums = _structure_luminances(svg)
        light = sum(1 for v in lums if v >= 0.8 * white) / len(lums)
        assert light >= 0.8, (style, light)


def test_top_material_is_a_drawn_param_that_follows_the_attribute() -> None:
    """The picture is the data: a dining table's ``top`` param is its ``top_material``."""
    seen = 0
    for doc in _furniture_docs():
        if doc["drawing"]["shape"] != "dining_table":
            continue
        held = [a["value"] for a in doc["attributes"] if a["key"] == "top_material"]
        top = doc["drawing"]["params"].get("top")
        assert top is not None, doc["product_id"]
        assert top == held[0].lower().replace("-", "_"), doc["product_id"]
        seen += 1
    assert seen == len(furniture_rows.DINING)


def _table(top: str, outline: str = "oval", base: str = "#1b1b1b") -> str:
    fill = kit.Fill("solid", base, "#333333", "#f2d14b")
    params = {"outline": outline, "seats": "6", "extending": "no", "top": top}
    return kit.render("dining_table", fill, params=params)


def test_a_glass_top_is_drawn_translucent_glass_over_the_record_coloured_legs() -> None:
    svg = _table("glass")
    tops = re.findall(r'<path[^>]*class="top"[^>]*>', svg)
    assert len(tops) == 1
    assert f'fill="{kit_furniture.GLASS}"' in tops[0]
    assert re.search(r'fill-opacity="0?\.\d+"', tops[0])
    assert 'class="grain"' not in svg and 'class="vein"' not in svg
    assert svg.count('fill="#1b1b1b"') >= 2  # the legs keep the record colour


def test_a_marble_effect_top_has_veins_and_no_grain() -> None:
    for outline in ("rectangular", "oval", "round", "square"):
        svg = _table("marble_effect", outline, "#f2efe8")
        assert len(re.findall(r'class="vein"', svg)) >= 3, outline
        assert 'class="grain"' not in svg, outline
        top = re.findall(r'<path[^>]*class="top"[^>]*>', svg)[0]
        assert 'fill="#f2efe8"' in top, outline  # the stone is the record colour


def test_a_timber_top_keeps_its_grain() -> None:
    for top in ("oak", "walnut"):
        svg = _table(top, "rectangular", "#c9a06a")
        assert 'class="grain"' in svg and 'class="vein"' not in svg, top


def test_each_top_material_draws_differently() -> None:
    drawn = {top: _table(top) for top in ("oak", "walnut", "glass", "marble_effect")}
    assert drawn["glass"] != drawn["marble_effect"] != drawn["oak"]
    assert drawn["glass"] != drawn["oak"]


def test_an_unknown_top_material_is_refused() -> None:
    try:
        _table("plastic")
    except ValueError as e:
        assert "top" in str(e)
    else:
        raise AssertionError("an unknown top drew silently")
