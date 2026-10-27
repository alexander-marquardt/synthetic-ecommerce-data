"""README.md has headroom under the file-size cap; the images reference has its own page (#701).

The README had refilled to three lines under the cap after the first split (#240), so the next
README-touching pull request would have turned main red. The ``## Images`` section (what a record
points at, the retail image release, the one renderer) now lives in ``docs/images.md`` and the
README keeps a short ``## Images`` that links it. These tests hold the split: the page holds the
three subsections, the README does not, the README links the page, no link dangles because a
section moved, and the README keeps real headroom (asserted, not only the cap).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PAGE = ROOT / "docs" / "images.md"

#: The three subsections of the README's old ``## Images`` section.
MOVED_HEADINGS = (
    "### Where a record points, and the bundle",
    "### The retail image release",
    "### One renderer",
)

#: The lines the README must stay under the cap by, and the size of the short section it keeps.
HEADROOM = 200
SHORT_SECTION_MAX_LINES = 10

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


def test_the_images_page_holds_the_moved_subsections():
    headings = _headings(PAGE)
    for h in MOVED_HEADINGS:
        assert h in headings, f"{PAGE.name} lost {h!r}"


def test_the_readme_no_longer_holds_the_moved_subsections():
    headings = _headings(README)
    for h in MOVED_HEADINGS:
        assert h not in headings, f"README.md still holds {h!r}"


def test_the_readme_links_the_images_page():
    assert any(
        link == "docs/images.md" or link.startswith("docs/images.md#") for link in _links(README)
    )


def test_the_readme_keeps_a_short_images_section():
    lines = _lines(README)
    start = lines.index("## Images")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    assert end - start <= SHORT_SECTION_MAX_LINES, f"## Images holds {end - start} lines"


def test_the_readme_has_headroom_under_the_file_size_cap():
    n = len(_lines(README))
    assert n <= _cap() - HEADROOM, f"README.md holds {n} lines against a cap of {_cap()}"


def test_no_link_in_the_readme_dangles():
    assert _dangling(README) == []


def test_no_link_in_the_images_page_dangles():
    assert _dangling(PAGE) == []


def test_no_doc_links_a_readme_anchor_of_a_moved_heading():
    moved = {_slug(h) for h in MOVED_HEADINGS}
    stale = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        for link in _links(path):
            target, _, anchor = link.partition("#")
            if target.endswith("README.md") and anchor in moved:
                stale.append(f"{path.relative_to(ROOT)}: {link}")
    assert stale == []


def test_the_docs_that_pointed_at_the_readme_images_section_resolve():
    for name in ("drawings.md", "retail-prototype.md"):
        path = ROOT / "docs" / name
        assert _dangling(path) == [], f"{name} has a dangling link"
        assert "../README.md#images" not in _links(path), f"{name} still points at the README"
