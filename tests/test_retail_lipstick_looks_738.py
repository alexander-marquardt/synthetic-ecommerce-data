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

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    kit,
    kit_home,
    lipstick_looks,
    scale,
    sheet_extent,
)
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
    [("Satin Lipstick", "satin"), ("Matte, Rouge Lipstick", "matte"), ("Sheer Lip", "sheer"),
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


def _drawn(**params: str) -> str:
    return kit.render("lipstick", kit.Fill("solid", "#c8102e", "#2b2b30"), params=params)


def test_every_look_stays_on_its_sheet() -> None:
    for case, bullet, emblem, finish in itertools.product(
        kit_home.LIPSTICK_CASES,
        kit_home.LIPSTICK_BULLETS,
        kit_home.LIPSTICK_EMBLEMS,
        kit_home.LIPSTICK_FINISHES,
    ):
        svg = _drawn(case=case, bullet=bullet, emblem=emblem, finish=finish)
        assert sheet_extent.overrun(svg, 400.0) == 0, (case, bullet, emblem, finish)


@pytest.mark.parametrize(
    ("param", "choices"),
    [
        ("case", kit_home.LIPSTICK_CASES),
        ("case_color", lipstick_looks.CASE_COLORS),
        ("collar", lipstick_looks.COLLARS),
        ("bullet", kit_home.LIPSTICK_BULLETS),
        ("emblem", kit_home.LIPSTICK_EMBLEMS),
        ("finish", kit_home.LIPSTICK_FINISHES),
    ],
)
def test_each_choice_of_a_look_draws_its_own_picture(param: str, choices: tuple) -> None:
    assert len({_drawn(**{param: choice}) for choice in choices}) == len(choices) >= 3


def test_a_case_and_its_collar_take_the_look_colors_and_the_cap_matches_the_base() -> None:
    svg = _drawn(case="slim", case_color="#123456", collar="#654321", emblem="dot")
    assert svg.count('fill="#123456"') == 2
    assert svg.count('fill="#654321"') == 4


def test_a_drawing_with_no_look_keeps_the_fill_accent_as_its_case() -> None:
    assert 'fill="#2b2b30"' in _drawn()


def test_only_a_satin_or_sheer_bullet_carries_gloss_and_only_sheer_shows_through() -> None:
    gloss = 'stroke="#ffffff"'
    assert gloss not in _drawn(finish="matte")
    assert gloss in _drawn(finish="satin")
    assert gloss in _drawn(finish="sheer")
    assert 'stroke="#000000"' in _drawn(finish="satin")
    assert 'stroke="#000000"' not in _drawn(finish="matte")
    assert "fill-opacity" not in _drawn(finish="satin")
    assert "fill-opacity" in _drawn(finish="sheer")


def _rgb(hex_color: str) -> tuple[int, ...]:
    return tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))


def test_the_case_colors_read_apart_at_a_tile() -> None:
    for one, other in itertools.combinations(lipstick_looks.CASE_COLORS, 2):
        apart = sum((a - b) ** 2 for a, b in zip(_rgb(one), _rgb(other), strict=True)) ** 0.5
        assert apart >= 45, (one, other)


def test_the_choices_have_room_for_every_model() -> None:
    room = (
        len(kit_home.LIPSTICK_CASES)
        * len(lipstick_looks.CASE_COLORS)
        * len(kit_home.LIPSTICK_BULLETS)
        * len(kit_home.LIPSTICK_EMBLEMS)
        * len(lipstick_looks.COLLARS)
    )
    assert room >= lipstick_looks.MODELS


def _number(line: str) -> int:
    try:
        return lipstick_looks._line_number(line)
    except ValueError as gone:
        raise AssertionError(f"{line!r} is outside the grammar and must hash: {gone}") from gone


def test_a_real_model_is_numbered_from_its_words() -> None:
    assert _number(f"{LEADS[0]} {NUMBERS[0]}") == 0
    assert _number(f"{LEADS[0]} {SUBS[0]} {NUMBERS[0]}") == len(NUMBERS)
    assert _number(f"{LEADS[1]} {NUMBERS[1]}") == (len(SUBS) + 1) * len(NUMBERS) + 1


@pytest.mark.parametrize(
    "near",
    [f"{LEADS[0]} 1", f"{LEADS[0]} Limited 2", f"Harbor {NUMBERS[0]}", LEADS[0],
     f"{LEADS[0]} {SUBS[0]}", f"{LEADS[0]} Plus Pro 2"],
)  # fmt: skip
def test_a_near_miss_of_the_grammar_hashes_into_the_models(near: str) -> None:
    assert 0 < _number(near) < lipstick_looks.MODELS


def test_models_that_differ_by_their_lead_alone_spread_over_the_cases_and_colors() -> None:
    specs = [_spec(_lipstick(f"{lead} Pro 4")) for lead in LEADS]
    assert len({s["case"] for s in specs}) == len(kit_home.LIPSTICK_CASES)
    assert len({s["case_color"] for s in specs}) >= 10


def test_each_look_lands_on_one_place() -> None:
    assert sorted(lipstick_looks.SCATTERED) == list(range(lipstick_looks.MODELS))


def _case(shape: str) -> list[str]:
    return kit_home._lipstick_case(shape, 100, 200, 60, 300, "#123456")


def test_each_case_draws_the_outline_its_name_says() -> None:
    assert len(_case("slim")) == 1 and " Q" not in _case("slim")[0]
    assert " Q" in _case("domed")[0] and "M96,300 L96,226" in _case("domed")[0]
    assert " Q" in _case("waisted")[0] and "Q110,250" in _case("waisted")[0]
    assert 'd="M108,200 L152,200 L164,300 L96,300 Z"' in _case("tapered")[0]
    assert len(_case("square")) == 2 and _case("square")[1].count("M") == 2
    assert len(_case("fluted")) == 2 and _case("fluted")[1].count("M") >= 4
