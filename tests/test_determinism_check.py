"""``scripts/check_determinism.py``: two builds of one seed and commit are byte-identical.

elastic/prism-industrial-products#129 requires the 100K build to be
deterministic, checked by two builds with identical digests. The script is that
check at any ``--lines``. Here it runs at a small size, and a planted one-byte
difference proves the comparison bites.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_determinism.py"


def _module():
    spec = importlib.util.spec_from_file_location("check_determinism", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_two_small_builds_are_byte_identical():
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "--lines", "160"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert "DETERMINISTIC" in done.stdout
    # every emitted file was compared, not an empty set
    assert done.stdout.count(" same ") >= 6, done.stdout


def test_a_one_byte_difference_is_reported(tmp_path):
    left, right = tmp_path / "a", tmp_path / "b"
    for side in (left, right):
        side.mkdir()
        (side / "flat.jsonl").write_text('{"sku": "1"}\n', encoding="utf-8")
        (side / "stats.json").write_text("{}\n", encoding="utf-8")
    (right / "flat.jsonl").write_text('{"sku": "2"}\n', encoding="utf-8")
    differing = _module().compare(left, right)
    assert differing == ["flat.jsonl"]


def test_a_file_only_one_build_wrote_is_reported(tmp_path):
    left, right = tmp_path / "a", tmp_path / "b"
    left.mkdir()
    right.mkdir()
    (left / "flat.jsonl").write_text("x\n", encoding="utf-8")
    assert _module().compare(left, right) == ["flat.jsonl"]
