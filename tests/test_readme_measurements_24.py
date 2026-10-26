"""The README holds no measured number a build can move (#24).

The README typed the flat shape's over-match counts, the defect table's
achieved column, the repeated-pair parent counts and the field-map sizes by
hand, and every one went stale as types landed. The same rule as #103 now
covers them: the build measures, ``golden-catalog/stats.json`` carries the
figures (``figures.flat_overmatch``, ``comparisons``), and the README points
at the file and at ``ecom-generate report`` instead of quoting.

The README also says what the personal site hosts: a small sample of
drawings, never the full set.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.prism.derive import flat_overmatch_figures

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "golden-catalog"
REBUILD = "uv run ecom-generate build --out golden-catalog"

SHANK = "Shank dia."
SHANK_VALUE = "3/8"


@pytest.fixture(scope="module")
def readme() -> str:
    return (ROOT / "README.md").read_text("utf-8")


@pytest.fixture(scope="module")
def stats() -> dict:
    return json.loads((GOLDEN / "stats.json").read_text("utf-8"))


def _flat() -> list[dict]:
    lines = (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()
    return [json.loads(line) for line in lines]


def test_the_flat_overmatch_is_the_committed_catalogs(stats: dict) -> None:
    """Counted here from ``flat.jsonl`` alone, as the README used to say it was."""
    matching = publishing = 0
    for doc in _flat():
        attributes = doc["attributes"]
        if any(a["name"] == SHANK for a in attributes) and any(
            a["value"] == SHANK_VALUE for a in attributes
        ):
            matching += 1
            publishing += any(
                a["name"] == SHANK and a["value"] == SHANK_VALUE for a in attributes
            )
    assert stats.get("figures", {}).get("flat_overmatch") == {
        "attribute": SHANK,
        "value": SHANK_VALUE,
        "matching": matching,
        "publishing": publishing,
    }, f"stats.json carries no (or a stale) flat over-match; run {REBUILD}"


def _doc(*pairs: tuple[str, str]) -> dict:
    return {"attributes": [{"name": name, "value": value} for name, value in pairs]}


def test_the_overmatch_counts_a_value_on_another_attribute_only_as_matching() -> None:
    """The count itself, on four constructed documents, so the code is what is tested."""
    rows = [
        _doc((SHANK, SHANK_VALUE)),  # publishes the shank: matching and publishing
        _doc((SHANK, "1/2"), ("Cut dia.", SHANK_VALUE)),  # the over-match: matching only
        _doc(("Cut dia.", SHANK_VALUE)),  # no shank attribute at all
        _doc((SHANK, "1/2")),  # a shank, but not 3/8
    ]
    assert flat_overmatch_figures(rows) == {
        "attribute": SHANK,
        "value": SHANK_VALUE,
        "matching": 2,
        "publishing": 1,
    }


def test_the_readme_types_no_overmatch_count(readme: str) -> None:
    typed = re.findall(r"matches\s+\*{0,2}\d[\d,]*\*{0,2}\s+documents", readme)
    assert typed == [], (
        f"README types the flat over-match count {typed}; point at "
        "`figures.flat_overmatch` in golden-catalog/stats.json"
    )


def test_the_readme_types_no_defect_table(readme: str) -> None:
    table = re.search(r"\|\s*property\s*\|\s*target\s*\|\s*achieved\s*\|", readme)
    stamped = re.search(r"Measured on `[0-9a-f]{7,}` with `uv run ecom-generate build`", readme)
    assert table is None and stamped is None, (
        "README types the defect table or the commit it was measured on; the "
        "rows are `comparisons` in golden-catalog/stats.json and "
        "`ecom-generate report` prints them"
    )


def test_the_readme_points_at_the_report(readme: str, stats: dict) -> None:
    assert "ecom-generate report" in readme
    assert "`comparisons`" in readme
    assert stats["comparisons"], "stats.json carries the defect comparisons"


def test_the_readme_types_no_repeated_pair_count(readme: str) -> None:
    typed = re.findall(r"\b\d+\s+of\s+the\s+[\d,]+\s+golden\s+parents", readme)
    assert typed == [], f"README types the repeated-pair parent count {typed}; read stats.json"


def test_the_readme_types_no_field_map_size(readme: str) -> None:
    typed = re.findall(
        r"Not all \d+\b|about \d+ distinct attribute names|\*\*fields in the field map\*\*"
        r"|\|\s*attributes declared\s*\|",
        readme,
    )
    assert typed == [], (
        f"README types field-map sizes {typed}; the generated "
        "`synthetic_industrial_flat.yaml` is the count"
    )


def test_the_readme_says_the_site_hosts_only_a_sample(readme: str) -> None:
    text = " ".join(readme.split())
    assert "hosts only a small sample" in text
    assert "few hundred" in text
    assert "release bundle" in text


def test_the_readme_invites_no_demo_to_point_at_the_site() -> None:
    text = " ".join((ROOT / "README.md").read_text("utf-8").split())
    site_urls = re.findall(r"https?://(?:www\.)?alexmarquardt\.com\S*", text)
    imaged = [url for url in site_urls if re.search(r"\.svg|/images", url)]
    inviting = re.findall(r"point (?:a|your|the) demo(?:s)? (?:at|to) the (?:site|blog)", text)
    assert imaged == [] and inviting == [], f"README points demos at the site: {imaged + inviting}"
