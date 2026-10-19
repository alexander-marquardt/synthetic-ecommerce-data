"""The large build is named for the lines it holds, and no SKU total of it is typed (#62).

``--lines 39000`` was named ``HUNDRED_K_LINES`` and described as "about 100,000 SKUs", but the
SKU total grows with every deepened type (99,929 when the name was chosen, over 120,000 since).
The knob is a line count; the SKU total of each build is measured output (``skus`` in the
build's ``stats.json``), so a name or a sentence that promises a total goes stale on the next
type. These tests hold the name, and the two places that typed a total in prose.
"""

from __future__ import annotations

import re
from pathlib import Path

from synthetic_ecommerce_data.core import config

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "src" / "synthetic_ecommerce_data" / "core" / "config.py"
#: The prose that described the large build by a SKU total.
PROMISE = re.compile(r"about\s+(?:100K|100,000)\s+SKUs")
OLD_NAME = "HUNDRED_K_LINES"


def test_the_large_build_setting_is_named_for_the_lines_it_holds() -> None:
    assert getattr(config, "LARGE_BUILD_LINES", None) == 39000


def test_no_doc_names_the_setting_by_a_sku_total() -> None:
    docs = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    offenders = [str(p.relative_to(ROOT)) for p in docs if OLD_NAME in p.read_text("utf-8")]
    assert offenders == [], f"{offenders} name the large build's line count {OLD_NAME}"


def test_the_config_types_no_sku_total_of_a_build() -> None:
    """A SKU total in a comment is the figure that was 99,929 and is no longer."""
    typed = re.findall(r"\d{1,3}(?:,\d{3})+\s+SKUs", CONFIG.read_text("utf-8"))
    assert typed == [], f"config.py types SKU totals {typed}; read `skus` in stats.json"


def test_the_readme_does_not_promise_the_large_build_lands_at_a_sku_total() -> None:
    text = " ".join((ROOT / "README.md").read_text("utf-8").split())
    promised = [match.group(0) for match in PROMISE.finditer(text)]
    assert promised == [], f"README.md promises a SKU total for the large build: {promised}"
