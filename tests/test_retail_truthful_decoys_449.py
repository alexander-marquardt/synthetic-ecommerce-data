"""Grocery, home and garden decoys and copy tell the truth (gen#449, the rule of #444).

A product's title, fields, description and drawing describe the one thing it is. The believability
audit of 2026-10-17 found a red wine carafe drawn as a red bottle, a grey sponge cake, loose
apples with a pack count, a "4 Pack" drawn as one pot, a mug-cake mix drawn as a celebration
cake, mushrooms drawn as strawberries, negations as titles ("Never Cordless", "Cantilever Free")
and grocery descriptions that were field dumps ("Pineapple, in 1L, 330ml."). One test per class.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_rows as dr  # noqa: E402
import image_release  # noqa: E402
import scale  # noqa: E402


@pytest.fixture(scope="module")
def by_id() -> dict[str, dict[str, Any]]:
    return {r["product_id"]: r for r in scale.build(10**6).records}


def _svg(rec: dict[str, Any]) -> str:
    return image_release.render(rec, rec["skus"][0], styled=False).decode()


def _attr(rec: dict[str, Any], key: str) -> list[str]:
    return [a["value"] for a in rec["attributes"] if a["key"] == key]


def test_a_wine_carafe_is_clear_glass_with_no_color_field(by_id: dict[str, dict]) -> None:
    rec = by_id["PLT-DXW04"]
    assert rec["title"] == "Glass Wine Carafe"
    assert not rec.get("color_options"), "a carafe is clear glass: it carries no color"
    assert rec["drawing"]["shape"] == "drinking_glass"
    assert rec["drawing"]["params"]["kind"] == "carafe"
    assert rec["drawing"]["base"].lower() != dr.RED


def test_no_text_match_decoy_is_drawn_in_the_grey_fallback() -> None:
    """A color the table does not know used to draw grey: the lemon sponge was a grey cake."""
    unknown = sorted({d.color for d in dr.TABLE} - set(dr.COLORS))
    assert unknown == []
    for d in dr.TABLE:
        drawn = d.style().colors[0][0][2]
        assert d.color == "Grey" or drawn != dr.GREY, d.code


def test_a_lemon_sponge_cake_is_drawn_yellow(by_id: dict[str, dict]) -> None:
    rec = by_id["PLT-DXI07"]
    assert rec["drawing"]["base"].lower() not in (dr.GREY, dr.RED)
    assert rec["drawing"]["base"].lower() == dr.COLORS["Yellow"].lower()


def test_apples_sold_four_to_a_pack_are_not_sold_loose(by_id: dict[str, dict]) -> None:
    rec = by_id["PLT-DXU04"]
    assert _attr(rec, "units_per_pack") == ["4"]
    assert "loose" not in rec["description"].lower()
    assert rec["drawing"]["params"]["pack"] == "net"
    assert rec["drawing"]["params"]["count"] == 4


def test_a_four_pack_of_yogurt_is_drawn_as_four_pots(by_id: dict[str, dict]) -> None:
    rec = by_id["PLT-DXI08"]
    assert _attr(rec, "units_per_pack") == ["4"]
    assert _svg(rec).count('class="pot"') == 4


def test_a_single_tub_is_still_one_pot(by_id: dict[str, dict]) -> None:
    single = next(
        r for r in by_id.values()
        if r["drawing"]["shape"] == "tub" and not (r["drawing"].get("params") or {}).get("count")
    )
    assert _svg(single).count('class="pot"') == 1


def test_a_boxed_mug_cake_mix_is_drawn_as_a_box_not_a_celebration_cake(
    by_id: dict[str, dict],
) -> None:
    rec = by_id["PLT-DY78"]
    assert "in a box" in rec["description"]
    assert rec["drawing"]["shape"] == "box"


def test_a_cake_is_drawn_with_candles_only_when_it_is_a_cake(by_id: dict[str, dict]) -> None:
    boxed = [r for r in by_id.values() if "in a box" in r["description"].lower()
             and r["drawing"]["shape"] == "cake"]
    assert [r["product_id"] for r in boxed] == []


def test_a_punnet_holds_what_the_title_says(by_id: dict[str, dict]) -> None:
    veg = [r for r in by_id.values() if r["product_id"].startswith("GRC-VEG-")]
    assert veg
    strawberry_red = "#d23a3a"
    for rec in veg:
        produce = (rec["drawing"].get("params") or {}).get("produce")
        svg = _svg(rec)
        title = rec["title"].lower()
        if "mushroom" in title:
            assert produce == "mushroom"
        if "carrot" in title:
            assert produce == "carrot"
        assert produce in {"tomato", "mushroom", "carrot", "bean", "herb", "pepper"}, rec["title"]
        assert strawberry_red not in svg or produce == "tomato", rec["title"]
    assert any("mushroom" in r["title"].lower() for r in veg)


def test_a_strawberry_punnet_keeps_its_berries(by_id: dict[str, dict]) -> None:
    import kit  # noqa: PLC0415

    svg = kit.render("punnet", kit.Fill("solid", "#2f6b3c", "#ffffff"), "Strawberries")
    assert "#d23a3a" in svg


NEGATION = re.compile(r"\b(never|not|no|free|without)\b", re.I)


@pytest.mark.parametrize(
    "pid",
    ["BRD-DCTA02", "BRD-DCGA02", "BRD-DCPA02", "PLT-DY62", "BRD-KDM232", "BRD-KDW232",
     "BRD-MDST632", "BRD-MDW732", "BRD-NXMET032"],
)
def test_a_title_states_what_the_product_is_never_what_it_is_not(
    by_id: dict[str, dict], pid: str
) -> None:
    title = by_id[pid]["title"]
    assert not NEGATION.search(title), title
    assert "Kids' Style" not in title, title


def test_the_corded_trimmers_and_the_tilting_parasol_read_as_listings(
    by_id: dict[str, dict],
) -> None:
    assert by_id["BRD-DCTA02"]["title"] == "Corded Grass Trimmer, 10 m Cable"
    assert by_id["BRD-DCGA02"]["title"] == "Corded Hedge Trimmer, 10 m Cable"
    assert by_id["BRD-DCPA02"]["title"] == "Center Pole Parasol with Tilt"
    assert by_id["PLT-DY62"]["title"] == "Quilted Throw with Batting"


FIELD_DUMP = re.compile(r", in \d|\. In \d|^[^.]*, in [0-9]")


def test_no_grocery_description_is_a_field_dump(by_id: dict[str, dict]) -> None:
    groceries = [r for r in by_id.values() if r["product_id"].startswith("GRC-")]
    assert groceries
    dumps = [(r["product_id"], r["description"]) for r in groceries
             if FIELD_DUMP.search(r["description"])]
    assert dumps[:5] == []


@pytest.mark.parametrize("pid", ["GRC-RDY-0052", "GRC-JUI-0048", "GRC-PAS-0065"])
def test_a_grocery_description_is_a_sentence_then_the_pack_and_storage_line(
    by_id: dict[str, dict], pid: str
) -> None:
    desc = by_id[pid]["description"]
    first, _, rest = desc.partition(". ")
    assert len(first.split()) >= 5 and rest, desc
    assert "Available as" in rest, desc
    assert not re.search(r"\b\d+g, \d+g\b|\b1L, 330ml\b", desc), desc


def test_a_named_dish_or_pasta_is_a_variety_not_a_flavor(by_id: dict[str, dict]) -> None:
    penne = by_id["GRC-PAS-0065"]
    assert "flavor" not in {a["key"] for a in penne["attributes"]}
    assert _attr(penne, "variety") == ["Gluten Free Penne"]
    juice = by_id["GRC-JUI-0048"]
    assert _attr(juice, "flavor") == ["Pineapple"], "a juice has a flavor"


def test_every_food_product_type_has_a_sentence_of_its_own() -> None:
    """A new grocery family cannot reach the catalogue without the copy that says what it is."""
    import grocery_rows as gr  # noqa: PLC0415

    food = [f for f in gr.FAMILIES if f.food]
    assert {f.product_type for f in food} <= set(gr.INTRO)
    by_code = {f.code: f for f in food}
    several = {f.product_type for f in food if f.per_style[1] > 1}
    several |= {by_code[a[0]].product_type for a in (*gr.ANCHORS, *gr.DECOY_ANCHORS)
                if a[0] in by_code and len(a[1]) > 1}
    assert several <= set(gr.INTRO_MULTI), several - set(gr.INTRO_MULTI)
    assert all("{name}" in text for text in gr.INTRO.values())
    assert not any("{name}" in text for text in gr.INTRO_MULTI.values())
