"""Grape Computer's and SingingSam's own accessories, and the rows that name their phones (#724).

The shape is what shoppers see for a popular phone: the maker's own accessory beside compatible
ones from other brands. ``real_brands.check`` runs over the ceiling build, not the templates alone.
"""

from __future__ import annotations

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import house_styles, real_brands, scale

GRAPE = "Grape Computer"
SINGINGSAM = "SingingSam"
FLYINGFOO = "FlyingFoo"
PHONE = "Smartphone"
CASE = "Phone Case"
PROTECTOR = "Screen Protector"
KEYBOARD = "Keyboard"
BRANDS = {"grape": GRAPE, "singingsam": SINGINGSAM}


def _attr(doc: dict, key: str) -> str | None:
    return next((a["value"] for a in doc["attributes"] if a["key"] == key), None)


def _of(docs: list[dict], product_type: str) -> list[dict]:
    return [d for d in docs if d["product_type"] == product_type]


def _phones(docs: list[dict], brand: str) -> set[str]:
    return {_attr(d, "model_line") for d in _of(docs, PHONE) if d["brand"] == brand}


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return ceiling_build().records


@pytest.mark.parametrize("brand", BRANDS.values(), ids=BRANDS)
def test_the_brand_sells_its_own_case_and_keyboard(templates, brand):
    assert [d for d in _of(templates, CASE) if d["brand"] == brand]
    assert [d for d in _of(templates, KEYBOARD) if d["brand"] == brand]


@pytest.mark.parametrize("brand", BRANDS.values(), ids=BRANDS)
def test_every_phone_of_the_line_has_a_case(templates, brand):
    phones = _phones(templates, brand)
    assert phones, brand
    cased = {_attr(d, "compatible_with") for d in _of(templates, CASE)}
    assert phones <= cased, sorted(phones - cased)


@pytest.mark.parametrize("brand", BRANDS.values(), ids=BRANDS)
def test_at_least_two_brands_sell_a_case_for_the_line(templates, brand):
    phones = _phones(templates, brand)
    sellers = {d["brand"] for d in _of(templates, CASE) if _attr(d, "compatible_with") in phones}
    assert len(sellers) >= 2, sellers


@pytest.mark.parametrize("product_type", [CASE, PROTECTOR])
def test_every_singingsam_phone_has_a_third_party_accessory_that_names_it(templates, product_type):
    for phone in _phones(templates, SINGINGSAM):
        rows = [d for d in _of(templates, product_type) if phone in d["title"]]
        assert [d for d in rows if d["brand"] != SINGINGSAM], phone
        assert all(_attr(d, "compatible_with") == phone for d in rows), phone


@pytest.mark.parametrize("brand", BRANDS.values(), ids=BRANDS)
def test_the_brand_keyboard_names_the_device_it_fits(templates, brand):
    keyboards = [d for d in _of(templates, KEYBOARD) if d["brand"] == brand]
    assert keyboards, brand
    for doc in keyboards:
        fits = _attr(doc, "compatible_with")
        assert fits, doc["title"]
        assert doc["title"].endswith(f" for {fits}")


def test_a_grapephone_keyboard_exists(templates):
    """The issue's trigger query, `grapephone keyboard`, meets a row that holds both words."""
    assert [d for d in _of(templates, KEYBOARD) if "GrapePhone" in d["title"]]


def test_flyingfoo_is_a_third_party_brand_with_a_mark_of_its_own(templates):
    style = house_styles.HOUSE_STYLES.get(FLYINGFOO)
    assert style is not None
    others = {s.mark for b, s in house_styles.HOUSE_STYLES.items() if b != FLYINGFOO}
    assert style.mark != house_styles.NO_MARK
    assert style.mark not in others
    rows = [d for d in templates if d["brand"] == FLYINGFOO]
    assert {d["product_type"] for d in rows} == {CASE, PROTECTOR}
    assert {d["brand_owner"] for d in rows} == {"third_party"}


def test_the_build_names_no_real_brand_with_the_new_rows(ceiling):
    assert real_brands.check(ceiling) == []
    assert FLYINGFOO in {d["brand"] for d in ceiling}


def test_a_brand_in_a_title_is_the_brand_of_the_row(ceiling):
    """A title that opens with a brand is that brand's product, in the whole build."""
    for doc in ceiling:
        if doc["product_type"] in (CASE, PROTECTOR, KEYBOARD):
            for brand in (GRAPE, SINGINGSAM, FLYINGFOO):
                if doc["title"].startswith(brand):
                    assert doc["brand"] == brand, doc["title"]
