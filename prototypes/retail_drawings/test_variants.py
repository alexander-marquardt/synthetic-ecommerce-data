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
    return [d for d in DOCS if d["variant_group"].startswith(prefix)]


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


def test_every_bra_doc_holds_only_valid_sizes_and_each_style_has_40_or_more() -> None:
    eu_of = {uk: eu for uk, eu, _ in vr.CUPS}
    us_of = {uk: us for uk, _, us in vr.CUPS}
    for d in _family_docs("BRA-"):
        assert len(d["size_uk"]) >= 40, d["title"]
        for uk, eu, us in zip(d["size_uk"], d["size_eu"], d["size_us"], strict=True):
            band, cup = int(uk[:2]), uk[2:]
            assert vr.bra_size_valid(band, cup), uk
            assert eu == f"{vr.eu_band(band)}{eu_of[cup]}"
            assert us == f"{band}{us_of[cup]}"


def test_the_rosedene_cross_drops_exactly_the_four_forbidden_pairs() -> None:
    style = next(s for s in vr.BRAS if s.code == "ROSEDENE")
    sizes = [r[0] for r in style.size_rows()]
    assert len(sizes) == 5 * 11 - 4
    assert {"36AA", "28FF", "28G", "28GG"}.isdisjoint(sizes)


def test_every_jeans_doc_holds_only_the_sizes_its_leg_length_is_cut_in() -> None:
    for d in _family_docs("JEA-"):
        who, length = _attr(d, "audience"), _attr(d, "length")
        for uk, eu, us in zip(d["size_uk"], d["size_eu"], d["size_us"], strict=True):
            n = int(uk)
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
        rows = list(zip(d["size_uk"], d["size_eu"], d["size_us"], strict=True))
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


def test_a_doc_is_one_style_x_colourway_x_length_and_counts_its_sizes() -> None:
    for fam, styles in vr.FAMILIES.items():
        for s in styles:
            ds = vr.style_docs(fam, s)
            want = len(s.washes) * len(s.lengths) if fam == "Jeans" else len(s.colourways)
            assert len(ds) == want, s.code
            assert {d["variant_group"] for d in ds} == {f"{fam[:3].upper()}-{s.code}"}
            for d in ds:
                assert d["sku_count"] == (len(d["size_uk"]) if "size_uk" in d else 1)
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


def test_the_table_holds_the_three_classes_named_on_the_issue() -> None:
    assert [(r.query, len(r.distractors)) for r in dz.TABLE] == [
        ("lemon", 5),
        ("jeans", 4),
        ("duvet", 4),
    ]


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
    with pytest.raises(ValueError, match="PLT-WEAK-01 scores"):
        dz.check(table, [*CORPUS, weak.doc])


def test_too_few_distractors_and_an_intended_one_are_refused() -> None:
    row = dz.TABLE[0]
    with pytest.raises(ValueError, match="2 distractors"):
        dz.check((_with(row, row.distractors[:2]),))
    lemons = dz.Distractor(dz.LEMONS, "none")
    with pytest.raises(ValueError, match="PLT-LEMONS-01 is an intended product"):
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
        "Jeans": 16, "Bras": 12, "Bedding": 9, "Beauty": 9, "Planted distractors": 14
    }  # fmt: skip
    for r in recs:
        assert ET.fromstring(drawing_svg(r)).tag.endswith("svg")
