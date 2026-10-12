"""The file-size budget: a file over its cap that grew is refused (elastic/prism#11683).

The check is elastic/prism's own ``scripts/check_file_size.py``, run on this
tree by ``scripts/file_size_gate.py``. Its rule: a measured file over the cap
in ``scripts/file_size_cap.txt`` may not hold more lines than it held at the
merge base, unless the pull-request body carries
``File-Size-Exception: `<path>` - <reason>``. Each case below builds a small
repository, plants a file, and runs the gate on it.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "file_size_gate.py"
CAP = 5


def _gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("file_size_gate", GATE)
    assert spec is not None and spec.loader is not None, f"{GATE} is missing"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        check=True,
        capture_output=True,
    )


def _write(repo: Path, relative: str, lines: int) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"x = {n}\n" for n in range(lines)), encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """``main``: README.md already over the cap, a small module, the cap file."""
    _git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / ".ignore").write_text("golden-catalog/\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "file_size_cap.txt").write_text(f"cap {CAP}\n", encoding="utf-8")
    _write(tmp_path, "README.md", CAP + 3)
    _write(tmp_path, "src/pkg/small.py", 2)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    _git(tmp_path, "switch", "-q", "-c", "change")
    return tmp_path


def _run(repo: Path, capsys: pytest.CaptureFixture[str], *argv: str, render=None):
    status = _gate().main(["--base", "main", *argv], root=repo, render=render)
    return status, capsys.readouterr().out


def test_a_new_file_over_the_cap_is_refused(repo, capsys) -> None:
    _write(repo, "src/pkg/big.py", CAP + 1)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "plant")
    status, out = _run(repo, capsys)
    assert status == 1, out
    assert "src/pkg/big.py" in out


def test_a_new_file_at_the_cap_is_accepted(repo, capsys) -> None:
    _write(repo, "src/pkg/fits.py", CAP)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "plant")
    status, out = _run(repo, capsys)
    assert status == 0, out


def test_an_over_cap_file_main_holds_passes_until_it_grows(repo, capsys) -> None:
    """Today's sizes are the seed: main is green, and only growth is refused."""
    status, out = _run(repo, capsys)
    assert status == 0, out
    _write(repo, "README.md", CAP + 4)
    status, out = _run(repo, capsys)
    assert status == 1, out
    assert "README.md" in out


def test_a_growth_the_body_declares_is_accepted(repo, capsys, tmp_path_factory) -> None:
    _write(repo, "README.md", CAP + 4)
    body = tmp_path_factory.mktemp("body") / "body.md"
    body.write_text("File-Size-Exception: `README.md` - one row more\n", encoding="utf-8")

    def render(_text: str) -> str:
        # What GitHub's /markdown answers for that body; no network in a test.
        return "<p>File-Size-Exception: <code>README.md</code> - one row more</p>"

    status, out = _run(repo, capsys, "--pr-body-file", str(body), render=render)
    assert status == 0, out


def test_the_vendored_core_copy_is_not_measured(repo, capsys) -> None:
    _write(repo, "vendor/prism/scripts/core_module.py", CAP + 1)
    status, out = _run(repo, capsys)
    assert status == 0, out


def test_this_tree_is_judged(capsys) -> None:
    """The gate reads this repository's cap file and ``.ignore`` and judges it."""
    status = _gate().main(["--list"])
    out = capsys.readouterr().out
    assert status == 0, out
    assert "scripts/mutation_check.py" in out
