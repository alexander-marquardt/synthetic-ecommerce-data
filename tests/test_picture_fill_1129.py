"""The picture sweep measures fill and flatness the way gen#1111 does, on any kit (gen#1129).

``scripts/picture_fill_1129.py`` renders one SKU per product type and ranks the pictures worst
first. These tests hold its readers to fixed SVGs: an arc and a ``<use>`` copy count as paint,
the paper, a ground shadow and the brand band do not, and a drawing is flat when one solid color
paints most of it or it has no highlight and no shadow. One test reads the base kit's tin, whose
arcs ``sheet_cover`` alone refuses. The industrial rows (slice 2) read a 200 x 300 sheet without
its brand plate, and call a type drawn to scale when its figure draws to a length it publishes.
"""

from __future__ import annotations

import importlib.util
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

import pytest

from synthetic_ecommerce_data.core import domain
from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
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
    assert pf.pack_size((("pack_size", "6 x 330ml"), ("pack_scale", 0.5))) == pytest.approx(990)
    assert pf.pack_size((("pack_size", "1L"),)) > pf.pack_size((("pack_size", "500ml"),))


def test_drawn_to_scale_is_a_dimension_the_kit_code_reads() -> None:
    source = 'def lampshade(...):\n    d = float(params["diameter_cm"])\n    pack_size.split()\n'
    assert pf.scaled_keys({"diameter_cm": {"30"}, "finish": {"brass"}}, source) == ["diameter_cm"]
    assert pf.scaled_keys({"length_mm": {"40"}}, source) == []  # an attribute the drawing ignores
    assert pf.scaled_keys({"pack_size": {"12 inch", "10 inch"}}, source) == ["pack_size"]  # pizza
    assert pf.scaled_keys({"pack_size": {"6 x 330ml", "1L"}}, source) == []  # a pack, not a length


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


# --- the industrial rows (slice 2) ----------------------------------------------------------


def _sheet(body: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="300" viewBox="0 0 200 300">'
        f'<rect width="200" height="300" fill="#ffffff"/>{body}</svg>'
    )


def test_an_industrial_sheet_counts_its_figure_not_the_paper_a_hole_or_the_plate() -> None:
    body = (
        '<rect x="6" y="6" width="188" height="288" rx="14" fill="none" stroke="#1b2a6b"/>'
        '<path d="M50 50L150 50L150 150L50 150Z" fill="#e7ecef" stroke="#1b2a6b"/>'
        '<path d="M90 90L110 90L110 110L90 110Z" fill="#ffffff"/>'  # a hole, in the paper's color
        '<path d="M14 240L46 240L46 272L14 272Z" fill="#1b2a6b"/>'  # the brand plate's mark
    )
    whole, area = pf.sheet_measures(_sheet(body))
    assert whole == pytest.approx((10000 - 400) / (200 * 300), abs=0.003)
    assert area.cover == pytest.approx((10000 - 400) / (164 * 200), abs=0.004)
    assert area.flat  # one solid grey, no highlight, no shadow


def test_a_length_is_made_longer_and_anything_else_is_not() -> None:
    assert parse_length(pf.lengthened('1/4"')).inches == pytest.approx(0.375)
    assert parse_length(pf.lengthened("10 mm")).inches == pytest.approx(15 / 25.4, abs=1e-4)
    for value in ("9", "1.50mm, 2mm, 2.50mm", "Steel", "1/4-20"):
        assert pf.lengthened(value) is None, value


def _figure_of(*read: str, refuse_over: float | None = None):
    """A figure function that draws a bar as long as each named length it reads."""

    def fn(record: dict) -> SimpleNamespace:
        fig, source = Figure(size_in=1.0), "record"
        for name in read:
            inches = parse_length(record[name]).inches
            if refuse_over is not None and inches > refuse_over:
                inches, source = 1.0, "nominal"
            fig.poly([(0, 0), (inches, 0), (inches, 0.1)])
        return SimpleNamespace(figure=fig, source=source)

    return fn


