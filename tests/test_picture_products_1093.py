"""gen#1093: step 2 makes a product of our own for a picture of every drawn type.

``book.TYPES`` described 10 of the 28 types ``drawings`` draws, so a picture of the other 18 (a
bookcase, a rug, a faucet, a fountain, ...) made no product. The fixture manifest
(``tests/fixtures/picture_products_1093/manifest.jsonl``) is written in the generator's own
drawing vocabulary only: two rows of every type in ``picture_manifest.TYPES``, one with each
part at its last drawn value and the shape's nominal proportions, one with each part at its
first value and narrower proportions, under random hex image ids. No benchmark data is in it.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data import picture_manifest as manifest
from synthetic_ecommerce_data.domains.retail import real_brands
from synthetic_ecommerce_data.picture_products import book, load_file, write

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "picture_products_1093" / "manifest.jsonl"

#: The store department each drawn type is filed under: the issue's 2026-11-21 table.
DEPARTMENT_OF = {
    **dict.fromkeys(("garden_statue", "fountain"), "Garden"),
    "office_chair": "Office & School",
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


def test_the_book_describes_every_type_the_manifest_names():
    assert len(manifest.TYPES) == 28
    assert sorted(book.TYPES) == sorted(manifest.TYPES)


def test_each_type_is_filed_under_the_department_the_issue_maps_it_to():
    for type_, tb in book.TYPES.items():
        assert tb.path[0] == DEPARTMENT_OF.get(type_, "Home"), type_
        assert tb.path[-1] and len(tb.path) >= 3, type_


def test_a_picture_of_every_drawn_type_makes_one_product(pictures, products):
    assert len(pictures) == len(products) == 56
    assert Counter(p.doc["drawing"]["shape"] for p in products) == dict.fromkeys(manifest.TYPES, 2)
    for picture, p in zip(pictures, products, strict=True):
        tb = book.TYPES[picture.type]
        assert p.doc["category_path"] == list(tb.path), picture.type
        assert p.doc["product_type"] == tb.product_type, picture.type
        assert re.fullmatch(r"BRD-PC[0-9A-F]{8}", p.doc["product_id"]), p.doc["product_id"]
        assert p.doc["sku_count"] == 1 and p.doc["price"] >= 9, picture.type


def test_each_products_attributes_state_the_parts_its_picture_draws(pictures, products):
    assert len(products) == 56
    for picture, p in zip(pictures, products, strict=True):
        attrs = _attrs(p.doc)
        drawn = p.doc["drawing"].get("params", {})
        assert set(drawn) == set(manifest.TYPES[picture.type]), picture.type
        for part, value in picture.parts:
            assert drawn[part] == value, (picture.type, part)
            if manifest.is_count(picture.type, part):
                key = f"{book.COUNTS[part][0].lower()}_count"
                assert attrs[key] == value, (picture.type, key)
            else:
                key = book.KEYS.get(part, part)
                assert attrs[key] == value.replace("_", " ").title(), (picture.type, key)


def test_a_cabinet_pulls_size_is_its_own_key_not_a_skus_size_option(products):
    pulls = [p for p in products if p.doc["drawing"]["shape"] == "cabinet_pull"]
    assert len(pulls) == 2
    for p in pulls:
        attrs = _attrs(p.doc)
        assert "size" not in attrs and attrs["pull_size"] in {"Small", "Large"}


def test_each_measured_size_is_in_the_types_range(pictures, products):
    assert len(products) == 56
    for picture, p in zip(pictures, products, strict=True):
        tb = book.TYPES[picture.type]
        attrs = _attrs(p.doc)
        w, h, d = (int(attrs[k]) for k in ("item_width", "item_height", "item_depth"))
        assert tb.width[0] <= w <= tb.width[1], (picture.type, w)
        assert tb.height[0] <= h <= tb.height[1], (picture.type, h)
        assert tb.depth[0] <= d <= tb.depth[1], (picture.type, d)


def test_a_title_holds_the_words_of_each_part_the_book_words(pictures, products):
    assert len(products) == 56
    worded = 0
    for picture, p in zip(pictures, products, strict=True):
        for part, value in dict(picture.parts).items():
            word = book.TITLE_WORDS.get((picture.type, part), {}).get(value)
            if word:
                worded += 1
                assert word in p.doc["title"], (picture.type, part, p.doc["title"])
    assert worded >= 40
    titles = {p.doc["title"] for p in products}
    assert not [t for t in titles if re.search(r"\d (Sink|Handle|Basin) ", t)], titles


def test_the_title_and_description_are_worded_from_the_generators_own_book(products):
    assert len(products) == 56
    words = set(GLUE)
    for brand, ranges in book.RANGES.items():
        words |= {*brand.split(), *(w for r in ranges for w in r.split())}
    for tb in book.TYPES.values():
        nouns = [tb.noun] if isinstance(tb.noun, str) else list(tb.noun[1].values())
        words |= {w for n in nouns for w in n.split()}
    for table in book.TITLE_WORDS.values():
        words |= {w for v in table.values() for w in v.split()}
    words |= {w for pair in (*book.COUNTS.values(), *book.COUNTS_OF.values()) for w in pair}
    words |= {w for n in book.NAMES.values() for w in n.split()}
    words |= {w for c in manifest.COLORS for w in c.split()}
    for table in manifest.TYPES.values():
        values = (v for vs in table.values() for v in vs)
        words |= {*table, *(w for v in values for w in re.split(r"[_ ]", v))}
    words |= {w.lower() for w in words} | {w.capitalize() for w in words}
    for p in products:
        for text in (p.doc["title"], p.doc["description"]):
            for token in re.findall(r"[A-Za-z&]+|\d+", text):
                assert token.isdigit() or token in words, (token, text)
    assert real_brands.check(p.doc for p in products) == []


def test_a_picture_with_no_parts_gets_a_description_without_an_empty_features_list(products):
    sofas = [p for p in products if p.doc["drawing"]["shape"] == "sofa"]
    assert len(sofas) == 2
    for p in sofas:
        text = p.doc["description"]
        assert "Features" not in text and text.endswith(".") and " cm deep, in " in text, text


def test_each_product_picture_is_drawn_again_in_the_brand_finish(pictures, products):
    assert len(products) == 56
    for picture, p in zip(pictures, products, strict=True):
        unbranded = drawings.render(
            picture.type, picture.attributes(), "unbranded", product_id=picture.image_id
        )
        assert p.svg.startswith("<svg") and p.svg != unbranded, picture.type
        assert '<g class="brand">' in p.svg, picture.type
