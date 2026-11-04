"""Screws, cap screws and bolts are three nodes under ``Fasteners`` (#767).

One node named all three, so its words stood for each other: ``screws`` reached the bolts, and a
filter on the node did not mean what the shopper typed. #658 had put them together so that
``screws`` reached one place; the maintainer's ruling on #767 replaces that.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.industrial import taxonomy

GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog"

#: Each new node, and the product types it holds.
NODES = {
    "Screws": {
        "lag_screws",
        "screw_deck",
        "screw_drywall",
        "screw_machine",
        "screw_sheet_metal",
        "screw_wood",
    },
    "Cap Screws": {
        "screw_button_head",
        "screw_flat_head",
        "screw_hex_head",
        "screw_low_head",
        "screw_socket_head",
    },
    "Bolts": {"bolt_hex", "carriage_bolts", "sems_bolts"},
}


@pytest.mark.parametrize("node", sorted(NODES))
def test_each_kind_of_fastener_is_its_own_node(node):
    held = {key for key, paths in taxonomy.LEAVES.items() if paths[0][:2] == ("Fasteners", node)}
    assert held == NODES[node]


def test_no_path_keeps_the_node_that_named_all_three():
    nodes = {path[1] for paths in taxonomy.LEAVES.values() for path in paths}
    assert "Bolts, Screws & Cap Screws" not in nodes


def test_the_neighboring_nodes_stay_where_they_are():
    nodes = {path[:2] for paths in taxonomy.LEAVES.values() for path in paths}
    assert ("Fasteners", "Set Screws") in nodes
    assert ("Fasteners", "Specialty Bolts") in nodes


@pytest.mark.parametrize("name", ["flat.jsonl", "nested.jsonl"])
def test_the_committed_catalog_files_no_product_under_the_old_name(name):
    assert b"Bolts, screws & cap screws" not in (GOLDEN / name).read_bytes()


def test_the_committed_catalog_files_each_type_under_its_node():
    types_by_node: defaultdict[str, set[str]] = defaultdict(set)
    with (GOLDEN / "flat.jsonl").open(encoding="utf-8") as lines:
        for line in lines:
            doc = json.loads(line)
            if doc["category_path"][:2] == ["Hardware", "Fasteners"]:
                types_by_node[doc["category_path"][2]].add(doc["product_type"])
    assert types_by_node["Screws"] == NODES["Screws"]
    assert types_by_node["Cap screws"] == NODES["Cap Screws"]
    assert types_by_node["Bolts"] == NODES["Bolts"]