def test_drawn_to_scale_is_a_published_length_the_figure_draws_to() -> None:
    record = {"Length": '2"', "Face Dia.": "25 mm", "Material": "Steel", "Piece Count": "9"}
    assert pf.drawn_to_scale(_figure_of("Length"), record) == ["Length"]
    assert pf.drawn_to_scale(_figure_of("Length", "Face Dia."), record) == ["Face Dia.", "Length"]
    assert pf.drawn_to_scale(_figure_of(), record) == []  # it reads no length: a fixed picture
    # a longer value it refuses and draws nominal instead is not a length it draws to
    assert pf.drawn_to_scale(_figure_of("Length", refuse_over=2.5), record) == []


def test_the_assortment_kit_figure_draws_to_no_length() -> None:
    fn, _ = domain.figure("kit_assortment")
    record = {"Type": "Hex Key Set", "Finish": "Chrome Plated", "Container Type": "Folding Holder",
              "Tip Style": "Ball End", "Piece Count": "9",
              "Sizes Included": "1.50mm, 2mm, 2.50mm, 3mm, 4mm, 5mm, 6mm, 8mm, 10mm"}  # fmt: skip
    assert pf.drawn_to_scale(fn, record) == []
    assert pf.figure_kit(fn, "kit_assortment") == ("industrial/case_figures", "kit")


def test_a_drawn_to_scale_type_is_out_of_scope_unless_the_maintainer_names_its_kind() -> None:
    assert pf.in_scope("washer_flat", ["Outside Dia."]) == (False, pf.OUT_OF_SCOPE)
    assert pf.in_scope("kit_assortment", []) == (True, "yes")
    assert pf.in_scope("hammer_claw", ["Overall Length"]) == (True, pf.NAMED_NOTE)


def test_a_kit_holding_both_kinds_is_split_and_the_contact_sheet_skips_the_scaled() -> None:
    renders = [
        {**_render("industrial/figures", "washer_flat", "common", 0.05), "scale": ["Thickness"],
         "in_scope": False, "note": pf.OUT_OF_SCOPE, "domain": "industrial"},
        {**_render("industrial/figures", "kit_assortment", "common", 0.21), "note": "yes",
         "domain": "industrial"},
    ]  # fmt: skip
    served = {("washer_flat", "washer_flat"): 40, ("kit_assortment", "kit_assortment"): 9}
    types = pf.type_rows(renders, served)
    kits = pf.kit_rows(types)
    assert sorted(r["kit"] for r in kits) == [
        "industrial/figures (drawn to scale)", "industrial/figures (in scope)"
    ]  # fmt: skip
    assert f"| {pf.OUT_OF_SCOPE} |" in pf.type_table(types)
    assert [r["type"] for r in pf.worst(types)] == ["kit_assortment"]


def test_the_contact_svg_keeps_each_cell_ids_apart() -> None:
    cell = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="300" viewBox="0 0 200 300">'
        '<defs><pattern id="h0" width="5" height="5"/></defs>'
        '<rect width="200" height="300" fill="url(#h0)"/></svg>'
    )
    rows = [
        {**_render("k", t, "common", 0.1), "area_min": 0.1, "area_max": 0.1, "skus": 1}
        for t in ("A", "B")
    ]
    out = pf.contact_svg(rows, {"A-common": cell.encode(), "B-common": cell.encode()})
    root = ET.fromstring(out)
    ids = [el.get("id") for el in root.iter() if el.get("id")]
    assert ids == ["c0-h0", "c1-h0"]
    assert 'fill="url(#c1-h0)"' in out
    inner = [el for el in root if el.tag.endswith("svg")]
    assert [(el.get("x"), el.get("width"), el.get("viewBox")) for el in inner] == [
        ("0", "200", "0 0 200 300"), ("200", "200", "0 0 200 300")
    ]  # fmt: skip
