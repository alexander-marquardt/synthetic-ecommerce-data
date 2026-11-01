"""A size system is read from one chart in core, and retail keeps none of its own (gen#125).

Slice 2 of the 2026-10-28 ruling on gen#125: the charts that give a size's UK, EU and US value
live in :mod:`synthetic_ecommerce_data.core.size_charts`, each retail module that sizes a
product reads them, and :func:`synthetic_ecommerce_data.core.standard.check_catalog` refuses a
variant whose three values are no row of a core chart (``tests/test_output_standard.py``).
"""

from __future__ import annotations

import re
from pathlib import Path

from synthetic_ecommerce_data.core import size_charts as sc
from synthetic_ecommerce_data.domains.retail import (
    footwear_rows,
    samples,
    samples_round2,
    variants,
)

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = ROOT / "src" / "synthetic_ecommerce_data" / "domains"

#: The ways a retail module used to build a chart of its own: the women's and men's formulas,
#: the shoe chart builder and the bra band's EU name.
CHART_BUILDERS = re.compile(r"uk \+ 28|w \+ 16|def _chart\b|def eu_band\b")


def test_retail_reads_each_chart_from_core():
    reads = {
        "variants.WOMENS_WAIST": (variants.WOMENS_WAIST, sc.WOMENS),
        "variants.MENS_WAIST": (variants.MENS_WAIST, sc.MENS_WAIST),
        "variants.BANDS": (variants.BANDS, sc.BRA_BANDS),
        "variants.CUPS": (variants.CUPS, sc.BRA_CUPS),
        "variants.BED": (variants.BED, sc.BEDDING),
        "footwear_rows.WOMEN": (footwear_rows.WOMEN, sc.WOMENS_SHOES),
        "footwear_rows.MEN": (footwear_rows.MEN, sc.MENS_SHOES),
        "footwear_rows.KIDS": (footwear_rows.KIDS, sc.KIDS_SHOES),
        "footwear_rows.SLIPPERS_WOMEN": (footwear_rows.SLIPPERS_WOMEN, sc.SLIPPERS_WOMEN),
        "footwear_rows.SLIPPERS_MEN": (footwear_rows.SLIPPERS_MEN, sc.SLIPPERS_MEN),
    }
    assert [name for name, (theirs, core) in reads.items() if theirs is not core] == []


def test_the_preview_samples_size_from_core_rows():
    rows = {
        "samples.WOMENS": samples.WOMENS,
        "samples.SHOES": samples.SHOES,
        "samples.LETTER": samples.LETTER,
        "samples.BRA": samples.BRA,
        "samples_round2.MENS_WAIST": samples_round2.MENS_WAIST,
        "samples_round2.KIDS": samples_round2.KIDS,
        "samples_round2.BABY": samples_round2.BABY,
    }
    every = {row for chart in sc.CHARTS.values() for row in chart.values()}
    off = {name: [r for r in chart if r not in every] for name, chart in rows.items()}
    assert {name: bad for name, bad in off.items() if bad} == {}
    assert all(rows.values())


def test_no_domain_builds_a_size_chart():
    found = [
        f"{path.relative_to(ROOT)}:{n}: {line.strip()}"
        for path in sorted(DOMAINS.rglob("*.py"))
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if CHART_BUILDERS.search(line)
    ]
    assert found == []


def test_a_chart_row_is_three_size_strings_and_its_key_names_it():
    assert sc.CHARTS
    for name, chart in sc.CHARTS.items():
        assert chart, name
        for key, row in chart.items():
            assert len(row) == 3 and all(isinstance(v, str) and v for v in row), (name, key)
            assert str(key) == row[0] or name in ("bedding", "slippers_women", "slippers_men"), (
                name,
                key,
            )


def test_the_bra_chart_is_every_band_by_every_cup():
    assert len(sc.BRAS) == len(sc.BRA_BANDS) * len(sc.BRA_CUPS)
    assert sc.BRAS.get("34DD") == ("34DD", "75E", "34DD")
    assert sc.BRAS.get("28A") == ("28A", "60A", "28A")
