"""The per-SKU drawings: no text, one per SKU, and every visual difference a real one.

Rulings (elastic/prism-industrial-products#103): one drawing per SKU drawn from
its own values; NO text of any kind in any drawing; brands visibly different by
house style; small SVG; the drawings never committed, only rebuilt into a pinned
bundle whose every file matches the digest the catalog records.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import statistics
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import bundle, emit
from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.generate import BRANDS, generate
from synthetic_industrial_products.catalog.vocab import VOCAB
from synthetic_industrial_products.drawing import FIGURES, draw_sku, text_in
from synthetic_industrial_products.drawing.model import Poly
from synthetic_industrial_products.drawing.style import (
    EXTRA_FINISH_TINT,
    MATERIAL_FILL,
    MATERIAL_HATCH,
    house_style,
)
from synthetic_industrial_products.render.marking import (
    BRAND_INK,
    FINISH_ATTRIBUTES,
    FINISH_TINT,
    MATERIAL_ATTRIBUTES,
)

REPO = Path(__file__).resolve().parents[1]
GOLDEN = REPO / "golden-catalog"
CATALOG = generate(SMALL)
DRAWINGS = list(emit.iter_drawings(CATALOG))


def test_every_product_type_has_a_figure():
    assert set(FIGURES) == set(VOCAB)
    assert {line.type_key for line, _, _, _ in DRAWINGS} == set(VOCAB)


# --- no text, of any kind -------------------------------------------------------


def test_no_drawing_carries_any_text():
    """The maintainer's ruling, asserted over every SKU of a generated catalog."""
    offenders = [(child.sku, text_in(data)) for _, child, data, _ in DRAWINGS if text_in(data)]
    assert offenders == []


@pytest.mark.parametrize(
    "planted",
    [
        b'<svg><text x="1" y="1">1/4"</text></svg>',
        b"<svg><text><tspan>M8</tspan></text></svg>",
        b'<svg><path id="DejaVuSans-31" d="M0 0"/></svg>',
        b'<svg style="font-family:Arial"></svg>',
    ],
)
def test_the_text_check_bites(planted):
    assert text_in(planted), planted


def test_every_drawing_is_well_formed_svg():
    for _, child, data, _ in DRAWINGS:
        root = ET.fromstring(data)
        assert root.tag.endswith("svg"), child.sku


def test_the_drawings_are_small():
    """Measured: ~1.6 KB mean on the committed catalog; a regression to text or
    glyph paths would multiply it (matplotlib's glyph-path card was ~26 KB)."""
    sizes = [len(data) for _, _, data, _ in DRAWINGS]
    assert statistics.mean(sizes) < 3000, statistics.mean(sizes)
    assert max(sizes) < 8000, max(sizes)


# --- one per SKU, and every difference a real one -----------------------------


def test_the_same_record_draws_the_same_bytes():
    line, child, data, _ = DRAWINGS[0]
    again, _ = draw_sku(line.type_key, line.brand, emit.drawing_record(CATALOG, line, child))
    assert again == data


def test_a_drawn_dimension_changes_the_drawing():
    """Two lengths of one screw must not look alike (the defect the ruling named)."""
    line, child, data, _ = next(d for d in DRAWINGS if d[0].type_key == "screw_socket_head")
    record = emit.drawing_record(CATALOG, line, child)
    longer = dict(record, Length='9"', **{"Length under Head": '9"', "Thread Length": '9"'})
    other, _ = draw_sku(line.type_key, line.brand, longer)
    assert other != data


def test_an_attribute_no_drawing_shows_does_not_change_it():
    """The control: a standard is not a shape. Only drawn values move the picture."""
    line, child, data, _ = DRAWINGS[0]
    record = emit.drawing_record(CATALOG, line, child)
    record["Standards"] = "ISO 9999, ANSI Z1"
    same, _ = draw_sku(line.type_key, line.brand, record)
    assert same == data


def test_the_brand_is_the_house_style():
    """Same record, another brand: different sheet, and the brand's own ink on it."""
    line, child, data, _ = DRAWINGS[0]
    record = emit.drawing_record(CATALOG, line, child)
    other_brand = next(b for b in BRANDS if b != line.brand)
    other, _ = draw_sku(line.type_key, other_brand, record)
    assert other != data
    assert BRAND_INK[other_brand].encode() in other
    assert BRAND_INK[line.brand].encode() not in other


def test_every_brand_has_a_house_style_and_they_differ():
    styles = {brand: house_style(brand) for brand in BRANDS}
    assert len({(s.ink, s.paper) for s in styles.values()}) == len(BRANDS)
    assert len({s.frame for s in styles.values()}) == 4


def test_every_published_finish_and_material_has_a_colour_and_a_hatch():
    """Swept from the data: a value with no style would refuse to draw."""
    finishes, materials = set(), set()
    for line, child in CATALOG.all_skus():
        record = emit.drawing_record(CATALOG, line, child)
        finishes |= {record[n] for n in FINISH_ATTRIBUTES if n in record}
        materials |= {record[n] for n in MATERIAL_ATTRIBUTES if n in record}
    assert finishes and materials
    assert finishes <= set(FINISH_TINT) | set(EXTRA_FINISH_TINT), finishes
    assert materials <= set(MATERIAL_FILL) & set(MATERIAL_HATCH), materials


