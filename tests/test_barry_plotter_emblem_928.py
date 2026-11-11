"""Barry Plotter's own emblem and licence line on every product of the range (gen#928).

The range of gen#925 sells its SKUs across 22 shapes, drawn like any other product of their
houses, so nothing in an image tied it to the range while each film product printed its film's
badge (gen#904). These tests read every range SKU's own image and find its motif's emblem on the
product and in the licence line, "Licensed from Barry Plotter Studios", beside the logo; and read
every film SKU's image and find its own film's emblem still there. Since gen#942 each motif has an
emblem of its own (:mod:`barry_plotter_emblems`), and the range sells 15 motifs.
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

STUDIO = "Barry Plotter Studios"
#: The range's SKUs on the default build: 75 per motif for 15 motifs, and 8 more from the two
#: kids' hoodies the build also sells in a second color (gen#942; gen#925 sold 608 for 8 motifs).
RANGE_SKUS = 1133


def _motif_of(title: str) -> str:
    (motif,) = [m for m in barry_plotter.MOTIFS if m in title]
    return motif


_MOTIF = {r.product_id: _motif_of(r.title) for r in barry_plotter.ROWS}


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


def test_each_motif_has_its_own_emblem_and_the_range_studio() -> None:
    for motif in barry_plotter.MOTIFS:
        assert film_emblems.STUDIOS.get(motif) == STUDIO, motif
        assert film_emblems.licence_text(motif) == f"Licensed from {STUDIO}", motif
    films = {film_emblems.badge(f) for f in kids_films.FILMS}
    motifs = {film_emblems.badge(m) for m in barry_plotter.MOTIFS}
    assert len(motifs) == len(barry_plotter.MOTIFS)
    assert motifs.isdisjoint(films)


def test_the_emblem_is_chosen_for_every_range_and_film_product_and_no_other() -> None:
    for i in barry_plotter.ids():
        assert film_emblems.emblem_of_id(i) == _MOTIF[i], i
    for i in kids_films.ids():
        assert film_emblems.emblem_of_id(i) == kids_films.film_of_id(i), i
    assert film_emblems.emblem_of_id("BRD-NOT-A-RANGE-PRODUCT") is None


def test_every_shape_the_range_sells_has_a_place_for_the_badge() -> None:
    shapes = {r.shape for r in barry_plotter.ROWS}
    assert shapes - set(film_emblems.PLACES) == set()


def test_every_range_sku_image_carries_its_motifs_emblem_and_licence_line(range_images) -> None:
    assert len(range_images) == RANGE_SKUS
    for pid, svg in range_images:
        motif = _MOTIF[pid]
        badge = film_emblems.badge(motif)
        assert _emblems_in(svg) == {motif}, (pid, sorted(_emblems_in(svg)))
        product, line = svg.split('<g class="brand">')
        assert badge in product, pid  # on each item a pack draws
        assert line.count(badge) == 1, pid  # and once in the licence line
        lines = re.findall(r">(Licensed from [^<]*)<", svg)
        assert lines == [f"Licensed from {STUDIO}"], (pid, lines)


def test_every_film_sku_image_still_carries_its_own_films_emblem(catalog) -> None:
    films = [d for d in catalog if d["product_id"] in kids_films.ids()]
    images = _images(films)
    assert images
    for pid, svg in images:
        film = kids_films.film_of_id(pid)
        assert _emblems_in(svg) == {film}, (pid, sorted(_emblems_in(svg)))
        assert re.findall(r">(Licensed from [^<]*)<", svg) == [film_emblems.licence_text(film)]
