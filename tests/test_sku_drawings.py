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
from synthetic_industrial_products.drawing import FIGURES, draw_sku, svg_problems
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
    offenders = [
        (child.sku, svg_problems(data)) for _, child, data, _ in DRAWINGS if svg_problems(data)
    ]
    assert offenders == []


#: Every form of text the review planted, and the older blacklist's own cases.
#: Each is injected into a REAL clean drawing, so the only difference between
#: the red and the green case is the planted element.
PLANTED_TEXT = {
    "text": '<text x="1" y="1">1/4"</text>',
    "tspan": "<g><tspan>M8</tspan></g>",
    "title": "<title>M8 x 1.25</title>",
    # Empty, so only the ELEMENT allow-list can catch it -- not the
    # character-data rule -- and each layer is proven on its own.
    "title-empty": "<title/>",
    "desc": "<desc>socket cap screw</desc>",
    "aria": '<g aria-label="1/4-20 x 1in"/>',
    "comment": "<!-- 3/8-16 x 1 -->",
    "metadata": "<metadata>SKU 21NB25</metadata>",
    "foreignObject": "<foreignObject><div>M8</div></foreignObject>",
    "raster": '<image href="data:image/png;base64,iVBORw0KGgo="/>',
    "font-face": "<style>@font-face{src:url(a.woff)}</style>",
    "glyph-id": '<path id="LiberationSans-31" d="M0 0"/>',
    "dejavu-id": '<path id="DejaVuSans-31" d="M0 0"/>',
    "font-attribute": '<path d="M0 0" font-family="Arial"/>',
    "char-data": "<g>1/4</g>",
    "processing-instruction": "<?render text?>",
    # Attribute VALUES (the second review): external and data paint servers,
    # free strings, and a nested document.
    "data-paint-server": '<path d="M0 0" fill="url(data:image/svg+xml;base64,PHN2Zy8+#p)"/>',
    "external-paint-server": '<path d="M0 0" fill="url(https://example.invalid/p.svg#p)"/>',
    "named-fill": '<path d="M0 0" fill="red"/>',
    "free-transform": '<g transform="translate(1,1) scale(9)"/>',
    "letters-in-path-data": '<path d="M0 0 A1 1 0 0 1 2 2"/>',
    "char-ref-in-value": '<path d="M0 0" stroke="&#35;123abc"/>',
    "nested-svg": '<svg viewBox="0 0 1 1"/>',
}


@pytest.mark.parametrize("name", sorted(PLANTED_TEXT))
def test_the_allow_list_refuses_every_planted_text_form(name):
    clean = DRAWINGS[0][2]
    assert svg_problems(clean) == [], "the control drawing must be clean"
    planted = clean.replace(b"</svg>", PLANTED_TEXT[name].encode() + b"</svg>")
    assert svg_problems(planted), name


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
    assert all(not svg_problems(data) for _, data in files)


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


# --- sizes are visible: one scale per type -------------------------------------

#: Attributes no figure draws, so siblings differing ONLY in these may draw
#: alike: conformance claims, identifiers, commercial quantities, ratings and
#: speeds, a hammer's weight (a weight is not a shape), and names of the
#: measurement system.
NOT_DRAWN_BY_ANY_FIGURE = frozenset(
    {
        "Standards", "Dimension Type", "Measurement System", "System of Measurement",
        "List Number", "Head Weight", "Package Quantity", "Max. RPM", "Grade",
        "Dynamic Load Capacity", "Static Load Capacity", "Decimal Equivalent", "Item",
    }
)  # fmt: skip


def test_siblings_whose_drawn_values_differ_never_draw_alike():
    """Over the COMMITTED catalog: a product's variants must look different.

    Measured before the fix: 84 of 2,746 multi-variant products had siblings
    whose drawings were identical bytes although their dimensions differed --
    proportional end mills, and every washer below half the largest, clamped
    to one size.
    """
    offenders = []
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        if len(parent["variants"]) < 2:
            continue
        drawn: dict[bytes, dict] = {}
        for variant in parent["variants"]:
            record = bundle._record(parent, variant)
            data, _ = draw_sku(parent["product_type"], parent["brand"], record)
            shown = {k: v for k, v in record.items() if k not in NOT_DRAWN_BY_ANY_FIGURE}
            if data in drawn and drawn[data] != shown:
                offenders.append(parent["product_id"])
                break
            drawn[data] = shown
    assert offenders == [], f"{len(offenders)} products: {offenders[:5]}"


