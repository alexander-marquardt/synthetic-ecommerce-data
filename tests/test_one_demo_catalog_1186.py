"""One demo catalog: R&I's ``catalog_combined``, with retail and industrial as its domains.

Prose that puts "retail" before "demo" or "catalog" reads as a second catalog or demo, which
does not exist (gen#1186). This lint refuses it in every tracked file: write "the retail
domain", "retail products" or "the R&I demo". The refused phrases are built from parts here so
this file does not hold them.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: A phrase may wrap: a line break, a comment, quote or list marker, or the quotes of two
#: adjacent string literals, between the two words is still one phrase. A hyphen, an underscore
#: or a slash is not (``docs/retail-catalog-batch-1.md``, a path): those are names, not prose.
REFUSED = re.compile(r"""\bretail["']?\s[\s#>*"']*(?:demos?\b|catalog)""", re.IGNORECASE)

#: Files that may hold a refused phrase: a copy of the R&I repo's block pinned by sha256
#: (``scripts/check_industrial_unit_pin.py``), so its comments change there first
#: (elastic/prism-retail-and-industrial#2143).
EXEMPT = {"tests/data/industrial_canonical_units.yaml"}


def refused(text: str) -> list[int]:
    """The line numbers (from 1) at which ``text`` starts a refused phrase."""
    return [text.count("\n", 0, m.start()) + 1 for m in REFUSED.finditer(text)]


def tree_hits(root: Path) -> list[str]:
    """``path:line`` of each refused phrase in the tracked files under ``root``."""
    names = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True
    ).stdout.decode().split("\0")
    hits = []
    for name in filter(None, names):
        path = root / name
        if name in EXEMPT or not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="ignore")
        hits += [f"{name}:{line}" for line in refused(text)]
    return hits


@pytest.mark.parametrize(
    "text",
    [
        "Adds it to the retail " + "catalogue.",
        "the Retail " + "catalog at a size",
        "retail " + "catalogs",
        "a general-retail " + "demo",
        "the retail " + "demos",
        "rows of the retail\n" + "catalog",
        "# rows of the retail\n    # " + "catalogue",
        '"rows of the retail "\n    "' + 'catalog"',
    ],
)
def test_a_phrase_that_names_a_second_catalog_or_demo_is_refused(text) -> None:
    assert refused(f"first line\n{text}\n") == [2]


@pytest.mark.parametrize(
    "text",
    [
        "Adds it to the retail domain of the R&I catalogue (`catalog_combined`).",
        "retail products in the R&I demo",
        "a live retailer's catalog",
        "see docs/retail-catalog-batch-1.md",
        "from domains.retail.catalog import rows",
        'ROOT / "retail" / "catalog.jsonl"',
        "retail demographics",
    ],
)
def test_prose_that_names_the_domain_passes(text) -> None:
    assert refused(text) == []


def test_the_lint_names_the_file_and_line_of_a_tracked_phrase(tmp_path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "bad.md").write_text("# Page\n\nThe retail " + "catalogue has it.\n")
    (tmp_path / "docs" / "good.md").write_text("The retail domain has it.\n")
    (tmp_path / "untracked.md").write_text("the retail " + "demo\n")
    for args in (["init", "-q"], ["add", "docs"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True)
    assert tree_hits(tmp_path) == ["docs/bad.md:3"]


def test_no_tracked_file_names_a_second_catalog_or_demo() -> None:
    assert tree_hits(ROOT) == []


@pytest.mark.parametrize("name", sorted(EXEMPT))
def test_an_exempt_file_still_holds_a_refused_phrase(name) -> None:
    """Once its source is corrected and the copy is refreshed, the exemption goes with it."""
    assert refused((ROOT / name).read_text("utf-8")), f"{name} is clean: take it out of EXEMPT"
