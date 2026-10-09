"""The retail size parameter (gen#125): a target SKU count, reached from the 328 templates.

``prototypes/retail_drawings/scale.py`` derives styles from the hand-authored
ones until the SKUs reach the target. These tests hold it at the first load
size, about 20K SKUs: it reaches the count, stays deterministic, meets the
output standard, adds no duplicate title or clone, keeps every derived fact
honest to its template, and keeps the drawings bounded.
"""

from __future__ import annotations

import collections
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core.standard import check_catalog

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402

#: The first load: about 20K SKUs, about 1,000 styles.
TARGET = 20_000
TEMPLATES = 328
#: Every template exhausted, seed 0: today's ceiling (styles, SKUs). More brands per
#: type, title-visible values or templates raise it; update this pin then.
CAPACITY = (1_866, 30_150)


@pytest.fixture(scope="module")
def built() -> scale.Scaled:
    return scale.build(TARGET)


@pytest.fixture(scope="module")
def pairs(built) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """(derived style, its template) for every derived style."""
    by_id = {t["product_id"]: t for t in scale.templates()}
    return [(r, by_id[built.template_of[r["product_id"]]]) for r in built.records[TEMPLATES:]]


def test_the_size_parameter_reaches_the_target_sku_count(built):
    assert built.skus >= TARGET
    assert built.skus - built.records[-1]["sku_count"] < TARGET
    assert len(built.records) > TEMPLATES
    assert len(built.template_of) == len(built.records) - TEMPLATES


def test_the_templates_come_first_and_a_small_target_takes_a_prefix(built):
    ids = [t["product_id"] for t in scale.templates()]
    assert [r["product_id"] for r in built.records[:TEMPLATES]] == ids
    small = scale.build(100)
    assert small.template_of == {}
    assert [r["product_id"] for r in small.records] == ids[: len(small.records)]
    assert small.skus >= 100


def test_the_build_is_deterministic_by_seed():
    a, b, c = scale.build(9_000, seed=3), scale.build(9_000, seed=3), scale.build(9_000, seed=4)
    assert a.records == b.records
    assert [r["title"] for r in a.records] != [r["title"] for r in c.records]


def test_the_20k_build_meets_the_output_standard(built):
    assert check_catalog(scale.documents(built)) == []


def test_a_derived_style_adds_no_duplicate_title_and_no_twin(built, pairs):
    titles = collections.Counter(r["title"] for r in built.records)
    twins = collections.Counter(scale.twin_key(r) for r in built.records)
    assert [r["title"] for r, _ in pairs if titles[r["title"]] > 1] == []
    assert [r["product_id"] for r, _ in pairs if twins[scale.twin_key(r)] > 1] == []
    got, authored = scale.distinctness(built.records), scale.distinctness(scale.templates())
    assert (got["duplicate_titles"], got["clones"]) == (
        authored["duplicate_titles"],
        authored["clones"],
    )


def test_near_duplicate_listings_stay_rare(built):
    report = scale.distinctness(built.records, sample=500)
    assert report["near_duplicate_sample"] == 500
    assert report["near_duplicate_rate"] <= 0.05


def test_a_derived_style_keeps_its_place_and_every_value_that_names_it(pairs):
    for r, t in pairs:
        assert [r[k] for k in ("category_path", "category_leaf", "product_type", "department")] == [
            t[k] for k in ("category_path", "category_leaf", "product_type", "department")
        ]
        names = " ".join([*t["category_path"], t["product_type"]])
        frozen = scale.FROZEN_KEYS - {"line"}
        kept = {
            (a["key"], str(a["value"]))
            for a in t["attributes"]
            if a["key"] in frozen or scale._has_word(names, str(a["value"]))
        }
        assert kept <= {(a["key"], str(a["value"])) for a in r["attributes"]}, r["product_id"]
        assert [a["key"] for a in r["attributes"]] == [a["key"] for a in t["attributes"]]


def test_a_changed_value_is_rewritten_in_the_title(pairs):
    rewritten = 0
    for r, t in pairs:
        new = {a["key"]: str(a["value"]) for a in r["attributes"]}
        for a in t["attributes"]:
            old = str(a["value"])
            if a["key"] == "line" or new[a["key"]] == old or not scale._has_word(t["title"], old):
                continue
            assert scale._has_word(r["title"], new[a["key"]]), (
                r["product_id"],
                r["title"],
                new[a["key"]],
            )
            rewritten += 1
    assert rewritten > 0


def test_a_derived_style_carries_its_range_name_in_title_and_line(pairs):
    for r, _ in pairs:
        assert r["product_line"] in scale.RANGE_NAMES
        assert scale._has_word(r["title"], r["product_line"])
        lines = [a["value"] for a in r["attributes"] if a["key"] == "line"]
        assert lines in ([], [r["product_line"]])


def test_skus_are_the_templates_size_run_times_a_color_subset(pairs):
    def runs(rec: dict) -> dict[Any, list[dict]]:
        out: dict[Any, list[dict]] = collections.defaultdict(list)
        for s in rec["skus"]:
            out[s.get("color")].append({k: v for k, v in s.items() if k != "sku"})
        return out

    for r, t in pairs:
        mine, theirs = runs(r), runs(t)
        assert mine and set(mine) <= set(theirs)
        assert all(mine[c] == theirs[c] for c in mine), r["product_id"]
        assert [s["sku"] for s in r["skus"]] == [
            f"{r['product_id']}-{n:03d}" for n in range(1, len(r["skus"]) + 1)
        ]


def test_every_leaf_keeps_products_with_a_long_tail(built):
    report = scale.coverage(built.records)
    assert report["leaves"] == len({t["category_leaf"] for t in scale.templates()})
    sizes = report["leaf_size"]
    assert sizes["min"] >= 1
    assert sizes["max"] >= 5 * sizes["median"]
    assert set(report["skus_per_style_by_department"]) == {
        str(t["department"][0]) for t in scale.templates()
    }


def test_the_drawings_stay_bounded(built):
    authored = scale.coverage(scale.templates())["images"]["distinct_drawings"]
    assert scale.coverage(built.records)["images"]["distinct_drawings"] <= 2 * authored


def test_the_cli_writes_the_report_and_the_documents(tmp_path):
    out, report = tmp_path / "retail.jsonl", tmp_path / "report.json"
    argv = ["--skus", "8000", "--out", str(out), "--report", str(report)]
    done = subprocess.run(
        [sys.executable, str(RETAIL / "scale.py"), *argv],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    got = json.loads(report.read_text(encoding="utf-8"))
    assert got["reached_target"] is True
    assert got["standard_problems"] == 0
    assert got["coverage"]["skus"] >= 8000
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == got["coverage"]["styles"]
    assert sum(json.loads(line)["variant_count"] for line in lines) == got["coverage"]["skus"]


def test_a_target_past_the_capacity_stops_there_and_the_cli_says_so(tmp_path):
    report = tmp_path / "report.json"
    done = subprocess.run(
        [sys.executable, str(RETAIL / "scale.py"), "--skus", "100000", "--report", str(report)],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert done.returncode == 2, done.stderr[-2000:]
    assert "short: 30150 SKUs of 100000" in done.stderr
    got = json.loads(report.read_text(encoding="utf-8"))
    assert got["reached_target"] is False
    assert got["standard_problems"] == 0
    assert (got["coverage"]["styles"], got["coverage"]["skus"]) == CAPACITY
