"""The retail tree nests a product type under its generic category (gen#283).

``Home > Furniture`` held ``Sofas`` beside ``Corner Sofas``, ``Recliner Sofas`` and the rest, so a
hierarchy filter on ``Sofas`` dropped the corner sofas that were most of the red ones. The tree
nests them (``Sofas > Corner Sofas``), and three rules in ``tree_guard.py`` keep it nested:

* (a) no node has a sibling whose label is its head noun;
* (b) three or more siblings with one head noun sit under a parent that names it, or declare why
  not;
* (c) a product whose title names a more specific node of its department sits in that node.

The first block runs the rules over the built tree (the ceiling build, every authored and derived
style). The second feeds them a tree broken on purpose, the mutant the issue asks for: ``Corner
Sofas`` put back beside ``Sofas`` fails rule (a), and each of the others fails its own rule.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402
import tree_guard  # noqa: E402

CEILING = 10_000_000  # more SKUs than the templates reach, so ``scale.build`` runs to its ceiling

#: The least number of types nested under a generic category the built tree holds. #284 moved 34;
#: the floor sits a little under, so a sibling PR that renames one does not red it, and a build
#: that un-nests the tree does.
NESTED_FLOOR = 30


@pytest.fixture(scope="module")
def records() -> list[dict]:
    """The SHIPPED documents, not the build records: a jean's fit and a bra's style are leaves of
    the record (it keeps them so its drawing and image id do not move) and facets of the document
    (``facet_leaves``), so the tree a retailer loads is the document's."""
    return scale.documents(scale.build(CEILING))


@pytest.fixture(scope="module")
def paths(records: list[dict]) -> set[tuple[str, ...]]:
    return {tuple(r["category_path"]) for r in records}


def test_no_node_has_a_sibling_that_is_its_head_noun(paths: set[tuple[str, ...]]) -> None:
    assert tree_guard.sibling_head_noun_findings(paths) == []


def test_the_tree_holds_its_nested_types(paths: set[tuple[str, ...]]) -> None:
    """The rules above say what may not sit beside a generic node; this says the types are
    nested under it (rather than dropped), without pinning which ones."""
    assert len(tree_guard.nested_pairs(paths)) >= NESTED_FLOOR


def test_three_siblings_with_one_head_noun_sit_under_a_parent_that_names_it(
    paths: set[tuple[str, ...]],
) -> None:
    assert tree_guard.headless_group_findings(paths) == []


def test_every_declared_exception_has_a_reason_and_still_applies(
    paths: set[tuple[str, ...]],
) -> None:
    assert tree_guard.stale_exception_findings(paths, tree_guard.EXCEPTIONS) == []


def test_a_title_that_names_a_more_specific_node_sits_in_that_node(records: list[dict]) -> None:
    rows = [(r["product_id"], r["title"], r["category_path"]) for r in records]
    assert tree_guard.misplaced_title_findings(rows) == []


def test_each_product_keeps_one_tree_location(records: list[dict]) -> None:
    places: dict[str, set[tuple[str, ...]]] = collections.defaultdict(set)
    for r in records:
        places[r["product_id"]].add(tuple(r["category_path"]))
    assert {pid: sorted(p) for pid, p in places.items() if len(p) != 1} == {}
    assert len(places) == len(records)  # no product id is built twice


# --- the guard itself: a tree broken on purpose must fail ---------------------------------

NESTED = [
    ("Home", "Furniture", "Sofas"),
    ("Home", "Furniture", "Sofas", "Corner Sofas"),
    ("Home", "Furniture", "Sofas", "Sofa Beds"),
    ("Home", "Furniture", "Beds"),
]
# the mutant: ``Corner Sofas`` back as a sibling of ``Sofas``
FLAT = [
    ("Home", "Furniture", "Sofas"),
    ("Home", "Furniture", "Corner Sofas"),
    ("Home", "Furniture", "Sofa Beds"),
    ("Home", "Furniture", "Beds"),
]
LAMPS = [("Home", "Lighting", label) for label in ("Desk Lamps", "Floor Lamps", "Table Lamps")]


def test_the_mutant_with_corner_sofas_beside_sofas_fails_rule_a() -> None:
    findings = tree_guard.sibling_head_noun_findings(FLAT)
    assert "Home > Furniture: 'Sofas' sits beside 'Corner Sofas'" in findings
    assert "Home > Furniture: 'Beds' sits beside 'Sofa Beds'" in findings


def test_the_nested_tree_passes_rule_a() -> None:
    assert tree_guard.sibling_head_noun_findings(NESTED) == []


JEANS = [
    ("Women", "Jeans", "Skinny Jeans"),
    ("Women", "Jeans", "Super Skinny Jeans"),
    ("Women", "Jeans", "Straight Jeans"),
]
BRAS = [
    ("Women", "Lingerie", "Bras", "Plunge Bras"),
    ("Women", "Lingerie", "Bras", "Deep Plunge Bras"),
    ("Women", "Lingerie", "Bras", "Lace Plunge Bras"),
    ("Women", "Lingerie", "Bras", "Demi Bras"),
]


