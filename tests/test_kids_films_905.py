"""Five invented films whose names hold a category word sell nothing in that category (gen#905).

``the toy movie``, ``frozen story``, ``the home run``, ``the lady in high heels`` and ``the haunted
dollhouse`` each hold a word a category holds (Toys, Frozen, Home and Running Shoes, Heels, Dolls'
Houses). The films' products sit in other categories, so a search for the name that became a
category filter would lose them all. These tests check that no film product's category path holds
a word its film's name names, that each such word is a category of the catalogue (so the check
is not empty), and that each film sells 25 to 35 SKUs, as the films of gen#887 do.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import kids_films, scale

NEW_FILMS = (
    "The Toy Movie",
    "Frozen Story",
    "The Home Run",
    "The Lady in High Heels",
    "The Haunted Dollhouse",
)
#: The SKUs each new film sells, the range of gen#887's films (26 to 37).
SKUS = range(25, 36)


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return scale.templates()


def _film_docs(catalog: list[dict], film: str) -> list[dict]:
    by_id = {r.product_id: kids_films.film_of(r) for r in kids_films.ROWS}
    return [d for d in catalog if by_id.get(d["product_id"]) == film]


def _path(doc: dict) -> str:
    return " > ".join(doc["category_path"]).lower()


def test_the_named_films_are_the_five_new_ones() -> None:
    assert tuple(kids_films.NAMED_CATEGORIES) == NEW_FILMS
    assert tuple(kids_films.FILMS)[-5:] == NEW_FILMS


@pytest.mark.parametrize("film", NEW_FILMS)
def test_each_named_word_is_a_category_of_the_catalogue(catalog, film) -> None:
    """The check below is not empty: each word names categories other products sell in."""
    paths = {_path(d) for d in catalog}
    for word in kids_films.NAMED_CATEGORIES[film]:
        assert any(word in p for p in paths), word


@pytest.mark.parametrize("film", NEW_FILMS)
def test_no_film_sells_in_the_category_its_name_names(catalog, film) -> None:
    docs = _film_docs(catalog, film)
    assert docs
    words = kids_films.NAMED_CATEGORIES[film]
    inside = {d["product_id"]: _path(d) for d in docs if any(w in _path(d) for w in words)}
    assert inside == {}


@pytest.mark.parametrize("film", NEW_FILMS)
def test_each_new_film_sells_25_to_35_skus(catalog, film) -> None:
    docs = _film_docs(catalog, film)
    counts = {d["product_id"]: len(d["skus"]) for d in docs}
    assert sum(counts.values()) in SKUS, counts
