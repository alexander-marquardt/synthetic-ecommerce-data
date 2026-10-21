"""A product id and a SKU name the product, not its row position (gen#626).

A partial reload writes a SKU as the Elasticsearch ``_id``, so a SKU that moves between two
exports overwrites another product (51K moved and 14.7K named a different product in the
measured pair). Guard 1: add a template, rebuild, and every other SKU and product id stays.
Guard 2: the generator raises on a collision and does not bump a counter past it.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402
import stable_ids  # noqa: E402
import variants  # noqa: E402

#: The derived SKUs the build draws past the templates: enough styles to read.
DERIVED_SKUS = 2_000
#: Where the added template goes: near the start, so every template after it moves a row.
INSERT_AT = 3


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _added(tpls: list[dict]) -> dict:
    """A template of its own leaf and type: no pool, brand pool or near-duplicate check of any
    other style sees it, so the only thing the build can change for them is a row position."""
    src = next(t for t in scale.derivable(tpls) if t["product_id"].startswith("JEA-"))
    new = copy.deepcopy(src)
    new["product_id"] = "BRD-ZZ626"
    new["title"] = "Registry Guard Test Jacket"
    new["category_leaf"] = "Registry Guard Test Leaf"
    new["product_type"] = "registry-guard-test"
    for s in new["skus"]:
        s["sku"] = new["product_id"] + s["sku"][len(src["product_id"]):]
    return new


def _build(monkeypatch, tpls: list[dict], total: int) -> scale.Scaled:
    monkeypatch.setattr(scale, "templates", lambda baseline=True: copy.deepcopy(tpls))
    return scale.build(total)


def _skus(records: list[dict]) -> dict[str, str]:
    return {s["sku"]: r["product_id"] for r in records for s in r["skus"]}


def test_an_added_template_moves_no_other_sku_or_product_id(monkeypatch, templates):
    total = sum(t["sku_count"] for t in templates) + DERIVED_SKUS
    base = _build(monkeypatch, templates, total)
    extra = _added(templates)
    grown = [*templates[:INSERT_AT], extra, *templates[INSERT_AT:]]
    after = _build(monkeypatch, grown, total + extra["sku_count"])
    before_skus, after_skus = _skus(base.records), _skus(after.records)
    by_id = {r["product_id"]: r for r in base.records}
    derived = [p for p in by_id if p in base.template_of]
    assert len(derived) > 20, "the build must draw derived styles for the guard to read"
    # No SKU names another product: a style both builds hold is the same document.
    kept = {r["product_id"]: r for r in after.records}
    changed = [p for p in derived if p in kept and kept[p] != by_id[p]]
    assert not changed, f"{len(changed)} styles are another product now, e.g. {changed[:3]}"
    own = {r["product_id"] for r in after.records
           if r["product_id"] == extra["product_id"]
           or after.template_of.get(r["product_id"]) == extra["product_id"]}
    new = {p for s, p in after_skus.items() if s not in before_skus}
    assert new <= own, f"styles other than the added one's are new: {sorted(new - own)[:3]}"
    # What leaves is the tail of the drawn styles (the added SKUs take their room), no other.
    gone = [p for p in derived if p not in {r["product_id"] for r in after.records}]
    assert gone == derived[len(derived) - len(gone):], "a style left that was not the last drawn"
    assert len(gone) <= 3, f"{len(gone)} styles left for {extra['sku_count']} added SKUs"


def test_the_same_template_yields_the_same_ids_whatever_the_target(monkeypatch, templates):
    total = sum(t["sku_count"] for t in templates)
    small = _build(monkeypatch, templates, total + 800)
    large = _build(monkeypatch, templates, total + 2_400)
    first = _skus(small.records)
    second = _skus(large.records)
    assert len(first) > 0
    assert set(first) <= set(second), "a smaller build holds a SKU the larger build lacks"
    assert {s: p for s, p in first.items() if second[s] != p} == {}


def test_two_skus_of_one_product_with_the_same_axes_raise():
    skus = [{"size": "M", "color": "Blue", "price": p} for p in (10.0, 12.0)]
    swatches = {"Blue": {"color": "Blue", "hex": "#00f", "pattern": "plain"}}
    with pytest.raises(stable_ids.IdCollision):
        variants.product("BRD-X", skus, swatches)


def test_two_products_with_one_id_raise():
    one = {"product_id": "BRD-A", "skus": [{"sku": "BRD-A-1"}]}
    two = {"product_id": "BRD-A", "skus": [{"sku": "BRD-A-2"}]}
    with pytest.raises(stable_ids.IdCollision):
        stable_ids.check_unique([one, two])


def test_two_products_with_one_sku_raise():
    one = {"product_id": "BRD-A", "skus": [{"sku": "SAME"}]}
    two = {"product_id": "BRD-B", "skus": [{"sku": "SAME"}]}
    with pytest.raises(stable_ids.IdCollision):
        stable_ids.check_unique([one, two])


def test_a_build_that_gives_two_styles_one_id_raises(monkeypatch, templates):
    monkeypatch.setattr(scale, "style_id", lambda prefix, *identity: f"{prefix}-SAME")
    total = sum(t["sku_count"] for t in templates) + 400
    with pytest.raises(stable_ids.IdCollision):
        _build(monkeypatch, templates, total)


def test_the_department_rates_give_the_department_shares(templates):
    """The rates are constants, so a template added to a department moves its share: this fails
    then, and DEPARTMENT_RATE is recomputed (shares / summed leaf weights)."""
    base = scale.derivable(templates)
    want, got = scale.department_targets(base), scale.department_shares(base)
    off = {d: (round(want[d], 3), round(got.get(d, 0), 3)) for d in want
           if abs(want[d] - got.get(d, 0)) > 0.03}
    assert not off, f"department shares drift from their targets (target, got): {off}"