def test_the_bearing_closure_is_visible():
    """Variants that differ only in closure must not draw alike."""
    by_product = defaultdict(list)
    for line, _child, data, _ in DRAWINGS:
        if line.type_key == "bearing_radial_ball":
            by_product[line.product_id].append(data)
    multi = [drawings for drawings in by_product.values() if len(drawings) > 1]
    assert multi, "no bearing had two closures to compare"
    for drawings in multi:
        assert len(set(drawings)) == len(drawings)


def test_nominal_geometry_stays_rare():
    """How often a drawing could not read its primary dimension, per type.

    A drawing whose primary dimension is unreadable is drawn at its kind's
    nominal proportions. That is honest -- it states no number -- but it
    should be the exception the defect rates make it, not a default.
    """
    by_type: dict[str, Counter] = defaultdict(Counter)
    for line, _, _, source in DRAWINGS:
        by_type[line.type_key][source] += 1
    for type_key, counts in by_type.items():
        share = counts["nominal"] / sum(counts.values())
        assert share <= 0.1, (type_key, dict(counts))


# --- the bundle ------------------------------------------------------------------


def test_the_committed_catalog_rebuilds_into_its_recorded_drawings():
    """Every drawing the committed images.jsonl names, rebuilt, matches its digest."""
    files = bundle.rebuild(GOLDEN)
    rows = [json.loads(line) for line in (GOLDEN / "images.jsonl").read_text().splitlines()]
    assert len(files) == len(rows)
    assert all(not text_in(data) for _, data in files)


def test_a_drawing_that_moved_without_a_regeneration_refuses_the_bundle(tmp_path):
    shutil.copy(GOLDEN / "nested.jsonl", tmp_path / "nested.jsonl")
    lines = (GOLDEN / "images.jsonl").read_text().splitlines()
    row = json.loads(lines[0])
    row["sha256"] = hashlib.sha256(b"a different drawing").hexdigest()
    lines[0] = json.dumps(row)
    (tmp_path / "images.jsonl").write_text("\n".join(lines) + "\n")
    with pytest.raises(bundle.BundleMismatchError):
        bundle.rebuild(tmp_path)


def test_the_archive_is_deterministic(tmp_path):
    files = [("a/b/1.svg", b"<svg/>"), ("a/b/2.svg", b"<svg></svg>")]
    first = bundle.write_archive(files, tmp_path / "one.tar.gz")
    second = bundle.write_archive(list(reversed(files)), tmp_path / "two.tar.gz")
    assert first == second
    assert (tmp_path / "one.tar.gz").read_bytes() == (tmp_path / "two.tar.gz").read_bytes()


def test_rendered_drawings_are_never_committable():
    """The bundle's output folder is ignored by git, so a drawing cannot be committed."""
    probe = REPO / "out" / "images" / "never-commit-probe.svg"
    result = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q", str(probe)], check=False)
    assert result.returncode == 0, "out/images/ is not ignored by .gitignore"


@pytest.mark.parametrize(
    "type_key",
    ["screw_socket_head", "screw_flat_head", "bolt_hex", "end_mill_square", "drill_jobber"],
)
def test_elongated_parts_are_drawn_to_their_published_length(type_key):
    """The drawn length IS the record's: extent in inches equals the geometry's.

    Read against the dimensioned renderer's own geometry, so a figure that
    stopped reading a length -- and drew a nominal one -- reds here even though
    its bytes would still change with the size cue.
    """
    from synthetic_industrial_products.render import drill, endmill, fastener

    geometry = {
        "screw_socket_head": lambda r: fastener.geometry_from_record(r).total_height,
        "screw_flat_head": lambda r: fastener.geometry_from_record(r).total_height,
        "bolt_hex": lambda r: fastener.geometry_from_record(r).total_height,
        "end_mill_square": lambda r: endmill.geometry_from_record(r).oal.inches,
        "drill_jobber": lambda r: drill.geometry_from_record(r).oal.inches,
    }[type_key]
    figure_fn, _ = FIGURES[type_key]
    checked = 0
    for line, child in CATALOG.all_skus():
        if line.type_key != type_key:
            continue
        record = emit.drawing_record(CATALOG, line, child)
        drawn = figure_fn(dict(record))
        if drawn.source != "record":
            continue
        # The part on the axis, top to tip; end views sit beside it.
        on_axis = [
            point
            for shape in drawn.figure.shapes
            if isinstance(shape, Poly)
            and min(x for x, _ in shape.points) < 0 < max(x for x, _ in shape.points)
            for point in shape.points
        ]
        extent = max(y for _, y in on_axis) - min(y for _, y in on_axis)
        assert extent == pytest.approx(geometry(record), rel=1e-6), child.sku
        checked += 1
    assert checked > 3, f"only {checked} {type_key} records drawn from the record"
