"""Two lipsticks of different lines look different, and a line's SKUs share a case (gen#738).

Every lipstick drew one black case and only its shade changed, so a page of separate products read
as a grouping failure. These tests read what the release draws: a product's image with its shade
taken out is the picture a line owns.
"""

from __future__ import annotations

import copy
import itertools
import re

import pytest

from synthetic_ecommerce_data.domains.retail import export, image_release, scale
from synthetic_ecommerce_data.domains.retail.line_grammar_families.beauty import (
    LEADS,
    NUMBERS,
    SUBS,
)

SATIN = next(r for r in scale.templates() if r["product_id"] == "BEA-LIPSAT")


def _lipstick(
    line: str | None = "Renew 2", finish: str | None = "Satin", title: str = "Lip"
) -> dict:
    """A copy of the satin lipstick on ``line`` in ``finish``, its first SKU alone."""
    rec = copy.deepcopy(SATIN)
    rec["skus"] = rec["skus"][:1]
    rec["product_line"], rec["title"] = line, title
    rec["attributes"] = [{"key": "finish", "value": finish}] if finish else []
    return rec


def _picture(rec: dict, sku: dict) -> str:
    """What ``sku``'s image draws, with its shade blanked and the product's own ids gone."""
    svg = image_release.render(rec, sku).decode()
    svg = svg.replace(image_release.colorway_drawing(rec, sku)["base"], "SHADE")
    return svg.replace(rec["product_id"], "ID")


def _spec(rec: dict) -> dict:
    return export.drawing_spec(rec, rec["skus"][0]).get("params", {})


def test_every_model_of_the_grammar_draws_a_look_of_its_own() -> None:
    subs = ("", *(f"{s} " for s in SUBS))
    lines = [f"{a} {b}{n}" for a, b, n in itertools.product(LEADS, subs, NUMBERS)]
    assert len({str(_spec(_lipstick(line))) for line in lines}) == len(lines)


def test_two_lines_draw_different_pictures_of_one_shade() -> None:
    one, other = _lipstick("Renew 2"), _lipstick("Renew 4")
    assert _picture(one, one["skus"][0]) != _picture(other, other["skus"][0])


def test_two_titles_with_no_model_draw_different_pictures() -> None:
    one, other = _lipstick(None, title="Satin Lipstick"), _lipstick(None, title="Lipstick Rouge")
    assert _picture(one, one["skus"][0]) != _picture(other, other["skus"][0])


def test_a_line_outside_the_grammar_draws_too() -> None:
    assert _spec(_lipstick("Harbor Limited 3")) != _spec(_lipstick("Harbor Limited 4"))


def test_a_model_of_one_line_keeps_its_case_in_both_finishes() -> None:
    matte, satin = _spec(_lipstick(finish="Matte")), _spec(_lipstick(finish="Satin"))
    assert matte and satin
    assert {k: v for k, v in matte.items() if k != "finish"} == {
        k: v for k, v in satin.items() if k != "finish"
    }


@pytest.mark.parametrize(
    ("one", "other"), [("Matte", "Satin"), ("Satin", "Sheer"), ("Matte", "Sheer")]
)
def test_two_finishes_of_one_shade_draw_differently(one: str, other: str) -> None:
    a, b = _lipstick(finish=one), _lipstick(finish=other)
    assert _picture(a, a["skus"][0]) != _picture(b, b["skus"][0])


def test_the_attribute_states_the_finish_over_the_title() -> None:
    assert _spec(_lipstick(finish="Matte", title="Satin Lipstick")).get("finish") == "matte"


@pytest.mark.parametrize(
    ("title", "finish"),
    [("Satin Lipstick", "satin"), ("Rouge, Matte Lipstick", "matte"), ("Sheer Lip", "sheer"),
     ("Rouge Lipstick", "satin")],
)  # fmt: skip
def test_a_product_with_no_finish_attribute_reads_its_title(title: str, finish: str) -> None:
    assert _spec(_lipstick(finish=None, title=title)).get("finish") == finish


def test_each_sku_of_a_product_shares_the_case_and_draws_its_own_shade() -> None:
    assert len(SATIN["skus"]) == 24
    assert len({_picture(SATIN, s) for s in SATIN["skus"]}) == 1
    for sku in SATIN["skus"]:
        shade = image_release.colorway_drawing(SATIN, sku)["base"]
        assert shade in image_release.render(SATIN, sku).decode()


def test_another_shape_takes_no_look() -> None:
    bottle = _lipstick()
    bottle["drawing"] = {**bottle["drawing"], "shape": "bottle"}
    assert _spec(bottle) == {}


def test_no_shade_of_the_range_is_a_case_color() -> None:
    pattern = re.compile(r"#[0-9a-f]{6}")
    shades = {c["hex"] for r in scale.templates() if r["drawing"]["shape"] == "lipstick"
              for c in r.get("color_options", ())}  # fmt: skip
    drawn = set(pattern.findall(str(_spec(_lipstick()))))
    assert shades and drawn and not shades & drawn
