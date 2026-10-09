"""Round 4's tests: size validity, SKU counts, distractors outranking, departments.

Run: ``uv run pytest prototypes/retail_drawings/test_variants.py``.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_preview4  # noqa: E402
import distractors as dz  # noqa: E402
import house_styles as hs  # noqa: E402
import variants as vr  # noqa: E402
from build_preview import drawing_svg  # noqa: E402
from departments import DEPARTMENTS  # noqa: E402
from departments import check as check_departments  # noqa: E402

DOCS = vr.docs()
CORPUS = dz.corpus()


def _family_docs(prefix: str) -> list[dict]:
    return [d for d in DOCS if d["product_id"].startswith(prefix)]


def _sizes(sku: dict) -> tuple[str, str, str]:
    """One SKU's size in every size system: (UK, EU, US)."""
    return sku["size_uk"], sku["size_eu"], sku["size_us"]


def _attr(doc: dict, key: str) -> str:
    return next(a["value"] for a in doc["attributes"] if a["key"] == key)


# --------------------------------------------------------------------------
# Size validity
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("band", "cup"),
    [(36, "AA"), (40, "A"), (28, "FF"), (42, "HH"), (46, "J"), (27, "C"), (34, "Z")],
)
def test_a_bra_size_a_rule_forbids_is_refused(band: int, cup: str) -> None:
    assert vr.bra_size_valid(band, cup) is False


@pytest.mark.parametrize(("band", "cup"), [(34, "AA"), (40, "B"), (30, "FF"), (40, "J"), (46, "H")])
def test_a_bra_size_every_rule_allows_is_kept(band: int, cup: str) -> None:
    assert vr.bra_size_valid(band, cup) is True


def test_every_bra_sku_holds_a_valid_size_and_each_color_has_40_or_more() -> None:
    eu_of = {uk: eu for uk, eu, _ in vr.CUPS}
    us_of = {uk: us for uk, _, us in vr.CUPS}
    for d in _family_docs("BRA-"):
        for c in d["color_options"]:
            assert sum(s["color"] == c["color"] for s in d["skus"]) >= 40, (d["title"], c)
        for uk, eu, us in map(_sizes, d["skus"]):
            band, cup = int(uk[:2]), uk[2:]
            assert vr.bra_size_valid(band, cup), uk
            assert eu == f"{vr.eu_band(band)}{eu_of[cup]}"
            assert us == f"{band}{us_of[cup]}"


def test_the_rosedene_cross_drops_exactly_the_four_forbidden_pairs() -> None:
    style = next(s for s in vr.BRAS if s.code == "ROSEDENE")
    sizes = [r[0] for r in style.size_rows()]
    assert len(sizes) == 5 * 11 - 4
    assert {"36AA", "28FF", "28G", "28GG"}.isdisjoint(sizes)


def test_every_jeans_sku_holds_only_a_size_its_leg_length_is_cut_in() -> None:
    for d in _family_docs("JEA-"):
        who = _attr(d, "audience")
        for sku in d["skus"]:
            uk, eu, us = _sizes(sku)
            length, n = sku["length"], int(uk)
            assert vr.jeans_size_valid(who, length, n), (d["title"], uk)
            assert (eu, us) == ((str(n + 28), str(n - 4)) if who == "Womens" else (str(n + 16), uk))


def test_the_harrow_petite_stops_at_uk_18_and_the_long_starts_at_uk_8() -> None:
    harrow = next(s for s in vr.JEANS if s.code == "HARROW")
    assert [r[0] for r in harrow.sizes("Petite")] == ["4", "6", "8", "10", "12", "14", "16", "18"]
    assert [r[0] for r in harrow.sizes("Long")][0] == "8"
    assert [r[0] for r in harrow.sizes("Extra Long")] == ["10", "12", "14", "16", "18", "20", "22"]


def test_a_leg_length_with_no_rule_is_refused() -> None:
    with pytest.raises(KeyError):
        vr.jeans_size_valid("Womens", "Short", 10)


def test_bedding_sizes_come_from_one_chart_per_system() -> None:
    for d in _family_docs("BED-"):
        rows = [_sizes(s) for s in d["skus"]]
        assert rows, d["title"]
        assert all(row in vr.BED.values() for row in rows), d["title"]


# --------------------------------------------------------------------------
# SKU counts
# --------------------------------------------------------------------------

EXPECTED = {
    "Jeans": {"HARROW": 444, "BRINDLE": 208, "CORVEY": 144, "MARDALE": 110, "PENHALLOW": 65,
              "QUENBY": 132, "ROOKLEY": 92, "TOLLAND": 370, "WEXCOMBE": 248, "ASHLOW": 126,
              "KELDEN": 155, "FENNICK": 63},
    "Bras": {"SORREL": 318, "LINNET": 184, "FARNLEY": 270, "HALDEN": 472, "THORNBY": 80,
             "KINVER": 207, "ELSDON": 126, "BRAYFORD": 42, "PELLOW": 96, "ROSEDENE": 255},
    "Bedding": {"DUVHOL": 4, "DUVDWN": 3, "COVPER": 24, "COVPRT": 9, "PILMIC": 2, "PCSPER": 18,
                "TOPMEM": 4, "PROQLT": 5},
    "Beauty": {"LIPSAT": 24, "LIPMAT": 12, "BALTNT": 5, "FNDFTH": 40, "FNDSRM": 20, "TNTMST": 8},
}  # fmt: skip


