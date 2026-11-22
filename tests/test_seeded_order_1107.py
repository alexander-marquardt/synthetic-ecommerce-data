"""``--order-seed=<n>`` shuffles the collected tests from a seed, off by default (#1107).

The hook is ``tests/conftest.py``'s own, so each child run here copies that conftest into a
temporary directory beside three small modules and reads the order back from ``--collect-only``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: Three modules of four tests each, one with a class, so a shuffle has room to move them.
METHODS = "".join(f"    def test_b{n}(self):\n        pass\n\n" for n in range(4))
MODULES = {
    "test_a.py": "".join(f"def test_a{n}():\n    pass\n\n\n" for n in range(4)),
    "test_b.py": "class TestB:\n" + METHODS,
    "test_c.py": "".join(f"def test_c{n}():\n    pass\n\n\n" for n in range(4)),
}


def _run(tmp_path: Path, *options: str) -> str:
    """What a child pytest's ``--collect-only`` over the three modules prints."""
    (tmp_path / "conftest.py").write_text(
        (REPO / "tests" / "conftest.py").read_text(encoding="utf-8"), encoding="utf-8"
    )
    for name, text in MODULES.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    drop = ("PYTEST_ADDOPTS", "CI_SHARD", "CI_SHARDS", "WORKER_PEAK_DIR", "RETAIL_FIGURES_CACHE")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env["PYTHONPATH"] = str(REPO / "tests")
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-o", "addopts=", "-p", "no:cacheprovider",
         "--rootdir", str(tmp_path), "--collect-only", *options, *MODULES],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout


def _collected(tmp_path: Path, *options: str) -> list[str]:
    """The node ids a child pytest collects, in its order."""
    printed = _run(tmp_path, "-q", *options)
    ids = [line for line in printed.splitlines() if "::" in line]
    assert len(ids) == 12, printed
    return ids


def test_no_seed_keeps_the_file_order(tmp_path) -> None:
    ids = _collected(tmp_path)
    assert ids[0] == "test_a.py::test_a0" and ids[-1] == "test_c.py::test_c3", ids
    assert ids == sorted(ids, key=lambda i: (i[5], int(i[-1]))), ids
    assert "test order" not in _run(tmp_path)


def test_the_same_seed_gives_the_same_order_and_another_seed_another(tmp_path) -> None:
    first = _collected(tmp_path, "--order-seed=7")
    again = _collected(tmp_path, "--order-seed=7")
    other = _collected(tmp_path, "--order-seed=8")
    plain = _collected(tmp_path)
    assert first == again
    assert first != other
    assert sorted(first) == sorted(other) == sorted(plain)
    assert first != plain and other != plain
    assert "test order: shuffled by --order-seed=7" in _run(tmp_path, "--order-seed=7")


def test_a_shuffle_keeps_each_module_together(tmp_path) -> None:
    """A module's fixtures are built once: its tests are never split by another module's."""
    for seed in ("1", "2", "3"):
        ids = _collected(tmp_path, f"--order-seed={seed}")
        files = [i.split("::")[0] for i in ids]
        runs = [f for n, f in enumerate(files) if n == 0 or files[n - 1] != f]
        assert sorted(runs) == sorted(MODULES), (seed, ids)


def test_pytest_randomly_is_in_no_dependency_list_or_lock() -> None:
    for name in ("pyproject.toml", "uv.lock"):
        assert "pytest-randomly" not in (REPO / name).read_text(encoding="utf-8"), name
