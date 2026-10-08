"""Failure classes 2 to 7 of gen#125: the records, the policy bodies and the recorded proof."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import distractors as dz  # noqa: E402
import house_styles as hs  # noqa: E402
import kit  # noqa: E402
import kit_home  # noqa: E402,F401 -- registers table_lamp
import kit_more  # noqa: E402,F401 -- registers chairbed
import real_classes as rc  # noqa: E402

CLASS_DOCS = rc.class_docs()
CORPUS = rc.corpus()
PROOF = json.loads((HERE / "real_classes_proof.json").read_text(encoding="utf-8"))
NEW_FIELDS = {"rating", "product_type", "audience", "size_range", "neckline", "pattern",
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
        (10, "beer", 3, 5),
        (11, "oranges", 3, 6),
        (12, "face cream", 3, 8),
        (13, "single bed", 3, 5),
        (14, "rose gold", 5, 5),
    ]
    # One product per style: the rows, the beauty styles, the offers, the honey
    # and the crew-neck tee.
    assert len(CLASS_DOCS) == 102 + 2 + 4 + 1 + 1


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


def test_a_style_in_five_colors_is_one_product_holding_them_all() -> None:
    barrel = _style("PLT-BRLMID")
    assert barrel["title"] == "Mid Rise Barrel Jeans"
    assert len(barrel["color_options"]) == len(_colors(barrel)) == 5
    assert sum(d["title"] == "Mid Rise Barrel Jeans" for d in CLASS_DOCS) == 1
    assert all(not ({"style_id", "variant_group"} & d.keys()) for d in CLASS_DOCS)
    per_style = sorted(n for n in (len(_colors(d)) for d in CLASS_DOCS) if n > 1)
    # The nine styles sold in more than one color, and the crew-neck tee.
    assert per_style == [2, 2, 2, 2, 2, 3, 3, 3, 4, 5]


def test_every_target_is_intended_and_no_distractor_is() -> None:
    for row in rc.ROWS:
        for style in row.targets:
            assert row.is_intended(style.doc()), (row.query, style.code)
        for style, fix in row.distractors:
            assert fix
            assert not row.is_intended(style.doc()), (row.query, style.code)


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
# Variant structure: style (one doc), color and size options, SKU (nested)
# --------------------------------------------------------------------------


def _style(product_id: str) -> dict:
    docs = [d for d in CLASS_DOCS if d["product_id"] == product_id]
    assert len(docs) == 1, product_id
    return docs[0]


def _colors(d: dict) -> list[str]:
    """The SKU colors of ``d``, in first-SKU order."""
    out: list[str] = []
    for s in d["skus"]:
        if "color" in s and s["color"] not in out:
            out.append(s["color"])
    return out


def test_a_style_carries_one_swatch_per_sku_color_with_its_family() -> None:
    barrel = _style("PLT-BRLMID")
    shades = ["Mid Wash", "Light Wash", "Black", "Ecru", "Vintage Blue"]
    assert [o["color"] for o in barrel["color_options"]] == shades
    families = ["blue", "blue", "black", "cream", "blue"]
    assert [o["family"] for o in barrel["color_options"]] == families
    colorless = [d for d in CLASS_DOCS if "color_options" not in d]
    assert len(colorless) == 32  # food and furniture: no color facet, no swatches
    for d in colorless:
        assert _colors(d) == [] and not any("color_family" in s for s in d["skus"]), d["product_id"]
    for d in (d for d in CLASS_DOCS if "color_options" in d):
        assert [o["color"] for o in d["color_options"]] == _colors(d), d["product_id"]
        family = {s["color"]: s["color_family"] for s in d["skus"]}
        for o in d["color_options"]:
            assert o["family"] == family[o["color"]] and o["family"] in rc.COLOR_FAMILIES
        # The tile draws the lead color: the first swatch.
        assert d["color_options"][0]["hex"] == d["drawing"]["base"], d["product_id"]


def test_rating_and_review_count_are_pooled_once_per_style() -> None:
    for d in CLASS_DOCS:
        assert 3.5 <= d["rating"] <= 5.0 and d["review_count"] >= 1, d["product_id"]
        assert not any("rating" in s or "review_count" in s for s in d["skus"])
    assert len({d["rating"] for d in CLASS_DOCS}) > 10
    # Popularity is the style's too: the sales of every color, summed.
    styles = [s for r in rc.ROWS for s in (*r.targets, *(x for x, _ in r.distractors))]
    for s in styles:
        assert _style(f"PLT-{s.code}")["sold_last_5_days"] == sum(n for _, n in s.colors), s.code
    assert _style("PLT-BRLMID")["sold_last_5_days"] == 3610


def test_legwear_skus_are_waist_by_inside_leg_with_stock_per_color() -> None:
    mid = _style("PLT-BRLMID")
    assert len(mid["skus"]) == mid["sku_count"] == 5 * 10 * 5
    assert {tuple(sorted(s)) for s in mid["skus"]} == {
        ("color", "color_family", "in_stock", "inside_leg", "price", "sku", "waist")
    }
    assert [s["sku"] for s in mid["skus"]] == [f"PLT-BRLMID-{n:03d}" for n in range(1, 251)]
    per_color = {c: [s for s in mid["skus"] if s["color"] == c] for c in _colors(mid)}
    for skus in per_color.values():
        assert len(skus) == 10 * 5
        assert sorted({s["waist"] for s in skus}, key=int) == [str(n) for n in range(6, 25, 2)]
        assert {s["inside_leg"] for s in skus} == set(rc.INSIDE_LEGS)
        assert 0 < sum(not s["in_stock"] for s in skus) < len(skus) // 2
    greyed = [frozenset((s["waist"], s["inside_leg"]) for s in skus if not s["in_stock"])
              for skus in per_color.values()]  # fmt: skip
    assert len(set(greyed)) == len(per_color) == 5
    assert mid["size_options"] == {"inside_leg": list(rc.INSIDE_LEGS),
                                   "waist": [str(n) for n in range(6, 25, 2)]}  # fmt: skip
    legwear = [d for d in CLASS_DOCS if d["product_type"] in ("Jeans", "Trousers")]
    assert len(legwear) == 13
    assert all(d["skus"] and "rise" in d for d in legwear)
    kids = _style("PLT-BRLKID")
    assert {s["inside_leg"] for s in kids["skus"]} == {"Regular"}
    assert all(s["waist"].endswith(" Yrs") for s in kids["skus"])


def test_size_range_is_the_set_of_in_stock_lengths_across_the_style() -> None:
    assert rc.derive_size_range([
        {"inside_leg": "Short/Petite", "in_stock": False},
        {"inside_leg": "Extra Long", "in_stock": True},
        {"inside_leg": "Regular", "in_stock": True},
    ]) == ["regular", "tall"]  # fmt: skip
    assert rc.LENGTH_RANGE["Short/Petite"] == "petite"
    legwear = [d for d in CLASS_DOCS if d["skus"] and "inside_leg" in d["skus"][0]]
    assert len(legwear) == 13
    for d in legwear:
        assert d["size_range"] == rc.derive_size_range(d["skus"]), d["product_id"]
    assert _style("PLT-PETJNS")["size_range"] == ["petite"]
    assert _style("PLT-STRJNS")["size_range"] == ["regular", "petite", "tall"]
    # Cut in petite, but every petite SKU is sold out: no petite in its range.
    slim = _style("PLT-SLMJNS")
    assert "Short/Petite" in {s["inside_leg"] for s in slim["skus"]}
    assert slim["size_range"] == ["regular", "tall"]
    for d in (d for d in CLASS_DOCS if "size_range" in d):
        assert d["size_range"] == [r for r in rc.SIZE_RANGES if r in d["size_range"]] != []
    assert sum("size_range" in d for d in CLASS_DOCS) == 42


def test_bedding_skus_are_bed_sizes_labelled_with_their_dimension_and_priced_each() -> None:
    topper = _style("PLT-MTTMEM")
    white = {"color": "White", "color_family": "white"}
    stock = {"in_stock": True}
    assert topper["skus"] == [
        {"sku": "PLT-MTTMEM-001", **white, "bed_size": "Single (3 ft)", "price": 60.0, **stock},
        {"sku": "PLT-MTTMEM-002", **white, "bed_size": "Double (4 ft 6)", "price": 75.0, **stock},
        {"sku": "PLT-MTTMEM-003", **white, "bed_size": "King Size (5 ft)", "price": 90.0, **stock},
        {"sku": "PLT-MTTMEM-004", **white, "bed_size": "Super King Size (6 ft)", "price": 105.0,
         **stock},
    ]  # fmt: skip
    assert topper["size_options"] == {"bed_size": list(rc.BED_SIZES)}
    assert (topper["price"], topper["price_min"], topper["price_max"]) == (60.0, 60.0, 105.0)
    bedded = [d for d in CLASS_DOCS if d["skus"] and "bed_size" in d["skus"][0]]
    # 9 bedding styles (label and price only), then 8 beds (with dimensions).
    assert len(bedded) == 17
    assert sum("width_cm" in d["skus"][0] for d in bedded) == 8


def test_price_min_and_max_are_derived_from_the_skus() -> None:
    for d in CLASS_DOCS:
        prices = [s["price"] for s in d["skus"]] or [d["price"]]
        assert (d["price_min"], d["price_max"]) == (min(prices), max(prices)), d["product_id"]
        assert d["price"] == d["price_min"]
        assert d["sku_count"] == max(1, len(d["skus"]))


def test_beauty_shades_are_the_sku_colors_of_one_product_with_a_unit_size() -> None:
    shades = {f"PLT-{s.code}" for s in rc.BEAUTY}
    beauty = [d for d in CLASS_DOCS if d["product_id"] in shades]
    assert sorted((d["product_id"], d["unit_size"], d["unit_measure"]) for d in beauty) == [
        ("PLT-BTYFND", 30.0, "ml"),
        ("PLT-BTYLIP", 1.9, "g"),
    ]
    lip = _style("PLT-BTYLIP")
    assert _colors(lip) == ["Wild Honey", "Mocha Kiss", "Cherry Pop"] and lip["sku_count"] == 3
    assert {d["brand"] for d in beauty} == {"Kestlewood Cosmetics"}
    row_codes = {s.code for r in rc.ROWS for s in (*r.targets, *(x for x, _ in r.distractors))}
    assert {s.code for s in rc.BEAUTY} == {"BTYLIP", "BTYFND"} and not row_codes & {"BTYLIP"}


def test_the_index_maps_the_skus_as_nested_and_the_variant_facets_as_keywords() -> None:
    props = rc.index_body()["mappings"]["properties"]
    assert props["skus"]["type"] == "nested"
    assert {k for d in CLASS_DOCS for s in d["skus"] for k in s} == set(props["skus"]["properties"])
    for key in ("size_range", "rise"):
        assert props[key] == {"type": "keyword"}
    # Color is per SKU: a color filter or facet goes through the nested rows.
    for key in ("sku", "color", "color_family", "finish", "size", "bed_size"):
        assert props["skus"]["properties"][key] == {"type": "keyword"}, key
    assert not {"color", "color_family", "color_shade"} & props.keys()


def test_jeans_carry_the_rise_their_drawing_shows() -> None:
    jeans = [d for d in CLASS_DOCS if d["product_type"] == "Jeans"]
    assert len(jeans) == 9
    for d in jeans:
        assert d["rise"] in rc.RISES and d["rise"] == d["drawing"]["params"]["rise"]


# --------------------------------------------------------------------------
# The Elasticsearch bodies
# --------------------------------------------------------------------------


def test_the_baseline_is_text_times_popularity_with_no_filter() -> None:
    for row in rc.ROWS:
        fs = rc.baseline_body(row)["query"]["function_score"]
        assert fs["query"] == rc.text_query(row.query)
        assert fs["functions"] == list(rc.POPULARITY)
        assert "collapse" not in rc.baseline_body(row)


def test_the_policy_body_carries_each_filter_and_boost_and_never_collapses() -> None:
    sale = rc.policy_body(_row("petite sale"))
    assert sale["query"]["function_score"]["query"]["bool"]["filter"] == [
        {"terms": {"size_range": ["petite"]}},
        {"script": {"script": rc.ON_SALE}},
    ]
    balloon = rc.policy_body(_row("balloon jeans"))
    assert balloon["query"]["function_score"]["functions"][-1] == {
        "filter": {"terms": {"leg_style": ["balloon"]}},
        "weight": 10.0,
    }
    # One doc per style: nothing left to collapse.
    assert sum("collapse" in rc.policy_body(r) for r in rc.ROWS) == 0


def test_the_color_search_filters_one_in_stock_sku_and_returns_the_matches() -> None:
    body = rc.color_body("tee", "Navy")
    fs = body["query"]["function_score"]
    assert fs["functions"] == list(rc.POPULARITY)
    assert fs["query"]["bool"]["must"] == rc.text_query("tee")
    assert fs["query"]["bool"]["filter"] == [{"nested": {
        "path": "skus",
        "query": {"bool": {"filter": [{"term": {"skus.color": "Navy"}}],
                           "must_not": [{"term": {"skus.in_stock": False}}]}},
        "inner_hits": {"size": 100}}}]  # fmt: skip
    colors = body["aggs"]["skus"]["aggs"]["colors"]
    assert body["aggs"]["skus"]["nested"] == {"path": "skus"}
    assert colors["terms"]["field"] == "skus.color"
    assert colors["aggs"] == {"products": {"reverse_nested": {}}}


def test_the_rulings_tee_is_one_product_of_11_skus_in_three_colors() -> None:
    tee = _style("PLT-CRWTEE")
    assert tee["sku_count"] == 11 and _colors(tee) == ["Navy", "White", "Heather Grey"]
    assert tee["size_options"] == {"size": ["S", "M", "L", "XL"]}
    assert rc.COLOR_QUERY == ("tee", "Navy")


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


def test_the_committed_color_search_preselects_the_navy_skus_and_counts_products() -> None:
    got = PROOF["color_search"]
    tee = _style("PLT-CRWTEE")
    navy = [s["sku"] for s in tee["skus"] if s["color"] == "Navy" and s["in_stock"]]
    assert len(navy) == 4
    # The nested filter returns the product once, with the SKUs that matched.
    assert [h["product_id"] for h in got["nested"]] == ["PLT-CRWTEE"]
    assert [s["sku"] for s in got["nested"][0]["matched_skus"]] == navy
    assert {s["color"] for s in got["nested"][0]["matched_skus"]} == {"Navy"}
    # Plain text finds the product too, but names no SKU: nothing to preselect.
    assert "PLT-CRWTEE" in [h["product_id"] for h in got["baseline"]]
    assert all(h["matched_skus"] == [] for h in got["baseline"])
    # The facet counts SKUs and, through reverse_nested, products.
    assert got["facet"] == [
        {"color": "Navy", "skus": 4, "products": 1},
        {"color": "White", "skus": 4, "products": 1},
        {"color": "Heather Grey", "skus": 3, "products": 1},
    ]


def test_the_readme_table_is_the_committed_proofs() -> None:
    readme = (HERE.parents[1] / "README.md").read_text(encoding="utf-8")
    assert rc.markdown(PROOF, CORPUS) in readme


def test_a_target_in_the_baseline_top_3_is_refused() -> None:
    assert [r["query"] for r in PROOF["rows"]] == [r.query for r in rc.ROWS] != []
    bad = copy.deepcopy(PROOF)
    bad["rows"][0]["baseline"][2] = bad["rows"][0]["policy"][0]
    assert rc.verdicts(bad, CORPUS) == ["'mattress topper': a target is in the baseline top 3"]


def test_a_distractor_or_a_short_policy_top_3_is_refused() -> None:
    assert len(PROOF["rows"]) == len(rc.ROWS) == 12
    bad = copy.deepcopy(PROOF)
    bad["rows"][1]["policy"][2] = bad["rows"][1]["baseline"][0]
    bad["rows"][4]["policy"] = bad["rows"][4]["policy"][:2]
    assert rc.verdicts(bad, CORPUS) == [
        "'balloon jeans': the policy top 3 is not all targets",
        "'petite sale': the policy top 3 is not all targets",
    ]


def test_a_proof_over_other_records_is_stale() -> None:
    changed = [*CORPUS[:-1], {**CORPUS[-1], "sold_last_5_days": CORPUS[-1]["sold_last_5_days"] + 1}]
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


# --------------------------------------------------------------------------
# The proof's fingerprint covers what Elasticsearch indexes, not the drawing
# --------------------------------------------------------------------------


def test_a_drawing_change_keeps_the_fingerprint_and_a_title_change_alters_it() -> None:
    """The mapping is ``dynamic: false`` and maps no ``drawing``: a new tile needs no re-run."""
    assert "drawing" not in rc.index_body()["mappings"]["properties"]
    redrawn = [{**d, "drawing": {**d["drawing"], "base": "#000000"}} for d in CORPUS]
    retitled = [{**CORPUS[0], "title": CORPUS[0]["title"] + " Deluxe"}, *CORPUS[1:]]
    assert rc.fingerprint(redrawn) == rc.fingerprint(CORPUS)
    assert rc.fingerprint(retitled) != rc.fingerprint(CORPUS)
    assert rc.verdicts(PROOF, redrawn) == []
    assert rc.verdicts(PROOF, retitled) == [
        "the proof was taken over another catalog: re-run es_proof.py"
    ]


# --------------------------------------------------------------------------
# The rose gold table lamp: the record says rose gold base, white linen shade
# --------------------------------------------------------------------------

_LAMP_BASE_D = "M200,206"  # the gourd base's path
_LAMP_SHADE_D = "M146,62"  # the tapered shade's path


def _fill_of(svg: str, d_prefix: str) -> str:
    found = re.findall(rf'<path d="{d_prefix}[^"]*" fill="([^"]+)"', svg)
    assert len(found) == 1, d_prefix
    return found[0]


def _lamp_svg(drawing: dict) -> str:
    fill = kit.Fill(drawing["pattern"], drawing["base"], drawing["accent"])
    return kit.render("table_lamp", fill, params=drawing.get("params"))


def test_the_lamp_base_and_shade_each_take_their_color_from_the_record() -> None:
    """Swapping the two colors in the shape fails this: the colors are told apart."""
    svg = kit.render(
        "table_lamp",
        kit.Fill("solid", "#112233", "#445566"),
        params={"shade": "#aabbcc"},
    )
    assert _fill_of(svg, _LAMP_BASE_D) == "#112233"
    assert _fill_of(svg, _LAMP_SHADE_D) == "#aabbcc"


def test_the_rose_gold_lamp_is_drawn_with_a_rose_gold_base_and_a_white_linen_shade() -> None:
    rec = _style("PLT-RGLAMP")
    assert "rose gold metal base and a white linen shade" in rec["description"]
    svg = _lamp_svg(rec["drawing"])
    assert _fill_of(svg, _LAMP_BASE_D) == rec["drawing"]["base"] == "#d8a28f"
    shade = _fill_of(svg, _LAMP_SHADE_D)
    assert shade == rec["drawing"].get("params", {}).get("shade")
    assert min(int(shade[i : i + 2], 16) for i in (1, 3, 5)) >= 0xE0  # near white


def test_the_chairbed_is_an_armchair_with_a_mattress_pulled_out() -> None:
    """Back, two arms and a seat in the record's color; a mattress section and a dashed bed."""
    svg = kit.render("chairbed", kit.Fill("solid", "#123456", "#654321"))
    assert svg.count('fill="#123456"') == 4  # the back, the seat and the two arms
    assert svg.count('d="M112,296 L288,296') == 1  # the section pulled out of the seat's front
    assert svg.count("stroke-dasharray") == 2  # the unfolded bed and the mattress seam
