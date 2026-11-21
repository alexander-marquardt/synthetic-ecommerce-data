"""#1101, slice 3: the build report audits what it tilts, and a turned fridge fails the build.

The maintainer, 2026-11-21: "Can you have the generator do a sanity check on what it is tilting?"
The retail build report (:func:`.scale.main`) has a ``tilt`` section (:func:`.tilt_audit.audit`):
per category, the products and how many are turned, the 20 largest turned items, and each
turned product in a never-tilt category or over the size limit, which fails the build.

The products are the recorded slice of slice 1 (``tests/fixtures/tilt_slice_1101.json``: a sofa,
a mountain bike, a fridge, a wardrobe and a glove from the built catalogue). The planted turn
switches off slice 1's guard and slice 2's level default for the fridge alone, the regression
the audit is there to catch.
"""

from __future__ import annotations

import copy
import json
import pathlib

import pytest

from synthetic_ecommerce_data.domains.retail import orientation, scale, tilt_audit

SLICE = json.loads(
    (pathlib.Path(__file__).parent / "fixtures" / "tilt_slice_1101.json").read_text()
)

FRIDGE = "BRD-GLA001"
GLOVE = "BRD-DCGLV1"


@pytest.fixture
def turned_fridge(monkeypatch):
    """The fridge drawn ``upright`` (+-36 degrees), as every unsure shape was before #1101."""
    of, level_because = orientation.of, orientation.level_because
    monkeypatch.setattr(orientation, "of", lambda s: "upright" if s == "fridge" else of(s))
    monkeypatch.setattr(
        orientation,
        "level_because",
        lambda rec: None if rec["product_id"] == FRIDGE else level_because(rec),
    )
    fridge = next(r for r in SLICE if r["product_id"] == FRIDGE)
    assert orientation.drawn_angle(fridge) != 0, "the planted fridge must turn"


def test_the_slice_audit_counts_one_turned_product_the_glove_and_refuses_none():
    section = tilt_audit.audit(SLICE)
    assert (section["products"], section["turned"]) == (5, 1)
    assert [r["product_id"] for r in section["largest_turned"]] == [GLOVE]
    assert section["refused"] == []
    gloves = [k for k, c in section["per_category"].items() if c["turned"]]
    assert len(gloves) == 1 and "Gloves" in gloves[0], section["per_category"]
    assert sum(c["products"] for c in section["per_category"].values()) == 5


def test_a_turned_fridge_is_refused_for_its_category(turned_fridge):
    section = tilt_audit.audit(SLICE)
    assert [r["product_id"] for r in section["refused"]] == [FRIDGE]
    (row,) = section["refused"]
    assert row["because"] == ["category"], row  # it states only its 55 cm width
    assert row["category"].startswith("Home > Large Appliances")
    assert {r["product_id"] for r in section["largest_turned"]} == {FRIDGE, GLOVE}


def test_a_turned_glove_that_states_a_size_over_the_limit_is_refused_for_size(monkeypatch):
    glove = copy.deepcopy(next(r for r in SLICE if r["product_id"] == GLOVE))
    glove["attributes"].append({"key": "item_length", "value": "75"})
    monkeypatch.setattr(orientation, "level_because", lambda rec: None)  # the guard off
    refused = tilt_audit.audit([glove])["refused"]
    assert len(refused) == 1, refused
    (row,) = refused
    assert (row["because"], row["stated_cm"]) == (["size"], 75.0)


def test_the_largest_turned_list_holds_at_most_twenty_largest_first(monkeypatch):
    glove = next(r for r in SLICE if r["product_id"] == GLOVE)
    many = []
    for n in range(30):
        rec = copy.deepcopy(glove)
        rec["product_id"] = f"{GLOVE}-{n}"
        rec["attributes"].append({"key": "item_length", "value": str(10 + n)})
        many.append(rec)
    monkeypatch.setattr(orientation, "drawn_angle", lambda rec: 15)
    largest = tilt_audit.audit(many)["largest_turned"]
    assert [r["stated_cm"] for r in largest] == [float(39 - n) for n in range(tilt_audit.LARGEST)]


def _build_report(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(scale, "build", lambda skus, seed=0: scale.Scaled(copy.deepcopy(SLICE), {}))
    report = tmp_path / "report.json"
    code = scale.main(["--skus", "1", "--report", str(report)])
    return code, json.loads(report.read_text()), capsys.readouterr().err


def test_the_build_report_carries_the_tilt_audit_and_passes(monkeypatch, tmp_path, capsys):
    code, report, err = _build_report(monkeypatch, tmp_path, capsys)
    assert code == 0, err
    assert report["tilt"]["turned"] == 1 and report["tilt"]["refused"] == []


def test_the_build_fails_on_a_planted_turned_fridge(turned_fridge, monkeypatch, tmp_path, capsys):
    code, report, err = _build_report(monkeypatch, tmp_path, capsys)
    assert code == 3, err
    assert [r["product_id"] for r in report["tilt"]["refused"]] == [FRIDGE]
    assert f"tilt refused (category): {FRIDGE}" in err, err
