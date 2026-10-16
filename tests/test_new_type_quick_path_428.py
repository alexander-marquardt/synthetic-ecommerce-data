"""docs/new-type-quick-path.md covers a type with its own drawn shape and its decoys (gen#428).

The page used to cover clothing and beauty scaffolds only, so an agent adding a type with its own
shape and cross-type text-match decoys read about 30 files to find where each piece goes (the
gifts and toy-vehicle agents spent 154K tokens on it). The section "A type with its own drawing
shape" lists every file such a type touches, one line each, and names two merged worked examples.
Three guards keep it true:

* every file the page names exists (a renamed file reds here, not in an agent's context);
* the section names each file in :data:`TOUCHED` (a file dropped from the list reds);
* the worked example is read from the live registry: its shape is drawn by the kit module the
  section names, and no retail module reads a part-number block (the page says there is none).
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

import kit  # noqa: E402
import type_registry  # noqa: E402

DOC = ROOT / "docs" / "new-type-quick-path.md"
HEADING = "## A type with its own drawing shape"
EXAMPLE = "garden_hose"

#: Every file (or family of files) an own-shape type touches or reads, as the section writes it.
TOUCHED = (
    "prototypes/retail_drawings/type_specs/<key>.py",
    "prototypes/retail_drawings/kit_garden.py",
    "prototypes/retail_drawings/kit_sports.py",
    "prototypes/retail_drawings/export.py",
    "prototypes/retail_drawings/main_color_hex.py",
    "prototypes/retail_drawings/main_colors.py",
    "prototypes/retail_drawings/decoy_product_words.py",
    "prototypes/retail_drawings/garden_rows.py",
    "prototypes/retail_drawings/tree_guard.py",
    "tests/test_retail_type_specs_351.py",
    "tests/test_retail_main_colors_275.py",
    "tests/test_retail_tree_nesting_283.py",
    "tests/test_retail_sports_265.py",
    "tests/test_retail_sports_decoys_368.py",
    "tests/test_retail_figures_162.py",
    "golden-retail/stats.json",
    "docs/retail-apparel-decoys.md",
    "docs/retail-product-word-decoys.md",
    "docs/retail-sports-tree.md",
    "prototypes/retail_drawings/retail_figures.py",
    "scripts/mutation_rows_",
)

PATH = re.compile(r"`([A-Za-z0-9_./<>*-]+\.(?:py|md|json|txt|sh))`")


def _text() -> str:
    return DOC.read_text("utf-8")


def _section() -> str:
    text = _text()
    assert HEADING in text, f"{DOC.name} has no section {HEADING!r}"
    body = text.split(HEADING, 1)[1]
    nxt = re.search(r"^## ", body, re.M)
    return body[: nxt.start()] if nxt else body


def _exists(name: str) -> bool:
    """A named file exists under the repo root or one of the directories the page abbreviates."""
    pattern = re.sub(r"<[a-z_]+>", "*", name)
    bases = (ROOT, RETAIL, ROOT / "scripts", ROOT / "docs")
    return any(next(base.glob(pattern), None) is not None for base in bases)


def test_the_page_has_an_own_shape_section_with_a_files_table() -> None:
    section = _section()
    assert "| File | Why |" in section
    rows = [line for line in section.splitlines() if re.match(r"\| `", line)]
    assert len(rows) >= 12, len(rows)


def test_every_path_the_page_names_exists() -> None:
    named = sorted(set(PATH.findall(_text())))
    assert len(named) >= 30, named
    missing = [name for name in named if not _exists(name)]
    assert not missing, f"{DOC.name} names files that do not exist: {missing}"


@pytest.mark.parametrize("name", TOUCHED)
def test_the_section_names_each_file_an_own_shape_type_touches(name: str) -> None:
    assert name in _section(), name


def test_each_listed_file_has_a_reason_in_the_same_row() -> None:
    rows = [line for line in _section().splitlines() if re.match(r"\| `", line)]
    thin = [r for r in rows if len(r.split("|")[2].strip().split()) < 4]
    assert not thin, thin


def test_the_section_names_two_merged_worked_examples() -> None:
    section = _section()
    assert "49438fc" in section and "bb49c3f" in section
    assert f"type_specs/{EXAMPLE}.py" in section


def test_the_worked_example_is_drawn_by_the_kit_module_the_section_names() -> None:
    spec = type_registry.specs()[EXAMPLE]
    shapes = {r.shape for r in spec.rows}
    assert len(shapes) == 1, shapes
    (shape,) = shapes
    module = kit.SHAPES[shape].__module__
    assert f"prototypes/retail_drawings/{module}.py" in _section(), module


def test_the_section_says_a_retail_type_has_no_part_number_block() -> None:
    """``ecom-generate block`` is the industrial catalog's: a retail id is ``BRD-<row code>``."""
    section = _section()
    assert "There is no part-number block" in section
    assert "BRD-" in section and "ecom-generate block" in section
    # rglob: type_specs/ holds most retail modules, and a glob of the top level never saw it
    readers = [
        str(p.relative_to(RETAIL))
        for p in RETAIL.rglob("*.py")
        if "block_of" in p.read_text("utf-8")
    ]
    assert not readers, f"a retail module reads a part-number block: {readers}"
