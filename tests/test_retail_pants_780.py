"""Pants as everyday underwear for women and men, and no period products in clothing (gen#780).

The catalogue sold period pants (``Womens/Lingerie/Period Pants``) and period swim bottoms
(``Womens/Swimwear/Period Swimwear``), each with an ``absorbency`` attribute, and these were the
only products whose titles said ``pants``. Men had no pants. For a live demo, the British
``pants`` should find everyday underwear: the women's styles become plain pants, a men's type
of the same size gets its own drawing, and the swim bottoms become plain bikini bottoms. The
floors and leaves are written out here, not read from the rows, so dropping rows fails this file.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import decoy_apparel, scale, type_registry

WOMENS = ("Womens", "Lingerie", "Pants")
MENS = ("Mens", "Underwear", "Pants")
SWIM_BOTTOMS = ("Womens", "Swimwear", "Bikini Bottoms")
APPAREL = set(type_registry.APPAREL_DEPARTMENTS)

#: The wording of period products: the word itself, tampons, flow levels and absorbency.
PERIOD_WORDS = re.compile(
    r"\b(period\w*|menstrua\w*|tampons?|flow|absorb\w*|absorption|leak\w*)\b", re.I
)


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _leaf(templates: list[dict], path: tuple[str, ...]) -> list[dict]:
    return [r for r in templates if tuple(r["category_path"]) == path]


def _real(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["product_id"] not in decoy_apparel.ids()]


def _clothing(templates: list[dict]) -> list[dict]:
    return [r for r in templates if set(r["department"]) & APPAREL]


def _text(r: dict) -> str:
    attrs = " ".join(f"{a['key']} {a['name']} {a['value']}" for a in r["attributes"])
    return " ".join(
        [r["title"], r["description"], " ".join(r["category_path"]), r["product_type"], attrs]
    )


def test_no_clothing_product_says_period_or_states_an_absorbency(templates):
    said = sorted(
        f"{r['product_id']} {r['title']!r}: {sorted({w.lower() for w in words})}"
        for r in _clothing(templates)
        if (words := PERIOD_WORDS.findall(_text(r)))
    )
    assert said == []
    assert [
        r["product_id"] for r in templates if any(a["key"] == "absorbency" for a in r["attributes"])
    ] == []


def test_no_period_leaf_or_type_is_left():
    paths = {r.path for s in type_registry.specs().values() for r in s.rows}
    assert ("Womens", "Lingerie", "Period Pants") not in paths
    assert ("Womens", "Swimwear", "Period Swimwear") not in paths
    assert {"period_pants", "period_swimwear"}.isdisjoint(type_registry.specs())


def test_womens_pants_are_plain_pants_in_their_own_lingerie_leaf(templates):
    rows = _leaf(templates, WOMENS)
    real = _real(rows)
    assert len(real) >= 10
    assert {r["product_type"] for r in rows} == {"Pants"}
    assert all(re.search(r"\bpants\b", r["title"], re.I) for r in rows), [r["title"] for r in rows]
    for r in real:
        keys = {a["key"] for a in r["attributes"]}
        assert {"cut", "fabric"} <= keys, r["title"]


def test_womens_pants_keep_the_knicker_drawings(templates):
    """The type needs no new art: each style is drawn as the knicker cut it states."""
    assert {r["drawing"]["shape"] for r in _leaf(templates, WOMENS)} == {"knickers"}


def test_mens_pants_are_a_leaf_of_their_own_at_about_the_womens_size(templates):
    mens, womens = _leaf(templates, MENS), _leaf(templates, WOMENS)
    assert len(_real(mens)) >= 10
    assert {r["product_type"] for r in mens} == {"Mens Pants"}
    assert all(re.search(r"\bpants\b", r["title"], re.I) for r in mens), [r["title"] for r in mens]
    skus = sum(len(r["skus"]) for r in mens)
    assert 0.7 <= skus / sum(len(r["skus"]) for r in womens) <= 1.4, skus


def test_mens_pants_have_a_drawing_no_other_type_uses(templates):
    shapes = {r["drawing"]["shape"] for r in _leaf(templates, MENS)}
    assert shapes == {"mens_pants"}
    others = {r["drawing"]["shape"] for r in templates if tuple(r["category_path"]) != MENS}
    assert "mens_pants" not in others


def test_the_swim_bottoms_are_plain_bikini_bottoms_that_keep_their_cut(templates):
    real = _real([r for r in _leaf(templates, SWIM_BOTTOMS) if r["product_type"] == "Swim Bottoms"])
    assert len(real) == 4
    assert all("Swim Bottoms" in r["title"] for r in real), [r["title"] for r in real]
    assert {
        v for r in real for a in r["attributes"] if a["key"] == "cut" for v in [a["value"]]
    } == {
        "Bikini",
        "High-Waisted",
    }
    assert {r["drawing"]["shape"] for r in real} == {"swim_bottoms"}


def test_every_real_product_titled_pants_is_underwear(templates):
    """A search for ``pants`` meets the two underwear leaves and nothing else of its own kind."""
    leaves = {
        tuple(r["category_path"])
        for r in _real(templates)
        if re.search(r"\bpants\b", r["title"], re.I)
    }
    assert leaves == {WOMENS, MENS}
