"""The per-SKU drawings: no text, one per SKU, and every visual difference a real one.

Rulings (elastic/prism-industrial-products#103): one drawing per SKU drawn from
its own values; NO text of any kind in any drawing; brands visibly different by
house style; small SVG; the drawings never committed, only rebuilt into a pinned
bundle whose every file matches the digest the catalog records.
"""

from __future__ import annotations

import functools
import hashlib
import json
import shutil
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import bundle, emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.drawing import FIGURES, draw_product, draw_sku, svg_problems
from synthetic_ecommerce_data.core.drawing.model import Poly
from synthetic_ecommerce_data.core.drawing.style import (
    EXTRA_FINISH_TINT,
    MATERIAL_FILL,
    MATERIAL_HATCH,
    house_style,
)
from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, all_type_keys, generate
from synthetic_ecommerce_data.domains.industrial.render.marking import (
    BRAND_INK,
    FINISH_ATTRIBUTES,
    FINISH_TINT,
    MATERIAL_ATTRIBUTES,
)
from synthetic_ecommerce_data.domains.industrial.vocab import VOCAB

REPO = Path(__file__).resolve().parents[1]
GOLDEN = REPO / "golden-catalog"


@functools.cache
def _facets() -> dict[str, dict]:
    """``{sku: facets}``: a nested entry carries no spelling, so a drawing reads it here (#42)."""
    return bundle.flat_facets(GOLDEN)


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


#: No drawing may reach this many bytes. A type whose figure could approach it
#: holds its own worst case to it too, beyond what one seed stocks.
MAX_DRAWING_BYTES = 8000


def test_the_drawings_are_small():
    """Measured: ~2.0 KB mean on the committed catalog; a regression to text or
    glyph paths would multiply it (matplotlib's glyph-path card was ~26 KB)."""
    sizes = [len(data) for _, _, data, _ in DRAWINGS]
    assert statistics.mean(sizes) < 3000, statistics.mean(sizes)
    assert max(sizes) < MAX_DRAWING_BYTES, max(sizes)


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
    # Another INK: brands share inks now (the (ink, frame) pair names a brand).
    other_brand = next(b for b in BRANDS if BRAND_INK[b] != BRAND_INK[line.brand])
    other, _ = draw_sku(line.type_key, other_brand, record)
    assert other != data
    assert BRAND_INK[other_brand].encode() in other
    assert BRAND_INK[line.brand].encode() not in other