def test_the_sku_count_of_every_style_is_pinned() -> None:
    assert vr.sku_counts() == EXPECTED


def test_family_totals_and_style_counts() -> None:
    totals = {f: sum(c.values()) for f, c in vr.sku_counts().items()}
    assert totals == {"Jeans": 2157, "Bras": 2050, "Bedding": 69, "Beauty": 109}
    assert {f: len(s) for f, s in vr.FAMILIES.items()} == {
        "Jeans": 12, "Bras": 10, "Bedding": 8, "Beauty": 6
    }  # fmt: skip


def test_the_mix_reaches_the_hundreds_and_stays_under_ten() -> None:
    every = [n for c in vr.sku_counts().values() for n in c.values()]
    assert sum(n >= 200 for n in every) == 9
    assert sum(n < 10 for n in every) == 8
    assert max(every) <= 500


def test_a_doc_is_one_style_and_its_skus_cover_every_color_and_length() -> None:
    for fam, styles in vr.FAMILIES.items():
        for s in styles:
            ds = vr.style_docs(fam, s)
            assert len(ds) == 1, s.code
            (d,) = ds
            assert d["product_id"] == f"{fam[:3].upper()}-{s.code}"
            assert d["sku_count"] == len(d["skus"]) == len({k["sku"] for k in d["skus"]})
            assert len(d["color_options"]) == len(s.colors), s.code
            if fam == "Jeans":
                pairs = {(k["color"], k["length"]) for k in d["skus"]}
                assert len(pairs) == len(s.washes) * len(s.lengths), s.code
            else:
                assert len({k["color"] for k in d["skus"]}) == len(s.colors), s.code
    assert len({d["product_id"] for d in CORPUS}) == len(CORPUS)


# --------------------------------------------------------------------------
# Distractors
# --------------------------------------------------------------------------


def test_every_distractor_outranks_the_best_intended_product_on_text() -> None:
    dz.check()
    for row in dz.TABLE:
        best, each = dz.scores(row, CORPUS)
        assert best > 0, row.query
        assert all(s > best for _, s in each), (row.query, best, each)
        assert dz.MIN_DISTRACTORS <= len(each) <= dz.MAX_DISTRACTORS


def test_the_table_holds_the_three_issue_classes_and_the_gift_bag_class() -> None:
    assert [(r.query, len(r.distractors), len(r.tail)) for r in dz.TABLE] == [
        ("lemon", 7, 0),
        ("oranges", 4, 0),
        ("jeans", 4, 0),
        ("duvet", 4, 0),
        ("dinosaur", 3, 0),
        ("gift bag", 10, 8),
    ]


# --------------------------------------------------------------------------
# Gift bags: an observed "gift bag" failure, with every name invented
# --------------------------------------------------------------------------

def _gift() -> dz.Row:
    rows = [r for r in dz.TABLE if r.query == "gift bag"]
    assert len(rows) == 1
    return rows[0]


def test_the_real_gift_bag_is_one_product_of_three_sizes_x_three_prints_in_gift_wrap() -> None:
    gift = _gift()
    bags = [d for d in CORPUS if gift.is_intended(d)]
    assert [d["product_id"] for d in bags] == ["GFT-KRAFT"]
    skus = bags[0]["skus"]
    assert bags[0]["sku_count"] == len(skus) == 9
    assert {d["category_path"][1] for d in bags} == {"Gift Wrap"}
    assert sorted(s["size"] for s in skus) == ["Large"] * 3 + ["Medium"] * 3 + ["Small"] * 3
    assert len({s["color"] for s in skus}) == 3
    assert len({(s["color"], s["size"]) for s in skus}) == 9
    # The observed failure: the real ones never say "gift" in their text.
    assert all("gift" not in dz.text_of(d) for d in bags)


def test_the_gift_bag_distractors_hold_the_observed_mix() -> None:
    gift = _gift()
    kinds = [x.doc["category_path"][-1] for x in gift.distractors]
    assert sorted(kinds) == sorted(
        ["Bath & Body Gifts", "Skincare Gifts", "Haircare Gifts",
         "Wash Bags", "Make-Up Bags", "Hospital Bags",
         "Make-Up Gift Sets", "Make-Up Gift Sets",
         "Travel Sets", "Summer Sets"]
    )  # fmt: skip
    beauty = [x.doc["title"] for x in gift.distractors if x.doc["category_path"][1] == "Gift Sets"]
    assert sum(t.endswith("Gift Bag") for t in beauty) == 3
    assert sum("with Limited Edition" in t and t.endswith("Bag") for t in beauty) == 2
    tail = sorted(x.doc["category_path"][-1] for x in gift.tail)
    assert tail == sorted(
        ["Wallet Gift Sets", "Wallet Gift Sets", "Hampers", "Hampers", "Letterbox Gifts",
         "Letterbox Gifts", "Gift Plants", "Keyrings"]
    )  # fmt: skip
    titles = [x.doc["title"] for x in gift.tail]
    assert sum(" in " in t and t.endswith("Gift Bag") for t in titles) == 1
    assert sum(t.startswith("Gift Boxed") for t in titles) == 1


