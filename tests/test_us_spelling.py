"""One spelling of the color word, US, in every tracked file (gen#125 ruling).

The field key is ``color`` and the label "Color", so a filter, a facet and a
grep each find one word. The British spelling is built from parts here so
this file does not hold it.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRITISH = re.compile("colo" + "u" + "r", re.IGNORECASE)

sys.path.insert(0, str(ROOT / "scripts"))
from file_size_gate import pinned_files  # noqa: E402  (the path is set up just above)

#: Core's vendored gate is a byte-for-byte copy (vendor/prism/PIN.txt), so a
#: word in it is respelt in core, never here; each path is exempt by name.
VENDORED = {f"vendor/prism/{path}" for path in pinned_files()}


def test_no_tracked_file_spells_color_the_british_way() -> None:
    names = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True
    ).stdout.decode().split("\0")
    hits = []
    for name in filter(None, names):
        if name in VENDORED:
            continue
        if BRITISH.search(name):
            hits.append(name)
            continue
        path = ROOT / name
        if not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="ignore")
        n = len(BRITISH.findall(text))
        if n:
            hits.append(f"{name}: {n}")
    assert hits == []


#: The retail catalogue's source: every module whose strings become a title, a description or a
#: drawing label, and whose docstrings and comments the same maintainers read. One spelling,
#: "center", in all of it (gen#291). The industrial engine's drawing code uses the engineering
#: "centre" for a bolt circle or a shaft axis and writes no catalogue text, so it is outside
#: this scope by name, not by omission.
RETAIL_SOURCE = ROOT / "prototypes" / "retail_drawings"
BRITISH_CENTER = re.compile("(?<![a-z])cent" + "(?:re|res|red|ring)(?![a-z])", re.IGNORECASE)


def test_no_retail_source_spells_center_the_british_way() -> None:
    files = sorted(RETAIL_SOURCE.glob("*.py"))
    assert len(files) > 20, "the scope glob found no retail modules"
    hits = []
    for path in files:
        n = len(BRITISH_CENTER.findall(path.read_text()))
        if n:
            hits.append(f"{path.name}: {n}")
    assert hits == []
