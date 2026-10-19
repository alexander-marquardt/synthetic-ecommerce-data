"""Womens knitwear states a neckline and a sleeve length (gen#434, gap 2).

``long sleeve v neck cardigan`` and ``white crew neck jumper`` read a neckline and a sleeve
length. Twenty Womens knitwear styles (the first jumpers and cardigans, the color-group rows and
the text-match decoys cloned from them) stated no sleeve length, and the sleeves the shop knits
were long or none: no three quarter, no short. Knitwear also had no cowl neck. The floors are
written out here, so dropping a style fails this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def knit(templates: list[dict]) -> list[dict]:
    return [r for r in templates if r["category_path"][:2] == ["Womens", "Knitwear"]]


def _sleeves(rec: dict) -> list[str]:
    return [a["value"] for a in rec["attributes"] if a["key"] == "sleeve_length"]


#: The sleeve values as the rest of the catalogue spells them (tops write "Three quarter").
SLEEVES = ("Long", "Three quarter", "Short", "Sleeveless")
#: The drawing kit's sleeve key for each stored value.
DRAWN = {"Long": "long", "Three quarter": "three_quarter", "Short": "short",
         "Sleeveless": "sleeveless"}  # fmt: skip


def test_every_womens_knit_states_one_sleeve_length(knit: list[dict]) -> None:
    bad = [r["product_id"] for r in knit if len(_sleeves(r)) != 1 or _sleeves(r)[0] not in SLEEVES]
    assert not bad, f"{len(bad)} Womens knitwear styles without one sleeve length: {bad[:6]}"


def test_every_womens_knit_states_a_neckline(knit: list[dict]) -> None:
    assert not [r["product_id"] for r in knit if not r.get("neckline")]


@pytest.mark.parametrize("value", SLEEVES)
def test_each_sleeve_length_has_womens_knitwear(knit: list[dict], value: str) -> None:
    held = [r for r in knit if _sleeves(r) == [value]]
    assert len(held) >= 5, f"{len(held)} Womens knitwear products with sleeve {value}"


def test_womens_knitwear_has_cowl_neck_products(knit: list[dict]) -> None:
    held = [r for r in knit if r.get("neckline") == "cowl"]
    assert len(held) >= 5, f"{len(held)} Womens knitwear products with a cowl neck"


def test_at_least_five_white_long_sleeve_crew_neck_jumpers(knit: list[dict]) -> None:
    held = [
        r for r in knit
        if r["category_path"][2] == "Jumpers" and r.get("neckline") == "crew"
        and _sleeves(r) == ["Long"] and any(s["color"] == "White" for s in r["skus"])
    ]  # fmt: skip
    assert len(held) >= 5, f"{len(held)} white long sleeve crew neck Womens jumpers"


def test_the_drawing_shows_the_sleeve_the_attribute_states(knit: list[dict]) -> None:
    """A knit whose drawing carries a sleeve is drawn with the one it states."""
    wrong = []
    for r in knit:
        drawn = ((r.get("drawing") or {}).get("params") or {}).get("sleeve")
        if drawn and _sleeves(r) and DRAWN.get(_sleeves(r)[0]) != drawn:
            wrong.append((r["product_id"], _sleeves(r), drawn))
    assert not wrong, wrong[:6]


@pytest.mark.parametrize(
    ("words", "value"),
    [("three quarter sleeve", "Three quarter"), ("short sleeve", "Short")],
)
def test_a_title_naming_a_sleeve_states_it(knit: list[dict], words: str, value: str) -> None:
    named = [r for r in knit if words in r["title"].lower()]
    assert named, f"no Womens knitwear title names a {words}"
    wrong = [r["product_id"] for r in named if _sleeves(r) != [value]]
    assert not wrong, wrong


@pytest.mark.parametrize(
    "pid", ["PLT-JMPCBL", "BRD-NWJ1", "BRD-NWC2", "BRD-CLRCDG", "PLT-DA03100", "PLT-DA10100"]
)
def test_a_knit_that_stated_none_is_long_sleeved(knit: list[dict], pid: str) -> None:
    """The first rows, a color-group row and the decoys cloned from them are long sleeved."""
    held = [r for r in knit if r["product_id"] == pid]
    assert held, f"{pid} is not a Womens knitwear template"
    assert _sleeves(held[0]) == ["Long"]
