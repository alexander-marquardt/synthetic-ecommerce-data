"""Industrial house styles: one declared row per brand; an opt-in path, off by default.

Run: ``uv run pytest prototypes/industrial_drawings/test_industrial_styles.py``.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from itertools import combinations
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import industrial_styles as hs  # noqa: E402

from synthetic_industrial_products.catalog import brands, bundle  # noqa: E402

hk = hs.hk  # the shared kit, on the path once industrial_styles is imported
GOLDEN = HERE.parents[1] / "golden-catalog"
ROWS = hs.HOUSE_STYLES

#: The drawings digest of the committed catalog this path was built against
#: (``bundle.manifest_digest`` at 3bc5173). The default render must keep it.
DRAWINGS_DIGEST = "1760830ab4834f204d606cae8909da02248a52df73dccbee1ae83cd85dd86ddf"


def _parent(product_type: str) -> tuple[dict, list[dict]]:
    facets = bundle.flat_facets(GOLDEN)
    for line in (GOLDEN / "nested.jsonl").read_text().splitlines():
        p = json.loads(line)
        if p["product_type"] == product_type:
            return p, bundle.records(p, facets)
    raise AssertionError(product_type)


# --- the table ------------------------------------------------------------------


def test_every_brand_in_the_brand_book_has_exactly_one_row() -> None:
    assert sorted(ROWS) == sorted(brands.BRANDS)
    assert len(ROWS) == 45


def test_a_brand_with_no_row_is_refused_at_render() -> None:
    p, records = _parent("end_mill_square")
    with pytest.raises(KeyError):
        hs.branded_svg(p["product_type"], "Nobody Tools", records[0], 1.0)


def test_no_two_brands_share_a_row_a_mark_or_a_lockup() -> None:
    assert hk.duplicates(ROWS.values()) == {}
    assert hk.duplicates(hs.mark_key(s) for s in ROWS.values()) == {}
    assert hk.duplicates(hs.lockup_key(s) for s in ROWS.values()) == {}


def test_any_two_brands_differ_in_at_least_five_levers() -> None:
    pairs = combinations(ROWS.items(), 2)
    close = [(a, b) for (a, sa), (b, sb) in pairs if hk.differing(sa, sb) < 5]
    assert close == []


def test_no_motif_carries_more_than_three_brands() -> None:
    assert {m: c for m, c in hk.duplicates(s.mark for s in ROWS.values()).items() if c > 3} == {}


def test_hazard_stripes_and_blueprint_paper_are_used_sparingly() -> None:
    assert sum(s.band != "none" for s in ROWS.values()) == 6
    assert sum(s.texture == "blueprint" for s in ROWS.values()) == 2


def test_every_mark_draws_in_its_colour() -> None:
    for s in ROWS.values():
        svg = hs.mark_svg(s, 0, 0, hs.MARK, s.colour)
        ET.fromstring(svg)
        assert s.colour in svg


def test_every_name_fits_its_lockup() -> None:
    for brand, s in ROWS.items():
        start = 12 if s.layout in ("title_block", "mark_above") else hs.NAME_SIZE
        size = hs.name_size(s, brand, hs.name_room(s), start)
        assert hs.text_width(s, brand, size) <= hs.name_room(s), brand


# --- the opt-in render -------------------------------------------------------------


def test_the_default_render_of_the_golden_catalog_is_byte_identical() -> None:
    """``house=False`` over every committed product rebuilds the recorded drawings."""
    facets = bundle.flat_facets(GOLDEN)
    manifest = {
        json.loads(line)["image_id"]: json.loads(line)
        for line in (GOLDEN / "images.jsonl").read_text().splitlines()
    }
    entries = []
    for line in (GOLDEN / "nested.jsonl").read_text().splitlines():
        p = json.loads(line)
        drawn = hs.render(p["product_type"], p["brand"], bundle.records(p, facets))
        for variant, data in zip(p["variants"], drawn, strict=True):
            row = manifest[variant["image_id"]]
            entries.append((bundle.member_path(row["path"]), hashlib.sha256(data).hexdigest()))
    assert len(entries) == len(manifest) == 11614
    assert bundle.content_digest(entries) == DRAWINGS_DIGEST
    assert bundle.manifest_digest(GOLDEN) == DRAWINGS_DIGEST


def test_house_true_dresses_the_drawing_and_its_only_text_is_the_brand() -> None:
    p, records = _parent("drill_jobber")
    plain = hs.render(p["product_type"], p["brand"], records)[0]
    dressed = hs.render(p["product_type"], p["brand"], records, house=True)[0]
    assert dressed != plain
    root = ET.fromstring(dressed)
    texts = [el.text for el in root.iter() if el.text and el.text.strip()]
    assert texts == [hk.cased(ROWS[p["brand"]].case, p["brand"])]


def test_two_brands_dress_one_product_without_changing_its_fill() -> None:
    """The part's fill comes from its finish or material; only paper and ink are the brand's."""
    p, records = _parent("washer_flat")
    drawn = {
        brand: hs.branded_svg(p["product_type"], brand, records[0], 1.0)
        for brand in ("Rivenhall", "Lintmoor")
    }
    fills = {}
    for brand, svg in drawn.items():
        product = svg.split('<g class="product"', 1)[1].split('<g class="brand">', 1)[0]
        own = {ROWS[brand].paper, ROWS[brand].ink}
        fills[brand] = sorted(
            set(re.findall(r'fill="(#[0-9a-f]{6})"', product)) - own - {"#ffffff"}
        )
    assert drawn["Rivenhall"] != drawn["Lintmoor"]
    assert fills["Rivenhall"] == fills["Lintmoor"] != []
