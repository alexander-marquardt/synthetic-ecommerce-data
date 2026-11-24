"""Step 2 of gen#1022: a product of our own around each picture of a manifest.

The fixture manifest (``tests/fixtures/picture_products_1022/manifest.json``) is made from the
generator's own drawing vocabulary: twelve pictures of the slice 1 and 2 furniture shapes, under
random hex image ids. No benchmark data is anywhere in it. Pinned here: Done-when 5 (each picture
yields a product whose attributes describe it, and whose title, description and measured values
are the generator's own), Done-when 7 (the loader refuses a free-text field and an
out-of-vocabulary value; the import test) and Done-when 8 (no product, SKU or image file name holds
an image id, and each product's picture differs from the same figure's ``unbranded`` picture).
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data import picture_manifest as manifest
from synthetic_ecommerce_data.domains.retail import real_brands
from synthetic_ecommerce_data.picture_products import __main__ as cli
from synthetic_ecommerce_data.picture_products import book, load, load_file, write

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "picture_products_1022" / "manifest.json"
PACKAGE = ROOT / "src" / "synthetic_ecommerce_data" / "picture_products"
ROW = {
    "image_id": "0f1e2d3c4b5a6978",
    "type": "sideboard",
    "color": "Natural",
    "parts": {"doors": 2, "drawers": 3, "legs": "tapered"},
    "proportions": {"height_per_width": 0.5, "depth_per_width": 0.27},
}
#: The words a title or a description may hold besides the book's own and the numbers.
GLUE = {"The", "from", "cm", "wide", "high", "and", "deep", "in", "Features", "no"}


@pytest.fixture(scope="module")
def pictures():
    return load_file(FIXTURE)


@pytest.fixture(scope="module")
def products(pictures):
    return write(pictures)


def _attrs(doc: dict) -> dict[str, str]:
    return {a["key"]: a["value"] for a in doc["attributes"]}


def _refused(row) -> str | None:
    """The loader's refusal of ``row``, or None when it takes it."""
    try:
        load([row])
    except ValueError as e:
        return str(e)
    return None


def test_the_fixture_manifest_yields_one_product_per_picture(pictures, products):
    assert len(pictures) == len(products) == 12
    assert [p.type for p in pictures] == [p.doc["drawing"]["shape"] for p in products]
    for p in products:
        doc = p.doc
        assert re.fullmatch(r"BRD-PC[0-9A-F]{8}", doc["product_id"]), doc["product_id"]
        assert doc["brand"] in book.RANGES
        assert doc["product_line"] in book.RANGES[doc["brand"]]
        assert doc["sku_count"] == 1 and doc["price"] > 0


def test_the_attributes_describe_the_picture(pictures, products):
    assert len(pictures) == len(products) == 12
    for picture, p in zip(pictures, products, strict=True):
        doc, attrs = p.doc, _attrs(p.doc)
        assert doc["category_path"] == list(book.TYPES[picture.type].path)
        assert [s["color"] for s in doc["skus"]] == [picture.color]
        assert doc["drawing"]["base"] == manifest.COLORS[picture.color]
        drawn = doc["drawing"]["params"]
        assert set(drawn) == set(manifest.TYPES[picture.type]), picture.type
        for part, value in picture.parts:
            assert drawn[part] == value, (picture.type, part)
            if manifest.is_count(picture.type, part):
                key = f"{book.COUNTS[part][0].lower()}_count"
                assert attrs[key] == value, (picture.type, key)
            else:
                assert attrs[part] == value.replace("_", " ").title(), (picture.type, part)


def test_the_measured_size_is_the_generators_own_at_the_drawn_proportions(pictures, products):
    assert len(pictures) == len(products) == 12
    for picture, p in zip(pictures, products, strict=True):
        tb, attrs = book.TYPES[picture.type], _attrs(p.doc)
        w, h, d = (int(attrs[f"item_{k}"]) for k in ("width", "height", "depth"))
        assert tb.width[0] <= w <= tb.width[1], (picture.type, w)
        assert tb.height[0] <= h <= tb.height[1], (picture.type, h)
        assert tb.depth[0] <= d <= tb.depth[1], (picture.type, d)
        rh, rd = picture.proportions
        assert abs(h - w * rh) <= 1, (picture.type, w, h, rh)
        assert abs(d - w * rd) <= 1, (picture.type, w, d, rd)


