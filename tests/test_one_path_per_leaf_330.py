"""One category path per leaf (gen#330).

A leaf that sits under two paths splits its products, and a category route (the Engine's
"query names a category" policy) filters to one of them: "honey" routed to the single honey
jar of ``Honey & Spreads/Honey`` while 92 honey jars sat under ``Jam & Honey``. Two builds
of the Food & Drink tree had grown side by side, the grocery families of gen#154 and the
earlier hand-authored rows, each with its own breadcrumb for pasta, tea, coffee, oranges
and lemons. The grocery tree is the one the catalog holds; every other row follows it.

The rule: within one root (a store department), a leaf label is reached by one path.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402

#: Leaves a shopper reaches through the audience they shop for: the audience is the parent
#: (Kids > Boys > Jeans, Kids > Girls > Jeans), so the label repeats by design. A leaf not
#: named here that repeats is a defect.
AUDIENCE_SPLIT = frozenset({
    ("Gifts", "Wallet Gift Sets"),
    ("Kids", "Coats & Jackets"),
    ("Kids", "Jeans"),
    ("Kids", "Swimwear"),
    ("Kids", "Tracksuits"),
})  # fmt: skip


def leaves_on_several_paths(records: list[dict]) -> dict[tuple[str, str], list[str]]:
    """``{(root, leaf label): its paths}`` for every leaf label reached by more than one path."""
    paths: dict[tuple[str, str], set[tuple[str, ...]]] = collections.defaultdict(set)
    for r in records:
        p = tuple(r["category_path"])
        paths[(p[0], p[-1])].add(p)
    return {
        key: sorted("/".join(p) for p in ps)
        for key, ps in sorted(paths.items())
        if len(ps) > 1
    }


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def test_no_leaf_is_reachable_under_two_paths(templates: list[dict]) -> None:
    found = {
        key: ps
        for key, ps in leaves_on_several_paths(templates).items()
        if key not in AUDIENCE_SPLIT
    }
    assert found == {}, (
        "a leaf label sits under more than one path, so a category route filters to a "
        f"fraction of its products (gen#330): {found}"
    )


def test_every_honey_jar_sits_on_the_one_honey_leaf(templates: list[dict]) -> None:
    jars = [r for r in templates if r.get("drawing", {}).get("label") == "Honey"]
    assert {tuple(r["category_path"]) for r in jars} == {
        ("Food & Drink", "Food Cupboard", "Honey")
    }
    assert len(jars) > 1


def test_the_guard_refuses_a_leaf_on_two_paths() -> None:
    twin = [
        {"category_path": ["Food & Drink", "Food Cupboard", "Pasta"]},
        {"category_path": ["Food & Drink", "Pantry", "Pasta"]},
        {"category_path": ["Food & Drink", "Food Cupboard", "Rice & Grains"]},
        {"category_path": ["Home", "Pantry", "Pasta"]},
    ]
    assert leaves_on_several_paths(twin) == {
        ("Food & Drink", "Pasta"): ["Food & Drink/Food Cupboard/Pasta", "Food & Drink/Pantry/Pasta"]
    }
