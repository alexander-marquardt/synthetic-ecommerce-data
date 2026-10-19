"""Thin leaves the retail classes name hold at least fifteen products (gen#434, gap 3).

``chips`` filled the top of the results with fresh potatoes because the Frozen Chips leaf held
one product; Beds held six and Womens check bomber jackets three. Each leaf now holds fifteen or
more (face creams are gen#542's). The floors are written out here, so dropping rows fails this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import class_model  # noqa: E402
import scale  # noqa: E402

#: The shared bed sizes the issue names, as the vocabulary spells them.
BED_SIZES = ("Single (3 ft)", "Double (4 ft 6)", "King Size (5 ft)", "Super King Size (6 ft)")
FLOOR = 15


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _leaf(templates: list[dict], path: tuple[str, ...]) -> list[dict]:
    return [r for r in templates if tuple(r["category_path"]) == path]


CHIPS = ("Food & Drink", "Frozen Food", "Chips & Potatoes")
BEDS = ("Home", "Furniture", "Beds")
BOMBERS = ("Womens", "Coats & Jackets", "Bomber Jackets")


@pytest.mark.parametrize("path", [CHIPS, BEDS, BOMBERS], ids=["chips", "beds", "bombers"])
def test_a_named_leaf_holds_at_least_fifteen_products(templates: list[dict], path: tuple) -> None:
    held = _leaf(templates, path)
    assert len(held) >= FLOOR, f"{' / '.join(path)} holds {len(held)}"


def test_at_least_fifteen_womens_check_bomber_jackets(templates: list[dict]) -> None:
    held = [r for r in _leaf(templates, BOMBERS) if r.get("pattern") == "check"]
    assert len(held) >= FLOOR, f"{len(held)} Womens bomber jackets with pattern = check"


def test_a_check_bomber_is_a_check_in_its_swatch(templates: list[dict]) -> None:
    """The data is true: a bomber stated as a check carries a check colorway, never a plain one."""
    bad = [
        r["product_id"] for r in _leaf(templates, BOMBERS) if r.get("pattern") == "check"
        and not any(c.get("pattern") == "gingham" for c in r["color_options"])
    ]  # fmt: skip
    assert not bad, bad


def test_every_bed_states_its_sizes_from_the_shared_vocabulary(templates: list[dict]) -> None:
    beds = _leaf(templates, BEDS)
    assert beds, "no beds"
    for r in beds:
        sizes = {s.get("bed_size") for s in r["skus"]}
        assert sizes and sizes <= set(class_model.BED_SIZE_DIMS), (r["product_id"], sizes)
        assert all(s["width_cm"] and s["length_cm"] for s in r["skus"]), r["product_id"]


@pytest.mark.parametrize("size", BED_SIZES)
def test_at_least_six_beds_are_made_in_each_named_size(
    templates: list[dict], size: str
) -> None:
    made = [r for r in _leaf(templates, BEDS) if any(s.get("bed_size") == size for s in r["skus"])]
    assert len(made) >= 6, f"{len(made)} beds are made in {size}"


def test_the_chips_leaf_holds_chips_and_potato_products(templates: list[dict]) -> None:
    words = ("chips", "fries", "wedges", "hash", "potato", "rosti", "waffles", "croquettes")
    held = _leaf(templates, CHIPS)
    off = [r["title"] for r in held if not any(w in r["title"].lower() for w in words)]
    assert held and not off, off
    assert sum("chips" in r["title"].lower() for r in held) >= 4
