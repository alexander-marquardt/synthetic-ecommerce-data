"""Books, slice 1 (gen#1119): a department of invented titles in three formats.

The retail catalogue had no books: Bookcase and E-reader were the only book-related types. The
maintainer's ruling (2026-11-21) asks for about 1,500 SKUs of invented titles in hardback,
paperback and ebook, whose words collide with other departments ('The Book of Chocolate' beside
the chocolate bars), so a search has to tell a book from the thing the book is about. Slice 1
adds the department (``core/departments.RETAIL``) and its one type, Book
(``type_specs/book.py``), whose rows :mod:`books_rows` builds and :mod:`kit_books` draws. These
checks hold the slice's Done-when: the department is on the closed list, the ceiling build holds
at least 1,400 book SKUs, each title is sold in exactly the three formats, each carries the
issue's attributes (an age band on a children's title only), its id is our own and not an ISBN,
no author is a brand, at least 30 titles collide with a type of another department in the
build (the ruling's three among the titles), and every title of a leaf draws its own cover.
"""

from __future__ import annotations

import collections
import importlib
import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import departments
from synthetic_ecommerce_data.domains.retail import (
    barry_plotter,
    barry_plotter_books,
    brand_owners,
    kit,
    scale,
    type_registry,
)
from synthetic_ecommerce_data.domains.retail import departments as retail_departments

ROOT = "Books"
#: The issue's floor at the ceiling build: 480 titles in 3 formats, less a margin.
FLOOR = 1_400
FORMATS = ("Ebook", "Paperback", "Hardback")
#: Every title carries these; a children's title carries ``age_band`` as well.
KEYS = {"author", "publisher", "genre", "pages", "publication_year"}
CHILDRENS = "Children's Books"
#: The ruling's three collision titles (2026-11-21): each must be a title.
RULED = ("The Book of Chocolate", "How to Make Brownies", "Learn to Sew")
#: An ISBN-10 or ISBN-13 shape: 10 or 13 digits, perhaps hyphenated, or a 978/979 prefix.
ISBN = re.compile(r"(97[89][-\s]?)?\d[-\s]?\d{2,5}[-\s]?\d{2,7}[-\s]?[\dX]$|\d{10}|\d{13}")


def _rows_module():
    return importlib.import_module("synthetic_ecommerce_data.domains.retail.books_rows")


def _spec() -> type_registry.TypeSpec:
    specs = type_registry.specs()
    # An assertion, not a KeyError, so a build without the Book type fails as a red test.
    assert "book" in specs, "no 'book' type spec is registered"
    return specs["book"]


@pytest.fixture(scope="module")
def books() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


def test_the_department_is_on_the_closed_list() -> None:
    assert ROOT in departments.RETAIL
    assert ROOT in retail_departments.RETAIL


def test_the_ceiling_build_holds_the_slice_floor_of_book_skus(books) -> None:
    skus = sum(r["sku_count"] for r in books)
    assert skus >= FLOOR, skus


def test_every_title_is_sold_in_exactly_the_three_formats_cheapest_first() -> None:
    # The Barry Plotter series has a box set and an illustrated edition in fewer formats;
    # tests/test_barry_plotter_books_1119.py checks it.
    rows = [r for r in _spec().rows if r.product_id not in barry_plotter_books.ids()]
    assert len(rows) == 480
    for row in rows:
        assert row.size_key == "format", row.code
        assert tuple(s for s, _ in row.sizes) == FORMATS, row.code
        prices = [p for _, p in row.sizes]
        assert prices == sorted(prices) and len(set(prices)) == 3, (row.code, prices)
        assert all(f"{p:.2f}".endswith(".99") for p in prices), (row.code, prices)


def test_every_title_carries_the_issue_attributes_and_an_age_band_only_for_children() -> None:
    for row in _spec().rows:
        keys = {a[0] for a in row.attrs}
        assert keys >= KEYS, (row.code, sorted(KEYS - keys))
        attrs = {a[0]: a[2] for a in row.attrs}
        assert attrs["publisher"] == row.brand, row.code
        assert ("age_band" in keys) == (row.path[-1] == CHILDRENS), row.code
        assert 2015 <= int(attrs["publication_year"]) <= 2026, row.code


