"""Barry Plotter's own emblem and licence line on every product of the range (gen#928).

The range of gen#925 sells 608 SKUs across 22 shapes, drawn like any other product of their
houses, so nothing in an image tied it to the range while each film product printed its film's
badge (gen#904). These tests read every range SKU's own image and find the range's emblem on the
product and in the licence line, "Licensed from Barry Plotter Studios", beside the logo; and read
every film SKU's image and find its own film's emblem still there.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    barry_plotter,
    export,
    film_emblems,
    image_release,
    kids_films,
    scale,
)

RANGE = barry_plotter.NAME


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return scale.templates()


def _images(docs: list[dict]) -> list[tuple[str, str]]:
    """``(product id, svg)`` for every SKU's own image file of ``docs``."""
    files = dict(image_release.image_files(docs))
    member = {image_release.member_path(export.image_id(d, s)): d for d in docs for s in d["skus"]}
    return [(d["product_id"], files[m].decode()) for m, d in member.items()]


@pytest.fixture(scope="module")
def range_images(catalog) -> list[tuple[str, str]]:
    return _images([d for d in catalog if d["product_id"] in barry_plotter.ids()])


def _emblems_in(svg: str) -> set[str]:
    return {e for e in film_emblems.STUDIOS if film_emblems.badge(e) in svg}


def test_the_range_has_its_own_emblem_and_studio() -> None:
    assert film_emblems.STUDIOS.get(RANGE) == "Barry Plotter Studios"
    assert film_emblems.licence_text(RANGE) == "Licensed from Barry Plotter Studios"
    films = {film_emblems.badge(f) for f in kids_films.FILMS}
    assert film_emblems.badge(RANGE) not in films


def test_the_emblem_is_chosen_for_every_range_and_film_product_and_no_other() -> None:
    assert {film_emblems.emblem_of_id(i) for i in barry_plotter.ids()} == {RANGE}
    for i in kids_films.ids():
        assert film_emblems.emblem_of_id(i) == kids_films.film_of_id(i), i
    assert film_emblems.emblem_of_id("BRD-NOT-A-RANGE-PRODUCT") is None


def test_every_shape_the_range_sells_has_a_place_for_the_badge() -> None:
    shapes = {r.shape for r in barry_plotter.ROWS}
    assert shapes - set(film_emblems.PLACES) == set()


def test_every_range_sku_image_carries_the_range_emblem_and_licence_line(range_images) -> None:
    assert len(range_images) == 608
    for pid, svg in range_images:
        assert _emblems_in(svg) == {RANGE}, (pid, sorted(_emblems_in(svg)))
        assert svg.count(film_emblems.badge(RANGE)) == 2, pid  # on the product and in the line
        lines = re.findall(r">(Licensed from [^<]*)<", svg)
        assert lines == ["Licensed from Barry Plotter Studios"], (pid, lines)


def test_every_film_sku_image_still_carries_its_own_films_emblem(catalog) -> None:
    films = [d for d in catalog if d["product_id"] in kids_films.ids()]
    images = _images(films)
    assert images
    for pid, svg in images:
        film = kids_films.film_of_id(pid)
        assert _emblems_in(svg) == {film}, (pid, sorted(_emblems_in(svg)))
        assert re.findall(r">(Licensed from [^<]*)<", svg) == [film_emblems.licence_text(film)]
