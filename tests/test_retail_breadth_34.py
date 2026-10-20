"""The retail breadth tier (gen#34, first increment): plain products in new leaves.

Each row of ``breadth_rows.BREADTH_34`` is one or two products in a category no other
template uses, so a shopper query for cutlery, a claw hammer or cherries finds a category
at all. These checks hold what makes a row breadth and not depth.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import breadth_rows  # noqa: E402
import color_word_brand_rows  # noqa: E402
import garden_rows  # noqa: E402
import kit  # noqa: E402
import scale  # noqa: E402

ROWS = breadth_rows.BREADTH_34


def _leaves() -> dict[tuple[str, ...], list[breadth_rows.Row]]:
    out: dict[tuple[str, ...], list[breadth_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        out[row.path].append(row)
    return out


def test_every_leaf_holds_one_or_two_products_and_there_are_at_least_twenty_leaves() -> None:
    leaves = _leaves()
    assert len(leaves) >= 20
    assert {p: len(r) for p, r in leaves.items() if not 1 <= len(r) <= 2} == {}


def _lunch_cooler_ids() -> set[str]:
    """The ids of the class-8 decoys whose true type is a lunch box (``DY`` + the row number)."""
    from feature_decoys import large_appliances

    return {f"PLT-DY{r[0]:02d}" for r in large_appliances._ROWS if r[1] == "la_lunch"}


def test_no_other_template_uses_a_breadth_leaf() -> None:
    mine = {r.code for r in ROWS}
    other = {
        tuple(d["category_path"])
        for d in scale.templates()
        if d["product_id"].removeprefix("BRD-") not in mine
        # a garden decoy sits in a sibling's leaf on purpose (gen#203, gen#294)
        and d["product_id"] not in garden_rows.decoy_ids()
        # a color-word brand row sits in a breadth leaf on purpose (gen#312)
        and d["product_id"] not in color_word_brand_rows.product_ids()
        # the lunch cooler named for a fridge is a real lunch box, so it sits in that leaf (gen#334)
        and d["product_id"] not in _lunch_cooler_ids()
    }
    assert sorted(set(_leaves()) & other) == []


#: Branches this tier adds on purpose, each under a node the catalog already has.
NEW_BRANCHES = frozenset({
    ("Beauty", "Fragrance"),
    ("Beauty", "Make-Up", "Eyes"),
    ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Berries"),
    ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Stone Fruit"),
    ("Garden", "Seeds"),
    ("Home", "DIY & Tools"),
    # gen#283: a type nests under its generic category, which these leaves are the first of
    ("Home", "DIY & Tools", "Drills"),
    ("Home", "DIY & Tools", "Tool Sets"),
    ("Cleaning", "Kitchen & Surfaces", "Cleaners"),
})


def _existing_nodes() -> set[tuple[str, ...]]:
    """Every node (every prefix of a path) used by a template that is not a breadth row."""
    mine = {r.code for r in ROWS}
    nodes: set[tuple[str, ...]] = set()
    for d in scale.templates():
        if d["product_id"].removeprefix("BRD-") in mine:
            continue
        path = tuple(d["category_path"])
        nodes.update(path[:i] for i in range(1, len(path) + 1))
    return nodes


def test_a_new_leaf_sits_inside_the_existing_tree_not_beside_it() -> None:
    """A leaf's parent is an existing node or a listed new branch (whose own parent exists),
    and the leaf is not placed beside a node named for its own product type (a Cherries leaf
    under Fruit & Vegetables, next to Fresh Fruit, belongs inside Fresh Fruit)."""
    nodes = _existing_nodes()
    unknown_parent = sorted(
        r.path for r in ROWS if r.path[:-1] not in nodes | NEW_BRANCHES
    )
    orphan_branch = sorted(b for b in NEW_BRANCHES if b[:-1] not in nodes | NEW_BRANCHES)
    beside = sorted(
        (r.path, r.product_type)
        for r in ROWS
        if (*r.path[:-1], r.product_type) in nodes
    )
    assert unknown_parent == []
    assert orphan_branch == []
    assert beside == []


def test_no_node_sits_directly_under_a_parent_of_the_same_name() -> None:
    pairs = {p: zip(p, p[1:], strict=False) for p in _leaves()}
    same = [p for p, z in pairs.items() if any(a.lower() == b.lower() for a, b in z)]
    assert same == []


def test_titles_and_codes_are_unique_and_every_row_builds_a_valid_document() -> None:
    titles = [r.title for r in ROWS]
    codes = [r.code for r in ROWS]
    assert len(set(titles)) == len(titles)
    assert len(set(codes)) == len(codes)
    for row in ROWS:
        doc = row.doc()
        assert doc["skus"], row.code
        assert doc["attributes"], row.code
        assert doc["drawing"]["shape"] in kit.SHAPES, row.code
        assert doc["drawing"].get("label") is None, row.code


def test_a_unit_free_key_names_no_unit_and_a_unit_key_ends_in_its_unit() -> None:
    """A material or a variety has no unit in its key; a measured figure ends in it
    (``head_weight_oz``, unit code ONZ; ``voltage_v``, VLT; ``piece_count``, a C62 count);
    a size is a SKU field."""
    units = {"ONZ": "oz", "VLT": "v", "C62": "count"}
    tokens = ("mm", "cm", "ml", "kg", "g", "l", "in", "ft", "oz")
    bad = []
    for r in ROWS:
        for a in r.attrs:
            key, code = a[0], (a[3] if len(a) > 3 else None)
            if code is None and any(u in key.split("_") for u in tokens):
                bad.append((r.code, key))
            if code is not None and not key.endswith("_" + units[code]):
                bad.append((r.code, key))
    assert bad == []


# ---- gen#173: drill voltage and set piece count ------------------------------------

import re  # noqa: E402


def _attr(row: breadth_rows.Row, key: str) -> dict | None:
    return next((a for a in row.doc()["attributes"] if a["key"] == key), None)


def _is_set(row: breadth_rows.Row) -> bool:
    return row.product_type.endswith(" Set") or re.search(r"\bSet\b", row.title) is not None


def _title_count(row: breadth_rows.Row) -> int | None:
    m = re.search(r"(\d+) Piece", row.title)
    return int(m.group(1)) if m else None


def test_every_set_carries_a_piece_count_the_title_agrees_with() -> None:
    sets = [r for r in ROWS if _is_set(r)]
    assert len(sets) >= 8
    missing = [r.code for r in sets if _attr(r, "piece_count") is None]
    assert missing == []
    for r in sets:
        a = _attr(r, "piece_count")
        assert a["unit_code"] == "C62" and a["value_canonical"] == float(a["value"]), r.code
        assert int(a["value"]) > 1, r.code
        assert _title_count(r) == int(a["value"]), r.code


def test_a_bigger_set_of_one_leaf_costs_more() -> None:
    """Within a leaf of sets, price rises strictly with the piece count."""
    checked = 0
    for rows in _leaves().values():
        sets = [r for r in rows if _is_set(r)]
        if len(sets) < 2:
            continue
        assert all(_attr(r, "piece_count") for r in sets), rows[0].path
        by_count = sorted(sets, key=lambda r: int(_attr(r, "piece_count")["value"]))
        prices = [r.price for r in by_count]
        assert prices == sorted(set(prices)), by_count[0].path
        checked += 1
    assert checked >= 3


def test_piece_counts_fill_several_buckets_and_include_a_hundred_piece_set() -> None:
    counts = {int(_attr(r, "piece_count")["value"]) for r in ROWS if _attr(r, "piece_count")}
    assert len(counts) >= 5
    assert max(counts) >= 100


def test_every_cordless_drill_carries_a_voltage_its_title_names() -> None:
    drills = [r for r in ROWS if r.product_type == "Cordless Drill"]
    assert len(drills) >= 4
    volts = set()
    for r in drills:
        a = _attr(r, "voltage_v")
        assert a is not None, r.code
        assert a["unit_code"] == "VLT" and a["value_canonical"] == float(a["value"]), r.code
        assert f"{a['value']} V " in r.title, r.code
        volts.add(int(a["value"]))
    assert volts <= {12, 18, 20, 40}
    assert len(volts) >= 4, "a voltage facet needs at least four values"


#: Product types allowed a voltage; a new battery tool is added here, not rejected.
VOLTAGE_TYPES = frozenset({"Cordless Drill"})


def test_a_voltage_sits_only_on_a_product_type_that_may_carry_one() -> None:
    odd = [r.code for r in ROWS if _attr(r, "voltage_v") and r.product_type not in VOLTAGE_TYPES]
    assert odd == []


def _listed_pieces(row: breadth_rows.Row) -> int | None:
    """The sum of the quantities in the description's "Includes 4 a, 4 b and 4 c." sentence."""
    m = re.match(r"Includes (.+?)\.(?: |$)", row.description)
    if not m:
        return None
    parts = re.split(r", | and ", m.group(1))
    if not all(re.match(r"\d+ \S", p) for p in parts):
        return None
    return sum(int(p.split()[0]) for p in parts)


def test_every_product_that_states_a_piece_count_lists_exactly_that_many_pieces() -> None:
    """For every row with a piece count: title, attribute and listed contents agree."""
    stated = [r for r in ROWS if _attr(r, "piece_count") or _title_count(r)]
    assert len(stated) >= 8
    for r in stated:
        listed = _listed_pieces(r)
        assert listed is not None, f"{r.code}: the description does not list the contents"
        assert listed == int(_attr(r, "piece_count")["value"]) == _title_count(r), r.code


def test_the_attributes_are_deterministic_and_reach_the_standard() -> None:
    """The same rows give the same documents, and the shared standard accepts the new units."""
    from synthetic_ecommerce_data.core.entry import CANONICAL_PER_UNIT

    assert "VLT" in CANONICAL_PER_UNIT
    first = [r.doc()["attributes"] for r in ROWS]
    assert first == [r.doc()["attributes"] for r in ROWS]
