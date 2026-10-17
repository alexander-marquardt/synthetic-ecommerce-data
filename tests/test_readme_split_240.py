"""README.md stays under the file-size cap; the retail prototype reference has its own page (#240).

Every retail type batch used to add a line to the README, which was over the cap, so each
batch PR failed the ``file-size`` job after a full local CI run. The retail prototype
sections (planted distractors to the committed retail scale) now live in
``docs/retail-prototype.md``; a batch adds its listing line there. These tests hold the
split: the README is under the cap, the page holds the sections, the README points at it,
and no link in either file dangles because a section moved.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PAGE = ROOT / "docs" / "retail-prototype.md"

#: The first and last heading of the block that moved, and one heading from its middle.
MOVED_HEADINGS = (
    "## Planted distractors (retail prototype)",
    "### Footwear",
    "### Grocery",
    "### Observed failure classes 2 to 15, before and after on Elasticsearch",
    "### The retail catalog at a size: `scale.py --skus N`",
)

LINK = re.compile(r"\]\(([^)\s]+)\)")


def _cap() -> int:
    text = (ROOT / "scripts" / "file_size_cap.txt").read_text(encoding="utf-8")
    return int(next(ln.split()[1] for ln in text.splitlines() if ln.startswith("cap ")))


def _lines(path: Path) -> list[str]:
    assert path.exists(), f"{path.relative_to(ROOT)} is missing"
    return path.read_text(encoding="utf-8").splitlines()


def _headings(path: Path) -> list[str]:
    """Heading lines outside code fences."""
    out, fenced = [], False
    for line in _lines(path):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and re.match(r"#{1,6} ", line):
            out.append(line)
    return out


def _slug(heading: str) -> str:
    """GitHub's anchor for a heading line."""
    text = heading.lstrip("#").strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def _links(path: Path) -> list[str]:
    return [m.group(1) for line in _lines(path) for m in LINK.finditer(line)]


def test_readme_is_under_the_file_size_cap():
    n = len(_lines(README))
    assert n <= _cap(), f"README.md holds {n} lines against a cap of {_cap()}"


def test_the_retail_page_holds_the_moved_sections():
    headings = _headings(PAGE)
    for h in MOVED_HEADINGS:
        assert h in headings, f"{PAGE.name} lost {h!r}"


def test_the_readme_no_longer_holds_the_moved_sections():
    headings = _headings(README)
    for h in MOVED_HEADINGS:
        assert h not in headings, f"README.md still holds {h!r}"


def test_the_readme_links_the_retail_page():
    assert "docs/retail-prototype.md" in _links(README) or any(
        link.startswith("docs/retail-prototype.md#") for link in _links(README)
    )


def _dangling(path: Path) -> list[str]:
    own = {_slug(h) for h in _headings(path)}
    bad = []
    for link in _links(path):
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        target, _, anchor = link.partition("#")
        if not target:
            if anchor and anchor not in own:
                bad.append(link)
            continue
        dest = (path.parent / target).resolve()
        missing = not dest.exists()
        if not missing and anchor and dest.suffix == ".md":
            missing = anchor not in {_slug(h) for h in _headings(dest)}
        if missing:
            bad.append(link)
    return bad


def test_no_link_in_the_readme_dangles():
    assert _dangling(README) == []


def test_no_link_in_the_retail_page_dangles():
    assert _dangling(PAGE) == []
