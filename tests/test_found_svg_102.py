"""Found SVG drawings (#102): the normaliser, the licence manifest, C-clamps as the proof.

A found drawing is only ever used after ``scripts/normalise_found_svg.py`` has reduced it to plain
filled outlines in a role vocabulary, and only if ``MANIFEST.csv`` records where it came from and
under what licence. These tests pin both, and pin that the C-clamps breadth row draws the found
clamp (CC0) instead of the generic bracket.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.drawing import draw_sku, svg_problems
from synthetic_ecommerce_data.core.drawing.model import Poly
from synthetic_ecommerce_data.domains.industrial import breadth
from synthetic_ecommerce_data.domains.industrial.drawing import found_shapes
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_shapes import BREADTH_SHAPES

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "normalise_found_svg.py"
FOUND = ROOT / "src/synthetic_ecommerce_data/domains/industrial/data/found_svg"
NS = "{http://www.w3.org/2000/svg}"

#: A source with the faults a real download has: a transform on an ancestor, a logo and a text in
#: sibling groups, strokes, a curve, a multi-subpath path using a relative ``m`` after ``z``.
SOURCE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
 <metadata>made with a tool</metadata>
 <g transform="translate(10 20)">
  <g><path fill="#ff0000" d="M0 0h5v5z"/><text>Brand</text></g>
  <g stroke-width=".2">
   <path fill="#b3b3b3" stroke="#000" d="M0 0h10v10h-10z"/>
   <path fill="gray" d="M20 0c0 5 10 5 10 0z"/>
   <path fill="#b3b3b3" d="M0 40h10v10h-10zm20 0h10v10h-10z"/>
  </g>
 </g>
</svg>"""
ROLES = {"#b3b3b3": "part", "gray": "plain"}


def _script():
    spec = importlib.util.spec_from_file_location("normalise_found_svg", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["normalise_found_svg"] = module
    spec.loader.exec_module(module)
    return module


def _paths(text: str) -> list[tuple[str, list[tuple[float, float]]]]:
    root = ET.fromstring(text)
    out = []
    for path in root.iter(NS + "path"):
        numbers = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", path.get("d", ""))]
        out.append((path.get("class", ""), list(zip(numbers[::2], numbers[1::2], strict=True))))
    return out


def _normalised() -> str:
    out = _script().normalise(SOURCE, select="0/-1", roles=ROLES)
    assert out.startswith("<svg"), "the normaliser wrote no SVG"
    return out


def test_the_normaliser_keeps_only_the_selected_group_as_plain_paths():
    out = _normalised()
    root = ET.fromstring(out)
    tags = {element.tag for element in root.iter()}
    assert tags == {NS + "svg", NS + "path"}
    assert "Brand" not in out and "#ff0000" not in out and "made with" not in out
    for word in ("stroke", "transform", "fill", "style"):
        assert word not in out, word


def test_the_normaliser_applies_the_ancestor_transform_and_scales_to_one_thousand():
    out = _normalised()
    assert ET.fromstring(out).get("viewBox", "").split()[:3] == ["0", "0", "1000"]
    role, square = _paths(out)[0]
    assert role == "part"
    xs, ys = [p[0] for p in square], [p[1] for p in square]
    assert (min(xs), min(ys)) == pytest.approx((0, 0), abs=0.06)
    assert (max(xs), max(ys)) == pytest.approx((1000 / 3, 1000 / 3), abs=0.06)


def test_the_normaliser_flattens_a_curve_and_maps_each_fill_to_its_role():
    paths = _paths(_normalised())
    role, curve = paths[1]
    assert role == "plain"
    assert len(curve) >= 8
    assert max(p[1] for p in curve) == pytest.approx(3.75 * 1000 / 30, abs=0.1)


def test_a_relative_move_after_close_starts_from_the_subpath_start():
    paths = _paths(_normalised())
    assert len(paths) == 4, "each subpath is its own path"
    first, second = paths[2][1], paths[3][1]
    assert min(p[0] for p in first) == pytest.approx(0, abs=0.06)
    assert min(p[0] for p in second) == pytest.approx(20 * 1000 / 30, abs=0.1)


def test_an_unmapped_fill_is_refused_not_defaulted():
    with pytest.raises(ValueError, match="fill"):
        _script().normalise(SOURCE, select="0/-1", roles={"#b3b3b3": "part"})


def test_an_arc_command_is_refused():
    arc = SOURCE.replace("M20 0c0 5 10 5 10 0z", "M20 0a5 5 0 0 1 10 0z")
    with pytest.raises(ValueError, match="arc"):
        _script().normalise(arc, select="0/-1", roles=ROLES)


def _manifest() -> list[dict[str, str]]:
    assert (FOUND / "MANIFEST.csv").exists(), "found_svg/MANIFEST.csv is missing"
    with (FOUND / "MANIFEST.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_every_found_file_has_a_manifest_row_and_every_row_a_file():
    rows = _manifest()
    assert rows, "the manifest is empty"
    listed = {row["file"] for row in rows}
    on_disk = {p.name for p in FOUND.glob("*.svg")}
    assert listed == on_disk


def test_every_manifest_row_names_a_tier_one_or_two_licence_and_its_source():
    tier_licences = {"1": {"CC0-1.0", "PD"}, "2": {"CC-BY-4.0", "CC-BY-SA-4.0"}}
    for row in _manifest():
        assert row["tier"] in tier_licences, row
        assert row["licence"] in tier_licences[row["tier"]], row
        assert row["author"].strip() and row["source_url"].startswith("https://"), row
        assert (row["share_alike"] == "yes") == (row["licence"] == "CC-BY-SA-4.0"), row
        assert re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]), row


