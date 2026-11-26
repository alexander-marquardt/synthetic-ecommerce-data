"""gen#1093: the wands-inspired products ship in the retail build, and pass both audits.

The WANDS persona's full picture manifest is pinned in the package
(``picture_products/pictures.jsonl``), and the retail build reads it as its ``picture_products``
source. These tests hold, on the ceiling build (seed 0):

- the pinned file is the one elastic/prism-wands drew its image set from (its sha256);
- every type a picture of the manifest shows has wands-inspired products, under a spec that names
  the source as a home the scaled build does not derive from;
- the product-split and the non-copying audits of ``tests/test_sideboard_ships_1022.py`` pass
  over every one of them;
- the per-type SKU rows that ``docs/catalogue-mix-837.md`` records for gen#1093 are the build's.

No WANDS title, description, id, category text or attribute tuple is in the manifest: its closed
schema (``picture_manifest``) holds the generator's own drawing vocabulary under opaque ids.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build  # noqa: E402
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import picture_products, scale, type_registry
from synthetic_ecommerce_data.domains.retail.type_registry import Home
from synthetic_ecommerce_data.picture_manifest import Picture
from synthetic_ecommerce_data.picture_products import book, shipped, writer
from test_sideboard_ships_1022 import copy_problems, split_problems

DOC = Path(__file__).resolve().parents[1] / "docs" / "catalogue-mix-837.md"
HOME = Home("picture_products", False)


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


@pytest.fixture(scope="module")
def pictured(ceiling) -> list[dict]:
    ids = picture_products.ids()
    return [r for r in ceiling.records if r["product_id"] in ids]


def test_the_pinned_manifest_is_the_one_the_image_set_was_drawn_from():
    assert hashlib.sha256(shipped.PINNED.read_bytes()).hexdigest() == shipped.SHA256
    rows = shipped.pictures()
    assert len(rows) == 42_994
    assert len(writer.described(rows)) == 13_373


def test_every_wands_inspired_product_ships_in_the_ceiling_build(pictured):
    assert {r["product_id"] for r in pictured} == picture_products.ids()
    assert len(pictured) == len(shipped.docs()) == 11_178


def test_every_type_a_picture_shows_has_products_under_its_mapped_path(pictured):
    shown = {p.type for p in writer.described(shipped.pictures())}
    assert shown == set(book.TYPES)
    want = {(book.TYPES[t].path, book.TYPES[t].product_type) for t in shown}
    got = {(tuple(r["category_path"]), r["product_type"]) for r in pictured}
    assert got == want
    assert len({ptype for _path, ptype in got}) == 28


def test_each_shipped_type_has_a_spec_that_homes_the_source_and_derives_none():
    ptypes = {book.TYPES[t].product_type for t in book.TYPES}
    homing = {s.product_type: s for s in type_registry.specs().values() if HOME in s.homes}
    assert set(homing) == ptypes
    assert "picture_products" in type_registry.BUILD_SOURCES


def test_the_wands_inspired_products_meet_the_output_standard(pictured):
    docs = scale.documents(scale.Scaled(pictured, {}))
    assert check_catalog(docs, text_exempt=scale.TEXT_EXEMPT) == []


def test_the_wands_inspired_products_pass_the_product_split_audit(pictured):
    assert split_problems(pictured) == []


def test_the_wands_inspired_products_pass_the_non_copying_audit(pictured):
    assert copy_problems(pictured) == []


def test_pictures_of_one_spec_make_one_product_sold_in_each_of_their_colors():
    """Two pictures whose products would share a brand, a range, a size and every part are one
    product; a third in a color it already sells adds no SKU."""
    first = writer.described(shipped.pictures())[0]
    code, brand, range_, size = writer._style(first)
    twins = []
    for n in range(200_000):
        p = Picture(f"{n:032x}", first.type, first.color, first.parts, first.proportions)
        if writer._style(p)[1:] == (brand, range_, size):
            twins.append(p)
        if len(twins) == 2:
            break
    other = next(c for c in ("White", "Black", "Grey") if c != first.color)
    group = [first, Picture(twins[0].image_id, first.type, other, first.parts, first.proportions),
             twins[1]]  # fmt: skip
    (merged,) = writer.docs(group)
    assert merged["product_id"] == f"BRD-{code}"
    assert [s["color"] for s in merged["skus"]] == [first.color, other]
    either = f"{first.color.lower()} or {other.lower()}"
    assert f" in {either}." in merged["description"]
    assert len(writer.write(group)) == 3  # the step-2 command still writes one per picture


def test_every_picture_s_color_is_sold_by_the_product_its_spec_makes():
    by_id = {d["product_id"]: d for d in shipped.docs()}
    first: dict[tuple, str] = {}
    for p in writer.described(shipped.pictures()):
        code, brand, range_, size = writer._style(p)
        key = (p.type, brand, range_, size, tuple(writer._parts(p)))
        pid = by_id[first.setdefault(key, f"BRD-{code}")]
        assert p.color in {s["color"] for s in pid["skus"]}, p.image_id


def _doc_rows() -> dict[str, int]:
    out = {}
    for line in DOC.read_text(encoding="utf-8").splitlines():
        if line.startswith("| gen#1093"):
            _issue, _dept, ptype, skus = (c.strip() for c in line.strip("|").split("|"))
            out[ptype] = int(skus.replace(",", ""))
    return out


def test_catalogue_mix_records_each_type_s_skus_as_the_build_has_them(pictured):
    skus = Counter()
    for r in pictured:
        skus[r["product_type"]] += r["sku_count"]
    assert _doc_rows() == dict(skus)
    text = DOC.read_text(encoding="utf-8")
    total = re.search(r"make ([\d,]+) products and ([\d,]+) SKUs", text)
    assert total and (total[1], total[2]) == (f"{len(pictured):,}", f"{sum(skus.values()):,}")