def test_every_brand_has_a_house_style_and_they_differ():
    """Twelve inks and four frames over the brand book: the PAIR is the brand."""
    styles = {brand: house_style(brand) for brand in BRANDS}
    assert len({(s.ink, s.frame) for s in styles.values()}) == len(BRANDS)
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

    Exempts the breadth categories (:mod:`.catalog.breadth`,
    alexander-marquardt/synthetic-ecommerce-data#34): their fixed-shape
    drawings never read the record AT ALL, so ``source`` is "nominal" for
    100% of them, by design (maintainer, 2026-09-30: "just something to fill
    up the image").
    """
    by_type: dict[str, Counter] = defaultdict(Counter)
    for line, _, _, source in DRAWINGS:
        if line.spec_quality == "fast_and_cheap":
            continue
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


def test_rebuild_called_directly_draws_a_breadth_product(tmp_path):
    """A fresh interpreter that imports only the bundle can rebuild a breadth product.

    In this process something else has already imported the breadth module, which
    is what registers its figures, so the check runs in a subprocess that imports
    nothing first.
    """
    nested = [json.loads(line) for line in (GOLDEN / "nested.jsonl").read_text().splitlines()]
    breadth_types = set(all_type_keys("breadth"))
    parent = next(p for p in nested if p["product_type"] in breadth_types)
    skus = {variant["sku"] for variant in parent["variants"]}
    (tmp_path / "nested.jsonl").write_text(json.dumps(parent) + "\n")
    for name in ("flat.jsonl", "images.jsonl"):
        rows = [r for r in (GOLDEN / name).read_text().splitlines() if json.loads(r)["sku"] in skus]
        (tmp_path / name).write_text("\n".join(rows) + "\n")
    script = (
        "import sys; from pathlib import Path; "
        "from synthetic_ecommerce_data.core.bundle import rebuild; "
        "print(len(rebuild(Path(sys.argv[1]))))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.strip() == str(len(skus))


def test_a_drawing_that_moved_without_a_regeneration_refuses_the_bundle(tmp_path):
    shutil.copy(GOLDEN / "nested.jsonl", tmp_path / "nested.jsonl")
    shutil.copy(GOLDEN / "flat.jsonl", tmp_path / "flat.jsonl")
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
    from synthetic_ecommerce_data.domains.industrial.render import drill, endmill, fastener

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

    Exempts the breadth categories (:mod:`.catalog.breadth`,
    alexander-marquardt/synthetic-ecommerce-data#34): their fixed-shape
    drawings never read the record, so two siblings of one breadth product --
    say two ball diameters -- draw identically BY DESIGN, the property this
    test exists to catch everywhere else.
    """
    offenders = []
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        if parent.get("spec_quality") == "fast_and_cheap":
            continue
        if len(parent["variants"]) < 2:
            continue
        drawn: dict[bytes, dict] = {}
        for variant in parent["variants"]:
            record = bundle._record(parent, variant, _facets()[variant["sku"]])
            data, _ = draw_sku(parent["product_type"], parent["brand"], record)
            shown = {k: v for k, v in record.items() if k not in NOT_DRAWN_BY_ANY_FIGURE}
            if data in drawn and drawn[data] != shown:
                offenders.append(parent["product_id"])
                break
            drawn[data] = shown
    assert offenders == [], f"{len(offenders)} products: {offenders[:5]}"


def _true_scale_copy(svg: bytes) -> list[ET.Element]:
    """The drawing's elements that belong to the TRUE-scale part.

    A plain drawing is all part. A magnified one paints the true-scale part
    first, then the white lens (the one un-stroked ``#ffffff`` circle), then
    the enlarged copy and the glyph -- so the part is what precedes the lens.
    """
    out = []
    for element in list(ET.fromstring(svg)):
        tag = element.tag.split("}")[-1]
        if (
            tag == "circle"
            and element.attrib.get("fill") == "#ffffff"
            and "stroke" not in element.attrib
        ):
            break
        if tag in ("rect", "defs"):  # the paper, a rule frame and the hatch patterns
            continue
        if element.attrib.get("stroke-width") == "2":  # a corner-marker frame
            continue
        out.append(element)
    return out


def _circle_radii(elements) -> list[float]:
    return sorted(float(e.attrib["r"]) for e in elements if e.tag.endswith("circle"))


def _type_scale(type_key: str) -> float:
    from synthetic_ecommerce_data.core.drawing.sheet import type_scale

    return type_scale(FIGURES[type_key][1])


def test_an_m3_washer_is_drawn_smaller_than_an_m16_in_true_proportion():
    """The ruling's own example: an M4 washer vs an M16 washer must LOOK different.

    ISO 7089: M3 is 7 mm across, M16 is 30 mm. Both are drawn at the type's one
    scale, so the true-scale M3 is exactly 7/30 of the M16.
    """
    m3 = {"Size": "M3", "Inside Dia.": "3.20mm", "Outside Dia.": "7mm", "Thickness": "0.50mm"}
    m16 = {"Size": "M16", "Inside Dia.": "17mm", "Outside Dia.": "30mm", "Thickness": "3mm"}
    small, _ = draw_sku("washer_flat", "Dravenholt", m3)
    large, _ = draw_sku("washer_flat", "Dravenholt", m16)
    ratio = _circle_radii(_true_scale_copy(small))[-1] / _circle_radii(_true_scale_copy(large))[-1]
    assert ratio == pytest.approx(7 / 30, abs=0.01), ratio


def _golden_products():
    """(type, product_id, [(sku, figure)], largest size_in) for every committed product."""
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        figure_fn, _ = FIGURES[parent["product_type"]]
        figures = [
            (variant["sku"], figure_fn(record).figure)
            for variant, record in zip(
                parent["variants"], bundle.records(parent, _facets()), strict=True
            )
        ]
        largest = max(figure.size_in for _, figure in figures)
        yield parent["product_type"], parent["product_id"], figures, largest, parent


GOLDEN_PRODUCTS = list(_golden_products())


def test_no_product_exceeds_its_types_extent():
    """The type's scale is a constant only while every product fits its declared extent."""
    for type_key, _, figures, _, _ in GOLDEN_PRODUCTS:
        width, height = FIGURES[type_key][1]
        for sku, figure in figures:
            x0, y0, x1, y1 = figure.bounds()
            assert x1 - x0 <= width and y1 - y0 <= height, (type_key, sku, x1 - x0, y1 - y0)


def test_every_drawing_fits_its_sheet():
    """At the type's scale every SKU fits inside the sheet's margin."""
    from synthetic_ecommerce_data.core.drawing import svg as page
    from synthetic_ecommerce_data.core.drawing.sheet import MARGIN

    for type_key, _, figures, _, _ in GOLDEN_PRODUCTS:
        scale = _type_scale(type_key)
        for sku, figure in figures:
            x0, y0, x1, y1 = figure.bounds()
            assert (x1 - x0) * scale <= page.WIDTH - 2 * MARGIN + 1e-6, (type_key, sku)
            assert (y1 - y0) * scale <= page.HEIGHT - 2 * MARGIN + 1e-6, (type_key, sku)


def test_siblings_are_drawn_at_one_scale_so_what_they_share_is_drawn_identically():
    """No dimension of one sibling is drawn smaller than the same dimension of another.

    Measured on the TRUE-scale part of each drawing, over the committed
    catalog: siblings that publish the same head (screws and bolts) or the same
    rings (a bearing's closures) draw those circles at exactly the same radii,
    whether or not one of them is also shown in a magnifier.
    """
    shared_by = {
        "screw_socket_head": ("Head Dia.", "Drive Size"),
        "screw_flat_head": ("Head Dia.", "Drive Size"),
        "screw_button_head": ("Head Dia.", "Drive Size"),
        "screw_low_head": ("Head Dia.", "Drive Size"),
        "bearing_radial_ball": ("Bore Dia.", "Outside Dia.", "Width"),
    }
    checked = 0
    offenders = []
    for type_key, product_id, _, _, parent in GOLDEN_PRODUCTS:
        names = shared_by.get(type_key)
        if names is None or len(parent["variants"]) < 2:
            continue
        records = bundle.records(parent, _facets())
        drawn = draw_product(type_key, parent["brand"], records)
        groups: dict[tuple, set] = defaultdict(set)
        for record, (data, _) in zip(records, drawn, strict=True):
            key = tuple(record.get(name) for name in names)
            groups[key].add(_circle_radii(_true_scale_copy(data))[-1])
        for radii in groups.values():
            checked += 1
            if len(radii) > 1:
                offenders.append(product_id)
    assert checked > 100
    assert offenders == [], f"{len(offenders)} products: {offenders[:5]}"


def test_within_a_type_every_part_is_drawn_in_true_proportion():
    """One scale per type: a part's drawn size is its published size times that constant."""
    from synthetic_ecommerce_data.core.drawing import product_scale_for

    for type_key, product_id, _figures, _largest, parent in GOLDEN_PRODUCTS:
        records = bundle.records(parent, _facets())
        assert product_scale_for(type_key, records) == _type_scale(type_key), product_id


def test_the_reviews_cross_product_case_reads_the_right_way_round():
    """An M20 x 35 mm flat head (40 mm head) is drawn wider than a #6-32 x 1-3/8" one."""
    m20 = {"Head Type": "Flat", "Dia./Thread Size": "M20x2.5", "Length": "35mm",
           "Thread Length": "35mm", "Head Dia.": "40mm", "Head Height": "10mm"}  # fmt: skip
    no6 = {"Head Type": "Flat", "Dia./Thread Size": "#6-32", "Length": '1-3/8"',
           "Thread Length": '1-3/8"', "Head Dia.": '0.2620"', "Head Height": '0.0830"'}  # fmt: skip
    figure_fn, _ = FIGURES["screw_flat_head"]
    widths = {}
    for name, record in (("m20", m20), ("no6", no6)):
        x0, _, x1, _ = figure_fn(record).figure.bounds()
        widths[name] = (x1 - x0) * _type_scale("screw_flat_head")
    assert widths["m20"] > 3 * widths["no6"], widths


# --- the magnifier (ruling on elastic/prism-industrial-products#103, v8) ----------

LENS_COLOUR = "#ffffff"


def _has_lens(svg: bytes) -> bool:
    return any(
        e.tag.endswith("circle")
        and e.attrib.get("fill") == LENS_COLOUR
        and "stroke" not in e.attrib
        for e in ET.fromstring(svg)
    )


def _drawn_size(type_key: str, record) -> tuple[float, float]:
    x0, y0, x1, y1 = FIGURES[type_key][0](dict(record)).figure.bounds()
    scale = _type_scale(type_key)
    return (x1 - x0) * scale, (y1 - y0) * scale


def _too_small(width: float, height: float) -> bool:
    """The ruling, written out independently of :func:`sheet.magnifier`:
    drawn at most 1/5 of the sheet's width AND at most 1/6 of its height."""
    return width <= 200 / 5 and height <= 300 / 6


def _handled_k(width: float, height: float) -> float:
    """What the handled glass would enlarge the part by, from the glyph's own extents."""
    import math

    from synthetic_ecommerce_data.core.drawing.sheet import _glyph_extent

    _, left, right, bottom = _glyph_extent(1.0, floor=False)
    radius = min((200 - 24) / (right - left), (300 - 24 - 14 - height) / (-left + bottom))
    return 0.92 * 2 * radius / math.hypot(width, height)


def _golden_skus():
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        for variant in parent["variants"]:
            yield parent, variant, bundle._record(parent, variant, _facets()[variant["sku"]])


def test_the_lens_appears_exactly_when_the_rule_says():
    """Over every committed SKU: a lens iff the part is drawn w <= 1/5 AND h <= 1/6 of the sheet."""
    wrong, lensed, plain = [], 0, 0
    for parent, variant, record in _golden_skus():
        type_key = parent["product_type"]
        data, _ = draw_sku(type_key, parent["brand"], record)
        expected = _too_small(*_drawn_size(type_key, record))
        if _has_lens(data) != expected:
            wrong.append(variant["sku"])
        lensed += expected
        plain += not expected
    assert wrong == [], f"{len(wrong)} SKUs: {wrong[:5]}"
    # Non-vacuity both ways, on the committed catalog.
    assert lensed > 1000 and plain > 5000, (lensed, plain)


#: The smallest enlargement any committed lens gives, measured and rounded
#: down to 0.01: the handled glass is used only at x2.5 or more. The floor is
#: a hex socket set screw (1/4-20 x 3/4" flat point), drawn at an extent no
#: wider than its 1" size needs; widening the extent to lift it would draw
#: every set screw smaller.
CATALOG_MIN_ENLARGEMENT = 2.45

#: What the handle-less lens gives at the rule's extreme, a part drawn a full
#: 40 x 50 (1/5 x 1/6 of the sheet). BELOW x2.5, and stated rather than hidden:
#: the lens is width-bound -- at the 8-unit margin that clears the brand frame
#: its interior radius is ~84.1 units -- so no larger lens fits.
EXTREME_ENLARGEMENT = 2.41

#: Two committed SKUs the handle-less lens must serve: an in-between screw (an
#: M6x1 x 10mm socket head) and a hairline drill (a 1/16" jobber). Re-picked on
#: every regeneration; the test fails if either is gone. Re-picked for
#: alexander-marquardt/synthetic-ecommerce-data#39 (Corner Radius/Neck
#: Length applied once instead of twice, which moved every SKU code): the
#: drill happened to keep its sku, ``3BF24``; the screw did not, so
#: ``19DG33`` became ``45HC83``. Re-picked for
#: alexander-marquardt/synthetic-ecommerce-data#48, which made every SKU
#: a ten-digit part number from its type's own block: each is the first
#: committed SKU, in catalog order, that matches the description and is drawn
#: under the handle-less lens.
PINNED_HANDLE_LESS = ("2334357307", "3818559508")
#: The hairline drill of the pair, by name, for the stroke test below.
HAIRLINE_DRILL = PINNED_HANDLE_LESS[1]


def test_every_lens_enlarges_at_least_the_measured_floor_and_is_handle_less_only_when_it_must_be():
    """Handled glass when it reaches x2.5; otherwise the larger handle-less lens.

    Over every committed SKU the rule applies to. The floor is the catalog's
    measured minimum; at the rule's extreme the handle-less lens gives ~x2.42.
    """
    from synthetic_ecommerce_data.core.drawing.sheet import magnifier

    counts = {True: 0, False: 0}
    lowest = 99.0
    pinned: set[str] = set()
    for parent, variant, record in _golden_skus():
        width, height = _drawn_size(parent["product_type"], record)
        mag = magnifier(width, height)
        if mag is None:
            continue
        lowest = min(lowest, mag.k)
        assert mag.handle == (_handled_k(width, height) >= 2.5), variant["sku"]
        counts[mag.handle] += 1
        if variant["sku"] in PINNED_HANDLE_LESS:
            assert not mag.handle, variant["sku"]
            pinned.add(variant["sku"])
    # Asserted, not assumed: a regeneration renumbers SKUs, and a pinned id
    # that no longer exists used to leave this check asserting nothing.
    assert pinned == set(PINNED_HANDLE_LESS), sorted(set(PINNED_HANDLE_LESS) - pinned)
    assert counts[True] > 100 and counts[False] > 500, counts
    assert CATALOG_MIN_ENLARGEMENT <= lowest < CATALOG_MIN_ENLARGEMENT + 0.01, lowest
    extreme = magnifier(200 / 5 - 1e-9, 300 / 6 - 1e-9)
    assert extreme is not None and not extreme.handle
    assert EXTREME_ENLARGEMENT <= extreme.k < 2.5, extreme.k


def test_the_handle_less_lens_clears_the_brand_frame():
    """The widest lens is 8 units in; frames sit 6 in with strokes at most 2 wide."""
    from synthetic_ecommerce_data.core.drawing.sheet import magnifier

    mag = magnifier(39, 49)
    assert mag is not None and not mag.handle
    assert mag.lens[0] - (mag.radius + mag.stroke) == pytest.approx(8.0)
    assert 8.0 - (6 + 2 / 2) >= 1.0


def test_a_part_just_over_the_share_in_ONE_dimension_is_drawn_plain():
    """Both dimensions must be small; each alone is not enough, and each binds.

    Width at 1/5 of the sheet (40), height at 1/6 (50).
    """
    from synthetic_ecommerce_data.core.drawing.sheet import magnifier

    assert magnifier(39, 5) is not None
    assert magnifier(41, 5) is None
    assert magnifier(5, 49) is not None
    assert magnifier(5, 300 / 6 + 0.5) is None


def test_long_thin_parts_never_get_a_lens():
    """A long drill, a long screw and a long hex key are thin but not small."""
    checked = 0
    for parent, _, record in _golden_skus():
        width, height = _drawn_size(parent["product_type"], record)
        if max(width, height) > 300 / 6 and min(width, height) < 200 / 6:
            data, _ = draw_sku(parent["product_type"], parent["brand"], record)
            assert not _has_lens(data), parent["product_id"]
            checked += 1
    assert checked > 1000


def _numbers(element: ET.Element) -> list[float]:
    import re

    if element.tag.endswith("circle"):
        return [float(element.attrib[k]) for k in ("cx", "cy", "r")]
    return [float(n) for n in re.findall(r"-?\d+\.?\d*", element.attrib.get("d", ""))]


def test_the_lens_shows_the_same_part_enlarged():
    """Every shape of the true-scale part appears in the lens, scaled about the two centres.

    Over the committed catalog's magnified SKUs: the enlarged copy has the same
    element sequence as the true-scale one, and every coordinate maps by
    ``lens + k * (p - part)`` with the layout's own ``k``.
    """
    from synthetic_ecommerce_data.core.drawing.sheet import magnifier

    checked = 0
    for parent, variant, record in _golden_skus():
        type_key = parent["product_type"]
        width, height = _drawn_size(type_key, record)
        mag = magnifier(width, height)
        if mag is None:
            continue
        data, _ = draw_sku(type_key, parent["brand"], record)
        small = _true_scale_copy(data)
        after = list(ET.fromstring(data))
        lens_at = next(
            i
            for i, e in enumerate(after)
            if e.attrib.get("fill") == LENS_COLOUR and "stroke" not in e.attrib
        )
        large = after[lens_at + 1 : lens_at + 1 + len(small)]
        assert [e.tag for e in large] == [e.tag for e in small], variant["sku"]
        for a, b in zip(small, large, strict=True):
            na, nb = _numbers(a), _numbers(b)
            assert len(na) == len(nb), variant["sku"]
            if a.tag.endswith("circle"):
                expected = [
                    mag.lens[0] + mag.k * (na[0] - mag.part[0]),
                    mag.lens[1] + mag.k * (na[1] - mag.part[1]),
                    mag.k * na[2],
                ]
                assert nb == pytest.approx(expected, abs=0.15 * mag.k + 0.15), variant["sku"]
        checked += 1
    assert checked > 100


def test_the_enlarged_part_stays_inside_the_lens():
    import math

    from synthetic_ecommerce_data.core.drawing.sheet import magnifier

    for w, h in ((5, 40), (30, 30), (20, 8), (33, 50)):
        mag = magnifier(w, h)
        if mag is not None:
            assert math.hypot(w, h) * mag.k / 2 <= mag.radius


def test_the_space_above_the_glyph_equals_the_space_below_the_part():
    from synthetic_ecommerce_data.core.drawing.sheet import (
        GLYPH_GAP,
        _glyph_extent,
        magnifier,
    )

    seen = set()
    for w, h in ((8, 30), (20, 20), (25, 15), (30, 45), (2, 43)):
        mag = magnifier(w, h)
        assert mag is not None
        seen.add(mag.handle)
        if mag.handle:
            _, left, right, bottom = _glyph_extent(mag.radius)
        else:
            outer = mag.radius + mag.stroke
            left, right, bottom = -outer, outer, outer
        glyph_top = mag.lens[1] + left
        glyph_bottom = mag.lens[1] + bottom
        part_bottom = mag.part[1] + h / 2
        assert glyph_top == pytest.approx(300 - part_bottom), (w, h)
        assert (mag.part[1] - h / 2) - glyph_bottom == pytest.approx(GLYPH_GAP)
        # The WHOLE glyph is centred, and so is the part.
        assert mag.lens[0] + (left + right) / 2 == pytest.approx(100)
        assert mag.part[0] == pytest.approx(100)
    assert seen == {True, False}


def test_the_glyph_is_in_the_brand_ink():
    """Ring, shaft and grip are stroked in the house ink -- never black, never another brand's.

    The handled glass has a shaft and a grip; the handle-less lens has neither.
    """
    s6 = {"Head Type": "Socket", "Dia./Thread Size": "#6-32", "Length": '1/4"',
          "Thread Length": '1/4"', "Head Dia.": '0.2260"', "Head Height": '0.1380"'}  # fmt: skip
    m3 = {"Size": "M3", "Inside Dia.": "3.20mm", "Outside Dia.": "7mm", "Thickness": "0.50mm"}
    for type_key, record, handles in (("screw_socket_head", s6, 2), ("washer_flat", m3, 0)):
        for brand in BRANDS:
            data, _ = draw_sku(type_key, brand, record)
            assert _has_lens(data)
            root = list(ET.fromstring(data))
            glyph = [e for e in root if e.attrib.get("stroke-linecap") == "round"]
            ring = [e for e in root if e.tag.endswith("circle") and e.attrib.get("fill") == "none"]
            assert len(glyph) == handles and len(ring) == 1, (type_key, brand)
            assert {e.attrib["stroke"] for e in [*glyph, *ring]} == {house_style(brand).ink}


def test_no_outline_is_thinner_than_the_minimum_stroke():
    """Every outline and the glyph are at least MIN_STROKE (2.3 units, ~2 px at 180 px).

    Over every committed drawing. Detail lines (flutes, threads) and the hatch
    pattern are texture, not outlines, and are the stated exemption: the
    detail lines carry ``stroke-opacity``, the hatch lives inside ``<pattern>``.
    The brand's frame is the brand's, not the part's, and is exempt too.
    """
    from synthetic_ecommerce_data.core.drawing.sheet import MIN_STROKE

    assert MIN_STROKE * 180 / 200 >= 2.0
    thinnest = 99.0
    for parent, variant, record in _golden_skus():
        data, _ = draw_sku(parent["product_type"], parent["brand"], record)
        for element in ET.fromstring(data):
            width = element.attrib.get("stroke-width")
            if width is None or "stroke-opacity" in element.attrib:
                continue
            tag = element.tag.split("}")[-1]
            if (
                tag in ("rect", "path")
                and element.attrib.get("fill") == "none"
                and not ({"stroke-linejoin", "stroke-linecap"} & set(element.attrib))
            ):
                continue  # the brand's frame (rule, rounded or corner markers)
            thinnest = min(thinnest, float(width))
            assert float(width) >= MIN_STROKE - 1e-9, (variant["sku"], element.tag, width)
    assert thinnest == pytest.approx(MIN_STROKE)


def test_a_hairline_drill_is_drawn_with_a_visible_outline():
    """Planted: HAIRLINE_DRILL (a 1/16" jobber) is drawn under 2.3 units wide at its scale."""
    for parent, variant, record in _golden_skus():
        if variant["sku"] == HAIRLINE_DRILL:
            width, _ = _drawn_size(parent["product_type"], record)
            assert width < 2.3
            data, _ = draw_sku(parent["product_type"], parent["brand"], record)
            outlines = [
                e for e in _true_scale_copy(data) if e.attrib.get("stroke-linejoin") == "round"
            ]
            assert outlines and all(float(e.attrib["stroke-width"]) >= 2.3 for e in outlines)
            return
    raise AssertionError(f"{HAIRLINE_DRILL} is not in the committed catalog")


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


#: The screw and bolt extents before the 100K catalog. An outlier length is
#: drawn broken; it never shrinks the type's scale for every other part.
PRE_100K_FASTENER_EXTENTS = {
    "screw_socket_head": (2.75, 5.95),
    "screw_flat_head": (3.7, 3.25),
    "screw_button_head": (2.56, 2.8),
    "screw_low_head": (2.75, 3.3),
    "bolt_hex": (2.85, 5.35),
}


def test_no_fastener_is_drawn_smaller_because_of_an_outlier():
    for type_key, extent in PRE_100K_FASTENER_EXTENTS.items():
        assert FIGURES[type_key][1] == extent, type_key


def test_a_part_longer_than_its_extent_is_drawn_broken_and_fits():
    """A 14-5/8" socket screw -- the 100K catalog's longest -- fits the 5.95"
    extent with two break lines, and a longer one still draws taller."""
    record = {
        "Dia./Thread Size": "3/4-10",
        "Length": '14-5/8"',
        "Length under Head": '14-5/8"',
        "Thread Length": '2-1/4"',
    }
    figure_fn, (width, height) = FIGURES["screw_socket_head"]
    long_part = figure_fn(record).figure
    x0, y0, x1, y1 = long_part.bounds()
    assert y1 - y0 <= height
    breaks = [s for s in long_part.shapes if type(s).__name__ == "Lines" and len(s.segments) == 6]
    assert len(breaks) >= 2
    shorter = dict(record, **{"Length": '10"', "Length under Head": '10"'})
    sy0, sy1 = figure_fn(shorter).figure.bounds()[1::2]
    assert sy1 - sy0 < y1 - y0, "a longer part must still draw taller"