def test_ids_and_titles_are_unique_and_no_id_is_an_isbn() -> None:
    rows = _spec().rows
    ids = [r.product_id for r in rows]
    titles = [r.title for r in rows]
    assert len(ids) == len(set(ids))
    assert len(titles) == len(set(titles)), [
        t for t, n in collections.Counter(titles).items() if n > 1
    ]
    for pid in ids:
        assert not ISBN.search(pid.removeprefix("BRD-")), pid


def test_no_author_is_a_brand() -> None:
    brands = set(brand_owners.table())
    authors = {a[2] for r in _spec().rows for a in r.attrs if a[0] == "author"}
    assert authors and not authors & brands, sorted(authors & brands)


def test_the_ruling_titles_are_among_the_titles() -> None:
    titles = {r.title for r in _spec().rows}
    assert set(RULED) <= titles, sorted(set(RULED) - titles)


def test_thirty_titles_collide_with_a_type_of_another_department_in_the_build() -> None:
    collisions = _rows_module().COLLISIONS
    titles = {r.title for r in _spec().rows}
    by_type: dict[str, list[str]] = collections.defaultdict(list)
    for rec in ceiling_build().records:
        if rec["category_path"][0] != ROOT:
            by_type[rec["product_type"]].append(rec["title"].lower())
    held = []
    for title, ptype, word in collisions:
        assert title in titles, title
        pattern = re.compile(rf"\b{re.escape(word.lower())}\b")
        assert pattern.search(title.lower()), (title, word)
        if any(pattern.search(t) for t in by_type.get(ptype, ())):
            held.append(title)
    assert len(set(held)) >= 30, (
        len(set(held)),
        sorted(set(t for t, _, _ in collisions) - set(held)),
    )


def test_every_title_of_a_leaf_draws_its_own_cover() -> None:
    by_leaf: dict[tuple[str, ...], set[str]] = collections.defaultdict(set)
    n: collections.Counter = collections.Counter()
    for row in _spec().rows:
        c = row.colors[0]
        svg = kit.render(row.shape, kit.Fill(c[1], c[2], c[3]), params=dict(row.params))
        by_leaf[row.path].add(svg)
        n[row.path] += 1
    for leaf, svgs in by_leaf.items():
        assert len(svgs) == n[leaf], (leaf, n[leaf] - len(svgs))


@pytest.mark.parametrize("param,a,b", [("layout", "0", "3"), ("genre", "cookery", "travel")])
def test_each_cover_param_changes_the_drawing(param, a, b) -> None:
    _rows_module()
    fill = kit.Fill("solid", "#2f6b45")
    assert kit.render("book_cover", fill, params={param: a}) != kit.render(
        "book_cover", fill, params={param: b}
    )


def test_few_book_styles_share_a_results_grid_tile(books) -> None:
    report = scale.grid_clones(books)
    assert report["grid_clones"] == 0, report


def test_no_book_word_takes_a_range_word_of_a_derived_family() -> None:
    """A word that any template's text uses is no derived model's range (#851): a book title or
    blurb that used 'Craft' or 'Spice' would rename the derived jeans or kitchen ranges. A word the
    Barry Plotter merchandise already uses (gen#925: 'Moonlit', 'Bramble') takes no more."""
    from synthetic_ecommerce_data.domains.retail import line_grammar

    def words_of(rows) -> set[str]:
        out: set[str] = set()
        for r in rows:
            values = " ".join(str(a[2]) for a in r.attrs)
            text = f"{r.title} {r.description} {r.brand} {values}".lower()
            out.update(re.findall(r"[a-z]+", text))
        return out

    own = [r for r in _spec().rows if r.product_id in barry_plotter_books.ids()]
    rest = [r for r in _spec().rows if r.product_id not in barry_plotter_books.ids()]
    words = words_of(rest) | (words_of(own) - words_of(barry_plotter.ROWS))
    hits = {
        fam: [w for w in (*spec.leads, *spec.grocery_leads) if w.lower() in words]
        for fam, spec in line_grammar._NUMBERED.items()
    }
    assert not {f: h for f, h in hits.items() if h}