def test_a_duplicate_listing_publishes_one_product_id_under_two_categories() -> None:
    assert len({d["product_id"] for d in CORPUS}) == len(CORPUS)
    dup = dz.corpus(duplicate_listing=True)
    assert len(dup) == len(CORPUS) + 1
    ids = [d["product_id"] for d in dup]
    twice = sorted({i for i in ids if ids.count(i) == 2})
    assert twice == [dz.DUPLICATED]
    a, b = (d for d in dup if d["product_id"] == dz.DUPLICATED)
    assert a["category_path"] != b["category_path"]
    assert {k: v for k, v in a.items() if k != "category_path"} == {
        k: v for k, v in b.items() if k != "category_path"
    }
    assert dz.DUPLICATED in {x.doc["product_id"] for x in _gift().distractors}


def test_the_committed_samples_and_preview_are_what_the_builder_writes() -> None:
    html, ndjson = build_preview4.outputs()
    assert ndjson == (HERE / "samples4.ndjson").read_text(encoding="utf-8")
    assert html == (HERE / "preview4.html").read_text(encoding="utf-8")


def test_the_duplicate_listing_option_adds_exactly_one_record() -> None:
    _, plain = build_preview4.outputs()
    _, dup = build_preview4.outputs(duplicate_listing=True)
    extra = dup.splitlines()[len(plain.splitlines()) :]
    assert dup.startswith(plain)
    assert len(extra) == 1
    assert f'"product_id": "{dz.DUPLICATED}"' in extra[0]


def test_the_readme_class_table_names_every_class() -> None:
    readme = (HERE.parents[1] / "README.md").read_text(encoding="utf-8")
    for row in dz.TABLE:
        assert f"| {row.cls} | *{row.query}*" in readme, row.cls


def _with(row: dz.Row, extra: tuple[dz.Distractor, ...]) -> dz.Row:
    return dz.Row(row.cls, row.query, row.intended, row.is_intended, row.policy, extra)


def test_a_distractor_that_cannot_outrank_is_refused() -> None:
    weak = dz.Distractor(
        dz.product(
            "WEAK", "Citrus Garden Candle", "Velling Apothecary", "Home",
            ("Home", "Fragrance", "Candles"), 12.0,
            "A hand-poured soy candle with notes of grapefruit, bergamot, vetiver, cedar and "
            "a faint hint of lemon, in a reusable glass tumbler with a wooden lid.",
            vr.drawing("jar", vr.cw("Amber", "#d9a95b")),
        ),
        "none",
    )  # fmt: skip
    row = dz.TABLE[0]
    table = (_with(row, (*row.distractors, weak)),)
    with pytest.raises(ValueError, match="PLT-WEAK scores"):
        dz.check(table, [*CORPUS, weak.doc])


def test_too_few_distractors_and_an_intended_one_are_refused() -> None:
    row = dz.TABLE[0]
    with pytest.raises(ValueError, match="2 distractors"):
        dz.check((_with(row, row.distractors[:2]),))
    lemons = dz.Distractor(dz.LEMONS, "none")
    with pytest.raises(ValueError, match="PLT-LEMONS is an intended product"):
        dz.check((_with(row, (*row.distractors, lemons)),))


# --------------------------------------------------------------------------
# Departments, brands and drawings
# --------------------------------------------------------------------------


def test_every_doc_has_a_department_from_the_closed_list() -> None:
    for d in CORPUS:
        assert d["department"], d["title"]
        assert set(d["department"]) <= set(DEPARTMENTS), d["title"]
    assert len(DEPARTMENTS) == 20


def test_an_unknown_or_missing_department_is_refused() -> None:
    with pytest.raises(ValueError, match="not on the closed list"):
        check_departments(["Womenswear"])
    with pytest.raises(ValueError, match="no department"):
        check_departments([])


def test_every_brand_has_a_house_style_and_every_sample_draws() -> None:
    assert sorted({d["brand"] for d in CORPUS} - set(hs.HOUSE_STYLES)) == []
    sections = build_preview4.samples()
    recs = [r for rs in sections.values() for r in rs]
    assert len(recs) == build_preview4.SAMPLES
    assert {k: len(v) for k, v in sections.items()} == {
        "Jeans": 12, "Bras": 10, "Bedding": 8, "Beauty": 6, "Planted distractors": 25,
        "Print range": 91, "Gift wrap": 1, "Gift bag distractors": 18,
        "Observed failure classes": 123, "Footwear": 31, "Footwear distractors": 3,
    }  # fmt: skip
    for r in recs:
        assert ET.fromstring(drawing_svg(r)).tag.endswith("svg")
