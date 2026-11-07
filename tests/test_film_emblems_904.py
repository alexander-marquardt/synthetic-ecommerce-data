"""Each invented film's one emblem on every product it sells, and The Blue Balloon in many
colors (gen#904).

The films of gen#887 sell mugs, tees, stickers and cakes drawn with their types' own shapes. These
tests read every film SKU's own image and find its film's emblem in it, and no other film's; find
the licence line naming the film's studio beside the logo; find neither on the other products of
the types the films sell; and check that The Blue Balloon's colored SKUs are mostly not blue,
with each title naming its product's one color.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    film_emblems,
    image_release,
    kids_films,
    scale,
    sheet_extent,
)

#: The colors The Blue Balloon sells in, at least.
BALLOON_COLORS = {"Red", "Yellow", "White", "Green", "Blue"}


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def films(catalog) -> list[dict]:
    return [d for d in catalog if d["product_id"] in kids_films.ids()]


@pytest.fixture(scope="module")
def images(films) -> list[tuple[str, str]]:
    """``(film, svg)`` for every film SKU's own image file."""
    files = dict(image_release.image_files(films))
    member = {image_release.member_path(export.image_id(d, s)): d for d in films for s in d["skus"]}
    return [(kids_films.film_of_id(d["product_id"]), files[m].decode()) for m, d in member.items()]


def _emblems_in(svg: str) -> set[str]:
    return {f for f in kids_films.FILMS if film_emblems.badge(f) in svg}


def test_each_film_has_its_own_emblem_and_studio() -> None:
    assert set(film_emblems.STUDIOS) == set(kids_films.FILMS)
    assert len({film_emblems.badge(f) for f in kids_films.FILMS}) == len(kids_films.FILMS)
    for film, studio in film_emblems.STUDIOS.items():
        assert film.removeprefix("The ") in studio and studio.endswith(" Studios"), film


def test_every_film_sku_image_carries_its_films_emblem_and_no_other(images) -> None:
    assert images
    wrong = [(film, sorted(_emblems_in(svg))) for film, svg in images if _emblems_in(svg) != {film}]
    assert wrong == []


def test_every_film_sku_image_sets_its_studios_licence_line(images) -> None:
    for film, svg in images:
        lines = re.findall(r">(Licensed from [^<]*)<", svg)
        assert lines == [film_emblems.licence_text(film)], (film, lines)
        assert svg.count(film_emblems.badge(film)) == 2, film  # on the product and in the line


def test_the_product_is_drawn_clear_of_the_licence_line(images) -> None:
    """The product moves off the line as it does off the logo: their boxes share no row."""
    half = film_emblems.LICENCE_HEIGHT / 2
    for film, svg in images:
        product = svg[svg.index('<g class="product"') : svg.index('<g class="brand">')]
        _, y0, _, y1 = sheet_extent.reach(
            f'<svg xmlns="http://www.w3.org/2000/svg">{product}</svg>'
        )
        baseline = float(re.search(r'<text x="[\d.]+" y="([\d.]+)"[^>]*>Licensed from', svg)[1])
        center = baseline - film_emblems.LICENCE_SIZE * 0.35  # the line's middle, near enough
        assert y1 <= center - half or y0 >= center + half, (film, y0, y1, center)


def test_the_blue_balloon_emblem_is_blue_on_a_product_of_any_color(images) -> None:
    assert film_emblems.BALLOON_BLUE in film_emblems.badge("The Blue Balloon")
    balloon = [svg for film, svg in images if film == "The Blue Balloon"]
    assert balloon and all(film_emblems.badge("The Blue Balloon") in svg for svg in balloon)


def test_no_other_product_of_a_film_type_carries_an_emblem_or_a_licence(catalog) -> None:
    types = {r.product_type for r in kids_films.ROWS}
    others = [
        d for d in catalog if d["product_type"] in types and d["product_id"] not in kids_films.ids()
    ]
    assert others
    for d in others:
        svg = image_release.render(d, d["skus"][0]).decode()
        assert 'class="emblem"' not in svg and "Licensed from" not in svg, d["product_id"]


def _balloon(films) -> list[dict]:
    return [d for d in films if kids_films.film_of_id(d["product_id"]) == "The Blue Balloon"]


def test_most_of_the_blue_balloons_colored_skus_are_not_blue(films) -> None:
    colors = [s["color"] for d in _balloon(films) for s in d["skus"] if s.get("color")]
    assert set(colors) >= BALLOON_COLORS, sorted(set(colors))
    assert sum(c != "Blue" for c in colors) * 2 >= len(colors), colors


def test_each_colored_blue_balloon_product_has_one_color_its_title_names(films) -> None:
    for d in _balloon(films):
        colors = [c["color"] for c in d.get("color_options") or ()]
        if not colors:
            continue
        assert len(colors) == 1, (d["product_id"], colors)
        rest = d["title"].replace("The Blue Balloon", "")
        assert re.search(rf"\b{colors[0]}\b", rest), (d["product_id"], d["title"])
