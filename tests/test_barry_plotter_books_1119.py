"""The Barry Plotter book series, slice 2 of Books (gen#1119).

The invented franchise of gen#925 (:mod:`barry_plotter`) sold merchandise but none of the books it
is named for. The series is seven numbered volumes in three formats, a box set of the seven in
paperback and in hardback, and an illustrated hardback of book 1: 24 SKUs of the Book type. These
checks hold the slice's Done-when, and the rules of gen#925: the name is in the title and the
description only, no description says "Barry's", and a title is built from the range's own motifs.
"""

from __future__ import annotations

import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    barry_plotter,
    barry_plotter_books,
    book_brand_styles,
    brand_owners,
    film_emblems,
    house_styles,
    image_release,
    type_registry,
)

VOLUMES = 7
FORMATS = ("Ebook", "Paperback", "Hardback")
#: A numbered volume's title: the series, its number and one of the range's motifs.
VOLUME = re.compile(r"Barry Plotter, Book ([1-9]): The ([A-Z][A-Za-z ]+)")
BOX_SET = "Barry Plotter Box Set, Books 1 to 7"
#: A well-known series' title pattern, which no title may follow.
NAME_AND_THE = re.compile(r"\bBarry Plotter and\b", re.IGNORECASE)


@pytest.fixture(scope="module")
def series() -> list[dict]:
    """The build's books that name Barry Plotter."""
    return [
        r
        for r in ceiling_build().records
        if r["category_path"][0] == "Books" and "barry plotter" in r["title"].lower()
    ]


def _volumes(series: list[dict]) -> dict[int, dict]:
    found = {int(m[1]): r for r in series if (m := VOLUME.fullmatch(r["title"]))}
    assert sorted(found) == list(range(1, VOLUMES + 1))
    return found


def _formats(rec: dict) -> tuple[str, ...]:
    return tuple(s["format"] for s in rec["skus"])


def _attrs(rec: dict) -> dict[str, str]:
    return {a["key"]: a["value"] for a in rec["attributes"]}


def test_the_build_holds_the_series_and_its_24_skus(series) -> None:
    assert sum(len(r["skus"]) for r in series) == 24
    assert {r["product_id"] for r in series} == barry_plotter_books.ids()


def test_seven_numbered_volumes_are_each_sold_in_the_three_formats(series) -> None:
    for n, rec in _volumes(series).items():
        assert _formats(rec) == FORMATS, n
        prices = [s["price"] for s in rec["skus"]]
        assert prices == sorted(prices) and len(set(prices)) == 3, (n, prices)


def test_a_box_set_is_sold_in_paperback_and_hardback(series) -> None:
    boxes = [r for r in series if "Box Set" in r["title"]]
    assert [(r["title"], _formats(r)) for r in boxes] == [(BOX_SET, ("Paperback", "Hardback"))]
    (box,) = boxes
    volumes = _volumes(series).values()
    assert int(_attrs(box)["pages"]) == sum(int(_attrs(v)["pages"]) for v in volumes)
    for i, fmt in enumerate(("Paperback", "Hardback"), start=1):
        apart = sum(v["skus"][i]["price"] for v in volumes)
        assert box["skus"][i - 1]["price"] < apart, fmt


def test_one_illustrated_hardback_is_of_book_1(series) -> None:
    illustrated = [r for r in series if "Illustrated" in r["title"]]
    first = _volumes(series)[1]["title"]
    assert [(r["title"], _formats(r)) for r in illustrated] == [
        (f"{first}, Illustrated Edition", ("Hardback",))
    ]


def test_every_title_is_built_from_a_motif_of_the_range_and_echoes_no_other_series(series) -> None:
    motifs = [VOLUME.fullmatch(r["title"])[2] for r in _volumes(series).values()]
    assert set(motifs) <= set(barry_plotter.MOTIFS), motifs
    assert len(set(motifs)) == VOLUMES
    for r in series:
        assert not NAME_AND_THE.search(r["title"]), r["title"]


def test_every_description_names_the_books_and_never_the_films_or_a_possessive(series) -> None:
    assert series
    for r in series:
        assert "the Barry Plotter books" in r["description"], r["product_id"]
        assert "film" not in r["description"].lower(), r["product_id"]
        text = f"{r['title']} {r['description']}".lower()
        assert "barry's" not in text and "plotter's" not in text, r["product_id"]


def test_no_structured_field_names_the_series(series) -> None:
    assert series
    for r in series:
        assert barry_plotter.structured_names(r) == [], r["product_id"]


def test_the_series_has_one_invented_author_and_publisher_of_its_own(series) -> None:
    assert {r["brand"] for r in series} == {barry_plotter_books.PUBLISHER}
    assert {_attrs(r)["publisher"] for r in series} == {barry_plotter_books.PUBLISHER}
    assert {_attrs(r)["author"] for r in series} == {barry_plotter_books.AUTHOR}
    assert barry_plotter_books.AUTHOR not in brand_owners.table()
    other = {r.brand for r in type_registry.specs()["book"].rows if r.product_id
             not in barry_plotter_books.ids()}  # fmt: skip
    assert barry_plotter_books.PUBLISHER not in other
    assert barry_plotter_books.PUBLISHER in book_brand_styles.STYLES
    assert barry_plotter_books.PUBLISHER in house_styles.HOUSE_STYLES


def test_the_series_is_for_ages_9_to_12_in_childrens_books(series) -> None:
    assert series
    for r in series:
        assert tuple(r["category_path"]) == ("Books", "Children's Books"), r["product_id"]
        assert _attrs(r)["age_band"] == "9-12 years", r["product_id"]


def test_each_cover_prints_the_badge_of_the_motif_its_title_names(series) -> None:
    svgs = {}
    for r in series:
        svg = image_release.render(r, r["skus"][0]).decode()
        drawn = {m for m in barry_plotter.MOTIFS if film_emblems.badge(m) in svg}
        named = {m for m in barry_plotter.MOTIFS if m in r["title"]}
        assert drawn == (named or {barry_plotter_books.BOX_MOTIF}), r["title"]
        assert "Licensed from" not in svg, r["title"]  # the books are the source, not a licence
        svgs[r["product_id"]] = svg
    assert len(set(svgs.values())) == len(svgs) == 9
