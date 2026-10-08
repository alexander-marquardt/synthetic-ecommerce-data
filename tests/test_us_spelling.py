"""One spelling of the color word, US, in every tracked file (gen#125 ruling).

The field key is ``color`` and the label "Color", so a filter, a facet and a
grep each find one word. The British spelling is built from parts here so
this file does not hold it.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRITISH = re.compile("colo" + "u" + "r", re.IGNORECASE)


def test_no_tracked_file_spells_color_the_british_way() -> None:
    names = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True
    ).stdout.decode().split("\0")
    hits = []
    for name in filter(None, names):
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