def test_the_manifest_hash_is_the_committed_file_so_a_hand_edit_is_caught():
    for row in _manifest():
        data = (FOUND / row["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"], row["file"]


def test_a_committed_found_file_is_plain_paths_in_the_role_vocabulary():
    for row in _manifest():
        root = ET.fromstring((FOUND / row["file"]).read_text())
        assert {e.tag for e in root.iter()} == {NS + "svg", NS + "path"}, row["file"]
        assert {p.get("class") for p in root.iter(NS + "path")} <= {"part", "plain"}


def test_the_c_clamps_row_draws_the_found_clamp_not_the_bracket():
    row = next(r for r in breadth.rows() if r.key == "c_clamps")
    assert row.shape == "c_clamp"
    assert "c_clamp" in BREADTH_SHAPES


def _clamp():
    assert "c_clamp" in BREADTH_SHAPES, "no c_clamp breadth shape"
    return BREADTH_SHAPES["c_clamp"]


def test_the_found_clamp_is_many_parts_scaled_to_its_extent():
    fn, extent = _clamp()
    fig = fn({"Size": "2 in"}).figure
    polys = [s for s in fig.shapes if isinstance(s, Poly)]
    assert len(polys) >= 10
    x0, y0, x1, y1 = fig.bounds()
    assert max(x1 - x0, y1 - y0) == pytest.approx(max(extent), rel=1e-6)
    assert (x1 - x0) <= extent[0] + 1e-9 and (y1 - y0) <= extent[1] + 1e-9


def test_the_found_clamp_does_not_read_the_record():
    fn, _ = _clamp()
    assert fn({"Size": "2 in"}).figure == fn({"Size": "6 in"}).figure


def test_the_loader_refuses_a_shape_with_no_file():
    with pytest.raises(FileNotFoundError):
        found_shapes.load("no_such_shape", 1.0)


def test_a_c_clamps_sheet_passes_the_svg_gate():
    data, _ = draw_sku("c_clamps", brands.BRANDS[0], {"Material": "Steel", "Size": "3 in"})
    assert svg_problems(data) == []
    drawn = b" ".join(re.findall(rb' d="([^"]*)"', data))
    assert len(re.findall(rb"\d", drawn)) >= 400, "a clamp, not a six-point bracket"