def _outer_radius(svg: bytes) -> float:
    root = ET.fromstring(svg)
    return max(float(c.attrib["r"]) for c in root.iter() if c.tag.endswith("circle"))


def test_an_m3_washer_is_drawn_smaller_than_an_m16_in_proportion():
    """The ruling's own example: an M4 washer vs an M16 washer must LOOK different.

    ISO 7089: M3 is 7 mm across, M16 is 30 mm (true ratio 0.233). Drawn on
    the type's one scale, lifted by exactly the documented floor rule on the
    small one -- measured 0.285.
    """
    m3 = {"Size": "M3", "Inside Dia.": "3.20mm", "Outside Dia.": "7mm", "Thickness": "0.50mm"}
    m16 = {"Size": "M16", "Inside Dia.": "17mm", "Outside Dia.": "30mm", "Thickness": "3mm"}
    small, _ = draw_sku("washer_flat", "Corvane", m3)
    large, _ = draw_sku("washer_flat", "Corvane", m16)
    ratio = _outer_radius(small) / _outer_radius(large)
    # M16 is drawn at the type's scale; M3 falls under the legibility floor and
    # is drawn sqrt(FLOOR * d) across instead of d -- still smaller, by the
    # stated rule, and no further from the true 7/30 than that rule allows.
    from synthetic_industrial_products.drawing.sheet import FLOOR, type_scale

    scale = type_scale(FIGURES["washer_flat"][1])
    d3, d16 = scale * 7 / 25.4, scale * 30 / 25.4
    expected = ((FLOOR * d3) ** 0.5 if d3 < FLOOR else d3) / d16
    assert ratio == pytest.approx(expected, rel=0.02), (ratio, expected)
    assert 7 / 30 <= ratio < 0.35


def _golden_figures():
    """(type, product_id, sku, figure) for every SKU of the committed catalog."""
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        figure_fn, _ = FIGURES[parent["product_type"]]
        for variant in parent["variants"]:
            yield (
                parent["product_type"],
                parent["product_id"],
                variant["sku"],
                figure_fn(bundle._record(parent, variant)).figure,
            )


GOLDEN_FIGURES = list(_golden_figures())


def test_no_product_exceeds_its_types_extent():
    """The type's scale is a constant only while every product fits its declared extent."""
    for type_key, _, sku, figure in GOLDEN_FIGURES:
        x0, y0, x1, y1 = figure.bounds()
        width, height = FIGURES[type_key][1]
        assert x1 - x0 <= width and y1 - y0 <= height, (type_key, sku, x1 - x0, y1 - y0)


def test_every_drawing_fits_its_sheet():
    """The legibility lift enlarges small parts; it must never push one off the sheet."""
    from synthetic_industrial_products.drawing import svg as page
    from synthetic_industrial_products.drawing.sheet import MARGIN, product_scale

    for type_key, _, sku, figure in GOLDEN_FIGURES:
        x0, y0, x1, y1 = figure.bounds()
        scale = product_scale(FIGURES[type_key][1], figure.size_in)
        assert (x1 - x0) * scale <= page.WIDTH - 2 * MARGIN + 1e-6, (type_key, sku)
        assert (y1 - y0) * scale <= page.HEIGHT - 2 * MARGIN + 1e-6, (type_key, sku)


