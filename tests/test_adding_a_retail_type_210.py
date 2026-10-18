"""docs/adding-a-retail-type.md is the one-page map of what a retail type touches (gen#210).

Each new-type batch (#196 to #199) spent a third to a half of an agent's context learning the
retail scale derivation, the export and the tests before writing code. The page lists those
places, one line each. Three guards keep it true and complete:

* the page names each topic the issue asks for (a topic dropped from the page reds here);
* every file path it names exists (a renamed file reds here, not in an agent's context);
* every ``module.NAME`` it names resolves and every command it shows runs a script that exists.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

DOC = ROOT / "docs" / "adding-a-retail-type.md"

#: The topics the issue lists (key: what it asks for), each with the words the page must carry.
#: row_subclass: where a Row goes and when to subclass it. frozen_keys: drawn attributes.
#: unit_canonicals: cm to mm and what check_catalog expects. plain_colors: color words, the
#: material apart. export_options: SKU options. owners_house_styles: brand owners and house
#: styles. templates_smaller_builds: where a row goes in templates(). image_per_colorway: one
#: image per style and colorway. stats_rebuild, tests_to_run, render_svgs: as named.
TOPICS = {
    "row_subclass": ("breadth_rows.Row", "FurnitureRow", "LRow"),
    "frozen_keys": ("scale.FROZEN_KEYS",),
    "unit_canonicals": ("value_canonical", "check_catalog", "CMT"),
    "plain_colors": ("COLOR_WORDS", "material"),
    "export_options": ("export.OPTIONS",),
    "owners_house_styles": ("breadth_rows.OWNERS", "house_styles.HOUSE_STYLES"),
    "templates_smaller_builds": ("scale.templates", "scale.build"),
    "image_per_colorway": ("image_id",),
    "stats_rebuild": ("retail_figures.py", "golden-retail/stats.json"),
    "tests_to_run": ("tests/test_retail_scale.py", "tests/test_output_standard.py"),
    "render_svgs": ("qlmanage", "ImageMagick"),
}

PATH = re.compile(r"`([A-Za-z0-9_./<>*-]+\.(?:py|md|json|txt|sh))`")
DOTTED = re.compile(r"`((?:[a-z_]+\.)+[A-Za-z_]+)(?:\(\))?`")
NODE = re.compile(r"`([A-Za-z0-9_./-]+\.py)::(\w+)`")
COMMAND = re.compile(r"`(uv run (?:python|pytest) [^`]+)`")


def _text() -> str:
    assert DOC.exists(), f"{DOC.relative_to(ROOT)} does not exist"
    return DOC.read_text("utf-8")


def _exists(name: str) -> bool:
    """A named file exists under the repo root or a directory the page abbreviates."""
    pattern = re.sub(r"<[a-z_]+>", "*", name)
    bases = (ROOT, RETAIL, ROOT / "tests", ROOT / "docs", ROOT / "scripts")
    return any(next(base.glob(pattern), None) is not None for base in bases)


@pytest.mark.parametrize("topic", sorted(TOPICS))
def test_the_page_covers_each_topic_the_issue_lists(topic: str) -> None:
    text = _text()
    missing = [word for word in TOPICS[topic] if word not in text]
    assert not missing, f"the page does not cover {topic!r}: it never names {missing}"


def test_the_page_is_one_page_and_points_to_the_quick_path() -> None:
    text = _text()
    assert len(text.splitlines()) <= 140, "a one-page map: keep it to 140 lines"
    assert "new-type-quick-path.md" in text, "the page does not say where the one-file path is"


def test_every_file_the_page_names_exists() -> None:
    names = sorted(set(PATH.findall(_text())))
    assert len(names) >= 15, f"the page names only {len(names)} files: {names}"
    missing = [n for n in names if not _exists(n)]
    assert not missing, f"docs/adding-a-retail-type.md names files that do not exist: {missing}"


def _resolve(dotted: str) -> bool:
    """``dotted`` is a module attribute (``scale.FROZEN_KEYS``) of a retail module or of the
    package: import the longest module prefix, then walk the rest as attributes."""
    parts = dotted.split(".")
    for i in range(len(parts) - 1, 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:i]))
        except ImportError:
            continue
        for attr in parts[i:]:
            if not hasattr(obj, attr):
                return False
            obj = getattr(obj, attr)
        return True
    return False


def test_every_module_name_the_page_names_resolves() -> None:
    retail = {p.stem for p in RETAIL.glob("*.py")}
    names = sorted(
        {
            n
            for n in DOTTED.findall(_text())
            if n.rsplit(".", 1)[1] not in {"py", "md", "json", "txt", "sh"}
            and (n.split(".")[0] in retail or n.startswith("synth"))
        }
    )
    assert len(names) >= 10, f"the page names only {len(names)} module attributes: {names}"
    missing = [n for n in names if not _resolve(n)]
    assert not missing, f"{DOC.name} names attributes that do not exist: {missing}"


def test_every_test_the_page_names_is_defined() -> None:
    nodes = NODE.findall(_text())
    assert nodes, "the page names no test by node id"
    missing = [
        f"{f}::{name}"
        for f, name in nodes
        if not (ROOT / f).exists() or f"def {name}(" not in (ROOT / f).read_text("utf-8")
    ]
    assert not missing, f"the page names tests that are not defined: {missing}"


def test_every_command_the_page_shows_runs_files_that_exist() -> None:
    commands = COMMAND.findall(_text())
    assert len(commands) >= 2, f"the page shows only {len(commands)} commands"
    missing = [
        f"{c}: {tok}"
        for c in commands
        for tok in c.split()
        if re.search(r"\.(py|md)$", tok) and not _exists(tok)
    ]
    assert not missing, f"commands name files that do not exist: {missing}"


def test_the_color_and_figures_sections_name_the_real_mechanism() -> None:
    text = _text()
    for needed in ("colorwords.PLAIN", "variants.cw", "docs/retail-apparel-decoys.md"):
        assert needed in text, f"the page does not name {needed}"
    assert "`Dark Brown`, `White`" not in text, "Dark Brown is a modifier plus a word"
    assert "millimetres" not in text, "US spelling: millimeters"
