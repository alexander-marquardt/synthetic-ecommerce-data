"""The retail build's measured totals are build output, not prose (gen#162, as #115 did for #103).

The styles, SKUs, per-department and per-grocery-family counts, the grocery attribute-value
counts and the near-duplicate rate move with every grocery or type pull request. Typed into
a test, the README or a docstring, each such PR restated them in about ten places and
conflicted with its siblings on every one.

``prototypes/retail_drawings/retail_figures.py`` writes them to ``golden-retail/stats.json``.
These tests hold the two ends: the committed file is what the build measures, and no test,
doc or source comment restates a total in it. Invariants keep their own asserts elsewhere:
no twins in a family, every allergen derived from the ingredients, and the caps.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import retail_figures  # noqa: E402

REBUILD = retail_figures.REBUILD

#: Where the totals used to be typed. A file that quotes one again conflicts with every
#: grocery or type PR again. This module and ``retail_figures.py`` are the only places a
#: total may be named, and they name none.
QUOTING = (
    "README.md",
    "prototypes/retail_drawings/scale.py",
    "prototypes/retail_drawings/grocery.py",
    "tests/test_grocery_154.py",
    "tests/test_grocery_beer_oranges_161.py",
    "tests/test_grocery_ingredients_154.py",
    "tests/test_output_standard.py",
    "tests/test_retail_color_words.py",
    "tests/test_retail_distractors.py",
    "tests/test_retail_drawing_honesty.py",
    "tests/test_retail_grocery_in_scale_154.py",
    "tests/test_retail_image_release.py",
    "tests/test_retail_scale.py",
)

#: Constants that tune the build, not totals it measures: a small total that happens to equal
#: one (gen#200's 40 household styles and ``ATTEMPTS = 40``) is a collision, not a quotation.
TUNING = ("ATTEMPTS",)


#: Sections of a quoting file that report the INDUSTRIAL build. Their figures (a bearing count of
#: 11,340) are not retail totals and may equal one by chance, so the guard does not read them;
#: a retail PR must never bend its data to dodge such a collision. Keyed by file, by heading line.
INDUSTRIAL_SECTIONS = {"README.md": ("### The 100K catalog",)}


def _scoped(path: str, text: str) -> str:
    """``text`` with each industrial section blanked, line for line so a line number stays true.

    A section runs from its heading to the next heading of any level. A heading that is no longer
    there fails, so a renamed section cannot silently widen or narrow what the guard reads."""
    lines = text.split("\n")
    for heading in INDUSTRIAL_SECTIONS.get(path, ()):
        assert heading in lines, f"{path}: the industrial section {heading!r} is gone; update it"
        start = lines.index(heading)
        after = range(start + 1, len(lines))
        end = next((i for i in after if lines[i].startswith("#")), len(lines))
        lines[start:end] = [""] * (end - start)
    return "\n".join(lines)


@pytest.fixture(scope="module")
def stats() -> dict:
    return retail_figures.committed()


def _numbers(node: object, path: str = "") -> dict[str, int | float]:
    """Every leaf of the figures by its dotted path (a department or a family is a key)."""
    if isinstance(node, dict):
        found: dict[str, int | float] = {}
        for name, child in node.items():
            found.update(_numbers(child, f"{path}.{name}"))
        return found
    return {path.lstrip("."): node}  # type: ignore[dict-item]


def _quotations(stats: dict) -> dict[str, str]:
    """Each measured total as a test or prose would spell it, by the figure it quotes.

    A number of four digits or more is refused anywhere (``90071``, ``90_071``, ``90,071``).
    A shorter one collides with ordinary numbers, so it is refused only as the value of a
    constant (``AUTHORED = 328``) or in front of the noun it counts (``328 authored styles``).
    A rate is refused as a percentage (``3.5%``).
    """
    patterns: dict[str, str] = {}
    for name, value in _numbers(stats).items():
        if name.startswith(("departments.", "grocery_families.")):
            continue  # read at run time; never typed (see test_the_per_family_counts_add_up)
        if isinstance(value, float):
            for places in (1, 2):
                text = f"{value * 100:.{places}f}"
                patterns[f"{name}@{places}"] = rf"(?<![\d.]){re.escape(text)}\s*%"
        elif value >= 1000:
            plain = rf"(?<![\d.,_]){value}(?![\d,_])"
            grouped = rf"(?<![\d.,_]){value:,}(?!\d)|(?<![\d.,_]){value:_}(?!\d)"
            patterns[name] = f"{plain}|{grouped}"
        else:
            noun = r"(?:authored\s+|deep-SKU\s+|grocery\s+)?(?:styles?|SKUs?|images?)\b"
            patterns[name] = (
                rf"^(?!(?:{'|'.join(TUNING)})\b)[A-Z][A-Z_]+\s*=\s*{value}\b"
                rf"|(?<![\d.,_]){value}\s+{noun}"
            )
    return patterns


def test_the_committed_figures_are_what_the_build_measures(stats: dict) -> None:
    fresh = retail_figures.render(retail_figures.measure())
    assert retail_figures.STATS.read_text("utf-8") == fresh, (
        f"golden-retail/stats.json is stale; run {REBUILD} and commit it"
    )


def test_the_per_family_counts_add_up(stats: dict) -> None:
    """The family and department counts are read from the file, so they must cover the build."""
    groc = stats["ceiling"]["grocery"]
    families = stats["grocery_families"].values()
    assert sum(f["styles"] for f in families) == groc["styles"]
    assert sum(f["skus"] for f in families) == groc["skus"]
    assert groc == stats["templates"]["grocery"]
    assert sum(stats["departments"].values()) == stats["ceiling"]["non_grocery"]["styles"]


@pytest.mark.parametrize("path", QUOTING)
def test_no_test_or_doc_restates_a_total_the_build_measures(stats: dict, path: str) -> None:
    text = _scoped(path, (ROOT / path).read_text("utf-8"))
    quoted = sorted(
        f"{figure} ({match.group(0)!r}, line {text.count(chr(10), 0, match.start()) + 1})"
        for figure, pattern in _quotations(stats).items()
        for match in re.finditer(pattern, text, re.MULTILINE)
    )
    assert quoted == [], (
        f"{path} restates totals the retail build measures: {quoted}. Read them from "
        f"golden-retail/stats.json (retail_figures.committed()) instead; {REBUILD} rewrites them"
    )


def test_the_guard_catches_a_restated_total(stats: dict) -> None:
    """Plants: each way a total was typed before is found by the patterns above."""
    plants = {
        "ceiling.skus": f"CAPACITY = (6_904, {stats['ceiling']['skus']:_})",
        "ceiling.styles": f"The ceiling is {stats['ceiling']['styles']:,} styles",
        "templates.authored.styles": f"AUTHORED = {stats['templates']['authored']['styles']}",
        "templates.main_food.styles": f"keeps {stats['templates']['main_food']['styles']} styles",
        "near_duplicates.grocery@1": f"(measured {stats['near_duplicates']['grocery'] * 100:.1f}%)",
    }
    patterns = _quotations(stats)
    missed = [
        name
        for name, text in plants.items()
        if not any(
            re.search(p, text, re.MULTILINE) for key, p in patterns.items() if key.startswith(name)
        )
    ]
    assert missed == []


def test_an_industrial_section_is_not_read_but_a_retail_figure_still_is(stats: dict) -> None:
    """An industrial figure equal to a retail total is let through; a stale retail one is not."""
    total = f"{stats['ceiling']['skus']:,}"
    doc = f"# R\n\nRetail text.\n\n### The 100K catalog\n\n{total} bearings\n\n## Brands\n\n"
    patterns = _quotations(stats)

    def hits(text: str) -> list[str]:
        return [k for k, p in patterns.items() if re.search(p, text, re.MULTILINE)]

    scoped = _scoped("README.md", doc)
    assert hits(doc) and hits(scoped) == []
    assert scoped.count("\n") == doc.count("\n")
    assert hits(_scoped("README.md", doc + f"The ceiling is {total} SKUs.")) != []
