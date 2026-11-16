"""README.md warns while a split is still cheap; the data model has its own page (#1034).

The images split (#701) left the README 10 lines under the bound that
``test_readme_split_images.py`` holds (the cap minus 200), and two approved pull requests that
each added five or six README lines went red together on the merge train. The README's
``### The data model`` section (what a parent and its SKUs are, the three tiers, the two shapes)
now lives in ``docs/data-model.md``. A second, earlier bound fails while main's README is within
``SPLIT_DUE`` lines of that one, so the next split is filed before README-touching pull requests
start colliding, not after.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from test_readme_split_images import HEADROOM, _cap, _dangling, _headings, _links

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PAGE = ROOT / "docs" / "data-model.md"

#: How near the headroom bound main's README may come before its next split is due: several
#: pull requests' worth of lines, so the split lands before two of them collide.
SPLIT_DUE = 50

#: The headings of the README's old ``### The data model`` section, one level up on its page.
MOVED_HEADINGS = (
    "## The data model",
    "### Three tiers say what makes a SKU different",
    "## Two shapes, one catalog",
)


def split_due(path: Path, cap: int) -> str | None:
    """Why ``path`` needs its next split filed now, or ``None`` while it has the slack."""
    n = len(path.read_text(encoding="utf-8").splitlines())
    bound = cap - HEADROOM
    if n <= bound - SPLIT_DUE:
        return None
    return (
        f"{path.name} holds {n} lines, within {SPLIT_DUE} of its bound of {bound} (the cap "
        f"{cap} minus {HEADROOM} lines of headroom): file the issue that moves one section to a "
        "page under docs/ (as #701 and #1034 did) before README-touching pull requests collide"
    )


def test_the_readme_has_a_split_s_slack_under_its_headroom_bound():
    assert split_due(README, _cap()) is None, split_due(README, _cap())


@pytest.mark.parametrize(("lines", "due"), [(1499, False), (1500, False), (1501, True)])
def test_the_split_falls_due_past_1500_lines_at_a_cap_of_1750(tmp_path, lines, due):
    readme = tmp_path / "README.md"
    readme.write_text("line\n" * lines, encoding="utf-8")
    assert (split_due(readme, 1750) is not None) is due


def test_the_data_model_page_holds_the_moved_sections():
    assert PAGE.exists(), f"{PAGE.relative_to(ROOT)} is missing"
    headings = _headings(PAGE)
    for h in MOVED_HEADINGS:
        assert h in headings, f"{PAGE.name} lost {h!r}"


def test_the_readme_no_longer_holds_the_moved_sections():
    headings = _headings(README)
    for h in MOVED_HEADINGS[1:]:
        assert "#" + h not in headings, f"README.md still holds {'#' + h!r}"


def test_the_readme_links_the_data_model_page():
    assert "docs/data-model.md" in _links(README)


def test_no_link_in_the_data_model_page_dangles():
    assert PAGE.exists(), f"{PAGE.relative_to(ROOT)} is missing"
    assert _dangling(PAGE) == []