def test_a_multi_word_generic_sibling_fails_rule_a() -> None:
    assert tree_guard.sibling_head_noun_findings(JEANS) == [
        "Women > Jeans: 'Skinny Jeans' sits beside 'Super Skinny Jeans'"
    ]
    assert tree_guard.sibling_head_noun_findings(BRAS) == [
        "Women > Lingerie > Bras: 'Plunge Bras' sits beside 'Deep Plunge Bras'",
        "Women > Lingerie > Bras: 'Plunge Bras' sits beside 'Lace Plunge Bras'",
    ]


def test_a_label_that_merely_shares_words_is_not_a_generic_sibling() -> None:
    """Only a word-SUFFIX is the generic parent: 'Skinny Jeans' is not 'Skinny Fit Jeans'' parent,
    and 'Plunge Bras' does not make 'Plunge Bralette' its child."""
    paths = [
        ("Women", "Jeans", "Skinny Jeans"),
        ("Women", "Jeans", "Skinny Fit Jeans"),
        ("Women", "Lingerie", "Plunge Bras"),
        ("Women", "Lingerie", "Plunge Bralettes"),
    ]
    assert tree_guard.sibling_head_noun_findings(paths) == []


def test_the_multi_word_pairs_pass_once_nested() -> None:
    nested = [
        ("Women", "Jeans", "Skinny Jeans"),
        ("Women", "Jeans", "Skinny Jeans", "Super Skinny Jeans"),
        ("Women", "Lingerie", "Bras", "Plunge Bras", "Deep Plunge Bras"),
    ]
    assert tree_guard.sibling_head_noun_findings(nested) == []
    assert tree_guard.nested_pairs(nested) == [
        (("Women", "Jeans"), ("Women", "Jeans", "Skinny Jeans")),
        (
            ("Women", "Jeans", "Skinny Jeans"),
            ("Women", "Jeans", "Skinny Jeans", "Super Skinny Jeans"),
        ),
        (("Women", "Lingerie", "Bras"), ("Women", "Lingerie", "Bras", "Plunge Bras")),
        (
            ("Women", "Lingerie", "Bras", "Plunge Bras"),
            ("Women", "Lingerie", "Bras", "Plunge Bras", "Deep Plunge Bras"),
        ),
    ]


def test_three_lamps_without_a_lamps_parent_fail_rule_b() -> None:
    findings = tree_guard.headless_group_findings(LAMPS)
    assert len(findings) == 1
    assert "Desk Lamps" in findings[0]
    assert "'lamp'" in findings[0]


def test_three_lamps_under_lamps_pass_rule_b() -> None:
    nested = [("Home", "Lighting", "Lamps", path[-1]) for path in LAMPS]
    assert tree_guard.headless_group_findings(nested) == []


def test_two_siblings_with_one_head_noun_need_no_parent() -> None:
    assert tree_guard.headless_group_findings(LAMPS[:2]) == []


def test_a_declared_exception_with_a_reason_silences_rule_b() -> None:
    declared = {(("Home", "Lighting"), "lamp"): "lamps are sold by room, not as one type"}
    assert tree_guard.headless_group_findings(LAMPS, exceptions=declared) == []
    assert tree_guard.stale_exception_findings(LAMPS, declared) == []


def test_an_exception_without_a_reason_or_without_a_group_is_a_finding() -> None:
    nested = [("Home", "Lighting", "Lamps", path[-1]) for path in LAMPS]
    assert tree_guard.stale_exception_findings(LAMPS, {(("Home", "Lighting"), "lamp"): " "}) == [
        "Home > Lighting: exception for 'lamp' has no reason"
    ]
    assert tree_guard.stale_exception_findings(
        nested, {(("Home", "Lighting"), "lamp"): "a reason"}
    ) == ["Home > Lighting: exception for 'lamp' no longer applies"]


def test_a_corner_sofa_titled_product_in_sofas_fails_rule_c() -> None:
    sofas = ("Home", "Furniture", "Sofas")
    corner = ("Home", "Furniture", "Sofas", "Corner Sofas")
    placed = [("PLT-X", "Ashby U-Shaped Corner Sofa", corner)]
    misplaced = [("PLT-SOFCRN-1", "Four Seater Corner Sofa", sofas), *placed]
    assert tree_guard.misplaced_title_findings(misplaced) == [
        "PLT-SOFCRN-1 'Four Seater Corner Sofa' sits in Home > Furniture > Sofas, "
        "names Home > Furniture > Sofas > Corner Sofas"
    ]
    assert tree_guard.misplaced_title_findings(placed) == []


def test_a_title_naming_another_departments_node_is_not_misplaced() -> None:
    rows = [
        ("K-1", "Girls' Barrel Jeans (6-16 Yrs)", ("Kids", "Girls", "Jeans")),
        ("W-1", "Barrel Jeans", ("Women", "Jeans", "Barrel Jeans")),
    ]
    assert tree_guard.misplaced_title_findings(rows) == []