def test_the_title_and_description_are_worded_from_the_generators_own_book(products):
    assert len(products) == 12
    words = set(GLUE)
    for brand, ranges in book.RANGES.items():
        words |= {*brand.split(), *(w for r in ranges for w in r.split())}
    for tb in book.TYPES.values():
        nouns = [tb.noun] if isinstance(tb.noun, str) else list(tb.noun[1].values())
        words |= {w for n in nouns for w in n.split()}
    for table in book.TITLE_WORDS.values():
        words |= {w for v in table.values() for w in v.split()}
    words |= {w for pair in book.COUNTS.values() for w in pair}
    words |= {w for n in book.NAMES.values() for w in n.split()}
    words |= {w for c in manifest.COLORS for w in c.split()}
    for table in manifest.TYPES.values():
        words |= {*table, *(w for vs in table.values() for v in vs for w in v.split("_"))}
    words |= {w.lower() for w in words} | {w.capitalize() for w in words}
    for p in products:
        for text in (p.doc["title"], p.doc["description"]):
            for token in re.findall(r"[A-Za-z&]+|\d+", text):
                assert token.isdigit() or token in words, (token, text)
    assert real_brands.check(p.doc for p in products) == []


@pytest.mark.parametrize(
    ("change", "named"),
    [
        ({"title": "Mid Century Sideboard"}, "title"),
        ({"description": "A sideboard."}, "description"),
        ({"color": "Teal"}, "Teal"),
        ({"type": "sofa_bed"}, "sofa_bed"),
        ({"parts": {"doors": 7}}, "doors"),
        ({"parts": {"doors": "3"}}, "doors"),
        ({"parts": {"legs": "cabriole"}}, "cabriole"),
        ({"parts": {"handles": "brass"}}, "handles"),
        ({"proportions": {"height_per_width": 0.333}}, "height_per_width"),
        ({"proportions": {"depth_per_width": 25}}, "depth_per_width"),
        ({"proportions": {"length_per_width": 2.0}}, "length_per_width"),
        ({"image_id": "Oak Sideboard 72in"}, "image_id"),
    ],
)
def test_a_row_outside_the_closed_schema_is_refused(change, named):
    assert _refused(ROW) is None
    message = _refused({**ROW, **change})
    assert message is not None and named in message, (change, message)


def test_a_missing_field_or_a_repeated_image_id_is_refused():
    assert _refused({k: v for k, v in ROW.items() if k != "color"}) is not None
    with pytest.raises(ValueError, match="repeated"):
        load([ROW, ROW])


def test_step_2_imports_nothing_named_for_the_benchmark_and_step_1_does_not_import_step_2():
    imported: set[str] = set()
    for path in PACKAGE.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported |= {f"{node.module}.{a.name}" for a in node.names}
    assert imported, "the walk found the package's imports"
    assert not [m for m in imported if "wands" in m.lower()], imported
    code = (
        "import sys; import synthetic_ecommerce_data.drawings; "
        "print(sorted(m for m in sys.modules if 'picture_products' in m or 'wands' in m))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]", out.stdout


def test_no_product_sku_or_picture_name_holds_an_image_id(pictures, products):
    assert len(pictures) == len(products) == 12
    ids = [p.image_id for p in pictures]
    for p in products:
        text = json.dumps(p.doc) + p.image_name
        assert not [i for i in ids if i in text], p.doc["product_id"]
        assert p.image_name == f"{p.doc['product_id']}.svg"


def test_each_product_picture_differs_from_the_same_figures_unbranded_picture(pictures, products):
    assert len(pictures) == len(products) == 12
    for picture, p in zip(pictures, products, strict=True):
        unbranded = drawings.render(
            picture.type, picture.attributes(), "unbranded", product_id=picture.image_id
        )
        assert p.svg.startswith("<svg") and p.svg != unbranded, picture.image_id
        assert '<g class="brand">' in p.svg and '<g class="brand">' not in unbranded


def test_the_entry_point_writes_the_products_and_their_pictures(tmp_path, products):
    assert len(products) == 12
    assert cli.main([str(FIXTURE), str(tmp_path)]) == 0
    lines = (tmp_path / "products.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line) for line in lines] == [p.doc for p in products]
    names = sorted(f.name for f in (tmp_path / "images").iterdir())
    assert names == sorted(p.image_name for p in products)
    first = products[0]
    assert (tmp_path / "images" / first.image_name).read_text(encoding="utf-8") == first.svg
