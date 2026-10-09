"""The measured catalog figures are build output, not prose (#103).

A figure the default build measures (how many types, brands and drawings, the
facet rule's dispersion band) moves with every type a pull request adds. Typed
into the README, the drawings doc or a source constant, it put every type PR
on the same lines, so each one conflicted with the last to merge and had to be
merged and re-measured by hand.

``ecom-generate build`` now writes them into ``stats.json`` under ``figures``,
beside the ``lines`` and ``skus`` it already carried. The golden test rebuilds
that file and compares bytes, so a figure that moves still reds, naming the
rebuild command, and ``scripts/merge_pr.sh`` resolves a conflict in it by
rebuilding. These tests hold the two ends: the figures are the committed
catalog's, read off it independently of the build; and no doc or source
comment restates one, which is what made the conflicts.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.industrial.generate import all_type_keys

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "golden-catalog"
REBUILD = "uv run ecom-generate build --out golden-catalog"

#: Where the figures used to be typed. A file that quotes one again conflicts
#: with every type PR again.
QUOTING = (
    "README.md",
    "docs/drawings.md",
    "docs/adding-a-type.md",
    "src/synthetic_ecommerce_data/prism/derive.py",
)


@pytest.fixture(scope="module")
def stats() -> dict:
    return json.loads((GOLDEN / "stats.json").read_text("utf-8"))


def _jsonl(name: str) -> list[dict]:
    lines = (GOLDEN / name).read_text("utf-8").splitlines()
    return [json.loads(line) for line in lines]


def test_the_build_writes_the_measured_figures(stats: dict) -> None:
    figures = stats.get("figures", {})
    assert sorted(figures) == ["catalog", "dispersion", "drawings"], (
        f"golden-catalog/stats.json carries no measured figures; run {REBUILD}"
    )


def test_the_catalog_and_drawing_figures_are_the_committed_catalogs(stats: dict) -> None:
    """Read off the committed files, not from the code that wrote them."""
    flat = _jsonl("flat.jsonl")
    images = _jsonl("images.jsonl")
    largest = max(images, key=lambda image: (image["bytes"], image["image_id"]))
    figures = stats.get("figures", {})
    assert figures.get("catalog") == {
        "modelled_types": len(all_type_keys("modelled")) + len(all_type_keys("new")),
        "breadth_categories": len(all_type_keys("breadth")),
        "brands": len({doc["brand"] for doc in flat}),
    }
    assert figures.get("drawings") == {
        "count": len(images),
        "bytes": sum(image["bytes"] for image in images),
        "geometry": dict(sorted(Counter(image["geometry"] for image in images).items())),
        "largest_bytes": largest["bytes"],
        "largest_product_type": largest["product_type"],
    }


def _quotations(stats: dict) -> dict[str, str]:
    """Each measured figure as the prose spelled it, by the figure it quotes.

    The whitespace between words is any run, because a figure and its noun
    were often split across a wrapped line.
    """
    figures = stats.get("figures", {})
    catalog = figures.get("catalog", {})
    drawings = figures.get("drawings", {})
    patterns = {
        "skus": rf"\b{stats['skus']:,}\b",
        "lines": rf"\b{stats['lines']:,}\b",
    }
    if catalog:
        patterns["catalog.modelled_types"] = rf"\b{catalog['modelled_types']}\s+depth\s+types"
        patterns["catalog.breadth_categories"] = (
            rf"\b{catalog['breadth_categories']}\s+\[?breadth\s+categor"
        )
        patterns["catalog.brands"] = rf"\b{catalog['brands']}\s+invented\s+brands"
    if drawings:
        patterns["drawings.bytes"] = rf"\b{drawings['bytes'] / 1e6:.1f}\s+MB"
        patterns["drawings.largest_bytes"] = rf"\b{drawings['largest_bytes']:,}\s+bytes"
        for rung, count in drawings["geometry"].items():
            patterns[f"drawings.geometry.{rung}"] = rf"\b{count:,}\s+`{rung}`"
    for key, value in figures.get("dispersion", {}).items():
        # Four-place ratios only: a two-place share such as 0.28 is also a
        # census share elsewhere in the README.
        if isinstance(value, float) and len(str(value).partition(".")[2]) >= 3:
            patterns[f"dispersion.{key}"] = rf"(?<![\d.]){re.escape(str(value))}\b"
    return patterns


@pytest.mark.parametrize("path", QUOTING)
def test_no_doc_restates_a_figure_the_build_measures(stats: dict, path: str) -> None:
    text = (ROOT / path).read_text("utf-8")
    quoted = sorted(
        f"{figure} ({match.group(0)!r}, line {text.count(chr(10), 0, match.start()) + 1})"
        for figure, pattern in _quotations(stats).items()
        for match in re.finditer(pattern, text)
    )
    assert quoted == [], (
        f"{path} restates figures the build measures: {quoted}. Point at "
        f"`figures` (or `skus` / `lines`) in golden-catalog/stats.json instead; "
        f"{REBUILD} rewrites them there"
    )


def test_no_per_type_size_is_typed_by_hand() -> None:
    """A type's lines and SKUs are ``stats.json``'s (``type_facts.default_size``).

    A ``default_lines`` / ``default_skus`` field or a ``SHARED_SIZE`` table
    typed again would put every type PR back on the same lines (#103).
    """
    pattern = re.compile(r"\bdefault_lines\b|\bdefault_skus\b|\bSHARED_SIZE\b")
    paths = [
        *(ROOT / "src").rglob("*.py"),
        *(ROOT / "tests").glob("*.py"),
        ROOT / "docs" / "adding-a-type.md",
    ]
    offenders = sorted(
        str(path.relative_to(ROOT))
        for path in paths
        if path.name != Path(__file__).name and pattern.search(path.read_text("utf-8"))
    )
    assert offenders == [], f"typed-by-hand per-type sizes in {offenders}; read stats.json"
