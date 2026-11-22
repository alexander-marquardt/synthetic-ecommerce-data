"""The picture sweep measures fill and flatness the way gen#1111 does, on any kit (gen#1129).

``scripts/picture_fill_1129.py`` renders one SKU per product type and ranks the pictures worst
first. These tests hold its readers to fixed SVGs: an arc and a ``<use>`` copy count as paint,
the paper, a ground shadow and the brand band do not, and a drawing is flat when one solid color
paints most of it or it has no highlight and no shadow. One test reads the base kit's tin, whose
arcs ``sheet_cover`` alone refuses.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import kit, sheet_cover
from synthetic_ecommerce_data.domains.retail.build_preview import drawing_svg
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "picture_fill_1129", REPO / "scripts" / "picture_fill_1129.py"
)
pf = importlib.util.module_from_spec(_spec)
sys.modules["picture_fill_1129"] = pf
_spec.loader.exec_module(pf)

BASE = "#c0392b"
IMAGE = (0.0, 0.0, 400.0, 400.0)


def _svg(body: str, defs: str = "") -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">'
        f'<defs>{defs}</defs><rect width="400" height="400" fill="#fbfaf6"/>{body}</svg>'
    )


def test_an_arc_is_read_as_its_curve() -> None:
    circle = '<path d="M150,200 A50,50 0 1 0 250,200 A50,50 0 1 0 150,200 Z" fill="#c0392b"/>'
    assert pf.measure(_svg(circle), IMAGE).cover == pytest.approx(
        math.pi * 50**2 / 400**2, abs=0.003
    )


def test_each_use_copy_paints() -> None:
    defs = '<rect id="can" width="40" height="40" fill="#c0392b"/>'
    body = '<use href="#can" x="0" y="0"/><use href="#can" x="100" y="100"/>'
    assert pf.measure(_svg(body, defs), IMAGE).cover == pytest.approx(2 * 1600 / 160000, abs=0.002)


def test_the_paper_the_ground_and_the_brand_band_are_not_the_figure() -> None:
    body = (
        '<g class="product"><ellipse class="ground" cx="200" cy="380" rx="150" ry="20"/>'
        '<rect x="100" y="100" width="200" height="200" fill="#c0392b"/></g>'
        '<g class="brand"><rect width="400" height="100" fill="#123456"/></g>'
    )
    assert pf.measure(_svg(body), IMAGE, only="product").cover == pytest.approx(0.25, abs=0.002)
    assert pf.measure(_svg(body), IMAGE).cover == pytest.approx(0.5, abs=0.002)


def test_one_solid_color_is_flat() -> None:
    m = pf.measure(_svg('<rect x="100" y="100" width="200" height="200" fill="#c0392b"/>'), IMAGE)
    assert (m.solid, m.highlight, m.shadow, m.flat) == (1.0, False, False, True)


def test_a_kit_shade_over_half_the_figure_is_a_shadow_and_not_flat() -> None:
    body = (
        f'<rect x="100" y="100" width="100" height="200" fill="{BASE}"/>'
        f'<rect x="200" y="100" width="100" height="200" fill="{kit._shade(BASE)}"/>'
    )
    m = pf.measure(_svg(body), IMAGE)
    assert (m.solid, m.shadow, m.flat) == (0.5, True, False)


def test_a_gradient_is_a_highlight_and_a_shadow() -> None:
    defs = '<radialGradient id="gloss"><stop offset="0" stop-color="#fff"/></radialGradient>'
    m = pf.measure(_svg('<circle cx="200" cy="200" r="100" fill="url(#gloss)"/>', defs), IMAGE)
    assert (m.solid, m.highlight, m.shadow, m.flat) == (0.0, True, True, False)


@pytest.mark.parametrize(
    ("overlay", "reads"),
    [
        (
            '<rect x="100" y="100" width="120" height="200" fill="#ffffff" fill-opacity="0.3"/>',
            "highlight",
        ),
        (
            '<rect x="100" y="100" width="120" height="200" fill="#000000" fill-opacity="0.2"/>',
            "shadow",
        ),
        (
            '<path d="M120,120 L180,120" fill="none" stroke="#ffffff" stroke-opacity="0.6"/>',
            "highlight",
        ),
    ],
    ids=["white-overlay", "dark-overlay", "gloss-stroke"],
)
def test_a_translucent_overlay_or_gloss_stroke_is_shading(overlay: str, reads: str) -> None:
    body = f'<rect x="100" y="100" width="200" height="200" fill="{BASE}"/>{overlay}'
    m = pf.measure(_svg(body), IMAGE)
    assert getattr(m, reads)
    assert not m.flat or m.solid > pf.FLAT_SHARE


def test_a_tone_is_a_kit_shade_or_tint_of_a_color_not_two_greys() -> None:
    assert pf.tone(kit._shade(BASE), BASE) == "shade"
    assert pf.tone(kit._tint(BASE, 0.3), BASE) == "tint"
    assert pf.tone("#d9dde0", "#ffffff") is None  # a tin's grey lid on its white label
    assert pf.tone("#2b4a80", BASE) is None


def test_the_base_kit_tin_is_read_through_its_arcs() -> None:
    rec = {
        "product_id": "GRC-TIN-T",
        "brand": "Test",
        "drawing": {"shape": "tin", "pattern": "solid", "base": "#f2c14e", "accent": "#333333",
                    "third": "#ffffff", "label": "Beans"},
    }  # fmt: skip
    with pytest.raises(ValueError, match="'A'"):
        sheet_cover.cover(drawing_svg(rec, styled=False), TURN_AREA)
    m = pf.measure(drawing_svg(rec, styled=False), TURN_AREA)
    assert 0.3 < m.cover < 0.6, m  # the full-size tin, about 40% in gen#1111's sample
    assert m.flat


def test_the_packs_drawn_are_the_most_common_then_the_largest_and_smallest() -> None:
    one, four, twelve = (("pack_count", 1),), (("pack_count", 4),), (("pack_count", 12),)
    keys = [four, one, four, twelve, four, one]
    assert pf.chosen_packs(keys) == [("common", four), ("largest", twelve), ("smallest", one)]
    assert pf.chosen_packs([(), ()]) == [("common", ())]
    assert pf.pack_size((("pack_size", "6 x 330ml"), ("pack_scale", 0.5))) == pytest.approx(3.0)


def test_drawn_to_scale_is_a_dimension_the_kit_code_reads() -> None:
    source = 'def lampshade(...):\n    d = float(params["diameter_cm"])\n'
    assert pf.scaled_keys({"diameter_cm", "finish"}, source) == ["diameter_cm"]
    assert pf.scaled_keys({"length_mm"}, source) == []  # a SKU attribute the drawing ignores
    assert pf.scaled_keys({"pack_size"}, 'params["pack_size"]') == []  # a pack, not a dimension


def _render(kit_name: str, ptype: str, role: str, area: float, flat: bool = True) -> dict:
    return {"kit": kit_name, "type": ptype, "shape": ptype.lower(), "role": role, "area": area,
            "whole": area / 2, "flat": flat, "empty": area < pf.EMPTY_FLOOR, "scale": [],
            "in_scope": True, "sku": f"{ptype}-{role}"}  # fmt: skip


def test_the_tables_rank_worst_first_from_the_common_pack() -> None:
    renders = [
        _render("kit_a", "Tin", "common", 0.20),
        _render("kit_a", "Tin", "largest", 0.80),
        _render("kit_a", "Jar", "common", 0.50, flat=False),
        _render("kit_b", "Bag", "common", 0.10),
    ]
    served = {("Tin", "tin"): 300, ("Jar", "jar"): 100, ("Bag", "bag"): 5}
    types = pf.type_rows(renders, served)
    assert [(r["type"], r["area"], r["area_max"], r["empty"]) for r in types] == [
        ("Bag", 0.10, 0.10, True), ("Tin", 0.20, 0.80, True), ("Jar", 0.50, 0.50, False)
    ]  # fmt: skip
    kits = pf.kit_rows(types)
    assert [(r["kit"], r["skus"], r["area"], r["flat"], r["empty"]) for r in kits] == [
        ("kit_b", 5, 0.10, True, True), ("kit_a", 400, 0.35, False, False)
    ]  # fmt: skip
    header = pf.type_table(types).splitlines()[0]
    assert "drawn to scale" in header and "in scope" in header and "SKUs served" in header
    assert "| 1 | `kit_b` | Bag |" in pf.type_table(types)
    assert "| 1 | `kit_b` |" in pf.kit_table(kits, ["kit_unused"])
    assert "`kit_unused`" in pf.kit_table(kits, ["kit_unused"])


def test_the_render_cost_gives_the_median_p95_and_the_wall_time() -> None:
    spent = pf.cost([0.001] * 19 + [0.021], skus=500_000, vcpus=32)
    assert spent["median_s"] == pytest.approx(0.001)
    assert spent["p95_s"] == pytest.approx(0.001)
    assert spent["wall_s"] == pytest.approx(0.002 * 500_000 / 32)