def test_a_larger_primary_dimension_is_never_drawn_shorter():
    """Order on the sheet is order in the record: within a product AND across a type.

    The primary dimension is the figure's ``size_in`` -- a screw's length, a
    washer's diameter, a hex key's length. Measured before the constant scale:
    ball end mill ``OST-R122-0771`` drew a 3.0625" tool 71.5 units long and its
    3.125" sibling 59.6, and an M20 x 35 mm flat head drew smaller than a
    #6-32 x 1-3/8" one.
    """
    from synthetic_industrial_products.drawing.sheet import product_scale

    by_type: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    for type_key, _, sku, figure in GOLDEN_FIGURES:
        drawn = figure.size_in * product_scale(FIGURES[type_key][1], figure.size_in)
        by_type[type_key].append((figure.size_in, drawn, sku))
    for type_key, rows in by_type.items():
        rows.sort()
        for (size_a, drawn_a, sku_a), (size_b, drawn_b, sku_b) in zip(rows, rows[1:], strict=False):
            if size_b > size_a + 1e-9:
                assert drawn_b > drawn_a, (type_key, sku_a, size_a, drawn_a, sku_b, size_b)


def test_the_scale_is_one_constant_per_type_above_the_floor():
    from synthetic_industrial_products.drawing.sheet import FLOOR, product_scale, type_scale

    for type_key, _, sku, figure in GOLDEN_FIGURES:
        extent = FIGURES[type_key][1]
        if type_scale(extent) * figure.size_in >= FLOOR:
            assert product_scale(extent, figure.size_in) == type_scale(extent), (type_key, sku)


def test_the_reviews_cross_product_case_reads_the_right_way_round():
    """An M20 x 35 mm flat head (40 mm head) is drawn wider than a #6-32 x 1-3/8" one."""
    from synthetic_industrial_products.drawing.sheet import product_scale

    extent = FIGURES["screw_flat_head"][1]
    m20 = {"Head Type": "Flat", "Dia./Thread Size": "M20x2.5", "Length": "35mm",
           "Thread Length": "35mm", "Head Dia.": "40mm", "Head Height": "10mm"}  # fmt: skip
    no6 = {"Head Type": "Flat", "Dia./Thread Size": "#6-32", "Length": '1-3/8"',
           "Thread Length": '1-3/8"', "Head Dia.": '0.2620"', "Head Height": '0.0830"'}  # fmt: skip
    figure_fn, _ = FIGURES["screw_flat_head"]
    widths = {}
    for name, record in (("m20", m20), ("no6", no6)):
        figure = figure_fn(record).figure
        x0, _, x1, _ = figure.bounds()
        widths[name] = (x1 - x0) * product_scale(extent, figure.size_in)
    assert widths["m20"] > 3 * widths["no6"], widths


# --- the archive layout and its pinnable digest ----------------------------------


def test_every_archive_member_is_the_image_urls_path_under_images():
    """The cross-repo contract: member ``industrial/<...>.svg`` is served at /images/<member>."""
    files = bundle.rebuild(GOLDEN)
    rows = [json.loads(line) for line in (GOLDEN / "images.jsonl").read_text().splitlines()]
    members = {path for path, _ in files}
    assert all(path.startswith(emit.IMAGE_ROOT + "/") for path in members)
    assert {row["url"] for row in rows} == {f"/images/{path}" for path in members}


def test_the_content_digest_is_derivable_from_the_committed_manifest():
    """What the customization pins needs no build, no zlib, only images.jsonl."""
    assert bundle.manifest_digest(GOLDEN) == bundle.files_digest(bundle.rebuild(GOLDEN))


def test_the_content_digest_does_not_depend_on_compression(tmp_path):
    """Two compressions of one content: different archive bytes may happen, one content digest."""
    import gzip
    import io
    import tarfile

    files = [("industrial/a/b/1.svg", b"<svg/>"), ("industrial/a/b/2.svg", b"<svg></svg>")]
    digests = set()
    for level in (1, 9):
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode="w") as tar:
            for path, data in files:
                info = tarfile.TarInfo(path)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        packed = gzip.compress(raw.getvalue(), compresslevel=level, mtime=0)
        with tarfile.open(fileobj=io.BytesIO(packed), mode="r:gz") as tar:
            unpacked = [(m.name, tar.extractfile(m).read()) for m in tar.getmembers()]
        digests.add(bundle.files_digest(unpacked))
    assert len(digests) == 1


def test_a_changed_drawing_changes_the_content_digest():
    files = [("industrial/a/b/1.svg", b"<svg/>")]
    assert bundle.files_digest(files) != bundle.files_digest([("industrial/a/b/1.svg", b"<svg />")])
