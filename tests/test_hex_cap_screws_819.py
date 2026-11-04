"""The catalog stocks hex head cap screws in a node of their own (#819).

A hex cap screw (ASME B18.2.1, SAE J429 grades) is not the hex bolt: closer
tolerances, a washer face, a chamfered point, made to be turned by its head
into a tapped hole. The parametric demo query names one, so the committed
catalog has to carry the exact product, not the hex bolt near miss.
"""

from __future__ import annotations

import json
from pathlib import Path

from synthetic_ecommerce_data.core import bundle

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

NODE = ["Hardware", "Fasteners", "Cap screws", "Hex head cap screws"]

#: The demo query's product, every clause of it, as the catalog spells it.
DEMO = {
    "Dia./Thread Size": "7/16-14",
    "Length": '1-3/4"',
    "Material": "Grade 8 Alloy Steel",
    "Finish": "Zinc Yellow",
}


def _parents() -> list[dict]:
    return [json.loads(line) for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()]


def test_the_hex_head_cap_screws_have_their_own_node_beside_the_socket_cap_screws():
    paths = {tuple(p["category_path"]) for p in _parents()}
    assert tuple(NODE) in paths
    assert ("Hardware", "Fasteners", "Cap screws", "Socket cap screws") in paths
    assert not any(p[:3] == ("Hardware", "Fasteners", "Screws") and "Cap" in p[-1] for p in paths)


def test_the_committed_catalog_stocks_the_demo_hex_cap_screw():
    facets = bundle.flat_facets(GOLDEN)
    found = [
        record
        for parent in _parents()
        if parent["category_path"] == NODE
        for record in bundle.records(parent, facets)
        if all(record.get(name) == value for name, value in DEMO.items())
    ]
    assert found, f"no {NODE[-1]} SKU carries {DEMO}"
