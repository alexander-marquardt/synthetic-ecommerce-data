"""Failure classes 2 to 7 of gen#125: the records, the policy bodies and the recorded proof."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import distractors as dz  # noqa: E402
import house_styles as hs  # noqa: E402
import real_classes as rc  # noqa: E402

CLASS_DOCS = rc.class_docs()
CORPUS = rc.corpus()
PROOF = json.loads((HERE / "real_classes_proof.json").read_text(encoding="utf-8"))
NEW_FIELDS = {"style_id", "product_type", "audience", "size_range", "neckline", "pattern",
              "leg_style", "was_price", "sold_last_5_days", "bestseller_rank"}  # fmt: skip


def _row(query: str) -> rc.ClassRow:
    rows = [r for r in rc.ROWS if r.query == query]
    assert len(rows) == 1
    return rows[0]


def test_the_rows_are_the_observed_classes_2_to_7() -> None:
    assert [(r.n, r.query, len(r.targets), len(r.distractors)) for r in rc.ROWS] == [
        (2, "mattress topper", 3, 6),
        (3, "balloon jeans", 3, 4),
        (4, "womens boat neck top", 3, 6),
        (5, "check contrast bomber jacket", 3, 6),
        (6, "petite sale", 3, 4),
        (7, "womens sale dresses", 3, 5),
        (9, "5 pack socks", 3, 4),
    ]
    assert len(CLASS_DOCS) == 62


def test_the_pack_count_is_a_c62_count_and_the_titles_spell_it_three_ways() -> None:
    fives = [d for d in CLASS_DOCS if d.get("units_per_pack") == 5 and d["audience"] == "adult"]
    assert sorted(d["title"].split()[-1] for d in fives) == ["5", "5pk", "Pack"]
    for d in (d for d in CLASS_DOCS if "units_per_pack" in d):
        count = [a for a in d["attributes"] if a["key"] == "units_per_pack"]
        assert count == [{"key": "units_per_pack", "name": "Units per pack",
                          "value": str(d["units_per_pack"]), "unit_code": "C62",
                          "value_canonical": float(d["units_per_pack"])}]  # fmt: skip


def test_every_class_record_carries_the_policy_fields_from_the_closed_lists() -> None:
    closed = {
        "audience": rc.AUDIENCES,
        "size_range": rc.SIZE_RANGES,
        "neckline": rc.NECKLINES,
        "pattern": rc.PATTERNS,
        "leg_style": rc.LEG_STYLES,
    }
    for d in CLASS_DOCS:
        assert isinstance(d["product_type"], str) and d["product_type"], d["title"]
        assert d["audience"] in rc.AUDIENCES
        for key, values in closed.items():
            assert d.get(key, values[0]) in values, (d["product_id"], key)
        assert isinstance(d["sold_last_5_days"], int) and d["sold_last_5_days"] >= 1
        if "was_price" in d:
            assert d["was_price"] > d["price"], d["product_id"]
    assert CLASS_DOCS
    ranks = sorted(d["bestseller_rank"] for d in CLASS_DOCS)
    assert ranks == list(range(1, len(CLASS_DOCS) + 1))
    best = min(CLASS_DOCS, key=lambda d: d["bestseller_rank"])
    assert best["sold_last_5_days"] == max(d["sold_last_5_days"] for d in CLASS_DOCS)


def test_the_round_4_records_are_unchanged_and_carry_none_of_the_new_fields() -> None:
    base = dz.corpus()
    assert CORPUS[: len(base)] == base
    assert all(not (NEW_FIELDS & d.keys()) for d in base)
    optional = {"was_price", "size_range", "neckline", "pattern", "leg_style"}
    assert all(NEW_FIELDS - optional <= d.keys() for d in CLASS_DOCS)
    ids = [d["product_id"] for d in CORPUS]
    assert len(ids) == len(set(ids))


def test_a_styles_colourway_docs_share_one_style_id_and_title() -> None:
    barrel = [d for d in CLASS_DOCS if d["style_id"] == "PLT-BRLMID"]
    assert len(barrel) == 5
    assert {d["title"] for d in barrel} == {"Mid Rise Barrel Jeans"}
    assert len({d["attributes"][0]["value"] for d in barrel}) == 5
    assert all(d["style_id"] == d["variant_group"] for d in CLASS_DOCS)
    per_style = sorted(
        n for n in (sum(d["style_id"] == s for d in CLASS_DOCS)
                    for s in {d["style_id"] for d in CLASS_DOCS}) if n > 1
    )  # fmt: skip
    assert per_style == [2, 2, 5]


def test_every_target_is_intended_and_no_distractor_is() -> None:
    for row in rc.ROWS:
        for style in row.targets:
            assert all(row.is_intended(d) for d in style.docs()), (row.query, style.code)
        for style, fix in row.distractors:
            assert fix
            assert not any(row.is_intended(d) for d in style.docs()), (row.query, style.code)


def test_the_kids_and_baby_distractors_are_marked_by_audience() -> None:
    young = sorted((d["audience"], d["title"]) for d in CLASS_DOCS if d["audience"] != "adult")
    assert young == [
        ("baby", "Baby Bomber Jacket (3-36 Mths)"),
        ("kids", "Boys' Bomber Jacket (2-8 Yrs)"),
        ("kids", "Girls' Barrel Jeans (6-16 Yrs)"),
        ("kids", "Girls' Party Dress (2-8 Yrs)"),
        ("kids", "Kids' School Socks 5 Pack (6-16 Yrs)"),
    ]


def test_every_class_brand_has_a_house_style() -> None:
    assert sorted({d["brand"] for d in CLASS_DOCS} - set(hs.HOUSE_STYLES)) == []


# --------------------------------------------------------------------------
# The Elasticsearch bodies
# --------------------------------------------------------------------------


def test_the_baseline_is_text_times_popularity_with_no_filter() -> None:
    for row in rc.ROWS:
        fs = rc.baseline_body(row)["query"]["function_score"]
        assert fs["query"] == rc.text_query(row.query)
        assert fs["functions"] == list(rc.POPULARITY)
        assert "collapse" not in rc.baseline_body(row)


def test_the_policy_body_carries_each_filter_boost_and_collapse() -> None:
    sale = rc.policy_body(_row("petite sale"))
    assert sale["query"]["function_score"]["query"]["bool"]["filter"] == [
        {"terms": {"size_range": ["petite"]}},
        {"script": {"script": rc.ON_SALE}},
    ]
    balloon = rc.policy_body(_row("balloon jeans"))
    assert balloon["collapse"] == {"field": "style_id"}
    assert balloon["query"]["function_score"]["functions"][-1] == {
        "filter": {"terms": {"leg_style": ["balloon"]}},
        "weight": 10.0,
    }
    assert sum("collapse" in rc.policy_body(r) for r in rc.ROWS) == 1


def test_the_synonym_is_search_time_only() -> None:
    body = rc.index_body()
    assert set(body) == {"settings", "mappings"}
    title = body["mappings"]["properties"]["title"]
    assert (title["analyzer"], title["search_analyzer"]) == ("plain", "with_synonyms")
    analyzers = body["settings"]["analysis"]["analyzer"]
    assert "styles" not in analyzers["plain"]["filter"]
    assert "styles" in analyzers["with_synonyms"]["filter"]


# --------------------------------------------------------------------------
# The recorded proof
# --------------------------------------------------------------------------


def test_the_committed_proof_holds_the_claim_over_the_current_records() -> None:
    assert rc.verdicts(PROOF, CORPUS) == []
    assert PROOF["docs"] == len(CORPUS)


def test_the_readme_table_is_the_committed_proofs() -> None:
    readme = (HERE.parents[1] / "README.md").read_text(encoding="utf-8")
    assert rc.markdown(PROOF, CORPUS) in readme


def test_a_target_in_the_baseline_top_3_is_refused() -> None:
    assert [r["query"] for r in PROOF["rows"]] == [r.query for r in rc.ROWS] != []
    bad = copy.deepcopy(PROOF)
    bad["rows"][0]["baseline"][2] = bad["rows"][0]["policy"][0]
    assert rc.verdicts(bad, CORPUS) == ["'mattress topper': a target is in the baseline top 3"]


def test_a_distractor_or_a_short_policy_top_3_is_refused() -> None:
    assert len(PROOF["rows"]) == len(rc.ROWS) == 7
    bad = copy.deepcopy(PROOF)
    bad["rows"][1]["policy"][2] = bad["rows"][1]["baseline"][0]
    bad["rows"][4]["policy"] = bad["rows"][4]["policy"][:2]
    assert rc.verdicts(bad, CORPUS) == [
        "'balloon jeans': the policy top 3 is not all targets",
        "'petite sale': the policy top 3 is not all targets",
    ]


def test_a_proof_over_other_records_is_stale() -> None:
    changed = [*CORPUS[:-1], {**CORPUS[-1], "sold_last_5_days": 1}]
    assert rc.verdicts(PROOF, changed) == [
        "the proof was taken over another catalog: re-run es_proof.py"
    ]


def test_es_proof_runs_and_names_its_host_option() -> None:
    out = subprocess.run(
        [sys.executable, str(HERE / "es_proof.py"), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--host" in out.stdout


@pytest.mark.parametrize("row", rc.ROWS, ids=lambda r: r.query)
def test_the_proof_names_only_records_of_the_catalog(row: rc.ClassRow) -> None:
    ids = {d["product_id"] for d in CORPUS}
    rec = next(r for r in PROOF["rows"] if r["query"] == row.query)
    assert len(rec["baseline"]) == 5
    assert {h["product_id"] for h in (*rec["baseline"], *rec["policy"])} <= ids
