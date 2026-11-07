"""The merchandise of twelve invented kids' films, named only in the product text (gen#887, #905).

A film's name is a phrase a shopper types (``plaything story mug``) that no structured field
holds: the products keep their makers' brands, no series and their types' categories. These tests
pin the film list, that no film name sits in a brand, series or category field anywhere in the
catalogue, that every film sells in five categories or more with a grocery item among them, that
every description calls the film a movie, that each film has a product named in its description
only, and that each SKU draws its own picture in code.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    kids_films,
    sale_share,
    scale,
)

FILMS = (
    "Plaything Story",
    "Lovely and the Beast",
    "Duck Run",
    "Really Cold",
    "Little Tiny Queen",
    "Home Without Anybody",
    "The Blue Balloon",
    "The Toy Movie",
    "Frozen Story",
    "The Home Run",
    "The Lady in High Heels",
    "The Haunted Dollhouse",
)
#: The fewest categories (leaves) each film sells in.
MIN_CATEGORIES = 5


@pytest.fixture(scope="module")
def catalog() -> list[dict]:
    return scale.templates()


def _names(doc: dict, film: str) -> bool:
    text = f"{doc['title']} {doc['description']}"
    return re.search(rf"\b{re.escape(film)}\b", text, re.IGNORECASE) is not None


def _of(catalog: list[dict], film: str) -> list[dict]:
    return [d for d in catalog if _names(d, film)]


def test_the_film_list_is_the_twelve_invented_films() -> None:
    assert tuple(kids_films.FILMS) == FILMS


def test_no_film_name_is_in_a_brand_series_or_category_field(catalog) -> None:
    named = {d["product_id"]: kids_films.structured_names(d) for d in catalog}
    assert {p: n for p, n in named.items() if n} == {}


def test_structured_names_finds_a_film_in_each_field() -> None:
    """The guard above can fail: a film in the brand, the series, the path or the leaf is found."""
    plain = {"brand": "Little Fernby", "category_path": ["Kids", "Tops"], "category_leaf": "Tops"}
    assert kids_films.structured_names(plain) == []
    assert kids_films.structured_names({**plain, "brand": "Duck Run Toys"}) == ["Duck Run"]
    assert kids_films.structured_names({**plain, "product_line": "Really Cold"}) == ["Really Cold"]
    leaf = {**plain, "category_leaf": "The Blue Balloon"}
    assert kids_films.structured_names(leaf) == ["The Blue Balloon"]


def test_only_the_film_rows_name_a_film(catalog) -> None:
    named = {d["product_id"] for f in FILMS for d in _of(catalog, f)}
    assert named == kids_films.ids()


@pytest.mark.parametrize("film", FILMS)
def test_each_film_sells_in_five_categories_and_a_grocery_one(catalog, film) -> None:
    docs = _of(catalog, film)
    leaves = {d["category_leaf"] for d in docs}
    assert len(leaves) >= MIN_CATEGORIES, sorted(leaves)
    assert any(d["category_path"][0] == "Food & Drink" for d in docs), sorted(leaves)


@pytest.mark.parametrize("film", FILMS)
def test_every_description_calls_the_film_a_movie_and_no_title_does(catalog, film) -> None:
    for d in _of(catalog, film):
        assert kids_films.called_a_movie(film).lower() in d["description"].lower(), d["product_id"]
        assert kids_films.MOVIE not in d["title"].lower().replace(film.lower(), ""), d["product_id"]


@pytest.mark.parametrize("film", FILMS)
def test_each_film_has_a_product_named_in_its_description_only(catalog, film) -> None:
    docs = _of(catalog, film)
    only = [d["product_id"] for d in docs if film.lower() not in d["title"].lower()]
    titled = [d["product_id"] for d in docs if film.lower() in d["title"].lower()]
    assert only and titled, (only, titled)
    assert set(only) <= kids_films.DESCRIPTION_ONLY


def test_a_blue_balloon_product_with_a_color_sells_blue(catalog) -> None:
    """Its title names Blue, so the product carries it: the text and the color field agree."""
    for d in _of(catalog, "The Blue Balloon"):
        if d.get("color_options") and "blue" in d["title"].lower():
            assert "Blue" in [c["color"] for c in d["color_options"]], d["product_id"]


def test_film_products_have_ordinary_skus_and_variants(catalog) -> None:
    docs = [d for d in catalog if d["product_id"] in kids_films.ids()]
    assert len(docs) == len(kids_films.ROWS)
    assert all(d["skus"] for d in docs)
    assert sum(len(d["skus"]) > 1 for d in docs) >= len(docs) // 2


def test_film_products_keep_their_authored_colors(catalog) -> None:
    """They stay out of the main-color pass, so no other style's copied color moves when a film
    product is added."""
    by_id = {d["product_id"]: d for d in catalog}
    for row in kids_films.ROWS:
        doc = by_id[row.product_id]
        colors = [c["color"] for c in doc.get("color_options") or ()]
        assert colors == ([] if row.colorless else [c[0] for c in row.colors]), row.product_id


def test_the_films_carry_their_own_sale_share(catalog) -> None:
    """Their sale comes from a pass of their own (gen#905): in each people department the film
    SKUs on sale reach the department's share, so the films do not thin it."""
    films = [d for d in catalog if d["product_id"] in kids_films.ids()]
    for dept in {sale_share.department(d) for d in films} - {None}:
        docs = [d for d in films if sale_share.department(d) == dept]
        total = sum(d["sku_count"] for d in docs)
        held = sum(d["sku_count"] for d in docs if "was_price" in d)
        assert held >= sale_share.SHARE[dept] * total, (dept, held, total)
    assert not any("was_price" in d for d in films if sale_share.department(d) is None)


def test_every_film_sku_draws_its_own_picture_in_code(catalog) -> None:
    recs = [d for d in catalog if d["product_id"] in kids_films.ids()]
    ids = [export.image_id(r, s) for r in recs for s in r["skus"]]
    assert len(set(ids)) == len(ids)
    files = dict(image_release.image_files(recs))
    assert {image_release.member_path(i) for i in ids} == set(files)
    for name, svg in files.items():
        text = svg.decode()
        assert text.startswith("<svg") and "<path" in text, name
        assert "<image" not in text and "href=" not in text, name


#: The other products of the types the films join, as main built them before the films came
#: (tests/data/kids_films_887_neighbors.json). A film row in a decoy, main-color or sale pass
#: would move one of them.
NEIGHBORS = Path(__file__).parent / "data" / "kids_films_887_neighbors.json"
NEIGHBOR_FIELDS = (
    "title", "brand", "category_path", "sku_count", "price_min", "price_max", "was_price",
)


def test_the_other_products_of_the_joined_types_are_what_they_were_on_main(catalog) -> None:
    pinned = json.loads(NEIGHBORS.read_text())
    types = set(pinned["product_types"])
    got = {
        d["product_id"]: {
            **{f: d.get(f) for f in NEIGHBOR_FIELDS},
            "colors": [c["color"] for c in d.get("color_options") or ()],
        }
        for d in catalog
        if d["product_type"] in types and d["product_id"] not in kids_films.ids()
    }
    new = sorted(set(got) - set(pinned["products"]))
    assert all(pid.startswith("BRD-STK") for pid in new), new
    assert {pid: got[pid] for pid in pinned["products"]} == pinned["products"]
